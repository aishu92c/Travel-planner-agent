#!/usr/bin/env python3
"""Test Retry Utilities.

Run this script to verify all retry utilities are working correctly.

Prerequisites:
    1. Set up virtual environment and install dependencies:
       ./setup-venv.sh

    2. Or manually:
       python3.13 -m venv venv
       source venv/bin/activate
       pip install -r requirements.txt
       pip install -r requirements-dev.txt

Usage:
    python test_retry.py

Note:
    This test uses mocking and does not require AWS credentials.
"""

import asyncio
import sys
import time
from pathlib import Path
from unittest.mock import patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_imports():
    """Test that all imports work correctly."""
    print("=" * 70)
    print("Testing Imports")
    print("=" * 70)

    from utils import (
        RetryContext,
        async_retry_with_exponential_backoff,
        calculate_backoff_delay,
        retry_on_rate_limit,
        retry_with_exponential_backoff,
    )

    print("✓ All retry utilities imported successfully")

    # Verify all are callable
    assert callable(retry_with_exponential_backoff)
    assert callable(async_retry_with_exponential_backoff)
    assert callable(retry_on_rate_limit)
    assert callable(calculate_backoff_delay)
    assert callable(RetryContext)
    print("✓ All retry utilities are callable")

    print()


def test_retry_with_exponential_backoff_success():
    """Test successful execution without retries."""
    print("=" * 70)
    print("Testing retry_with_exponential_backoff - Success Case")
    print("=" * 70)

    from utils import retry_with_exponential_backoff

    call_count = 0

    @retry_with_exponential_backoff(max_attempts=3)
    def successful_function():
        nonlocal call_count
        call_count += 1
        return "success"

    result = successful_function()
    print(f"✓ Function succeeded: {result}")
    assert result == "success"
    assert call_count == 1
    print(f"✓ Function called exactly once: {call_count} call(s)")

    print()


def test_retry_with_exponential_backoff_retry():
    """Test retry logic with transient failures."""
    print("=" * 70)
    print("Testing retry_with_exponential_backoff - Retry Case")
    print("=" * 70)

    from utils import retry_with_exponential_backoff

    call_count = 0

    @retry_with_exponential_backoff(max_attempts=5, initial_delay=0.1)
    def flaky_function():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError(f"Transient error on attempt {call_count}")
        return "success"

    start_time = time.time()
    result = flaky_function()
    elapsed = time.time() - start_time

    print(f"✓ Function eventually succeeded: {result}")
    assert result == "success"
    assert call_count == 3
    print(f"✓ Function called 3 times (2 failures + 1 success): {call_count} call(s)")
    print(f"✓ Total time with backoff: {elapsed:.2f}s")

    print()


def test_retry_with_exponential_backoff_max_attempts():
    """Test that function fails after max attempts."""
    print("=" * 70)
    print("Testing retry_with_exponential_backoff - Max Attempts")
    print("=" * 70)

    from utils import retry_with_exponential_backoff

    call_count = 0

    @retry_with_exponential_backoff(max_attempts=3, initial_delay=0.1)
    def always_failing_function():
        nonlocal call_count
        call_count += 1
        raise ValueError(f"Error on attempt {call_count}")

    try:
        always_failing_function()
        print("❌ Should have raised ValueError")
    except ValueError as e:
        print(f"✓ Function failed after max attempts: {e}")
        assert call_count == 3
        print(f"✓ Function called exactly {call_count} times")

    print()


