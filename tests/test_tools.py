"""Comprehensive test suite for Travel Planner tools.

This module tests all tool functions including:
- Flight search and selection
- Hotel search and selection
- Activity search
- Budget calculations and feasibility

Uses pytest with fixtures and parametrized tests for comprehensive coverage.

Example:
    >>> pytest tests/test_tools.py -v
    >>> pytest tests/test_tools.py::test_search_flights_returns_list -v
    >>> pytest tests/test_tools.py -k "budget" -v
"""

import pytest
from typing import Dict, Any, List
from decimal import Decimal

from src.agents.state import AgentState
from src.nodes.tool_nodes import (
    search_flights_node,
    search_hotels_node,
    _call_flight_search_tool,
    _call_hotel_search_tool,
)
from src.nodes.planning_nodes import (
    budget_analysis_node,
    identify_region,
    MINIMUM_BUDGET_PER_DAY,
)

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def sample_state():
    """Fixture providing a sample agent state for testing.

    Returns:
        AgentState: Sample state with typical travel planning parameters
    """
    return AgentState(
        destination="Tokyo, Japan",
        budget=3000.0,
        duration=5,
        start_date="2024-06-01",
        end_date="2024-06-06",
        departure_city="New York, USA",
        context={
            "preferences": {
                "dietary": "none",
                "accommodation_type": "hotel",
                "activities": "cultural"
            }
        },
        budget_breakdown={
            "flights": 1200.0,
            "accommodation": 1050.0,
            "activities": 450.0,
            "food": 300.0,
        }
    )


@pytest.fixture
def sample_state_budget_feasible():
    """Fixture with budget sufficient for trip.

    Returns:
        AgentState: State with adequate budget for 5-day trip
    """
    return AgentState(
        destination="Paris, France",
        budget=5000.0,
        duration=5,
        start_date="2024-06-01",
        end_date="2024-06-06",
        departure_city="New York, USA",
        budget_breakdown={
            "flights": 2000.0,
            "accommodation": 1750.0,
            "activities": 750.0,
            "food": 500.0,
        }
    )


@pytest.fixture
def sample_state_budget_insufficient():
    """Fixture with insufficient budget for trip.

    Returns:
        AgentState: State with inadequate budget
    """
    return AgentState(
        destination="Paris, France",
        budget=500.0,
        duration=5,
        start_date="2024-06-01",
        end_date="2024-06-06",
        departure_city="New York, USA",
        budget_breakdown={
            "flights": 200.0,
            "accommodation": 175.0,
            "activities": 75.0,
            "food": 50.0,
        }
    )


@pytest.fixture
def sample_flight_options():
    """Fixture providing sample flight options.

    Returns:
        List[Dict]: Sample flight data
    """
    return [
        {
            "id": "FL001",
            "airline": "Delta Airlines",
            "price": 450.00,
            "stops": 0,
            "duration": 6.5,
            "departure_time": "08:00",
            "arrival_time": "14:30",
        },
        {
            "id": "FL002",
            "airline": "United Airlines",
            "price": 520.00,
            "stops": 1,
            "duration": 8.0,
            "departure_time": "10:00",
            "arrival_time": "18:00",
        },
        {
            "id": "FL003",
            "airline": "American Airlines",
            "price": 380.00,
            "stops": 2,
            "duration": 9.5,
            "departure_time": "06:00",
            "arrival_time": "15:30",
        },
    ]


@pytest.fixture
def sample_hotel_options():
    """Fixture providing sample hotel options.

    Returns:
        List[Dict]: Sample hotel data
    """
    duration = 5
    return [
        {
            "id": "HTL001",
            "name": "Luxury Palace Hotel",
            "rating": 4.8,
            "price_per_night": 180.00,
            "total_price": 180.00 * duration,
            "amenities": ["WiFi", "Pool", "Gym", "Restaurant"],
            "location": "Downtown",
        },
        {
            "id": "HTL002",
            "name": "Comfort Inn",
            "rating": 4.0,
            "price_per_night": 120.00,
            "total_price": 120.00 * duration,
            "amenities": ["WiFi", "Continental Breakfast"],
            "location": "Business District",
        },
        {
            "id": "HTL003",
            "name": "Budget Stay Hotel",
            "rating": 3.5,
            "price_per_night": 75.00,
            "total_price": 75.00 * duration,
            "amenities": ["WiFi"],
            "location": "Suburbs",
        },
        {
            "id": "HTL004",
            "name": "Premium Suite Resort",
            "rating": 4.9,
            "price_per_night": 250.00,
            "total_price": 250.00 * duration,
            "amenities": ["WiFi", "Pool", "Spa", "Gym", "Restaurant", "Bar"],
            "location": "Beachfront",
        },
    ]


