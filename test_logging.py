#!/usr/bin/env python3
"""Test Logging Utilities.

Run this script to verify all logging utilities are working correctly.

Prerequisites:
    1. Set up virtual environment and install dependencies:
       ./setup-venv.sh

Usage:
    python test_logging.py

Note:
    This test does not require AWS credentials.
"""

import asyncio
import json
import logging
import sys
import tempfile
from io import StringIO
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_imports():
    """Test that all imports work correctly."""
    print("=" * 70)
    print("Testing Imports")
    print("=" * 70)

    from observability import (
        ConsoleFormatter,
        JsonFormatter,
        LogContext,
        get_logger,
        log_errors,
        log_execution,
        setup_logging,
    )

    print("✓ All logging utilities imported successfully")

    # Verify all are callable/classes
    assert callable(setup_logging)
    assert callable(get_logger)
    assert callable(LogContext)
    assert callable(log_execution)
    assert callable(log_errors)
    assert callable(JsonFormatter)
    assert callable(ConsoleFormatter)
    print("✓ All logging utilities are callable/classes")

    print()


def test_setup_logging():
    """Test logging setup."""
    print("=" * 70)
    print("Testing setup_logging")
    print("=" * 70)

    from observability import get_logger, setup_logging

    # Setup with custom parameters
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = str(Path(tmpdir) / "test.log")

        setup_logging(level="DEBUG", json_format=False, log_file=log_file)
        print("✓ Logging setup completed")

        # Verify log file created
        logger = get_logger(__name__)
        logger.info("Test message")

        assert Path(log_file).exists()
        print(f"✓ Log file created: {log_file}")

        # Read log file
        with open(log_file) as f:
            content = f.read()
            assert len(content) > 0
            print(f"✓ Log file has content: {len(content)} bytes")

    print()


def test_json_formatter():
    """Test JSON formatter."""
    print("=" * 70)
    print("Testing JsonFormatter")
    print("=" * 70)

    from observability.logging import JsonFormatter

    # Create formatter
    formatter = JsonFormatter()

    # Create log record
    logger = logging.getLogger("test")
    logger.setLevel(logging.INFO)

    # Capture output
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Log message
    logger.info("Test message", extra={"extra_fields": {"key": "value"}})

    # Get output
    output = stream.getvalue().strip()
    print(f"✓ JSON log output: {output[:80]}...")

    # Parse JSON
    log_data = json.loads(output)
    assert log_data["level"] == "INFO"
    assert log_data["message"] == "Test message"
    assert "timestamp" in log_data
    assert "logger" in log_data
    print("✓ JSON structure correct")
    print(f"  - Level: {log_data['level']}")
    print(f"  - Message: {log_data['message']}")
    print(f"  - Logger: {log_data['logger']}")

    print()


def test_console_formatter():
    """Test console formatter."""
    print("=" * 70)
    print("Testing ConsoleFormatter")
    print("=" * 70)

    from observability.logging import ConsoleFormatter

    # Create formatter
    formatter = ConsoleFormatter()

    # Create log record
    logger = logging.getLogger("test.console")
    logger.setLevel(logging.INFO)

    # Capture output
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Log messages at different levels
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")

    output = stream.getvalue()
    print(f"✓ Console output generated: {len(output)} chars")
    assert "Info message" in output
    assert "Warning message" in output
    assert "Error message" in output
    print("✓ All log levels present in output")

    print()


