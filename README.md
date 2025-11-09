# 🌍 Travel Planner AI Agent

Intelligent travel planning agent using LangGraph and LLM orchestration. Automatically plans trips, breaks down budgets, searches for flights and hotels, and generates personalized itineraries.

## 🎯 Overview

The Travel Planner is an AI-powered agent that:
- Analyzes trip budgets and validates feasibility
- Searches for flights, hotels, and activities
- Creates personalized day-by-day itineraries
- Provides alternative suggestions when budget is insufficient
- Handles errors gracefully with helpful feedback

**Perfect for**: Travel planning automation, budget optimization, preference-based travel recommendations.

## ✨ Features

✅ **Budget-Aware Planning**
- Automatic budget breakdown (40% flights, 35% accommodation, 15% activities, 10% food)
- Region-specific minimum daily rates (Asia: $100, Europe: $150, Americas: $120, etc.)
- Feasibility checking with deficit calculation
- Alternative suggestions when budget insufficient

✅ **Multi-Tool Coordination**
- Search and filter flights by price and stops
- Search and filter hotels by rating and price
- Search activities by destination and preferences
- Intelligent selection algorithms for best options

✅ **Smart Routing**
- Conditional branching based on budget feasibility
- Alternative flow for insufficient budgets
- Error handling and graceful degradation
- State preservation throughout workflow

✅ **Personalized Itineraries**
- Day-by-day activity planning
- Restaurant suggestions matching dietary preferences
- Practical travel tips (transport, customs, safety)
- Cost tracking and budget allocation
- Markdown formatting with clear sections

✅ **Production Quality**
- Comprehensive error handling
- Detailed logging throughout execution
- Type hints and validation
- 42+ integration and unit tests
- 2,000+ lines of documentation

## 🏗️ Architecture

### Multi-Step Workflow

The Travel Planner uses LangGraph to orchestrate a 7-node workflow:

```
┌─────────────────────────────────────────────┐
│     1. Budget Analysis (Entry Point)         │
│     • Validate budget feasibility            │
│     • Calculate budget breakdown             │
│     • Identify region and rates              │
└────────────┬────────────────────────────────┘
             │
             ├─ Feasible ──────┐
             ├─ Insufficient ──┤
             └─ Error ────────┐
                              │
        ┌─────────────────────┴──────────────────────┐
        │                                             │
        v                                             v
┌────────────────────┐                    ┌────────────────────────┐
│ 2. Search Flights  │                    │ 6. Suggest Alternatives│
│ (Filtered/Scored)  │                    │ (Budget Options)       │
└────────────┬───────┘                    └────────────┬───────────┘
             │                                          │
             v                                          v
┌────────────────────┐                    ┌────────────────────────┐
│ 3. Search Hotels   │                    │ 7. Error Handler       │
│ (Best Rated)       │                    │ (Graceful Errors)      │
└────────────┬───────┘                    └────────────┬───────────┘
             │                                          │
             ├─ Hotel Found ────┐                      │
             │                  │                      │
             v                  v                      │
┌──────────────────────┐  ┌────────────────────┐     │
│ 4. Search Activities │  │ 5. Generate         │     │
│ (Preferences)        │  │    Itinerary (No    │     │
└──────────┬───────────┘  │    Activities)      │     │
           │              └──────────┬──────────┘     │
           v                         │                │
┌────────────────────────┐            v                │
│ 5. Generate Itinerary  │      ┌──────────────────┐ │
│ (Full Plan)            │      │      END         │◄┤
└──────────────┬─────────┘      └──────────────────┘ │
               │                                      │
               └──────────────────────────────────────┘
                      v
                 ┌──────────────────┐
                 │      END         │
                 └──────────────────┘
```

### Key Components

**1. Budget Analysis Node** - Entry point
- Analyzes trip feasibility based on destination and budget
- Calculates budget allocation percentages
- Identifies region and minimum daily requirements
- Sets workflow direction based on feasibility

