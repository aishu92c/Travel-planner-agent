"""API Models.

Pydantic models for API requests and responses.

Example:
    >>> from api.models import QueryRequest, QueryResponse
    >>> request = QueryRequest(
    ...     query="What is AI?",
    ...     context={"user_id": "123"}
    ... )
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, field_validator


class QueryRequest(BaseModel):
    """API request schema for agent queries.

    Example:
        >>> request = QueryRequest(
        ...     query="What is the capital of France?",
        ...     context={"user_id": "user_123", "session_id": "sess_456"},
        ...     stream=False,
        ...     max_tokens=1000
        ... )
    """

    query: str = Field(
        description="User query to process",
        min_length=1,
        max_length=10000,
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context for the query",
    )
    user_id: str | None = Field(
        default=None,
        description="User identifier",
    )
    session_id: str | None = Field(
        default=None,
        description="Session identifier for conversation continuity",
    )
    stream: bool = Field(
        default=False,
        description="Whether to stream the response",
    )
    max_tokens: int | None = Field(
        default=None,
        gt=0,
        le=200000,
        description="Maximum tokens in response",
    )
    temperature: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Sampling temperature for generation",
    )
    enable_rag: bool = Field(
        default=True,
        description="Whether to use RAG retrieval",
    )
    enable_tools: bool = Field(
        default=True,
        description="Whether to allow tool usage",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional request metadata",
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate query is not empty or just whitespace."""
        if not v.strip():
            raise ValueError("Query cannot be empty or just whitespace")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the capital of France?",
                "context": {
                    "user_id": "user_123",
                    "preferences": {"language": "en"},
                },
                "user_id": "user_123",
                "session_id": "sess_456",
                "stream": False,
                "max_tokens": 1000,
                "temperature": 0.7,
                "enable_rag": True,
                "enable_tools": True,
                "metadata": {"source": "web_app"},
            }
        }


class ResponseStatus(str, Enum):
    """Status of the response."""

    SUCCESS = "success"
    PARTIAL = "partial"
    ERROR = "error"
    TIMEOUT = "timeout"


class Citation(BaseModel):
    """Citation for information in the response.

    Example:
        >>> citation = Citation(
        ...     text="Paris is the capital",
        ...     source="Wikipedia",
        ...     url="https://en.wikipedia.org/wiki/Paris"
        ... )
    """

    text: str = Field(description="Cited text snippet")
    source: str = Field(description="Source name")
    url: HttpUrl | None = Field(
        default=None,
        description="URL to the source",
    )
    document_id: str | None = Field(
        default=None,
        description="ID of source document if from RAG",
    )
    relevance_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Relevance score for this citation",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Paris is the capital and largest city of France",
                "source": "Wikipedia - Paris",
                "url": "https://en.wikipedia.org/wiki/Paris",
                "document_id": "doc_123",
                "relevance_score": 0.95,
            }
        }


class Usage(BaseModel):
    """Token usage statistics.

    Example:
        >>> usage = Usage(
        ...     prompt_tokens=100,
        ...     completion_tokens=50,
        ...     total_tokens=150
        ... )
    """

    prompt_tokens: int = Field(ge=0, description="Tokens in the prompt")
    completion_tokens: int = Field(ge=0, description="Tokens in the completion")
    total_tokens: int = Field(ge=0, description="Total tokens used")
    estimated_cost_usd: float | None = Field(
        default=None,
        ge=0.0,
        description="Estimated cost in USD",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt_tokens": 150,
                "completion_tokens": 75,
                "total_tokens": 225,
                "estimated_cost_usd": 0.0045,
            }
        }


