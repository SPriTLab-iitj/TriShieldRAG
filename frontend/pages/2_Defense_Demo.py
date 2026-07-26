import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "components"))
from _shared import answer_is_correct, cached_answer, doc_row, get_shield, get_targets, show_log_panel
import streamlit as st

st.set_page_config(page_title="Defense Demo", page_icon="🛡️", layout="wide")
st.title("🛡️ Defense Demo — RAG-Shield turns the attack back")
st.markdown("Same poisoned knowledge base, now with the 3-ring defense engaged.")

shield = get_shield(poisoned=True)
targets = get_targets()
choice = st.selectbox("Pick a target question", [t["question"] for t in targets])
t = next(x for x in targets if x["question"] == choice)
cands = [t["true_answer"], t["wrong_answer"]]

if st.button("Run with RAG-Shield", type="primary"):
    out = cached_answer(choice, True, t["true_answer"], t["wrong_answer"])
    tr = out["trace"]

    st.markdown("### Ring-by-ring trace")
    r1, r2, r3 = st.columns(3)
    with r1:
        st.markdown("#### 🟦 Ring 1 — Ingest Guard")
        st.metric("Docs blocked at ingest", len(tr.get("ring1_blocked", [])))
        for d in tr.get("ring1_blocked", [])[:5]:
            v = d.get("_ring1", {})
            st.caption(f"🔴 {d.get('title','')[:40]} — score={v.get('score')} "
                       f"(perp={v.get('perplexity')}, pat={v.get('pattern')})")
    with r2:
        st.markdown("#### 🟩 Ring 2 — Retrieval Scorer")
        st.metric("Low-trust docs dropped", len(tr.get("ring2_dropped", [])))
        for d in tr.get("ring2_kept", [])[:5]:
            st.caption(f"kept · trust={d.get('trust')} · {d.get('title','')[:40]}")
    with r3:
        st.markdown("#### 🟪 Ring 3 — Cross-LLM Consensus")
        v = tr.get("ring3", {})
        st.metric("Panel agreement", f"{int((v.get('agreement') or 0)*100)}%")
        for a in v.get("answers", []):
            st.caption(f"{a['llm']}: `{a['answer']}`")
        if v.get("reretrieved"):
            st.warning(f"Disagreement → re-retrieved without {v.get('dropped_suspects')}")

    st.divider()
    defended = answer_is_correct(out["answer"], t["true_answer"])
    st.markdown(f"## Final answer: {'🟢 ' if defended else '🔴 '}`{out['answer']}`")
    if defended:
        st.success(f"DEFENDED — correct answer **{t['true_answer']}** restored.")
    else:
        st.error("Poison still got through — tune the ring thresholds.")

st.divider(); show_log_panel(n=40)
