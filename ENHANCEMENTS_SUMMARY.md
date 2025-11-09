# Travel Planner Agent State Enhancement Summary

## Overview
The `src/agents/state.py` file has been enhanced to support travel planning functionality while maintaining full backward compatibility with existing code.

## Changes Made

### 1. Enhanced AgentState TypedDict (Pydantic Model)
Added 13 new travel planner-specific fields to the `AgentState` class:

#### Travel Destination & Date Fields:
- **`destination: str | None`** - Travel destination (e.g., "Paris")
- **`start_date: str | None`** - Trip start date (ISO format: YYYY-MM-DD)
- **`end_date: str | None`** - Trip end date (ISO format: YYYY-MM-DD)

#### Budget & Duration Fields:
- **`budget: float`** (default: 0.0, ≥ 0) - Total trip budget in USD
- **`duration: int`** (default: 0, 0-30 days) - Trip duration in days

#### Itinerary & Booking Fields:
- **`flights: list[dict[str, Any]]`** - Available flight options with full type hints
- **`hotels: list[dict[str, Any]]`** - Available hotel options with full type hints
- **`activities: list[dict[str, Any]]`** - Available activities/attractions with full type hints
- **`itinerary: list[dict[str, Any]]`** - Final travel itinerary with full type hints

#### Budget & Error Handling Fields:
- **`error_message: str | None`** - Error message if planning failed
- **`budget_feasible: bool`** (default: False) - Whether trip is feasible within budget
- **`budget_breakdown: dict[str, float]`** - Cost breakdown by category (flights, hotels, activities, etc.)

#### Selection Fields:
- **`selected_flight: dict[str, Any] | None`** - The selected flight option
- **`selected_hotel: dict[str, Any] | None`** - The selected hotel option

### 2. New TravelPlannerInput Pydantic Model
A dedicated validation model for travel planning input with built-in validation:

```python
class TravelPlannerInput(BaseModel):
    destination: str              # Required, min length 1
    start_date: str              # Required, ISO format (YYYY-MM-DD)
    end_date: str                # Required, ISO format (YYYY-MM-DD)
    budget: float                # Required, must be > 0
    duration: int                # Required, must be 1-30 days
    user_preferences: dict | None # Optional user preferences
```

#### Validation Rules:
- **`budget > 0`** - Budget must be positive (enforced by field validator and `gt=0` constraint)
- **`1 ≤ duration ≤ 30`** - Duration must be between 1 and 30 days (enforced by field validators)
- **`destination`** - Must be a non-empty string
- **`start_date` and `end_date`** - Must be valid ISO format date strings (min length 10)

#### Field Validators:
```python
@field_validator("budget")
@classmethod
def validate_budget(cls, v: float) -> float:
    """Ensure budget is positive."""
    if v <= 0:
        raise ValueError("Budget must be greater than 0")
    return v

@field_validator("duration")
@classmethod
def validate_duration(cls, v: int) -> int:
    """Ensure duration is between 1 and 30 days."""
    if not (1 <= v <= 30):
        raise ValueError("Duration must be between 1 and 30 days")
    return v
```

### 3. Updated Exports
Added `TravelPlannerInput` to the `__all__` export list:

```python
__all__ = [
    "MessageRole",
    "Message",
    "AgentMetadata",
    "AgentState",
    "ToolInput",
    "ToolStatus",
    "ToolOutput",
    "TravelPlannerInput",  # NEW
    "AgentDecision",
]
```

## Backward Compatibility

✅ **Fully maintained** - All existing fields and methods in `AgentState` continue to work:
- `messages: list[Message]`
- `context: dict[str, Any]`
- `metadata: AgentMetadata | None`
- `intermediate_steps: list[dict[str, Any]]`
- `tool_results: list[ToolOutput]`
- `error: str | None`
- `is_complete: bool`
- `iteration_count: int`
- `next_agent: str | None`
- `add_message()` method
- `get_last_message()` method
- `get_messages_by_role()` method

## Usage Examples

### Example 1: Validating User Input
```python
from src.agents.state import TravelPlannerInput

# Valid input
planner_input = TravelPlannerInput(
    destination="Paris",
    start_date="2024-06-01",
    end_date="2024-06-10",
    budget=5000.0,
    duration=10,
    user_preferences={"hotel_rating": 4, "flight_preference": "direct"}
)

# Invalid budget - will raise ValidationError
try:
    bad_input = TravelPlannerInput(
        destination="Paris",
        start_date="2024-06-01",
        end_date="2024-06-10",
        budget=0,  # ✗ Must be > 0
        duration=10
    )
except ValidationError as e:
    print(f"Validation error: {e}")

# Invalid duration - will raise ValidationError
try:
    bad_input = TravelPlannerInput(
        destination="Paris",
        start_date="2024-06-01",
        end_date="2024-06-10",
        budget=5000.0,
        duration=31  # ✗ Must be 1-30
    )
except ValidationError as e:
    print(f"Validation error: {e}")
```