class QueryResponse(BaseModel):
    """API response schema for agent queries.

    Example:
        >>> response = QueryResponse(
        ...     response="The capital of France is Paris.",
        ...     status="success",
        ...     request_id="req_123"
        ... )
    """

    response: str = Field(description="Generated response text")
    status: ResponseStatus = Field(description="Status of the response")
    request_id: str = Field(description="Unique request identifier")
    session_id: str | None = Field(
        default=None,
        description="Session identifier",
    )
    citations: list[Citation] = Field(
        default_factory=list,
        description="Citations supporting the response",
    )
    usage: Usage | None = Field(
        default=None,
        description="Token usage statistics",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional response metadata",
    )
    processing_time_seconds: float = Field(
        default=0.0,
        ge=0.0,
        description="Time taken to process the request",
    )
    model: str | None = Field(
        default=None,
        description="Model used for generation",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Any warnings during processing",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "response": "The capital of France is Paris. Paris is located "
                "in the north-central part of France.",
                "status": "success",
                "request_id": "req_abc123",
                "session_id": "sess_456",
                "citations": [
                    {
                        "text": "Paris is the capital",
                        "source": "Wikipedia",
                        "url": "https://en.wikipedia.org/wiki/Paris",
                        "relevance_score": 0.95,
                    }
                ],
                "usage": {
                    "prompt_tokens": 150,
                    "completion_tokens": 75,
                    "total_tokens": 225,
                },
                "metadata": {
                    "agent_type": "qa",
                    "rag_used": True,
                    "tools_used": [],
                },
                "processing_time_seconds": 1.25,
                "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
                "timestamp": "2024-01-01T12:00:00Z",
                "warnings": [],
            }
        }


class StreamChunk(BaseModel):
    """Chunk of a streamed response.

    Example:
        >>> chunk = StreamChunk(
        ...     chunk="Hello",
        ...     is_final=False,
        ...     request_id="req_123"
        ... )
    """

    chunk: str = Field(description="Text chunk")
    is_final: bool = Field(
        default=False,
        description="Whether this is the final chunk",
    )
    request_id: str = Field(description="Request identifier")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Chunk metadata",
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "chunk": "The capital",
                    "is_final": False,
                    "request_id": "req_123",
                    "metadata": {"index": 0},
                },
                {
                    "chunk": " of France is Paris.",
                    "is_final": True,
                    "request_id": "req_123",
                    "metadata": {"index": 1, "total_tokens": 50},
                },
            ]
        }


class ServiceStatus(str, Enum):
    """Status of a service component."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class HealthCheckResponse(BaseModel):
    """Health check endpoint response.

    Example:
        >>> health = HealthCheckResponse(
        ...     status="healthy",
        ...     version="0.1.0",
        ...     uptime_seconds=3600
        ... )
    """

    status: ServiceStatus = Field(description="Overall system status")
    version: str = Field(description="Application version")
    environment: str = Field(
        default="unknown",
        description="Environment (dev, staging, prod)",
    )
    uptime_seconds: float = Field(
        ge=0.0,
        description="System uptime in seconds",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Health check timestamp",
    )
    services: dict[str, ServiceStatus] = Field(
        default_factory=dict,
        description="Status of individual services",
    )
    metrics: dict[str, Any] = Field(
        default_factory=dict,
        description="System metrics",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Any system warnings",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "0.1.0",
                "environment": "production",
                "uptime_seconds": 86400.0,
                "timestamp": "2024-01-01T12:00:00Z",
                "services": {
                    "database": "healthy",
                    "cache": "healthy",
                    "vectordb": "healthy",
                    "llm": "healthy",
                },
                "metrics": {
                    "requests_per_second": 150,
                    "avg_latency_ms": 250,
                    "error_rate": 0.01,
                    "cache_hit_rate": 0.75,
                },
                "warnings": [],
            }
        }


class ErrorDetail(BaseModel):
    """Detailed error information.

    Example:
        >>> detail = ErrorDetail(
        ...     field="query",
        ...     message="Query cannot be empty",
        ...     error_code="VALIDATION_ERROR"
        ... )
    """

    field: str | None = Field(
        default=None,
        description="Field that caused the error",
    )
    message: str = Field(description="Error message")
    error_code: str | None = Field(
        default=None,
        description="Machine-readable error code",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "field": "query",
                "message": "Query cannot be empty",
                "error_code": "VALIDATION_ERROR",
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response format.

    Example:
        >>> error = ErrorResponse(
        ...     error="Validation Error",
        ...     message="Invalid request parameters",
        ...     status_code=400
        ... )
    """

    error: str = Field(description="Error type/title")
    message: str = Field(description="Human-readable error message")
    status_code: int = Field(
        ge=400,
        le=599,
        description="HTTP status code",
    )
    request_id: str | None = Field(
        default=None,
        description="Request identifier for tracing",
    )
    details: list[ErrorDetail] = Field(
        default_factory=list,
        description="Detailed error information",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Error timestamp",
    )
    documentation_url: HttpUrl | None = Field(
        default=None,
        description="URL to error documentation",
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "error": "Validation Error",
                    "message": "Invalid request parameters",
                    "status_code": 400,
                    "request_id": "req_123",
                    "details": [
                        {
                            "field": "query",
                            "message": "Query cannot be empty",
                            "error_code": "REQUIRED_FIELD",
                        }
                    ],
                    "timestamp": "2024-01-01T12:00:00Z",
                },
                {
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred",
                    "status_code": 500,
                    "request_id": "req_456",
                    "details": [],
                    "timestamp": "2024-01-01T12:00:00Z",
                    "documentation_url": "https://docs.example.com/errors/500",
                },
            ]
        }


