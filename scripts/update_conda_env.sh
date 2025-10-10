#!/usr/bin/env bash
set -euo pipefail

# Update or create a conda env with a target Python version, then install requirements.txt
# Usage:
#   scripts/update_conda_env.sh [ENV_NAME] [PY_VERSION]
# Defaults:
#   ENV_NAME=mtrader
#   PY_VERSION=3.11

ENV_NAME=${1:-mtrader}
PY_VERSION=${2:-3.11}

echo "[info] Target env: $ENV_NAME  Python: $PY_VERSION"

if ! command -v conda >/dev/null 2>&1; then
  echo "[error] conda not found in PATH. Initialize Anaconda/Miniconda first." >&2
  exit 1
fi

if conda env list | awk '{print $1}' | grep -qx "$ENV_NAME"; then
  echo "[info] Environment '$ENV_NAME' exists. Updating Python and installing requirements..."
  conda install -n "$ENV_NAME" "python=$PY_VERSION" -y
else
  echo "[info] Environment '$ENV_NAME' does not exist. Creating it..."
  conda create -n "$ENV_NAME" "python=$PY_VERSION" -y
fi

echo "[info] Upgrading pip and installing requirements in '$ENV_NAME'..."
conda run -n "$ENV_NAME" python -m pip install --upgrade pip
conda run -n "$ENV_NAME" python -m pip install -r requirements.txt

echo "[ok] Env '$ENV_NAME' is ready. Activate with: conda activate $ENV_NAME"

