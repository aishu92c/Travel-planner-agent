#!/usr/bin/env python3.11
"""Simple test runner for test_tools.py"""

import subprocess
import sys

# Run pytest
result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_tools.py", "-v", "--tb=short"],
    cwd="/Users/ab000746/Downloads/Travel-planner-agent",
    capture_output=True,
    text=True,
    timeout=120
)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print(f"\nReturn code: {result.returncode}")

