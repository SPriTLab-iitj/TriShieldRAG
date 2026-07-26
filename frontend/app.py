# """
# RAG-Shield interactive demo — main entry.
# Run:  streamlit run frontend/app.py
# """
# import sys, os
# from pathlib import Path
# # make the project root importable (so `import ragshield_core` works)
# ROOT = Path(__file__).resolve().parent.parent
# sys.path.insert(0, str(ROOT))

# import streamlit as st
# from ragshield_core import config

# st.set_page_config(page_title="RAG-Shield|3_Rings|Group_6", page_icon="🛡️", layout="wide")

# # ---- shared styling ----
# st.markdown("""
# <style>
#   .stApp { background: #0E1726; }
#   h1, h2, h3 { color: #E8EDF7; font-family: Georgia, serif; }
#   .big { font-size: 2.4rem; font-weight: 800; color:#38BDF8; }
#   .tag { display:inline-block; padding:2px 10px; border-radius:8px;
#          background:#243352; color:#94A3B8; font-size:0.8rem; margin-right:6px;}
#   .ok   { color:#34D399; font-weight:700; }
#   .bad  { color:#F87171; font-weight:700; }
#   .warn { color:#FBBF24; font-weight:700; }
# </style>
# """, unsafe_allow_html=True)

# st.markdown('<div class="big">🛡️ RAG-Shield</div>', unsafe_allow_html=True)
# st.markdown("**Multi-Layer Defense Against Knowledge-Base Poisoning** · "
#             "PoisonedRAG (USENIX Security 2025) reproduction + our 3-ring defense")

# mode = "DEMO (TF-IDF + mock LLMs, no keys needed)" if config.demo_mode() \
#        else "LIVE (FAISS + real LLM backends)"
# st.markdown(f'<span class="tag">Mode: {mode}</span>'
#             f'<span class="tag">top-K = {config.TOP_K}</span>'
#             f'<span class="tag">Group 6 · IIT Jodhpur</span>', unsafe_allow_html=True)

# st.divider()
# st.subheader("What you can do here")
# st.markdown("""
# Use the **pages in the left sidebar**:

# 1. **Attack Demo** — watch 5 poison docs hijack the answer.
# 2. **Defense Demo** — turn on RAG-Shield and watch each ring fire.
# 3. **Side-by-Side** — same question, poisoned vs shielded, together.
# 4. **Forensic Explorer** — inspect exactly which docs each ring flagged and why.
# 5. **Results Dashboard** — attack-success-rate chart across configurations.
# """)

# st.info("Demo mode runs instantly with no API keys. To use real Claude + LLaMA, "
#         "set `DEMO_MODE=0` in your environment and fill `.env`.", icon="💡")

# st.divider()

# # ---------------------------------------------------------------------------
# # Team credits — Group 6
# # ---------------------------------------------------------------------------
# import base64
# TEAM = [
#     ("Jeenal Chaudhary",  "G25AIT2027", "RAG fundamentals & pipeline · Intro"),
#     ("Rohit Patel",       "G25AIT2089", "Architecture · Implementation · Demo"),
#     ("Amit Singh",        "G25AIT2007", "Threat model & problem framing"),
#     ("Sharvan Vittala",   "G25AIT2099", "Attack mechanics · Ring 1 design"),
#     ("Sudeb Ghosh",       "G25AIT2113", "Attack deep-dive · Adversarial tests"),
#     ("Kosuru Yuvaraj",    "G25AIT2054", "Gap analysis · Ring 2 design"),
#     ("Pujan Chakraborty", "G25AIT2076", "RAG-Shield design · Evaluation"),
#     ("Vishnu Priya",      "G25AIT2128", "Frontend/UI · Results & report"),
#     ("Disha Singhania",   "G25AIT2031", "Environment setup · Testing · Docs"),
# ]
# _GRADS = ["#6366f1,#8b5cf6", "#ec4899,#f43f5e", "#14b8a6,#0ea5e9",
#           "#f59e0b,#ef4444", "#22c55e,#16a34a", "#a855f7,#6366f1",
#           "#0ea5e9,#3b82f6", "#f43f5e,#ec4899", "#10b981,#14b8a6"]
# _PHOTO_DIR = ROOT / "frontend" / "assets" / "team"

