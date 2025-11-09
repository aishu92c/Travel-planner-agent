#!/usr/bin/env python3
"""
Travel Planner Main Module - Usage Examples

This file contains practical examples of how to use src/main.py
both as a CLI tool and as a programmatic API.

Run individual examples with:
    python MAIN_USAGE_EXAMPLES.py
"""

import json
from typing import Dict, Any

# ============================================================================
# PROGRAMMATIC EXAMPLES
# ============================================================================

def example_1_basic_trip():
    """Example 1: Basic Trip Planning

    The simplest use case - just provide destination, budget, and duration.
    """
    print("\n" + "=" * 70)
    print("Example 1: Basic Trip Planning")
    print("=" * 70)

    from src.main import run_travel_planner

    print("\nCode:")
    print("""
    result = run_travel_planner(
        destination="Paris, France",
        budget=2000,
        duration=5
    )
    """)

    result = run_travel_planner(
        destination="Paris, France",
        budget=2000,
        duration=5
    )

    print(f"\nStatus: {result['status']}")
    print(f"Message: {result['message']}")

    state = result['state']
    print(f"\nKey Results:")
    print(f"  • Destination: {state['destination']}")
    print(f"  • Budget: ${state['budget']:,.2f}")
    print(f"  • Duration: {state['duration']} days")
    print(f"  • Budget Feasible: {state['budget_feasible']}")
    if state.get('budget_breakdown'):
        print(f"  • Budget Breakdown:")
        for category, amount in state['budget_breakdown'].items():
            print(f"    - {category}: ${amount:,.2f}")


def example_2_with_preferences():
    """Example 2: Trip with Preferences

    Planning a trip with dietary and accommodation preferences.
    """
    print("\n" + "=" * 70)
    print("Example 2: Trip with Preferences")
    print("=" * 70)

    from src.main import run_travel_planner

    print("\nCode:")
    print("""
    result = run_travel_planner(
        destination="Tokyo, Japan",
        budget=3500,
        duration=7,
        departure_city="Los Angeles, USA",
        preferences={
            "dietary": "vegan",
            "accommodation_type": "airbnb",
            "activities": "cultural"
        }
    )
    """)

    result = run_travel_planner(
        destination="Tokyo, Japan",
        budget=3500,
        duration=7,
        departure_city="Los Angeles, USA",
        preferences={
            "dietary": "vegan",
            "accommodation_type": "airbnb",
            "activities": "cultural"
        }
    )

    print(f"\nStatus: {result['status']}")

    state = result['state']
    if state.get('context'):
        print(f"\nPreferences:")
        preferences = state['context'].get('preferences', {})
        for key, value in preferences.items():
            print(f"  • {key}: {value}")


def example_3_budget_constrained():
    """Example 3: Budget-Constrained Trip

    When budget is insufficient, the system suggests alternatives.
    """
    print("\n" + "=" * 70)
    print("Example 3: Budget-Constrained Trip")
    print("=" * 70)

    from src.main import run_travel_planner

    print("\nCode:")
    print("""
    result = run_travel_planner(
        destination="Paris, France",
        budget=500,  # Very limited
        duration=5
    )
    """)

    result = run_travel_planner(
        destination="Paris, France",
        budget=500,  # Very limited
        duration=5
    )

    print(f"\nStatus: {result['status']}")

    state = result['state']
    print(f"Budget Feasible: {state['budget_feasible']}")
    if not state['budget_feasible']:
        print(f"Error: {state.get('error_message', 'Budget insufficient')}")


def example_4_dry_run():
    """Example 4: Dry-Run Mode

    Validate inputs without making LLM calls.
    """
    print("\n" + "=" * 70)
    print("Example 4: Dry-Run Mode (No LLM Calls)")
    print("=" * 70)

    from src.main import run_travel_planner

    print("\nCode:")
    print("""
    result = run_travel_planner(
        destination="Barcelona, Spain",
        budget=2500,
        duration=6,
        dry_run=True
    )
    """)

    result = run_travel_planner(
        destination="Barcelona, Spain",
        budget=2500,
        duration=6,
        dry_run=True
    )

    print(f"\nStatus: {result['status']}")
    print(f"Message: {result['message']}")

    state = result['state']
    if state.get('budget_breakdown'):
        print(f"\nBudget Breakdown (calculated in dry-run):")
        for category, amount in state['budget_breakdown'].items():
            print(f"  • {category}: ${amount:,.2f}")


