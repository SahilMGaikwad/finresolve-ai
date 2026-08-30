#!/usr/bin/env bash
# ============================================
# FinResolve AI — Development Setup Script
# ============================================
# Usage: ./scripts/setup_dev.sh
# ============================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "============================================"
echo "  FinResolve AI — Development Setup"
echo "============================================"
echo ""

# Check Python version
echo "[1/5] Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1)
echo "  Found: $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "[2/5] Creating virtual environment..."
if [ -d "$PROJECT_ROOT/.venv" ]; then
    echo "  Virtual environment already exists at .venv/"
else
    python3 -m venv "$PROJECT_ROOT/.venv"
    echo "  Created .venv/"
fi

# Activate and install dependencies
echo ""
echo "[3/5] Installing dependencies..."
source "$PROJECT_ROOT/.venv/bin/activate"
pip install --quiet --upgrade pip
pip install --quiet -r "$PROJECT_ROOT/apps/api/requirements.txt"
echo "  Dependencies installed."

# Copy .env if it doesn't exist
echo ""
echo "[4/5] Checking environment configuration..."
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo "  .env already exists."
else
    cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
    echo "  Created .env from .env.example"
    echo "  ⚠️  Review .env and update values as needed."
fi

# Run tests
echo ""
echo "[5/5] Running tests..."
cd "$PROJECT_ROOT"
python -m pytest tests/ -v

echo ""
echo "============================================"
echo "  Setup complete!"
echo ""
echo "  Activate the virtual environment:"
echo "    source .venv/bin/activate"
echo ""
echo "  Start the API server:"
echo "    uvicorn apps.api.main:app --reload"
echo ""
echo "  Or use Docker:"
echo "    docker compose up"
echo "============================================"
