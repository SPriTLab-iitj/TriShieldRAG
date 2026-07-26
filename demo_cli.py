"""
demo_cli.py — quick terminal demo (backup if Streamlit isn't handy).
Run:  python demo_cli.py "Who founded Tesla Motors?"
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ragshield_core.rag_shield import RAGShield
from ragshield_core.retriever import load_targets


def main():
    q = sys.argv[1] if len(sys.argv) > 1 else "Who founded Tesla Motors?"
    targets = {t["question"]: t for t in load_targets()}
    t = targets.get(q)
    cands = [t["true_answer"], t["wrong_answer"]] if t else None

    shield = RAGShield().setup(poisoned=True)
    print(f"\nQuestion: {q}")
    if t:
        print(f"Truth: {t['true_answer']}   Attacker wants: {t['wrong_answer']}")

    nd = shield.answer(q, defense=False, candidates=cands)
    print(f"\n[NO DEFENSE]  -> {nd['answer']}")

    sh = shield.answer(q, defense=True, candidates=cands)
    tr = sh["trace"]
    print(f"[RAG-SHIELD]  -> {sh['answer']}")
    print(f"   Ring1 blocked={len(tr.get('ring1_blocked',[]))}  "
          f"Ring2 dropped={len(tr.get('ring2_dropped',[]))}  "
          f"Ring3 agreement={tr.get('ring3',{}).get('agreement')}")


if __name__ == "__main__":
    main()
