# LLM Configuration Guide

## Overview

The travel planner agent uses OpenAI's GPT models for itinerary generation and other LLM-powered features. This guide explains how to configure and use the LLM settings.

## Quick Start

### 1. Get an OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (it starts with `sk-`)

### 2. Set Up Environment

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Add your API key to `.env`:
```
LLM__OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. Verify Configuration

```python
from src.config import get_settings, validate_llm_settings, get_llm

# Check settings
settings = get_settings()
print(f"Model: {settings.llm.model_name}")
print(f"Temperature: {settings.llm.temperature}")

# Validate LLM settings
validate_llm_settings()
print("✓ Settings validated")

# Get configured LLM instance
llm = get_llm()
print("✓ LLM initialized")

# Test it
response = llm.invoke("Hello, what is your name?")
print(response.content)
```

## Configuration Options

### API Keys

#### `LLM__OPENAI_API_KEY` (Required)
- Your OpenAI API key
- Format: `sk-...` (47 characters)
- Get from: https://platform.openai.com/api-keys
- **CRITICAL**: Never share or commit this to version control

```bash
LLM__OPENAI_API_KEY=sk-proj-abc123...
```

#### `LLM__LANGSMITH_API_KEY` (Optional)
- LangSmith API key for debugging and tracing
- Get from: https://smith.langchain.com
- Useful for debugging LLM calls in production

```bash
LLM__LANGSMITH_API_KEY=ls_api_key...
```

#### `LLM__ANTHROPIC_API_KEY` (Optional)
- Anthropic API key if using Claude models
- Get from: https://console.anthropic.com

```bash
LLM__ANTHROPIC_API_KEY=sk-ant-...
```

### Model Configuration

#### `LLM__MODEL_NAME`
- Model to use for LLM calls
- Default: `gpt-4-turbo-preview`
- Available models:
  - `gpt-4-turbo-preview` - Most capable, highest cost
  - `gpt-4` - Stable GPT-4 version
  - `gpt-3.5-turbo` - Fast, cheaper option
  - `claude-3-opus-20240229` - Anthropic Claude 3 (requires ANTHROPIC_API_KEY)

```bash
LLM__MODEL_NAME=gpt-4-turbo-preview
```

#### `LLM__TEMPERATURE`
- Controls randomness of responses (0.0 to 2.0)
- **0.0** = Deterministic (same input = same output)
- **0.7** = Balanced (default)
- **2.0** = Maximum creativity/randomness

Best practices:
- Itinerary generation: 0.7 (balanced)
- Data extraction: 0.0-0.3 (deterministic)
- Creative writing: 1.0-1.5 (creative)

```bash
LLM__TEMPERATURE=0.7
```

#### `LLM__MAX_TOKENS`
- Maximum length of response in tokens
- Default: 2000
- Range: 1 to 200,000
- **Note**: Each token ≈ 4 characters
- For itineraries: 2000-4000 recommended

```bash
LLM__MAX_TOKENS=2000
```

#### `LLM__TOP_P`
- Nucleus sampling parameter (0.0 to 1.0)
- Default: 1.0
- Controls diversity vs quality trade-off
- Lower = more focused, Higher = more diverse

```bash
LLM__TOP_P=1.0
```

#### `LLM__FREQUENCY_PENALTY`
- Penalizes frequent token repetition (-2.0 to 2.0)
- Default: 0.0
- Positive values reduce repetition
- Use 0.5-1.0 to discourage repeated phrases

```bash
LLM__FREQUENCY_PENALTY=0.0
```

#### `LLM__PRESENCE_PENALTY`
- Penalizes discussed topics (-2.0 to 2.0)
- Default: 0.0
- Positive values encourage new topics
- Use 0.5-1.0 for more topic diversity

```bash
LLM__PRESENCE_PENALTY=0.0
```

### Logging Configuration

#### `LLM__LOG_LEVEL`
- Logging verbosity level
- Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Default: INFO
- DEBUG = most verbose, CRITICAL = least verbose

```bash
LLM__LOG_LEVEL=INFO
```

#### `LLM__LOG_FORMAT`
- Log message format string
- Default: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

```bash
LLM__LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### Cache Configuration (Phase 4)

#### `LLM__CACHE_ENABLED`
- Enable response caching to reduce API calls
- Default: false
- Use with caution for deterministic tasks

```bash
LLM__CACHE_ENABLED=false
```

#### `LLM__CACHE_TTL`
- Cache time-to-live in seconds
- Default: 3600 (1 hour)
- 0 = no expiration

```bash
LLM__CACHE_TTL=3600
```

### Cost Tracking (Phase 2)

#### `LLM__TRACK_TOKEN_USAGE`
- Track token usage for cost monitoring
- Default: true
- Logs input and output tokens for each call

```bash
LLM__TRACK_TOKEN_USAGE=true
```

### Timeouts & Retries

#### `LLM__TIMEOUT_SECONDS`
- Timeout for LLM API calls
- Default: 60
- Range: 1 to 300 seconds

```bash
LLM__TIMEOUT_SECONDS=60
```

#### `LLM__MAX_RETRIES`
- Maximum retry attempts on failure
- Default: 3
- Range: 0 to 10

