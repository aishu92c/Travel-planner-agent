"""RAG (Retrieval-Augmented Generation) Models.

Pydantic models for RAG pipeline components including documents,
chunks, embeddings, and search results.

Example:
    >>> from rag.models import Document, Chunk, VectorSearchResult
    >>> doc = Document(
    ...     id="doc_123",
    ...     content="This is a document",
    ...     metadata={"source": "wiki"}
    ... )
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class DocumentSource(str, Enum):
    """Source type of a document."""

    LOCAL_FILE = "local_file"
    S3 = "s3"
    URL = "url"
    API = "api"
    DATABASE = "database"
    USER_UPLOAD = "user_upload"
    UNKNOWN = "unknown"


class Document(BaseModel):
    """Schema for documents in RAG system.

    Example:
        >>> doc = Document(
        ...     id="doc_123",
        ...     content="Python is a programming language",
        ...     metadata={
        ...         "source": "wikipedia",
        ...         "title": "Python Programming",
        ...         "author": "Various"
        ...     }
        ... )
    """

    id: str = Field(description="Unique identifier for the document")
    content: str = Field(
        description="Raw text content of the document",
        min_length=1,
    )
    title: str | None = Field(
        default=None,
        description="Document title",
    )
    source: DocumentSource = Field(
        default=DocumentSource.UNKNOWN,
        description="Source type of the document",
    )
    source_uri: str | None = Field(
        default=None,
        description="URI/path to the original document",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the document",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the document was created/ingested",
    )
    updated_at: datetime | None = Field(
        default=None,
        description="When the document was last updated",
    )
    word_count: int | None = Field(
        default=None,
        ge=0,
        description="Number of words in the document",
    )
    language: str = Field(
        default="en",
        description="Document language code (ISO 639-1)",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorization",
    )

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Validate language code format."""
        if len(v) not in (2, 3):  # ISO 639-1 or 639-2
            raise ValueError("Language code must be 2 or 3 characters")
        return v.lower()

    def __len__(self) -> int:
        """Return the length of the document content."""
        return len(self.content)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "doc_123",
                "content": "Python is a high-level programming language...",
                "title": "Introduction to Python",
                "source": "local_file",
                "source_uri": "/data/python_intro.pdf",
                "metadata": {
                    "author": "John Doe",
                    "publication_date": "2024-01-01",
                    "category": "programming",
                },
                "created_at": "2024-01-01T12:00:00Z",
                "word_count": 1500,
                "language": "en",
                "tags": ["python", "programming", "tutorial"],
            }
        }


class ChunkingStrategy(str, Enum):
    """Strategy used for chunking documents."""

    FIXED_SIZE = "fixed_size"
    SENTENCE = "sentence"
    PARAGRAPH = "paragraph"
    SEMANTIC = "semantic"
    RECURSIVE = "recursive"


class Chunk(BaseModel):
    """Schema for document chunks.

    Example:
        >>> chunk = Chunk(
        ...     id="chunk_456",
        ...     document_id="doc_123",
        ...     content="Python is a programming language",
        ...     chunk_index=0,
        ...     start_char=0,
        ...     end_char=35
        ... )
    """

    id: str = Field(description="Unique identifier for the chunk")
    document_id: str = Field(description="ID of the parent document")
    content: str = Field(
        description="Text content of the chunk",
        min_length=1,
    )
    chunk_index: int = Field(
        ge=0,
        description="Index of this chunk in the document",
    )
    start_char: int = Field(
        ge=0,
        description="Start character position in original document",
    )
    end_char: int = Field(
        ge=0,
        description="End character position in original document",
    )
    embedding: list[float] | None = Field(
        default=None,
        description="Vector embedding for this chunk",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Chunk-specific metadata",
    )
    chunking_strategy: ChunkingStrategy = Field(
        default=ChunkingStrategy.FIXED_SIZE,
        description="Strategy used to create this chunk",
    )
    overlap_with_previous: int = Field(
        default=0,
        ge=0,
        description="Number of overlapping characters with previous chunk",
    )
    overlap_with_next: int = Field(
        default=0,
        ge=0,
        description="Number of overlapping characters with next chunk",
    )

    @model_validator(mode="after")
    def validate_char_positions(self) -> "Chunk":
        """Validate start_char < end_char."""
        if self.start_char >= self.end_char:
            raise ValueError("start_char must be less than end_char")
        if len(self.content) != (self.end_char - self.start_char):
            raise ValueError("Content length must match character position range")
        return self

    @field_validator("embedding")
    @classmethod
    def validate_embedding(cls, v: list[float] | None) -> list[float] | None:
        """Validate embedding dimensions."""
        if v is not None:
            if not v:
                raise ValueError("Embedding cannot be empty")
            if not all(isinstance(x, (int, float)) for x in v):
                raise ValueError("All embedding values must be numeric")
        return v

    def __len__(self) -> int:
        """Return the length of the chunk content."""
        return len(self.content)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "chunk_456",
                "document_id": "doc_123",
                "content": "Python is a high-level programming language.",
                "chunk_index": 0,
                "start_char": 0,
                "end_char": 46,
                "embedding": [0.1, 0.2, 0.3],  # Truncated for example
                "metadata": {"section": "introduction"},
                "chunking_strategy": "sentence",
                "overlap_with_previous": 0,
                "overlap_with_next": 10,
            }
        }


