# Graph Visualization Module - Documentation

## 📋 Overview

Comprehensive visualization utilities for the Travel Planner LangGraph workflow.

**File**: `src/utils/visualize.py`  
**Lines**: ~500  
**Status**: ✅ Production Ready

---

## 🎯 Main Functions

### 1. generate_graph_visualization()

Generates comprehensive documentation of the graph workflow including Mermaid diagrams and markdown.

**Signature**:
```python
def generate_graph_visualization(output_dir: str = "docs/architecture") -> Dict[str, str]
```

**Parameters**:
- `output_dir` (str): Directory to save documentation (default: "docs/architecture")

**Returns**:
```python
{
    'markdown_file': '/path/to/graph.md',      # Full path to markdown documentation
    'png_file': '/path/to/graph.png' or None,  # PNG if graphviz installed, else None
    'mermaid_code': '...',                      # Raw Mermaid diagram code
    'status': 'Success message or error'
}
```

**Logic**:
1. Import and compile the LangGraph workflow
2. Extract graph structure
3. Generate Mermaid diagram code
4. Create output directory structure
5. Generate comprehensive markdown documentation with:
   - Title and overview
   - Mermaid diagram
   - Node descriptions
   - Routing logic explanation
   - Example workflows
   - Region budget tiers
   - Performance characteristics
6. Attempt PNG generation (optional, requires graphviz)

**Example**:
```python
from src.utils.visualize import generate_graph_visualization

# Generate visualization
result = generate_graph_visualization()

if result['status'].startswith('✓'):
    print(f"Markdown saved to: {result['markdown_file']}")
    if result['png_file']:
        print(f"PNG saved to: {result['png_file']}")
else:
    print(f"Error: {result['status']}")
```

**Output Files**:
- `docs/architecture/graph.md` - Markdown documentation with Mermaid diagram
- `docs/architecture/graph.png` - PNG visualization (if graphviz installed)

### 2. print_graph_structure()

Prints the graph structure to console for debugging and understanding.

**Signature**:
```python
def print_graph_structure() -> None
```

**Parameters**: None

**Returns**: None (prints to console)

**Output**:
```
======================================================================
TRAVEL PLANNER GRAPH STRUCTURE
======================================================================

NODES (7 total):
----------------------------------------------------------------------
  • budget_analysis         [entry]
    └─ Analyzes trip feasibility based on budget
  • search_flights          [regular]
    └─ Searches and selects best flight option
  • search_hotels           [regular]
    └─ Searches and selects best hotel option
  • search_activities       [regular]
    └─ Searches for activities at destination
  • generate_itinerary      [regular]
    └─ Generates detailed day-by-day itinerary
  • suggest_alternatives    [alternative]
    └─ Suggests budget-friendly alternatives
  • error_handler           [error]
    └─ Handles errors gracefully

EDGES (14 total):
----------------------------------------------------------------------
  budget_analysis
    ├─→ search_flights [CONDITIONAL]
    ├─→ suggest_alternatives [CONDITIONAL]
    └─→ error_handler [CONDITIONAL]
  search_flights
    └─→ search_hotels
  search_hotels
    ├─→ search_activities [CONDITIONAL]
    └─→ generate_itinerary [CONDITIONAL]
  search_activities
    └─→ generate_itinerary

WORKFLOW:
----------------------------------------------------------------------
  Entry Point: budget_analysis
  Exit Point:  END

CONDITIONAL ROUTING:
----------------------------------------------------------------------

  After budget_analysis:
    ├─ IF budget_feasible == True  → search_flights (main flow)
    ├─ IF budget_feasible == False → suggest_alternatives (alternative flow)
    └─ IF error set                → error_handler (error flow)
  
  After search_hotels:
    ├─ IF hotel selected → search_activities
    └─ IF no hotel       → generate_itinerary

EXAMPLE PATHS:
----------------------------------------------------------------------

  Successful Planning:
    budget_analysis → search_flights → search_hotels → 
    search_activities → generate_itinerary → END
  
  Insufficient Budget:
    budget_analysis → suggest_alternatives → END
  
  Error Handling:
    [Any Node] → error_handler → END

======================================================================
✓ Graph structure printed successfully
======================================================================
```

