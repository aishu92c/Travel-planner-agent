"""AWS Helper Functions.

Utility functions for interacting with AWS services including Bedrock,
DynamoDB, S3, and Secrets Manager.

Example:
    >>> from utils.aws_helpers import get_bedrock_client, get_dynamodb_table
    >>> bedrock = get_bedrock_client()
    >>> table = get_dynamodb_table("my-table")
"""

import json
import logging
from functools import lru_cache
from typing import Any

import boto3
from botocore.config import Config
from botocore.exceptions import (
    ClientError,
    NoCredentialsError,
    PartialCredentialsError,
)
from config import get_settings

# Configure logging
logger = logging.getLogger(__name__)


class AWSError(Exception):
    """Base exception for AWS-related errors."""

    pass


class AWSCredentialsError(AWSError):
    """Exception raised when AWS credentials are invalid or missing."""

    pass


class AWSServiceError(AWSError):
    """Exception raised when AWS service calls fail."""

    pass


def _get_boto_config(
    max_retries: int = 3,
    timeout: int = 30,
    **kwargs: Any,
) -> Config:
    """Get boto3 client configuration.

    Args:
        max_retries: Maximum number of retry attempts
        timeout: Connection timeout in seconds
        **kwargs: Additional config parameters

    Returns:
        Config: Boto3 client configuration

    Example:
        >>> config = _get_boto_config(max_retries=5, timeout=60)
    """
    settings = get_settings()

    config_params = {
        "region_name": settings.aws.region,
        "retries": {
            "max_attempts": max_retries,
            "mode": "adaptive",  # Use adaptive retry mode
        },
        "connect_timeout": timeout,
        "read_timeout": timeout * 2,  # Read timeout typically longer
        "max_pool_connections": 50,
        **kwargs,
    }

    return Config(**config_params)


def get_boto3_client(
    service_name: str,
    region_name: str | None = None,
    max_retries: int = 3,
    timeout: int = 30,
    **kwargs: Any,
) -> boto3.client:
    """Get a boto3 client for the specified AWS service.

    This function creates a boto3 client with proper error handling,
    retry logic, and configuration from settings.

    Args:
        service_name: AWS service name (e.g., 's3', 'dynamodb', 'bedrock-runtime')
        region_name: AWS region (defaults to settings.aws.region)
        max_retries: Maximum number of retry attempts
        timeout: Connection timeout in seconds
        **kwargs: Additional client parameters

    Returns:
        boto3.client: Configured AWS service client

    Raises:
        AWSCredentialsError: If AWS credentials are invalid or missing
        AWSServiceError: If client creation fails

    Example:
        >>> s3_client = get_boto3_client('s3')
        >>> bedrock = get_boto3_client('bedrock-runtime', region_name='us-east-1')
    """
    try:
        settings = get_settings()

        # Use provided region or fall back to settings
        region = region_name or settings.aws.region

        # Get boto config
        config = _get_boto_config(max_retries=max_retries, timeout=timeout)

        # Create client
        client = boto3.client(
            service_name,
            region_name=region,
            config=config,
            **kwargs,
        )

        logger.info(f"Created boto3 client for service '{service_name}' in region '{region}'")

        return client

    except NoCredentialsError as e:
        error_msg = (
            "AWS credentials not found. Please configure AWS credentials "
            "using AWS CLI, environment variables, or IAM role."
        )
        logger.error(error_msg)
        raise AWSCredentialsError(error_msg) from e

    except PartialCredentialsError as e:
        error_msg = (
            "Incomplete AWS credentials. Please ensure both "
            "AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are set."
        )
        logger.error(error_msg)
        raise AWSCredentialsError(error_msg) from e

    except ClientError as e:
        error_msg = f"Failed to create boto3 client for '{service_name}': {e}"
        logger.error(error_msg)
        raise AWSServiceError(error_msg) from e

    except Exception as e:
        error_msg = f"Unexpected error creating boto3 client: {e}"
        logger.error(error_msg)
        raise AWSServiceError(error_msg) from e


@lru_cache(maxsize=10)
def get_bedrock_client(
    region_name: str | None = None,
    max_retries: int = 5,
) -> boto3.client:
    """Get AWS Bedrock Runtime client.

    This is a cached function that returns a singleton Bedrock client
    for the specified region.

    Args:
        region_name: AWS region (defaults to settings.aws.bedrock_runtime_region)
        max_retries: Maximum number of retry attempts

    Returns:
        boto3.client: Bedrock Runtime client

    Raises:
        AWSCredentialsError: If AWS credentials are invalid
        AWSServiceError: If client creation fails

    Example:
        >>> bedrock = get_bedrock_client()
        >>> response = bedrock.invoke_model(
        ...     modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        ...     body=json.dumps({"prompt": "Hello"})
        ... )
    """
    try:
        settings = get_settings()

        # Use provided region or fall back to bedrock_runtime_region
        region = region_name or settings.aws.bedrock_runtime_region

        logger.info(f"Creating Bedrock Runtime client in region '{region}'")

        return get_boto3_client(
            "bedrock-runtime",
            region_name=region,
            max_retries=max_retries,
            timeout=120,  # Longer timeout for LLM calls
        )

    except Exception as e:
        logger.error(f"Failed to create Bedrock client: {e}")
        raise


