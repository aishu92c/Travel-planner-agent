# Travel Planner - Main Module Quick Reference

## 🚀 Quick Start

### CLI (Command Line Interface)

```bash
# Basic usage
python -m src.main plan --destination "Paris, France" --budget 2000 --duration 5

# With preferences
python -m src.main plan \
  --destination "Paris, France" \
  --budget 2000 \
  --duration 5 \
  --dietary vegetarian \
  --accommodation-type hotel \
  --activities cultural

# Dry-run mode (no LLM calls)
python -m src.main plan --destination "Paris, France" --budget 2000 --duration 5 --dry-run

# Verbose mode (debug logging)
python -m src.main plan --destination "Paris, France" --budget 2000 --duration 5 --verbose
```

### Programmatic API

```python
from src.main import run_travel_planner

result = run_travel_planner(
    destination="Paris, France",
    budget=2000,
    duration=5,
    preferences={
        "dietary": "vegetarian",
        "accommodation_type": "hotel",
        "activities": "cultural"
    }
)

# Access results
if result["status"] == "success":
    state = result["state"]
    print(f"Budget feasible: {state['budget_feasible']}")
    print(f"Flight selected: {state.get('selected_flight', {}).get('airline')}")
    print(f"Hotel selected: {state.get('selected_hotel', {}).get('name')}")
```

---

## 📋 Arguments Reference

### Required Arguments

| Argument | Type | Description | Example |
|----------|------|-------------|---------|
| `--destination` | str | Travel destination | "Paris, France" |
| `--budget` | float | Budget in USD (must be > 0) | 2000 |
| `--duration` | int | Trip duration in days (1-30) | 5 |

### Optional Arguments

| Argument | Type | Choices | Default | Description |
|----------|------|---------|---------|-------------|
| `--departure-city` | str | Any city | "New York, USA" | Where you're departing from |
| `--accommodation-type` | str | hotel, hostel, airbnb | None | Accommodation preference |
| `--dietary` | str | none, vegetarian, vegan, halal | None | Dietary restrictions |
| `--activities` | str | adventure, cultural, relaxation, nightlife | None | Activity preference |
| `--dry-run` | flag | - | False | Test without LLM calls |
| `--verbose` | flag | - | False | Enable debug logging |

---

## 🎯 Use Cases

### Basic Trip Planning
```bash
python -m src.main plan \
  --destination "Barcelona, Spain" \
  --budget 2500 \
  --duration 6
```

### Budget-Conscious Travel
```bash
python -m src.main plan \
  --destination "Bangkok, Thailand" \
  --budget 800 \
  --duration 10 \
  --accommodation-type hostel
```

### Luxury Travel
```bash
python -m src.main plan \
  --destination "Tokyo, Japan" \
  --budget 5000 \
  --duration 5 \
  --accommodation-type hotel \
  --activities cultural \
  --dietary none
```

### Adventure Trip
```bash
python -m src.main plan \
  --destination "New Zealand" \
  --budget 3500 \
  --duration 7 \
  --activities adventure
```

### Vegan Traveler
```bash
python -m src.main plan \
  --destination "Berlin, Germany" \
  --budget 1800 \
  --duration 4 \
  --dietary vegan \
  --accommodation-type airbnb
```

---

## 📊 Output Examples

### Success Output
```
====================================================================
Trip Planning Summary
====================================================================

Property              Value
──────────────────────────────────────────────────────────────────
Destination           Paris, France
Budget                $2,000.00
Duration              5 days
Budget Feasible       ✓ Yes
Status                Success

====================================================================
Budget Breakdown
====================================================================

Category              Amount (USD)    Percentage
──────────────────────────────────────────────────────────────────
Flights               $800.00         40.0%
Accommodation         $700.00         35.0%
Activities            $300.00         15.0%
Food                  $200.00         10.0%
──────────────────────────────────────────────────────────────────
Total                 $2,000.00       100.0%

✓ Selected Flight
────────────────────────────────────────────────────────────────
Airline: Air France
Departure: 2024-06-01 10:00 AM
Arrival: 2024-06-01 4:30 PM (local time)
Price: $600.00
Stops: 0
Duration: 8 hours 30 minutes

✓ Selected Hotel
────────────────────────────────────────────────────────────────
Name: Hotel Le Marais
Location: Paris, France
Rating: 4.5/5.0
Price Per Night: $140.00
Total for 5 nights: $700.00
Amenities: WiFi, Breakfast, Gym, Free cancellation

====================================================================
Final Itinerary
====================================================================

# 5-Day Paris Itinerary

## Day 1: Arrival & Orientation
**Morning**: Arrive at CDG airport, take RER to hotel
**Afternoon**: Check-in, rest, explore Le Marais neighborhood
**Evening**: Dinner at Café de Flore (vegetarian options)

Cost estimate: $200 (includes transport and meals)

[... itinerary continues ...]
```