```bash
LLM__MAX_RETRIES=3
```

## Usage Examples

### Basic Usage

```python
from src.config import get_llm, get_settings

# Get configured LLM
llm = get_llm()

# Invoke the LLM
response = llm.invoke("Create a 3-day itinerary for Paris")
print(response.content)
```

### With Custom Settings

```python
from src.config import Settings, LLMSettings, get_llm

# Create custom settings
settings = Settings()
settings.llm.temperature = 0.5
settings.llm.model_name = "gpt-3.5-turbo"

# Get LLM with custom settings
llm = get_llm(settings)
```

### With Error Handling

```python
from src.config import get_llm, validate_llm_settings

try:
    # Validate settings first
    validate_llm_settings()
    
    # Get LLM
    llm = get_llm()
    
    # Use LLM
    response = llm.invoke("Test")
    
except ValueError as e:
    print(f"Configuration error: {e}")
except ImportError as e:
    print(f"Missing dependency: {e}")
```

### In LangGraph Nodes

```python
from src.config import get_llm
from src.agents.state import AgentState

def generate_itinerary_node(state: AgentState):
    """Generate itinerary using configured LLM."""
    llm = get_llm()
    
    prompt = f"""Create a {state.duration}-day itinerary for {state.destination}
    with a budget of ${state.budget}."""
    
    response = llm.invoke(prompt)
    return {"final_itinerary": response.content}
```

## Cost Estimation

### Token Pricing (as of November 2024)

**GPT-4 Turbo:**
- Input: $0.01 per 1K tokens
- Output: $0.03 per 1K tokens

**GPT-3.5 Turbo:**
- Input: $0.50 per 1M tokens
- Output: $1.50 per 1M tokens

### Example Costs

Generating a 10-day itinerary:
- Input tokens: ~1,500 (prompt + context)
- Output tokens: ~2,500 (itinerary)
- GPT-4 Turbo: ~$0.105 per itinerary
- GPT-3.5 Turbo: ~0.005$ per itinerary

## Troubleshooting

### Error: "OPENAI_API_KEY is not set"

**Solution**: 
1. Create `.env` file in project root
2. Add: `LLM__OPENAI_API_KEY=sk-...`
3. Restart your application

### Error: "langchain_openai is not installed"

**Solution**:
```bash
pip install langchain-openai
```

### Error: "Invalid API key"

**Solution**:
1. Check API key format (should start with `sk-`)
2. Verify key is not expired
3. Generate new key from: https://platform.openai.com/api-keys

### Error: "Model not found"

**Solution**:
1. Verify model name is correct
2. Check that model is available in your region
3. Ensure your account has access to the model

### Slow Responses

**Solutions**:
- Reduce `max_tokens`
- Use `gpt-3.5-turbo` instead of `gpt-4`
- Enable `cache_enabled` for repeated queries
- Increase `timeout_seconds` if network is slow

### High Costs

**Solutions**:
- Use `gpt-3.5-turbo` (10x cheaper)
- Reduce `max_tokens`
- Enable caching
- Monitor `track_token_usage` logs

## Production Best Practices

### 1. Secure API Keys
```bash
# Never commit .env to git
echo ".env" >> .gitignore

# Use environment variables in CI/CD
# Never hardcode API keys in code
```

### 2. Monitor Costs
```python
# Enable token tracking
LLM__TRACK_TOKEN_USAGE=true

# Log costs regularly
# Check OpenAI dashboard: https://platform.openai.com/account/billing/overview
```

### 3. Set Appropriate Timeouts
```bash
# Use reasonable timeouts
LLM__TIMEOUT_SECONDS=60

# For production, consider 30-120 seconds
```

### 4. Error Handling
```python
from src.config import get_llm, validate_llm_settings

try:
    validate_llm_settings()
    llm = get_llm()
except ValueError as e:
    # Handle missing config
    logger.error(f"Config error: {e}")
except Exception as e:
    # Handle API errors
    logger.error(f"LLM error: {e}")
```

### 5. Use Appropriate Model
- Production: `gpt-4-turbo-preview` or `gpt-3.5-turbo`
- Development: `gpt-3.5-turbo` (cheaper for testing)
- High-accuracy: `gpt-4` (if needed)

## Configuration Validation

The system validates all LLM settings on initialization:

```python
from src.config import validate_llm_settings

# Validation checks:
# ✓ OPENAI_API_KEY is set and starts with 'sk-'
# ✓ model_name is not empty
# ✓ temperature is between 0.0 and 2.0
# ✓ max_tokens is at least 1
# ✓ cache settings are consistent

validate_llm_settings()  # Raises ValueError if invalid
```

## Related Documentation

- **Main Settings Guide**: See `src/config/settings.py`
- **API Configuration**: See API__* settings
- **AWS Configuration**: See AWS__* settings
- **LangGraph Configuration**: See LANGGRAPH__* settings

## Support

For issues with:
- **OpenAI API**: https://platform.openai.com/docs
- **LangChain**: https://python.langchain.com
- **LangSmith**: https://smith.langchain.com/docs
- **This Project**: Check PROJECT_INDEX.md

---

**Last Updated**: November 7, 2025
**Version**: 1.0

