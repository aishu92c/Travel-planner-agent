"""Travel Planner Agent Graph using LangGraph.

This module defines the workflow graph for the travel planner agent using LangGraph.
It implements conditional routing based on budget feasibility and error handling.

Graph Workflow:
1. Entry point: budget_analysis
2. Conditional routing:
   - If budget_feasible: search_flights -> search_hotels -> search_activities -> generate_itinerary -> END
   - If budget_feasible == False: suggest_alternatives -> END
3. Error handling: Any error_message triggers error_handler -> END
"""

import logging
from typing import Any, Dict

from langgraph.graph import StateGraph, END
from langgraph.types import Command

from src.agents.state import AgentState
from src.nodes import (
    budget_analysis_node,
    search_flights_node,
    search_hotels_node,
    generate_itinerary_node,
)

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Add console handler if not already present
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# ============================================================================
# CONDITIONAL ROUTING FUNCTIONS
# ============================================================================

def should_continue_planning(state: AgentState) -> str:
    """Determine whether to continue with planning or suggest alternatives.

    This function implements the main branching logic:
    - If budget_feasible == True: continue with flight/hotel search
    - If budget_feasible == False: suggest alternatives
    - If error_message set: route to error handler

    Args:
        state: Current agent state

    Returns:
        str: Next node name ("search_flights", "suggest_alternatives", or "error_handler")
    """
    logger.info("=" * 70)
    logger.info("Evaluating budget feasibility for routing...")
    logger.info("=" * 70)

    # Check for errors first
    if state.error_message:
        logger.warning(f"Error detected: {state.error_message}")
        logger.info("Routing to: error_handler")
        return "error_handler"

    # Check budget feasibility
    budget_feasible = state.budget_feasible

    logger.info(f"Budget Feasible: {budget_feasible}")

    if budget_feasible:
        logger.info("✓ Trip is within budget")
        logger.info("Routing to: search_flights")
        return "search_flights"
    else:
        logger.warning("✗ Trip exceeds budget")
        logger.info("Routing to: suggest_alternatives")
        return "suggest_alternatives"


def should_search_activities(state: AgentState) -> str:
    """Determine whether to search for activities or proceed to itinerary.

    Args:
        state: Current agent state

    Returns:
        str: Next node name ("search_activities" or "generate_itinerary")
    """
    logger.info("Checking if activities search is needed...")

    # If we have hotel selected, search for activities
    if state.selected_hotel:
        logger.info("✓ Hotel selected. Proceeding to activity search")
        return "search_activities"
    else:
        logger.warning("No hotel selected. Skipping activity search")
        logger.info("Proceeding directly to itinerary generation")
        return "generate_itinerary"


def check_for_errors(state: AgentState) -> str:
    """Check if any errors occurred during execution.

    This function is called at various points to check if an error occurred
    that should interrupt the normal flow.

    Args:
        state: Current agent state

    Returns:
        str: Next node name ("error_handler" or continue with main flow)
    """
    if state.error_message:
        logger.warning(f"Error detected during execution: {state.error_message}")
        return "error_handler"

    return None  # Continue with normal flow


# ============================================================================
# ERROR HANDLER NODE
# ============================================================================

def error_handler_node(state: AgentState) -> Dict[str, Any]:
    """Handle errors and format user-friendly error messages.

    This node is invoked when an error occurs at any point in the workflow.
    It formats the error message and prepares a response for the user.

    Args:
        state: Current agent state with error_message set

    Returns:
        Dictionary with formatted error information
    """
    logger.info("=" * 70)
    logger.info("Handling error in travel planning")
    logger.info("=" * 70)

    error_message = state.error_message or "An unknown error occurred"

    logger.error(f"Error: {error_message}")

    # Create user-friendly error message
    user_friendly_message = format_error_message(error_message)

    logger.info(f"Formatted error message: {user_friendly_message}")

    return {
        "error_message": error_message,
        "user_message": user_friendly_message,
        "status": "error",
    }


def format_error_message(error: str) -> str:
    """Format technical error messages into user-friendly messages.

    Args:
        error: Technical error message

    Returns:
        User-friendly error message
    """
    logger.debug(f"Formatting error message: {error}")

    # Map common errors to user-friendly messages
    error_mappings = {
        "budget": "Your budget is insufficient for the desired travel dates and destination. "
                  "Please try adjusting your budget, destination, or trip duration.",
        "flight": "We had trouble finding flights for your trip. "
                  "Please try different dates or destination.",
        "hotel": "We had trouble finding hotels for your trip. "
                 "Please try different dates or location.",
        "activity": "We had trouble finding activities for your destination. "
                    "Please try a different location.",
        "invalid": "Invalid trip parameters provided. "
                   "Please check your destination, dates, and budget.",
        "api": "We encountered an issue connecting to our services. "
               "Please try again later.",
    }

    # Check for keywords in error message
    error_lower = error.lower()
    for keyword, message in error_mappings.items():
        if keyword in error_lower:
            logger.debug(f"Matched error keyword: {keyword}")
            return message

    # Default message
    return ("We encountered an issue planning your trip. "
            "Please try again with different parameters.")


