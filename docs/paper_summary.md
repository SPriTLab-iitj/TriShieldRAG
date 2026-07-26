<a id="top"></a>

[Repo Home](../README.md) · [Docs Index](README.md) · **Paper Summary** · [Gap & Fix](gap_and_fix.md) · [Viva Q&A](viva_qa.md)

---

# Paper Summary — PoisonedRAG

> **For the team.** Read this once and you'll understand the paper well enough to present your section and answer questions. ~10 minute read.

**Paper:** PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation of Large Language Models
**Authors:** Wei Zou, Runpeng Geng (Penn State); Binghui Wang (Illinois Tech); Jinyuan Jia (Penn State)
**Venue:** 34th USENIX Security Symposium (USENIX Security '25), Seattle, pp. 3827–3844
**arXiv:** 2402.07867

---

## 1. Background — what is RAG and why it exists

Large Language Models have two well-known weaknesses:

- **Outdated knowledge** — a model only knows what it saw during training.
- **Hallucination** — it can confidently make things up.

**Retrieval-Augmented Generation (RAG)** fixes both. Instead of answering from memory alone, the system:

1. Takes the user's question.
2. **Retrieves** the top-K most relevant documents from an external **knowledge base (KB)** (using a retriever like Contriever/DPR/ANCE over vector embeddings).
3. Feeds those documents to the LLM as context.
4. The LLM generates an answer **grounded** in the retrieved text.

> **Analogy:** RAG is an open-book exam. The model looks up relevant pages before answering instead of memorizing everything.

This is now used everywhere: ChatGPT browsing, Bing Chat, enterprise search, customer-support bots, and medical/legal/financial assistants.

---

## 2. The problem — a new attack surface

Prior research focused on making RAG **more accurate** or **more efficient**. Its **security was largely unexplored.**

The paper's key realization: **the knowledge base itself is a new, practical attack surface.** If an attacker can add even a handful of documents to the KB, they may be able to control what the LLM says — *without touching the model, its weights, or even needing API access.*

This is the **first knowledge-corruption attack against RAG.**

---

## 3. The threat model — what the attacker controls

The attacker:

- Picks a **target question** (e.g., *"Who is the CEO of Company X?"*).
- Picks a **target answer** — the (wrong) answer they want the LLM to give.
- **Injects a few malicious texts** into the KB.
- **Goal:** make the LLM output the target answer for the target question.

Two settings based on attacker knowledge:

| Setting | Attacker knows | Realism |
|---------|----------------|---------|
| **Black-box** | Only the question | High — like editing a wiki or uploading a doc |
| **White-box** | Also the retriever's model + weights | Low — but shows the upper bound |

---

## 4. How the attack works — the two conditions

A malicious text is only useful if it satisfies **both** of these at once:

1. **Retrieval condition** — the text must be similar enough to the target question to be **retrieved** into the top-K. *(If it's never retrieved, it never reaches the LLM.)*
2. **Generation condition** — once retrieved, the text must **mislead the LLM** into producing the target answer. *(If it doesn't mislead, the attack fails.)*

### The decomposition trick: `P = S + I`

Each poison document `P` is split into two purpose-built halves:

- **`S` — retrieval trigger:** crafted to match the question semantically → solves the retrieval condition. *(The disguise.)*
- **`I` — injection text:** contains the misinformation that pushes the LLM toward the wrong answer → solves the generation condition. *(The payload.)*

> **Trojan-horse analogy:** `S` is the disguise that gets the horse through the gate (retrieval). `I` is the soldier hiding inside that does the damage (generation).

### Framed as optimization

Crafting poison is framed as an **optimization problem**: find the set of malicious texts that maximizes the chance of the target answer, subject to being retrievable. Two solvers:

- **Black-box solver:** use an LLM to *generate* the poison directly ("write a passage supporting this answer for this question"), embed the question's keywords for retrieval. No internal access needed.
- **White-box solver:** use **gradient-based optimization (HotFlip-style)** to perfect the retrieval trigger `S`. Higher success, but needs retriever weights.

---

## 5. Results — the headline numbers

| Metric | Value |
|--------|-------|
| **Attack success rate** | **~90%** |
| Poison docs per question | **5** |
| Clean docs in KB | **millions** |

Proven across:

- **LLMs:** GPT-4, GPT-3.5, LLaMA-2, Vicuna, PaLM 2
- **Retrievers:** Contriever, DPR, ANCE
- **Datasets:** Natural Questions (NQ), HotpotQA, MS-MARCO

The attack **generalizes** — it isn't a one-off against a single configuration.

---

## 6. Defenses the paper tested — and why they fail

The authors evaluated the obvious defenses and showed all are **insufficient**:

| Defense | What it does | Why it fails |
|---------|--------------|--------------|
| **Perplexity filtering** | Drop docs with abnormal (high-perplexity) language | Poison is LLM-generated, so it reads fluently with *natural* perplexity |
| **Query paraphrasing** | Reword the question before retrieval | Poison matches *meaning*, not exact words — rewording doesn't move embeddings enough |
| **Knowledge expansion** | Retrieve more docs to dilute poison | More docs still include the poison, and the LLM keeps weighting it |

**Even with defenses on, attack success stays alarmingly high (~30%+).** The paper explicitly concludes that current defenses don't work and **calls for new defenses.**

> **This sentence is our entire project justification.** The authors admit the gap; we fill it.

---

## 7. Key terms cheat-sheet

| Term | Meaning |
|------|---------|
| **RAG** | Retrieval-Augmented Generation |
| **KB** | Knowledge Base — the document store the retriever searches |
| **Retriever** | Model that finds top-K relevant docs (Contriever, DPR, ANCE) |
| **top-K** | The K most-similar docs returned for a query |
| **ASR** | Attack Success Rate |
| **Poison doc** | A malicious text injected into the KB |
| **`S` / `I`** | Retrieval trigger / Injection text (the two halves of a poison doc) |
| **Black-box** | Attacker knows only the question |
| **White-box** | Attacker also knows retriever internals |
| **HotFlip** | Gradient-based token-substitution technique used in white-box |
| **Perplexity** | A measure of how "surprising"/unnatural text is to a language model |

---

## 8. One-line summary to memorize

> *"PoisonedRAG is the first attack to weaponize the RAG knowledge base: 5 fake documents among millions achieve 90% attack success, and the paper's own tests show existing defenses can't stop it."*

Next: see [`gap_and_fix.md`](gap_and_fix.md) for what we build on top of this.


---

[Repo Home](../README.md) · [Docs Index](README.md) · **Paper Summary** · [Gap & Fix](gap_and_fix.md) · [Viva Q&A](viva_qa.md)

[↑ Back to top](#top)
