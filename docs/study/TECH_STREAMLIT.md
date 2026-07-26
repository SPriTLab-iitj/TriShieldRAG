<a id="top"></a>

# 📙 TECH GUIDE — Streamlit
### The Tool That Turns a Python Script Into a Website
### Explained & Useful for the Author

---

## 🔝 Top Navigation

[⬅ Repo Home](../../README.md) · [Docs Index](../README.md) · [🏠 Study Index](RAGSHIELD_INDEX.md) · [🔍 FAISS](TECH_FAISS.md) · [📗 sentence-transformers](TECH_SENTENCE_TRANSFORMERS.md) · [📕 LLM APIs ➡](TECH_LLM_APIS.md)

---

## 📌 Table of Contents

- [A. The Story — What Problem Does Streamlit Solve?](#a--story)
- [B. What Streamlit Actually Is](#b-what-is-streamlit)
- [C. Notation and Vocabulary](#c-notation)
- [D. Step-by-Step — How Our 5 Pages Work](#d-step-by-step)
- [E. The Caching Trick — Why Re-Running Is Instant](#e-caching)
- [F. Where Streamlit Lives in Our Code](#f-in-our-code)
- [G. Mnemonics](#g-mnemonics)
- [H. Cheatsheet](#h-cheatsheet)
- [I. Exam Hacks](#i-exam-hacks)

---

<a id="a--story"></a>
## A. The Story — What Problem Does Streamlit Solve?

Imagine you wrote a really smart Python program that can answer
questions. It works great when YOU run it and type in the terminal.
But your friend doesn't know how to use a terminal, and definitely
doesn't want to install Python just to try your program.

```
WITHOUT Streamlit:
  Your friend needs: Python installed, your code downloaded,
  knowledge of command-line typing, patience.

WITH Streamlit:
  Your friend needs: a web browser. That's it. They click buttons,
  see pretty boxes and charts, just like any normal website.
```

**Streamlit is a tool that turns your Python code into a clickable
website, without you needing to learn any web-design languages
(HTML, CSS, JavaScript) at all.** You just write normal Python, and
Streamlit handles turning it into buttons, dropdowns, and charts on
a webpage.

[⬆ Back to top](#top)

---

<a id="b-what-is-streamlit"></a>
## B. What Streamlit Actually Is

Streamlit is a Python LIBRARY (a collection of ready-made tools you
can import and use) specifically designed for building simple,
interactive data apps and demos QUICKLY — in hours, not weeks.

```
Normal web development:  HTML (structure) + CSS (styling) +
                          JavaScript (interactivity) + a backend
                          server language — many moving parts

Streamlit development:   just write Python. Streamlit converts your
                          Python function calls directly into
                          webpage elements.
```

**Example — this is genuinely ALL the code needed for a button:**

```python
import streamlit as st

if st.button("Run attack (no defense)"):
    st.write("Attack running!")
```

That's it. `st.button(...)` becomes a real clickable button on the
webpage. `st.write(...)` displays text. No HTML, no JavaScript.

[⬆ Back to top](#top)

---

<a id="c-notation"></a>
## C. Notation and Vocabulary

```
st                = the standard short name everyone uses for the
                    streamlit library (import streamlit as st)

widget            = any interactive element — button, dropdown,
                    text box, slider — that a user can click/type into

page              = one "screen" of the app; our project has 5:
                    Attack Demo, Defense Demo, Side by Side,
                    Forensic Explorer, Results Dashboard

session           = one user's ongoing visit to the app — Streamlit
                    remembers some things (like which page you're
                    on) for the DURATION of your visit

rerun             = every time you click ANYTHING in a Streamlit
                    app, the ENTIRE Python script re-runs from top
                    to bottom (this sounds wasteful, but Streamlit
                    is built to make this fast)

cache             = a "memory" that stores the RESULT of an
                    expensive calculation, so if you ask for the
                    same thing twice, Streamlit gives you the
                    saved answer instantly instead of recalculating
```

[⬆ Back to top](#top)

---

<a id="d-step-by-step"></a>
## D. Step-by-Step — How Our 5 Pages Work

```
STEP 1 — The user opens the app in their browser
    Streamlit runs frontend/app.py (or the main entry file),
    which shows a sidebar listing all 5 pages

STEP 2 — The user clicks a page name (e.g. "Attack Demo")
    Streamlit runs that page's specific Python file:
    frontend/pages/1_Attack_Demo.py — TOP TO BOTTOM, every time

STEP 3 — The page displays widgets
    st.selectbox(...) shows a dropdown of questions
    st.button(...) shows a clickable "Run attack" button

STEP 4 — The user clicks "Run attack"
    Streamlit RE-RUNS the entire 1_Attack_Demo.py file again,
    from the top — but THIS time, st.button(...) returns True
    (because it was just clicked), so the code inside the
    "if st.button(...):" block actually executes

STEP 5 — Results display
    The retrieved documents, LLM answer, and success/failure
    message all get shown using st.write(), st.markdown(), etc.
```

**The "rerun from the top every time" idea is the single most
important thing to understand about Streamlit** — and it's exactly
why caching (next section) matters so much.

[⬆ Back to top](#top)

---

<a id="e-caching"></a>
## E. The Caching Trick — Why Re-Running Is Instant

If EVERY click re-runs the whole script from scratch, wouldn't
clicking a button re-call the (slow, costly) LLM APIs every single
time, even for the same question you already asked?

**Without caching: YES, that would happen — slow and wasteful.**

**With caching: NO — Streamlit remembers past results.**

```python
@st.cache_data
def cached_answer(question, defense, true_answer, wrong_answer):
    # this expensive function calls Ring 1, Ring 2, Ring 3,
    # and the real LLM APIs
    return shield.answer(question, defense=defense, ...)
```

`@st.cache_data` is a **decorator** (a special marker placed above a
function) that tells Streamlit: "remember the OUTPUT of this
function for each unique combination of INPUTS. If it's ever called
again with the EXACT SAME inputs, skip running it again — just
return the saved answer instantly."

```
First time you click "Run" for the Tesla question:
    cached_answer("Who founded Tesla Motors?", True, ...)
    → NOT in cache yet → actually calls Claude/Mistral/LLaMA
    → takes 2-10 seconds → result gets SAVED in the cache

Second time (e.g. switching to Side-by-Side page, same question):
    cached_answer("Who founded Tesla Motors?", True, ...)
    → ALREADY in cache! → returns instantly, no API calls at all
```

This is exactly why our Results Dashboard and Side-by-Side pages
feel instant — they're reusing answers already computed (and
cached) by the Attack Demo / Defense Demo pages.

[⬆ Back to top](#top)

---

<a id="f-in-our-code"></a>
## F. Where Streamlit Lives in Our Code

```python
# frontend/pages/2_Defense_Demo.py

import streamlit as st

st.title("🛡️ Defense Demo — RAG-Shield turns the attack back")

question = st.selectbox("Pick a target question", all_questions)

if st.button("Run with RAG-Shield"):
    result = cached_answer(question, defense=True, ...)

    col1, col2, col3 = st.columns(3)   # 3 side-by-side boxes
    with col1:
        st.metric("Docs blocked at ingest", result["ring1_blocked"])
    with col2:
        st.metric("Low-trust docs dropped", result["ring2_dropped"])
    with col3:
        st.metric("Panel agreement", f"{result['ring3_agreement']}%")

    st.success(f"Final answer: {result['answer']}")
```

`st.columns(3)` is a layout tool — it splits the page into 3
side-by-side sections, which is exactly how our Ring 1 / Ring 2 /
Ring 3 boxes appear next to each other on screen.

`st.metric(...)` displays a big number with a label — used for
showing "5" (docs blocked), "0" (docs dropped), "100%" (agreement).

[⬆ Back to top](#top)

---

<a id="g-mnemonics"></a>
## G. Mnemonics

```
STREAMLIT = "Python code becomes a website, no web-design needed"

RERUN = every click re-runs the ENTIRE script top to bottom
        (this is the #1 thing to remember about how Streamlit works)

CACHE = "remember the answer so you don't redo the expensive work
         twice for the same question"

@st.cache_data = the magic word that turns ON this memory trick
```

[⬆ Back to top](#top)

---

<a id="h-cheatsheet"></a>
## H. Cheatsheet

```
┌──────────────────────────────────────────────────────────────┐
│ STREAMLIT FUNCTION   │  WHAT IT SHOWS ON THE PAGE            │
├──────────────────────────────────────────────────────────────┤
│ st.title(...)        │ big page heading                      │
│ st.selectbox(...)    │ a dropdown menu                       │
│ st.button(...)       │ a clickable button                    │
│ st.write(...) /      │ plain text or formatted markdown      │
│ st.markdown(...)     │                                       │
│ st.columns(3)        │splits page into 3 side-by-side boxes  │
│ st.metric(...)       │ a big number with a small label       │
│ st.success(...) /    │ a green / red highlighted message box │
│ st.error(...)        │                                       │
│ @st.cache_data       │ remembers past function results       │
│ @st.cache_resource   │ remembers a shared object (like the   │
│                      │ whole RAGShield system) across pages  │
└──────────────────────────────────────────────────────────────┘
```

[⬆ Back to top](#top)

---

<a id="i-exam-hacks"></a>
## I. Exam Hacks

```
TRAP: "Why does the WHOLE script re-run on every click? Isn't that
       wasteful?"
SAFE: "Streamlit's design trade-off: simplicity for the developer
       (no manual state management needed) at the cost of re-running
       code. Caching (@st.cache_data) solves the 'wasteful' part by
       skipping expensive re-computation for repeated inputs."

TRAP: "What's the difference between @st.cache_data and
       @st.cache_resource?"
SAFE: "cache_data is for return VALUES like our LLM answers —
       Streamlit checks if the inputs match something already
       computed. cache_resource is for SHARED OBJECTS like our
       whole RAGShield system object, which should be built once
       and reused across every page, not recreated per click."

TRAP: "Could this be built without Streamlit?"
SAFE: "Yes, with a full web stack (HTML/CSS/JavaScript/backend
       server) — but that would take far longer to build for a
       project whose main goal is demonstrating the DEFENSE LOGIC,
       not web development skill. Streamlit let us focus effort on
       the actual research contribution."
```

[⬆ Back to top](#top)

---

## 🔚 Bottom Navigation

[⬅ Repo Home](../../README.md) · [Docs Index](../README.md) · [🏠 Study Index](RAGSHIELD_INDEX.md) · [🔍 FAISS](TECH_FAISS.md) · [📗 sentence-transformers](TECH_SENTENCE_TRANSFORMERS.md) · [📕 LLM APIs ➡](TECH_LLM_APIS.md)

[⬆ Back to top](#top)
