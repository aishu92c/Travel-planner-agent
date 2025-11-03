#!/bin/bash
# Quick Setup Script for LangGraph AWS Template
# Run this after downloading the template files

set -e

echo "🚀 LangGraph AWS Template - Quick Setup"
echo "========================================"
echo ""

# Check Python version
echo "✓ Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Found Python $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "✓ Creating virtual environment..."
python3 -m venv venv
echo "  Virtual environment created at ./venv"

# Activate virtual environment
echo ""
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "✓ Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo ""
echo "✓ Installing dependencies (this may take a few minutes)..."
if pip install -e ".[dev]" 2>/dev/null; then
    echo "  ✓ Installed in editable mode"
else
    echo "  ⚠ Editable install failed, trying alternative method..."
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    echo "  ✓ Installed dependencies directly"
    echo "  Note: Using PYTHONPATH instead of editable install"
    export PYTHONPATH="$(pwd)/src:${PYTHONPATH}"
fi

# Create .env file
echo ""
echo "✓ Setting up environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "  Created .env from template"
else
    echo "  .env already exists, skipping"
fi

# Install pre-commit hooks
echo ""
echo "✓ Installing pre-commit hooks..."
pre-commit install

# Create directory structure
echo ""
echo "✓ Creating project directories..."
mkdir -p src/{data_pipeline,rag,agents/{routes},cache,api,observability,config/environments,utils}
mkdir -p infrastructure/{stacks,constructs}
mkdir -p tests/{unit,integration,evaluation,mocks}
mkdir -p scripts docs docker examples .github/workflows .github/ISSUE_TEMPLATE

# Create __init__.py files
echo ""
echo "✓ Creating Python package structure..."
touch src/__init__.py
touch src/data_pipeline/__init__.py
touch src/rag/__init__.py
touch src/agents/__init__.py
touch src/cache/__init__.py
touch src/api/__init__.py
touch src/api/routes/__init__.py
touch src/observability/__init__.py
touch src/config/__init__.py
touch src/utils/__init__.py
touch infrastructure/__init__.py
touch infrastructure/stacks/__init__.py
touch infrastructure/constructs/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py
touch tests/evaluation/__init__.py
touch tests/mocks/__init__.py

# Initialize git
echo ""
echo "✓ Initializing git repository..."
if [ ! -d .git ]; then
    git init
    git add .
    git commit -m "Initial commit: Phase 1 complete"
    echo "  Git repository initialized"
else
    echo "  Git repository already exists, skipping"
fi

# Run initial tests
echo ""
echo "✓ Running initial validation..."
make lint || echo "  Note: Some linting warnings expected with empty files"

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your configuration"
echo "2. Review PROJECT_PLAN.md for roadmap"
echo "3. Run 'make help' to see available commands"
echo "4. Open project in VS Code: code ."
echo ""
echo "To activate the virtual environment in the future:"
echo "  source venv/bin/activate"
echo ""
echo "💡 If you installed without editable mode, add to your shell config:"
echo "  export PYTHONPATH=\"\$(pwd)/src:\${PYTHONPATH}\""
echo ""
echo "Happy coding! 🎉"
