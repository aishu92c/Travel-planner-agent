# Configuration System

Comprehensive configuration management using Pydantic Settings.

## Quick Start

```python
from config import get_settings

# Load settings from environment variables and .env file
settings = get_settings()

# Access nested settings
print(settings.aws.region)
print(settings.api.port)
print(settings.agent.temperature)
```

## Environment Setup

1. Copy `.env.example` to `.env`:

   ```bash
   cp .env.example .env
   ```

2. Update `.env` with your values:

   ```bash
   # Change the secret key
   API_SECRET_KEY=your-secure-random-string-here

   # Set your AWS region
   AWS_REGION=us-west-2

   # Configure environment
   ENVIRONMENT=development
   ```

3. Settings are automatically loaded when you import:

   ```python
   from config import get_settings
   settings = get_settings()
   ```

## Configuration Structure

### Settings Domains

The configuration is organized into logical domains:

| Domain | Description | Example |
|--------|-------------|---------|
| `aws` | AWS service configurations | `settings.aws.region` |
| `api` | API server settings | `settings.api.port` |
| `database` | DynamoDB tables | `settings.database.agents_table` |
| `vectordb` | Vector database | `settings.vectordb.provider` |
| `cache` | Redis caching | `settings.cache.redis_host` |
| `langgraph` | LangGraph settings | `settings.langgraph.max_iterations` |
| `agent` | Agent/LLM parameters | `settings.agent.temperature` |
| `observability` | Monitoring | `settings.observability.log_level` |
| `features` | Feature flags | `settings.features.enable_rag` |

### Environment-Specific Settings

Use pre-configured settings for different environments:

```python
from config.environments import (
    get_dev_settings,
    get_staging_settings,
    get_prod_settings
)

# Development - optimized for local development
dev_settings = get_dev_settings()
# - DEBUG=true
# - In-memory cache
# - Local vector DB
# - Verbose logging

# Staging - mirrors production
staging_settings = get_staging_settings()
# - DEBUG=false
# - Real AWS services
# - Enhanced tracing
# - Most features enabled

# Production - optimized for performance and security
prod_settings = get_prod_settings()
# - DEBUG=false
# - Multiple workers
# - SSL enabled
# - Sampled tracing
# - Only stable features
```

## Environment Variables

### Naming Convention

Environment variables use prefixes for each domain:

- `AWS_*` - AWS settings
- `API_*` - API settings
- `DB_*` - Database settings
- `VECTORDB_*` - Vector DB settings
- `CACHE_*` - Cache settings
- `LANGGRAPH_*` - LangGraph settings
- `AGENT_*` - Agent settings
- `OBSERVABILITY_*` - Observability settings
- `FEATURE_*` - Feature flags

### Nested Settings

Use double underscores (`__`) for nested settings:

```bash
# Access: settings.aws.bedrock_model_id
AWS_BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0

# Access: settings.api.cors_origins
API_CORS_ORIGINS=["http://localhost:3000"]
```

## Usage Examples

### Basic Usage

```python
from config import get_settings

settings = get_settings()

# AWS settings
print(f"Region: {settings.aws.region}")
print(f"Bedrock Model: {settings.aws.bedrock_model_id}")

# API settings
print(f"Host: {settings.api.host}:{settings.api.port}")
print(f"Workers: {settings.api.workers}")

# Agent settings
print(f"Temperature: {settings.agent.temperature}")
print(f"Max Tokens: {settings.agent.max_tokens}")
```

### Environment Detection

```python
from config import get_settings

settings = get_settings()

if settings.is_production():
    print("Running in production mode")
elif settings.is_staging():
    print("Running in staging mode")
else:
    print("Running in development mode")
```

### Feature Flags

```python
from config import get_settings

settings = get_settings()

# Check if features are enabled
if settings.features.enable_rag:
    # Initialize RAG pipeline
    pass

if settings.features.enable_caching:
    # Initialize cache
    pass

if settings.features.enable_streaming:
    # Enable streaming responses
    pass
```

### Reloading Settings

```python
from config import reload_settings

# Clear cache and reload settings
# Useful for testing or when environment changes
settings = reload_settings()
```

## Validation

Settings are validated on load:

```python
from config import get_settings
from pydantic import ValidationError

try:
    settings = get_settings()
except ValidationError as e:
    print(f"Configuration error: {e}")
```

### Production Validation

Production environment has additional validation:

- `API_SECRET_KEY` must not be the default value
- `DEBUG` must be false
- Warnings for disabled critical features

## Configuration Files

```text
src/config/
├── __init__.py                  # Main exports
├── settings.py                  # Settings definitions
├── environments/
│   ├── __init__.py
│   ├── development.py          # Dev-specific settings
│   ├── staging.py              # Staging settings
│   └── production.py           # Production settings
└── README.md                   # This file
```

## Best Practices

1. **Never commit `.env` files** - Use `.env.example` as template
2. **Use environment-specific configs** - For consistent setups
3. **Validate in production** - Settings are auto-validated
4. **Cache settings** - `get_settings()` is cached for performance
5. **Type safety** - All settings are fully typed
6. **Document changes** - Update `.env.example` when adding settings

## Adding New Settings

1. Define in appropriate settings class in `settings.py`:

   ```python
   class APISettings(BaseSettings):
       new_setting: str = Field(
           default="default_value",
           description="Description of setting"
       )
   ```

2. Add to `.env.example`:

   ```bash
   API_NEW_SETTING=default_value
   ```

3. Use in your code:

   ```python
   settings = get_settings()
   print(settings.api.new_setting)
   ```

## Troubleshooting

### Settings Not Loading

1. Check `.env` file exists
2. Verify environment variable names
3. Check for validation errors
4. Ensure proper typing

### Type Errors

```python
# Wrong - will cause validation error
AGENT_TEMPERATURE=high  # Should be float

# Correct
AGENT_TEMPERATURE=0.7
```

### Production Errors

```bash
# This will fail in production
ENVIRONMENT=production
API_SECRET_KEY=change-me-in-production  # Must change!
DEBUG=true  # Must be false!
```

## Reference

See `settings.py` for complete documentation of all available settings and
their defaults.
