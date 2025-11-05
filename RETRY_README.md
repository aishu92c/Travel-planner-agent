# Retry Utilities

Robust retry decorators with exponential backoff for handling transient
failures in AWS services and APIs.

## Overview

The retry utilities module (`src/utils/retry.py`) provides production-ready
retry decorators with exponential backoff:

- **Synchronous retry decorator** - For regular Python functions
- **Asynchronous retry decorator** - For async/await functions
- **Rate limit retry decorator** - Specialized for API rate limits
- **Retry context manager** - For manual retry control
- **Backoff calculation utility** - Standalone delay calculator

## Quick Start

```python
from utils import retry_with_exponential_backoff, get_bedrock_client
from botocore.exceptions import ClientError
import json

@retry_with_exponential_backoff(
    max_attempts=5,
    initial_delay=1.0,
    exceptions=(ClientError,)
)
def invoke_claude(prompt: str) -> dict:
    bedrock = get_bedrock_client()
    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}]
        })
    )
    return json.loads(response["body"].read())

# Will automatically retry on ClientError up to 5 times
result = invoke_claude("Hello, Claude!")
```

## Decorators

### `retry_with_exponential_backoff`

Retry decorator for synchronous functions with exponential backoff.

**Parameters:**

- `max_attempts` (int) - Maximum number of attempts (default: 3)
- `initial_delay` (float) - Initial delay in seconds (default: 1.0)
- `max_delay` (float) - Maximum delay in seconds (default: 60.0)
- `exponential_base` (float) - Base for exponential backoff (default: 2.0)
- `jitter` (bool) - Add random jitter to prevent thundering herd (default: True)
- `exceptions` (tuple) - Exception types to retry on (default: (Exception,))
- `on_retry` (callable) - Optional callback(exception, attempt) on each retry

**Backoff Formula:**

```text
delay = min(initial_delay * (base ^ attempt), max_delay)
if jitter: delay = delay * (0.5 + random())
```

**Example - Basic Usage:**

```python
from utils import retry_with_exponential_backoff

@retry_with_exponential_backoff(max_attempts=3)
def unstable_api_call():
    response = requests.get("https://api.example.com/data")
    response.raise_for_status()
    return response.json()

# Will retry up to 3 times with exponential backoff
data = unstable_api_call()
```

**Example - Specific Exceptions:**

```python
from utils import retry_with_exponential_backoff
from botocore.exceptions import ClientError

@retry_with_exponential_backoff(
    max_attempts=5,
    initial_delay=2.0,
    exceptions=(ClientError, TimeoutError)
)
def call_aws_service():
    # Only retries on ClientError or TimeoutError
    return client.describe_table(TableName="my-table")
```

**Example - Custom Retry Callback:**

```python
from utils import retry_with_exponential_backoff

def log_retry(exc: Exception, attempt: int):
    print(f"Retry #{attempt} after error: {type(exc).__name__}")

@retry_with_exponential_backoff(
    max_attempts=5,
    on_retry=log_retry
)
def monitored_function():
    return risky_operation()
```

### `async_retry_with_exponential_backoff`

Async version of retry decorator for async/await functions.

**Parameters:** Same as `retry_with_exponential_backoff`

**Example - Async Function:**

```python
from utils import async_retry_with_exponential_backoff
import asyncio

@async_retry_with_exponential_backoff(
    max_attempts=5,
    initial_delay=1.0
)
async def fetch_data_async(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Use in async context
async def main():
    data = await fetch_data_async("https://api.example.com/data")
    print(data)

asyncio.run(main())
```

**Example - Async Bedrock Call (with aioboto3):**

```python
from utils import async_retry_with_exponential_backoff
from botocore.exceptions import ClientError
import aioboto3
import json

@async_retry_with_exponential_backoff(
    max_attempts=5,
    exceptions=(ClientError,)
)
async def invoke_bedrock_async(prompt: str) -> dict:
    session = aioboto3.Session()
    async with session.client("bedrock-runtime") as bedrock:
        response = await bedrock.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        body = await response["body"].read()
        return json.loads(body)

# Use it
async def main():
    result = await invoke_bedrock_async("Hello!")
    print(result)
```

### `retry_on_rate_limit`

Specialized retry decorator optimized for API rate limits.

**Key Differences from Standard Retry:**

- Higher max attempts (default: 5)
- Longer initial delay (default: 2.0s)
- Longer max delay (default: 120s)
- Always uses jitter
- Auto-detects common rate limit errors

**Parameters:**

- `max_attempts` (int) - Maximum attempts (default: 5)
- `initial_delay` (float) - Initial delay (default: 2.0)
- `max_delay` (float) - Max delay (default: 120.0)
- `exponential_base` (float) - Backoff base (default: 2.0)
- `rate_limit_exceptions` (tuple) - Rate limit exception types
  (default: auto-detect)

**Auto-Detected Rate Limits:**

