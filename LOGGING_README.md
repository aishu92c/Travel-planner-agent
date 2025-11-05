# Centralized Logging System

Production-ready structured logging with JSON formatting, context management,
and CloudWatch integration.

## Overview

The logging system (`src/observability/logging.py`) provides:

- **Structured Logging** - JSON format for production, readable console for development
- **Request ID Tracking** - Automatic request/user tracking across all logs
- **Context Management** - Add context to all logs within a scope
- **Logging Decorators** - Auto-log function execution and errors
- **Multiple Outputs** - Console, file, and CloudWatch
- **Environment-Aware** - Different configs for dev/staging/production
- **Async Support** - Full support for async/await functions

## Quick Start

```python
from observability import setup_logging, get_logger, LogContext

# 1. Setup logging once at app startup
setup_logging()

# 2. Get logger for your module
logger = get_logger(__name__)

# 3. Use logging
logger.info("Application started")

# 4. Add context for request tracking
with LogContext(request_id="req-123", user_id="user-456"):
    logger.info("Processing request")
    # All logs include request_id and user_id
```

## Core Functions

### `setup_logging()`

Configure centralized logging for the application.

**Parameters:**

- `level` - Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Defaults to
  settings or INFO.
- `json_format` - Use JSON formatting. Defaults to True for production, False
  for development.
- `log_file` - Path to log file. Optional.
- `enable_cloudwatch` - Enable CloudWatch logging. Defaults to settings.
- `cloudwatch_log_group` - CloudWatch log group name.
- `cloudwatch_log_stream` - CloudWatch log stream name.

**Example - Basic Setup:**

```python
from observability import setup_logging

# Use default settings
setup_logging()
```

**Example - Custom Setup:**

```python
from observability import setup_logging

setup_logging(
    level="DEBUG",
    json_format=False,
    log_file="/var/log/app.log"
)
```

**Example - Production Setup with CloudWatch:**

```python
from observability import setup_logging

setup_logging(
    level="INFO",
    json_format=True,
    log_file="/var/log/production.log",
    enable_cloudwatch=True,
    cloudwatch_log_group="myapp-production",
    cloudwatch_log_stream="instance-1"
)
```

**Example - FastAPI Integration:**

```python
from fastapi import FastAPI
from observability import setup_logging, get_logger

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    setup_logging()
    logger = get_logger(__name__)
    logger.info("Application started")

@app.on_event("shutdown")
async def shutdown_event():
    logger = get_logger(__name__)
    logger.info("Application shutting down")
```

### `get_logger(name: str)`

Get a context-aware logger for a module.

**Parameters:**

- `name` - Logger name (typically `__name__`)

**Returns:** Logger with automatic context support

**Example:**

```python
from observability import get_logger

logger = get_logger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

**Example - With Extra Fields:**

```python
from observability import get_logger

logger = get_logger(__name__)

logger.info(
    "User logged in",
    extra={
        "user_id": "user-123",
        "ip_address": "192.168.1.1",
        "login_method": "oauth"
    }
)
```

### `LogContext`

Context manager for adding context to all logs within a scope.

**Example - Basic Usage:**

```python
from observability import get_logger, LogContext

logger = get_logger(__name__)

with LogContext(request_id="req-123", user_id="user-456"):
    logger.info("Processing request")
    # Log includes: request_id and user_id

    logger.info("Validating input")
    # Log includes: request_id and user_id
```

**Example - Nested Context:**

```python
with LogContext(request_id="req-123"):
    logger.info("Request started")  # Has request_id

    with LogContext(operation="validate"):
        logger.info("Validating")  # Has request_id + operation

    logger.info("Request completed")  # Has request_id only
```

**Example - API Request Tracking:**

```python
from fastapi import Request
from observability import LogContext, get_logger
import uuid

logger = get_logger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())

    with LogContext(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host
    ):
        logger.info("Request started")

        response = await call_next(request)

        logger.info(
            "Request completed",
            extra={"status_code": response.status_code}
        )

        return response
```

**Methods:**

- `LogContext.current()` - Get current context dictionary
- `LogContext.clear()` - Clear all context

### `@log_execution`

Decorator to automatically log function execution.

**Parameters:**

- `level` - Log level (default: "INFO")
- `include_args` - Log function arguments (default: True)
- `include_result` - Log function result (default: False)
- `include_duration` - Log execution duration (default: True)

**Example - Basic Usage:**

```python
from observability import log_execution, get_logger

logger = get_logger(__name__)

@log_execution(level="INFO", include_duration=True)
def process_data(data: dict) -> dict:
    # Process data
    return result

# Logs:
# - "Executing process_data"
# - "process_data completed successfully" (with duration)
```

**Example - With Arguments:**

```python
@log_execution(
    level="DEBUG",
    include_args=True,
    include_result=True
)
def calculate(x: int, y: int) -> int:
    return x + y

