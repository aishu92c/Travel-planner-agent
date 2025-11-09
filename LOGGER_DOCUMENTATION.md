
The logger system provides comprehensive logging capabilities for the travel planner agent, including:
- Centralized logging configuration
- Specialized loggers for nodes and tools
- Execution time tracking
- Performance monitoring
- State transition logging
- LLM call tracking
- Error logging with context

**Location**: `src/utils/logger.py`

## Quick Start

### Basic Setup

The logger is automatically configured when the module is imported:

```python
from src.utils.logger import get_node_logger, get_tool_logger

# Create node logger
logger = get_node_logger("budget_analysis")
logger.info("Starting budget analysis")

# Create tool logger
tool_logger = get_tool_logger("flight_search")
tool_logger.debug("Searching for flights")
```

### Configuration

Logging is automatically configured from settings:

```python
# src/config/settings.py
settings.observability.log_level  # Log level (DEBUG, INFO, WARNING, ERROR)
settings.observability.log_format # Log format string
```

Default settings:
- **Log Level**: INFO
- **Format**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Output**: Console + File (`logs/agent.log`)
- **Rotation**: 10MB per file, 5 backup files

## Logger Functions

### `get_node_logger(node_name: str) -> Logger`

Get a specialized logger for a node.

**Parameters**:
- `node_name` (str): Name of the node (e.g., "budget_analysis")

**Returns**: `Logger` instance with node-specific naming

**Example**:
```python
from src.utils.logger import get_node_logger

logger = get_node_logger("search_flights")
logger.info("Starting flight search")
# Output: 2024-11-07 10:30:00 - nodes.search_flights - INFO - Starting flight search
```

### `get_tool_logger(tool_name: str) -> Logger`

Get a specialized logger for a tool.

**Parameters**:
- `tool_name` (str): Name of the tool (e.g., "flight_search")

**Returns**: `Logger` instance with tool-specific naming

**Example**:
```python
from src.utils.logger import get_tool_logger

logger = get_tool_logger("hotel_search")
logger.info("Searching for hotels")
# Output: 2024-11-07 10:30:00 - tools.hotel_search - INFO - Searching for hotels
```

## Helper Functions

### `log_state_transition(from_node: str, to_node: str, state: dict) -> None`

Log a state transition between nodes.

**Parameters**:
- `from_node` (str): Source node name
- `to_node` (str): Destination node name
- `state` (dict): Current state dictionary

**Features**:
- Logs safe state keys (excludes sensitive fields)
- Truncates large values
- Logs boundaries with separators

**Example**:
```python
from src.utils.logger import log_state_transition

state = {
    "destination": "Paris",
    "budget": 3000.0,
    "budget_feasible": True,
}

log_state_transition("budget_analysis", "search_flights", state)
# Output:
# ======================================================================
# STATE TRANSITION: budget_analysis → search_flights
# State keys: destination, budget, budget_feasible
# ...
```

### `log_tool_call(tool_name: str, inputs: dict, outputs: dict, duration: float) -> None`

Log a tool call with inputs, outputs, and execution time.

**Parameters**:
- `tool_name` (str): Name of the tool
- `inputs` (dict): Input parameters
- `outputs` (dict): Output/results
- `duration` (float): Execution time in seconds

**Features**:
- Logs tool name and duration
- Summarizes large inputs/outputs
- Shows parameter types

**Example**:
```python
from src.utils.logger import log_tool_call

inputs = {"destination": "Paris", "date": "2024-06-01"}
outputs = {"flights": [...], "selected_flight": {...}}
duration = 1.23

log_tool_call("flight_search", inputs, outputs, duration)
# Output:
# TOOL CALL: flight_search
# Duration: 1.23s
# Inputs: destination, date
# ...
```

### `log_llm_call(prompt: str, response: str, tokens_used: int, cost: float) -> None`

Log an LLM API call with metrics.

**Parameters**:
- `prompt` (str): Input prompt sent to LLM
- `response` (str): Response received
- `tokens_used` (int): Total tokens used
- `cost` (float): Estimated cost in USD

**Features**:
- Logs prompt/response previews
- Tracks token usage for cost monitoring
- Logs estimated API cost

