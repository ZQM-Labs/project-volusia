#!/bin/bash
# dev-up.sh - One-command development environment setup
# Usage: ./scripts/dev-up.sh

set -e

echo "🔧 Setting up Project Volusia development environment..."

# Check Python version
PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
echo "  Python: $PYTHON_VERSION"

# Create venv if not exists
if [ ! -d ".venv" ]; then
    echo "  Creating virtual environment..."
    python -m venv .venv
fi

# Activate venv (cross-platform)
if [ -f ".venv/bin/activate" ]; then
    # Unix/macOS
    source .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
    # Windows
    source .venv/Scripts/activate
else
    echo "  ERROR: Could not find venv activation script"
    exit 1
fi

# Install dependencies
echo "  Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -e ".[dev]"
pip install --quiet pre-commit

# Install pre-commit hooks
echo "  Installing pre-commit hooks..."
pre-commit install

# Run database migration if needed
if [ -f "Tools/volusia_data/migrate_db.py" ]; then
    echo "  Running database migration..."
    python Tools/volusia_data/migrate_db.py || true
fi

echo ""
echo "✅ Development environment ready!"
echo ""
echo "Usage:"
echo "  source .venv/bin/activate    # Activate venv (Unix/macOS)"
echo "  source .venv/Scripts/activate # Activate venv (Windows)"
echo "  make dev                     # Start portal with auto-reload"
echo "  make test                    # Run tests"
echo "  make lint                    # Check code quality"
echo ""