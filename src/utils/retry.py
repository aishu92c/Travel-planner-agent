"""Retry Utilities.

Provides robust retry decorators with exponential backoff for handling transient failures.

This module provides:
- Synchronous retry decorator with exponential backoff
- Asynchronous retry decorator with exponential backoff
- Specialized retry for API rate limits
- Configurable backoff strategies
- Comprehensive logging

Example:
    >>> from utils.retry import retry_with_exponential_backoff
    >>> @retry_with_exponential_backoff(max_attempts=3)
    >>> def call_api():
    ...     return api.get_data()
"""

import asyncio
import functools
import logging
import random
import time
from collections.abc import Callable
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

# Type variables for decorators
F = TypeVar("F", bound=Callable[..., Any])
AsyncF = TypeVar("AsyncF", bound=Callable[..., Any])


def retry_with_exponential_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    on_retry: Callable[[Exception, int], None] | None = None,
) -> Callable[[F], F]:
    """Retry decorator with exponential backoff for synchronous functions.

    Retries a function call with exponential backoff when specified exceptions occur.
    The delay between retries grows exponentially: delay = initial_delay * (base ^ attempt).

    Args:
        max_attempts: Maximum number of attempts (default: 3)
        initial_delay: Initial delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        exponential_base: Base for exponential backoff (default: 2.0)
        jitter: Add random jitter to delay to prevent thundering herd (default: True)
        exceptions: Tuple of exception types to retry on (default: (Exception,))
        on_retry: Optional callback function(exception, attempt) called on each retry

    Returns:
        Decorated function that retries on failure

    Raises:
        The last exception if all retry attempts fail

    Example:
        >>> from utils.retry import retry_with_exponential_backoff
        >>> from botocore.exceptions import ClientError
        >>>
        >>> @retry_with_exponential_backoff(
        ...     max_attempts=5,
        ...     initial_delay=1.0,
        ...     exceptions=(ClientError,)
        ... )
        >>> def invoke_bedrock(prompt: str) -> dict:
        ...     import boto3
        ...     import json
        ...
        ...     bedrock = boto3.client("bedrock-runtime")
        ...     response = bedrock.invoke_model(
        ...         modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        ...         body=json.dumps({
        ...             "anthropic_version": "bedrock-2023-05-31",
        ...             "max_tokens": 1000,
        ...             "messages": [{"role": "user", "content": prompt}]
        ...         })
        ...     )
        ...     return json.loads(response["body"].read())
        >>>
        >>> # Will retry up to 5 times with exponential backoff on ClientError
        >>> result = invoke_bedrock("Hello, Claude!")

    Example with custom retry callback:
        >>> def log_retry(exc: Exception, attempt: int) -> None:
        ...     print(f"Retry attempt {attempt} after error: {exc}")
        >>>
        >>> @retry_with_exponential_backoff(
        ...     max_attempts=3,
        ...     on_retry=log_retry
        ... )
        >>> def unstable_function():
        ...     # Function that might fail
        ...     return api.call()
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Exception | None = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_attempts:
                        logger.error(
                            f"Function '{func.__name__}' failed after {max_attempts} attempts. "
                            f"Last error: {e}"
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(initial_delay * (exponential_base ** (attempt - 1)), max_delay)

                    # Add jitter to prevent thundering herd
                    if jitter:
                        delay = delay * (0.5 + random.random())  # nosec B311 - Not for cryptography

                    logger.warning(
                        f"Function '{func.__name__}' failed on attempt {attempt}/{max_attempts}. "
                        f"Error: {e}. Retrying in {delay:.2f}s..."
                    )

                    # Call custom retry callback if provided
                    if on_retry:
                        try:
                            on_retry(e, attempt)
                        except Exception as callback_error:
                            logger.error(f"Error in retry callback: {callback_error}")

                    time.sleep(delay)

            # This should never happen, but satisfy type checker
            if last_exception:
                raise last_exception
            raise RuntimeError("Retry logic error: no exception to raise")

        return wrapper  # type: ignore

    return decorator


def async_retry_with_exponential_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    on_retry: Callable[[Exception, int], None] | None = None,
) -> Callable[[AsyncF], AsyncF]:
    """Retry decorator with exponential backoff for asynchronous functions.

    Async version of retry_with_exponential_backoff. Uses asyncio.sleep instead of time.sleep.

    Args:
        max_attempts: Maximum number of attempts (default: 3)
        initial_delay: Initial delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        exponential_base: Base for exponential backoff (default: 2.0)
        jitter: Add random jitter to delay to prevent thundering herd (default: True)
        exceptions: Tuple of exception types to retry on (default: (Exception,))
        on_retry: Optional callback function(exception, attempt) called on each retry

    Returns:
        Decorated async function that retries on failure

    Raises:
        The last exception if all retry attempts fail

    Example:
        >>> from utils.retry import async_retry_with_exponential_backoff
        >>> from botocore.exceptions import ClientError
        >>> import asyncio
        >>>
        >>> @async_retry_with_exponential_backoff(
        ...     max_attempts=5,
        ...     initial_delay=1.0,
        ...     exceptions=(ClientError,)
        ... )
        >>> async def invoke_bedrock_async(prompt: str) -> dict:
        ...     import boto3
        ...     import json
        ...
        ...     # Note: boto3 is sync, but this shows the pattern
        ...     # In production, use aioboto3 for true async
        ...     bedrock = boto3.client("bedrock-runtime")
        ...     response = bedrock.invoke_model(
        ...         modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        ...         body=json.dumps({
        ...             "anthropic_version": "bedrock-2023-05-31",
        ...             "max_tokens": 1000,
        ...             "messages": [{"role": "user", "content": prompt}]
        ...         })
        ...     )
        ...     return json.loads(response["body"].read())
        >>>
        >>> # Use in async context
        >>> async def main():
        ...     result = await invoke_bedrock_async("Hello, Claude!")
        ...     print(result)
        >>>
        >>> asyncio.run(main())

    Example with aioboto3 (true async):
        >>> @async_retry_with_exponential_backoff(max_attempts=5)
        >>> async def invoke_bedrock_async(prompt: str) -> dict:
        ...     import aioboto3
        ...     import json
        ...
        ...     session = aioboto3.Session()
        ...     async with session.client("bedrock-runtime") as bedrock:
        ...         response = await bedrock.invoke_model(
        ...             modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        ...             body=json.dumps({
        ...                 "anthropic_version": "bedrock-2023-05-31",
        ...                 "max_tokens": 1000,
        ...                 "messages": [{"role": "user", "content": prompt}]
        ...             })
        ...         )
        ...         body = await response["body"].read()
        ...         return json.loads(body)
    """

    def decorator(func: AsyncF) -> AsyncF:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Exception | None = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_attempts:
                        logger.error(
                            f"Async function '{func.__name__}' failed after {max_attempts} attempts. "
                            f"Last error: {e}"
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(initial_delay * (exponential_base ** (attempt - 1)), max_delay)

                    # Add jitter to prevent thundering herd
                    if jitter:
                        delay = delay * (0.5 + random.random())  # nosec B311 - Not for cryptography

                    logger.warning(
                        f"Async function '{func.__name__}' failed on attempt {attempt}/{max_attempts}. "
                        f"Error: {e}. Retrying in {delay:.2f}s..."
                    )

                    # Call custom retry callback if provided
                    if on_retry:
                        try:
                            on_retry(e, attempt)
                        except Exception as callback_error:
                            logger.error(f"Error in retry callback: {callback_error}")

                    await asyncio.sleep(delay)

            # This should never happen, but satisfy type checker
            if last_exception:
                raise last_exception
            raise RuntimeError("Retry logic error: no exception to raise")

        return wrapper  # type: ignore

    return decorator


def retry_on_rate_limit(
    max_attempts: int = 5,
    initial_delay: float = 2.0,
    max_delay: float = 120.0,
    exponential_base: float = 2.0,
    rate_limit_exceptions: tuple[type[Exception], ...] | None = None,
) -> Callable[[F], F]:
    """Specialized retry decorator for API rate limit errors.

    Retries specifically on rate limit errors with longer delays and more attempts
    than typical transient errors. Default configuration is optimized for API rate limits.

    Args:
        max_attempts: Maximum number of attempts (default: 5, higher for rate limits)
        initial_delay: Initial delay in seconds (default: 2.0, longer for rate limits)
        max_delay: Maximum delay in seconds (default: 120.0, 2 minutes max)
        exponential_base: Base for exponential backoff (default: 2.0)
        rate_limit_exceptions: Tuple of rate limit exception types to retry on.
            If None, uses common rate limit exceptions (default: None)

    Returns:
        Decorated function that retries on rate limit errors

    Raises:
        The last exception if all retry attempts fail

    Example:
        >>> from utils.retry import retry_on_rate_limit
        >>> from botocore.exceptions import ClientError
        >>>
        >>> @retry_on_rate_limit(max_attempts=10, initial_delay=5.0)
        >>> def call_bedrock_with_rate_limit(prompt: str) -> dict:
        ...     import boto3
        ...     import json
        ...
        ...     bedrock = boto3.client("bedrock-runtime")
        ...     try:
        ...         response = bedrock.invoke_model(
        ...             modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        ...             body=json.dumps({
        ...                 "anthropic_version": "bedrock-2023-05-31",
        ...                 "max_tokens": 1000,
        ...                 "messages": [{"role": "user", "content": prompt}]
        ...             })
        ...         )
        ...         return json.loads(response["body"].read())
        ...     except ClientError as e:
        ...         if e.response["Error"]["Code"] == "ThrottlingException":
        ...             raise  # Will be retried by decorator
        ...         raise  # Other errors won't be retried
        >>>
        >>> result = call_bedrock_with_rate_limit("Hello!")

    Example with custom rate limit exception:
        >>> class RateLimitError(Exception):
        ...     pass
        >>>
        >>> @retry_on_rate_limit(
        ...     max_attempts=7,
        ...     rate_limit_exceptions=(RateLimitError,)
        ... )
        >>> def call_api():
        ...     response = api.call()
        ...     if response.status_code == 429:
        ...         raise RateLimitError("Rate limit exceeded")
        ...     return response.json()

    Example for AWS Bedrock throttling:
        >>> from botocore.exceptions import ClientError
        >>>
        >>> def is_rate_limit_error(exc: Exception) -> bool:
        ...     if isinstance(exc, ClientError):
        ...         error_code = exc.response.get("Error", {}).get("Code", "")
        ...         return error_code in ["ThrottlingException", "TooManyRequestsException"]
        ...     return False
        >>>
        >>> @retry_on_rate_limit(max_attempts=10)
        >>> def invoke_bedrock_safe(prompt: str) -> dict:
        ...     import boto3
        ...     import json
        ...
        ...     bedrock = boto3.client("bedrock-runtime")
        ...     response = bedrock.invoke_model(
        ...         modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        ...         body=json.dumps({
        ...             "anthropic_version": "bedrock-2023-05-31",
        ...             "max_tokens": 1000,
        ...             "messages": [{"role": "user", "content": prompt}]
        ...         })
        ...     )
        ...     return json.loads(response["body"].read())
    """
    # Default rate limit exceptions if not provided
    if rate_limit_exceptions is None:
        try:
            from botocore.exceptions import ClientError

            rate_limit_exceptions = (ClientError,)
        except ImportError:
            # If boto not available, use generic Exception
            rate_limit_exceptions = (Exception,)

    def is_rate_limit_error(exc: Exception) -> bool:
        """Check if exception is a rate limit error."""
        # Check for botocore ClientError with throttling codes
        try:
            from botocore.exceptions import ClientError

            if isinstance(exc, ClientError):
                error_code = exc.response.get("Error", {}).get("Code", "")
                return error_code in [
                    "ThrottlingException",
                    "TooManyRequestsException",
                    "RequestLimitExceeded",
                    "ProvisionedThroughputExceededException",
                ]
        except ImportError:
            pass

        # Check for HTTP 429 in exception message
        exc_str = str(exc).lower()
        if "429" in exc_str or "rate limit" in exc_str or "throttl" in exc_str:
            return True

        return False

    def on_rate_limit_retry(exc: Exception, attempt: int) -> None:
        """Custom callback for rate limit retries."""
        if is_rate_limit_error(exc):
            logger.info(
                f"Rate limit detected on attempt {attempt}. "
                f"This is normal - backing off and retrying..."
            )

    # Use the standard retry decorator with rate-limit-specific settings
    return retry_with_exponential_backoff(
        max_attempts=max_attempts,
        initial_delay=initial_delay,
        max_delay=max_delay,
        exponential_base=exponential_base,
        jitter=True,  # Always use jitter for rate limits
        exceptions=rate_limit_exceptions,
        on_retry=on_rate_limit_retry,
    )


def calculate_backoff_delay(
    attempt: int,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
) -> float:
    """Calculate backoff delay for a given attempt.

    Utility function to calculate delay without using the decorator.
    Useful for manual retry logic.

    Args:
        attempt: Current attempt number (1-indexed)
        initial_delay: Initial delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        exponential_base: Base for exponential backoff (default: 2.0)
        jitter: Add random jitter to delay (default: True)

    Returns:
        Delay in seconds

    Example:
        >>> from utils.retry import calculate_backoff_delay
        >>>
        >>> # Manual retry loop
        >>> for attempt in range(1, 6):
        ...     try:
        ...         result = risky_operation()
        ...         break
        ...     except Exception as e:
        ...         if attempt == 5:
        ...             raise
        ...         delay = calculate_backoff_delay(attempt)
        ...         print(f"Retrying in {delay:.2f}s...")
        ...         time.sleep(delay)
    """
    delay = min(initial_delay * (exponential_base ** (attempt - 1)), max_delay)

    if jitter:
        delay = delay * (0.5 + random.random())  # nosec B311 - Not for cryptography

    return delay


class RetryContext:
    """Context manager for retry logic with custom state tracking.

    Provides a context manager interface for retry logic with state tracking.
    Useful when you need more control over retry behavior.

    Example:
        >>> from utils.retry import RetryContext
        >>> from botocore.exceptions import ClientError
        >>>
        >>> retry_ctx = RetryContext(
        ...     max_attempts=5,
        ...     initial_delay=1.0,
        ...     exceptions=(ClientError,)
        ... )
        >>>
        >>> for attempt in retry_ctx:
        ...     try:
        ...         result = bedrock.invoke_model(...)
        ...         break  # Success, exit loop
        ...     except ClientError as e:
        ...         retry_ctx.record_failure(e)
        ...         if not retry_ctx.should_retry():
        ...             raise
        ...         retry_ctx.wait()
        >>>
        >>> print(f"Succeeded after {retry_ctx.current_attempt} attempts")
    """

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        exceptions: tuple[type[Exception], ...] = (Exception,),
    ):
        """Initialize retry context.

        Args:
            max_attempts: Maximum number of attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff
            jitter: Add random jitter to delay
            exceptions: Tuple of exception types to retry on
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.exceptions = exceptions

        self.current_attempt = 0
        self.last_exception: Exception | None = None

    def __iter__(self):
        """Iterate through retry attempts."""
        self.current_attempt = 0
        return self

    def __next__(self) -> int:
        """Get next attempt number."""
        self.current_attempt += 1
        if self.current_attempt > self.max_attempts:
            raise StopIteration
        return self.current_attempt

    def record_failure(self, exception: Exception) -> None:
        """Record a failed attempt.

        Args:
            exception: The exception that caused the failure
        """
        self.last_exception = exception

    def should_retry(self) -> bool:
        """Check if we should retry.

        Returns:
            True if we should retry, False otherwise
        """
        if self.current_attempt >= self.max_attempts:
            return False

        if self.last_exception is None:
            return True

        return isinstance(self.last_exception, self.exceptions)

    def wait(self) -> None:
        """Wait before next retry with exponential backoff."""
        delay = calculate_backoff_delay(
            attempt=self.current_attempt,
            initial_delay=self.initial_delay,
            max_delay=self.max_delay,
            exponential_base=self.exponential_base,
            jitter=self.jitter,
        )
        time.sleep(delay)

    def get_delay(self) -> float:
        """Get the delay for the next retry without waiting.

        Returns:
            Delay in seconds
        """
        return calculate_backoff_delay(
            attempt=self.current_attempt,
            initial_delay=self.initial_delay,
            max_delay=self.max_delay,
            exponential_base=self.exponential_base,
            jitter=self.jitter,
        )


__all__ = [
    "retry_with_exponential_backoff",
    "async_retry_with_exponential_backoff",
    "retry_on_rate_limit",
    "calculate_backoff_delay",
    "RetryContext",
]
