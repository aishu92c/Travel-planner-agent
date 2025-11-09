"""
CODE REFERENCE: Enhanced AgentState and TravelPlannerInput

This document shows the exact implementation added to src/agents/state.py
"""

# ============================================================================
# 1. UPDATED IMPORTS (Added ConfigDict)
# ============================================================================

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


# ============================================================================
# 2. ENHANCED AGENTSTATE CLASS (Added travel planner fields)
# ============================================================================

class AgentState(BaseModel):
    """LangGraph agent state schema with travel planning support.
    
    Existing fields maintained for backward compatibility:
    - messages: list[Message]
    - context: dict[str, Any]
    - metadata: AgentMetadata | None
    - intermediate_steps: list[dict[str, Any]]
    - tool_results: list[ToolOutput]
    - error: str | None
    - is_complete: bool
    - iteration_count: int
    - next_agent: str | None
    
    NEW travel planner fields:
    """

    # ... existing fields ...

    # Travel Planner specific fields
    destination: str | None = Field(
        default=None,
        description="Travel destination",
    )
    start_date: str | None = Field(
        default=None,
        description="Trip start date (ISO format)",
    )
    end_date: str | None = Field(
        default=None,
        description="Trip end date (ISO format)",
    )
    budget: float = Field(
        default=0.0,
        ge=0,
        description="Budget for the trip",
    )
    duration: int = Field(
        default=0,
        ge=0,
        le=30,
        description="Trip duration in days (1-30)",
    )
    flights: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of available flight options",
    )
    hotels: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of available hotel options",
    )
    activities: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of available activities/attractions",
    )
    itinerary: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Final travel itinerary",
    )
    error_message: str | None = Field(
        default=None,
        description="Error message if planning failed",
    )
    budget_feasible: bool = Field(
        default=False,
        description="Whether the trip is feasible within budget",
    )
    budget_breakdown: dict[str, float] = Field(
        default_factory=dict,
        description="Cost breakdown by category (flights, hotels, activities, etc.)",
    )
    selected_flight: dict[str, Any] | None = Field(
        default=None,
        description="The selected flight option",
    )
    selected_hotel: dict[str, Any] | None = Field(
        default=None,
        description="The selected hotel option",
    )


# ============================================================================
# 3. NEW TRAVELPLANNERINPUT MODEL (Pydantic validation model)
# ============================================================================

class TravelPlannerInput(BaseModel):
    """Pydantic model for travel planner input validation.

    This model validates user input for travel planning with:
    - Budget must be greater than 0
    - Duration must be between 1 and 30 days
    - Required fields for destination and dates

    Example:
        >>> planner_input = TravelPlannerInput(
        ...     destination="Paris",
        ...     start_date="2024-06-01",
        ...     end_date="2024-06-10",
        ...     budget=5000.0,
        ...     duration=10,
        ...     user_preferences={"hotel_rating": 4}
        ... )
    """

    destination: str = Field(
        description="Travel destination",
        min_length=1,
    )
    start_date: str = Field(
        description="Trip start date (ISO format: YYYY-MM-DD)",
        min_length=10,
    )
    end_date: str = Field(
        description="Trip end date (ISO format: YYYY-MM-DD)",
        min_length=10,
    )
    budget: float = Field(
        description="Budget for the trip in USD",
        gt=0,  # Must be greater than 0
    )
    duration: int = Field(
        description="Trip duration in days",
        ge=1,
        le=30,  # Must be between 1 and 30
    )
    user_preferences: dict[str, Any] | None = Field(
        default=None,
        description="Optional user preferences (hotel rating, activities, etc.)",
    )

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

    class Config:
        json_schema_extra = {
            "example": {
                "destination": "Paris",
                "start_date": "2024-06-01",
                "end_date": "2024-06-10",
                "budget": 5000.0,
                "duration": 10,
                "user_preferences": {
                    "hotel_rating": 4,
                    "flight_preference": "direct",
                    "activities": ["museums", "restaurants"],
                },
            }
        }


# ============================================================================
# 4. UPDATED EXPORTS
# ============================================================================

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


# ============================================================================
# VALIDATION BEHAVIOR
# ============================================================================

