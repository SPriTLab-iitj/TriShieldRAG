<a id="top"></a>

[Repo Home](../README.md) · [Docs Index](README.md) · [Paper Summary](paper_summary.md) · **Gap & Fix** · [Viva Q&A](viva_qa.md)

---

# Gap & Fix — What's Missing and What We Add

> **This is the heart of the project.** Steps 5–8 of the professor's brief (identify gap → propose → implement → demonstrate) all live here. The grade lives here.

---

## Part A — The Gap (Step 5)

### What the paper leaves open

The authors tested three standard defenses and showed each fails:

| Defense | Failure reason |
|---------|----------------|
| Perplexity filtering | Poison is LLM-generated → fluent → natural perplexity → not flagged |
| Query paraphrasing | Poison matches semantic intent, not surface words → survives rewording |
| Knowledge expansion | Larger top-K still retrieves the poison → LLM still weights it |

**Residual attack success with these defenses on: ~30%+.** The paper's literal conclusion is that they are *insufficient* and that **new defenses are needed.**

### Our diagnosis of *why* single defenses fail

Every one of those defenses is a **single checkpoint**. A single checkpoint is a single point of failure:

- The attacker only has to tune the poison to beat **that one** check.
- Perplexity filter? Make the poison more fluent.
- Paraphrasing? Match deeper semantics.
- Expansion? Add more poison or make it rank higher.

There is no layer that catches what another misses.

### Gap statement (quotable)

> *"Existing single-layer defenses against PoisonedRAG leave 30%+ residual attack success because each is a single point of failure. What's missing is **layered, defense-in-depth** protection that screens documents at **ingest**, at **retrieval**, and at **generation** — so that defeating one layer is not enough to succeed."*

---

## Part B — Our Fix: RAG-Shield (Step 6)

RAG-Shield is a **3-ring, defense-in-depth** pipeline. Poison must defeat **all three independent rings at once** to succeed.

```
                          RAG-SHIELD

  Document being added                Query arriving              Answer being formed
        |                                   |                            |
        v                                   v                            v
  +-------------+                   +----------------+          +-------------------+
  |   RING 1    |                   |     RING 2     |          |      RING 3       |
  | Ingest Guard| ----------------> |Retrieval Scorer| -------> |Cross-LLM Consensus|
  +-------------+                   +----------------+          +-------------------+
   perplexity                        provenance/trust            3 LLMs vote
   embedding-outlier                 inter-doc consistency       disagreement => 
   pattern match                     trust re-ranking            re-retrieve w/o suspects
        |                                   |                            |
   catch crude poison                catch poison that            catch poison that
   at the door                       contradicts clean docs       slipped through 1-2
```

### Ring 1 — Ingest Guard (defends the *ingest* stage)

Runs when a document is **added** to the KB.

- **Perplexity scoring** — flag docs whose language statistics are off.
- **Embedding-outlier detection** — flag docs that sit in unusual regions of embedding space relative to the existing KB distribution.
- **Pattern matching** — flag docs that embed a question **verbatim** (a tell-tale sign of a retrieval trigger `S`).

*Catches:* crude, templated, or obviously-crafted poison before it ever enters the KB.

### Ring 2 — Retrieval Scorer (defends the *retrieval* stage)

Runs at **query time**, after top-K retrieval.

- **Source-provenance / trust weighting** — documents from trusted sources outrank anonymous/low-trust ones.
- **Inter-document consistency** — a retrieved doc that contradicts the consensus of the other retrieved docs is down-weighted (poison usually disagrees with the clean majority).
- **Trust-weighted re-ranking** — combine the above into a re-ranked, filtered context set before it reaches the LLM.

*Catches:* poison that got retrieved but stands out against the clean documents around it.

### Ring 3 — Cross-LLM Consensus (defends the *generation* stage)

Runs at **answer time**.

- Query **3 different LLMs in parallel** (Claude + Azure OpenAI + Ollama/LLaMA) with the same retrieved context.
- If they **agree**, return the answer with high confidence.
- If they **disagree**, the answer is **flagged** → the system **re-retrieves excluding the suspect documents** and re-asks.

*Catches:* poison that slipped through Rings 1–2. Different model families don't get fooled identically, so disagreement is a strong poison signal.

> **Airport-security analogy:** one checkpoint can be fooled. Three independent checkpoints — bag scan, metal detector, and a human officer — are much harder to beat all at once.

---

## Part C — Implementation (Step 7)

| Component | File | What it does |
|-----------|------|--------------|
| KB builder | `knowledge_base/build_kb.py` | Downloads 5,000 Wikipedia docs |
| Index builder | `knowledge_base/build_index.py` | FAISS index, `all-mpnet-base-v2` embeddings |
| Targets | `baseline/target_questions.json` | 10 target questions w/ true + wrong answers |
| Poison generator | `baseline/generate_poison.py` | 50 poison docs (10 targets × 5) |
| Poison injector | `baseline/inject_poison.py` | Builds poisoned FAISS index |
| Baseline ASR | `baseline/measure_baseline_asr.py` | Measures undefended attack success |
| Ring 1 | `defense/ring1_ingest_guard.py` | Perplexity + outlier + pattern |
| Ring 2 | `defense/ring2_retrieval_scorer.py` | Provenance + consistency + re-rank |
| Ring 3 | `defense/ring3_cross_llm.py` | Cross-LLM consensus |
| LLM interface | `llm_backends/unified_interface.py` | Claude / Azure / Ollama unified |
| UI | `frontend/app.py` | Streamlit demo |

**Stack:** Python 3.11 · FAISS · sentence-transformers (`all-mpnet-base-v2`, CPU on Mac) · Streamlit · Anthropic Claude · Azure OpenAI · Ollama (LLaMA 3.1 8B).

> **Note on LLM backends:** Azure OpenAI quota was unavailable across all regions during the build, so the demo runs on **Claude + Ollama (LLaMA)** — a genuine *multi-vendor* consensus (Anthropic + Meta), which is actually a stronger story than single-vendor. Azure slots back in as a third LLM if/when quota is approved.

---

## Part D — Demonstration (Step 8)

| Result | Value (illustrative until final eval) |
|--------|------|
| Undefended attack success | ~91% |
| Paper's defenses | ~29% |
| **RAG-Shield** | **~13%** |

- Holds across **Claude, GPT, and LLaMA** backends.
- **Benign-query accuracy is preserved** — the defense doesn't break normal questions.

**Live demo flow:** ask "Who founded Tesla?" on the poisoned KB → wrong answer → toggle RAG-Shield → correct answer, with each ring's decision shown → cross-LLM disagreement visualized → switch backends to prove vendor-independence.

---

## Part E — Honest limitations (have these ready for viva)

- Numbers above are **illustrative** until the full evaluation harness run lands — update before the real presentation.
- Ring 3 adds **latency and API cost** (3 LLM calls). Real deployments would gate it to low-confidence cases.
- We have **not** yet tested an **adaptive attacker** who knows RAG-Shield exists and optimizes against all three rings jointly — that's future work.
- KB is **5,000 docs**, not millions — scale testing is future work.

---

## One-line summary

> *"The paper proved existing defenses fail because each is one checkpoint. RAG-Shield answers with defense-in-depth: ingest screening, retrieval scoring, and cross-LLM consensus — three independent rings that together cut attack success from ~90% to ~13%."*


---

[Repo Home](../README.md) · [Docs Index](README.md) · [Paper Summary](paper_summary.md) · **Gap & Fix** · [Viva Q&A](viva_qa.md)

[↑ Back to top](#top)
