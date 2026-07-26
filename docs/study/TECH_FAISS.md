<a id="top"></a>

# 🔍 TECH GUIDE — FAISS
### The Library That Finds "Similar" Things Fast
### Explained & Useful for the Author

---

## 🔝 Top Navigation

[⬅ Repo Home](../../README.md) · [Docs Index](../README.md) · [🏠 Study Index](RAGSHIELD_INDEX.md) · [🎓 Math Primer](RAGSHIELD_MATH_PRIMER.md) · [📗 sentence-transformers ➡](TECH_SENTENCE_TRANSFORMERS.md) · [📙 Streamlit ➡](TECH_STREAMLIT.md) · [📕 LLM APIs ➡](TECH_LLM_APIS.md)

---

## 📌 Table of Contents

- [A. The Baby Story — What Problem Does FAISS Solve?](#a-baby-story)
- [B. What FAISS Actually Is](#b-what-is-faiss)
- [C. Notation and Vocabulary](#c-notation)
- [D. The Two Index Types We Use](#d-index-types)
- [E. Step-by-Step — How a Search Actually Happens](#e-step-by-step)
- [F. Where FAISS Lives in Our Code](#f-in-our-code)
- [G. Scaling — 5,000 Docs vs 2.6 Million Docs](#g-scaling)
- [H. Mnemonics](#h-mnemonics)
- [I. Cheatsheet](#i-cheatsheet)
- [J. Exam Hacks](#j-exam-hacks)

---

<a id="a-baby-story"></a>
## A. The Baby Story — What Problem Does FAISS Solve?

Imagine a **giant toy box** with a million toys in it. You're holding
a red rubber ball and you want to find the 5 toys in the box that are
MOST SIMILAR to your ball.

```
   YOUR BALL              THE GIANT TOY BOX (1,000,000 toys)
   (red, round,           [toy1] [toy2] [toy3] ... [toy999999] [toy1000000]
    rubber)

   You want: the 5 MOST SIMILAR toys, out of a million, FAST.
```

If you checked every single toy one by one, comparing it to your
ball, that would take forever with a million toys. **FAISS is a
tool built by Facebook/Meta that does this comparison job
extremely fast**, even with millions or billions of "toys"
(in our case, "toys" = documents turned into number-lists).

**FAISS = Facebook AI Similarity Search.** That's literally what the
name means — a search tool for finding similar things, made by
Facebook's AI researchers.

[⬆ Back to top](#top)

---

<a id="b-what-is-faiss"></a>
## B. What FAISS Actually Is

FAISS is NOT an AI model. It doesn't "understand" anything. It's a
**super-fast calculator for comparing lists of numbers** (vectors —
see [Math Primer, Part 2](RAGSHIELD_MATH_PRIMER.md#part2) if you
haven't read that yet).

```
INPUT to FAISS:  a big pile of vectors (lists of numbers),
                 PLUS one "query" vector you want matches for

OUTPUT from FAISS: the IDs of the vectors most similar to your query,
                   ranked from most similar to least similar,
                   computed FAST even with millions of vectors
```

In our project, every document gets turned into a 768-number vector
(using a different tool called `sentence-transformers` — see its
own guide). FAISS's ONLY job is: given all those vectors, find the
5 closest ones to whatever question the user just asked.

[⬆ Back to top](#top)

---

<a id="c-notation"></a>
## C. Notation and Vocabulary — Read This First

```
vector           = a list of numbers describing a "location"
                   (e.g. [0.02, -0.44, 0.19, ...] with 768 numbers)

dimension (d)    = how many numbers are in each vector
                   our project uses d = 768

index            = FAISS's internal organised storage of all vectors,
                   built so that searching through it is fast

query vector     = the ONE vector you're searching FOR
                   (the user's question, turned into numbers)

top-K            = "give me the K closest matches"
                   our project uses K = 5

similarity score = a number saying how close two vectors are
                   (we use "inner product," explained below)

inner product    = multiply matching numbers together, then add
                   them all up (see Math Primer, Part 3, for the
                   full "dot product" explanation)

nlist            = (only for the scaled-up index) how many "bins"
                   we sort vectors into ahead of time

nprobe           = (only for the scaled-up index) how many bins we
                   actually check per search
```

[⬆ Back to top](#top)

---

<a id="d-index-types"></a>
## D. The Two Index Types We Use

### D.1 — `IndexFlatIP` (what our current 5,000-doc demo uses)

**"Flat" means: no shortcuts. Check EVERY single vector, one by one.**

```
Imagine you have 12 crayons in a small box. To find the reddest
crayon, you just look at ALL 12 — that's fast enough with only 12.

IndexFlatIP does the SAME THING but with math: compares your query
vector against EVERY vector in the index, computes the similarity
score for each one, then returns the top-K highest scores.

"IP" = Inner Product — the specific math operation used to measure
similarity (see Math Primer for the dot-product explanation; when
both vectors are normalised to length 1, inner product = cosine
similarity).
```

**Why this is fine for our current project (~5,000-12 docs):**
Checking every single one of 5,000 vectors takes a tiny fraction of
a second on a normal computer. No shortcuts needed yet.

**Why this becomes a problem at 2.6 million docs:**
Checking every single one of 2.6 million vectors, for EVERY query,
starts taking noticeably longer, and storing 2.6 million vectors
needs a lot of computer memory (~8 gigabytes just for the vectors).
This is explained fully in
[Numericals Section H](RAGSHIELD_NUMERICALS.md#h-scaling-math).

### D.2 — `IndexIVFFlat` (what we'll switch to at scale)

**"IVF" = Inverted File index. The kid version: sort toys into
labelled bins FIRST, then only check the most promising bins.**

```
Instead of comparing your red ball to all 1,000,000 toys,
imagine someone ALREADY sorted the toy box into 4,096 labelled
bins by rough colour/shape/material BEFORE you even started
looking. Now you only need to check the ~32 bins most likely to
have similar toys — not all 4,096, and definitely not all
1,000,000 individual toys.

This is dramatically faster. The tiny cost: there's a small chance
a genuinely similar toy got sorted into a bin you didn't check.
That's called "approximate" search — see Math Primer Part 10.2 for
why "approximate" isn't a bad word here; it's industry-standard
at this scale.
```

```python
import faiss
d = 768
nlist = 4096                                  # number of "bins"
quantizer = faiss.IndexFlatIP(d)              # used to build the bins
index = faiss.IndexIVFFlat(quantizer, d, nlist,
                            faiss.METRIC_INNER_PRODUCT)
index.train(sample_vectors)                   # teaches FAISS how
                                               # to sort into bins
index.add(all_2_million_vectors)              # actually stores them
index.nprobe = 32                             # how many bins to
                                               # check per search
```

[⬆ Back to top](#top)

---

<a id="e-step-by-step"></a>
## E. Step-by-Step — How a Search Actually Happens

```
STEP 1 — Build time (happens ONCE, when the knowledge base is created)
    Every document is turned into a 768-number vector
    (using sentence-transformers — see its own guide)
    All these vectors get loaded into a FAISS index:
        index.add(all_document_vectors)

STEP 2 — Query time (happens EVERY time a user asks a question)
    The user's question also gets turned into a 768-number vector
    (using the SAME sentence-transformers model, so they're
     comparable — like using the same ruler to measure two things)

STEP 3 — FAISS searches
    scores, doc_ids = index.search(query_vector, k=5)
    "search" compares the query vector against the stored vectors
    (all of them, if IndexFlatIP; only the nearby "bins," if
     IndexIVFFlat) and returns the 5 best matches

STEP 4 — Ranking
    FAISS returns doc_ids sorted from MOST similar to LEAST similar,
    along with their similarity scores
    RAG-Shield then hands these 5 documents to Ring 1 for screening
```

[⬆ Back to top](#top)

---

<a id="f-in-our-code"></a>
## F. Where FAISS Lives in Our Code

**File:** `ragshield_core/retriever.py`

```python
# Building the index (happens once)
self._faiss = faiss.IndexFlatIP(emb.shape[1])   # emb.shape[1] = 768
self._faiss.add(emb.astype(np.float32))          # store all doc vectors

# Searching (happens per query)
scores, idx = self._faiss.search(qv, k)
# scores = similarity numbers, idx = which documents they belong to
```

`emb.astype(np.float32)` converts the numbers into a specific storage
format (32-bit floating point) that FAISS is optimised to work with
— think of it like making sure everyone's using the same units
(metres vs feet) before comparing measurements.

[⬆ Back to top](#top)

---

<a id="g-scaling"></a>
## G. Scaling — 5,000 Docs vs 2.6 Million Docs

```
                        5,000 docs          2.6 million docs
─────────────────────────────────────────────────────────────
Index type              IndexFlatIP         IndexIVFFlat
Search style             Exact (checks       Approximate (checks
                        everything)          only nearby "bins")
Memory needed            ~15 MB               ~8 GB
Search speed             Instant              Still fast, if tuned
                                              well (nprobe matters)
Setup complexity          Trivial              Needs a "training"
                                              step first
```

The GOOD NEWS (proven in
[Numericals Section H](RAGSHIELD_NUMERICALS.md#h-scaling-math)):
switching index types changes NOTHING about Ring 1, Ring 2, or
Ring 3's math. Only this one retrieval step changes.

[⬆ Back to top](#top)

---

<a id="h-mnemonics"></a>
## H. Mnemonics

```
FAISS = "Facebook AI Similarity Search" — a calculator for comparing
        lists of numbers FAST, not an AI model itself

FLAT = "no shortcuts, check everything" (exact, small-scale)
IVF  = "sort into bins first, check only nearby bins"
       (approximate, large-scale)

IP = Inner Product — multiply-then-add, the same idea as cosine
     similarity when vectors are normalised to length 1
```

[⬆ Back to top](#top)

---

<a id="i-cheatsheet"></a>
## I. Cheatsheet

```
┌──────────────────────────────────────────────────────────────┐
│ CONCEPT       │ MEANING                                      │
├──────────────────────────────────────────────────────────────┤
│ FAISS         │ Fast tool for comparing vectors, by Meta     │
│ Index         │ FAISS's organised storage of all vectors     │
│ IndexFlatIP   │ Exact search — checks EVERY vector           │
│ IndexIVFFlat  │Approximate search — checks nearby "bins" only│
│ nlist         │ How many bins to create                      │
│ nprobe        │ How many bins to check per search            │
│ top-K         │ How many best matches to return (K=5 for us) │
└──────────────────────────────────────────────────────────────┘
```

[⬆ Back to top](#top)

---

<a id="j-exam-hacks"></a>
## J. Exam Hacks

```
TRAP: "Isn't FAISS an AI model that understands documents?"
SAFE: "No — FAISS only compares numbers. A separate model
       (sentence-transformers) turns documents into numbers first.
       FAISS's only job is fast comparison of those numbers."

TRAP: "Why not use IndexIVFFlat from the start, even at small scale?"
SAFE: "IndexIVFFlat needs a training step and introduces a small
       recall trade-off — unnecessary complexity at 5,000 docs
       where exact search is already instant. We use it only when
       scale demands it."

TRAP: "Does switching index types change RAG-Shield's defense math?"
SAFE: "No — Ring 1/2/3 formulas never reference which index
       produced the retrieval score. Proven in Numericals Section H."
```

[⬆ Back to top](#top)

---

## 🔚 Bottom Navigation

[⬅ Repo Home](../../README.md) · [Docs Index](../README.md) · [🏠 Study Index](RAGSHIELD_INDEX.md) · [🎓 Math Primer](RAGSHIELD_MATH_PRIMER.md) · [📗 sentence-transformers ➡](TECH_SENTENCE_TRANSFORMERS.md) · [📙 Streamlit ➡](TECH_STREAMLIT.md) · [📕 LLM APIs ➡](TECH_LLM_APIS.md)

[⬆ Back to top](#top)
