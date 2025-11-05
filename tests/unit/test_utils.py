"""Tests for utility functions.

Tests all utility modules including:
- validators
- retry logic
- AWS helpers (mocked)
"""

import asyncio
import json
import time
from unittest.mock import Mock, patch

import pytest

# ============================================================================
# Validator Tests
# ============================================================================


class TestValidators:
    """Test validation utilities."""

    def test_validate_aws_region_valid(self):
        """Test validating valid AWS regions."""
        from utils.validators import validate_aws_region

        valid_regions = [
            "us-east-1",
            "us-west-2",
            "eu-west-1",
            "ap-southeast-1",
        ]

        for region in valid_regions:
            assert validate_aws_region(region) is True

    def test_validate_aws_region_invalid(self):
        """Test validating invalid AWS regions."""
        from utils.validators import ValidationError, validate_aws_region

        invalid_regions = [
            "invalid-region",
            "us-east-99",
            "",
            "UPPERCASE",
        ]

        for region in invalid_regions:
            with pytest.raises(ValidationError):
                validate_aws_region(region)

    def test_validate_model_id_valid(self):
        """Test validating valid Bedrock model IDs."""
        from utils.validators import validate_model_id

        valid_models = [
            "anthropic.claude-3-5-sonnet-20241022-v2:0",
            "amazon.titan-text-express-v1:0",
            "ai21.j2-ultra-v1",
        ]

        for model_id in valid_models:
            assert validate_model_id(model_id) is True

    def test_validate_model_id_invalid(self):
        """Test validating invalid model IDs."""
        from utils.validators import ValidationError, validate_model_id

        invalid_models = [
            "gpt-4",
            "invalid-model",
            "",
        ]

        for model_id in invalid_models:
            with pytest.raises(ValidationError):
                validate_model_id(model_id)

    def test_validate_s3_uri_valid(self):
        """Test validating and parsing valid S3 URIs."""
        from utils.validators import validate_s3_uri

        test_cases = [
            ("s3://my-bucket/file.txt", "my-bucket", "file.txt"),
            ("s3://data/path/to/file.csv", "data", "path/to/file.csv"),
        ]

        for uri, expected_bucket, expected_key in test_cases:
            bucket, key = validate_s3_uri(uri)
            assert bucket == expected_bucket
            assert key == expected_key

    def test_validate_s3_uri_invalid(self):
        """Test validating invalid S3 URIs."""
        from utils.validators import ValidationError, validate_s3_uri

        invalid_uris = [
            "https://example.com/file.txt",
            "s3://",
            "s3://bucket",
            "",
        ]

        for uri in invalid_uris:
            with pytest.raises(ValidationError):
                validate_s3_uri(uri)

    def test_validate_query_length_valid(self):
        """Test validating query lengths."""
        from utils.validators import validate_query_length

        assert validate_query_length("Hello") is True
        assert validate_query_length("x" * 100) is True
        assert validate_query_length("Valid query", max_length=100) is True

    def test_validate_query_length_invalid(self):
        """Test invalid query lengths."""
        from utils.validators import ValidationError, validate_query_length

        # Too short
        with pytest.raises(ValidationError):
            validate_query_length("")

        # Whitespace only
        with pytest.raises(ValidationError):
            validate_query_length("   ")

        # Too long
        with pytest.raises(ValidationError):
            validate_query_length("x" * 10001)

    def test_sanitize_input_removes_html(self):
        """Test HTML removal."""
        from utils.validators import sanitize_input

        test_cases = [
            ("<b>Bold</b>", "Bold"),
            ("<script>alert('xss')</script>Safe", "Safe"),
            ("Hello <div>World</div>", "Hello World"),
        ]

        for input_text, expected in test_cases:
            result = sanitize_input(input_text)
            assert result == expected

    def test_sanitize_input_sql_injection(self):
        """Test SQL injection detection."""
        from utils.validators import ValidationError, sanitize_input

        dangerous_inputs = [
            "SELECT * FROM users WHERE id = 1 OR 1=1--",
            "'; DROP TABLE users; --",
        ]

        for input_text in dangerous_inputs:
            with pytest.raises(ValidationError):
                sanitize_input(input_text)

    def test_sanitize_input_truncation(self):
        """Test input truncation."""
        from utils.validators import sanitize_input

        long_text = "x" * 1000
        result = sanitize_input(long_text, max_length=100)
        assert len(result) == 100

    def test_validate_json_schema_valid(self):
        """Test valid JSON schema validation."""
        from utils.validators import validate_json_schema

        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"},
            },
            "required": ["name"],
        }

        data = {"name": "John", "age": 30}
        assert validate_json_schema(data, schema) is True

    def test_validate_json_schema_invalid(self):
        """Test invalid JSON schema validation."""
        from utils.validators import ValidationError, validate_json_schema

        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
            },
            "required": ["name"],
        }

        # Missing required field
        data = {"age": 30}
        with pytest.raises(ValidationError):
            validate_json_schema(data, schema)


