"""Validation Utilities.

Provides comprehensive validation functions for AWS resources, user input, and data schemas.

This module provides:
- AWS resource validation (regions, model IDs, S3 URIs)
- Input sanitization and validation
- JSON schema validation
- Custom validation exceptions

Example:
    >>> from utils.validators import validate_aws_region, validate_s3_uri
    >>> validate_aws_region("us-east-1")  # Returns True
    >>> bucket, key = validate_s3_uri("s3://my-bucket/path/to/file.txt")
"""

import html
import re
from typing import Any
from urllib.parse import urlparse

# Custom validation exception


class ValidationError(ValueError):
    """Exception raised when validation fails.

    Attributes:
        message: Human-readable error message
        field: Optional field name that failed validation
        value: Optional value that failed validation
    """

    def __init__(self, message: str, field: str | None = None, value: Any | None = None):
        """Initialize validation error.

        Args:
            message: Error message
            field: Optional field name
            value: Optional invalid value
        """
        self.message = message
        self.field = field
        self.value = value

        # Build full error message
        full_message = message
        if field:
            full_message = f"{field}: {message}"
        if value is not None:
            full_message = f"{full_message} (got: {value!r})"

        super().__init__(full_message)


# AWS Region validation

# List of valid AWS regions as of 2024
VALID_AWS_REGIONS = {
    # US Regions
    "us-east-1",  # N. Virginia
    "us-east-2",  # Ohio
    "us-west-1",  # N. California
    "us-west-2",  # Oregon
    # Africa
    "af-south-1",  # Cape Town
    # Asia Pacific
    "ap-east-1",  # Hong Kong
    "ap-south-1",  # Mumbai
    "ap-south-2",  # Hyderabad
    "ap-northeast-1",  # Tokyo
    "ap-northeast-2",  # Seoul
    "ap-northeast-3",  # Osaka
    "ap-southeast-1",  # Singapore
    "ap-southeast-2",  # Sydney
    "ap-southeast-3",  # Jakarta
    "ap-southeast-4",  # Melbourne
    # Canada
    "ca-central-1",  # Canada (Central)
    # Europe
    "eu-central-1",  # Frankfurt
    "eu-central-2",  # Zurich
    "eu-west-1",  # Ireland
    "eu-west-2",  # London
    "eu-west-3",  # Paris
    "eu-south-1",  # Milan
    "eu-south-2",  # Spain
    "eu-north-1",  # Stockholm
    # Middle East
    "me-south-1",  # Bahrain
    "me-central-1",  # UAE
    # South America
    "sa-east-1",  # São Paulo
    # AWS GovCloud
    "us-gov-east-1",
    "us-gov-west-1",
}


def validate_aws_region(region: str) -> bool:
    """Validate AWS region name.

    Checks if the provided region string is a valid AWS region.

    Args:
        region: AWS region name to validate (e.g., "us-east-1")

    Returns:
        True if region is valid

    Raises:
        ValidationError: If region is invalid

    Example:
        >>> from utils.validators import validate_aws_region
        >>>
        >>> # Valid regions
        >>> validate_aws_region("us-east-1")
        True
        >>> validate_aws_region("eu-west-1")
        True
        >>>
        >>> # Invalid region
        >>> try:
        ...     validate_aws_region("invalid-region")
        ... except ValidationError as e:
        ...     print(f"Error: {e}")
        Error: region: Invalid AWS region (got: 'invalid-region')

    Example with configuration:
        >>> from utils.validators import validate_aws_region
        >>> from config import get_settings
        >>>
        >>> settings = get_settings()
        >>> try:
        ...     validate_aws_region(settings.aws.region)
        ...     print(f"Region {settings.aws.region} is valid")
        ... except ValidationError as e:
        ...     print(f"Invalid region in config: {e}")
    """
    if not region or not isinstance(region, str):
        raise ValidationError("Region must be a non-empty string", field="region", value=region)

    region = region.strip().lower()

    if region not in VALID_AWS_REGIONS:
        raise ValidationError(
            f"Invalid AWS region. Valid regions: {', '.join(sorted(VALID_AWS_REGIONS)[:5])}...",
            field="region",
            value=region,
        )

    return True


# Bedrock Model validation

