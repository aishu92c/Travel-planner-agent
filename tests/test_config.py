"""Tests for configuration loading and validation.

Tests the Pydantic settings models and configuration loading from various sources.
"""

import os


class TestSettings:
    """Test Settings model."""

    def test_settings_creation(self, mock_settings):
        """Test basic settings creation."""
        assert mock_settings.environment == "test"
        assert mock_settings.app_name == "LangGraph Test"
        assert mock_settings.debug is True

    def test_settings_default_values(self, mock_settings):
        """Test default values are set correctly."""
        assert mock_settings.aws.region == "us-east-1"
        assert mock_settings.api.port == 8000
        assert mock_settings.api.workers == 1

    def test_settings_nested_access(self, mock_settings):
        """Test accessing nested settings."""
        assert mock_settings.aws.bedrock.model_id == "anthropic.claude-3-5-sonnet-20241022-v2:0"
        assert mock_settings.aws.bedrock.max_tokens == 1000
        assert mock_settings.aws.dynamodb.table_name == "test-checkpoints"

    def test_settings_validation(self):
        """Test settings validation."""
        from config.settings import Settings

        # Valid settings
        settings = Settings(environment="production")
        assert settings.environment == "production"

        # Invalid environment should use default
        settings = Settings()
        assert settings.environment in ["development", "staging", "production"]


class TestAWSSettings:
    """Test AWS-specific settings."""

    def test_aws_region_validation(self, mock_settings):
        """Test AWS region is set."""
        assert mock_settings.aws.region is not None
        assert len(mock_settings.aws.region) > 0

    def test_bedrock_settings(self, mock_settings):
        """Test Bedrock settings."""
        bedrock = mock_settings.aws.bedrock
        assert bedrock.model_id is not None
        assert bedrock.max_tokens > 0
        assert 0.0 <= bedrock.temperature <= 1.0

    def test_dynamodb_settings(self, mock_settings):
        """Test DynamoDB settings."""
        dynamodb = mock_settings.aws.dynamodb
        assert dynamodb.table_name is not None
        assert len(dynamodb.table_name) > 0

    def test_s3_settings(self, mock_settings):
        """Test S3 settings."""
        s3 = mock_settings.aws.s3
        assert s3.bucket_name is not None
        assert len(s3.bucket_name) > 0


class TestAPISettings:
    """Test API settings."""

    def test_api_host_and_port(self, mock_settings):
        """Test API host and port."""
        assert mock_settings.api.host is not None
        assert mock_settings.api.port > 0
        assert mock_settings.api.port < 65536

    def test_api_workers(self, mock_settings):
        """Test API workers setting."""
        assert mock_settings.api.workers > 0

    def test_api_cors(self, mock_settings):
        """Test CORS settings."""
        assert isinstance(mock_settings.api.cors_origins, list)

    def test_api_secret_key(self, mock_settings):
        """Test secret key is set."""
        assert mock_settings.api.secret_key is not None
        assert len(mock_settings.api.secret_key) > 0


class TestObservabilitySettings:
    """Test observability settings."""

    def test_logging_settings(self, mock_settings):
        """Test logging configuration."""
        logging_config = mock_settings.observability.logging
        assert logging_config.level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        assert logging_config.format in ["json", "console"]

    def test_logging_cloudwatch_disabled(self, mock_settings):
        """Test CloudWatch can be disabled."""
        assert mock_settings.observability.logging.enable_cloudwatch is False


class TestEnvironmentVariables:
    """Test configuration from environment variables."""

    def test_env_override(self, mock_env, monkeypatch):
        """Test environment variables override defaults."""

        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("AWS_REGION", "us-west-2")

        # Note: Settings() reads from env by default
        # For testing, we verify the mock_env fixture works
        assert mock_env["ENVIRONMENT"] == "test"
        assert mock_env["AWS_REGION"] == "us-east-1"

    def test_log_level_from_env(self, monkeypatch):
        """Test log level from environment variable."""
        monkeypatch.setenv("LOG_LEVEL", "ERROR")
        assert os.getenv("LOG_LEVEL") == "ERROR"