**Example**:
```python
from src.utils.logger import log_llm_call

log_llm_call(
    prompt="Create a 3-day itinerary for Paris",
    response="# Paris Itinerary...",
    tokens_used=2850,
    cost=0.00683,
)
# Output:
# LLM CALL
# Prompt (28 chars): Create a 3-day itinerary for Paris
# Response (23 chars): # Paris Itinerary...
# Tokens used: 2,850
# Estimated cost: $0.006830
```

## Context Managers

### `log_execution_time(logger: Logger, operation: str) -> Generator`

Context manager for timing code execution.

**Parameters**:
- `logger` (Logger): Logger instance to use
- `operation` (str): Name of the operation

**Usage**:
```python
from src.utils.logger import get_node_logger, log_execution_time

logger = get_node_logger("search_flights")

with log_execution_time(logger, "Flight search"):
    # Your code here
    flights = search_for_flights()

# Output:
# [START] Flight search at 2024-11-07 10:30:00
# [END] Flight search completed in 1.23s
```

**Error Handling**:
- Automatically logs errors with duration
- Re-raises exception after logging

```python
try:
    with log_execution_time(logger, "Search"):
        # Code that might fail
        result = risky_operation()
except Exception as e:
    # Error is already logged with duration
    pass
```

### `log_section(logger: Logger, title: str, level: str = "INFO") -> Generator`

Context manager for grouping log messages.

**Parameters**:
- `logger` (Logger): Logger instance
- `title` (str): Section title
- `level` (str): Log level (DEBUG, INFO, WARNING, ERROR)

**Usage**:
```python
from src.utils.logger import get_node_logger, log_section

logger = get_node_logger("budget_analysis")

with log_section(logger, "Budget Calculation"):
    logger.info("Step 1: Calculate breakdown")
    logger.info("Step 2: Identify region")
    logger.info("Step 3: Check feasibility")

# Output:
# ======================================================================
# >>> Budget Calculation
# ======================================================================
# Step 1: Calculate breakdown
# Step 2: Identify region
# Step 3: Check feasibility
# ======================================================================
```

## Performance Logger

### `PerformanceLogger` Class

Track performance metrics with checkpoints.

**Methods**:
- `mark_checkpoint(name: str)`: Mark a checkpoint
- `log_performance() -> float`: Log all metrics and return duration

**Example**:
```python
from src.utils.logger import get_node_logger, PerformanceLogger

logger = get_node_logger("workflow")
perf = PerformanceLogger("workflow_execution", logger)

# Mark checkpoints
perf.mark_checkpoint("budget_analysis")
time.sleep(0.5)

perf.mark_checkpoint("search_flights")
time.sleep(0.3)

perf.mark_checkpoint("generate_itinerary")

# Log results
total_duration = perf.log_performance()

# Output:
# PERFORMANCE: workflow_execution
# Total duration: 0.83s
#   budget_analysis: 0.50s
#   search_flights: 0.30s
#   generate_itinerary: 0.03s
```

## Error Logging

### `log_error_with_context(logger: Logger, error: Exception, context: dict) -> None`

Log an error with contextual information.

**Parameters**:
- `logger` (Logger): Logger instance
- `error` (Exception): Exception that occurred
- `context` (dict): Contextual information

**Example**:
```python
from src.utils.logger import get_node_logger, log_error_with_context

logger = get_node_logger("search_flights")

try:
    flights = search_for_flights("invalid_destination")
except Exception as e:
    log_error_with_context(logger, e, {
        "node": "search_flights",
        "destination": "invalid_destination",
        "function": "search_for_flights",
    })

# Output:
# ERROR: ValueError: Invalid destination
# Context: {'node': 'search_flights', ...}
# Full traceback: [complete stack trace]
```

## Integration with Nodes

### Pattern 1: Simple Node Logging

```python
from src.utils.logger import get_node_logger, log_section

def my_node(state):
    logger = get_node_logger("my_node")
    
    with log_section(logger, "My Node"):
        logger.info("Processing state")
        # Do work
        logger.info("✓ Completed")
    
    return state
```

### Pattern 2: Node with Timing

```python
from src.utils.logger import get_node_logger, log_execution_time

def my_node(state):
    logger = get_node_logger("my_node")
    
    with log_execution_time(logger, "Node execution"):
        # Do work
        result = process_state(state)
    
    return result
```

### Pattern 3: Node with State Transition

```python
from src.utils.logger import get_node_logger, log_state_transition
from src.graph import should_continue_planning

def budget_analysis_node(state):
    logger = get_node_logger("budget_analysis")
    
    logger.info("Analyzing budget")
    # Do analysis
    
    next_node = should_continue_planning(state)
    log_state_transition("budget_analysis", next_node, state.__dict__)
    
    return state
```