# Valid Bedrock model ID patterns and families
BEDROCK_MODEL_FAMILIES = {
    "anthropic.claude": {
        "pattern": r"^anthropic\.claude-[a-z0-9\-\.]+:\d+$",
        "examples": [
            "anthropic.claude-3-5-sonnet-20241022-v2:0",
            "anthropic.claude-3-opus-20240229-v1:0",
            "anthropic.claude-3-sonnet-20240229-v1:0",
            "anthropic.claude-3-haiku-20240307-v1:0",
        ],
    },
    "amazon.titan": {
        "pattern": r"^amazon\.titan-[a-z0-9\-]+:\d+$",
        "examples": [
            "amazon.titan-text-express-v1:0",
            "amazon.titan-text-lite-v1:0",
            "amazon.titan-embed-text-v2:0",
            "amazon.titan-embed-text-v1:0",
        ],
    },
    "ai21.j2": {
        "pattern": r"^ai21\.j2-[a-z0-9\-]+$",
        "examples": ["ai21.j2-ultra-v1", "ai21.j2-mid-v1"],
    },
    "cohere.command": {
        "pattern": r"^cohere\.command-[a-z0-9\-]+$",
        "examples": ["cohere.command-text-v14", "cohere.command-light-text-v14"],
    },
    "meta.llama": {
        "pattern": r"^meta\.llama[0-9]+-[a-z0-9\-]+$",
        "examples": ["meta.llama2-13b-chat-v1", "meta.llama2-70b-chat-v1"],
    },
    "mistral.mistral": {
        "pattern": r"^mistral\.mistral-[a-z0-9\-]+$",
        "examples": ["mistral.mistral-7b-instruct-v0:2"],
    },
}


def validate_model_id(model_id: str) -> bool:
    """Validate AWS Bedrock model ID.

    Checks if the provided model ID matches a valid Bedrock model pattern.

    Args:
        model_id: Bedrock model ID to validate

    Returns:
        True if model ID is valid

    Raises:
        ValidationError: If model ID is invalid

    Example:
        >>> from utils.validators import validate_model_id
        >>>
        >>> # Valid model IDs
        >>> validate_model_id("anthropic.claude-3-5-sonnet-20241022-v2:0")
        True
        >>> validate_model_id("amazon.titan-text-express-v1:0")
        True
        >>>
        >>> # Invalid model ID
        >>> try:
        ...     validate_model_id("invalid-model")
        ... except ValidationError as e:
        ...     print(f"Error: {e}")
        Error: model_id: Invalid Bedrock model ID (got: 'invalid-model')

    Example with Bedrock call:
        >>> from utils.validators import validate_model_id
        >>> from utils import get_bedrock_client
        >>> import json
        >>>
        >>> def invoke_model_safe(model_id: str, prompt: str):
        ...     # Validate before calling Bedrock
        ...     validate_model_id(model_id)
        ...
        ...     bedrock = get_bedrock_client()
        ...     response = bedrock.invoke_model(
        ...         modelId=model_id,
        ...         body=json.dumps({
        ...             "anthropic_version": "bedrock-2023-05-31",
        ...             "max_tokens": 1000,
        ...             "messages": [{"role": "user", "content": prompt}]
        ...         })
        ...     )
        ...     return json.loads(response["body"].read())
    """
    if not model_id or not isinstance(model_id, str):
        raise ValidationError(
            "Model ID must be a non-empty string", field="model_id", value=model_id
        )

    model_id = model_id.strip()

    # Check against known model families
    for family, config in BEDROCK_MODEL_FAMILIES.items():
        if re.match(config["pattern"], model_id):
            return True

    # If no pattern matched, provide helpful error
    example_models = []
    for family_config in BEDROCK_MODEL_FAMILIES.values():
        example_models.extend(family_config["examples"][:2])

    raise ValidationError(
        f"Invalid Bedrock model ID. Examples: {', '.join(example_models[:4])}...",
        field="model_id",
        value=model_id,
    )


# S3 URI validation


