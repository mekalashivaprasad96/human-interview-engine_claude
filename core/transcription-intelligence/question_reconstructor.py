"""
Question Reconstructor - Reconstructs questions from fragmented or unclear transcripts.
"""

import re
from dataclasses import dataclass
from typing import Optional
from .transcript_cleaner import TranscriptCleaner
from .technical_term_corrector import TechnicalTermCorrector


@dataclass
class ReconstructedQuestion:
    text: str
    confidence: float
    original_fragments: list
    reconstruction_notes: list = field(default_factory=list)
    question_type: str = "unknown"
    requires_clarification: bool = False
    clarification_question: str = ""


class QuestionReconstructor:
    """Reconstructs clear questions from transcript fragments."""

    QUESTION_STARTERS = [
        "can you", "could you", "would you", "tell me", "describe",
        "explain", "how do", "what is", "what was", "why did",
        "how would", "what would", "give me", "walk me through",
        "give an example", "give me an example", "share an example",
    ]

    QUESTION_PATTERNS = {
        "factual": [r"what is", r"define", r"explain", r"difference between"],
        "behavioral": [r"tell me about a time", r"give an example", r"describe a situation"],
        "technical": [r"how (do|would) you", r"implement", r"design", r"architecture"],
        "numerical": [r"how (many|much)", r"what (percentage|ratio|number)", r"give me a number"],
        "hypothetical": [r"how would you", r"what would you do", r"imagine", r"suppose"],
        "system_design": [r"design a", r"architect a", r"scale to", r"high availability"],
        "troubleshooting": [r"debug", r"troubleshoot", r"incident", r"outage", r"root cause"],
    }

    def __init__(self):
        self.cleaner = TranscriptCleaner()
        self.corrector = TechnicalTermCorrector()

    def reconstruct(self, transcript: str, context: dict = None) -> list[ReconstructedQuestion]:
        """Reconstruct questions from a transcript."""
        # First clean the transcript
        cleaned = self.cleaner.clean(transcript)

        # Correct technical terms
        corrected_text, corrections = self.corrector.correct(cleaned.text, context)

        # Extract question fragments
        fragments = self._extract_fragments(corrected_text)

        # Reconstruct each fragment into a question
        questions = []
        for fragment in fragments:
            question = self._reconstruct_fragment(fragment, corrected_text, corrections, context)
            if question:
                questions.append(question)

        return questions

    def _extract_fragments(self, text: str) -> list[str]:
        """Extract potential question fragments from text."""
        fragments = []

        # Split by question marks
        parts = re.split(r'\?\s*', text)
        for part in parts:
            part = part.strip()
            if part and len(part) > 5:
                fragments.append(part + "?")

        # Also look for question starters without question marks
        for starter in self.QUESTION_STARTERS:
            pattern = rf'({starter}.*?)(?=\s+(?:{"|".join(self.QUESTION_STARTERS)})|$)'
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                match = match.strip()
                if match and len(match) > 10 and match not in [f.rstrip('?') for f in fragments]:
                    fragments.append(match + "?")

        return fragments

    def _reconstruct_fragment(self, fragment: str, full_text: str,
                               corrections: list, context: dict) -> Optional[ReconstructedQuestion]:
        """Reconstruct a single fragment into a clear question."""
        # Classify question type
        question_type = self._classify_question(fragment)

        # Check if fragment is complete
        is_complete = self._is_complete_question(fragment)

        # Calculate confidence
        confidence = 0.8 if is_complete else 0.5

        # Boost confidence if technical terms were corrected
        if corrections:
            confidence = min(confidence + 0.1, 1.0)

        # Reduce confidence for very short fragments
        if len(fragment.split()) < 5:
            confidence -= 0.2

        # Check if clarification needed
        requires_clarification = not is_complete or confidence < 0.6
        clarification_question = ""
        if requires_clarification:
            clarification_question = self._generate_clarification(fragment, question_type)

        # Build reconstruction notes
        notes = []
        if corrections:
            notes.append(f"Corrected {len(corrections)} technical term(s)")
        if not is_complete:
            notes.append("Fragment appears incomplete")
        if context:
            notes.append(f"Context: {context.get('interviewer_role', 'unknown')} interviewer")

        return ReconstructedQuestion(
            text=fragment,
            confidence=max(confidence, 0.0),
            original_fragments=[fragment],
            reconstruction_notes=notes,
            question_type=question_type,
            requires_clarification=requires_clarification,
            clarification_question=clarification_question,
        )

    def _classify_question(self, question: str) -> str:
        """Classify question type."""
        q_lower = question.lower()

        for qtype, patterns in self.QUESTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, q_lower):
                    return qtype

        return "unknown"

    def _is_complete_question(self, question: str) -> bool:
        """Check if question appears complete."""
        q_lower = question.lower().strip()

        # Has question mark
        if q_lower.endswith('?'):
            return True

        # Has question starter and reasonable length
        for starter in self.QUESTION_STARTERS:
            if q_lower.startswith(starter) and len(q_lower.split()) >= 6:
                return True

        # Has question word in middle
        question_words = ["what", "how", "why", "when", "where", "which", "who"]
        for qw in question_words:
            if qw in q_lower and len(q_lower.split()) >= 6:
                return True

        return False

    def _generate_clarification(self, fragment: str, question_type: str) -> str:
        """Generate a clarification question."""
        clarifications = {
            "factual": "Could you clarify what specific aspect you'd like me to explain?",
            "behavioral": "Are you looking for a specific type of situation, like a conflict, failure, or leadership example?",
            "technical": "Should I focus on the implementation details, architecture, or a specific technology?",
            "numerical": "What specific metric or number are you looking for?",
            "hypothetical": "What constraints or context should I assume for this scenario?",
            "system_design": "What scale and requirements should I design for?",
            "troubleshooting": "What type of incident or system are you thinking of?",
            "unknown": "Could you rephrase or provide more context for your question?",
        }

        return clarifications.get(question_type, clarifications["unknown"])

    def merge_fragments(self, fragments: list[str]) -> str:
        """Merge related fragments into a single question."""
        if len(fragments) <= 1:
            return fragments[0] if fragments else ""

        # Find common question starter
        starters = [f.lower().split()[0] for f in fragments if f.split()]
        if not starters:
            return fragments[0]

        # Use the most complete fragment as base
        base = max(fragments, key=len)
        return base

    def handle_interruptions(self, transcript: str) -> list[str]:
        """Handle interviewer interruptions in transcript."""
        # Split on interruption markers
        interruption_markers = [
            "hold on", "wait", "stop", "let me interrupt",
            "before you go on", "actually", "correction",
        ]

        parts = [transcript]
        for marker in interruption_markers:
            new_parts = []
            for part in parts:
                split_parts = re.split(rf'(?i)\b{re.escape(marker)}\b', part)
                new_parts.extend(split_parts)
            parts = new_parts

        # Clean up parts
        cleaned = [p.strip() for p in parts if p.strip() and len(p.strip()) > 10]
        return cleaned


from dataclasses import field