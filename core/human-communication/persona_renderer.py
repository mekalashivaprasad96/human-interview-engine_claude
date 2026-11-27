"""
Persona Renderer - Renders the candidate persona consistently across responses.
"""

from dataclasses import dataclass
from typing import Optional
from ..candidate_intelligence.persona_builder import ProfessionalPersona


@dataclass
class PersonaRenderConfig:
    use_contractions: bool = True
    sentence_variance: str = "medium"  # low, medium, high
    preferred_openings: list = field(default_factory=list)
    preferred_transitions: list = field(default_factory=list)
    preferred_closings: list = field(default_factory=list)
    avoid_phrases: list = field(default_factory=list)
    signature_phrases: list = field(default_factory=list)


class PersonaRenderer:
    """Renders candidate persona consistently in responses."""

    def __init__(self, persona: ProfessionalPersona):
        self.persona = persona
        self.config = self._build_config()

    def _build_config(self) -> PersonaRenderConfig:
        """Build rendering config from persona."""
        config = PersonaRenderConfig()

        # Contractions
        config.use_contractions = True  # Default to natural speech

        # Sentence variance
        config.sentence_variance = self.persona.sentence_variance if hasattr(self.persona, 'sentence_variance') else "medium"

        # Signature phrases
        config.signature_phrases = getattr(self.persona, 'signature_phrases', [])

        # Avoid phrases
        config.avoid_phrases = getattr(self.persona, 'avoid_phrases', [])

        # Preferred openings by communication style
        openings = {
            "direct": ["So, ", "The short answer: ", "Here's what happened: ", "Directly: "],
            "analytical": ["Breaking it down, ", "There are a few factors: ", "Let me structure this: "],
            "narrative": ["Let me give you an example: ", "Here's what happened: ", "The context was: "],
            "collaborative": ["From the team's perspective, ", "We approached it by ", "The consensus was "],
            "executive": ["Strategically, ", "The business impact: ", "At the organizational level: "],
            "technical-deep": ["Implementation-wise, ", "Under the hood, ", "At the system level: "],
            "balanced": ["In practice, ", "What worked was: ", "The approach was: "],
        }
        config.preferred_openings = openings.get(self.persona.communication_style, openings["balanced"])

        # Transitions
        transitions = {
            "direct": ["The key thing: ", "Bottom line: ", "Directly: "],
            "analytical": ["The critical factor: ", "Data shows: ", "From the numbers: "],
            "narrative": ["For instance, ", "A concrete example: ", "Specifically: "],
            "collaborative": ["The team found: ", "We discovered: ", "Together we: "],
            "executive": ["Key takeaway: ", "Business impact: ", "Strategically: "],
            "technical-deep": ["Technically: ", "Under the hood: ", "At the code level: "],
            "balanced": ["The important part: ", "What mattered: ", "In practice: "],
        }
        config.preferred_transitions = transitions.get(self.persona.communication_style, transitions["balanced"])

        # Closings
        closings = {
            "direct": [".", " That's it.", " Done."],
            "analytical": [".", " That's the analysis.", " Data-driven."],
            "narrative": [".", " That's how it played out.", " End of story."],
            "collaborative": [".", " Team effort.", " We delivered."],
            "executive": [".", " Strategic win.", " Bottom line impact."],
            "technical-deep": [".", " Technical debt paid.", " Shipped."],
            "balanced": [".", " That worked.", " Made a difference."],
        }
        config.preferred_closings = closings.get(self.persona.communication_style, closings["balanced"])

        return config

    def render_opening(self, response_index: int) -> str:
        """Render a natural opening."""
        if response_index == 0:
            return ""  # First response often doesn't need opening

        # Use signature phrase occasionally
        if self.config.signature_phrases and response_index % 4 == 0:
            phrase = self.config.signature_phrases[response_index % len(self.config.signature_phrases)]
            return f"{phrase} "

        # Use preferred opening
        openings = self.config.preferred_openings
        return f"{openings[response_index % len(openings)]}"

    def render_transition(self, transition_type: str, response_index: int) -> str:
        """Render a transition phrase."""
        transitions = {
            "elaboration": ["The key thing was ", "What made the difference: ", "Critical decision: "],
            "contrast": ["However, ", "On the flip side, ", "That said, "],
            "causation": ["Because ", "Since ", "Given that "],
            "example": ["For instance, ", "Specifically, ", "In one case: "],
            "conclusion": ["Ultimately, ", "End result: ", "What it came down to: "],
        }

        pool = transitions.get(transition_type, transitions["elaboration"])
        # Add persona-specific transitions
        pool.extend(self.config.preferred_transitions)

        return pool[response_index % len(pool)]

    def render_closing(self, response_index: int, question_type: str) -> str:
        """Render a natural closing."""
        # Don't close every response
        if question_type in ["numerical", "narrow_technical_followup", "acknowledgment"]:
            return ""

        if response_index % 3 != 0:
            return ""

        closings = self.config.preferred_closings
        return f" {closings[response_index % len(closings)]}"

    def apply_contractions(self, text: str) -> str:
        """Apply natural contractions."""
        if not self.config.use_contractions:
            return text

        contractions = {
            "I am": "I'm",
            "I have": "I've",
            "I will": "I'll",
            "I would": "I'd",
            "I had": "I'd",
            "we are": "we're",
            "we have": "we've",
            "we will": "we'll",
            "we would": "we'd",
            "it is": "it's",
            "it has": "it's",
            "it will": "it'll",
            "that is": "that's",
            "that has": "that's",
            "there is": "there's",
            "there has": "there's",
            "cannot": "can't",
            "will not": "won't",
            "do not": "don't",
            "does not": "doesn't",
            "did not": "didn't",
            "has not": "hasn't",
            "have not": "haven't",
            "had not": "hadn't",
            "is not": "isn't",
            "are not": "aren't",
            "was not": "wasn't",
            "were not": "weren't",
            "could not": "couldn't",
            "would not": "wouldn't",
            "should not": "shouldn't",
            "must not": "mustn't",
        }

        for full, contracted in contractions.items():
            # Case-insensitive replacement preserving capitalization
            text = re.sub(r'\b' + re.escape(full) + r'\b', contracted, text, flags=re.IGNORECASE)

        return text

    def vary_sentence_structure(self, text: str, variance_level: str = None) -> str:
        """Vary sentence structure for naturalness."""
        level = variance_level or self.config.sentence_variance

        if level == "low":
            return text

        sentences = re.split(r'(?<=[.!?])\s+', text)
        if len(sentences) <= 1:
            return text

        # Simple variation: occasionally combine or split
        if level == "high" and len(sentences) > 2:
            # Combine some short sentences
            combined = []
            i = 0
            while i < len(sentences):
                if i + 1 < len(sentences) and len(sentences[i].split()) < 10 and len(sentences[i+1].split()) < 10:
                    if hash(sentences[i]) % 3 == 0:
                        combined.append(sentences[i].rstrip('.') + ", and " + sentences[i+1][0].lower() + sentences[i+1][1:])
                        i += 2
                        continue
                combined.append(sentences[i])
                i += 1
            text = " ".join(combined)

        return text

    def filter_avoided_phrases(self, text: str) -> str:
        """Remove avoided phrases."""
        for phrase in self.config.avoid_phrases:
            # Case-insensitive removal
            pattern = re.escape(phrase)
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s+([.!?])', r'\1', text)

        return text.strip()

    def render_full_response(self, core_text: str, response_index: int,
                              question_type: str, include_opening: bool = True,
                              include_closing: bool = True) -> str:
        """Render a complete response with persona applied."""
        parts = []

        # Opening
        if include_opening:
            opening = self.render_opening(response_index)
            if opening:
                parts.append(opening)

        # Core text
        parts.append(core_text)

        # Closing
        if include_closing:
            closing = self.render_closing(response_index, question_type)
            if closing:
                parts.append(closing)

        # Assemble
        response = " ".join(parts)

        # Apply persona transformations
        response = self.apply_contractions(response)
        response = self.vary_sentence_structure(response)
        response = self.filter_avoided_phrases(response)

        # Final cleanup
        response = re.sub(r'\s+', ' ', response)
        response = response.strip()

        # Ensure proper capitalization
        if response and response[0].islower():
            response = response[0].upper() + response[1:]

        return response


import re
from dataclasses import field