class VectorSearchResult(BaseModel):
    """Search result from vector database.

    Example:
        >>> result = VectorSearchResult(
        ...     chunk_id="chunk_456",
        ...     document_id="doc_123",
        ...     content="Python is a programming language",
        ...     score=0.95,
        ...     metadata={"source": "wiki"}
        ... )
    """

    chunk_id: str = Field(description="ID of the matched chunk")
    document_id: str = Field(description="ID of the source document")
    content: str = Field(description="Content of the matched chunk")
    score: float = Field(
        ge=0.0,
        le=1.0,
        description="Similarity score (0-1, higher is better)",
    )
    distance: float | None = Field(
        default=None,
        ge=0.0,
        description="Distance metric (lower is better)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata from the chunk/document",
    )
    rank: int | None = Field(
        default=None,
        ge=1,
        description="Rank in search results",
    )
    chunk_index: int | None = Field(
        default=None,
        ge=0,
        description="Index of chunk in original document",
    )
    document_title: str | None = Field(
        default=None,
        description="Title of the source document",
    )
    highlights: list[str] = Field(
        default_factory=list,
        description="Highlighted matching portions",
    )

    @model_validator(mode="after")
    def validate_score_distance(self) -> "VectorSearchResult":
        """Ensure score and distance are consistent."""
        if self.distance is not None:
            # If distance is provided, it should be inversely related to score
            # This is a sanity check, not a strict mathematical relationship
            if self.distance > 100:  # Arbitrary large distance
                if self.score > 0.5:
                    raise ValueError("High distance should correspond to low score")
        return self

    def is_relevant(self, threshold: float = 0.7) -> bool:
        """Check if result meets relevance threshold."""
        return self.score >= threshold

    class Config:
        json_schema_extra = {
            "example": {
                "chunk_id": "chunk_456",
                "document_id": "doc_123",
                "content": "Python is a high-level programming language...",
                "score": 0.95,
                "distance": 0.05,
                "metadata": {
                    "source": "wikipedia",
                    "section": "introduction",
                },
                "rank": 1,
                "chunk_index": 0,
                "document_title": "Introduction to Python",
                "highlights": ["Python", "programming language"],
            }
        }