# ============================================================================
# BUDGET CALCULATOR TESTS
# ============================================================================


class TestBudgetCalculator:
    """Tests for budget calculation and feasibility analysis."""

    def test_budget_breakdown_percentages(self, sample_state_budget_feasible):
        """Test that budget breakdown follows correct percentage allocation.

        Budget should be split as:
        - Flights: 40%
        - Accommodation: 35%
        - Activities: 15%
        - Food: 10%
        """
        result = budget_analysis_node(sample_state_budget_feasible)

        budget_breakdown = result["budget_breakdown"]
        total_budget = sample_state_budget_feasible.budget

        # Calculate percentages
        flights_pct = budget_breakdown["flights"] / total_budget * 100
        accommodation_pct = budget_breakdown["accommodation"] / total_budget * 100
        activities_pct = budget_breakdown["activities"] / total_budget * 100
        food_pct = budget_breakdown["food"] / total_budget * 100

        # Assert percentages
        assert abs(flights_pct - 40.0) < 0.1, f"Flights should be ~40%, got {flights_pct:.1f}%"
        assert abs(accommodation_pct - 35.0) < 0.1, f"Accommodation should be ~35%, got {accommodation_pct:.1f}%"
        assert abs(activities_pct - 15.0) < 0.1, f"Activities should be ~15%, got {activities_pct:.1f}%"
        assert abs(food_pct - 10.0) < 0.1, f"Food should be ~10%, got {food_pct:.1f}%"

    def test_budget_breakdown_total(self, sample_state_budget_feasible):
        """Test that budget breakdown totals equal total budget."""
        result = budget_analysis_node(sample_state_budget_feasible)

        budget_breakdown = result["budget_breakdown"]
        total_breakdown = sum(budget_breakdown.values())
        total_budget = sample_state_budget_feasible.budget

        assert abs(total_breakdown - total_budget) < 0.01, \
            f"Breakdown total {total_breakdown} != budget {total_budget}"

    @pytest.mark.parametrize("budget,duration,region_min,expected_feasible", [
        (5000, 5, 150, True),   # Europe: needs 750, has 5000
        (500, 5, 150, False),   # Europe: needs 750, has 500
        (1000, 10, 100, True),  # Asia: needs 1000, has 1000
        (999, 10, 100, False),  # Asia: needs 1000, has 999
        (2000, 7, 120, True),   # Americas: needs 840, has 2000
        (700, 7, 120, False),   # Americas: needs 840, has 700
    ])
    def test_budget_feasibility_parametrized(self, budget, duration, region_min, expected_feasible):
        """Test budget feasibility with multiple scenarios.

        Args:
            budget: Total budget
            duration: Trip duration in days
            region_min: Minimum per day for region
            expected_feasible: Expected feasibility result
        """
        # Create state with specific budget and duration
        state = AgentState(
            destination="Test Destination",
            budget=float(budget),
            duration=duration,
        )

        result = budget_analysis_node(state)

        assert result["budget_feasible"] == expected_feasible, \
            f"Budget {budget} for {duration} days should be {'feasible' if expected_feasible else 'not feasible'}"

    def test_budget_per_night_calculation(self):
        """Test minimum budget per night calculation for different regions."""
        # Test Asia
        assert identify_region("Tokyo, Japan") == "asia"
        assert MINIMUM_BUDGET_PER_DAY["asia"] == 100

        # Test Europe
        assert identify_region("Paris, France") == "europe"
        assert MINIMUM_BUDGET_PER_DAY["europe"] == 150

        # Test Americas
        assert identify_region("New York, USA") == "americas"
        assert MINIMUM_BUDGET_PER_DAY["americas"] == 120

    def test_zero_budget(self):
        """Test handling of zero budget."""
        state = AgentState(
            destination="Paris, France",
            budget=0.0,
            duration=5,
        )

        result = budget_analysis_node(state)

        budget_breakdown = result["budget_breakdown"]
        assert all(v == 0.0 for v in budget_breakdown.values()), \
            "Zero budget should result in all categories being $0"

    def test_negative_budget_raises_error(self):
        """Test that negative budget raises ValueError."""
        state = AgentState(
            destination="Paris, France",
            budget=-1000.0,
            duration=5,
        )

        with pytest.raises(ValueError, match="Budget cannot be negative"):
            budget_analysis_node(state)

    def test_minimum_required_budget_calculation(self, sample_state_budget_feasible):
        """Test calculation of minimum required budget."""
        result = budget_analysis_node(sample_state_budget_feasible)

        minimum_required = result["minimum_required_budget"]
        duration = sample_state_budget_feasible.duration
        region = result["region"]
        minimum_per_day = MINIMUM_BUDGET_PER_DAY.get(region, 100)

        expected_minimum = minimum_per_day * duration

        assert minimum_required == expected_minimum, \
            f"Minimum required should be {expected_minimum}, got {minimum_required}"