def validate_s3_uri(uri: str) -> tuple[str, str]:
    """Validate and parse S3 URI.

    Parses an S3 URI and returns the bucket name and key (object path).

    Args:
        uri: S3 URI to validate (e.g., "s3://bucket/path/to/file.txt")

    Returns:
        Tuple of (bucket_name, object_key)

    Raises:
        ValidationError: If URI is invalid or not an S3 URI

    Example:
        >>> from utils.validators import validate_s3_uri
        >>>
        >>> # Valid S3 URIs
        >>> bucket, key = validate_s3_uri("s3://my-bucket/path/to/file.txt")
        >>> print(f"Bucket: {bucket}, Key: {key}")
        Bucket: my-bucket, Key: path/to/file.txt
        >>>
        >>> bucket, key = validate_s3_uri("s3://data-bucket/documents/report.pdf")
        >>> print(f"Bucket: {bucket}, Key: {key}")
        Bucket: data-bucket, Key: documents/report.pdf
        >>>
        >>> # Invalid URIs
        >>> try:
        ...     validate_s3_uri("https://example.com/file.txt")
        ... except ValidationError as e:
        ...     print(f"Error: {e}")
        Error: uri: URI must use s3:// scheme (got: 'https://example.com/file.txt')

    Example with S3 download:
        >>> from utils.validators import validate_s3_uri
        >>> from utils import get_s3_bucket
        >>>
        >>> def download_from_s3(s3_uri: str, local_path: str):
        ...     # Validate and parse URI
        ...     bucket_name, key = validate_s3_uri(s3_uri)
        ...
        ...     # Download file
        ...     bucket = get_s3_bucket(bucket_name)
        ...     bucket.download_file(key, local_path)
        ...     print(f"Downloaded {s3_uri} to {local_path}")
        >>>
        >>> download_from_s3("s3://my-bucket/data.csv", "/tmp/data.csv")

    Example with validation and error handling:
        >>> from utils.validators import validate_s3_uri, ValidationError
        >>>
        >>> def process_s3_file(uri: str):
        ...     try:
        ...         bucket, key = validate_s3_uri(uri)
        ...         print(f"Processing s3://{bucket}/{key}")
        ...         # ... process file
        ...     except ValidationError as e:
        ...         print(f"Invalid S3 URI: {e}")
        ...         return None
    """
    if not uri or not isinstance(uri, str):
        raise ValidationError("S3 URI must be a non-empty string", field="uri", value=uri)

    uri = uri.strip()

    # Parse URI
    try:
        parsed = urlparse(uri)
    except Exception as e:
        raise ValidationError(f"Failed to parse URI: {e}", field="uri", value=uri) from e

    # Check scheme
    if parsed.scheme != "s3":
        raise ValidationError("URI must use s3:// scheme", field="uri", value=uri)

    # Extract bucket and key
    bucket = parsed.netloc
    key = parsed.path.lstrip("/")

    # Validate bucket name
    if not bucket:
        raise ValidationError("S3 URI must include bucket name", field="uri", value=uri)

    # Validate bucket name format (simplified rules)
    if not re.match(r"^[a-z0-9][a-z0-9\-\.]{1,61}[a-z0-9]$", bucket):
        raise ValidationError(
            "Invalid S3 bucket name format. Must be 3-63 chars, lowercase, "
            "alphanumeric with hyphens/periods",
            field="bucket",
            value=bucket,
        )

    # Validate key
    if not key:
        raise ValidationError("S3 URI must include object key (path)", field="uri", value=uri)

    # Check for invalid characters in key
    if "\\" in key or "\0" in key:
        raise ValidationError("S3 object key contains invalid characters", field="key", value=key)

    return bucket, key


# Query validation


def validate_query_length(query: str, max_length: int = 10000, min_length: int = 1) -> bool:
    """Validate query text length.

    Checks if query length is within acceptable bounds.

    Args:
        query: Query text to validate
        max_length: Maximum allowed length (default: 10000)
        min_length: Minimum allowed length (default: 1)

    Returns:
        True if query length is valid

    Raises:
        ValidationError: If query length is invalid

    Example:
        >>> from utils.validators import validate_query_length
        >>>
        >>> # Valid queries
        >>> validate_query_length("What is AI?")
        True
        >>> validate_query_length("Short query", max_length=100)
        True
        >>>
        >>> # Invalid queries
        >>> try:
        ...     validate_query_length("")
        ... except ValidationError as e:
        ...     print(f"Error: {e}")
        Error: query: Query too short. Minimum length: 1 characters (got: '')
        >>>
        >>> try:
        ...     validate_query_length("x" * 10001)
        ... except ValidationError as e:
        ...     print(f"Error: {e}")
        Error: query: Query too long. Maximum length: 10000 characters

    Example with API request validation:
        >>> from utils.validators import validate_query_length
        >>> from api import QueryRequest
        >>>
        >>> def process_query(query: str):
        ...     # Validate query length before processing
        ...     validate_query_length(query, max_length=5000)
        ...
        ...     # Create request
        ...     request = QueryRequest(query=query)
        ...     # ... process request
        ...     return response

    Example with user input:
        >>> from utils.validators import validate_query_length, ValidationError
        >>>
        >>> def handle_user_query(query: str):
        ...     try:
        ...         validate_query_length(query, max_length=1000, min_length=3)
        ...         print(f"Processing: {query}")
        ...     except ValidationError as e:
        ...         print(f"Invalid query: {e}")
        ...         return {"error": str(e)}
    """
    if not isinstance(query, str):
        raise ValidationError("Query must be a string", field="query", value=type(query).__name__)

    query_length = len(query)

    if query_length < min_length:
        raise ValidationError(
            f"Query too short. Minimum length: {min_length} characters",
            field="query",
            value=query if len(query) <= 50 else f"{query[:50]}...",
        )

    if query_length > max_length:
        raise ValidationError(
            f"Query too long. Maximum length: {max_length} characters",
            field="query",
            value=f"Length: {query_length}",
        )

    # Check for whitespace-only query
    if not query.strip():
        raise ValidationError(
            "Query cannot be empty or whitespace only", field="query", value=query
        )

    return True