# def _initials(name):
#     p = name.split()
#     return (p[0][0] + p[-1][0]).upper() if len(p) >= 2 else name[:2].upper()

# def _avatar(name, sid, grad):
#     for ext in ("png", "jpg", "jpeg", "webp"):
#         p = _PHOTO_DIR / f"{sid}.{ext}"
#         if p.exists():
#             b64 = base64.b64encode(p.read_bytes()).decode()
#             mime = "jpeg" if ext in ("jpg", "jpeg") else ext
#             return (f'<div style="width:64px;height:64px;margin:0 auto 10px;border-radius:50%;'
#                     f'background-image:url(data:image/{mime};base64,{b64});background-size:cover;'
#                     f'background-position:center;box-shadow:0 4px 14px rgba(0,0,0,.3);"></div>')
#     return (f'<div style="width:64px;height:64px;margin:0 auto 10px;border-radius:50%;'
#             f'background:linear-gradient(135deg,{grad});display:flex;align-items:center;'
#             f'justify-content:center;font-size:22px;font-weight:700;color:#fff;'
#             f'box-shadow:0 4px 14px rgba(0,0,0,.3);">{_initials(name)}</div>')

# st.subheader("Group 6 — The Team Behind RAG-Shield")
# st.caption("CSL6010 Cyber Security · M.Tech AI · IIT Jodhpur · Prof. Susil Kumar Mohanty")
# _cols = st.columns(3)
# for _i, (_n, _s, _r) in enumerate(TEAM):
#     with _cols[_i % 3]:
#         st.markdown(f'''
#         <div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);
#                     border-radius:14px;padding:16px;margin-bottom:14px;text-align:center;">
#           {_avatar(_n, _s, _GRADS[_i % len(_GRADS)])}
#           <div style="font-size:15px;font-weight:700;color:#E8EDF7;">{_n}</div>
#           <div style="font-size:11px;color:#94A3B8;font-family:monospace;margin:2px 0 6px;">{_s}</div>
#           <div style="font-size:12px;color:#CBD5E1;line-height:1.35;">{_r}</div>
#         </div>
#         ''', unsafe_allow_html=True)

# st.divider()
# st.caption("PoisonedRAG · RAG-Shield  |  Group 6 · CSL6010 Cyber Security · "
#            "Prof. Susil Kumar Mohanty · IIT Jodhpur")


"""
RAG-Shield interactive demo — main entry.
Run:  streamlit run frontend/app.py
"""
import sys, os
from pathlib import Path
# make the project root importable (so `import ragshield_core` works)
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
from ragshield_core import config

st.set_page_config(page_title="RAG-Shield|3_Rings|Group_6", page_icon="🛡️", layout="wide")

