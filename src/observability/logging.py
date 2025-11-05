"""Centralized Logging Setup.

Provides structured logging with JSON formatting, context management, and CloudWatch integration.

This module provides:
- Structured logging with JSON format for production
- Different log levels per environment
- Request ID tracking across logs
- Context management (user, request, custom fields)
- Console and file output handlers
- Optional CloudWatch integration
- Logging decorators for functions

Example:
    >>> from observability.logging import setup_logging, get_logger, LogContext
    >>>
    >>> # Setup logging once at app startup
    >>> setup_logging()
    >>>
    >>> # Get logger for your module
    >>> logger = get_logger(__name__)
    >>>
    >>> # Add context to all subsequent logs
    >>> with LogContext(request_id="req-123", user_id="user-456"):
    ...     logger.info("Processing request")
    ...     # All logs in this block include request_id and user_id
"""

import asyncio
import contextvars
import functools
import json
import logging
import logging.handlers
import os
import sys
import time
import traceback
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TypeVar

# Context variables for request tracking
_log_context: contextvars.ContextVar[dict[str, Any]] = contextvars.ContextVar(
    "log_context", default={}
)

# Type variable for decorators
F = TypeVar("F", bound=Callable[..., Any])


class JsonFormatter(logging.Formatter):
    """JSON log formatter for structured logging.

    Formats log records as JSON with standardized fields including timestamp,
    level, message, and any additional context.

    Example output:
        {
            "timestamp": "2024-01-15T10:30:00.123456Z",
            "level": "INFO",
            "logger": "app.module",
            "message": "Request processed",
            "request_id": "req-123",
            "user_id": "user-456",
            "duration_ms": 150.5
        }
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: Log record to format

        Returns:
            JSON-formatted log string
        """
        # Build base log entry
        log_data = {
            "timestamp": self.format_timestamp(record.created),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add context from context variables
        context = _log_context.get()
        if context:
            log_data.update(context)

        # Add extra fields from record
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.format_exception(record.exc_info),
            }

        # Add source location
        log_data["source"] = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }

        # Add process/thread info
        log_data["process"] = {
            "pid": record.process,
            "thread": record.thread,
            "thread_name": record.threadName,
        }

        return json.dumps(log_data, default=str)

    @staticmethod
    def format_timestamp(timestamp: float) -> str:
        """Format timestamp in ISO 8601 format with UTC timezone.

        Args:
            timestamp: Unix timestamp

        Returns:
            ISO 8601 formatted timestamp string
        """
        dt = datetime.fromtimestamp(timestamp, tz=UTC)
        return dt.isoformat()

    @staticmethod
    def format_exception(exc_info: tuple) -> str:
        """Format exception traceback.

        Args:
            exc_info: Exception info tuple from sys.exc_info()

        Returns:
            Formatted traceback string
        """
        return "".join(traceback.format_exception(*exc_info))


