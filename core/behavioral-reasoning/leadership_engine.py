"""
Leadership Engine - Handles leadership and management behavioral questions.
"""

from dataclasses import dataclass, field
from typing import Optional
from ..candidate_intelligence.persona_builder import ProfessionalPersona
from ..candidate_intelligence.competency_mapper import CompetencyProfile
from .behavioral_engine import BehavioralEngine


@dataclass
class LeadershipReasoning:
    scenario_type: str  # people_management, technical_leadership, project_leadership, organizational
    team_context: dict = field(default_factory=dict)
    challenge: str = ""
    approach: str = ""
    actions: list = field(default_factory=list)
    outcome: str = ""
    metrics: list = field(default_factory=list)
    reflection: str = ""
    leadership_style: str = ""
    competencies: list = field(default_factory=list)


class LeadershipEngine:
    """Reasons about leadership and management scenarios."""

    LEADERSHIP_SCENARIOS = {
        "people_management": [
            "hiring", "firing", "performance_improvement", "promotion", "team_restructure",
            "conflict_resolution", "career_development", "retention", "onboarding",
            "diversity_inclusion", "remote_team", "burnout_prevention",
        ],
        "technical_leadership": [
            "architecture_decision", "tech_debt_prioritization", "standard_setting",
            "code_review_culture", "incident_response_leadership", "migration_leadership",
            "innovation_initiative", "vendor_evaluation", "build_vs_buy",
        ],
        "project_leadership": [
            "cross_functional_coordination", "deadline_recovery", "scope_management",
            "stakeholder_alignment", "risk_mitigation", "dependency_management",
            "delivery_acceleration", "quality_improvement",
        ],
        "organizational": [
            "strategic_planning", "budget_allocation", "org_design", "culture_change",
            "transformation", "merger_integration", "cost_optimization", "process_improvement",
        ],
    }

    def __init__(self):
        self.behavioral_engine = BehavioralEngine()

    def reason_about_leadership(self, scenario, model, question: str,
                                 persona: ProfessionalPersona,
                                 competencies: CompetencyProfile) -> LeadershipReasoning:
        """Generate leadership reasoning."""
        reasoning = LeadershipReasoning()

        # Determine scenario type
        reasoning.scenario_type = self._determine_scenario_type(question)

        # Team context
        reasoning.team_context = self._build_team_context(model, competencies)

        # Challenge
        reasoning.challenge = self._identify_challenge(scenario, question, reasoning.scenario_type)

        # Approach
        reasoning.approach = self._determine_approach(persona, reasoning.scenario_type)

        # Actions
        reasoning.actions = self._generate_actions(scenario, reasoning.scenario_type, persona)

        # Outcome
        reasoning.outcome = self._determine_outcome(scenario, reasoning.scenario_type)

        # Metrics
        reasoning.metrics = self._extract_leadership_metrics(scenario)

        # Reflection
        reasoning.reflection = self._generate_reflection(persona, reasoning.scenario_type)

        # Leadership style
        reasoning.leadership_style = self._determine_leadership_style(persona)

        # Competencies
        reasoning.competencies = self._identify_leadership_competencies(competencies)

        return reasoning

    def _determine_scenario_type(self, question: str) -> str:
        """Determine leadership scenario type from question."""
        q_lower = question.lower()

        for scenario_type, keywords in self.LEADERSHIP_SCENARIOS.items():
            for kw in keywords:
                if kw.replace('_', ' ') in q_lower:
                    return scenario_type

        # Default based on question phrasing
        if any(kw in q_lower for kw in ['hire', 'fire', 'performance', 'promote', 'team', 'people', 'manage']):
            return "people_management"
        if any(kw in q_lower for kw in ['architecture', 'technical', 'tech debt', 'code review', 'standard']):
            return "technical_leadership"
        if any(kw in q_lower for kw in ['project', 'deliver', 'deadline', 'stakeholder', 'coordinate']):
            return "project_leadership"
        if any(kw in q_lower for kw in ['strategy', 'budget', 'organization', 'culture', 'transformation']):
            return "organizational"

        return "people_management"

    def _build_team_context(self, model, competencies: CompetencyProfile) -> dict:
        """Build team context for leadership scenario."""
        leadership = competencies.leadership

        return {
            "team_size": leadership.get('team_size_managed', 0) or model.team.get('total_size', 5),
            "composition": model.team.get('composition', {}),
            "reports": leadership.get('team_size_managed', 0),
            "span_of_control": "direct" if leadership.get('people_management') else "influence",
            "seniority_mix": "mixed" if model.team.get('total_size', 0) > 5 else "junior-heavy",
            "distribution": "co-located" if model.team.get('total_size', 0) < 10 else "hybrid",
        }

    def _identify_challenge(self, scenario, question: str, scenario_type: str) -> str:
        """Identify the leadership challenge."""
        challenges = {
            "people_management": [
                "Underperforming team member despite coaching",
                "High performer asking for promotion beyond readiness",
                "Team conflict between senior engineers",
                "Retention risk for key talent",
                "Building diverse team in competitive market",
            ],
            "technical_leadership": [
                "Architecture disagreement blocking progress",
                "Technical debt slowing delivery velocity",
                "Legacy system migration with zero-downtime requirement",
                "Vendor lock-in vs build decision",
                "Setting engineering standards across teams",
            ],
            "project_leadership": [
                "Cross-functional project 30% behind schedule",
                "Conflicting priorities from multiple stakeholders",
                "Critical dependency on external team",
                "Scope creep threatening delivery date",
                "Quality issues discovered late in cycle",
            ],
            "organizational": [
                "Engineering transformation with resistant culture",
                "Budget cuts requiring team restructuring",
                "Merger integration of engineering organizations",
                "Process improvement with low adoption",
                "Strategic pivot requiring skill shifts",
            ],
        }

        type_challenges = challenges.get(scenario_type, challenges["people_management"])

        # Select based on scenario details
        if scenario and scenario.challenges:
            for ch in scenario.challenges:
                if any(kw in ch.get('description', '').lower() for kw in type_challenges[0].split()):
                    return ch.get('description', type_challenges[0])

        return type_challenges[0]

    def _determine_approach(self, persona: ProfessionalPersona, scenario_type: str) -> str:
        """Determine leadership approach based on persona."""
        approaches = {
            "people_management": {
                "collaborative": "Coach-first approach: understand goals, create growth plan, regular check-ins",
                "direct": "Clear expectations, direct feedback, documented improvement plan",
                "analytical": "Data-driven: performance metrics, skill gaps, structured development",
                "narrative": "Story-based: share similar experiences, build trust, guide through example",
            },
            "technical_leadership": {
                "collaborative": "Consensus-building: RFC process, team discussion, documented decisions",
                "direct": "Decisive: evaluate tradeoffs, make call, communicate rationale",
                "analytical": "Evidence-based: prototypes, benchmarks, cost-benefit analysis",
                "narrative": "Vision-driven: paint technical future, inspire adoption",
            },
            "project_leadership": {
                "collaborative": "Facilitative: align stakeholders, clear roles, shared accountability",
                "direct": "Command: critical path focus, rapid decisions, escalation clarity",
                "analytical": "Structured: risk register, dependency map, milestone tracking",
                "narrative": "Inspiring: connect to mission, celebrate milestones, maintain momentum",
            },
            "organizational": {
                "collaborative": "Inclusive: broad input, pilot programs, iterative rollout",
                "direct": "Decisive: clear direction, timeline, accountability",
                "analytical": "Strategic: market analysis, ROI modeling, phased approach",
                "narrative": "Transformational: compelling vision, change champions, cultural anchors",
            },
        }

        style_approaches = approaches.get(scenario_type, approaches["people_management"])
        return style_approaches.get(persona.communication_style, style_approaches["collaborative"])

    def _generate_actions(self, scenario, scenario_type: str, persona: ProfessionalPersona) -> list:
        """Generate specific leadership actions."""
        base_actions = {
            "people_management": [
                "Scheduled 1:1 to understand perspective and goals",
                "Created 90-day improvement plan with measurable milestones",
                "Arranged mentorship pairing with senior team member",
                "Weekly check-ins with documented progress",
                "Escalated to HR/manager when improvement not achieved",
                "Made difficult decision with empathy and clarity",
            ],
            "technical_leadership": [
                "Initiated RFC process with clear problem statement",
                "Facilitated architecture review with all stakeholders",
                "Ran proof-of-concept for top 2 alternatives",
                "Documented decision with tradeoffs and rationale",
                "Defined implementation roadmap with milestones",
                "Established coding standards and review process",
            ],
            "project_leadership": [
                "Mapped critical path and identified bottlenecks",
                "Negotiated scope reduction with product stakeholders",
                "Reallocated resources to unblock critical path",
                "Established daily standups for coordination",
                "Created risk register with mitigation plans",
                "Delivered MVP on revised timeline",
            ],
            "organizational": [
                "Conducted org health assessment (survey + interviews)",
                "Designed target org structure with clear ownership",
                "Created transition plan with 30/60/90 day milestones",
                "Identified change champions in each team",
                "Ran pilot with one team before full rollout",
                "Established metrics for adoption and success",
            ],
        }

        actions = base_actions.get(scenario_type, base_actions["people_management"])

        # Customize for persona
        if persona.communication_style == "direct":
            actions = [a.replace("Facilitated", "Led").replace("Coached", "Directed") for a in actions]
        elif persona.communication_style == "collaborative":
            actions = [a.replace("Directed", "Facilitated").replace("Decided", "Align team on") for a in actions]

        return actions

    def _determine_outcome(self, scenario, scenario_type: str) -> str:
        """Determine leadership outcome."""
        outcomes = {
            "people_management": [
                "Team member improved to meeting expectations within 60 days",
                "High performer promoted after stretch assignment",
                "Conflict resolved; both engineers collaborating effectively",
                "Retained key talent with growth plan and compensation adjustment",
                "Hired 3 senior engineers in 90 days, exceeding diversity targets",
            ],
            "technical_leadership": [
                "Architecture decision unblocked 3 teams, reduced latency 40%",
                "Tech debt paydown freed 20% capacity for feature work",
                "Migration completed zero-downtime, saved $2M/year",
                "Vendor evaluation saved $500K, avoided lock-in",
                "Engineering standards adopted org-wide, reduced review time 50%",
            ],
            "project_leadership": [
                "Project delivered 2 weeks early after scope negotiation",
                "Stakeholder alignment achieved; clear priorities documented",
                "Dependency risk mitigated; parallel workstreams unblocked",
                "Quality gates implemented; production defects reduced 60%",
                "Cross-functional team celebrated successful launch",
            ],
            "organizational": [
                "Engineering transformation: deployment frequency 10x, MTTR 80% down",
                "Restructure completed with 95% retention, clear career paths",
                "Merger integration: unified stack, $3M annual savings",
                "Process adoption: 80% teams using new workflow in 60 days",
                "Strategic pivot: new product line launched, $10M ARR in year 1",
            ],
        }

        type_outcomes = outcomes.get(scenario_type, outcomes["people_management"])
        return type_outcomes[0]

    def _extract_leadership_metrics(self, scenario) -> list:
        """Extract leadership-relevant metrics."""
        metrics = scenario.outcomes.get('metrics', [])

        leadership_metrics = [
            "Team engagement score: 4.2/5.0 (up from 3.6)",
            "Voluntary attrition: 5% (industry avg 13%)",
            "Promotion rate: 25% of team in 18 months",
            "Diversity hiring: 40% underrepresented in last 6 hires",
            "Delivery predictability: 90% on-time (up from 65%)",
            "Incident MTTR: 15 min (down from 60 min)",
            "Code review turnaround: 4 hours (down from 24 hours)",
            "Engineering satisfaction: 4.5/5.0",
        ]

        # Add scenario metrics if relevant
        for m in metrics:
            if any(kw in m.lower() for kw in ['team', 'people', 'hire', 'retention', 'engagement', 'promotion']):
                leadership_metrics.append(m)

        return leadership_metrics[:5]

    def _generate_reflection(self, persona: ProfessionalPersona, scenario_type: str) -> str:
        """Generate leadership reflection."""
        reflections = {
            "people_management": {
                "collaborative": "The biggest lesson: people don't need fixing, they need understanding and support.",
                "direct": "Clear expectations and timely feedback are the kindest form of leadership.",
                "analytical": "Data helps remove bias, but empathy drives the conversation.",
                "narrative": "Sharing my own growth struggles built more trust than any framework.",
            },
            "technical_leadership": {
                "collaborative": "The best architecture decisions come from inclusive debate, not authority.",
                "direct": "Sometimes the team needs a decision more than a perfect decision.",
                "analytical": "Prototypes speak louder than slides; evidence builds consensus.",
                "narrative": "Painting the 'why' before the 'what' gets true buy-in.",
            },
            "project_leadership": {
                "collaborative": "Shared ownership beats individual heroics every time.",
                "direct": "Protecting the critical path means saying no to good ideas.",
                "analytical": "Visible risk tracking prevents surprise more than status reports.",
                "narrative": "Celebrating small wins keeps momentum through the long haul.",
            },
            "organizational": {
                "collaborative": "Change succeeds when people co-create it, not when it's imposed.",
                "direct": "Organizational clarity enables team autonomy.",
                "analytical": "Pilot, measure, iterate—then scale what works.",
                "narrative": "Culture change is a story we write together, one chapter at a time.",
            },
        }

        type_reflections = reflections.get(scenario_type, reflections["people_management"])
        return type_reflections.get(persona.communication_style, type_reflections["collaborative"])

    def _determine_leadership_style(self, persona: ProfessionalPersona) -> str:
        """Determine leadership style from persona."""
        style_map = {
            "collaborative": "Servant/Coach - empower through support and growth",
            "direct": "Authoritative/Decisive - clear direction, high standards",
            "analytical": "Data-driven/Evidence-based - decisions from evidence",
            "narrative": "Transformational/Visionary - inspire through purpose",
            "executive": "Strategic/Organizational - align to business outcomes",
            "technical-deep": "Technical/Expert - lead by technical credibility",
            "balanced": "Situational - adapt style to context and individual",
        }
        return style_map.get(persona.communication_style, style_map["balanced"])

    def _identify_leadership_competencies(self, competencies: CompetencyProfile) -> list:
        """Identify demonstrated leadership competencies."""
        comps = []
        leadership = competencies.leadership

        if leadership.get('people_management'):
            comps.append("People Management")
        if leadership.get('technical_leadership'):
            comps.append("Technical Leadership")
        if leadership.get('project_leadership'):
            comps.append("Project Leadership")
        if leadership.get('mentoring'):
            comps.append("Mentoring & Development")
        if leadership.get('hiring'):
            comps.append("Hiring & Team Building")

        # Add from transferable
        transferable = competencies.transferable
        if 'engineering_management' in transferable:
            comps.append("Engineering Management")
        if 'technical_strategy' in transferable:
            comps.append("Technical Strategy")
        if 'cross_industry_adaptability' in transferable:
            comps.append("Change Management")

        return comps

    def generate_response(self, reasoning: LeadershipReasoning,
                          question: str, persona: ProfessionalPersona,
                          interviewer_type: str) -> str:
        """Generate natural leadership response."""
        parts = []

        # Context
        parts.append(f"Team context: {reasoning.team_context.get('team_size', 'N/A')} engineers, {reasoning.team_context.get('distribution', 'co-located')}.")

        # Challenge
        parts.append(f"Challenge: {reasoning.challenge}.")

        # Approach
        parts.append(f"My approach: {reasoning.approach}.")

        # Actions (2-3 key ones)
        for action in reasoning.actions[:3]:
            parts.append(action + ".")

        # Outcome
        parts.append(f"Result: {reasoning.outcome}.")

        # Metrics
        if reasoning.metrics:
            parts.append(f"Metrics: {reasoning.metrics[0].lower()}.")

        # Reflection for senior
        if persona.ownership_level in ['system', 'platform', 'organization']:
            parts.append(reasoning.reflection)

        return " ".join(parts)