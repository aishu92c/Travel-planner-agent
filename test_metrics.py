#!/usr/bin/env python3
"""Test Metrics Collection Framework.

Run this script to verify all metrics utilities are working correctly.

Prerequisites:
    1. Set up virtual environment and install dependencies:
       ./setup-venv.sh

    2. Or manually:
       python3.13 -m venv venv
       source venv/bin/activate
       pip install -r requirements.txt
       pip install -r requirements-dev.txt
       pip install prometheus-client

Usage:
    python test_metrics.py

Note:
    This test does not require AWS credentials.
"""

import asyncio
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_imports():
    """Test that all imports work correctly."""
    print("=" * 70)
    print("Testing Imports")
    print("=" * 70)

    from observability import (
        MetricsCollector,
        get_metrics_app,
        get_metrics_collector,
        get_metrics_text,
        track_duration,
        track_errors,
    )

    print("✓ All metrics utilities imported successfully")

    # Verify all are callable/classes
    assert callable(MetricsCollector)
    assert callable(get_metrics_collector)
    assert callable(track_duration)
    assert callable(track_errors)
    assert callable(get_metrics_app)
    assert callable(get_metrics_text)
    print("✓ All metrics utilities are callable/classes")

    print()


def test_metrics_collector():
    """Test MetricsCollector class."""
    print("=" * 70)
    print("Testing MetricsCollector")
    print("=" * 70)

    from observability import get_metrics_collector

    metrics = get_metrics_collector()
    print(f"✓ Got metrics collector: {type(metrics)}")

    # Test counter
    metrics.increment_counter(
        "request_count", labels={"endpoint": "/query", "method": "POST", "status": "200"}
    )
    print("✓ Incremented counter")

    # Test histogram
    metrics.record_histogram(
        "request_duration", value=0.5, labels={"endpoint": "/query", "method": "POST"}
    )
    print("✓ Recorded histogram value")

    # Test gauge
    metrics.set_gauge("active_requests", value=10, labels={"endpoint": "/query"})
    print("✓ Set gauge value")

    # Test gauge increment/decrement
    metrics.increment_gauge("active_requests", labels={"endpoint": "/query"})
    print("✓ Incremented gauge")

    metrics.decrement_gauge("active_requests", labels={"endpoint": "/query"})
    print("✓ Decremented gauge")

    print()


def test_counter_metrics():
    """Test counter metrics."""
    print("=" * 70)
    print("Testing Counter Metrics")
    print("=" * 70)

    from observability import get_metrics_collector

    metrics = get_metrics_collector()

    # Test all counter types
    metrics.increment_counter(
        "request_count", labels={"endpoint": "/test", "method": "GET", "status": "200"}
    )
    print("✓ request_count incremented")

    metrics.increment_counter(
        "error_count",
        labels={"error_type": "ValueError", "endpoint": "/test", "function": "test_func"},
    )
    print("✓ error_count incremented")

    metrics.increment_counter("cache_hits", labels={"cache_name": "embeddings", "operation": "get"})
    print("✓ cache_hits incremented")

    metrics.increment_counter(
        "cache_misses", labels={"cache_name": "embeddings", "operation": "get"}
    )
    print("✓ cache_misses incremented")

    metrics.increment_counter(
        "bedrock_invocations", labels={"model_id": "claude-3", "status": "success"}
    )
    print("✓ bedrock_invocations incremented")

    metrics.increment_counter(
        "rag_queries", labels={"operation": "vector_search", "status": "success"}
    )
    print("✓ rag_queries incremented")

    print()


def test_histogram_metrics():
    """Test histogram metrics."""
    print("=" * 70)
    print("Testing Histogram Metrics")
    print("=" * 70)

    from observability import get_metrics_collector

    metrics = get_metrics_collector()

    # Test all histogram types
    metrics.record_histogram(
        "request_duration", value=0.5, labels={"endpoint": "/test", "method": "GET"}
    )
    print("✓ request_duration recorded")

    metrics.record_histogram(
        "token_usage", value=1500, labels={"model_id": "claude-3", "token_type": "total"}
    )
    print("✓ token_usage recorded")

    metrics.record_histogram(
        "retrieval_time", value=0.05, labels={"operation": "vector_search", "source": "chroma"}
    )
    print("✓ retrieval_time recorded")

    metrics.record_histogram("bedrock_duration", value=2.5, labels={"model_id": "claude-3"})
    print("✓ bedrock_duration recorded")

    metrics.record_histogram(
        "database_query_duration", value=0.01, labels={"operation": "select", "table": "users"}
    )
    print("✓ database_query_duration recorded")

    print()


