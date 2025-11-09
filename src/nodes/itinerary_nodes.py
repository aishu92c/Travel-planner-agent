"""Itinerary generation node for travel planner agent.

This module contains the generate_itinerary_node function which creates
detailed, day-by-day travel itineraries with cost tracking and practical tips.
"""

import logging
from typing import Any, Dict

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


def generate_itinerary_node(state: AgentState) -> Dict[str, Any]:
    """Generate a detailed, day-by-day itinerary with costs and practical tips.

    This node creates a comprehensive travel itinerary using LLM, including:
    1. Day-by-day breakdown with activities, restaurants, and costs
    2. Selected flight and hotel details integration
    3. Structured output with budget tracking
    4. Practical tips for travel (transport, customs, safety)
    5. Token usage logging for cost monitoring

    Args:
        state: The current agent state with:
            - destination: Travel destination
            - start_date: Trip start date
            - end_date: Trip end date
            - duration: Trip duration in days
            - budget: Total budget
            - budget_breakdown: Dict with flights, accommodation, activities, food budgets
            - selected_flight: Dict with flight details (airline, price, times, etc.)
            - selected_hotel: Dict with hotel details (name, rating, amenities, price)
            - messages: Conversation history for context

    Returns:
        Dictionary containing:
            - final_itinerary: str - Detailed markdown itinerary with daily breakdown
            - input_tokens: int - Tokens used in prompt
            - output_tokens: int - Tokens generated in response
            - estimated_cost: float - Estimated API cost (for monitoring)
            - error_message: str | None - Error if generation failed
    """
    logger.info("=" * 70)
    logger.info("Starting itinerary generation node")
    logger.info("=" * 70)

    try:
        # Extract information from state
        destination = state.destination or "Unknown"
        start_date = state.start_date or "Unknown"
        end_date = state.end_date or "Unknown"
        duration = state.duration or 1
        total_budget = state.budget or 0.0
        budget_breakdown = state.budget_breakdown or {}
        selected_flight = state.selected_flight or {}
        selected_hotel = state.selected_hotel or {}

        logger.info(f"Trip Details:")
        logger.info(f"  Destination: {destination}")
        logger.info(f"  Dates: {start_date} to {end_date}")
        logger.info(f"  Duration: {duration} days")
        logger.info(f"  Total Budget: ${total_budget:.2f}")

        # Calculate activity and food budgets
        activities_budget = budget_breakdown.get("activities", 0.0)
        food_budget = budget_breakdown.get("food", 0.0)
        daily_activity_budget = activities_budget / duration if duration > 0 else 0.0
        daily_food_budget = food_budget / duration if duration > 0 else 0.0

        logger.info(f"\nBudget Breakdown:")
        logger.info(f"  Activities: ${activities_budget:.2f} (${daily_activity_budget:.2f}/day)")
        logger.info(f"  Food: ${food_budget:.2f} (${daily_food_budget:.2f}/day)")

        # Step 1: Initialize LLM
        logger.info("\nStep 1: Initializing LLM...")
        try:
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.7,
                max_tokens=4000,
            )
            logger.info("✓ LLM initialized successfully")
        except ImportError:
            logger.warning("langchain_openai not available, using structured fallback")
            llm = None
        except Exception as e:
            logger.warning(f"Failed to initialize LLM: {e}. Using fallback itinerary.")
            llm = None

        # Step 2: Create detailed prompt
        logger.info("\nStep 2: Creating detailed prompt template...")

        system_prompt = _create_system_prompt()
        human_prompt = _create_human_prompt(
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            duration=duration,
            total_budget=total_budget,
            activities_budget=activities_budget,
            food_budget=food_budget,
            daily_activity_budget=daily_activity_budget,
            daily_food_budget=daily_food_budget,
            selected_flight=selected_flight,
            selected_hotel=selected_hotel,
        )

        logger.info("✓ Prompt created")
        logger.info(f"  System prompt length: {len(system_prompt)} chars")
        logger.info(f"  Human prompt length: {len(human_prompt)} chars")

        # Step 3: Invoke LLM with token tracking
        logger.info("\nStep 3: Invoking LLM to generate itinerary...")

        if llm:
            try:
                from langchain_core.messages import SystemMessage, HumanMessage

                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=human_prompt)
                ]

                # Invoke LLM
                response = llm.invoke(messages)
                itinerary = response.content

                # Extract token usage information
                input_tokens = response.response_metadata.get("usage", {}).get("prompt_tokens", 0)
                output_tokens = response.response_metadata.get("usage", {}).get("completion_tokens", 0)

                logger.info("✓ LLM response received successfully")
                logger.info(f"  Input tokens: {input_tokens}")
                logger.info(f"  Output tokens: {output_tokens}")

            except Exception as e:
                logger.error(f"LLM invocation failed: {e}")
                itinerary = _generate_fallback_itinerary(
                    destination=destination,
                    duration=duration,
                    start_date=start_date,
                    selected_flight=selected_flight,
                    selected_hotel=selected_hotel,
                    activities_budget=activities_budget,
                    food_budget=food_budget,
                    daily_activity_budget=daily_activity_budget,
                    daily_food_budget=daily_food_budget,
                )
                input_tokens = 0
                output_tokens = 0
                logger.info("Using fallback itinerary")
        else:
            # Generate fallback itinerary
            itinerary = _generate_fallback_itinerary(
                destination=destination,
                duration=duration,
                start_date=start_date,
                selected_flight=selected_flight,
                selected_hotel=selected_hotel,
                activities_budget=activities_budget,
                food_budget=food_budget,
                daily_activity_budget=daily_activity_budget,
                daily_food_budget=daily_food_budget,
            )
            input_tokens = 0
            output_tokens = 0
            logger.info("Using fallback itinerary (LLM not available)")

        # Step 4: Calculate token cost (for Phase 2 monitoring)
        # GPT-3.5-turbo pricing: $0.50 per 1M input tokens, $1.50 per 1M output tokens
        estimated_cost = (input_tokens * 0.50 / 1_000_000) + (output_tokens * 1.50 / 1_000_000)

        logger.info(f"\nStep 4: Token Usage Summary")
        logger.info(f"  Input tokens: {input_tokens}")
        logger.info(f"  Output tokens: {output_tokens}")
        logger.info(f"  Total tokens: {input_tokens + output_tokens}")
        logger.info(f"  Estimated cost: ${estimated_cost:.6f}")

        # Step 5: Prepare result
        logger.info("\nStep 5: Preparing results...")

        result = {
            "final_itinerary": itinerary,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost": estimated_cost,
            "error_message": None,
        }

        logger.info("=" * 70)
        logger.info("Itinerary generation completed successfully")
        logger.info(f"Itinerary length: {len(itinerary)} characters")
        logger.info("=" * 70)

        return result

    except Exception as e:
        logger.exception(f"Error in itinerary generation node: {str(e)}")
        return {
            "final_itinerary": _generate_fallback_itinerary(
                destination=state.destination or "Unknown",
                duration=state.duration or 1,
                start_date=state.start_date or "Unknown",
                selected_flight=state.selected_flight or {},
                selected_hotel=state.selected_hotel or {},
                activities_budget=state.budget_breakdown.get("activities", 0) if state.budget_breakdown else 0,
                food_budget=state.budget_breakdown.get("food", 0) if state.budget_breakdown else 0,
                daily_activity_budget=0.0,
                daily_food_budget=0.0,
            ),
            "input_tokens": 0,
            "output_tokens": 0,
            "estimated_cost": 0.0,
            "error_message": f"Itinerary generation failed: {str(e)}",
        }


