# AWS Helpers Module

Comprehensive AWS utility functions for the LangGraph AWS Template.

## Overview

The AWS helpers module (`src/utils/aws_helpers.py`) provides production-ready
utility functions for interacting with AWS services:

- **AWS Bedrock** - LLM inference with Claude models
- **AWS DynamoDB** - State storage and checkpoints
- **AWS S3** - Document and artifact storage
- **AWS Secrets Manager** - Secure credential management
- **AWS STS** - Credential validation and account information

## Quick Start

```python
from utils import (
    get_bedrock_client,
    get_dynamodb_table,
    get_s3_bucket,
    get_secret,
    check_aws_credentials
)

# Check AWS credentials
if check_aws_credentials():
    print("AWS credentials are valid!")

# Get Bedrock client (cached)
bedrock = get_bedrock_client()

# Access DynamoDB table
table = get_dynamodb_table("my-table")

# Access S3 bucket
bucket = get_s3_bucket("my-bucket")

# Retrieve secret
api_key = get_secret("api-key")
```

## Functions

### Client Creation

#### `get_boto3_client(service_name, region_name=None, max_retries=3, ...)`

Create a boto3 client with retry logic and error handling.

```python
from utils import get_boto3_client

# Create S3 client
s3 = get_boto3_client("s3")

# Create client with custom region and retries
dynamodb = get_boto3_client("dynamodb", region_name="us-west-2", max_retries=5)
```

**Features:**

- Automatic retry with adaptive mode
- Configurable timeout and max retries
- Uses settings from config
- Comprehensive error handling

### Bedrock Clients

#### `get_bedrock_client(region_name=None, max_retries=5)`

Get AWS Bedrock Runtime client (cached with @lru_cache).

```python
from utils import get_bedrock_client

# Get cached Bedrock client
bedrock = get_bedrock_client()

# Invoke Claude model
response = bedrock.invoke_model(
    modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [{"role": "user", "content": "Hello!"}]
    })
)
```

**Features:**

- LRU caching for performance
- 5 retries by default (LLM calls can be flaky)
- 120-second timeout

#### `get_bedrock_agent_client(region_name=None, max_retries=3)`

Get AWS Bedrock Agent client for multi-agent workflows.

```python
from utils import get_bedrock_agent_client

agent = get_bedrock_agent_client()
```

### DynamoDB Helpers

#### `get_dynamodb_resource(region_name=None, endpoint_url=None)`

Get DynamoDB resource.

```python
from utils import get_dynamodb_resource

# Production
dynamodb = get_dynamodb_resource()

# Local DynamoDB
dynamodb = get_dynamodb_resource(endpoint_url="http://localhost:8000")
```

#### `get_dynamodb_table(table_name, region_name=None, endpoint_url=None)`

Get DynamoDB table resource with existence verification.

```python
from utils import get_dynamodb_table

# Get table (verifies it exists)
table = get_dynamodb_table("agent-checkpoints")

# Put item
table.put_item(Item={"id": "123", "data": "value"})

# Get item
response = table.get_item(Key={"id": "123"})
```

**Features:**

- Automatic table existence check
- Support for local DynamoDB
- Uses settings from config

### S3 Helpers

#### `get_s3_resource(region_name=None, endpoint_url=None)`

Get S3 resource.

```python
from utils import get_s3_resource

# Production S3
s3 = get_s3_resource()

# LocalStack
s3 = get_s3_resource(endpoint_url="http://localhost:4566")
```

#### `get_s3_bucket(bucket_name, region_name=None, endpoint_url=None)`

Get S3 bucket resource with existence verification.

```python
from utils import get_s3_bucket

# Get bucket (verifies it exists)
bucket = get_s3_bucket("my-documents")

# Upload file
bucket.upload_file("/path/to/file.pdf", "documents/file.pdf")

# Download file
bucket.download_file("documents/file.pdf", "/path/to/download.pdf")
```

**Features:**

- Automatic bucket existence check
- Support for LocalStack
- Uses settings from config

### Credentials & Account

#### `check_aws_credentials(region_name=None)`

Validate AWS credentials using STS.

```python
from utils import check_aws_credentials

if check_aws_credentials():
    print("AWS credentials are valid")
else:
    print("AWS credentials are invalid or missing")
```

**Returns:** `bool` - True if credentials are valid, False otherwise

#### `get_aws_account_id(region_name=None)`

Get AWS account ID.

```python
from utils import get_aws_account_id

account_id = get_aws_account_id()
print(f"AWS Account: {account_id}")
```

**Returns:** `str` - AWS account ID (12 digits)

### Secrets Manager

#### `get_secret(secret_name, region_name=None, version_id=None, version_stage="AWSCURRENT")`

Retrieve secret from AWS Secrets Manager.

```python
from utils import get_secret

# Get JSON secret
db_creds = get_secret("database-credentials")
# Returns: {"username": "admin", "password": "secret123"}

# Get plain text secret
api_key = get_secret("api-key")
# Returns: {"value": "sk-abc123..."}

# Get binary secret
cert = get_secret("ssl-certificate")
# Returns: {"binary": b"..."}

# Get specific version
old_key = get_secret("api-key", version_id="v1")
```

