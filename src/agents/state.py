"""Agent State Models.

Pydantic models for LangGraph agent state management, including
state schemas, tool inputs/outputs, and message handling.

Example:
    >>> from agents.state import AgentState, ToolInput, ToolOutput
    >>> state = AgentState(
    ...     messages=[{"role": "user", "content": "Hello"}],
    ...     context={"user_id": "123"}
    ... )
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class MessageRole(str, Enum):
    """Message role in conversation."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TOOL = "tool"


class Message(BaseModel):
    """A single message in the conversation.

    Example:
        >>> msg = Message(
        ...     role="user",
        ...     content="What is the weather?",
        ...     name="user_123"
        ... )
    """

    role: MessageRole = Field(description="Role of the message sender")
    content: str = Field(
        description="Content of the message",
        min_length=1,
    )
    name: str | None = Field(
        default=None,
        description="Optional name of the sender",
    )
    function_call: dict[str, Any] | None = Field(
        default=None,
        description="Function call details if role is function",
    )
    tool_calls: list[dict[str, Any]] | None = Field(
        default=None,
        description="Tool calls made in this message",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the message was created",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "What is the capital of France?",
                "name": "user_123",
                "metadata": {"source": "web"},
                "timestamp": "2024-01-01T12:00:00Z",
            }
        }


class AgentMetadata(BaseModel):
    """Metadata for agent execution.

    Example:
        >>> metadata = AgentMetadata(
        ...     agent_id="research_agent",
        ...     user_id="user_123",
        ...     session_id="session_456"
        ... )
    """

    agent_id: str = Field(description="Unique identifier for the agent")
    user_id: str | None = Field(
        default=None,
        description="User identifier",
    )
    session_id: str | None = Field(
        default=None,
        description="Session identifier",
    )
    parent_run_id: str | None = Field(
        default=None,
        description="Parent run ID for nested agents",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorization",
    )
    custom_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Custom metadata fields",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "research_agent",
                "user_id": "user_123",
                "session_id": "session_456",
                "tags": ["research", "finance"],
                "custom_data": {"department": "analytics"},
                "created_at": "2024-01-01T12:00:00Z",
            }
        }


class AgentState(BaseModel):
    """LangGraph agent state schema.

    This represents the complete state of an agent execution,
    including conversation history, context, and metadata.

    Example:
        >>> state = AgentState(
        ...     messages=[
        ...         Message(role="user", content="Hello"),
        ...         Message(role="assistant", content="Hi there!"),
        ...     ],
        ...     context={"user_id": "123", "session": "abc"},
        ...     metadata=AgentMetadata(agent_id="chat_agent")
        ... )
    """

    messages: list[Message] = Field(
        default_factory=list,
        description="Conversation message history",
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context for the agent",
    )
    metadata: AgentMetadata | None = Field(
        default=None,
        description="Execution metadata",
    )
    intermediate_steps: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Steps taken during execution",
    )
    tool_results: list["ToolOutput"] = Field(
        default_factory=list,
        description="Results from tool calls",
    )
    error: str | None = Field(
        default=None,
        description="Error message if execution failed",
    )
    is_complete: bool = Field(
        default=False,
        description="Whether execution is complete",
    )
    iteration_count: int = Field(
        default=0,
        ge=0,
        description="Number of iterations executed",
    )
    next_agent: str | None = Field(
        default=None,
        description="Next agent to route to (for multi-agent)",
    )

    @field_validator("iteration_count")
    @classmethod
    def validate_iteration_count(cls, v: int) -> int:
        """Validate iteration count is reasonable."""
        if v > 100:
            raise ValueError("Iteration count exceeds maximum (100)")
        return v

    def add_message(self, role: str | MessageRole, content: str, **kwargs: Any) -> None:
        """Add a message to the conversation.

        Args:
            role: Message role
            content: Message content
            **kwargs: Additional message fields
        """
        if isinstance(role, str):
            role = MessageRole(role)
        msg = Message(role=role, content=content, **kwargs)
        self.messages.append(msg)

    def get_last_message(self) -> Message | None:
        """Get the last message in the conversation."""
        return self.messages[-1] if self.messages else None

    def get_messages_by_role(self, role: str | MessageRole) -> list[Message]:
        """Get all messages with a specific role."""
        if isinstance(role, str):
            role = MessageRole(role)
        return [msg for msg in self.messages if msg.role == role]

    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {
                        "role": "user",
                        "content": "What is AI?",
                        "timestamp": "2024-01-01T12:00:00Z",
                    },
                    {
                        "role": "assistant",
                        "content": "AI stands for Artificial Intelligence...",
                        "timestamp": "2024-01-01T12:00:01Z",
                    },
                ],
                "context": {"user_id": "123", "source": "web"},
                "metadata": {
                    "agent_id": "qa_agent",
                    "session_id": "sess_123",
                },
                "is_complete": True,
                "iteration_count": 1,
            }
        }


