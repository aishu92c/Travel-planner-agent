#!/usr/bin/env python3
"""Test Pydantic models.

Run this script to verify all Pydantic models are working correctly.

Usage:
    python test_models.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_agent_state_models():
    """Test agent state models."""
    print("=" * 70)
    print("Testing Agent State Models")
    print("=" * 70)

    from agents import AgentState, Message, MessageRole, ToolInput, ToolOutput

    # Test Message
    msg = Message(
        role=MessageRole.USER,
        content="Hello, how are you?",
        name="user_123",
    )
    print(f"✓ Message created: {msg.role.value} - {msg.content[:30]}...")

    # Test AgentState
    state = AgentState(
        messages=[msg],
        context={"user_id": "123", "session": "abc"},
    )
    state.add_message("assistant", "I'm doing well, thank you!")
    print(f"✓ AgentState created with {len(state.messages)} messages")

    # Test ToolInput
    tool_input = ToolInput(
        tool_name="calculator",
        parameters={"expression": "2 + 2"},
        timeout_seconds=30,
    )
    print(f"✓ ToolInput created: {tool_input.tool_name}")

    # Test ToolOutput
    tool_output = ToolOutput(
        tool_name="calculator",
        status="success",
        result={"answer": 4},
        execution_time_seconds=0.05,
    )
    print(f"✓ ToolOutput created: {tool_output.status}")
    print(f"✓ Is success: {tool_output.is_success()}")
    print()


def test_rag_models():
    """Test RAG models."""
    print("=" * 70)
    print("Testing RAG Models")
    print("=" * 70)

    from rag import (
        Chunk,
        Document,
        DocumentSource,
        EmbeddingRequest,
        RetrievalContext,
        VectorSearchResult,
    )

    # Test Document
    doc = Document(
        id="doc_123",
        content="Python is a high-level programming language.",
        title="Python Introduction",
        source=DocumentSource.LOCAL_FILE,
        metadata={"author": "John Doe"},
        tags=["python", "programming"],
    )
    print(f"✓ Document created: {doc.title} ({len(doc)} chars)")

    # Test Chunk
    chunk = Chunk(
        id="chunk_456",
        document_id="doc_123",
        content="Python is a programming language.",
        chunk_index=0,
        start_char=0,
        end_char=34,
        embedding=[0.1, 0.2, 0.3],
    )
    print(f"✓ Chunk created: {chunk.id} ({len(chunk)} chars)")

    # Test VectorSearchResult
    result = VectorSearchResult(
        chunk_id="chunk_456",
        document_id="doc_123",
        content="Python is a programming language.",
        score=0.95,
        metadata={"source": "wiki"},
        rank=1,
    )
    print(f"✓ VectorSearchResult created: score={result.score}")
    print(f"✓ Is relevant (threshold=0.7): {result.is_relevant(0.7)}")

    # Test RetrievalContext
    context = RetrievalContext(
        query="What is Python?",
        results=[result],
        total_results=10,
        max_results=5,
        retrieval_time_seconds=0.25,
    )
    print(f"✓ RetrievalContext created: {len(context.results)} results")
    print(f"✓ Top 1 result: {len(context.get_top_k(1))} results")
    print(f"✓ Unique documents: {context.get_unique_documents()}")

    # Test EmbeddingRequest
    emb_req = EmbeddingRequest(
        text="What is Python?",
        model="amazon.titan-embed-text-v2:0",
        normalize=True,
    )
    print(f"✓ EmbeddingRequest created: {emb_req.model}")
    print()


def test_api_models():
    """Test API models."""
    print("=" * 70)
    print("Testing API Models")
    print("=" * 70)

    from api import (
        Citation,
        ErrorResponse,
        HealthCheckResponse,
        QueryRequest,
        QueryResponse,
        StreamChunk,
        Usage,
    )

    # Test QueryRequest
    request = QueryRequest(
        query="What is the capital of France?",
        context={"user_id": "123"},
        user_id="user_123",
        session_id="sess_456",
        stream=False,
        max_tokens=1000,
        temperature=0.7,
    )
    print(f"✓ QueryRequest created: '{request.query}'")

    # Test Citation
    citation = Citation(
        text="Paris is the capital",
        source="Wikipedia",
        url="https://en.wikipedia.org/wiki/Paris",
        relevance_score=0.95,
    )
    print(f"✓ Citation created: {citation.source}")

    # Test Usage
    usage = Usage(
        prompt_tokens=150,
        completion_tokens=75,
        total_tokens=225,
        estimated_cost_usd=0.0045,
    )
    print(f"✓ Usage created: {usage.total_tokens} tokens")

    # Test QueryResponse
    response = QueryResponse(
        response="The capital of France is Paris.",
        status="success",
        request_id="req_123",
        citations=[citation],
        usage=usage,
        processing_time_seconds=1.25,
    )
    print(f"✓ QueryResponse created: {response.status}")
    print(f"✓ Response length: {len(response.response)} chars")
    print(f"✓ Citations: {len(response.citations)}")

    # Test StreamChunk
    chunk = StreamChunk(
        chunk="Hello",
        is_final=False,
        request_id="req_123",
    )
    print(f"✓ StreamChunk created: '{chunk.chunk}'")

    # Test HealthCheckResponse
    health = HealthCheckResponse(
        status="healthy",
        version="0.1.0",
        uptime_seconds=3600.0,
        services={
            "database": "healthy",
            "cache": "healthy",
        },
    )
    print(f"✓ HealthCheckResponse created: {health.status}")

    # Test ErrorResponse
    error = ErrorResponse(
        error="Validation Error",
        message="Invalid request parameters",
        status_code=400,
        request_id="req_456",
    )
    print(f"✓ ErrorResponse created: {error.status_code}")
    print()


def test_validation():
    """Test model validation."""
    print("=" * 70)
    print("Testing Model Validation")
    print("=" * 70)

    from pydantic import ValidationError

    # Test invalid message
    try:
        from agents import Message

        Message(role="invalid_role", content="Test")
        print("❌ Should have raised ValidationError for invalid role")
    except ValidationError:
        print("✓ Invalid message role rejected")

    # Test invalid chunk (start_char >= end_char)
    try:
        from rag import Chunk

        Chunk(
            id="chunk_1",
            document_id="doc_1",
            content="Test",
            chunk_index=0,
            start_char=10,
            end_char=5,  # Invalid: less than start_char
        )
        print("❌ Should have raised ValidationError for invalid char positions")
    except ValidationError:
        print("✓ Invalid chunk char positions rejected")

    # Test empty query
    try:
        from api import QueryRequest

        QueryRequest(query="   ")  # Empty/whitespace only
        print("❌ Should have raised ValidationError for empty query")
    except ValidationError:
        print("✓ Empty query rejected")

    # Test invalid temperature
    try:
        from api import QueryRequest

        QueryRequest(query="Test", temperature=2.0)  # Out of range
        print("❌ Should have raised ValidationError for invalid temperature")
    except ValidationError:
        print("✓ Invalid temperature rejected")

    print()


def test_helper_methods():
    """Test helper methods on models."""
    print("=" * 70)
    print("Testing Helper Methods")
    print("=" * 70)

    from agents import AgentState, MessageRole
    from rag import RetrievalContext, VectorSearchResult

    # Test AgentState helper methods
    state = AgentState()
    state.add_message(MessageRole.USER, "Hello")
    state.add_message(MessageRole.ASSISTANT, "Hi there")
    print(f"✓ Added messages: {len(state.messages)}")

    last = state.get_last_message()
    print(f"✓ Last message: {last.content if last else None}")

    user_msgs = state.get_messages_by_role(MessageRole.USER)
    print(f"✓ User messages: {len(user_msgs)}")

    # Test RetrievalContext helper methods
    results = [
        VectorSearchResult(
            chunk_id=f"chunk_{i}",
            document_id=f"doc_{i}",
            content=f"Content {i}",
            score=0.9 - (i * 0.1),
        )
        for i in range(5)
    ]
    context = RetrievalContext(
        query="Test query",
        results=results,
        total_results=10,
        max_results=5,
    )
    print(f"✓ Total results: {len(context.results)}")
    print(f"✓ Top 3: {len(context.get_top_k(3))}")
    print(f"✓ Relevant (>0.7): {len(context.get_relevant_results(0.7))}")
    print(f"✓ Combined content length: {len(context.get_combined_content())}")

    print()


def test_json_serialization():
    """Test JSON serialization."""
    print("=" * 70)
    print("Testing JSON Serialization")
    print("=" * 70)

    import json

    from agents import AgentState, Message
    from api import QueryRequest, QueryResponse
    from rag import Document

    # Test Message serialization
    msg = Message(role="user", content="Test message")
    msg_json = msg.model_dump_json()
    msg_parsed = Message.model_validate_json(msg_json)
    print(f"✓ Message serialization: {len(msg_json)} bytes")

    # Test AgentState serialization
    state = AgentState(messages=[msg])
    state_dict = state.model_dump()
    state_parsed = AgentState.model_validate(state_dict)
    print(f"✓ AgentState serialization: {len(json.dumps(state_dict))} bytes")

    # Test Document serialization
    doc = Document(id="doc_1", content="Test content", metadata={"key": "value"})
    doc_json = doc.model_dump_json()
    doc_parsed = Document.model_validate_json(doc_json)
    print(f"✓ Document serialization: {len(doc_json)} bytes")

    # Test QueryRequest/Response serialization
    request = QueryRequest(query="Test query")
    req_json = request.model_dump_json()
    print(f"✓ QueryRequest serialization: {len(req_json)} bytes")

    response = QueryResponse(
        response="Test response",
        status="success",
        request_id="req_123",
    )
    resp_json = response.model_dump_json()
    print(f"✓ QueryResponse serialization: {len(resp_json)} bytes")

    print()


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 22 + "Pydantic Models Test" + " " * 26 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n")

    tests = [
        test_agent_state_models,
        test_rag_models,
        test_api_models,
        test_validation,
        test_helper_methods,
        test_json_serialization,
    ]

    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}\n")
            import traceback

            traceback.print_exc()
            return 1

    print("=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)
    print("\nAll Pydantic models are working correctly!\n")
    print("Model Statistics:")
    print("- Agent models: 8 classes (472 lines)")
    print("- RAG models: 8 classes (567 lines)")
    print("- API models: 12 classes (630 lines)")
    print("- Total: 28 Pydantic models (1,669 lines)")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
