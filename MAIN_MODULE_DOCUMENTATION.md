"""
Travel Planner Main Module Documentation

File: src/main.py
Purpose: Provides CLI interface, programmatic API, and beautiful console output for the travel planner
"""

# ============================================================================
# TABLE OF CONTENTS
# ============================================================================

1. OVERVIEW
2. FEATURES
3. PROGRAMMATIC INTERFACE
4. CLI INTERFACE
5. OUTPUT FORMATTING
6. EXAMPLES
7. ERROR HANDLING
8. CONFIGURATION

# ============================================================================
# 1. OVERVIEW
# ============================================================================

The src/main.py module provides a complete interface to the travel planner system:

✓ Programmatic API: run_travel_planner() function for programmatic use
✓ CLI Interface: Full argparse-based command-line interface
✓ Beautiful Output: Rich library for formatted console output
✓ Input Validation: Pydantic model validation
✓ Error Handling: Comprehensive error messages
✓ Dry-Run Mode: Test without making LLM calls
✓ Verbose Logging: Debug mode for troubleshooting

# ============================================================================
# 2. FEATURES
# ============================================================================

### Input Validation
- Uses TravelPlannerInput Pydantic model
- Validates budget > 0
- Validates duration 1-30 days
- Type checking for all inputs
- Clear error messages for validation failures

### Budget Analysis
- Calculates budget breakdown (40/35/15/10 split)
- Region-aware minimum cost calculation
- Feasibility determination
- Detailed cost tracking

### Search & Selection
- Intelligent flight filtering and selection
- Smart hotel filtering and selection
- Budget constraint enforcement
- All options stored for reference

### Output Formatting
- Color-coded messages (green/red/yellow)
- Formatted tables for budget breakdown
- Panels for selected options
- Markdown rendering for itineraries
- Professional styling with rich library

### Dry-Run Mode
- Validates inputs without LLM calls
- Shows what would be planned
- No API calls made
- Perfect for testing

# ============================================================================
# 3. PROGRAMMATIC INTERFACE
# ============================================================================

### Function: run_travel_planner()