def get_bedrock_agent_client(
    region_name: str | None = None,
) -> boto3.client:
    """Get AWS Bedrock Agent client.

    Args:
        region_name: AWS region (defaults to settings.aws.region)

    Returns:
        boto3.client: Bedrock Agent client

    Raises:
        AWSCredentialsError: If AWS credentials are invalid
        AWSServiceError: If client creation fails

    Example:
        >>> bedrock_agent = get_bedrock_agent_client()
    """
    try:
        settings = get_settings()
        region = region_name or settings.aws.region

        logger.info(f"Creating Bedrock Agent client in region '{region}'")

        return get_boto3_client(
            "bedrock-agent-runtime",
            region_name=region,
            max_retries=5,
        )

    except Exception as e:
        logger.error(f"Failed to create Bedrock Agent client: {e}")
        raise


def get_dynamodb_resource(
    region_name: str | None = None,
    endpoint_url: str | None = None,
) -> boto3.resource:
    """Get DynamoDB resource.

    Args:
        region_name: AWS region (defaults to settings.aws.region)
        endpoint_url: Custom endpoint URL (for local DynamoDB)

    Returns:
        boto3.resource: DynamoDB resource

    Raises:
        AWSCredentialsError: If AWS credentials are invalid
        AWSServiceError: If resource creation fails

    Example:
        >>> dynamodb = get_dynamodb_resource()
        >>> table = dynamodb.Table('my-table')
    """
    try:
        settings = get_settings()

        region = region_name or settings.aws.region
        endpoint = endpoint_url or settings.aws.dynamodb_endpoint_url

        config = _get_boto_config(
            max_retries=settings.database.max_retries,
            timeout=settings.database.timeout_seconds,
        )

        # Create resource
        resource_kwargs = {
            "region_name": region,
            "config": config,
        }

        # Add endpoint URL if specified (for local DynamoDB)
        if endpoint:
            resource_kwargs["endpoint_url"] = endpoint
            logger.info(f"Using custom DynamoDB endpoint: {endpoint}")

        dynamodb = boto3.resource("dynamodb", **resource_kwargs)

        logger.info(f"Created DynamoDB resource in region '{region}'")

        return dynamodb

    except Exception as e:
        error_msg = f"Failed to create DynamoDB resource: {e}"
        logger.error(error_msg)
        raise AWSServiceError(error_msg) from e


def get_dynamodb_table(
    table_name: str,
    region_name: str | None = None,
    endpoint_url: str | None = None,
) -> Any:
    """Get DynamoDB table resource.

    Args:
        table_name: Name of the DynamoDB table
        region_name: AWS region (defaults to settings.aws.region)
        endpoint_url: Custom endpoint URL (for local DynamoDB)

    Returns:
        boto3.resources.dynamodb.Table: DynamoDB table resource

    Raises:
        AWSServiceError: If table doesn't exist or access fails

    Example:
        >>> table = get_dynamodb_table('langgraph-checkpoints')
        >>> response = table.get_item(Key={'id': '123'})
    """
    try:
        dynamodb = get_dynamodb_resource(
            region_name=region_name,
            endpoint_url=endpoint_url,
        )

        table = dynamodb.Table(table_name)

        # Verify table exists by loading metadata
        table.load()

        logger.info(f"Successfully connected to DynamoDB table '{table_name}'")

        return table

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            error_msg = f"DynamoDB table '{table_name}' not found"
            logger.error(error_msg)
            raise AWSServiceError(error_msg) from e
        else:
            error_msg = f"Failed to access DynamoDB table '{table_name}': {e}"
            logger.error(error_msg)
            raise AWSServiceError(error_msg) from e

    except Exception as e:
        error_msg = f"Unexpected error accessing DynamoDB table: {e}"
        logger.error(error_msg)
        raise AWSServiceError(error_msg) from e


