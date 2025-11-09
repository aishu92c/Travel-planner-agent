# Validation Utilities

Comprehensive validation functions for AWS resources, user input, and data
schemas.

## Overview

The validation utilities module (`src/utils/validators.py`) provides
production-ready validation functions:

- **AWS Resource Validation** - Regions, Bedrock models, S3 URIs
- **Input Sanitization** - Remove harmful content (XSS, SQL injection)
- **Query Validation** - Length and content checks
- **JSON Schema Validation** - Validate data against schemas
- **Custom Exceptions** - Descriptive ValidationError with field/value info

## Quick Start

```python
from utils import (
    validate_aws_region,
    validate_model_id,
    validate_s3_uri,
    sanitize_input,
    ValidationError
)

# Validate AWS region
validate_aws_region("us-east-1")  # Returns True

# Validate Bedrock model
validate_model_id("anthropic.claude-3-5-sonnet-20241022-v2:0")

# Parse S3 URI
bucket, key = validate_s3_uri("s3://my-bucket/path/to/file.txt")

# Sanitize user input
safe_text = sanitize_input("<script>alert('xss')</script>Hello")
# Returns: "Hello"
```

## Exception: ValidationError

Custom exception with enhanced error information.

```python
class ValidationError(ValueError):
    """Exception raised when validation fails."""

    def __init__(self, message: str, field: str = None, value: Any = None):
        ...
```

**Attributes:**

- `message` - Human-readable error message
- `field` - Optional field name that failed
- `value` - Optional value that failed

**Example:**

```python
from utils import ValidationError

try:
    validate_aws_region("invalid-region")
except ValidationError as e:
    print(f"Field: {e.field}")      # region
    print(f"Value: {e.value}")      # invalid-region
    print(f"Message: {e.message}")  # Invalid AWS region...
```

## Functions

### `validate_aws_region(region: str) -> bool`

Validate AWS region name.

**Parameters:**

- `region` - AWS region name (e.g., "us-east-1")

**Returns:** `True` if valid

**Raises:** `ValidationError` if invalid

**Supported Regions:**

- US: `us-east-1`, `us-east-2`, `us-west-1`, `us-west-2`
- Europe: `eu-central-1`, `eu-west-1`, `eu-west-2`, `eu-west-3`,
  `eu-north-1`, `eu-south-1`, `eu-south-2`, `eu-central-2`
- Asia Pacific: `ap-southeast-1`, `ap-southeast-2`, `ap-northeast-1`,
  `ap-northeast-2`, `ap-south-1`, `ap-east-1`, etc.
- Africa: `af-south-1`
- Middle East: `me-south-1`, `me-central-1`
- South America: `sa-east-1`
- Canada: `ca-central-1`
- GovCloud: `us-gov-east-1`, `us-gov-west-1`

**Example:**

```python
from utils import validate_aws_region, ValidationError

# Valid regions
validate_aws_region("us-east-1")     # ✓
validate_aws_region("eu-west-1")     # ✓
validate_aws_region("ap-southeast-1") # ✓

# Invalid regions
try:
    validate_aws_region("invalid-region")
except ValidationError as e:
    print(f"Error: {e}")
```

**Example with Configuration:**

```python
from utils import validate_aws_region
from config import get_settings

settings = get_settings()

# Validate region from config
try:
    validate_aws_region(settings.aws.region)
    print(f"Using region: {settings.aws.region}")
except ValidationError as e:
    print(f"Invalid region in configuration: {e}")
```

### `validate_model_id(model_id: str) -> bool`

Validate AWS Bedrock model ID.

**Parameters:**

- `model_id` - Bedrock model ID

**Returns:** `True` if valid

**Raises:** `ValidationError` if invalid

**Supported Model Families:**

- **Anthropic Claude**: `anthropic.claude-*`
- **Amazon Titan**: `amazon.titan-*`
- **AI21 Jurassic**: `ai21.j2-*`
- **Cohere Command**: `cohere.command-*`
- **Meta Llama**: `meta.llama*-*`
- **Mistral**: `mistral.mistral-*`

**Example:**

```python
from utils import validate_model_id, ValidationError

# Valid models
validate_model_id("anthropic.claude-3-5-sonnet-20241022-v2:0")  # ✓
validate_model_id("amazon.titan-text-express-v1:0")  # ✓
validate_model_id("ai21.j2-ultra-v1")  # ✓

# Invalid models
try:
    validate_model_id("gpt-4")  # Not a Bedrock model
except ValidationError as e:
    print(f"Error: {e}")
```

**Example with Bedrock Call:**

