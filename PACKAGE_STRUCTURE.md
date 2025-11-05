# Package Structure

Complete Python package structure for the LangGraph AWS Template.

## Directory Layout

```text
src/
├── __init__.py                    # Main package with version info (v0.1.0)
├── agents/                        # LangGraph agent definitions
│   └── __init__.py
├── api/                          # FastAPI application
│   ├── __init__.py
│   └── routes/                   # API route definitions
│       └── __init__.py
├── cache/                        # Caching strategies
│   └── __init__.py
├── config/                       # Configuration management
│   ├── __init__.py
│   └── environments/             # Environment-specific configs
│       └── __init__.py
├── data_pipeline/                # Data ingestion and processing
│   └── __init__.py
├── observability/                # Monitoring and tracing
│   └── __init__.py
├── rag/                          # RAG components
│   └── __init__.py
└── utils/                        # Common utilities
    └── __init__.py
```

## Module Descriptions

### `src/__init__.py`

Main package initialization with version info (`__version__ = "0.1.0"`).

### `src/agents/`

LangGraph agent definitions and multi-agent orchestration:

- Agent state management with DynamoDB checkpointing
- Conditional routing logic
- Tool definitions and integrations
- Supervisor and coordinator patterns

### `src/api/`

FastAPI REST API layer:

- Agent invocation endpoints
- WebSocket streaming support
- Authentication and authorization
- Rate limiting middleware

### `src/api/routes/`

API route definitions organized by domain:

- Agent routes
- Health checks
- Webhooks
- Admin endpoints

### `src/cache/`

Caching strategies for optimization:

- Semantic caching
- Exact match caching
- Redis integration
- TTL management

### `src/config/`

Application configuration using Pydantic settings:

- Environment-specific configs
- AWS service settings
- LLM model configurations
- Secret management

### `src/config/environments/`

Environment-specific configuration files:

- Development settings
- Staging settings
- Production settings

### `src/data_pipeline/`

Data ingestion and processing:

- Document ingestion from S3/local/APIs
- Data cleaning and preprocessing
- Chunking strategies for RAG
- Batch processing

### `src/observability/`

Monitoring and observability:

- OpenTelemetry tracing
- Prometheus metrics
- CloudWatch logging
- Performance monitoring

### `src/rag/`

Retrieval-Augmented Generation components:

- Vector database integrations (ChromaDB, FAISS)
- Embedding generation
- Semantic search and retrieval
- Document reranking

### `src/utils/`

Common utility functions:

- Text processing
- Date/time helpers
- Retry and backoff decorators
- Validation utilities

## Import Examples

```python
# Main package
from src import __version__
print(__version__)  # "0.1.0"

# When modules are implemented, you'll be able to:
from agents import ResearchAgent, create_agent_graph
from rag import VectorStore, Retriever
from cache import SemanticCache
from config import get_settings
from api import create_app
```

## Next Steps

1. Implement core modules in each package
2. Add tests for each module in `tests/`
3. Update `__all__` exports in each `__init__.py` as modules are added
4. Add type hints to all functions and classes
5. Write comprehensive docstrings

## Development Guidelines

- Each module should have corresponding tests in `tests/`
- All public APIs should be exported via `__all__` in `__init__.py`
- Use type hints for all function signatures
- Follow Google-style docstrings
- Keep imports organized (stdlib, third-party, local)
