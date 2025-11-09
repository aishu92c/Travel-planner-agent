# Metrics Collection Framework

Production-ready Prometheus metrics collection for monitoring application
performance and health.

## Overview

The metrics system (`src/observability/metrics.py`) provides:

- **Counter Metrics** - Track events (requests, errors, cache hits/misses)
- **Histogram Metrics** - Track distributions (durations, token usage)
- **Gauge Metrics** - Track current values (active requests, cache size)
- **MetricsCollector Class** - Unified interface for all metrics
- **Decorators** - Automatic tracking for functions
- **Prometheus Integration** - Standard Prometheus exposition format
- **ASGI Endpoint** - `/metrics` endpoint for Prometheus scraping

## Quick Start

```python
from observability import get_metrics_collector, track_duration

# Get metrics collector
metrics = get_metrics_collector()

# Track events
metrics.increment_counter("request_count",
    labels={"endpoint": "/query", "method": "POST", "status": "200"})

# Track duration
with metrics.track_duration("request_duration",
        labels={"endpoint": "/query", "method": "POST"}):
    process_request()

# Use decorator
@track_duration("bedrock_duration", labels={"model_id": "claude-3"})
def invoke_bedrock(prompt: str):
    return bedrock.invoke_model(...)
```

## Installation

Install prometheus_client:

```bash
pip install prometheus-client
```

Or add to `requirements.txt`:

```text
prometheus-client>=0.19.0
```

## Metrics Types

### Counter Metrics

Counters only increase (never decrease).

**Available Counters:**

- `request_count` - Total requests (labels: endpoint, method, status)
- `error_count` - Total errors (labels: error_type, endpoint, function)
- `cache_hits` - Cache hits (labels: cache_name, operation)
- `cache_misses` - Cache misses (labels: cache_name, operation)
- `bedrock_invocations` - Bedrock calls (labels: model_id, status)
- `rag_queries` - RAG queries (labels: operation, status)

**Example:**

```python
from observability import get_metrics_collector

metrics = get_metrics_collector()

# Increment by 1 (default)
metrics.increment_counter("request_count",
    labels={"endpoint": "/query", "method": "POST", "status": "200"})

# Increment by custom amount
metrics.increment_counter("cache_hits", value=5,
    labels={"cache_name": "embeddings", "operation": "get"})
```

### Histogram Metrics

Histograms track the distribution of values (useful for latencies, sizes).

**Available Histograms:**

- `request_duration` - Request duration in seconds (labels: endpoint, method)
- `token_usage` - Tokens per request (labels: model_id, token_type)
- `retrieval_time` - Retrieval time in seconds (labels: operation, source)
- `bedrock_duration` - Bedrock call duration (labels: model_id)
- `database_query_duration` - DB query duration (labels: operation, table)

**Buckets:**

- Request duration: 5ms to 10s
- Token usage: 10 to 50,000 tokens
- Retrieval time: 1ms to 5s
- Bedrock duration: 100ms to 30s
- Database duration: 1ms to 1s

**Example:**

```python
import time

start = time.time()
process_request()
duration = time.time() - start

metrics.record_histogram("request_duration", value=duration,
    labels={"endpoint": "/query", "method": "POST"})
```

### Gauge Metrics

Gauges can increase or decrease (current values).

**Available Gauges:**

- `active_requests` - Current active requests (labels: endpoint)
- `cache_size` - Cache size in bytes (labels: cache_name)
- `active_connections` - Active connections (labels: connection_type)
- `memory_usage` - Memory usage in bytes (labels: process)
- `queue_size` - Queue size (labels: queue_name)

**Example:**

```python
# Set absolute value
metrics.set_gauge("cache_size", value=1024*1024*100,
    labels={"cache_name": "embeddings"})

# Increment
metrics.increment_gauge("active_requests",
    labels={"endpoint": "/query"})

# Decrement
metrics.decrement_gauge("active_requests",
    labels={"endpoint": "/query"})
```