def get_s3_resource(
    region_name: str | None = None,
    endpoint_url: str | None = None,
) -> boto3.resource:
    """Get S3 resource.

    Args:
        region_name: AWS region (defaults to settings.aws.region)
        endpoint_url: Custom endpoint URL (for LocalStack)

    Returns:
        boto3.resource: S3 resource

    Raises:
        AWSCredentialsError: If AWS credentials are invalid
        AWSServiceError: If resource creation fails

    Example:
        >>> s3 = get_s3_resource()
        >>> bucket = s3.Bucket('my-bucket')
    """
    try:
        settings = get_settings()

        region = region_name or settings.aws.region
        endpoint = endpoint_url or settings.aws.s3_endpoint_url

        config = _get_boto_config(max_retries=3, timeout=30)

        # Create resource
        resource_kwargs = {
            "region_name": region,
            "config": config,
        }

        # Add endpoint URL if specified (for LocalStack)
        if endpoint:
            resource_kwargs["endpoint_url"] = endpoint
            logger.info(f"Using custom S3 endpoint: {endpoint}")

        s3 = boto3.resource("s3", **resource_kwargs)

        logger.info(f"Created S3 resource in region '{region}'")

        return s3

    except Exception as e:
        error_msg = f"Failed to create S3 resource: {e}"
        logger.error(error_msg)
        raise AWSServiceError(error_msg) from e


def get_s3_bucket(
    bucket_name: str,
    region_name: str | None = None,
    endpoint_url: str | None = None,
) -> Any:
    """Get S3 bucket resource.

    Args:
        bucket_name: Name of the S3 bucket
        region_name: AWS region (defaults to settings.aws.region)
        endpoint_url: Custom endpoint URL (for LocalStack)

    Returns:
        boto3.resources.s3.Bucket: S3 bucket resource

    Raises:
        AWSServiceError: If bucket doesn't exist or access fails

    Example:
        >>> bucket = get_s3_bucket('my-artifacts-bucket')
        >>> bucket.upload_file('local.txt', 'remote.txt')
    """
    try:
        s3 = get_s3_resource(region_name=region_name, endpoint_url=endpoint_url)

        bucket = s3.Bucket(bucket_name)

        # Verify bucket exists and is accessible
        try:
            s3.meta.client.head_bucket(Bucket=bucket_name)
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                error_msg = f"S3 bucket '{bucket_name}' not found"
                logger.error(error_msg)
                raise AWSServiceError(error_msg) from e
            elif error_code == "403":
                error_msg = f"Access denied to S3 bucket '{bucket_name}'"
                logger.error(error_msg)
                raise AWSServiceError(error_msg) from e
            else:
                raise

        logger.info(f"Successfully connected to S3 bucket '{bucket_name}'")

        return bucket

    except AWSServiceError:
        # Re-raise AWSServiceError as-is
        raise

    except Exception as e:
        error_msg = f"Unexpected error accessing S3 bucket: {e}"
        logger.error(error_msg)
        raise AWSServiceError(error_msg) from e


def check_aws_credentials() -> bool:
    """Check if AWS credentials are valid.

    This function attempts to call AWS STS GetCallerIdentity to verify
    that credentials are configured and valid.

    Returns:
        bool: True if credentials are valid, False otherwise

    Example:
        >>> if check_aws_credentials():
        ...     print("AWS credentials are valid")
        ... else:
        ...     print("AWS credentials are invalid")
    """
    try:
        # Use STS to verify credentials
        sts = get_boto3_client("sts", timeout=10)

        # GetCallerIdentity doesn't require any permissions
        response = sts.get_caller_identity()

        account_id = response.get("Account")
        arn = response.get("Arn")

        logger.info(f"AWS credentials verified for account: {account_id}")
        logger.debug(f"Caller identity ARN: {arn}")

        return True

    except AWSCredentialsError:
        logger.warning("AWS credentials are not configured or invalid")
        return False

    except AWSServiceError:
        logger.warning("Failed to verify AWS credentials")
        return False

    except Exception as e:
        logger.warning(f"Unexpected error checking AWS credentials: {e}")
        return False


def get_aws_account_id() -> str | None:
    """Get the AWS account ID.

    Returns:
        Optional[str]: AWS account ID, or None if unable to retrieve

    Example:
        >>> account_id = get_aws_account_id()
        >>> print(f"Account ID: {account_id}")
    """
    try:
        sts = get_boto3_client("sts", timeout=10)
        response = sts.get_caller_identity()
        account_id = response.get("Account")

        logger.debug(f"Retrieved AWS account ID: {account_id}")

        return account_id

    except Exception as e:
        logger.warning(f"Failed to get AWS account ID: {e}")
        return None


