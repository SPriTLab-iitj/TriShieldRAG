import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "components"))
from _shared import get_shield, get_targets
import streamlit as st

st.set_page_config(page_title="Forensic Explorer", page_icon="🔬", layout="wide")
st.title("🔬 Forensic Explorer — why each doc was flagged")

shield = get_shield(poisoned=True)
targets = get_targets()
choice = st.selectbox("Pick a target question", [t["question"] for t in targets])
t = next(x for x in targets if x["question"] == choice)
cands = [t["true_answer"], t["wrong_answer"]]

tr = shield.trace(choice, defense=True, candidates=cands)

st.markdown("### Retrieved documents and ring verdicts")
for d in tr["retrieved"]:
    src = d.get("source", "clean")
    icon = "🔴" if src == "POISONED" else "🟢"
    with st.expander(f"{icon} {d.get('title','')[:60]}  ·  score={d.get('score',0):.3f}"):
        st.write(d.get("text", "")[:400])
        v = shield.ingest.inspect(d, shield._questions)
        st.json({"ring1_ingest": v})

st.divider()
st.markdown("### Ring 1 — blocked at ingest")
for d in tr.get("ring1_blocked", []):
    st.caption(f"🔴 {d.get('title','')[:50]} — {d.get('_ring1')}")

st.markdown("### Ring 2 — trust re-ranking")
for d in tr.get("ring2_kept", []):
    st.caption(f"kept trust={d.get('trust')} — {d.get('_ring2')}")
for d in tr.get("ring2_dropped", []):
    st.caption(f"DROPPED trust={d.get('trust')} — {d.get('title','')[:40]}")

st.markdown("### Ring 3 — cross-LLM panel")
st.json(tr.get("ring3", {}))
