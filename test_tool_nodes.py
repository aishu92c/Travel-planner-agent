"""Test suite for tool nodes (flight and hotel search and selection).

Tests the search_flights_node and search_hotels_node functions with various
scenarios including budget constraints, filtering, sorting, and selection logic.
"""

import pytest
from src.agents.state import AgentState
from src.nodes.tool_nodes import search_flights_node, search_hotels_node


class TestSearchFlightsNode:
    """Test flight search and selection node."""

    def test_flights_search_successful(self):
        """Test successful flight search with valid parameters."""
        state = AgentState(
            destination="Paris",
            start_date="2024-06-01",
            end_date="2024-06-10",
            budget=3000.0,
            duration=10,
            budget_breakdown={
                "flights": 1200.0,
                "accommodation": 1050.0,
                "activities": 450.0,
                "food": 300.0,
            }
        )

        result = search_flights_node(state)

        assert result is not None
        assert "flights" in result
        assert "selected_flight" in result
        assert "error_message" in result
        assert len(result["flights"]) > 0
        assert result["selected_flight"] is not None
        assert result["error_message"] is None

    def test_flights_filtering_by_budget(self):
        """Test that flights are filtered by budget constraint."""
        state = AgentState(
            destination="Paris",
            start_date="2024-06-01",
            end_date="2024-06-10",
            budget=400.0,  # Low budget
            duration=10,
            budget_breakdown={
                "flights": 300.0,  # Only $300 for flights
                "accommodation": 50.0,
                "activities": 30.0,
                "food": 20.0,
            }
        )

        result = search_flights_node(state)

        # Should find some flights within budget
        if result["selected_flight"]:
            assert result["selected_flight"]["price"] <= 300.0
        else:
            # Should have error message if no flights within budget
            assert result["error_message"] is not None

    def test_flights_selection_prefers_cheaper_fewer_stops(self):
        """Test that selected flight prefers cheaper options with fewer stops."""
        state = AgentState(
            destination="Paris",
            start_date="2024-06-01",
            end_date="2024-06-10",
            budget=3000.0,
            duration=10,
            budget_breakdown={
                "flights": 1200.0,
                "accommodation": 1050.0,
                "activities": 450.0,
                "food": 300.0,
            }
        )

        result = search_flights_node(state)

        if result["selected_flight"]:
            selected = result["selected_flight"]
            # Calculate score for selected flight
            selected_score = (selected["price"] * 0.7) + (selected["stops"] * 100)

            # Verify selected flight is affordable
            assert selected["price"] <= 1200.0

            # Verify it's the best option (check against all flights)
            for flight in result["flights"]:
                if flight["price"] <= 1200.0:
                    flight_score = (flight["price"] * 0.7) + (flight["stops"] * 100)
                    # Selected should have lowest score
                    assert selected_score <= flight_score + 0.01  # Allow for floating point

    def test_flights_insufficient_budget_error(self):
        """Test error handling when budget is too low."""
        state = AgentState(
            destination="Paris",
            start_date="2024-06-01",
            end_date="2024-06-10",
            budget=100.0,  # Very low budget
            duration=10,
            budget_breakdown={
                "flights": 50.0,  # Only $50 for flights
                "accommodation": 30.0,
                "activities": 10.0,
                "food": 10.0,
            }
        )

        result = search_flights_node(state)

        # Should have error since budget is too low
        assert result["selected_flight"] is None
        assert result["error_message"] is not None
        assert "No flights within budget" in result["error_message"]

    def test_flights_missing_budget_breakdown(self):
        """Test flight search with missing budget breakdown."""
        state = AgentState(
            destination="Paris",
            start_date="2024-06-01",
            end_date="2024-06-10",
            budget=3000.0,
            duration=10,
            budget_breakdown={}  # Empty breakdown
        )

        result = search_flights_node(state)

        # Should handle missing budget breakdown gracefully
        assert "flights" in result
        assert "error_message" in result

    def test_flights_return_all_options(self):
        """Test that all flight options are returned in results."""
        state = AgentState(
            destination="Paris",
            start_date="2024-06-01",
            end_date="2024-06-10",
            budget=3000.0,
            duration=10,
            budget_breakdown={
                "flights": 1200.0,
                "accommodation": 1050.0,
                "activities": 450.0,
                "food": 300.0,
            }
        )

        result = search_flights_node(state)

        # Should return all flight options
        assert len(result["flights"]) > 0

        # Should have required fields
        for flight in result["flights"]:
            assert "price" in flight
            assert "stops" in flight
            assert "airline" in flight