# Input sanitization

# Patterns for potentially harmful content
SCRIPT_PATTERN = re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
SQL_INJECTION_PATTERNS = [
    re.compile(r"(\bUNION\b.*\bSELECT\b)", re.IGNORECASE),
    re.compile(r"(\bDROP\b.*\bTABLE\b)", re.IGNORECASE),
    re.compile(r"(\bINSERT\b.*\bINTO\b)", re.IGNORECASE),
    re.compile(r"(--|\#|/\*|\*/)", re.IGNORECASE),
]


def sanitize_input(
    text: str,
    remove_html: bool = True,
    remove_scripts: bool = True,
    check_sql_injection: bool = True,
    max_length: int | None = None,
) -> str:
    """Sanitize user input by removing potentially harmful content.

    Removes or escapes dangerous content from user input including:
    - HTML tags and entities
    - JavaScript/script tags
    - SQL injection patterns
    - Control characters

    Args:
        text: Input text to sanitize
        remove_html: Remove HTML tags (default: True)
        remove_scripts: Remove script tags (default: True)
        check_sql_injection: Check for SQL injection patterns (default: True)
        max_length: Optional maximum length to truncate to

    Returns:
        Sanitized text

    Raises:
        ValidationError: If text contains dangerous patterns that can't be safely removed

    Example:
        >>> from utils.validators import sanitize_input
        >>>
        >>> # Basic sanitization
        >>> clean = sanitize_input("<b>Hello</b> World!")
        >>> print(clean)
        Hello World!
        >>>
        >>> # Remove scripts
        >>> clean = sanitize_input("<script>alert('xss')</script>Safe text")
        >>> print(clean)
        Safe text
        >>>
        >>> # HTML entities
        >>> clean = sanitize_input("5 &lt; 10 &amp; 10 &gt; 5")
        >>> print(clean)
        5 < 10 & 10 > 5

    Example with user input:
        >>> from utils.validators import sanitize_input
        >>>
        >>> def process_user_input(user_text: str):
        ...     # Sanitize before using
        ...     safe_text = sanitize_input(
        ...         user_text,
        ...         remove_html=True,
        ...         max_length=1000
        ...     )
        ...     return safe_text

    Example with SQL injection detection:
        >>> from utils.validators import sanitize_input, ValidationError
        >>>
        >>> try:
        ...     sanitize_input("SELECT * FROM users WHERE id = 1 OR 1=1--")
        ... except ValidationError as e:
        ...     print(f"Blocked: {e}")
        Blocked: text: Input contains potential SQL injection pattern

    Example with LLM prompt:
        >>> from utils.validators import sanitize_input
        >>> from utils import get_bedrock_client
        >>>
        >>> def safe_llm_query(user_query: str):
        ...     # Sanitize user input before sending to LLM
        ...     safe_query = sanitize_input(
        ...         user_query,
        ...         remove_html=True,
        ...         remove_scripts=True,
        ...         max_length=5000
        ...     )
        ...
        ...     bedrock = get_bedrock_client()
        ...     # ... invoke model with safe_query
        ...     return response
    """
    if not isinstance(text, str):
        raise ValidationError("Input must be a string", field="text", value=type(text).__name__)

    # Start with original text
    sanitized = text

    # Remove script tags first
    if remove_scripts:
        sanitized = SCRIPT_PATTERN.sub("", sanitized)

    # Check for SQL injection patterns
    if check_sql_injection:
        for pattern in SQL_INJECTION_PATTERNS:
            if pattern.search(sanitized):
                raise ValidationError(
                    "Input contains potential SQL injection pattern",
                    field="text",
                    value=sanitized[:100],
                )

    # Remove/escape HTML
    if remove_html:
        # First unescape HTML entities to get actual characters
        sanitized = html.unescape(sanitized)
        # Then remove all HTML tags
        sanitized = re.sub(r"<[^>]+>", "", sanitized)

    # Remove control characters (except newline, tab, carriage return)
    sanitized = "".join(char for char in sanitized if char in "\n\r\t" or ord(char) >= 32)

    # Strip leading/trailing whitespace
    sanitized = sanitized.strip()

    # Truncate if max_length specified
    if max_length is not None and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized


