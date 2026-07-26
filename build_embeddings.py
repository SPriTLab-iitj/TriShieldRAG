"""
build_embeddings.py — embed a dataset into 768-dim vectors and save
to disk, ready for FAISS indexing.

Usage:
    python3 build_embeddings.py --dataset nq --batch-size 256 --device cpu
    python3 build_embeddings.py --dataset nq --batch-size 256 --device mps
    python3 build_embeddings.py --dataset demo --batch-size 32 --device cpu

Notes for Mac users:
    --device cuda   WILL NOT WORK on a Mac (no NVIDIA GPU). Use "mps"
                    (Apple Silicon GPU) or "cpu" instead.
    --device mps    Apple Silicon GPU acceleration. Faster than CPU,
                    but known to be less stable in some sentence-
                    transformers versions on long-running jobs — if
                    it crashes partway through, re-run with "cpu".
    --device cpu    Slowest but most stable. On an M1 Max, budget
                    roughly 10-14 hours for the full 2.6M-passage
                    Natural Questions corpus. Consider running
                    overnight, or in smaller chunks (see --limit).
"""

import argparse
import json
import re
import time
import sys
from pathlib import Path
from typing import Optional, List

import numpy as np


def get_args():
    p = argparse.ArgumentParser(description="Build sentence embeddings for RAG-Shield")
    p.add_argument("--dataset", type=str, default="demo",
                    choices=["demo", "nq"],
                    help="'demo' = your existing small KB. "
                         "'nq' = Natural Questions corpus (~2.6M passages)")
    p.add_argument("--batch-size", type=int, default=32,
                    help="How many documents to embed at once. "
                         "Larger = faster but more memory used.")
    p.add_argument("--device", type=str, default="cpu",
                    choices=["cpu", "mps", "cuda"],
                    help="cpu (safe, slow) / mps (Apple GPU) / "
                         "cuda (NVIDIA GPU only — will NOT work on Mac)")
    p.add_argument("--limit", type=int, default=None,
                    help="Optional: only embed the first N documents "
                         "(useful for testing before committing to "
                         "the full multi-hour run)")
    p.add_argument("--output", type=str, default="embeddings/nq_embeddings.npy",
                    help="Where to save the resulting embeddings")
    return p.parse_args()


def load_documents(dataset_name: str, limit: Optional[int]) -> List[dict]:
    """
    FIXED: previously this returned a plain list of TEXT STRINGS,
    which get embedded but then THROWN AWAY — only the resulting
    vectors were saved, never the original document title/text.
    This meant Scale Mode's retriever.py had no real document
    content to show, only auto-generated placeholder text, which
    in turn broke question generation (see generate_scale_targets.py
    v2's docstring for the full chain of consequences).

    Now returns a list of {"title": ..., "text": ...} dicts, so
    main() below can save BOTH the embeddings AND a matching
    metadata file with real document content.
    """
    if dataset_name == "demo":
        # Reuses your existing small demo KB from retriever.py
        from ragshield_core.retriever import _DEMO_CLEAN
        docs = [{"title": d.get("title", ""), "text": d["text"]} for d in _DEMO_CLEAN]
        print(f"Loaded {len(docs)} demo documents.")
        return docs

    elif dataset_name == "nq":
        try:
            from datasets import load_dataset
        except ImportError:
            print("ERROR: 'datasets' library not installed.")
            print("Run: pip install datasets")
            sys.exit(1)

        print("Downloading/loading Natural Questions corpus "
              "(this can take a while the first time)...")
        ds = load_dataset("natural_questions", split="train")

        docs = []
        for i, row in enumerate(ds):
            if limit is not None and i >= limit:
                break
            # FIXED: the OLD code checked "html" FIRST, only falling
            # back to "text" if html was empty. Natural Questions'
            # raw records almost ALWAYS have "html" populated — with
            # the entire raw Wikipedia page markup (<!DOCTYPE html>,
            # CSS, reference-tooltip JavaScript styling, etc) — so
            # "html" nearly always "won" via the `or`, and the CLEAN
            # "text" field was almost never actually used. This
            # produced documents whose "text" was thousands of
            # characters of markup instead of readable article
            # content — which is why questions built from this text
            # made no sense and the LLM correctly refused to answer
            # them (see generate_scale_targets.py's docstring for
            # the earlier, related placeholder-text bug this
            # compounds with).
            #
            # THE FIX: check "text" FIRST (the clean field), only
            # falling back to "html" if text is truly empty — and
            # even then, STRIP any HTML tags out before using it.
            raw_text = row.get("document", {}).get("text", "")
            if not raw_text:
                raw_html = row.get("document", {}).get("html", "")
                # crude but effective: strip all HTML tags, collapse
                # whitespace. Good enough for a demo corpus — a
                # production pipeline would use a real HTML parser
                # (e.g. BeautifulSoup) for cleaner extraction.
                raw_text = re.sub(r"<[^>]+>", " ", raw_html)
                raw_text = re.sub(r"\s+", " ", raw_text).strip()
            text = raw_text
            title = row.get("document", {}).get("title", f"NQ document {i}")
            if text:
                docs.append({"title": title, "text": text})

        print(f"Loaded {len(docs)} documents from Natural Questions "
              f"({'limited to ' + str(limit) if limit else 'full corpus'}).")
        return docs

    return []


