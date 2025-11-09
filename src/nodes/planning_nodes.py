"""Planning nodes for travel planner agent.

This module contains node functions for the LangGraph workflow that handle
various planning operations including budget analysis, destination selection,
and itinerary building.
"""

import logging
from typing import Any, Dict

from src.agents.state import AgentState
from src.utils.error_handler import handle_node_errors

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Add console handler if not already present
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# Mapping of common destination patterns to regions
REGION_KEYWORDS = {
    'asia': ['tokyo', 'bangkok', 'singapore', 'hong kong', 'bali', 'dubai', 'india',
             'china', 'vietnam', 'korea', 'thailand', 'indonesia', 'philippines',
             'malaysia', 'pakistan', 'sri lanka', 'japan'],
    'europe': ['paris', 'london', 'rome', 'berlin', 'madrid', 'amsterdam', 'barcelona',
               'prague', 'vienna', 'istanbul', 'venice', 'athens', 'lisbon', 'dublin',
               'zurich', 'munich', 'budapest', 'scandinavia', 'italy', 'france', 'spain',
               'germany', 'uk', 'ireland', 'netherlands', 'poland', 'greece', 'portugal',
               'switzerland', 'austria', 'belgium', 'denmark', 'sweden', 'norway'],
    'americas': ['new york', 'los angeles', 'chicago', 'san francisco', 'miami', 'boston',
                 'washington', 'denver', 'seattle', 'mexico city', 'cancun', 'buenos aires',
                 'toronto', 'vancouver', 'caribbean', 'jamaica', 'cuba', 'dominican',
                 'usa', 'united states', 'canada', 'mexico', 'brazil', 'argentina', 'peru',
                 'chile', 'colombia', 'costa rica'],
    'africa': ['cairo', 'johannesburg', 'cape town', 'marrakech', 'nairobi', 'tanzania',
               'kenya', 'morocco', 'egypt', 'south africa', 'uganda', 'ethiopia'],
    'oceania': ['sydney', 'auckland', 'fiji', 'bali', 'australia', 'new zealand',
                'samoa', 'polynesia', 'melanesia'],
}

# Minimum budget per day by region (in USD)
MINIMUM_BUDGET_PER_DAY = {
    'asia': 100,
    'europe': 150,
    'americas': 120,
    'africa': 110,
    'oceania': 130,
}

# Default minimum budget per day for unknown regions
DEFAULT_MINIMUM_PER_DAY = 100


def identify_region(destination: str) -> str:
    """Identify the region based on destination name.

    Args:
        destination: The travel destination name

    Returns:
        The region name (asia, europe, americas, africa, oceania)
    """
    destination_lower = destination.lower().strip()

    for region, keywords in REGION_KEYWORDS.items():
        if any(keyword in destination_lower for keyword in keywords):
            logger.debug(f"Destination '{destination}' identified as region: {region}")
            return region

    logger.warning(
        f"Destination '{destination}' not recognized. "
        f"Using default region (asia) with ${DEFAULT_MINIMUM_PER_DAY}/day"
    )
    return 'asia'  # Default to Asia as fallback