# ============================================================================
# Retry Tests
# ============================================================================


class TestRetry:
    """Test retry utilities."""

    def test_retry_success_no_retry(self):
        """Test successful execution without retry."""
        from utils.retry import retry_with_exponential_backoff

        call_count = 0

        @retry_with_exponential_backoff(max_attempts=3)
        def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"

        result = successful_function()
        assert result == "success"
        assert call_count == 1

    def test_retry_with_retries(self):
        """Test retry on transient failures."""
        from utils.retry import retry_with_exponential_backoff

        call_count = 0

        @retry_with_exponential_backoff(max_attempts=5, initial_delay=0.01)
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Transient error")
            return "success"

        result = flaky_function()
        assert result == "success"
        assert call_count == 3

    def test_retry_max_attempts(self):
        """Test failure after max attempts."""
        from utils.retry import retry_with_exponential_backoff

        call_count = 0

        @retry_with_exponential_backoff(max_attempts=3, initial_delay=0.01)
        def always_failing():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")

        with pytest.raises(ValueError):
            always_failing()

        assert call_count == 3

    def test_retry_specific_exceptions(self):
        """Test retry only on specific exceptions."""
        from utils.retry import retry_with_exponential_backoff

        class RetryableError(Exception):
            pass

        class NonRetryableError(Exception):
            pass

        @retry_with_exponential_backoff(
            max_attempts=5, initial_delay=0.01, exceptions=(RetryableError,)
        )
        def selective_function(should_retry: bool):
            if should_retry:
                raise RetryableError()
            raise NonRetryableError()

        # Retryable error - should retry
        with pytest.raises(RetryableError):
            selective_function(True)

        # Non-retryable error - should fail immediately
        call_count = 0

        @retry_with_exponential_backoff(
            max_attempts=5, initial_delay=0.01, exceptions=(RetryableError,)
        )
        def non_retry_function():
            nonlocal call_count
            call_count += 1
            raise NonRetryableError()

        with pytest.raises(NonRetryableError):
            non_retry_function()

        assert call_count == 1  # No retries

    def test_async_retry(self):
        """Test async retry decorator."""
        from utils.retry import async_retry_with_exponential_backoff

        call_count = 0

        @async_retry_with_exponential_backoff(max_attempts=3, initial_delay=0.01)
        async def async_flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Async error")
            return "async success"

        result = asyncio.run(async_flaky())
        assert result == "async success"
        assert call_count == 3

    def test_calculate_backoff_delay(self):
        """Test backoff delay calculation."""
        from utils.retry import calculate_backoff_delay

        # Without jitter
        delay1 = calculate_backoff_delay(1, initial_delay=1.0, jitter=False)
        delay2 = calculate_backoff_delay(2, initial_delay=1.0, jitter=False)
        delay3 = calculate_backoff_delay(3, initial_delay=1.0, jitter=False)

        assert delay1 == 1.0  # 1 * 2^0
        assert delay2 == 2.0  # 1 * 2^1
        assert delay3 == 4.0  # 1 * 2^2

        # Max delay
        delay_max = calculate_backoff_delay(10, initial_delay=1.0, max_delay=10.0, jitter=False)
        assert delay_max == 10.0

    def test_retry_context(self):
        """Test RetryContext."""
        from utils.retry import RetryContext

        call_count = 0
        retry_ctx = RetryContext(max_attempts=3, initial_delay=0.01)

        for attempt in retry_ctx:
            call_count += 1
            try:
                if call_count < 3:
                    raise ValueError("Error")
                result = "success"
                break
            except ValueError as e:
                retry_ctx.record_failure(e)
                if not retry_ctx.should_retry():
                    raise
                retry_ctx.wait()

        assert result == "success"
        assert call_count == 3


# ============================================================================
# AWS Helpers Tests (Mocked)
# ============================================================================


