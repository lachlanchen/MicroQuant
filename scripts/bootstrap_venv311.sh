#!/usr/bin/env bash
set -euo pipefail

# Create a local Python 3.11 venv and install pip requirements.
# Usage:
#   scripts/bootstrap_venv311.sh [PYTHON_BIN]
# Defaults:
#   PYTHON_BIN=python3.11

PY_BIN=${1:-python3.11}

if ! command -v "$PY_BIN" >/dev/null 2>&1; then
  echo "[error] $PY_BIN not found in PATH." >&2
  echo "Install Python 3.11 (e.g., sudo apt install python3.11 python3.11-venv)" >&2
  echo "or pass an explicit path to a 3.11 interpreter." >&2
  exit 1
fi

echo "[info] Using Python: $($PY_BIN --version)"

$PY_BIN -m venv .venv311
source .venv311/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "[ok] Venv ready. Activate with: source .venv311/bin/activate"

