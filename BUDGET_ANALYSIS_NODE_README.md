# Budget Analysis Node Documentation

## Overview

The `budget_analysis_node` is a LangGraph node function that analyzes and validates the feasibility of a travel plan based on budget constraints. It performs comprehensive budget analysis including breakdown allocation and regional minimum requirements.

**Location**: `src/nodes/planning_nodes.py`

## Function Signature

```python
def budget_analysis_node(state: AgentState) -> Dict[str, Any]:
    """Analyze and validate trip budget feasibility."""
```

## Parameters

### Input (AgentState)

The function expects an `AgentState` object with the following relevant fields:

- **`budget`** (float): The total budget available for the trip (in USD)
- **`destination`** (str | None): The travel destination name
- **`duration`** (int): Trip duration in days (1-30)

## Return Value

Returns a dictionary containing:

```python
{
    "budget_breakdown": {
        "flights": float,           # 40% of budget
        "accommodation": float,     # 35% of budget
        "activities": float,        # 15% of budget
        "food": float              # 10% of budget
    },
    "budget_feasible": bool,        # True if budget is sufficient
    "minimum_required_budget": float, # Minimum budget needed
    "analysis_summary": str,        # Human-readable summary
    "region": str,                  # Identified region
    "minimum_per_day": float        # Minimum per day for region
}
```

## Functionality

### Step 1: Budget Breakdown Calculation

The node allocates the total budget across four categories:

| Category | Percentage | Usage |
|----------|-----------|-------|
| Flights | 40% | International/domestic flights |
| Accommodation | 35% | Hotels, hostels, etc. |
| Activities | 15% | Tours, attractions, entertainment |
| Food | 10% | Meals and dining |

**Example**: For a $1000 budget:
- Flights: $400
- Accommodation: $350
- Activities: $150
- Food: $100

### Step 2: Region Identification

The node identifies the travel destination's region to determine appropriate minimum budget requirements.

**Supported Regions**:

1. **Asia** - $100/day
   - Keywords: Tokyo, Bangkok, Singapore, Bali, India, China, Vietnam, Thailand, etc.

2. **Europe** - $150/day
   - Keywords: Paris, London, Rome, Berlin, Madrid, Amsterdam, Barcelona, etc.

3. **Americas** - $120/day
   - Keywords: New York, Los Angeles, Toronto, Mexico City, Buenos Aires, etc.

4. **Africa** - $110/day
   - Keywords: Cairo, Cape Town, Marrakech, Johannesburg, etc.

5. **Oceania** - $130/day
   - Keywords: Sydney, Auckland, Fiji, Australia, New Zealand, etc.

**Default**: Unknown destinations default to **Asia** ($100/day)

### Step 3: Minimum Budget Calculation

```
minimum_required_budget = minimum_per_day × duration
```

**Examples**:
- Paris (Europe) for 10 days: $150 × 10 = $1,500
- Bangkok (Asia) for 14 days: $100 × 14 = $1,400
- New York (Americas) for 7 days: $120 × 7 = $840

### Step 4: Budget Feasibility Check

```python
budget_feasible = total_budget >= minimum_required_budget
```

The node compares the available budget against the minimum required budget:

- **Feasible**: When `total_budget >= minimum_required_budget`
- **Not Feasible**: When `total_budget < minimum_required_budget`

## Usage Examples

### Example 1: Feasible Budget (Paris)

```python
from src.agents.state import AgentState
from src.nodes.planning_nodes import budget_analysis_node

state = AgentState(
    destination="Paris",
    budget=3000.0,
    duration=10,
)

result = budget_analysis_node(state)

print(result)
# Output:
# {
#     "budget_breakdown": {
#         "flights": 1200.0,
#         "accommodation": 1050.0,
#         "activities": 450.0,
#         "food": 300.0
#     },
#     "budget_feasible": True,
#     "minimum_required_budget": 1500.0,
#     "analysis_summary": "Budget Analysis for Paris (10 days)\n...",
#     "region": "europe",
#     "minimum_per_day": 150
# }
```