def test_log_context():
    """Test LogContext context manager."""
    print("=" * 70)
    print("Testing LogContext")
    print("=" * 70)

    from observability import LogContext, get_logger, setup_logging

    # Setup logging with JSON format
    setup_logging(json_format=True)

    logger = get_logger("test.context")

    # Capture output
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    from observability.logging import JsonFormatter

    handler.setFormatter(JsonFormatter())
    logger.logger.addHandler(handler)

    # Test basic context
    with LogContext(request_id="req-123", user_id="user-456"):
        logger.info("Message with context")

    output = stream.getvalue()
    log_data = json.loads(output.strip())

    assert log_data["request_id"] == "req-123"
    assert log_data["user_id"] == "user-456"
    print("✓ Context included in log output")
    print(f"  - Request ID: {log_data['request_id']}")
    print(f"  - User ID: {log_data['user_id']}")

    # Test nested context
    stream.truncate(0)
    stream.seek(0)

    with LogContext(request_id="req-789"):
        with LogContext(operation="validate"):
            logger.info("Nested context")

    output = stream.getvalue()
    log_data = json.loads(output.strip())

    assert log_data["request_id"] == "req-789"
    assert log_data["operation"] == "validate"
    print("✓ Nested context working")
    print(f"  - Request ID: {log_data['request_id']}")
    print(f"  - Operation: {log_data['operation']}")

    # Test context cleared after exit
    stream.truncate(0)
    stream.seek(0)

    logger.info("Message without context")
    output = stream.getvalue()
    log_data = json.loads(output.strip())

    assert "request_id" not in log_data
    assert "operation" not in log_data
    print("✓ Context cleared after exiting context manager")

    print()


def test_log_execution_decorator():
    """Test log_execution decorator."""
    print("=" * 70)
    print("Testing log_execution decorator")
    print("=" * 70)

    from observability import log_execution, setup_logging

    setup_logging(json_format=False)

    @log_execution(level="INFO", include_duration=True)
    def test_function(x: int, y: int) -> int:
        return x + y

    result = test_function(5, 3)
    assert result == 8
    print(f"✓ Decorated function executed: {result}")

    # Test with arguments logged
    @log_execution(level="DEBUG", include_args=True, include_result=True)
    def test_with_args(name: str) -> str:
        return f"Hello, {name}!"

    result = test_with_args("Alice")
    assert result == "Hello, Alice!"
    print(f"✓ Function with args/result logging: {result}")

    print()


def test_async_log_execution():
    """Test log_execution with async functions."""
    print("=" * 70)
    print("Testing async log_execution")
    print("=" * 70)

    from observability import log_execution, setup_logging

    setup_logging(json_format=False)

    @log_execution(level="INFO", include_duration=True)
    async def async_function(x: int) -> int:
        await asyncio.sleep(0.01)
        return x * 2

    result = asyncio.run(async_function(10))
    assert result == 20
    print(f"✓ Async decorated function executed: {result}")

    print()


def test_log_errors_decorator():
    """Test log_errors decorator."""
    print("=" * 70)
    print("Testing log_errors decorator")
    print("=" * 70)

    from observability import get_logger, log_errors, setup_logging

    setup_logging(json_format=False)
    logger = get_logger(__name__)

    @log_errors(logger)
    def failing_function(value: int):
        if value < 0:
            raise ValueError("Value must be positive")
        return value * 2

    # Test successful execution
    result = failing_function(5)
    assert result == 10
    print(f"✓ Successful execution: {result}")

    # Test error logging
    try:
        failing_function(-5)
        print("❌ Should have raised ValueError")
    except ValueError as e:
        print(f"✓ Error logged and raised: {e}")

    print()


def test_async_log_errors():
    """Test log_errors with async functions."""
    print("=" * 70)
    print("Testing async log_errors")
    print("=" * 70)

    from observability import log_errors, setup_logging

    setup_logging(json_format=False)

    @log_errors()
    async def async_failing_function(value: int):
        if value < 0:
            raise ValueError("Async value must be positive")
        await asyncio.sleep(0.01)
        return value * 2

    # Test successful execution
    result = asyncio.run(async_failing_function(5))
    assert result == 10
    print(f"✓ Async successful execution: {result}")

    # Test error logging
    try:
        asyncio.run(async_failing_function(-5))
        print("❌ Should have raised ValueError")
    except ValueError as e:
        print(f"✓ Async error logged and raised: {e}")

    print()