def _create_system_prompt() -> str:
    """Create the system prompt for itinerary generation.

    Returns:
        System prompt string
    """
    return """You are an expert travel advisor specializing in creating personalized, 
detailed itineraries. You provide practical, enjoyable travel plans with:

1. Day-by-day breakdowns with specific times and activities
2. Realistic restaurant recommendations matching traveler preferences
3. Accurate cost estimates for each day
4. Practical travel tips (transportation, customs, safety, local culture)
5. Hidden gems and local experiences alongside main attractions
6. Clear, well-organized markdown formatting

Your itineraries are engaging, informative, and budget-conscious."""


def _create_human_prompt(
    destination: str,
    start_date: str,
    end_date: str,
    duration: int,
    total_budget: float,
    activities_budget: float,
    food_budget: float,
    daily_activity_budget: float,
    daily_food_budget: float,
    selected_flight: Dict[str, Any],
    selected_hotel: Dict[str, Any],
) -> str:
    """Create the human prompt for itinerary generation.

    Args:
        destination: Travel destination
        start_date: Trip start date
        end_date: Trip end date
        duration: Trip duration in days
        total_budget: Total budget
        activities_budget: Budget for activities
        food_budget: Budget for food
        daily_activity_budget: Daily activity budget
        daily_food_budget: Daily food budget
        selected_flight: Selected flight details
        selected_hotel: Selected hotel details

    Returns:
        Human prompt string
    """
    flight_info = _format_flight_info(selected_flight)
    hotel_info = _format_hotel_info(selected_hotel)

    prompt = f"""Please create a detailed, day-by-day itinerary for a {duration}-day trip to {destination}.

## Trip Information
- **Destination**: {destination}
- **Dates**: {start_date} to {end_date}
- **Duration**: {duration} days
- **Total Budget**: ${total_budget:.2f}

## Flight Details
{flight_info}

## Hotel Details
{hotel_info}

## Budget Allocation
- **Total Budget**: ${total_budget:.2f}
- **Activities Budget**: ${activities_budget:.2f} (${daily_activity_budget:.2f}/day)
- **Food Budget**: ${food_budget:.2f} (${daily_food_budget:.2f}/day)

## Itinerary Requirements
Please provide a structured itinerary with the following for each day:

1. **Day Breakdown**:
   - Morning (8am-12pm): Specific activities with estimated duration
   - Afternoon (12pm-6pm): Main attractions and activities
   - Evening (6pm-late): Dinner and entertainment

2. **Dining Recommendations**:
   - Breakfast location and estimated cost
   - Lunch location and estimated cost
   - Dinner location and estimated cost
   - Budget breakdown: aim for ${daily_food_budget:.2f}/day

3. **Activity Costs**:
   - List each activity with entrance fee/cost
   - Total daily activity cost (target: ${daily_activity_budget:.2f})

4. **Transportation**:
   - How to get to/between locations
   - Estimated transport costs for the day
   - Local transport tips

5. **Daily Summary**:
   - Total estimated cost for the day
   - Highlights and must-see items

## Additional Requirements
- Use markdown formatting with clear headers (##, ###)
- Include practical tips (customs, safety, local etiquette)
- Suggest hidden gems and local experiences
- Note best times to visit popular attractions (crowds, hours)
- Include estimated costs for ALL activities and meals
- Keep daily costs within budget constraints
- Format as a practical, easy-to-follow guide

Create an engaging, detailed itinerary that maximizes the ${total_budget:.2f} budget while ensuring 
a memorable {duration}-day experience in {destination}."""

    return prompt


