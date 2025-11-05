"""Observability Module.

Provides monitoring, logging, tracing, and metrics collection for the system.

This module provides:
- Structured logging with JSON formatting
- Request ID tracking and context management
- Logging decorators for functions
- Prometheus metrics collection
- Counter, histogram, and gauge metrics
- Metrics decorators for tracking duration and errors
- Metrics endpoint for Prometheus scraping
- OpenTelemetry tracing integration (future)
- CloudWatch integration
- Distributed tracing across services (future)

Example:
    >>> from observability import (
    ...     setup_logging, get_logger, LogContext,
    ...     get_metrics_collector, track_duration
    ... )
    >>>
    >>> # Setup logging at app startup
    >>> setup_logging()
    >>>
    >>> # Get logger and metrics
    >>> logger = get_logger(__name__)
    >>> metrics = get_metrics_collector()
    >>>
    >>> # Use with context and metrics
    >>> with LogContext(request_id="req-123", user_id="user-456"):
    ...     logger.info("Processing request")
    ...     metrics.increment_counter("request_count",
    ...         labels={"endpoint": "/query"})
    ...
    ...     with metrics.track_duration("request_duration",
    ...             labels={"endpoint": "/query"}):
    ...         process_request()
"""

# Logging utilities
from .logging import (
    ConsoleFormatter,
    ContextLogger,
    JsonFormatter,
    LogContext,
    get_logger,
    log_errors,
    log_execution,
    setup_logging,
)

# Metrics utilities
from .metrics import (
    MetricsCollector,
    get_metrics_app,
    get_metrics_collector,
    get_metrics_text,
    track_duration,
    track_errors,
)

# Future imports will go here when modules are created
# Example:
# from .tracing import TracingManager
# from .metrics import MetricsCollector
# from .cloudwatch import CloudWatchLogger

__all__ = [
    # Logging
    "setup_logging",
    "get_logger",
    "LogContext",
    "log_execution",
    "log_errors",
    "JsonFormatter",
    "ConsoleFormatter",
    "ContextLogger",
    # Metrics
    "MetricsCollector",
    "get_metrics_collector",
    "track_duration",
    "track_errors",
    "get_metrics_app",
    "get_metrics_text",
    # Future exports will be added here
]