calculate(5, 3)
# Logs arguments (5, 3) and result (8)
```

**Example - Async Functions:**

```python
@log_execution(level="INFO", include_duration=True)
async def fetch_user(user_id: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"/users/{user_id}") as response:
            return await response.json()

await fetch_user("user-123")
# Logs execution and duration
```

**Example - Bedrock Call:**

```python
from observability import log_execution, get_logger
from utils import get_bedrock_client
import json

@log_execution(level="INFO", include_duration=True)
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

# Logs function execution and duration
result = invoke_claude("Hello, Claude!")
```

### `@log_errors`

Decorator to automatically log errors with full context.

**Parameters:**

- `logger` - Logger to use. If None, uses function's module logger.

**Example:**

```python
from observability import log_errors, get_logger

logger = get_logger(__name__)

@log_errors(logger)
def risky_operation(value: int) -> int:
    if value < 0:
        raise ValueError("Value must be positive")
    return value * 2

try:
    risky_operation(-5)
except ValueError:
    pass  # Error already logged with full traceback
```

**Example - Without Explicit Logger:**

```python
@log_errors()
def process_file(path: str) -> str:
    with open(path) as f:
        return f.read()

# Automatically uses logger from current module
process_file("nonexistent.txt")
# Logs FileNotFoundError with traceback
```

**Example - Async Functions:**

```python
@log_errors()
async def fetch_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Logs any errors with full context
```

**Example - Combined with log_execution:**

```python
@log_execution(level="INFO", include_duration=True)
@log_errors()
def complex_operation(data: dict) -> dict:
    # Both execution and errors are logged
    return process(data)
```

## Log Formats

### JSON Format (Production)

Structured logs in JSON format for easy parsing and indexing.

**Example Output:**

```json
{
    "timestamp": "2025-01-15T10:30:00.123456Z",
    "level": "INFO",
    "logger": "app.services.user",
    "message": "User created",
    "request_id": "req-abc123",
    "user_id": "user-456",
    "duration_ms": 150.5,
    "source": {
        "file": "/app/services/user.py",
        "line": 42,
        "function": "create_user"
    },
    "process": {
        "pid": 12345,
        "thread": 67890,
        "thread_name": "MainThread"
    }
}
```

### Console Format (Development)

Human-readable format with colors for development.

**Example Output:**

```text
2025-01-15 10:30:00 INFO     [app.services.user] User created
    (request_id=req-abc123 user_id=user-456)
2025-01-15 10:30:01 WARNING  [app.validation] Invalid input (request_id=req-abc123)
2025-01-15 10:30:02 ERROR    [app.database] Connection failed
```

**Color Coding:**

- DEBUG - Cyan
- INFO - Green
- WARNING - Yellow
- ERROR - Red
- CRITICAL - Magenta

## Production Examples

### Example 1: LangGraph Agent with Logging

```python
from observability import setup_logging, get_logger, LogContext, log_execution
from utils import get_bedrock_client, retry_with_exponential_backoff
import json
import uuid

# Setup logging
setup_logging()
logger = get_logger(__name__)

@log_execution(level="INFO", include_duration=True)
@retry_with_exponential_backoff(max_attempts=3)
def invoke_agent(state: dict) -> dict:
    bedrock = get_bedrock_client()

    logger.info(
        "Invoking agent",
        extra={
            "message_count": len(state["messages"]),
            "has_context": bool(state.get("context"))
        }
    )

    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "messages": state["messages"]
        })
    )

    result = json.loads(response["body"].read())

    logger.info(
        "Agent response received",
        extra={
            "tokens_used": result.get("usage", {}).get("total_tokens", 0)
        }
    )

    return result

def process_query(query: str, user_id: str) -> dict:
    request_id = str(uuid.uuid4())

    with LogContext(request_id=request_id, user_id=user_id):
        logger.info("Query received", extra={"query": query})

        state = {
            "messages": [{"role": "user", "content": query}]
        }

        result = invoke_agent(state)

        logger.info("Query completed")

        return result
```

### Example 2: API with Request Tracking

```python
from fastapi import FastAPI, Request, HTTPException
from observability import setup_logging, get_logger, LogContext
import uuid
import time

app = FastAPI()

# Setup logging on startup
@app.on_event("startup")
async def startup():
    setup_logging()

logger = get_logger(__name__)

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()

    with LogContext(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host
    ):
        logger.info("Request started")

        try:
            response = await call_next(request)

            duration = time.time() - start_time

            logger.info(
                "Request completed",
                extra={
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2)
                }
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            duration = time.time() - start_time

            logger.error(
                f"Request failed: {e}",
                exc_info=True,
                extra={"duration_ms": round(duration * 1000, 2)}
            )

            raise

