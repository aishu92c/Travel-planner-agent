#!/bin/bash
set -e

echo "================================"
echo "Running Integration Tests"
echo "================================"

cd /Users/ab000746/Downloads/Travel-planner-agent

# Run tests with minimal output
python3.11 -m pytest tests/test_integration.py -v --tb=short -x

echo ""
echo "================================"
echo "Integration Tests Complete!"
echo "================================"