**Analysis**:
- Region: Europe ($150/day minimum)
- Minimum required: $150 × 10 = $1,500
- Available: $3,000
- **Result**: ✓ Budget feasible (surplus: $1,500)

### Example 2: Infeasible Budget (Tokyo)

```python
state = AgentState(
    destination="Tokyo",
    budget=500.0,
    duration=7,
)

result = budget_analysis_node(state)

print(result["budget_feasible"])  # False
print(result["minimum_required_budget"])  # 700.0
```

**Analysis**:
- Region: Asia ($100/day minimum)
- Minimum required: $100 × 7 = $700
- Available: $500
- **Result**: ✗ Budget not feasible (deficit: $200)

### Example 3: Unknown Destination

```python
state = AgentState(
    destination="Atlantis",
    budget=1500.0,
    duration=10,
)

result = budget_analysis_node(state)

print(result["region"])  # "asia" (default)
print(result["budget_feasible"])  # True
```

**Analysis**:
- Region: Asia (default, since "Atlantis" is unknown)
- Minimum per day: $100
- Minimum required: $100 × 10 = $1,000
- Available: $1,500
- **Result**: ✓ Budget feasible

## Logging

The node uses Python's `logging` module to track analysis progress. Log levels:

- **INFO**: Main analysis steps, feasibility results
- **DEBUG**: Destination to region mapping
- **WARNING**: Unrecognized destinations, infeasible budgets

### Sample Log Output

```
======================================================================
Starting budget analysis node
======================================================================
Input parameters:
  Total Budget: $3000.00
  Destination: Paris
  Duration: 10 days

Step 1: Calculating budget breakdown...
Budget allocation:
  Flights: $1200.00 (40.0%)
  Accommodation: $1050.00 (35.0%)
  Activities: $450.00 (15.0%)
  Food: $300.00 (10.0%)

Step 2: Determining minimum required budget...
  Region identified: EUROPE
  Minimum per day for europe: $150/day
  Duration: 10 days
  Minimum required budget: $150 × 10 days = $1500.00

Step 3: Checking budget feasibility...
  ✓ BUDGET FEASIBLE
  Available budget: $3000.00
  Minimum required: $1500.00
  Surplus/flexibility: $1500.00

Step 4: Generating analysis summary...

Analysis Summary:
Budget Analysis for Paris (10 days)
Total Budget: $3000.00
Region: EUROPE
Minimum per day: $150
Minimum total required: $1500.00
Feasible: Yes

======================================================================
Budget analysis node completed successfully
======================================================================
```

## Region Identification Logic

The `identify_region()` helper function uses keyword matching:

```python
def identify_region(destination: str) -> str:
    """Identify region based on destination keywords."""
    destination_lower = destination.lower().strip()
    
    for region, keywords in REGION_KEYWORDS.items():
        if any(keyword in destination_lower for keyword in keywords):
            return region
    
    return 'asia'  # Default fallback
```

### Region Keywords

**Asia**: tokyo, bangkok, singapore, hong kong, bali, dubai, india, china, vietnam, korea, thailand, indonesia, philippines, malaysia, pakistan, sri lanka, japan

**Europe**: paris, london, rome, berlin, madrid, amsterdam, barcelona, prague, vienna, istanbul, venice, athens, lisbon, dublin, zurich, munich, budapest, scandinavia, italy, france, spain, germany, uk, ireland, netherlands, poland, greece, portugal, switzerland, austria, belgium, denmark, sweden, norway

**Americas**: new york, los angeles, chicago, san francisco, miami, boston, washington, denver, seattle, mexico city, cancun, buenos aires, toronto, vancouver, caribbean, jamaica, cuba, dominican, usa, united states, canada, mexico, brazil, argentina, peru, chile, colombia, costa rica

**Africa**: cairo, johannesburg, cape town, marrakech, nairobi, tanzania, kenya, morocco, egypt, south africa, uganda, ethiopia

**Oceania**: sydney, auckland, fiji, bali, australia, new zealand, samoa, polynesia, melanesia

## Error Handling

The node validates input and raises `ValueError` for:

