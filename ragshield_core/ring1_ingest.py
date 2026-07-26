"""
ragshield_core.ring1_ingest
RING 1 - Ingest Guard. Screens a document BEFORE it enters the KB.

Three independent detectors (each returns a 0..1 suspicion score):
  - PerplexityDetector : flags text that is too repetitive / keyword-stuffed
                         (a tell of crafted retrieval triggers). Demo uses a
                         repetition/burstiness proxy; real mode can swap in GPT-2.
  - PatternDetector    : flags a document that embeds a question verbatim or
                         repeats the same query-like sentence (PoisonedRAG hallmark).
  - OutlierDetector    : flags a document whose vector is far from the KB centroid.

A document is BLOCKED if the combined score exceeds `threshold`.
"""
from __future__ import annotations
import re
from collections import Counter
import numpy as np


class PerplexityDetector:
    """Proxy perplexity: high repetition / low lexical diversity => suspicious."""
    def score(self, text: str) -> float:
        words = re.findall(r"\w+", text.lower())
        if len(words) < 8:
            return 0.0
        diversity = len(set(words)) / len(words)          # 1.0 = all unique
        rep = 1.0 - diversity                              # high => repetitive
        # keyword stuffing: most common word frequency
        top = Counter(words).most_common(1)[0][1] / len(words)
        return float(min(1.0, 0.6 * rep + 2.0 * max(0.0, top - 0.12)))


class PatternDetector:
    """Detects verbatim-question embedding and self-referential query stuffing."""
    def score(self, text: str, kb_questions: list[str] | None = None) -> float:
        s = 0.0
        # repeated question-like sentences ending in '?'
        q_sents = re.findall(r"[^.?!]*\?", text)
        if len(q_sents) >= 1 and len(text) < 400:
            s += 0.4
        # a known target question appears verbatim
        if kb_questions:
            for q in kb_questions:
                if q.lower().strip("? ") in text.lower():
                    s += 0.5
                    break
        # "according to verified/multiple sources" style assertion stuffing
        if re.search(r"(verified records|multiple independent sources|widely accepted|well documented)", text, re.I):
            s += 0.3
        return float(min(1.0, s))


class OutlierDetector:
    """Embedding-space outlier vs KB centroid (cosine distance)."""
    def __init__(self):
        self._centroid = None

    def fit(self, vectors: np.ndarray):
        v = np.asarray(vectors, dtype=np.float32)
        c = v.mean(axis=0)
        n = np.linalg.norm(c)
        self._centroid = c / n if n else c
        return self

    def score(self, vector: np.ndarray) -> float:
        if self._centroid is None:
            return 0.0
        v = np.asarray(vector, dtype=np.float32)
        n = np.linalg.norm(v)
        v = v / n if n else v
        cos = float(np.dot(v, self._centroid))
        return float(min(1.0, max(0.0, 1.0 - cos)))   # far from centroid => high


class IngestGuard:
    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        self.perp = PerplexityDetector()
        self.pat = PatternDetector()
        self.out = OutlierDetector()

    def inspect(self, doc: dict, kb_questions: list[str] | None = None,
                vector: np.ndarray | None = None) -> dict:
        text = f"{doc.get('title','')} {doc.get('text','')}"
        p = self.perp.score(text)
        pa = self.pat.score(text, kb_questions)
        o = self.out.score(vector) if vector is not None else 0.0
        combined = max(p, pa, 0.7 * o + 0.3 * max(p, pa))   # any strong signal blocks
        return {
            "perplexity": round(p, 3), "pattern": round(pa, 3), "outlier": round(o, 3),
            "score": round(combined, 3), "blocked": combined >= self.threshold,
        }

    def filter_corpus(self, docs: list[dict], kb_questions: list[str] | None = None) -> tuple[list[dict], list[dict]]:
        """Return (kept, blocked)."""
        kept, blocked = [], []
        for d in docs:
            verdict = self.inspect(d, kb_questions)
            (blocked if verdict["blocked"] else kept).append({**d, "_ring1": verdict})
        return kept, blocked