**2. Search Nodes** - Data gathering
- `search_flights`: Finds flights, filters by budget, scores by price + stops
- `search_hotels`: Finds hotels, filters by budget, ranks by rating
- `search_activities`: Finds activities matching preferences

**3. Planning Node** - Itinerary generation
- Uses LLM to create day-by-day itinerary
- Includes activities, restaurants, tips, cost tracking
- Formats as structured markdown
- Tracks budget allocation

**4. Alternative Suggestions Node** - Fallback
- Uses LLM to suggest budget-friendly alternatives
- Proposes cheaper destinations, reduced trips, budget accommodations
- Provides money-saving tips

**5. Error Handler Node** - Safety net
- Catches and formats errors gracefully
- Provides helpful user-facing messages
- Logs technical details for debugging

### State Management

Uses **LangGraph's StateGraph** with typed **AgentState**:

```python
class AgentState(TypedDict):
    # Input
    destination: str
    budget: float
    duration: int
    
    # Processing
    budget_breakdown: Dict[str, float]
    budget_feasible: bool
    selected_flight: Dict[str, Any]
    selected_hotel: Dict[str, Any]
    
    # Output
    final_itinerary: str
    error_message: Optional[str]
```

### Conditional Routing

**After budget_analysis**:
- ✅ Feasible ($3000 ≥ minimum) → `search_flights`
- ❌ Insufficient ($500 < minimum) → `suggest_alternatives`
- ⚠️ Error → `error_handler`

**After search_hotels**:
- ✅ Hotel found → `search_activities`
- ❌ No hotel → `generate_itinerary` (skip activities)

## 🚀 Setup

### Prerequisites

