"""API Module.

FastAPI application for exposing LangGraph agents and services.

This module provides:
- REST API endpoints for agent invocation
- WebSocket support for streaming responses
- Authentication and authorization
- Rate limiting middleware
- Request/response validation
- API documentation (OpenAPI/Swagger)

Example:
    >>> from api import create_app
    >>> from api.models import QueryRequest, QueryResponse
    >>> app = create_app()
    >>> # Run with: uvicorn api:app --reload
"""

# API models
from .models import (
    BatchQueryRequest,
    BatchQueryResponse,
    Citation,
    ErrorDetail,
    ErrorResponse,
    HealthCheckResponse,
    QueryRequest,
    QueryResponse,
    ResponseStatus,
    ServiceStatus,
    StreamChunk,
    Usage,
)

# Future implementations will go here
# from .app import create_app
# from .dependencies import get_current_user, get_agent
# from .middleware import RateLimitMiddleware

__all__ = [
    # Request/Response models
    "QueryRequest",
    "ResponseStatus",
    "Citation",
    "Usage",
    "QueryResponse",
    "StreamChunk",
    # Health & Error models
    "ServiceStatus",
    "HealthCheckResponse",
    "ErrorDetail",
    "ErrorResponse",
    # Batch models
    "BatchQueryRequest",
    "BatchQueryResponse",
    # Future implementations will be added here
]