# ============================================================================
# GRAPH CREATION
# ============================================================================

def create_graph() -> Any:
    """Create and compile the travel planner agent graph.

    This function builds the LangGraph workflow with:
    1. Budget analysis as entry point
    2. Conditional routing based on budget feasibility
    3. Main flow for feasible trips
    4. Alternative flow for insufficient budgets
    5. Error handling throughout

    Returns:
        Compiled LangGraph workflow

    Example:
        >>> from src.graph import create_graph
        >>> graph = create_graph()
        >>> result = graph.invoke({"destination": "Paris", "budget": 3000})
    """
    logger.info("=" * 70)
    logger.info("Creating travel planner graph...")
    logger.info("=" * 70)

    # Create state graph
    workflow = StateGraph(AgentState)

    logger.info("Created state graph")

    # ====================================================================
    # ADD NODES
    # ====================================================================

    logger.info("\nAdding nodes to graph...")

    # Entry point: Budget analysis
    logger.info("  • budget_analysis")
    workflow.add_node("budget_analysis", budget_analysis_node)

    # Main flow nodes
    logger.info("  • search_flights")
    workflow.add_node("search_flights", search_flights_node)

    logger.info("  • search_hotels")
    workflow.add_node("search_hotels", search_hotels_node)

    logger.info("  • search_activities (placeholder for future implementation)")
    # Placeholder for search_activities_node
    workflow.add_node("search_activities", lambda state: {})

    logger.info("  • generate_itinerary")
    workflow.add_node("generate_itinerary", generate_itinerary_node)

    # Alternative flow node
    logger.info("  • suggest_alternatives (placeholder for future implementation)")
    # Placeholder for suggest_alternatives_node
    workflow.add_node("suggest_alternatives", lambda state: {
        "alternative_suggestions": "Suggestions for budget-friendly options",
        "final_itinerary": "",
    })

    # Error handling node
    logger.info("  • error_handler")
    workflow.add_node("error_handler", error_handler_node)

    # ====================================================================
    # ADD EDGES
    # ====================================================================

    logger.info("\nAdding edges to graph...")

    # Entry point edge
    logger.info("  • START -> budget_analysis")
    workflow.set_entry_point("budget_analysis")

    # Conditional edge after budget_analysis
    logger.info("  • budget_analysis -> (CONDITIONAL)")
    logger.info("    - budget_feasible=True  -> search_flights")
    logger.info("    - budget_feasible=False -> suggest_alternatives")
    logger.info("    - error_message set    -> error_handler")
    workflow.add_conditional_edges(
        "budget_analysis",
        should_continue_planning,
        {
            "search_flights": "search_flights",
            "suggest_alternatives": "suggest_alternatives",
            "error_handler": "error_handler",
        }
    )

    # Main flow edges (when budget feasible)
    logger.info("  • search_flights -> search_hotels")
    workflow.add_edge("search_flights", "search_hotels")

    logger.info("  • search_hotels -> (CONDITIONAL to activities or itinerary)")
    workflow.add_conditional_edges(
        "search_hotels",
        should_search_activities,
        {
            "search_activities": "search_activities",
            "generate_itinerary": "generate_itinerary",
        }
    )

    logger.info("  • search_activities -> generate_itinerary")
    workflow.add_edge("search_activities", "generate_itinerary")

    logger.info("  • generate_itinerary -> END")
    workflow.add_edge("generate_itinerary", END)

    # Alternative flow edges (when budget insufficient)
    logger.info("  • suggest_alternatives -> END")
    workflow.add_edge("suggest_alternatives", END)

    # Error handling edges
    logger.info("  • error_handler -> END")
    workflow.add_edge("error_handler", END)

    # ====================================================================
    # COMPILE GRAPH
    # ====================================================================

    logger.info("\nCompiling graph...")
    compiled_graph = workflow.compile()

    logger.info("=" * 70)
    logger.info("✓ Graph created and compiled successfully")
    logger.info("=" * 70)

    return compiled_graph


# ============================================================================
# GRAPH EXECUTION UTILITIES
# ============================================================================

def run_travel_planning_workflow(
    destination: str,
    start_date: str,
    end_date: str,
    budget: float,
    duration: int,
) -> Dict[str, Any]:
    """Execute the travel planning workflow with given parameters.

    This is a convenience function to run the entire workflow from start to finish.

    Args:
        destination: Travel destination
        start_date: Trip start date (ISO format)
        end_date: Trip end date (ISO format)
        budget: Total budget in USD
        duration: Trip duration in days

    Returns:
        Final state after workflow execution

    Example:
        >>> result = run_travel_planning_workflow(
        ...     destination="Paris",
        ...     start_date="2024-06-01",
        ...     end_date="2024-06-10",
        ...     budget=3000.0,
        ...     duration=10,
        ... )
        >>> print(result["final_itinerary"])
    """
    logger.info("=" * 70)
    logger.info("Starting travel planning workflow execution")
    logger.info("=" * 70)

    # Create initial state
    initial_state = AgentState(
        destination=destination,
        start_date=start_date,
        end_date=end_date,
        budget=budget,
        duration=duration,
    )

    logger.info(f"Initial State:")
    logger.info(f"  Destination: {destination}")
    logger.info(f"  Duration: {duration} days")
    logger.info(f"  Budget: ${budget:.2f}")

    # Create and execute graph
    graph = create_graph()

    logger.info("\nInvoking workflow...")
    final_state = graph.invoke(initial_state)

    logger.info("=" * 70)
    logger.info("✓ Workflow execution completed")
    logger.info("=" * 70)

    return final_state


