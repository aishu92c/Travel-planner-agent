# Graph Visualization - Quick Reference

## 🚀 Quick Start

### Generate Visualization
```bash
python -m src.main --visualize
```

### Print Structure to Console
```bash
python -c "from src.utils.visualize import print_graph_structure; print_graph_structure()"
```

### Programmatic Usage
```python
from src.utils.visualize import generate_graph_visualization, print_graph_structure

# Generate documentation
result = generate_graph_visualization()
print(result['status'])
print(result['markdown_file'])

# Print structure
print_graph_structure()
```

---

## 📊 Output Files

| File | Purpose |
|------|---------|
| `docs/architecture/graph.md` | Comprehensive documentation with Mermaid diagram |
| `docs/architecture/graph.png` | PNG visualization (if graphviz installed) |

---

## 🎯 Functions

### generate_graph_visualization(output_dir="docs/architecture")

**Returns**:
```python
{
    'markdown_file': str,      # Path to .md file
    'png_file': str or None,   # Path to .png or None
    'mermaid_code': str,       # Mermaid diagram code
    'status': str              # Success/error message
}
```

**Example**:
```python
result = generate_graph_visualization()
print(f"Saved to: {result['markdown_file']}")
```

### print_graph_structure()

**Returns**: None (prints to console)

**Example**:
```python
print_graph_structure()
```

---

## 📋 Graph Nodes

| Node | Type | Purpose |
|------|------|---------|
| budget_analysis | Entry | Analyze budget feasibility |
| search_flights | Regular | Find best flight |
| search_hotels | Regular | Find best hotel |
| search_activities | Conditional | Find activities |
| generate_itinerary | Regular | Create itinerary |
| suggest_alternatives | Alternative | Budget suggestions |
| error_handler | Error | Handle errors |

---

## 🔄 Routing Logic

**After budget_analysis**:
- ✅ Feasible → search_flights
- ❌ Infeasible → suggest_alternatives
- ⚠️ Error → error_handler

**After search_hotels**:
- ✅ Hotel found → search_activities
- ❌ No hotel → generate_itinerary

---

## 💡 Installation (Optional)

For PNG generation:
```bash
pip install graphviz
brew install graphviz  # macOS
apt-get install graphviz  # Ubuntu
```

---

## ✨ Features

✅ Auto-generates Mermaid diagrams  
✅ Creates comprehensive markdown docs  
✅ Prints structure for debugging  
✅ Optional PNG support  
✅ Graceful error handling  
✅ Detailed logging  

---

**Version**: 1.0.0  
**Status**: Production Ready ✓