def _format_flight_info(flight: Dict[str, Any]) -> str:
    """Format flight information for the prompt.

    Args:
        flight: Flight details dictionary

    Returns:
        Formatted flight information string
    """
    if not flight:
        return "- **Status**: No flight selected (arrange independently)"

    return f"""- **Airline**: {flight.get('airline', 'Unknown')}
- **Price**: ${flight.get('price', 0):.2f}
- **Stops**: {flight.get('stops', 0)}
- **Duration**: {flight.get('duration', 0)} hours
- **Departure**: {flight.get('departure_time', 'Unknown')}
- **Arrival**: {flight.get('arrival_time', 'Unknown')}"""


def _format_hotel_info(hotel: Dict[str, Any]) -> str:
    """Format hotel information for the prompt.

    Args:
        hotel: Hotel details dictionary

    Returns:
        Formatted hotel information string
    """
    if not hotel:
        return "- **Status**: No hotel selected (arrange independently)"

    amenities = hotel.get('amenities', [])
    amenities_str = ", ".join(amenities) if amenities else "N/A"

    return f"""- **Name**: {hotel.get('name', 'Unknown')}
- **Rating**: {'⭐' * int(hotel.get('rating', 0))}{' ' if hotel.get('rating') else ''}{hotel.get('rating', 'N/A')}
- **Price**: ${hotel.get('price_per_night', 0):.2f}/night
- **Total**: ${hotel.get('total_price', 0):.2f}
- **Location**: {hotel.get('location', 'Unknown')}
- **Amenities**: {amenities_str}"""