def test_gauge_metrics():
    """Test gauge metrics."""
    print("=" * 70)
    print("Testing Gauge Metrics")
    print("=" * 70)

    from observability import get_metrics_collector

    metrics = get_metrics_collector()

    # Test all gauge types
    metrics.set_gauge("active_requests", value=10, labels={"endpoint": "/test"})
    print("✓ active_requests set")

    metrics.set_gauge("cache_size", value=1024 * 1024 * 100, labels={"cache_name": "embeddings"})
    print("✓ cache_size set")

    metrics.set_gauge("active_connections", value=50, labels={"connection_type": "database"})
    print("✓ active_connections set")

    metrics.set_gauge("memory_usage", value=1024 * 1024 * 500, labels={"process": "main"})
    print("✓ memory_usage set")

    metrics.set_gauge("queue_size", value=25, labels={"queue_name": "processing"})
    print("✓ queue_size set")

    print()


def test_track_duration_context_manager():
    """Test track_duration context manager."""
    print("=" * 70)
    print("Testing track_duration Context Manager")
    print("=" * 70)

    from observability import get_metrics_collector

    metrics = get_metrics_collector()

    # Test basic duration tracking
    with metrics.track_duration("request_duration", labels={"endpoint": "/test", "method": "POST"}):
        time.sleep(0.1)
    print("✓ Duration tracked with context manager")

    # Test multiple operations
    for i in range(3):
        with metrics.track_duration(
            "database_query_duration", labels={"operation": "select", "table": "users"}
        ):
            time.sleep(0.01)
    print("✓ Multiple durations tracked")

    print()


def test_track_active_context_manager():
    """Test track_active context manager."""
    print("=" * 70)
    print("Testing track_active Context Manager")
    print("=" * 70)

    from observability import get_metrics_collector

    metrics = get_metrics_collector()

    # Test active tracking
    with metrics.track_active("active_requests", labels={"endpoint": "/test"}):
        time.sleep(0.05)
    print("✓ Active requests tracked with context manager")

    # Test nested active tracking
    with metrics.track_active("active_connections", labels={"connection_type": "database"}):
        with metrics.track_active("active_requests", labels={"endpoint": "/query"}):
            time.sleep(0.05)
    print("✓ Nested active tracking working")

    print()


def test_track_duration_decorator():
    """Test track_duration decorator."""
    print("=" * 70)
    print("Testing track_duration Decorator")
    print("=" * 70)

    from observability import track_duration

    @track_duration("request_duration", labels={"endpoint": "/test", "method": "GET"})
    def test_function():
        time.sleep(0.05)
        return "success"

    result = test_function()
    assert result == "success"
    print(f"✓ Decorated function executed: {result}")

    # Test with arguments
    @track_duration("database_query_duration", labels={"operation": "select", "table": "users"})
    def query_users(count: int):
        time.sleep(0.01)
        return f"Found {count} users"

    result = query_users(10)
    assert "10 users" in result
    print(f"✓ Function with arguments: {result}")

    print()


def test_async_track_duration():
    """Test track_duration with async functions."""
    print("=" * 70)
    print("Testing Async track_duration")
    print("=" * 70)

    from observability import track_duration

    @track_duration("bedrock_duration", labels={"model_id": "claude-3"})
    async def async_function():
        await asyncio.sleep(0.05)
        return "async success"

    result = asyncio.run(async_function())
    assert result == "async success"
    print(f"✓ Async decorated function executed: {result}")

    print()


def test_track_errors_decorator():
    """Test track_errors decorator."""
    print("=" * 70)
    print("Testing track_errors Decorator")
    print("=" * 70)

    from observability import track_errors

    @track_errors(labels={"endpoint": "/test"})
    def failing_function(value: int):
        if value < 0:
            raise ValueError("Value must be positive")
        return value * 2

    # Test successful execution
    result = failing_function(5)
    assert result == 10
    print(f"✓ Successful execution: {result}")

    # Test error tracking
    try:
        failing_function(-5)
        print("❌ Should have raised ValueError")
    except ValueError as e:
        print(f"✓ Error tracked and raised: {e}")

    print()


def test_async_track_errors():
    """Test track_errors with async functions."""
    print("=" * 70)
    print("Testing Async track_errors")
    print("=" * 70)

    from observability import track_errors

    @track_errors(labels={"operation": "async_test"})
    async def async_failing_function(value: int):
        if value < 0:
            raise ValueError("Async value must be positive")
        await asyncio.sleep(0.01)
        return value * 2

    # Test successful execution
    result = asyncio.run(async_failing_function(5))
    assert result == 10
    print(f"✓ Async successful execution: {result}")

    # Test error tracking
    try:
        asyncio.run(async_failing_function(-5))
        print("❌ Should have raised ValueError")
    except ValueError as e:
        print(f"✓ Async error tracked and raised: {e}")

    print()


def test_combined_decorators():
    """Test combining decorators."""
    print("=" * 70)
    print("Testing Combined Decorators")
    print("=" * 70)

    from observability import track_duration, track_errors

    @track_duration("request_duration", labels={"endpoint": "/combined", "method": "POST"})
    @track_errors(labels={"endpoint": "/combined"})
    def combined_function(x: int, y: int):
        if x < 0 or y < 0:
            raise ValueError("Values must be positive")
        time.sleep(0.05)
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