```python
from utils import validate_model_id, get_bedrock_client
import json

def invoke_model_safe(model_id: str, prompt: str):
    # Validate before calling Bedrock
    validate_model_id(model_id)

    bedrock = get_bedrock_client()
    response = bedrock.invoke_model(
        modelId=model_id,
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}]
        })
    )
    return json.loads(response["body"].read())
```

### `validate_s3_uri(uri: str) -> Tuple[str, str]`

Validate and parse S3 URI.

**Parameters:**

- `uri` - S3 URI (e.g., "s3://bucket/path/to/file.txt")

**Returns:** Tuple of `(bucket_name, object_key)`

**Raises:** `ValidationError` if invalid

**Example:**

```python
from utils import validate_s3_uri, ValidationError

# Valid URIs
bucket, key = validate_s3_uri("s3://my-bucket/file.txt")
print(f"Bucket: {bucket}, Key: {key}")
# Output: Bucket: my-bucket, Key: file.txt

bucket, key = validate_s3_uri("s3://data/reports/2024/report.pdf")
print(f"Bucket: {bucket}, Key: {key}")
# Output: Bucket: data, Key: reports/2024/report.pdf

# Invalid URIs
try:
    validate_s3_uri("https://example.com/file.txt")  # Wrong scheme
except ValidationError as e:
    print(f"Error: {e}")
```

**Example with S3 Download:**

```python
from utils import validate_s3_uri, get_s3_bucket

def download_from_s3(s3_uri: str, local_path: str):
    # Validate and parse URI
    bucket_name, key = validate_s3_uri(s3_uri)

    # Download file
    bucket = get_s3_bucket(bucket_name)
    bucket.download_file(key, local_path)
    print(f"Downloaded {s3_uri} to {local_path}")

download_from_s3("s3://my-bucket/data.csv", "/tmp/data.csv")
```

**Bucket Name Rules:**

- 3-63 characters
- Lowercase letters, numbers, hyphens, periods
- Must start and end with letter or number
- No uppercase, underscores, or spaces

**Key (Object Path) Rules:**

- Must not be empty
- Cannot contain backslashes or null characters
- Can include forward slashes for directory structure

### `validate_query_length(query, max_length=10000, min_length=1)`

Validate query text length.

**Parameters:**

- `query` - Query text
- `max_length` - Maximum length (default: 10000)
- `min_length` - Minimum length (default: 1)

**Returns:** `True` if valid

**Raises:** `ValidationError` if invalid

**Example:**

```python
from utils import validate_query_length, ValidationError

# Valid queries
validate_query_length("What is AI?")  # ✓
validate_query_length("Short query", max_length=100)  # ✓

# Invalid queries
try:
    validate_query_length("")  # Empty
except ValidationError as e:
    print(f"Error: {e}")

try:
    validate_query_length("x" * 10001)  # Too long
except ValidationError as e:
    print(f"Error: {e}")

try:
    validate_query_length("ab", min_length=3)  # Too short
except ValidationError as e:
    print(f"Error: {e}")
```

**Example with API Request:**

```python
from utils import validate_query_length
from api import QueryRequest

def process_query(query: str):
    # Validate before processing
    validate_query_length(query, max_length=5000, min_length=3)

    request = QueryRequest(query=query)
    # ... process request
    return response
```

**Checks:**

- Must be a string
- Length within min/max bounds
- Cannot be empty or whitespace-only

### `sanitize_input(text: str, ...) -> str`

Sanitize user input by removing harmful content.

**Parameters:**

- `text` - Input text to sanitize
- `remove_html` - Remove HTML tags (default: True)
- `remove_scripts` - Remove script tags (default: True)
- `check_sql_injection` - Check for SQL patterns (default: True)
- `max_length` - Optional max length to truncate to

**Returns:** Sanitized text

**Raises:** `ValidationError` if contains dangerous SQL patterns

**Example:**

```python
from utils import sanitize_input

# Remove HTML tags
clean = sanitize_input("<b>Hello</b> <i>World</i>!")
print(clean)  # Output: "Hello World!"

# Remove scripts
clean = sanitize_input("<script>alert('xss')</script>Safe text")
print(clean)  # Output: "Safe text"

# HTML entities
clean = sanitize_input("5 &lt; 10 &amp; 10 &gt; 5")
print(clean)  # Output: "5 < 10 & 10 > 5"

# Truncate
clean = sanitize_input("x" * 1000, max_length=100)
print(len(clean))  # Output: 100
```

**Example with SQL Injection Detection:**

