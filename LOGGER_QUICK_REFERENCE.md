# Logger System - Quick Reference

## ⚡ Quick Start

### Import
```python
from src.utils.logger import (
    get_node_logger,
    get_tool_logger,
    log_execution_time,
    log_section,
    log_state_transition,
    log_tool_call,
    log_llm_call,
)
```

### Basic Usage
```python
# Get logger
logger = get_node_logger("node_name")
logger = get_tool_logger("tool_name")

# Log messages
logger.info("Message")
logger.debug("Debug info")
logger.warning("Warning")
logger.error("Error")

# Time execution
with log_execution_time(logger, "Operation"):
    # Your code here
    pass

# Log section
with log_section(logger, "Section Title"):
    logger.info("Message")
```

## 📋 Functions

### Logger Creation
| Function | Purpose | Example |
|----------|---------|---------|
| `get_node_logger(name)` | Node logger | `get_node_logger("budget_analysis")` |
| `get_tool_logger(name)` | Tool logger | `get_tool_logger("flight_search")` |

### Logging
| Function | Purpose | Parameters |
|----------|---------|-----------|
| `log_state_transition()` | Log state change | from_node, to_node, state |
| `log_tool_call()` | Log tool execution | tool_name, inputs, outputs, duration |
| `log_llm_call()` | Log LLM call | prompt, response, tokens_used, cost |

### Context Managers
| Manager | Purpose | Example |
|---------|---------|---------|
| `log_execution_time()` | Time code block | `with log_execution_time(logger, "op"):` |
| `log_section()` | Group messages | `with log_section(logger, "title"):` |

### Utilities
| Function | Purpose |
|----------|---------|
| `log_error_with_context()` | Log error with context |
| `PerformanceLogger` | Track performance with checkpoints |

## 🔧 Common Patterns

### Node Pattern
```python
def my_node(state):
    logger = get_node_logger("my_node")
    
    with log_section(logger, "Node Operation"):
        with log_execution_time(logger, "Processing"):
            logger.info("Starting")
            # Do work
            logger.info("✓ Complete")
    
    return state
```

### Tool Pattern
```python
def my_tool(inputs):
    logger = get_tool_logger("my_tool")
    
    with log_execution_time(logger, "Tool execution"):
        logger.debug(f"Inputs: {inputs}")
        result = execute_tool(inputs)
        logger.debug(f"Outputs: {result}")
    
    duration = 0.5  # Actual duration
    log_tool_call("my_tool", inputs, result, duration)
    return result
```

### State Transition Pattern
```python
log_state_transition("node1", "node2", state.__dict__)
```

### LLM Call Pattern
```python
log_llm_call(
    prompt="Your prompt",
    response="LLM response",
    tokens_used=1500,
    cost=0.0045
)
```

## 📊 Log Output

### Console Format
```
2024-11-07 10:30:00 - nodes.budget_analysis - INFO - Starting budget analysis
2024-11-07 10:30:01 - nodes.budget_analysis - DEBUG - Budget: $3000
2024-11-07 10:30:02 - nodes.budget_analysis - INFO - ✓ Complete
```

### File Location
- `logs/agent.log` - Current log
- `logs/agent.log.1-5` - Backups (auto-rotated at 10MB)

## 🎯 Log Levels

| Level | When to Use |
|-------|------------|
| DEBUG | Detailed info (variables, iterations) |
| INFO | General info (start, end, key events) |
| WARNING | Unexpected but handled (retries) |
| ERROR | Error conditions (exceptions) |

## ⚙️ Configuration

Set in `.env`:
```
OBSERVABILITY__LOG_LEVEL=INFO
```

Default:
- Level: INFO
- Format: `timestamp - name - level - message`
- Output: Console + File
- Rotation: 10MB per file, 5 backups

## 🔒 Security

### Safe Logging
```python
# ✓ Safe: Excludes sensitive fields
log_state_transition("node1", "node2", state)

# ✗ Unsafe: May log API keys
logger.info(f"State: {state}")
```

### Never Log
- API keys
- Tokens
- Secrets
- Passwords
- Sensitive user data

## 📈 Performance Monitoring

```python
from src.utils.logger import PerformanceLogger

perf = PerformanceLogger("workflow", logger)

perf.mark_checkpoint("step1")
# Do work

perf.mark_checkpoint("step2")
# Do more work

perf.log_performance()
# Output: Shows time for each checkpoint
```

## 🐛 Debugging

### Enable Debug Logging
Set in `.env`:
```
OBSERVABILITY__LOG_LEVEL=DEBUG
```

### View Logs
```bash
# Real-time
tail -f logs/agent.log

# Last 100 lines
tail -100 logs/agent.log

# Search
grep "ERROR" logs/agent.log
grep "flight_search" logs/agent.log
```

## 📝 Examples

Basic:
```python
from src.utils.logger import get_node_logger

logger = get_node_logger("my_node")
logger.info("Hello world")
```

With Timing:
```python
from src.utils.logger import get_node_logger, log_execution_time

logger = get_node_logger("my_node")
with log_execution_time(logger, "My operation"):
    # Do work
    pass
```

Complex:
```python
from src.utils.logger import (
    get_node_logger,
    log_section,
    log_execution_time,
    log_state_transition,
)

logger = get_node_logger("my_node")

with log_section(logger, "Complex Operation"):
    with log_execution_time(logger, "Processing"):
        logger.info("Starting")
        # Do work
        log_state_transition("node1", "node2", state)
        logger.info("✓ Complete")
```

## 🚀 Deployment

### Production Setup
```
OBSERVABILITY__LOG_LEVEL=WARNING
```

### Development Setup
```
OBSERVABILITY__LOG_LEVEL=DEBUG
```

## 📞 Help

- **Full Documentation**: `LOGGER_DOCUMENTATION.md`
- **Examples**: `LOGGER_EXAMPLES.py`
- **Source**: `src/utils/logger.py`

---

**Version**: 1.0 | **Updated**: November 7, 2025

