<a id="top"></a>

# 📕 TECH GUIDE — LLM APIs (Claude, Mistral, Ollama/LLaMA)
### How We Talk to Three Different AI "Brains"
### Explained & Useful for the Author

---

## 🔝 Top Navigation

[⬅ Repo Home](../../README.md) · [Docs Index](../README.md) · [🏠 Study Index](RAGSHIELD_INDEX.md) · [🔍 FAISS](TECH_FAISS.md) · [📗 sentence-transformers](TECH_SENTENCE_TRANSFORMERS.md) · [📙 Streamlit](TECH_STREAMLIT.md)

---

## 📌 Table of Contents

- [A. The Story — What Is an "API"?](#a-story)
- [B. What Each of the Three AI Models Actually Is](#b-three-models)
- [C. Notation and Vocabulary](#c-notation)
- [D. Step-by-Step — How a Question Reaches an LLM and Comes Back](#d-step-by-step)
- [E. Why Three DIFFERENT Companies, Not the Same Model Three Times](#e-why-three)
- [F. Where This Lives in Our Code](#f-in-our-code)
- [G. Black-Box vs White-Box — Why It Matters](#g-black-white-box)
- [H. Mnemonics](#h-mnemonics)
- [I. Cheatsheet](#i-cheatsheet)
- [J. Exam Hacks](#j-exam-hacks)

---

<a id="a-story"></a>
## A. The Story — What Is an "API"?

Imagine a **restaurant with a kitchen you can't see into**. You don't
walk into the kitchen and cook yourself. Instead:

```
YOU (the customer)          THE WAITER               THE KITCHEN
"I'd like a burger,   --->  takes your order   --->  cooks it
 medium rare"                to the kitchen           (you never
                                                        see HOW)
                            brings back        <---
                            your food
```

**An API (Application Programming Interface) is exactly like that
waiter.** You send a request ("here's my question and some context
documents"), and you get back a response ("here's the answer"),
without ever seeing or controlling what happens INSIDE the AI model.

In our project, we send requests to THREE different "kitchens"
(Anthropic's Claude, Mistral AI's Mistral Small, and a locally-run
LLaMA model via Ollama), and each sends back an answer.

[⬆ Back to top](#top)

---

<a id="b-three-models"></a>
## B. What Each of the Three AI Models Actually Is

```
CLAUDE (by Anthropic, USA)
  A large language model trained by Anthropic, a company focused
  heavily on AI safety research. We access it over the internet —
  Anthropic runs the actual computer hardware; we just send
  requests and get answers back (this is called a "hosted" or
  "closed-source" model).

MISTRAL SMALL (by Mistral AI, France)
  A large language model trained by a French AI company. Also
  accessed over the internet in the same "hosted" way. Different
  company, different country, different training data and
  approach compared to Claude.

LLaMA 3.2 (by Meta, but run LOCALLY via Ollama)
  Meta (Facebook's parent company) trained this model and released
  its "weights" (the actual learned numbers inside the model)
  publicly — this is called "open-weight." Because the weights are
  public, we can download the ENTIRE model and run it directly on
  our own computer, with no internet connection needed once
  downloaded. "Ollama" is just a convenient tool that makes running
  these open-weight models on your own laptop easy.
```

**The one-sentence summary:** two AI "brains" live on someone else's
computer far away (Claude, Mistral) and we ask them questions over
the internet; one AI "brain" lives right here on our own laptop
(LLaMA via Ollama).

[⬆ Back to top](#top)

---

<a id="c-notation"></a>
## C. Notation and Vocabulary

```
API              = the "waiter" — a defined way to send a request
                   and receive a response from a service you don't
                   control internally

API key           = like a restaurant membership card — proves
                   you're allowed to place orders (and often, that
                   you're willing to pay for them)

endpoint          = the specific "address" you send your request to
                   (e.g. "https://api.anthropic.com" for Claude)

request / prompt  = the message you send TO the AI (your question
                   plus any context documents)

response          = the message you get BACK from the AI (the
                   generated answer)

temperature        = a setting that controls how "creative" vs
                   "predictable" the AI's answer is
                   (0.0 = always gives the most likely/consistent
                    answer; higher = more variety, less predictable)

max_tokens         = a limit on how LONG the AI's answer is allowed
                   to be (a "token" is roughly a word or word-piece)

local model        = an AI model running on YOUR OWN computer,
                   no internet needed once downloaded

hosted model       = an AI model running on SOMEONE ELSE's computer,
                   accessed over the internet

open-weight         = a model whose internal learned numbers are
                   publicly downloadable (like LLaMA)

closed-source       = a model whose internal numbers are kept
                   private by the company (like Claude, Mistral)
```

[⬆ Back to top](#top)

---

<a id="d-step-by-step"></a>
## D. Step-by-Step — How a Question Reaches an LLM and Comes Back

```
STEP 1 — RAG-Shield has already retrieved and filtered documents
    (Ring 1 and Ring 2 have already run — see Theory/Numericals)

STEP 2 — Build the prompt (the actual message to send)
    prompt = f"Answer using ONLY the context. One short sentence.

    Context:
    {clean_documents}

    Question: {user_question}

    Answer:"

STEP 3 — Send the SAME prompt to all three LLMs (this is Ring 3)
    answer_1 = ask_claude(prompt)
    answer_2 = ask_mistral(prompt)
    answer_3 = ask_llama(prompt)

STEP 4 — Each LLM independently "thinks" and responds
    (we don't see HOW they think — this is the "black box" idea,
     see Section G below)

STEP 5 — Compare the three answers (Ring 3's voting math)
    See Numericals Section F for the exact agreement-fraction math

STEP 6 — If enough agree, accept the answer; otherwise, retry once
```

[⬆ Back to top](#top)

---

<a id="e-why-three"></a>
## E. Why Three DIFFERENT Companies, Not the Same Model Three Times

Imagine asking the SAME person the same trick question three times
in a row. If they were fooled the first time, they'll probably be
fooled the SAME WAY all three times — asking again doesn't help.

```
Asking Claude 3 times:
  Claude answer 1: (fooled by poison)
  Claude answer 2: (fooled the SAME way — same training, same
                    weaknesses)
  Claude answer 3: (fooled the SAME way again)
  → "voting" among 3 identical brains proves NOTHING new

Asking Claude, Mistral, AND LLaMA (3 DIFFERENT companies):
  Claude: trained by Anthropic, one set of safety techniques
  Mistral: trained by a French company, different data/approach
  LLaMA: trained by Meta, open-weight, different training entirely

  A cleverly-worded poison document that fools Claude's specific
  training might NOT fool Mistral's different training, and vice
  versa. Genuine DIVERSITY of "brains" means genuine diversity of
  potential mistakes — which is exactly what makes a majority vote
  meaningful.
```

This directly uses Assumption A3 from our threat model
([see full threat model](RAGSHIELD_THEORY.md#c-fix)): heterogeneous LLMs don't share identical
failure modes against the same poison document.

[⬆ Back to top](#top)

---

<a id="f-in-our-code"></a>
## F. Where This Lives in Our Code

**File:** `ragshield_core/llm_backends.py`

```python
# Claude — hosted, Anthropic's own API
from anthropic import Anthropic
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=64,
    temperature=0.0,             # deterministic — same input,
                                  # same output, every time
    messages=[{"role": "user", "content": prompt}]
)

# Mistral — hosted, Mistral AI's own API
from mistralai import Mistral
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
response = client.chat.complete(
    model="mistral-small-latest",
    max_tokens=64,
    temperature=0.0,
    messages=[{"role": "user", "content": prompt}]
)

# LLaMA via Ollama — local, running on YOUR computer
from openai import OpenAI     # Ollama copies OpenAI's request format
client = OpenAI(
    base_url="http://localhost:11434/v1",   # "localhost" = this
                                              # computer, not the internet
    api_key="ollama",                         # dummy value — Ollama
                                              # doesn't check it
)
response = client.chat.completions.create(
    model="llama3.2:3b",
    max_tokens=64,
    messages=[{"role": "user", "content": prompt}]
)
```

**Why `temperature=0.0` everywhere?** Because Ring 3's voting only
makes sense if each model gives a CONSISTENT answer for the same
input. High temperature would introduce randomness, making the
SAME model potentially disagree with ITSELF across runs — that
would corrupt our measurement of genuine cross-model agreement.

[⬆ Back to top](#top)

---

<a id="g-black-white-box"></a>
## G. Black-Box vs White-Box — Why It Matters

```
BLACK-BOX access = you only see the INPUT you send and the OUTPUT
                    you get back. You cannot look INSIDE the model
                    while it's "thinking."

WHITE-BOX access  = you CAN look inside — for example, seeing
                    which words the model paid the most "attention"
                    to while forming its answer (this requires
                    running the model yourself, with full access
                    to its internals)
```

**RAG-Shield's Ring 3 is entirely black-box.** We only ever send a
prompt and read back a text answer — we never need to peek inside
any of the three models. This matters enormously in practice:

```
Claude and Mistral are CLOSED-SOURCE, hosted models — there is NO
WAY to get white-box access to them even if you wanted to. Companies
do not expose their models' internal "attention weights" through
their public APIs.

This means: any defense technique that REQUIRES white-box access
(like some competing research we compared against — see Theory
Section G, "Stealth Lens") literally CANNOT run against Claude or
Mistral's real APIs. It can only work with open-weight models you
run yourself.

RAG-Shield's black-box design means it works with ANY LLM — hosted
or local, open or closed — without needing special access most
companies simply don't provide.
```

[⬆ Back to top](#top)

---

<a id="h-mnemonics"></a>
## H. Mnemonics

```
API = "the waiter" — you order, kitchen cooks, you never see how

HOSTED vs LOCAL:
  hosted = "someone else's computer, over the internet"
  local  = "your own computer, no internet needed"

BLACK-BOX = "input and output only, no peeking inside"
WHITE-BOX = "can see the model's internal workings"

TEMPERATURE 0.0 = "always give me the same, most confident answer"
                  (needed so Ring 3's voting is meaningful)

THREE DIFFERENT BRAINS > ONE BRAIN ASKED THREE TIMES
  (this one sentence is the entire justification for Ring 3's design)
```

[⬆ Back to top](#top)

---

<a id="i-cheatsheet"></a>
## I. Cheatsheet

```
┌──────────────────────────────────────────────────────────────┐
│ MODEL         │ COMPANY   │ HOSTED OR LOCAL │ OPEN OR CLOSED │
├──────────────────────────────────────────────────────────────┤
│ Claude Haiku  │ Anthropic │ Hosted          │ Closed-source  │
│ Mistral Small │Mistral AI │ Hosted          │ Closed-source  │
│ LLaMA 3.2     │ Meta      │ Local (Ollama)  │ Open-weight    │
└──────────────────────────────────────────────────────────────┘

KEY SETTINGS USED EVERYWHERE:
  temperature = 0.0    → consistent, repeatable answers
  max_tokens  = 64      → short answers, faster + cheaper
```

[⬆ Back to top](#top)

---

<a id="j-exam-hacks"></a>
## J. Exam Hacks

```
TRAP: "Why not just use one really powerful LLM instead of three?"
SAFE: "Defense-in-depth (see Theory Section C) — a single model,
       however powerful, is a single point of failure. Three
       DIFFERENT companies' models fail differently, so genuine
       majority agreement is a much stronger signal than one
       model's confidence alone."

TRAP: "Is Ollama an AI model itself?"
SAFE: "No — Ollama is a TOOL that makes it easy to download and run
       OTHER companies' open-weight models (like Meta's LLaMA) on
       your own computer. It's similar in spirit to how Streamlit
       isn't itself an AI model but a tool for building AI-powered
       apps."

TRAP: "Why does temperature=0.0 matter so much for THIS project
       specifically?"
SAFE: "Ring 3's entire logic depends on comparing multiple models'
       answers to the SAME prompt. If any model gave a different,
       random answer each time (high temperature), we couldn't
       reliably measure whether models genuinely agree or just
       happened to align by chance on one particular run."

TRAP: "Could RAG-Shield work with a defense technique that needs
       white-box access, like inspecting attention weights?"
SAFE: "Not with Claude or Mistral's real hosted APIs — those
       companies don't expose internal model internals through
       their public APIs. This is exactly why RAG-Shield is
       designed to be fully black-box: it must work with the kind
       of access real production systems actually have."
```

[⬆ Back to top](#top)

---

## 🔚 Bottom Navigation

[⬅ Repo Home](../../README.md) · [Docs Index](../README.md) · [🏠 Study Index](RAGSHIELD_INDEX.md) · [🔍 FAISS](TECH_FAISS.md) · [📗 sentence-transformers](TECH_SENTENCE_TRANSFORMERS.md) · [📙 Streamlit](TECH_STREAMLIT.md)

[⬆ Back to top](#top)
