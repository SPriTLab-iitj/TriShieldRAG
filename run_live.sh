# #!/usr/bin/env bash
# # run_live.sh — launch LITE-LIVE (real local LLMs, light retriever, watcher off).
# set -e
# pkill -9 -f streamlit 2>/dev/null || true
# lsof -ti :8501,:8502 2>/dev/null | xargs kill -9 2>/dev/null || true
# export SETUPTOOLS_USE_DISTUTILS=stdlib OMP_NUM_THREADS=1 TOKENIZERS_PARALLELISM=false KMP_DUPLICATE_LIB_OK=TRUE
# export PYTORCH_ENABLE_MPS_FALLBACK=1
# export DEMO_MODE=0 RETRIEVER=tfidf
# echo "==> LITE-LIVE  ->  http://localhost:8502"
# .venv/bin/python -m streamlit run frontend/app.py \
#   --server.port 8502 --server.headless true \
#   --server.fileWatcherType none --server.runOnSave false


#!/usr/bin/env bash
# run_live.sh — launch the live app (real LLMs).
#
# Respects whatever DEMO_MODE was already set by the caller.
# Run it like this:
#   DEMO_MODE=0 bash run_live.sh     -> LIVE mode (small demo KB)
#   DEMO_MODE=2 bash run_live.sh     -> SCALE mode (YOUR large dataset)
#
# If DEMO_MODE isn't set at all when you call this script, it
# defaults to 0 (classic live mode) — NOT to 1 (mock demo), since
# calling run_live.sh at all signals you want real LLMs.
set -e
pkill -9 -f streamlit 2>/dev/null || true
lsof -ti :8501,:8502 2>/dev/null | xargs kill -9 2>/dev/null || true
export SETUPTOOLS_USE_DISTUTILS=stdlib OMP_NUM_THREADS=1 TOKENIZERS_PARALLELISM=false KMP_DUPLICATE_LIB_OK=TRUE
export PYTORCH_ENABLE_MPS_FALLBACK=1

# ── FIXED: previously this line HARDCODED DEMO_MODE=0, silently
# overwriting whatever you set on the command line. That meant
# "DEMO_MODE=2 bash run_live.sh" ran LIVE mode instead of SCALE mode
# every single time, with no error or warning. Now we only supply a
# DEFAULT if DEMO_MODE isn't already set, using bash's ":-" syntax
# ("use $DEMO_MODE if it's set, otherwise use 0"). RETRIEVER=faiss
# is set explicitly too, matching the retriever_backend() fix in
# config.py (so live mode gets REAL search, not the tfidf/demo path).
export DEMO_MODE="${DEMO_MODE:-0}"
export RETRIEVER="${RETRIEVER:-faiss}"

# ── Label the terminal banner based on the ACTUAL mode running,
# not a fixed string — this was also wrong before (always said
# "LITE-LIVE" regardless of which mode you picked).
case "$DEMO_MODE" in
  2) echo "==> SCALE MODE ->  http://localhost:8502  (RPTL's large dataset)" ;;
  0) echo "==> LIVE MODE  ->  http://localhost:8502  (small built-in KB)" ;;
  *) echo "==> DEMO MODE  ->  http://localhost:8502  (mock LLMs)" ;;
esac

.venv/bin/python -m streamlit run frontend/app.py \
  --server.port 8502 --server.headless true \
  --server.fileWatcherType none --server.runOnSave false
