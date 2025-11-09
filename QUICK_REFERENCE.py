#!/usr/bin/env python3
"""
QUICK REFERENCE: Enhanced Travel Planner State
Fast lookup guide for common operations
"""

# ============================================================================
# 1. IMPORT THE MODELS
# ============================================================================

from src.agents.state import AgentState, TravelPlannerInput, Message
from pydantic import ValidationError

# ============================================================================
# 2. VALIDATE USER INPUT
# ============================================================================

def validate_trip_request(destination: str, start_date: str, end_date: str,
                         budget: float, duration: int):
    """Validate travel planner input."""
    try:
        user_input = TravelPlannerInput(
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            duration=duration,
        )
        return user_input, None
    except ValidationError as e:
        return None, str(e)


# Example:
# user_input, error = validate_trip_request(
#     "Paris", "2024-06-01", "2024-06-10", 5000.0, 10
# )
# if error:
#     print(f"Validation failed: {error}")


# ============================================================================
# 3. CREATE INITIAL STATE
# ============================================================================

def create_travel_state(user_input: TravelPlannerInput):
    """Create agent state from validated input."""
    state = AgentState(
        messages=[
            Message(
                role="user",
                content=f"Plan my trip to {user_input.destination}"
            )
        ],
        destination=user_input.destination,
        start_date=user_input.start_date,
        end_date=user_input.end_date,
        budget=user_input.budget,
        duration=user_input.duration,
    )
    return state


# Example:
# state = create_travel_state(user_input)


# ============================================================================
# 4. ADD TRAVEL OPTIONS
# ============================================================================

def add_flights_to_state(state: AgentState, flights: list[dict]):
    """Add available flights to state."""
    state.flights = flights
    return state


def add_hotels_to_state(state: AgentState, hotels: list[dict]):
    """Add available hotels to state."""
    state.hotels = hotels
    return state


def add_activities_to_state(state: AgentState, activities: list[dict]):
    """Add available activities to state."""
    state.activities = activities
    return state


# Example:
# state.flights = [
#     {"id": "FL1", "airline": "BA", "price": 500, "duration": "8h"},
#     {"id": "FL2", "airline": "AF", "price": 480, "duration": "9h"},
# ]
# state.hotels = [
#     {"id": "H1", "name": "Hotel A", "price": 100, "rating": 4.5},
#     {"id": "H2", "name": "Hotel B", "price": 120, "rating": 4.8},
# ]
# state.activities = [
#     {"id": "A1", "name": "Eiffel Tower", "price": 20},
#     {"id": "A2", "name": "Louvre Museum", "price": 25},
# ]


# ============================================================================
# 5. CALCULATE BUDGET
# ============================================================================

def calculate_budget_breakdown(state: AgentState) -> dict[str, float]:
    """Calculate costs by category."""
    breakdown = {}

    # Flight cost (cheapest option)
    if state.flights:
        breakdown["flights"] = min(f.get("price", 0) for f in state.flights)

    # Hotel cost (per night × duration)
    if state.hotels:
        cheapest_hotel = min(h.get("price", 0) for h in state.hotels)
        breakdown["hotels"] = cheapest_hotel * state.duration

    # Activities (sample)
    if state.activities:
        breakdown["activities"] = sum(
            a.get("price", 0) for a in state.activities[:5]
        )

    return breakdown


def check_budget_feasible(state: AgentState) -> tuple[bool, float, float]:
    """Check if trip is within budget.

    Returns:
        (is_feasible, total_cost, remaining_budget)
    """
    state.budget_breakdown = calculate_budget_breakdown(state)
    total_cost = sum(state.budget_breakdown.values())
    is_feasible = total_cost <= state.budget
    remaining = state.budget - total_cost

    state.budget_feasible = is_feasible

    return is_feasible, total_cost, remaining


# Example:
# is_feasible, total, remaining = check_budget_feasible(state)
# print(f"Budget feasible: {is_feasible}")
# print(f"Total cost: ${total:.2f}")
# print(f"Remaining budget: ${remaining:.2f}")
# print(f"Breakdown: {state.budget_breakdown}")


# ============================================================================
# 6. SELECT OPTIONS
# ============================================================================

def select_options(state: AgentState, flight_id: str, hotel_id: str):
    """Select flight and hotel from available options."""
    # Find and select flight
    flight = next((f for f in state.flights if f.get("id") == flight_id), None)
    if flight:
        state.selected_flight = flight
    else:
        raise ValueError(f"Flight {flight_id} not found")

    # Find and select hotel
    hotel = next((h for h in state.hotels if h.get("id") == hotel_id), None)
    if hotel:
        state.selected_hotel = hotel
    else:
        raise ValueError(f"Hotel {hotel_id} not found")

    return state