def test_retry_with_specific_exceptions():
    """Test retry only on specific exceptions."""
    print("=" * 70)
    print("Testing retry_with_exponential_backoff - Specific Exceptions")
    print("=" * 70)

    from utils import retry_with_exponential_backoff

    call_count = 0

    class RetryableError(Exception):
        pass

    class NonRetryableError(Exception):
        pass

    @retry_with_exponential_backoff(max_attempts=5, initial_delay=0.1, exceptions=(RetryableError,))
    def selective_retry_function(should_retry: bool):
        nonlocal call_count
        call_count += 1
        if should_retry:
            raise RetryableError("This will be retried")
        raise NonRetryableError("This will not be retried")

    # Test retryable error
    call_count = 0
    try:
        selective_retry_function(should_retry=True)
        print("❌ Should have raised RetryableError")
    except RetryableError:
        print(f"✓ Retryable error retried {call_count} times")
        assert call_count == 5

    # Test non-retryable error
    call_count = 0
    try:
        selective_retry_function(should_retry=False)
        print("❌ Should have raised NonRetryableError")
    except NonRetryableError:
        print(f"✓ Non-retryable error failed immediately: {call_count} call(s)")
        assert call_count == 1

    print()


def test_retry_callback():
    """Test custom retry callback."""
    print("=" * 70)
    print("Testing retry_with_exponential_backoff - Retry Callback")
    print("=" * 70)

    from utils import retry_with_exponential_backoff

    callback_calls = []

    def custom_callback(exc: Exception, attempt: int):
        callback_calls.append((str(exc), attempt))

    call_count = 0

    @retry_with_exponential_backoff(max_attempts=3, initial_delay=0.1, on_retry=custom_callback)
    def function_with_callback():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError(f"Error {call_count}")
        return "success"

    result = function_with_callback()
    print(f"✓ Function succeeded: {result}")
    print(f"✓ Callback called {len(callback_calls)} times")
    assert len(callback_calls) == 2  # 2 failures before success
    for i, (error, attempt) in enumerate(callback_calls, start=1):
        print(f"  - Callback {i}: attempt={attempt}, error='{error}'")

    print()


def test_async_retry_with_exponential_backoff():
    """Test async retry decorator."""
    print("=" * 70)
    print("Testing async_retry_with_exponential_backoff")
    print("=" * 70)

    from utils import async_retry_with_exponential_backoff

    call_count = 0

    @async_retry_with_exponential_backoff(max_attempts=3, initial_delay=0.1)
    async def async_flaky_function():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError(f"Async error on attempt {call_count}")
        await asyncio.sleep(0.01)  # Simulate async work
        return "async success"

    async def run_test():
        nonlocal call_count
        call_count = 0
        start_time = time.time()
        result = await async_flaky_function()
        elapsed = time.time() - start_time
        return result, call_count, elapsed

    result, count, elapsed = asyncio.run(run_test())
    print(f"✓ Async function succeeded: {result}")
    assert result == "async success"
    assert count == 3
    print(f"✓ Async function called {count} times")
    print(f"✓ Total time with backoff: {elapsed:.2f}s")

    print()


def test_retry_on_rate_limit():
    """Test rate limit retry decorator."""
    print("=" * 70)
    print("Testing retry_on_rate_limit")
    print("=" * 70)

    from utils import retry_on_rate_limit

    # Mock ClientError for rate limit testing
    class MockClientError(Exception):
        def __init__(self, error_code: str):
            self.response = {"Error": {"Code": error_code}}
            super().__init__(error_code)

    call_count = 0

    @retry_on_rate_limit(max_attempts=5, initial_delay=0.1)
    def rate_limited_function():
        nonlocal call_count
        call_count += 1
        if call_count < 4:
            raise MockClientError("ThrottlingException")
        return "success"

    # Patch botocore.exceptions.ClientError
    with patch("utils.retry.ClientError", MockClientError):
        start_time = time.time()
        result = rate_limited_function()
        elapsed = time.time() - start_time

        print(f"✓ Rate limited function succeeded: {result}")
        assert result == "success"
        assert call_count == 4
        print(f"✓ Function called {call_count} times (3 throttles + 1 success)")
        print(f"✓ Total time with rate limit backoff: {elapsed:.2f}s")

    print()