# JSON Schema validation


def validate_json_schema(data: dict[str, Any], schema: dict[str, Any]) -> bool:
    """Validate JSON data against a schema.

    Validates that a JSON/dict object conforms to a JSON Schema specification.

    Args:
        data: Data dictionary to validate
        schema: JSON Schema dictionary

    Returns:
        True if data is valid

    Raises:
        ValidationError: If data doesn't match schema
        ImportError: If jsonschema package is not installed

    Example:
        >>> from utils.validators import validate_json_schema
        >>>
        >>> # Define schema
        >>> schema = {
        ...     "type": "object",
        ...     "properties": {
        ...         "name": {"type": "string"},
        ...         "age": {"type": "number", "minimum": 0},
        ...         "email": {"type": "string", "format": "email"}
        ...     },
        ...     "required": ["name", "age"]
        ... }
        >>>
        >>> # Valid data
        >>> data = {"name": "John", "age": 30, "email": "john@example.com"}
        >>> validate_json_schema(data, schema)
        True
        >>>
        >>> # Invalid data
        >>> try:
        ...     invalid_data = {"name": "Jane", "age": -5}
        ...     validate_json_schema(invalid_data, schema)
        ... except ValidationError as e:
        ...     print(f"Error: {e}")
        Error: data: -5 is less than the minimum of 0

    Example with API request:
        >>> from utils.validators import validate_json_schema
        >>>
        >>> # Schema for chat message
        >>> message_schema = {
        ...     "type": "object",
        ...     "properties": {
        ...         "role": {"type": "string", "enum": ["user", "assistant", "system"]},
        ...         "content": {"type": "string", "minLength": 1}
        ...     },
        ...     "required": ["role", "content"]
        ... }
        >>>
        >>> def validate_message(message: dict):
        ...     validate_json_schema(message, message_schema)
        ...     return message

    Example with configuration:
        >>> from utils.validators import validate_json_schema
        >>>
        >>> # Schema for config
        >>> config_schema = {
        ...     "type": "object",
        ...     "properties": {
        ...         "api_key": {"type": "string", "minLength": 32},
        ...         "timeout": {"type": "number", "minimum": 0, "maximum": 300},
        ...         "retry_attempts": {"type": "integer", "minimum": 1, "maximum": 10}
        ...     },
        ...     "required": ["api_key"]
        ... }
        >>>
        >>> config = {
        ...     "api_key": "sk-1234567890abcdef1234567890abcdef",
        ...     "timeout": 30,
        ...     "retry_attempts": 3
        ... }
        >>> validate_json_schema(config, config_schema)
        True

    Example with Pydantic integration:
        >>> from utils.validators import validate_json_schema
        >>> from pydantic import BaseModel
        >>>
        >>> class User(BaseModel):
        ...     name: str
        ...     age: int
        >>>
        >>> # Get schema from Pydantic model
        >>> schema = User.model_json_schema()
        >>>
        >>> # Validate raw dict before creating model
        >>> user_data = {"name": "Alice", "age": 25}
        >>> validate_json_schema(user_data, schema)
        >>> user = User(**user_data)
    """
    try:
        import jsonschema
    except ImportError as e:
        raise ImportError(
            "jsonschema package is required for JSON schema validation. "
            "Install it with: pip install jsonschema"
        ) from e

    if not isinstance(data, dict):
        raise ValidationError("Data must be a dictionary", field="data", value=type(data).__name__)

    if not isinstance(schema, dict):
        raise ValidationError(
            "Schema must be a dictionary", field="schema", value=type(schema).__name__
        )

    try:
        jsonschema.validate(instance=data, schema=schema)
        return True
    except jsonschema.ValidationError as e:
        # Extract the most relevant error message
        error_path = " -> ".join(str(p) for p in e.path) if e.path else "root"
        raise ValidationError(
            f"{e.message}", field=f"data.{error_path}" if e.path else "data"
        ) from e
    except jsonschema.SchemaError as e:
        raise ValidationError(f"Invalid schema: {e.message}", field="schema") from e


__all__ = [
    "ValidationError",
    "validate_aws_region",
    "validate_model_id",
    "validate_s3_uri",
    "validate_query_length",
    "sanitize_input",
    "validate_json_schema",
]
