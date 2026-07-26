import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "components"))
from _shared import get_shield, get_targets, doc_row, cached_answer, attack_succeeded, is_refusal, show_log_panel
import streamlit as st

st.set_page_config(page_title="Attack Demo", page_icon="🔴", layout="wide")
st.title("🔴 Attack Demo — PoisonedRAG in action")
st.markdown("A handful of poison documents injected into the knowledge base hijack the answer.")

shield = get_shield(poisoned=True)
targets = get_targets()
labels = [t["question"] for t in targets]
choice = st.selectbox("Pick a target question", labels)
t = next(x for x in targets if x["question"] == choice)
cands = [t["true_answer"], t["wrong_answer"]]

if st.button("Run attack (no defense)", type="primary"):
    out = cached_answer(choice, False, t["true_answer"], t["wrong_answer"])
    tr = out["trace"]
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### Retrieved context (raw)")
        for d in tr["retrieved"]:
            line, title, text = doc_row(d)
            st.markdown(f"**{title}** — {line}")
            st.caption(text)

    with c2:
        st.markdown("#### Result")
        st.markdown(f"True answer: **{t['true_answer']}**")
        st.markdown(f"Attacker's target: **{t['wrong_answer']}**")

        fooled = attack_succeeded(out["answer"], t["wrong_answer"], t["true_answer"])
        answer_txt = out["answer"]

        st.markdown(f"### LLM said: {'🔴 ' if fooled else '🟢 '}`{answer_txt}`")

        if fooled:
            st.error("⚠️  ATTACK SUCCEEDED — the LLM returned the attacker's planted answer.")
            st.caption(
                "The poison docs out-ranked the clean ones in retrieval "
                "and dominated the context the LLM reads."
            )
        else:
            # Work out WHY the attack didn't land — helpful for examiner
            poison_docs = [d for d in tr["retrieved"] if d.get("source") == "POISONED"]
            clean_docs  = [d for d in tr["retrieved"] if d.get("source") != "POISONED"]

            if clean_docs and poison_docs:
                top_clean  = max(clean_docs,  key=lambda d: d.get("score", 0))
                top_poison = max(poison_docs, key=lambda d: d.get("score", 0))
                if top_clean["score"] > top_poison["score"]:
                    reason = (
                        f"The clean doc '{top_clean.get('title','')[:40]}' "
                        f"(score {top_clean['score']:.3f}) ranked above the poison "
                        f"docs (score {top_poison['score']:.3f}) — the LLM saw the "
                        f"real answer first."
                    )
                else:
                    reason = (
                        "Poison docs were retrieved but the LLM still returned "
                        "the correct answer — the injection text wasn't convincing "
                        "enough to override the clean evidence."
                    )
            elif not poison_docs:
                reason = "No poison docs appeared in the top-K for this question."
            else:
                reason = "The LLM answered correctly despite the poisoned context."

            st.success("✅  Attack did not land this time.")
            st.caption(reason)

st.divider()
show_log_panel(n=30)
