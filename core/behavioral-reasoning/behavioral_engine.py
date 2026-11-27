"""
Behavioral Engine - Handles behavioral interview reasoning with implicit STAR.
"""

from dataclasses import dataclass, field
from typing import Optional
from ..experience_enrichment.scenario_generator import Scenario
from ..experience_enrichment.project_modeler import ProjectModel
from ..candidate_intelligence.persona_builder import ProfessionalPersona
from .story_selector import StorySelector


@dataclass
class BehavioralReasoning:
    situation: str = ""
    task: str = ""
    action: str = ""
    result: str = ""
    ownership: str = "primary"  # sole, primary, shared, advisory
    competencies_demonstrated: list = field(default_factory=list)
    challenges_faced: list = field(default_factory=list)
    lessons_learned: list = field(default_factory=list)
    alternative_approaches: list = field(default_factory=list)
    stakeholder_interactions: list = field(default_factory=list)
    metrics: list = field(default_factory=list)
    reflection: str = ""


class BehavioralEngine:
    """Reasons about behavioral questions using implicit STAR."""

    BEHAVIORAL_CATEGORIES = {
        "leadership": [
            "lead a team", "manage people", "mentor", "hire", "build team",
            "performance review", "promote", "difficult conversation",
        ],
        "conflict": [
            "disagreement", "conflict", "difficult stakeholder", "pushback",
            "compromise", "mediation", "conflicting priorities",
        ],
        "failure": [
            "mistake", "failure", "missed deadline", "bug in production",
            "wrong decision", "project failed", "learned the hard way",
        ],
        "pressure": [
            "tight deadline", "under pressure", "crisis", "incident",
            "last minute", "high stakes", "burnout",
        ],
        "ambiguity": [
            "unclear requirements", "ambiguity", "unknown", "figure it out",
            "no direction", "blank slate", "first time",
        ],
        "influence": [
            "convince", "influence", "persuade", "get buy-in", "sell idea",
            "change mind", "advocate", "champion",
        ],
        "collaboration": [
            "cross-functional", "work with", "partner with", "coordinate",
            "align", "shared goal", "team effort",
        ],
        "innovation": [
            "improve", "innovate", "new approach", "better way", "optimize",
            "automate", "creative solution", "out of the box",
        ],
        "customer": [
            "customer", "client", "user", "stakeholder", "external",
            "feedback", "complaint", "requirement",
        ],
        "growth": [
            "learn", "grow", "develop", "skill", "stretch", "new role",
            "promotion", "career",
        ],
    }

    def __init__(self):
        self.story_selector = StorySelector()

    def reason_about_behavioral(self, scenario: Scenario, model: ProjectModel,
                                 question: str, persona: ProfessionalPersona,
                                 used_stories: list = None) -> BehavioralReasoning:
        """Generate behavioral reasoning for a question."""
        reasoning = BehavioralReasoning()

        # Classify question category
        category = self._classify_question(question)

        # Select appropriate story
        story = self.story_selector.select_story(
            scenario, category, used_stories or [], persona
        )

        # Build STAR components (implicit)
        reasoning.situation = self._build_situation(story, scenario)
        reasoning.task = self._build_task(story, scenario, question)
        reasoning.action = self._build_action(story, scenario, persona)
        reasoning.result = self._build_result(story, scenario)
        reasoning.ownership = story.get('ownership', 'primary')

        # Competencies
        reasoning.competencies_demonstrated = self._identify_competencies(story, category)

        # Challenges
        reasoning.challenges_faced = self._extract_challenges(story, scenario)

        # Lessons
        reasoning.lessons_learned = scenario.outcomes.get('lessons_learned', [])

        # Alternatives
        reasoning.alternative_approaches = self._generate_alternatives(story, scenario)

        # Stakeholders
        reasoning.stakeholder_interactions = self._identify_stakeholders(story, scenario)

        # Metrics
        reasoning.metrics = scenario.outcomes.get('metrics', [])

        # Reflection
        reasoning.reflection = self._generate_reflection(story, scenario, persona)

        return reasoning

    def _classify_question(self, question: str) -> str:
        """Classify behavioral question category."""
        q_lower = question.lower()

        for category, keywords in self.BEHAVIORAL_CATEGORIES.items():
            for kw in keywords:
                if kw in q_lower:
                    return category

        # Default based on question structure
        if "tell me about a time" in q_lower or "give an example" in q_lower:
            return "general"
        if "how do you handle" in q_lower:
            return "pressure"
        if "describe a situation" in q_lower:
            return "general"

        return "general"

    def _build_situation(self, story: dict, scenario: Scenario) -> str:
        """Build situation context."""
        if not story:
            return f"At {scenario.employer}, we were {scenario.business_objective.lower()}."

        situation = story.get('situation', '')
        if situation:
            return situation

        # Build from scenario
        return (f"At {scenario.employer}, during my time as {scenario.candidate_role}, "
                f"we were working on {scenario.business_objective.lower()}. "
                f"The scope was {scenario.scope.lower()}.")

    def _build_task(self, story: dict, scenario: Scenario, question: str) -> str:
        """Build task/responsibility."""
        if not story:
            return "I was responsible for the technical implementation and delivery."

        task = story.get('task', '')
        if task:
            return task

        # Build from scenario and question
        q_lower = question.lower()
        if "lead" in q_lower or "manage" in q_lower:
            return "I needed to lead the technical approach and coordinate across teams."
        if "conflict" in q_lower or "disagree" in q_lower:
            return "I had to navigate a significant disagreement on the technical direction."
        if "fail" in q_lower or "mistake" in q_lower:
            return "I needed to recover from a production issue and prevent recurrence."
        if "pressure" in q_lower or "deadline" in q_lower:
            return "We had a hard deadline with significant technical risk."

        return "I owned the end-to-end delivery of my component."

    def _build_action(self, story: dict, scenario: Scenario, persona: ProfessionalPersona) -> str:
        """Build action taken."""
        if not story:
            actions = [
                "I designed the system architecture and defined API contracts.",
                "I implemented the core service with comprehensive testing.",
                "I coordinated with dependent teams on integration points.",
                "I set up monitoring, alerting, and runbooks for production readiness.",
            ]
            return " ".join(actions)

        action = story.get('action', '')
        if action:
            return action

        # Build from scenario
        contributions = scenario.individual_contributions
        if contributions:
            action_parts = []
            for contrib in contributions[:3]:
                ownership_word = self._ownership_word(contrib.get('ownership', 'primary'))
                action_parts.append(f"{ownership_word} {contrib.get('action', '').lower()}")
            return ". ".join(action_parts) + "."

        return "I took ownership of the technical design and implementation."

    def _build_result(self, story: dict, scenario: Scenario) -> str:
        """Build result/outcome."""
        if not story:
            metrics = scenario.outcomes.get('metrics', [])
            if metrics:
                return f"The result: {metrics[0].lower()}. {scenario.outcomes.get('business_impact', '')}."

        result = story.get('result', '')
        if result:
            return result

        metrics = scenario.outcomes.get('metrics', [])
        if metrics:
            return f"We delivered successfully: {metrics[0].lower()}. {scenario.outcomes.get('business_impact', '')}."

        return "The project delivered on time with the expected outcomes."

    def _identify_competencies(self, story: dict, category: str) -> list:
        """Identify competencies demonstrated."""
        competency_map = {
            "leadership": ["technical leadership", "team coordination", "decision making", "mentoring"],
            "conflict": ["conflict resolution", "stakeholder management", "negotiation", "communication"],
            "failure": ["accountability", "root cause analysis", "learning agility", "process improvement"],
            "pressure": ["prioritization", "calm under pressure", "rapid decision making", "delivery focus"],
            "ambiguity": ["problem structuring", "initiative", "resourcefulness", "clarity seeking"],
            "influence": ["persuasion", "evidence-based argument", "relationship building", "strategic thinking"],
            "collaboration": ["cross-functional coordination", "alignment", "shared ownership", "communication"],
            "innovation": ["creative problem solving", "technical vision", "risk taking", "impact focus"],
            "customer": ["customer empathy", "requirement gathering", "feedback incorporation", "value delivery"],
            "growth": ["self-awareness", "skill development", "adaptability", "career ownership"],
        }
        return competency_map.get(category, ["problem solving", "communication", "technical judgment", "ownership"])

    def _extract_challenges(self, story: dict, scenario: Scenario) -> list:
        """Extract challenges from scenario."""
        challenges = []

        for challenge in scenario.challenges:
            challenges.append({
                "description": challenge.get('description', ''),
                "resolution": challenge.get('resolution', ''),
                "my_role": challenge.get('candidate_involvement', ''),
            })

        return challenges

    def _generate_alternatives(self, story: dict, scenario: Scenario) -> list:
        """Generate alternative approaches considered."""
        alternatives = scenario.architecture.get('key_decisions', [])

        alt_list = []
        for alt in alternatives:
            for a in alt.get('alternatives', []):
                alt_list.append({
                    "approach": a,
                    "why_not_chosen": alt.get('tradeoffs', [''])[0] if alt.get('tradeoffs') else '',
                })

        if not alt_list:
            alt_list = [
                {"approach": "Alternative technical approach", "why_not_chosen": "Higher risk/complexity"},
                {"approach": "Different team structure", "why_not_chosen": "Resource constraints"},
                {"approach": "Buy vs build", "why_not_chosen": "Customization needs"},
            ]

        return alt_list[:3]

    def _identify_stakeholders(self, story: dict, scenario: Scenario) -> list:
        """Identify stakeholder interactions."""
        stakeholders = [
            "Product Manager: requirements and prioritization",
            "Engineering Lead: technical review and approval",
            "Dependent Teams: API contracts and integration testing",
            "DevOps/SRE: deployment, monitoring, on-call",
            "Security: review and compliance",
        ]

        # Filter based on scenario
        if scenario.type == 'incident':
            stakeholders.insert(0, "Incident Commander: coordination and communication")
            stakeholders.append("Customer Support: user impact updates")

        return stakeholders

    def _generate_reflection(self, story: dict, scenario: Scenario, persona: ProfessionalPersona) -> str:
        """Generate reflective closing."""
        lessons = scenario.outcomes.get('lessons_learned', [])

        if lessons:
            return f"Looking back, {lessons[0].lower()}. It shaped how I approach similar situations now."

        reflections = {
            "leadership": "The key insight was that technical leadership is as much about alignment as architecture.",
            "conflict": "I learned that disagreements often stem from different assumptions, not bad intentions.",
            "failure": "That failure taught me that observability isn't optional—it's the difference between hours and minutes to resolution.",
            "pressure": "Under pressure, the best decisions come from clear prioritization, not heroics.",
            "ambiguity": "When things are unclear, the most valuable thing you can do is create clarity for the team.",
            "influence": "Influence comes from demonstrating you've done the work, not from authority.",
            "collaboration": "The best cross-functional work happens when everyone understands the 'why', not just the 'what'.",
            "innovation": "Innovation isn't about new tech—it's about solving the right problem better.",
            "customer": "Customer feedback is the ultimate reality check on technical decisions.",
            "growth": "Growth happens at the edge of your comfort zone.",
        }

        category = self._classify_question("")
        return reflections.get(category, "That experience shaped how I think about engineering leadership.")

    def _ownership_word(self, ownership: str) -> str:
        """Convert ownership level to natural language."""
        mapping = {
            "sole": "I personally",
            "primary": "I led",
            "shared": "I co-led",
            "advisory": "I advised on",
            "validation": "I validated",
        }
        return mapping.get(ownership, "I")

    def generate_response(self, reasoning: BehavioralReasoning,
                          question: str, persona: ProfessionalPersona,
                          interviewer_type: str) -> str:
        """Generate natural behavioral response (implicit STAR)."""
        parts = []

        # Situation + Task (combined naturally)
        if reasoning.situation:
            parts.append(reasoning.situation)

        # Action (the meat)
        if reasoning.action:
            parts.append(reasoning.action)

        # Result
        if reasoning.result:
            parts.append(reasoning.result)

        # Reflection for senior candidates
        if persona.ownership_level in ['system', 'platform', 'organization'] and reasoning.reflection:
            parts.append(reasoning.reflection)

        response = " ".join(parts)

        # Ensure natural flow
        response = response.replace("I needed to I", "I needed to").replace("I led I", "I led")

        return response