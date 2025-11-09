#!/usr/bin/env python3.11
"""Quick test to verify core functionality works."""

import sys
sys.path.insert(0, '/Users/ab000746/Downloads/Travel-planner-agent/src')

try:
    print("=" * 70)
    print("Testing Travel Planner Core Functionality")
    print("=" * 70)

    # Test 1: Import checks
    print("\n1. Testing imports...")
    from agents.state import AgentState
    from nodes.planning_nodes import budget_analysis_node
    print("   ✓ Imports successful")

    # Test 2: Create state
    print("\n2. Creating AgentState...")
    state = AgentState(
        destination="Paris, France",
        budget=3000.0,
        duration=5,
    )
    print(f"   ✓ State created: {state.destination}, ${state.budget}, {state.duration} days")

    # Test 3: Run budget analysis
    print("\n3. Running budget analysis...")
    result = budget_analysis_node(state)
    print(f"   ✓ Budget analysis complete")
    print(f"     - Feasible: {result['budget_feasible']}")
    print(f"     - Breakdown: {result['budget_breakdown']}")
    print(f"     - Min required: ${result['minimum_required_budget']}")

    # Test 4: Verify calculations
    print("\n4. Verifying calculations...")
    breakdown = result['budget_breakdown']
    total = sum(breakdown.values())
    assert abs(total - 3000.0) < 0.01, f"Total should be $3000, got ${total}"
    assert breakdown['flights'] == 1200.0, f"Flights should be $1200, got ${breakdown['flights']}"
    assert breakdown['accommodation'] == 1050.0, f"Accommodation should be $1050"
    assert breakdown['activities'] == 450.0, f"Activities should be $450"
    assert breakdown['food'] == 300.0, f"Food should be $300"
    print("   ✓ All calculations verified")

    # Test 5: Test insufficient budget
    print("\n5. Testing insufficient budget...")
    state2 = AgentState(
        destination="Tokyo, Japan",
        budget=500.0,
        duration=7,
    )
    result2 = budget_analysis_node(state2)
    assert result2['budget_feasible'] is False, "Budget should not be feasible"
    assert result2['minimum_required_budget'] == 700.0, f"Min should be $700, got ${result2['minimum_required_budget']}"
    print(f"   ✓ Insufficient budget test passed")
    print(f"     - Budget available: $500")
    print(f"     - Minimum required: ${result2['minimum_required_budget']}")

    # Test 6: Settings validation
    print("\n6. Testing configuration...")
    from config.settings import APISettings
    api_settings = APISettings()
    assert len(api_settings.secret_key) >= 32, f"Secret key too short: {len(api_settings.secret_key)}"
    print(f"   ✓ Configuration valid")
    print(f"     - Secret key length: {len(api_settings.secret_key)} chars")

    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)
    sys.exit(0)

except Exception as e:
    print("\n" + "=" * 70)
    print(f"❌ TEST FAILED: {e}")
    print("=" * 70)
    import traceback
    traceback.print_exc()
    sys.exit(1)

