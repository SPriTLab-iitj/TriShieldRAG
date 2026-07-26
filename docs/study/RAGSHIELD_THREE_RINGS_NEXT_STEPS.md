# RAG-Shield (A Three Ring Defense System) — Roadmap to USENIX Security / NDSS / S&P Submission

This file is the persistent checklist for taking RAG-Shield from its
current arXiv-ready initial version to a genuinely competitive
submission at a top-tier security venue. Keep this updated as items
are completed.

**Current status:** arXiv-ready. Not yet ready for USENIX Security,
NDSS, or S&P — see gap analysis below.

---

## The Gap, Stated Plainly

| What top-4 venues expect | What we currently have |
|---|---|
| Millions-of-documents scale (PoisonedRAG itself: 2.6M) | 5,000 documents — ~520x smaller |
| Adaptive attacker evaluated | Not yet tested |
| Independently confirmed theoretical claims | Proposition 1 derived, consistent with one data point only |
| Novel technical contribution beyond composing known techniques | Real, but under-argued — reviewers will ask what's new beyond engineering |

Our own paper already states these gaps honestly in the Discussion
section. That is correct for an arXiv preprint and is exactly why it
is not yet submission-ready for these venues.

---

## The Checklist, In Priority Order

### 1. Scale the evaluation to 2M+ documents on GPU hardware
- [ ] Rebuild the FAISS index at 2 million or more documents
- [ ] Use GPU-accelerated embedding generation (current setup is CPU-only, fine at 5K docs, too slow at 2M+)
- [ ] Switch from `IndexFlatIP` (exact) to an approximate index -- `IndexIVFFlat` or HNSW -- to keep retrieval latency tractable at that scale
- [ ] Re-run the full experimental setup (10 target questions, n_p=5 poison docs) at this new scale
- [ ] Confirm whether the ~91% -> ~13% ASR reduction holds, improves, or degrades at real scale

### 2. Evaluate an adaptive attacker
- [ ] Design poison specifically engineered to evade Ring 1's known detectors:
  - Avoid verbatim-question repetition (defeats the Pattern Detector)
  - Avoid boilerplate phrases like "verified records confirm..." (defeats the Pattern Detector)
  - Keep the false claim's *meaning* intact while changing its *surface form*
- [ ] Re-run the full pipeline against this adaptive poison
- [ ] Report the result honestly, whatever it is -- this is the single most important open item; its current absence is disqualifying at top-4 venues
- [ ] Consider a white-box variant (attacker has retriever embedding access, can use HotFlip-style optimization) as a stretch goal

### 3. Independently confirm Proposition 1 (the minority-poison assumption)
- [ ] Design a controlled experiment that sweeps the poison fraction rho across the minority/majority boundary (e.g., rho = 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8)
- [ ] At each rho, measure whether Ring 2 and Ring 3 actually recover the correct answer below the predicted threshold and fail above it
- [ ] This turns "consistent with one data point" into a genuinely tested, falsifiable claim

### 4. Lower priority, still listed in the paper
- [ ] Run the full 30-question evaluation harness to replace the illustrative paper's-defenses baseline (~29%) with a directly comparable, live-computed number

---

## Once Items 1-3 Are Done

You have a genuinely competitive submission. Most likely strongest
fit: **USENIX Security**, given the direct lineage from PoisonedRAG
(USENIX Security 2025) being extended here.

## In the Meantime

The current version is ready for **arXiv** as an initial version --
publish it to establish priority for the three-ring defense-in-depth
approach, then execute this checklist before targeting a venue
submission.

---

*Last updated: alongside arXiv initial version submission.*
*Repo: https://github.com/rpaut03l/poisonedrag-ragshield-group6-iitj*
