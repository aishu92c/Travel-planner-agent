"""Metrics Collection Framework.

Provides Prometheus-based metrics collection for monitoring application performance.

This module provides:
- Counter metrics for tracking events (requests, errors, cache hits/misses)
- Histogram metrics for tracking distributions (durations, token usage)
- Gauge metrics for tracking current values (active requests, cache size)
- MetricsCollector class for unified metrics management
- Decorators for automatic metrics tracking
- Prometheus endpoint for metrics scraping

Example:
    >>> from observability.metrics import get_metrics_collector, track_duration
    >>>
    >>> # Get metrics collector
    >>> metrics = get_metrics_collector()
    >>>
    >>> # Track events
    >>> metrics.increment_counter("request_count", labels={"endpoint": "/query"})
    >>>
    >>> # Track duration
    >>> @track_duration("bedrock_call")
    >>> def invoke_bedrock(prompt: str):
    ...     return bedrock.invoke_model(...)
"""

import asyncio
import functools
import time
from collections.abc import Callable
from contextlib import contextmanager
from typing import Any, TypeVar

from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
    make_asgi_app,
)

# Type variable for decorators
F = TypeVar("F", bound=Callable[..., Any])

# Default registry for all metrics
DEFAULT_REGISTRY = CollectorRegistry()

# Define all metrics

# ============================================================================
# COUNTER METRICS
# ============================================================================

REQUEST_COUNTER = Counter(
    "request_count",
    "Total number of requests",
    ["endpoint", "method", "status"],
    registry=DEFAULT_REGISTRY,
)

ERROR_COUNTER = Counter(
    "error_count",
    "Total number of errors",
    ["error_type", "endpoint", "function"],
    registry=DEFAULT_REGISTRY,
)

CACHE_HITS_COUNTER = Counter(
    "cache_hits",
    "Total number of cache hits",
    ["cache_name", "operation"],
    registry=DEFAULT_REGISTRY,
)

CACHE_MISSES_COUNTER = Counter(
    "cache_misses",
    "Total number of cache misses",
    ["cache_name", "operation"],
    registry=DEFAULT_REGISTRY,
)

BEDROCK_INVOCATIONS_COUNTER = Counter(
    "bedrock_invocations",
    "Total number of Bedrock model invocations",
    ["model_id", "status"],
    registry=DEFAULT_REGISTRY,
)

RAG_QUERIES_COUNTER = Counter(
    "rag_queries",
    "Total number of RAG queries",
    ["operation", "status"],
    registry=DEFAULT_REGISTRY,
)

# ============================================================================
# HISTOGRAM METRICS
# ============================================================================

