# 📚 Travel Planner Examples

This directory contains practical examples demonstrating different travel planning scenarios using the Travel Planner agent.

## 🚀 Quick Start

Run any example with:

```bash
bash examples/successful_planning.sh
./examples/luxury_trip.sh
# etc.
```

---

## 📋 Examples Overview

### 1. **successful_planning.sh** - Feasible Budget Trip ✅
**Scenario**: 5-day trip to Barcelona with sufficient budget

```bash
./examples/successful_planning.sh
```

**Parameters**:
- Destination: Barcelona, Spain
- Budget: $2,500
- Duration: 5 days
- Accommodation: Hotel (★★★★)
- Activities: Cultural
- Dietary: None

**Expected Output**:
- ✅ Budget Status: **FEASIBLE**
- ✅ Selected Flight: ~$400-500 (40% of budget)
- ✅ Selected Hotel: ~$180-210/night (35% of budget)
- ✅ Activities Budget: ~$375 (15% of budget)
- ✅ Food Budget: ~$250 (10% of budget)
- ✅ Day-by-day itinerary with cultural attractions
- ✅ Restaurant recommendations
- ✅ Practical travel tips for Barcelona

**Use Case**: Demonstrates successful workflow when budget is sufficient
**Learning**: See how the agent plans a realistic European city trip with cultural focus

**Budget Breakdown**:
```
Total Budget: $2,500
├─ Flights: 40% = $1,000
├─ Accommodation: 35% = $875
├─ Activities: 15% = $375
└─ Food: 10% = $250
```

---

### 2. **insufficient_budget.sh** - Budget Constraints ❌
**Scenario**: 7-day trip to Tokyo with insufficient budget

```bash
./examples/insufficient_budget.sh
```

**Parameters**:
- Destination: Tokyo, Japan
- Budget: $800
- Duration: 7 days
- Accommodation: Not specified (default)
- Activities: Not specified (default)
- Dietary: Not specified (default)

**Expected Output**:
- ❌ Budget Status: **NOT FEASIBLE**
- 📍 Minimum Required: ~$700-800 (Asia: $100/day base)
- 💡 Alternative Suggestions:
  ```
  1. Cheaper Destination: "Consider Bangkok instead - $100/day vs Tokyo's higher costs"
  2. Duration Reduction: "Try 4 days instead of 7"
  3. Budget Accommodation: "Stay in budget hostels ($3-4/night)"
  4. Cost-Saving Tips: Region-specific money-saving advice
  ```
- ❌ No itinerary generated (insufficient budget)

**Use Case**: Demonstrates error handling and alternative suggestion generation
**Learning**: See how the agent gracefully handles budget constraints with helpful alternatives

**Analysis**:
- Budget: $800
- Needed: ~$700-800 minimum
- Deficit: ~$0-100 AFTER allocation
- Solution: Agent suggests alternatives rather than failing

---

### 3. **luxury_trip.sh** - Premium Travel 🏖️
**Scenario**: 5-day luxury resort trip to Maldives

```bash
./examples/luxury_trip.sh
```

**Parameters**:
- Destination: Maldives
- Budget: $5,000 (Premium)
- Duration: 5 days
- Accommodation: Resort (5-star)
- Activities: Relaxation
- Dietary: None

**Expected Output**:
- ✅ Budget Status: **FEASIBLE** (with substantial surplus)
- ✅ Selected Flight: ~$2,000 (40% - international premium)
- ✅ Selected Resort: ~$1,750 (35% - $350/night 5-star)
- ✅ Activities Budget: ~$750 (15% - premium experiences)
- ✅ Food Budget: ~$500 (10% - fine dining)
- ✅ Luxury itinerary including:
  - Overwater bungalow recommendations
  - Water sports (snorkeling, diving, surfing)
  - Spa and wellness treatments
  - Fine dining restaurants
  - Sunset island excursions

**Use Case**: Demonstrates high-budget luxury travel planning
**Learning**: See how the agent plans premium experiences with substantial budget margins

**Budget Breakdown**:
```
Total Budget: $5,000
├─ Flights: 40% = $2,000 (Premium airlines)
├─ Accommodation: 35% = $1,750 (Resort $350/night)
├─ Activities: 15% = $750 (Premium experiences)
└─ Food: 10% = $500 (Fine dining)
```

**Luxury Elements**:
- Premium airline selection (comfort, amenities)
- 5-star resort with premium amenities
- Exclusive water sports and activities
- Spa treatments and wellness
- Fine dining experiences
- Private island tours