### Insufficient Budget Output
```
✗ Error: Your budget is insufficient for the desired travel dates and destination.

====================================================================
Alternative Suggestions
====================================================================

# 3 Budget-Friendly Alternatives

## 1. Cheaper Nearby Destination
Consider Lisbon, Portugal instead of Paris. Similar charm but 30% cheaper.
Average cost: $1,400 for 5 days

## 2. Ways to Reduce Trip Cost
- Reduce duration from 5 to 3 days (save ~$600)
- Use hostels instead of hotels (save ~$200/night)
- Book budget airlines in advance (save ~$150)

## 3. Money-Saving Tips for Paris
- Visit free attractions: Sacré-Cœur, Pont des Arts
- Use metro pass (10 journeys): €17.15
- Eat at bistros vs. tourist restaurants: Save 50%
```

---

## 🔧 Dry-Run Mode

Perfect for testing and validation without making LLM calls:

```bash
python -m src.main plan \
  --destination "Paris, France" \
  --budget 2000 \
  --duration 5 \
  --dry-run
```

**Output**:
- Input validation results
- Budget breakdown calculation
- No API calls or LLM invocations
- `status: "dry_run"`

---

## 🐛 Debugging

### Verbose Mode
Enable detailed logging to troubleshoot issues:

```bash
python -m src.main plan \
  --destination "Paris, France" \
  --budget 2000 \
  --duration 5 \
  --verbose
```

Shows:
- Detailed state transitions
- Graph execution steps
- Tool call details
- Token usage information
- Error stack traces

### Common Issues

| Issue | Solution |
|-------|----------|
| "Budget must be > 0" | Ensure budget is a positive number |
| "Duration must be between 1 and 30" | Set duration between 1-30 days |
| "Invalid destination" | Use a recognizable city/country name |
| "Graph execution failed" | Try --verbose flag for details, check API keys |
| "No rich output" | Install rich: `pip install rich>=13.0.0` |

---

## 📦 Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install rich for beautiful output:
```bash
pip install rich>=13.0.0
```

3. Set up environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Run:
```bash
python -m src.main plan --destination "Paris, France" --budget 2000 --duration 5
```

---

## 📚 File Structure

```
src/
├── main.py                    ← Main module (you are here)
├── agents/
│   └── state.py              ← AgentState & TravelPlannerInput models
├── graph.py                  ← LangGraph workflow
├── nodes/
│   ├── planning_nodes.py      ← Budget analysis, alternatives
│   ├── tool_nodes.py          ← Flight/hotel search
│   └── itinerary_nodes.py     ← Itinerary generation
└── config/
    └── settings.py            ← Configuration management
```

---

## 🔗 Related Documentation

- **MAIN_MODULE_DOCUMENTATION.md**: Complete reference guide
- **GRAPH_README.md**: LangGraph workflow details
- **TOOL_NODES_README.md**: Search & selection logic
- **BUDGET_ANALYSIS_NODE_README.md**: Budget calculations
- **ITINERARY_NODES_README.md**: Itinerary generation

---

## 💡 Tips & Tricks

### Tip 1: Save Results to File
```python
import json
result = run_travel_planner(...)
with open("trip.json", "w") as f:
    json.dump(result["state"], f, indent=2)
```

### Tip 2: Batch Planning
```python
destinations = ["Paris", "London", "Berlin"]
for dest in destinations:
    result = run_travel_planner(
        destination=dest,
        budget=2000,
        duration=5
    )
```

### Tip 3: Test with Dry-Run First
```bash
# Validate inputs first
python -m src.main plan --destination "Paris" --budget 2000 --duration 5 --dry-run

# Then run full planning
python -m src.main plan --destination "Paris" --budget 2000 --duration 5
```

### Tip 4: Use in Scripts
```bash
#!/bin/bash
python -m src.main plan \
  --destination "Paris, France" \
  --budget 2000 \
  --duration 5 \
  --verbose > trip_log.txt 2>&1
```

---

## 🎓 Learning Resources

1. **For CLI Users**:
   - Run: `python -m src.main --help`
   - Run: `python -m src.main plan --help`
   - Try examples in "Use Cases" section above

2. **For Developers**:
   - Review `src/main.py` source code
   - Check `MAIN_MODULE_DOCUMENTATION.md`
   - Run `test_main.py` for testing

3. **For Integration**:
   - Import `run_travel_planner` function
   - Pass required parameters
   - Process returned dictionary

---

## 📞 Support

For issues or questions:

1. Run with `--verbose` flag to see detailed logs
2. Check `MAIN_MODULE_DOCUMENTATION.md` for comprehensive docs
3. Review error messages (they're user-friendly!)
4. Check GraphREADME.md for workflow details

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Status**: Production Ready ✓