class ToolInput(BaseModel):
    """Schema for tool invocations.

    Example:
        >>> tool_input = ToolInput(
        ...     tool_name="web_search",
        ...     parameters={"query": "Python tutorials", "max_results": 5},
        ...     metadata={"priority": "high"}
        ... )
    """

    tool_name: str = Field(
        description="Name of the tool to invoke",
        min_length=1,
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters to pass to the tool",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for the tool call",
    )
    timeout_seconds: float | None = Field(
        default=None,
        gt=0,
        le=300,
        description="Timeout for tool execution",
    )
    retry_on_failure: bool = Field(
        default=True,
        description="Whether to retry on failure",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of retries",
    )

    @field_validator("tool_name")
    @classmethod
    def validate_tool_name(cls, v: str) -> str:
        """Validate tool name format."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "Tool name must contain only letters, numbers, " "underscores, and hyphens"
            )
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "tool_name": "web_search",
                "parameters": {
                    "query": "Python tutorials",
                    "max_results": 5,
                },
                "metadata": {"source": "agent"},
                "timeout_seconds": 30,
                "retry_on_failure": True,
                "max_retries": 3,
            }
        }


class ToolStatus(str, Enum):
    """Status of tool execution."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class ToolOutput(BaseModel):
    """Schema for tool execution results.

    Example:
        >>> output = ToolOutput(
        ...     tool_name="calculator",
        ...     status="success",
        ...     result={"answer": 42},
        ...     execution_time_seconds=0.5
        ... )
    """

    tool_name: str = Field(description="Name of the executed tool")
    status: ToolStatus = Field(description="Execution status")
    result: Any | None = Field(
        default=None,
        description="Result data from the tool",
    )
    error: str | None = Field(
        default=None,
        description="Error message if execution failed",
    )
    error_type: str | None = Field(
        default=None,
        description="Type of error that occurred",
    )
    execution_time_seconds: float = Field(
        default=0.0,
        ge=0,
        description="Time taken to execute the tool",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )
    logs: list[str] = Field(
        default_factory=list,
        description="Execution logs",
    )
    artifacts: dict[str, str] = Field(
        default_factory=dict,
        description="Generated artifacts (file paths, URLs, etc.)",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the tool was executed",
    )

    @model_validator(mode="after")
    def validate_result_or_error(self) -> "ToolOutput":
        """Ensure result or error is present based on status."""
        if self.status == ToolStatus.SUCCESS and self.result is None:
            raise ValueError("Success status requires a result")
        if self.status == ToolStatus.FAILED and not self.error:
            raise ValueError("Failed status requires an error message")
        return self

    def is_success(self) -> bool:
        """Check if tool execution was successful."""
        return self.status == ToolStatus.SUCCESS

    def is_failure(self) -> bool:
        """Check if tool execution failed."""
        return self.status in (ToolStatus.FAILED, ToolStatus.TIMEOUT)

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "tool_name": "calculator",
                    "status": "success",
                    "result": {"answer": 42, "expression": "6 * 7"},
                    "execution_time_seconds": 0.05,
                    "timestamp": "2024-01-01T12:00:00Z",
                },
                {
                    "tool_name": "web_search",
                    "status": "failed",
                    "error": "API rate limit exceeded",
                    "error_type": "RateLimitError",
                    "execution_time_seconds": 1.2,
                    "logs": ["Attempting request...", "Rate limit hit"],
                    "timestamp": "2024-01-01T12:00:00Z",
                },
            ]
        }


class AgentDecision(BaseModel):
    """Represents an agent's decision at a routing point.

    Example:
        >>> decision = AgentDecision(
        ...     next_node="research_agent",
        ...     reasoning="User query requires research",
        ...     confidence=0.95
        ... )
    """

    next_node: str = Field(description="Next node/agent to route to")
    reasoning: str = Field(description="Explanation for the decision")
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score for the decision",
    )
    alternatives: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Alternative routing options considered",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional decision metadata",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "next_node": "research_agent",
                "reasoning": "Query requires external research",
                "confidence": 0.95,
                "alternatives": [
                    {"node": "qa_agent", "confidence": 0.3},
                    {"node": "end", "confidence": 0.1},
                ],
            }
        }


# Export all models
__all__ = [
    "MessageRole",
    "Message",
    "AgentMetadata",
    "AgentState",
    "ToolInput",
    "ToolStatus",
    "ToolOutput",
    "AgentDecision",
]
