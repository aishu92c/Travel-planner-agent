#!/bin/bash

################################################################################
# Example 3: Luxury Trip Planning to Maldives
#
# This example demonstrates high-budget luxury travel planning:
# - Destination: Maldives (Oceania)
# - Budget: $5000 (premium budget)
# - Duration: 5 days
# - Preferences: Resort accommodation, relaxation activities
#
# Expected Output:
# ✅ Budget Analysis: FEASIBLE (substantial margin)
# ✅ Selected Flight: ~$2000 (international, premium airlines)
# ✅ Selected Hotel: ~$1750 (★★★★★ resort, $350/night)
# ✅ Activities Budget: ~$750 (water sports, spa, excursions)
# ✅ Food Budget: ~$500 (fine dining options)
# ✅ Luxury itinerary with premium recommendations
#
# Budget Breakdown for $5000:
#   • Flights: 40% = $2,000
#   • Accommodation: 35% = $1,750
#   • Activities: 15% = $750
#   • Food: 10% = $500
#
# Usage:
#   bash examples/luxury_trip.sh
#   or
#   ./examples/luxury_trip.sh
#
################################################################################

set -e  # Exit on any error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Example 3: Luxury Trip Planning to Maldives                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Trip Details:"
echo "  • Destination: Maldives (Oceania - Tropical Paradise)"
echo "  • Budget: $5,000 USD (Premium)"
echo "  • Duration: 5 days"
echo "  • Accommodation: Resort (5-star)"
echo "  • Dietary: None"
echo "  • Activities: Relaxation (water sports, spa, diving)"
echo ""
echo "Expected Outcome:"
echo "  ✅ Budget will be marked as FEASIBLE with substantial surplus"
echo "  ✅ Premium flight options selected"
echo "  ✅ Luxury resort accommodation ($300-400/night)"
echo "  ✅ Premium activities:"
echo "     • Water sports (snorkeling, diving)"
echo "     • Spa and wellness treatments"
echo "     • Island excursions"
echo "     • Fine dining experiences"
echo "  ✅ Comprehensive luxury itinerary generated"
echo ""
echo "Budget Breakdown:"
echo "  • Flights: $2,000 (40%)"
echo "  • Accommodation: $1,750 (35%)"
echo "  • Activities: $750 (15%)"
echo "  • Food/Dining: $500 (10%)"
echo ""
echo "Running command..."
echo ""

python3 -m src.main plan \
  --destination "Maldives" \
  --budget 5000 \
  --duration 5 \
  --accommodation-type resort \
  --activities relaxation

echo ""
echo "✅ Luxury example completed!"
echo "   Notice the substantial budget available for premium experiences."
echo ""

