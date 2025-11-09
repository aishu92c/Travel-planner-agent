#!/bin/bash

################################################################################
# Example 2: Insufficient Budget - Triggers Alternative Suggestions
#
# This example demonstrates budget constraint handling:
# - Destination: Tokyo, Japan (Asia)
# - Budget: $800 (insufficient for 7 days)
# - Duration: 7 days
# - Minimum Required: $700 (100/day for Asia + base costs)
# - Deficit: ~$200 or more after budget breakdown
#
# Expected Output:
# ❌ Budget Analysis: NOT FEASIBLE
# ✅ Alternative Suggestions provided:
#    • "Consider visiting Bangkok instead - $100/day vs $100+/day"
#    • "Reduce trip to 4 days instead of 7"
#    • "Stay in budget hostels instead of hotels"
#    • Money-saving tips specific to the region
# ❌ No itinerary will be generated (as budget is insufficient)
#
# Usage:
#   bash examples/insufficient_budget.sh
#   or
#   ./examples/insufficient_budget.sh
#
################################################################################

set -e  # Exit on any error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Example 2: Insufficient Budget - Alternatives Suggested       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Trip Details:"
echo "  • Destination: Tokyo, Japan (Asia)"
echo "  • Budget: $800 USD"
echo "  • Duration: 7 days"
echo "  • Minimum Required: ~$700-800 (100/day for Asia)"
echo ""
echo "Expected Outcome:"
echo "  ❌ Budget will be marked as NOT FEASIBLE"
echo "  ✅ Alternative suggestions will be provided:"
echo "     • Cheaper destination recommendations"
echo "     • Trip duration reduction options"
echo "     • Budget accommodation recommendations"
echo "     • Regional money-saving tips"
echo "  ❌ No full itinerary (insufficient budget)"
echo ""
echo "Running command..."
echo ""

python3 -m src.main plan \
  --destination "Tokyo, Japan" \
  --budget 800 \
  --duration 7

echo ""
echo "✅ Example completed - Note the alternative suggestions above!"
echo ""