@app.post("/query")
async def handle_query(query: str, user_id: str):
    with LogContext(user_id=user_id):
        logger.info("Processing query", extra={"query_length": len(query)})

        result = process_query(query)

        logger.info("Query processed", extra={"result_length": len(result)})

        return {"result": result}
```

### Example 3: Background Task Logging

```python
from observability import get_logger, LogContext, log_execution, log_errors
import uuid

logger = get_logger(__name__)

@log_execution(level="INFO", include_duration=True)
@log_errors()
def process_batch(items: list) -> dict:
    batch_id = str(uuid.uuid4())

    with LogContext(batch_id=batch_id, batch_size=len(items)):
        logger.info("Batch processing started")

        results = []
        errors = []

        for i, item in enumerate(items):
            with LogContext(item_index=i, item_id=item.get("id")):
                try:
                    result = process_item(item)
                    results.append(result)
                    logger.debug("Item processed successfully")

                except Exception as e:
                    errors.append({"item": item, "error": str(e)})
                    logger.warning(f"Item processing failed: {e}")

        logger.info(
            "Batch processing completed",
            extra={
                "success_count": len(results),
                "error_count": len(errors)
            }
        )

        return {
            "batch_id": batch_id,
            "results": results,
            "errors": errors
        }
```

### Example 4: Multi-Service Tracing

```python
from observability import get_logger, LogContext
import uuid

logger = get_logger(__name__)

def process_request(request_data: dict):
    # Generate trace ID for distributed tracing
    trace_id = str(uuid.uuid4())

    with LogContext(trace_id=trace_id):
        logger.info("Request processing started")

        # Call service A
        with LogContext(service="service_a"):
            logger.info("Calling Service A")
            result_a = call_service_a(request_data)
            logger.info("Service A completed")

        # Call service B
        with LogContext(service="service_b"):
            logger.info("Calling Service B")
            result_b = call_service_b(result_a)
            logger.info("Service B completed")

        # Aggregate results
        logger.info("Aggregating results")
        final_result = aggregate(result_a, result_b)

        logger.info("Request processing completed")

        return final_result
```

## CloudWatch Integration

### Setup

Install CloudWatch handler:

```bash
pip install logging-cloudwatch
```

### Configuration

```python
from observability import setup_logging

setup_logging(
    enable_cloudwatch=True,
    cloudwatch_log_group="myapp-production",
    cloudwatch_log_stream=f"instance-{instance_id}"
)
```

### Environment Variables

```bash
# .env
LOG_LEVEL=INFO
ENABLE_CLOUDWATCH=true
CLOUDWATCH_LOG_GROUP=myapp-production
CLOUDWATCH_LOG_STREAM=instance-1
```

### Searching CloudWatch Logs

**By Request ID:**

```json
{ $.request_id = "req-abc123" }
```

**By User ID:**

```json
{ $.user_id = "user-456" }
```

**By Error:**

```json
{ $.level = "ERROR" }
```

**By Duration:**

```json
{ $.duration_ms > 1000 }
```

## Best Practices

### 1. Setup Logging Early

Setup logging at application startup:

```python
from observability import setup_logging

if __name__ == "__main__":
    setup_logging()
    # ... rest of app
```

### 2. Use Context for Request Tracking

Always use LogContext for request tracking:

```python
with LogContext(request_id=request_id, user_id=user_id):
    # All logs automatically include request_id and user_id
    process_request()
```

### 3. Log at Appropriate Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages (recoverable issues)
- **ERROR**: Error messages (something failed)
- **CRITICAL**: Critical issues (system unstable)

### 4. Include Useful Context

```python
logger.info(
    "Operation completed",
    extra={
        "duration_ms": duration,
        "items_processed": count,
        "success_rate": rate
    }
)
```

### 5. Don't Log Sensitive Data

```python
# Bad
logger.info(f"User logged in with password: {password}")

# Good
logger.info(f"User logged in", extra={"user_id": user_id})
```

### 6. Use Decorators for Consistency

```python
@log_execution(level="INFO")
@log_errors()
def important_function():
    # Automatically logged
    pass
```

## Testing

Run the test suite:

```bash
# Install dependencies
./setup-venv.sh

# Run tests
python test_logging.py
```

Tests cover:

- Logging setup
- JSON and console formatters
- LogContext management
- Decorators (sync and async)
- Error logging
- Real-world scenarios

## Summary

- **Structured logging** with JSON format for production
- **Request ID tracking** across all logs
- **Context management** with LogContext
- **Decorators** for automatic logging
- **Multiple outputs** (console, file, CloudWatch)
- **Environment-aware** configuration
- **Async support** for modern Python
- **Production-ready** with comprehensive testing

Use this logging system to build observable, debuggable applications!
