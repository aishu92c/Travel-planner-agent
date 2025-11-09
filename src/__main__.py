"""Entry point for Travel Planner package when run as module.

This allows running the package with:
    python -m src plan --destination "..." --budget ... --duration ...
"""

import sys
from src.main import main

if __name__ == "__main__":
    sys.exit(main())

