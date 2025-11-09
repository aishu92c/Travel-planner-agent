"""Tool nodes for travel planner agent.

This module contains node functions that interact with external tools
for searching flights, hotels, and activities, with built-in selection
logic to choose the best options within budget constraints.
"""

import logging
from typing import Any, Dict, List
from decimal import Decimal

from src.agents.state import AgentState

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


# ============================================================================
# FLIGHT SEARCH AND SELECTION
# ============================================================================

def search_flights_node(state: AgentState) -> Dict[str, Any]:
    """Search for flights and select the best option within budget.

    This node:
    1. Calls the flight search tool
    2. Filters flights by budget constraint
    3. Sorts by price and stops (prefer cheaper, fewer stops)
    4. Selects the top result
    5. Returns state with all options and selected flight

    Args:
        state: The current agent state with destination, dates, and budget info

    Returns:
        Dictionary with:
            - flights: List of all flight options found
            - selected_flight: Best flight option selected
            - error_message: Error message if search failed

    Raises:
        No exceptions - errors are captured and logged
    """
    logger.info("=" * 70)
    logger.info("Starting flight search node")
    logger.info("=" * 70)

    try:
        # Extract information from state
        destination = state.destination or "Unknown"
        start_date = state.start_date or "Unknown"
        end_date = state.end_date or "Unknown"
        budget_breakdown = state.budget_breakdown or {}
        flights_budget = budget_breakdown.get("flights", 0.0)

        logger.info(f"Search Parameters:")
        logger.info(f"  Destination: {destination}")
        logger.info(f"  Start Date: {start_date}")
        logger.info(f"  End Date: {end_date}")
        logger.info(f"  Flights Budget: ${flights_budget:.2f}")

        # STEP 1: Call flight search tool
        logger.info("\nStep 1: Calling flight search tool...")
        flight_results = _call_flight_search_tool(
            destination=destination,
            start_date=start_date,
            end_date=end_date,
        )

        if not flight_results:
            logger.warning("No flights found for the search criteria")
            return {
                "flights": [],
                "selected_flight": None,
                "error_message": "No flights found for the specified destination and dates",
            }

        logger.info(f"Found {len(flight_results)} flight options")

        # STEP 2: Filter by budget
        logger.info("\nStep 2: Filtering flights by budget...")
        affordable_flights = [
            flight for flight in flight_results
            if flight.get("price", 0) <= flights_budget
        ]

        logger.info(f"Affordable flights: {len(affordable_flights)} out of {len(flight_results)}")

        if not affordable_flights:
            logger.warning(
                f"No flights within budget. Cheapest: ${min(f.get('price', 0) for f in flight_results):.2f}"
            )
            return {
                "flights": flight_results,
                "selected_flight": None,
                "error_message": (
                    f"No flights within budget ${flights_budget:.2f}. "
                    f"Cheapest option: ${min(f.get('price', 0) for f in flight_results):.2f}"
                ),
            }

        # STEP 3: Sort by score (price * 0.7 + stops * 100)
        logger.info("\nStep 3: Sorting flights by score...")
        scored_flights = []
        for flight in affordable_flights:
            price = float(flight.get("price", 0))
            stops = int(flight.get("stops", 0))
            score = (price * 0.7) + (stops * 100)
            scored_flights.append({
                **flight,
                "score": score,
            })

        # Sort by score ascending (lower score is better)
        scored_flights.sort(key=lambda x: x["score"])

        logger.info("Top 3 options:")
        for i, flight in enumerate(scored_flights[:3], 1):
            logger.info(
                f"  {i}. {flight.get('airline', 'Unknown')} - "
                f"${flight.get('price', 0):.2f} "
                f"({flight.get('stops', 0)} stops, score: {flight.get('score', 0):.2f})"
            )

        # STEP 4: Select top result
        selected_flight = scored_flights[0]
        logger.info("\nStep 4: Selecting best flight...")
        logger.info(f"✓ Selected: {selected_flight.get('airline', 'Unknown')} - "
                   f"${selected_flight.get('price', 0):.2f} "
                   f"({selected_flight.get('stops', 0)} stops)")

        # STEP 5: Create result
        result = {
            "flights": flight_results,
            "selected_flight": selected_flight,
            "error_message": None,
        }

        logger.info("=" * 70)
        logger.info("Flight search completed successfully")
        logger.info("=" * 70)

        return result

    except Exception as e:
        logger.exception(f"Error during flight search: {str(e)}")
        return {
            "flights": [],
            "selected_flight": None,
            "error_message": f"Flight search failed: {str(e)}",
        }


# ============================================================================
# HOTEL SEARCH AND SELECTION
# ============================================================================