def _generate_fallback_itinerary(
    destination: str,
    duration: int,
    start_date: str,
    selected_flight: Dict[str, Any],
    selected_hotel: Dict[str, Any],
    activities_budget: float,
    food_budget: float,
    daily_activity_budget: float,
    daily_food_budget: float,
) -> str:
    """Generate a structured fallback itinerary when LLM is not available.

    Args:
        destination: Travel destination
        duration: Trip duration in days
        start_date: Trip start date
        selected_flight: Selected flight details
        selected_hotel: Selected hotel details
        activities_budget: Total activities budget
        food_budget: Total food budget
        daily_activity_budget: Daily activity budget
        daily_food_budget: Daily food budget

    Returns:
        Formatted itinerary string
    """
    logger.info("Generating fallback itinerary...")

    flight_info = _format_flight_info(selected_flight)
    hotel_info = _format_hotel_info(selected_hotel)

    itinerary_days = []

    for day in range(1, duration + 1):
        day_itinerary = f"""
## Day {day}

### Morning Activity (8am-12pm)
- Explore local neighborhood and markets
- Estimated cost: ${daily_activity_budget * 0.3:.2f}

### Lunch
- Local restaurant recommendation
- Estimated cost: ${daily_food_budget * 0.3:.2f}

### Afternoon Activity (12pm-6pm)
- Main attraction or sightseeing
- Estimated cost: ${daily_activity_budget * 0.4:.2f}

### Dinner
- Restaurant suggestion
- Estimated cost: ${daily_food_budget * 0.4:.2f}

### Evening Activity (6pm-late)
- Local entertainment or leisure
- Estimated cost: ${daily_activity_budget * 0.3:.2f}

### Day {day} Summary
- **Activities**: ${daily_activity_budget:.2f}
- **Food**: ${daily_food_budget:.2f}
- **Daily Total**: ${daily_activity_budget + daily_food_budget:.2f}
"""
        itinerary_days.append(day_itinerary)

    full_itinerary = f"""# {destination} Itinerary - {duration} Days

## Trip Overview
- **Destination**: {destination}
- **Start Date**: {start_date}
- **Duration**: {duration} days
- **Total Activities Budget**: ${activities_budget:.2f}
- **Total Food Budget**: ${food_budget:.2f}

## Transportation Details
{flight_info}

## Accommodation Details
{hotel_info}

## Budget Summary
- **Daily Activities Budget**: ${daily_activity_budget:.2f}
- **Daily Food Budget**: ${daily_food_budget:.2f}
- **Daily Total**: ${daily_activity_budget + daily_food_budget:.2f}
- **Total for {duration} days**: ${(daily_activity_budget + daily_food_budget) * duration:.2f}

## Practical Tips
- Arrive early to popular attractions to avoid crowds
- Use public transportation when available
- Eat where locals eat for authentic and budget-friendly meals
- Book major activities in advance for better rates
- Keep emergency cash and cards in separate places
- Check local customs and dress codes for religious sites

## Daily Breakdown
{''.join(itinerary_days)}

## General Recommendations
- Download offline maps before traveling
- Inform your bank about your trip
- Get travel insurance
- Learn a few local phrases
- Respect local customs and culture
- Take time to explore beyond main attractions

**Happy travels! Enjoy your {duration}-day adventure in {destination}!**"""

    return full_itinerary