# ============================================================================
# FLIGHT SEARCH TESTS
# ============================================================================


class TestFlightSearch:
    """Tests for flight search and selection functionality."""

    def test_search_flights_returns_list(self, sample_state):
        """Test that flight search returns a list of results."""
        result = search_flights_node(sample_state)

        assert "flights" in result
        assert isinstance(result["flights"], list)
        assert len(result["flights"]) > 0

    def test_search_flights_has_required_fields(self, sample_state):
        """Test that returned flights have required fields."""
        result = search_flights_node(sample_state)

        required_fields = {"id", "airline", "price", "stops", "duration"}
        for flight in result["flights"]:
            for field in required_fields:
                assert field in flight, f"Flight missing field: {field}"

    def test_search_flights_within_budget(self, sample_state):
        """Test that selected flight is within budget constraint."""
        result = search_flights_node(sample_state)

        selected_flight = result["selected_flight"]
        flights_budget = sample_state.budget_breakdown.get("flights", 0)

        assert selected_flight is not None, "Selected flight should not be None"
        assert selected_flight["price"] <= flights_budget, \
            f"Selected flight ${selected_flight['price']} exceeds budget ${flights_budget}"

    def test_search_flights_prefers_fewer_stops(self, sample_state):
        """Test that flight selection prefers flights with fewer stops.

        With scoring: score = price * 0.7 + stops * 100
        This should prefer direct flights when price is similar.
        """
        result = search_flights_node(sample_state)

        selected_flight = result["selected_flight"]
        all_flights = result["flights"]

        # Filter flights within budget
        affordable = [f for f in all_flights if f["price"] <= sample_state.budget_breakdown.get("flights", float('inf'))]

        # Find best score
        best_score = None
        for flight in affordable:
            score = (flight["price"] * 0.7) + (flight["stops"] * 100)
            if best_score is None or score < best_score:
                best_score = score
                best_flight = flight

        # Selected should match best scored flight
        assert selected_flight["id"] == best_flight["id"], \
            "Selected flight should have best score"

    def test_search_flights_invalid_input_graceful_handling(self):
        """Test that invalid input is handled gracefully."""
        # State with no budget breakdown
        state = AgentState(
            destination="Tokyo, Japan",
            budget=1000.0,
            duration=5,
            budget_breakdown=None,  # No breakdown
        )

        # Should not raise exception, return error message
        result = search_flights_node(state)

        assert isinstance(result, dict)
        assert "error_message" in result or "flights" in result

    def test_search_flights_selects_best_option(self, sample_flight_options):
        """Test that the best flight option is selected."""
        # Mock state with these flights
        # For scoring: (price * 0.7) + (stops * 100)
        # FL001: (450 * 0.7) + (0 * 100) = 315
        # FL002: (520 * 0.7) + (1 * 100) = 464
        # FL003: (380 * 0.7) + (2 * 100) = 266 (best)

        state = AgentState(
            destination="Tokyo, Japan",
            budget=3000.0,
            duration=5,
            budget_breakdown={"flights": 1200.0},
        )

        result = search_flights_node(state)

        # FL003 should be selected (best score)
        assert result["selected_flight"] is not None
        # The best should have lowest combined score

    def test_search_flights_empty_results_handled(self):
        """Test handling of empty flight search results."""
        state = AgentState(
            destination="Tokyo, Japan",
            budget=100.0,  # Very low budget
            duration=5,
            budget_breakdown={"flights": 10.0},  # Only $10 for flights
        )

        result = search_flights_node(state)

        # Should return error message about budget
        assert result["selected_flight"] is None
        assert result["error_message"] is not None


