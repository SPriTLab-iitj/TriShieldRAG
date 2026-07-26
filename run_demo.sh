#!/usr/bin/env bash
# run_demo.sh — launch the RAG-Shield Streamlit demo
# Usage: ./run_demo.sh
set -euo pipefail

# default to instant demo mode unless caller overrides
export DEMO_MODE="${DEMO_MODE:-1}"

# activate venv if present
if [ -d ".venv" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

echo "==> RAG-Shield demo  (DEMO_MODE=$DEMO_MODE)"
echo "==> opening http://localhost:8501"
streamlit run frontend/app.py
