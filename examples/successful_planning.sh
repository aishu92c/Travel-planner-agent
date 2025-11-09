#!/bin/bash

################################################################################
# Example 1: Successful Trip Planning to Barcelona
#
# This example demonstrates a successful trip planning scenario:
# - Destination: Barcelona, Spain (Europe)
# - Budget: $2500 (sufficient for the trip)
# - Duration: 5 days
# - Preferences: Hotel accommodation, cultural activities
#
# Expected Output:
# ✅ Budget Analysis: Feasible
# ✅ Selected Flight: ~$400-500 (40% of budget)
# ✅ Selected Hotel: ~$900-1050 (35% of budget, ~$180-210/night)
# ✅ Activities Budget: ~$375 (15% remaining)
# ✅ Food Budget: ~$250 (10% remaining)
# ✅ Complete itinerary generated with day-by-day activities
#
# Usage:
#   bash examples/successful_planning.sh
#   or
#   ./examples/successful_planning.sh
#
################################################################################

set -e  # Exit on any error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Example 1: Successful Trip Planning to Barcelona              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Trip Details:"
echo "  • Destination: Barcelona, Spain (Europe)"
echo "  • Budget: $2,500 USD"
echo "  • Duration: 5 days"
echo "  • Departure City: London, UK"
echo "  • Accommodation: Hotel"
echo "  • Dietary: None"
echo "  • Activities: Cultural"
echo ""
echo "Expected Outcome:"
echo "  ✅ Budget will be marked as FEASIBLE"
echo "  ✅ Flight will be selected within budget ($400-500)"
echo "  ✅ Hotel will be selected (★★★★ rating, $180-210/night)"
echo "  ✅ Activities and dining recommendations included"
echo "  ✅ Day-by-day itinerary will be generated"
echo ""
echo "Running command..."
echo ""

python3 -m src.main plan \
  --destination "Barcelona, Spain" \
  --budget 2500 \
  --duration 5 \
  --departure-city "London, UK" \
  --accommodation-type hotel \
  --dietary none \
  --activities cultural

echo ""
echo "✅ Example completed successfully!"
echo ""