"""
AGENTSTATE VALIDATION:
- All new fields have defaults (optional by default)
- Budget: must be >= 0 (float, default 0.0)
- Duration: must be 0-30 (int, default 0)
- Lists (flights, hotels, activities, itinerary): default to empty []
- Dictionaries (budget_breakdown): default to empty {}
- Optional strings (destination, start_date, end_date, error_message): default to None
- Optional dicts (selected_flight, selected_hotel): default to None
- Boolean (budget_feasible): default False

TRAVELPLANNERINPUT VALIDATION:
- All fields are REQUIRED (no defaults)
- destination: non-empty string
- start_date: ISO format string (min 10 chars for YYYY-MM-DD)
- end_date: ISO format string (min 10 chars for YYYY-MM-DD)
- budget: must be > 0 (both gt=0 constraint AND field_validator)
- duration: must be 1-30 (both ge=1, le=30 constraints AND field_validator)
- user_preferences: optional dict

FIELD VALIDATORS:
- budget validator: checks v > 0, raises ValueError if not
- duration validator: checks 1 <= v <= 30, raises ValueError if not
"""


# ============================================================================
# EXAMPLE USAGE PATTERNS
# ============================================================================

"""
Pattern 1: Simple State Creation
----------------------------------------
state = AgentState(messages=[])
# All travel fields optional, use defaults

Pattern 2: Full State with Travel Data
----------------------------------------
state = AgentState(
    messages=[Message(role="user", content="Plan my trip")],
    destination="Paris",
    start_date="2024-06-01",
    end_date="2024-06-10",
    budget=5000.0,
    duration=10,
    flights=[{"id": "FL1", "price": 500}],
    hotels=[{"id": "H1", "price": 100}],
    error_message=None,
    budget_feasible=True,
    budget_breakdown={"flights": 500, "hotels": 1000},
    selected_flight={"id": "FL1", "price": 500},
    selected_hotel={"id": "H1", "price": 100}
)

Pattern 3: Input Validation
----------------------------------------
# Validate user input first
user_input = TravelPlannerInput(
    destination="Paris",
    start_date="2024-06-01",
    end_date="2024-06-10",
    budget=5000.0,
    duration=10
)

# Then populate state from validated input
state = AgentState(
    messages=[],
    destination=user_input.destination,
    start_date=user_input.start_date,
    end_date=user_input.end_date,
    budget=user_input.budget,
    duration=user_input.duration,
)

Pattern 4: Workflow with Budget Tracking
----------------------------------------
# Start with input
input_data = TravelPlannerInput(
    destination="Tokyo",
    start_date="2024-07-01",
    end_date="2024-07-14",
    budget=4000.0,
    duration=14
)

# Create state
state = AgentState(
    messages=[],
    destination=input_data.destination,
    budget=input_data.budget,
    duration=input_data.duration,
)

# Add results
state.flights = [...]
state.hotels = [...]
state.activities = [...]

# Calculate budget
state.budget_breakdown = {
    "flights": 800,
    "hotels": 1400,
    "activities": 500,
}
total = sum(state.budget_breakdown.values())  # 2700
state.budget_feasible = total <= state.budget  # True if <= 4000

# Make selections
state.selected_flight = state.flights[0]
state.selected_hotel = state.hotels[0]

# Create final itinerary
state.itinerary = [
    {"day": 1, "activity": "Arrival"},
    {"day": 2, "activity": "Sightseeing"},
]
"""


# ============================================================================
# TYPE HINTS SUMMARY
# ============================================================================

"""
COMPLETE TYPE HINTS:

AgentState fields (NEW):
  destination: str | None
  start_date: str | None
  end_date: str | None
  budget: float
  duration: int
  flights: list[dict[str, Any]]
  hotels: list[dict[str, Any]]
  activities: list[dict[str, Any]]
  itinerary: list[dict[str, Any]]
  error_message: str | None
  budget_feasible: bool
  budget_breakdown: dict[str, float]
  selected_flight: dict[str, Any] | None
  selected_hotel: dict[str, Any] | None

TravelPlannerInput fields:
  destination: str
  start_date: str
  end_date: str
  budget: float
  duration: int
  user_preferences: dict[str, Any] | None
"""