def test_calculate_backoff_delay():
    """Test backoff delay calculation."""
    print("=" * 70)
    print("Testing calculate_backoff_delay")
    print("=" * 70)

    from utils import calculate_backoff_delay

    # Test without jitter
    delay1 = calculate_backoff_delay(1, initial_delay=1.0, jitter=False)
    delay2 = calculate_backoff_delay(2, initial_delay=1.0, jitter=False)
    delay3 = calculate_backoff_delay(3, initial_delay=1.0, jitter=False)

    print(f"✓ Delay for attempt 1: {delay1:.2f}s")
    print(f"✓ Delay for attempt 2: {delay2:.2f}s")
    print(f"✓ Delay for attempt 3: {delay3:.2f}s")

    assert delay1 == 1.0  # 1 * 2^0
    assert delay2 == 2.0  # 1 * 2^1
    assert delay3 == 4.0  # 1 * 2^2
    print("✓ Exponential backoff working correctly")

    # Test max delay
    delay_max = calculate_backoff_delay(10, initial_delay=1.0, max_delay=10.0, jitter=False)
    print(f"✓ Delay capped at max_delay: {delay_max:.2f}s (should be 10.0s)")
    assert delay_max == 10.0

    # Test with jitter
    delay_jitter = calculate_backoff_delay(2, initial_delay=1.0, jitter=True)
    print(f"✓ Delay with jitter: {delay_jitter:.2f}s (between 1.0s and 2.0s)")
    assert 1.0 <= delay_jitter <= 2.0

    print()


def test_retry_context():
    """Test RetryContext context manager."""
    print("=" * 70)
    print("Testing RetryContext")
    print("=" * 70)

    from utils import RetryContext

    call_count = 0
    retry_ctx = RetryContext(max_attempts=5, initial_delay=0.1)

    for attempt in retry_ctx:
        call_count += 1
        try:
            if call_count < 3:
                raise ValueError(f"Error on attempt {call_count}")
            result = "success"
            break
        except ValueError as e:
            retry_ctx.record_failure(e)
            if not retry_ctx.should_retry():
                raise
            retry_ctx.wait()

    print(f"✓ RetryContext succeeded: {result}")
    assert result == "success"
    assert call_count == 3
    print(f"✓ RetryContext attempted {call_count} times")
    print(f"✓ Current attempt: {retry_ctx.current_attempt}")

    print()


def test_retry_context_max_attempts():
    """Test RetryContext respects max attempts."""
    print("=" * 70)
    print("Testing RetryContext - Max Attempts")
    print("=" * 70)

    from utils import RetryContext

    call_count = 0
    retry_ctx = RetryContext(max_attempts=3, initial_delay=0.1)

    last_exception = None
    for attempt in retry_ctx:
        call_count += 1
        try:
            raise ValueError(f"Error on attempt {call_count}")
        except ValueError as e:
            last_exception = e
            retry_ctx.record_failure(e)
            if not retry_ctx.should_retry():
                break
            retry_ctx.wait()

    print("✓ RetryContext stopped after max attempts")
    assert call_count == 3
    print(f"✓ Attempted exactly {call_count} times")
    assert last_exception is not None
    print(f"✓ Last exception preserved: {last_exception}")

    print()


def test_bedrock_example():
    """Test retry with mocked Bedrock call."""
    print("=" * 70)
    print("Testing Retry with Mocked Bedrock Call")
    print("=" * 70)

    from utils import retry_with_exponential_backoff

    # Mock ClientError
    class MockClientError(Exception):
        def __init__(self, error_code: str):
            self.response = {"Error": {"Code": error_code}}
            super().__init__(error_code)

    call_count = 0

    @retry_with_exponential_backoff(
        max_attempts=5, initial_delay=0.1, exceptions=(MockClientError,)
    )
    def invoke_bedrock_mock(prompt: str):
        nonlocal call_count
        call_count += 1

        # Simulate throttling on first 2 attempts
        if call_count < 3:
            raise MockClientError("ThrottlingException")

        # Simulate successful response
        return {
            "content": [{"text": f"Response to: {prompt}"}],
            "usage": {"input_tokens": 10, "output_tokens": 20},
        }

    result = invoke_bedrock_mock("Hello, Claude!")
    print("✓ Bedrock call succeeded after retries")
    print(f"✓ Response: {result['content'][0]['text']}")
    assert call_count == 3
    print(f"✓ Total attempts: {call_count}")

    print()