```python
from utils import sanitize_input, ValidationError

# Blocked SQL patterns
dangerous_inputs = [
    "SELECT * FROM users WHERE id = 1 OR 1=1--",
    "'; DROP TABLE users; --",
    "UNION SELECT password FROM users"
]

for input_text in dangerous_inputs:
    try:
        sanitize_input(input_text)
        print(f"❌ Should have blocked: {input_text}")
    except ValidationError as e:
        print(f"✓ Blocked: {e}")
```

**Example with LLM Prompt:**

```python
from utils import sanitize_input, get_bedrock_client
import json

def safe_llm_query(user_query: str):
    # Sanitize user input before sending to LLM
    safe_query = sanitize_input(
        user_query,
        remove_html=True,
        remove_scripts=True,
        max_length=5000
    )

    bedrock = get_bedrock_client()
    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": safe_query}]
        })
    )
    return json.loads(response["body"].read())
```

**What Gets Removed:**

- HTML tags: `<script>`, `<div>`, `<p>`, etc.
- JavaScript: Script tags and content
- Control characters: Except `\n`, `\r`, `\t`
- SQL injection patterns (raises ValidationError)

**What's Preserved:**

- Unicode characters
- Newlines and tabs
- Legitimate special characters

### `validate_json_schema(data: dict, schema: dict) -> bool`

Validate JSON data against a schema.

**Parameters:**

- `data` - Data dictionary to validate
- `schema` - JSON Schema dictionary

**Returns:** `True` if valid

**Raises:**

- `ValidationError` if data doesn't match schema
- `ImportError` if jsonschema package not installed

**Example:**

```python
from utils import validate_json_schema, ValidationError

# Define schema
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "number", "minimum": 0},
        "email": {"type": "string", "format": "email"}
    },
    "required": ["name", "age"]
}

# Valid data
data = {"name": "John", "age": 30, "email": "john@example.com"}
validate_json_schema(data, schema)  # ✓

# Invalid data
try:
    invalid = {"name": "Jane", "age": -5}  # Age < 0
    validate_json_schema(invalid, schema)
except ValidationError as e:
    print(f"Error: {e}")
```

**Example with Chat Messages:**

```python
from utils import validate_json_schema

# Schema for chat message
message_schema = {
    "type": "object",
    "properties": {
        "role": {
            "type": "string",
            "enum": ["user", "assistant", "system"]
        },
        "content": {
            "type": "string",
            "minLength": 1
        }
    },
    "required": ["role", "content"]
}

def validate_message(message: dict):
    validate_json_schema(message, message_schema)
    return message

# Valid message
msg = {"role": "user", "content": "Hello!"}
validate_message(msg)  # ✓
```

**Example with Pydantic Integration:**

```python
from utils import validate_json_schema
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

# Get schema from Pydantic model
schema = User.model_json_schema()

# Validate raw dict before creating model
user_data = {"name": "Alice", "age": 25}
validate_json_schema(user_data, schema)
user = User(**user_data)
```

**Requires:** `pip install jsonschema`

## Production Examples

### Example 1: Complete Request Validation

```python
from utils import (
    validate_aws_region,
    validate_model_id,
    validate_query_length,
    validate_s3_uri,
    sanitize_input,
    ValidationError
)

def validate_bedrock_request(
    region: str,
    model_id: str,
    query: str,
    output_uri: str
):
    """Validate all parameters for a Bedrock request."""
    try:
        # Validate AWS region
        validate_aws_region(region)

        # Validate Bedrock model
        validate_model_id(model_id)

        # Validate and sanitize query
        validate_query_length(query, max_length=5000)
        safe_query = sanitize_input(query)

        # Validate S3 output URI
        bucket, key = validate_s3_uri(output_uri)

        return {
            "region": region,
            "model_id": model_id,
            "query": safe_query,
            "output_bucket": bucket,
            "output_key": key
        }
    except ValidationError as e:
        print(f"Validation failed: {e}")
        raise

# Use it
validated = validate_bedrock_request(
    region="us-east-1",
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    query="What is machine learning?",
    output_uri="s3://my-bucket/outputs/result.json"
)
```

### Example 2: API Endpoint Validation

```python
from fastapi import FastAPI, HTTPException
from utils import (
    validate_query_length,
    sanitize_input,
    ValidationError
)

app = FastAPI()

@app.post("/query")
async def process_query(query: str):
    """Process user query with validation."""
    try:
        # Validate length
        validate_query_length(query, max_length=1000, min_length=3)

        # Sanitize input
        safe_query = sanitize_input(query)

        # Process query
        result = process_llm_query(safe_query)

        return {"response": result}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Example 3: Configuration Validation

```python
from utils import validate_aws_region, validate_model_id, ValidationError
from config import get_settings