- **Negative budget**: "Budget cannot be negative"
- **Non-positive duration**: "Duration must be positive"

```python
try:
    result = budget_analysis_node(state)
except ValueError as e:
    print(f"Invalid input: {e}")
```

## Integration with LangGraph

### Using in a Workflow

```python
from langgraph.graph import StateGraph
from src.nodes.planning_nodes import budget_analysis_node

# Create graph
graph = StateGraph(AgentState)

# Add node
graph.add_node("budget_analysis", budget_analysis_node)

# Add edge
graph.add_edge("input", "budget_analysis")
graph.add_edge("budget_analysis", "next_node")

# Compile
workflow = graph.compile()

# Execute
result = workflow.invoke({"destination": "Paris", "budget": 3000.0, "duration": 10})
```

### Using Result in Another Node

```python
def next_node(state: AgentState, budget_result: Dict) -> Dict:
    """Use budget analysis results for next planning step."""
    
    if budget_result["budget_feasible"]:
        # Plan with full budget
        state.budget_breakdown = budget_result["budget_breakdown"]
    else:
        # Suggest alternative trip or budget adjustment
        deficit = (budget_result["minimum_required_budget"] - 
                   state.budget)
        return {
            "error_message": f"Budget short by ${deficit:.2f}"
        }
    
    return {}
```

## Testing

The node is thoroughly tested with:

- **Region identification** (5 regions, 50+ destinations)
- **Budget calculations** (various amounts, edge cases)
- **Feasible scenarios** (multiple regions and durations)
- **Infeasible scenarios** (insufficient budgets)
- **Edge cases** (zero budget, 1-day trips, boundary conditions)
- **Error handling** (invalid inputs)
- **Rounding precision** (2 decimal places)

Run tests:

```bash
pytest test_budget_analysis_node.py -v
```

## Performance

- **Time Complexity**: O(1) - constant time for budget calculations
- **Space Complexity**: O(1) - fixed number of outputs
- **Execution**: Sub-millisecond for typical inputs

## Best Practices

1. **Always validate user input** before creating AgentState
2. **Use TravelPlannerInput model** for input validation:
   ```python
   from src.agents.state import TravelPlannerInput
   
   user_input = TravelPlannerInput(
       destination="Paris",
       budget=3000.0,
       duration=10
   )
   ```

3. **Handle budget_feasible flag** appropriately in workflow
4. **Suggest alternatives** when budget is not feasible
5. **Log analysis results** for audit trails

## Future Enhancements

Potential improvements for future versions:

1. **Seasonal pricing adjustments**
   - Higher rates for peak seasons
   - Lower rates for off-season travel

2. **Custom budget categories**
   - Allow user-defined allocation percentages
   - Add more specific categories (transport, shopping, etc.)

3. **Exchange rate handling**
   - Support multiple currencies
   - Real-time conversion rates

4. **Historical data integration**
   - Use actual trip costs from databases
   - Learn from past bookings

5. **Machine learning predictions**
   - Predict actual costs more accurately
   - Personalized recommendations

## Troubleshooting

### Issue: Unexpected region identification

**Problem**: Destination mapped to wrong region

**Solution**: Update `REGION_KEYWORDS` dictionary with destination aliases

```python
REGION_KEYWORDS['europe'].append('your_destination')
```

### Issue: Budget always shows infeasible

**Problem**: Minimum per day might be too high

**Solution**: Check minimum per day values and adjust based on market research

```python
MINIMUM_BUDGET_PER_DAY['asia'] = 80  # Adjust if needed
```

### Issue: Logging not showing

**Problem**: Logger not configured

**Solution**: Configure logging in your application:

```python
import logging

logging.basicConfig(level=logging.INFO)
```

## Related Files

- **State Definition**: `src/agents/state.py`
- **Tests**: `test_budget_analysis_node.py`
- **Other Nodes**: `src/nodes/planning_nodes.py`

## References

- LangGraph Documentation: https://langchain-ai.github.io/langgraph/
- AgentState Documentation: See `src/agents/state.py`
- Budget Analysis Examples: See examples section above