class TestSearchHotelsNode:
    """Test hotel search and selection node."""

    def test_hotels_search_successful(self):
        """Test successful hotel search with valid parameters."""
        state = AgentState(
            destination="Paris",
            start_date="2024-06-01",
            end_date="2024-06-10",
            budget=3000.0,
            duration=10,
            budget_breakdown={
                "flights": 1200.0,
                "accommodation": 1050.0,
                "activities": 450.0,
                "food": 300.0,
            }
        )

        result = search_hotels_node(state)

        assert result is not None
        assert "hotels" in result
        assert "selected_hotel" in result
        assert "error_message" in result
        assert len(result["hotels"]) > 0
        assert result["selected_hotel"] is not None
        assert result["error_message"] is None

    def test_hotels_filtering_by_budget(self):
        """Test that hotels are filtered by budget constraint."""
        state = AgentState(
            destination="Paris",
            start_date="2024-06-01",
            end_date="2024-06-10",
            budget=1000.0,
            duration=10,
            budget_breakdown={
                "flights": 400.0,
                "accommodation": 300.0,  # Only $300 for hotels (10 nights)
                "activities": 150.0,
                "food": 150.0,
            }
        )

        result = search_hotels_node(state)

        # Should find hotels or have error if none within budget
        if result["selected_hotel"]:
            assert result["selected_hotel"]["total_price"] <= 300.0
        else:
            assert result["error_message"] is not None

    def test_hotels_selection_prefers_rating_then_price(self):
        """Test that selected hotel prefers higher rating, then lower price."""
        state = AgentState(
            destination="Paris",
            start_date="2024-06-01",
            end_date="2024-06-10",
            budget=3000.0,
            duration=10,
            budget_breakdown={
                "flights": 1200.0,
                "accommodation": 1050.0,
                "activities": 450.0,
                "food": 300.0,
            }
        )

        result = search_hotels_node(state)

        if result["selected_hotel"]:
            selected = result["selected_hotel"]
            # Calculate score for selected hotel
            selected_score = (selected["rating"] * -100) + selected["price_per_night"]

            # Verify selected hotel is affordable
            assert selected["total_price"] <= 1050.0

            # Verify it's the best option (check against all hotels)
            for hotel in result["hotels"]:
                if hotel["total_price"] <= 1050.0:
                    hotel_score = (hotel["rating"] * -100) + hotel["price_per_night"]
                    # Selected should have lowest score
                    assert selected_score <= hotel_score + 0.01  # Allow for floating point

    def test_hotels_insufficient_budget_error(self):
        """Test error handling when budget is too low."""
        state = AgentState(
            destination="Paris",
            start_date="2024-06-01",
            end_date="2024-06-10",
            budget=500.0,
            duration=10,
            budget_breakdown={
                "flights": 300.0,
                "accommodation": 100.0,  # Only $100 for 10 nights = $10/night
                "activities": 50.0,
                "food": 50.0,
            }
        )

        result = search_hotels_node(state)

        # Should have error since budget is too low
        assert result["selected_hotel"] is None
        assert result["error_message"] is not None
        assert "No hotels within budget" in result["error_message"]

    def test_hotels_return_all_options(self):
        """Test that all hotel options are returned in results."""
        state = AgentState(
            destination="Paris",
            start_date="2024-06-01",
            end_date="2024-06-10",
            budget=3000.0,
            duration=10,
            budget_breakdown={
                "flights": 1200.0,
                "accommodation": 1050.0,
                "activities": 450.0,
                "food": 300.0,
            }
        )

        result = search_hotels_node(state)

        # Should return all hotel options
        assert len(result["hotels"]) > 0

        # Should have required fields
        for hotel in result["hotels"]:
            assert "price_per_night" in hotel
            assert "rating" in hotel
            assert "name" in hotel
            assert "total_price" in hotel

    def test_hotels_duration_calculation(self):
        """Test that total price is correctly calculated for duration."""
        state = AgentState(
            destination="Paris",
            start_date="2024-06-01",
            end_date="2024-06-15",
            budget=3000.0,
            duration=14,  # 14 nights
            budget_breakdown={
                "flights": 1200.0,
                "accommodation": 1050.0,
                "activities": 450.0,
                "food": 300.0,
            }
        )

        result = search_hotels_node(state)

        # Verify total price calculations
        for hotel in result["hotels"]:
            expected_total = hotel["price_per_night"] * 14
            assert hotel["total_price"] == expected_total


class TestErrorHandling:
    """Test error handling in search nodes."""

    def test_flights_error_with_exception(self):
        """Test that flights node handles exceptions gracefully."""
        # Create state with invalid values that might cause issues
        state = AgentState(
            destination=None,
            start_date=None,
            end_date=None,
            budget=0.0,
            duration=0,
            budget_breakdown=None,
        )

        result = search_flights_node(state)

        # Should still return valid result structure even with error
        assert "flights" in result
        assert "error_message" in result
        assert "selected_flight" in result

    def test_hotels_error_with_exception(self):
        """Test that hotels node handles exceptions gracefully."""
        # Create state with invalid values that might cause issues
        state = AgentState(
            destination=None,
            start_date=None,
            end_date=None,
            budget=0.0,
            duration=0,
            budget_breakdown=None,
        )

        result = search_hotels_node(state)

        # Should still return valid result structure even with error
        assert "hotels" in result
        assert "error_message" in result
        assert "selected_hotel" in result


class TestResultStructure:
    """Test that results have correct structure."""

    def test_flights_result_structure(self):
        """Test flight result has all required fields."""
        state = AgentState(
            destination="Paris",
            start_date="2024-06-01",
            end_date="2024-06-10",
            budget=3000.0,
            duration=10,
            budget_breakdown={
                "flights": 1200.0,
                "accommodation": 1050.0,
                "activities": 450.0,
                "food": 300.0,
            }
        )

        result = search_flights_node(state)

        # Check all required keys
        required_keys = {"flights", "selected_flight", "error_message"}
        assert all(key in result for key in required_keys)

        # Check types
        assert isinstance(result["flights"], list)
        assert result["selected_flight"] is None or isinstance(result["selected_flight"], dict)
        assert result["error_message"] is None or isinstance(result["error_message"], str)

    def test_hotels_result_structure(self):
        """Test hotel result has all required fields."""
        state = AgentState(
            destination="Paris",
            start_date="2024-06-01",
            end_date="2024-06-10",
            budget=3000.0,
            duration=10,
            budget_breakdown={
                "flights": 1200.0,
                "accommodation": 1050.0,
                "activities": 450.0,
                "food": 300.0,
            }
        )

        result = search_hotels_node(state)

        # Check all required keys
        required_keys = {"hotels", "selected_hotel", "error_message"}
        assert all(key in result for key in required_keys)

        # Check types
        assert isinstance(result["hotels"], list)
        assert result["selected_hotel"] is None or isinstance(result["selected_hotel"], dict)
        assert result["error_message"] is None or isinstance(result["error_message"], str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