- AWS: `ThrottlingException`, `TooManyRequestsException`,
  `RequestLimitExceeded`, `ProvisionedThroughputExceededException`
- HTTP: 429 status codes
- Message patterns: "rate limit", "throttl"

**Example - AWS Bedrock Rate Limits:**

```python
from utils import retry_on_rate_limit

@retry_on_rate_limit(max_attempts=10, initial_delay=5.0)
def invoke_bedrock_with_rate_limit(prompt: str) -> dict:
    bedrock = get_bedrock_client()
    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}]
        })
    )
    return json.loads(response["body"].read())

# Will retry up to 10 times with longer delays for rate limits
result = invoke_bedrock_with_rate_limit("Hello!")
```

**Example - Custom Rate Limit Exception:**

```python
from utils import retry_on_rate_limit

class APIRateLimitError(Exception):
    pass

@retry_on_rate_limit(
    max_attempts=7,
    rate_limit_exceptions=(APIRateLimitError,)
)
def call_rate_limited_api():
    response = api.call()
    if response.status_code == 429:
        raise APIRateLimitError("Too many requests")
    return response.json()
```

## Utilities

### `calculate_backoff_delay`

Calculate backoff delay for manual retry logic.

**Parameters:**

- `attempt` (int) - Current attempt number (1-indexed)
- `initial_delay` (float) - Initial delay (default: 1.0)
- `max_delay` (float) - Max delay (default: 60.0)
- `exponential_base` (float) - Backoff base (default: 2.0)
- `jitter` (bool) - Add jitter (default: True)

**Returns:** `float` - Delay in seconds

**Example:**

```python
from utils import calculate_backoff_delay
import time

for attempt in range(1, 6):
    try:
        result = risky_operation()
        break
    except Exception as e:
        if attempt == 5:
            raise

        delay = calculate_backoff_delay(attempt)
        print(f"Retrying in {delay:.2f}s...")
        time.sleep(delay)
```

**Example - Manual Backoff Schedule:**

```python
from utils import calculate_backoff_delay

# Calculate a backoff schedule
schedule = [
    calculate_backoff_delay(i, initial_delay=1.0, jitter=False)
    for i in range(1, 6)
]
print(f"Backoff schedule: {schedule}")
# Output: [1.0, 2.0, 4.0, 8.0, 16.0]
```

### `RetryContext`

Context manager for manual retry control with state tracking.

**Parameters:** Same as `retry_with_exponential_backoff`

**Methods:**

- `record_failure(exception)` - Record a failed attempt
- `should_retry()` - Check if should retry
- `wait()` - Wait with exponential backoff
- `get_delay()` - Get delay without waiting

**Example - Basic Usage:**

```python
from utils import RetryContext
from botocore.exceptions import ClientError

retry_ctx = RetryContext(
    max_attempts=5,
    initial_delay=1.0,
    exceptions=(ClientError,)
)

for attempt in retry_ctx:
    try:
        result = bedrock.invoke_model(...)
        break  # Success
    except ClientError as e:
        retry_ctx.record_failure(e)
        if not retry_ctx.should_retry():
            raise
        retry_ctx.wait()

print(f"Succeeded after {retry_ctx.current_attempt} attempts")
```

**Example - Custom Backoff Logic:**

```python
from utils import RetryContext

retry_ctx = RetryContext(max_attempts=5)

for attempt in retry_ctx:
    try:
        result = risky_operation()
        break
    except Exception as e:
        retry_ctx.record_failure(e)
        if not retry_ctx.should_retry():
            raise

        # Custom logging
        delay = retry_ctx.get_delay()
        print(f"Attempt {attempt} failed. Waiting {delay:.2f}s...")
        retry_ctx.wait()
```

## Best Practices

### 1. Use Specific Exceptions

Always specify which exceptions to retry:

```python
# Good - only retries on specific errors
@retry_with_exponential_backoff(
    exceptions=(ClientError, TimeoutError)
)
def call_aws():
    ...

# Bad - retries on all exceptions including bugs
@retry_with_exponential_backoff()
def call_aws():
    ...
```

### 2. Set Appropriate Max Attempts

Different operations need different retry counts:

```python
# Quick operations - fewer retries
@retry_with_exponential_backoff(max_attempts=3)
def fast_api_call():
    ...

# Rate-limited operations - more retries
@retry_on_rate_limit(max_attempts=10)
def bedrock_call():
    ...
```

### 3. Use Rate Limit Decorator for APIs

For rate-limited APIs, use the specialized decorator:

```python
# Good - optimized for rate limits
@retry_on_rate_limit()
def call_bedrock():
    ...

# Suboptimal - standard retry might give up too quickly
@retry_with_exponential_backoff()
def call_bedrock():
    ...
```

### 4. Log Retry Attempts

Use callback to monitor retries:

```python
import logging

logger = logging.getLogger(__name__)

def log_retry(exc: Exception, attempt: int):
    logger.warning(f"Retry {attempt}: {exc}")

@retry_with_exponential_backoff(on_retry=log_retry)
def monitored_function():
    ...
```

### 5. Combine with Circuit Breaker

For production systems, combine with circuit breaker pattern:

```python
from utils import retry_on_rate_limit

class CircuitBreaker:
    def __init__(self, max_failures=5):
        self.failures = 0
        self.max_failures = max_failures

    def is_open(self):
        return self.failures >= self.max_failures

    def record_failure(self):
        self.failures += 1

    def reset(self):
        self.failures = 0

circuit = CircuitBreaker()

@retry_on_rate_limit(max_attempts=5)
def protected_call():
    if circuit.is_open():
        raise RuntimeError("Circuit breaker is open")

    try:
        result = bedrock.invoke_model(...)
        circuit.reset()
        return result
    except Exception as e:
        circuit.record_failure()
        raise
```

## Production Examples

### Example 1: LangGraph Agent with Retry

```python
from utils import retry_with_exponential_backoff, get_bedrock_client
from botocore.exceptions import ClientError
import json

@retry_with_exponential_backoff(
    max_attempts=5,
    initial_delay=1.0,
    exceptions=(ClientError,)
)
def invoke_agent(state: dict) -> dict:
    bedrock = get_bedrock_client()

    # Build prompt from state
    messages = state.get("messages", [])

    # Call Bedrock with retry
    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "messages": messages
        })
    )

    result = json.loads(response["body"].read())

    # Update state
    state["messages"].append({
        "role": "assistant",
        "content": result["content"][0]["text"]
    })

    return state
```

### Example 2: RAG with Vector Search Retry

```python
from utils import retry_with_exponential_backoff
from requests.exceptions import RequestException

@retry_with_exponential_backoff(
    max_attempts=3,
    exceptions=(RequestException, TimeoutError)
)
def vector_search(query: str, top_k: int = 5):
    """Search vector database with retry."""
    response = vector_db_client.search(
        query=query,
        top_k=top_k,
        timeout=10
    )
    return response.results
```

### Example 3: Batch Processing with Rate Limits

```python
from utils import retry_on_rate_limit
import time

@retry_on_rate_limit(max_attempts=10)
def process_item(item: dict) -> dict:
    """Process single item with rate limit handling."""
    return bedrock.invoke_model(...)

def process_batch(items: list) -> list:
    """Process batch of items with retry."""
    results = []

    for i, item in enumerate(items):
        print(f"Processing item {i+1}/{len(items)}")

        try:
            result = process_item(item)
            results.append(result)
        except Exception as e:
            print(f"Failed to process item {i}: {e}")
            # Continue with next item
            continue

        # Small delay between items to avoid rate limits
        time.sleep(0.5)

    return results
```

### Example 4: Async Streaming with Retry

```python
from utils import async_retry_with_exponential_backoff
import aioboto3
import json

@async_retry_with_exponential_backoff(max_attempts=5)
async def invoke_bedrock_streaming(prompt: str):
    """Invoke Bedrock with streaming and retry."""
    session = aioboto3.Session()

    async with session.client("bedrock-runtime") as bedrock:
        response = await bedrock.invoke_model_with_response_stream(
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            })
        )

        async for event in response["body"]:
            chunk = json.loads(event["chunk"]["bytes"])
            if chunk["type"] == "content_block_delta":
                yield chunk["delta"]["text"]
```

## Testing

Run the test suite:

```bash
# Install dependencies first
./setup-venv.sh

# Run tests
python test_retry.py
```

Tests cover:

- Success without retry
- Retry on transient failures
- Max attempts enforcement
- Specific exception handling
- Custom retry callbacks
- Async retry behavior
- Rate limit retry
- Backoff calculation
- RetryContext usage
- Logging behavior

## Configuration

### Tuning Retry Parameters

Different scenarios need different settings:

**Fast, Reliable APIs:**

```python
@retry_with_exponential_backoff(
    max_attempts=3,
    initial_delay=0.5,
    max_delay=5.0
)
```

**Slow, Rate-Limited APIs:**

```python
@retry_on_rate_limit(
    max_attempts=10,
    initial_delay=5.0,
    max_delay=300.0  # 5 minutes
)
```

**Critical Operations:**

```python
@retry_with_exponential_backoff(
    max_attempts=7,
    initial_delay=2.0,
    max_delay=120.0
)
```

## Summary

- **3 retry decorators** (sync, async, rate limit)
- **Exponential backoff** with configurable parameters
- **Jitter** to prevent thundering herd
- **Specific exception handling** for fine-grained control
- **Custom callbacks** for monitoring
- **Context manager** for manual control
- **Full type hints** and comprehensive documentation
- **Production-tested** with AWS Bedrock examples

Use retry utilities to build resilient applications that gracefully handle
transient failures!
