# Pydantic Models Documentation

Comprehensive Pydantic models for the LangGraph AWS Template.

## Overview

This project includes 28 production-ready Pydantic models organized into three modules:

- **Agent Models** (`src/agents/state.py`) - 8 models, 472 lines
- **RAG Models** (`src/rag/models.py`) - 8 models, 567 lines
- **API Models** (`src/api/models.py`) - 12 models, 630 lines

Total: **1,669 lines of fully typed, validated, and documented models**.

## Quick Start

```python
# Import agent models
from agents import AgentState, Message, ToolInput, ToolOutput

# Import RAG models
from rag import Document, Chunk, VectorSearchResult, RetrievalContext

# Import API models
from api import QueryRequest, QueryResponse, HealthCheckResponse, ErrorResponse
```

## Agent Models (`agents.state`)

### Agent Core Models

#### Message

Represents a single message in a conversation.

```python
from agents import Message, MessageRole

msg = Message(
    role=MessageRole.USER,
    content="What is AI?",
    name="user_123",
    metadata={"source": "web"}
)
```

#### AgentState

Complete state of a LangGraph agent execution.

```python
from agents import AgentState, Message

state = AgentState(
    messages=[Message(role="user", content="Hello")],
    context={"user_id": "123"},
    is_complete=False
)

# Helper methods
state.add_message("assistant", "Hi there!")
last_msg = state.get_last_message()
user_messages = state.get_messages_by_role("user")
```

#### ToolInput

Schema for tool invocations.

```python
from agents import ToolInput

tool_input = ToolInput(
    tool_name="web_search",
    parameters={"query": "Python tutorials", "max_results": 5},
    timeout_seconds=30,
    max_retries=3
)
```

#### ToolOutput

Results from tool execution.

```python
from agents import ToolOutput

output = ToolOutput(
    tool_name="calculator",
    status="success",
    result={"answer": 42},
    execution_time_seconds=0.5
)

# Helper methods
if output.is_success():
    print(output.result)
```

### Agent Supporting Models

- **MessageRole** - Enum for message roles (user, assistant, system, tool)
- **AgentMetadata** - Execution metadata (agent_id, user_id, session_id, etc.)
- **ToolStatus** - Enum for tool status (success, failed, timeout, etc.)
- **AgentDecision** - Routing decisions in multi-agent workflows

## RAG Models (`rag.models`)

### RAG Core Models

#### Document

Complete document in the RAG system.

```python
from rag import Document, DocumentSource

doc = Document(
    id="doc_123",
    content="Python is a programming language...",
    title="Python Introduction",
    source=DocumentSource.LOCAL_FILE,
    metadata={"author": "John Doe"},
    tags=["python", "programming"]
)

print(len(doc))  # Content length
```

#### Chunk

Document chunks for vector storage.

```python
from rag import Chunk, ChunkingStrategy

chunk = Chunk(
    id="chunk_456",
    document_id="doc_123",
    content="Python is a programming language.",
    chunk_index=0,
    start_char=0,
    end_char=34,
    embedding=[0.1, 0.2, 0.3],  # Vector embedding
    chunking_strategy=ChunkingStrategy.SENTENCE
)
```

#### VectorSearchResult

Search result from vector database.

```python
from rag import VectorSearchResult

result = VectorSearchResult(
    chunk_id="chunk_456",
    document_id="doc_123",
    content="Python is a programming language.",
    score=0.95,
    rank=1,
    metadata={"source": "wiki"}
)

# Helper method
if result.is_relevant(threshold=0.7):
    print("Result is relevant!")
```

#### RetrievalContext

Aggregated retrieval context for agents.

```python
from rag import RetrievalContext

context = RetrievalContext(
    query="What is Python?",
    results=[result1, result2, result3],
    total_results=10,
    max_results=5,
    retrieval_time_seconds=0.25
)

# Helper methods
top_3 = context.get_top_k(3)
relevant = context.get_relevant_results(threshold=0.7)
combined_text = context.get_combined_content()
unique_docs = context.get_unique_documents()
```

### RAG Supporting Models

- **DocumentSource** - Enum for document sources (local_file, s3, url, etc.)
- **ChunkingStrategy** - Enum for chunking strategies (fixed_size, sentence,
  semantic, etc.)
- **EmbeddingRequest** - Request for generating embeddings
- **EmbeddingResponse** - Response with generated embeddings

## API Models (`api.models`)

### API Core Models

#### QueryRequest

API request for agent queries.

```python
from api import QueryRequest

request = QueryRequest(
    query="What is the capital of France?",
    context={"user_id": "123"},
    user_id="user_123",
    session_id="sess_456",
    stream=False,
    max_tokens=1000,
    temperature=0.7,
    enable_rag=True,
    enable_tools=True
)
```

#### QueryResponse

API response with results.

```python
from api import QueryResponse, Citation, Usage

response = QueryResponse(
    response="The capital of France is Paris.",
    status="success",
    request_id="req_123",
    citations=[
        Citation(
            text="Paris is the capital",
            source="Wikipedia",
            url="https://en.wikipedia.org/wiki/Paris",
            relevance_score=0.95
        )
    ],
    usage=Usage(
        prompt_tokens=150,
        completion_tokens=75,
        total_tokens=225
    ),
    processing_time_seconds=1.25
)
```

#### HealthCheckResponse

Health endpoint response.

```python
from api import HealthCheckResponse, ServiceStatus

health = HealthCheckResponse(
    status=ServiceStatus.HEALTHY,
    version="0.1.0",
    uptime_seconds=3600.0,
    services={
        "database": ServiceStatus.HEALTHY,
        "cache": ServiceStatus.HEALTHY,
        "vectordb": ServiceStatus.HEALTHY
    },
    metrics={
        "requests_per_second": 150,
        "avg_latency_ms": 250,
        "error_rate": 0.01
    }
)
```