class ConsoleFormatter(logging.Formatter):
    """Human-readable console formatter with colors.

    Formats logs for console output with colors and readable structure.
    """

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record for console.

        Args:
            record: Log record to format

        Returns:
            Formatted log string with colors
        """
        # Get color for level
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]

        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")

        # Build message
        parts = [
            f"{timestamp}",
            f"{color}{record.levelname:8}{reset}",
            f"[{record.name}]",
            record.getMessage(),
        ]

        # Add context if present
        context = _log_context.get()
        if context:
            context_str = " ".join(f"{k}={v}" for k, v in context.items())
            parts.append(f"({context_str})")

        message = " ".join(parts)

        # Add exception if present
        if record.exc_info:
            message += "\n" + self.formatException(record.exc_info)

        return message


class ContextLogger(logging.LoggerAdapter):
    """Logger adapter that includes context in all log messages.

    Automatically adds context from context variables to log records.
    """

    def process(self, msg: str, kwargs: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """Process log call to add context.

        Args:
            msg: Log message
            kwargs: Log kwargs

        Returns:
            Tuple of (message, kwargs) with added context
        """
        # Get current context
        context = _log_context.get()

        # Add context to extra fields
        if "extra" not in kwargs:
            kwargs["extra"] = {}

        # Store extra fields for JSON formatter
        extra_fields = kwargs["extra"].copy()
        extra_fields.update(context)
        kwargs["extra"]["extra_fields"] = extra_fields

        return msg, kwargs


class LogContext:
    """Context manager for adding context to all logs within a block.

    Context is stored in context variables and automatically included in all
    log messages within the context manager's scope.

    Example:
        >>> from observability.logging import get_logger, LogContext
        >>>
        >>> logger = get_logger(__name__)
        >>>
        >>> with LogContext(request_id="req-123", user_id="user-456"):
        ...     logger.info("Processing request")
        ...     # Log includes request_id and user_id
        ...
        ...     with LogContext(operation="validate"):
        ...         logger.info("Validating input")
        ...         # Log includes request_id, user_id, and operation
        ...
        ...     logger.info("Request complete")
        ...     # Log includes request_id and user_id (operation cleared)

    Example with API request:
        >>> from observability.logging import LogContext
        >>> import uuid
        >>>
        >>> @app.middleware("http")
        >>> async def log_requests(request: Request, call_next):
        ...     request_id = str(uuid.uuid4())
        ...
        ...     with LogContext(
        ...         request_id=request_id,
        ...         method=request.method,
        ...         path=request.url.path,
        ...         client_ip=request.client.host
        ...     ):
        ...         logger.info("Request started")
        ...         response = await call_next(request)
        ...         logger.info("Request completed",
        ...                    extra={"status_code": response.status_code})
        ...         return response
    """

    def __init__(self, **context: Any):
        """Initialize log context.

        Args:
            **context: Key-value pairs to add to log context
        """
        self.context = context
        self.token: contextvars.Token | None = None
        self.previous_context: dict[str, Any] = {}

    def __enter__(self) -> "LogContext":
        """Enter context manager and set context.

        Returns:
            Self for context manager protocol
        """
        # Get current context
        self.previous_context = _log_context.get().copy()

        # Merge new context with existing
        new_context = self.previous_context.copy()
        new_context.update(self.context)

        # Set new context
        self.token = _log_context.set(new_context)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and restore previous context.

        Args:
            exc_type: Exception type if raised
            exc_val: Exception value if raised
            exc_tb: Exception traceback if raised
        """
        # Restore previous context
        if self.token:
            _log_context.reset(self.token)

    @classmethod
    def current(cls) -> dict[str, Any]:
        """Get current log context.

        Returns:
            Current context dictionary
        """
        return _log_context.get().copy()

    @classmethod
    def clear(cls) -> None:
        """Clear all log context."""
        _log_context.set({})