Signature:
    run_travel_planner(
        destination: str,
        budget: float,
        duration: int,
        departure_city: str = "New York, USA",
        preferences: Optional[Dict[str, Any]] = None,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> Dict[str, Any]

Parameters:
    destination (str):
        Travel destination (e.g., "Paris, France")
        Required

    budget (float):
        Budget in USD
        Must be > 0
        Required

    duration (int):
        Trip duration in days
        Must be between 1 and 30
        Required

    departure_city (str, optional):
        City from which you're departing
        Default: "New York, USA"

    preferences (dict, optional):
        User preferences with keys:
        - dietary: "none", "vegetarian", "vegan", "halal"
        - accommodation_type: "hotel", "hostel", "airbnb"
        - activities: "adventure", "cultural", "relaxation", "nightlife"
        Default: None (no preferences)

    dry_run (bool, optional):
        If True, validates inputs without making LLM calls
        Default: False

    verbose (bool, optional):
        If True, enables debug-level logging
        Default: False

Returns:
    Dictionary with structure:
    {
        "status": "success" | "error" | "dry_run",
        "state": {
            "destination": str,
            "budget": float,
            "duration": int,
            "budget_feasible": bool,
            "budget_breakdown": dict[str, float],
            "selected_flight": dict[str, Any] | None,
            "selected_hotel": dict[str, Any] | None,
            "error_message": str | None,
            ...
        },
        "message": str
    }

Example:
    >>> result = run_travel_planner(
    ...     destination="Paris, France",
    ...     budget=2000.0,
    ...     duration=5,
    ...     preferences={
    ...         "dietary": "vegetarian",
    ...         "accommodation_type": "hotel",
    ...         "activities": "cultural"
    ...     }
    ... )
    >>> print(result["status"])  # "success"
    >>> print(result["state"]["budget_breakdown"])
    # {'flights': 800.0, 'accommodation': 700.0, 'activities': 300.0, 'food': 200.0}

# ============================================================================
# 4. CLI INTERFACE
# ============================================================================

### Getting Help

Show main help:
    python -m src.main --help

Show plan subcommand help:
    python -m src.main plan --help

### Basic Usage

Minimal trip planning:
    python -m src.main plan \
        --destination "Paris, France" \
        --budget 2000 \
        --duration 5

### With Preferences

Include dietary and accommodation preferences:
    python -m src.main plan \
        --destination "Paris, France" \
        --budget 2000 \
        --duration 5 \
        --dietary vegetarian \
        --accommodation-type hotel

### With All Options

Complete example with all options:
    python -m src.main plan \
        --destination "Tokyo, Japan" \
        --budget 3000 \
        --duration 7 \
        --departure-city "Los Angeles, USA" \
        --dietary vegan \
        --accommodation-type airbnb \
        --activities adventure \
        --verbose

### Dry-Run Mode

Validate inputs without making LLM calls:
    python -m src.main plan \
        --destination "Paris, France" \
        --budget 2000 \
        --duration 5 \
        --dry-run

### Verbose Mode

Enable debug logging for troubleshooting:
    python -m src.main plan \
        --destination "Paris, France" \
        --budget 2000 \
        --duration 5 \
        --verbose

### Argument Reference

Required Arguments:
    --destination DESTINATION
        Travel destination (e.g., "Paris, France")

    --budget AMOUNT
        Budget in USD (must be > 0)

    --duration DAYS
        Trip duration in days (1-30)

Optional Arguments:
    --departure-city CITY
        Departure city (default: "New York, USA")

    --accommodation-type {hotel,hostel,airbnb}
        Accommodation preference

    --dietary {none,vegetarian,vegan,halal}
        Dietary restrictions

    --activities {adventure,cultural,relaxation,nightlife}
        Activity preferences

Flags:
    --dry-run
        Validate inputs without LLM calls

    --verbose, -v
        Enable debug logging

# ============================================================================
# 5. OUTPUT FORMATTING
# ============================================================================

### Colors Used

✓ Green: Success messages, selected options, trip feasibility
✗ Red: Error messages, failed operations
⚠ Yellow: Warnings, insufficient budget
ℹ Blue: Information messages, status updates
✓ Cyan: Section headers, table columns

### Output Sections

1. Trip Planning Summary
   - Displays key trip parameters
   - Shows budget feasibility status

2. Budget Breakdown
   - Table with category breakdown
   - Shows amounts and percentages
   - Total row at bottom

3. Selected Flight (if available)
   - Flight details in formatted panel
   - Airline, times, price, stops, etc.

4. Selected Hotel (if available)
   - Hotel details in formatted panel
   - Name, rating, amenities, price, etc.

5. Final Itinerary
   - Rendered as markdown
   - Day-by-day breakdown
   - Activity suggestions with costs
   - Restaurant recommendations
   - Practical tips

6. Alternative Suggestions (if budget insufficient)
   - Markdown-formatted suggestions
   - 3 practical alternatives
   - Money-saving tips

### Rich Library Features

Used when available (installs via: pip install rich):
- Colored output
- Formatted tables
- Panels with borders
- Markdown rendering
- Text styling

Fallback (if rich not installed):
- Plain text output
- Simple formatting
- No colors/styling
- Basic table layout

# ============================================================================
# 6. EXAMPLES
# ============================================================================

### Example 1: Basic Trip Planning

import run_travel_planner from src.main

result = run_travel_planner(
    destination="Paris, France",
    budget=2000,
    duration=5
)

# Output shows:
# - Budget breakdown: Flights $800, Hotels $700, Activities $300, Food $200
# - Budget feasible: Yes
# - Selected flight and hotel
# - Day-by-day itinerary

### Example 2: Budget-Constrained Trip

result = run_travel_planner(
    destination="Paris, France",
    budget=500,  # Very limited budget
    duration=5
)

# Output shows:
# - Budget insufficient warning
# - Alternative suggestions
# - Ways to reduce costs
# - Money-saving tips for destination

### Example 3: Customized Preferences

result = run_travel_planner(
    destination="Tokyo, Japan",
    budget=3500,
    duration=7,
    departure_city="Los Angeles, USA",
    preferences={
        "dietary": "vegan",
        "accommodation_type": "airbnb",
        "activities": "cultural"
    }
)

# Output shows:
# - Vegan-friendly restaurant recommendations
# - Airbnb accommodations selected
# - Cultural activities highlighted

### Example 4: Dry-Run Mode

result = run_travel_planner(
    destination="Paris, France",
    budget=2000,
    duration=5,
    dry_run=True
)

# Output shows:
# - Only validation results
# - Budget breakdown calculation
# - No LLM calls made
# - Message: "Dry run completed"

### Example 5: CLI with Full Options

bash $ python -m src.main plan \
    --destination "Barcelona, Spain" \
    --budget 2500 \
    --duration 6 \
    --departure-city "Miami, USA" \
    --dietary vegetarian \
    --accommodation-type hotel \
    --activities relaxation \
    --verbose

# Output shows:
# - Detailed logging messages
# - Color-coded sections
# - Formatted tables and panels
# - Complete itinerary

# ============================================================================
# 7. ERROR HANDLING
# ============================================================================

### Validation Errors

Error: Budget must be > 0
    Solution: Set budget > 0

Error: Duration must be between 1 and 30 days
    Solution: Set duration between 1 and 30

Error: Invalid destination
    Solution: Use a valid city/country name

Error: Invalid dietary preference
    Solution: Use one of: none, vegetarian, vegan, halal

### Runtime Errors

Error: Failed to create graph
    Solution: Check LangGraph installation and configuration

Error: Graph execution failed
    Solution: Check error details, try with --verbose flag

Error: LLM call failed
    Solution: Verify API keys and internet connection

### User-Friendly Error Messages

The system converts technical errors to user-friendly messages:

Technical: "Budget insufficient for destination and duration"
User Message: "Your budget is insufficient for the desired travel dates
             and destination. Please try adjusting your budget,
             destination, or trip duration."

Technical: "Flight search API returned empty results"
User Message: "We had trouble finding flights for your trip. Please try
             different dates or destination."

# ============================================================================
# 8. CONFIGURATION
# ============================================================================

### Environment Variables

Optional environment variables:
- AWS_REGION: AWS region (default: us-east-1)
- LOG_LEVEL: Logging level (default: INFO)
- OPENAI_API_KEY: OpenAI API key (if using OpenAI)

### Settings

Configuration loaded from src/config/settings.py:
- Model parameters (temperature, max_tokens)
- API settings (host, port)
- Logging configuration
- Cache settings

### Logging

When verbose=True:
    Log level set to DEBUG
    Shows detailed execution steps
    Useful for troubleshooting

Default:
    Log level set to INFO
    Shows progress updates
    Clean console output

### Error Handling Strategy

1. Input Validation
   - Validate using Pydantic models
   - Provide clear error messages
   - Exit early if invalid

2. Graph Execution
   - Try-except wrapper
   - Log detailed errors
   - Return user-friendly message

3. State Processing
   - Check for error_message field
   - Route to error handler if needed
   - Format for user display

4. Output Formatting
   - Handle missing data gracefully
   - Use defaults where appropriate
   - Display errors in prominent colors

# ============================================================================
# QUICK REFERENCE
# ============================================================================

### Common Commands

Run with defaults:
    python -m src.main plan --destination "Paris, France" --budget 2000 --duration 5

Test mode (no LLM calls):
    python -m src.main plan --destination "Paris, France" --budget 2000 --duration 5 --dry-run

Debug mode:
    python -m src.main plan --destination "Paris, France" --budget 2000 --duration 5 --verbose

With preferences:
    python -m src.main plan --destination "Paris, France" --budget 2000 --duration 5 \
        --dietary vegetarian --accommodation-type hotel --activities cultural

### Programmatic API

Import:
    from src.main import run_travel_planner

Call:
    result = run_travel_planner(
        destination="Paris, France",
        budget=2000,
        duration=5
    )

Check result:
    if result["status"] == "success":
        budget_breakdown = result["state"]["budget_breakdown"]
        print(f"Flights: ${budget_breakdown['flights']}")
    else:
        print(f"Error: {result['message']}")

# ============================================================================
# INSTALLATION & SETUP
# ============================================================================

1. Install dependencies:
   pip install -r requirements.txt

2. For beautiful output, ensure rich is installed:
   pip install rich>=13.0.0

3. Set up environment variables:
   cp .env.example .env
   # Edit .env with your API keys

4. Run the planner:
   python -m src.main plan --destination "Paris, France" --budget 2000 --duration 5

# ============================================================================
# TESTING
# ============================================================================

Run test suite:
    python test_main.py

This verifies:
- Module imports work correctly
- CLI parser creation succeeds
- Help output is available
- Subcommands are properly configured

# ============================================================================
# END OF DOCUMENTATION
# ============================================================================
"""

