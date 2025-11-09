"""Logging utilities usage examples and patterns.

Demonstrates common logging patterns used throughout the travel planner agent.
"""

import time

from src.utils.logger import (
    PerformanceLogger,
    get_node_logger,
    get_tool_logger,
    log_error_with_context,
    log_execution_time,
    log_llm_call,
    log_section,
    log_state_transition,
    log_tool_call,
)


# ============================================================================
# EXAMPLE 1: Node Logging
# ============================================================================

def example_node_logging():
    """Example: Logging in a node."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Node Logging")
    print("=" * 70)

    logger = get_node_logger("budget_analysis")

    with log_section(logger, "Budget Analysis"):
        logger.info("Analyzing budget feasibility")
        logger.debug("Destination: Paris")
        logger.debug("Budget: $3000")
        logger.debug("Duration: 10 days")
        logger.info("✓ Budget analysis completed")


# ============================================================================
# EXAMPLE 2: Tool Logging
# ============================================================================

def example_tool_logging():
    """Example: Logging tool calls."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Tool Logging")
    print("=" * 70)

    logger = get_tool_logger("flight_search")

    with log_execution_time(logger, "Flight search"):
        # Simulate flight search
        time.sleep(0.5)

        inputs = {
            "destination": "Paris",
            "date": "2024-06-01",
            "budget": 1200.0,
        }

        outputs = {
            "flights": ["Flight 1", "Flight 2", "Flight 3"],
            "selected_flight": "Flight 1",
        }

        duration = 0.5
        log_tool_call("flight_search", inputs, outputs, duration)


# ============================================================================
# EXAMPLE 3: State Transitions
# ============================================================================

def example_state_transition():
    """Example: Logging state transitions."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: State Transitions")
    print("=" * 70)

    state = {
        "destination": "Paris",
        "budget": 3000.0,
        "duration": 10,
        "budget_feasible": True,
        "flights": ["Flight 1"],
        "selected_flight": "Flight 1",
    }

    log_state_transition("budget_analysis", "search_flights", state)


# ============================================================================
# EXAMPLE 4: LLM Call Logging
# ============================================================================

def example_llm_logging():
    """Example: Logging LLM calls."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: LLM Call Logging")
    print("=" * 70)

    prompt = "Create a 3-day itinerary for Paris with a budget of $1500"
    response = "# Paris Itinerary - 3 Days\n\n## Day 1\n...[longer response]..."
    tokens_used = 2850
    cost = 0.00683

    log_llm_call(prompt, response, tokens_used, cost)


# ============================================================================
# EXAMPLE 5: Execution Timing
# ============================================================================

def example_execution_timing():
    """Example: Timing code execution."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Execution Timing")
    print("=" * 70)

    logger = get_node_logger("complex_operation")

    with log_execution_time(logger, "Budget analysis"):
        # Simulate work
        logger.info("Step 1: Calculate budget breakdown")
        time.sleep(0.2)

        logger.info("Step 2: Identify region")
        time.sleep(0.3)

        logger.info("Step 3: Calculate minimum budget")
        time.sleep(0.1)


# ============================================================================
# EXAMPLE 6: Performance Tracking
# ============================================================================

def example_performance_tracking():
    """Example: Tracking performance with checkpoints."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Performance Tracking")
    print("=" * 70)

    logger = get_node_logger("performance_test")
    perf = PerformanceLogger("workflow_execution", logger)

    # Simulate workflow steps
    time.sleep(0.1)
    perf.mark_checkpoint("budget_analysis_done")

    time.sleep(0.2)
    perf.mark_checkpoint("search_flights_done")

    time.sleep(0.15)
    perf.mark_checkpoint("search_hotels_done")

    time.sleep(0.1)
    perf.mark_checkpoint("generate_itinerary_done")

    total_duration = perf.log_performance()
    print(f"\nTotal workflow time: {total_duration:.2f} seconds")


# ============================================================================
# EXAMPLE 7: Error Logging
# ============================================================================

def example_error_logging():
    """Example: Logging errors with context."""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Error Logging")
    print("=" * 70)

    logger = get_node_logger("error_example")

    try:
        # Simulate an error
        raise ValueError("Invalid destination")
    except ValueError as e:
        context = {
            "node": "budget_analysis",
            "destination": "Paris",
            "budget": 3000.0,
            "function": "identify_region",
        }
        log_error_with_context(logger, e, context)


# ============================================================================
# EXAMPLE 8: Logging in Production Node
# ============================================================================

