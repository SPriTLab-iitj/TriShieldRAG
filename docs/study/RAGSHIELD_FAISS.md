<a id="top"></a>

# 🔍 RAGSHIELD_FAISS.md — FAISS & IndexFlatIP Explained
### How fast document search actually works — in RAG generally, and in RAG-Shield specifically

---

## 🔝 TOP NAVIGATION — Jump to any file

**Related:** [RAGSHIELD_THEORY.md](RAGSHIELD_THEORY.md#top) (the story) → [RAGSHIELD_NUMERICALS.md](RAGSHIELD_NUMERICALS.md#top) (the math) → [RAGSHIELD_PRACTICE.md](RAGSHIELD_PRACTICE.md#top) (running it) → **This file:** RAGSHIELD_FAISS.md (the search engine)
 
[🏠 Repo Home](../../README.md) &nbsp;·&nbsp; [📂 Docs Index](../README.md) &nbsp;·&nbsp; [📘 Theory](RAGSHIELD_THEORY.md#top) &nbsp;·&nbsp; [🧮 Numericals](RAGSHIELD_NUMERICALS.md#top) &nbsp;·&nbsp; [🛠️ Practice](RAGSHIELD_PRACTICE.md#top) &nbsp;·&nbsp; [🔍 FAISS (you are here)](#top) &nbsp;·&nbsp; [📖 Architectures](RAG_ARCHITECTURES.md#top)

---

## 📌 TABLE OF CONTENTS

```
┌─────────────────────────────────────────────────────────────┐
│  This file stands ALONGSIDE Theory/Numericals/Practice —    │
│  it zooms into ONE specific tool (FAISS) used inside the    │
│  RETRIEVAL step, before Ring 1/2/3 ever run.                │
└─────────────────────────────────────────────────────────────┘
```

- [A. The Simple Story — Why Do We Need FAISS At All?](#a-simple-story)
- [B. What "IndexFlatIP" Actually Means, Word by Word](#b-word-by-word)
- [C. Notation and Vocabulary — Every Term, In Full Depth](#c-notation)
  - [C.0 Quick Lookup Table](#c0-quick-lookup)
  - [C.1 vector](#c1-vector)
  - [C.2 dimension (d)](#c2-dimension)
  - [C.3 index](#c3-index)
  - [C.4 query vector](#c4-query-vector)
  - [C.5 top-K](#c5-top-k)
  - [C.6 similarity score](#c6-similarity-score)
  - [C.7 inner product (IP) — quick preview](#c7-inner-product-preview)
  - [C.8 exhaustive search](#c8-exhaustive-search)
  - [C.9 approximate search, nlist, and nprobe](#c9-approximate-nlist-nprobe)
  - [C.10 Everything Together — A Full Worked Search](#c10-everything-together)
- [D. The Math — Inner Product, Step by Step](#d-math)
- [E. Step-by-Step — Building and Searching an Index](#e-step-by-step)
- [F. How RAG (in General) Uses FAISS](#f-rag-general)
- [G. How RAG-Shield Specifically Uses FAISS](#g-ragshield-specific)
- [H. IndexFlatIP vs IndexIVFFlat — Side by Side](#h-flat-vs-ivf)
- [I. Full Code Walkthrough From Our Repo](#i-code-walkthrough)
- [J. Mnemonics](#j-mnemonics)
- [K. Cheatsheet](#k-cheatsheet)
- [L. Exam Hacks](#l-exam-hacks)

---

<a id="a-simple-story"></a>
## A. The Simple Story — Why Do We Need FAISS At All?

Imagine a **giant toy box** with a million toys inside. You're
holding a red rubber ball and want to find the 5 toys in the box
that are MOST SIMILAR to your ball.

```
   YOUR BALL              THE GIANT TOY BOX (1,000,000 toys)
   (red, round,           [toy1] [toy2] [toy3] ... [toy999999] [toy1000000]
    rubber)

   You want: the 5 MOST SIMILAR toys, out of a million, FAST.
```

If you checked every single toy one by one, comparing it to your
ball, that would take forever with a million toys. **FAISS is a
tool built by Meta (Facebook) that does this comparison job
extremely fast**, even with millions or billions of "toys" — in
our case, documents that have been turned into lists of numbers.

**FAISS = Facebook AI Similarity Search.** That's literally what
the name means — a search tool for finding similar things.

**Important: FAISS does NOT understand meaning.** It's not an AI
model. It's a super-fast calculator for comparing lists of numbers.
A separate tool (`all-mpnet-base-v2`, a sentence-embedding model)
does the job of turning text into meaningful numbers FIRST — FAISS
only compares those numbers afterward.

[⬆ Back to top](#top)

---

<a id="b-word-by-word"></a>
## B. What "IndexFlatIP" Actually Means, Word by Word

```
"Index"  = FAISS's organised storage container for all your
           vectors — think of it as a specially-designed filing
           cabinet built for fast similarity lookups

"Flat"   = NO shortcuts. Every single vector gets checked, one by
           one, every single search. Nothing is skipped, nothing
           is pre-sorted into groups.

"IP"     = Inner Product — the specific MATH RULE used to measure
           how similar two vectors are (explained fully in
           Section D below)
```

**Put together:** `IndexFlatIP` = "a storage container that checks
EVERY vector exhaustively, using the inner-product math rule to
measure similarity." It is the SIMPLEST, most STRAIGHTFORWARD, and
most EXACT search method FAISS offers — nothing clever, nothing
approximate, just a thorough, honest, one-by-one comparison.

[⬆ Back to top](#top)

---

<a id="c-notation"></a>
## C. Notation and Vocabulary — Every Term, In Full Depth

<a id="c0-quick-lookup"></a>
### C.0 — Quick Lookup Table (skim this first, full depth below)

```
┌───────────────────────────────────────────────────────────────────┐
│  TERM               │  ONE-LINE MEANING                           │
├───────────────────────────────────────────────────────────────────┤
│  vector             │  a list of numbers describing a "location"  │
│  dimension (d)      │  how many numbers are in each vector (768)  │
│  index              │  FAISS's organised storage of all vectors   │
│  query vector       │  the ONE vector you're searching FOR        │
│  top-K              │  "give me the K closest matches" (K=5)      │
│  similarity score   │  a number saying how close two vectors are  │
│  inner product (IP) │  multiply matching numbers, add them up     │
│  exhaustive search  │  checking EVERY vector, no shortcuts        │
│  approximate search │  checking only nearby "bins" — faster       │
│  nlist              │  how many "bins" get created ahead of time  │
│  nprobe             │  how many bins get checked per search       │
└───────────────────────────────────────────────────────────────────┘
```

This section goes term-by-term, in depth, before Section D shows
you the full inner-product formula worked by hand and Section H
compares the two index types side by side.

[⬆ Back to top](#top)

---

<a id="c1-vector"></a>
### C.1 — `vector` — "A List of Numbers Describing a Location"

Imagine a treasure map. To describe ONE spot on that map, you need
2 numbers: how far right, how far up.

```
   location = (3, 5)     "3 steps right, 5 steps up"
```

That's a **2-dimensional vector** — just 2 numbers, describing a
location. Now imagine a "map" that needs 768 different directions
instead of just "right" and "up" to pin down a location. That's a
**768-dimensional vector** — still just a list of numbers, only a
much longer list:

```
   v = [0.02, -0.44, 0.19, 0.07, -0.31, ..., 0.11]
        └──────────────── 768 numbers total ────────────────┘
```

*(Confirmed: `len([0.02, -0.44, 0.19]) = 3` — the dimension is
simply how many numbers are in the list.)*

In RAG-Shield, this "location" isn't a place on a physical map —
it's a location in **meaning-space**. A special AI model
(`all-mpnet-base-v2`) reads a sentence and converts its MEANING
into 768 numbers. Sentences with SIMILAR meaning end up at SIMILAR
locations in this space — that's the entire trick behind semantic
search (full explanation in
[RAGSHIELD_NUMERICALS.md, Notation Key](RAGSHIELD_NUMERICALS.md#notation)).

**Where this appears in your code:**
```python
# ragshield_core/retriever.py
emb = self._embedder.encode(texts, normalize_embeddings=True, ...)
# emb is a GRID of vectors — one 768-number row per document
```

[⬆ Back to top](#top)

---

<a id="c2-dimension"></a>
### C.2 — `dimension (d)` — "How Many Numbers Are In Each Vector"

```
dimension = the COUNT of numbers in one vector

v = [0.02, -0.44, 0.19]
len(v)  # = 3  <- this is the dimension
```

Our project always uses **d = 768**, because that's the exact
number of outputs the `all-mpnet-base-v2` model was trained to
produce for every sentence it encodes.

**Why does FAISS need to know `d` up front?**
```python
self._faiss = faiss.IndexFlatIP(emb.shape[1])
#                                 ^^^^^^^^^^^^
#                    this pulls out d = 768 from the embeddings'
#                    shape, and tells FAISS "every vector you'll
#                    ever store or search must have EXACTLY this
#                    many numbers" — like telling a filing cabinet
#                    "every folder here is letter-size, no other
#                    size folders allowed"
```

[⬆ Back to top](#top)

---

<a id="c3-index"></a>
### C.3 — `index` — "FAISS's Organised Storage of All Vectors"

Think of a **library card catalog** — not the books themselves, but
the organised SYSTEM that lets you find a book fast without walking
every aisle. A FAISS "index" is exactly that, but for vectors
instead of books.

```
┌─────────────────────────────────────────────────────────┐
│                    THE INDEX                            │
│                                                         │
│   doc_1's vector  ──┐                                   │
│   doc_2's vector  ──┼──▶  organised, searchable storage │
│   doc_3's vector  ──┤                                   │
│   ...             ──┘                                   │
│                                                         │
│   .search(query_vector, k=5)                            │
│         │                                               │
│         ▼                                               │
│   returns the 5 CLOSEST vectors, fast                   │
└─────────────────────────────────────────────────────────┘
```

That diagram is the 10-second version. Here's the master-level
version — what EXACTLY does an index store, what EXACTLY does
`.search()` hand back, and how does that ever turn into a document
you can read?

#### C.3.1 — What the Index Actually Stores (and Does NOT Store)

**The index stores ONLY numbers — never any text, titles, or
document IDs.** This surprises almost everyone the first time they
learn it.

```
┌──────────────────────────────────────────────────────────────────┐
│  WHAT LIVES INSIDE THE FAISS INDEX                               │
│                                                                  │
│  position 0:  [0.99, 0.11, 0.06, 0.02]   <- just numbers         │
│  position 1:  [0.11, 0.97, 0.23, 0.06]   <- just numbers         │
│  position 2:  [0.98, 0.17, 0.09, 0.01]   <- just numbers         │
│  position 3:  [0.05, 0.05, 0.99, 0.10]   <- just numbers         │
│  position 4:  [0.18, 0.94, 0.29, 0.04]   <- just numbers         │
│                                                                  │
│  NOTHING ELSE lives here. No titles. No text. No "this is        │
│  about Tesla" label. Just raw numbers, in the ORDER they         │
│  were added.                                                     │
└──────────────────────────────────────────────────────────────────┘
```

The only thing FAISS tracks per vector is its **position number**
— 0, 1, 2, 3, 4, in the exact order you called `.add()`. This
position number is the ENTIRE link between "a vector FAISS knows
about" and "a real document you can read." Nothing more.

#### C.3.2 — What `.search()` Actually Returns — Proven With Real Code

Let's build a real, tiny index and inspect EXACTLY what comes back
— no guessing, this is copy-pasted from an actual run:

```python
import faiss
import numpy as np

# 5 tiny 4-number "document vectors" (normally 768 numbers each —
# using 4 here purely so we can print them and read them easily)
doc_vectors = np.array([
    [0.90, 0.10, 0.05, 0.02],   # position 0 — pretend: "Tesla founding doc"
    [0.10, 0.85, 0.20, 0.05],   # position 1 — pretend: "Eiffel Tower doc"
    [0.88, 0.15, 0.08, 0.01],   # position 2 — pretend: ALSO about Tesla
    [0.05, 0.05, 0.95, 0.10],   # position 3 — pretend: "Einstein doc"
    [0.15, 0.80, 0.25, 0.03],   # position 4 — pretend: ALSO about Eiffel Tower
], dtype=np.float32)

# normalise every vector to length 1 first (see Section D.4)
doc_vectors = doc_vectors / np.linalg.norm(doc_vectors, axis=1, keepdims=True)

index = faiss.IndexFlatIP(4)
index.add(doc_vectors)
print(index.ntotal)   # -> 5   (confirms 5 vectors are stored)
```

```python
query_vector = np.array([[0.91, 0.09, 0.06, 0.01]], dtype=np.float32)
query_vector = query_vector / np.linalg.norm(query_vector)

scores, indices = index.search(query_vector, k=3)
```

**Here is the EXACT, real output of that call:**

```
scores.shape  = (1, 3)      <- (1 query, 3 results)
indices.shape = (1, 3)

RAW scores:  [[0.9998 0.9973 0.2866]]
RAW indices: [[0      2      4    ]]
```

**Reading this precisely:**

```
Rank 1: position 0, score 0.9998   <- the Tesla-founding doc, highest match
Rank 2: position 2, score 0.9973   <- the OTHER Tesla doc, second-highest
Rank 3: position 4, score 0.2866   <- an Eiffel Tower doc, barely related
```

**Two things to notice, both provable and both important:**

```
1. FAISS returned TWO separate arrays, not one combined result:
     - "scores"  = HOW SIMILAR (a plain number, 0.0 to 1.0)
     - "indices" = WHICH POSITION (a plain integer, 0 to N-1)

   It did NOT return document text, titles, or anything human-
   readable. Those two arrays of numbers are 100% of what FAISS
   gives you — full stop.

2. Both arrays are shaped (num_queries, k) — even when you send
   just ONE query, you get back a 2D array with ONE row, not a
   flat list. This trips people up constantly — always index with
   [0] to get "the first (and only) query's results":
       my_indices = indices[0]   # not indices, not indices[:,0]
```

#### C.3.3 — What Happens if You Ask for MORE Results Than Exist?

A genuinely important edge case, proven by actually running it:

```python
# only 5 documents exist, but we ask for k=10
scores_big, indices_big = index.search(query_vector, k=10)
```

```
indices returned: [[0, 2, 4, 1, 3, -1, -1, -1, -1, -1]]
scores returned:  [[0.9998, 0.9973, 0.2866, 0.2231, 0.1230,
                     -3.4e38, -3.4e38, -3.4e38, -3.4e38, -3.4e38]]
```

**FAISS PADS the extra slots with `-1` (an impossible index) and an
extremely negative/meaningless score.** This is not a bug — it's
FAISS telling you "I ran out of real results to give you." Any
production code that reads `.search()` output MUST check for
`idx == -1` and skip those entries, otherwise you'll try to look up
"document number -1" and either crash or silently pull the WRONG
document (Python allows negative indexing, so `self.docs[-1]`
would silently return your LAST document — a real, sneaky bug if
you don't guard against it).

#### C.3.4 — Batch Searching — Multiple Questions at Once

FAISS can search several queries in ONE call — useful for
evaluating many test questions quickly (see
[RAGSHIELD_PRACTICE.md's evaluation harness](RAGSHIELD_PRACTICE.md#e-scaling-steps)),
though our live Streamlit app only ever sends one question at a
time.

```python
query1 = [...]   # e.g. Tesla-like question
query2 = [...]   # e.g. Einstein-like question
queries = np.stack([query1, query2])   # shape: (2, 768)

scores, indices = index.search(queries, k=2)
# scores.shape  = (2, 2)   <- 2 queries, 2 results each
# indices.shape = (2, 2)

# Row 0 = query1's top-2 results
# Row 1 = query2's top-2 results — completely independent of row 0
```

Each row is its own, independent search — query2 doesn't "see" or
get influenced by query1 in any way. They just happen to run in the
same function call for efficiency.

#### C.3.5 — Does FAISS Return "Collections" or "Groups" of Documents?

**No — FAISS has no concept of a document "collection," "cluster
label," or "group" that it hands back to you.** Even `IndexIVFFlat`
(which internally sorts vectors into bins for faster searching —
see [C.9](#c9-approximate-nlist-nprobe)) never reveals WHICH bin a
result came from in its `.search()` output. Bins are a purely
INTERNAL optimisation detail; from the outside, `.search()` always
looks identical regardless of index type: two arrays, `scores` and
`indices`, nothing more.

```
┌──────────────────────────────────────────────────────────────────┐
│  MENTAL MODEL CORRECTION                                         │
│                                                                  │
│  WRONG: "FAISS returns a list of matching documents"             │
│  RIGHT: "FAISS returns a list of POSITION NUMBERS and SCORES —   │
│          converting position numbers into actual documents is    │
│          a separate step YOUR code does afterward"               │
└──────────────────────────────────────────────────────────────────┘
```

#### C.3.6 — The Missing Link: Turning Position Numbers Into Real Documents

This is the step that makes everything click. FAISS's index
positions are USELESS on their own — you need a second, parallel
list that remembers "position 0 = which real document?"

```python
# self.docs in ragshield_core/retriever.py is EXACTLY this parallel
# list — built in the SAME ORDER the vectors were added to FAISS:
docs = [
    {"id": "d0", "title": "Tesla, Inc.",            "text": "..."},  # position 0
    {"id": "d1", "title": "Eiffel Tower",            "text": "..."},  # position 1
    {"id": "d2", "title": "Tesla Motors History",    "text": "..."},  # position 2
    {"id": "d3", "title": "Theory of Relativity",    "text": "..."},  # position 3
    {"id": "d4", "title": "Eiffel Tower Construction","text": "..."},  # position 4
]
```

**Real, verified output — connecting FAISS's numbers back to actual
readable documents:**

```python
scores, indices = index.search(query_vector, k=3)

for score, idx in zip(scores[0], indices[0]):
    if idx == -1:
        continue          # skip FAISS's padding (see C.3.3)
    doc = docs[int(idx)]  # <- THE key lookup step
    print(doc["title"], score)
```

```
Tesla, Inc.              0.9998
Tesla Motors History     0.9973
Eiffel Tower Construction 0.2866
```

**This exact pattern — `docs[int(idx)]` — is precisely what
`ragshield_core/retriever.py`'s `retrieve()` method does.** FAISS's
`idx` is nothing more than a plain array-index number; `self.docs`
is a Python list kept in perfect lockstep with the vectors inside
FAISS. The moment these two lists get OUT of sync (for example, if
you add a vector to FAISS but forget to also append to
`self.docs`), position 5 in FAISS would silently return the WRONG
document's title/text — an easy, dangerous bug to introduce in any
system that manages a parallel index-to-document mapping by hand.

#### C.3.7 — Summary Table — Every Question Answered

```
┌──────────────────────────────────────────────────────────────────┐
│  QUESTION                         │  ANSWER                      │
├──────────────────────────────────────────────────────────────────┤
│  Does FAISS store text?           │  NO — only number vectors    │
│  Does FAISS return text?          │  NO — only scores+indices    │
│  Does FAISS return "documents"?   │  NO — just position numbers  │
│  Does FAISS return "collections"? │  NO — no grouping concept    │
│  What connects numbers to text?   │  YOUR OWN parallel list      │
│                                   │  (self.docs in retriever.py) │
│  What if k > stored vectors?      │  padded with -1 / -inf       │
│  Can you search many queries      │  YES — batched, one row per  │
│  at once?                         │  query, fully independent    │
└──────────────────────────────────────────────────────────────────┘
```

Two different "organisation styles" (index TYPES) exist —
`IndexFlatIP` (exact, checks everything) and `IndexIVFFlat`
(approximate, sorts into bins first). The FULL side-by-side
comparison is in [Section H](#h-flat-vs-ivf) below.

**Where this appears in your code:**
```python
self._faiss = faiss.IndexFlatIP(768)     # <- creates an empty index
self._faiss.add(emb.astype(np.float32))  # <- stores vectors in it
```

[⬆ Back to top](#top)

---

<a id="c4-query-vector"></a>
### C.4 — `query vector` — "The ONE Vector You're Searching FOR"

Every OTHER vector in this whole system describes a STORED
document. The query vector is different — it's the temporary,
one-time vector built from whatever the USER just asked, used only
to search against everything already stored.

```
┌───────────────────────────────────────────────────────────┐
│  STORED (many, built once, sit in the index)              │
│    doc_1 → [0.02, -0.44, ...]                             │
│    doc_2 → [0.31,  0.02, ...]                             │
│    doc_3 → [-0.11, 0.55, ...]                             │
│                                                           │
│  QUERY (one, built fresh every time a question arrives)   │
│    "Who founded Tesla Motors?" → [0.03, -0.41, ...]       │
└───────────────────────────────────────────────────────────┘
```

That's the summary. Now let's go deeper into WHY it works this way,
what makes a query vector special, and a common trap to avoid.

#### C.4.1 — A Query Vector Is Built EXACTLY Like a Document Vector

This is worth stating explicitly, because it's easy to assume
"searching" and "storing" are different operations that need
different tools. **They don't.** A query vector is produced by
feeding text through the SAME embedding model, using the SAME
settings, as every document vector already sitting in the index:

```python
# building a DOCUMENT vector (happens once, at KB build time):
doc_vec = model.encode(["Tesla was founded in 2003..."],
                        normalize_embeddings=True)

# building a QUERY vector (happens fresh, every single question):
query_vec = model.encode(["Who founded Tesla Motors?"],
                          normalize_embeddings=True)

# THE SAME FUNCTION. THE SAME MODEL. THE SAME normalize_embeddings
# SETTING. The only difference is WHEN you call it and WHAT text
# you feed it — not HOW you call it.
```

There is no special "query mode" inside the embedding model. If you
called `model.encode()` on a stored document's text a second time,
you'd get back the exact same vector every time (the model has no
randomness) — and that's the whole point: documents and queries
must land in the SAME 768-number space to be meaningfully
comparable at all.

#### C.4.2 — Why "Temporary" and "One-Time" Actually Matter

```
┌────────────────────────────────────────────────────────────────────┐
│  DOCUMENT VECTORS                      │  QUERY VECTOR             │
├────────────────────────────────────────────────────────────────────┤
│  Computed ONCE, when the KB is built   │  Computed FRESH, every    │
│  (or when new docs get added)          │  single time a question   │
│                                        │  arrives                  │
│                                        │                           │
│  STORED permanently inside the FAISS   │  NEVER stored inside      │
│  index — that's the whole point of     │  FAISS at all — used for  │
│  building an index in the first place  │  exactly one .search()    │
│                                        │  call, then thrown away   │
│                                        │                           │
│  If you ask the SAME question again    │  A brand-new query vector │
│  10 minutes later, the DOCUMENT        │  gets computed for THAT   │
│  vectors haven't changed at all        │  new request, even if the │
│                                        │  text is word-for-word    │
│                                        │  identical to a previous  │
│                                        │  question                 │
└────────────────────────────────────────────────────────────────────┘
```

**Where this appears in your code — traced through the full
request lifecycle:**

```python
# ragshield_core/retriever.py

class Retriever:
    def _ensure_faiss(self):
        # DOCUMENT vectors — built ONCE, when the KB is first loaded
        emb = self._embedder.encode(texts, normalize_embeddings=True, ...)
        self._faiss = faiss.IndexFlatIP(emb.shape[1])
        self._faiss.add(emb.astype(np.float32))
        # from this point on, these vectors just SIT in the index,
        # unchanged, ready to be searched against many times

    def retrieve(self, query: str, k: int = None):
        # QUERY vector — built FRESH, every single call to retrieve()
        qv = self._embedder.encode([query], normalize_embeddings=True)
        #    ^^ this line runs EVERY TIME a user asks a question —
        #       even if it's the exact same question as last time
        scores, idx = self._faiss.search(qv, k)
        ...
```

#### C.4.3 — The Trap: Mixing Embedding Models

**Critical detail:** the query MUST be turned into a vector using
the exact SAME embedding model as the stored documents — like using
the same ruler to measure both things you're comparing. Mixing
rulers (or embedding models) gives meaningless comparisons.

**Why this breaks things so badly, made concrete:**

```
Model A (e.g. all-mpnet-base-v2, 768 dimensions) places "Tesla" at
  roughly [0.9, 0.1, ...] in ITS OWN 768-number meaning-space.

Model B (e.g. a completely different model, maybe even a DIFFERENT
  number of dimensions, like 384) would place "Tesla" at a totally
  DIFFERENT set of numbers, in a DIFFERENT-shaped space, that has
  NO mathematical relationship to Model A's space at all.

If your DOCUMENTS were embedded with Model A, but your QUERY
accidentally gets embedded with Model B:
  - the dimensions might not even MATCH (768 vs 384 — FAISS would
    outright ERROR, refusing to compare vectors of different sizes)
  - even in the rare case dimensions happened to match by
    coincidence, the actual NUMBERS would mean something completely
    different in each model's space — like comparing a distance
    measured in miles against a distance measured in an entirely
    different, unrelated unit that just happens to also be called
    "miles"
  - inner product / similarity scores would become PURE NOISE —
    not "less accurate," but literally meaningless, since the two
    vectors don't share a common coordinate system at all
```

**How RAG-Shield guards against this in practice:** both the
document-embedding step (`_ensure_faiss`) and the query-embedding
step (`retrieve`) read the SAME `config.EMBED_MODEL` setting and use
the SAME `self._embedder` object — there is only ONE embedding
model loaded per `Retriever` instance, so this mismatch is
structurally impossible to introduce by accident in this codebase.

#### C.4.4 — Summary Table

```
┌──────────────────────────────────────────────────────────────────┐
│  QUESTION                           │  ANSWER                    │
├──────────────────────────────────────────────────────────────────┤
│  Built how many times?              │  ONCE per user question,   │
│                                     │  every single time         │
│  Stored inside FAISS permanently?   │  NO — used once, discarded │
│  Same embedding process as docs?    │  YES — identical function, │
│                                     │  identical model, identical│
│                                     │  settings                  │
│  Can it use a different model       │  NEVER — breaks the whole  │
│  than the documents?                │  comparison mathematically │
└──────────────────────────────────────────────────────────────────┘
```

**Where this appears in your code:**
```python
# ragshield_core/retriever.py, inside retrieve():
qv = self._embedder.encode([query], normalize_embeddings=True)
#    ^^ this ONE query gets embedded fresh, every single call
scores, idx = self._faiss.search(qv, k)
```

[⬆ Back to top](#top)

---

<a id="c5-top-k"></a>
### C.5 — `top-K` — "Give Me the K Closest Matches"

`K` is just a number you choose: "how many results do I want back?"

```
top-K = 5   means:   "return the 5 BEST matches, ranked
                       from most similar to least similar,
                       and throw away everything else"
```

**Worked example — what it actually feels like:**

```
Imagine 10,000 documents in your knowledge base.
A user asks a question.
FAISS compares the question to ALL 10,000 (or, at scale,
to the most likely candidates — see C.9 below).

Instead of handing the AI all 10,000 possibly-relevant documents
(slow, expensive, and mostly irrelevant), FAISS hands over ONLY
the top-5 best matches:

  Rank 1: doc_4821, similarity 0.87
  Rank 2: doc_0093, similarity 0.81
  Rank 3: doc_7734, similarity 0.79
  Rank 4: doc_2210, similarity 0.75
  Rank 5: doc_5567, similarity 0.71
  (all other 9,995 documents: ignored for this query)
```

This project always uses **K = 5** — a deliberate choice matching
the exact setup used in the PoisonedRAG paper we're defending
against (see [RAGSHIELD_THEORY.md, Section B](RAGSHIELD_THEORY.md#b-attack)),
so our results are directly comparable to theirs.

[⬆ Back to top](#top)

---

<a id="c6-similarity-score"></a>
### C.6 — `similarity score` — "A Number Saying How Close Two Vectors Are"

This is the actual NUMBER that comes out when FAISS compares two
vectors — the raw material Ring 2's trust formula partly relies on
(see [RAGSHIELD_NUMERICALS.md, Section E.3](RAGSHIELD_NUMERICALS.md#e-ring2-math)).

```
similarity score = 1.0   →  "these two mean almost exactly the
                             same thing"
similarity score = 0.5   →  "somewhat related"
similarity score = 0.0   →  "completely unrelated"
```

**Which specific formula produces this number in our project?**
**Inner product** — the full step-by-step formula and worked
example live in [Section D](#d-math) right after this section.

[⬆ Back to top](#top)

---

<a id="c7-inner-product-preview"></a>
### C.7 — `inner product (IP)` — Quick Preview (Full Detail in Section D)

```
inner product = multiply matching numbers together, then add
                up all the results
```

A tiny taste of the math, verified by actually running it:

```
query = [1, 2, 3]
doc   = [4, 5, 6]

1×4 = 4
2×5 = 10
3×6 = 18
sum = 4 + 10 + 18 = 32

inner_product(query, doc) = 32
```

**Don't stop here** — [Section D](#d-math) below expands this into
the full formula for all 768 numbers, explains WHY a bigger number
means "more similar," and covers the crucial normalisation detail
that makes this calculation trustworthy in the first place.

[⬆ Back to top](#top)

---

<a id="c8-exhaustive-search"></a>
### C.8 — `exhaustive search` — "Checking EVERY Vector, No Shortcuts"

This is what the word **"Flat"** in `IndexFlatIP` means (see
[Section B](#b-word-by-word)). Every single stored vector gets
compared against the query — nothing pre-sorted, nothing skipped.

```
┌─────────────────────────────────────────────────────────┐
│  EXHAUSTIVE SEARCH — checks ALL N vectors, every time   │
│                                                         │
│  query ──▶ compare to doc_1                             │
│        ──▶ compare to doc_2                             │
│        ──▶ compare to doc_3                             │
│        ──▶ ... every single one, no exceptions ...      │
│        ──▶ compare to doc_N                             │
│                                                         │
│  Guarantees: the TRUE top-K, always, no approximation   │
│  Cost: gets slower as N grows — at N=2.6 million,       │
│        that's 2.6 million comparisons PER QUERY         │
└─────────────────────────────────────────────────────────┘
```

This is exactly why `IndexFlatIP` is perfect for our current
5,000–20,000-document experiments (instant, exact) but needs to be
swapped for approximate search at 2.6-million-document scale —
covered next in C.9, and compared side-by-side in
[Section H](#h-flat-vs-ivf).

[⬆ Back to top](#top)

---

<a id="c9-approximate-nlist-nprobe"></a>
### C.9 — `approximate search`, `nlist`, and `nprobe`

**Approximate search** trades a small, controllable amount of
accuracy for a MASSIVE speed gain at scale — this is what
`IndexIVFFlat` does instead of checking everything.

```
┌─────────────────────────────────────────────────────────┐
│  APPROXIMATE SEARCH — sorts vectors into "bins" first,  │
│  then only checks a FEW nearby bins per query           │
│                                                         │
│  Building time (once):                                  │
│    all vectors ──▶ sorted into NLIST labelled bins      │
│                                                         │
│  Query time (every search):                             │
│    query ──▶ only checks NPROBE bins (the ones closest  │
│              to the query) — NOT all of them            │
└─────────────────────────────────────────────────────────┘
```

**`nlist`** = how many bins get created, ahead of time.
**`nprobe`** = how many of those bins actually get checked, per
search.

```
nlist = 500    →  sort all vectors into 500 labelled bins
nprobe = 31    →  only check the 31 bins CLOSEST to the query
                   (not all 500)

31 / 500 = 6.2% of all bins get checked per search
```

**The formulas this project actually uses** (see
[RAGSHIELD_NUMERICALS.md, Section H](RAGSHIELD_NUMERICALS.md#h-scaling-math)
for the full derivation, and
[RAGSHIELD_PRACTICE.md's troubleshooting section](RAGSHIELD_PRACTICE.md#d-troubleshooting)
for the exact bug this formula was built to avoid):

```python
nlist  = max(1, min(int(4 * math.sqrt(n)), n // 40, n))
nprobe = max(1, nlist // 16)
```

**Worked examples, computed and verified at real project scales:**

```
┌──────────────────────────────────────────────────────────────┐
│  n (documents)   │  nlist (bins)  │  nprobe (bins checked)   │
├──────────────────────────────────────────────────────────────┤
│       5,000      │      125       │        7  (5.6%)         │
│      10,000      │      250       │       15  (6.0%)         │
│      20,000      │      500       │       31  (6.2%)         │
│   2,600,000      │    6,449       │      403  (6.2%)         │
└──────────────────────────────────────────────────────────────┘
```

Notice the checked-percentage stays remarkably steady (~6%) at
every scale — that's `nlist // 16` doing its job: a fixed FRACTION
of bins gets checked no matter how many bins exist in total.

**Why `4 × sqrt(n)` for nlist?** FAISS's own commonly-recommended
rule of thumb — enough bins to meaningfully group similar vectors
together, without creating SO many bins that each one only has a
handful of vectors (which breaks clustering quality — see the
`nlist` warning explained in
[RAGSHIELD_PRACTICE.md's troubleshooting section](RAGSHIELD_PRACTICE.md#d-troubleshooting)).
Capping at `n // 40` keeps at least ~39 training vectors per bin,
which is what FAISS needs for good clustering.

[⬆ Back to top](#top)

---

<a id="c10-everything-together"></a>
## C.10 — Everything Together — One Real Search, Traced Term by Term

```
USER ASKS: "Who founded Tesla Motors?"

Step 1 — build a QUERY VECTOR (C.4)
    The question text is fed through all-mpnet-base-v2, producing
    a 768-DIMENSION (C.2) VECTOR (C.1): [0.03, -0.41, 0.22, ...]

Step 2 — the INDEX (C.3) is searched
    If using IndexFlatIP: EXHAUSTIVE SEARCH (C.8) compares the
    query against EVERY stored vector.
    If using IndexIVFFlat at scale: APPROXIMATE SEARCH (C.9)
    compares the query only against vectors in the NPROBE nearest
    of NLIST total bins.

Step 3 — INNER PRODUCT (C.7, fully detailed in Section D) computes
    a SIMILARITY SCORE (C.6) for each candidate — since every
    vector was normalised to length 1 first, this score behaves
    exactly like cosine similarity (0.0 = unrelated, 1.0 = identical)

Step 4 — the TOP-K (C.5, K=5) highest-scoring vectors are returned,
    ranked from most similar to least

Step 5 — those 5 documents get handed to Ring 1 for screening
    (see RAGSHIELD_THEORY.md, Section D)
```

[⬆ Back to top](#top)

---

<a id="d-math"></a>
## D. The Math — Inner Product, Step by Step

### D.1 — What "Inner Product" Actually Computes

```
Given two vectors:
    query  = [q1, q2, q3, ..., q768]
    doc    = [d1, d2, d3, ..., d768]

Inner product formula:
    IP(query, doc) = (q1×d1) + (q2×d2) + (q3×d3) + ... + (q768×d768)

In plain words: multiply each MATCHING pair of numbers together,
then add up ALL of those products into one single final number.
```

### D.2 — A Tiny Worked Example (3 numbers instead of 768)

```
query = [1, 2, 3]
doc   = [4, 5, 6]

Step 1 — multiply matching positions:
    1×4 = 4
    2×5 = 10
    3×6 = 18

Step 2 — add them all up:
    4 + 10 + 18 = 32

IP(query, doc) = 32
```

*(Verified by actually running this: `np.dot([1,2,3],[4,5,6])`
returns exactly `32`.)*

### D.3 — Why a BIGGER Inner Product Means MORE Similar

```
If two vectors point in a SIMILAR direction (similar meaning),
their matching numbers tend to have the SAME SIGN (both positive
or both negative) and similar SIZE — so each multiplication
produces a bigger positive number, and the total sum is large.

If two vectors point in DIFFERENT directions (different meaning),
their matching numbers often have OPPOSITE signs or very different
sizes — multiplications partly cancel out, and the total sum is
smaller (or even negative).

RULE: Bigger inner product = more similar. Smaller (or negative)
      inner product = less similar.
```

### D.4 — The Crucial Detail: Normalisation

```
Inner product ALONE is influenced by both DIRECTION and LENGTH of
the vectors. A very long vector pointing in a so-so direction could
score higher than a short vector pointing in a PERFECT direction —
which would be misleading.
```

**Proven with real numbers — an unnormalised vector can win purely
by being longer, not by being more similar:**

```
short_vec         = [1, 0, 0]      (length 1.0)
long_vec_same_dir = [10, 0, 0]     (length 10.0 — SAME direction!)
other_vec         = [0.9, 0.1, 0]  (length 0.91)

IP(short_vec, other_vec)         = 0.900
IP(long_vec_same_dir, other_vec) = 9.000

Both short_vec and long_vec_same_dir point in the EXACT SAME
direction — they should be EQUALLY similar to other_vec. But raw
inner product says long_vec_same_dir is 10x more similar, purely
because it's a LONGER vector. Misleading.
```

**The fix — normalise every vector to length 1 first:**

```
After normalising (shrinking each vector to length exactly 1.0,
keeping its direction unchanged):

IP(short_norm, other_norm) = 0.9939
IP(long_norm, other_norm)  = 0.9939

IDENTICAL now — once length is removed from the equation, inner
product ONLY reflects DIRECTION (meaning), which is what we
actually want to measure. At this point, inner product of two
length-1 vectors becomes mathematically IDENTICAL to cosine
similarity (see RAGSHIELD_NUMERICALS.md, Section D.3, for the
cosine similarity explanation used inside Ring 1's OutlierDetector).
```

This is why our code always sets `normalize_embeddings=True` when
creating vectors — see [Section I](#i-code-walkthrough) below.

[⬆ Back to top](#top)

---

<a id="e-step-by-step"></a>
## E. Step-by-Step — Building and Searching an Index

```
STEP 1 — Build time (happens ONCE, when the knowledge base is made)
    Every document is turned into a 768-number vector
    All these vectors get loaded into a FAISS index:
        index.add(all_document_vectors)

STEP 2 — Query time (happens EVERY time a user asks a question)
    The user's question ALSO gets turned into a 768-number vector,
    using the SAME embedding model (so they're comparable — like
    using the same ruler to measure two different things)

STEP 3 — FAISS searches
    scores, doc_ids = index.search(query_vector, k=5)
    "search" computes the inner product between the query and
    EVERY stored vector (for IndexFlatIP specifically — no
    shortcuts), then returns the 5 best matches

STEP 4 — Ranking
    FAISS returns doc_ids sorted from MOST similar to LEAST
    similar, along with their similarity scores

STEP 5 — Hand off to Ring 1
    RAG-Shield takes these 5 documents and passes them to
    Ring 1 (Ingest Guard) for screening — see
    RAGSHIELD_THEORY.md, Section D
```

[⬆ Back to top](#top)

---

<a id="f-rag-general"></a>
## F. How RAG (in General) Uses FAISS

This section explains the ROLE FAISS plays in ANY RAG system, not
just this project — so you understand the general pattern before
seeing our specific implementation.

```
                     GENERIC RAG PIPELINE
                     =====================

  Knowledge Base           User Question          Answer
  (millions of docs)            │                    ▲
       │                        │                    │
       ▼                        ▼                    │
  ┌───────────┐          ┌─────────────┐       ┌─────────────┐
  │  Embed    │          │   Embed     │       │     LLM     │
  │  ALL docs │          │  the query  │       │  generates  │
  │  (once)   │          │  (each time)│       │  the answer │
  └───────────┘          └─────────────┘       └─────────────┘
       │                        │                    ▲
       ▼                        ▼                    │
  ┌─────────────────────────────────────┐            │
  │            FAISS INDEX              │            │
  │  Stores all doc vectors, finds the  │────────────┘
  │  TOP-K most similar to the query    │
  └─────────────────────────────────────┘
```

**Why FAISS specifically, and not just a simple loop comparing
every document one by one in plain Python?**

```
A simple Python loop over 1 million documents, computing inner
product by hand for each one, would be SLOW — Python itself has
overhead for every single operation.

FAISS is written in C++ (a much faster, lower-level programming
language) and is specifically OPTIMISED for exactly this kind of
massive, repetitive numerical comparison. It can also use special
CPU/GPU instructions that do many calculations simultaneously
instead of one at a time.

Result: FAISS can search millions of vectors in milliseconds,
where a naive Python loop might take many seconds or even minutes
for the same task.
```

[⬆ Back to top](#top)

---

<a id="g-ragshield-specific"></a>
## G. How RAG-Shield Specifically Uses FAISS

```
┌────────────────────────────────────────────────────────────┐
│  WHERE FAISS SITS IN THE RAG-SHIELD PIPELINE               │
├────────────────────────────────────────────────────────────┤
│                                                            │
│   Documents added to KB                                    │
│         │                                                  │
│         ▼                                                  │
│   sentence-transformers embeds them (768-dim vectors)      │
│         │                                                  │
│         ▼                                                  │
│   ★ FAISS (IndexFlatIP) stores + indexes them ★            │
│         │                                                  │
│         ▼                                                  │
│   User asks a question                                     │
│         │                                                  │
│         ▼                                                  │
│   sentence-transformers embeds the QUESTION                │
│         │                                                  │
│         ▼                                                  │
│   ★ FAISS.search() finds top-5 most similar docs ★         │
│         │                                                  │
│         ▼                                                  │
│   RING 1 — Ingest Guard screens those 5 docs               │
│         │                                                  │
│         ▼                                                  │
│   RING 2 — Retrieval Scorer re-ranks by trust              │
│         │                                                  │
│         ▼                                                  │
│   RING 3 — Cross-LLM Consensus generates final answer      │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Critical fact tying this back to Numericals/Theory:** FAISS's
similarity score becomes `ret_score` inside Ring 2's trust formula
(see [RAGSHIELD_NUMERICALS.md, Section E.3](RAGSHIELD_NUMERICALS.md#e-ring2-math)):

```
trust = 0.45×prov + 0.35×cons + 0.20×ret_score
                                      ^^^^^^^^^
                                      this number
                                      comes directly
                                      from FAISS's
                                      inner-product
                                      search
```

**Why `ret_score` is weighted LOWEST (0.20) in that formula:**
because poison documents are SPECIFICALLY crafted to score high on
FAISS similarity (the "S" component of P=S+I — see
[RAGSHIELD_THEORY.md, Section B](RAGSHIELD_THEORY.md#b-attack)).
Trusting FAISS's number heavily would hand the attacker exactly
what they optimised for, so Ring 2 deliberately discounts it.

[⬆ Back to top](#top)

---

<a id="h-flat-vs-ivf"></a>
## H. IndexFlatIP vs IndexIVFFlat — Side by Side

```
┌───────────────────┬───────────────────────┬───────────────────────┐
│                   │ IndexFlatIP           │ IndexIVFFlat          │
│                   │ (current, small scale)│ (planned, 2M+ scale)  │
├───────────────────┼───────────────────────┼───────────────────────┤
│ Search style      │ Exact — checks EVERY  │ Approximate — checks  │
│                   │ vector, no shortcuts  │ only nearby "bins"    │
├───────────────────┼───────────────────────┼───────────────────────┤
│ Setup complexity  │ Trivial — just add()  │ Needs a "training"    │
│                   │ vectors and search    │ step first (see       │
│                   │                       │RAGSHIELD_NUMERICALS   │
│                   │                       │.md Section H)         │
├───────────────────┼───────────────────────┼───────────────────────┤
│ Search speed at   │ Instant               │ Instant               │
│ 5,000 docs        │                       │                       │
├───────────────────┼───────────────────────┼───────────────────────┤
│ Search speed at   │ Noticeably slower —   │ Still fast, if nlist/ │
│ 2.6 million docs  │ 2.6M comparisons per  │ nprobe are tuned wel  │
│                   │ query                 │                       │
├───────────────────┼───────────────────────┼───────────────────────┤
│ Memory at 2.6M    │ ~8GB just for vectors │ Similar memory, plus  │
│ docs              │                       │ small overhead for    │
│                   │                       │ bin structure         │
├───────────────────┼───────────────────────┼───────────────────────┤
│ Accuracy          │ 100% exact — always   │Slightly approximate—  │
│                   │ finds the TRUE top-K  │ tiny chance of missing│
│                   │                       │ a true top-K match    │
│                   │                       │ (tunable via nprobe)  │
└───────────────────┴───────────────────────┴───────────────────────┘
```

**The simplest possible summary:** IndexFlatIP is honest and exact
but doesn't scale forever. IndexIVFFlat sorts things into labelled
bins first so it only has to check a handful of bins instead of
every single vector — trading a tiny, controllable bit of accuracy
for a massive speed gain at large scale. Full detail on the
IndexIVFFlat side is in
[RAGSHIELD_NUMERICALS.md, Section H](RAGSHIELD_NUMERICALS.md#h-scaling-math)
and [RAGSHIELD_PRACTICE.md, Section E](RAGSHIELD_PRACTICE.md#e-scaling-steps).

[⬆ Back to top](#top)

---

<a id="i-code-walkthrough"></a>
## I. Full Code Walkthrough From Our Repo

**File:** `ragshield_core/retriever.py`

```python
# ── BUILDING the index (happens once, when the KB is created) ──

self._faiss = faiss.IndexFlatIP(emb.shape[1])
```
> Creates a new, empty IndexFlatIP. `emb.shape[1]` grabs the SECOND
> number from the embeddings' shape (recall `.shape` gives you
> `(number_of_docs, dimension)` — so `[1]` picks out just the
> dimension, which is 768). This tells FAISS "expect vectors with
> exactly 768 numbers each."

```python
self._faiss.add(emb.astype(np.float32))
```
> `emb.astype(np.float32)` converts all the numbers into a specific
> storage format (32-bit floating point) that FAISS is built to
> work with efficiently — similar to making sure everyone uses the
> same units (metres, not a mix of metres and feet) before
> comparing measurements. `.add(...)` then actually stores all
> these vectors inside the index.

```python
# ── SEARCHING the index (happens every time a query comes in) ──

scores, idx = self._faiss.search(qv, k)
```
> `qv` is the query vector (the user's question, already turned
> into 768 numbers by the same embedding model). `k` is how many
> results you want back (5, in our project). `.search(...)` runs
> the inner-product comparison against every stored vector (because
> this is IndexFlatIP — exhaustive, no shortcuts) and returns TWO
> things at once:
> - `scores` — the similarity numbers for the best matches
> - `idx` — WHICH documents those scores belong to (their index
>   positions, so you can look up the actual text)

**Where `normalize_embeddings=True` comes in (from
`ragshield_core/retriever.py`, using `sentence-transformers`):**

```python
doc_embeddings = model.encode(
    all_document_texts,
    normalize_embeddings=True,   # <- shrinks every vector to length 1
    batch_size=32,
)
```
> This is the step that makes IndexFlatIP's inner product
> mathematically EQUIVALENT to cosine similarity (see Section D.4
> above). Without this, longer documents might unfairly score
> higher purely because their vector happens to be longer, not
> because their MEANING is more similar.

[⬆ Back to top](#top)

---

<a id="j-mnemonics"></a>
## J. Mnemonics

```
FAISS = "Facebook AI Similarity Search" — fast calculator for
        comparing lists of numbers, NOT an AI model itself

FLAT  = "no shortcuts, check everything" (exact search)
IP    = "Inner Product" — multiply matching numbers, add them up

BIGGER IP = MORE SIMILAR (once vectors are normalised to length 1)

NORMALISE FIRST = "make every vector length 1 before comparing,
                   so only DIRECTION (meaning) matters, not length"

NLIST = bins created, NPROBE = bins checked
        "L for List (all of them exist), P for Probe (only
         probing a few of them per search)"

6% RULE OF THUMB = nprobe/nlist stays around 6% at every scale
                    in this project, because nprobe = nlist // 16

ret_score IS WEIGHTED LOWEST in Ring 2's trust formula because
poison is DESIGNED to maximise exactly this number
```

[⬆ Back to top](#top)

---

<a id="k-cheatsheet"></a>
## K. Cheatsheet

```
┌────────────────────────────────────────────────────────────────────┐
│ TERM                │ MEANING                                      │
├────────────────────────────────────────────────────────────────────┤
│ FAISS               │ Meta's fast vector-comparison library        │
│ vector              │ list of numbers describing a location        │
│ dimension (d)       │ how many numbers per vector (768 here)       │
│ Index               │ FAISS's organised storage of vectors         │
│ query vector        │ the temporary vector built from the question │
│ top-K               │ how many best matches to return (K=5 here)   │
│ IndexFlatIP         │ Exact search using inner product             │
│ Inner product (IP)  │ multiply matching numbers, then add them up  │
│ normalize_embeddings│ shrink vectors to length 1 before comparing  │
│ exhaustive search   │ checks EVERY vector, no shortcuts            │
│ approximate search  │ checks only nearby "bins" — faster           │
│ nlist               │ how many bins get created                    │
│ nprobe              │ how many bins get checked per search         │
│ ret_score           │ the similarity number FAISS returns, later   │
│                     │ used inside Ring 2's trust formula           │
│ IndexIVFFlat        │ approximate version, used for scaling to     │
│                     │ millions of documents (see Numericals/       │
│                     │ Practice for full detail)                    │
└────────────────────────────────────────────────────────────────────┘
```

[⬆ Back to top](#top)

---

<a id="l-exam-hacks"></a>
## L. Exam Hacks

```
TRAP: "Does FAISS understand what documents MEAN?"
SAFE: "No — FAISS only compares numbers. A separate model
       (sentence-transformers / all-mpnet-base-v2) turns text into
       meaningful numbers FIRST. FAISS's only job is fast, exact
       comparison of those numbers using inner product."

TRAP: "Why do we normalise embeddings before using FAISS?"
SAFE: "So that inner product only reflects DIRECTION (meaning)
       and not vector LENGTH. Once every vector has length 1,
       inner product becomes mathematically identical to cosine
       similarity."

TRAP: "Isn't a bigger inner product always better regardless of
       normalisation?"
SAFE: "Only if vectors are already normalised to the same length.
       Without normalisation, a longer vector could win purely by
       being longer, not by being more semantically similar —
       which is why normalize_embeddings=True matters."

TRAP: "Why does Ring 2 trust FAISS's score the LEAST of its three
       inputs?"
SAFE: "Because poison documents are specifically engineered to
       maximise FAISS similarity — that's the 'S' (search-trigger)
       component of P=S+I. Weighting it lowest (0.20) prevents the
       attacker's own optimisation target from being the strongest
       signal in our defense."

TRAP: "What's the difference between nlist and nprobe?"
SAFE: "nlist is how many bins get CREATED when the index is built.
       nprobe is how many of those bins actually get CHECKED per
       search. In this project nprobe = nlist // 16, so roughly
       6% of all bins get checked at any scale."

TRAP: "Why not just always use exhaustive search — isn't it more
       accurate?"
SAFE: "It IS more accurate — IndexFlatIP always finds the TRUE
       top-K. But it gets slower as the document count grows,
       since every query compares against every single vector. At
       2.6 million documents that's 2.6 million comparisons per
       query. Approximate search (IndexIVFFlat) trades a small,
       controllable amount of that accuracy for a massive speed
       gain, which is standard practice at this scale."
```

[⬆ Back to top](#top)

---

## 🔚 BOTTOM NAVIGATION — Jump to any file

**Related:** [RAGSHIELD_THEORY.md](RAGSHIELD_THEORY.md#top) (the story) → [RAGSHIELD_NUMERICALS.md](RAGSHIELD_NUMERICALS.md#top) (the math) → [RAGSHIELD_PRACTICE.md](RAGSHIELD_PRACTICE.md#top) (running it) → **This file:** RAGSHIELD_FAISS.md (the search engine)
 
[🏠 Repo Home](../../README.md) &nbsp;·&nbsp; [📂 Docs Index](../README.md) &nbsp;·&nbsp; [📘 Theory](RAGSHIELD_THEORY.md#top) &nbsp;·&nbsp; [🧮 Numericals](RAGSHIELD_NUMERICALS.md#top) &nbsp;·&nbsp; [🛠️ Practice](RAGSHIELD_PRACTICE.md#top) &nbsp;·&nbsp; [🔍 FAISS (you are here)](#top) &nbsp;·&nbsp; [📖 Architectures](RAG_ARCHITECTURES.md#top)

[⬆ Back to top](#top)
