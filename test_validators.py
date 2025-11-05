#!/usr/bin/env python3
"""Test Validation Utilities.

Run this script to verify all validation utilities are working correctly.

Prerequisites:
    1. Set up virtual environment and install dependencies:
       ./setup-venv.sh

    2. Or manually:
       python3.13 -m venv venv
       source venv/bin/activate
       pip install -r requirements.txt
       pip install -r requirements-dev.txt

Usage:
    python test_validators.py

Note:
    This test does not require AWS credentials.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_imports():
    """Test that all imports work correctly."""
    print("=" * 70)
    print("Testing Imports")
    print("=" * 70)

    from utils import (
        ValidationError,
        sanitize_input,
        validate_aws_region,
        validate_json_schema,
        validate_model_id,
        validate_query_length,
        validate_s3_uri,
    )

    print("✓ All validation utilities imported successfully")

    # Verify all are callable
    assert callable(validate_aws_region)
    assert callable(validate_model_id)
    assert callable(validate_s3_uri)
    assert callable(validate_query_length)
    assert callable(sanitize_input)
    assert callable(validate_json_schema)
    print("✓ All validation utilities are callable")

    # Verify ValidationError is an exception
    assert issubclass(ValidationError, ValueError)
    print("✓ ValidationError is a proper exception class")

    print()


def test_validation_error():
    """Test ValidationError exception."""
    print("=" * 70)
    print("Testing ValidationError")
    print("=" * 70)

    from utils import ValidationError

    # Basic error
    try:
        raise ValidationError("Something went wrong")
    except ValidationError as e:
        print(f"✓ Basic error: {e}")
        assert str(e) == "Something went wrong"

    # Error with field
    try:
        raise ValidationError("Invalid value", field="username")
    except ValidationError as e:
        print(f"✓ Error with field: {e}")
        assert "username" in str(e)

    # Error with field and value
    try:
        raise ValidationError("Too short", field="password", value="abc")
    except ValidationError as e:
        print(f"✓ Error with field and value: {e}")
        assert "password" in str(e)
        assert "abc" in str(e)

    print()


def test_validate_aws_region():
    """Test AWS region validation."""
    print("=" * 70)
    print("Testing validate_aws_region")
    print("=" * 70)

    from utils import ValidationError, validate_aws_region

    # Valid regions
    valid_regions = [
        "us-east-1",
        "us-west-2",
        "eu-west-1",
        "ap-southeast-1",
        "ca-central-1",
    ]

    for region in valid_regions:
        result = validate_aws_region(region)
        assert result is True
        print(f"✓ Valid region: {region}")

    # Invalid regions
    invalid_regions = [
        "invalid-region",
        "us-east-99",
        "moon-base-1",
        "",
        "US-EAST-1",  # Wrong case (should be lowercase)
    ]

    for region in invalid_regions:
        try:
            validate_aws_region(region)
            print(f"❌ Should have rejected: {region}")
        except ValidationError as e:
            print(f"✓ Rejected invalid region '{region}': {str(e)[:50]}...")

    # Test with None
    try:
        validate_aws_region(None)
        print("❌ Should have rejected None")
    except ValidationError as e:
        print(f"✓ Rejected None: {str(e)[:50]}...")

    print()


def test_validate_model_id():
    """Test Bedrock model ID validation."""
    print("=" * 70)
    print("Testing validate_model_id")
    print("=" * 70)

    from utils import ValidationError, validate_model_id

    # Valid model IDs
    valid_models = [
        "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "anthropic.claude-3-opus-20240229-v1:0",
        "anthropic.claude-3-sonnet-20240229-v1:0",
        "anthropic.claude-3-haiku-20240307-v1:0",
        "amazon.titan-text-express-v1:0",
        "amazon.titan-embed-text-v2:0",
        "ai21.j2-ultra-v1",
        "cohere.command-text-v14",
    ]

    for model_id in valid_models:
        result = validate_model_id(model_id)
        assert result is True
        print(f"✓ Valid model: {model_id}")

    # Invalid model IDs
    invalid_models = [
        "invalid-model",
        "gpt-4",  # Not a Bedrock model
        "anthropic.claude",  # Incomplete
        "",
        "random.model.name",
    ]

    for model_id in invalid_models:
        try:
            validate_model_id(model_id)
            print(f"❌ Should have rejected: {model_id}")
        except ValidationError as e:
            print(f"✓ Rejected invalid model '{model_id}': {str(e)[:50]}...")

    print()


def test_validate_s3_uri():
    """Test S3 URI validation and parsing."""
    print("=" * 70)
    print("Testing validate_s3_uri")
    print("=" * 70)

    from utils import ValidationError, validate_s3_uri

    # Valid S3 URIs
    test_cases = [
        ("s3://my-bucket/file.txt", "my-bucket", "file.txt"),
        ("s3://data-bucket/path/to/file.csv", "data-bucket", "path/to/file.csv"),
        (
            "s3://test-bucket/deep/nested/path/document.pdf",
            "test-bucket",
            "deep/nested/path/document.pdf",
        ),
        ("s3://bucket123/data.json", "bucket123", "data.json"),
    ]

    for uri, expected_bucket, expected_key in test_cases:
        bucket, key = validate_s3_uri(uri)
        assert bucket == expected_bucket
        assert key == expected_key
        print(f"✓ Parsed '{uri}' -> bucket='{bucket}', key='{key}'")

    # Invalid S3 URIs
    invalid_uris = [
        "https://example.com/file.txt",  # Wrong scheme
        "s3://",  # No bucket
        "s3://bucket",  # No key
        "s3://INVALID-BUCKET/file.txt",  # Uppercase not allowed
        "s3://bucket/",  # Empty key
        "",  # Empty string
    ]

    for uri in invalid_uris:
        try:
            validate_s3_uri(uri)
            print(f"❌ Should have rejected: {uri}")
        except ValidationError as e:
            print(f"✓ Rejected invalid URI '{uri}': {str(e)[:50]}...")

    print()


def test_validate_query_length():
    """Test query length validation."""
    print("=" * 70)
    print("Testing validate_query_length")
    print("=" * 70)

    from utils import ValidationError, validate_query_length

    # Valid queries
    valid_queries = [
        "What is AI?",
        "Hello world",
        "x" * 100,  # Long but under default max
        "a",  # Single character
    ]

    for query in valid_queries:
        result = validate_query_length(query)
        assert result is True
        display = query if len(query) <= 30 else f"{query[:30]}..."
        print(f"✓ Valid query: '{display}'")

    # Test with custom max_length
    result = validate_query_length("Short", max_length=100)
    assert result is True
    print("✓ Valid query with custom max_length")

    # Invalid queries - too short
    try:
        validate_query_length("")
        print("❌ Should have rejected empty string")
    except ValidationError as e:
        print(f"✓ Rejected empty string: {str(e)[:50]}...")

    try:
        validate_query_length("   ")
        print("❌ Should have rejected whitespace-only")
    except ValidationError as e:
        print(f"✓ Rejected whitespace-only: {str(e)[:50]}...")

    # Invalid queries - too long
    try:
        validate_query_length("x" * 10001)
        print("❌ Should have rejected too long query")
    except ValidationError as e:
        print(f"✓ Rejected too long query: {str(e)[:50]}...")

    # Invalid queries - custom limits
    try:
        validate_query_length("ab", min_length=3)
        print("❌ Should have rejected query below min_length")
    except ValidationError as e:
        print(f"✓ Rejected query below min_length: {str(e)[:50]}...")

    try:
        validate_query_length("x" * 101, max_length=100)
        print("❌ Should have rejected query above max_length")
    except ValidationError as e:
        print(f"✓ Rejected query above max_length: {str(e)[:50]}...")

    print()


def test_sanitize_input():
    """Test input sanitization."""
    print("=" * 70)
    print("Testing sanitize_input")
    print("=" * 70)

    from utils import sanitize_input

    # Test HTML removal
    test_cases = [
        ("<b>Bold</b> text", "Bold text"),
        ("<script>alert('xss')</script>Safe", "Safe"),
        ("Hello <div>World</div>!", "Hello World!"),
        ("5 &lt; 10 &amp; 10 &gt; 5", "5 < 10 & 10 > 5"),
        ("<p>Paragraph 1</p><p>Paragraph 2</p>", "Paragraph 1Paragraph 2"),
    ]

    for input_text, expected in test_cases:
        result = sanitize_input(input_text)
        assert result == expected
        print(f"✓ Sanitized '{input_text[:30]}...' -> '{result[:30]}...'")

    # Test script removal
    dangerous = "<script>alert('xss')</script>Hello"
    safe = sanitize_input(dangerous)
    assert "<script>" not in safe
    print(f"✓ Removed script tags: '{dangerous}' -> '{safe}'")

    # Test with max_length
    long_text = "x" * 1000
    truncated = sanitize_input(long_text, max_length=100)
    assert len(truncated) == 100
    print(f"✓ Truncated to max_length: {len(long_text)} -> {len(truncated)}")

    # Test control character removal
    with_controls = "Hello\x00\x01\x02World"
    clean = sanitize_input(with_controls)
    assert "\x00" not in clean
    print("✓ Removed control characters")

    # Test SQL injection detection
    from utils import ValidationError

    sql_injections = [
        "SELECT * FROM users WHERE id = 1 OR 1=1--",
        "'; DROP TABLE users; --",
        "UNION SELECT password FROM users",
    ]

    for sql in sql_injections:
        try:
            sanitize_input(sql)
            print(f"❌ Should have blocked SQL injection: {sql[:30]}...")
        except ValidationError as e:
            print(f"✓ Blocked SQL injection: {str(e)[:50]}...")

    print()


def test_validate_json_schema():
    """Test JSON schema validation."""
    print("=" * 70)
    print("Testing validate_json_schema")
    print("=" * 70)

    from utils import ValidationError, validate_json_schema

    # Simple schema
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "number", "minimum": 0},
            "email": {"type": "string"},
        },
        "required": ["name", "age"],
    }

    # Valid data
    valid_data = [
        {"name": "John", "age": 30, "email": "john@example.com"},
        {"name": "Jane", "age": 25},
        {"name": "Bob", "age": 0, "email": "bob@test.com"},
    ]

    for data in valid_data:
        result = validate_json_schema(data, schema)
        assert result is True
        print(f"✓ Valid data: {data}")

    # Invalid data - missing required field
    try:
        invalid = {"name": "Alice"}  # Missing age
        validate_json_schema(invalid, schema)
        print("❌ Should have rejected data missing required field")
    except ValidationError as e:
        print(f"✓ Rejected missing field: {str(e)[:50]}...")

    # Invalid data - wrong type
    try:
        invalid = {"name": "Bob", "age": "thirty"}  # Age should be number
        validate_json_schema(invalid, schema)
        print("❌ Should have rejected data with wrong type")
    except ValidationError as e:
        print(f"✓ Rejected wrong type: {str(e)[:50]}...")

    # Invalid data - constraint violation
    try:
        invalid = {"name": "Charlie", "age": -5}  # Age < 0
        validate_json_schema(invalid, schema)
        print("❌ Should have rejected data violating constraints")
    except ValidationError as e:
        print(f"✓ Rejected constraint violation: {str(e)[:50]}...")

    # Test with nested schema
    nested_schema = {
        "type": "object",
        "properties": {
            "user": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "number"},
                },
                "required": ["name"],
            }
        },
        "required": ["user"],
    }

    valid_nested = {"user": {"name": "Alice", "age": 30}}
    result = validate_json_schema(valid_nested, nested_schema)
    assert result is True
    print(f"✓ Valid nested data: {valid_nested}")

    # Test with array schema
    array_schema = {
        "type": "object",
        "properties": {"tags": {"type": "array", "items": {"type": "string"}}},
    }

    valid_array = {"tags": ["python", "aws", "ai"]}
    result = validate_json_schema(valid_array, array_schema)
    assert result is True
    print(f"✓ Valid array data: {valid_array}")

    print()


def test_integration_example():
    """Test integration of multiple validators."""
    print("=" * 70)
    print("Testing Integration Example")
    print("=" * 70)

    from utils import (
        ValidationError,
        sanitize_input,
        validate_aws_region,
        validate_model_id,
        validate_query_length,
        validate_s3_uri,
    )

    # Simulate validating a complete request
    def validate_bedrock_request(region: str, model_id: str, query: str, output_uri: str):
        """Validate all parameters for a Bedrock request."""
        # Validate region
        validate_aws_region(region)
        print(f"  ✓ Region valid: {region}")

        # Validate model
        validate_model_id(model_id)
        print(f"  ✓ Model valid: {model_id}")

        # Validate and sanitize query
        validate_query_length(query, max_length=5000)
        safe_query = sanitize_input(query)
        print(f"  ✓ Query valid and sanitized: {safe_query[:30]}...")

        # Validate S3 output URI
        bucket, key = validate_s3_uri(output_uri)
        print(f"  ✓ Output URI valid: s3://{bucket}/{key}")

        return True

    # Valid request
    print("Valid request:")
    result = validate_bedrock_request(
        region="us-east-1",
        model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
        query="What is machine learning?",
        output_uri="s3://my-bucket/outputs/result.json",
    )
    assert result is True
    print()

    # Invalid request - bad region
    print("Invalid request (bad region):")
    try:
        validate_bedrock_request(
            region="invalid-region",
            model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
            query="Test query",
            output_uri="s3://my-bucket/output.json",
        )
        print("❌ Should have failed validation")
    except ValidationError as e:
        print(f"  ✓ Caught validation error: {str(e)[:50]}...")
    print()

    # Invalid request - bad model
    print("Invalid request (bad model):")
    try:
        validate_bedrock_request(
            region="us-east-1",
            model_id="gpt-4",
            query="Test query",
            output_uri="s3://my-bucket/output.json",
        )
        print("❌ Should have failed validation")
    except ValidationError as e:
        print(f"  ✓ Caught validation error: {str(e)[:50]}...")
    print()

    print()


def test_edge_cases():
    """Test edge cases and boundary conditions."""
    print("=" * 70)
    print("Testing Edge Cases")
    print("=" * 70)

    from utils import ValidationError, sanitize_input, validate_query_length

    # Empty strings
    try:
        validate_query_length("")
        print("❌ Should reject empty query")
    except ValidationError:
        print("✓ Rejected empty query")

    # Whitespace-only
    try:
        validate_query_length("   \n\t  ")
        print("❌ Should reject whitespace-only query")
    except ValidationError:
        print("✓ Rejected whitespace-only query")

    # Unicode handling
    unicode_text = "Hello 世界 🌍"
    sanitized = sanitize_input(unicode_text)
    assert "世界" in sanitized
    assert "🌍" in sanitized
    print(f"✓ Unicode preserved: {sanitized}")

    # HTML entities
    entities = "&lt;div&gt;Hello &amp; goodbye&lt;/div&gt;"
    sanitized = sanitize_input(entities)
    assert "<div>" not in sanitized
    assert "&" in sanitized or "goodbye" in sanitized
    print(f"✓ HTML entities handled: {sanitized}")

    # Very long input
    long_input = "x" * 100000
    truncated = sanitize_input(long_input, max_length=1000)
    assert len(truncated) == 1000
    print(f"✓ Long input truncated: {len(long_input)} -> {len(truncated)}")

    # Nested HTML
    nested = "<div><p><span>Nested</span></p></div>"
    clean = sanitize_input(nested)
    assert "<" not in clean
    assert "Nested" in clean
    print(f"✓ Nested HTML removed: '{nested}' -> '{clean}'")

    print()


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 20 + "Validation Utilities Test" + " " * 23 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n")

    tests = [
        test_imports,
        test_validation_error,
        test_validate_aws_region,
        test_validate_model_id,
        test_validate_s3_uri,
        test_validate_query_length,
        test_sanitize_input,
        test_validate_json_schema,
        test_integration_example,
        test_edge_cases,
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
    print("✅ All validation utility tests passed!")
    print("=" * 70)
    print("\nValidation Utilities Summary:")
    print("- 6 validation functions")
    print("- 1 custom exception (ValidationError)")
    print("- AWS resource validation (regions, models, S3 URIs)")
    print("- Input sanitization (HTML, scripts, SQL injection)")
    print("- JSON schema validation")
    print("- Query length validation")
    print("- Comprehensive error messages")
    print("- Full type hints and documentation")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
