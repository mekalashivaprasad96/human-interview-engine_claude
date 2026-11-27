"""
Troubleshooting Engine - Handles production troubleshooting reasoning.
"""

from dataclasses import dataclass, field
from typing import Optional
from ..experience_enrichment.scenario_generator import Scenario
from ..experience_enrichment.project_modeler import ProjectModel


@dataclass
class TroubleshootingReasoning:
    symptoms: list = field(default_factory=list)
    business_impact: str = ""
    scope: str = ""
    recent_changes: list = field(default_factory=list)
    hypotheses: list = field(default_factory=list)
    evidence_gathered: list = field(default_factory=list)
    root_cause: str = ""
    mitigation: str = ""
    permanent_fix: str = ""
    verification: str = ""
    prevention: list = field(default_factory=list)
    communication: list = field(default_factory=list)
    timeline: list = field(default_factory=list)
    tools_used: list = field(default_factory=list)
    lessons_learned: list = field(default_factory=list)


class TroubleshootingEngine:
    """Reasons about production troubleshooting scenarios."""

    TROUBLESHOOTING_METHODOLOGY = [
        "establish_symptoms",
        "understand_business_impact",
        "determine_scope",
        "identify_recent_changes",
        "gather_evidence",
        "form_hypotheses",
        "prioritize_causes",
        "isolate_components",
        "validate_assumptions",
        "identify_root_cause",
        "implement_mitigation",
        "confirm_recovery",
        "prevent_recurrence",
    ]

    def __init__(self):
        pass

    def reason_about_incident(self, scenario: Scenario, model: ProjectModel,
                               question: str, focus: str = None) -> TroubleshootingReasoning:
        """Generate troubleshooting reasoning."""
        reasoning = TroubleshootingReasoning()

        # Symptoms from scenario
        reasoning.symptoms = self._extract_symptoms(scenario)

        # Business impact
        reasoning.business_impact = scenario.outcomes.get('business_impact', '')

        # Scope
        reasoning.scope = self._determine_scope(scenario, model)

        # Recent changes
        reasoning.recent_changes = self._identify_recent_changes(scenario)

        # Hypotheses
        reasoning.hypotheses = self._form_hypotheses(scenario, model)

        # Evidence
        reasoning.evidence_gathered = self._gather_evidence(scenario, model)

        # Root cause
        reasoning.root_cause = self._identify_root_cause(scenario)

        # Mitigation
        reasoning.mitigation = self._determine_mitigation(scenario)

        # Permanent fix
        reasoning.permanent_fix = self._determine_permanent_fix(scenario)

        # Verification
        reasoning.verification = self._determine_verification(scenario)

        # Prevention
        reasoning.prevention = self._determine_prevention(scenario)

        # Communication
        reasoning.communication = self._determine_communication(scenario)

        # Timeline
        reasoning.timeline = self._build_timeline(scenario)

        # Tools
        reasoning.tools_used = self._list_tools(scenario, model)

        # Lessons
        reasoning.lessons_learned = scenario.outcomes.get('lessons_learned', [])

        return reasoning

    def _extract_symptoms(self, scenario: Scenario) -> list:
        """Extract symptoms from scenario."""
        symptoms = []

        for challenge in scenario.challenges:
            symptoms.append(challenge.get('description', ''))

        # Add common symptoms based on type
        if scenario.type == 'incident':
            symptoms.extend([
                "Elevated error rates (5xx > 5%)",
                "Increased latency (p99 > 2x baseline)",
                "Alert firing: high_error_rate, high_latency",
                "Customer reports of failed transactions",
            ])

        return symptoms

    def _determine_scope(self, scenario: Scenario, model: ProjectModel) -> str:
        """Determine incident scope."""
        arch = scenario.architecture
        components = arch.get('components', [])

        affected = []
        for comp in components:
            if 'core' in comp['name'].lower() or 'api' in comp['name'].lower():
                affected.append(comp['name'])

        if not affected:
            affected = [c['name'] for c in components[:3]]

        return f"Affected components: {', '.join(affected)}. Estimated blast radius: {len(affected)} services."

    def _identify_recent_changes(self, scenario: Scenario) -> list:
        """Identify recent changes that could cause issues."""
        changes = [
            "Deployment v2.3.1 rolled out 2 hours before incident",
            "Config change: increased thread pool from 100 to 200",
            "New feature flag enabled: 'new-checkout-flow'",
            "Database schema migration: added index on orders.created_at",
            "Infrastructure: scaled Kafka brokers from 6 to 9",
        ]

        # Filter based on scenario challenges
        for challenge in scenario.challenges:
            if 'deployment' in challenge.get('description', '').lower():
                changes.append(f"Related to: {challenge['description']}")

        return changes

    def _form_hypotheses(self, scenario: Scenario, model: ProjectModel) -> list:
        """Form troubleshooting hypotheses."""
        hypotheses = [
            "H1: Database connection pool exhaustion due to thread pool increase",
            "H2: New feature flag introduced memory leak in checkout service",
            "H3: Kafka rebalance causing temporary partition unavailability",
            "H4: New index causing write contention on orders table",
            "H5: Downstream payment provider latency spike",
        ]

        # Prioritize based on evidence
        prioritized = []
        for h in hypotheses:
            priority = "high" if any(kw in h.lower() for kw in ['deployment', 'config', 'feature']) else "medium"
            prioritized.append({"hypothesis": h, "priority": priority})

        return prioritized

    def _gather_evidence(self, scenario: Scenario, model: ProjectModel) -> list:
        """Gather evidence for hypotheses."""
        evidence = [
            "Distributed traces show 200ms→2s latency increase in checkout service",
            "Database metrics: connections jumped from 50 to 180 (max 200)",
            "Thread pool queue depth: 0 → 500 in 5 minutes",
            "JVM heap: stable, no GC spikes",
            "Network: no packet loss, normal latency between services",
            "Payment provider: normal latency, 99.9% success",
            "Kafka: consumer lag normal, no under-replicated partitions",
            "New feature flag: 100% rollout, error rate 0% before incident",
        ]

        return evidence

    def _identify_root_cause(self, scenario: Scenario) -> str:
        """Identify root cause."""
        for challenge in scenario.challenges:
            if challenge.get('root_cause'):
                return challenge['root_cause']

        return ("Database connection pool exhaustion caused by thread pool increase "
                "without corresponding pool size adjustment. "
                "Connection pool maxed at 200 while thread pool grew to 200, "
                "causing queue buildup and cascade timeouts.")

    def _determine_mitigation(self, scenario: Scenario) -> str:
        """Determine immediate mitigation."""
        return ("1. Rolled back thread pool config to 100 via feature flag (2 min)\n"
                "2. Increased DB connection pool to 300 as emergency measure (5 min)\n"
                "3. Enabled circuit breaker on checkout service to fail fast (3 min)\n"
                "4. Service recovered within 10 minutes of mitigation start")

    def _determine_permanent_fix(self, scenario: Scenario) -> str:
        """Determine permanent fix."""
        return ("1. Added connection pool monitoring with alert at 70% utilization\n"
                "2. Implemented circuit breaker pattern for all downstream calls\n"
                "3. Added config validation: thread pool size <= 0.5 * DB pool size\n"
                "4. Load tested connection pool sizing under 3x expected load\n"
                "5. Updated runbook with connection pool exhaustion scenario")

    def _determine_verification(self, scenario: Scenario) -> str:
        """Determine verification steps."""
        return ("1. Synthetic transactions every 30s for 24h post-fix\n"
                "2. Load test at 3x normal traffic with chaos injection\n"
                "3. Connection pool metrics dashboard review\n"
                "4. Circuit breaker activation test in staging\n"
                "5. Postmortem review with all stakeholders")

    def _determine_prevention(self, scenario: Scenario) -> list:
        """Determine prevention measures."""
        return [
            "Config validation in CI/CD: prevent unsafe thread/pool ratios",
            "Circuit breakers on all external dependencies",
            "Connection pool utilization alerts at 70%/85%/95%",
            "Regular load testing with connection pool stress",
            "Runbook update: connection pool exhaustion playbook",
            "Architecture review: evaluate async processing for write-heavy paths",
        ]

    def _determine_communication(self, scenario: Scenario) -> list:
        """Determine communication actions."""
        return [
            "Slack incident channel created within 2 min",
            "StatusPage updated: 'Investigating checkout latency' (5 min)",
            "Stakeholder notification: Engineering lead, PM, Support lead (10 min)",
            "Customer-facing: 'Experiencing delays, working on fix' (15 min)",
            "Post-incident: detailed postmortem shared within 48h",
        ]

    def _build_timeline(self, scenario: Scenario) -> list:
        """Build incident timeline."""
        return [
            "T+0min: Deployment v2.3.1 rolled out",
            "T+10min: Thread pool config change via feature flag",
            "T+20min: Error rate alert fires (5xx > 1%)",
            "T+22min: On-call paged, joins incident channel",
            "T+25min: Latency p99 crosses 2s threshold",
            "T+30min: DB connection pool at 95% utilization identified",
            "T+32min: Thread pool rollback initiated",
            "T+35min: Connection pool increased to 300",
            "T+37min: Circuit breaker enabled on checkout",
            "T+42min: Error rate drops below 0.1%",
            "T+45min: Latency p99 returns to baseline",
            "T+60min: All-clear declared, monitoring continues",
        ]

    def _list_tools(self, scenario: Scenario, model: ProjectModel) -> list:
        """List tools used in troubleshooting."""
        tools = [
            "Distributed tracing: Jaeger/OpenTelemetry",
            "Metrics: Prometheus/Grafana dashboards",
            "Logs: ELK/CloudWatch with correlation IDs",
            "Database: pg_stat_activity, EXPLAIN ANALYZE",
            "Kubernetes: kubectl, stern, k9s",
            "Profiling: async-profiler, JFR, py-spy",
            "Network: tcpdump, nsenter, cilium",
            "Chaos: Litmus/Gremlin for validation",
        ]

        # Add stack-specific tools
        techs = model.technologies
        if 'java' in str(techs).lower():
            tools.append("JFR/JMC for JVM profiling")
        if 'go' in str(techs).lower():
            tools.append("pprof for Go profiling")
        if 'python' in str(techs).lower():
            tools.append("py-spy / cProfile for Python profiling")

        return tools

    def generate_response(self, reasoning: TroubleshootingReasoning,
                          question: str, persona, interviewer_type: str) -> str:
        """Generate natural response from reasoning."""
        q_lower = question.lower()

        if "what happened" in q_lower or "walk me through" in q_lower:
            # Full narrative
            parts = []
            parts.append(f"So we had an incident where {reasoning.symptoms[0].lower()}.")
            parts.append(f"Business impact: {reasoning.business_impact.lower()}.")
            parts.append(f"Scope was {reasoning.scope.lower()}.")
            parts.append(f"Root cause: {reasoning.root_cause.lower()}.")
            parts.append(f"Mitigation: {reasoning.mitigation.split('.')[0].lower()}.")
            parts.append(f"Permanent fix: {reasoning.permanent_fix.split('.')[0].lower()}.")
            return " ".join(parts)

        if "root cause" in q_lower:
            return f"Root cause was {reasoning.root_cause.lower()}."

        if "how did you fix" in q_lower or "mitigation" in q_lower:
            return f"Immediate mitigation: {reasoning.mitigation.split('.')[0].lower()}. Permanent fix: {reasoning.permanent_fix.split('.')[0].lower()}."

        if "tool" in q_lower:
            tools = reasoning.tools_used[:3]
            return f"Main tools: {', '.join(tools).lower()}."

        if "timeline" in q_lower or "how long" in q_lower:
            return f"Total incident duration about 45 minutes. Detection to mitigation about 12 minutes."

        if "prevent" in q_lower:
            prev = reasoning.prevention[:2]
            return f"Key prevention: {prev[0].lower()}. Also {prev[1].lower()}."

        # Default
        return f"We debugged it systematically: {reasoning.root_cause.lower()}. Fixed with {reasoning.mitigation.split('.')[0].lower()}."