"""
Business Engine - Handles business reasoning and decision-making.
"""

from dataclasses import dataclass, field
from typing import Optional
from ..experience_enrichment.scenario_generator import Scenario
from ..experience_enrichment.project_modeler import ProjectModel
from ..candidate_intelligence.competency_mapper import CompetencyProfile
from ..candidate_intelligence.persona_builder import ProfessionalPersona


@dataclass
class BusinessReasoning:
    business_context: str = ""
    problem_statement: str = ""
    objectives: list = field(default_factory=list)
    stakeholders: list = field(default_factory=list)
    constraints: list = field(default_factory=list)
    options_considered: list = field(default_factory=list)
    decision_rationale: str = ""
    financial_impact: dict = field(default_factory=dict)
    risk_assessment: list = field(default_factory=list)
    success_metrics: list = field(default_factory=list)
    implementation_plan: list = field(default_factory=list)
    communication_strategy: str = ""


class BusinessEngine:
    """Reasons about business decisions and strategy."""

    def __init__(self):
        pass

    def reason_about_business(self, scenario: Scenario, model: ProjectModel,
                               question: str, competencies: CompetencyProfile,
                               persona: ProfessionalPersona) -> BusinessReasoning:
        """Generate business reasoning for a question."""
        reasoning = BusinessReasoning()

        # Business context
        reasoning.business_context = self._build_business_context(scenario, model)

        # Problem statement
        reasoning.problem_statement = self._identify_problem(scenario, question)

        # Objectives
        reasoning.objectives = self._define_objectives(scenario, model)

        # Stakeholders
        reasoning.stakeholders = self._identify_stakeholders(scenario, model)

        # Constraints
        reasoning.constraints = self._identify_constraints(scenario, model)

        # Options
        reasoning.options_considered = self._generate_options(scenario, question)

        # Decision rationale
        reasoning.decision_rationale = self._determine_rationale(scenario, competencies, persona)

        # Financial impact
        reasoning.financial_impact = self._estimate_financial_impact(scenario, model)

        # Risk assessment
        reasoning.risk_assessment = self._assess_risks(scenario, model)

        # Success metrics
        reasoning.success_metrics = self._define_success_metrics(scenario, model)

        # Implementation plan
        reasoning.implementation_plan = self._create_implementation_plan(scenario, model)

        # Communication strategy
        reasoning.communication_strategy = self._determine_communication(persona)

        return reasoning

    def _build_business_context(self, scenario: Scenario, model: ProjectModel) -> str:
        """Build business context."""
        industry = scenario.employer if scenario.employer else "our organization"
        return (f"At {industry}, operating in the {scenario.technical_environment.get('industry', 'technology')} space, "
                f"we were focused on {scenario.business_objective.lower()}. "
                f"The project scope was {scenario.scope.lower()}.")

    def _identify_problem(self, scenario: Scenario, question: str) -> str:
        """Identify the business problem."""
        q_lower = question.lower()

        if "priorit" in q_lower:
            return "Competing priorities with limited engineering capacity"
        if "roi" in q_lower or "investment" in q_lower or "budget" in q_lower:
            return "Justifying technical investment to leadership"
        if "customer" in q_lower or "user" in q_lower:
            return "Meeting customer needs while managing technical constraints"
        if "strateg" in q_lower:
            return "Aligning technical strategy with business goals"
        if "build vs buy" in q_lower or "vendor" in q_lower:
            return "Build vs buy decision for critical capability"
        if "technical debt" in q_lower or "debt" in q_lower:
            return "Balancing feature delivery with technical debt reduction"

        return scenario.business_objective

    def _define_objectives(self, scenario: Scenario, model: ProjectModel) -> list:
        """Define business objectives."""
        objectives = [
            scenario.business_objective,
        ]

        # Add from outcomes
        outcomes = scenario.outcomes
        if outcomes.get('business_impact'):
            objectives.append(outcomes['business_impact'])

        # Add standard objectives
        objectives.extend([
            "Deliver customer value incrementally",
            "Maintain system reliability and performance",
            "Enable future scalability",
            "Optimize cost efficiency",
        ])

        return objectives

    def _identify_stakeholders(self, scenario: Scenario, model: ProjectModel) -> list:
        """Identify key stakeholders."""
        stakeholders = [
            "Engineering Team: implementation and delivery",
            "Product Management: requirements and prioritization",
            "Engineering Leadership: resource allocation and strategy",
            "Customers/Users: value delivery and feedback",
        ]

        # Add based on scenario
        if scenario.type == 'migration':
            stakeholders.extend([
                "Operations/SRE: migration execution and monitoring",
                "Security/Compliance: data integrity and regulatory",
                "Finance: cost tracking and optimization",
            ])
        if scenario.type == 'incident':
            stakeholders.extend([
                "Customer Support: user communication",
                "Executive Leadership: business impact visibility",
                "Legal/Compliance: if data breach involved",
            ])

        return stakeholders

    def _identify_constraints(self, scenario: Scenario, model: ProjectModel) -> list:
        """Identify business constraints."""
        constraints = [
            f"Team capacity: {model.team.get('total_size', 5)} engineers",
            f"Timeline: {sum(p.get('duration_weeks', 0) for p in model.timeline)} weeks",
            "Budget: allocated project budget",
            "Compliance: industry regulations",
            "Technical: existing system integration",
            "Organizational: change management capacity",
        ]

        return constraints

    def _generate_options(self, scenario: Scenario, question: str) -> list:
        """Generate options considered."""
        options = scenario.architecture.get('key_decisions', [])

        option_list = []
        for opt in options:
            option_list.append({
                "option": opt.get('decision', ''),
                "pros": opt.get('rationale', ''),
                "cons": opt.get('tradeoffs', []),
            })

        if not option_list:
            option_list = [
                {
                    "option": "Proposed approach",
                    "pros": "Meets requirements, team expertise",
                    "cons": "Implementation effort",
                },
                {
                    "option": "Alternative 1: Buy/Managed service",
                    "pros": "Faster time to market, less ops burden",
                    "cons": "Vendor lock-in, customization limits",
                },
                {
                    "option": "Alternative 2: Minimal viable approach",
                    "pros": "Lower cost, faster delivery",
                    "cons": "Technical debt, limited scalability",
                },
            ]

        return option_list

    def _determine_rationale(self, scenario: Scenario, competencies: CompetencyProfile,
                              persona: ProfessionalPersona) -> str:
        """Determine decision rationale."""
        rationales = {
            "collaborative": "We aligned the team around this approach through RFC process and consensus building.",
            "direct": "The data clearly supported this approach; I made the call to unblock the team.",
            "analytical": "We ran a cost-benefit analysis and prototype validation; results favored this path.",
            "narrative": "The vision for where we needed to go made this the obvious strategic choice.",
            "executive": "This aligns with our organizational priorities and delivers the highest ROI.",
            "technical-deep": "Technical evaluation showed this approach best meets our scale and reliability requirements.",
        }
        return rationales.get(persona.communication_style, rationales["balanced"])

    def _estimate_financial_impact(self, scenario: Scenario, model: ProjectModel) -> dict:
        """Estimate financial impact."""
        cost_model = model.numerical_model.get('cost', {})

        return {
            "development_cost": f"${cost_model.get('monthly_usd', 10000) * 3:,.0f} (3 months)",
            "operational_cost_monthly": f"${cost_model.get('monthly_usd', 10000):,.0f}/month",
            "cost_savings": scenario.outcomes.get('cost', {}).get('optimization_savings_pct', 0),
            "revenue_impact": "Enabled $2M ARR new revenue stream" if scenario.type == 'project' else "Protected existing revenue",
            "roi_timeline": "6-12 months",
            "cost_per_request": f"${cost_model.get('cost_per_request', 0.00001):.6f}",
        }

    def _assess_risks(self, scenario: Scenario, model: ProjectModel) -> list:
        """Assess business risks."""
        risks = [
            {
                "risk": "Delivery delay",
                "likelihood": "Medium",
                "impact": "High",
                "mitigation": "Incremental delivery, scope flexibility",
            },
            {
                "risk": "Cost overrun",
                "likelihood": "Low",
                "impact": "Medium",
                "mitigation": "Monthly budget review, reserved instances",
            },
            {
                "risk": "Technical failure in production",
                "likelihood": "Low",
                "impact": "High",
                "mitigation": "Canary deployment, automated rollback, chaos testing",
            },
            {
                "risk": "Low adoption",
                "likelihood": "Medium",
                "impact": "Medium",
                "mitigation": "User research, beta program, feedback loops",
            },
            {
                "risk": "Security/compliance gap",
                "likelihood": "Low",
                "impact": "Critical",
                "mitigation": "Security review gates, automated compliance checks",
            },
        ]

        # Add scenario-specific risks
        if scenario.type == 'migration':
            risks.append({
                "risk": "Data loss during migration",
                "likelihood": "Low",
                "impact": "Critical",
                "mitigation": "CDC with reconciliation, dual-write verification",
            })

        return risks

    def _define_success_metrics(self, scenario: Scenario, model: ProjectModel) -> list:
        """Define success metrics."""
        metrics = scenario.outcomes.get('metrics', [])

        success_metrics = [
            "On-time delivery: within 10% of planned timeline",
            "Quality: <0.1% production defect rate",
            "Performance: p99 latency < SLA",
            "Adoption: >80% target users active in 30 days",
            "Cost: within 15% of budget",
        ]

        # Add scenario metrics
        for m in metrics:
            success_metrics.append(m)

        return success_metrics

    def _create_implementation_plan(self, scenario: Scenario, model: ProjectModel) -> list:
        """Create implementation plan."""
        plan = []

        for phase in model.timeline:
            plan.append({
                "phase": phase.get('name', 'Phase'),
                "duration": f"{phase.get('duration_weeks', 0)} weeks",
                "deliverables": phase.get('deliverables', []),
                "owner": scenario.candidate_role,
            })

        return plan

    def _determine_communication(self, persona: ProfessionalPersona) -> str:
        """Determine communication strategy."""
        strategies = {
            "executive": "Executive summary with key metrics, risks, and decisions needed. Monthly steering committee updates.",
            "direct": "Clear, concise updates with decision points highlighted. Weekly sync with stakeholders.",
            "analytical": "Data-driven updates with dashboards and trend analysis. Bi-weekly deep-dive reviews.",
            "narrative": "Story-based progress updates connecting work to customer outcomes. Monthly all-hands demo.",
            "collaborative": "Inclusive updates with team recognition. Regular retrospectives and course corrections.",
            "technical-deep": "Technical deep-dives for engineering stakeholders. Executive summary for leadership.",
            "balanced": "Tailored communication: technical details for engineers, business outcomes for leadership.",
        }
        return strategies.get(persona.communication_style, strategies["balanced"])

    def generate_response(self, reasoning: BusinessReasoning,
                          question: str, persona: ProfessionalPersona,
                          interviewer_type: str) -> str:
        """Generate natural business response."""
        q_lower = question.lower()

        if "priorit" in q_lower:
            return (f"Prioritization framework: {reasoning.objectives[0]}. "
                    f"Constraints: {reasoning.constraints[0]}. "
                    f"We evaluated {len(reasoning.options_considered)} options. "
                    f"Decision: {reasoning.decision_rationale}")

        if "roi" in q_lower or "investment" in q_lower:
            fin = reasoning.financial_impact
            return (f"Investment: {fin['development_cost']}. "
                    f"Ongoing: {fin['operational_cost_monthly']}. "
                    f"Expected ROI: {fin['roi_timeline']}. "
                    f"Revenue impact: {fin['revenue_impact']}.")

        if "risk" in q_lower:
            risk = reasoning.risk_assessment[0]
            return (f"Top risk: {risk['risk']} ({risk['likelihood']} likelihood, {risk['impact']} impact). "
                    f"Mitigation: {risk['mitigation']}. "
                    f"We track {len(reasoning.risk_assessment)} risks total.")

        if "stakeholder" in q_lower or "communicat" in q_lower:
            return (f"Stakeholders: {', '.join(reasoning.stakeholders[:3])}. "
                    f"Communication: {reasoning.communication_strategy}")

        if "metric" in q_lower or "success" in q_lower:
            return (f"Success metrics: {reasoning.success_metrics[0]}, {reasoning.success_metrics[1]}. "
                    f"Also tracking: {reasoning.success_metrics[2]}.")

        if "strateg" in q_lower:
            return (f"Strategy: {reasoning.problem_statement}. "
                    f"Approach: {reasoning.decision_rationale}. "
                    f"Key tradeoff: {reasoning.options_considered[0].get('cons', [''])[0] if reasoning.options_considered else 'resource allocation'}.")

        return (f"Business context: {reasoning.business_context}. "
                f"Problem: {reasoning.problem_statement}. "
                f"Solution: {reasoning.options_considered[0].get('option', 'proposed approach') if reasoning.options_considered else 'proposed approach'}.")