## MetricsCollector Class

Unified interface for collecting metrics.

### Methods

**`increment_counter(name, value=1, labels=None)`**

```python
metrics.increment_counter("request_count",
    labels={"endpoint": "/query", "method": "POST", "status": "200"})
```

**`record_histogram(name, value, labels=None)`**

```python
metrics.record_histogram("request_duration", value=0.5,
    labels={"endpoint": "/query", "method": "POST"})
```

**`set_gauge(name, value, labels=None)`**

```python
metrics.set_gauge("active_requests", value=10,
    labels={"endpoint": "/query"})
```

**`increment_gauge(name, value=1, labels=None)`**

```python
metrics.increment_gauge("active_requests",
    labels={"endpoint": "/query"})
```

**`decrement_gauge(name, value=1, labels=None)`**

```python
metrics.decrement_gauge("active_requests",
    labels={"endpoint": "/query"})
```

### Context Managers

**`track_duration(name, labels=None)`**

Track duration of a code block:

```python
with metrics.track_duration("database_query_duration",
        labels={"operation": "select", "table": "users"}):
    result = db.query("SELECT * FROM users")
```

**`track_active(name, labels=None)`**

Track active operations (increments on entry, decrements on exit):

```python
with metrics.track_active("active_requests",
        labels={"endpoint": "/query"}):
    process_request()
```

## Decorators

### `@track_duration`

Automatically track function execution time:

```python
from observability import track_duration

@track_duration("bedrock_duration", labels={"model_id": "claude-3"})
def invoke_bedrock(prompt: str):
    bedrock = get_bedrock_client()
    return bedrock.invoke_model(...)

invoke_bedrock("Hello")
# Duration automatically recorded
```

**Async Support:**

```python
@track_duration("api_call_duration", labels={"service": "external"})
async def fetch_data(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

### `@track_errors`

Automatically track errors:

```python
from observability import track_errors

@track_errors(labels={"endpoint": "/query"})
def process_query(query: str):
    if not query:
        raise ValueError("Query cannot be empty")
    return process(query)

try:
    process_query("")
except ValueError:
    pass  # Error automatically counted
```

**Combined Decorators:**

```python
@track_duration("request_duration", labels={"endpoint": "/query"})
@track_errors(labels={"endpoint": "/query"})
def handle_request(data: dict):
    # Both duration and errors tracked
    return process(data)
```

## Prometheus Endpoint

### FastAPI Integration

```python
from fastapi import FastAPI
from observability import get_metrics_app, get_metrics_collector

app = FastAPI()

# Mount metrics endpoint
app.mount("/metrics", get_metrics_app())

# Use metrics in endpoints
metrics = get_metrics_collector()

@app.get("/health")
def health():
    metrics.increment_counter("request_count",
        labels={"endpoint": "/health", "method": "GET", "status": "200"})
    return {"status": "healthy"}
```

**Access metrics:** `http://localhost:8000/metrics`

### Starlette Integration

```python
from starlette.applications import Starlette
from starlette.routing import Mount
from observability import get_metrics_app

app = Starlette(routes=[
    Mount("/metrics", app=get_metrics_app())
])
```

### Get Metrics Text

For custom integrations:

```python
from observability import get_metrics_text

metrics = get_metrics_text()
print(metrics.decode())

# Output:
# # HELP request_count Total number of requests
# # TYPE request_count counter
# request_count{endpoint="/query",method="POST",status="200"} 150.0
# ...
```

## Production Examples

### Example 1: API Request Tracking

