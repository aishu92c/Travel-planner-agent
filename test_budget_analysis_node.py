"""Test suite for budget analysis node.

Tests the budget_analysis_node function with various scenarios including:
- Feasible budgets with different destinations
- Infeasible budgets with different durations
- Unknown destinations
- Edge cases (zero budget, single day trips)
"""

import pytest
from src.agents.state import AgentState
from src.nodes.planning_nodes import budget_analysis_node, identify_region


class TestIdentifyRegion:
    """Test the region identification logic."""

    def test_identify_asia_destinations(self):
        """Test recognition of Asian destinations."""
        assert identify_region("Tokyo") == "asia"
        assert identify_region("Bangkok") == "asia"
        assert identify_region("Singapore") == "asia"
        assert identify_region("New Delhi, India") == "asia"
        assert identify_region("BALI") == "asia"  # Case insensitive

    def test_identify_europe_destinations(self):
        """Test recognition of European destinations."""
        assert identify_region("Paris") == "europe"
        assert identify_region("London") == "europe"
        assert identify_region("Rome") == "europe"
        assert identify_region("Berlin") == "europe"
        assert identify_region("amsterdam") == "europe"  # Case insensitive

    def test_identify_americas_destinations(self):
        """Test recognition of American destinations."""
        assert identify_region("New York") == "americas"
        assert identify_region("Los Angeles") == "americas"
        assert identify_region("Toronto") == "americas"
        assert identify_region("Mexico City") == "americas"
        assert identify_region("Buenos Aires") == "americas"

    def test_identify_africa_destinations(self):
        """Test recognition of African destinations."""
        assert identify_region("Cairo") == "africa"
        assert identify_region("Cape Town") == "africa"
        assert identify_region("Marrakech") == "africa"

    def test_identify_oceania_destinations(self):
        """Test recognition of Oceania destinations."""
        assert identify_region("Sydney") == "oceania"
        assert identify_region("Auckland") == "oceania"

    def test_unknown_destination_defaults_to_asia(self):
        """Test that unknown destinations default to Asia."""
        assert identify_region("Unknown Place") == "asia"
        assert identify_region("Random City") == "asia"
        assert identify_region("XYZ Location") == "asia"


