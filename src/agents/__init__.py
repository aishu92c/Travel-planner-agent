"""LangGraph Agents Module.

Contains LangGraph agent definitions and orchestration logic.

This module provides:
- Multi-agent workflow definitions
- Agent state management with DynamoDB checkpointing
- Conditional routing logic
- Tool definitions and integrations
- Human-in-the-loop capabilities
- Agent supervisor and coordinator patterns

Example:
    >>> from agents import AgentState, Message, ToolInput, ToolOutput
    >>> from agents import ResearchAgent, AnalysisAgent, create_agent_graph
    >>> state = AgentState(messages=[Message(role="user", content="Hello")])
    >>> graph = create_agent_graph()
    >>> result = graph.invoke(state)
"""

# State models
from .state import (
    AgentDecision,
    AgentMetadata,
    AgentState,
    Message,
    MessageRole,
    ToolInput,
    ToolOutput,
    ToolStatus,
)

# Future agent implementations will go here
# from .base import BaseAgent
# from .research import ResearchAgent
# from .analysis import AnalysisAgent
# from .supervisor import SupervisorAgent
# from .graph import create_agent_graph

__all__ = [
    # State models
    "MessageRole",
    "Message",
    "AgentMetadata",
    "AgentState",
    "ToolInput",
    "ToolStatus",
    "ToolOutput",
    "AgentDecision",
    # Future agent classes will be added here
]