```python
from fastapi import FastAPI, Request
from observability import get_metrics_collector, track_duration
import time

app = FastAPI()
metrics = get_metrics_collector()

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    # Track active requests
    endpoint = request.url.path
    with metrics.track_active("active_requests", labels={"endpoint": endpoint}):
        # Track duration
        start_time = time.time()

        try:
            response = await call_next(request)

            # Track request
            metrics.increment_counter("request_count",
                labels={
                    "endpoint": endpoint,
                    "method": request.method,
                    "status": str(response.status_code)
                })

            # Record duration
            duration = time.time() - start_time
            metrics.record_histogram("request_duration",
                value=duration,
                labels={"endpoint": endpoint, "method": request.method})

            return response

        except Exception as e:
            # Track error
            metrics.increment_counter("error_count",
                labels={
                    "error_type": type(e).__name__,
                    "endpoint": endpoint,
                    "function": "middleware"
                })
            raise
```

### Example 2: Bedrock Metrics

```python
from observability import get_metrics_collector, track_duration, track_errors
from utils import get_bedrock_client
import json
import time

metrics = get_metrics_collector()

@track_duration("bedrock_duration", labels={"model_id": "claude-3"})
@track_errors(labels={"function": "invoke_bedrock"})
def invoke_bedrock(prompt: str) -> dict:
    # Track invocation start
    metrics.increment_counter("bedrock_invocations",
        labels={"model_id": "claude-3", "status": "started"})

    bedrock = get_bedrock_client()

    try:
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            })
        )

        result = json.loads(response["body"].read())

        # Track token usage
        usage = result.get("usage", {})
        metrics.record_histogram("token_usage",
            value=usage.get("input_tokens", 0),
            labels={"model_id": "claude-3", "token_type": "input"})
        metrics.record_histogram("token_usage",
            value=usage.get("output_tokens", 0),
            labels={"model_id": "claude-3", "token_type": "output"})
        metrics.record_histogram("token_usage",
            value=usage.get("total_tokens", 0),
            labels={"model_id": "claude-3", "token_type": "total"})

        # Track successful invocation
        metrics.increment_counter("bedrock_invocations",
            labels={"model_id": "claude-3", "status": "success"})

        return result

    except Exception as e:
        # Track failed invocation
        metrics.increment_counter("bedrock_invocations",
            labels={"model_id": "claude-3", "status": "failed"})
        raise
```

### Example 3: Cache Metrics

```python
from observability import get_metrics_collector
from typing import Optional, Any
import hashlib

metrics = get_metrics_collector()

class CacheWithMetrics:
    def __init__(self, name: str):
        self.name = name
        self.cache = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            # Track cache hit
            metrics.increment_counter("cache_hits",
                labels={"cache_name": self.name, "operation": "get"})
            return self.cache[key]
        else:
            # Track cache miss
            metrics.increment_counter("cache_misses",
                labels={"cache_name": self.name, "operation": "get"})
            return None

    def set(self, key: str, value: Any):
        self.cache[key] = value

        # Update cache size
        size_bytes = sum(
            len(str(k)) + len(str(v))
            for k, v in self.cache.items()
        )
        metrics.set_gauge("cache_size",
            value=size_bytes,
            labels={"cache_name": self.name})

    def clear(self):
        self.cache.clear()
        metrics.set_gauge("cache_size", value=0,
            labels={"cache_name": self.name})

# Usage
cache = CacheWithMetrics("embeddings")
result = cache.get("key1")  # Cache miss recorded
cache.set("key1", "value1")  # Cache size updated
result = cache.get("key1")   # Cache hit recorded
```

### Example 4: RAG Metrics

```python
from observability import get_metrics_collector, track_duration

metrics = get_metrics_collector()

@track_duration("retrieval_time",
    labels={"operation": "vector_search", "source": "chroma"})
def vector_search(query: str, top_k: int = 5):
    # Track query
    metrics.increment_counter("rag_queries",
        labels={"operation": "vector_search", "status": "started"})

    try:
        # Perform search
        results = vector_db.search(query, top_k=top_k)

        # Track success
        metrics.increment_counter("rag_queries",
            labels={"operation": "vector_search", "status": "success"})

        return results

    except Exception as e:
        # Track failure
        metrics.increment_counter("rag_queries",
            labels={"operation": "vector_search", "status": "failed"})
        raise
```

### Example 5: Database Metrics