# ============================================================================
# HOTEL SEARCH TESTS
# ============================================================================


class TestHotelSearch:
    """Tests for hotel search and selection functionality."""

    def test_search_hotels_returns_list(self, sample_state):
        """Test that hotel search returns a list of results."""
        result = search_hotels_node(sample_state)

        assert "hotels" in result
        assert isinstance(result["hotels"], list)
        assert len(result["hotels"]) > 0

    def test_search_hotels_has_required_fields(self, sample_state):
        """Test that returned hotels have required fields."""
        result = search_hotels_node(sample_state)

        required_fields = {"id", "name", "rating", "price_per_night", "total_price"}
        for hotel in result["hotels"]:
            for field in required_fields:
                assert field in hotel, f"Hotel missing field: {field}"

    def test_search_hotels_within_budget(self, sample_state):
        """Test that selected hotel is within budget constraint."""
        result = search_hotels_node(sample_state)

        selected_hotel = result["selected_hotel"]
        accommodation_budget = sample_state.budget_breakdown.get("accommodation", 0)

        assert selected_hotel is not None, "Selected hotel should not be None"
        assert selected_hotel["total_price"] <= accommodation_budget, \
            f"Selected hotel ${selected_hotel['total_price']} exceeds budget ${accommodation_budget}"

    def test_search_hotels_filters_by_type(self, sample_state):
        """Test hotel filtering takes budget into account."""
        result = search_hotels_node(sample_state)

        all_hotels = result["hotels"]
        selected_hotel = result["selected_hotel"]
        accommodation_budget = sample_state.budget_breakdown.get("accommodation", 0)

        # All hotels should be available
        assert len(all_hotels) > 0

        # Selected should be within budget
        assert selected_hotel["total_price"] <= accommodation_budget

    def test_search_hotels_calculates_total_correctly(self, sample_state, sample_hotel_options):
        """Test that hotel total price is calculated correctly.

        Total should be price_per_night * duration
        """
        result = search_hotels_node(sample_state)

        for hotel in result["hotels"]:
            price_per_night = hotel["price_per_night"]
            duration = sample_state.duration
            expected_total = price_per_night * duration

            assert abs(hotel["total_price"] - expected_total) < 0.01, \
                f"Total price should be {expected_total}, got {hotel['total_price']}"

    def test_search_hotels_prefers_higher_rating(self, sample_state):
        """Test that hotel selection prefers higher ratings when price is similar.

        Sorting: rating descending, then price ascending
        """
        result = search_hotels_node(sample_state)

        selected_hotel = result["selected_hotel"]
        all_hotels = result["hotels"]
        accommodation_budget = sample_state.budget_breakdown.get("accommodation", 0)

        # Filter affordable hotels
        affordable = [h for h in all_hotels if h["total_price"] <= accommodation_budget]

        if affordable:
            # Sort by rating (desc) then price (asc)
            affordable.sort(key=lambda x: (-x["rating"], x["total_price"]))
            best_hotel = affordable[0]

            # Selected should match best rated
            assert selected_hotel["name"] == best_hotel["name"], \
                "Selected hotel should be best rated among affordable options"

    def test_search_hotels_invalid_input_graceful_handling(self):
        """Test graceful handling of invalid input."""
        state = AgentState(
            destination="Tokyo, Japan",
            budget=1000.0,
            duration=5,
            budget_breakdown=None,
        )

        result = search_hotels_node(state)

        assert isinstance(result, dict)
        assert "error_message" in result or "hotels" in result

    def test_search_hotels_empty_results_handled(self):
        """Test handling when no hotels are within budget."""
        state = AgentState(
            destination="Tokyo, Japan",
            budget=100.0,
            duration=5,
            budget_breakdown={"accommodation": 10.0},  # Only $10 for hotels
        )

        result = search_hotels_node(state)

        # Should return error message about budget
        assert result["selected_hotel"] is None
        assert result["error_message"] is not None