def example_5_verbose_logging():
    """Example 5: Verbose Logging

    Enable debug logging to see detailed execution information.
    """
    print("\n" + "=" * 70)
    print("Example 5: Verbose Logging")
    print("=" * 70)

    from src.main import run_travel_planner

    print("\nCode:")
    print("""
    result = run_travel_planner(
        destination="Rome, Italy",
        budget=2000,
        duration=4,
        verbose=True
    )
    """)

    print("\nNote: Verbose mode will show detailed logging information")
    print("(See full console output for detailed logs)")

    result = run_travel_planner(
        destination="Rome, Italy",
        budget=2000,
        duration=4,
        verbose=True
    )

    print(f"\nStatus: {result['status']}")


def example_6_result_processing():
    """Example 6: Processing Results

    How to extract and process information from the result.
    """
    print("\n" + "=" * 70)
    print("Example 6: Processing Results")
    print("=" * 70)

    from src.main import run_travel_planner

    print("\nCode:")
    print("""
    result = run_travel_planner(...)

    # Extract data
    if result['status'] == 'success':
        state = result['state']
        
        # Get budget details
        budget_breakdown = state['budget_breakdown']
        flights_budget = budget_breakdown.get('flights', 0)
        hotel_budget = budget_breakdown.get('accommodation', 0)
        
        # Get selected options
        flight = state.get('selected_flight')
        hotel = state.get('selected_hotel')
        
        # Print summary
        print(f"Flights: ${flights_budget}")
        print(f"Hotels: ${hotel_budget}")
        if flight:
            print(f"Selected Flight: {flight.get('airline')}")
        if hotel:
            print(f"Selected Hotel: {hotel.get('name')}")
    """)

    result = run_travel_planner(
        destination="Bangkok, Thailand",
        budget=1500,
        duration=5
    )

    if result['status'] == 'success':
        state = result['state']

        print(f"\nExtracted Results:")
        print(f"  • Destination: {state['destination']}")
        print(f"  • Total Budget: ${state['budget']}")
        print(f"  • Feasible: {state['budget_feasible']}")

        if state.get('budget_breakdown'):
            print(f"  • Breakdown:")
            for cat, amt in state['budget_breakdown'].items():
                print(f"    - {cat}: ${amt:,.2f}")

        if state.get('selected_flight'):
            flight = state['selected_flight']
            print(f"  • Flight:")
            print(f"    - Airline: {flight.get('airline', 'N/A')}")
            print(f"    - Price: ${flight.get('price', 0):,.2f}")

        if state.get('selected_hotel'):
            hotel = state['selected_hotel']
            print(f"  • Hotel:")
            print(f"    - Name: {hotel.get('name', 'N/A')}")
            print(f"    - Rating: {hotel.get('rating', 0)}/5")


def example_7_multiple_trips():
    """Example 7: Planning Multiple Trips

    How to plan multiple trips programmatically.
    """
    print("\n" + "=" * 70)
    print("Example 7: Planning Multiple Trips")
    print("=" * 70)

    from src.main import run_travel_planner

    trips = [
        {"destination": "Paris, France", "budget": 2000, "duration": 5},
        {"destination": "Tokyo, Japan", "budget": 3000, "duration": 7},
        {"destination": "Barcelona, Spain", "budget": 1800, "duration": 4},
    ]

    print(f"\nPlanning {len(trips)} trips...")

    for trip in trips:
        print(f"\nPlanning: {trip['destination']}")
        result = run_travel_planner(**trip)

        if result['status'] == 'success':
            state = result['state']
            print(f"  ✓ Status: {state['budget_feasible']}")
            print(f"    Budget: ${state['budget']}")
            print(f"    Duration: {state['duration']} days")
        else:
            print(f"  ✗ Error: {result['message']}")


