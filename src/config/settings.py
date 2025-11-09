"""Configuration Management using Pydantic Settings.

This module provides a comprehensive configuration system that:
- Loads settings from environment variables and .env files
- Validates all configuration values
- Supports multiple environments (dev, staging, prod)
- Provides sensible defaults for all settings
- Type-safe configuration access

Example:
    >>> from config.settings import get_settings
    >>> settings = get_settings()
    >>> print(settings.aws.region)
    >>> print(settings.api.host)
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, ValidationInfo, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AWSSettings(BaseSettings):
    """AWS service configuration."""

    region: str = Field(
        default="us-east-1",
        description="AWS region for all services",
    )
    account_id: str | None = Field(
        default=None,
        description="AWS account ID (optional, can be retrieved dynamically)",
    )

    # AWS Bedrock
    bedrock_model_id: str = Field(
        default="anthropic.claude-3-5-sonnet-20241022-v2:0",
        description="AWS Bedrock model ID for LLM calls",
    )
    bedrock_runtime_region: str | None = Field(
        default=None,
        description="Bedrock runtime region (defaults to main region)",
    )

    # DynamoDB
    dynamodb_endpoint_url: str | None = Field(
        default=None,
        description="Custom DynamoDB endpoint (for local development)",
    )

    # S3
    s3_bucket_artifacts: str = Field(
        default="langgraph-artifacts",
        description="S3 bucket for storing artifacts",
    )
    s3_bucket_documents: str = Field(
        default="langgraph-documents",
        description="S3 bucket for storing documents",
    )

    # Secrets Manager
    secrets_manager_prefix: str = Field(
        default="langgraph/",
        description="Prefix for secrets in AWS Secrets Manager",
    )

    @field_validator("bedrock_runtime_region")
    @classmethod
    def set_bedrock_region(cls, v: str | None, info: ValidationInfo) -> str:
        """Default bedrock_runtime_region to main region if not set."""
        if v is None and info.data and "region" in info.data:
            return str(info.data["region"])
        return v or "us-east-1"

    model_config = SettingsConfigDict(env_prefix="AWS_")


class APISettings(BaseSettings):
    """API server configuration."""

    host: str = Field(
        default="0.0.0.0",  # nosec B104 - Required for Docker/cloud deployments
        description="API server host",
    )
    port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="API server port",
    )
    workers: int = Field(
        default=4,
        ge=1,
        le=32,
        description="Number of uvicorn worker processes",
    )
    reload: bool = Field(
        default=False,
        description="Enable auto-reload for development",
    )

    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins",
    )
    cors_allow_credentials: bool = Field(
        default=True,
        description="Allow credentials in CORS requests",
    )

    # Security
    api_key_header: str = Field(
        default="X-API-Key",
        description="Header name for API key authentication",
    )
    secret_key: str = Field(
        default="change-me-in-production-with-secure-key",
        min_length=32,
        description="Secret key for JWT signing (MUST change in production)",
    )
    access_token_expire_minutes: int = Field(
        default=60,
        ge=1,
        description="JWT access token expiration time in minutes",
    )

    # Rate Limiting
    rate_limit_enabled: bool = Field(
        default=True,
        description="Enable rate limiting",
    )
    rate_limit_requests: int = Field(
        default=100,
        ge=1,
        description="Number of requests allowed per window",
    )
    rate_limit_window_seconds: int = Field(
        default=60,
        ge=1,
        description="Rate limit time window in seconds",
    )

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Warn if using default secret key."""
        if v == "change-me-in-production":
            import warnings

            warnings.warn(
                "Using default SECRET_KEY! Change this in production!",
                UserWarning,
                stacklevel=2,
            )
        return v

    model_config = SettingsConfigDict(env_prefix="API_")