- Python 3.10+
- OpenAI API key (get from https://platform.openai.com/api-keys)

### Installation

```bash
# Clone repository
git clone <repository-url>
cd Travel-planner-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install optional dependencies for visualization
pip install graphviz  # For PNG diagram generation
brew install graphviz  # macOS
apt-get install graphviz  # Ubuntu

# Configure environment
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...
```

**Need help?** See [SETUP.md](SETUP.md) for detailed troubleshooting.

## 📖 Usage

### Command Line

```bash
# Basic trip planning
python -m src.main plan \
  --destination "Barcelona, Spain" \
  --budget 2500 \
  --duration 7

# With preferences
python -m src.main plan \
  --destination "Tokyo, Japan" \
  --budget 3000 \
  --duration 5 \
  --dietary vegetarian \
  --accommodation-type hotel \
  --activities cultural

# Dry-run mode (validation only, no LLM calls)
python -m src.main plan \
  --destination "Paris, France" \
  --budget 2000 \
  --duration 5 \
  --dry-run

# Verbose mode (debug logging)
python -m src.main plan \
  --destination "Berlin, Germany" \
  --budget 1800 \
  --duration 4 \
  --verbose

# View CLI help
python -m src.main plan --help
```

### Python API

```python
from src.main import run_travel_planner

# Basic usage
result = run_travel_planner(
    destination="Paris, France",
    budget=2000,
    duration=5
)

# With preferences
result = run_travel_planner(
    destination="Tokyo, Japan",
    budget=3000,
    duration=5,
    preferences={
        "dietary": "vegetarian",
        "accommodation_type": "hotel",
        "activities": "cultural"
    }
)

# Process results
if result["status"] == "success":
    state = result["state"]
    print(f"Budget Feasible: {state['budget_feasible']}")
    print(f"Selected Flight: {state['selected_flight']['airline']}")
    print(f"Selected Hotel: {state['selected_hotel']['name']}")
    print(f"Itinerary:\n{result['final_itinerary']}")
else:
    print(f"Error: {result['error']}")
```

### Visualization

```bash
# Generate architecture diagram
python -m src.main --visualize

# Outputs:
# - docs/architecture/graph.md (comprehensive documentation)
# - docs/architecture/graph.png (diagram, requires graphviz)
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test suite
pytest tests/test_integration.py -v           # End-to-end workflows
pytest tests/test_tools.py -v                 # Unit tests for tools
pytest tests/test_main.py -v                  # CLI and API tests

# Run with coverage report
pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html in browser

# Run specific test
pytest tests/test_integration.py::TestSuccessfulWorkflow::test_successful_planning_workflow -v

# Stop on first failure
pytest tests/ -x

# Show print statements
pytest tests/ -s

# Run with timeout protection
pytest tests/test_integration.py --timeout=30
```

**Test Coverage**:
- ✅ 42+ tool tests (budget, flights, hotels, regions)
- ✅ 30+ integration tests (workflows, edge cases)
- ✅ 4+ main module tests (CLI, API)
- ✅ Coverage: >90%

## 📊 Project Structure

```
Travel-planner-agent/
├── src/
│   ├── __init__.py
│   ├── main.py                      # CLI and API entry point
│   ├── graph.py                     # LangGraph workflow definition
│   ├── agents/
│   │   ├── state.py                 # AgentState TypedDict + Pydantic models
│   │   └── __init__.py
│   ├── nodes/
│   │   ├── planning_nodes.py         # Budget analysis, alternatives, itinerary
│   │   ├── tool_nodes.py             # Flight/hotel/activity search
│   │   ├── itinerary_nodes.py        # Itinerary generation
│   │   └── __init__.py
│   ├── config/
│   │   ├── settings.py               # Pydantic settings (API keys, models)
│   │   ├── environments/             # Environment configurations
│   │   └── __init__.py
│   ├── utils/
│   │   ├── visualize.py              # Graph visualization utilities
│   │   ├── logger.py                 # Logging configuration
│   │   ├── validators.py             # Input validation
│   │   ├── retry.py                  # Retry logic
│   │   ├── error_handler.py           # Error handling
│   │   └── __init__.py
│   ├── api/
│   │   ├── models.py                 # API request/response models
│   │   ├── routes/                   # API endpoints
│   │   └── __init__.py
│   ├── observability/
│   │   ├── logging.py                # Logging utilities
│   │   ├── metrics.py                # Metrics tracking
│   │   └── __init__.py
│   └── cache/
│       ├── __init__.py
│
├── tests/
│   ├── test_main.py                  # CLI and API tests
│   ├── test_tools.py                 # Unit tests (42+ cases)
│   ├── test_integration.py            # E2E tests (30+ cases)
│   ├── conftest.py                   # Pytest fixtures
│   └── unit/
│
├── docs/
│   ├── architecture/
│   │   └── graph.md                  # Generated graph documentation
│   └── README.md                     # This file
│
├── requirements.txt                  # Dependencies
├── requirements-dev.txt               # Dev dependencies
├── .env.example                      # Environment template
├── SETUP.md                          # Installation guide
├── README.md                         # This file
└── Makefile                          # Common commands

```

## 📚 Documentation

- **[SETUP.md](SETUP.md)** - Installation and troubleshooting
- **[docs/architecture/graph.md](docs/architecture/graph.md)** - Detailed workflow architecture with Mermaid diagrams
- **[VISUALIZATION_DOCUMENTATION.md](VISUALIZATION_DOCUMENTATION.md)** - How to use visualization utilities
- **[TEST_TOOLS_DOCUMENTATION.md](TEST_TOOLS_DOCUMENTATION.md)** - Unit test documentation
- **[TEST_INTEGRATION_DOCUMENTATION.md](TEST_INTEGRATION_DOCUMENTATION.md)** - Integration test documentation
- **[MAIN_MODULE_DOCUMENTATION.md](MAIN_MODULE_DOCUMENTATION.md)** - CLI and API documentation

## 🔧 Development

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type checking
mypy src/

# View graph visualization
python -m src.main --visualize

# Test with coverage
pytest tests/ --cov=src --cov-report=html
```

## 📦 Key Dependencies

- **LangGraph** (0.2.50+) - Multi-step workflow orchestration
- **LangChain** - LLM framework and tools
- **Pydantic** (2.9.0+) - Data validation
- **OpenAI** - LLM API integration
- **pytest** (8.3.0+) - Testing framework
- **rich** (13.0.0+) - Beautiful console output

## 🎯 Common Use Cases

### 1. Quick Trip Planning
```bash
python -m src.main plan --destination "Rome" --budget 1500 --duration 4
```

### 2. Budget-Conscious Travel
```bash
python -m src.main plan \
  --destination "Bangkok" \
  --budget 1000 \
  --duration 7 \
  --accommodation-type hostel
```

### 3. Luxury Travel
```bash
python -m src.main plan \
  --destination "Maldives" \
  --budget 5000 \
  --duration 5 \
  --accommodation-type resort
```

### 4. Dietary-Specific Planning
```bash
python -m src.main plan \
  --destination "Tel Aviv" \
  --budget 2500 \
  --duration 3 \
  --dietary halal
```

### 5. Activity-Based Trip
```bash
python -m src.main plan \
  --destination "Bali" \
  --budget 2000 \
  --duration 7 \
  --activities adventure
```

## 🤝 Contributing

Contributions welcome! Areas for enhancement:
- Additional search providers (Kayak, Booking.com APIs)
- Real-time flight/hotel pricing
- Weather integration
- Multi-city trips
- Group travel optimization

## 📄 License

[License information]

## 🚀 Quick Start Commands

```bash
# One-liner to get started
git clone <url> && cd Travel-planner-agent && \
  python3 -m venv venv && source venv/bin/activate && \
  pip install -r requirements.txt && \
  cp .env.example .env && \
  echo "Edit .env with your OpenAI API key, then run:" && \
  echo "python -m src.main plan --destination 'Paris' --budget 2000 --duration 5"
```

## 📞 Support

- **Installation issues**: See [SETUP.md](SETUP.md)
- **Architecture questions**: See [docs/architecture/graph.md](docs/architecture/graph.md)
- **Test documentation**: See [TEST_TOOLS_DOCUMENTATION.md](TEST_TOOLS_DOCUMENTATION.md)
- **CLI/API help**: Run `python -m src.main plan --help`

## 🔍 Monitoring

The Travel Planner provides comprehensive logging and monitoring:

### Logging
- **Log Location**: `logs/agent.log`
- **Log Level**: Configurable (INFO, DEBUG, WARNING, ERROR)
- **Format**: Timestamp - Logger Name - Level - Message
- **Rotation**: Automatic log file rotation (10MB max, 5 backups retained)

### Features
✅ **Step-by-Step Logging**
- Each node logs entry and exit
- Budget calculation steps logged
- Search results logged with counts
- Selection criteria and scoring logged
- Itinerary generation progress tracked

✅ **Token Usage Tracking**
- Input tokens per LLM call
- Output tokens per response
- Total tokens per workflow
- Cost estimation (for monitoring)

✅ **Performance Metrics**
- Execution time per node
- Total workflow time
- API response times
- Cache hit/miss rates

✅ **Error Logging**
- Exception details captured
- Stack traces preserved
- User-friendly error messages
- Recovery attempts logged

### Example Log Output
```
2025-11-08 14:30:45 - budget_analysis - INFO - ======================================================================
2025-11-08 14:30:45 - budget_analysis - INFO - Starting budget analysis node
2025-11-08 14:30:45 - budget_analysis - INFO - ======================================================================
2025-11-08 14:30:45 - budget_analysis - INFO - Input parameters:
2025-11-08 14:30:45 - budget_analysis - INFO -   Total Budget: $3000.00
2025-11-08 14:30:45 - budget_analysis - INFO -   Destination: Paris, France
2025-11-08 14:30:45 - budget_analysis - INFO -   Duration: 5 days
2025-11-08 14:30:45 - budget_analysis - INFO - ✓ Budget Analysis completed: Feasible ✓
2025-11-08 14:30:47 - search_flights - INFO - ✓ Found 4 flight options
2025-11-08 14:30:47 - search_flights - INFO - ✓ Selected: Delta Airlines - $450
2025-11-08 14:30:49 - search_hotels - INFO - ✓ Found 4 hotel options
2025-11-08 14:30:49 - search_hotels - INFO - ✓ Selected: Luxury Palace Hotel - $180/night
```

### Accessing Logs

```bash
# View recent logs
tail -f logs/agent.log

# Search for errors
grep ERROR logs/agent.log

# Check specific node logs
grep "search_flights" logs/agent.log

# Monitor real-time execution
tail -f logs/agent.log | grep "Step"
```

## 🗺️ Roadmap

The Travel Planner is built with extensibility in mind. Here's the planned development roadmap:

### ✅ Phase 1: Core Planning (COMPLETE)
- [x] Budget analysis and feasibility
- [x] Flight search and selection
- [x] Hotel search and selection
- [x] Activity search and filtering
- [x] Itinerary generation with LLM
- [x] Alternative suggestions
- [x] Error handling and logging
- [x] CLI and Python API
- [x] Comprehensive testing (70+ tests)
- [x] Full documentation

### 🔜 Phase 2: Evaluation & Quality Assurance (PLANNED)
- [ ] Evaluation framework for itinerary quality
- [ ] User satisfaction metrics
- [ ] Budget accuracy validation
- [ ] Multi-destination trip support
- [ ] Enhanced preference matching
- [ ] A/B testing framework
- [ ] Quality dashboards

### 🔜 Phase 3: RAG Integration (PLANNED)
- [ ] Travel knowledge base (destinations, attractions, restaurants)
- [ ] Embedding models for semantic search
- [ ] Real-time travel tips and updates
- [ ] Weather integration
- [ ] Safety and health information
- [ ] Local transportation guides
- [ ] Cultural insights for destinations

### 🔜 Phase 4: Caching & Cost Optimization (PLANNED)
- [ ] Redis caching layer
- [ ] Destination information caching
- [ ] LLM response caching
- [ ] Token cost optimization
- [ ] Request batching
- [ ] Cache invalidation strategies
- [ ] Cost monitoring dashboard

### 🔜 Phase 5: AWS Deployment (PLANNED)
- [ ] AWS Lambda functions for nodes
- [ ] DynamoDB for state persistence
- [ ] S3 for itinerary storage
- [ ] API Gateway for REST endpoints
- [ ] CloudWatch integration
- [ ] Auto-scaling configuration
- [ ] Production deployment guide

### Future Enhancements
- Real-time flight and hotel pricing APIs
- User preference learning
- Group travel optimization
- Multi-language support
- Mobile app integration
- Sustainable/eco-friendly travel options
- Social trip sharing
- Travel insurance recommendations

## 📝 License

MIT License

Copyright (c) 2025 Travel Planner Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

**Status**: ✅ Production Ready | **Version**: 1.0.0 | **Last Updated**: November 8, 2025
- **ChromaDB/FAISS**: Vector databases
- **Redis**: Caching layer

## 🔐 Security

- AWS IAM roles and policies
- API key authentication
- Secrets management via AWS Secrets Manager
- Rate limiting and request validation
- Security scanning in CI/CD

## 📊 Observability

- Prometheus metrics
- OpenTelemetry tracing
- Structured logging
- CloudWatch integration
- Custom dashboards

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## 📝 License

This project is licensed under the MIT License - see the
[LICENSE](LICENSE) file for details.

## 🙋 Support

- Setup Help: See [SETUP.md](SETUP.md)
- Documentation: Check the docs/ folder (coming soon)

## 🗺️ Roadmap

- [ ] Multi-region deployment support
- [ ] Additional vector database integrations
- [ ] Enhanced evaluation metrics
- [ ] Streaming responses optimization
- [ ] Advanced caching strategies

## 📈 Performance

- Semantic caching for repeated queries
- Optimized vector search
- Async operations throughout
- Connection pooling
- Request batching

## 🏆 Acknowledgments

Built with:

- [LangGraph](https://github.com/langchain-ai/langgraph)
- [LangChain](https://github.com/langchain-ai/langchain)
- [AWS CDK](https://aws.amazon.com/cdk/)
- [FastAPI](https://fastapi.tiangolo.com/)

---

Made with ❤️ by [Your Name]
