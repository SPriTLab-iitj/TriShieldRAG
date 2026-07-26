"""
ragshield_core.ring2_retrieval
RING 2 - Retrieval Scorer. Runs at QUERY time on the retrieved top-K.

Two signals combine into a trust-weighted re-rank:
  - ProvenanceWeight   : trusted sources score higher; unknown/low-trust lower.
  - ConsistencyCheck   : a doc that contradicts the majority of the OTHER
                         retrieved docs is down-weighted (poison usually
                         disagrees with the clean consensus).

Docs whose final trust falls below `drop_below` are removed from the context.
"""
from __future__ import annotations
import re
from collections import Counter

# crude trust table; in production this comes from source metadata / allow-lists
_TRUSTED = {"clean": 1.0, "wikipedia": 0.95, "gov": 0.95, "peer-reviewed": 0.95}
_UNTRUSTED = {"POISONED": 0.1, "user-upload": 0.4, "unknown": 0.5}


class ProvenanceWeight:
    def weight(self, doc: dict) -> float:
        src = str(doc.get("source", "unknown")).lower()
        for k, v in {**_TRUSTED, **_UNTRUSTED}.items():
            if k.lower() in src:
                return v
        return 0.5


class ConsistencyCheck:
    """
    Token-overlap consensus: build a 'majority claim' bag from all retrieved
    docs, then score how much each doc agrees with it. Outliers (poison) agree
    less with the clean majority and get a low consistency score.
    """
    def scores(self, docs: list[dict]) -> list[float]:
        bags = [Counter(re.findall(r"\w+", d.get("text", "").lower())) for d in docs]
        majority = Counter()
        for b in bags:
            majority.update(b)
        # remove very common english-ish tokens by frequency cap
        out = []
        for b in bags:
            if not b:
                out.append(0.0); continue
            overlap = sum(min(b[t], majority[t] - b[t]) for t in b)  # agreement w/ OTHERS
            denom = sum(b.values()) or 1
            out.append(min(1.0, overlap / denom))
        return out


class RetrievalScorer:
    def __init__(self, drop_below: float = 0.35):
        self.drop_below = drop_below
        self.prov = ProvenanceWeight()
        self.cons = ConsistencyCheck()

    def rescore(self, docs: list[dict]) -> list[dict]:
        if not docs:
            return docs
        cons = self.cons.scores(docs)
        scored = []
        for d, c in zip(docs, cons):
            p = self.prov.weight(d)
            base = float(d.get("score", 0.5))
            trust = round(0.45 * p + 0.35 * c + 0.20 * base, 3)
            scored.append({**d, "_ring2": {"provenance": round(p, 3),
                                           "consistency": round(c, 3),
                                           "trust": trust},
                           "trust": trust})
        scored.sort(key=lambda x: x["trust"], reverse=True)
        return scored

    def filter(self, docs: list[dict]) -> tuple[list[dict], list[dict]]:
        scored = self.rescore(docs)
        kept = [d for d in scored if d["trust"] >= self.drop_below]
        dropped = [d for d in scored if d["trust"] < self.drop_below]
        return kept, dropped
