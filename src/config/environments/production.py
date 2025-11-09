"""Production Environment Configuration.

This module provides production-specific settings with security
and performance optimizations.

Example:
    >>> from config.environments.production import get_prod_settings
    >>> settings = get_prod_settings()
"""

from config.settings import Settings


def get_prod_settings() -> Settings:
    """Get production environment settings.

    Returns:
        Settings: Settings configured for production environment

    Note:
        This automatically sets:
        - DEBUG=false
        - API reload disabled
        - Multiple workers for performance
        - Production AWS services
        - Optimized caching and rate limiting
        - Selective tracing sampling
        - Only stable features enabled

    Raises:
        ValueError: If SECRET_KEY is not set or using default value
    """
    return Settings(
        environment="production",
        debug=False,
        # API Settings
        api__reload=False,
        api__workers=8,  # More workers for production
        api__rate_limit_enabled=True,
        api__rate_limit_requests=1000,
        api__rate_limit_window_seconds=60,
        # Production AWS services
        langgraph__checkpoint_backend="dynamodb",
        cache__provider="redis",
        cache__redis_ssl=True,  # Use SSL in production
        vectordb__provider="chromadb",
        # Optimized settings
        agent__max_retries=5,
        langgraph__max_concurrent_executions=50,
        # Observability
        observability__tracing_enabled=True,
        observability__tracing_sample_rate=0.1,  # Sample 10% to reduce overhead
        observability__metrics_enabled=True,
        observability__log_level="INFO",
        observability__log_format="json",
        observability__cloudwatch_enabled=True,
        # Only stable features
        features__enable_rag=True,
        features__enable_caching=True,
        features__enable_streaming=True,
        features__enable_multi_agent=True,
        features__enable_tool_calling=True,
        features__enable_query_rewriting=False,  # Experimental - disabled
        features__enable_adaptive_retrieval=False,  # Experimental - disabled
        features__enable_human_in_loop=False,  # Requires UI
    )
