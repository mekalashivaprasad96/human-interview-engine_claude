"""
Implementation Engine - Handles technical implementation reasoning and explanation.
"""

from dataclasses import dataclass, field
from typing import Optional
from ..experience_enrichment.scenario_generator import Scenario
from ..experience_enrichment.project_modeler import ProjectModel
from ..experience_enrichment.implementation_detailer import ImplementationDetailer


@dataclass
class ImplementationReasoning:
    problem: str
    requirements: list = field(default_factory=list)
    approach: str = ""
    technology_selection: dict = field(default_factory=dict)
    architecture: dict = field(default_factory=dict)
    key_decisions: list = field(default_factory=list)
    implementation_steps: list = field(default_factory=list)
    configuration_details: list = field(default_factory=list)
    testing_strategy: str = ""
    deployment_approach: str = ""
    monitoring_setup: list = field(default_factory=list)
    security_measures: list = field(default_factory=list)
    performance_considerations: list = field(default_factory=list)
    scalability_plan: str = ""
    failure_modes: list = field(default_factory=list)
    rollback_plan: str = ""
    maintenance_approach: str = ""
    tradeoffs: list = field(default_factory=list)
    alternatives_considered: list = field(default_factory=list)
    constraints: list = field(default_factory=list)


class ImplementationEngine:
    """Reasons about technical implementations."""

    def __init__(self):
        self.detailer = ImplementationDetailer()

    def reason_about_implementation(self, scenario: Scenario, model: ProjectModel,
                                     question: str, focus_area: str = None) -> ImplementationReasoning:
        """Generate implementation reasoning for a question."""
        reasoning = ImplementationReasoning(
            problem=scenario.business_objective,
        )

        # Extract requirements from scenario
        reasoning.requirements = self._extract_requirements(scenario)

        # Determine approach
        reasoning.approach = self._determine_approach(scenario, model, focus_area)

        # Technology selection rationale
        reasoning.technology_selection = self._explain_technology_choices(scenario, model)

        # Architecture
        reasoning.architecture = scenario.architecture

        # Key decisions
        reasoning.key_decisions = self._extract_key_decisions(scenario, model)

        # Implementation steps
        reasoning.implementation_steps = self._generate_implementation_steps(scenario, model, focus_area)

        # Configuration details
        reasoning.configuration_details = self._get_configuration_details(scenario, model, focus_area)

        # Testing strategy
        reasoning.testing_strategy = scenario.implementation_details.get('testing_strategy', '')

        # Deployment approach
        reasoning.deployment_approach = scenario.implementation_details.get('deployment_approach', '')

        # Monitoring
        reasoning.monitoring_setup = scenario.implementation_details.get('monitoring_observability', [])

        # Security
        reasoning.security_measures = scenario.implementation_details.get('security_measures', [])

        # Performance
        reasoning.performance_considerations = self._get_performance_considerations(scenario, model)

        # Scalability
        reasoning.scalability_plan = self._get_scalability_plan(scenario, model)

        # Failure modes
        reasoning.failure_modes = self._identify_failure_modes(scenario, model)

        # Rollback
        reasoning.rollback_plan = self._get_rollback_plan(scenario, model)

        # Maintenance
        reasoning.maintenance_approach = self._get_maintenance_approach(scenario, model)

        # Tradeoffs
        reasoning.tradeoffs = scenario.architecture.get('tradeoffs', [])

        # Alternatives
        reasoning.alternatives_considered = self._get_alternatives(scenario)

        # Constraints
        reasoning.constraints = self._get_constraints(scenario, model)

        return reasoning

    def _extract_requirements(self, scenario: Scenario) -> list:
        """Extract requirements from scenario."""
        reqs = [
            scenario.business_objective,
            f"Scale: {scenario.technical_environment.get('scale', {})}",
        ]

        # Add non-functional requirements
        tech_env = scenario.technical_environment
        if tech_env.get('scale', {}).get('requests_per_second', 0) > 10000:
            reqs.append("High throughput (10K+ RPS)")
        if tech_env.get('scale', {}).get('data_volume_tb', 0) > 10:
            reqs.append("Large data volume (10+ TB)")

        # Industry-specific
        if scenario.employer and 'fintech' in scenario.employer.lower():
            reqs.append("Financial-grade reliability and auditability")
        elif 'healthcare' in scenario.employer.lower():
            reqs.append("HIPAA compliance and data privacy")

        return reqs

    def _determine_approach(self, scenario: Scenario, model: ProjectModel, focus_area: str) -> str:
        """Determine implementation approach."""
        approach_map = {
            'project': "Iterative delivery with feature flags, starting with core domain model",
            'incident': "Rapid diagnosis using distributed tracing, then targeted fix with canary deployment",
            'migration': "Strangler Fig pattern with dual-write and CDC-based verification",
            'optimization': "Measure-first approach: profile, identify bottlenecks, optimize, validate",
            'leadership': "Collaborative design review, clear ownership, regular check-ins",
        }
        return approach_map.get(scenario.type, "Systematic approach: requirements → design → implement → validate")

    def _explain_technology_choices(self, scenario: Scenario, model: ProjectModel) -> dict:
        """Explain why technologies were chosen."""
        techs = model.technologies
        choices = {}

        # Primary language
        if techs.get('languages'):
            primary = techs['languages'][0]
            choices[primary] = f"Team expertise, ecosystem maturity for {scenario.employer} domain"

        # Framework
        if techs.get('frameworks'):
            fw = techs['frameworks'][0]
            choices[fw] = f"Standard for {techs.get('languages', [''])[0]} ecosystem, good operational tooling"

        # Database
        if techs.get('databases'):
            db = techs['databases'][0]
            choices[db] = "Proven at scale, strong consistency model, team familiarity"

        # Infrastructure
        if techs.get('infrastructure'):
            infra = techs['infrastructure'][0]
            choices[infra] = "Industry standard, cloud-agnostic, strong ecosystem"

        # Messaging
        if techs.get('messaging'):
            msg = techs['messaging'][0]
            choices[msg] = "High throughput, durability guarantees, operational maturity"

        return choices

    def _extract_key_decisions(self, scenario: Scenario, model: ProjectModel) -> list:
        """Extract key architectural decisions."""
        decisions = scenario.architecture.get('key_decisions', [])

        # Add scenario-specific decisions
        if scenario.type == 'migration':
            decisions.append({
                'decision': 'Strangler Fig with CDC for zero-downtime migration',
                'alternatives': ['Big bang', 'Parallel run without CDC'],
                'rationale': 'Minimizes risk, allows incremental validation',
                'tradeoffs': ['Operational complexity', 'Dual-write latency'],
            })
        elif scenario.type == 'optimization':
            decisions.append({
                'decision': 'Multi-tier caching (local → Redis → CDN)',
                'alternatives': ['Redis only', 'Database query cache'],
                'rationale': 'Local cache eliminates network for hot keys; CDN for static assets',
                'tradeoffs': ['Cache invalidation complexity', 'Staleness windows'],
            })
        elif scenario.type == 'incident':
            decisions.append({
                'decision': 'Circuit breaker pattern for downstream resilience',
                'alternatives': ['Retry with backoff only', 'Bulkhead pattern'],
                'rationale': 'Prevents cascade failures, enables fast failure',
                'tradeoffs': ['Added latency', 'Configuration complexity'],
            })

        return decisions

    def _generate_implementation_steps(self, scenario: Scenario, model: ProjectModel,
                                        focus_area: str) -> list:
        """Generate implementation steps."""
        steps = []

        if scenario.type == 'project':
            steps = [
                "1. Domain modeling and API contract design (OpenAPI/Protobuf)",
                "2. Database schema design with migration strategy",
                "3. Core service implementation with unit tests (80%+ coverage)",
                "4. Integration layer: messaging, external APIs, auth",
                "5. Contract testing between services",
                "6. Load testing and performance baseline",
                "7. Canary deployment with automated rollback",
                "8. Full rollout with monitoring and alerting",
            ]
        elif scenario.type == 'migration':
            steps = [
                "1. Current system analysis and data model mapping",
                "2. CDC pipeline setup (Debezium → Kafka → target)",
                "3. Dual-write implementation with feature flag",
                "4. Reconciliation job for consistency verification",
                "5. Gradual traffic shift with canary analysis",
                "6. Read path cutover with fallback",
                "7. Write path cutover with rollback plan",
                "8. Legacy decommission and cost verification",
            ]
        elif scenario.type == 'optimization':
            steps = [
                "1. Distributed tracing setup (OpenTelemetry → Jaeger)",
                "2. Profiling: CPU, memory, lock contention, GC",
                "3. Database query analysis: EXPLAIN ANALYZE, missing indexes",
                "4. Quick wins: config tuning, connection pooling, caching",
                "5. Deep optimization: algorithmic improvements, data structure changes",
                "6. Load testing with realistic traffic patterns",
                "7. Regression testing and canary deployment",
                "8. Post-deployment monitoring and alerting",
            ]
        elif scenario.type == 'incident':
            steps = [
                "1. Symptom identification: alerts, logs, metrics, user reports",
                "2. Impact assessment: revenue, users, SLA",
                "3. Recent changes review: deployments, config, infrastructure",
                "4. Hypothesis formation and prioritization",
                "5. Isolation: traffic splitting, feature flags, circuit breakers",
                "6. Root cause identification with evidence",
                "7. Fix implementation with minimal blast radius",
                "8. Verification: synthetic tests, canary, full rollout",
                "9. Postmortem: timeline, root cause, action items",
            ]

        return steps

    def _get_configuration_details(self, scenario: Scenario, model: ProjectModel,
                                    focus_area: str) -> list:
        """Get relevant configuration details."""
        configs = scenario.implementation_details.get('key_configurations', [])

        # Add focus-area specific configs
        if focus_area == 'kubernetes':
            configs.extend([
                "HPA: minReplicas=3, maxReplicas=50, targetCPUUtilization=70%",
                "PDB: minAvailable=80% for zero-downtime deployments",
                "Resources: requests=500m CPU/1Gi RAM, limits=2000m/4Gi",
                "Service mesh: Istio mTLS STRICT, circuit breaker 5xx>5%",
            ])
        elif focus_area == 'kafka':
            configs.extend([
                "acks=all, min.insync.replicas=2 for durability",
                "linger.ms=5, batch.size=64KB for throughput",
                "retention=7d, cleanup.policy=compact for event sourcing",
                "partitions=6x brokers for scalability",
            ])
        elif focus_area == 'database':
            configs.extend([
                "shared_buffers=25% RAM, effective_cache_size=75% RAM",
                "work_mem=64MB, maintenance_work_mem=512MB",
                "PgBouncer: pool_mode=transaction, max_client_conn=1000",
                "Partitioning: native range by created_at monthly",
            ])

        return configs

    def _get_performance_considerations(self, scenario: Scenario, model: ProjectModel) -> list:
        """Get performance considerations."""
        considerations = [
            "Connection pooling for database and HTTP clients",
            "Async/non-blocking I/O for high concurrency",
            "Caching strategy: local (Caffeine) → distributed (Redis) → CDN",
            "Database indexing: B-tree for equality, GIN for JSONB, BRIN for time-series",
            "Pagination with cursor-based for large datasets",
            "Batch processing for write-heavy workloads",
        ]

        # Scale-specific
        rps = scenario.technical_environment.get('scale', {}).get('requests_per_second', 0)
        if rps > 50000:
            considerations.extend([
                "Sharding strategy for horizontal scaling",
                "Read replicas for query distribution",
                "Async processing with message queues",
                "Edge caching with Cloudflare/Fastly",
            ])

        return considerations

    def _get_scalability_plan(self, scenario: Scenario, model: ProjectModel) -> str:
        """Get scalability plan."""
        rps = scenario.technical_environment.get('scale', {}).get('requests_per_second', 10000)

        if rps > 50000:
            return ("Horizontal sharding by tenant/user, read replicas, "
                    "async event processing, multi-region active-active")
        elif rps > 10000:
            return ("Horizontal pod autoscaling, read replicas, "
                    "caching layer, connection pooling")
        else:
            return ("Vertical scaling headroom, HPA with custom metrics, "
                    "database read replicas for query distribution")

    def _identify_failure_modes(self, scenario: Scenario, model: ProjectModel) -> list:
        """Identify potential failure modes."""
        modes = [
            "Database connection pool exhaustion under load",
            "Cascading timeout from downstream service degradation",
            "Cache stampede on cold start or invalidation",
            "Message queue backlog causing memory pressure",
            "Network partition between availability zones",
            "Deployment rollback failure due to schema migration",
            "Credential rotation causing auth failures",
            "Resource quota exhaustion (CPU, memory, disk, IP)",
        ]

        # Scenario-specific
        if scenario.type == 'migration':
            modes.extend([
                "CDC pipeline lag causing data inconsistency",
                "Dual-write race conditions",
                "Reconciliation job failures",
            ])

        return modes

    def _get_rollback_plan(self, scenario: Scenario, model: ProjectModel) -> str:
        """Get rollback plan."""
        return ("Automated rollback on error rate >1% or p99 latency >500ms. "
                "Blue-green for stateful services with PVC migration. "
                "Database migrations: backward-compatible only, separate deploy. "
                "Feature flags for instant kill-switch. "
                "Rollback target: <5 minutes for stateless, <15 minutes for stateful.")

    def _get_maintenance_approach(self, scenario: Scenario, model: ProjectModel) -> str:
        """Get maintenance approach."""
        return ("Weekly dependency updates with Dependabot. "
                "Monthly chaos engineering (Litmus/Gremlin). "
                "Quarterly capacity planning and cost optimization. "
                "Semi-annual architecture review. "
                "Runbook updates after every incident. "
                "On-call rotation with 24/7 coverage, 1-week shifts.")

    def _get_alternatives(self, scenario: Scenario) -> list:
        """Get alternatives considered."""
        alts = {
            'project': ['Serverless functions', 'Monolithic deployment', 'Managed PaaS'],
            'migration': ['Big bang cutover', 'Parallel run without CDC', 'Application-level dual-write'],
            'optimization': ['Vertical scaling', 'Read replicas only', 'Query optimization only'],
            'incident': ['Full service restart', 'Traffic drain and wait', 'Manual intervention'],
        }
        return alts.get(scenario.type, ['Alternative approaches evaluated'])

    def _get_constraints(self, scenario: Scenario, model: ProjectModel) -> list:
        """Get project constraints."""
        constraints = [
            "Team size and expertise",
            "Existing technology standards",
            "Compliance requirements (SOC2, PCI, HIPAA)",
            "Budget and cost targets",
            "Timeline and delivery commitments",
            "Legacy system integration",
            "Data residency requirements",
            "Security review gates",
        ]

        # Add scenario-specific
        if scenario.type == 'migration':
            constraints.append("Zero-downtime requirement")
        if scenario.type == 'incident':
            constraints.append("SLA breach timeline")

        return constraints

    def generate_response(self, reasoning: ImplementationReasoning,
                          question: str, persona, interviewer_type: str) -> str:
        """Generate natural response from reasoning."""
        # This would integrate with the response generator
        # For now, return structured summary
        response_parts = []

        # Direct answer
        if "how" in question.lower() and "implement" in question.lower():
            response_parts.append(f"We approached it by {reasoning.approach.lower()}.")

        # Key decision
        if reasoning.key_decisions:
            kd = reasoning.key_decisions[0]
            response_parts.append(f"The main decision was {kd.get('decision', '').lower()} because {kd.get('rationale', '').lower()}.")

        # Implementation detail
        if reasoning.implementation_steps:
            response_parts.append(f"Implementation was {len(reasoning.implementation_steps)}-phase: {reasoning.implementation_steps[0].lower()}.")

        # Configuration if asked
        if any(kw in question.lower() for kw in ['config', 'setting', 'parameter']):
            if reasoning.configuration_details:
                response_parts.append(f"Key config: {reasoning.configuration_details[0]}.")

        return " ".join(response_parts)