**Example**:
```python
from src.utils.visualize import print_graph_structure

print_graph_structure()
```

---

## 🚀 Integration with main.py

### Adding --visualize Flag

To integrate visualization with the CLI:

```python
# In src/main.py

import argparse
from src.utils.visualize import generate_graph_visualization, print_graph_structure

def create_cli_parser():
    parser = argparse.ArgumentParser()
    
    # ... other arguments ...
    
    parser.add_argument(
        '--visualize',
        action='store_true',
        help='Generate graph visualization and print structure'
    )
    
    return parser

def main():
    args = parse_args()
    
    # If --visualize flag is set
    if args.visualize:
        logger.info("Generating graph visualization...")
        result = generate_graph_visualization()
        print_graph_structure()
        logger.info(result['status'])
        if result['png_file']:
            logger.info(f"PNG generated: {result['png_file']}")
        return
    
    # ... rest of main function ...
```

### CLI Usage

```bash
# Generate visualization only
python -m src.main --visualize

# Output:
# ✓ Visualization created successfully
# 📄 Markdown: /path/to/docs/architecture/graph.md
# 🖼️  PNG:      /path/to/docs/architecture/graph.png

# Print graph structure to console
python -m src.main plan --destination "Paris" --budget 3000 --duration 5 --visualize
```

---

## 📊 Generated Documentation

### Markdown Output (docs/architecture/graph.md)

Contains:

1. **Overview**: Purpose and architecture of the graph
2. **Workflow Diagram**: Mermaid diagram showing all nodes and edges
3. **Node Descriptions**: 7 nodes with:
   - Purpose
   - Input/Output
   - Node type
   - Logic explanation
   - Selection criteria
   - Examples

4. **Conditional Routing**: Decision logic for branching
5. **Workflow Paths**: 3 example paths:
   - Successful planning
   - Budget insufficient
   - Error handling

6. **Region-Based Budgets**: Daily minimums by region
7. **Budget Allocation**: Percentage breakdown
8. **Performance Metrics**: Typical execution times
9. **Implementation Details**: Tech stack and components
10. **Extensibility Guide**: How to add new nodes/edges
11. **Testing Strategy**: Test coverage information
12. **Deployment Guide**: Production deployment steps

### Mermaid Diagram

Generates a visual flowchart showing:
- All 7 nodes with color coding
- Entry point (START)
- Exit point (END)
- Regular edges
- Conditional edges
- Decision nodes
- Node types:
  - Budget analysis (blue)
  - Search nodes (green)
  - Itinerary generation (yellow)
  - Alternatives (orange)
  - Error handling (red)

### PNG Output (Optional)

If graphviz is installed, generates a high-quality PNG image of the workflow diagram.

**Installation**:
```bash
pip install graphviz
# Also need system graphviz
brew install graphviz  # macOS
apt-get install graphviz  # Ubuntu
```

---

## 🔧 Helper Functions

### _create_manual_mermaid_diagram()

Creates a manual Mermaid diagram if automatic generation fails.

**Returns**: Mermaid code as string

### _create_markdown_documentation(mermaid_code)

Generates comprehensive markdown documentation.

**Parameters**:
- `mermaid_code` (str): Mermaid diagram code

**Returns**: Complete markdown as string

### _extract_nodes(graph)

Extracts nodes from graph structure.

**Returns**: Dict mapping node names to metadata

### _extract_edges(graph)

Extracts edges from graph structure.

**Returns**: List of (source, target, edge_type) tuples

### _print_conditional_routing()

Prints conditional routing logic to console.

### _print_example_paths()

Prints example workflow paths to console.

### _get_timestamp()

Gets current timestamp for documentation.

**Returns**: Formatted timestamp string

---

## 📁 Output Structure

```
docs/
├── architecture/
│   ├── graph.md          # Main documentation
│   └── graph.png         # Optional PNG diagram
```

---

## 🎯 Use Cases

### 1. Architecture Documentation

Generate documentation for team understanding:
```python
result = generate_graph_visualization()
print(f"Documentation saved to: {result['markdown_file']}")
```

