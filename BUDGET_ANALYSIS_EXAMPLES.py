"""
Budget Analysis Node - Usage Guide & Examples
==============================================

This document provides practical examples of using the budget_analysis_node
in your travel planner application.
"""

# ============================================================================
# IMPORT STATEMENTS
# ============================================================================

from src.agents.state import AgentState, TravelPlannerInput
from src.nodes.planning_nodes import budget_analysis_node
import logging

# Configure logging to see detailed analysis
logging.basicConfig(level=logging.INFO)


# ============================================================================
# EXAMPLE 1: Simple Budget Analysis
# ============================================================================

def example_1_simple_analysis():
    """Example 1: Basic budget analysis for a Paris trip."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Simple Budget Analysis - Paris")
    print("="*70)

    # Create agent state
    state = AgentState(
        destination="Paris",
        budget=3000.0,
        duration=10,
    )

    # Analyze budget
    result = budget_analysis_node(state)

    # Display results
    print(f"\n✓ Budget Feasible: {result['budget_feasible']}")
    print(f"  Region: {result['region'].upper()}")
    print(f"  Minimum Required: ${result['minimum_required_budget']:.2f}")
    print(f"\nBudget Breakdown:")
    for category, amount in result['budget_breakdown'].items():
        print(f"  • {category.capitalize()}: ${amount:.2f}")


# ============================================================================
# EXAMPLE 2: Infeasible Budget Analysis
# ============================================================================

def example_2_infeasible_budget():
    """Example 2: Budget analysis revealing insufficient funds."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Infeasible Budget Analysis - Tokyo")
    print("="*70)

    # Create state with insufficient budget
    state = AgentState(
        destination="Tokyo",
        budget=500.0,
        duration=7,
    )

    # Analyze budget
    result = budget_analysis_node(state)

    # Display results and suggestion
    print(f"\n✗ Budget Feasible: {result['budget_feasible']}")
    print(f"  Available: ${state.budget:.2f}")
    print(f"  Minimum Required: ${result['minimum_required_budget']:.2f}")

    # Calculate deficit
    deficit = result['minimum_required_budget'] - state.budget
    print(f"  Deficit: ${deficit:.2f}")
    print(f"\nSuggestion: Consider these alternatives:")
    print(f"  • Increase budget by ${deficit:.2f}")
    print(f"  • Reduce trip duration to {int(state.budget / result['minimum_per_day'])} days")
    print(f"  • Choose a cheaper destination (e.g., Asia: $100/day)")


# ============================================================================
# EXAMPLE 3: Workflow Integration
# ============================================================================

def example_3_workflow_integration():
    """Example 3: Integrating budget analysis in a planning workflow."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Workflow Integration")
    print("="*70)

    # Step 1: Get user input and validate
    print("\nStep 1: Validating user input...")
    try:
        user_input = TravelPlannerInput(
            destination="London",
            start_date="2024-06-01",
            end_date="2024-06-15",
            budget=2500.0,
            duration=14,
        )
        print("✓ Input validated successfully")
    except ValueError as e:
        print(f"✗ Validation failed: {e}")
        return

    # Step 2: Create agent state
    print("\nStep 2: Creating agent state...")
    state = AgentState(
        destination=user_input.destination,
        start_date=user_input.start_date,
        end_date=user_input.end_date,
        budget=user_input.budget,
        duration=user_input.duration,
    )
    print("✓ State created")

    # Step 3: Analyze budget
    print("\nStep 3: Analyzing budget...")
    budget_result = budget_analysis_node(state)

    # Step 4: Process results
    print("\nStep 4: Processing results...")
    if budget_result['budget_feasible']:
        print("✓ Trip is feasible!")
        print(f"  Budget breakdown:")
        for category, amount in budget_result['budget_breakdown'].items():
            print(f"    • {category}: ${amount:.2f}")

        # Update state with breakdown
        state.budget_breakdown = budget_result['budget_breakdown']
        state.budget_feasible = True
        print("✓ State updated with budget information")
    else:
        print("✗ Trip exceeds budget!")
        deficit = budget_result['minimum_required_budget'] - user_input.budget
        print(f"  Additional budget needed: ${deficit:.2f}")

        # Update state with error
        state.error_message = (
            f"Budget insufficient. Need ${deficit:.2f} more. "
            f"Consider increasing budget or reducing duration."
        )
        state.budget_feasible = False
        print("✓ State updated with error information")


# ============================================================================
# EXAMPLE 4: Multiple Destinations Comparison
# ============================================================================

def example_4_destination_comparison():
    """Example 4: Compare budget feasibility across destinations."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Destination Comparison")
    print("="*70)

    destinations = [
        ("Bangkok", 1400),
        ("Paris", 1400),
        ("New York", 1400),
        ("Cairo", 1400),
    ]

    budget = 2000.0
    duration = 10

    print(f"\nComparing destinations with ${budget:.2f} budget for {duration} days:\n")
    print(f"{'Destination':<15} {'Region':<10} {'Min Req':<12} {'Feasible':<10} {'Surplus':<10}")
    print("-" * 60)

    for destination, min_budget in destinations:
        state = AgentState(
            destination=destination,
            budget=budget,
            duration=duration,
        )

        result = budget_analysis_node(state)

        surplus = budget - result['minimum_required_budget']
        feasible = "✓ Yes" if result['budget_feasible'] else "✗ No"

        print(f"{destination:<15} {result['region']:<10} "
              f"${result['minimum_required_budget']:<11.2f} {feasible:<10} "
              f"${surplus:>8.2f}")


# ============================================================================
# EXAMPLE 5: Custom Budget Allocation
# ============================================================================