def get_secret(
    secret_name: str,
    region_name: str | None = None,
    version_id: str | None = None,
    version_stage: str = "AWSCURRENT",
) -> dict[str, Any]:
    """Retrieve a secret from AWS Secrets Manager.

    Args:
        secret_name: Name or ARN of the secret
        region_name: AWS region (defaults to settings.aws.region)
        version_id: Version ID of the secret (optional)
        version_stage: Version stage (default: AWSCURRENT)

    Returns:
        Dict[str, Any]: Secret value as a dictionary

    Raises:
        AWSServiceError: If secret doesn't exist or retrieval fails

    Example:
        >>> secret = get_secret('langgraph/api_key')
        >>> api_key = secret.get('api_key')
    """
    try:
        settings = get_settings()

        # Add prefix if configured
        if not secret_name.startswith("arn:"):
            secret_name = f"{settings.aws.secrets_manager_prefix}{secret_name}"

        region = region_name or settings.aws.region

        # Get Secrets Manager client
        client = get_boto3_client("secretsmanager", region_name=region)

        # Build request parameters
        kwargs = {"SecretId": secret_name}

        if version_id:
            kwargs["VersionId"] = version_id
        else:
            kwargs["VersionStage"] = version_stage

        # Get secret value
        logger.info(f"Retrieving secret '{secret_name}' from Secrets Manager")

        response = client.get_secret_value(**kwargs)

        # Parse secret value
        if "SecretString" in response:
            secret_value = response["SecretString"]
            try:
                # Try to parse as JSON
                return json.loads(secret_value)
            except json.JSONDecodeError:
                # Return as plain string in a dict
                return {"value": secret_value}
        else:
            # Binary secret
            return {"binary": response["SecretBinary"]}

    except ClientError as e:
        error_code = e.response["Error"]["Code"]

        if error_code == "ResourceNotFoundException":
            error_msg = f"Secret '{secret_name}' not found in Secrets Manager"
            logger.error(error_msg)
            raise AWSServiceError(error_msg) from e

        elif error_code == "AccessDeniedException":
            error_msg = f"Access denied to secret '{secret_name}'"
            logger.error(error_msg)
            raise AWSServiceError(error_msg) from e

        elif error_code == "InvalidRequestException":
            error_msg = f"Invalid request for secret '{secret_name}': {e}"
            logger.error(error_msg)
            raise AWSServiceError(error_msg) from e

        else:
            error_msg = f"Failed to retrieve secret '{secret_name}': {e}"
            logger.error(error_msg)
            raise AWSServiceError(error_msg) from e

    except Exception as e:
        error_msg = f"Unexpected error retrieving secret: {e}"
        logger.error(error_msg)
        raise AWSServiceError(error_msg) from e


def put_secret(
    secret_name: str,
    secret_value: dict[str, Any],
    region_name: str | None = None,
    description: str | None = None,
) -> str:
    """Store or update a secret in AWS Secrets Manager.

    Args:
        secret_name: Name of the secret
        secret_value: Secret value as a dictionary
        region_name: AWS region (defaults to settings.aws.region)
        description: Description of the secret (optional)

    Returns:
        str: ARN of the created/updated secret

    Raises:
        AWSServiceError: If secret storage fails

    Example:
        >>> arn = put_secret(
        ...     'api_key',
        ...     {'key': 'secret-value-123'},
        ...     description='API key for external service'
        ... )
    """
    try:
        settings = get_settings()

        # Add prefix if configured
        if not secret_name.startswith("arn:"):
            secret_name = f"{settings.aws.secrets_manager_prefix}{secret_name}"

        region = region_name or settings.aws.region

        # Get Secrets Manager client
        client = get_boto3_client("secretsmanager", region_name=region)

        # Convert secret value to JSON
        secret_string = json.dumps(secret_value)

        try:
            # Try to update existing secret
            logger.info(f"Updating secret '{secret_name}'")

            response = client.put_secret_value(
                SecretId=secret_name,
                SecretString=secret_string,
            )

            return response["ARN"]

        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                # Secret doesn't exist, create it
                logger.info(f"Creating new secret '{secret_name}'")

                create_kwargs = {
                    "Name": secret_name,
                    "SecretString": secret_string,
                }

                if description:
                    create_kwargs["Description"] = description

                response = client.create_secret(**create_kwargs)

                return response["ARN"]
            else:
                raise

    except Exception as e:
        error_msg = f"Failed to store secret '{secret_name}': {e}"
        logger.error(error_msg)
        raise AWSServiceError(error_msg) from e


# Export all functions
__all__ = [
    # Exceptions
    "AWSError",
    "AWSCredentialsError",
    "AWSServiceError",
    # Client functions
    "get_boto3_client",
    "get_bedrock_client",
    "get_bedrock_agent_client",
    # DynamoDB functions
    "get_dynamodb_resource",
    "get_dynamodb_table",
    # S3 functions
    "get_s3_resource",
    "get_s3_bucket",
    # Utility functions
    "check_aws_credentials",
    "get_aws_account_id",
    # Secrets Manager functions
    "get_secret",
    "put_secret",
]