def setup_logging(
    level: str | None = None,
    json_format: bool | None = None,
    log_file: str | None = None,
    enable_cloudwatch: bool | None = None,
    cloudwatch_log_group: str | None = None,
    cloudwatch_log_stream: str | None = None,
) -> None:
    """Setup centralized logging configuration.

    Configures logging based on settings with support for:
    - JSON formatting for production
    - Console output with colors for development
    - Optional file output
    - Optional CloudWatch integration

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
            If None, reads from settings or defaults to INFO.
        json_format: Use JSON formatting. If None, reads from settings
            (True for production, False for development).
        log_file: Path to log file. If None, reads from settings.
        enable_cloudwatch: Enable CloudWatch logging. If None, reads from settings.
        cloudwatch_log_group: CloudWatch log group name. If None, reads from settings.
        cloudwatch_log_stream: CloudWatch log stream name. If None, reads from settings.

    Example:
        >>> from observability.logging import setup_logging
        >>>
        >>> # Basic setup (uses settings)
        >>> setup_logging()
        >>>
        >>> # Custom setup
        >>> setup_logging(
        ...     level="DEBUG",
        ...     json_format=False,
        ...     log_file="/var/log/app.log"
        ... )

    Example with FastAPI:
        >>> from fastapi import FastAPI
        >>> from observability.logging import setup_logging, get_logger
        >>>
        >>> app = FastAPI()
        >>>
        >>> @app.on_event("startup")
        >>> async def startup_event():
        ...     setup_logging()
        ...     logger = get_logger(__name__)
        ...     logger.info("Application started")
    """
    # Import settings
    try:
        from config import get_settings

        settings = get_settings()
    except ImportError:
        settings = None

    # Determine log level
    if level is None:
        if settings:
            level = settings.observability.logging.level
        else:
            level = os.getenv("LOG_LEVEL", "INFO")

    # Determine format
    if json_format is None:
        if settings:
            json_format = settings.observability.logging.format == "json"
        else:
            json_format = os.getenv("ENVIRONMENT", "development") == "production"

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Create formatter
    if json_format:
        formatter = JsonFormatter()
    else:
        formatter = ConsoleFormatter()

    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Add file handler if specified
    if log_file is None and settings:
        log_file = settings.observability.logging.file_path

    if log_file:
        # Create log directory if needed
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Create rotating file handler (10MB max, 5 backups)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(JsonFormatter())  # Always use JSON for files
        root_logger.addHandler(file_handler)

    # Add CloudWatch handler if enabled
    if enable_cloudwatch is None and settings:
        enable_cloudwatch = settings.observability.logging.enable_cloudwatch

    if enable_cloudwatch:
        try:
            import boto3
            from logging_cloudwatch import CloudwatchHandler

            # Get CloudWatch settings
            if cloudwatch_log_group is None and settings:
                cloudwatch_log_group = settings.observability.logging.cloudwatch_log_group

            if cloudwatch_log_stream is None and settings:
                cloudwatch_log_stream = settings.observability.logging.cloudwatch_log_stream

            if cloudwatch_log_group and cloudwatch_log_stream:
                # Create CloudWatch handler
                cloudwatch_handler = CloudwatchHandler(
                    log_group=cloudwatch_log_group,
                    log_stream=cloudwatch_log_stream,
                    send_interval=5,  # Send logs every 5 seconds
                    max_batch_size=100,  # Max 100 logs per batch
                )
                cloudwatch_handler.setLevel(level)
                cloudwatch_handler.setFormatter(JsonFormatter())
                root_logger.addHandler(cloudwatch_handler)

                root_logger.info(
                    f"CloudWatch logging enabled: {cloudwatch_log_group}/{cloudwatch_log_stream}"
                )
        except ImportError:
            root_logger.warning(
                "CloudWatch logging requested but dependencies not installed. "
                "Install with: pip install logging-cloudwatch"
            )

    # Log setup completion
    root_logger.info(
        f"Logging configured: level={level}, format={'json' if json_format else 'console'}"
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger with context support.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger with context support

    Example:
        >>> from observability.logging import get_logger, LogContext
        >>>
        >>> logger = get_logger(__name__)
        >>>
        >>> logger.info("Simple log")
        >>>
        >>> with LogContext(user_id="user-123"):
        ...     logger.info("Log with context")
        ...     # Includes user_id in output

    Example with module structure:
        >>> # In app/services/user_service.py
        >>> from observability.logging import get_logger
        >>>
        >>> logger = get_logger(__name__)  # logger name: "app.services.user_service"
        >>>
        >>> def get_user(user_id: str):
        ...     logger.info(f"Fetching user: {user_id}")
        ...     # ... fetch user
        ...     logger.debug(f"User data: {user}")
        ...     return user
    """
    # Get base logger
    base_logger = logging.getLogger(name)

    # Wrap in ContextLogger for automatic context inclusion
    return ContextLogger(base_logger, {})


def log_execution(
    level: str = "INFO",
    include_args: bool = True,
    include_result: bool = False,
    include_duration: bool = True,
) -> Callable[[F], F]:
    """Decorator to log function execution.

    Logs function entry, exit, duration, and optionally arguments and results.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        include_args: Include function arguments in logs
        include_result: Include function result in logs
        include_duration: Include execution duration in logs

    Returns:
        Decorated function

    Example:
        >>> from observability.logging import log_execution, get_logger
        >>>
        >>> logger = get_logger(__name__)
        >>>
        >>> @log_execution(level="INFO", include_duration=True)
        >>> def process_data(data: dict):
        ...     # Process data
        ...     return result
        >>>
        >>> process_data({"key": "value"})
        >>> # Logs: "Executing process_data" and "process_data completed in 0.15s"

    Example with async function:
        >>> import asyncio
        >>>
        >>> @log_execution(level="DEBUG", include_args=True, include_result=True)
        >>> async def fetch_user(user_id: str):
        ...     await asyncio.sleep(0.1)
        ...     return {"id": user_id, "name": "John"}
        >>>
        >>> asyncio.run(fetch_user("user-123"))
        >>> # Logs args, result, and duration
    """
    log_level = getattr(logging, level.upper())

    def decorator(func: F) -> F:
        logger = get_logger(func.__module__)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Build context
            context = {"function": func.__name__}

            if include_args:
                context["function_args"] = args
                context["function_kwargs"] = kwargs

            # Log entry
            logger.log(log_level, f"Executing {func.__name__}", extra=context)

            # Execute function
            start_time = time.time()
            try:
                result = func(*args, **kwargs)

                # Calculate duration
                duration = time.time() - start_time

                # Build exit context
                exit_context = {"function": func.__name__}

                if include_duration:
                    exit_context["duration_ms"] = round(duration * 1000, 2)

                if include_result:
                    exit_context["result"] = result

                # Log completion
                logger.log(
                    log_level,
                    f"{func.__name__} completed successfully",
                    extra=exit_context,
                )

                return result

            except Exception:
                # Calculate duration
                duration = time.time() - start_time

                # Log error
                logger.error(
                    f"{func.__name__} failed after {duration:.2f}s",
                    exc_info=True,
                    extra={"function": func.__name__, "duration_ms": duration * 1000},
                )
                raise

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Build context
            context = {"function": func.__name__, "async": True}

            if include_args:
                context["function_args"] = args
                context["function_kwargs"] = kwargs

            # Log entry
            logger.log(log_level, f"Executing {func.__name__}", extra=context)

            # Execute function
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)

                # Calculate duration
                duration = time.time() - start_time

                # Build exit context
                exit_context = {"function": func.__name__, "async": True}

                if include_duration:
                    exit_context["duration_ms"] = round(duration * 1000, 2)

                if include_result:
                    exit_context["result"] = result

                # Log completion
                logger.log(
                    log_level,
                    f"{func.__name__} completed successfully",
                    extra=exit_context,
                )

                return result

            except Exception:
                # Calculate duration
                duration = time.time() - start_time

                # Log error
                logger.error(
                    f"{func.__name__} failed after {duration:.2f}s",
                    exc_info=True,
                    extra={"function": func.__name__, "duration_ms": duration * 1000},
                )
                raise

        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return sync_wrapper  # type: ignore

    return decorator


def log_errors(logger: logging.Logger | None = None) -> Callable[[F], F]:
    """Decorator to log errors with full context.

    Logs exceptions with traceback and context, then re-raises.

    Args:
        logger: Logger to use. If None, creates logger from function's module.

    Returns:
        Decorated function

    Example:
        >>> from observability.logging import log_errors, get_logger
        >>>
        >>> logger = get_logger(__name__)
        >>>
        >>> @log_errors(logger)
        >>> def risky_operation(value: int):
        ...     if value < 0:
        ...         raise ValueError("Value must be positive")
        ...     return value * 2
        >>>
        >>> risky_operation(-5)
        >>> # Logs error with full traceback, then raises exception

    Example without explicit logger:
        >>> @log_errors()
        >>> def process_file(path: str):
        ...     with open(path) as f:
        ...         return f.read()
        >>>
        >>> process_file("nonexistent.txt")
        >>> # Logs FileNotFoundError with traceback
    """

    def decorator(func: F) -> F:
        nonlocal logger
        if logger is None:
            logger = get_logger(func.__module__)

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Error in {func.__name__}: {e}",
                    exc_info=True,
                    extra={
                        "function": func.__name__,
                        "function_args": args,
                        "function_kwargs": kwargs,
                        "error_type": type(e).__name__,
                    },
                )
                raise

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Error in {func.__name__}: {e}",
                    exc_info=True,
                    extra={
                        "function": func.__name__,
                        "function_args": args,
                        "function_kwargs": kwargs,
                        "error_type": type(e).__name__,
                        "async": True,
                    },
                )
                raise

        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return sync_wrapper  # type: ignore

    return decorator


__all__ = [
    "setup_logging",
    "get_logger",
    "LogContext",
    "log_execution",
    "log_errors",
    "JsonFormatter",
    "ConsoleFormatter",
    "ContextLogger",
]