class DatabaseSettings(BaseSettings):
    """Database configuration for DynamoDB."""

    # DynamoDB Table Names
    agents_table: str = Field(
        default="langgraph-agents",
        description="DynamoDB table for agent state",
    )
    checkpoints_table: str = Field(
        default="langgraph-checkpoints",
        description="DynamoDB table for LangGraph checkpoints",
    )
    cache_table: str = Field(
        default="langgraph-cache",
        description="DynamoDB table for caching",
    )

    # Table Configuration
    read_capacity_units: int = Field(
        default=5,
        ge=1,
        description="DynamoDB read capacity units (on-demand if 0)",
    )
    write_capacity_units: int = Field(
        default=5,
        ge=1,
        description="DynamoDB write capacity units (on-demand if 0)",
    )
    billing_mode: Literal["PROVISIONED", "PAY_PER_REQUEST"] = Field(
        default="PAY_PER_REQUEST",
        description="DynamoDB billing mode",
    )

    # Connection Settings
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of retry attempts",
    )
    timeout_seconds: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Connection timeout in seconds",
    )

    model_config = SettingsConfigDict(env_prefix="DB_")


class VectorDBSettings(BaseSettings):
    """Vector database configuration."""

    provider: Literal["chromadb", "faiss", "pinecone", "weaviate"] = Field(
        default="chromadb",
        description="Vector database provider",
    )

    # ChromaDB Settings
    chroma_host: str = Field(
        default="localhost",
        description="ChromaDB host",
    )
    chroma_port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="ChromaDB port",
    )
    chroma_collection: str = Field(
        default="langgraph-documents",
        description="ChromaDB collection name",
    )

    # FAISS Settings
    faiss_index_path: str = Field(
        default="./data/faiss_index",
        description="Path to FAISS index file",
    )

    # Embedding Settings
    embedding_model: str = Field(
        default="amazon.titan-embed-text-v2:0",
        description="Embedding model ID",
    )
    embedding_dimension: int = Field(
        default=1024,
        ge=128,
        le=4096,
        description="Embedding vector dimension",
    )

    # Search Settings
    top_k: int = Field(
        default=5,
        ge=1,
        le=100,
        description="Number of documents to retrieve",
    )
    similarity_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score threshold",
    )

    model_config = SettingsConfigDict(env_prefix="VECTORDB_")


class CacheSettings(BaseSettings):
    """Cache configuration for Redis."""

    enabled: bool = Field(
        default=True,
        description="Enable caching",
    )
    provider: Literal["redis", "memory"] = Field(
        default="redis",
        description="Cache provider",
    )

    # Redis Settings
    redis_host: str = Field(
        default="localhost",
        description="Redis host",
    )
    redis_port: int = Field(
        default=6379,
        ge=1,
        le=65535,
        description="Redis port",
    )
    redis_db: int = Field(
        default=0,
        ge=0,
        le=15,
        description="Redis database number",
    )
    redis_password: str | None = Field(
        default=None,
        description="Redis password (optional)",
    )
    redis_ssl: bool = Field(
        default=False,
        description="Use SSL for Redis connection",
    )

    # Cache Settings
    ttl_seconds: int = Field(
        default=3600,
        ge=0,
        description="Cache TTL in seconds (0 = no expiration)",
    )
    max_memory_mb: int = Field(
        default=512,
        ge=64,
        le=8192,
        description="Maximum cache memory in MB",
    )

    # Semantic Cache Settings
    semantic_cache_enabled: bool = Field(
        default=True,
        description="Enable semantic caching",
    )
    semantic_similarity_threshold: float = Field(
        default=0.95,
        ge=0.0,
        le=1.0,
        description="Similarity threshold for semantic cache hits",
    )

    model_config = SettingsConfigDict(env_prefix="CACHE_")


class LangGraphSettings(BaseSettings):
    """LangGraph configuration."""

    # Checkpoint Backend
    checkpoint_backend: Literal["dynamodb", "memory", "sqlite"] = Field(
        default="dynamodb",
        description="Checkpoint storage backend",
    )
    checkpoint_namespace: str = Field(
        default="langgraph",
        description="Namespace for checkpoints",
    )

    # Execution Limits
    max_iterations: int = Field(
        default=25,
        ge=1,
        le=100,
        description="Maximum iterations per agent execution",
    )
    max_execution_time_seconds: int = Field(
        default=300,
        ge=1,
        le=3600,
        description="Maximum execution time in seconds",
    )

    # Concurrency
    max_concurrent_executions: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum concurrent agent executions",
    )

    # Streaming
    stream_mode: Literal["values", "updates", "debug"] = Field(
        default="values",
        description="Stream mode for agent responses",
    )

    model_config = SettingsConfigDict(env_prefix="LANGGRAPH_")


