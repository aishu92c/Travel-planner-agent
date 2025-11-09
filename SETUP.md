# Setup Guide

Complete installation and troubleshooting guide for the LangGraph AWS Starter project.

## Prerequisites

- Python 3.13 or higher (also compatible with 3.11+)
- pip 23.0 or higher
- AWS Account with appropriate permissions
- Git

## Quick Installation

```bash
# 1. Clone and navigate to the repository
git clone <your-repo-url>
cd langgraph-aws-starter

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Upgrade pip (IMPORTANT!)
pip install --upgrade pip setuptools wheel

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# 6. Add src to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

## Verify Installation

```bash
# Check Python version
python3.13 --version  # Should be 3.13.x

# Check pip version
pip --version  # Should be 23.0+

# Verify virtual environment is activated
which python  # Should point to venv/bin/python

# Test imports
python -c "import sys; print('Python', sys.version)"
```

## Make PYTHONPATH Permanent

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Add this line (replace with your actual path)
export PYTHONPATH="${PYTHONPATH}:/path/to/langgraph-aws-starter/src"

# Reload shell config
source ~/.bashrc  # or source ~/.zshrc
```

## Common Issues & Solutions

### Issue: Python Version < 3.13

**Solution**: Install Python 3.13

macOS (Homebrew):

```bash
brew install python@3.13
python3.13 -m venv venv
```

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install python3.13 python3.13-venv
python3.13 -m venv venv
```

Windows: Download from [python.org](https://www.python.org/downloads/)

### Issue: "No module named 'src'"

**Solution**: Set PYTHONPATH

```bash
# Temporary (current session only)
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export PYTHONPATH="${PYTHONPATH}:'$(pwd)'/src"' >> ~/.bashrc
source ~/.bashrc
```

### Issue: Virtual Environment Not Activating

macOS/Linux:

```bash
source venv/bin/activate
```

Windows (CMD):

```bash
venv\Scripts\activate
```

Windows (PowerShell):

```bash
venv\Scripts\Activate.ps1
```

### Issue: Permission Denied

If you encounter permission issues:

```bash
# Make scripts executable
chmod +x setup.sh

# Or run with bash
bash setup.sh
```

### Issue: pip Version Too Old

```bash
# Upgrade pip
pip install --upgrade pip setuptools wheel

# Verify version
pip --version
```

## AWS Configuration

```bash
# Configure AWS credentials
aws configure

# Or set environment variables in .env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
```

## Development Setup

### Create Project Structure

```bash
# Create necessary directories
mkdir -p src/{data_pipeline,rag,agents,cache,api,observability,config,utils}
mkdir -p tests/{unit,integration,evaluation,mocks}
mkdir -p infrastructure/{stacks,constructs}

# Create __init__.py files
touch src/__init__.py
find src -type d -exec touch {}/__init__.py \;
find tests -type d -exec touch {}/__init__.py \;
```

### Install Development Tools (Optional)

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Install linting and formatting tools
pip install black ruff mypy pytest pytest-cov
```

## Docker Alternative

Skip local Python setup entirely:

```bash
# Build Docker image
docker build -t langgraph-aws .

# Run container
docker run -it -v $(pwd):/app langgraph-aws bash

# Inside container, you're ready to go!
```

## Troubleshooting Checklist

If you're having issues, verify:

1. **Python version**: `python3.13 --version` (must be 3.13+)
2. **pip version**: `pip --version` (should be 23.0+)
3. **Virtual env active**: `which python` should point to venv
4. **PYTHONPATH set**: `echo $PYTHONPATH` should include src directory
5. **Dependencies installed**: `pip list` should show required packages

## Getting Help

If you're still stuck after trying the above:

1. Delete `venv/` and start fresh
2. Check that all files in the repository are present
3. Verify you have the correct Python version
4. Ensure you're in the project root directory

## Next Steps

Once setup is complete:

1. Edit your `.env` file with actual configuration
2. Run tests to verify everything works: `pytest tests/`
3. Start developing your agents
4. See README.md for project structure and usage

## Additional Resources

- Python Virtual Environments: <https://docs.python.org/3/tutorial/venv.html>
- pip Documentation: <https://pip.pypa.io/>
- AWS CLI Configuration: <https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html>