**Features:**

- Auto-parses JSON secrets
- Wraps plain text in `{"value": "..."}` dict
- Returns binary as `{"binary": b"..."}`
- Supports secret versioning
- Automatic prefix from settings

#### `put_secret(secret_name, secret_value, description=None, region_name=None, tags=None)`

Create or update secret in AWS Secrets Manager.

```python
from utils import put_secret

# Create new secret
put_secret(
    "database-credentials",
    {"username": "admin", "password": "newpass123"},
    description="Database credentials for production"
)

# Update existing secret (automatically detected)
put_secret("api-key", {"value": "sk-new-key-456"})

# Create with tags
put_secret(
    "api-key",
    {"value": "sk-abc123"},
    tags={"Environment": "production", "Service": "api"}
)
```

**Features:**

- Automatically creates or updates
- Supports dict or string values
- Optional description and tags
- Uses prefix from settings

## Error Handling

### Custom Exceptions

```python
from utils import AWSError, AWSCredentialsError, AWSServiceError

try:
    client = get_bedrock_client()
except AWSCredentialsError as e:
    print(f"Credentials error: {e}")
except AWSServiceError as e:
    print(f"AWS service error: {e}")
except AWSError as e:
    print(f"General AWS error: {e}")
```

**Exception Hierarchy:**

- `AWSError` - Base exception for all AWS errors
- `AWSCredentialsError(AWSError)` - Credentials not found or invalid
- `AWSServiceError(AWSError)` - AWS service errors (throttling, etc.)

## Configuration

All functions use settings from `src/config/settings.py`:

```python
# Example settings from .env or config
AWS_REGION=us-east-1
AWS_BEDROCK_RUNTIME_REGION=us-east-1
AWS_DYNAMODB_TABLE_NAME=agent-checkpoints
AWS_S3_BUCKET_NAME=langgraph-artifacts
AWS_SECRETS_MANAGER_PREFIX=langgraph/
```

Access settings in code:

```python
from config import get_settings

settings = get_settings()
print(f"Region: {settings.aws.region}")
print(f"Table: {settings.aws.dynamodb.table_name}")
print(f"Bucket: {settings.aws.s3.bucket_name}")
```

## Retry Logic

All AWS clients use adaptive retry mode with exponential backoff:

```python
from botocore.config import Config

config = Config(
    retries={
        "mode": "adaptive",
        "max_attempts": max_retries,
    },
    connect_timeout=timeout,
    read_timeout=timeout,
)
```

**Benefits:**

- Automatic retry on transient failures
- Exponential backoff prevents overwhelming services
- Configurable retry attempts per function

## Caching

Bedrock client is cached with `@lru_cache`:

```python
@lru_cache(maxsize=10)
def get_bedrock_client(region_name=None, max_retries=5):
    # Client creation is expensive, cache it
    ...
```

**Benefits:**

- Avoid recreating clients unnecessarily
- Improved performance for frequent calls
- Cache up to 10 different configurations

Clear cache if needed:

```python
from utils import get_bedrock_client

get_bedrock_client.cache_clear()
```

## Testing

Run the test suite:

```bash
# Install dependencies first
./setup-venv.sh

# Run tests (uses mocking, no AWS credentials needed)
python test_aws_helpers.py
```

Tests cover:

- All 11 helper functions
- Custom exceptions
- Error handling
- Retry logic
- Configuration integration
- Caching behavior

## Production Usage

### Example: LangGraph Agent with Bedrock

```python
from utils import get_bedrock_client, get_dynamodb_table
import json

# Get clients
bedrock = get_bedrock_client()
checkpoints = get_dynamodb_table("agent-checkpoints")

# Invoke Claude
response = bedrock.invoke_model(
    modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [{"role": "user", "content": "Hello!"}]
    })
)

# Parse response
result = json.loads(response["body"].read())

# Save checkpoint
checkpoints.put_item(
    Item={
        "id": "session_123",
        "messages": result["content"],
        "timestamp": int(time.time())
    }
)
```

### Example: RAG with S3 Documents

```python
from utils import get_s3_bucket, get_secret
import json

# Get S3 bucket
bucket = get_s3_bucket("document-store")

# Get API key from Secrets Manager
api_key = get_secret("openai-api-key")["value"]

# Download document
bucket.download_file("docs/manual.pdf", "/tmp/manual.pdf")

# Process document
# ... chunking, embedding, etc ...

# Upload results
bucket.upload_file("/tmp/embeddings.json", "embeddings/manual.json")
```

## File Structure

```text
src/utils/
├── __init__.py          # Exports all AWS helpers
└── aws_helpers.py       # Implementation (600+ lines)

test_aws_helpers.py      # Test suite
AWS_HELPERS_README.md    # This file
```

## Summary

- **11 helper functions** for AWS services
- **3 custom exception classes** for error handling
- **Full integration** with Pydantic Settings
- **Retry logic** with adaptive mode
- **LRU caching** for Bedrock client
- **600+ lines** of production-ready code
- **Comprehensive tests** with mocking

All AWS helpers are ready to use in your LangGraph agents!
