<a id="top"></a>

# 🎓 RAG-Shield MATH PRIMER
### For the Author — "I Know Nothing About Math" Starting Point
### Every concept taught from zero, then applied to My actual code

---

## 🔝 Top Navigation

[⬅ Repo Home](../../README.md) · [Docs Index](../README.md) · [🏠 Study Index](RAGSHIELD_INDEX.md) · [📘 Theory](RAGSHIELD_THEORY.md) · [🧮 Numericals](RAGSHIELD_NUMERICALS.md) · [🛠️ Practice](RAGSHIELD_PRACTICE.md)

---

> **Who this file is for:** You are the author of RAG-Shield. You built
> the system, but maybe nobody ever sat you down and explained WHY the
> math looks the way it does, or what each symbol technically means
> outside of "the code does this." This file assumes ZERO prior math
> background and builds up every concept, one brick at a time, until
> you understand not just WHAT the formulas say but WHY they're shaped
> that way — so you can defend every choice in a viva or a paper review.

---

## 📌 Table of Contents

- [Part 1 — The Absolute Basics (numbers, sets, functions)](#part1)
- [Part 2 — Vectors and "Meaning Space" (needed for Ring 1's OutlierDetector)](#part2)
- [Part 3 — Cosine Similarity Explained From Zero](#part3)
- [Part 4 — Probability-ish Thinking (needed for Ring 1's Perplexity)](#part4)
- [Part 5 — Weighted Averages (needed for Ring 2's Trust Score)](#part5)
- [Part 6 — Sets, Bags, and Overlap (needed for Ring 2's Consistency)](#part6)
- [Part 7 — Fractions and Thresholds (needed for Ring 3's Voting)](#part7)
- [Part 8 — Reading `min()` and `max()` Like a Human](#part8)
- [Part 9 — Every Formula in RAG-Shield, Now That You Know the Building Blocks](#part9)
- [Part 10 — Things You MUST Be Aware Of As the Author](#part10)
- [Mnemonics Master List](#mnemonics)
- [Cheatsheet](#cheatsheet)
- [Exam Hacks](#exam-hacks)

---

<a id="part1"></a>
## Part 1 — The Absolute Basics

### What is a "score between 0 and 1"?

Imagine a ruler that goes from 0 to 1, instead of 0 to 12 inches.

```
0.0 -------- 0.25 -------- 0.5 -------- 0.75 -------- 1.0
"totally      "a bit        "half        "quite       "totally
 innocent"     suspicious"   and half"    suspicious"  suspicious"
```

Every single score in RAG-Shield lives on this ruler. When you see
`p = 0.189`, read it as "18.9% suspicious" — not a percentage
technically, but that's the easiest way to feel it.

### What does `|X|` mean?

This means "the SIZE of X" — literally just "how many things are in X."

```
If X = ["apple", "banana", "apple"]
Then |X| = 3     (there are 3 items total, counting repeats)
```

### What is a "set" vs a "list"?

```
A LIST can have repeats:      ["cat", "dog", "cat"]     — 3 items
A SET removes repeats:         {"cat", "dog"}             — 2 items
```

In code: `unique(words)` turns a list into a set (removes duplicates).

### What is a "function"?

A function is a MACHINE. You put something IN, it gives something OUT.

```
   INPUT               MACHINE              OUTPUT
  "hello world"  --->  count_letters()  --->    10

f(x) = x + 1   means:  "put in x, get out x+1"
f(5) = 6       means:  "if x is 5, the answer is 6"
```

Every formula in this project (`p(t)`, `pa(t)`, `trust(d)`) is just a
machine: put in a document, get out a number between 0 and 1.

[⬆ Back to top](#top)

---

<a id="part2"></a>
## Part 2 — Vectors and "Meaning Space"

### What is a vector, in the simplest possible way?

A vector is just **a list of numbers that describes a location**.

```
Think of a treasure map. A location on the map needs 2 numbers:
   (3, 5)  = "3 steps right, 5 steps up"

That's a 2-DIMENSIONAL vector. It has 2 numbers.

Now imagine a map that needs 768 directions instead of just
"right" and "up" to describe a location. That's a 768-DIMENSIONAL
vector — still just a list of numbers, just a much longer list.

   v = [0.021, -0.443, 0.198, ..., 0.077]     <- 768 numbers total
```

### Why does RAG-Shield use 768-number vectors?

Because of **sentence embeddings**. A special AI model (called
`all-mpnet-base-v2` in our code) reads a sentence and converts its
MEANING into a location in this 768-dimensional space.

```
"Tesla was founded by Martin Eberhard"  --->  [0.02, -0.44, ...]
"Tesla Motors' founder was Eberhard"    --->  [0.03, -0.42, ...]
                                                (VERY CLOSE location —
                                                 similar meaning!)

"The Eiffel Tower is in Paris"          --->  [0.81, 0.12, ...]
                                                (FAR AWAY location —
                                                 different meaning!)
```

**Sentences with similar MEANING end up at similar LOCATIONS in this
768-number space.** That's the entire trick behind semantic search.
You're not matching exact words — you're matching LOCATIONS.

[⬆ Back to top](#top)

---

<a id="part3"></a>
## Part 3 — Cosine Similarity Explained From Zero

### The problem this solves

Given two locations (vectors), how do we measure "how similar" they
are? We can't just subtract them like normal numbers because they
have 768 numbers each.

### The kid version — two arrows from the same starting point

```
Imagine two arrows both starting from the same point (like a clock's
centre), pointing in different directions.

     ↑  (arrow A)
     |  ↗ (arrow B)
     | /
     |/________

If the two arrows point in EXACTLY the same direction → very similar
If the two arrows point in OPPOSITE directions → very different
If the two arrows are at a right angle (90°) → unrelated
```

**Cosine similarity measures the ANGLE between two arrows/vectors,**
not their length. It gives you a number:

```
cos = 1.0   →  pointing in EXACTLY the same direction (identical meaning)
cos = 0.5   →  somewhat similar direction
cos = 0.0   →  completely unrelated (90° angle)
cos = -1.0  →  pointing in OPPOSITE directions (rare in our use case)
```

### The formula (don't panic, we'll build it slowly)

```
cos(v, c) = v · c

This little dot "·" means "dot product" — here's what it actually does:

Step 1: multiply each matching pair of numbers together
Step 2: add up all those products

Example with tiny 3-number vectors (real ones have 768, same idea):
    v = [1, 2, 3]
    c = [4, 5, 6]

    v · c = (1×4) + (2×5) + (3×6)
          = 4 + 10 + 18
          = 32
```

**BUT** — this raw number (32) isn't between -1 and 1 yet. That's why
we first NORMALISE both vectors (make them length exactly 1) before
taking the dot product. Normalising means: divide every number in the
vector by the vector's own total length.

```
"Normalise" = "shrink or grow the arrow until its length is exactly 1,
               WITHOUT changing the direction it points"

Once BOTH vectors have length 1, their dot product automatically
comes out between -1 and 1 — and that IS the cosine similarity.
```

### Where this shows up in RAG-Shield

```python
# ragshield_core/ring1_ingest.py — OutlierDetector.score()

v = v_raw / np.linalg.norm(v_raw)   # normalise this doc's vector
cos = float(np.dot(v, self._centroid))   # dot product of two
                                          # ALREADY-normalised vectors
                                          # = cosine similarity
```

`np.linalg.norm(v_raw)` computes the vector's length (technically
called the "Euclidean norm" — just means "how long is this arrow").
Dividing by it shrinks the vector to length 1 without changing its
direction.

[⬆ Back to top](#top)

---

<a id="part4"></a>
## Part 4 — Probability-ish Thinking (for PerplexityDetector)

### What does "diversity" mean in plain English?

Imagine two short essays, both exactly 10 words long:

```
Essay A: "the cat sat on the mat and the dog ran"
         Unique words: the, cat, sat, on, mat, and, dog, ran  = 8 unique
         Total words: 10
         diversity = 8/10 = 0.8   (pretty varied)

Essay B: "tesla tesla tesla founded tesla tesla by tesla tesla tesla"
         Unique words: tesla, founded, by  = 3 unique
         Total words: 10
         diversity = 3/10 = 0.3   (very repetitive — SUSPICIOUS)
```

**Low diversity = high repetition = looks crafted/fake.** This is
the entire intuition behind `PerplexityDetector`.

### Why is it called "perplexity" if it's really about repetition?

True "perplexity" in AI research is a fancy measurement of how
SURPRISED a language model is by a piece of text (surprising text =
high perplexity = might be nonsense or unusual). Building a REAL
perplexity detector needs a whole extra AI model running in the
background, which is slow and expensive.

RAG-Shield uses a cheaper SHORTCUT that captures a similar idea:
crafted/fake text tends to be either overly repetitive OR
keyword-stuffed. Measuring word repetition (which is simple counting,
no extra AI model needed) approximates the same red flag much faster.
This is explicitly documented as a design trade-off in the code
comments.

[⬆ Back to top](#top)

---

<a id="part5"></a>
## Part 5 — Weighted Averages (for Ring 2's Trust Score)

### What is a normal average?

If you have 3 test scores — 80, 90, 100 — the average is:

```
average = (80 + 90 + 100) / 3 = 270/3 = 90
```

Every score counted EQUALLY (each got 1/3 of the "vote").

### What is a WEIGHTED average?

Now imagine your final grade depends on: 45% homework, 35% midterm,
20% final exam — NOT equal weights. If you scored 100 on homework,
80 on midterm, 60 on final:

```
final_grade = 0.45×100 + 0.35×80 + 0.20×60
            = 45 + 28 + 12
            = 85
```

**This is EXACTLY what Ring 2's trust formula does.** Instead of
homework/midterm/final, it's provenance/consistency/retrieval-score:

```python
trust = 0.45 * prov + 0.35 * cons + 0.20 * ret_score
```

The weights (0.45, 0.35, 0.20) always add up to 1.00 (that's what
makes it a proper weighted average) — this is worth double-checking
whenever you tune these numbers: **0.45 + 0.35 + 0.20 = 1.00 ✓**

### Why is retrieval_score weighted the LEAST (0.20)?

Because it's the number an ATTACKER specifically tries to maximise
(remember: poison documents are engineered to score high on
similarity to the question). If we trusted that number a lot, we'd
be trusting the attacker's own tool against us. So we deliberately
give it the smallest "vote" in the final decision.

[⬆ Back to top](#top)

---

<a id="part6"></a>
## Part 6 — Sets, Bags, and Overlap (for ConsistencyCheck)

### What is a "bag" (also called a multiset)?

A bag is like a set, but it REMEMBERS how many times each item
appears (a normal set throws that information away).

```
Text: "the cat sat on the mat"

As a SET:  {the, cat, sat, on, mat}          (5 unique words)
As a BAG:  {the: 2, cat: 1, sat: 1, on: 1, mat: 1}
           (remembers "the" appeared TWICE)
```

In code, this is exactly what Python's `Counter` does:

```python
from collections import Counter
bag = Counter(["the", "cat", "sat", "on", "the", "mat"])
# Counter({'the': 2, 'cat': 1, 'sat': 1, 'on': 1, 'mat': 1})
```

### What does "overlap between two bags" mean?

If Bag A has "eberhard" appearing 3 times, and Bag B (representing
everyone ELSE combined) has "eberhard" appearing 9 times total, how
much do they "agree" on this word?

```
overlap_contribution_for_this_word = min(A's count, B's count - A's count)
                                    = min(3, 9-3)
                                    = min(3, 6)
                                    = 3
```

We sum this `min(...)` calculation across EVERY word in the
document's bag, then divide by the document's total word count, to
get a single "how much does this document agree with the crowd"
score between 0 and 1. That's `ConsistencyCheck` in Ring 2.

[⬆ Back to top](#top)

---

<a id="part7"></a>
## Part 7 — Fractions and Thresholds (for Ring 3's Voting)

### What is a "fraction" here, in the simplest terms?

If 2 out of 3 friends agree on where to eat dinner, the fraction of
agreement is:

```
fraction = (number who agree) / (total number of friends)
         = 2 / 3
         = 0.667   (or "66.7%")
```

This is LITERALLY what Ring 3 computes:

```python
frac = agree_n / panel_size
```

### What is a "threshold" and why 0.66?

A threshold is just a LINE IN THE SAND: "if you're above this number,
you pass; if you're below, you don't."

```
Ring 3's threshold is 0.66 (two-thirds)

frac = 0.667  →  0.667 ≥ 0.66  →  PASS (2 of 3 agreed, that's enough)
frac = 0.333  →  0.333 ≥ 0.66  →  FAIL (only 1 of 3 agreed, not enough)
```

Why exactly 0.66 and not 0.5 (a simple majority) or 1.0 (unanimous)?
Because:
- 1.0 (unanimous) is too strict — one flaky LLM response would block
  every correct answer
- 0.5 (simple majority) is too loose — 2 could tie against 1 with no
  clear winner in a 3-way split scenario
- 0.66 (two-thirds) requires genuine agreement while tolerating ONE
  outlier response — the sweet spot for a 3-member panel

[⬆ Back to top](#top)

---

<a id="part8"></a>
## Part 8 — Reading `min()` and `max()` Like a Human

These two functions confuse people who haven't coded before, so
let's make them completely obvious.

```
min(a, b)  = "give me back whichever number is SMALLER"
max(a, b)  = "give me back whichever number is BIGGER"

min(3, 7) = 3        max(3, 7) = 7
min(0.9, 1.0) = 0.9   max(0.9, 1.0) = 1.0
```

### Why does RAG-Shield use `min(1.0, ...)` everywhere?

This is a **safety cap** — a way of saying "never let this score go
above 1.0, no matter how big the raw calculation gets."

```
min(1.0, 1.7)  = 1.0    <- capped! 1.7 is too big, clip it to 1.0
min(1.0, 0.4)  = 0.4    <- not capped, 0.4 was already fine
```

Think of it like a **volume knob that physically cannot go past 10**,
even if you try to turn it further.

### Why does RAG-Shield use `max(0, ...)` sometimes?

This is a **safety floor** — "never let this go BELOW 0."

```
max(0, -0.3) = 0      <- floored! -0.3 doesn't make sense here, clip to 0
max(0, 0.5)  = 0.5    <- not floored, 0.5 was already fine
```

**`min(1.0, max(0.0, X))` together = "clip X so it's always between
0 and 1, no matter what."** You'll see this pattern constantly.

[⬆ Back to top](#top)

---

<a id="part9"></a>
## Part 9 — Every Formula, Now That You Know the Building Blocks

You now have every piece of vocabulary needed. Here is EVERY formula
in RAG-Shield, explained using ONLY the concepts from Parts 1–8.

### Ring 1, Formula 1 — PerplexityDetector

```
p = min(1.0, 0.6×rep + 2.0×max(0, top−0.12))

Translation using what you now know:
  "rep" is 1 minus diversity (Part 4) — how repetitive the text is
  "top" is the share of the single most-repeated word (Part 4)
  The 0.6 and 2.0 are WEIGHTS (Part 5) — 2.0 matters more than 0.6
  max(0, top−0.12) is a SAFETY FLOOR (Part 8) — ignore small,
      normal amounts of repetition (up to 12%), only count the excess
  The outer min(1.0, ...) is a SAFETY CAP (Part 8) — never exceed 1.0
```

### Ring 1, Formula 2 — PatternDetector

```
pa = min(1.0, 0.4×signal1 + 0.5×signal2 + 0.3×signal3)

Translation:
  Three YES/NO signals (Part 1 — functions that output 0 or 1)
  Each signal contributes its own WEIGHT (Part 5) if triggered
  The min(1.0, ...) caps the total (Part 8)
```

### Ring 1, Formula 3 — OutlierDetector

```
o = min(1.0, max(0.0, 1.0 − cos(v, c)))

Translation:
  cos(v, c) is COSINE SIMILARITY (Part 3) between this doc's vector
      and the "average" vector (centroid) of the whole library
  1.0 − cos(...) flips similarity into DISTANCE
      (if cos=1.0 meaning "identical", distance = 0, meaning "not
       suspicious at all" — makes sense!)
  max(0.0, ...) and min(1.0, ...) are the usual safety floor/cap
```

### Ring 1, Combine Formula

```
combined = max(p, pa, 0.7×o + 0.3×max(p, pa))

Translation:
  Uses max() (Part 8) — "take whichever of these three signals
      is the LOUDEST alarm"
  The third option, 0.7×o + 0.3×max(p,pa), is a WEIGHTED AVERAGE
      (Part 5) that blends the outlier score with the best of the
      other two — this way outlier detection isn't totally ignored
      even when it doesn't win outright
```

### Ring 2 — Trust Score

```
trust = 0.45×prov + 0.35×cons + 0.20×ret_score

Translation: this is EXACTLY the weighted average from Part 5
(homework/midterm/final example), just renamed to
provenance/consistency/retrieval-score. Weights sum to 1.00.
```

### Ring 2 — Consistency Formula

```
cons_i = min(1.0, overlap_i / total_words_in_doc_i)

Translation: this uses the BAG OVERLAP idea from Part 6 — literally
counting how many words this document shares with "everyone else,"
then normalising into a 0–1 score with the usual safety cap.
```

### Ring 3 — Agreement Fraction

```
frac = agree_n / panel_size
agreed = (frac ≥ 0.66)

Translation: this is the FRACTION and THRESHOLD idea from Part 7 —
"what share of the group agrees, and is that share big enough?"
```

[⬆ Back to top](#top)

---

<a id="part10"></a>
## Part 10 — Things You MUST Be Aware Of As the Author

This section is your personal "don't get caught off guard" list —
things reviewers, professors, or curious readers WILL ask about.

### 10.1 — Every threshold is a DESIGN CHOICE, not a proven optimum

```
0.5  (Ring 1 block threshold)
0.35 (Ring 2 drop threshold)
0.66 (Ring 3 agreement threshold)

These were chosen empirically (by testing and observing what worked
well), NOT derived from a mathematical proof that they're the "best
possible" numbers. If asked "why 0.5 and not 0.6?" the honest answer
is: "we tuned it to balance catching poison against over-blocking
clean documents — a systematic threshold sensitivity study (trying
many values and plotting the trade-off) is good future work."
```

### 10.2 — "Approximate" is not a dirty word

When you scale to millions of documents (see Numericals Section H),
you'll switch from EXACT search (`IndexFlatIP`) to APPROXIMATE search
(`IndexIVFFlat`). Some people hear "approximate" and think it means
"less correct" in a bad way. In reality, approximate nearest-neighbour
search is INDUSTRY STANDARD at scale — Google, Meta, and every major
search engine use approximate methods because EXACT search becomes
physically too slow past a certain size. Know this so you never sound
apologetic about it — it's the right engineering choice, not a
compromise.

### 10.3 — Your defense is about REDUCING risk, not ELIMINATING it

Be careful never to claim "RAG-Shield makes RAG 100% safe." The
honest, defensible claim is: "RAG-Shield reduces attack success rate
from ~91% to 0–13% under our tested conditions." Security research
NEVER claims perfect safety — claiming that is an immediate red flag
to any reviewer and undermines your credibility. Always say
"reduces," "mitigates," "significantly lowers" — never "eliminates"
or "guarantees safety."

### 10.4 — You have NOT tested an adaptive attacker yet — say so proactively

An "adaptive attacker" is one who KNOWS your exact thresholds (0.5,
0.35, 0.66) and crafts poison specifically to slip just under them.
You have not tested this yet. This is completely fine AS LONG AS you
state it clearly as a limitation, rather than waiting for someone to
catch you not having done it. Reviewers respect honesty about
limitations far more than they respect an author claiming their
system has no weaknesses.

### 10.5 — Know the difference between "correlation" and "causation" language

When you say "poison documents have low diversity," you're describing
a PATTERN you observed, not a law of nature. Some real poison might
be well-written and NOT repetitive (fooling PerplexityDetector) —
that's exactly why you have 3 detectors in Ring 1 and 3 rings total,
not just one. Never imply your detectors are foolproof individually
— the whole POINT of the architecture is that no single piece needs
to be perfect, because of the layered design.

### 10.6 — The math is simple ON PURPOSE

Someone might ask "why not use a fancier machine learning model
instead of these hand-written formulas?" The honest answer: simple,
interpretable formulas mean you can EXPLAIN every decision (which
matters hugely in security — you want to know WHY something was
blocked, not just THAT it was blocked). A black-box ML classifier
might perform similarly but you'd lose this auditability. This is a
deliberate design trade-off favouring transparency, and it's a
STRENGTH to mention, not a weakness to hide.

### 10.7 — Always be ready to say what "black-box" and "white-box" mean

```
BLACK-BOX = you only see INPUT and OUTPUT of the AI model
            (you type a question, you get an answer — that's it)
WHITE-BOX = you can see INSIDE the AI model
            (you can inspect its internal "attention weights," etc.)

RAG-Shield is black-box. This is a STRENGTH because it means
RAG-Shield works with Claude, GPT-4, Mistral — ANY commercial AI —
without needing special access that most companies don't provide.
```

[⬆ Back to top](#top)

---

<a id="mnemonics"></a>
## Mnemonics Master List

```
SCORE RULER     → 0 = innocent, 1 = guilty. Every score lives here.

VECTOR = ARROW  → a vector is just an arrow pointing somewhere;
                  cosine similarity = "how similar are two arrows'
                  DIRECTIONS" (ignore their length)

WEIGHTED AVG    → "homework/midterm/final" — not all inputs count
                  equally; the weights must add up to 1.00

BAG NOT SET     → a bag remembers COUNTS, a set only remembers
                  WHO'S THERE (no counts)

min-CAP,        → min(1.0, X) = "never go above the ceiling"
max-FLOOR         max(0.0, X) = "never go below the floor"

FRACTION VOTE   → agree_n / panel_size = "what share agreed?"
                  compare against the THRESHOLD line-in-the-sand

APPROXIMATE ≠   → approximate search at scale is industry standard,
BAD               not a lesser compromise
```

[⬆ Back to top](#top)

---

<a id="cheatsheet"></a>
## Cheatsheet

```
┌─────────────────────────────────────────────────────────────────┐
│ CONCEPT              │ PLAIN MEANING          │ USED IN         │
├─────────────────────────────────────────────────────────────────┤
│ Vector               │ list of numbers =      │ OutlierDetector │
│                      │ a location             │                 │
├─────────────────────────────────────────────────────────────────┤
│ Cosine similarity    │ angle between two      │ OutlierDetector │
│                      │ arrows (0 to 1)        │                 │
├─────────────────────────────────────────────────────────────────┤
│ Diversity/repetition │ how varied the words   │ Perplexity      │
│                      │ in a text are          │ Detector        │
├─────────────────────────────────────────────────────────────────┤
│ Weighted average     │ some inputs count      │ Trust formula   │
│                      │ more than others       │ (Ring 2)        │
├─────────────────────────────────────────────────────────────────┤
│ Bag / Counter        │ counts of each word,   │ Consistency     │
│                      │ not just which exist   │ Check (Ring 2)  │
├─────────────────────────────────────────────────────────────────┤
│ Fraction + threshold │ what share agreed,     │ Ring 3 voting   │
│                      │ is it enough?          │                 │
├─────────────────────────────────────────────────────────────────┤
│ min() / max()        │ safety cap / floor     │ EVERYWHERE      │
└─────────────────────────────────────────────────────────────────┘
```

[⬆ Back to top](#top)

---

<a id="exam-hacks"></a>
## Exam Hacks

```
TRAP: "Explain cosine similarity in one sentence."
SAFE: "It measures the angle between two vectors, ignoring their
       length — 1.0 means pointing the exact same direction
       (identical meaning), 0.0 means unrelated."

TRAP: "Why do the weights in Ring 2's trust formula add up to 1.00?"
SAFE: "Because it's a weighted average — the weights represent
       proportions of trust that must sum to 100% (1.00) by
       definition, the same way percentages in a pie chart add to
       100%."

TRAP: "What's the difference between a set and a bag/Counter?"
SAFE: "A set only knows WHO's present, not how many times. A bag
       (Counter in Python) remembers the count of each item — needed
       for ConsistencyCheck because we care HOW MUCH a word is
       repeated across documents, not just whether it appears."

TRAP: "Is your defense mathematically proven to stop all attacks?"
SAFE: "No — we have formal guarantees for specific properties, like
       Ring 2 never dropping a correctly-labelled clean document
       (a proven guarantee), but we do not claim to have eliminated
       all possible attacks. We reduce attack success rate
       empirically; we have not yet tested an adaptive adversary
       who knows our exact thresholds."

TRAP: "Why not just use a neural network to detect poison instead
       of hand-written formulas?"
SAFE: "Interpretability. Every RAG-Shield decision can be traced
       back to an exact number and an exact reason — critical for
       security auditing. A black-box ML classifier might perform
       similarly but sacrifices this transparency."
```

[⬆ Back to top](#top)

---

## 🔚 Bottom Navigation

[⬅ Repo Home](../../README.md) · [Docs Index](../README.md) · [🏠 Study Index](RAGSHIELD_INDEX.md) · [📘 Theory ➡](RAGSHIELD_THEORY.md) · [🧮 Numericals ➡](RAGSHIELD_NUMERICALS.md) · [🛠️ Practice ➡](RAGSHIELD_PRACTICE.md)

[⬆ Back to top](#top)