### Pattern 4: Node with Tool Call Logging

```python
from src.utils.logger import get_node_logger, log_tool_call

def search_flights_node(state):
    logger = get_node_logger("search_flights")
    
    logger.info("Searching flights")
    start_time = time.time()
    
    flights = search_tool(state.destination, state.budget)
    duration = time.time() - start_time
    
    log_tool_call("flight_search", 
                  {"destination": state.destination},
                  {"flights": flights},
                  duration)
    
    return {"flights": flights}
```

## Log File Management

### Location
- Default: `logs/agent.log`
- Console output: stdout

### Rotation
- **Max size**: 10MB per file
- **Backup files**: 5 (agent.log.1 through agent.log.5)
- **Automatic rollover**: When 10MB is reached

### Example Log Structure
```
logs/
├── agent.log          # Current log file
├── agent.log.1        # Oldest backup
├── agent.log.2
├── agent.log.3
├── agent.log.4
└── agent.log.5        # Most recent backup
```

## Log Levels

| Level | Use Case | Example |
|-------|----------|---------|
| DEBUG | Detailed diagnostic info | Variable values, loop iterations |
| INFO | General info messages | Node start/end, operations |
| WARNING | Something unexpected | Retry attempts, config warnings |
| ERROR | Error condition | Exceptions, failed operations |
| CRITICAL | Serious error | System failures |

### Configuring Log Level

Set in `.env`:
```
OBSERVABILITY__LOG_LEVEL=INFO
```

Or programmatically:
```python
from src.config import get_settings

settings = get_settings()
print(settings.observability.log_level)
```

## Best Practices

### 1. Use Specialized Loggers
```python
# ✓ Good: Specific logger
logger = get_node_logger("budget_analysis")

# ✗ Bad: Generic logger
logger = logging.getLogger(__name__)
```

### 2. Use Appropriate Log Levels
```python
# ✓ Good: Appropriate levels
logger.debug("Variables: x={}, y={}".format(x, y))
logger.info("Processing started")
logger.warning("Retry attempt 2")
logger.error("Failed to connect")

# ✗ Bad: Wrong levels
logger.info("x={}, y={}".format(x, y))  # Too much info at INFO level
logger.error("Processing complete")      # Should be INFO
```

### 3. Use Context Managers
```python
# ✓ Good: Automatic timing
with log_execution_time(logger, "Search"):
    results = search()

# ✗ Bad: Manual timing (error-prone)
start = time.time()
results = search()
logger.info(f"Search took {time.time() - start}s")
```

### 4. Log Meaningful Context
```python
# ✓ Good: Meaningful context
log_state_transition("budget_analysis", "search_flights", state)

# ✗ Bad: Vague context
logger.info("Transitioning")
```

### 5. Avoid Logging Sensitive Data
```python
# ✓ Good: Exclude sensitive fields
safe_keys = [k for k in state.keys() if "token" not in k]

# ✗ Bad: Logging everything
logger.info(f"State: {state}")  # May include API keys!
```

## Troubleshooting

### Logs Not Appearing

1. Check log level configuration
```python
from src.config import get_settings
print(get_settings().observability.log_level)
```

2. Verify logs directory exists
```bash
ls -la logs/
```

3. Check file permissions
```bash
chmod 755 logs/
```

### Log File Growing Too Large

- The rotation handles this automatically
- Max size is 10MB per file
- Up to 5 backup files are kept
- Older files are automatically deleted

### Performance Impact

- Logging is minimal (< 1% overhead)
- File I/O is handled efficiently
- Debug logs can be disabled in production

## Examples

See `LOGGER_EXAMPLES.py` for comprehensive examples including:
- Node logging
- Tool logging
- State transitions
- LLM call tracking
- Performance monitoring
- Error handling
- Production patterns

Run examples:
```bash
python LOGGER_EXAMPLES.py
```

## Related Documentation

- **Configuration**: `src/config/settings.py` (observability section)
- **Examples**: `LOGGER_EXAMPLES.py`
- **Node Implementation**: `src/nodes/`
- **Tool Implementation**: `src/nodes/tool_nodes.py`

---

**Last Updated**: November 7, 2025
**Version**: 1.0
# Logger System Documentation

## Overview

