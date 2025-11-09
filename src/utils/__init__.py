"""Utilities Module.

Common utility functions and helpers used across the application.

This module provides:
- AWS service clients and helpers (Bedrock, DynamoDB, S3, Secrets Manager)
- Retry decorators with exponential backoff (sync and async)
- Validation utilities (AWS resources, input sanitization, JSON schemas)
- Text processing utilities
- Date/time helpers
- Async helpers
- Common data transformations

Example:
    >>> from utils import (
    ...     get_bedrock_client,
    ...     retry_with_exponential_backoff,
    ...     validate_model_id,
    ...     sanitize_input
    ... )
    >>> from botocore.exceptions import ClientError
    >>>
    >>> @retry_with_exponential_backoff(max_attempts=5, exceptions=(ClientError,))
    >>> def invoke_model(model_id: str, prompt: str):
    ...     # Validate model ID
    ...     validate_model_id(model_id)
    ...     # Sanitize user input
    ...     safe_prompt = sanitize_input(prompt)
    ...     # Get client and invoke
    ...     bedrock = get_bedrock_client()
    ...     return bedrock.invoke_model(...)
"""

# AWS Helpers
try:
    from .aws_helpers import (
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
except (ImportError, ModuleNotFoundError):
    # AWS helpers are optional - may not have AWS configured
    pass

# Retry Utilities
from .retry import (
    RetryContext,
    async_retry_with_exponential_backoff,
    calculate_backoff_delay,
    retry_on_rate_limit,
    retry_with_exponential_backoff,
)

# Validation Utilities
from .validators import (
    ValidationError,
    sanitize_input,
    validate_aws_region,
    validate_json_schema,
    validate_model_id,
    validate_query_length,
    validate_s3_uri,
)

# Logging Utilities
from .logger import (
    get_node_logger,
    get_tool_logger,
    log_execution_time,
    log_llm_call,
    log_state_transition,
    log_tool_call,
    setup_logging,
)

# Visualization Utilities
try:
    from .visualize import generate_graph_visualization, print_graph_structure
except ImportError:
    pass

__all__ = [
    # AWS Helpers
    "AWSError",
    "AWSCredentialsError",
    "AWSServiceError",
    "get_boto3_client",
    "get_bedrock_client",
    "get_bedrock_agent_client",
    "get_dynamodb_resource",
    "get_dynamodb_table",
    "get_s3_resource",
    "get_s3_bucket",
    "check_aws_credentials",
    "get_aws_account_id",
    "get_secret",
    "put_secret",
    # Retry Utilities
    "retry_with_exponential_backoff",
    "async_retry_with_exponential_backoff",
    "retry_on_rate_limit",
    "calculate_backoff_delay",
    "RetryContext",
    # Validation Utilities
    "ValidationError",
    "validate_aws_region",
    "validate_model_id",
    "validate_s3_uri",
    "validate_query_length",
    "sanitize_input",
    "validate_json_schema",
    # Logging Utilities
    "configure_logging",
    "get_node_logger",
    "get_tool_logger",
    "log_execution_time",
    "log_section",
    "log_state_transition",
    "log_tool_call",
    "log_llm_call",
    "log_error_with_context",
    "PerformanceLogger",
    # Visualization Utilities
    "generate_graph_visualization",
    "print_graph_structure",
]
