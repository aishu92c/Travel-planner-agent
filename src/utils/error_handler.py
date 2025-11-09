"""Custom exceptions and error handling utilities for the travel planner agent.

This module provides:
- Custom exception classes for different error scenarios
- Error handling decorators for nodes and tools
- Error recovery utilities
- Error context management

Example:
    >>> from src.utils.error_handler import (
    ...     AgentError,
    ...     ToolExecutionError,
    ...     handle_node_errors,
    ... )
    >>> @handle_node_errors
    ... def my_node(state):
    ...     # Your code here
    ...     return state
"""

import logging
import traceback
from functools import wraps
from typing import Any, Callable, Dict, Optional

from src.agents.state import AgentState


# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class AgentError(Exception):
    """Base exception for agent errors.

    All custom exceptions in the agent system inherit from this class.
    This allows for catching all agent-specific errors with a single
    except clause.

    Example:
        >>> try:
        ...     risky_operation()
        ... except AgentError as e:
        ...     print(f"Agent error: {e}")
    """
    pass


class ToolExecutionError(AgentError):
    """Raised when a tool fails to execute.

    This exception wraps errors that occur during tool execution,
    providing context about which tool failed and the original error.

    Attributes:
        tool_name: Name of the tool that failed
        original_error: The original exception that was raised

    Example:
        >>> try:
        ...     result = search_tool(inputs)
        ... except Exception as e:
        ...     raise ToolExecutionError("flight_search", e)
    """

    def __init__(self, tool_name: str, original_error: Exception):
        """Initialize ToolExecutionError.

        Args:
            tool_name: Name of the tool that failed
            original_error: The original exception that occurred
        """
        self.tool_name = tool_name
        self.original_error = original_error
        super().__init__(f"Tool '{tool_name}' failed: {str(original_error)}")


class BudgetValidationError(AgentError):
    """Raised when budget validation fails.

    This exception is raised when:
    - Budget is negative or zero
    - Budget is insufficient for the destination
    - Duration doesn't align with budget
    - Budget allocation is invalid

    Example:
        >>> if budget < minimum_required:
        ...     raise BudgetValidationError(
        ...         f"Budget ${budget} is less than minimum ${minimum_required}"
        ...     )
    """
    pass


class LLMError(AgentError):
    """Raised when LLM call fails.

    This exception is raised when:
    - API key is missing or invalid
    - API call times out
    - API returns an error
    - Response parsing fails
    - Rate limiting occurs

    Example:
        >>> try:
        ...     response = llm.invoke(prompt)
        ... except Exception as e:
        ...     raise LLMError(f"LLM call failed: {str(e)}")
    """
    pass


class StateValidationError(AgentError):
    """Raised when state validation fails.

    This exception is raised when required state fields are missing
    or have invalid values.

    Example:
        >>> if not state.destination:
        ...     raise StateValidationError("Destination is required")
    """
    pass


class SearchError(AgentError):
    """Raised when search (flights, hotels, activities) fails.

    This exception is raised when search operations return no results
    or encounter errors.
    """
    pass


class ItineraryGenerationError(AgentError):
    """Raised when itinerary generation fails.

    This exception is raised when the itinerary cannot be generated
    due to missing data, LLM errors, or other issues.
    """
    pass


# ============================================================================
# ERROR DECORATORS
# ============================================================================

def handle_node_errors(func: Callable) -> Callable:
    """Decorator to handle errors in node functions.

    This decorator wraps node functions to:
    1. Catch all exceptions
    2. Set state["error_message"] with error details
    3. Log the error with context
    4. Return state with error information

    The decorated function should accept state as first parameter
    and return a dictionary (or modified state).

    Args:
        func: Node function to wrap

    Returns:
        Wrapped function that handles errors gracefully

    Example:
        >>> @handle_node_errors
        ... def budget_analysis_node(state: AgentState):
        ...     # Your node logic
        ...     return state
        >>>
        >>> # If an error occurs, it's automatically caught and logged
        >>> result = budget_analysis_node(state)
        >>> if result.get("error_message"):
        ...     print(f"Error: {result['error_message']}")
    """
    logger = logging.getLogger(f"nodes.{func.__name__}")

    @wraps(func)
    def wrapper(state: AgentState, *args, **kwargs) -> Dict[str, Any]:
        """Wrap node execution with error handling.

        Args:
            state: Current agent state
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        Returns:
            State dictionary, potentially with error_message set
        """
        node_name = func.__name__

        try:
            logger.info(f"[START] {node_name}")
            logger.debug(f"Input state keys: {list(state.__dict__.keys())}")

            # Call the actual node function
            result = func(state, *args, **kwargs)

            logger.info(f"[END] {node_name} completed successfully")

            # Ensure result is a dictionary
            if isinstance(result, dict):
                return result
            else:
                logger.warning(f"{node_name} returned non-dict result: {type(result)}")
                return {"error_message": f"Invalid return type from {node_name}"}

        except AgentError as e:
            # Handle custom agent errors
            logger.error(f"[ERROR] {node_name}: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}")
            logger.exception("Stack trace:")

            return {
                "error_message": str(e),
                "error_type": type(e).__name__,
                "node_name": node_name,
            }

        except Exception as e:
            # Handle unexpected errors
            logger.error(f"[ERROR] {node_name}: Unexpected error")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}")
            logger.exception("Full traceback:")

            error_msg = f"Unexpected error in {node_name}: {type(e).__name__}: {str(e)}"

            return {
                "error_message": error_msg,
                "error_type": type(e).__name__,
                "node_name": node_name,
                "traceback": traceback.format_exc(),
            }

    return wrapper