```python
from observability import get_metrics_collector
from contextlib import contextmanager

metrics = get_metrics_collector()

@contextmanager
def database_connection(pool):
    # Track active connections
    with metrics.track_active("active_connections",
            labels={"connection_type": "database"}):
        conn = pool.get_connection()
        try:
            yield conn
        finally:
            pool.return_connection(conn)

def query_users(user_id: str):
    with database_connection(db_pool) as conn:
        # Track query duration
        with metrics.track_duration("database_query_duration",
                labels={"operation": "select", "table": "users"}):
            result = conn.query(
                "SELECT * FROM users WHERE id = ?",
                (user_id,)
            )
            return result
```

## Prometheus Configuration

### prometheus.yml

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'langgraph-app'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s
```

### Common Queries

**Request Rate:**

```promql
rate(request_count[5m])
```

**Error Rate:**

```promql
rate(error_count[5m]) / rate(request_count[5m])
```

**95th Percentile Latency:**

```promql
histogram_quantile(0.95, rate(request_duration_seconds_bucket[5m]))
```

**Average Token Usage:**

```promql
rate(token_usage_sum[5m]) / rate(token_usage_count[5m])
```

**Cache Hit Rate:**

```promql
rate(cache_hits[5m]) / (rate(cache_hits[5m]) + rate(cache_misses[5m]))
```

**Active Requests:**

```promql
active_requests
```

## Grafana Dashboards

### Key Metrics Dashboard

**Panels:**

1. Request Rate (QPS)
2. Error Rate (%)
3. P50/P95/P99 Latency
4. Active Requests
5. Token Usage (avg/max)
6. Cache Hit Rate (%)
7. Bedrock Invocations
8. Database Query Time

### Example Panel (Request Rate)

```json
{
  "title": "Request Rate",
  "targets": [{
    "expr": "rate(request_count[5m])",
    "legendFormat": "{{endpoint}} - {{method}}"
  }],
  "type": "graph"
}
```

## Best Practices

### 1. Use Descriptive Labels

```python
# Good
metrics.increment_counter("request_count",
    labels={"endpoint": "/query", "method": "POST", "status": "200"})

# Bad
metrics.increment_counter("request_count")
```

### 2. Keep Label Cardinality Low

```python
# Good - limited values
labels={"endpoint": "/query", "method": "POST"}

# Bad - unlimited values (user_id changes constantly)
labels={"endpoint": "/query", "user_id": "user-123-456-789"}
```

### 3. Track Both Success and Failure

```python
try:
    result = process()
    metrics.increment_counter("operations",
        labels={"operation": "process", "status": "success"})
except Exception:
    metrics.increment_counter("operations",
        labels={"operation": "process", "status": "failed"})
    raise
```

### 4. Use Context Managers for Active Tracking

```python
# Automatic increment/decrement
with metrics.track_active("active_requests", labels={"endpoint": "/query"}):
    process_request()
```

### 5. Combine with Logging

```python
from observability import get_logger, get_metrics_collector

logger = get_logger(__name__)
metrics = get_metrics_collector()

def process_request():
    metrics.increment_counter("request_count")
    logger.info("Processing request")
    # ... process
```

## Testing

Run the test suite:

```bash
# Install dependencies
pip install prometheus-client
./setup-venv.sh

# Run tests
python test_metrics.py
```

Tests cover:

- All metric types (counter, histogram, gauge)
- MetricsCollector methods
- Context managers
- Decorators (sync and async)
- Error handling
- Real-world scenarios

## Summary

- **Counter metrics** for tracking events
- **Histogram metrics** for tracking distributions
- **Gauge metrics** for current values
- **MetricsCollector** unified interface
- **Decorators** for automatic tracking
- **Context managers** for scoped tracking
- **Prometheus endpoint** for scraping
- **Full async support**
- **Production-ready** with comprehensive examples

Use this metrics system to monitor your application's performance, track
errors, and gain insights into system behavior!