# Example:
# select_options(state, "FL1", "H1")
# print(f"Selected: {state.selected_flight['airline']} flight")
# print(f"Selected: {state.selected_hotel['name']} hotel")


# ============================================================================
# 7. BUILD ITINERARY
# ============================================================================

def build_itinerary(state: AgentState) -> list[dict]:
    """Build day-by-day itinerary."""
    itinerary = []

    # Day 1: Arrival
    itinerary.append({
        "day": 1,
        "activity": "Arrival",
        "location": state.destination,
        "cost": 0,
        "notes": f"Fly in on {state.selected_flight['airline']}"
    })

    # Days 2-N: Activities
    activities_per_day = state.activities / (state.duration - 1) if state.duration > 1 else 0
    for day in range(2, state.duration + 1):
        activity = state.activities[(day - 2) % len(state.activities)] if state.activities else {}
        itinerary.append({
            "day": day,
            "activity": activity.get("name", "Exploration"),
            "cost": activity.get("price", 0),
            "notes": f"Stay at {state.selected_hotel['name']}"
        })

    state.itinerary = itinerary
    return itinerary


# Example:
# itinerary = build_itinerary(state)
# for item in state.itinerary:
#     print(f"Day {item['day']}: {item['activity']} - ${item['cost']}")


# ============================================================================
# 8. ERROR HANDLING
# ============================================================================

def handle_planning_error(state: AgentState, error: str):
    """Handle planning errors gracefully."""
    state.error_message = error
    state.budget_feasible = False
    return state


# Example:
# if total_cost > state.budget:
#     handle_planning_error(
#         state,
#         f"Total cost ${total_cost} exceeds budget ${state.budget}"
#     )


# ============================================================================
# 9. COMPLETE WORKFLOW
# ============================================================================

def plan_trip_workflow(destination: str, start_date: str, end_date: str,
                      budget: float, duration: int):
    """Complete travel planning workflow."""

    # Step 1: Validate input
    print(f"✓ Step 1: Validating input...")
    user_input, error = validate_trip_request(
        destination, start_date, end_date, budget, duration
    )
    if error:
        print(f"✗ Validation failed: {error}")
        return None

    # Step 2: Create state
    print(f"✓ Step 2: Creating state...")
    state = create_travel_state(user_input)

    # Step 3: Fetch options (mock data)
    print(f"✓ Step 3: Fetching travel options...")
    state.flights = [
        {"id": "FL1", "airline": "BA", "price": 500},
        {"id": "FL2", "airline": "AF", "price": 480},
    ]
    state.hotels = [
        {"id": "H1", "name": "Hotel A", "price": 100, "rating": 4.5},
        {"id": "H2", "name": "Hotel B", "price": 120, "rating": 4.8},
    ]
    state.activities = [
        {"id": "A1", "name": "Main attraction", "price": 50},
        {"id": "A2", "name": "Secondary attraction", "price": 30},
    ]

    # Step 4: Check budget
    print(f"✓ Step 4: Checking budget...")
    is_feasible, total, remaining = check_budget_feasible(state)
    if not is_feasible:
        handle_planning_error(
            state,
            f"Total ${total:.2f} exceeds budget ${state.budget:.2f}"
        )
        print(f"✗ Trip exceeds budget!")
        return state

    # Step 5: Select options
    print(f"✓ Step 5: Selecting best options...")
    select_options(state, "FL2", "H1")  # Choose cheapest

    # Step 6: Build itinerary
    print(f"✓ Step 6: Building itinerary...")
    build_itinerary(state)

    # Step 7: Summary
    print(f"\n✓ Trip successfully planned!")
    print(f"  Destination: {state.destination}")
    print(f"  Duration: {state.duration} days")
    print(f"  Budget: ${state.budget:.2f}")
    print(f"  Total Cost: ${total:.2f}")
    print(f"  Remaining: ${remaining:.2f}")
    print(f"  Flight: {state.selected_flight['airline']}")
    print(f"  Hotel: {state.selected_hotel['name']}")

    return state


# ============================================================================
# 10. USAGE
# ============================================================================

if __name__ == "__main__":
    # Plan a trip
    state = plan_trip_workflow(
        destination="Paris",
        start_date="2024-06-01",
        end_date="2024-06-10",
        budget=5000.0,
        duration=10
    )

    if state and state.budget_feasible:
        print(f"\n📋 Itinerary:")
        for day in state.itinerary:
            print(f"  Day {day['day']}: {day['activity']}")

        print(f"\n💰 Budget Breakdown:")
        for category, cost in state.budget_breakdown.items():
            print(f"  {category.capitalize()}: ${cost:.2f}")