#### ErrorResponse

Standard error format.

```python
from api import ErrorResponse, ErrorDetail

error = ErrorResponse(
    error="Validation Error",
    message="Invalid request parameters",
    status_code=400,
    request_id="req_456",
    details=[
        ErrorDetail(
            field="query",
            message="Query cannot be empty",
            error_code="REQUIRED_FIELD"
        )
    ]
)
```

### API Supporting Models

- **ResponseStatus** - Enum for response status (success, partial, error, timeout)
- **Citation** - Citation for information sources
- **Usage** - Token usage statistics
- **StreamChunk** - Chunk for streaming responses
- **ServiceStatus** - Enum for service health (healthy, degraded, unhealthy)
- **ErrorDetail** - Detailed error information
- **BatchQueryRequest** - Request for batch processing
- **BatchQueryResponse** - Response for batch processing

## Features

### Type Safety

All models are fully typed with proper type hints:

```python
from typing import List, Dict, Optional
from pydantic import Field

class Example(BaseModel):
    required_field: str = Field(description="Required string")
    optional_field: Optional[int] = Field(default=None, description="Optional int")
    list_field: List[str] = Field(default_factory=list)
    dict_field: Dict[str, Any] = Field(default_factory=dict)
```

### Validation

Built-in validation for all fields:

```python
from pydantic import Field, field_validator

class ValidatedModel(BaseModel):
    temperature: float = Field(ge=0.0, le=1.0)  # Range validation
    text: str = Field(min_length=1, max_length=1000)  # Length validation

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Text cannot be empty")
        return v.strip()
```

### Documentation

Every model includes:

- Field descriptions
- Usage examples
- Helper methods
- Validation rules

```python
class DocumentedModel(BaseModel):
    """Model with full documentation.

    Example:
        >>> model = DocumentedModel(field="value")
    """

    field: str = Field(
        description="Clear description of what this field represents"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "field": "example_value"
            }
        }
```

### Serialization

All models support JSON serialization:

```python
from agents import AgentState, Message

# Create model
state = AgentState(messages=[Message(role="user", content="Hello")])

# Serialize to JSON
json_str = state.model_dump_json()

# Deserialize from JSON
state_copy = AgentState.model_validate_json(json_str)

# Convert to dict
state_dict = state.model_dump()
```

## Testing

Run the comprehensive test suite:

```bash
python test_models.py
```

Tests cover:

- Model creation
- Validation
- Helper methods
- JSON serialization
- Error cases

## Best Practices

### 1. Always Use Type Hints

```python
# Good
from typing import List, Optional
field: Optional[List[str]] = Field(default=None)

# Bad
field = Field(default=None)
```

### 2. Provide Descriptions

```python
# Good
field: str = Field(description="Clear description of the field")

# Bad
field: str
```

### 3. Use Field Validators

```python
@field_validator("email")
@classmethod
def validate_email(cls, v: str) -> str:
    if "@" not in v:
        raise ValueError("Invalid email format")
    return v.lower()
```

### 4. Include Examples

```python
class Config:
    json_schema_extra = {
        "example": {
            "field1": "value1",
            "field2": 42
        }
    }
```

### 5. Use Enums for Fixed Values

```python
from enum import Enum

class Status(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
```

## Common Patterns

### Optional vs Required Fields

```python
# Required field
name: str = Field(description="Required name")

# Optional with default
count: int = Field(default=0, description="Optional count")

# Optional without default
metadata: Optional[Dict[str, Any]] = Field(default=None)

# Required with factory default
tags: List[str] = Field(default_factory=list)
```

### Validation Patterns

```python
# Range validation
age: int = Field(ge=0, le=120)
score: float = Field(ge=0.0, le=1.0)

# Length validation
text: str = Field(min_length=1, max_length=1000)
items: List[str] = Field(min_length=1, max_length=100)

# Custom validation
@field_validator("email")
@classmethod
def validate_email(cls, v: str) -> str:
    # Custom validation logic
    return v
```

### Model Composition

```python
class Inner(BaseModel):
    field1: str

class Outer(BaseModel):
    inner: Inner = Field(description="Nested model")
    inner_optional: Optional[Inner] = Field(default=None)
    inner_list: List[Inner] = Field(default_factory=list)
```

## Performance Considerations

1. **Use `default_factory`** for mutable defaults (list, dict)
2. **Cache settings** with `@lru_cache` when appropriate
3. **Use `model_copy()`** for efficient copying
4. **Validate once** at creation, not repeatedly

## Integration Examples

### With LangGraph

```python
from agents import AgentState, Message
from langgraph.graph import StateGraph

def process_message(state: AgentState) -> AgentState:
    # Process state
    state.add_message("assistant", "Response")
    return state

graph = StateGraph(AgentState)
graph.add_node("process", process_message)
```

### With FastAPI

```python
from fastapi import FastAPI
from api import QueryRequest, QueryResponse

app = FastAPI()

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    # Process request
    return QueryResponse(
        response="Generated response",
        status="success",
        request_id="req_123"
    )
```

### With AWS Bedrock

```python
from agents import AgentState
import boto3

def invoke_bedrock(state: AgentState) -> str:
    bedrock = boto3.client("bedrock-runtime")
    # Use state.messages to build prompt
    # Return response
    return "Response from Bedrock"
```

## Summary

- **28 Pydantic models** across 3 modules
- **Fully typed** with comprehensive type hints
- **Validated** with built-in and custom validators
- **Documented** with examples and descriptions
- **Tested** with comprehensive test suite
- **Production-ready** for immediate use

Run `python test_models.py` to verify everything works!