class TestBudgetAnalysisNode:
    """Test the budget_analysis_node function."""

    def test_feasible_budget_europe(self):
        """Test a feasible budget for European travel."""
        state = AgentState(
            destination="Paris",
            budget=2000.0,
            duration=10,
        )

        result = budget_analysis_node(state)

        assert result["budget_feasible"] is True
        assert result["region"] == "europe"
        assert result["minimum_per_day"] == 150
        assert result["minimum_required_budget"] == 1500.0
        assert "budget_breakdown" in result
        assert len(result["budget_breakdown"]) == 4

    def test_infeasible_budget_europe(self):
        """Test an infeasible budget for European travel."""
        state = AgentState(
            destination="Rome",
            budget=500.0,
            duration=10,
        )

        result = budget_analysis_node(state)

        assert result["budget_feasible"] is False
        assert result["region"] == "europe"
        assert result["minimum_per_day"] == 150
        assert result["minimum_required_budget"] == 1500.0

    def test_feasible_budget_asia(self):
        """Test a feasible budget for Asian travel."""
        state = AgentState(
            destination="Bangkok",
            budget=1500.0,
            duration=14,
        )

        result = budget_analysis_node(state)

        assert result["budget_feasible"] is True
        assert result["region"] == "asia"
        assert result["minimum_per_day"] == 100
        assert result["minimum_required_budget"] == 1400.0

    def test_infeasible_budget_asia(self):
        """Test an infeasible budget for Asian travel."""
        state = AgentState(
            destination="Tokyo",
            budget=300.0,
            duration=7,
        )

        result = budget_analysis_node(state)

        assert result["budget_feasible"] is False
        assert result["region"] == "asia"
        assert result["minimum_required_budget"] == 700.0

    def test_budget_breakdown_allocation(self):
        """Test the budget breakdown percentages."""
        state = AgentState(
            destination="Paris",
            budget=1000.0,
            duration=5,
        )

        result = budget_analysis_node(state)
        breakdown = result["budget_breakdown"]

        # Check percentages
        assert breakdown["flights"] == 400.0      # 40%
        assert breakdown["accommodation"] == 350.0  # 35%
        assert breakdown["activities"] == 150.0     # 15%
        assert breakdown["food"] == 100.0           # 10%

        # Check total
        total = sum(breakdown.values())
        assert total == 1000.0

    def test_budget_breakdown_with_different_amounts(self):
        """Test budget breakdown with various amounts."""
        for budget in [500, 1000, 5000, 10000]:
            state = AgentState(
                destination="London",
                budget=float(budget),
                duration=5,
            )

            result = budget_analysis_node(state)
            breakdown = result["budget_breakdown"]

            # Verify percentages
            assert breakdown["flights"] == round(budget * 0.40, 2)
            assert breakdown["accommodation"] == round(budget * 0.35, 2)
            assert breakdown["activities"] == round(budget * 0.15, 2)
            assert breakdown["food"] == round(budget * 0.10, 2)

    def test_zero_budget(self):
        """Test budget analysis with zero budget."""
        state = AgentState(
            destination="Paris",
            budget=0.0,
            duration=10,
        )

        result = budget_analysis_node(state)

        assert result["budget_feasible"] is False
        assert result["budget_breakdown"]["flights"] == 0.0
        assert result["budget_breakdown"]["accommodation"] == 0.0
        assert result["budget_breakdown"]["activities"] == 0.0
        assert result["budget_breakdown"]["food"] == 0.0

    def test_single_day_trip(self):
        """Test budget analysis for a single day trip."""
        state = AgentState(
            destination="London",
            budget=500.0,
            duration=1,
        )

        result = budget_analysis_node(state)

        assert result["region"] == "europe"
        assert result["minimum_per_day"] == 150
        assert result["minimum_required_budget"] == 150.0
        assert result["budget_feasible"] is True

    def test_long_trip_europe(self):
        """Test budget analysis for a long European trip."""
        state = AgentState(
            destination="Barcelona",
            budget=5000.0,
            duration=30,
        )

        result = budget_analysis_node(state)

        assert result["region"] == "europe"
        assert result["minimum_per_day"] == 150
        assert result["minimum_required_budget"] == 4500.0
        assert result["budget_feasible"] is True

    def test_long_trip_infeasible(self):
        """Test budget analysis for a long trip with insufficient budget."""
        state = AgentState(
            destination="Tokyo",
            budget=500.0,
            duration=30,
        )

        result = budget_analysis_node(state)

        assert result["region"] == "asia"
        assert result["minimum_required_budget"] == 3000.0
        assert result["budget_feasible"] is False

    def test_americas_budget_analysis(self):
        """Test budget analysis for American destination."""
        state = AgentState(
            destination="New York",
            budget=2000.0,
            duration=10,
        )

        result = budget_analysis_node(state)

        assert result["region"] == "americas"
        assert result["minimum_per_day"] == 120
        assert result["minimum_required_budget"] == 1200.0
        assert result["budget_feasible"] is True

    def test_unknown_destination_analysis(self):
        """Test budget analysis for unknown destination (defaults to Asia)."""
        state = AgentState(
            destination="Atlantis",
            budget=1500.0,
            duration=10,
        )

        result = budget_analysis_node(state)

        assert result["region"] == "asia"
        assert result["minimum_per_day"] == 100
        assert result["minimum_required_budget"] == 1000.0
        assert result["budget_feasible"] is True

    def test_analysis_summary_generation(self):
        """Test that analysis summary is generated correctly."""
        state = AgentState(
            destination="Paris",
            budget=2000.0,
            duration=10,
        )

        result = budget_analysis_node(state)
        summary = result["analysis_summary"]

        assert "Paris" in summary
        assert "10 days" in summary
        assert "$2000" in summary or "2000" in summary
        assert "EUROPE" in summary
        assert "Yes" in summary  # Feasible

    def test_analysis_summary_infeasible(self):
        """Test analysis summary for infeasible budget."""
        state = AgentState(
            destination="Rome",
            budget=500.0,
            duration=10,
        )

        result = budget_analysis_node(state)
        summary = result["analysis_summary"]

        assert "Rome" in summary
        assert "10 days" in summary
        assert "No" in summary  # Not feasible

    def test_result_keys(self):
        """Test that all required keys are in the result."""
        state = AgentState(
            destination="Paris",
            budget=2000.0,
            duration=10,
        )

        result = budget_analysis_node(state)

        required_keys = [
            "budget_breakdown",
            "budget_feasible",
            "minimum_required_budget",
            "analysis_summary",
            "region",
            "minimum_per_day",
        ]

        for key in required_keys:
            assert key in result, f"Missing key: {key}"

    def test_invalid_budget_raises_error(self):
        """Test that negative budget raises an error."""
        state = AgentState(
            destination="Paris",
            budget=-100.0,
            duration=10,
        )

        with pytest.raises(ValueError, match="Budget cannot be negative"):
            budget_analysis_node(state)

    def test_invalid_duration_raises_error(self):
        """Test that non-positive duration raises an error."""
        state = AgentState(
            destination="Paris",
            budget=2000.0,
            duration=0,
        )

        with pytest.raises(ValueError, match="Duration must be positive"):
            budget_analysis_node(state)


class TestBudgetBreakdownRounding:
    """Test that budget breakdown calculations are properly rounded."""

    def test_rounding_with_odd_budget(self):
        """Test rounding with odd budget amounts."""
        state = AgentState(
            destination="London",
            budget=1234.56,
            duration=5,
        )

        result = budget_analysis_node(state)
        breakdown = result["budget_breakdown"]

        # Verify rounding to 2 decimal places
        for category, amount in breakdown.items():
            assert isinstance(amount, float)
            # Check that amount has at most 2 decimal places
            assert len(str(amount).split('.')[-1]) <= 2

        # Verify sum is close to original budget
        total = sum(breakdown.values())
        assert abs(total - 1234.56) < 0.01


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_minimum_budget_exactly_required(self):
        """Test when budget exactly equals minimum required."""
        state = AgentState(
            destination="London",
            budget=1500.0,
            duration=10,
        )

        result = budget_analysis_node(state)

        assert result["budget_feasible"] is True
        assert result["budget"] == result["minimum_required_budget"]

    def test_budget_one_cent_above_minimum(self):
        """Test budget that's one cent above minimum."""
        state = AgentState(
            destination="London",
            budget=1500.01,
            duration=10,
        )

        result = budget_analysis_node(state)

        assert result["budget_feasible"] is True

    def test_budget_one_cent_below_minimum(self):
        """Test budget that's one cent below minimum."""
        state = AgentState(
            destination="London",
            budget=1499.99,
            duration=10,
        )

        result = budget_analysis_node(state)

        assert result["budget_feasible"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

