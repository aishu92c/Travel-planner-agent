"""Environment Configurations Module.

Contains environment-specific configuration files.

This module provides:
- Development environment settings
- Staging environment settings
- Production environment settings
- Environment variable templates

Example:
    >>> from config.environments import get_dev_settings, get_prod_settings
    >>> settings = get_dev_settings()  # For development
    >>> settings = get_prod_settings()  # For production
"""

from .development import get_dev_settings
from .production import get_prod_settings
from .staging import get_staging_settings

__all__ = [
    "get_dev_settings",
    "get_staging_settings",
    "get_prod_settings",
]
