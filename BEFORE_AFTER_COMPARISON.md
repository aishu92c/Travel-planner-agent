"""
BEFORE & AFTER COMPARISON
Travel Planner Agent State Enhancement
"""

# ============================================================================
# BEFORE: Original AgentState (simplified view)
# ============================================================================

BEFORE = """
class AgentState(BaseModel):
    messages: list[Message]
    context: dict[str, Any]
    metadata: AgentMetadata | None
    intermediate_steps: list[dict[str, Any]]
    tool_results: list[ToolOutput]
    error: str | None
    is_complete: bool
    iteration_count: int
    next_agent: str | None
    
    # Methods
    def add_message(...)
    def get_last_message(...)
    def get_messages_by_role(...)
"""

# ============================================================================
# AFTER: Enhanced AgentState (new fields highlighted)
# ============================================================================

AFTER = """
class AgentState(BaseModel):
    # EXISTING FIELDS (unchanged)
    messages: list[Message]
    context: dict[str, Any]
    metadata: AgentMetadata | None
    intermediate_steps: list[dict[str, Any]]
    tool_results: list[ToolOutput]
    error: str | None
    is_complete: bool
    iteration_count: int
    next_agent: str | None
    
    # NEW: Travel Planning Fields (13 new fields)
    destination: str | None                      # ← NEW
    start_date: str | None                       # ← NEW
    end_date: str | None                         # ← NEW
    budget: float                                # ← NEW
    duration: int                                # ← NEW
    flights: list[dict[str, Any]]               # ← NEW (with type hints)
    hotels: list[dict[str, Any]]                # ← NEW (with type hints)
    activities: list[dict[str, Any]]            # ← NEW (with type hints)
    itinerary: list[dict[str, Any]]             # ← NEW (with type hints)
    error_message: str | None                   # ← NEW
    budget_feasible: bool                       # ← NEW
    budget_breakdown: dict[str, float]          # ← NEW
    selected_flight: dict[str, Any] | None      # ← NEW
    selected_hotel: dict[str, Any] | None       # ← NEW
    
    # Methods (unchanged)
    def add_message(...)
    def get_last_message(...)
    def get_messages_by_role(...)
"""

# ============================================================================
# NEW: TravelPlannerInput Model (completely new)
# ============================================================================

NEW_MODEL = """
class TravelPlannerInput(BaseModel):  # ← COMPLETELY NEW
    destination: str              # Required, non-empty
    start_date: str              # Required, ISO format (min_length=10)
    end_date: str                # Required, ISO format (min_length=10)
    budget: float                # Required, MUST BE > 0 (gt=0)
    duration: int                # Required, MUST BE 1-30 (ge=1, le=30)
    user_preferences: dict | None # Optional
    
    @field_validator("budget")   # ← NEW
    @classmethod
    def validate_budget(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Budget must be greater than 0")
        return v
    
    @field_validator("duration")  # ← NEW
    @classmethod
    def validate_duration(cls, v: int) -> int:
        if not (1 <= v <= 30):
            raise ValueError("Duration must be between 1 and 30 days")
        return v
"""

# ============================================================================
# COMPARISON TABLE
# ============================================================================

