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
    ObservabilitySettings,
    Settings,
    VectorDBSettings,
    get_settings,
    reload_settings,
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
    "ObservabilitySettings",
    "FeatureFlags",
]
