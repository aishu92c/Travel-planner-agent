"""Travel Planner Main Module.

This module provides:
1. Main programmatic interface: run_travel_planner()
2. CLI interface using argparse
3. Beautiful console output using rich library
4. Dry-run mode for testing
5. Input validation using Pydantic models

Example:
    >>> from src.main import run_travel_planner
    >>> result = run_travel_planner(
    ...     destination="Paris, France",
    ...     budget=2000,
    ...     duration=5,
    ...     preferences={"dietary": "vegetarian"}
    ... )
    >>> print(result)

CLI Usage:
    >>> python -m src.main plan \\
    ...     --destination "Paris, France" \\
    ...     --budget 2000 \\
    ...     --duration 5 \\
    ...     --dietary vegetarian
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from pydantic import ValidationError

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

from src.agents.state import AgentState, TravelPlannerInput
from src.config.settings import get_settings
from src.graph import create_graph
from src.utils.logger import get_node_logger

# ============================================================================
# SETUP
# ============================================================================

logger = get_node_logger("main")
console = Console() if HAS_RICH else None

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def print_section(title: str, message: str = "") -> None:
    """Print a formatted section header.

    Args:
        title: Section title
        message: Optional message after title
    """
    if HAS_RICH:
        console.print(f"\n[bold cyan]{'=' * 70}[/bold cyan]")
        console.print(f"[bold cyan]{title}[/bold cyan]", end="")
        if message:
            console.print(f" [yellow]{message}[/yellow]")
        else:
            console.print()
        console.print(f"[bold cyan]{'=' * 70}[/bold cyan]\n")
    else:
        print(f"\n{'=' * 70}")
        print(f"{title} {message}".strip())
        print(f"{'=' * 70}\n")


def print_error(message: str) -> None:
    """Print an error message.

    Args:
        message: Error message to display
    """
    if HAS_RICH:
        console.print(f"[bold red]✗ Error:[/bold red] {message}")
    else:
        print(f"✗ Error: {message}")


def print_success(message: str) -> None:
    """Print a success message.

    Args:
        message: Success message to display
    """
    if HAS_RICH:
        console.print(f"[bold green]✓ Success:[/bold green] {message}")
    else:
        print(f"✓ Success: {message}")


def print_warning(message: str) -> None:
    """Print a warning message.

    Args:
        message: Warning message to display
    """
    if HAS_RICH:
        console.print(f"[bold yellow]⚠ Warning:[/bold yellow] {message}")
    else:
        print(f"⚠ Warning: {message}")


def print_info(message: str) -> None:
    """Print an info message.

    Args:
        message: Info message to display
    """
    if HAS_RICH:
        console.print(f"[blue]ℹ[/blue] {message}")
    else:
        print(f"ℹ {message}")


# ============================================================================
# OUTPUT FORMATTING FUNCTIONS
# ============================================================================


def format_budget_breakdown(budget_breakdown: Dict[str, float]) -> None:
    """Display budget breakdown in a formatted table.

    Args:
        budget_breakdown: Dictionary with budget categories and amounts
    """
    if not budget_breakdown:
        print_info("No budget breakdown available")
        return

    print_section("Budget Breakdown")

    if HAS_RICH:
        table = Table(title="Budget Distribution", show_header=True)
        table.add_column("Category", style="cyan")
        table.add_column("Amount (USD)", style="green", justify="right")
        table.add_column("Percentage", style="yellow", justify="right")

        total = sum(budget_breakdown.values())
        for category, amount in sorted(budget_breakdown.items(), reverse=True):
            percentage = (amount / total * 100) if total > 0 else 0
            table.add_row(
                category.replace("_", " ").title(),
                f"${amount:,.2f}",
                f"{percentage:.1f}%"
            )

        table.add_row("", "", "")
        table.add_row(
            "[bold]Total[/bold]",
            f"[bold]${total:,.2f}[/bold]",
            "[bold]100.0%[/bold]"
        )

        console.print(table)
    else:
        total = sum(budget_breakdown.values())
        print(f"{'Category':<20} {'Amount (USD)':<15} {'Percentage':<15}")
        print("-" * 50)
        for category, amount in sorted(budget_breakdown.items(), reverse=True):
            percentage = (amount / total * 100) if total > 0 else 0
            print(f"{category.replace('_', ' ').title():<20} ${amount:>13,.2f} {percentage:>13.1f}%")
        print("-" * 50)
        print(f"{'Total':<20} ${total:>13,.2f} {100.0:>13.1f}%")


def format_selected_option(title: str, option: Dict[str, Any]) -> None:
    """Display selected option in a formatted panel.

    Args:
        title: Panel title (e.g., "Selected Flight")
        option: Dictionary with option details
    """
    if not option:
        print_warning(f"No {title} selected")
        return

    if HAS_RICH:
        # Format the option details
        details = []
        for key, value in option.items():
            formatted_key = key.replace("_", " ").title()
            if isinstance(value, (int, float)):
                if "price" in key.lower() or "cost" in key.lower():
                    formatted_value = f"${value:,.2f}"
                else:
                    formatted_value = f"{value:,.2f}"
            else:
                formatted_value = str(value)
            details.append(f"[cyan]{formatted_key}:[/cyan] {formatted_value}")

        panel_content = "\n".join(details)
        panel = Panel(
            panel_content,
            title=f"[bold green]✓ {title}[/bold green]",
            border_style="green",
            padding=(1, 2)
        )
        console.print(panel)
    else:
        print(f"\n{title}")
        print("-" * 50)
        for key, value in option.items():
            formatted_key = key.replace("_", " ").title()
            if isinstance(value, (int, float)):
                if "price" in key.lower() or "cost" in key.lower():
                    formatted_value = f"${value:,.2f}"
                else:
                    formatted_value = f"{value:,.2f}"
            else:
                formatted_value = str(value)
            print(f"{formatted_key}: {formatted_value}")


def format_itinerary(itinerary: str) -> None:
    """Display itinerary with syntax highlighting.

    Args:
        itinerary: Itinerary text (usually markdown)
    """
    print_section("Final Itinerary")

    if HAS_RICH and itinerary:
        # Try to render as markdown
        try:
            console.print(Markdown(itinerary))
        except Exception:
            # Fallback to plain text if markdown rendering fails
            console.print(itinerary)
    else:
        print(itinerary if itinerary else "No itinerary generated")


def format_alternative_suggestions(suggestions: str) -> None:
    """Display alternative suggestions.

    Args:
        suggestions: Suggestions text
    """
    print_section("Alternative Suggestions")

    if HAS_RICH and suggestions:
        try:
            console.print(Markdown(suggestions))
        except Exception:
            console.print(suggestions)
    else:
        print(suggestions if suggestions else "No suggestions available")


def format_state_summary(state: AgentState) -> None:
    """Display a summary of the final state.

    Args:
        state: Final agent state
    """
    print_section("Trip Planning Summary")

    if HAS_RICH:
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Property", style="cyan")
        table.add_column("Value")

        # Add key properties
        properties = [
            ("Destination", state.destination or "N/A"),
            ("Budget", f"${state.budget:,.2f}"),
            ("Duration", f"{state.duration} days"),
            ("Budget Feasible", "✓ Yes" if state.budget_feasible else "✗ No"),
            ("Status", "Success" if not state.error_message else "Error"),
        ]

        for prop, value in properties:
            table.add_row(prop, str(value))

        console.print(table)
    else:
        print(f"Destination: {state.destination or 'N/A'}")
        print(f"Budget: ${state.budget:,.2f}")
        print(f"Duration: {state.duration} days")
        print(f"Budget Feasible: {'Yes' if state.budget_feasible else 'No'}")
        print(f"Status: {'Success' if not state.error_message else 'Error'}")


# ============================================================================
# MAIN FUNCTIONS
# ============================================================================


def run_travel_planner(
    destination: str,
    budget: float,
    duration: int,
    departure_city: str = "New York, USA",
    preferences: Optional[Dict[str, Any]] = None,
    dry_run: bool = False,
    verbose: bool = False,
) -> Dict[str, Any]:
    """Main function to run the travel planner.

    This function:
    1. Validates inputs using TravelPlannerInput Pydantic model
    2. Creates initial state
    3. Loads and invokes the graph
    4. Returns formatted results

    Args:
        destination: Travel destination
        budget: Budget in USD
        duration: Trip duration in days
        departure_city: Departure city (default: "New York, USA")
        preferences: Optional preferences dict with keys:
            - dietary: "none", "vegetarian", "vegan", "halal"
            - accommodation_type: "hotel", "hostel", "airbnb"
            - activities: "adventure", "cultural", "relaxation", "nightlife"
        dry_run: If True, only validate inputs and return (no LLM calls)
        verbose: If True, enable debug logging

    Returns:
        Dictionary with the final state and formatted results

    Example:
        >>> result = run_travel_planner(
        ...     destination="Paris, France",
        ...     budget=2000,
        ...     duration=5,
        ...     preferences={"dietary": "vegetarian"}
        ... )
    """
    # Setup logging
    if verbose:
        logging.getLogger("src").setLevel(logging.DEBUG)
    else:
        logging.getLogger("src").setLevel(logging.INFO)

    print_section("Travel Planner - Starting", "Initializing...")

    # ========================================================================
    # 1. VALIDATE INPUTS
    # ========================================================================
    print_info("Validating input parameters...")

    try:
        # Calculate start and end dates
        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=duration)).strftime("%Y-%m-%d")

        # Create Pydantic validation model
        planner_input = TravelPlannerInput(
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            duration=duration,
            user_preferences=preferences or {},
        )

        print_success(f"Input validation passed")
        logger.info(f"Validated input: {planner_input}")

    except ValidationError as e:
        print_error("Input validation failed:")
        for error in e.errors():
            field = error["loc"][0]
            message = error["msg"]
            print_error(f"  • {field}: {message}")
        logger.error(f"Validation error: {e}")
        sys.exit(1)

    except ValueError as e:
        print_error(f"Invalid input: {str(e)}")
        logger.error(f"Value error: {e}")
        sys.exit(1)

    # ========================================================================
    # 2. DRY-RUN MODE
    # ========================================================================
    if dry_run:
        print_section("Dry-Run Mode", "No LLM calls will be made")
        print_info("This shows what would be planned:")

        # Create dummy state for display
        dummy_state = AgentState(
            destination=destination,
            budget=budget,
            duration=duration,
            budget_breakdown={
                "flights": budget * 0.40,
                "accommodation": budget * 0.35,
                "activities": budget * 0.15,
                "food": budget * 0.10,
            },
            budget_feasible=True,
        )

        print("\n")
        format_budget_breakdown(dummy_state.budget_breakdown)

        print_info("To run the actual planner, remove the --dry-run flag")

        return {
            "status": "dry_run",
            "state": dummy_state.model_dump(),
            "message": "Dry run completed. No LLM calls were made.",
        }

    # ========================================================================
    # 3. CREATE INITIAL STATE
    # ========================================================================
    print_info("Creating initial state...")

    initial_state = AgentState(
        destination=destination,
        budget=budget,
        duration=duration,
        start_date=planner_input.start_date,
        end_date=planner_input.end_date,
        context={
            "departure_city": departure_city,
            "preferences": preferences or {},
        },
    )

    logger.info(f"Created initial state for {destination}")

    # ========================================================================
    # 4. LOAD GRAPH
    # ========================================================================
    print_info("Loading travel planning graph...")

    try:
        graph = create_graph()
        print_success("Graph loaded successfully")
        logger.info("Graph created and compiled")
    except Exception as e:
        print_error(f"Failed to create graph: {str(e)}")
        logger.error(f"Graph creation error: {e}", exc_info=True)
        sys.exit(1)

    # ========================================================================
    # 5. INVOKE GRAPH
    # ========================================================================
    print_section("Executing Travel Plan", "Analyzing budget and searching for options...")

    try:
        result = graph.invoke(initial_state)
        logger.info("Graph execution completed successfully")

    except Exception as e:
        print_error(f"Graph execution failed: {str(e)}")
        logger.error(f"Execution error: {e}", exc_info=True)
        sys.exit(1)

    # ========================================================================
    # 6. FORMAT AND DISPLAY RESULTS
    # ========================================================================
    print_section("Results")

    # Convert result to AgentState if needed
    if isinstance(result, dict):
        final_state = AgentState(**result)
    else:
        final_state = result

    # Display summary
    format_state_summary(final_state)

    # Check for errors
    if final_state.error_message:
        print("\n")
        print_error(final_state.error_message)
        logger.warning(f"Trip planning resulted in error: {final_state.error_message}")

    # Display based on feasibility
    if final_state.budget_feasible:
        print("\n")
        format_budget_breakdown(final_state.budget_breakdown)

        if final_state.selected_flight:
            print("\n")
            format_selected_option("Selected Flight", final_state.selected_flight)

        if final_state.selected_hotel:
            print("\n")
            format_selected_option("Selected Hotel", final_state.selected_hotel)

        if final_state.context.get("final_itinerary"):
            print("\n")
            format_itinerary(final_state.context.get("final_itinerary", ""))

    else:
        # Show alternative suggestions if available
        if final_state.context.get("alternative_suggestions"):
            print("\n")
            format_alternative_suggestions(
                final_state.context.get("alternative_suggestions", "")
            )

    # ========================================================================
    # 7. RETURN RESULTS
    # ========================================================================
    print_section("Complete", "✓ Travel planning finished")

    return {
        "status": "success" if not final_state.error_message else "error",
        "state": final_state.model_dump(),
        "message": "Trip planning completed successfully"
        if not final_state.error_message
        else final_state.error_message,
    }


# ============================================================================
# CLI INTERFACE
# ============================================================================


def create_cli_parser() -> argparse.ArgumentParser:
    """Create and configure the CLI argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description="Travel Planner Agent - Plan your perfect trip",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  %(prog)s plan --destination "Paris, France" --budget 2000 --duration 5

  # With preferences
  %(prog)s plan --destination "Paris, France" --budget 2000 --duration 5 \\
    --dietary vegetarian --accommodation-type hotel

  # Dry-run mode (no LLM calls)
  %(prog)s plan --destination "Paris, France" --budget 2000 --duration 5 --dry-run

  # Verbose mode with debugging
  %(prog)s plan --destination "Paris, France" --budget 2000 --duration 5 --verbose
        """,
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # "plan" subcommand
    plan_parser = subparsers.add_parser(
        "plan",
        help="Plan a trip",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Required arguments
    plan_parser.add_argument(
        "--destination",
        required=True,
        type=str,
        help="Travel destination (e.g., 'Paris, France')",
        metavar="DESTINATION",
    )

    plan_parser.add_argument(
        "--budget",
        required=True,
        type=float,
        help="Budget in USD (must be > 0)",
        metavar="AMOUNT",
    )

    plan_parser.add_argument(
        "--duration",
        required=True,
        type=int,
        help="Trip duration in days (1-30)",
        metavar="DAYS",
    )

    # Optional arguments
    plan_parser.add_argument(
        "--departure-city",
        type=str,
        default="New York, USA",
        help="Departure city (default: New York, USA)",
        metavar="CITY",
    )

    plan_parser.add_argument(
        "--accommodation-type",
        type=str,
        choices=["hotel", "hostel", "airbnb"],
        help="Accommodation preference (hotel/hostel/airbnb)",
        metavar="TYPE",
    )

    plan_parser.add_argument(
        "--dietary",
        type=str,
        choices=["none", "vegetarian", "vegan", "halal"],
        help="Dietary preferences (none/vegetarian/vegan/halal)",
        metavar="DIET",
    )

    plan_parser.add_argument(
        "--activities",
        type=str,
        choices=["adventure", "cultural", "relaxation", "nightlife"],
        help="Activity preferences (adventure/cultural/relaxation/nightlife)",
        metavar="ACTIVITY",
    )

    # Flags
    plan_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry-run mode: validate inputs without making LLM calls",
    )

    plan_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose/debug logging",
    )

    return parser


def main() -> int:
    """CLI entry point.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_cli_parser()
    args = parser.parse_args()

    # Handle no command
    if not args.command:
        parser.print_help()
        return 0

    # Handle "plan" command
    if args.command == "plan":
        try:
            # Build preferences dict
            preferences = {}
            if args.accommodation_type:
                preferences["accommodation_type"] = args.accommodation_type
            if args.dietary:
                preferences["dietary"] = args.dietary
            if args.activities:
                preferences["activities"] = args.activities

            # Run planner
            result = run_travel_planner(
                destination=args.destination,
                budget=args.budget,
                duration=args.duration,
                departure_city=args.departure_city,
                preferences=preferences if preferences else None,
                dry_run=args.dry_run,
                verbose=args.verbose,
            )

            return 0 if result["status"] in ["success", "dry_run"] else 1

        except KeyboardInterrupt:
            print("\n")
            print_warning("Trip planning cancelled by user")
            return 1
        except Exception as e:
            print_error(f"Unexpected error: {str(e)}")
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

