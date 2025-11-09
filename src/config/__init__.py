"""Configuration Module.

Manages application configuration using Pydantic settings.

This module provides:
- Environment-specific configurations (dev, staging, prod)
- Settings validation with Pydantic
- AWS service configurations
- LLM model settings
- Database connection settings
- Secret management integration

Example:
    >>> from config import get_settings
    >>> settings = get_settings()
    >>> print(settings.aws.region)
    >>> print(settings.api.port)
"""

from .settings import (
    AgentSettings,
    APISettings,
    AWSSettings,
    CacheSettings,
    DatabaseSettings,
    FeatureFlags,
    LangGraphSettings,
    LLMSettings,
    ObservabilitySettings,
    Settings,
    VectorDBSettings,
    get_llm,
    get_settings,
    reload_settings,
    validate_llm_settings,
)

__all__ = [
    # Main settings
    "Settings",
    "get_settings",
    "reload_settings",
    # Domain settings
    "AWSSettings",
    "APISettings",
    "DatabaseSettings",
    "VectorDBSettings",
    "CacheSettings",
    "LangGraphSettings",
    "AgentSettings",
    "LLMSettings",
    "ObservabilitySettings",
    "FeatureFlags",
    # LLM functions
    "get_llm",
    "validate_llm_settings",
]
