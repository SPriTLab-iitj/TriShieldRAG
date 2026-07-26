<a id="top"></a>

# 🗂️ RAG-Shield Study Hub — INDEX

> **Read this first.** This is the map. Three study files live below it —
> Theory, Numericals, Practice — and every one of them links back here.

```
+-------------------------------------------------------------+
|                     RAGSHIELD_INDEX.md  (you are here)      |
|                              |                              |
|        +---------------------+---------------------+        |
|        |                     |                     |        |
|   THEORY.md            NUMERICALS.md          PRACTICE.md   |
|  (what & why)          (the math, worked)    (run it, break |
|                                                it, fix it)  |
+-------------------------------------------------------------+
```

---

## 📌 Quick Nav — Jump Anywhere

- [What is this hub for?](#what-is-this-hub-for)
- [The three files, one line each](#the-three-files-one-line-each)
- [Repository map — where everything lives](#repository-map)
- [Reading order — kid-simple version](#reading-order)
- [The one-page cheat sheet](#one-page-cheat-sheet)
- [Mnemonics master list](#mnemonics-master-list)
- [Tech Stack Deep-Dive Guides](#tech-stack-guides)
- [Links to other docs in this repo](#links-to-other-docs)

---

<a id="what-is-this-hub-for"></a>
## 🧠 What Is This Hub For?

Imagine you're studying for an exam on **RAG-Shield** — the defense system
this repo builds. You have three kinds of things to learn:

1. **The story** — what does each part DO and WHY does it exist? → `THEORY.md`
2. **The math** — what are the exact formulas, worked out with real numbers? → `NUMERICALS.md`
3. **The doing** — how do I run it, test it, and fix it when it breaks? → `PRACTICE.md`

This INDEX file is the front door. Every other file links back here with a
**"⬆ Back to Index"** button at the top and bottom, so you never get lost.

---

<a id="the-three-files-one-line-each"></a>
## 📖 The Three Files — One Line Each

| File | What it teaches | Read this if... |
|---|---|---|
| [`THEORY.md`](RAGSHIELD_THEORY.md) | Concepts, diagrams, why 3 rings, comparison with 6 other papers | You're meeting your professor and need to explain WHY |
| [`NUMERICALS.md`](RAGSHIELD_NUMERICALS.md) | Every formula in Ring 1/2/3, worked step-by-step with real numbers | You need to derive a score by hand or defend a number in viva |
| [`PRACTICE.md`](RAGSHIELD_PRACTICE.md) | Commands, setup, troubleshooting, exam-style Q&A | You're about to run the demo or sit the viva |

---

<a id="repository-map"></a>
## 🗺️ Repository Map — Where Everything Lives

```
poisonedrag-ragshield-group6-iitj/
│
├── README.md                      <- project overview (existing)
├── requirements.txt                <- Python deps
├── .env.example                    <- config template
│
├── ragshield_core/                 <- THE BRAIN (all 3 rings live here)
│   ├── ring1_ingest.py             <- Ring 1: PerplexityDetector,
│   │                                   PatternDetector, OutlierDetector
│   ├── ring2_retrieval.py          <- Ring 2: ProvenanceWeight,
│   │                                   ConsistencyCheck, trust formula
│   ├── ring3_consensus.py          <- Ring 3: CrossLLMConsensus,
│   │                                   candidate_match(), disagreement protocol
│   ├── llm_backends.py             <- Claude/Mistral/Ollama unified interface
│   ├── retriever.py                <- FAISS/TF-IDF + poison synthesis
│   ├── config.py                   <- available_backends(), env loading
│   └── rag_shield.py               <- orchestrator (setup/answer/trace)
│
├── frontend/                       <- THE FACE (Streamlit UI)
│   ├── pages/1_Attack_Demo.py
│   ├── pages/2_Defense_Demo.py
│   ├── pages/3_Side_by_Side.py
│   ├── pages/4_Forensic_Explorer.py
│   ├── pages/5_Results_Dashboard.py
│   └── components/_shared.py       <- attack_succeeded(), caching
│
├── evaluation/
│   └── target_questions.json       <- 10 questions, true+wrong answers
│
├── docs/                            <- ★ THIS STUDY SET GOES HERE ★
│   ├── README.md                    <- docs index (existing)
│   ├── viva_qa.md                   <- existing Q&A doc
│   ├── gap_and_fix.md               <- existing gap analysis
│   ├── paper_summary.md             <- existing PoisonedRAG summary
│   ├── flow_diagram_details_rptl.docx
│   │
│   └── study/                       <- ★★★ NEW FOLDER — PUT THESE 4 FILES HERE ★★★
│       ├── RAGSHIELD_INDEX.md       <- (this file)
│       ├── RAGSHIELD_THEORY.md
│       ├── RAGSHIELD_NUMERICALS.md
│       └── RAGSHIELD_PRACTICE.md
│
├── backends_status.py               <- pre-flight LLM health check
├── run_live.sh / run_demo.sh        <- startup scripts
└── tail_logs.sh                     <- live log viewer
```

> **Exact placement instruction:** create a new folder `docs/study/` inside
> your repo and drop all four `.md` files there. This keeps them separate
> from your existing `docs/` files (viva_qa.md etc.) while still being one
> click away.

---

<a id="reading-order"></a>
## 🚸 Reading Order — Kid-Simple Version

Think of it like learning to bake a cake:

```
Step 1 — THEORY.md   = reading the recipe and understanding
                        WHY you add sugar before eggs
                        (the story, the reasons, the pictures)

Step 2 — NUMERICALS.md = measuring exact grams and following
                        the exact formula for how much of
                        each ingredient
                        (the math, the exact numbers)

Step 3 — PRACTICE.md = actually turning on the oven, baking
                        it, and knowing what to do if it burns
                        (running it, fixing it, being tested on it)
```

**If you only have 1 hour before an exam:** read THEORY.md fully,
skim NUMERICALS.md formulas, and read the "Exam Hacks" section at
the bottom of PRACTICE.md.

---

<a id="one-page-cheat-sheet"></a>
## 🎴 One-Page Cheat Sheet — The Whole Project in One Screen

```
┌─────────────────────────────────────────────────────────────────┐
│  RAG-SHIELD — the whole idea in one box                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PROBLEM: PoisonedRAG attack — 5 fake docs hijack an LLM's      │
│           answer, 91% of the time                               │
│                                                                 │
│  FIX: three independent checkpoints ("rings") that the          │
│       poison must beat ALL THREE of to succeed                  │
│                                                                 │
│  RING 1 (Ingest Guard)     — checks docs BEFORE they're stored  │
│    formula: combined = max(p, pa, 0.7·o + 0.3·max(p,pa))        │
│    block if combined ≥ 0.5                                      │
│                                                                 │
│  RING 2 (Retrieval Scorer) — checks docs AFTER retrieval        │
│    formula: trust = 0.45·provenance + 0.35·consistency          │
│                    + 0.20·retrieval_score                       │
│    drop if trust < 0.35                                         │
│                                                                 │
│  RING 3 (Cross-LLM Consensus) — checks the ANSWER itself        │
│    formula: frac = agree_n / panel_size                         │
│    accept if frac ≥ 0.66 (two-thirds majority)                  │
│                                                                 │
│  RESULT: 91% attack success  →  0-13% attack success            │
│                                                                 │
│  STACK: FAISS + sentence-transformers + Streamlit +             │
│         Claude + Mistral Small + LLaMA 3.2 (Ollama)             │
└─────────────────────────────────────────────────────────────────┘
```

---

<a id="mnemonics-master-list"></a>
## 🧩 Mnemonics Master List — All in One Place

```
I-R-C           → Ingest, Retrieval, Consensus (the 3 rings in order)
                  "I-R-C, easy as ABC"

BAPS            → Black-box, All-3-stages, Pipeline, Scalable
                  (RAG-Shield's 4 advantages over every competitor paper)

P = S + I       → PoisonedRAG's attack formula
                  S = retrieval trigger (Search bait)
                  I = Injection payload (the lie)

45-35-20        → Ring 2 trust weights
                  "45 cents Provenance, 35 cents Consistency,
                   20 cents retrieval Score" (add up to $1.00)

0.5 / 0.35 / 0.66 → the three thresholds, smallest to largest
                  Ring 1 blocks at 0.5 ("half is suspicious enough")
                  Ring 2 drops below 0.35 ("more than a third trust needed")
                  Ring 3 needs 0.66 ("two-thirds majority wins")

SAD vs GLAD     → how RAG-Shield differs from the 2 attack papers
                  they make RAG SAD (Structured/Attack-only/Demo-scale)
                  we make it GLAD (Generation-covered/Layered/
                  Actually-runnable/Defense-built)
```

---

<a id="tech-stack-guides"></a>
## 🔧 Tech Stack Deep-Dive Guides

Beyond the RAG-Shield defense logic itself, these guides explain
every underlying technology from zero — same kid-simple style,
same mnemonics/cheatsheet/exam-hacks structure:

| Guide | Explains |
|---|---|
| [`TECH_FAISS.md`](TECH_FAISS.md) | How FAISS finds "similar" documents fast, IndexFlatIP vs IndexIVFFlat |
| [`TECH_SENTENCE_TRANSFORMERS.md`](TECH_SENTENCE_TRANSFORMERS.md) | How all-mpnet-base-v2 turns sentences into 768-number vectors |
| [`TECH_STREAMLIT.md`](TECH_STREAMLIT.md) | How our 5-page demo app works, caching, reruns |
| [`TECH_LLM_APIS.md`](TECH_LLM_APIS.md) | How we talk to Claude, Mistral, and local LLaMA — black-box vs white-box |

[⬆ Back to top](#top)

---

<a id="links-to-other-docs"></a>
## 🔗 Links to Other Docs in This Repo

- [Repo Home (`README.md`)](../../README.md)
- [Docs Index (`docs/README.md`)](../README.md)
- [Viva Q&A (`docs/viva_qa.md`)](../viva_qa.md)
- [Gap & Fix (`docs/gap_and_fix.md`)](../gap_and_fix.md)
- [PoisonedRAG Paper Summary (`docs/paper_summary.md`)](../paper_summary.md)

**Within this study set:**
- ➡️ Next: [THEORY.md — start here for concepts](RAGSHIELD_THEORY.md#top)
- ➡️ [NUMERICALS.md — the math, worked step by step](RAGSHIELD_NUMERICALS.md#top)
- ➡️ [PRACTICE.md — commands, troubleshooting, exam hacks](RAGSHIELD_PRACTICE.md#top)

[⬆ Back to top](#top)
