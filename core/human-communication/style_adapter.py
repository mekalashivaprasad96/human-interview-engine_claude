"""
Style Adapter - Adapts response style to interviewer type and candidate persona.
"""

from dataclasses import dataclass
from typing import Optional
from ..candidate_intelligence.persona_builder import ProfessionalPersona


@dataclass
class StyleRules:
    verbosity: str  # concise, balanced, detailed
    technical_depth: str  # high-level, implementation, architecture
    jargon_level: str  # minimal, moderate, full
    formality: str  # casual, professional, formal
    focus_areas: list = field(default_factory=list)
    avoid_patterns: list = field(default_factory=list)


class StyleAdapter:
    """Adapts communication style based on persona and interviewer."""

    # Base style rules by interviewer type
    INTERVIEWER_STYLES = {
        "recruiter": StyleRules(
            verbosity="concise",
            technical_depth="high-level",
            jargon_level="minimal",
            formality="professional",
            focus_areas=["qualifications", "motivation", "career progression", "culture fit"],
            avoid_patterns=["deep_technical_jargon", "implementation_details", "architecture_deep_dive"],
        ),
        "hiring_manager": StyleRules(
            verbosity="balanced",
            technical_depth="mixed",
            jargon_level="moderate",
            formality="professional",
            focus_areas=["ownership", "decision_making", "team_dynamics", "delivery", "growth"],
            avoid_patterns=["pure_coding", "excessive_theory"],
        ),
        "technical_specialist": StyleRules(
            verbosity="detailed",
            technical_depth="implementation",
            jargon_level="full",
            formality="professional",
            focus_areas=["implementation", "debugging", "performance", "best_practices", "tools"],
            avoid_patterns=["high_level_only", "business_fluff"],
        ),
        "senior_engineer": StyleRules(
            verbosity="detailed",
            technical_depth="implementation",
            jargon_level="full",
            formality="professional",
            focus_areas=["technical_judgment", "tradeoffs", "scalability", "maintainability", "mentoring"],
            avoid_patterns=["textbook_answers", "rigid_thinking"],
        ),
        "architect": StyleRules(
            verbosity="detailed",
            technical_depth="architecture",
            jargon_level="full",
            formality="professional",
            focus_areas=["requirements", "constraints", "tradeoffs", "failure_modes", "operations", "evolution"],
            avoid_patterns=["single_service_focus", "ignoring_operations"],
        ),
        "executive": StyleRules(
            verbosity="concise",
            technical_depth="business",
            jargon_level="business",
            formality="formal",
            focus_areas=["business_outcomes", "strategy", "risk", "investment", "customer_impact", "roi"],
            avoid_patterns=["implementation_details", "technical_jargon", "low_level_decisions"],
        ),
        "behavioral_interviewer": StyleRules(
            verbosity="balanced",
            technical_depth="high-level",
            jargon_level="minimal",
            formality="professional",
            focus_areas=["leadership", "conflict", "failure", "growth", "collaboration", "influence"],
            avoid_patterns=["technical_deep_dive", "hypothetical_only"],
        ),
        "system_design_interviewer": StyleRules(
            verbosity="detailed",
            technical_depth="architecture",
            jargon_level="full",
            formality="professional",
            focus_areas=["scalability", "reliability", "consistency", "latency", "cost", "operability"],
            avoid_patterns=["coding_focus", "single_technology_focus"],
        ),
        "skeptical_interviewer": StyleRules(
            verbosity="balanced",
            technical_depth="mixed",
            jargon_level="moderate",
            formality="professional",
            focus_areas=["evidence", "specifics", "ownership", "validation", "lessons_learned"],
            avoid_patterns=["vague_claims", "hand_waving", "overconfidence"],
        ),
        "collaborative_interviewer": StyleRules(
            verbosity="balanced",
            technical_depth="mixed",
            jargon_level="moderate",
            formality="casual",
            focus_areas=["thinking_process", "collaboration", "learning", "team_approach"],
            avoid_patterns=["competitive_tone", "rigid_answers"],
        ),
    }

    # Persona adjustments
    PERSONA_ADJUSTMENTS = {
        "junior": {
            "verbosity": "balanced",
            "technical_depth": "implementation",
            "humility_markers": ["I was learning", "My mentor suggested", "The team helped me"],
            "ownership_language": "contributed to",
        },
        "mid": {
            "verbosity": "balanced",
            "technical_depth": "implementation",
            "humility_markers": ["We decided", "The approach we took"],
            "ownership_language": "led the implementation of",
        },
        "senior": {
            "verbosity": "concise",
            "technical_depth": "architecture",
            "humility_markers": ["Looking back", "In hindsight", "We could have"],
            "ownership_language": "designed and led",
        },
        "staff": {
            "verbosity": "concise",
            "technical_depth": "architecture",
            "humility_markers": ["The team executed", "Credit goes to"],
            "ownership_language": "architected the strategy for",
        },
        "principal": {
            "verbosity": "concise",
            "technical_depth": "architecture",
            "humility_markers": ["Organizationally", "Across teams"],
            "ownership_language": "drove the organizational strategy for",
        },
        "manager": {
            "verbosity": "balanced",
            "technical_depth": "mixed",
            "humility_markers": ["My team", "We collectively"],
            "ownership_language": "managed the delivery of",
        },
        "director": {
            "verbosity": "concise",
            "technical_depth": "business",
            "humility_markers": ["The organization", "Cross-functionally"],
            "ownership_language": "directed the strategy for",
        },
    }

    def __init__(self, persona: ProfessionalPersona):
        self.persona = persona

    def apply_style(self, text: str, context) -> str:
        """Apply style adaptations to response text."""
        # Get interviewer style
        interviewer_type = getattr(context, 'interviewer_type', 'technical_specialist')
        base_style = self.INTERVIEWER_STYLES.get(interviewer_type, self.INTERVIEWER_STYLES["technical_specialist"])

        # Get persona adjustments
        seniority = getattr(self.persona, 'ownership_level', 'mid')
        if seniority in ['system', 'platform', 'organization']:
            seniority_key = 'senior'
        elif seniority == 'feature':
            seniority_key = 'mid'
        elif seniority == 'task':
            seniority_key = 'junior'
        else:
            seniority_key = 'mid'

        persona_adj = self.PERSONA_ADJUSTMENTS.get(seniority_key, self.PERSONA_ADJUSTMENTS["mid"])

        # Apply transformations
        text = self._adjust_verbosity(text, base_style.verbosity, persona_adj["verbosity"])
        text = self._adjust_technical_depth(text, base_style.technical_depth, persona_adj["technical_depth"])
        text = self._adjust_jargon(text, base_style.jargon_level)
        text = self._adjust_formality(text, base_style.formality)
        text = self._apply_ownership_language(text, persona_adj["ownership_language"])
        text = self._apply_humility_markers(text, persona_adj["humility_markers"], context)
        text = self._remove_avoided_patterns(text, base_style.avoid_patterns)

        return text

    def _adjust_verbosity(self, text: str, base_verbosity: str, persona_verbosity: str) -> str:
        """Adjust verbosity based on style."""
        # Determine effective verbosity (more concise wins)
        verbosity_priority = {"concise": 0, "balanced": 1, "detailed": 2}
        base_level = verbosity_priority.get(base_verbosity, 1)
        persona_level = verbosity_priority.get(persona_verbosity, 1)
        effective_level = min(base_level, persona_level)

        if effective_level == 0:  # concise
            # Remove filler phrases
            filler = [
                r'\b(basically|actually|essentially|fundamentally)\b',
                r'\b(in terms of|with respect to|regarding)\b',
                r'\b(the fact that|the reality that)\b',
            ]
            for pattern in filler:
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        elif effective_level == 2:  # detailed
            # Ensure enough detail (handled by content generation)
            pass

        return text

    def _adjust_technical_depth(self, text: str, base_depth: str, persona_depth: str) -> str:
        """Adjust technical depth."""
        depth_priority = {"high-level": 0, "mixed": 1, "business": 0, "implementation": 2, "architecture": 3}
        base_level = depth_priority.get(base_depth, 1)
        persona_level = depth_priority.get(persona_depth, 1)
        # Use the deeper of the two
        effective_level = max(base_level, persona_level)

        # This is primarily handled during content generation
        # Here we just ensure we don't over-explain for high-level audiences
        if effective_level <= 1 and base_depth == "high-level":
            # Simplify technical explanations
            text = re.sub(r'\b(implementation detail|under the hood|internally)\b.*?\.', '', text, flags=re.IGNORECASE)

        return text

    def _adjust_jargon(self, text: str, jargon_level: str) -> str:
        """Adjust jargon level."""
        if jargon_level == "minimal":
            # Replace technical terms with simpler equivalents
            replacements = {
                r'\b(microservices?)\b': 'services',
                r'\b(containerization?)\b': 'containerized deployment',
                r'\b(orchestration)\b': 'management',
                r'\b(idempotenc(y|ies))\b': 'safe retry behavior',
                r'\b(observabilit(y|ies))\b': 'monitoring and visibility',
                r'\b(latency)\b': 'response time',
                r'\b(throughput)\b': 'request volume',
                r'\b(control plane)\b': 'management layer',
                r'\b(data plane)\b': 'processing layer',
            }
            for pattern, replacement in replacements.items():
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        return text

    def _adjust_formality(self, text: str, formality: str) -> str:
        """Adjust formality level."""
        if formality == "casual":
            # More contractions, simpler language
            text = text.replace("cannot", "can't").replace("will not", "won't").replace("do not", "don't")
        elif formality == "formal":
            # Fewer contractions, more precise language
            text = text.replace("can't", "cannot").replace("won't", "will not").replace("don't", "do not")

        return text

    def _apply_ownership_language(self, text: str, ownership: str) -> str:
        """Apply appropriate ownership language."""
        # This is primarily handled during content generation
        # Just ensure consistency
        if ownership == "contributed to":
            text = text.replace("I built", "I contributed to building")
            text = text.replace("I designed", "I helped design")
        elif ownership in ["designed and led", "architected the strategy for", "drove the organizational strategy for"]:
            text = text.replace("we did", "I led the team to")
            text = text.replace("the team did", "my team executed")

        return text

    def _apply_humility_markers(self, text: str, markers: list, context) -> str:
        """Apply humility markers appropriately."""
        # Add occasional humility marker for senior roles
        if markers and context.followup_depth == 0 and hash(context.question) % 3 == 0:
            marker = markers[hash(context.question) % len(markers)]
            # Insert naturally
            if "looking back" in marker.lower() or "in hindsight" in marker.lower():
                text = f"{marker}, {text[0].lower() + text[1:]}"

        return text

    def _remove_avoided_patterns(self, text: str, avoid_patterns: list) -> str:
        """Remove avoided patterns for interviewer type."""
        pattern_map = {
            "deep_technical_jargon": [
                r'\b(kubernetes|k8s|istio|envoy|ebpf|grpc|protobuf)\b',
            ],
            "implementation_details": [
                r'\b(configuration|parameter|setting|flag)\b.*?\d+',
            ],
            "architecture_deep_dive": [
                r'\b(consistency model|cap theorem|paxos|raft)\b',
            ],
            "pure_coding": [
                r'\b(leetcode|algorithm|complexity|big.o)\b',
            ],
            "excessive_theory": [
                r'\b(theoretically|in theory|academically)\b',
            ],
            "high_level_only": [
                r'\b(without getting into details|at a high level)\b',
            ],
            "business_fluff": [
                r'\b(synergy|paradigm|leverage|holistic)\b',
            ],
            "textbook_answers": [
                r'\b(textbook|standard approach|by the book)\b',
            ],
            "rigid_thinking": [
                r'\b(always|never|must|only way)\b',
            ],
            "single_service_focus": [
                r'\b(this service|my service)\b(?!.*other|.*team|.*depend)',
            ],
            "ignoring_operations": [
                r'\b(deploy|operat|monitor|alert|on.call)\b.*?(not|didn\'t|wasn\'t)',
            ],
            "single_technology_focus": [
                r'\b(only|exclusively|just)\s+\w+\s+(for|to)\b',
            ],
            "vague_claims": [
                r'\b(improved|optimized|enhanced|better|faster)\b(?!.*by.*%|.*from.*to|.*\d)',
            ],
            "hand_waving": [
                r'\b(somehow|magically|automatically|transparent)\b',
            ],
            "overconfidence": [
                r'\b(guaranteed|perfect|flawless|zero issues)\b',
            ],
            "hypothetical_only": [
                r'\b(i would|i\'d)\b(?!.*have done|.*did)',
            ],
            "competitive_tone": [
                r'\b(i beat|i won|better than|superior to)\b',
            ],
            "rigid_answers": [
                r'\b(the answer is|the solution is|the only way)\b',
            ],
        }

        for pattern_name in avoid_patterns:
            patterns = pattern_map.get(pattern_name, [])
            for pattern in patterns:
                text = re.sub(pattern, '[REDACTED]', text, flags=re.IGNORECASE)

        # Clean up any redaction artifacts
        text = re.sub(r'\s+\[REDACTED\]\s*', ' ', text)
        text = re.sub(r'\s+', ' ', text)

        return text


import re
from dataclasses import field