class RetrievalContext(BaseModel):
    """Combined retrieval context for agent.

    This aggregates multiple search results into a structured
    context that can be passed to the agent.

    Example:
        >>> context = RetrievalContext(
        ...     query="What is Python?",
        ...     results=[result1, result2],
        ...     total_results=5,
        ...     max_results=10
        ... )
    """

    query: str = Field(description="Original search query")
    results: list[VectorSearchResult] = Field(description="Retrieved search results")
    total_results: int = Field(
        ge=0,
        description="Total number of results found",
    )
    max_results: int = Field(
        ge=1,
        description="Maximum number of results requested",
    )
    retrieval_time_seconds: float = Field(
        default=0.0,
        ge=0.0,
        description="Time taken for retrieval",
    )
    reranked: bool = Field(
        default=False,
        description="Whether results were reranked",
    )
    filters_applied: dict[str, Any] = Field(
        default_factory=dict,
        description="Filters that were applied",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context metadata",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the retrieval occurred",
    )

    @field_validator("results")
    @classmethod
    def validate_results_count(cls, v: list[VectorSearchResult], info) -> list[VectorSearchResult]:
        """Validate results count matches constraints."""
        if "max_results" in info.data:
            max_results = info.data["max_results"]
            if len(v) > max_results:
                raise ValueError(
                    f"Number of results ({len(v)}) exceeds " f"max_results ({max_results})"
                )
        return v

    def get_top_k(self, k: int = 3) -> list[VectorSearchResult]:
        """Get top-k results."""
        return self.results[:k]

    def get_relevant_results(self, threshold: float = 0.7) -> list[VectorSearchResult]:
        """Get results above relevance threshold."""
        return [r for r in self.results if r.score >= threshold]

    def get_combined_content(self, separator: str = "\n\n") -> str:
        """Get all result content as a single string."""
        return separator.join(r.content for r in self.results)

    def get_unique_documents(self) -> list[str]:
        """Get list of unique document IDs in results."""
        return list(set(r.document_id for r in self.results))

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is Python programming?",
                "results": [
                    {
                        "chunk_id": "chunk_1",
                        "document_id": "doc_123",
                        "content": "Python is a high-level language...",
                        "score": 0.95,
                        "rank": 1,
                    },
                    {
                        "chunk_id": "chunk_2",
                        "document_id": "doc_124",
                        "content": "Python supports multiple paradigms...",
                        "score": 0.88,
                        "rank": 2,
                    },
                ],
                "total_results": 10,
                "max_results": 5,
                "retrieval_time_seconds": 0.25,
                "reranked": True,
                "filters_applied": {"language": "en", "tags": ["python"]},
                "timestamp": "2024-01-01T12:00:00Z",
            }
        }


class EmbeddingRequest(BaseModel):
    """Request for generating embeddings.

    Example:
        >>> request = EmbeddingRequest(
        ...     text="What is Python?",
        ...     model="amazon.titan-embed-text-v2:0"
        ... )
    """

    text: str | list[str] = Field(description="Text or list of texts to embed")
    model: str = Field(
        default="amazon.titan-embed-text-v2:0",
        description="Embedding model to use",
    )
    normalize: bool = Field(
        default=True,
        description="Whether to normalize embeddings",
    )
    dimensions: int | None = Field(
        default=None,
        gt=0,
        le=4096,
        description="Target embedding dimensions (if supported)",
    )

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str | list[str]) -> str | list[str]:
        """Validate text is not empty."""
        if isinstance(v, str):
            if not v.strip():
                raise ValueError("Text cannot be empty")
        elif isinstance(v, list):
            if not v:
                raise ValueError("Text list cannot be empty")
            if not all(isinstance(t, str) and t.strip() for t in v):
                raise ValueError("All texts must be non-empty strings")
        return v

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "text": "What is Python programming?",
                    "model": "amazon.titan-embed-text-v2:0",
                    "normalize": True,
                },
                {
                    "text": ["First text", "Second text"],
                    "model": "amazon.titan-embed-text-v2:0",
                    "normalize": True,
                    "dimensions": 1024,
                },
            ]
        }


class EmbeddingResponse(BaseModel):
    """Response containing embeddings.

    Example:
        >>> response = EmbeddingResponse(
        ...     embeddings=[[0.1, 0.2, 0.3]],
        ...     model="amazon.titan-embed-text-v2:0",
        ...     dimensions=3
        ... )
    """

    embeddings: list[list[float]] = Field(description="Generated embeddings")
    model: str = Field(description="Model used for embeddings")
    dimensions: int = Field(
        gt=0,
        description="Dimension of each embedding",
    )
    usage: dict[str, int] | None = Field(
        default=None,
        description="Token usage statistics",
    )

    @field_validator("embeddings")
    @classmethod
    def validate_embeddings(cls, v: list[list[float]]) -> list[list[float]]:
        """Validate embeddings are consistent."""
        if not v:
            raise ValueError("Embeddings list cannot be empty")

        # Check all embeddings have same dimension
        first_dim = len(v[0])
        if not all(len(emb) == first_dim for emb in v):
            raise ValueError("All embeddings must have the same dimension")

        return v

    class Config:
        json_schema_extra = {
            "example": {
                "embeddings": [
                    [0.1, 0.2, 0.3],  # Truncated for example
                    [0.4, 0.5, 0.6],
                ],
                "model": "amazon.titan-embed-text-v2:0",
                "dimensions": 3,
                "usage": {"total_tokens": 150},
            }
        }


# Export all models
__all__ = [
    "DocumentSource",
    "Document",
    "ChunkingStrategy",
    "Chunk",
    "VectorSearchResult",
    "RetrievalContext",
    "EmbeddingRequest",
    "EmbeddingResponse",
]
