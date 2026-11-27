"""
System Design Engine - Handles system design and architecture reasoning.
"""

from dataclasses import dataclass, field
from typing import Optional
from ..experience_enrichment.scenario_generator import Scenario
from ..experience_enrichment.project_modeler import ProjectModel


@dataclass
class SystemDesignReasoning:
    requirements: dict = field(default_factory=dict)
    constraints: list = field(default_factory=list)
    scale_estimates: dict = field(default_factory=dict)
    availability_requirements: dict = field(default_factory=dict)
    data_model: dict = field(default_factory=dict)
    api_design: dict = field(default_factory=dict)
    architecture_pattern: str = ""
    components: list = field(default_factory=list)
    data_flow: str = ""
    technology_choices: dict = field(default_factory=dict)
    tradeoffs: list = field(default_factory=list)
    failure_modes: list = field(default_factory=list)
    scaling_strategy: str = ""
    operational_considerations: list = field(default_factory=list)
    cost_estimate: dict = field(default_factory=dict)
    security_considerations: list = field(default_factory=list)
    migration_plan: str = ""
    validation_criteria: list = field(default_factory=list)


class SystemDesignEngine:
    """Reasons about system design and architecture."""

    DESIGN_METHODOLOGY = [
        "understand_requirements",
        "identify_constraints",
        "establish_scale",
        "determine_availability",
        "consider_security",
        "identify_dependencies",
        "evaluate_alternatives",
        "explain_interactions",
        "discuss_tradeoffs",
        "consider_operations",
        "evaluate_costs",
        "address_failures",
        "define_validation",
    ]

    def __init__(self):
        pass

    def reason_about_design(self, scenario: Scenario, model: ProjectModel,
                             question: str, focus: str = None) -> SystemDesignReasoning:
        """Generate system design reasoning."""
        reasoning = SystemDesignReasoning()

        # Requirements
        reasoning.requirements = self._gather_requirements(scenario, model)

        # Constraints
        reasoning.constraints = self._identify_constraints(scenario, model)

        # Scale estimates
        reasoning.scale_estimates = self._estimate_scale(scenario, model)

        # Availability
        reasoning.availability_requirements = self._determine_availability(scenario, model)

        # Data model
        reasoning.data_model = self._design_data_model(scenario, model)

        # API design
        reasoning.api_design = self._design_api(scenario, model)

        # Architecture pattern
        reasoning.architecture_pattern = scenario.architecture.get('pattern', 'microservices')

        # Components
        reasoning.components = scenario.architecture.get('components', [])

        # Data flow
        reasoning.data_flow = scenario.architecture.get('data_flow', '')

        # Technology choices
        reasoning.technology_choices = self._justify_technology_choices(scenario, model)

        # Tradeoffs
        reasoning.tradeoffs = scenario.architecture.get('tradeoffs', [])

        # Failure modes
        reasoning.failure_modes = self._analyze_failure_modes(scenario, model)

        # Scaling strategy
        reasoning.scaling_strategy = self._design_scaling_strategy(scenario, model)

        # Operations
        reasoning.operational_considerations = self._identify_operational_considerations(scenario, model)

        # Cost
        reasoning.cost_estimate = self._estimate_cost(scenario, model)

        # Security
        reasoning.security_considerations = self._identify_security_considerations(scenario, model)

        # Migration
        reasoning.migration_plan = self._design_migration_plan(scenario, model)

        # Validation
        reasoning.validation_criteria = self._define_validation_criteria(scenario, model)

        return reasoning

    def _gather_requirements(self, scenario: Scenario, model: ProjectModel) -> dict:
        """Gather functional and non-functional requirements."""
        return {
            "functional": [
                scenario.business_objective,
                "Core CRUD operations for primary entities",
                "Search and filtering capabilities",
                "Real-time updates/notifications",
                "Audit logging for compliance",
            ],
            "non_functional": {
                "scale": scenario.technical_environment.get('scale', {}),
                "latency": "p99 < 200ms for 95th percentile",
                "availability": "99.99% (52 min/year downtime)",
                "consistency": "Strong for financial, eventual for analytics",
                "durability": "Zero data loss (RPO=0)",
                "security": "Encryption at rest/transit, authZ/authN",
                "compliance": self._get_compliance_requirements(scenario),
            },
        }

    def _get_compliance_requirements(self, scenario: Scenario) -> list:
        """Get compliance requirements based on industry."""
        industry = scenario.employer.lower() if scenario.employer else ""

        if 'fintech' in industry or 'bank' in industry:
            return ["PCI-DSS", "SOX", "GDPR", "KYC/AML"]
        elif 'healthcare' in industry or 'medical' in industry:
            return ["HIPAA", "HITRUST", "FDA 21 CFR Part 11"]
        elif 'ecommerce' in industry:
            return ["PCI-DSS", "GDPR", "CCPA"]
        return ["SOC2", "GDPR"]

    def _identify_constraints(self, scenario: Scenario, model: ProjectModel) -> list:
        """Identify system constraints."""
        constraints = [
            "Team size: {} engineers".format(model.team.get('total_size', 5)),
            "Existing tech stack: {}".format(", ".join(model.technologies.get('languages', ['Python']))),
            "Cloud provider: {}".format(model.technologies.get('infrastructure', ['AWS'])[0]),
            "Legacy integration: {} systems".format(len(scenario.technical_environment.get('dependencies', []))),
            "Deployment: Kubernetes with GitOps",
            "Monitoring: Prometheus/Grafana stack",
        ]

        # Budget constraint
        constraints.append("Cost target: <$X/month for current scale")

        # Timeline
        constraints.append("Delivery timeline: {} weeks".format(
            sum(p.get('duration_weeks', 0) for p in model.timeline)
        ))

        return constraints

    def _estimate_scale(self, scenario: Scenario, model: ProjectModel) -> dict:
        """Estimate system scale."""
        scale = scenario.technical_environment.get('scale', {})

        return {
            "requests_per_second": scale.get('requests_per_second', 10000),
            "peak_rps": scale.get('peak_rps', 30000),
            "daily_active_users": scale.get('users', 100000),
            "data_volume_tb": scale.get('data_volume_tb', 10),
            "storage_growth_tb_per_month": 2,
            "geographic_regions": scale.get('regions', 2),
            "services_count": len(scenario.architecture.get('components', [])),
            "team_size": model.team.get('total_size', 5),
        }

    def _determine_availability(self, scenario: Scenario, model: ProjectModel) -> dict:
        """Determine availability requirements."""
        avail = scenario.technical_environment.get('scale', {}).get('availability', {})

        return {
            "target": avail.get('target_pct', 99.99),
            "actual": avail.get('actual_pct', 99.95),
            "downtime_budget_min_per_month": avail.get('downtime_minutes_per_month', 4.3),
            "mttr_target_minutes": avail.get('mttr_minutes', 30),
            "rpo": "0 (synchronous replication)",
            "rto": "5 minutes (automated failover)",
            "multi_az": True,
            "multi_region": True,
        }

    def _design_data_model(self, scenario: Scenario, model: ProjectModel) -> dict:
        """Design data model."""
        return {
            "primary_database": model.technologies.get('databases', ['PostgreSQL'])[0],
            "schema_approach": "Normalized with selective denormalization for read paths",
            "partitioning": "Range partitioning by tenant/date for large tables",
            "indexing_strategy": "B-tree for equality, GIN for JSONB, BRIN for time-series",
            "caching_layers": [
                "Local: Caffeine (hot keys, <10ms)",
                "Distributed: Redis Cluster (shared, <5ms)",
                "CDN: CloudFront (static assets, <50ms)",
            ],
            "read_replicas": 2,
            "backup_strategy": "Continuous WAL archiving + daily snapshots",
            "migration_tool": "Flyway/Liquibase with backward-compatible only",
        }

    def _design_api(self, scenario: Scenario, model: ProjectModel) -> dict:
        """Design API."""
        return {
            "style": "REST with GraphQL for flexible queries",
            "protocol": "HTTP/2 with gRPC for service-to-service",
            "versioning": "URL versioning (/v1/, /v2/) with header fallback",
            "authentication": "OAuth2/OIDC with JWT, mTLS for service-to-service",
            "rate_limiting": "Token bucket: 1000/min per client, burst 200",
            "pagination": "Cursor-based for lists, offset for small datasets",
            "filtering": "Standard query params + GraphQL for complex",
            "webhooks": "Retry with exponential backoff, idempotency keys",
            "documentation": "OpenAPI 3.0 + GraphQL schema, auto-generated",
            "testing": "Contract tests (Pact), load tests (k6)",
        }

    def _justify_technology_choices(self, scenario: Scenario, model: ProjectModel) -> dict:
        """Justify technology choices."""
        choices = {}

        techs = model.technologies
        for category, tech_list in techs.items():
            if tech_list:
                primary = tech_list[0]
                choices[category] = {
                    "selected": primary,
                    "reason": self._get_selection_reason(category, primary, scenario),
                    "alternatives": tech_list[1:4] if len(tech_list) > 1 else [],
                }

        return choices

    def _get_selection_reason(self, category: str, tech: str, scenario: Scenario) -> str:
        """Get reason for technology selection."""
        reasons = {
            "languages": f"Team expertise, ecosystem for {scenario.employer} domain",
            "frameworks": f"Standard for {model.technologies.get('languages', [''])[0]}, good tooling",
            "databases": "Proven at scale, strong consistency, team familiarity",
            "infrastructure": "Industry standard, cloud-agnostic, strong ecosystem",
            "messaging": "High throughput, durability, operational maturity",
            "monitoring": "CNCF graduated, Prometheus ecosystem integration",
            "ci_cd": "GitOps native, Kubernetes integration, policy enforcement",
        }
        return reasons.get(category, "Evaluated against alternatives, met requirements")

    def _analyze_failure_modes(self, scenario: Scenario, model: ProjectModel) -> list:
        """Analyze system failure modes."""
        modes = [
            {
                "scenario": "Database primary failure",
                "detection": "Health check + replication lag monitor",
                "mitigation": "Automated failover to replica (<30s)",
                "impact": "Brief read-only window, zero data loss",
            },
            {
                "scenario": "AZ outage",
                "detection": "Cloud provider health API + synthetic checks",
                "mitigation": "Multi-AZ deployment, traffic shift via DNS/ALB",
                "impact": "Minimal, capacity reduction in remaining AZs",
            },
            {
                "scenario": "Cache cluster failure",
                "detection": "Redis Sentinel + application metrics",
                "mitigation": "Circuit breaker → direct DB reads, cache rebuild",
                "impact": "Latency spike (10-50x) for 2-5 minutes",
            },
            {
                "scenario": "Message queue backlog",
                "detection": "Consumer lag alerts, disk usage monitors",
                "mitigation": "Horizontal consumer scaling, dead letter queue",
                "impact": "Async processing delay, sync paths unaffected",
            },
            {
                "scenario": "Deployment failure",
                "detection": "ArgoCD health assessment, canary metrics",
                "mitigation": "Automated rollback on error rate >1%",
                "impact": "Zero customer impact if canary catches it",
            },
            {
                "scenario": "Network partition",
                "detection": "Inter-service latency/error rate correlation",
                "mitigation": "Graceful degradation, cached responses",
                "impact": "Partial functionality, core reads available",
            },
        ]
        return modes

    def _design_scaling_strategy(self, scenario: Scenario, model: ProjectModel) -> str:
        """Design scaling strategy."""
        rps = scenario.technical_environment.get('scale', {}).get('requests_per_second', 10000)

        if rps > 50000:
            return ("Horizontal sharding by tenant_id/user_id. "
                    "Read replicas for query distribution. "
                    "Async event processing for write-heavy paths. "
                    "Multi-region active-active for global traffic. "
                    "Custom load shedding at edge.")
        elif rps > 10000:
            return ("Horizontal pod autoscaling (HPA) with custom metrics (queue depth, latency). "
                    "Database read replicas (2-3). "
                    "Redis Cluster for distributed caching. "
                    "CDN for static assets and API responses. "
                    "Connection pooling (PgBouncer) at 100:1 ratio.")
        else:
            return ("Vertical scaling headroom (2x current). "
                    "HPA with CPU/memory triggers. "
                    "Single read replica for reporting queries. "
                    "Redis Sentinel for HA caching. "
                    "Database connection pooling at 50:1.")

    def _identify_operational_considerations(self, scenario: Scenario, model: ProjectModel) -> list:
        """Identify operational considerations."""
        return [
            "Deployment: Blue-green with canary analysis (ArgoCD)",
            "Rollback: Automated on error rate >1% or p99 >500ms",
            "Observability: RED metrics per service, USE per node",
            "Alerting: Tiered (team → on-call → manager), runbook links",
            "On-call: 1-week rotation, 24/7 coverage, escalation policy",
            "Capacity: Monthly review, 3-month forecast, 20% headroom",
            "Chaos: Monthly Litmus experiments (pod kill, network partition)",
            "Security: Weekly dependency scans, monthly pen test scope",
            "Compliance: Quarterly audit, automated evidence collection",
            "Cost: Daily FinOps dashboard, reserved instances for baseline",
            "Documentation: Architecture decision records (ADRs), runbooks",
            "Training: Quarterly incident simulation, monthly tech talks",
        ]

    def _estimate_cost(self, scenario: Scenario, model: ProjectModel) -> dict:
        """Estimate infrastructure cost."""
        compute = model.numerical_model.get('compute', {})
        nodes = compute.get('nodes', 20)

        return {
            "compute_monthly_usd": nodes * 500,
            "database_monthly_usd": 2000,
            "cache_monthly_usd": 500,
            "storage_monthly_usd": 300,
            "network_monthly_usd": 400,
            "monitoring_monthly_usd": 200,
            "total_monthly_usd": nodes * 500 + 3400,
            "cost_per_request_usd": 0.00001,
            "optimization_potential": "30-40% with reserved instances and right-sizing",
        }

    def _identify_security_considerations(self, scenario: Scenario, model: ProjectModel) -> list:
        """Identify security considerations."""
        return [
            "Network: mTLS everywhere (Istio), zero-trust network policies",
            "Data: Encryption at rest (KMS), in transit (TLS 1.3), field-level for PII",
            "Identity: OAuth2/OIDC with short-lived JWT, SPIFFE for workloads",
            "Secrets: HashiCorp Vault, dynamic credentials, rotation automation",
            "Supply chain: SBOM generation, image signing (cosign), admission control",
            "Runtime: Falco for anomaly detection, OPA/Gatekeeper for policy",
            "Compliance: Automated evidence collection for SOC2/PCI",
            "Incident: IR plan with forensic readiness, immutable logs",
        ]

    def _design_migration_plan(self, scenario: Scenario, model: ProjectModel) -> str:
        """Design migration plan."""
        if scenario.type == 'migration':
            return ("Strangler Fig: new services alongside legacy. "
                    "CDC (Debezium) for real-time sync. "
                    "Dual-write with feature flags. "
                    "Gradual traffic shift: 10% → 50% → 100%. "
                    "Reconciliation job for consistency. "
                    "Legacy decommission after 30-day parallel run.")
        return ("Greenfield: infrastructure first (Terraform), then services. "
                "Shared libraries for common patterns. "
                "Contract-first API development. "
                "Incremental feature delivery behind flags.")

    def _define_validation_criteria(self, scenario: Scenario, model: ProjectModel) -> list:
        """Define validation criteria."""
        return [
            "Functional: All acceptance criteria passing in CI",
            "Performance: Load test at 3x expected peak, p99 < SLA",
            "Reliability: Chaos experiments pass (no data loss, <30s recovery)",
            "Security: SAST/DAST clean, dependency scan clean, pen test findings addressed",
            "Operational: Runbooks validated, alerting tested, on-call shadowed",
            "Cost: Within 10% of estimate, reserved instance coverage >70%",
            "Compliance: Automated evidence passing, audit-ready",
            "Team: Knowledge transfer complete, bus factor >2 per component",
        ]

    def generate_response(self, reasoning: SystemDesignReasoning,
                          question: str, persona, interviewer_type: str) -> str:
        """Generate natural response from reasoning."""
        q_lower = question.lower()

        if "design" in q_lower and ("system" in q_lower or "architecture" in q_lower):
            # Full design overview
            parts = []
            parts.append(f"Requirements: {reasoning.requirements['functional'][0]}. Scale: {reasoning.scale_estimates['requests_per_second']:,} RPS, {reasoning.scale_estimates['data_volume_tb']}TB.")
            parts.append(f"Architecture: {reasoning.architecture_pattern} with {len(reasoning.components)} services.")
            parts.append(f"Data: {reasoning.data_model['primary_database']} with {reasoning.data_model['caching_layers'][0].split(':')[0]} caching.")
            parts.append(f"Key tradeoff: {reasoning.tradeoffs[0] if reasoning.tradeoffs else 'consistency vs availability'}.")
            return " ".join(parts)

        if "scale" in q_lower or "handle" in q_lower:
            return f"Designed for {reasoning.scale_estimates['requests_per_second']:,} RPS baseline, {reasoning.scale_estimates['peak_rps']:,} peak. Scaling: {reasoning.scaling_strategy.split('.')[0]}."

        if "database" in q_lower or "data model" in q_lower:
            return f"Primary: {reasoning.data_model['primary_database']}. {reasoning.data_model['partitioning']}. Caching: {', '.join([c.split(':')[0] for c in reasoning.data_model['caching_layers']])}."

        if "api" in q_lower:
            return f"{reasoning.api_design['style']} with {reasoning.api_design['protocol']}. Auth: {reasoning.api_design['authentication']}. Rate limit: {reasoning.api_design['rate_limiting']}."

        if "failure" in q_lower or "resilience" in q_lower:
            fm = reasoning.failure_modes[0]
            return f"Main failure modes: {fm['scenario']}. Detection: {fm['detection']}. Mitigation: {fm['mitigation']}."

        if "tradeoff" in q_lower:
            return f"Key tradeoffs: {'; '.join(reasoning.tradeoffs[:2])}."

        if "cost" in q_lower:
            cost = reasoning.cost_estimate
            return f"Estimated ${cost['total_monthly_usd']:,}/month. ${cost['cost_per_request_usd']}/request. {cost['optimization_potential']}."

        if "security" in q_lower:
            return f"Security: {reasoning.security_considerations[0].lower()}. Also {reasoning.security_considerations[1].lower()}."

        if "operational" in q_lower or "deploy" in q_lower:
            return f"Deploy: {reasoning.operational_considerations[0].split(':')[1].strip()}. Rollback: {reasoning.operational_considerations[1].split(':')[1].strip()}."

        return f"System design: {reasoning.architecture_pattern} for {reasoning.requirements['functional'][0]}. {reasoning.scale_estimates['requests_per_second']:,} RPS, {reasoning.availability_requirements['target']}% availability."