"""Logging configuration for Travel Planner.

Provides:
- Centralized logging setup
- Node-specific loggers
- Tool call tracking
- Execution timing
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from contextlib import contextmanager
import time
from typing import Optional, Any, Dict

# ============================================================================
# LOGGER SETUP
# ============================================================================

LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "agent.log"

# Create formatters
DETAILED_FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Setup root logger
def setup_logging(level: str = "INFO") -> logging.Logger:
    """Setup logging configuration.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Configured logger
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level))

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level))
    console_handler.setFormatter(DETAILED_FORMATTER)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(DETAILED_FORMATTER)

    # Add handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    return root_logger


# Initialize logging
setup_logging()


# ============================================================================
# LOGGER FUNCTIONS
# ============================================================================

def get_node_logger(node_name: str) -> logging.Logger:
    """Get logger for a specific node.

    Args:
        node_name: Name of the node

    Returns:
        Logger instance for the node
    """
    return logging.getLogger(f"{node_name}")


def get_tool_logger(tool_name: str) -> logging.Logger:
    """Get logger for a specific tool.

    Args:
        tool_name: Name of the tool

    Returns:
        Logger instance for the tool
    """
    return logging.getLogger(f"tool.{tool_name}")


# ============================================================================
# LOGGING HELPERS
# ============================================================================

def log_state_transition(from_node: str, to_node: str, state: Dict[str, Any]) -> None:
    """Log state transition between nodes.

    Args:
        from_node: Previous node name
        to_node: Next node name
        state: Current state dictionary
    """
    logger = logging.getLogger("transitions")
    logger.info(f"Transition: {from_node} → {to_node}")
    if "budget_feasible" in state:
        logger.debug(f"  budget_feasible: {state['budget_feasible']}")


def log_tool_call(
    tool_name: str,
    inputs: Dict[str, Any],
    outputs: Dict[str, Any],
    duration: float
) -> None:
    """Log tool function call with inputs, outputs, and duration.

    Args:
        tool_name: Name of the tool
        inputs: Input parameters to the tool
        outputs: Output/result from the tool
        duration: Execution time in seconds
    """
    logger = get_tool_logger(tool_name)
    logger.info(f"Call: {tool_name}")
    logger.debug(f"  Inputs: {inputs}")
    logger.debug(f"  Outputs: {outputs}")
    logger.debug(f"  Duration: {duration:.3f}s")


def log_llm_call(
    prompt: str,
    response: str,
    tokens_used: int,
    cost: float
) -> None:
    """Log LLM API call with tokens and cost.

    Args:
        prompt: Input prompt to LLM
        response: Response from LLM
        tokens_used: Number of tokens used
        cost: Cost in dollars
    """
    logger = logging.getLogger("llm")
    logger.info(f"LLM Call")
    logger.debug(f"  Prompt length: {len(prompt)} chars")
    logger.debug(f"  Response length: {len(response)} chars")
    logger.debug(f"  Tokens: {tokens_used}")
    logger.debug(f"  Cost: ${cost:.4f}")


# ============================================================================
# CONTEXT MANAGERS
# ============================================================================

@contextmanager
def log_execution_time(logger: logging.Logger, operation: str):
    """Context manager to log execution time of an operation.

    Args:
        logger: Logger instance
        operation: Name of the operation

    Example:
        >>> with log_execution_time(logger, "flight_search"):
        ...     results = search_flights(...)
    """
    logger.info(f"Starting: {operation}")
    start_time = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start_time
        logger.info(f"Completed: {operation} ({elapsed:.2f}s)")


# ============================================================================
# INITIALIZATION
# ============================================================================

if __name__ == "__main__":
    # Test logging
    logger = get_node_logger("test")
    logger.info("Logger initialized successfully")