def example_8_saving_results():
    """Example 8: Saving Results

    How to save trip planning results to files.
    """
    print("\n" + "=" * 70)
    print("Example 8: Saving Results to File")
    print("=" * 70)

    from src.main import run_travel_planner
    import json
    from datetime import datetime

    print("\nCode:")
    print("""
    result = run_travel_planner(...)
    
    # Save as JSON
    filename = f"trip_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(result['state'], f, indent=2)
    
    print(f"Results saved to {filename}")
    """)

    result = run_travel_planner(
        destination="Amsterdam, Netherlands",
        budget=2200,
        duration=5
    )

    # Save results
    filename = f"trip_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(result['state'], f, indent=2)

    print(f"\n✓ Results saved to: {filename}")
    print(f"  File size: {len(json.dumps(result['state']))} bytes")


def example_9_error_handling():
    """Example 9: Error Handling

    How to handle validation errors.
    """
    print("\n" + "=" * 70)
    print("Example 9: Error Handling")
    print("=" * 70)

    from src.main import run_travel_planner

    print("\nExample 1: Invalid budget")
    print("Code: budget=0 (must be > 0)")
    print("Expected: Validation error")

    try:
        result = run_travel_planner(
            destination="Paris, France",
            budget=0,  # Invalid!
            duration=5
        )
        print(f"Result: {result['status']}")
    except SystemExit:
        print("✓ Caught validation error")
    except Exception as e:
        print(f"✓ Error: {e}")

    print("\nExample 2: Invalid duration")
    print("Code: duration=35 (must be 1-30)")
    print("Expected: Validation error")

    try:
        result = run_travel_planner(
            destination="Paris, France",
            budget=2000,
            duration=35  # Invalid!
        )
        print(f"Result: {result['status']}")
    except SystemExit:
        print("✓ Caught validation error")
    except Exception as e:
        print(f"✓ Error: {e}")


# ============================================================================
# CLI EXAMPLES
# ============================================================================

def print_cli_examples():
    """Print CLI usage examples."""

    print("\n" + "=" * 70)
    print("CLI (Command Line Interface) Examples")
    print("=" * 70)

    examples = [
        {
            "title": "Basic Usage",
            "command": 'python -m src.main plan --destination "Paris, France" --budget 2000 --duration 5',
            "description": "Simple trip planning with required parameters only"
        },
        {
            "title": "With Preferences",
            "command": '''python -m src.main plan \\
    --destination "Tokyo, Japan" \\
    --budget 3500 \\
    --duration 7 \\
    --dietary vegan \\
    --accommodation-type airbnb \\
    --activities cultural''',
            "description": "Trip with dietary, accommodation, and activity preferences"
        },
        {
            "title": "With Departure City",
            "command": '''python -m src.main plan \\
    --destination "Barcelona, Spain" \\
    --budget 2500 \\
    --duration 6 \\
    --departure-city "Miami, USA"''',
            "description": "Specify departure city for flight calculations"
        },
        {
            "title": "Dry-Run Mode",
            "command": 'python -m src.main plan --destination "Paris, France" --budget 2000 --duration 5 --dry-run',
            "description": "Validate inputs without making LLM calls (for testing)"
        },
        {
            "title": "Verbose Debugging",
            "command": 'python -m src.main plan --destination "Paris, France" --budget 2000 --duration 5 --verbose',
            "description": "Enable debug logging to see detailed execution"
        },
        {
            "title": "Show Help",
            "command": "python -m src.main --help",
            "description": "Display main help message"
        },
        {
            "title": "Show Plan Help",
            "command": "python -m src.main plan --help",
            "description": "Display help for 'plan' subcommand"
        },
    ]

    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['title']}")
        print(f"   {example['description']}")
        print(f"\n   $ {example['command']}\n")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run all examples."""

    print("\n" + "=" * 70)
    print("Travel Planner - Main Module Usage Examples")
    print("=" * 70)

    print("""
This file demonstrates how to use src/main.py both programmatically
and via the CLI (command line interface).

To run examples:
    python MAIN_USAGE_EXAMPLES.py

Note: These examples require the travel planner environment to be
configured with all dependencies installed.
    """)

    # Uncomment to run individual examples:

    # example_1_basic_trip()
    # example_2_with_preferences()
    # example_3_budget_constrained()
    # example_4_dry_run()
    # example_5_verbose_logging()
    # example_6_result_processing()
    # example_7_multiple_trips()
    # example_8_saving_results()
    # example_9_error_handling()

    print_cli_examples()

    print("\n" + "=" * 70)
    print("To run the examples, uncomment them in the main() function")
    print("=" * 70)


if __name__ == "__main__":
    main()