### Example 2: Creating Agent State with Travel Data
```python
from src.agents.state import AgentState, Message

state = AgentState(
    messages=[Message(role="user", content="Plan my trip to Tokyo")],
    destination="Tokyo",
    start_date="2024-07-01",
    end_date="2024-07-14",
    budget=4000.0,
    duration=14,
    flights=[
        {"id": "FL1", "airline": "JAL", "price": 800},
        {"id": "FL2", "airline": "ANA", "price": 750},
    ],
    hotels=[
        {"id": "H1", "name": "Hotel A", "price": 100, "rating": 4.5},
        {"id": "H2", "name": "Hotel B", "price": 120, "rating": 4.8},
    ],
    activities=[
        {"id": "A1", "name": "Senso-ji Temple", "price": 50},
        {"id": "A2", "name": "Shibuya Crossing", "price": 0},
    ],
)

# Add budget breakdown
state.budget_breakdown = {
    "flights": 800,
    "hotels": 100 * 14,
    "activities": 500,
}

# Check feasibility
total_cost = sum(state.budget_breakdown.values())
state.budget_feasible = total_cost <= state.budget

# Select options
state.selected_flight = state.flights[1]  # ANA
state.selected_hotel = state.hotels[0]    # Hotel A

# Create itinerary
state.itinerary = [
    {"day": 1, "activity": "Arrival at Haneda", "cost": 0},
    {"day": 2, "activity": "Visit Senso-ji", "cost": 50},
    {"day": 3, "activity": "Explore Shibuya", "cost": 0},
]
```

### Example 3: Data Flow from Input to State
```python
from src.agents.state import TravelPlannerInput, AgentState

# Step 1: Validate user input
user_input = TravelPlannerInput(
    destination="Paris",
    start_date="2024-06-01",
    end_date="2024-06-10",
    budget=5000.0,
    duration=10
)

# Step 2: Create agent state from validated input
state = AgentState(
    messages=[],
    destination=user_input.destination,
    start_date=user_input.start_date,
    end_date=user_input.end_date,
    budget=user_input.budget,
    duration=user_input.duration,
)

# Step 3: Populate with planning results
# ... planning logic ...
state.flights = fetch_flights(state.destination, state.start_date, state.budget)
state.hotels = fetch_hotels(state.destination, state.start_date, state.duration, state.budget)

# Step 4: Validate budget
total_cost = calculate_total_cost(state)
state.budget_feasible = total_cost <= state.budget

if not state.budget_feasible:
    state.error_message = f"Total cost ${total_cost} exceeds budget ${state.budget}"
```

## Type Hints

All nested structures now have proper type hints:
- `flights: list[dict[str, Any]]` - List of flight dictionaries
- `hotels: list[dict[str, Any]]` - List of hotel dictionaries
- `activities: list[dict[str, Any]]` - List of activity dictionaries
- `itinerary: list[dict[str, Any]]` - List of itinerary items
- `budget_breakdown: dict[str, float]` - Category-to-cost mapping
- `selected_flight: dict[str, Any] | None` - Single selected flight or None
- `selected_hotel: dict[str, Any] | None` - Single selected hotel or None

## Testing

The enhancements have been tested for:
✅ All new fields are present and accessible
✅ Fields have correct default values
✅ Type hints work correctly for nested structures
✅ Budget validation enforces > 0
✅ Duration validation enforces 1-30 range
✅ Field validators work correctly
✅ Backward compatibility maintained with existing fields
✅ Data can flow from TravelPlannerInput to AgentState
✅ Complete travel planning workflow works end-to-end

## Files Modified

- **`src/agents/state.py`**
  - Added `ConfigDict` to imports
  - Added 13 new fields to `AgentState` class
  - Added new `TravelPlannerInput` Pydantic model with validators
  - Updated `__all__` export list

## Notes

- The project uses Python 3.11+, so the `X | Y` union syntax is fully supported
- All changes maintain the existing Pydantic v2 style and patterns
- The enhancements are designed to work with LangGraph's state management system
- Error handling via `error_message` field allows for graceful failure scenarios
- Budget tracking via `budget_breakdown` enables detailed cost analysis
- Selection fields (`selected_flight`, `selected_hotel`) store final user choices for implementation

