#!/bin/bash

################################################################################
# Example 4: Budget Backpacking Trip to Southeast Asia
#
# This example demonstrates budget-conscious travel planning:
# - Destination: Bangkok, Thailand (Asia)
# - Budget: $1200 (tight budget for 8 days)
# - Duration: 8 days
# - Preferences: Hostel accommodation, adventure activities
#
# Expected Output:
# ✅ Budget Analysis: FEASIBLE (minimum budget area)
# ✅ Selected Flight: ~$480 (budget airlines)
# ✅ Selected Hotel: ~$420 (budget hostels, $3-4/night avg)
# ✅ Activities Budget: ~$180 (free/cheap attractions, street food)
# ✅ Food Budget: ~$120 (street food, local restaurants $2-3/meal)
# ✅ Budget itinerary with cost-saving tips
#
# Budget Breakdown for $1200:
#   • Flights: 40% = $480
#   • Accommodation: 35% = $420
#   • Activities: 15% = $180
#   • Food: 10% = $120
#
# Money-Saving Tips Included:
#   • Use public transportation
#   • Eat local street food
#   • Visit free attractions
#   • Take walking tours
#   • Stay in hostels with free breakfast
#
# Usage:
#   bash examples/budget_backpacking.sh
#   or
#   ./examples/budget_backpacking.sh
#
################################################################################

set -e  # Exit on any error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Example 4: Budget Backpacking in Southeast Asia               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Trip Details:"
echo "  • Destination: Bangkok, Thailand (Southeast Asia - Asia)"
echo "  • Budget: $1,200 USD (Budget Backpacking)"
echo "  • Duration: 8 days"
echo "  • Accommodation: Hostel"
echo "  • Dietary: None"
echo "  • Activities: Adventure (temples, street food tours, local culture)"
echo ""
echo "Expected Outcome:"
echo "  ✅ Budget will be marked as FEASIBLE"
echo "  ✅ Budget airline options ($400-500 roundtrip)"
echo "  ✅ Hostel accommodation (\$3-4/night average)"
echo "  ✅ Budget adventure activities:"
echo "     • Temple visits (free/low cost)"
echo "     • Street food tours (\$2-3 per meal)"
echo "     • Walking tours (\$3-5)"
echo "     • Night markets and local experiences"
echo "  ✅ Cost-conscious itinerary with budget tips"
echo ""
echo "Budget Breakdown:"
echo "  • Flights: $480 (40%)"
echo "  • Accommodation: $420 (35% - hostels ~\$3-4/night)"
echo "  • Activities: $180 (15% - temples, tours, experiences)"
echo "  • Food/Dining: $120 (10% - street food, local restaurants)"
echo ""
echo "Money-Saving Tips:"
echo "  • Use BTS/MRT for local transport (\$0.50-1 per trip)"
echo "  • Eat at street stalls and local markets (\$1-2 meals)"
echo "  • Free activities: Temples, markets, riverside walks"
echo "  • Walking tours usually \$3-5 or free"
echo "  • Hostels often include free breakfast"
echo ""
echo "Running command..."
echo ""

python3 -m src.main plan \
  --destination "Bangkok, Thailand" \
  --budget 1200 \
  --duration 8 \
  --accommodation-type hostel \
  --activities adventure

echo ""
echo "✅ Budget backpacking example completed!"
echo "   Notice the detailed cost-saving recommendations and budget breakdown."
echo ""

