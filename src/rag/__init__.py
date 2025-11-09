"""RAG (Retrieval-Augmented Generation) Module.

Provides retrieval-augmented generation capabilities for the LangGraph system.

This module provides:
- Vector database integrations (ChromaDB, FAISS)
- Embedding generation with AWS Bedrock
- Semantic search and retrieval
- Document reranking strategies
- Query reformulation
- Context window management

Example:
    >>> from rag import Document, Chunk, VectorSearchResult, RetrievalContext
    >>> from rag import VectorStore, Retriever
    >>> doc = Document(id="doc_1", content="Python is great", metadata={})
    >>> vector_store = VectorStore(provider="chromadb")
    >>> retriever = Retriever(vector_store=vector_store)
    >>> results = retriever.retrieve("What is LangGraph?", top_k=5)
"""

# Data models
from .models import (
    Chunk,
    ChunkingStrategy,
    Document,
    DocumentSource,
    EmbeddingRequest,
    EmbeddingResponse,
    RetrievalContext,
    VectorSearchResult,
)

# Future implementations will go here
# from .vector_store import VectorStore
# from .retriever import Retriever
# from .embeddings import EmbeddingGenerator
# from .reranker import Reranker

__all__ = [
    # Data models
    "DocumentSource",
    "Document",
    "ChunkingStrategy",
    "Chunk",
    "VectorSearchResult",
    "RetrievalContext",
    "EmbeddingRequest",
    "EmbeddingResponse",
    # Future implementations will be added here
]
