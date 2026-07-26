<a id="top"></a>

# 📗 TECH GUIDE — sentence-transformers & all-mpnet-base-v2
### The Tool That Turns Sentences Into Numbers
### Explained & Useful for the Author

---

## 🔝 Top Navigation

[⬅ Repo Home](../../README.md) · [Docs Index](../README.md) · [🏠 Study Index](RAGSHIELD_INDEX.md) · [🔍 FAISS](TECH_FAISS.md) · [📙 Streamlit ➡](TECH_STREAMLIT.md) · [📕 LLM APIs ➡](TECH_LLM_APIS.md)

---

## 📌 Table of Contents

- [A. The Story — Why Turn Words Into Numbers?](#a--story)
- [B. What "all-mpnet-base-v2" Actually Is](#b-what-is-mpnet)
- [C. Notation and Vocabulary](#c-notation)
- [D. Step-by-Step — How a Sentence Becomes a Vector](#d-step-by-step)
- [E. Why "Meaning Space" Works — A Worked Example](#e-meaning-space)
- [F. Where This Tool Lives in Our Code](#f-in-our-code)
- [G. Why 768 Dimensions? Why Not More or Fewer?](#g-why-768)
- [H. CPU vs GPU — Why We Use CPU](#h-cpu-vs-gpu)
- [I. Mnemonics](#i-mnemonics)
- [J. Cheatsheet](#j-cheatsheet)
- [K. Exam Hacks](#k-exam-hacks)

---

<a id="a--story"></a>
## A. The Story — Why Turn Words Into Numbers?

Computers are REALLY good at comparing numbers. They are TERRIBLE at
directly understanding "meaning" the way humans do.

```
Can a computer easily tell these two sentences mean almost the
same thing?

  "Tesla was founded by Martin Eberhard"
  "The person who started Tesla was Eberhard"

Not directly — the WORDS are different (was founded by vs
the person who started), even though the MEANING is nearly
identical to a human reader.
```

**The trick:** use a special AI model to convert each sentence into
a list of numbers (a "vector" — see
[Math Primer, Part 2](RAGSHIELD_MATH_PRIMER.md#part2)) such that
sentences with SIMILAR MEANING end up as SIMILAR NUMBER-LISTS, even
if they use completely different words.

```
"Tesla was founded by Martin Eberhard"
      --->  [0.021, -0.443, 0.198, ..., 0.077]

"The person who started Tesla was Eberhard"
      --->  [0.019, -0.451, 0.203, ..., 0.081]
             (VERY CLOSE numbers — even though different words!)

"The Eiffel Tower is in Paris"
      --->  [0.812, 0.114, -0.290, ..., 0.445]
             (VERY DIFFERENT numbers — different meaning!)
```

**`sentence-transformers` is the Python library that does this
conversion. `all-mpnet-base-v2` is the specific pre-trained AI model
we chose to use inside that library.**

[⬆ Back to top](#top)

---

<a id="b-what-is-mpnet"></a>
## B. What "all-mpnet-base-v2" Actually Is

Breaking down the name piece by piece:

```
"all"    = trained on a huge VARIETY of text sources (not just one
           narrow topic), so it understands general English well

"mpnet"  = the specific neural network ARCHITECTURE (design blueprint)
           this model is built on — "MPNet" is a type of transformer
           model, similar in spirit to BERT but with some
           improvements to how it learns word order and context

"base"   = the "medium size" version — not the tiniest, not the
           biggest, a good balance of speed and quality

"v2"     = "version 2" — an improved, later release compared to
           earlier attempts at this same model
```

**In plain English:** it's a well-tested, general-purpose,
medium-sized AI model, specifically trained to be GOOD at the exact
job we need — turning sentences into meaningful number-lists.

[⬆ Back to top](#top)

---

<a id="c-notation"></a>
## C. Notation and Vocabulary

```
encoder / embedding model  = the AI model that converts text into
                             vectors (all-mpnet-base-v2 is our encoder)

embedding                  = the resulting vector — the "location"
                             a piece of text ends up at in meaning-space

embedding dimension        = how many numbers are in each vector
                             (768 for our model)

tokenization                = breaking a sentence into smaller pieces
                             (roughly words or parts of words) before
                             the model processes them

encoding / inference        = the actual act of running text THROUGH
                             the model to produce its vector

batch                       = processing several sentences at once
                             (faster than one at a time)

normalize_embeddings         = an option that shrinks every output
                             vector to length exactly 1 (see Math
                             Primer's cosine similarity section for
                             why this matters)
```

[⬆ Back to top](#top)

---

<a id="d-step-by-step"></a>
## D. Step-by-Step — How a Sentence Becomes a Vector

```
STEP 1 — Tokenization
    "Tesla was founded by Martin Eberhard"
    breaks into tokens (roughly):
    ["Tesla", "was", "founded", "by", "Martin", "Eber", "##hard"]
    (some rare words get split into smaller pieces — this is normal)

STEP 2 — Each token gets an initial number-representation
    The model has already LEARNED (during its original training,
    on huge amounts of text) a rough numerical meaning for common
    word-pieces

STEP 3 — The Transformer processes them TOGETHER, not separately
    This is the clever part: the model looks at ALL the tokens in
    context together, so "founded" next to "Tesla" and "Eberhard"
    gets adjusted differently than "founded" in a totally different
    sentence about, say, a country's founding

STEP 4 — Pooling — combine all token-level outputs into ONE vector
    The model produces one output per token, but we want ONE vector
    for the WHOLE sentence — so the outputs get averaged/combined
    into a single 768-number summary vector

STEP 5 — (Optional) Normalisation
    If normalize_embeddings=True, the final vector is shrunk to
    length exactly 1 (see Math Primer Part 3) — this makes later
    cosine-similarity comparisons in FAISS simpler and faster
```

[⬆ Back to top](#top)

---

<a id="e-meaning-space"></a>
## E. Why "Meaning Space" Works — A Worked Example

Imagine a 2-number simplified version (real vectors have 768 numbers,
but 2 is easier to visualise on a piece of paper):

```
                      y-axis
                        |
   "car" topics  •      |
     •  •               |
        •               |    • "boat" topics
                        |  •
    ─────────────────────────────────── x-axis
                        |
   "food" topics •      |
        •  •            |
                        |

Sentences about similar topics cluster together in this space.
"Tesla founded by Eberhard" and "Eberhard started Tesla" would land
VERY close to each other, even with different wording — because the
MODEL learned that these phrasings carry similar meaning during its
original training on billions of sentences.
```

This is exactly why FAISS's job (comparing these vectors' locations)
works so well for finding "similar meaning" documents — the hard
work of UNDERSTANDING meaning was already done by
`all-mpnet-base-v2`; FAISS just measures distances in the resulting
number-space.

[⬆ Back to top](#top)

---

<a id="f-in-our-code"></a>
## F. Where This Tool Lives in Our Code

**File:** `ragshield_core/retriever.py`

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-mpnet-base-v2", device="cpu")

# Encoding documents (happens once, when building the KB)
doc_embeddings = model.encode(
    all_document_texts,
    normalize_embeddings=True,   # shrink every vector to length 1
    batch_size=32,                # process 32 docs at once (faster)
)

# Encoding a query (happens per user question)
query_embedding = model.encode(
    [user_question],
    normalize_embeddings=True,
)
```

`doc_embeddings` and `query_embedding` are then handed straight to
FAISS (see [TECH_FAISS.md](TECH_FAISS.md)) for the actual similarity
search.

[⬆ Back to top](#top)

---

<a id="g-why-768"></a>
## G. Why 768 Dimensions? Why Not More or Fewer?

```
Fewer dimensions (e.g. 384, used by smaller models like MiniLM):
  + Faster to compute and search
  + Less memory needed
  − Less capacity to capture subtle shades of meaning

More dimensions (e.g. 1024, used by larger models):
  + More capacity for nuance
  − Slower, more memory, diminishing returns for most use cases

768 dimensions (all-mpnet-base-v2):
  A well-tested "sweet spot" — enough capacity to distinguish
  subtle meaning differences (needed to catch cleverly-worded
  poison text) while remaining fast enough for interactive,
  real-time search over thousands to millions of documents.
```

This is exactly the kind of trade-off discussed in
[Math Primer, Part 10.2](RAGSHIELD_MATH_PRIMER.md#part10) —
"approximate/smaller" isn't automatically worse; it's a deliberate
balance of cost and capability.

[⬆ Back to top](#top)

---

<a id="h-cpu-vs-gpu"></a>
## H. CPU vs GPU — Why We Use CPU

```
GPU (Graphics Processing Unit) = a chip designed to do MANY
    calculations at once, in parallel — great for AI, generally
    much faster than CPU for this kind of work

CPU (Central Processing Unit) = the "regular" main processor in
    every computer, good at a wide variety of tasks but generally
    slower for this specific kind of massive parallel math
```

**Why we deliberately use CPU (`device="cpu"`) despite GPU usually
being faster:** on Apple Silicon Macs (like the M1 Max used in this
project), the GPU acceleration path for `sentence-transformers`
(called "MPS," Apple's GPU framework) has a known bug that causes
crashes specifically inside long-running Streamlit sessions. CPU
mode is roughly 5x slower per encode, but it never crashes — and
for our KB sizes (thousands, not millions, of documents), CPU speed
is still fast enough that the trade-off is clearly worth it for
demo stability.

[⬆ Back to top](#top)

---

<a id="i-mnemonics"></a>
## I. Mnemonics

```
ENCODER = "meaning-to-numbers translator"

all-mpnet-base-v2 = "ALL-purpose, MPNet design, BASE size, Version 2"

SIMILAR MEANING = SIMILAR NUMBERS
    (this one sentence explains the entire point of embeddings)

768 = the sweet spot: enough detail, still fast
```

[⬆ Back to top](#top)

---

<a id="j-cheatsheet"></a>
## J. Cheatsheet

```
┌──────────────────────────────────────────────────────────────┐
│ TERM                  │ MEANING                              │
├──────────────────────────────────────────────────────────────┤
│ sentence-transformers │ Python library for text-to-vector    │
│ all-mpnet-base-v2     │ the specific AI model we use         │
│ Embedding             │ the output vector (768 numbers)      │
│ Tokenization          │ breaking text into pieces before     │
│                       │ feeding it to the model              │
│ Pooling               │ combining per-token outputs into ONE │
│                       │ sentence-level vector                │
│ normalize_embeddings  │ shrink vector to length 1 (helps     │
│                       │ cosine similarity math later)        │
│ device="cpu"          │ run on the normal processor, not GPU,│
│                       │ to avoid an Apple MPS crash bug      │
└──────────────────────────────────────────────────────────────┘
```

[⬆ Back to top](#top)

---

<a id="k-exam-hacks"></a>
## K. Exam Hacks

```
TRAP: "Does sentence-transformers understand the TEXT MEANING like
       a human?"
SAFE: "Not in a human sense — it's a statistical model trained on
       massive amounts of text to place similar-meaning sentences
       at similar numerical locations. It's pattern-matching at
       enormous scale, not conscious understanding."

TRAP: "Why CPU instead of GPU if GPU is normally faster?"
SAFE: "Apple's GPU acceleration path (MPS) has a known crash bug
       inside long-running Streamlit sessions on M1/M2 Macs. CPU
       is slower per-call but never crashes — the right trade-off
       at our current knowledge-base scale."

TRAP: "Why exactly 768 dimensions?"
SAFE: "It's the dimensionality all-mpnet-base-v2 was trained to
       output — a deliberately chosen balance between capturing
       enough semantic nuance and staying fast enough for
       real-time search."
```

[⬆ Back to top](#top)

---

## 🔚 Bottom Navigation

[⬅ Repo Home](../../README.md) · [Docs Index](../README.md) · [🏠 Study Index](RAGSHIELD_INDEX.md) · [🔍 FAISS](TECH_FAISS.md) · [📙 Streamlit ➡](TECH_STREAMLIT.md) · [📕 LLM APIs ➡](TECH_LLM_APIS.md)

[⬆ Back to top](#top)