---

### 4. **budget_backpacking.sh** - Budget Backpacking 🎒
**Scenario**: 8-day budget backpacking trip to Bangkok

```bash
./examples/budget_backpacking.sh
```

**Parameters**:
- Destination: Bangkok, Thailand
- Budget: $1,200 (Tight budget)
- Duration: 8 days
- Accommodation: Hostel
- Activities: Adventure
- Dietary: None

**Expected Output**:
- ✅ Budget Status: **FEASIBLE** (tight margins)
- ✅ Selected Flight: ~$480 (40% - budget airlines)
- ✅ Selected Hostel: ~$420 (35% - $3-4/night average)
- ✅ Activities Budget: ~$180 (15% - cheap/free attractions)
- ✅ Food Budget: ~$120 (10% - street food $1-2/meal)
- ✅ Budget itinerary with cost-saving tips:
  - Free/cheap temples and attractions
  - Street food recommendations
  - Walking tours (free or $2-3)
  - Local market experiences
  - Public transportation tips
  - Hostel social activities

**Use Case**: Demonstrates budget-conscious travel planning
**Learning**: See how the agent maximizes experiences while minimizing costs

**Budget Breakdown**:
```
Total Budget: $1,200
├─ Flights: 40% = $480 (Budget airlines)
├─ Accommodation: 35% = $420 (Hostels $3-4/night)
├─ Activities: 15% = $180 (Free/cheap attractions)
└─ Food: 10% = $120 (Street food $1-2/meal)
```

**Money-Saving Tips**:
- Use BTS/MRT (Bangkok metro): $0.50-1 per trip
- Eat at street stalls: $1-3 per meal
- Visit temples: Free to $1 donation
- Walking tours: Free or $3-5
- Hostels: Often include free breakfast and WiFi
- Night markets: Free to explore, cheap to eat

**Cost Breakdown Per Day**:
```
8-Day Trip Average Daily Cost: ~$150
├─ Flight average: $60/day
├─ Accommodation: $52.50/day (hostels)
├─ Activities: $22.50/day (cheap attractions)
└─ Food: $15/day (street food)

Daily Discretionary Budget: ~$25-30
(For special meals, shopping, activities)
```

---

## 📊 Comparison Table

| Aspect | Successful | Insufficient | Luxury | Budget |
|--------|-----------|--------------|--------|---------|
| **Destination** | Barcelona | Tokyo | Maldives | Bangkok |
| **Budget** | $2,500 | $800 | $5,000 | $1,200 |
| **Duration** | 5 days | 7 days | 5 days | 8 days |
| **Accommodation** | Hotel ★★★★ | - | Resort ★★★★★ | Hostel |
| **Daily Cost** | $500 | $114 | $1,000 | $150 |
| **Feasible?** | ✅ YES | ❌ NO | ✅ YES | ✅ YES |
| **Result** | Full Plan | Alternatives | Luxury Plan | Budget Plan |

---

## 🎯 Regional Budget Minimum Rates

The agent uses region-specific minimum daily rates:

| Region | Min/Day | Example | Tokyo Budget | 7 days |
|--------|---------|---------|--------------|--------|
| **Asia** | $100 | Tokyo, Bangkok | $100 | $700 |
| **Europe** | $150 | Barcelona, Paris | N/A | N/A |
| **Americas** | $120 | NYC, Toronto | N/A | N/A |
| **Africa** | $110 | Cairo, Cape Town | N/A | N/A |
| **Oceania** | $130 | Sydney, Fiji | N/A | N/A |

---

## 💰 Understanding Budget Allocation

All examples use the same budget allocation formula:

```
Total Budget Allocation:
├─ Flights: 40% - International/domestic transport
├─ Accommodation: 35% - Hotels, hostels, resorts
├─ Activities: 15% - Tours, attractions, entertainment
└─ Food: 10% - Meals and dining experiences
```

**Example: $2,500 Budget**
```
Flights:        $1,000 (40%)
Accommodation:   $875  (35%)
Activities:      $375  (15%)
Food:            $250  (10%)
─────────────────────────
Total:         $2,500
```

---

## 🔄 Running All Examples

To run all examples in sequence:

```bash
#!/bin/bash
echo "Running all Travel Planner examples..."
echo ""

echo "1. Successful Planning Example"
./examples/successful_planning.sh
sleep 2

echo "2. Insufficient Budget Example"
./examples/insufficient_budget.sh
sleep 2

echo "3. Luxury Trip Example"
./examples/luxury_trip.sh
sleep 2

echo "4. Budget Backpacking Example"
./examples/budget_backpacking.sh

echo ""
echo "✅ All examples completed!"
```

---

## 📝 Key Learnings from Examples

### Example 1: Successful Planning
- **Demonstrates**: Happy path workflow
- **Key Points**:
  - Budget feasibility check
  - Intelligent flight/hotel selection
  - Budget allocation across categories
  - Complete itinerary generation
  - Practical recommendations

### Example 2: Insufficient Budget
- **Demonstrates**: Error handling and graceful degradation
- **Key Points**:
  - Budget analysis identifies insufficiency
  - Alternative suggestions provided
  - Helpful recommendations instead of failure
  - Cost-saving tips generated

### Example 3: Luxury Trip
- **Demonstrates**: High-budget planning
- **Key Points**:
  - Premium option selection
  - Substantial budget margin
  - Luxury amenities and experiences
  - Fine dining and exclusive activities

### Example 4: Budget Backpacking
- **Demonstrates**: Cost optimization
- **Key Points**:
  - Minimal budget management
  - Hostels and budget accommodations
  - Free/cheap attractions
  - Local food and experiences
  - Street-smart travel tips

---

## 🛠️ Customizing Examples

To create your own example, use this template:

```bash
#!/bin/bash

echo "Example: Your Trip Description"
echo ""

python -m src.main plan \
  --destination "Your Destination, Country" \
  --budget <your_budget> \
  --duration <days> \
  --departure-city "Your City, Country" \
  --accommodation-type <hotel|hostel|airbnb|resort> \
  --dietary <none|vegetarian|vegan|halal> \
  --activities <adventure|cultural|relaxation|nightlife>

echo "Done!"
```

**Available Options**:
- `--accommodation-type`: hotel, hostel, airbnb, resort
- `--dietary`: none, vegetarian, vegan, halal
- `--activities`: adventure, cultural, relaxation, nightlife

---

## 📊 Expected Outputs Explained

### Budget Feasible (✅)
```
Budget Analysis:
├─ Total Budget: $2,500
├─ Destination: Barcelona, Spain (Europe)
├─ Duration: 5 days
├─ Minimum Daily Rate: $150/day (Europe)
├─ Minimum Required: $750
├─ Budget Feasible: ✅ YES (Surplus: $1,750)
│
├─ Budget Breakdown:
│ ├─ Flights: $1,000 (40%)
│ ├─ Accommodation: $875 (35%)
│ ├─ Activities: $375 (15%)
│ └─ Food: $250 (10%)
│
└─ → Workflow continues to flight/hotel search
```

### Budget Not Feasible (❌)
```
Budget Analysis:
├─ Total Budget: $800
├─ Destination: Tokyo, Japan (Asia)
├─ Duration: 7 days
├─ Minimum Daily Rate: $100/day (Asia)
├─ Minimum Required: $700
├─ Budget Feasible: ❌ NO (Deficit: ~$0-100 after allocation)
│
└─ → Workflow routes to alternative suggestions
    ├─ Cheaper destinations
    ├─ Duration reduction options
    ├─ Budget accommodation tips
    └─ Money-saving recommendations
```

---

## 🔍 Monitoring & Logging

When running examples, you can monitor execution in real-time:

```bash
# View logs while example runs
tail -f logs/agent.log

# Or run with verbose flag
python -m src.main plan --destination "Barcelona, Spain" --budget 2500 --duration 5 --verbose
```

---

## 📚 Related Documentation

- **[README.md](../README.md)** - Main project documentation
- **[SETUP.md](../SETUP.md)** - Installation and setup
- **[docs/architecture/graph.md](../docs/architecture/graph.md)** - Workflow architecture
- **[TEST_TOOLS_DOCUMENTATION.md](../TEST_TOOLS_DOCUMENTATION.md)** - Testing guide

---

## ✨ Next Steps

1. **Run the Examples**: Try each example to see different scenarios
2. **Review Outputs**: Compare the outputs from different budget levels
3. **Create Custom Examples**: Use the template to create your own
4. **Check Logs**: Monitor `logs/agent.log` to see execution details
5. **Modify Parameters**: Try different destinations and budgets

---

**Status**: ✅ Production Ready | **Version**: 1.0.0 | **Last Updated**: November 8, 2025