def test_async_bedrock_example():
    """Test async retry with mocked Bedrock call."""
    print("=" * 70)
    print("Testing Async Retry with Mocked Bedrock Call")
    print("=" * 70)

    from utils import async_retry_with_exponential_backoff

    class MockClientError(Exception):
        def __init__(self, error_code: str):
            self.response = {"Error": {"Code": error_code}}
            super().__init__(error_code)

    call_count = 0

    @async_retry_with_exponential_backoff(
        max_attempts=5, initial_delay=0.1, exceptions=(MockClientError,)
    )
    async def invoke_bedrock_async_mock(prompt: str):
        nonlocal call_count
        call_count += 1

        await asyncio.sleep(0.01)  # Simulate network delay

        if call_count < 3:
            raise MockClientError("ThrottlingException")

        return {
            "content": [{"text": f"Async response to: {prompt}"}],
            "usage": {"input_tokens": 10, "output_tokens": 20},
        }

    async def run_test():
        nonlocal call_count
        call_count = 0
        result = await invoke_bedrock_async_mock("Hello, Claude!")
        return result, call_count

    result, count = asyncio.run(run_test())
    print("✓ Async Bedrock call succeeded after retries")
    print(f"✓ Response: {result['content'][0]['text']}")
    assert count == 3
    print(f"✓ Total attempts: {count}")

    print()


def test_logging():
    """Test that retry decorator logs appropriately."""
    print("=" * 70)
    print("Testing Retry Logging")
    print("=" * 70)

    import logging

    from utils import retry_with_exponential_backoff

    # Capture log messages
    log_messages = []

    class TestHandler(logging.Handler):
        def emit(self, record):
            log_messages.append(record.getMessage())

    handler = TestHandler()
    logger = logging.getLogger("utils.retry")
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)

    call_count = 0

    @retry_with_exponential_backoff(max_attempts=3, initial_delay=0.1)
    def logging_test_function():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError(f"Error {call_count}")
        return "success"

    result = logging_test_function()

    # Clean up
    logger.removeHandler(handler)

    print(f"✓ Function succeeded: {result}")
    print(f"✓ Logged {len(log_messages)} warning messages")
    for i, msg in enumerate(log_messages, start=1):
        print(f"  - Log {i}: {msg[:60]}...")

    assert len(log_messages) >= 2  # At least 2 retry warnings
    print("✓ Retry warnings logged correctly")

    print()


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 22 + "Retry Utilities Test" + " " * 26 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n")

    tests = [
        test_imports,
        test_retry_with_exponential_backoff_success,
        test_retry_with_exponential_backoff_retry,
        test_retry_with_exponential_backoff_max_attempts,
        test_retry_with_specific_exceptions,
        test_retry_callback,
        test_async_retry_with_exponential_backoff,
        test_retry_on_rate_limit,
        test_calculate_backoff_delay,
        test_retry_context,
        test_retry_context_max_attempts,
        test_bedrock_example,
        test_async_bedrock_example,
        test_logging,
    ]

    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}\n")
            import traceback

            traceback.print_exc()
            return 1

    print("=" * 70)
    print("✅ All retry utility tests passed!")
    print("=" * 70)
    print("\nRetry Utilities Summary:")
    print("- 3 retry decorators (sync, async, rate limit)")
    print("- 1 utility function (calculate_backoff_delay)")
    print("- 1 context manager (RetryContext)")
    print("- Exponential backoff with jitter")
    print("- Configurable exceptions and callbacks")
    print("- Comprehensive logging")
    print("- Full type hints and documentation")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
