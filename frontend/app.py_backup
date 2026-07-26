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

st.set_page_config(page_title="RAG-Shield", page_icon="🛡️", layout="wide")

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

mode = "DEMO (TF-IDF + mock LLMs, no keys needed)" if config.demo_mode() \
       else "LIVE (FAISS + real LLM backends)"
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
st.caption("PoisonedRAG · RAG-Shield  |  Group 6 · CSL6010 Cyber Security · "
           "Prof. Susil Kumar Mohanty · IIT Jodhpur")
