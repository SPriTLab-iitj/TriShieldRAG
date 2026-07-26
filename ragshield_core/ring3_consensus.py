"""
ragshield_core.ring3_consensus
RING 3 - Cross-LLM Consensus. Runs at ANSWER time.

Query N LLMs with the same context. If they AGREE -> high confidence, return.
If they DISAGREE -> flag, drop the lowest-trust doc(s), re-retrieve/re-ask once.
Different model families don't get fooled identically, so disagreement is a
strong poison signal.
"""
from __future__ import annotations
from collections import Counter
from typing import Callable, Optional
import re as _re


class CrossLLMConsensus:
    def __init__(self, panel, agreement: float = 0.66):
        """panel = list[LLMBackend]; agreement = fraction needed to accept."""
        self.panel = panel
        self.agreement = agreement

    def _norm(self, s: str) -> str:
        """Normalise for comparison — lowercase, collapse spaces, strip punct."""
        s = s.lower().strip()
        s = _re.sub(r"[^a-z0-9 ]", "", s)   # strip punctuation
        s = _re.sub(r"\s+", " ", s).strip()
        return s[:120]                        # longer window than before (was 80)

    def _candidate_match(self, answer: str, candidate: str) -> bool:
        """True if the candidate name is meaningfully present in the answer."""
        a = self._norm(answer)
        c = self._norm(candidate)
        # direct substring match
        if c in a:
            return True
        # match on first-name or last-name token (handles "Martin Eberhard" vs
        # "founded by Martin Eberhard and Marc Tarpenning" vs "Eberhard")
        tokens = [t for t in c.split() if len(t) > 3]
        return all(t in a for t in tokens) if tokens else False

    _NO_ANSWER = ("no answer","no mention", "not mentioned", "does not mention",
                  "no information", "cannot find", "can't find",
                  "not in the provided", "does not provide", "not contain",
                  "i don't know", "i do not know", "unable to", "[error",
                  "dont have", "don't have")

    def _is_no_answer(self, s: str) -> bool:
        s = s.lower()
        return any(p in s for p in self._NO_ANSWER)

    def vote(self, question: str, context_docs: list[dict],
             candidates: Optional[list[str]] = None) -> dict:
        answers = []
        for llm in self.panel:
            try:
                a = llm.answer_with_context(question, context_docs, candidates)
            except Exception as e:
                a = f"[error: {e}]"
            answers.append({"llm": llm.name, "answer": a})

        substantive = [a for a in answers if not self._is_no_answer(a["answer"])]
        pool = substantive if substantive else answers

        # ── Candidate-aware agreement ─────────────────────────────────────────
        # If candidates supplied, group answers by WHICH candidate they support
        # rather than exact string match. This handles Claude saying a longer
        # sentence than Mistral while both correctly name "Martin Eberhard".
        if candidates and len(candidates) >= 2:
            buckets = {self._norm(c): [] for c in candidates}
            buckets["other"] = []
            for a in pool:
                matched = False
                for c in candidates:
                    if self._candidate_match(a["answer"], c):
                        buckets[self._norm(c)].append(a)
                        matched = True
                        break
                if not matched:
                    buckets["other"].append(a)

            # find the largest bucket
            best_key = max(buckets, key=lambda k: len(buckets[k]))
            best_pool = buckets[best_key]
            agree_n = len(best_pool)
            frac = agree_n / len(answers)
            agreed = frac >= self.agreement
            # winner = shortest answer in the winning bucket (cleaner display)
            winner_entry = min(best_pool, key=lambda a: len(a["answer"])) \
                if best_pool else pool[0]
            winner = winner_entry["answer"]
        else:
            # fallback: exact-norm match (no candidates given)
            norm = [self._norm(a["answer"]) for a in pool]
            tally = Counter(norm)
            top, count = tally.most_common(1)[0]
            agree_n = sum(1 for a in answers if self._norm(a["answer"]) == top)
            frac = agree_n / len(answers)
            agreed = frac >= self.agreement
            winner = next(a["answer"] for a in pool if self._norm(a["answer"]) == top)

        return {
            "answers":   answers,
            "agreement": round(frac, 2),
            "agreed":    agreed,
            "answer":    winner,
        }

    def run(self, question: str, context_docs: list[dict],
            candidates: Optional[list[str]] = None,
            reretrieve: Optional[Callable[[list[dict]], list[dict]]] = None) -> dict:
        first = self.vote(question, context_docs, candidates)
        if first["agreed"] or reretrieve is None:
            first["reretrieved"] = False
            return first
        # disagreement -> drop lowest-trust doc(s) and try once more
        ranked = sorted(context_docs, key=lambda d: d.get("trust", d.get("score", 0)))
        suspects = ranked[: max(1, len(ranked) // 3)]
        cleaner = reretrieve(suspects)
        second = self.vote(question, cleaner, candidates)
        second["reretrieved"] = True
        second["dropped_suspects"] = [s.get("id") for s in suspects]
        return second
