"""
Persona Builder - Constructs coherent professional persona from candidate profile.
"""

from dataclasses import dataclass, field
from typing import Optional
from .career_chronology import CareerChronology
from .competency_mapper import CompetencyProfile


@dataclass
class ProfessionalPersona:
    communication_style: str = "balanced"
    technical_confidence: str = "solid"
    professional_maturity: str = "established"
    problem_solving_approach: str = "systematic"
    decision_making: str = "data-driven"
    ownership_level: str = "feature"
    business_awareness: str = "team-aware"
    humility_level: str = "appropriate"
    preferred_detail_level: str = "balanced"
    signature_phrases: list = field(default_factory=list)
    avoid_phrases: list = field(default_factory=list)
    sentence_variance: str = "medium"


class PersonaBuilder:
    """Builds professional persona from career data and competencies."""

    STYLE_BY_SENIORITY = {
        'junior': {
            'communication_style': 'collaborative',
            'technical_confidence': 'developing',
            'professional_maturity': 'early-career',
            'problem_solving_approach': 'systematic',
            'decision_making': 'consensus-seeking',
            'ownership_level': 'task',
            'business_awareness': 'task-focused',
            'humility_level': 'high',
            'preferred_detail_level': 'high-level',
        },
        'mid': {
            'communication_style': 'balanced',
            'technical_confidence': 'solid',
            'professional_maturity': 'established',
            'problem_solving_approach': 'pragmatic',
            'decision_making': 'data-driven',
            'ownership_level': 'feature',
            'business_awareness': 'team-aware',
            'humility_level': 'appropriate',
            'preferred_detail_level': 'balanced',
        },
        'senior': {
            'communication_style': 'direct',
            'technical_confidence': 'high',
            'professional_maturity': 'seasoned',
            'problem_solving_approach': 'pragmatic',
            'decision_making': 'experience-guided',
            'ownership_level': 'system',
            'business_awareness': 'org-aware',
            'humility_level': 'appropriate',
            'preferred_detail_level': 'deep-technical',
        },
        'staff': {
            'communication_style': 'analytical',
            'technical_confidence': 'expert',
            'professional_maturity': 'seasoned',
            'problem_solving_approach': 'systematic',
            'decision_making': 'data-driven',
            'ownership_level': 'platform',
            'business_awareness': 'org-aware',
            'humility_level': 'appropriate',
            'preferred_detail_level': 'deep-technical',
        },
        'principal': {
            'communication_style': 'executive',
            'technical_confidence': 'expert',
            'professional_maturity': 'veteran',
            'problem_solving_approach': 'innovative',
            'decision_making': 'decisive',
            'ownership_level': 'organization',
            'business_awareness': 'strategic',
            'humility_level': 'appropriate',
            'preferred_detail_level': 'deep-technical',
        },
        'manager': {
            'communication_style': 'collaborative',
            'technical_confidence': 'high',
            'professional_maturity': 'seasoned',
            'problem_solving_approach': 'risk-aware',
            'decision_making': 'consensus-seeking',
            'ownership_level': 'system',
            'business_awareness': 'org-aware',
            'humility_level': 'appropriate',
            'preferred_detail_level': 'balanced',
        },
        'director': {
            'communication_style': 'executive',
            'technical_confidence': 'high',
            'professional_maturity': 'veteran',
            'problem_solving_approach': 'strategic',
            'decision_making': 'decisive',
            'ownership_level': 'organization',
            'business_awareness': 'strategic',
            'humility_level': 'appropriate',
            'preferred_detail_level': 'high-level',
        },
        'vp': {
            'communication_style': 'executive',
            'technical_confidence': 'expert',
            'professional_maturity': 'veteran',
            'problem_solving_approach': 'strategic',
            'decision_making': 'decisive',
            'ownership_level': 'organization',
            'business_awareness': 'strategic',
            'humility_level': 'appropriate',
            'preferred_detail_level': 'high-level',
        },
    }

    STYLE_BY_ROLE_TYPE = {
        'engineering': {
            'communication_style': 'technical-deep',
            'problem_solving_approach': 'systematic',
        },
        'architecture': {
            'communication_style': 'analytical',
            'problem_solving_approach': 'systematic',
            'preferred_detail_level': 'deep-technical',
        },
        'management': {
            'communication_style': 'collaborative',
            'problem_solving_approach': 'risk-aware',
            'decision_making': 'consensus-seeking',
        },
        'consulting': {
            'communication_style': 'narrative',
            'problem_solving_approach': 'customer-first',
        },
        'sales-engineering': {
            'communication_style': 'narrative',
            'business_awareness': 'strategic',
        },
        'product': {
            'communication_style': 'direct',
            'problem_solving_approach': 'customer-first',
            'business_awareness': 'strategic',
        },
    }

    def build(self, chronology: CareerChronology, competencies: CompetencyProfile,
              current_level: Optional[str] = None) -> ProfessionalPersona:
        """Build professional persona from career data."""
        # Determine primary level
        level = current_level or chronology.current_level

        # Get base style from seniority
        base_style = self.STYLE_BY_SENIORITY.get(level, self.STYLE_BY_SENIORITY['mid']).copy()

        # Adjust for role type
        primary_role = self._get_primary_role_type(chronology)
        role_adjustments = self.STYLE_BY_ROLE_TYPE.get(primary_role, {})
        base_style.update(role_adjustments)

        # Adjust for competencies
        base_style = self._adjust_for_competencies(base_style, competencies)

        # Adjust for trajectory
        base_style = self._adjust_for_trajectory(base_style, chronology)

        # Generate signature and avoid phrases
        signature_phrases = self._generate_signature_phrases(base_style, competencies)
        avoid_phrases = self._generate_avoid_phrases(base_style)

        # Create persona
        persona = ProfessionalPersona(
            communication_style=base_style['communication_style'],
            technical_confidence=base_style['technical_confidence'],
            professional_maturity=base_style['professional_maturity'],
            problem_solving_approach=base_style['problem_solving_approach'],
            decision_making=base_style['decision_making'],
            ownership_level=base_style['ownership_level'],
            business_awareness=base_style['business_awareness'],
            humility_level=base_style['humility_level'],
            preferred_detail_level=base_style['preferred_detail_level'],
            signature_phrases=signature_phrases,
            avoid_phrases=avoid_phrases,
            sentence_variance='high' if level in ['senior', 'staff', 'principal'] else 'medium'
        )

        return persona

    def _get_primary_role_type(self, chronology: CareerChronology) -> str:
        """Determine primary role type from career."""
        if not chronology.entries:
            return 'engineering'

        role_counts = {}
        for entry in chronology.entries:
            role_counts[entry.role_type] = role_counts.get(entry.role_type, 0) + entry.duration_months

        return max(role_counts, key=role_counts.get)

    def _adjust_for_competencies(self, style: dict, competencies: CompetencyProfile) -> dict:
        """Adjust persona based on competencies."""
        # Technical breadth -> more analytical
        tech_domains = len(competencies.technical.get('domains', []))
        if tech_domains >= 5:
            style['communication_style'] = 'analytical'
            style['problem_solving_approach'] = 'systematic'

        # Customer facing -> more narrative
        if competencies.business.get('customer_facing'):
            style['communication_style'] = 'narrative'

        # Strategic planning -> executive style
        if competencies.business.get('strategic_planning'):
            style['business_awareness'] = 'strategic'
            style['communication_style'] = 'executive'

        # People management -> collaborative
        if competencies.leadership.get('people_management'):
            style['decision_making'] = 'consensus-seeking'
            style['communication_style'] = 'collaborative'

        return style

    def _adjust_for_trajectory(self, style: dict, chronology: CareerChronology) -> dict:
        """Adjust persona based on career trajectory."""
        if chronology.trajectory == 'accelerated':
            style['technical_confidence'] = 'high'
            style['professional_maturity'] = 'established' if style['professional_maturity'] == 'early-career' else style['professional_maturity']
        elif chronology.trajectory == 'lateral':
            style['problem_solving_approach'] = 'pragmatic'
            style['business_awareness'] = 'org-aware'

        return style

    def _generate_signature_phrases(self, style: dict, competencies: CompetencyProfile) -> list:
        """Generate characteristic phrases for this persona."""
        phrases = []

        # By communication style
        style_phrases = {
            'direct': ["Here's the thing:", "Bottom line:", "Directly:", "Simply put:"],
            'analytical': ["Breaking it down:", "The key factors are:", "Looking at the data:", "From first principles:"],
            'narrative': ["Let me give you an example:", "Here's what happened:", "The context was:", "Walking through it:"],
            'collaborative': ["From the team's perspective:", "We approached it by:", "The consensus was:", "Working together:"],
            'executive': ["Strategically:", "The business impact:", "At the organizational level:", "Key takeaway:"],
            'technical-deep': ["Implementation-wise:", "Under the hood:", "At the system level:", "Technically:"],
            'balanced': ["In practice:", "What worked was:", "The approach was:", "Here's how it worked:"],
        }

        phrases.extend(style_phrases.get(style['communication_style'], style_phrases['balanced']))

        # By technical confidence
        if style['technical_confidence'] in ['high', 'expert']:
            phrases.append("I've seen this pattern before")

        # By ownership
        if style['ownership_level'] in ['system', 'platform', 'organization']:
            phrases.append("End-to-end ownership")

        return phrases[:5]  # Limit to top 5

    def _generate_avoid_phrases(self, style: dict) -> list:
        """Generate phrases this persona should avoid."""
        avoid = [
            "That's a great question",
            "Absolutely",
            "In my previous role",
            "That's how I approach these situations",
            "As an AI language model",
            "Based on the resume you uploaded",
        ]

        # Add style-specific avoids
        if style['communication_style'] == 'direct':
            avoid.extend(["I think maybe", "Perhaps we could", "It might be worth considering"])
        elif style['communication_style'] == 'executive':
            avoid.extend(["Technically speaking", "In the weeds", "Implementation detail"])

        return avoid