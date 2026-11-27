"""
Story Selector - Selects appropriate stories for behavioral questions.
"""

from dataclasses import dataclass
from typing import Optional
from ..experience_enrichment.scenario_generator import Scenario
from ..candidate_intelligence.persona_builder import ProfessionalPersona


@dataclass
class StoryCandidate:
    scenario: Scenario
    relevance_score: float
    category_match: bool
    ownership_clarity: float
    metrics_strength: float
    recency: float
    diversity_bonus: float


class StorySelector:
    """Selects the best story for a behavioral question."""

    def __init__(self):
        pass

    def select_story(self, scenario: Scenario, category: str,
                      used_stories: list, persona: ProfessionalPersona) -> Optional[Scenario]:
        """Select the most appropriate story for a behavioral question."""
        # In a full implementation, this would search a story bank
        # For now, return the scenario if it matches, or create a suitable one

        candidates = self._generate_candidates(scenario, category)

        if not candidates:
            return scenario  # Fallback

        # Score candidates
        scored = []
        for candidate in candidates:
            score = self._score_candidate(candidate, category, used_stories, persona)
            scored.append((score, candidate))

        # Sort by score
        scored.sort(key=lambda x: x[0], reverse=True)

        # Return best candidate (with some randomization for variety)
        import random
        top_n = min(3, len(scored))
        return random.choice(scored[:top_n])[1]

    def _generate_candidates(self, scenario: Scenario, category: str) -> list[Scenario]:
        """Generate candidate stories from scenario bank."""
        # In production, this would query the experience story bank
        # For now, return the scenario with variations
        candidates = [scenario]

        # Add variations based on category
        if category in ['leadership', 'conflict', 'influence']:
            # These work well with project scenarios
            pass
        elif category in ['failure', 'pressure']:
            # These work well with incident scenarios
            pass
        elif category in ['growth', 'ambiguity']:
            # These work well with migration/optimization
            pass

        return candidates

    def _score_candidate(self, candidate: Scenario, category: str,
                          used_stories: list, persona: ProfessionalPersona) -> float:
        """Score a candidate story."""
        score = 0.5  # Base score

        # Category match
        category_match = self._category_matches(candidate, category)
        if category_match:
            score += 0.3

        # Ownership clarity
        ownership = self._get_ownership_clarity(candidate)
        score += ownership * 0.2

        # Metrics strength
        metrics = self._get_metrics_strength(candidate)
        score += metrics * 0.15

        # Recency (more recent = better)
        recency = self._get_recency_score(candidate)
        score += recency * 0.1

        # Diversity bonus (not used recently)
        diversity = self._get_diversity_bonus(candidate, used_stories)
        score += diversity * 0.15

        # Persona alignment
        alignment = self._get_persona_alignment(candidate, persona)
        score += alignment * 0.1

        return min(score, 1.0)

    def _category_matches(self, scenario: Scenario, category: str) -> bool:
        """Check if scenario matches behavioral category."""
        scenario_type = scenario.type

        category_mapping = {
            "leadership": ["project", "migration", "optimization"],
            "conflict": ["project", "incident", "migration"],
            "failure": ["incident", "migration"],
            "pressure": ["incident", "project"],
            "ambiguity": ["migration", "optimization", "project"],
            "influence": ["project", "migration", "optimization"],
            "collaboration": ["project", "migration"],
            "innovation": ["optimization", "project"],
            "customer": ["project", "incident"],
            "growth": ["project", "migration", "optimization"],
        }

        matching_types = category_mapping.get(category, ["project", "incident", "migration"])
        return scenario_type in matching_types

    def _get_ownership_clarity(self, scenario: Scenario) -> float:
        """Get ownership clarity score."""
        role = scenario.candidate_role.lower()

        if any(kw in role for kw in ['lead', 'architect', 'owner', 'principal']):
            return 1.0
        elif any(kw in role for kw in ['senior', 'primary', 'feature lead']):
            return 0.8
        elif any(kw in role for kw in ['engineer', 'implement', 'contributing']):
            return 0.6
        return 0.4

    def _get_metrics_strength(self, scenario: Scenario) -> float:
        """Get metrics strength score."""
        metrics = scenario.outcomes.get('metrics', [])

        if not metrics:
            return 0.2

        # Check for quantitative metrics
        quantitative = sum(1 for m in metrics if any(c.isdigit() for c in m))
        if quantitative >= 2:
            return 1.0
        elif quantitative >= 1:
            return 0.7
        return 0.4

    def _get_recency_score(self, scenario: Scenario) -> float:
        """Get recency score based on period."""
        # Parse end date
        import re
        period = scenario.period
        year_match = re.search(r'(20\d{2})', period)
        if year_match:
            end_year = int(year_match.group(1))
            current_year = 2025
            years_ago = current_year - end_year
            if years_ago <= 1:
                return 1.0
            elif years_ago <= 3:
                return 0.8
            elif years_ago <= 5:
                return 0.6
            return 0.4
        return 0.5

    def _get_diversity_bonus(self, scenario: Scenario, used_stories: list) -> float:
        """Get diversity bonus for not reusing stories."""
        scenario_id = scenario.id

        if scenario_id in used_stories:
            return 0.0  # Penalty for reuse

        # Bonus for different employer
        used_employers = set()
        # In production, would check used_stories for employers
        # For now, assume some diversity
        return 0.1

    def _get_persona_alignment(self, scenario: Scenario, persona: ProfessionalPersona) -> float:
        """Get alignment with candidate persona."""
        # Senior candidates should use senior-appropriate stories
        if persona.ownership_level in ['system', 'platform', 'organization']:
            if scenario.candidate_role and any(kw in scenario.candidate_role.lower()
                                                for kw in ['lead', 'architect', 'principal', 'director']):
                return 1.0
            return 0.6

        # Junior candidates should use implementation stories
        if persona.ownership_level in ['task', 'feature']:
            if scenario.candidate_role and any(kw in scenario.candidate_role.lower()
                                                for kw in ['engineer', 'implement', 'contributing']):
                return 1.0
            return 0.7

        return 0.8

    def get_story_summary(self, scenario: Scenario) -> dict:
        """Get a summary of a story for reference."""
        return {
            "id": scenario.id,
            "title": scenario.title,
            "type": scenario.type,
            "employer": scenario.employer,
            "period": scenario.period,
            "role": scenario.candidate_role,
            "ownership": self._get_ownership_clarity(scenario),
            "key_metrics": scenario.outcomes.get('metrics', [])[:2],
            "challenges": len(scenario.challenges),
            "followup_resilience": scenario.followup_resilience,
        }