class TestAWSHelpers:
    """Test AWS helper functions with mocking."""

    def test_get_boto3_client(self, mock_aws_credentials):
        """Test creating boto3 client."""
        with patch("utils.aws_helpers.boto3.client") as mock_client:
            from utils.aws_helpers import get_boto3_client

            mock_client.return_value = Mock()
            client = get_boto3_client("s3")
            assert client is not None
            mock_client.assert_called_once()

    def test_get_bedrock_client(self, mock_bedrock_client):
        """Test getting Bedrock client."""
        with patch("utils.aws_helpers.boto3.client", return_value=mock_bedrock_client):
            from utils.aws_helpers import get_bedrock_client

            # Clear cache first
            get_bedrock_client.cache_clear()

            client = get_bedrock_client()
            assert client is not None

    def test_check_aws_credentials_valid(self, mock_aws_credentials):
        """Test checking valid AWS credentials."""
        with patch("utils.aws_helpers.get_boto3_client") as mock_get_client:
            from utils.aws_helpers import check_aws_credentials

            mock_sts = Mock()
            mock_sts.get_caller_identity.return_value = {"Account": "123456789012"}
            mock_get_client.return_value = mock_sts

            result = check_aws_credentials()
            assert result is True

    def test_check_aws_credentials_invalid(self):
        """Test checking invalid AWS credentials."""
        from botocore.exceptions import NoCredentialsError

        with patch("utils.aws_helpers.get_boto3_client") as mock_get_client:
            from utils.aws_helpers import check_aws_credentials

            mock_get_client.side_effect = NoCredentialsError()

            result = check_aws_credentials()
            assert result is False

    def test_get_aws_account_id(self, mock_aws_credentials):
        """Test getting AWS account ID."""
        with patch("utils.aws_helpers.get_boto3_client") as mock_get_client:
            from utils.aws_helpers import get_aws_account_id

            mock_sts = Mock()
            mock_sts.get_caller_identity.return_value = {"Account": "123456789012"}
            mock_get_client.return_value = mock_sts

            account_id = get_aws_account_id()
            assert account_id == "123456789012"

    def test_validate_s3_uri(self):
        """Test S3 URI validation and parsing."""
        from utils.validators import validate_s3_uri

        bucket, key = validate_s3_uri("s3://my-bucket/path/to/file.txt")
        assert bucket == "my-bucket"
        assert key == "path/to/file.txt"

    def test_get_secret_json(self, mock_secrets_manager):
        """Test getting JSON secret."""
        # Create secret
        secret_value = {"username": "admin", "password": "secret123"}
        mock_secrets_manager.create_secret(
            Name="test-secret", SecretString=json.dumps(secret_value)
        )

        with patch("utils.aws_helpers.get_boto3_client", return_value=mock_secrets_manager):
            from utils.aws_helpers import get_secret

            secret = get_secret("test-secret")
            assert secret == secret_value

    def test_put_secret(self, mock_secrets_manager):
        """Test putting secret."""
        with patch("utils.aws_helpers.get_boto3_client", return_value=mock_secrets_manager):
            from utils.aws_helpers import put_secret

            result = put_secret("new-secret", {"key": "value"})
            assert "ARN" in result

            # Verify secret was created
            response = mock_secrets_manager.get_secret_value(SecretId="new-secret")
            assert json.loads(response["SecretString"]) == {"key": "value"}


# ============================================================================
# Performance Tests
# ============================================================================


class TestPerformance:
    """Test utility function performance."""

    def test_sanitize_input_performance(self):
        """Test input sanitization performance."""
        from utils.validators import sanitize_input

        # Large input
        large_input = "x" * 10000

        start = time.time()
        for _ in range(100):
            sanitize_input(large_input, max_length=1000)
        duration = time.time() - start

        # Should complete in reasonable time
        assert duration < 1.0  # Less than 1 second for 100 iterations

    def test_validate_region_performance(self):
        """Test region validation performance."""
        from utils.validators import validate_aws_region

        start = time.time()
        for _ in range(1000):
            validate_aws_region("us-east-1")
        duration = time.time() - start

        # Should be very fast
        assert duration < 0.1  # Less than 100ms for 1000 iterations

    def test_retry_performance(self):
        """Test retry doesn't add significant overhead on success."""
        from utils.retry import retry_with_exponential_backoff

        @retry_with_exponential_backoff(max_attempts=3)
        def fast_function():
            return "success"

        start = time.time()
        for _ in range(100):
            fast_function()
        duration = time.time() - start

        # Should have minimal overhead
        assert duration < 0.1  # Less than 100ms for 100 iterations


# ============================================================================
# Edge Cases
# ============================================================================


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_string_validation(self):
        """Test empty string validation."""
        from utils.validators import ValidationError, validate_query_length

        with pytest.raises(ValidationError):
            validate_query_length("")

    def test_none_value_validation(self):
        """Test None value validation."""
        from utils.validators import ValidationError, validate_aws_region

        with pytest.raises(ValidationError):
            validate_aws_region(None)

    def test_unicode_handling(self):
        """Test unicode in sanitization."""
        from utils.validators import sanitize_input

        unicode_text = "Hello 世界 🌍"
        result = sanitize_input(unicode_text)
        assert "世界" in result
        assert "🌍" in result

    def test_very_long_input(self):
        """Test very long input handling."""
        from utils.validators import sanitize_input

        very_long = "x" * 1000000
        result = sanitize_input(very_long, max_length=1000)
        assert len(result) == 1000

    def test_nested_html(self):
        """Test nested HTML removal."""
        from utils.validators import sanitize_input

        nested = "<div><p><span>Nested</span></p></div>"
        result = sanitize_input(nested)
        assert "<" not in result
        assert "Nested" in result
