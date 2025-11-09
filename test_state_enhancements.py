#!/usr/bin/env python3
"""Test suite for enhanced AgentState and TravelPlannerInput models.

This test suite verifies:
1. AgentState now includes travel planner-specific fields
2. TravelPlannerInput validates budget and duration correctly
3. Backward compatibility with existing AgentState usage
"""

import json
from datetime import datetime

import pytest
from pydantic import ValidationError

from src.agents.state import (
    AgentState,
    Message,
    MessageRole,
    AgentMetadata,
    TravelPlannerInput,
)


class TestAgentStateEnhancedFields:
    """Test enhanced AgentState with travel planner fields."""

    def test_agent_state_travel_planner_fields_exist(self):
        """Verify all new travel planner fields are present."""
        state = AgentState(
            messages=[],
            destination="Paris",
            start_date="2024-06-01",
            end_date="2024-06-10",
            budget=5000.0,
            duration=10,
            flights=[{"id": "FL1", "price": 500}],
            hotels=[{"id": "H1", "price": 100, "rating": 4.5}],
            activities=[{"id": "A1", "name": "Eiffel Tower", "price": 20}],
            itinerary=[{"day": 1, "activity": "Check-in"}],
            error_message=None,
            budget_feasible=True,
            budget_breakdown={"flights": 500, "hotels": 1000, "activities": 100},
            selected_flight={"id": "FL1", "price": 500},
            selected_hotel={"id": "H1", "price": 100},
        )

        assert state.destination == "Paris"
        assert state.start_date == "2024-06-01"
        assert state.end_date == "2024-06-10"
        assert state.budget == 5000.0
        assert state.duration == 10
        assert len(state.flights) == 1
        assert len(state.hotels) == 1
        assert len(state.activities) == 1
        assert len(state.itinerary) == 1
        assert state.error_message is None
        assert state.budget_feasible is True
        assert "flights" in state.budget_breakdown
        assert state.selected_flight is not None
        assert state.selected_hotel is not None

    def test_agent_state_default_values(self):
        """Verify default values for travel planner fields."""
        state = AgentState(messages=[])

        assert state.destination is None
        assert state.start_date is None
        assert state.end_date is None
        assert state.budget == 0.0
        assert state.duration == 0
        assert state.flights == []
        assert state.hotels == []
        assert state.activities == []
        assert state.itinerary == []
        assert state.error_message is None
        assert state.budget_feasible is False
        assert state.budget_breakdown == {}
        assert state.selected_flight is None
        assert state.selected_hotel is None

    def test_agent_state_type_hints_list_dict(self):
        """Verify type hints work correctly for List[Dict[str, Any]] structures."""
        flights = [
            {"id": "FL1", "airline": "BA", "price": 500, "duration": 8},
            {"id": "FL2", "airline": "AF", "price": 480, "duration": 9},
        ]
        hotels = [
            {"id": "H1", "name": "Hotel A", "price": 100, "rating": 4.5},
            {"id": "H2", "name": "Hotel B", "price": 150, "rating": 4.8},
        ]

        state = AgentState(
            messages=[],
            flights=flights,
            hotels=hotels,
        )

        assert len(state.flights) == 2
        assert state.flights[0]["id"] == "FL1"
        assert state.flights[1]["price"] == 480
        assert len(state.hotels) == 2
        assert state.hotels[0]["rating"] == 4.5

    def test_agent_state_backward_compatibility(self):
        """Verify existing AgentState functionality still works."""
        msg = Message(role="user", content="Plan my trip")
        metadata = AgentMetadata(agent_id="planner")

        state = AgentState(
            messages=[msg],
            context={"user_id": "123"},
            metadata=metadata,
            is_complete=False,
            iteration_count=1,
        )

        assert len(state.messages) == 1
        assert state.messages[0].content == "Plan my trip"
        assert state.context["user_id"] == "123"
        assert state.metadata.agent_id == "planner"
        assert state.is_complete is False
        assert state.iteration_count == 1

    def test_agent_state_budget_constraints(self):
        """Verify budget field accepts valid values."""
        state = AgentState(
            messages=[],
            budget=5000.0,
            duration=10,
        )

        assert state.budget == 5000.0
        assert state.duration == 10

    def test_agent_state_duration_constraints(self):
        """Verify duration field respects constraints (0-30)."""
        # Valid durations
        for duration in [0, 1, 15, 30]:
            state = AgentState(messages=[], duration=duration)
            assert state.duration == duration