def validate_configuration():
    """Validate application configuration on startup."""
    settings = get_settings()
    errors = []

    # Validate AWS region
    try:
        validate_aws_region(settings.aws.region)
    except ValidationError as e:
        errors.append(f"Invalid AWS region: {e}")

    # Validate Bedrock model
    try:
        validate_model_id(settings.aws.bedrock.model_id)
    except ValidationError as e:
        errors.append(f"Invalid Bedrock model: {e}")

    if errors:
        raise ValueError(f"Configuration errors:\n" + "\n".join(errors))

    print("✓ Configuration validated successfully")

# Call on app startup
validate_configuration()
```

### Example 4: S3 Data Pipeline

```python
from utils import validate_s3_uri, get_s3_bucket, ValidationError

def process_s3_files(input_uris: list[str], output_uri: str):
    """Process multiple S3 files with validation."""
    # Validate all URIs first
    validated_inputs = []
    for uri in input_uris:
        try:
            bucket, key = validate_s3_uri(uri)
            validated_inputs.append((bucket, key))
        except ValidationError as e:
            print(f"Skipping invalid URI {uri}: {e}")
            continue

    # Validate output URI
    output_bucket, output_key_prefix = validate_s3_uri(output_uri)

    # Process files
    results = []
    for bucket_name, key in validated_inputs:
        bucket = get_s3_bucket(bucket_name)
        # ... process file
        results.append(result)

    return results
```

### Example 5: Form Input Sanitization

```python
from utils import sanitize_input, validate_query_length, ValidationError

def process_user_form(form_data: dict):
    """Process and sanitize user form submission."""
    sanitized = {}

    for field, value in form_data.items():
        if not isinstance(value, str):
            continue

        # Sanitize each field
        safe_value = sanitize_input(
            value,
            remove_html=True,
            remove_scripts=True,
            max_length=1000
        )

        sanitized[field] = safe_value

    # Validate comment length if present
    if "comment" in sanitized:
        try:
            validate_query_length(
                sanitized["comment"],
                max_length=500,
                min_length=10
            )
        except ValidationError as e:
            return {"error": f"Invalid comment: {e}"}

    return {"data": sanitized}
```

## Testing

Run the test suite:

```bash
# Install dependencies first
./setup-venv.sh

# Run tests
python test_validators.py
```

Tests cover:

- All validation functions
- ValidationError exception
- Valid and invalid inputs
- Edge cases (empty, whitespace, unicode)
- Integration scenarios
- SQL injection detection
- HTML/XSS prevention
- JSON schema validation

## Best Practices

### 1. Validate Early

Validate inputs as early as possible:

```python
from utils import validate_model_id, ValidationError

def invoke_model(model_id: str, prompt: str):
    # Validate BEFORE making expensive API call
    validate_model_id(model_id)

    # Now make the call
    return bedrock.invoke_model(...)
```

### 2. Always Sanitize User Input

Never trust user input:

```python
from utils import sanitize_input

def process_user_query(query: str):
    # ALWAYS sanitize before using
    safe_query = sanitize_input(query)
    return llm.query(safe_query)
```

### 3. Provide Helpful Error Messages

Use ValidationError's field and value:

```python
from utils import ValidationError

try:
    validate_aws_region(user_region)
except ValidationError as e:
    return {
        "error": str(e),
        "field": e.field,
        "suggestion": "Use us-east-1, eu-west-1, etc."
    }
```

### 4. Combine Multiple Validations

```python
from utils import (
    validate_query_length,
    sanitize_input,
    ValidationError
)

def safe_query_processing(query: str):
    # Multiple layers of validation
    validate_query_length(query, max_length=1000)
    safe_query = sanitize_input(query)

    # Additional business logic validation
    if not safe_query.endswith("?"):
        raise ValidationError("Query must be a question")

    return safe_query
```

### 5. Validate Configuration on Startup

```python
from utils import validate_aws_region, validate_model_id
from config import get_settings

# Validate on app startup
settings = get_settings()
validate_aws_region(settings.aws.region)
validate_model_id(settings.aws.bedrock.model_id)
```

## Summary

- **6 validation functions** for AWS resources and user input
- **Custom ValidationError** with field and value info
- **AWS validation** for regions, models, S3 URIs
- **Input sanitization** for XSS, SQL injection, HTML
- **Query validation** with length checks
- **JSON schema validation** with descriptive errors
- **Comprehensive tests** covering all functions
- **Production examples** for common use cases

Use these validators to build secure, robust applications with proper input
validation!
