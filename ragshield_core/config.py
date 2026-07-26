"""
ragshield_core.config
Central configuration: paths, environment, and run-mode flags.

Three run modes:
  - DEMO_MODE=1  (default): lightweight TF-IDF retriever + heuristic "mock" LLM.
                 Runs instantly, no API keys, no Ollama, no FAISS needed.
  - DEMO_MODE=0 : real FAISS index + sentence-transformers + live LLM backends
                 (Anthropic / Mistral / Ollama / Azure). Uses the small
                 built-in demo KB (5 questions). Use once your KB + keys
                 are ready.
  - DEMO_MODE=2 : SCALE mode (NEW). Same live LLM backends as DEMO_MODE=0,
                 but retrieves from a large, pre-built Natural Questions
                 embeddings file + FAISS index (built with
                 build_embeddings.py) instead of the small demo KB.
                 This is how you test RAG-Shield against a
                 5,000-to-2,600,000-document corpus without touching the
                 existing demo/live code paths at all.
"""
from __future__ import annotations
import os
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# ---- project paths -------------------------------------------------
# This file lives in <root>/llm_backends/ ... no — it's imported as a sibling.
# We resolve ROOT as the project root (the dir that contains this package's parent).
ROOT = Path(__file__).resolve().parent.parent
KB_DIR = ROOT / "knowledge_base"
VECTOR_DIR = KB_DIR / "vector_store"
KB_DOCS = KB_DIR / "kb_data" / "kb_docs.jsonl"
FAISS_INDEX = VECTOR_DIR / "kb.faiss"
FAISS_META = VECTOR_DIR / "kb_meta.json"
POISON_CORPUS = ROOT / "baseline" / "poison_corpus.jsonl"
TARGETS = ROOT / "evaluation" / "target_questions.json"
RESULTS_DIR = ROOT / "evaluation" / "results"

# ---- run mode ------------------------------------------------------
def demo_mode() -> bool:
    """True unless DEMO_MODE=0 or DEMO_MODE=2 is explicitly set."""
    return os.getenv("DEMO_MODE", "1") not in ("0", "false", "False", "2")


# ── NEW: Scale Mode (DEMO_MODE=2) ────────────────────────────────────
# Everything below in this section is ADDITIVE. Nothing above this
# comment was changed from the original file, and demo_mode() above
# has only ONE new value ("2") added to its existing exclusion list —
# its behaviour for "0", "false", "False" is completely unchanged.

def scale_mode() -> bool:
    """True only when DEMO_MODE=2 is explicitly set."""
    return os.getenv("DEMO_MODE", "1") == "2"


def scale_kb_paths() -> tuple[str, str]:
    """
    Returns (embeddings_path, faiss_index_path) for Scale Mode.
    Both are configurable via .env so you can point at whichever
    scale-up run you last built (5K test, 50K test, or full 2.6M).

    Defaults match the filenames produced by build_embeddings.py and
    the FAISS index-building script documented in
    docs/study/RAGSHIELD_FAISS.md.
    """
    embeddings = os.getenv("SCALE_EMBEDDINGS_PATH", "embeddings/nq_embeddings.npy")
    index = os.getenv("SCALE_FAISS_INDEX_PATH", "ragshield_2m.index")
    return embeddings, index


def scale_meta_path() -> str:
    """
    Returns the path to an OPTIONAL metadata file (a JSON list of
    document dicts, one per embedded vector, in the same order).
    If this file doesn't exist, Scale Mode still works — it falls
    back to placeholder document text (see retriever.py).
    """
    return os.getenv("SCALE_META_PATH", "embeddings/nq_embeddings.meta.json")


def scale_targets_path() -> str:
    """
    Returns the path to an OPTIONAL target-questions file for Scale
    Mode — a JSON list in the SAME format as evaluation/target_questions.json,
    but with questions/answers that actually relate to YOUR large
    dataset's content, instead of the small demo's Tesla/Eiffel
    Tower/Einstein questions.

    If this file doesn't exist, load_targets() falls back to the
    small demo questions with a clear console warning (see
    retriever.py) — Scale Mode still works for retrieval either way,
    but the on-screen QUESTIONS won't match your dataset's actual
    content until this file is built.
    """
    return os.getenv("SCALE_TARGETS_PATH", "evaluation/scale_target_questions.json")

# ---- end of Scale Mode addition -------------------------------------


# ---- retrieval defaults --------------------------------------------
TOP_K = int(os.getenv("TOP_K", "5"))

def retriever_backend() -> str:
    if scale_mode():          # NEW: checked FIRST, before demo_mode()
        return "scale"
    if demo_mode():
        return "demo"
    # FIXED: when DEMO_MODE=0 (live mode) and RETRIEVER isn't explicitly
    # set, default to "faiss" (real embeddings), not "tfidf" (demo-style
    # retriever). Previously this defaulted to "tfidf", which the
    # Retriever class treats as "demo" backend — meaning DEMO_MODE=0
    # silently behaved like DEMO_MODE=1 unless you remembered to also
    # export RETRIEVER=faiss by hand. Now DEMO_MODE=0 alone is enough.
    return os.getenv("RETRIEVER", "faiss")
EMBED_MODEL = os.getenv("EMBED_MODEL", "all-mpnet-base-v2")

# ---- LLM backend defaults ------------------------------------------
def available_backends() -> list[str]:
    """Which real LLM backends are configured (besides the always-on mock)."""
    out = []
    if os.getenv("ANTHROPIC_API_KEY"):
        out.append("anthropic")
    if os.getenv("MISTRAL_API_KEY"):
        out.append("mistral")
    # ollama assumed reachable on localhost; user can pick it
    out.append("ollama")
    if os.getenv("AZURE_OPENAI_API_KEY") and os.getenv("AZURE_OPENAI_ENDPOINT"):
        out.append("azure_openai")
    return out