COMPARISON = """
┌─────────────────────────────────────────────────────────────────────────────┐
│ FEATURE                          │ BEFORE           │ AFTER                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ Travel Destination Storage        │ ✗ Not supported  │ ✓ destination field   │
│ Date Tracking                     │ ✗ Not supported  │ ✓ start_date/end_date │
│ Budget Support                    │ ✗ Not supported  │ ✓ budget field        │
│ Duration Tracking                 │ ✗ Not supported  │ ✓ duration field      │
│ Flights Storage                   │ ✗ Not supported  │ ✓ flights list        │
│ Hotels Storage                    │ ✗ Not supported  │ ✓ hotels list         │
│ Activities Storage                │ ✗ Not supported  │ ✓ activities list     │
│ Itinerary Storage                 │ ✗ Not supported  │ ✓ itinerary list      │
│ Error Handling                    │ ✗ Not supported  │ ✓ error_message field │
│ Budget Feasibility Check          │ ✗ Not supported  │ ✓ budget_feasible     │
│ Cost Breakdown                    │ ✗ Not supported  │ ✓ budget_breakdown    │
│ Flight Selection                  │ ✗ Not supported  │ ✓ selected_flight     │
│ Hotel Selection                   │ ✗ Not supported  │ ✓ selected_hotel      │
│ Input Validation Model            │ ✗ None           │ ✓ TravelPlannerInput  │
│ Budget Validation                 │ ✗ None           │ ✓ Enforces > 0        │
│ Duration Validation               │ ✗ None           │ ✓ Enforces 1-30 days  │
│ Field Validators                  │ ✗ None           │ ✓ 2 validators        │
│ Type Hints (nested)               │ ✗ Partial/Untyped│ ✓ List[Dict[str,Any]] │
│ Backward Compatibility            │ N/A              │ ✓ 100% Compatible     │
└─────────────────────────────────────────────────────────────────────────────┘
"""

# ============================================================================
# USE CASE COMPARISON
# ============================================================================

USE_CASE_BEFORE = """
BEFORE: Creating state for travel planning
──────────────────────────────────────────

state = AgentState(messages=[])

# Problem: No fields to store travel data!
# Had to:
# 1. Store everything in context dict (untyped, error-prone)
# 2. No validation of user input
# 3. No way to track budget, flights, hotels
# 4. Error handling mixed in with general errors

state.context["destination"] = "Paris"  # ✗ Untyped, no validation
state.context["budget"] = 0  # ✗ Can be any value!
state.context["flights"] = []  # ✗ No schema

# Workflow was messy and error-prone
"""

USE_CASE_AFTER = """
AFTER: Creating state for travel planning
──────────────────────────────────────────

# Step 1: Validate user input with TravelPlannerInput
try:
    user_input = TravelPlannerInput(  # ✓ Type-safe
        destination="Paris",
        start_date="2024-06-01",
        end_date="2024-06-10",
        budget=5000.0,  # ✓ Validated > 0
        duration=10     # ✓ Validated 1-30
    )
except ValidationError as e:
    handle_validation_error(e)

# Step 2: Create state with validated data
state = AgentState(
    messages=[Message(role="user", content="Plan my trip")],
    destination=user_input.destination,    # ✓ Typed
    start_date=user_input.start_date,      # ✓ Typed
    end_date=user_input.end_date,          # ✓ Typed
    budget=user_input.budget,              # ✓ Typed
    duration=user_input.duration,          # ✓ Typed
)

# Step 3: Add travel data
state.flights = [
    {"id": "FL1", "airline": "BA", "price": 500},
    {"id": "FL2", "airline": "AF", "price": 480},
]  # ✓ Properly typed list[dict[str, Any]]

state.hotels = [
    {"id": "H1", "name": "Hotel A", "price": 100},
]  # ✓ Properly typed list[dict[str, Any]]

# Step 4: Track budget
state.budget_breakdown = {
    "flights": 500,
    "hotels": 1000,
    "activities": 100,
}  # ✓ Properly typed dict[str, float]

total_cost = sum(state.budget_breakdown.values())
state.budget_feasible = total_cost <= state.budget  # ✓ Easy to check

# Step 5: Make selections
state.selected_flight = state.flights[0]   # ✓ Typed selection
state.selected_hotel = state.hotels[0]     # ✓ Typed selection

# Step 6: Build itinerary
state.itinerary = [
    {"day": 1, "activity": "Arrival"},
    {"day": 2, "activity": "Sightseeing"},
]  # ✓ Properly typed list[dict[str, Any]]

# Step 7: Handle errors gracefully
if not state.budget_feasible:
    state.error_message = f"Total ${total_cost} exceeds budget ${state.budget}"

# Workflow is clean, type-safe, and validated!
"""

# ============================================================================
# MIGRATION GUIDE
# ============================================================================

