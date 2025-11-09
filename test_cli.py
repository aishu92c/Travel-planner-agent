#!/usr/bin/env python3
"""Simple test script to diagnose import issues."""

import sys
import traceback

print("=" * 70)
print("Travel Planner CLI Test")
print("=" * 70)

try:
    print("\n1. Testing basic imports...")
    import os
    print("   ✓ os imported")

    from pathlib import Path
    print("   ✓ pathlib imported")

    print("\n2. Testing src package...")
    sys.path.insert(0, str(Path(__file__).parent))
    print(f"   - sys.path: {sys.path[0]}")

    print("\n3. Testing src.agents.state...")
    from src.agents.state import AgentState
    print("   ✓ AgentState imported")

    print("\n4. Testing src.graph...")
    from src.graph import create_graph
    print("   ✓ create_graph imported")

    print("\n5. Creating graph...")
    graph = create_graph()
    print("   ✓ Graph created successfully")

    print("\n6. Testing with sample input...")
    initial_state = {
        "destination": "Barcelona, Spain",
        "budget": 2500.0,
        "duration": 5,
        "departure_city": "London, UK",
        "preferences": {
            "accommodation_type": "hotel",
            "dietary": "none",
            "activities": "cultural"
        },
        "budget_breakdown": {},
        "budget_feasible": False,
        "flight_results": [],
        "hotel_results": [],
        "activity_results": [],
        "selected_flight": {},
        "selected_hotel": {},
        "final_itinerary": "",
        "error_message": None
    }
    print("   ✓ Initial state created")

    print("\n7. Invoking graph...")
    result = graph.invoke(initial_state)
    print("   ✓ Graph invoked successfully")
    print(f"\n   Result keys: {list(result.keys())}")
    print(f"   Budget feasible: {result.get('budget_feasible')}")
    print(f"   Error message: {result.get('error_message')}")

    print("\n" + "=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)

except Exception as e:
    print(f"\n❌ Error occurred: {e}")
    print("\nTraceback:")
    traceback.print_exc()
    sys.exit(1)

