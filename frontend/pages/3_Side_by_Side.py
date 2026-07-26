import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "components"))
from _shared import get_shield, get_targets, cached_answer, attack_succeeded, answer_is_correct, is_refusal
import streamlit as st

st.set_page_config(page_title="Side by Side", page_icon="⚖️", layout="wide")
st.title("⚖️ Side-by-Side — poisoned vs shielded")

shield = get_shield(poisoned=True)
targets = get_targets()
choice = st.selectbox("Pick a target question", [t["question"] for t in targets])
t = next(x for x in targets if x["question"] == choice)
cands = [t["true_answer"], t["wrong_answer"]]

if st.button("Compare", type="primary"):
    nd = cached_answer(choice, False, t["true_answer"], t["wrong_answer"])
    wd = cached_answer(choice, True, t["true_answer"], t["wrong_answer"])
    fooled = attack_succeeded(nd["answer"], t["wrong_answer"], t["true_answer"])
    defended = answer_is_correct(wd["answer"], t["true_answer"])

    a, b = st.columns(2)
    with a:
        st.markdown("### 🔴 Plain RAG (no defense)")
        st.markdown(f"# `{nd['answer']}`")
        st.error("Attacker's answer" if fooled else "Clean answer")
    with b:
        st.markdown("### 🛡️ RAG-Shield")
        st.markdown(f"# `{wd['answer']}`")
        st.success("Correct answer restored" if defended else "Still fooled")

    st.divider()
    st.markdown(f"Truth: **{t['true_answer']}**  ·  Attacker wanted: **{t['wrong_answer']}**")
    tr = wd["trace"]
    st.caption(f"Shield trace — Ring1 blocked {len(tr.get('ring1_blocked',[]))}, "
               f"Ring2 dropped {len(tr.get('ring2_dropped',[]))}, "
               f"Ring3 agreement {int((tr.get('ring3',{}).get('agreement') or 0)*100)}%")
