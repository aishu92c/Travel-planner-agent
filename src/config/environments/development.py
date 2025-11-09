"""Development Environment Configuration.

This module provides development-specific settings that override
the default configuration values.

Example:
    >>> from config.environments.development import get_dev_settings
    >>> settings = get_dev_settings()
"""

from config.settings import Settings


def get_dev_settings() -> Settings:
    """Get development environment settings.

    Returns:
        Settings: Settings configured for development environment

    Note:
        This automatically sets:
        - DEBUG=true
        - API reload enabled
        - Local services (ChromaDB, Redis on localhost)
        - Verbose logging
        - All features enabled for testing
    """
    return Settings(
        environment="development",
        debug=True,
        # API Settings
        api__reload=True,
        api__cors_origins=[
            "http://localhost:3000",
            "http://localhost:8000",
            "http://localhost:5173",  # Vite default
        ],
        # Use in-memory/local services
        cache__provider="memory",  # Use memory cache for quick dev
        vectordb__provider="faiss",  # FAISS for local dev
        langgraph__checkpoint_backend="memory",  # In-memory checkpoints
        # Verbose logging
        observability__log_level="DEBUG",
        observability__log_format="text",  # Human-readable logs
        # Enable all features for testing
        features__enable_rag=True,
        features__enable_caching=True,
        features__enable_streaming=True,
        features__enable_multi_agent=True,
        features__enable_tool_calling=True,
        features__enable_query_rewriting=True,
        features__enable_adaptive_retrieval=True,
    )
