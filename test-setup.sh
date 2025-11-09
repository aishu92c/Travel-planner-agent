#!/usr/bin/env bash
set -e

echo "======================================"
echo "🧪 Testing LangGraph AWS Setup"
echo "======================================"
echo ""

# Test 1: Check if venv exists and is Python 3.13
echo "📋 Test 1: Checking virtual environment..."
if [ -d "venv" ]; then
    if [ -f "venv/bin/python" ]; then
        VENV_VERSION=$(venv/bin/python --version 2>&1)
        echo "   ✅ venv exists: $VENV_VERSION"

        if [[ $VENV_VERSION == *"3.13"* ]]; then
            echo "   ✅ Python 3.13 detected"
        else
            echo "   ⚠️  Warning: Not using Python 3.13"
        fi
    else
        echo "   ❌ venv exists but no Python found"
        exit 1
    fi
else
    echo "   ❌ venv directory not found"
    echo "   👉 Run: ./setup-venv.sh"
    exit 1
fi
echo ""

# Test 2: Activate venv and check packages
echo "📋 Test 2: Checking installed packages..."
source venv/bin/activate

REQUIRED_PACKAGES=(
    "langgraph"
    "langchain"
    "boto3"
    "pydantic"
    "httpx"
)

for pkg in "${REQUIRED_PACKAGES[@]}"; do
    if pip show "$pkg" &> /dev/null; then
        VERSION=$(pip show "$pkg" | grep Version | cut -d' ' -f2)
        echo "   ✅ $pkg: $VERSION"
    else
        echo "   ❌ $pkg: NOT INSTALLED"
    fi
done
echo ""

# Test 3: Check dev packages
echo "📋 Test 3: Checking dev packages..."
DEV_PACKAGES=(
    "pytest"
    "black"
    "ruff"
    "mypy"
    "pre-commit"
)

for pkg in "${DEV_PACKAGES[@]}"; do
    if pip show "$pkg" &> /dev/null; then
        VERSION=$(pip show "$pkg" | grep Version | cut -d' ' -f2)
        echo "   ✅ $pkg: $VERSION"
    else
        echo "   ❌ $pkg: NOT INSTALLED"
    fi
done
echo ""

# Test 4: Check pre-commit hooks
echo "📋 Test 4: Checking pre-commit hooks..."
if [ -f ".git/hooks/pre-commit" ]; then
    echo "   ✅ pre-commit hook installed"
else
    echo "   ⚠️  pre-commit hook not installed"
    echo "   👉 Run: pre-commit install"
fi
echo ""

# Test 5: Test Python imports
echo "📋 Test 5: Testing Python imports..."
python -c "
import sys
print(f'   ✅ Python: {sys.version.split()[0]}')

try:
    import langgraph
    print(f'   ✅ langgraph imported')
except ImportError as e:
    print(f'   ❌ langgraph import failed: {e}')

try:
    import langchain
    print(f'   ✅ langchain imported')
except ImportError as e:
    print(f'   ❌ langchain import failed: {e}')

try:
    import boto3
    print(f'   ✅ boto3 imported')
except ImportError as e:
    print(f'   ❌ boto3 import failed: {e}')

try:
    import pydantic
    print(f'   ✅ pydantic imported')
except ImportError as e:
    print(f'   ❌ pydantic import failed: {e}')
"
echo ""

# Test 6: Check file structure
echo "📋 Test 6: Checking project structure..."
REQUIRED_DIRS=(
    "src"
    "tests"
    "src/agents"
    "src/api"
    "src/rag"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "   ✅ $dir/"
    else
        echo "   ❌ $dir/ missing"
    fi
done
echo ""

# Test 7: Check configuration files
echo "📋 Test 7: Checking configuration files..."
CONFIG_FILES=(
    "pyproject.toml"
    "requirements.txt"
    "requirements-dev.txt"
    ".pre-commit-config.yaml"
    "README.md"
    "SETUP.md"
)

for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file missing"
    fi
done
echo ""

# Test 8: Test pre-commit (if installed)
echo "📋 Test 8: Testing pre-commit hooks..."
if command -v pre-commit &> /dev/null; then
    echo "   Running pre-commit on all files..."
    if pre-commit run --all-files; then
        echo "   ✅ All pre-commit checks passed"
    else
        echo "   ⚠️  Some pre-commit checks failed (see above)"
    fi
else
    echo "   ⚠️  pre-commit not available"
fi
echo ""

# Summary
echo "======================================"
echo "✅ Setup test complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. If venv is missing: ./setup-venv.sh"
echo "2. If packages missing: pip install -r requirements.txt requirements-dev.txt"
echo "3. If pre-commit not installed: pre-commit install"
echo "4. Create .env file: cp .env.example .env"
echo ""