def budget_analysis_node(state: AgentState) -> Dict[str, Any]:
    """Analyze and validate trip budget feasibility.

    This node:
    1. Calculates budget breakdown by category (flights, accommodation, activities, food)
    2. Identifies the travel destination region
    3. Determines minimum required budget based on region and duration
    4. Checks if the available budget is sufficient for the trip

    Args:
        state: The current agent state containing budget, destination, and duration

    Returns:
        Dictionary containing:
            - budget_breakdown: Dict with cost breakdown by category
            - budget_feasible: Boolean indicating if trip is affordable
            - minimum_required_budget: Minimum budget needed for the trip
            - analysis_summary: Human-readable analysis summary
            - region: Identified region
            - minimum_per_day: Minimum budget per day for the region

    Example:
        >>> from src.agents.state import AgentState
        >>> state = AgentState(
        ...     destination="Paris",
        ...     budget=3000.0,
        ...     duration=10,
        ... )
        >>> result = budget_analysis_node(state)
        >>> print(result['budget_feasible'])
        True
    """
    logger.info("=" * 70)
    logger.info("Starting budget analysis node")
    logger.info("=" * 70)

    # Extract necessary information from state
    total_budget = state.budget
    destination = state.destination or "Unknown"
    duration = state.duration

    logger.info(f"Input parameters:")
    logger.info(f"  Total Budget: ${total_budget:.2f}")
    logger.info(f"  Destination: {destination}")
    logger.info(f"  Duration: {duration} days")

    # Validate inputs
    if total_budget < 0:
        logger.error(f"Invalid budget: ${total_budget}. Budget cannot be negative.")
        raise ValueError("Budget cannot be negative")

    if duration <= 0:
        logger.error(f"Invalid duration: {duration}. Duration must be positive.")
        raise ValueError("Duration must be positive")

    # Step 1: Calculate budget breakdown (percentage-based allocation)
    logger.info("\nStep 1: Calculating budget breakdown...")

    if total_budget == 0:
        budget_breakdown = {
            "flights": 0.0,
            "accommodation": 0.0,
            "activities": 0.0,
            "food": 0.0,
        }
        logger.warning("Budget is $0. All categories set to $0.")
    else:
        budget_breakdown = {
            "flights": round(total_budget * 0.40, 2),
            "accommodation": round(total_budget * 0.35, 2),
            "activities": round(total_budget * 0.15, 2),
            "food": round(total_budget * 0.10, 2),
        }

    logger.info("Budget allocation:")
    for category, amount in budget_breakdown.items():
        percentage = (amount / total_budget * 100) if total_budget > 0 else 0
        logger.info(f"  {category.capitalize()}: ${amount:.2f} ({percentage:.1f}%)")

    # Step 2: Identify region and determine minimum budget
    logger.info("\nStep 2: Determining minimum required budget...")
    region = identify_region(destination)
    minimum_per_day = MINIMUM_BUDGET_PER_DAY.get(region, DEFAULT_MINIMUM_PER_DAY)

    logger.info(f"  Region identified: {region.upper()}")
    logger.info(f"  Minimum per day for {region}: ${minimum_per_day}/day")

    # Calculate total minimum budget
    minimum_required_budget = minimum_per_day * duration
    logger.info(f"  Duration: {duration} days")
    logger.info(f"  Minimum required budget: ${minimum_per_day} × {duration} days = ${minimum_required_budget:.2f}")

    # Step 3: Check budget feasibility
    logger.info("\nStep 3: Checking budget feasibility...")
    budget_feasible = total_budget >= minimum_required_budget

    if budget_feasible:
        surplus = total_budget - minimum_required_budget
        logger.info(f"  ✓ BUDGET FEASIBLE")
        logger.info(f"  Available budget: ${total_budget:.2f}")
        logger.info(f"  Minimum required: ${minimum_required_budget:.2f}")
        logger.info(f"  Surplus/flexibility: ${surplus:.2f}")
    else:
        deficit = minimum_required_budget - total_budget
        logger.warning(f"  ✗ BUDGET NOT FEASIBLE")
        logger.warning(f"  Available budget: ${total_budget:.2f}")
        logger.warning(f"  Minimum required: ${minimum_required_budget:.2f}")
        logger.warning(f"  Budget deficit: ${deficit:.2f}")

    # Step 4: Create analysis summary
    logger.info("\nStep 4: Generating analysis summary...")
    analysis_summary = (
        f"Budget Analysis for {destination} ({duration} days)\n"
        f"Total Budget: ${total_budget:.2f}\n"
        f"Region: {region.upper()}\n"
        f"Minimum per day: ${minimum_per_day}\n"
        f"Minimum total required: ${minimum_required_budget:.2f}\n"
        f"Feasible: {'Yes' if budget_feasible else 'No'}"
    )
    logger.info(f"\nAnalysis Summary:\n{analysis_summary}")

    # Create result dictionary
    result = {
        "budget_breakdown": budget_breakdown,
        "budget_feasible": budget_feasible,
        "minimum_required_budget": minimum_required_budget,
        "analysis_summary": analysis_summary,
        "region": region,
        "minimum_per_day": minimum_per_day,
    }

    logger.info("=" * 70)
    logger.info("Budget analysis node completed successfully")
    logger.info("=" * 70)

    return result