def test_get_metrics_text():
    """Test getting metrics in text format."""
    print("=" * 70)
    print("Testing get_metrics_text")
    print("=" * 70)

    from observability import get_metrics_collector, get_metrics_text

    # Generate some metrics
    metrics = get_metrics_collector()
    metrics.increment_counter(
        "request_count", labels={"endpoint": "/test", "method": "GET", "status": "200"}
    )
    metrics.record_histogram(
        "request_duration", value=0.5, labels={"endpoint": "/test", "method": "GET"}
    )
    metrics.set_gauge("active_requests", value=5, labels={"endpoint": "/test"})

    # Get metrics text
    metrics_text = get_metrics_text()
    assert isinstance(metrics_text, bytes)
    print(f"✓ Got metrics text: {len(metrics_text)} bytes")

    # Check content
    text_str = metrics_text.decode()
    assert "request_count" in text_str
    assert "request_duration" in text_str
    assert "active_requests" in text_str
    print("✓ Metrics text contains expected metrics")

    # Print sample
    lines = text_str.split("\n")[:10]
    print("\nSample metrics output:")
    for line in lines:
        if line and not line.startswith("#"):
            print(f"  {line[:70]}...")

    print()


def test_get_metrics_app():
    """Test getting metrics ASGI app."""
    print("=" * 70)
    print("Testing get_metrics_app")
    print("=" * 70)

    from observability import get_metrics_app

    app = get_metrics_app()
    print(f"✓ Got metrics ASGI app: {type(app)}")

    # Verify it's an ASGI app
    assert callable(app)
    print("✓ Metrics app is callable")

    print()


def test_real_world_scenario():
    """Test real-world usage scenario."""
    print("=" * 70)
    print("Testing Real-World Scenario")
    print("=" * 70)

    from observability import get_metrics_collector, track_duration, track_errors

    metrics = get_metrics_collector()

    @track_duration("bedrock_duration", labels={"model_id": "claude-3"})
    @track_errors(labels={"function": "invoke_bedrock"})
    def invoke_bedrock(prompt: str):
        # Track invocation
        metrics.increment_counter(
            "bedrock_invocations", labels={"model_id": "claude-3", "status": "success"}
        )

        # Simulate work
        time.sleep(0.1)

        # Track token usage
        metrics.record_histogram(
            "token_usage", value=1500, labels={"model_id": "claude-3", "token_type": "total"}
        )

        return f"Response to: {prompt}"

    # Simulate API request
    with metrics.track_active("active_requests", labels={"endpoint": "/query"}):
        # Track request
        metrics.increment_counter(
            "request_count", labels={"endpoint": "/query", "method": "POST", "status": "200"}
        )

        # Process request
        with metrics.track_duration(
            "request_duration", labels={"endpoint": "/query", "method": "POST"}
        ):
            result = invoke_bedrock("What is AI?")

    assert "Response" in result
    print(f"✓ Real-world scenario completed: {result}")

    print()


def test_error_handling():
    """Test error handling in metrics."""
    print("=" * 70)
    print("Testing Error Handling")
    print("=" * 70)

    from observability import get_metrics_collector

    metrics = get_metrics_collector()

    # Test invalid metric name
    try:
        metrics.increment_counter("invalid_metric")
        print("❌ Should have raised ValueError")
    except ValueError as e:
        print(f"✓ Invalid counter rejected: {str(e)[:50]}...")

    try:
        metrics.record_histogram("invalid_metric", value=1.0)
        print("❌ Should have raised ValueError")
    except ValueError as e:
        print(f"✓ Invalid histogram rejected: {str(e)[:50]}...")

    try:
        metrics.set_gauge("invalid_metric", value=1.0)
        print("❌ Should have raised ValueError")
    except ValueError as e:
        print(f"✓ Invalid gauge rejected: {str(e)[:50]}...")

    print()


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 20 + "Metrics Collection Test" + " " * 25 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n")

    tests = [
        test_imports,
        test_metrics_collector,
        test_counter_metrics,
        test_histogram_metrics,
        test_gauge_metrics,
        test_track_duration_context_manager,
        test_track_active_context_manager,
        test_track_duration_decorator,
        test_async_track_duration,
        test_track_errors_decorator,
        test_async_track_errors,
        test_combined_decorators,
        test_get_metrics_text,
        test_get_metrics_app,
        test_real_world_scenario,
        test_error_handling,
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
    print("✅ All metrics tests passed!")
    print("=" * 70)
    print("\nMetrics Collection Summary:")
    print("- Counter metrics: request_count, error_count, cache_hits/misses")
    print("- Histogram metrics: request_duration, token_usage, retrieval_time")
    print("- Gauge metrics: active_requests, cache_size, memory_usage")
    print("- MetricsCollector class with unified interface")
    print("- @track_duration decorator for automatic timing")
    print("- @track_errors decorator for error tracking")
    print("- Context managers for duration and active tracking")
    print("- Prometheus metrics endpoint")
    print("- Full async support")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
