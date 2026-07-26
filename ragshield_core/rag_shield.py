"""
ragshield_core.rag_shield
The orchestrator. Wires Retriever + Ring1 + Ring2 + Ring3 into one pipeline
and exposes a single `answer()` call plus a `trace()` call that returns every
ring's decision for the forensic UI.

Usage:
    shield = RAGShield().setup(poisoned=True)
    out = shield.answer("Who founded Tesla Motors?", defense=True,
                        candidates=["Martin Eberhard", "Nikola Jones"])
"""
from __future__ import annotations
from typing import Optional

from .retriever import Retriever, load_targets
from .ring1_ingest import IngestGuard
from .ring2_retrieval import RetrievalScorer
from .ring3_consensus import CrossLLMConsensus
from .llm_backends import make_consensus_panel
from . import config
from .raglog import log


class RAGShield:
    def __init__(self, top_k: int = None):
        self.top_k = top_k or config.TOP_K
        self.retriever = Retriever()
        self.ingest = IngestGuard()
        self.scorer = RetrievalScorer()
        self.panel = make_consensus_panel()
        self.consensus = CrossLLMConsensus(self.panel)
        self._questions = [t["question"] for t in load_targets()]

    # ---------- setup ----------
    def setup(self, poisoned: bool = True):
        """
        Load KB and (optionally) inject poison into the corpus.
        NOTE: Ring 1 is NOT applied here. It is applied per-query only when
        defense=True, so the no-defense baseline genuinely sees the poison
        (otherwise the attack could never 'succeed' and the demo would lie).
        """
        self.retriever.load_kb()
        self.poisoned = poisoned
        if poisoned:
            self.retriever.load_poison()
            self.retriever.inject_poison()   # builds index with poison included
        else:
            self.retriever.build()
        self._ring1_blocked = []
        return self

    # ---------- main entry ----------
    def answer(self, question: str, defense: bool = True,
               candidates: Optional[list[str]] = None) -> dict:
        trace = self.trace(question, defense=defense, candidates=candidates)
        return {"answer": trace["answer"], "defense": defense, "trace": trace}

    def trace(self, question: str, defense: bool = True,
              candidates: Optional[list[str]] = None) -> dict:
        log(f"QUERY: {question!r}  (defense={'ON' if defense else 'OFF'})")
        retrieved = self.retriever.retrieve(question, self.top_k)
        log(f"  retrieved {len(retrieved)} docs "
            f"({sum(1 for d in retrieved if d.get('source')=='POISONED')} poison)")
        t = {"question": question, "defense": defense, "retrieved": retrieved,
             "ring1_blocked": []}

        if not defense:
            log("  NO DEFENSE: feeding raw context straight to the LLM")
            llm = self.panel[0]
            t["answer"] = llm.answer_with_context(question, retrieved, candidates)
            log(f"  ANSWER (undefended) -> {t['answer'][:60]!r}")
            t["mode"] = "no-defense"
            return t

        # ----- DEFENSE ON -----
        # Ring 1: screen the retrieved docs at query time (ingest-style checks)
        log("  RING 1 (Ingest Guard): screening retrieved docs...")
        kept1, blocked1 = self.ingest.filter_corpus(retrieved, self._questions)
        log(f"  RING 1 -> blocked {len(blocked1)} poison doc(s)")
        t["ring1_blocked"] = blocked1
        if kept1:
            retrieved = kept1
        else:
            blocked_ids = {b.get("id") for b in blocked1}
            wider = self.retriever.retrieve(question, self.top_k * 6)
            retrieved = [d for d in wider if d.get("id") not in blocked_ids
                         and d.get("source") != "POISONED"][: self.top_k]
            log(f"  RING 1 -> all poison; re-retrieved {len(retrieved)} clean doc(s) from KB")

        # Ring 2: rescore + drop low-trust
        log("  RING 2 (Retrieval Scorer): re-ranking by trust...")
        kept, dropped = self.scorer.filter(retrieved)
        log(f"  RING 2 -> kept {len(kept)}, dropped {len(dropped)} low-trust")
        t["ring2_kept"], t["ring2_dropped"] = kept, dropped

        # Ring 3: cross-LLM consensus with re-retrieval on disagreement
        def reretrieve(suspects):
            ids = {s.get("id") for s in suspects}
            return [d for d in kept if d.get("id") not in ids]

        log(f"  RING 3 (Cross-LLM Consensus): polling {len(self.panel)} models...")
        verdict = self.consensus.run(question, kept, candidates, reretrieve)
        log(f"  RING 3 -> agreement {int(verdict['agreement']*100)}%"
            + (" | DISAGREED, re-retrieved" if verdict.get("reretrieved") else " | agreed"))
        t["ring3"] = verdict
        t["answer"] = verdict["answer"]
        log(f"  FINAL ANSWER -> {t['answer'][:60]!r}")
        t["mode"] = "rag-shield"
        return t
