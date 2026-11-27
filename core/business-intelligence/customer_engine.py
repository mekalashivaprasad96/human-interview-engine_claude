"""
Customer Engine - Handles customer-facing reasoning and communication.
"""

from dataclasses import dataclass, field
from typing import Optional
from ..candidate_intelligence.persona_builder import ProfessionalPersona
from ..candidate_intelligence.competency_mapper import CompetencyProfile


@dataclass
class CustomerReasoning:
    customer_context: str = ""
    customer_need: str = ""
    pain_points: list = field(default_factory=list)
    proposed_solution: str = ""
    value_proposition: str = ""
    objections: list = field(default_factory=list)
    negotiation_points: list = field(default_factory=list)
    success_criteria: list = field(default_factory=list)
    relationship_strategy: str = ""
    communication_approach: str = ""


class CustomerEngine:
    """Reasons about customer-facing situations."""

    def __init__(self):
        pass

    def reason_about_customer(self, scenario, question: str,
                               persona: ProfessionalPersona,
                               competencies: CompetencyProfile) -> CustomerReasoning:
        """Generate customer-facing reasoning."""
        reasoning = CustomerReasoning()

        # Customer context
        reasoning.customer_context = self._build_customer_context(scenario)

        # Customer need
        reasoning.customer_need = self._identify_need(scenario, question)

        # Pain points
        reasoning.pain_points = self._identify_pain_points(scenario)

        # Proposed solution
        reasoning.proposed_solution = self._propose_solution(scenario, question)

        # Value proposition
        reasoning.value_proposition = self._articulate_value(scenario)

        # Objections
        reasoning.objections = self._anticipate_objections(scenario)

        # Negotiation
        reasoning.negotiation_points = self._identify_negotiation_points(scenario)

        # Success criteria
        reasoning.success_criteria = self._define_success_criteria(scenario)

        # Relationship strategy
        reasoning.relationship_strategy = self._determine_relationship_strategy(persona)

        # Communication
        reasoning.communication_approach = self._determine_communication(persona)

        return reasoning

    def _build_customer_context(self, scenario) -> str:
        """Build customer context."""
        return (f"Working with a {scenario.technical_environment.get('industry', 'enterprise')} customer "
                f"who needed {scenario.business_objective.lower()}. "
                f"They were using {', '.join(scenario.technical_environment.get('dependencies', ['legacy systems'])[:2])}.")

    def _identify_need(self, scenario, question: str) -> str:
        """Identify customer need from question."""
        q_lower = question.lower()

        if "requirement" in q_lower or "need" in q_lower:
            return "Customer needed a scalable, reliable solution for their growing user base"
        if "complaint" in q_lower or "unhappy" in q_lower or "escalation" in q_lower:
            return "Customer experienced repeated outages affecting their operations"
        if "renewal" in q_lower or "retention" in q_lower:
            return "Customer evaluating whether to renew/expand contract"
        if "feature" in q_lower or "request" in q_lower:
            return "Customer requested specific functionality not in current roadmap"
        if "security" in q_lower or "compliance" in q_lower:
            return "Customer needed compliance certification for their industry"

        return "Customer needed to modernize their platform for scale and reliability"

    def _identify_pain_points(self, scenario) -> list:
        """Identify customer pain points."""
        return [
            "Current system couldn't handle peak traffic",
            "Frequent outages during business hours",
            "Long feature delivery cycles (6+ months)",
            "Limited visibility into system health",
            "High operational overhead for their team",
        ]

    def _propose_solution(self, scenario, question: str) -> str:
        """Propose solution to customer."""
        return (f"We proposed a {scenario.architecture.get('pattern', 'microservices')} architecture "
                f"on {scenario.technical_environment.get('infrastructure', 'cloud')} "
                f"with {scenario.technical_environment.get('primary_technologies', ['modern stack'])[0]} "
                f"to address their scale and reliability needs.")

    def _articulate_value(self, scenario) -> str:
        """Articulate value proposition."""
        outcomes = scenario.outcomes
        metrics = outcomes.get('metrics', [])

        value = "Delivers: "
        if metrics:
            value += f"{metrics[0]}, "
        value += f"{outcomes.get('business_impact', 'significant operational improvement')}. "
        value += "Reduces their operational burden and enables faster feature delivery."

        return value

    def _anticipate_objections(self, scenario) -> list:
        """Anticipate customer objections."""
        return [
            "Cost: 'This seems expensive compared to our current spend'",
            "Migration risk: 'How do we move without downtime?'",
            "Lock-in: 'Will we be locked into your platform?'",
            "Timeline: 'Can you deliver in our Q3 deadline?'",
            "Support: 'What does ongoing support look like?'",
        ]

    def _identify_negotiation_points(self, scenario) -> list:
        """Identify negotiation points."""
        return [
            "Phased delivery with milestone payments",
            "Co-funded migration engineering effort",
            "SLA commitments with credits for downtime",
            "Contract flexibility for scaling up/down",
            "Joint roadmap planning sessions quarterly",
        ]

    def _define_success_criteria(self, scenario) -> list:
        """Define success criteria."""
        return [
            "Zero-downtime migration completed",
            "p99 latency < 200ms (from 2s)",
            "Availability > 99.99% (from 99.5%)",
            "Customer team can self-serve 80% of operations",
            "Feature delivery cycle < 2 weeks (from 6 months)",
        ]

    def _determine_relationship_strategy(self, persona: ProfessionalPersona) -> str:
        """Determine relationship strategy."""
        strategies = {
            "collaborative": "Partnership model: joint success metrics, shared roadmap, regular business reviews",
            "direct": "Trusted advisor: candid assessments, clear recommendations, accountable delivery",
            "analytical": "Data-driven: ROI dashboards, benchmark comparisons, measurable outcomes",
            "narrative": "Story-based: customer success stories, vision alignment, executive sponsorship",
            "executive": "Strategic: C-level engagement, multi-year agreements, organizational alignment",
            "technical-deep": "Technical partnership: architecture reviews, joint engineering, knowledge transfer",
        }
        return strategies.get(persona.communication_style, strategies["balanced"])

    def _determine_communication(self, persona: ProfessionalPersona) -> str:
        """Determine communication approach."""
        approaches = {
            "executive": "Executive summaries with business metrics. Monthly steering committee.",
            "direct": "Clear status with risks and decisions needed. Weekly standup.",
            "analytical": "Dashboards with trends. Bi-weekly deep-dive.",
            "narrative": "Customer journey updates. Quarterly business review with story.",
            "collaborative": "Inclusive updates. Regular retrospectives.",
            "technical-deep": "Architecture decision records. Technical syncs.",
        }
        return approaches.get(persona.communication_style, approaches["balanced"])

    def generate_response(self, reasoning: CustomerReasoning,
                          question: str, persona: ProfessionalPersona,
                          interviewer_type: str) -> str:
        """Generate natural customer-facing response."""
        q_lower = question.lower()

        if "unhappy" in q_lower or "complaint" in q_lower or "escalation" in q_lower:
            return (f"Customer was frustrated with {reasoning.pain_points[0].lower()}. "
                    f"We {reasoning.proposed_solution.lower()}. "
                    f"Result: {reasoning.success_criteria[0].lower()}.")

        if "requirement" in q_lower or "need" in q_lower:
            return (f"Customer needed {reasoning.customer_need.lower()}. "
                    f"We proposed {reasoning.proposed_solution.lower()}. "
                    f"Value: {reasoning.value_proposition.lower()}")

        if "objection" in q_lower or "pushback" in q_lower:
            obj = reasoning.objections[0]
            return (f"Main objection: {obj}. "
                    f"We addressed it by {reasoning.negotiation_points[0].lower()}.")

        if "negotiate" in q_lower or "deal" in q_lower:
            return (f"Negotiation points: {reasoning.negotiation_points[0].lower()}. "
                    f"Also {reasoning.negotiation_points[1].lower()}.")

        if "relationship" in q_lower or "partnership" in q_lower:
            return f"Relationship strategy: {reasoning.relationship_strategy}."

        return (f"Customer context: {reasoning.customer_context}. "
                f"Need: {reasoning.customer_need}. "
                f"Solution: {reasoning.proposed_solution}.")