class AgentSettings(BaseSettings):
    """Agent configuration for LLM calls."""

    # Model Parameters
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="LLM temperature for generation",
    )
    max_tokens: int = Field(
        default=4096,
        ge=1,
        le=200000,
        description="Maximum tokens for LLM response",
    )
    top_p: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Top-p sampling parameter",
    )

    # Timeouts & Retries
    timeout_seconds: int = Field(
        default=60,
        ge=1,
        le=300,
        description="Timeout for LLM calls in seconds",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts for failed calls",
    )
    retry_delay_seconds: float = Field(
        default=1.0,
        ge=0.1,
        le=10.0,
        description="Initial delay between retries (exponential backoff)",
    )

    # Context Management
    max_context_length: int = Field(
        default=100000,
        ge=1000,
        le=200000,
        description="Maximum context length in tokens",
    )

    # Tool Configuration
    max_tool_iterations: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum tool call iterations",
    )

    model_config = SettingsConfigDict(env_prefix="AGENT_")


class ObservabilitySettings(BaseSettings):
    """Observability and monitoring configuration."""

    # Tracing
    tracing_enabled: bool = Field(
        default=True,
        description="Enable OpenTelemetry tracing",
    )
    tracing_endpoint: str | None = Field(
        default=None,
        description="OpenTelemetry collector endpoint",
    )
    tracing_sample_rate: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Trace sampling rate (1.0 = 100%)",
    )

    # Metrics
    metrics_enabled: bool = Field(
        default=True,
        description="Enable Prometheus metrics",
    )
    metrics_port: int = Field(
        default=9090,
        ge=1,
        le=65535,
        description="Prometheus metrics port",
    )

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Application log level",
    )
    log_format: Literal["json", "text"] = Field(
        default="json",
        description="Log output format",
    )

    # CloudWatch
    cloudwatch_enabled: bool = Field(
        default=False,
        description="Enable CloudWatch logging",
    )
    cloudwatch_log_group: str = Field(
        default="/aws/langgraph/application",
        description="CloudWatch log group name",
    )

    model_config = SettingsConfigDict(env_prefix="OBSERVABILITY_")


class LLMSettings(BaseSettings):
    """Language Model configuration for LLM calls.

    This class manages LLM-specific settings including API keys, model names,
    and generation parameters.
    """

    # API Keys
    openai_api_key: str | None = Field(
        default=None,
        description="OpenAI API key (required for OpenAI models)",
    )
    langsmith_api_key: str | None = Field(
        default=None,
        description="LangSmith API key (optional, for debugging)",
    )
    anthropic_api_key: str | None = Field(
        default=None,
        description="Anthropic API key (for Claude models)",
    )

    # Model Configuration
    model_name: str = Field(
        default="gpt-4-turbo-preview",
        description="Model name to use for LLM calls",
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for generation (0.0-2.0)",
    )
    max_tokens: int = Field(
        default=2000,
        ge=1,
        le=200000,
        description="Maximum tokens in response",
    )
    top_p: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Top-p sampling parameter",
    )
    frequency_penalty: float = Field(
        default=0.0,
        ge=-2.0,
        le=2.0,
        description="Frequency penalty for repeated tokens",
    )
    presence_penalty: float = Field(
        default=0.0,
        ge=-2.0,
        le=2.0,
        description="Presence penalty for token diversity",
    )

    # Application Settings
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Logging format string",
    )

    # Cache Configuration (for Phase 4)
    cache_enabled: bool = Field(
        default=False,
        description="Enable response caching",
    )
    cache_ttl: int = Field(
        default=3600,
        ge=0,
        description="Cache time-to-live in seconds",
    )

    # Cost Tracking (for Phase 2)
    track_token_usage: bool = Field(
        default=True,
        description="Track and log token usage for cost monitoring",
    )

    # Timeouts & Retries
    timeout_seconds: int = Field(
        default=60,
        ge=1,
        description="Timeout for LLM calls",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        description="Maximum retry attempts",
    )

    @field_validator("openai_api_key")
    @classmethod
    def validate_openai_key(cls, v: str | None, info: ValidationInfo) -> str | None:
        """Validate that OpenAI API key is set if using OpenAI models."""
        if info.data and "model_name" in info.data:
            model_name = str(info.data.get("model_name", "")).lower()
            if "gpt" in model_name and not v:
                raise ValueError(
                    "OPENAI_API_KEY is required when using GPT models. "
                    "Set it in .env file: OPENAI_API_KEY=sk-..."
                )
        return v

    model_config = SettingsConfigDict(env_prefix="LLM_")