def example_production_node():
    """Example: Complete logging in a production node."""
    print("\n" + "=" * 70)
    print("EXAMPLE 8: Production Node Pattern")
    print("=" * 70)

    logger = get_node_logger("search_hotels")

    with log_section(logger, "Hotel Search"):
        with log_execution_time(logger, "Hotel search operation"):
            logger.info("Starting hotel search")

            # Simulate search
            time.sleep(0.3)

            # Log tool call
            inputs = {
                "destination": "Paris",
                "check_in": "2024-06-01",
                "check_out": "2024-06-10",
                "max_price": 1050.0,
            }

            outputs = {
                "hotels": ["Hotel A", "Hotel B", "Hotel C"],
                "selected_hotel": "Hotel A",
            }

            log_tool_call("hotel_search", inputs, outputs, 0.3)
            logger.info("✓ Hotel search completed")


# ============================================================================
# EXAMPLE 9: Logging Section with Different Levels
# ============================================================================

def example_logging_levels():
    """Example: Using different logging levels."""
    print("\n" + "=" * 70)
    print("EXAMPLE 9: Logging Levels")
    print("=" * 70)

    logger = get_node_logger("logging_levels")

    with log_section(logger, "Logging Levels Demo", level="DEBUG"):
        logger.debug("Debug message (detailed info)")
        logger.info("Info message (general info)")
        logger.warning("Warning message (something to watch)")
        logger.error("Error message (something went wrong)")


# ============================================================================
# EXAMPLE 10: Integration with Graph Nodes
# ============================================================================

def example_graph_node_integration():
    """Example: How to use logging in a LangGraph node."""
    print("\n" + "=" * 70)
    print("EXAMPLE 10: LangGraph Node Integration")
    print("=" * 70)

    from src.agents.state import AgentState

    # Simulated node function
    def budget_analysis_node(state: AgentState):
        logger = get_node_logger("budget_analysis")

        with log_section(logger, "Budget Analysis"):
            with log_execution_time(logger, "Budget analysis"):
                logger.info(f"Analyzing destination: {state.destination}")
                logger.info(f"Budget: ${state.budget:.2f}")
                logger.info(f"Duration: {state.duration} days")

                # Simulate analysis
                time.sleep(0.1)

                budget_breakdown = {
                    "flights": state.budget * 0.4,
                    "accommodation": state.budget * 0.35,
                    "activities": state.budget * 0.15,
                    "food": state.budget * 0.1,
                }

                budget_feasible = state.budget >= 2000

                logger.info(f"Budget feasible: {budget_feasible}")
                logger.debug(f"Budget breakdown: {budget_breakdown}")

                # Log state transition
                log_state_transition(
                    "budget_analysis",
                    "search_flights" if budget_feasible else "suggest_alternatives",
                    state.__dict__,
                )

                return {
                    "budget_breakdown": budget_breakdown,
                    "budget_feasible": budget_feasible,
                }

    # Create sample state
    state = AgentState(
        destination="Paris",
        budget=3000.0,
        duration=10,
    )

    result = budget_analysis_node(state)
    print(f"\nNode result: {result}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("LOGGING UTILITIES - COMPREHENSIVE EXAMPLES")
    print("=" * 70)

    # Run examples
    example_node_logging()
    example_tool_logging()
    example_state_transition()
    example_llm_logging()
    example_execution_timing()
    example_performance_tracking()
    example_error_logging()
    example_production_node()
    example_logging_levels()
    example_graph_node_integration()

    print("\n" + "=" * 70)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 70)
    print("""
LOGGING PATTERNS:

1. Node Logging:
   logger = get_node_logger("node_name")
   with log_section(logger, "Operation name"):
       logger.info("Message")

2. Tool Logging:
   logger = get_tool_logger("tool_name")
   with log_execution_time(logger, "Tool operation"):
       # Do work
       log_tool_call(name, inputs, outputs, duration)

3. State Transitions:
   log_state_transition("from_node", "to_node", state)

4. LLM Calls:
   log_llm_call(prompt, response, tokens, cost)

5. Performance Tracking:
   perf = PerformanceLogger("operation", logger)
   perf.mark_checkpoint("step1")
   perf.log_performance()

6. Error Handling:
   log_error_with_context(logger, error, context)

NEXT STEPS:
1. Import loggers in your nodes and tools
2. Use log_section() for code blocks
3. Use log_execution_time() for timing
4. Call log_tool_call() for tool invocations
5. Use get_node_logger/get_tool_logger for specialized logging

Check logs/agent.log for file output!
""")