def stream_travel_planning_workflow(
    destination: str,
    start_date: str,
    end_date: str,
    budget: float,
    duration: int,
):
    """Execute the travel planning workflow with streaming output.

    This function streams workflow execution for real-time updates.

    Args:
        destination: Travel destination
        start_date: Trip start date (ISO format)
        end_date: Trip end date (ISO format)
        budget: Total budget in USD
        duration: Trip duration in days

    Yields:
        Workflow state updates at each step

    Example:
        >>> for step in stream_travel_planning_workflow(...):
        ...     print(f"Node: {step['node']}")
        ...     print(f"State: {step['state']}")
    """
    logger.info("Starting streaming workflow execution")

    # Create initial state
    initial_state = AgentState(
        destination=destination,
        start_date=start_date,
        end_date=end_date,
        budget=budget,
        duration=duration,
    )

    # Create graph
    graph = create_graph()

    # Stream execution
    logger.info("Streaming workflow events...")
    for step in graph.stream(initial_state, stream_mode="updates"):
        logger.debug(f"Stream update: {step}")
        yield step


# ============================================================================
# GRAPH VISUALIZATION
# ============================================================================

def visualize_graph() -> str:
    """Generate a text visualization of the graph structure.

    Returns:
        String representation of the graph
    """
    graph = create_graph()

    visualization = """
╔════════════════════════════════════════════════════════════════════════════╗
║                    TRAVEL PLANNER AGENT GRAPH                             ║
╚════════════════════════════════════════════════════════════════════════════╝

                                  START
                                    |
                                    ↓
                        ┌──────────────────────┐
                        │  budget_analysis     │
                        │  - Calculate budget  │
                        │  - Check feasibility │
                        └──────────────────────┘
                                    |
                    ┌───────────────┴───────────────┐
                    |                               |
       budget_feasible=True              budget_feasible=False
                    |                               |
                    ↓                               ↓
        ┌──────────────────────┐      ┌──────────────────────────┐
        │  search_flights      │      │ suggest_alternatives     │
        │  - Find flights      │      │ - Budget-friendly opts   │
        │  - Select best       │      │ - Cost reduction tips    │
        └──────────────────────┘      └──────────────────────────┘
                    |                               |
                    ↓                               |
        ┌──────────────────────┐                   |
        │  search_hotels       │                   |
        │  - Find hotels       │                   |
        │  - Select best       │                   |
        └──────────────────────┘                   |
                    |                              |
                    ↓                              |
        ┌──────────────────────┐                   |
        │ search_activities    │ (optional)        |
        │ - Find activities    │                   |
        └──────────────────────┘                   |
                    |                              |
                    ↓                              |
        ┌──────────────────────┐                   |
        │generate_itinerary    │                   |
        │ - Create day-by-day  │                   |
        │ - Track costs        │                   |
        └──────────────────────┘                   |
                    |                              |
                    └───────────────┬──────────────┘
                                    |
                    ┌───────────────┴───────────────┐
                    |                               |
              Error Handler (if error_message set) |
                    |                               |
                    ↓                               ↓
        ┌──────────────────────┐                  END
        │  error_handler       │
        │  - Format error msg  │
        │  - User-friendly     │
        └──────────────────────┘
                    |
                    ↓
                  END

════════════════════════════════════════════════════════════════════════════

ROUTING LOGIC:

1. Entry Point: budget_analysis
   - Analyzes budget feasibility
   - Calculates budget breakdown
   - Checks if trip is affordable

2. Main Flow (Budget Feasible):
   budget_analysis → search_flights → search_hotels → [search_activities] → 
   generate_itinerary → END

3. Alternative Flow (Budget Insufficient):
   budget_analysis → suggest_alternatives → END

4. Error Flow (Any Error):
   [Any Node] → error_handler → END

════════════════════════════════════════════════════════════════════════════
"""

    return visualization


if __name__ == "__main__":
    # Display graph visualization
    print(visualize_graph())

    # Example execution
    print("\nExample execution:")
    print("Run: python -m src.graph")
    print("\nOr use programmatically:")
    print("  from src.graph import run_travel_planning_workflow")
    print("  result = run_travel_planning_workflow(")
    print('      destination="Paris",')
    print('      start_date="2024-06-01",')
    print('      end_date="2024-06-10",')
    print("      budget=3000.0,")
    print("      duration=10,")
    print("  )")

