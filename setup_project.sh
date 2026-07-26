#!/usr/bin/env bash
# =====================================================================
# setup_project.sh  —  one-shot setup for the PoisonedRAG / RAG-Shield demo
#
# FIX IN THIS VERSION:
#   - Hard-requires Python 3.11 (your earlier venv was 3.9, which is why
#     networkx>=3.3 / streamlit / torch could not install).
#   - Installs ONLY the light demo deps by default (no torch/faiss/networkx),
#     so the demo runs instantly. Heavy "live mode" deps are a separate step.
#
# RUN (from your project root):
#   cd ~/Desktop/MTech\ AI\ IIT-Jodhpur*/Cohort-2-Trimester-2/Cyber-Security_ES/Major-Project-PoisonedRAG
#   cp ~/Downloads/PoisonedRAG_Demo/setup_project.sh .
#   chmod +x setup_project.sh
#   ./setup_project.sh
# =====================================================================
set -euo pipefail

DEMO_SRC="${1:-$HOME/Downloads/PoisonedRAG_Demo}"
PROJECT_ROOT="$(pwd)"

echo "============================================================"
echo " RAG-Shield setup   (demo src: $DEMO_SRC)"
echo "============================================================"

# ---- 0. locate a real Python 3.11 ----
echo "==> 0/6  Locating Python 3.11"
PY311=""
for c in python3.11 /opt/homebrew/bin/python3.11 /usr/local/bin/python3.11 \
         /opt/homebrew/opt/python@3.11/bin/python3.11; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; exit(0 if sys.version_info[:2]==(3,11) else 1)' 2>/dev/null; then
    PY311="$c"; break
  fi
done
if [ -z "$PY311" ]; then
  echo "    Python 3.11 NOT found. Install it, then re-run this script:"
  echo "        brew install python@3.11"
  echo "    (If brew isn't installed: https://brew.sh )"
  exit 1
fi
echo "    found: $PY311  ($($PY311 --version 2>&1))"

# ---- 1. sanity: demo downloaded? ----
[ -d "$DEMO_SRC" ] || { echo "ERROR: demo not found at $DEMO_SRC — unzip PoisonedRAG_Demo.zip into ~/Downloads first."; exit 1; }

# ---- 2. merge demo -> project ----
echo "==> 1/6  Copying demo files into project"
if command -v rsync >/dev/null 2>&1; then
  rsync -a --exclude='.DS_Store' --exclude='__pycache__' "$DEMO_SRC"/ "$PROJECT_ROOT"/
else
  cp -R "$DEMO_SRC"/. "$PROJECT_ROOT"/
fi

# ---- 3. clean junk ----
echo "==> 2/6  Cleaning .DS_Store / __pycache__"
find "$PROJECT_ROOT" -name '.DS_Store' -delete 2>/dev/null || true
find "$PROJECT_ROOT" -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true

# ---- 4. rebuild venv with 3.11 ----
echo "==> 3/6  Rebuilding .venv with Python 3.11"
rm -rf .venv
"$PY311" -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
echo "    venv python: $(python --version 2>&1)"

# ---- 5. install LIGHT demo deps only ----
echo "==> 4/6  Installing demo dependencies (light, no torch/faiss)"
python -m pip install --upgrade pip --quiet
pip install --quiet -r requirements-demo.txt
echo "    installed core demo deps"

# ---- 6. smoke test ----
echo "==> 5/6  Smoke test"
DEMO_MODE=1 python demo_cli.py "Who founded Tesla Motors?"

echo "==> 6/6  Done."
echo "============================================================"
echo " LAUNCH THE DEMO:"
echo "     source .venv/bin/activate"
echo "     DEMO_MODE=1 streamlit run frontend/app.py"
echo "     # http://localhost:8501"
echo
echo " FULL EVALUATION:"
echo "     DEMO_MODE=1 python evaluation/run_experiments.py"
echo
echo " LIVE MODE LATER (real FAISS + Claude/LLaMA) — separate heavy install:"
echo "     pip install -r requirements.txt"
echo "     DEMO_MODE=0 streamlit run frontend/app.py"
echo "============================================================"