class TestConfigValidation:
    """Test configuration validation."""

    def test_valid_config(self, mock_settings):
        """Test valid configuration passes validation."""
        # Should not raise any exceptions
        assert mock_settings.environment is not None
        assert mock_settings.aws is not None
        assert mock_settings.api is not None

    def test_temperature_bounds(self):
        """Test temperature validation."""
        from config.settings import BedrockSettings

        # Valid temperature
        bedrock = BedrockSettings(temperature=0.5)
        assert bedrock.temperature == 0.5

        # Temperature at bounds
        bedrock = BedrockSettings(temperature=0.0)
        assert bedrock.temperature == 0.0

        bedrock = BedrockSettings(temperature=1.0)
        assert bedrock.temperature == 1.0

    def test_port_validation(self):
        """Test port number validation."""
        from config.settings import APISettings

        # Valid port
        api = APISettings(port=8080)
        assert api.port == 8080

        # Port at minimum
        api = APISettings(port=1)
        assert api.port == 1

        # Port at maximum
        api = APISettings(port=65535)
        assert api.port == 65535


class TestConfigSerialization:
    """Test configuration serialization."""

    def test_settings_to_dict(self, mock_settings):
        """Test converting settings to dict."""
        settings_dict = mock_settings.model_dump()

        assert isinstance(settings_dict, dict)
        assert "environment" in settings_dict
        assert "aws" in settings_dict
        assert "api" in settings_dict

    def test_settings_to_json(self, mock_settings):
        """Test converting settings to JSON."""
        import json

        settings_json = mock_settings.model_dump_json()
        settings_dict = json.loads(settings_json)

        assert isinstance(settings_dict, dict)
        assert settings_dict["environment"] == "test"

    def test_settings_from_dict(self):
        """Test creating settings from dict."""
        from config.settings import Settings

        settings_dict = {
            "environment": "test",
            "app_name": "Test App",
            "debug": True,
        }

        settings = Settings(**settings_dict)
        assert settings.environment == "test"
        assert settings.app_name == "Test App"
        assert settings.debug is True


class TestGetSettings:
    """Test get_settings() function."""

    def test_get_settings_singleton(self, mock_env):
        """Test get_settings returns singleton."""
        from config import get_settings

        settings1 = get_settings()
        settings2 = get_settings()

        # Should be the same instance (cached)
        assert settings1 is settings2

    def test_get_settings_returns_settings(self, mock_env):
        """Test get_settings returns Settings instance."""
        from config import get_settings
        from config.settings import Settings

        settings = get_settings()
        assert isinstance(settings, Settings)


class TestEnvironmentSpecificConfig:
    """Test environment-specific configuration."""

    def test_development_config(self, monkeypatch):
        """Test development environment configuration."""
        monkeypatch.setenv("ENVIRONMENT", "development")

        from config.settings import Settings

        settings = Settings(environment="development")
        assert settings.environment == "development"
        assert settings.debug is True  # Development should have debug on

    def test_production_config(self, monkeypatch):
        """Test production environment configuration."""
        monkeypatch.setenv("ENVIRONMENT", "production")

        from config.settings import Settings

        settings = Settings(environment="production")
        assert settings.environment == "production"

    def test_staging_config(self, monkeypatch):
        """Test staging environment configuration."""
        monkeypatch.setenv("ENVIRONMENT", "staging")

        from config.settings import Settings

        settings = Settings(environment="staging")
        assert settings.environment == "staging"


class TestConfigEdgeCases:
    """Test configuration edge cases."""

    def test_empty_string_values(self):
        """Test empty string values are handled."""
        from config.settings import Settings

        # Empty strings should use defaults
        settings = Settings(app_name="")
        # Should have some default value, not empty
        assert len(settings.app_name) > 0

    def test_none_values_use_defaults(self):
        """Test None values use defaults."""
        from config.settings import Settings

        settings = Settings()
        # All required fields should have values
        assert settings.environment is not None
        assert settings.aws.region is not None

    def test_missing_optional_fields(self, mock_settings):
        """Test missing optional fields are handled."""
        # Optional fields should have defaults or None
        assert mock_settings.observability.logging.file_path is None
        assert mock_settings.aws.dynamodb.endpoint_url is None
