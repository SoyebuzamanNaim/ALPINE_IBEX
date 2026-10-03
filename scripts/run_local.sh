#!/usr/bin/env bash
# ==============================================================================
# FLARE-X: Microgravity Combustion Flammability Explorer
# Single-command local launcher for FastAPI backend and Mission Control UI.
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "======================================================================"
echo "  🚀 FLARE-X: Flame in Freefall · NASA Flammability Explorer"
echo "======================================================================"

# 1. Resolve Python binary from virtual environment
if [ -d ".venv" ]; then
    PYTHON_BIN=".venv/bin/python"
elif command -v python3 &> /dev/null; then
    PYTHON_BIN="python3"
else
    echo "❌ Error: Python 3 not found."
    exit 1
fi

echo "✓ Using Python: $($PYTHON_BIN --version)"

# 2. Verify required artifacts
DATA_PATH="cache/experiments.parquet"
MODEL_PATH="models/flame_spread_gb.joblib"

if [ ! -f "$DATA_PATH" ]; then
    echo "⚠️ Warning: $DATA_PATH not found. Ingesting raw NASA records..."
    $PYTHON_BIN -c "from src.ingestion.extract import build_all; build_all()"
fi

if [ ! -f "$MODEL_PATH" ]; then
    echo "⚠️ Warning: $MODEL_PATH not found. Training baseline model..."
    $PYTHON_BIN src/compute/model.py
fi

echo "✓ Verified dataset: $DATA_PATH"
echo "✓ Verified model:   $MODEL_PATH"
echo ""
echo "----------------------------------------------------------------------"
echo "  Mission Control UI & REST API available at:"
echo "  👉  http://localhost:8000"
echo "  👉  API Docs: http://localhost:8000/docs"
echo "----------------------------------------------------------------------"
echo "Starting Uvicorn server (Press Ctrl+C to terminate)..."

exec $PYTHON_BIN -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --log-level info