class FeatureFlags(BaseSettings):
    """Feature flags for enabling/disabling features."""

    # Core Features
    enable_rag: bool = Field(
        default=True,
        description="Enable RAG pipeline",
    )
    enable_caching: bool = Field(
        default=True,
        description="Enable caching layer",
    )
    enable_streaming: bool = Field(
        default=True,
        description="Enable streaming responses",
    )

    # Advanced Features
    enable_multi_agent: bool = Field(
        default=True,
        description="Enable multi-agent workflows",
    )
    enable_human_in_loop: bool = Field(
        default=False,
        description="Enable human-in-the-loop capabilities",
    )
    enable_tool_calling: bool = Field(
        default=True,
        description="Enable tool calling for agents",
    )

    # Experimental Features
    enable_query_rewriting: bool = Field(
        default=False,
        description="Enable experimental query rewriting",
    )
    enable_adaptive_retrieval: bool = Field(
        default=False,
        description="Enable experimental adaptive retrieval",
    )

    model_config = SettingsConfigDict(env_prefix="FEATURE_")


class Settings(BaseSettings):
    """Main application settings.

    This is the primary settings class that aggregates all configuration
    domains. It loads settings from environment variables and .env files.

    Example:
        >>> settings = Settings()
        >>> print(settings.environment)
        >>> print(settings.aws.region)
        >>> print(settings.api.port)
    """

    # Application Settings
    app_name: str = Field(
        default="LangGraph AWS Template",
        description="Application name",
    )
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )
    version: str = Field(
        default="0.1.0",
        description="Application version",
    )

    # Nested Settings
    aws: AWSSettings = Field(default_factory=AWSSettings)
    api: APISettings = Field(default_factory=APISettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    vectordb: VectorDBSettings = Field(default_factory=VectorDBSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    langgraph: LangGraphSettings = Field(default_factory=LangGraphSettings)
    agent: AgentSettings = Field(default_factory=AgentSettings)
    observability: ObservabilitySettings = Field(default_factory=ObservabilitySettings)
    features: FeatureFlags = Field(default_factory=FeatureFlags)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Validate critical settings for production environment."""
        if self.environment == "production":
            errors = []

            # Check secret key
            if self.api.secret_key == "change-me-in-production":  # nosec B105
                errors.append("SECRET_KEY must be changed in production environment")

            # Check debug mode
            if self.debug:
                errors.append("DEBUG mode should be disabled in production")

            # Check tracing
            if not self.observability.tracing_enabled:
                import warnings

                warnings.warn(
                    "Tracing is disabled in production. "
                    "Consider enabling for better observability.",
                    UserWarning,
                    stacklevel=2,
                )

            if errors:
                raise ValueError("Production validation failed:\n" + "\n".join(errors))

        return self

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"

    def is_staging(self) -> bool:
        """Check if running in staging environment."""
        return self.environment == "staging"

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    This function returns a cached instance of Settings to avoid
    repeated environment variable parsing.

    Returns:
        Settings: Application settings instance

    Example:
        >>> from config.settings import get_settings
        >>> settings = get_settings()
        >>> print(settings.aws.region)
    """
    return Settings()


def reload_settings() -> Settings:
    """Reload settings by clearing the cache.

    Useful for testing or when environment variables change.

    Returns:
        Settings: Fresh settings instance
    """
    get_settings.cache_clear()
    return get_settings()


# ============================================================================
# LLM FACTORY FUNCTIONS
# ============================================================================

def get_llm(settings: Settings | None = None):
    """Get configured ChatOpenAI instance.

    This function creates and returns a ChatOpenAI instance configured with
    the settings from environment variables or the provided Settings object.

    Args:
        settings: Optional Settings instance. If not provided, uses get_settings()

    Returns:
        ChatOpenAI: Configured language model instance

    Raises:
        ValueError: If OPENAI_API_KEY is not set
        ImportError: If langchain_openai is not installed

    Example:
        >>> from src.config import get_llm
        >>> llm = get_llm()
        >>> response = llm.invoke("What is the capital of France?")
        >>> print(response.content)
    """
    import logging

    # Get settings if not provided
    if settings is None:
        settings = get_settings()

    logger = logging.getLogger(__name__)

    logger.info("Initializing LLM configuration")
    logger.debug(f"Model: {settings.llm.model_name}")
    logger.debug(f"Temperature: {settings.llm.temperature}")
    logger.debug(f"Max tokens: {settings.llm.max_tokens}")

    # Validate OpenAI API key
    if not settings.llm.openai_api_key:
        error_msg = (
            "OPENAI_API_KEY is not set. "
            "Please set it in your .env file: OPENAI_API_KEY=sk-... "
            "or as an environment variable."
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Try to import ChatOpenAI
    try:
        from langchain_openai import ChatOpenAI
    except ImportError as e:
        error_msg = (
            "langchain_openai is not installed. "
            "Install it with: pip install langchain-openai"
        )
        logger.error(error_msg)
        raise ImportError(error_msg) from e

    # Create ChatOpenAI instance with configured settings
    logger.info(f"Creating ChatOpenAI instance with model: {settings.llm.model_name}")

    try:
        llm = ChatOpenAI(
            model=settings.llm.model_name,
            api_key=settings.llm.openai_api_key,
            temperature=settings.llm.temperature,
            max_tokens=settings.llm.max_tokens,
            top_p=settings.llm.top_p,
            frequency_penalty=settings.llm.frequency_penalty,
            presence_penalty=settings.llm.presence_penalty,
            timeout=settings.llm.timeout_seconds,
            max_retries=settings.llm.max_retries,
        )

        logger.info(f"✓ LLM initialized successfully: {settings.llm.model_name}")
        logger.debug(f"Cache enabled: {settings.llm.cache_enabled}")
        logger.debug(f"Token tracking enabled: {settings.llm.track_token_usage}")

        return llm

    except Exception as e:
        logger.error(f"Failed to initialize LLM: {str(e)}")
        raise


def validate_llm_settings(settings: Settings | None = None) -> bool:
    """Validate LLM configuration settings.

    This function checks that all required LLM settings are properly configured
    and that the necessary API keys are available.

    Args:
        settings: Optional Settings instance. If not provided, uses get_settings()

    Returns:
        bool: True if all settings are valid

    Raises:
        ValueError: If any required settings are missing or invalid

    Example:
        >>> from src.config import validate_llm_settings
        >>> if validate_llm_settings():
        ...     print("LLM settings are valid")
    """
    import logging

    if settings is None:
        settings = get_settings()

    logger = logging.getLogger(__name__)
    errors = []

    # Check OpenAI API key
    if not settings.llm.openai_api_key:
        errors.append("OPENAI_API_KEY is not set")
    else:
        if not settings.llm.openai_api_key.startswith("sk-"):
            errors.append("OPENAI_API_KEY should start with 'sk-'")

    # Check model name
    if not settings.llm.model_name:
        errors.append("model_name is not set")

    # Check temperature range
    if not (0.0 <= settings.llm.temperature <= 2.0):
        errors.append(f"Temperature must be between 0.0 and 2.0, got {settings.llm.temperature}")

    # Check max_tokens
    if settings.llm.max_tokens < 1:
        errors.append(f"max_tokens must be at least 1, got {settings.llm.max_tokens}")

    # Check cache settings
    if settings.llm.cache_enabled and settings.llm.cache_ttl <= 0:
        errors.append("cache_ttl must be greater than 0 if caching is enabled")

    if errors:
        error_msg = "LLM settings validation failed:\n" + "\n".join(f"  • {e}" for e in errors)
        logger.error(error_msg)
        raise ValueError(error_msg)

    logger.info("✓ LLM settings validation passed")
    return True