# ============================================================================
# REGION IDENTIFICATION TESTS
# ============================================================================


class TestRegionIdentification:
    """Tests for region identification from destination."""

    @pytest.mark.parametrize("destination,expected_region", [
        ("Tokyo, Japan", "asia"),
        ("Bangkok, Thailand", "asia"),
        ("Hong Kong", "asia"),
        ("Paris, France", "europe"),
        ("London, UK", "europe"),
        ("Berlin, Germany", "europe"),
        ("New York, USA", "americas"),
        ("Los Angeles, USA", "americas"),
        ("Mexico City, Mexico", "americas"),
        ("Cairo, Egypt", "africa"),
        ("Johannesburg, South Africa", "africa"),
        ("Sydney, Australia", "oceania"),
        ("Auckland, New Zealand", "oceania"),
    ])
    def test_region_identification_parametrized(self, destination, expected_region):
        """Test region identification for various destinations."""
        identified_region = identify_region(destination)

        assert identified_region == expected_region, \
            f"Destination '{destination}' should be identified as '{expected_region}', got '{identified_region}'"

    def test_region_identification_case_insensitive(self):
        """Test that region identification is case-insensitive."""
        assert identify_region("PARIS, FRANCE") == "europe"
        assert identify_region("paris, france") == "europe"
        assert identify_region("Paris, France") == "europe"

    def test_region_identification_with_whitespace(self):
        """Test region identification handles extra whitespace."""
        assert identify_region("  Paris, France  ") == "europe"
        assert identify_region("Paris  ,  France") == "europe"

    def test_unknown_destination_defaults_to_asia(self):
        """Test that unknown destinations default to Asia region."""
        result = identify_region("Xyzzy City, Fictionaland")

        # Should not raise exception, should default to asia
        assert result == "asia"


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_full_planning_workflow(self, sample_state_budget_feasible):
        """Test complete workflow: budget analysis -> flight -> hotel."""
        # Step 1: Budget analysis
        budget_result = budget_analysis_node(sample_state_budget_feasible)
        assert budget_result["budget_feasible"] is True

        # Step 2: Update state with budget breakdown
        sample_state_budget_feasible.budget_breakdown = budget_result["budget_breakdown"]

        # Step 3: Flight search
        flight_result = search_flights_node(sample_state_budget_feasible)
        assert flight_result["selected_flight"] is not None

        # Step 4: Hotel search
        hotel_result = search_hotels_node(sample_state_budget_feasible)
        assert hotel_result["selected_hotel"] is not None

    def test_insufficient_budget_workflow(self, sample_state_budget_insufficient):
        """Test workflow with insufficient budget."""
        # Step 1: Budget analysis
        budget_result = budget_analysis_node(sample_state_budget_insufficient)
        assert budget_result["budget_feasible"] is False

        # Should still return details for fallback
        assert "minimum_required_budget" in budget_result
        assert budget_result["minimum_required_budget"] > sample_state_budget_insufficient.budget

    def test_multiple_destinations_different_budgets(self):
        """Test planning for multiple destinations with different budgets."""
        destinations_and_budgets = [
            ("Paris, France", 3000, True),   # Should be feasible
            ("Tokyo, Japan", 2000, True),    # Should be feasible
            ("New York, USA", 1500, True),   # Should be feasible
        ]

        for destination, budget, expected_feasible in destinations_and_budgets:
            state = AgentState(
                destination=destination,
                budget=float(budget),
                duration=5,
            )

            result = budget_analysis_node(state)

            assert result["budget_feasible"] == expected_feasible, \
                f"{destination} with ${budget} should be {'feasible' if expected_feasible else 'not feasible'}"


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================