class BatchQueryRequest(BaseModel):
    """Request for batch query processing.

    Example:
        >>> batch = BatchQueryRequest(
        ...     queries=["Query 1", "Query 2"],
        ...     shared_context={"user_id": "123"}
        ... )
    """

    queries: list[str] = Field(
        description="List of queries to process",
        min_length=1,
        max_length=100,
    )
    shared_context: dict[str, Any] = Field(
        default_factory=dict,
        description="Context shared across all queries",
    )
    parallel: bool = Field(
        default=True,
        description="Whether to process queries in parallel",
    )
    fail_fast: bool = Field(
        default=False,
        description="Stop on first error",
    )

    @field_validator("queries")
    @classmethod
    def validate_queries(cls, v: list[str]) -> list[str]:
        """Validate all queries are non-empty."""
        if not all(q.strip() for q in v):
            raise ValueError("All queries must be non-empty")
        return [q.strip() for q in v]

    class Config:
        json_schema_extra = {
            "example": {
                "queries": [
                    "What is Python?",
                    "What is JavaScript?",
                    "What is Go?",
                ],
                "shared_context": {"user_id": "user_123"},
                "parallel": True,
                "fail_fast": False,
            }
        }


class BatchQueryResponse(BaseModel):
    """Response for batch query processing.

    Example:
        >>> batch_response = BatchQueryResponse(
        ...     results=[response1, response2],
        ...     total_queries=2,
        ...     successful=2
        ... )
    """

    results: list[QueryResponse | ErrorResponse] = Field(description="Results for each query")
    total_queries: int = Field(
        ge=0,
        description="Total number of queries processed",
    )
    successful: int = Field(
        ge=0,
        description="Number of successful queries",
    )
    failed: int = Field(
        ge=0,
        description="Number of failed queries",
    )
    total_processing_time_seconds: float = Field(
        ge=0.0,
        description="Total processing time",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "results": [
                    {
                        "response": "Python is a programming language",
                        "status": "success",
                        "request_id": "req_1",
                    },
                    {
                        "error": "Rate Limit",
                        "message": "Too many requests",
                        "status_code": 429,
                        "request_id": "req_2",
                    },
                ],
                "total_queries": 2,
                "successful": 1,
                "failed": 1,
                "total_processing_time_seconds": 2.5,
            }
        }


# Export all models
__all__ = [
    "QueryRequest",
    "ResponseStatus",
    "Citation",
    "Usage",
    "QueryResponse",
    "StreamChunk",
    "ServiceStatus",
    "HealthCheckResponse",
    "ErrorDetail",
    "ErrorResponse",
    "BatchQueryRequest",
    "BatchQueryResponse",
]