def handle_tool_errors(func: Callable) -> Callable:
    """Decorator to handle errors in tool functions.

    Similar to handle_node_errors but specialized for tool execution.

    Args:
        func: Tool function to wrap

    Returns:
        Wrapped function that handles errors gracefully

    Example:
        >>> @handle_tool_errors
        ... def search_flights_tool(destination, budget):
        ...     # Your tool logic
        ...     return results
    """
    logger = logging.getLogger(f"tools.{func.__name__}")

    @wraps(func)
    def wrapper(*args, **kwargs) -> Dict[str, Any]:
        """Wrap tool execution with error handling.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Result dictionary, potentially with error info
        """
        tool_name = func.__name__

        try:
            logger.info(f"[START] {tool_name}")
            logger.debug(f"Arguments: args={args}, kwargs={kwargs}")

            result = func(*args, **kwargs)

            logger.info(f"[END] {tool_name} completed")

            return result if isinstance(result, dict) else {"result": result}

        except ToolExecutionError as e:
            logger.error(f"[ERROR] Tool execution failed: {str(e)}")
            logger.exception("Stack trace:")

            return {
                "error": str(e),
                "tool_name": e.tool_name,
                "original_error": str(e.original_error),
            }

        except Exception as e:
            logger.error(f"[ERROR] {tool_name}: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}")
            logger.exception("Full traceback:")

            raise ToolExecutionError(tool_name, e)

    return wrapper


# ============================================================================
# ERROR RECOVERY UTILITIES
# ============================================================================

def is_error_state(state: Dict[str, Any]) -> bool:
    """Check if state contains an error.

    Args:
        state: State dictionary to check

    Returns:
        True if error_message is set, False otherwise
    """
    return bool(state.get("error_message"))


def get_error_message(state: Dict[str, Any]) -> Optional[str]:
    """Get error message from state.

    Args:
        state: State dictionary

    Returns:
        Error message if present, None otherwise
    """
    return state.get("error_message")


def get_error_type(state: Dict[str, Any]) -> Optional[str]:
    """Get error type from state.

    Args:
        state: State dictionary

    Returns:
        Error type if present, None otherwise
    """
    return state.get("error_type")


def clear_error(state: Dict[str, Any]) -> Dict[str, Any]:
    """Clear error information from state.

    Args:
        state: State dictionary

    Returns:
        State with error fields removed
    """
    error_fields = ["error_message", "error_type", "node_name", "traceback"]
    return {k: v for k, v in state.items() if k not in error_fields}


# ============================================================================
# ERROR CONTEXT MANAGER
# ============================================================================

class ErrorContext:
    """Context manager for error handling with logging.

    Provides automatic error logging and recovery utilities.

    Example:
        >>> from src.utils.error_handler import ErrorContext
        >>> logger = logging.getLogger("my_module")
        >>>
        >>> with ErrorContext(logger, "operation_name"):
        ...     risky_operation()
        # Errors are automatically caught and logged
    """

    def __init__(
        self,
        logger: logging.Logger,
        operation: str,
        on_error: Optional[Callable] = None,
    ):
        """Initialize error context.

        Args:
            logger: Logger instance to use
            operation: Name of operation for logging
            on_error: Optional callback to call on error
        """
        self.logger = logger
        self.operation = operation
        self.on_error = on_error

    def __enter__(self):
        """Enter context."""
        self.logger.debug(f"[START] {self.operation}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and handle errors.

        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback

        Returns:
            False (don't suppress exception), True (suppress exception)
        """
        if exc_type is not None:
            self.logger.error(f"[ERROR] {self.operation}: {exc_type.__name__}")
            self.logger.error(f"Error: {str(exc_val)}")
            self.logger.exception("Traceback:")

            if self.on_error:
                try:
                    self.on_error(exc_type, exc_val, exc_tb)
                except Exception as e:
                    self.logger.error(f"Error in on_error handler: {str(e)}")

            return False  # Re-raise the exception
        else:
            self.logger.debug(f"[END] {self.operation} completed")
            return False


# ============================================================================
# ERROR FORMATTING
# ============================================================================

def format_error_for_user(state: Dict[str, Any]) -> str:
    """Format error message for user display.

    Converts technical error messages into user-friendly format.

    Args:
        state: State containing error information

    Returns:
        User-friendly error message
    """
    if not is_error_state(state):
        return ""

    error_msg = get_error_message(state)
    error_type = get_error_type(state)
    node_name = state.get("node_name", "Unknown")

    # Map error types to user-friendly messages
    error_messages = {
        "BudgetValidationError": "Your budget is insufficient for this trip. Please try adjusting your budget, destination, or duration.",
        "ToolExecutionError": f"We encountered an issue while searching for travel options. Please try again.",
        "LLMError": "We encountered an issue generating your itinerary. Please try again.",
        "SearchError": "We couldn't find any options matching your criteria. Please try different parameters.",
        "StateValidationError": "There's an issue with your trip parameters. Please check and try again.",
    }

    user_message = error_messages.get(error_type, f"An error occurred: {error_msg}")

    return user_message


def log_error_details(state: Dict[str, Any]) -> None:
    """Log detailed error information.

    Args:
        state: State containing error information
    """
    logger = logging.getLogger("error_handler")

    if not is_error_state(state):
        return

    logger.error("=" * 70)
    logger.error("ERROR DETAILS")
    logger.error("=" * 70)

    error_msg = get_error_message(state)
    error_type = get_error_type(state)
    node_name = state.get("node_name", "Unknown")

    logger.error(f"Node: {node_name}")
    logger.error(f"Error Type: {error_type}")
    logger.error(f"Error Message: {error_msg}")

    if "traceback" in state:
        logger.error("Traceback:")
        logger.error(state["traceback"])

    logger.error("=" * 70)