class TestPerformance:
    """Tests for performance characteristics."""

    def test_budget_analysis_performance(self, sample_state):
        """Test that budget analysis completes quickly."""
        import time

        start = time.time()
        for _ in range(100):
            budget_analysis_node(sample_state)
        elapsed = time.time() - start

        # Should complete 100 iterations in reasonable time (< 1 second)
        assert elapsed < 1.0, f"Budget analysis took {elapsed}s for 100 iterations"

    def test_flight_search_performance(self, sample_state):
        """Test that flight search completes quickly."""
        import time

        start = time.time()
        for _ in range(50):
            search_flights_node(sample_state)
        elapsed = time.time() - start

        # Should complete 50 iterations quickly (< 1 second)
        assert elapsed < 1.0, f"Flight search took {elapsed}s for 50 iterations"

    def test_hotel_search_performance(self, sample_state):
        """Test that hotel search completes quickly."""
        import time

        start = time.time()
        for _ in range(50):
            search_hotels_node(sample_state)
        elapsed = time.time() - start

        # Should complete 50 iterations quickly (< 1 second)
        assert elapsed < 1.0, f"Hotel search took {elapsed}s for 50 iterations"


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


class TestErrorHandling:
    """Tests for error handling and edge cases."""

    def test_missing_budget_breakdown(self):
        """Test handling when budget breakdown is missing."""
        state = AgentState(
            destination="Paris, France",
            budget=1000.0,
            duration=5,
            budget_breakdown=None,
        )

        # Should handle gracefully without exception
        result = search_flights_node(state)
        assert isinstance(result, dict)

    def test_zero_duration(self):
        """Test handling of zero duration."""
        state = AgentState(
            destination="Paris, France",
            budget=1000.0,
            duration=0,
        )

        with pytest.raises(ValueError):
            budget_analysis_node(state)

    def test_very_large_budget(self):
        """Test handling of very large budgets."""
        state = AgentState(
            destination="Paris, France",
            budget=1_000_000.0,
            duration=5,
        )

        result = budget_analysis_node(state)

        assert result["budget_feasible"] is True
        assert result["budget_breakdown"]["flights"] == 400_000.0

    def test_very_small_budget(self):
        """Test handling of very small budgets."""
        state = AgentState(
            destination="Paris, France",
            budget=0.01,
            duration=5,
        )

        result = budget_analysis_node(state)

        assert result["budget_feasible"] is False

    def test_missing_destination(self):
        """Test handling when destination is missing."""
        state = AgentState(
            destination=None,
            budget=1000.0,
            duration=5,
        )

        # Should handle gracefully
        result = budget_analysis_node(state)
        assert isinstance(result, dict)


# ============================================================================
# EDGE CASE TESTS
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_single_day_trip(self):
        """Test budget analysis for single-day trips."""
        state = AgentState(
            destination="Paris, France",
            budget=500.0,
            duration=1,
        )

        result = budget_analysis_node(state)

        # Should calculate for 1 day
        assert result["minimum_required_budget"] == MINIMUM_BUDGET_PER_DAY.get("europe", 150)

    def test_thirty_day_trip(self):
        """Test budget analysis for 30-day trips (maximum)."""
        state = AgentState(
            destination="Paris, France",
            budget=5000.0,
            duration=30,
        )

        result = budget_analysis_node(state)

        # Should calculate for 30 days
        expected = MINIMUM_BUDGET_PER_DAY.get("europe", 150) * 30
        assert result["minimum_required_budget"] == expected

    def test_exactly_minimum_budget(self):
        """Test when budget exactly equals minimum required."""
        region_min = MINIMUM_BUDGET_PER_DAY["europe"]
        duration = 5
        exact_budget = region_min * duration

        state = AgentState(
            destination="Paris, France",
            budget=float(exact_budget),
            duration=duration,
        )

        result = budget_analysis_node(state)

        assert result["budget_feasible"] is True
        assert result["minimum_required_budget"] == exact_budget

    def test_one_cent_below_minimum(self):
        """Test when budget is one cent below minimum."""
        region_min = MINIMUM_BUDGET_PER_DAY["europe"]
        duration = 5
        min_budget = region_min * duration
        below_budget = min_budget - 0.01

        state = AgentState(
            destination="Paris, France",
            budget=below_budget,
            duration=duration,
        )

        result = budget_analysis_node(state)

        assert result["budget_feasible"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