REQUEST_DURATION = Histogram(
    "request_duration_seconds",
    "Request duration in seconds",
    ["endpoint", "method"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=DEFAULT_REGISTRY,
)

TOKEN_USAGE = Histogram(
    "token_usage",
    "Token usage per request",
    ["model_id", "token_type"],
    buckets=(10, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000),
    registry=DEFAULT_REGISTRY,
)

RETRIEVAL_TIME = Histogram(
    "retrieval_time_seconds",
    "Time taken for retrieval operations in seconds",
    ["operation", "source"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
    registry=DEFAULT_REGISTRY,
)

BEDROCK_DURATION = Histogram(
    "bedrock_duration_seconds",
    "Bedrock invocation duration in seconds",
    ["model_id"],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0),
    registry=DEFAULT_REGISTRY,
)

DATABASE_QUERY_DURATION = Histogram(
    "database_query_duration_seconds",
    "Database query duration in seconds",
    ["operation", "table"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
    registry=DEFAULT_REGISTRY,
)

# ============================================================================
# GAUGE METRICS
# ============================================================================

ACTIVE_REQUESTS = Gauge(
    "active_requests",
    "Number of currently active requests",
    ["endpoint"],
    registry=DEFAULT_REGISTRY,
)

CACHE_SIZE = Gauge(
    "cache_size_bytes",
    "Current cache size in bytes",
    ["cache_name"],
    registry=DEFAULT_REGISTRY,
)

ACTIVE_CONNECTIONS = Gauge(
    "active_connections",
    "Number of active connections",
    ["connection_type"],
    registry=DEFAULT_REGISTRY,
)

MEMORY_USAGE = Gauge(
    "memory_usage_bytes",
    "Current memory usage in bytes",
    ["process"],
    registry=DEFAULT_REGISTRY,
)

QUEUE_SIZE = Gauge(
    "queue_size",
    "Current queue size",
    ["queue_name"],
    registry=DEFAULT_REGISTRY,
)


class MetricsCollector:
    """Unified metrics collector for application monitoring.

    Provides a centralized interface for collecting metrics using Prometheus.
    Supports counters, histograms, and gauges with labels.

    Example:
        >>> from observability.metrics import get_metrics_collector
        >>>
        >>> metrics = get_metrics_collector()
        >>>
        >>> # Increment counter
        >>> metrics.increment_counter("request_count",
        ...     labels={"endpoint": "/query", "method": "POST", "status": "200"})
        >>>
        >>> # Record histogram value
        >>> metrics.record_histogram("request_duration",
        ...     value=0.5, labels={"endpoint": "/query", "method": "POST"})
        >>>
        >>> # Set gauge value
        >>> metrics.set_gauge("active_requests", value=10, labels={"endpoint": "/query"})

    Example with context manager:
        >>> with metrics.track_duration("database_query",
        ...         labels={"operation": "select", "table": "users"}):
        ...     # Query executes here
        ...     result = db.query("SELECT * FROM users")
    """

    def __init__(self, registry: CollectorRegistry | None = None):
        """Initialize metrics collector.

        Args:
            registry: Prometheus registry. If None, uses default registry.
        """
        self.registry = registry or DEFAULT_REGISTRY

    def increment_counter(
        self, name: str, value: float = 1, labels: dict[str, str] | None = None
    ) -> None:
        """Increment a counter metric.

        Args:
            name: Counter name
            value: Amount to increment by (default: 1)
            labels: Label dictionary for the metric

        Example:
            >>> metrics = get_metrics_collector()
            >>>
            >>> # Simple increment
            >>> metrics.increment_counter("request_count")
            >>>
            >>> # Increment with labels
            >>> metrics.increment_counter("request_count",
            ...     labels={"endpoint": "/query", "method": "POST", "status": "200"})
            >>>
            >>> # Increment by custom amount
            >>> metrics.increment_counter("bytes_processed", value=1024,
            ...     labels={"operation": "upload"})
        """
        labels = labels or {}

        if name == "request_count":
            REQUEST_COUNTER.labels(**labels).inc(value)
        elif name == "error_count":
            ERROR_COUNTER.labels(**labels).inc(value)
        elif name == "cache_hits":
            CACHE_HITS_COUNTER.labels(**labels).inc(value)
        elif name == "cache_misses":
            CACHE_MISSES_COUNTER.labels(**labels).inc(value)
        elif name == "bedrock_invocations":
            BEDROCK_INVOCATIONS_COUNTER.labels(**labels).inc(value)
        elif name == "rag_queries":
            RAG_QUERIES_COUNTER.labels(**labels).inc(value)
        else:
            raise ValueError(f"Unknown counter metric: {name}")

    def record_histogram(
        self, name: str, value: float, labels: dict[str, str] | None = None
    ) -> None:
        """Record a value in a histogram metric.

        Args:
            name: Histogram name
            value: Value to record
            labels: Label dictionary for the metric

        Example:
            >>> metrics = get_metrics_collector()
            >>>
            >>> # Record request duration
            >>> metrics.record_histogram("request_duration",
            ...     value=0.5, labels={"endpoint": "/query", "method": "POST"})
            >>>
            >>> # Record token usage
            >>> metrics.record_histogram("token_usage",
            ...     value=1500, labels={"model_id": "claude-3", "token_type": "total"})
            >>>
            >>> # Record retrieval time
            >>> metrics.record_histogram("retrieval_time",
            ...     value=0.05, labels={"operation": "vector_search", "source": "chroma"})
        """
        labels = labels or {}

        if name == "request_duration":
            REQUEST_DURATION.labels(**labels).observe(value)
        elif name == "token_usage":
            TOKEN_USAGE.labels(**labels).observe(value)
        elif name == "retrieval_time":
            RETRIEVAL_TIME.labels(**labels).observe(value)
        elif name == "bedrock_duration":
            BEDROCK_DURATION.labels(**labels).observe(value)
        elif name == "database_query_duration":
            DATABASE_QUERY_DURATION.labels(**labels).observe(value)
        else:
            raise ValueError(f"Unknown histogram metric: {name}")

    def set_gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """Set a gauge metric to a specific value.

        Args:
            name: Gauge name
            value: Value to set
            labels: Label dictionary for the metric

        Example:
            >>> metrics = get_metrics_collector()
            >>>
            >>> # Set active requests
            >>> metrics.set_gauge("active_requests",
            ...     value=10, labels={"endpoint": "/query"})
            >>>
            >>> # Set cache size
            >>> metrics.set_gauge("cache_size",
            ...     value=1024*1024*100, labels={"cache_name": "embeddings"})
            >>>
            >>> # Set active connections
            >>> metrics.set_gauge("active_connections",
            ...     value=50, labels={"connection_type": "database"})
        """
        labels = labels or {}

        if name == "active_requests":
            ACTIVE_REQUESTS.labels(**labels).set(value)
        elif name == "cache_size":
            CACHE_SIZE.labels(**labels).set(value)
        elif name == "active_connections":
            ACTIVE_CONNECTIONS.labels(**labels).set(value)
        elif name == "memory_usage":
            MEMORY_USAGE.labels(**labels).set(value)
        elif name == "queue_size":
            QUEUE_SIZE.labels(**labels).set(value)
        else:
            raise ValueError(f"Unknown gauge metric: {name}")

    def increment_gauge(
        self, name: str, value: float = 1, labels: dict[str, str] | None = None
    ) -> None:
        """Increment a gauge metric.

        Args:
            name: Gauge name
            value: Amount to increment by (default: 1)
            labels: Label dictionary for the metric

        Example:
            >>> metrics = get_metrics_collector()
            >>>
            >>> # Increment active requests
            >>> metrics.increment_gauge("active_requests",
            ...     labels={"endpoint": "/query"})
            >>>
            >>> # Increment queue size
            >>> metrics.increment_gauge("queue_size", value=5,
            ...     labels={"queue_name": "processing"})
        """
        labels = labels or {}

        if name == "active_requests":
            ACTIVE_REQUESTS.labels(**labels).inc(value)
        elif name == "cache_size":
            CACHE_SIZE.labels(**labels).inc(value)
        elif name == "active_connections":
            ACTIVE_CONNECTIONS.labels(**labels).inc(value)
        elif name == "memory_usage":
            MEMORY_USAGE.labels(**labels).inc(value)
        elif name == "queue_size":
            QUEUE_SIZE.labels(**labels).inc(value)
        else:
            raise ValueError(f"Unknown gauge metric: {name}")

    def decrement_gauge(
        self, name: str, value: float = 1, labels: dict[str, str] | None = None
    ) -> None:
        """Decrement a gauge metric.

        Args:
            name: Gauge name
            value: Amount to decrement by (default: 1)
            labels: Label dictionary for the metric

        Example:
            >>> metrics = get_metrics_collector()
            >>>
            >>> # Decrement active requests
            >>> metrics.decrement_gauge("active_requests",
            ...     labels={"endpoint": "/query"})
            >>>
            >>> # Decrement queue size
            >>> metrics.decrement_gauge("queue_size", value=3,
            ...     labels={"queue_name": "processing"})
        """
        labels = labels or {}

        if name == "active_requests":
            ACTIVE_REQUESTS.labels(**labels).dec(value)
        elif name == "cache_size":
            CACHE_SIZE.labels(**labels).dec(value)
        elif name == "active_connections":
            ACTIVE_CONNECTIONS.labels(**labels).dec(value)
        elif name == "memory_usage":
            MEMORY_USAGE.labels(**labels).dec(value)
        elif name == "queue_size":
            QUEUE_SIZE.labels(**labels).dec(value)
        else:
            raise ValueError(f"Unknown gauge metric: {name}")

    @contextmanager
    def track_duration(self, name: str, labels: dict[str, str] | None = None):
        """Context manager for tracking operation duration.

        Args:
            name: Histogram name
            labels: Label dictionary for the metric

        Yields:
            None

        Example:
            >>> metrics = get_metrics_collector()
            >>>
            >>> # Track database query
            >>> with metrics.track_duration("database_query_duration",
            ...         labels={"operation": "select", "table": "users"}):
            ...     result = db.query("SELECT * FROM users")
            >>>
            >>> # Track Bedrock call
            >>> with metrics.track_duration("bedrock_duration",
            ...         labels={"model_id": "claude-3"}):
            ...     response = bedrock.invoke_model(...)
        """
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.record_histogram(name, duration, labels)

    @contextmanager
    def track_active(self, name: str, labels: dict[str, str] | None = None):
        """Context manager for tracking active operations.

        Increments gauge on entry, decrements on exit.

        Args:
            name: Gauge name
            labels: Label dictionary for the metric

        Yields:
            None

        Example:
            >>> metrics = get_metrics_collector()
            >>>
            >>> # Track active requests
            >>> with metrics.track_active("active_requests",
            ...         labels={"endpoint": "/query"}):
            ...     process_request()
            >>>
            >>> # Track active connections
            >>> with metrics.track_active("active_connections",
            ...         labels={"connection_type": "database"}):
            ...     with db.connection() as conn:
            ...         conn.query(...)
        """
        self.increment_gauge(name, labels=labels)
        try:
            yield
        finally:
            self.decrement_gauge(name, labels=labels)


# Global metrics collector instance
_metrics_collector: MetricsCollector | None = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance.

    Returns:
        Global MetricsCollector instance

    Example:
        >>> from observability.metrics import get_metrics_collector
        >>>
        >>> metrics = get_metrics_collector()
        >>> metrics.increment_counter("request_count")
    """
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def track_duration(metric_name: str, labels: dict[str, str] | None = None) -> Callable[[F], F]:
    """Decorator to automatically track function execution duration.

    Args:
        metric_name: Name of the histogram metric
        labels: Optional labels for the metric

    Returns:
        Decorated function

    Example:
        >>> from observability.metrics import track_duration
        >>>
        >>> @track_duration("bedrock_duration", labels={"model_id": "claude-3"})
        >>> def invoke_bedrock(prompt: str):
        ...     bedrock = get_bedrock_client()
        ...     return bedrock.invoke_model(...)
        >>>
        >>> invoke_bedrock("Hello")
        >>> # Duration automatically recorded

    Example with dynamic labels:
        >>> @track_duration("database_query_duration")
        >>> def query_users(table: str):
        ...     # Labels can be added at runtime
        ...     return db.query(f"SELECT * FROM {table}")

    Example with async:
        >>> @track_duration("api_call_duration", labels={"service": "external"})
        >>> async def fetch_data(url: str):
        ...     async with aiohttp.ClientSession() as session:
        ...         async with session.get(url) as response:
        ...             return await response.json()
    """
    labels = labels or {}
    metrics = get_metrics_collector()

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            with metrics.track_duration(metric_name, labels):
                return func(*args, **kwargs)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            with metrics.track_duration(metric_name, labels):
                return await func(*args, **kwargs)

        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return sync_wrapper  # type: ignore

    return decorator


def track_errors(
    counter_name: str = "error_count", labels: dict[str, str] | None = None
) -> Callable[[F], F]:
    """Decorator to automatically track function errors.

    Args:
        counter_name: Name of the counter metric (default: "error_count")
        labels: Optional labels for the metric

    Returns:
        Decorated function

    Example:
        >>> from observability.metrics import track_errors
        >>>
        >>> @track_errors(labels={"function": "process_data"})
        >>> def process_data(data: dict):
        ...     if not data:
        ...         raise ValueError("Data cannot be empty")
        ...     return process(data)
        >>>
        >>> try:
        ...     process_data({})
        ... except ValueError:
        ...     pass  # Error automatically counted
    """
    labels = labels or {}
    metrics = get_metrics_collector()

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_labels = labels.copy()
                error_labels["error_type"] = type(e).__name__
                error_labels["function"] = func.__name__
                metrics.increment_counter(counter_name, labels=error_labels)
                raise

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_labels = labels.copy()
                error_labels["error_type"] = type(e).__name__
                error_labels["function"] = func.__name__
                metrics.increment_counter(counter_name, labels=error_labels)
                raise

        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return sync_wrapper  # type: ignore

    return decorator


def get_metrics_app():
    """Get ASGI app for Prometheus metrics endpoint.

    Returns:
        ASGI app for serving metrics

    Example with FastAPI:
        >>> from fastapi import FastAPI
        >>> from observability.metrics import get_metrics_app
        >>>
        >>> app = FastAPI()
        >>>
        >>> # Mount metrics endpoint
        >>> app.mount("/metrics", get_metrics_app())
        >>>
        >>> # Metrics available at http://localhost:8000/metrics

    Example with Starlette:
        >>> from starlette.applications import Starlette
        >>> from starlette.routing import Mount
        >>> from observability.metrics import get_metrics_app
        >>>
        >>> app = Starlette(routes=[
        ...     Mount("/metrics", app=get_metrics_app())
        ... ])
    """
    return make_asgi_app(registry=DEFAULT_REGISTRY)


def get_metrics_text() -> bytes:
    """Get metrics in Prometheus text format.

    Returns:
        Metrics in Prometheus exposition format

    Example:
        >>> from observability.metrics import get_metrics_text
        >>>
        >>> # Get current metrics
        >>> metrics = get_metrics_text()
        >>> print(metrics.decode())
        # HELP request_count Total number of requests
        # TYPE request_count counter
        request_count{endpoint="/query",method="POST",status="200"} 150.0
        ...
    """
    return generate_latest(DEFAULT_REGISTRY)


__all__ = [
    "MetricsCollector",
    "get_metrics_collector",
    "track_duration",
    "track_errors",
    "get_metrics_app",
    "get_metrics_text",
    # Metric names for reference
    "REQUEST_COUNTER",
    "ERROR_COUNTER",
    "CACHE_HITS_COUNTER",
    "CACHE_MISSES_COUNTER",
    "REQUEST_DURATION",
    "TOKEN_USAGE",
    "RETRIEVAL_TIME",
    "ACTIVE_REQUESTS",
    "CACHE_SIZE",
]