### 2. Debugging

Understand graph structure during development:
```python
print_graph_structure()
```

### 3. Onboarding

Generate visualization when onboarding new team members:
```bash
python -m src.main --visualize
```

### 4. CI/CD Integration

Generate and version control the architecture diagram:
```bash
# In CI pipeline
python -c "from src.utils.visualize import generate_graph_visualization; \
           generate_graph_visualization(); print('Generated')"
```

### 5. Documentation Site

Embed Mermaid diagram in documentation website:
```markdown
<!-- Copy content from docs/architecture/graph.md -->
```

---

## ⚙️ Configuration

### Default Output Directory

```python
# Default
output_dir = "docs/architecture"

# Custom
result = generate_graph_visualization(output_dir="/custom/path")
```

### Directory Creation

Automatically creates directory structure if missing:
```
docs/
└── architecture/  # Auto-created
```

---

## 🔍 Error Handling

### Graceful Degradation

If auto-generation fails:
1. Falls back to manual Mermaid creation
2. Logs warning instead of error
3. Continues with documentation generation
4. PNG generation is optional

### Import Errors

If imports fail (e.g., graph module):
```python
try:
    from src.utils.visualize import generate_graph_visualization
except ImportError:
    print("Visualization module requires langgraph and other dependencies")
```

### Graphviz Not Available

PNG generation is optional:
```python
result = generate_graph_visualization()
if result['png_file']:
    print("PNG available")
else:
    print("PNG skipped (graphviz not installed)")
```

---

## 📊 Example Output

### Console Output

```
======================================================================
Generating graph visualization...
======================================================================

Step 1: Creating compiled graph...
✓ Graph created successfully

Step 2: Extracting graph structure...
✓ Graph structure extracted

Step 3: Generating Mermaid diagram...
✓ Mermaid diagram generated
  Mermaid code length: 1250 characters

Step 4: Creating output directory: docs/architecture...
✓ Directory created/verified: /Users/ab000746/Downloads/Travel-planner-agent/docs/architecture

Step 5: Generating markdown documentation...
✓ Markdown documentation saved: /Users/ab000746/Downloads/Travel-planner-agent/docs/architecture/graph.md
  File size: 15234 characters

Step 6: Attempting to generate PNG visualization...
✓ PNG visualization generated: /Users/ab000746/Downloads/Travel-planner-agent/docs/architecture/graph.png

======================================================================
Graph visualization completed successfully!
======================================================================
📄 Markdown: /Users/ab000746/Downloads/Travel-planner-agent/docs/architecture/graph.md
🖼️  PNG:      /Users/ab000746/Downloads/Travel-planner-agent/docs/architecture/graph.png

To view:
  Markdown: cat docs/architecture/graph.md
  Or open: /Users/ab000746/Downloads/Travel-planner-agent/docs/architecture/graph.md

======================================================================
TRAVEL PLANNER GRAPH STRUCTURE
======================================================================

NODES (7 total):
...
```

---

## ✨ Features

✅ **Automatic Diagram Generation** - Creates Mermaid diagrams automatically  
✅ **Comprehensive Documentation** - Detailed markdown with explanations  
✅ **Structure Printing** - Console output for debugging  
✅ **PNG Support** - Optional high-quality PNG visualization  
✅ **Error Handling** - Graceful degradation on failures  
✅ **Logging** - Detailed execution logging  
✅ **Type Hints** - Full type annotations  
✅ **Docstrings** - Comprehensive documentation  

---

## 🔐 Best Practices

1. **Run Visualization**: Generate after major workflow changes
2. **Version Control**: Commit generated markdown (not PNG)
3. **Documentation Site**: Embed Mermaid diagram in docs
4. **Team Sharing**: Use markdown for code reviews
5. **Debugging**: Use print_graph_structure() during development

---

## 📚 Related Files

- `src/graph.py` - Main graph definition
- `src/nodes/` - Node implementations
- `docs/architecture/graph.md` - Generated documentation
- `src/main.py` - CLI integration

---

**Status**: ✅ Complete and Production Ready  
**Version**: 1.0.0  
**Last Updated**: November 8, 2025