class TestTravelPlannerInput:
    """Test TravelPlannerInput validation model."""

    def test_valid_travel_planner_input(self):
        """Verify TravelPlannerInput accepts valid input."""
        input_data = TravelPlannerInput(
            destination="Paris",
            start_date="2024-06-01",
            end_date="2024-06-10",
            budget=5000.0,
            duration=10,
        )

        assert input_data.destination == "Paris"
        assert input_data.start_date == "2024-06-01"
        assert input_data.end_date == "2024-06-10"
        assert input_data.budget == 5000.0
        assert input_data.duration == 10

    def test_travel_planner_input_with_preferences(self):
        """Verify TravelPlannerInput accepts user preferences."""
        input_data = TravelPlannerInput(
            destination="Tokyo",
            start_date="2024-07-01",
            end_date="2024-07-14",
            budget=3000.0,
            duration=14,
            user_preferences={
                "hotel_rating": 4,
                "flight_preference": "direct",
                "activities": ["museums", "temples"],
            },
        )

        assert input_data.user_preferences is not None
        assert input_data.user_preferences["hotel_rating"] == 4
        assert "museums" in input_data.user_preferences["activities"]

    def test_travel_planner_input_budget_validation(self):
        """Verify budget must be greater than 0."""
        # Valid budgets
        TravelPlannerInput(
            destination="Paris",
            start_date="2024-06-01",
            end_date="2024-06-10",
            budget=0.01,  # Smallest positive value
            duration=10,
        )

        # Invalid budgets
        with pytest.raises(ValidationError) as exc_info:
            TravelPlannerInput(
                destination="Paris",
                start_date="2024-06-01",
                end_date="2024-06-10",
                budget=0,  # Zero not allowed
                duration=10,
            )
        assert "greater than 0" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            TravelPlannerInput(
                destination="Paris",
                start_date="2024-06-01",
                end_date="2024-06-10",
                budget=-100,  # Negative not allowed
                duration=10,
            )
        assert "greater than 0" in str(exc_info.value)

    def test_travel_planner_input_duration_validation(self):
        """Verify duration must be between 1 and 30 days."""
        # Valid durations
        for duration in [1, 15, 30]:
            input_data = TravelPlannerInput(
                destination="Paris",
                start_date="2024-06-01",
                end_date="2024-06-10",
                budget=5000.0,
                duration=duration,
            )
            assert input_data.duration == duration

        # Invalid durations
        with pytest.raises(ValidationError) as exc_info:
            TravelPlannerInput(
                destination="Paris",
                start_date="2024-06-01",
                end_date="2024-06-10",
                budget=5000.0,
                duration=0,  # Too small
            )
        assert "between 1 and 30" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            TravelPlannerInput(
                destination="Paris",
                start_date="2024-06-01",
                end_date="2024-06-10",
                budget=5000.0,
                duration=31,  # Too large
            )
        assert "between 1 and 30" in str(exc_info.value)

    def test_travel_planner_input_required_fields(self):
        """Verify all required fields are enforced."""
        with pytest.raises(ValidationError):
            TravelPlannerInput(
                destination="",  # Empty
                start_date="2024-06-01",
                end_date="2024-06-10",
                budget=5000.0,
                duration=10,
            )

        with pytest.raises(ValidationError):
            TravelPlannerInput(
                destination="Paris",
                start_date="2024-06",  # Invalid format
                end_date="2024-06-10",
                budget=5000.0,
                duration=10,
            )

    def test_travel_planner_input_serialization(self):
        """Verify TravelPlannerInput can be serialized to JSON."""
        input_data = TravelPlannerInput(
            destination="Paris",
            start_date="2024-06-01",
            end_date="2024-06-10",
            budget=5000.0,
            duration=10,
            user_preferences={"hotel_rating": 4},
        )

        json_str = input_data.model_dump_json()
        parsed = json.loads(json_str)

        assert parsed["destination"] == "Paris"
        assert parsed["budget"] == 5000.0
        assert parsed["duration"] == 10
        assert parsed["user_preferences"]["hotel_rating"] == 4


class TestIntegration:
    """Integration tests for AgentState and TravelPlannerInput."""

    def test_populate_agent_state_from_travel_planner_input(self):
        """Verify data can flow from TravelPlannerInput to AgentState."""
        planner_input = TravelPlannerInput(
            destination="Paris",
            start_date="2024-06-01",
            end_date="2024-06-10",
            budget=5000.0,
            duration=10,
            user_preferences={"hotel_rating": 4},
        )

        # Create AgentState from TravelPlannerInput data
        state = AgentState(
            messages=[Message(role="user", content="Plan my trip to Paris")],
            destination=planner_input.destination,
            start_date=planner_input.start_date,
            end_date=planner_input.end_date,
            budget=planner_input.budget,
            duration=planner_input.duration,
        )

        assert state.destination == planner_input.destination
        assert state.budget == planner_input.budget
        assert state.duration == planner_input.duration

    def test_full_travel_planning_workflow(self):
        """Test a complete travel planning workflow."""
        # Step 1: Validate user input
        planner_input = TravelPlannerInput(
            destination="Tokyo",
            start_date="2024-07-01",
            end_date="2024-07-14",
            budget=4000.0,
            duration=14,
        )

        # Step 2: Create initial state
        state = AgentState(
            messages=[Message(role="user", content="Plan my trip")],
            destination=planner_input.destination,
            start_date=planner_input.start_date,
            end_date=planner_input.end_date,
            budget=planner_input.budget,
            duration=planner_input.duration,
        )

        # Step 3: Add flights
        state.flights = [
            {"id": "FL1", "airline": "JAL", "price": 800},
            {"id": "FL2", "airline": "ANA", "price": 750},
        ]

        # Step 4: Add hotels
        state.hotels = [
            {"id": "H1", "name": "Hotel A", "price": 100},
            {"id": "H2", "name": "Hotel B", "price": 120},
        ]

        # Step 5: Calculate budget breakdown
        state.budget_breakdown = {
            "flights": 800,
            "hotels": 100 * 14,
            "activities": 500,
        }
        total_cost = sum(state.budget_breakdown.values())
        state.budget_feasible = total_cost <= state.budget

        # Step 6: Select options
        state.selected_flight = state.flights[1]
        state.selected_hotel = state.hotels[0]

        # Step 7: Create itinerary
        state.itinerary = [
            {"day": 1, "activity": "Arrival", "cost": 0},
            {"day": 2, "activity": "Senso-ji Temple", "cost": 50},
        ]

        # Verify workflow
        assert state.destination == "Tokyo"
        assert state.budget_feasible is True
        assert state.selected_flight["airline"] == "ANA"
        assert state.selected_hotel["name"] == "Hotel A"
        assert len(state.itinerary) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

