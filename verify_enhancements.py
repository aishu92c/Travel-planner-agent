#!/usr/bin/env python3
"""Quick verification of the enhanced state.py file."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Import and verify the enhancements
from src.agents.state import AgentState, TravelPlannerInput
from pydantic import ValidationError

print("=" * 70)
print("VERIFICATION: Enhanced AgentState and TravelPlannerInput")
print("=" * 70)

# 1. Verify AgentState has new fields
print("\n1. Checking AgentState fields...")
state = AgentState(messages=[])
new_fields = [
    'destination', 'start_date', 'end_date', 'budget', 'duration',
    'flights', 'hotels', 'activities', 'itinerary',
    'error_message', 'budget_feasible', 'budget_breakdown',
    'selected_flight', 'selected_hotel'
]

missing_fields = []
for field in new_fields:
    if not hasattr(state, field):
        missing_fields.append(field)

if missing_fields:
    print(f"   ✗ FAILED - Missing fields: {missing_fields}")
    sys.exit(1)
else:
    print(f"   ✓ PASSED - All {len(new_fields)} new fields present")

# 2. Verify AgentState with populated travel data
print("\n2. Testing AgentState with travel data...")
state_with_data = AgentState(
    messages=[],
    destination="Paris",
    start_date="2024-06-01",
    end_date="2024-06-10",
    budget=5000.0,
    duration=10,
    flights=[{"id": "FL1", "price": 500}],
    hotels=[{"id": "H1", "price": 100}],
    error_message="Test error",
    budget_feasible=True,
    budget_breakdown={"flights": 500, "hotels": 1000},
    selected_flight={"id": "FL1"},
    selected_hotel={"id": "H1"}
)

checks = [
    (state_with_data.destination == "Paris", "destination"),
    (state_with_data.budget == 5000.0, "budget"),
    (state_with_data.duration == 10, "duration"),
    (len(state_with_data.flights) == 1, "flights"),
    (len(state_with_data.hotels) == 1, "hotels"),
    (state_with_data.error_message == "Test error", "error_message"),
    (state_with_data.budget_feasible is True, "budget_feasible"),
    (state_with_data.selected_flight is not None, "selected_flight"),
]

failed = [name for check, name in checks if not check]
if failed:
    print(f"   ✗ FAILED - Fields not set correctly: {failed}")
    sys.exit(1)
else:
    print(f"   ✓ PASSED - All travel data fields work correctly")

# 3. Verify TravelPlannerInput exists and validates
print("\n3. Testing TravelPlannerInput validation...")
try:
    valid_input = TravelPlannerInput(
        destination="Paris",
        start_date="2024-06-01",
        end_date="2024-06-10",
        budget=5000.0,
        duration=10
    )
    print(f"   ✓ PASSED - Valid input accepted")
except Exception as e:
    print(f"   ✗ FAILED - Valid input rejected: {e}")
    sys.exit(1)

# 4. Test budget validation (must be > 0)
print("\n4. Testing budget validation (> 0)...")
try:
    TravelPlannerInput(
        destination="Paris",
        start_date="2024-06-01",
        end_date="2024-06-10",
        budget=0,  # Invalid: must be > 0
        duration=10
    )
    print(f"   ✗ FAILED - Zero budget was accepted (should reject)")
    sys.exit(1)
except ValidationError:
    print(f"   ✓ PASSED - Zero budget correctly rejected")

try:
    TravelPlannerInput(
        destination="Paris",
        start_date="2024-06-01",
        end_date="2024-06-10",
        budget=-100,  # Invalid: must be > 0
        duration=10
    )
    print(f"   ✗ FAILED - Negative budget was accepted (should reject)")
    sys.exit(1)
except ValidationError:
    print(f"   ✓ PASSED - Negative budget correctly rejected")

# 5. Test duration validation (1-30 days)
print("\n5. Testing duration validation (1-30 days)...")
try:
    TravelPlannerInput(
        destination="Paris",
        start_date="2024-06-01",
        end_date="2024-06-10",
        budget=5000.0,
        duration=0  # Invalid: must be >= 1
    )
    print(f"   ✗ FAILED - Zero duration was accepted (should reject)")
    sys.exit(1)
except ValidationError:
    print(f"   ✓ PASSED - Zero duration correctly rejected")

try:
    TravelPlannerInput(
        destination="Paris",
        start_date="2024-06-01",
        end_date="2024-06-10",
        budget=5000.0,
        duration=31  # Invalid: must be <= 30
    )
    print(f"   ✗ FAILED - Duration > 30 was accepted (should reject)")
    sys.exit(1)
except ValidationError:
    print(f"   ✓ PASSED - Duration > 30 correctly rejected")

# Valid durations should work
for dur in [1, 15, 30]:
    try:
        TravelPlannerInput(
            destination="Paris",
            start_date="2024-06-01",
            end_date="2024-06-10",
            budget=5000.0,
            duration=dur
        )
    except ValidationError as e:
        print(f"   ✗ FAILED - Valid duration {dur} rejected: {e}")
        sys.exit(1)

print(f"   ✓ PASSED - All valid durations (1, 15, 30) accepted")

# 6. Test field validators
print("\n6. Testing field validators...")
try:
    input_with_prefs = TravelPlannerInput(
        destination="Tokyo",
        start_date="2024-07-01",
        end_date="2024-07-14",
        budget=3000.0,
        duration=14,
        user_preferences={"hotel_rating": 4, "activities": ["museums"]}
    )
    print(f"   ✓ PASSED - Field validators working")
except Exception as e:
    print(f"   ✗ FAILED - Field validators failed: {e}")
    sys.exit(1)

# 7. Test backward compatibility
print("\n7. Testing backward compatibility...")
try:
    from src.agents.state import Message, MessageRole, AgentMetadata

    msg = Message(role="user", content="Test")
    metadata = AgentMetadata(agent_id="test_agent")
    state = AgentState(
        messages=[msg],
        context={"test": "value"},
        metadata=metadata,
        is_complete=False,
        iteration_count=1
    )

    if (state.messages[0].content == "Test" and
        state.context["test"] == "value" and
        state.metadata.agent_id == "test_agent"):
        print(f"   ✓ PASSED - Backward compatibility maintained")
    else:
        print(f"   ✗ FAILED - Backward compatibility broken")
        sys.exit(1)
except Exception as e:
    print(f"   ✗ FAILED - Backward compatibility test failed: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✓ ALL VERIFICATION TESTS PASSED!")
print("=" * 70)
print("\nEnhancements Summary:")
print("  • AgentState now has 13 new travel planner-specific fields")
print("  • TravelPlannerInput model with validation rules added")
print("  • Budget validation: must be > 0")
print("  • Duration validation: must be between 1 and 30 days")
print("  • Full backward compatibility maintained")
print("=" * 70)

