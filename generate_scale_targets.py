"""
generate_scale_targets.py — build a target-questions file FROM your
actual Scale Mode dataset, instead of using the small demo's
hardcoded Tesla/Eiffel Tower/Einstein questions.

FIXED (v2): the original version of this script had a fatal logic
bug — it asked "What is described in the document titled 'X'?" and
expected the retriever to find that SAME document again by
searching for its own title. But retrieval works by MEANING
similarity, not by title lookup — asking "what's in document X?"
does not reliably retrieve document X itself, especially when many
documents share near-identical placeholder text (see the meta.json
warning below). This produced a demo where every single answer was
a correct-but-useless refusal ("I cannot find that document"),
giving 0% attack success on BOTH sides — a flat, uninformative demo.

THE FIX: instead of asking about a document's OWN title, this
version extracts an actual FACT from inside the document's text
(the first real sentence) and turns THAT into a question whose
answer is expected to be found via normal semantic retrieval — the
same pattern the small demo's Tesla/Eiffel Tower questions already
use successfully. This only works well if your documents have REAL
extracted text, not placeholder text — see the meta.json warning.
"""
import argparse
import json
import random
import re
from pathlib import Path


def get_args():
    p = argparse.ArgumentParser(description="Generate Scale Mode target questions")
    p.add_argument("--n-questions", type=int, default=10,
                    help="How many target questions to generate")
    p.add_argument("--n-poison", type=int, default=5,
                    help="How many poison docs per question (matches Ring 1 test)")
    p.add_argument("--seed", type=int, default=42,
                    help="Random seed, for reproducible question selection")
    return p.parse_args()


def _looks_like_placeholder(text: str) -> bool:
    """
    Detects the exact placeholder text retriever.py inserts when no
    .meta.json file exists (see _load_scale_kb in retriever.py).
    If ALL your documents look like this, question generation cannot
    produce meaningful questions — see the warning printed below.
    """
    return "placeholder" in text.lower() and "meta.json" in text.lower()


