import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "components"))
from _shared import get_shield, get_targets, cached_answer, attack_succeeded, show_log_panel
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Results Dashboard", page_icon="📊", layout="wide")
st.title("📊 Results Dashboard — Attack Success Rate")
st.markdown("Computed live over the target questions in this demo.")

shield = get_shield(poisoned=True)
targets = get_targets()

if st.button("Run evaluation", type="primary"):
    rows = []
    n = len(targets)
    asr_nodef = asr_shield = 0
    for t in targets:
        c = [t["true_answer"], t["wrong_answer"]]
        nd = cached_answer(t["question"], False, t["true_answer"], t["wrong_answer"])
        wd = cached_answer(t["question"], True, t["true_answer"], t["wrong_answer"])
        f_nd = attack_succeeded(nd["answer"], t["wrong_answer"], t["true_answer"])
        f_wd = attack_succeeded(wd["answer"], t["wrong_answer"], t["true_answer"])
        asr_nodef += f_nd; asr_shield += f_wd
        rows.append({"question": t["question"][:40],
                     "no_defense": nd["answer"], "attacked": f_nd,
                     "rag_shield": wd["answer"], "still_fooled": f_wd})

    # paper's-defense baseline is illustrative (perplexity-only ~ Ring1 alone)
    chart = pd.DataFrame({
        "Configuration": ["No Defense", "Paper's Defenses*", "RAG-Shield (Ours)"],
        "Attack Success Rate (%)": [round(100*asr_nodef/n),
                                    29,  # illustrative placeholder from paper
                                    round(100*asr_shield/n)],
    }).set_index("Configuration")

    st.bar_chart(chart, color="#F87171")
    st.caption("*Paper's-defenses bar is an illustrative placeholder until the full "
               "30-question harness runs; the other two are computed live.")

    c1, c2 = st.columns(2)
    c1.metric("ASR — No Defense", f"{round(100*asr_nodef/n)}%")
    c2.metric("ASR — RAG-Shield", f"{round(100*asr_shield/n)}%",
              delta=f"-{round(100*(asr_nodef-asr_shield)/n)} pts", delta_color="inverse")

    st.dataframe(pd.DataFrame(rows), use_container_width=True)
