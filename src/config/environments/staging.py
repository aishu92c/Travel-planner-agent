"""Staging Environment Configuration.

This module provides staging-specific settings that closely mirror
production but with some relaxed constraints for testing.

Example:
    >>> from config.environments.staging import get_staging_settings
    >>> settings = get_staging_settings()
"""

from config.settings import Settings


def get_staging_settings() -> Settings:
    """Get staging environment settings.

    Returns:
        Settings: Settings configured for staging environment

    Note:
        This automatically sets:
        - DEBUG=false
        - Production-like services (DynamoDB, Redis, ChromaDB)
        - Enhanced logging and tracing
        - Most features enabled for pre-production testing
    """
    return Settings(
        environment="staging",
        debug=False,
        # API Settings
        api__reload=False,
        api__workers=2,  # Lower than production
        # Use real AWS services
        langgraph__checkpoint_backend="dynamodb",
        cache__provider="redis",
        vectordb__provider="chromadb",
        # Enhanced observability
        observability__tracing_enabled=True,
        observability__tracing_sample_rate=1.0,  # 100% in staging
        observability__metrics_enabled=True,
        observability__log_level="INFO",
        observability__log_format="json",
        observability__cloudwatch_enabled=True,
        # Enable most features (except experimental)
        features__enable_rag=True,
        features__enable_caching=True,
        features__enable_streaming=True,
        features__enable_multi_agent=True,
        features__enable_tool_calling=True,
        features__enable_query_rewriting=False,  # Experimental
        features__enable_adaptive_retrieval=False,  # Experimental
    )
