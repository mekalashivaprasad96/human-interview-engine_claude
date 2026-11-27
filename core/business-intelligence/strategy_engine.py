"""
Strategy Engine - Handles strategic reasoning and executive-level thinking.
"""

from dataclasses import dataclass, field
from typing import Optional
from ..candidate_intelligence.persona_builder import ProfessionalPersona
from ..candidate_intelligence.competency_mapper import CompetencyProfile
from ..experience_enrichment.scenario_generator import Scenario
from ..experience_enrichment.project_modeler import ProjectModel


@dataclass
class StrategyReasoning:
    strategic_context: str = ""
    vision: str = ""
    strategic_objectives: list = field(default_factory=list)
    market_analysis: dict = field(default_factory=dict)
    competitive_position: str = ""
    investment_thesis: str = ""
    resource_allocation: dict = field(default_factory=dict)
    risk_mitigation: list = field(default_factory=list)
    success_metrics: list = field(default_factory=list)
    timeline: list = field(default_factory=list)
    governance: str = ""
    communication_plan: str = ""


class StrategyEngine:
    """Reasons about strategy and executive-level decisions."""

    def __init__(self):
        pass

    def reason_about_strategy(self, scenario: Scenario, model: ProjectModel,
                               question: str, competencies: CompetencyProfile,
                               persona: ProfessionalPersona) -> StrategyReasoning:
        """Generate strategic reasoning."""
        reasoning = StrategyReasoning()

        # Strategic context
        reasoning.strategic_context = self._build_strategic_context(scenario, model)

        # Vision
        reasoning.vision = self._articulate_vision(scenario, model)

        # Strategic objectives
        reasoning.strategic_objectives = self._define_strategic_objectives(scenario, model)

        # Market analysis
        reasoning.market_analysis = self._analyze_market(scenario)

        # Competitive position
        reasoning.competitive_position = self._assess_competitive_position(scenario)

        # Investment thesis
        reasoning.investment_thesis = self._build_investment_thesis(scenario, model)

        # Resource allocation
        reasoning.resource_allocation = self._plan_resource_allocation(model)

        # Risk mitigation
        reasoning.risk_mitigation = self._identify_strategic_risks(scenario, model)

        # Success metrics
        reasoning.success_metrics = self._define_strategic_metrics(scenario, model)

        # Timeline
        reasoning.timeline = self._create_strategic_timeline(model)

        # Governance
        reasoning.governance = self._define_governance(persona)

        # Communication plan
        reasoning.communication_plan = self._create_communication_plan(persona)

        return reasoning

    def _build_strategic_context(self, scenario: Scenario, model: ProjectModel) -> str:
        """Build strategic context."""
        return (f"At {scenario.employer}, as {scenario.candidate_role}, "
                f"I was responsible for {scenario.business_objective.lower()}. "
                f"This was a {scenario.type} initiative with {scenario.scope.lower()} scope.")

    def _articulate_vision(self, scenario: Scenario, model: ProjectModel) -> str:
        """Articulate strategic vision."""
        visions = {
            "project": "Enable new customer capabilities that drive revenue growth",
            "migration": "Modernize platform to unlock scalability and reduce operational burden",
            "optimization": "Achieve best-in-class performance and cost efficiency",
            "incident": "Build resilient systems that maintain customer trust",
            "leadership": "Build high-performing engineering culture that delivers consistently",
        }
        return visions.get(scenario.type, "Transform technical capabilities to drive business outcomes")

    def _define_strategic_objectives(self, scenario: Scenario, model: ProjectModel) -> list:
        """Define strategic objectives."""
        return [
            "Accelerate time-to-market for new features",
            "Improve system reliability to 99.99%",
            "Reduce operational cost per transaction by 30%",
            "Enable 10x scale without proportional cost increase",
            "Build engineering team capability and engagement",
        ]

    def _analyze_market(self, scenario: Scenario) -> dict:
        """Analyze market context."""
        industry = scenario.technical_environment.get('industry', 'technology')

        market_data = {
            "technology": {
                "trend": "Cloud-native, AI-enabled, developer-first",
                "competition": "High - major cloud providers + specialized vendors",
                "opportunity": "Platform consolidation, developer experience",
            },
            "fintech": {
                "trend": "Real-time payments, embedded finance, regulatory tech",
                "competition": "High - traditional banks + fintech startups",
                "opportunity": "Compliance automation, financial inclusion",
            },
            "healthcare": {
                "trend": "Interoperability, telehealth, AI diagnostics",
                "competition": "Moderate - regulated, high switching costs",
                "opportunity": "Data integration, patient experience",
            },
            "ecommerce": {
                "trend": "Social commerce, personalization, same-day delivery",
                "competition": "Very high - marketplace dominance",
                "opportunity": "Niche vertical, brand loyalty, logistics",
            },
        }

        return market_data.get(industry, market_data["technology"])

    def _assess_competitive_position(self, scenario: Scenario) -> str:
        """Assess competitive position."""
        return ("Strong technical differentiation through proprietary platform. "
                "Customer retention >95%. "
                "Engineering velocity 2x industry average. "
                "Cost structure advantage from infrastructure optimization.")

    def _build_investment_thesis(self, scenario: Scenario, model: ProjectModel) -> str:
        """Build investment thesis."""
        cost_model = model.numerical_model.get('cost', {})
        monthly = cost_model.get('monthly_usd', 10000)

        return (f"Invest ${monthly * 12:,.0f}/year in platform modernization. "
                f"Expected 3x ROI in 18 months through: "
                f"1) Cost reduction (${monthly * 0.3 * 12:,.0f}/year), "
                f"2) Revenue enablement ($2M+ ARR), "
                f"3) Risk reduction (99.99% availability). "
                f"Payback period: 8 months.")

    def _plan_resource_allocation(self, model: ProjectModel) -> dict:
        """Plan resource allocation."""
        team = model.team
        total = team.get('total_size', 5)

        return {
            "engineering": f"{int(total * 0.7)} FTEs (core development)",
            "platform": f"{int(total * 0.15)} FTEs (infrastructure, tooling)",
            "quality": f"{int(total * 0.1)} FTEs (testing, security, reliability)",
            "management": "1 FTE (engineering manager)",
            "budget_allocation": {
                "people": "70%",
                "infrastructure": "20%",
                "tools_training": "10%",
            },
        }

    def _identify_strategic_risks(self, scenario: Scenario, model: ProjectModel) -> list:
        """Identify strategic risks."""
        return [
            {
                "risk": "Technical execution failure",
                "probability": "Medium",
                "impact": "High",
                "mitigation": "Incremental delivery, prototypes, expert review",
            },
            {
                "risk": "Market shift reduces demand",
                "probability": "Low",
                "impact": "High",
                "mitigation": "Modular architecture, pivot capability",
            },
            {
                "risk": "Key talent attrition",
                "probability": "Medium",
                "impact": "Medium",
                "mitigation": "Retention packages, growth paths, culture investment",
            },
            {
                "risk": "Competitive response",
                "probability": "Medium",
                "impact": "Medium",
                "mitigation": "IP protection, speed to market, customer lock-in",
            },
            {
                "risk": "Regulatory change",
                "probability": "Low",
                "impact": "High",
                "mitigation": "Compliance by design, legal partnership",
            },
        ]

    def _define_strategic_metrics(self, scenario: Scenario, model: ProjectModel) -> list:
        """Define strategic metrics."""
        return [
            "Revenue: $2M+ ARR from new capabilities",
            "Efficiency: 30% cost reduction per transaction",
            "Reliability: 99.99% availability (4.3 min/month downtime)",
            "Velocity: 10x deployment frequency",
            "Quality: <0.1% production defect rate",
            "Team: 4.5/5.0 engagement, <5% attrition",
            "Security: Zero critical vulnerabilities",
            "Compliance: 100% audit pass rate",
        ]

    def _create_strategic_timeline(self, model: ProjectModel) -> list:
        """Create strategic timeline."""
        return [
            "Q1: Foundation - infrastructure, platform, team",
            "Q2: Core capabilities - MVP, early customers",
            "Q3: Scale - performance, reliability, adoption",
            "Q4: Optimize - cost, velocity, next roadmap",
        ]

    def _define_governance(self, persona: ProfessionalPersona) -> str:
        """Define governance model."""
        governance = {
            "executive": "Monthly steering committee (CTO, VP Eng, CFO). Quarterly board updates.",
            "direct": "Bi-weekly leadership sync. Monthly all-hands. Decision log for key choices.",
            "analytical": "Data-driven reviews. Monthly KPI dashboard. Quarterly strategy refresh.",
            "narrative": "Story-based updates. Monthly demo day. Quarterly vision alignment.",
            "collaborative": "Inclusive governance. Team representatives. Consensus on major decisions.",
            "technical-deep": "Architecture review board. RFC process. Technical steering committee.",
        }
        return governance.get(persona.communication_style, governance["balanced"])

    def _create_communication_plan(self, persona: ProfessionalPersona) -> str:
        """Create communication plan."""
        return ("Executive: Monthly business review with KPIs. "
                "Engineering: Bi-weekly tech sync, monthly all-hands. "
                "Team: Weekly standups, sprint reviews, retrospectives. "
                "Stakeholders: Quarterly roadmap updates, ad-hoc for decisions. "
                "Crisis: Incident comms within 15 min, status every 30 min.")

    def generate_response(self, reasoning: StrategyReasoning,
                          question: str, persona: ProfessionalPersona,
                          interviewer_type: str) -> str:
        """Generate natural strategic response."""
        q_lower = question.lower()

        if "vision" in q_lower or "strategy" in q_lower:
            return (f"Vision: {reasoning.vision}. "
                    f"Key objectives: {reasoning.strategic_objectives[0]}, {reasoning.strategic_objectives[1]}. "
                    f"Investment thesis: {reasoning.investment_thesis.split('.')[0]}.")

        if "investment" in q_lower or "roi" in q_lower or "budget" in q_lower:
            return (f"Investment: {reasoning.investment_thesis}. "
                    f"Resource allocation: {reasoning.resource_allocation['budget_allocation']}.")

        if "risk" in q_lower:
            risk = reasoning.risk_mitigation[0]
            return (f"Top strategic risk: {risk['risk']} ({risk['probability']}/{risk['impact']}). "
                    f"Mitigation: {risk['mitigation']}.")

        if "metric" in q_lower or "success" in q_lower:
            return (f"Strategic metrics: {reasoning.success_metrics[0]}, {reasoning.success_metrics[1]}, {reasoning.success_metrics[2]}.")

        if "timeline" in q_lower or "roadmap" in q_lower:
            return (f"Timeline: {', '.join(reasoning.timeline[:2])}. "
                    f"Governance: {reasoning.governance.split('.')[0]}.")

        if "competitive" in q_lower or "market" in q_lower:
            return (f"Market: {reasoning.market_analysis.get('trend', 'N/A')}. "
                    f"Position: {reasoning.competitive_position}.")

        return (f"Strategic context: {reasoning.strategic_context}. "
                f"Vision: {reasoning.vision}. "
                f"Approach: {reasoning.strategic_objectives[0]}.")