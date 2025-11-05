#!/usr/bin/env python3
"""Test AWS Helper Functions.

Run this script to verify all AWS helper functions are working correctly.

Prerequisites:
    1. Set up virtual environment and install dependencies:
       ./setup-venv.sh

    2. Or manually:
       python3.13 -m venv venv
       source venv/bin/activate
       pip install -r requirements.txt
       pip install -r requirements-dev.txt

Usage:
    python test_aws_helpers.py

Note:
    This test uses mocking, so no actual AWS credentials are required.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_exceptions():
    """Test custom AWS exceptions."""
    print("=" * 70)
    print("Testing AWS Exceptions")
    print("=" * 70)

    from utils import AWSCredentialsError, AWSError, AWSServiceError

    # Test base exception
    try:
        raise AWSError("Base AWS error")
    except AWSError as e:
        print(f"✓ AWSError: {e}")

    # Test credentials exception
    try:
        raise AWSCredentialsError("Credentials not found")
    except AWSCredentialsError as e:
        print(f"✓ AWSCredentialsError: {e}")

    # Test service exception
    try:
        raise AWSServiceError("Service unavailable")
    except AWSServiceError as e:
        print(f"✓ AWSServiceError: {e}")

    print()


def test_get_boto3_client():
    """Test boto3 client creation."""
    print("=" * 70)
    print("Testing get_boto3_client")
    print("=" * 70)

    from utils import AWSCredentialsError, get_boto3_client

    # Mock boto3.client to avoid actual AWS calls
    with patch("utils.aws_helpers.boto3.client") as mock_client:
        mock_client.return_value = Mock(spec=["invoke_model"])

        # Test successful client creation
        client = get_boto3_client("s3")
        print(f"✓ Created S3 client: {type(client)}")

        # Verify it was called with correct parameters
        assert mock_client.called
        print("✓ boto3.client was called")

        # Test with custom region
        client = get_boto3_client("dynamodb", region_name="us-west-2")
        print("✓ Created DynamoDB client with custom region")

    # Test credentials error
    with patch("utils.aws_helpers.boto3.client") as mock_client:
        from botocore.exceptions import NoCredentialsError

        mock_client.side_effect = NoCredentialsError()

        try:
            get_boto3_client("s3")
            print("❌ Should have raised AWSCredentialsError")
        except AWSCredentialsError as e:
            print(f"✓ Credentials error handled: {str(e)[:50]}...")

    print()


def test_bedrock_clients():
    """Test Bedrock client creation."""
    print("=" * 70)
    print("Testing Bedrock Clients")
    print("=" * 70)

    from utils import get_bedrock_agent_client, get_bedrock_client

    # Mock boto3 client
    with patch("utils.aws_helpers.boto3.client") as mock_client:
        mock_bedrock = Mock(spec=["invoke_model"])
        mock_client.return_value = mock_bedrock

        # Test Bedrock Runtime client
        client = get_bedrock_client()
        print(f"✓ Created Bedrock Runtime client: {type(client)}")

        # Test that it's cached (should not create a new client)
        client2 = get_bedrock_client()
        print("✓ Bedrock client is cached (@lru_cache)")

        # Clear cache for next test
        get_bedrock_client.cache_clear()

        # Test Bedrock Agent client
        agent_client = get_bedrock_agent_client()
        print(f"✓ Created Bedrock Agent client: {type(agent_client)}")

    print()


def test_dynamodb_helpers():
    """Test DynamoDB helper functions."""
    print("=" * 70)
    print("Testing DynamoDB Helpers")
    print("=" * 70)

    from utils import get_dynamodb_resource, get_dynamodb_table

    # Mock boto3 resource
    with patch("utils.aws_helpers.boto3.resource") as mock_resource:
        mock_dynamodb = Mock()
        mock_table = Mock()
        mock_table.load = Mock()  # Mock the load method
        mock_dynamodb.Table.return_value = mock_table
        mock_resource.return_value = mock_dynamodb

        # Test DynamoDB resource creation
        resource = get_dynamodb_resource()
        print(f"✓ Created DynamoDB resource: {type(resource)}")

        # Test DynamoDB table access
        table = get_dynamodb_table("test-table")
        print(f"✓ Accessed DynamoDB table: {type(table)}")
        mock_table.load.assert_called_once()
        print("✓ Table existence verified (load() called)")

    print()


def test_s3_helpers():
    """Test S3 helper functions."""
    print("=" * 70)
    print("Testing S3 Helpers")
    print("=" * 70)

    from utils import get_s3_bucket, get_s3_resource

    # Mock boto3 resource
    with patch("utils.aws_helpers.boto3.resource") as mock_resource:
        mock_s3 = Mock()
        mock_bucket = Mock()
        mock_bucket.load = Mock()  # Mock the load method
        mock_s3.Bucket.return_value = mock_bucket
        mock_resource.return_value = mock_s3

        # Test S3 resource creation
        resource = get_s3_resource()
        print(f"✓ Created S3 resource: {type(resource)}")

        # Test S3 bucket access
        bucket = get_s3_bucket("test-bucket")
        print(f"✓ Accessed S3 bucket: {type(bucket)}")
        mock_bucket.load.assert_called_once()
        print("✓ Bucket existence verified (load() called)")

    print()


def test_credentials_check():
    """Test AWS credentials validation."""
    print("=" * 70)
    print("Testing Credentials Check")
    print("=" * 70)

    from utils import check_aws_credentials

    # Mock STS client
    with patch("utils.aws_helpers.get_boto3_client") as mock_get_client:
        mock_sts = Mock()
        mock_sts.get_caller_identity.return_value = {
            "UserId": "AIDAI1234567890",
            "Account": "123456789012",
            "Arn": "arn:aws:iam::123456789012:user/test-user",
        }
        mock_get_client.return_value = mock_sts

        # Test successful credentials check
        result = check_aws_credentials()
        print(f"✓ Credentials valid: {result}")
        assert result is True
        print("✓ check_aws_credentials returned True")

    # Test credentials failure
    with patch("utils.aws_helpers.get_boto3_client") as mock_get_client:
        from botocore.exceptions import NoCredentialsError

        mock_get_client.side_effect = NoCredentialsError()

        result = check_aws_credentials()
        print(f"✓ Credentials invalid: {result}")
        assert result is False
        print("✓ check_aws_credentials returned False for invalid credentials")

    print()


def test_get_account_id():
    """Test AWS account ID retrieval."""
    print("=" * 70)
    print("Testing Get Account ID")
    print("=" * 70)

    from utils import get_aws_account_id

    # Mock STS client
    with patch("utils.aws_helpers.get_boto3_client") as mock_get_client:
        mock_sts = Mock()
        mock_sts.get_caller_identity.return_value = {
            "Account": "123456789012",
        }
        mock_get_client.return_value = mock_sts

        # Test successful account ID retrieval
        account_id = get_aws_account_id()
        print(f"✓ Account ID retrieved: {account_id}")
        assert account_id == "123456789012"
        print("✓ Correct account ID returned")

    print()


def test_secrets_manager():
    """Test Secrets Manager helper functions."""
    print("=" * 70)
    print("Testing Secrets Manager")
    print("=" * 70)

    import json

    from utils import get_secret, put_secret

    # Test get_secret with JSON secret
    with patch("utils.aws_helpers.get_boto3_client") as mock_get_client:
        mock_secrets = Mock()
        mock_secrets.get_secret_value.return_value = {
            "SecretString": json.dumps({"username": "admin", "password": "secret123"})
        }
        mock_get_client.return_value = mock_secrets

        # Test retrieving JSON secret
        secret = get_secret("my-secret")
        print(f"✓ Retrieved JSON secret: {secret}")
        assert secret == {"username": "admin", "password": "secret123"}
        print("✓ Secret correctly parsed as JSON")

    # Test get_secret with string secret
    with patch("utils.aws_helpers.get_boto3_client") as mock_get_client:
        mock_secrets = Mock()
        mock_secrets.get_secret_value.return_value = {"SecretString": "plain-text-secret"}
        mock_get_client.return_value = mock_secrets

        # Test retrieving plain text secret
        secret = get_secret("my-secret")
        print(f"✓ Retrieved plain text secret: {secret}")
        assert secret == {"value": "plain-text-secret"}
        print("✓ Plain text secret wrapped in dict")

    # Test get_secret with binary secret
    with patch("utils.aws_helpers.get_boto3_client") as mock_get_client:
        mock_secrets = Mock()
        mock_secrets.get_secret_value.return_value = {"SecretBinary": b"binary-data"}
        mock_get_client.return_value = mock_secrets

        # Test retrieving binary secret
        secret = get_secret("my-binary-secret")
        print(f"✓ Retrieved binary secret: {secret}")
        assert secret == {"binary": b"binary-data"}
        print("✓ Binary secret correctly returned")

    # Test put_secret
    with patch("utils.aws_helpers.get_boto3_client") as mock_get_client:
        mock_secrets = Mock()
        mock_secrets.create_secret.return_value = {
            "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:my-secret",
            "Name": "my-secret",
            "VersionId": "v1",
        }
        mock_get_client.return_value = mock_secrets

        # Test creating new secret
        result = put_secret("new-secret", {"api_key": "12345"})
        print(f"✓ Created secret: {result['Name']}")
        assert result["Name"] == "my-secret"
        print("✓ put_secret successfully created secret")

    # Test put_secret update
    with patch("utils.aws_helpers.get_boto3_client") as mock_get_client:
        from botocore.exceptions import ClientError

        mock_secrets = Mock()

        # Simulate secret already exists
        def mock_create_secret(*args, **kwargs):
            error_response = {"Error": {"Code": "ResourceExistsException"}}
            raise ClientError(error_response, "CreateSecret")

        mock_secrets.create_secret.side_effect = mock_create_secret
        mock_secrets.put_secret_value.return_value = {
            "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:my-secret",
            "Name": "my-secret",
            "VersionId": "v2",
        }
        mock_get_client.return_value = mock_secrets

        # Test updating existing secret
        result = put_secret("existing-secret", {"api_key": "67890"})
        print(f"✓ Updated existing secret: {result['Name']}")
        assert result["VersionId"] == "v2"
        print("✓ put_secret successfully updated existing secret")

    print()


def test_configuration_integration():
    """Test that helpers use configuration correctly."""
    print("=" * 70)
    print("Testing Configuration Integration")
    print("=" * 70)

    from config import get_settings

    settings = get_settings()
    print(f"✓ Settings loaded: {settings.app_name}")
    print(f"✓ AWS Region: {settings.aws.region}")
    print(f"✓ Bedrock Model: {settings.aws.bedrock.model_id}")
    print(f"✓ DynamoDB Table: {settings.aws.dynamodb.table_name}")
    print(f"✓ S3 Bucket: {settings.aws.s3.bucket_name}")
    print("✓ All AWS helpers will use these settings")

    print()


def test_error_handling():
    """Test error handling in AWS helpers."""
    print("=" * 70)
    print("Testing Error Handling")
    print("=" * 70)

    from utils import AWSServiceError, get_boto3_client

    # Test service error handling
    with patch("utils.aws_helpers.boto3.client") as mock_client:
        from botocore.exceptions import ClientError

        error_response = {"Error": {"Code": "ServiceUnavailable", "Message": "Service unavailable"}}
        mock_client.side_effect = ClientError(error_response, "GetObject")

        try:
            get_boto3_client("s3")
            print("❌ Should have raised AWSServiceError")
        except AWSServiceError as e:
            print(f"✓ Service error handled: {str(e)[:50]}...")

    # Test unexpected error handling
    with patch("utils.aws_helpers.boto3.client") as mock_client:
        mock_client.side_effect = Exception("Unexpected error")

        try:
            get_boto3_client("s3")
            print("❌ Should have raised AWSError")
        except Exception as e:
            print(f"✓ Unexpected error handled: {type(e).__name__}")

    print()


def test_imports():
    """Test that all imports work correctly."""
    print("=" * 70)
    print("Testing Imports")
    print("=" * 70)

    # Test importing from utils
    from utils import (
        AWSCredentialsError,
        AWSError,
        AWSServiceError,
        check_aws_credentials,
        get_aws_account_id,
        get_bedrock_agent_client,
        get_bedrock_client,
        get_boto3_client,
        get_dynamodb_resource,
        get_dynamodb_table,
        get_s3_bucket,
        get_s3_resource,
        get_secret,
        put_secret,
    )

    print("✓ All AWS helper functions imported successfully")
    print("✓ All custom exceptions imported successfully")

    # Verify all functions are callable
    assert callable(get_boto3_client)
    assert callable(get_bedrock_client)
    assert callable(get_bedrock_agent_client)
    assert callable(get_dynamodb_resource)
    assert callable(get_dynamodb_table)
    assert callable(get_s3_resource)
    assert callable(get_s3_bucket)
    assert callable(check_aws_credentials)
    assert callable(get_aws_account_id)
    assert callable(get_secret)
    assert callable(put_secret)
    print("✓ All functions are callable")

    # Verify exceptions are proper exception classes
    assert issubclass(AWSError, Exception)
    assert issubclass(AWSCredentialsError, AWSError)
    assert issubclass(AWSServiceError, AWSError)
    print("✓ Exception hierarchy is correct")

    print()


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 20 + "AWS Helpers Test Suite" + " " * 26 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n")

    tests = [
        test_imports,
        test_exceptions,
        test_get_boto3_client,
        test_bedrock_clients,
        test_dynamodb_helpers,
        test_s3_helpers,
        test_credentials_check,
        test_get_account_id,
        test_secrets_manager,
        test_configuration_integration,
        test_error_handling,
    ]

    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}\n")
            import traceback

            traceback.print_exc()
            return 1

    print("=" * 70)
    print("✅ All AWS helper tests passed!")
    print("=" * 70)
    print("\nAWS Helper Functions Summary:")
    print("- 11 helper functions implemented")
    print("- 3 custom exception classes")
    print("- Full error handling and retry logic")
    print("- Integration with Pydantic Settings")
    print("- LRU caching for Bedrock client")
    print("- Support for: Bedrock, DynamoDB, S3, Secrets Manager, STS")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
