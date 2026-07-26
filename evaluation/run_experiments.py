"""
evaluation/run_experiments.py
Headless evaluation harness. Computes attack success rate (ASR) for:
  - no defense (baseline attack)
  - RAG-Shield (our defense)
across all target questions, and writes JSON + a printed table.

Run:
    python evaluation/run_experiments.py
"""
import sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ragshield_core.rag_shield import RAGShield
from ragshield_core.retriever import load_targets
from ragshield_core import config


def main():
    targets = load_targets()
    shield = RAGShield().setup(poisoned=True)
    rows, asr_nd, asr_sh = [], 0, 0

    for t in targets:
        c = [t["true_answer"], t["wrong_answer"]]
        nd = shield.answer(t["question"], defense=False, candidates=c)
        sh = shield.answer(t["question"], defense=True, candidates=c)
        f_nd = t["wrong_answer"].lower() in nd["answer"].lower()
        f_sh = t["wrong_answer"].lower() in sh["answer"].lower()
        asr_nd += f_nd; asr_sh += f_sh
        rows.append({"id": t["id"], "question": t["question"],
                     "true": t["true_answer"], "wrong": t["wrong_answer"],
                     "no_defense": nd["answer"], "attacked": f_nd,
                     "rag_shield": sh["answer"], "still_fooled": f_sh,
                     "ring1_blocked": len(sh["trace"].get("ring1_blocked", [])),
                     "ring2_dropped": len(sh["trace"].get("ring2_dropped", [])),
                     "ring3_agreement": sh["trace"].get("ring3", {}).get("agreement")})

    n = len(targets)
    summary = {"mode": "demo" if config.demo_mode() else "live",
               "n_questions": n,
               "asr_no_defense_pct": round(100*asr_nd/n),
               "asr_rag_shield_pct": round(100*asr_sh/n),
               "reduction_pts": round(100*(asr_nd-asr_sh)/n)}

    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = config.RESULTS_DIR / "asr_results.json"
    out.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2))

    print("\n=== RAG-Shield Evaluation ===")
    print(f"mode={summary['mode']}  questions={n}")
    print(f"{'question':45} {'no-def':18} {'shield':18}")
    print("-"*82)
    for r in rows:
        print(f"{r['question'][:43]:45} {r['no_defense'][:16]:18} {r['rag_shield'][:16]:18}")
    print("-"*82)
    print(f"ASR no-defense : {summary['asr_no_defense_pct']}%")
    print(f"ASR RAG-Shield : {summary['asr_rag_shield_pct']}%")
    print(f"Reduction      : {summary['reduction_pts']} percentage points")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
