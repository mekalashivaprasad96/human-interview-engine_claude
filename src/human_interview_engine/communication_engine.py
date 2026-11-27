"""Natural Human Communication Engine — shapes authentic, varied, non-robotic spoken answers."""

from __future__ import annotations

import re
from typing import Any

from .config_loader import EngineConfig
from .models import word_count


_CONTRACTIONS = (
    (r"\bI would\b", "I'd"),
    (r"\bI have\b", "I've"),
    (r"\bI am\b", "I'm"),
    (r"\bwe would\b", "we'd"),
    (r"\bwe have\b", "we've"),
    (r"\bwe were not\b", "we weren't"),
    (r"\bdid not\b", "didn't"),
    (r"\bdoes not\b", "doesn't"),
    (r"\bdo not\b", "don't"),
    (r"\bcould not\b", "couldn't"),
    (r"\bwould not\b", "wouldn't"),
    (r"\bwas not\b", "wasn't"),
    (r"\bwere not\b", "weren't"),
    (r"\bthat is\b", "that's"),
    (r"\bit is\b", "it's"),
    (r"\bthere is\b", "there's"),
)


class HumanCommunicationEngine:
    """Applies natural first-person cadence, opening/closing diversity, and strict spoken protocol."""

    def __init__(self, config: EngineConfig) -> None:
        self.config = config
        self.rules = config.communication_rules

    def select_opening_style(self, recent_openings: list[str], precision_targets: list[str], is_yes_no: bool) -> str:
        """Choose an opening style that avoids repeating consecutive opening stems."""
        if "yes_no_first" in precision_targets or is_yes_no:
            return "direct_yes_no_then_qualifier"
        styles = list(self.rules.get("varied_opening_styles", ["direct_fact", "context_first", "decision_first", "constraint_first"]))
        candidates = [s for s in styles if s != "direct_yes_no_then_qualifier"]
        if not recent_openings:
            return candidates[0]
        last_stem = recent_openings[-1].lower()
        # Rotate cleanly based on history length
        idx = len(recent_openings) % len(candidates)
        chosen = candidates[idx]
        if last_stem.startswith("at ") and chosen == "context_first":
            chosen = candidates[(idx + 1) % len(candidates)]
        return chosen

    def humanize_spoken_text(
        self,
        raw_text: str,
        use_contractions: bool = True,
        banned_phrases: list[str] | None = None,
        max_words: int | None = None,
    ) -> str:
        """Normalize prose to sound spoken aloud without AI formatting, STAR labels, or clichés."""
        text = (raw_text or "").strip()

        # Strip accidental markdown bullets/headings or STAR labels
        text = re.sub(r"^\s*(?:#{1,6}\s*|\*{1,2}(?:Situation|Task|Action|Result|Answer)\*{0,2}\s*:?\s*)", "", text, flags=re.IGNORECASE | re.MULTILINE)
        text = re.sub(r"\b(?:Situation|Task|Action|Result)\s*:\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"^\s*[-*•]\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"\s*\n+\s*", " ", text)

        # Strip banned phrases if any crept in
        all_banned = list(self.rules.get("banned_ai_and_cliche_phrases", [])) + list(banned_phrases or [])
        for phrase in all_banned:
            text = re.sub(rf"\b{re.escape(phrase)}[,.\s]*", "", text, flags=re.IGNORECASE)

        if use_contractions:
            for pat, rep in _CONTRACTIONS:
                text = re.sub(pat, rep, text)

        text = re.sub(r"\s{2,}", " ", text).strip()

        # Trim gracefully at sentence boundary if over max_words
        if max_words and word_count(text) > max_words:
            sentences = re.split(r"(?<=[.!?])\s+", text)
            kept: list[str] = []
            running = 0
            for sent in sentences:
                wc = word_count(sent)
                if kept and running + wc > max_words:
                    break
                kept.append(sent)
                running += wc
            if kept:
                text = " ".join(kept).strip()

        return text

    @staticmethod
    def extract_opening_stem(text: str) -> str:
        words = (text or "").strip().split()[:4]
        return " ".join(words).lower()

    @staticmethod
    def extract_closing_stem(text: str) -> str:
        words = (text or "").strip().split()[-5:]
        return " ".join(words).lower()
