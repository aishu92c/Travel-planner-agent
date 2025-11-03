#!/usr/bin/env bash
set -e

echo "🔧 Setting up Python 3.13 virtual environment..."

# Remove old venv if it exists
if [ -d "venv" ]; then
    echo "📦 Removing old venv..."
    rm -rf venv
fi

# Create new venv with Python 3.13
echo "🐍 Creating new venv with Python 3.13..."
python3.13 -m venv venv

# Activate venv
echo "✅ Activating venv..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Install dev dependencies
echo "🛠️  Installing dev dependencies..."
pip install -r requirements-dev.txt

# Install pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
pre-commit install

# Verify installation
echo ""
echo "✅ Setup complete!"
echo ""
echo "Python version: $(python --version)"
echo "Python location: $(which python)"
echo "Pip version: $(pip --version)"
echo ""
echo "🎉 Virtual environment is ready!"
echo ""
echo "To activate the venv in the future, run:"
echo "  source venv/bin/activate"