# ---- shared styling ----
st.markdown("""
<style>
  .stApp { background: #0E1726; }
  h1, h2, h3 { color: #E8EDF7; font-family: Georgia, serif; }
  .big { font-size: 2.4rem; font-weight: 800; color:#38BDF8; }
  .tag { display:inline-block; padding:2px 10px; border-radius:8px;
         background:#243352; color:#94A3B8; font-size:0.8rem; margin-right:6px;}
  .ok   { color:#34D399; font-weight:700; }
  .bad  { color:#F87171; font-weight:700; }
  .warn { color:#FBBF24; font-weight:700; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big">🛡️ RAG-Shield</div>', unsafe_allow_html=True)
st.markdown("**Multi-Layer Defense Against Knowledge-Base Poisoning** · "
            "PoisonedRAG (USENIX Security 2025) reproduction + our 3-ring defense")

if config.scale_mode():
    mode = "SCALE (FAISS + real LLM backends, YOUR large dataset)"
elif config.demo_mode():
    mode = "DEMO (TF-IDF + mock LLMs, no keys needed)"
else:
    mode = "LIVE (FAISS + real LLM backends)"
st.markdown(f'<span class="tag">Mode: {mode}</span>'
            f'<span class="tag">top-K = {config.TOP_K}</span>'
            f'<span class="tag">Group 6 · IIT Jodhpur</span>', unsafe_allow_html=True)

st.divider()
st.subheader("What you can do here")
st.markdown("""
Use the **pages in the left sidebar**:

1. **Attack Demo** — watch 5 poison docs hijack the answer.
2. **Defense Demo** — turn on RAG-Shield and watch each ring fire.
3. **Side-by-Side** — same question, poisoned vs shielded, together.
4. **Forensic Explorer** — inspect exactly which docs each ring flagged and why.
5. **Results Dashboard** — attack-success-rate chart across configurations.
""")

st.info("Demo mode runs instantly with no API keys. To use real Claude + LLaMA, "
        "set `DEMO_MODE=0` in your environment and fill `.env`.", icon="💡")

st.divider()

# ---------------------------------------------------------------------------
# Team credits — Group 6
# ---------------------------------------------------------------------------
import base64
TEAM = [
    ("Jeenal Chaudhary",  "G25AIT2027", "RAG fundamentals & pipeline · Intro"),
    ("Rohit Patel",       "G25AIT2089", "Architecture · Implementation · Demo"),
    ("Amit Singh",        "G25AIT2007", "Threat model & problem framing"),
    ("Sharvan Vittala",   "G25AIT2099", "Attack mechanics · Ring 1 design"),
    ("Sudeb Ghosh",       "G25AIT2113", "Attack deep-dive · Adversarial tests"),
    ("Kosuru Yuvaraj",    "G25AIT2054", "Gap analysis · Ring 2 design"),
    ("Pujan Chakraborty", "G25AIT2076", "RAG-Shield design · Evaluation"),
    ("Vishnu Priya",      "G25AIT2128", "Frontend/UI · Results & report"),
    ("Disha Singhania",   "G25AIT2031", "Environment setup · Testing · Docs"),
]
_GRADS = ["#6366f1,#8b5cf6", "#ec4899,#f43f5e", "#14b8a6,#0ea5e9",
          "#f59e0b,#ef4444", "#22c55e,#16a34a", "#a855f7,#6366f1",
          "#0ea5e9,#3b82f6", "#f43f5e,#ec4899", "#10b981,#14b8a6"]
_PHOTO_DIR = ROOT / "frontend" / "assets" / "team"

def _initials(name):
    p = name.split()
    return (p[0][0] + p[-1][0]).upper() if len(p) >= 2 else name[:2].upper()

def _avatar(name, sid, grad):
    for ext in ("png", "jpg", "jpeg", "webp"):
        p = _PHOTO_DIR / f"{sid}.{ext}"
        if p.exists():
            b64 = base64.b64encode(p.read_bytes()).decode()
            mime = "jpeg" if ext in ("jpg", "jpeg") else ext
            return (f'<div style="width:64px;height:64px;margin:0 auto 10px;border-radius:50%;'
                    f'background-image:url(data:image/{mime};base64,{b64});background-size:cover;'
                    f'background-position:center;box-shadow:0 4px 14px rgba(0,0,0,.3);"></div>')
    return (f'<div style="width:64px;height:64px;margin:0 auto 10px;border-radius:50%;'
            f'background:linear-gradient(135deg,{grad});display:flex;align-items:center;'
            f'justify-content:center;font-size:22px;font-weight:700;color:#fff;'
            f'box-shadow:0 4px 14px rgba(0,0,0,.3);">{_initials(name)}</div>')

st.subheader("Group 6 — The Team Behind RAG-Shield")
st.caption("CSL6010 Cyber Security · M.Tech AI · IIT Jodhpur · Prof. Susil Kumar Mohanty")
_cols = st.columns(3)
for _i, (_n, _s, _r) in enumerate(TEAM):
    with _cols[_i % 3]:
        st.markdown(f'''
        <div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);
                    border-radius:14px;padding:16px;margin-bottom:14px;text-align:center;">
          {_avatar(_n, _s, _GRADS[_i % len(_GRADS)])}
          <div style="font-size:15px;font-weight:700;color:#E8EDF7;">{_n}</div>
          <div style="font-size:11px;color:#94A3B8;font-family:monospace;margin:2px 0 6px;">{_s}</div>
          <div style="font-size:12px;color:#CBD5E1;line-height:1.35;">{_r}</div>
        </div>
        ''', unsafe_allow_html=True)

st.divider()
st.caption("PoisonedRAG · RAG-Shield  |  Group 6 · CSL6010 Cyber Security · "
           "Prof. Susil Kumar Mohanty · IIT Jodhpur")