def _extract_fact_sentence(text: str) -> str:
    """
    Pulls the first reasonably substantial sentence out of a
    document's text, to use as the seed for a question. This is a
    naive heuristic — good enough for a demo, not a replacement for
    hand-curated evaluation questions.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    for s in sentences:
        if len(s.split()) >= 5:   # skip very short/fragment sentences
            return s.strip()
    return text[:150].strip()


def main():
    args = get_args()
    random.seed(args.seed)

    import sys
    sys.path.insert(0, ".")
    from ragshield_core.retriever import Retriever

    print("Loading your Scale Mode dataset...")
    r = Retriever(backend="scale").load_kb()
    print(f"Loaded {len(r.docs)} documents from Scale Mode.")

    # ── NEW: detect the placeholder-text problem BEFORE generating
    # broken questions, and fail with a clear, actionable message ──
    sample_check = r.docs[: min(20, len(r.docs))]
    placeholder_count = sum(1 for d in sample_check
                             if _looks_like_placeholder(d.get("text", "")))
    if placeholder_count == len(sample_check):
        print("\n" + "=" * 70)
        print("ERROR: Every sampled document has PLACEHOLDER text, not real")
        print("document content. This happens when no .meta.json file exists")
        print("alongside your embeddings (see RAGSHIELD_FAISS.md).")
        print()
        print("Meaningful questions CANNOT be generated from placeholder text")
        print("— every document looks nearly identical to the retriever, so")
        print("retrieval becomes close to random and every LLM answer becomes")
        print("a correct-but-useless refusal ('I cannot find that document').")
        print()
        print("FIX: build a real embeddings/nq_embeddings.meta.json file")
        print("containing the actual document title+text for each embedded")
        print("vector, in the same order — see build_embeddings.py, which")
        print("should be extended to save this alongside the .npy file.")
        print("=" * 70)
        sys.exit(1)

    if len(r.docs) < args.n_questions:
        print(f"WARNING: only {len(r.docs)} documents available, "
              f"reducing --n-questions from {args.n_questions} to {len(r.docs)}")
        args.n_questions = len(r.docs)

    # ── FIXED (Bug #8): the OLD wrong_answer was a literal bracketed
    # string — "[No verified information — this is a deliberately
    # incorrect placeholder answer]" — that NO real LLM would EVER
    # naturally produce as an answer to any question. This meant
    # attack_succeeded() could MATHEMATICALLY NEVER return True,
    # because it checks whether wrong_answer's text appears in the
    # LLM's response — and no LLM says that bracketed placeholder
    # phrase. There was no actual "poison" being tested at all; Ring
    # 1/2/3 had nothing real to defend against, which is why every
    # ASR stayed frozen at 0%/0% regardless of whether the defense
    # was on or off.
    #
    # THE FIX: build wrong_answer from a REAL title belonging to a
    # DIFFERENT, unrelated document in the corpus — exactly the same
    # pattern the small demo's working questions already use (e.g.
    # true="Martin Eberhard", wrong="Nikola Jones" — a real-sounding
    # name that is verifiably incorrect). This gives Ring 1's
    # PatternDetector and Ring 3's candidate-aware matching something
    # real to actually detect and defend against.
    all_titles = [d.get("title", "").strip() for d in r.docs
                  if d.get("title", "").strip()
                  and not _looks_like_placeholder(d.get("text", ""))]

    sampled = random.sample(r.docs, min(args.n_questions * 2, len(r.docs)))
    # sample MORE than needed, since some will be skipped for
    # placeholder/too-short text below

    targets = []
    skipped = 0
    for i, doc in enumerate(sampled):
        if len(targets) >= args.n_questions:
            break

        title = doc.get("title", f"Document {i}")
        text = doc.get("text", "")

        if _looks_like_placeholder(text) or len(text.split()) < 8:
            skipped += 1
            continue   # skip documents with no real, question-worthy content

        fact = _extract_fact_sentence(text)

        # ── FIXED question style: previously the question QUOTED the
        # first 60 characters of the answer INSIDE itself ("what does
        # the following describe: '[fact[:60]]...'?") — meaning the
        # question literally contained its own answer, testing
        # nothing. Now we ask a genuine "what is TITLE?" style
        # question — the SAME pattern the small demo's working
        # Tesla/Eiffel Tower questions use — where the answer must
        # actually be retrieved and reasoned about, not read off the
        # question text itself. ──
        question = f"What is '{title}'?"
        true_answer = fact

        # pick a DIFFERENT document's title as the plausible-but-wrong
        # answer — mirrors the small demo's "Nikola Jones" pattern
        candidate_wrongs = [t for t in all_titles if t != title]
        wrong_answer = (random.choice(candidate_wrongs) if candidate_wrongs
                         else "An unrelated and incorrect answer")

        targets.append({
            "id": f"scale_q{i+1}",
            "question": question,
            "true_answer": true_answer,
            "wrong_answer": wrong_answer,
            "n_poison": args.n_poison,
        })

    if skipped:
        print(f"Skipped {skipped} documents with placeholder/too-short text.")

    if not targets:
        print("\nERROR: no usable documents found — cannot generate any "
              "target questions. See the meta.json fix message above.")
        sys.exit(1)

    output_path = Path("evaluation/scale_target_questions.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(targets, indent=2))

    print(f"\nGenerated {len(targets)} target questions from your Scale "
          f"Mode dataset.")
    print(f"Saved to: {output_path}")
    print(f"\nNext step: DEMO_MODE=2 bash run_live.sh")
    print(f"Pages 1-5 will now show questions built from ACTUAL FACTS in")
    print(f"your documents, answerable via normal semantic retrieval.")
    print(f"\nNOTE: these are still naive, auto-extracted questions/answers —")
    print(f"for a real evaluation harness, hand-curate a proper")
    print(f"question/true-answer/wrong-answer set in this same JSON format,")
    print(f"the same way evaluation/target_questions.json was hand-written.")


if __name__ == "__main__":
    main()