def search_hotels_node(state: AgentState) -> Dict[str, Any]:
    """Search for hotels and select the best option within budget.

    This node:
    1. Calls the hotel search tool
    2. Filters hotels by budget constraint
    3. Sorts by rating (descending) then price (ascending)
    4. Selects the top result
    5. Returns state with all options and selected hotel

    Args:
        state: The current agent state with destination, dates, and budget info

    Returns:
        Dictionary with:
            - hotels: List of all hotel options found
            - selected_hotel: Best hotel option selected
            - error_message: Error message if search failed

    Raises:
        No exceptions - errors are captured and logged
    """
    logger.info("=" * 70)
    logger.info("Starting hotel search node")
    logger.info("=" * 70)

    try:
        # Extract information from state
        destination = state.destination or "Unknown"
        start_date = state.start_date or "Unknown"
        end_date = state.end_date or "Unknown"
        duration = state.duration or 1
        budget_breakdown = state.budget_breakdown or {}
        accommodation_budget = budget_breakdown.get("accommodation", 0.0)

        logger.info(f"Search Parameters:")
        logger.info(f"  Destination: {destination}")
        logger.info(f"  Check-in: {start_date}")
        logger.info(f"  Check-out: {end_date}")
        logger.info(f"  Duration: {duration} nights")
        logger.info(f"  Accommodation Budget: ${accommodation_budget:.2f}")

        # STEP 1: Call hotel search tool
        logger.info("\nStep 1: Calling hotel search tool...")
        hotel_results = _call_hotel_search_tool(
            destination=destination,
            check_in_date=start_date,
            check_out_date=end_date,
            duration=duration,
        )

        if not hotel_results:
            logger.warning("No hotels found for the search criteria")
            return {
                "hotels": [],
                "selected_hotel": None,
                "error_message": "No hotels found for the specified destination and dates",
            }

        logger.info(f"Found {len(hotel_results)} hotel options")

        # STEP 2: Filter by budget
        logger.info("\nStep 2: Filtering hotels by budget...")
        affordable_hotels = [
            hotel for hotel in hotel_results
            if hotel.get("total_price", 0) <= accommodation_budget
        ]

        logger.info(f"Affordable hotels: {len(affordable_hotels)} out of {len(hotel_results)}")

        if not affordable_hotels:
            cheapest_price = min(h.get("total_price", 0) for h in hotel_results)
            logger.warning(f"No hotels within budget. Cheapest: ${cheapest_price:.2f}")
            return {
                "hotels": hotel_results,
                "selected_hotel": None,
                "error_message": (
                    f"No hotels within budget ${accommodation_budget:.2f}. "
                    f"Cheapest option: ${cheapest_price:.2f}"
                ),
            }

        # STEP 3: Sort by score (rating * -100 + price_per_night)
        # Negative rating to sort descending (higher rating first)
        logger.info("\nStep 3: Sorting hotels by rating then price...")
        scored_hotels = []
        for hotel in affordable_hotels:
            rating = float(hotel.get("rating", 0))
            price_per_night = float(hotel.get("price_per_night", 0))
            # Score: prefer higher rating (negative for descending), then lower price
            score = (rating * -100) + price_per_night
            scored_hotels.append({
                **hotel,
                "score": score,
            })

        # Sort by score ascending (lower score is better)
        scored_hotels.sort(key=lambda x: x["score"])

        logger.info("Top 3 options:")
        for i, hotel in enumerate(scored_hotels[:3], 1):
            logger.info(
                f"  {i}. {hotel.get('name', 'Unknown')} - "
                f"⭐ {hotel.get('rating', 0):.1f} - "
                f"${hotel.get('price_per_night', 0):.2f}/night "
                f"(Total: ${hotel.get('total_price', 0):.2f})"
            )

        # STEP 4: Select top result
        selected_hotel = scored_hotels[0]
        logger.info("\nStep 4: Selecting best hotel...")
        logger.info(f"✓ Selected: {selected_hotel.get('name', 'Unknown')} - "
                   f"⭐ {selected_hotel.get('rating', 0):.1f} - "
                   f"${selected_hotel.get('price_per_night', 0):.2f}/night "
                   f"(Total: ${selected_hotel.get('total_price', 0):.2f})")

        # STEP 5: Create result
        result = {
            "hotels": hotel_results,
            "selected_hotel": selected_hotel,
            "error_message": None,
        }

        logger.info("=" * 70)
        logger.info("Hotel search completed successfully")
        logger.info("=" * 70)

        return result

    except Exception as e:
        logger.exception(f"Error during hotel search: {str(e)}")
        return {
            "hotels": [],
            "selected_hotel": None,
            "error_message": f"Hotel search failed: {str(e)}",
        }


# ============================================================================
# MOCK TOOL IMPLEMENTATIONS
# ============================================================================

def _call_flight_search_tool(
    destination: str,
    start_date: str,
    end_date: str,
) -> List[Dict[str, Any]]:
    """Mock flight search tool.

    In production, this would call an actual flight search API.

    Args:
        destination: Travel destination
        start_date: Departure date (ISO format)
        end_date: Return date (ISO format)

    Returns:
        List of flight options with price, airline, stops, duration, etc.
    """
    logger.debug(f"Calling flight search tool for {destination}")

    # Mock flight data
    mock_flights = [
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
        {
            "id": "FL004",
            "airline": "Southwest Airlines",
            "price": 650.00,
            "stops": 0,
            "duration": 5.5,
            "departure_time": "14:00",
            "arrival_time": "19:30",
        },
    ]

    return mock_flights


def _call_hotel_search_tool(
    destination: str,
    check_in_date: str,
    check_out_date: str,
    duration: int,
) -> List[Dict[str, Any]]:
    """Mock hotel search tool.

    In production, this would call an actual hotel search API.

    Args:
        destination: Hotel destination
        check_in_date: Check-in date (ISO format)
        check_out_date: Check-out date (ISO format)
        duration: Number of nights

    Returns:
        List of hotel options with price, rating, amenities, etc.
    """
    logger.debug(f"Calling hotel search tool for {destination}")

    # Mock hotel data
    mock_hotels = [
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

    return mock_hotels