MIGRATION_GUIDE = """
HOW TO MIGRATE EXISTING CODE
─────────────────────────────

BEFORE (using context dict):
─────────────────────────────
state = AgentState(messages=[])
state.context["destination"] = "Paris"
state.context["budget"] = 5000
flight_options = state.context.get("flights", [])  # Untyped


AFTER (using new fields):
─────────────────────────
state = AgentState(
    messages=[],
    destination="Paris",     # ← Use new field
    budget=5000,            # ← Use new field
    flights=[],             # ← Use new field
)
flight_options = state.flights  # ← Type-safe and clear


NO CHANGES NEEDED:
──────────────────
# Existing code continues to work
state = AgentState(messages=[])  # Still works!
state.add_message("user", "Hello")  # Still works!
state.context = {"key": "value"}  # Still works!

# You can use new AND old fields together:
state = AgentState(
    messages=[],
    destination="Paris",     # ← New field
    context={"key": "value"} # ← Existing field, still works!
)
"""

# ============================================================================
# VALIDATION EXAMPLES
# ============================================================================

VALIDATION_EXAMPLES = """
TRAVELPLANNERINPUT VALIDATION BEHAVIOR
──────────────────────────────────────

✓ VALID INPUTS (accepted):

TravelPlannerInput(
    destination="Paris",
    start_date="2024-06-01",
    end_date="2024-06-10",
    budget=5000.0,     # ✓ > 0
    duration=10        # ✓ 1-30
)

TravelPlannerInput(
    destination="Tokyo",
    start_date="2024-07-01",
    end_date="2024-07-14",
    budget=0.01,       # ✓ > 0 (even tiny amounts OK)
    duration=1         # ✓ Minimum duration
)

TravelPlannerInput(
    destination="London",
    start_date="2024-08-01",
    end_date="2024-08-30",
    budget=999999.99,  # ✓ No upper limit
    duration=30        # ✓ Maximum duration
)


✗ INVALID INPUTS (rejected with ValidationError):

TravelPlannerInput(
    destination="",         # ✗ min_length=1
    ...
)
ValidationError: ensure this value has at least 1 characters

TravelPlannerInput(
    destination="Paris",
    start_date="2024-06",   # ✗ Invalid ISO format (min_length=10)
    ...
)
ValidationError: ensure this value has at least 10 characters

TravelPlannerInput(
    destination="Paris",
    start_date="2024-06-01",
    end_date="2024-06-10",
    budget=0,               # ✗ Must be > 0
    duration=10
)
ValidationError: Budget must be greater than 0

TravelPlannerInput(
    destination="Paris",
    start_date="2024-06-01",
    end_date="2024-06-10",
    budget=-100,            # ✗ Must be > 0
    duration=10
)
ValidationError: Budget must be greater than 0

TravelPlannerInput(
    destination="Paris",
    start_date="2024-06-01",
    end_date="2024-06-10",
    budget=5000.0,
    duration=0              # ✗ Must be >= 1
)
ValidationError: Duration must be between 1 and 30 days

TravelPlannerInput(
    destination="Paris",
    start_date="2024-06-01",
    end_date="2024-06-10",
    budget=5000.0,
    duration=31             # ✗ Must be <= 30
)
ValidationError: Duration must be between 1 and 30 days
"""

# ============================================================================
# SUMMARY
# ============================================================================

print("""
╔═════════════════════════════════════════════════════════════════════════════╗
║                    ENHANCEMENT SUMMARY                                     ║
╚═════════════════════════════════════════════════════════════════════════════╝

BEFORE: Generic agent state with no travel-specific support
  - Had to store everything in untyped context dict
  - No validation of travel parameters
  - No budget tracking
  - Error handling mixed with general errors

AFTER: Specialized travel planner state with full validation
  - 13 new typed fields for travel data
  - TravelPlannerInput model for input validation
  - Budget validation (must be > 0)
  - Duration validation (must be 1-30 days)
  - Cost breakdown tracking
  - Selection storage for flights/hotels
  - Error message field for graceful failures
  - 100% backward compatible

RESULT: Professional, type-safe travel planning agent state! ✨
""")