def example_5_custom_allocation():
    """Example 5: Using budget breakdown for custom planning."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Custom Budget Allocation")
    print("="*70)

    # Analyze budget
    state = AgentState(
        destination="Barcelona",
        budget=2000.0,
        duration=8,
    )

    result = budget_analysis_node(state)
    breakdown = result['budget_breakdown']

    # Use breakdown for planning
    print(f"\nUsing budget breakdown to plan activities:\n")

    print(f"FLIGHTS (${breakdown['flights']:.2f}):")
    print(f"  • 1 round-trip flight at this budget")

    print(f"\nACCOMMODATION (${breakdown['accommodation']:.2f}):")
    hotel_per_night = breakdown['accommodation'] / state.duration
    print(f"  • ${hotel_per_night:.2f}/night for {state.duration} nights")
    print(f"  • Options: Budget hotel, Airbnb, hostel")

    print(f"\nACTIVITIES (${breakdown['activities']:.2f}):")
    activities_per_day = breakdown['activities'] / state.duration
    print(f"  • ${activities_per_day:.2f}/day for activities")
    print(f"  • Options: Museum entry, tours, attractions")

    print(f"\nFOOD (${breakdown['food']:.2f}):")
    meals_per_day = breakdown['food'] / state.duration
    print(f"  • ${meals_per_day:.2f}/day for food")
    print(f"  • Options: Mix of restaurants and street food")


# ============================================================================
# EXAMPLE 6: Error Handling
# ============================================================================

def example_6_error_handling():
    """Example 6: Handling errors in budget analysis."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Error Handling")
    print("="*70)

    # Test 1: Invalid budget
    print("\nTest 1: Negative budget")
    try:
        state = AgentState(destination="Paris", budget=-100.0, duration=10)
        budget_analysis_node(state)
    except ValueError as e:
        print(f"✓ Caught error: {e}")

    # Test 2: Invalid duration
    print("\nTest 2: Zero duration")
    try:
        state = AgentState(destination="Paris", budget=2000.0, duration=0)
        budget_analysis_node(state)
    except ValueError as e:
        print(f"✓ Caught error: {e}")

    # Test 3: Unknown destination (should use default)
    print("\nTest 3: Unknown destination (defaults to Asia)")
    state = AgentState(
        destination="Unknown Planet",
        budget=1500.0,
        duration=10,
    )
    result = budget_analysis_node(state)
    print(f"✓ Region assigned: {result['region']}")
    print(f"  Minimum per day: ${result['minimum_per_day']}")


# ============================================================================
# EXAMPLE 7: Dynamic Duration Adjustment
# ============================================================================

def example_7_dynamic_adjustment():
    """Example 7: Finding optimal duration within budget."""
    print("\n" + "="*70)
    print("EXAMPLE 7: Dynamic Duration Adjustment")
    print("="*70)

    destination = "Paris"
    budget = 1000.0

    print(f"\nFinding optimal duration for {destination} with ${budget:.2f}:\n")
    print(f"{'Days':<8} {'Minimum':<12} {'Feasible':<12} {'Surplus':<10}")
    print("-" * 45)

    for duration in range(1, 11):
        state = AgentState(
            destination=destination,
            budget=budget,
            duration=duration,
        )

        result = budget_analysis_node(state)

        surplus = budget - result['minimum_required_budget']
        feasible = "✓ Yes" if result['budget_feasible'] else "✗ No"

        print(f"{duration:<8} ${result['minimum_required_budget']:<11.2f} "
              f"{feasible:<12} ${surplus:>8.2f}")

        if not result['budget_feasible']:
            break

    print(f"\nOptimal: Maximum {duration - 1} days with comfort buffer")


# ============================================================================
# EXAMPLE 8: Budget Optimization Strategies
# ============================================================================

def example_8_optimization_strategies():
    """Example 8: Strategies for budget optimization."""
    print("\n" + "="*70)
    print("EXAMPLE 8: Budget Optimization Strategies")
    print("="*70)

    destinations_and_budgets = [
        ("Paris", 1500.0, 10),
        ("Bangkok", 1500.0, 14),
        ("New York", 1500.0, 8),
    ]

    print("\nFinding the best value trip with $1500 budget:\n")
    print(f"{'Destination':<15} {'Days':<6} {'Feasible':<12} {'Comfort':<15}")
    print("-" * 50)

    best_value = None
    best_score = -1

    for dest, budget, duration in destinations_and_budgets:
        state = AgentState(
            destination=dest,
            budget=budget,
            duration=duration,
        )

        result = budget_analysis_node(state)

        feasible = "✓ Yes" if result['budget_feasible'] else "✗ No"

        # Calculate comfort score (days × feasibility + surplus)
        if result['budget_feasible']:
            surplus = budget - result['minimum_required_budget']
            score = duration + (surplus / 100)
            comfort = f"Excellent (+${surplus:.2f})"
        else:
            deficit = result['minimum_required_budget'] - budget
            score = duration - (deficit / 100)
            comfort = f"Low (-${deficit:.2f})"

        print(f"{dest:<15} {duration:<6} {feasible:<12} {comfort:<15}")

        if score > best_score and result['budget_feasible']:
            best_score = score
            best_value = (dest, duration, surplus)

    if best_value:
        print(f"\n✓ Best value: {best_value[0]} for {best_value[1]} days "
              f"(surplus: ${best_value[2]:.2f})")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("BUDGET ANALYSIS NODE - COMPREHENSIVE EXAMPLES")
    print("="*70)

    # Run all examples
    example_1_simple_analysis()
    example_2_infeasible_budget()
    example_3_workflow_integration()
    example_4_destination_comparison()
    example_5_custom_allocation()
    example_6_error_handling()
    example_7_dynamic_adjustment()
    example_8_optimization_strategies()

    print("\n" + "="*70)
    print("ALL EXAMPLES COMPLETED")
    print("="*70)