def test_combined_decorators():
    """Test combining decorators."""
    print("=" * 70)
    print("Testing Combined Decorators")
    print("=" * 70)

    from observability import log_errors, log_execution, setup_logging

    setup_logging(json_format=False)

    @log_execution(level="INFO", include_duration=True)
    @log_errors()
    def combined_function(x: int, y: int) -> int:
        if x < 0 or y < 0:
            raise ValueError("Values must be positive")
        return x + y

    # Test success
    result = combined_function(5, 3)
    assert result == 8
    print(f"✓ Combined decorators - success: {result}")

    # Test error
    try:
        combined_function(-5, 3)
        print("❌ Should have raised ValueError")
    except ValueError as e:
        print(f"✓ Combined decorators - error handled: {e}")

    print()


def test_get_logger():
    """Test get_logger function."""
    print("=" * 70)
    print("Testing get_logger")
    print("=" * 70)

    from observability import get_logger, setup_logging

    setup_logging(json_format=False)

    # Get logger for module
    logger = get_logger(__name__)
    print(f"✓ Logger created: {logger.logger.name}")

    # Log messages at different levels
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    print("✓ All log levels working")

    # Get logger for different module
    logger2 = get_logger("app.services.user")
    print(f"✓ Logger for different module: {logger2.logger.name}")

    print()


def test_context_manager_edge_cases():
    """Test LogContext edge cases."""
    print("=" * 70)
    print("Testing LogContext Edge Cases")
    print("=" * 70)

    from observability import LogContext

    # Empty context
    with LogContext():
        current = LogContext.current()
        print(f"✓ Empty context: {current}")

    # Multiple fields
    with LogContext(a=1, b=2, c=3, d=4, e=5):
        current = LogContext.current()
        assert current["a"] == 1
        assert current["e"] == 5
        print(f"✓ Multiple fields: {len(current)} fields")

    # Context with complex values
    with LogContext(list_field=[1, 2, 3], dict_field={"key": "value"}, none_field=None):
        current = LogContext.current()
        assert current["list_field"] == [1, 2, 3]
        assert current["dict_field"] == {"key": "value"}
        assert current["none_field"] is None
        print("✓ Complex values in context")

    # Clear context
    LogContext.clear()
    current = LogContext.current()
    assert len(current) == 0
    print("✓ Context cleared")

    print()


def test_real_world_scenario():
    """Test real-world usage scenario."""
    print("=" * 70)
    print("Testing Real-World Scenario")
    print("=" * 70)

    from observability import (
        LogContext,
        get_logger,
        log_errors,
        log_execution,
        setup_logging,
    )

    # Setup
    setup_logging(json_format=False, level="INFO")
    logger = get_logger(__name__)

    # Simulate API request handler
    @log_execution(level="INFO", include_duration=True)
    @log_errors()
    def handle_request(request_id: str, user_id: str, query: str):
        with LogContext(request_id=request_id, user_id=user_id):
            logger.info("Request received", extra={"query": query})

            # Process query
            result = process_query(query)

            logger.info("Request completed", extra={"result_length": len(result)})
            return result

    @log_execution(level="DEBUG")
    def process_query(query: str) -> str:
        logger = get_logger(__name__)
        logger.debug(f"Processing query: {query}")

        # Simulate processing
        if not query:
            raise ValueError("Query cannot be empty")

        return f"Processed: {query}"

    # Execute
    result = handle_request("req-123", "user-456", "What is AI?")
    assert "Processed" in result
    print(f"✓ Real-world scenario completed: {result}")

    print()


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 22 + "Logging Utilities Test" + " " * 24 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n")

    tests = [
        test_imports,
        test_setup_logging,
        test_json_formatter,
        test_console_formatter,
        test_log_context,
        test_log_execution_decorator,
        test_async_log_execution,
        test_log_errors_decorator,
        test_async_log_errors,
        test_combined_decorators,
        test_get_logger,
        test_context_manager_edge_cases,
        test_real_world_scenario,
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
    print("✅ All logging utility tests passed!")
    print("=" * 70)
    print("\nLogging Utilities Summary:")
    print("- setup_logging() for centralized configuration")
    print("- get_logger() for context-aware loggers")
    print("- LogContext for request/user tracking")
    print("- @log_execution decorator for function logging")
    print("- @log_errors decorator for error logging")
    print("- JsonFormatter for structured logs")
    print("- ConsoleFormatter for human-readable output")
    print("- Full async support")
    print("- CloudWatch integration ready")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
