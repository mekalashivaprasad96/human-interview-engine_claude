"""
Transcript Cleaner - Cleans and normalizes speech transcripts.
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class CleanedTranscript:
    text: str
    original: str
    corrections: list = field(default_factory=list)
    confidence: float = 1.0
    detected_language: str = "en"


class TranscriptCleaner:
    """Cleans speech recognition transcripts."""

    # Common speech recognition artifacts
    FILLER_WORDS = [
        "um", "uh", "er", "ah", "like", "you know", "i mean", "sort of",
        "kind of", "basically", "actually", "literally", "so", "right",
        "okay", "well", "anyway", "yeah", "yes", "no", "hmm"
    ]

    REPEATED_WORDS_PATTERN = r'\b(\w+)\s+\1\b'

    # Common misrecognitions
    COMMON_MISRECOGNITIONS = {
        "kubernetes": ["kubernetis", "cubernetes", "cubernetis", "k8s"],
        "docker": ["dockers", "doker", "dockr"],
        "kafka": ["cafka", "kafca", "kafa"],
        "redis": ["reddis", "redus", "reddis"],
        "postgresql": ["postgress", "postgre", "postgres ql"],
        "mysql": ["my sequel", "my sql", "my s q l"],
        "github": ["git hub", "get hub", "git hub"],
        "gitlab": ["git lab", "get lab"],
        "jenkins": ["jenkin", "jenkins"],
        "terraform": ["terraforms", "terrafoam", "terra firm"],
        "ansible": ["ansable", "ansibl", "an sibel"],
        "prometheus": ["promethius", "prometheus", "prometheous"],
        "grafana": ["grafana", "graphana", "graffana"],
        "microservices": ["micro services", "micro servis", "micro serves"],
        "kubernetes cluster": ["kubernetes cluster", "kubernetes clustar"],
        "load balancer": ["load balancer", "load balencer", "lode balancer"],
        "api gateway": ["api gateway", "a p i gateway", "api gate way"],
        "service mesh": ["service mesh", "service mech", "servis mesh"],
        "ci cd": ["c i cd", "ci cd", "c i c d", "cd ci"],
        "devops": ["dev ops", "de vops", "devops"],
        "sre": ["s r e", "sre", "sr e"],
        "rps": ["r p s", "rps", "are pea ess"],
        "tps": ["t p s", "tps", "tea pea ess"],
        "sla": ["s l a", "sla", "ess el ay"],
        "p99": ["p ninety nine", "p nine nine", "p 99"],
        "p95": ["p ninety five", "p nine five", "p 95"],
        "p50": ["p fifty", "p five zero", "p 50"],
    }

    def __init__(self):
        pass

    def clean(self, transcript: str) -> CleanedTranscript:
        """Clean a speech transcript."""
        original = transcript
        text = transcript
        corrections = []

        # 1. Remove excessive filler words
        text, filler_corrections = self._remove_fillers(text)
        corrections.extend(filler_corrections)

        # 2. Fix repeated words
        text, repeat_corrections = self._fix_repeated_words(text)
        corrections.extend(repeat_corrections)

        # 3. Fix common technical misrecognitions
        text, tech_corrections = self._fix_technical_terms(text)
        corrections.extend(tech_corrections)

        # 4. Normalize punctuation and capitalization
        text = self._normalize_punctuation(text)

        # 5. Fix sentence boundaries
        text = self._fix_sentence_boundaries(text)

        # 6. Handle incomplete sentences
        text = self._handle_incomplete(text)

        confidence = self._calculate_confidence(original, text, corrections)

        return CleanedTranscript(
            text=text.strip(),
            original=original,
            corrections=corrections,
            confidence=confidence,
        )

    def _remove_fillers(self, text: str) -> tuple[str, list]:
        """Remove filler words."""
        corrections = []
        words = text.split()
        cleaned = []
        i = 0

        while i < len(words):
            word = words[i].lower().strip('.,!?')
            if word in self.FILLER_WORDS:
                # Check if it's a standalone filler (not part of a technical term)
                if i > 0 and i < len(words) - 1:
                    prev = words[i-1].lower().strip('.,!?')
                    next_w = words[i+1].lower().strip('.,!?')
                    # Don't remove if part of technical term
                    if not (prev in ["kubernetes", "docker", "kafka"] or next_w in ["cluster", "container", "topic"]):
                        corrections.append(f"Removed filler: '{words[i]}'")
                        i += 1
                        continue
            cleaned.append(words[i])
            i += 1

        return " ".join(cleaned), corrections

    def _fix_repeated_words(self, text: str) -> tuple[str, list]:
        """Fix repeated words from stuttering."""
        corrections = []

        def replace_repeat(match):
            corrections.append(f"Fixed repetition: '{match.group(0)}'")
            return match.group(1)

        text = re.sub(self.REPEATED_WORDS_PATTERN, replace_repeat, text, flags=re.IGNORECASE)
        return text, corrections

    def _fix_technical_terms(self, text: str) -> tuple[str, list]:
        """Fix common technical term misrecognitions."""
        corrections = []
        text_lower = text.lower()

        for correct, variants in self.COMMON_MISRECOGNITIONS.items():
            for variant in variants:
                if variant in text_lower:
                    # Replace preserving case pattern
                    pattern = re.compile(re.escape(variant), re.IGNORECASE)
                    text = pattern.sub(correct, text)
                    corrections.append(f"Fixed '{variant}' → '{correct}'")

        return text, corrections

    def _normalize_punctuation(self, text: str) -> str:
        """Normalize punctuation."""
        # Fix spacing around punctuation
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        text = re.sub(r'([.,!?;:])\s*', r'\1 ', text)
        # Multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Capitalize first letter
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        return text

    def _fix_sentence_boundaries(self, text: str) -> str:
        """Fix sentence boundaries."""
        # Split on question words that likely start new questions
        question_starters = [
            "can you", "could you", "would you", "tell me", "describe",
            "explain", "how do", "what is", "what was", "why did",
            "how would", "what would", "give me", "walk me through",
        ]

        for starter in question_starters:
            pattern = rf'(?<=[.!?])\s+({starter}\s)'
            text = re.sub(pattern, r'\n\1', text, flags=re.IGNORECASE)

        return text

    def _handle_incomplete(self, text: str) -> str:
        """Handle incomplete sentences at end."""
        # Remove trailing incomplete fragments
        text = re.sub(r'\s+(and|or|but|so|because|since|if|when|then)\s*$', '', text, flags=re.IGNORECASE)
        return text

    def _calculate_confidence(self, original: str, cleaned: str, corrections: list) -> float:
        """Calculate confidence in cleaning."""
        if not original:
            return 0.0

        # Base confidence
        confidence = 1.0

        # Reduce for many corrections
        confidence -= min(len(corrections) * 0.05, 0.3)

        # Reduce for large length difference
        length_ratio = len(cleaned) / len(original) if original else 1
        if length_ratio < 0.7 or length_ratio > 1.3:
            confidence -= 0.1

        return max(confidence, 0.0)

    def extract_questions(self, transcript: str) -> list[str]:
        """Extract individual questions from a transcript."""
        cleaned = self.clean(transcript)
        text = cleaned.text

        # Split on question marks and question starters
        questions = []

        # Split by explicit question marks
        parts = re.split(r'\?\s*', text)
        for part in parts:
            part = part.strip()
            if part and len(part) > 10:
                # Ensure it ends with question mark
                if not part.endswith('?'):
                    part += '?'
                questions.append(part)

        # If no question marks found, try to split by question starters
        if not questions:
            question_starters = [
                "can you", "could you", "would you", "tell me", "describe",
                "explain", "how do", "what is", "what was", "why did",
                "how would", "what would", "give me", "walk me through",
            ]
            for starter in question_starters:
                pattern = rf'({starter}.*?)(?=\s+(?:{"|".join(question_starters)})|$)'
                matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    match = match.strip()
                    if match and len(match) > 10:
                        if not match.endswith('?'):
                            match += '?'
                        questions.append(match)

        return questions


from dataclasses import field