def main():
    args = get_args()

    print(f"\n{'='*60}")
    print(f"  RAG-Shield Embedding Builder")
    print(f"{'='*60}")
    print(f"  Dataset:     {args.dataset}")
    print(f"  Batch size:  {args.batch_size}")
    print(f"  Device:      {args.device}")
    print(f"  Limit:       {args.limit or 'none (full dataset)'}")
    print(f"  Output:      {args.output}")
    print(f"{'='*60}\n")

    if args.device == "cuda":
        print("WARNING: --device cuda requires an NVIDIA GPU.")
        print("If you are on a Mac, this will fail. Use --device mps")
        print("(Apple Silicon GPU) or --device cpu instead.\n")

    from sentence_transformers import SentenceTransformer

    print("Loading all-mpnet-base-v2 model...")
    model = SentenceTransformer("all-mpnet-base-v2", device=args.device)

    docs = load_documents(args.dataset, args.limit)

    if len(docs) == 0:
        print("ERROR: no documents loaded. Check your dataset choice.")
        sys.exit(1)

    # docs is now a list of {"title", "text"} dicts (see load_documents
    # fix above) — extract just the text strings for the embedding
    # model, which only accepts plain strings.
    texts = [d["text"] for d in docs]

    print(f"\nEmbedding {len(texts)} documents "
          f"(batch size {args.batch_size}, device {args.device})...")
    print("This is the slow part. Progress will print periodically.\n")

    start = time.time()

    embeddings = model.encode(
        texts,
        batch_size=args.batch_size,
        normalize_embeddings=True,   # unit-length vectors for cosine similarity
        show_progress_bar=True,
        convert_to_numpy=True,
    )

    elapsed = time.time() - start
    print(f"\nDone. Embedded {len(texts)} documents in "
          f"{elapsed/60:.1f} minutes ({elapsed/len(texts)*1000:.1f} ms/doc average).")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(output_path, embeddings)

    # ── NEW: save the matching metadata file so Scale Mode's
    # retriever.py can show REAL document title/text instead of
    # falling back to placeholder text. This is what generate_
    # scale_targets.py needs to produce meaningful questions —
    # see that script's docstring for the full bug chain this fixes.
    meta_path = output_path.parent / (output_path.stem + ".meta.json")
    meta_content = [{"id": f"nq_{i}", "title": d["title"],
                      "text": d["text"][:2000],  # cap length — full NQ
                                                  # documents can be huge;
                                                  # 2000 chars is plenty
                                                  # for a demo answer
                      "source": "clean"}
                     for i, d in enumerate(docs)]
    meta_path.write_text(json.dumps(meta_content, indent=2))

    print(f"\nSaved embeddings to: {output_path}")
    print(f"Saved document metadata to: {meta_path}")
    print(f"Shape: {embeddings.shape}  "
          f"({embeddings.shape[0]} docs x {embeddings.shape[1]} dimensions)")
    print(f"\nNext step: point SCALE_META_PATH at this file in your .env")
    print(f"(defaults already match: {meta_path}), then run:")
    print(f"  .venv/bin/python3.11 generate_scale_targets.py --n-questions 20")
    print(f"\nNext step: build a FAISS index from these embeddings.")
    print(f"See docs/TECH_FAISS.md for the IndexIVFFlat setup at this scale.")


if __name__ == "__main__":
    main()
