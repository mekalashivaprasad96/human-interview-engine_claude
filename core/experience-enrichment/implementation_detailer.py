"""
Implementation Detailer - Generates specific implementation details for technical deep-dives.
"""

from dataclasses import dataclass, field
from typing import Optional
from ..candidate_intelligence.career_chronology import CareerChronologyEntry
from .scenario_generator import Scenario
from .project_modeler import ProjectModel


@dataclass
class ImplementationDetail:
    component: str
    area: str  # config, algorithm, testing, deployment, monitoring, security, performance
    detail: str
    rationale: str
    alternatives_considered: list = field(default_factory=list)
    tradeoffs: list = field(default_factory=list)
    code_snippet: str = ""
    evidence_class: str = "simulated"


class ImplementationDetailer:
    """Generates detailed implementation specifics for technical follow-up questions."""

    def __init__(self):
        self.detail_templates = self._load_templates()

    def _load_templates(self) -> dict:
        """Load implementation detail templates by technology and area."""
        return {
            'kubernetes': {
                'config': [
                    'HPA with custom metrics: cpu > 70%, queue_depth > 100',
                    'PodDisruptionBudget: minAvailable 80% for rolling updates',
                    'Resource requests/limits: cpu 500m/2000m, memory 1Gi/4Gi',
                    'Service mesh: Istio mTLS STRICT, circuit breaker 5xx > 5%',
                ],
                'deployment': [
                    'ArgoCD with progressive delivery: canary 10% → 50% → 100%',
                    'Rollback: automated on error rate > 1% or latency p99 > 500ms',
                    'Blue-green for stateful services with PVC migration',
                ],
                'monitoring': [
                    'Prometheus rules: pod_restart_rate > 0.1, container_memory_usage > 90%',
                    'Grafana dashboards: RED metrics per service, USE metrics per node',
                    'Alerting: PagerDuty with tiered escalation (team → on-call → manager)',
                ],
            },
            'kafka': {
                'config': [
                    'acks=all, min.insync.replicas=2 for durability',
                    'linger.ms=5, batch.size=64KB for throughput',
                    'retention=7d, cleanup.policy=compact for event sourcing',
                    'partition count = 6x broker count for scalability',
                ],
                'performance': [
                    'Producer: async send with callback, max.in.flight=5',
                    'Consumer: fetch.min.bytes=1MB, max.poll.records=500',
                    'Monitoring: consumer_lag, under_replicated_partitions, offline_partitions',
                ],
            },
            'postgresql': {
                'config': [
                    'shared_buffers=25% RAM, effective_cache_size=75% RAM',
                    'work_mem=64MB, maintenance_work_mem=512MB',
                    'max_connections=200 with PgBouncer pool_mode=transaction',
                    'wal_level=replica, max_wal_senders=10 for streaming replication',
                ],
                'performance': [
                    'Index strategy: B-tree for equality, GIN for JSONB, BRIN for time-series',
                    'Partitioning: native range partitioning by created_at monthly',
                    'Query optimization: EXPLAIN ANALYZE, track_io_timing=on',
                ],
            },
            'redis': {
                'config': [
                    'maxmemory-policy=allkeys-lru for cache, volatile-ttl for sessions',
                    'lazyfree-lazy-eviction=yes, lazyfree-lazy-expire=yes',
                    'replica-read-only=yes, min-replicas-to-write=1',
                ],
                'performance': [
                    'Pipeline batch commands: MGET/MSET for bulk operations',
                    'Lua scripts for atomic multi-key operations',
                    'Key design: prefix:entity:id, TTL on all keys, SCAN not KEYS',
                ],
            },
            'python': {
                'config': [
                    'FastAPI with Pydantic v2 for validation, uvicorn workers=cpu_count',
                    'Poetry for dependency management, lock file committed',
                    'Structured logging: structlog with JSON output, correlation IDs',
                    'Type hints: mypy strict, pyright for IDE support',
                ],
                'testing': [
                    'pytest with fixtures, factory_boy for test data',
                    'Contract tests with schemathesis for OpenAPI validation',
                    'Property-based testing with hypothesis for edge cases',
                ],
            },
            'java': {
                'config': [
                    'Spring Boot 3.x, Java 21, virtual threads for I/O',
                    'GraalVM native image for cold start optimization',
                    'Micrometer + Prometheus for metrics, OpenTelemetry for tracing',
                ],
                'performance': [
                    'JMH benchmarks for critical paths',
                    'JFR profiling in production: continuous low-overhead',
                    'Escape analysis, scalar replacement, lock elision',
                ],
            },
            'go': {
                'config': [
                    'Go 1.22+, modules, go.work for monorepo',
                    'pprof endpoints enabled, runtime.SetMutexProfileFraction(10)',
                    'Structured logging: zerolog or slog with sampling',
                ],
                'performance': [
                    'Escape analysis: //go:noinline for benchmarking',
                    'sync.Pool for frequent allocations, bytes.Buffer reuse',
                    'fasthttp for extreme throughput, net/http for compatibility',
                ],
            },
        }

    def generate_details(self, scenario: Scenario, model: ProjectModel,
                          component: str = None, area: str = None) -> list[ImplementationDetail]:
        """Generate implementation details for a scenario/model."""
        details = []

        # Determine technologies in use
        technologies = self._get_technologies(model)

        # If specific component requested, focus on it
        components = [component] if component else self._get_components(model)

        for comp in components:
            comp_techs = self._get_component_technologies(comp, model)
            areas = [area] if area else ['config', 'algorithm', 'testing', 'deployment', 'monitoring', 'security', 'performance']

            for a in areas:
                for tech in comp_techs:
                    tech_details = self.detail_templates.get(tech.lower(), {}).get(a, [])
                    for detail_text in tech_details:
                        details.append(ImplementationDetail(
                            component=comp,
                            area=a,
                            detail=detail_text,
                            rationale=self._generate_rationale(tech, a, detail_text),
                            alternatives_considered=self._generate_alternatives(tech, a),
                            tradeoffs=self._generate_tradeoffs(tech, a),
                            evidence_class="simulated",
                        ))

        # Add scenario-specific details
        details.extend(self._generate_scenario_specific_details(scenario, model))

        return details

    def _get_technologies(self, model: ProjectModel) -> list:
        """Extract all technologies from model."""
        techs = []
        for category in ['languages', 'frameworks', 'databases', 'messaging', 'infrastructure', 'monitoring', 'ci_cd']:
            techs.extend(model.technologies.get(category, []))
        return list(set(techs))

    def _get_components(self, model: ProjectModel) -> list:
        """Get component names from architecture."""
        return [c['name'] for c in model.architecture.get('components', [])]

    def _get_component_technologies(self, component: str, model: ProjectModel) -> list:
        """Get technologies for a specific component."""
        arch = model.architecture
        for comp in arch.get('components', []):
            if comp['name'] == component:
                tech = comp.get('technology', '')
                return [tech] if tech else []
        return self._get_technologies(model)

    def _generate_rationale(self, tech: str, area: str, detail: str) -> str:
        """Generate rationale for implementation choice."""
        rationales = {
            'kubernetes': {
                'config': 'Balances resource efficiency with burst capacity; PDB ensures availability during deployments',
                'deployment': 'Progressive delivery reduces blast radius; automated rollback prevents bad releases',
                'monitoring': 'RED/USE methodology covers all failure modes; tiered alerting reduces noise',
            },
            'kafka': {
                'config': 'acks=all ensures durability; partition strategy enables horizontal scaling',
                'performance': 'Batching improves throughput; consumer tuning prevents lag buildup',
            },
            'postgresql': {
                'config': 'Shared buffers sizing follows PostgreSQL best practices; PgBouncer handles connection scaling',
                'performance': 'Partitioning enables partition pruning; index strategy matches query patterns',
            },
            'redis': {
                'config': 'LRU eviction appropriate for cache workload; lazy free reduces latency spikes',
                'performance': 'Pipelining reduces RTT overhead; Lua scripts ensure atomicity',
            },
            'python': {
                'config': 'FastAPI/Pydantic v2 provides best performance/ergonomics; structlog enables observability',
                'testing': 'Contract tests catch breaking changes; property-based finds edge cases',
            },
            'java': {
                'config': 'Virtual threads solve thread-per-request scalability; native image for serverless',
                'performance': 'JMH ensures reproducible benchmarks; JFR provides production visibility',
            },
            'go': {
                'config': 'Modern Go tooling; pprof enables continuous profiling',
                'performance': 'sync.Pool reduces GC pressure; fasthttp for latency-critical paths',
            },
        }
        return rationales.get(tech.lower(), {}).get(area, 'Chosen based on team expertise and operational requirements')

    def _generate_alternatives(self, tech: str, area: str) -> list:
        """Generate alternatives considered."""
        alternatives = {
            'kubernetes': {
                'config': ['ECS Fargate', 'Nomad', 'VM-based with ASG'],
                'deployment': ['Spinnaker', 'Flux', 'Manual kubectl'],
                'monitoring': ['Datadog', 'New Relic', 'CloudWatch'],
            },
            'kafka': {
                'config': ['Pulsar', 'Redpanda', 'RabbitMQ'],
                'performance': ['Higher partition count', 'Tiered storage', 'KRaft mode'],
            },
            'postgresql': {
                'config': ['MySQL', 'CockroachDB', 'YugabyteDB'],
                'performance': ['Read replicas', 'Citus', 'Materialized views'],
            },
            'redis': {
                'config': ['Memcached', 'Dragonfly', 'KeyDB'],
                'performance': ['Redis Cluster', 'Lua scripting', 'Pipelining'],
            },
            'python': {
                'config': ['Node.js', 'Go', 'Java'],
                'testing': ['Postman', 'Pact', 'Manual testing'],
            },
            'java': {
                'config': ['Kotlin', 'Go', 'Python'],
                'performance': ['Async/await', 'Project Loom', 'Quarkus'],
            },
            'go': {
                'config': ['Rust', 'Java', 'Python'],
                'performance': ['C++', 'Rust', 'Node.js'],
            },
        }
        return alternatives.get(tech.lower(), {}).get(area, ['Alternative approaches evaluated but not selected'])

    def _generate_tradeoffs(self, tech: str, area: str) -> list:
        """Generate tradeoffs for implementation choice."""
        tradeoffs = {
            'kubernetes': {
                'config': ['Complexity overhead', 'Learning curve', 'Resource overhead ~10-15%'],
                'deployment': ['Slower than direct deploy', 'Requires GitOps discipline', 'Rollback complexity'],
                'monitoring': ['High cardinality costs', 'Alert fatigue risk', 'Requires SRE investment'],
            },
            'kafka': {
                'config': ['Operational complexity', 'ZooKeeper dependency (pre-KRaft)', 'Disk space for retention'],
                'performance': ['Latency vs throughput tuning', 'Partition rebalance storms', 'Consumer group coordination'],
            },
            'postgresql': {
                'config': ['Connection pooling required at scale', 'Vacuum tuning complexity', 'Limited horizontal scaling'],
                'performance': ['Index write overhead', 'Partition management', 'Statistics maintenance'],
            },
            'redis': {
                'config': ['Memory cost', 'Single-threaded (mostly)', 'Persistence tradeoffs'],
                'performance': ['Lua script blocking', 'Key expiration scan', 'Cluster resharding'],
            },
        }
        return tradeoffs.get(tech.lower(), {}).get(area, ['Standard tradeoffs apply'])

    def _generate_scenario_specific_details(self, scenario: Scenario, model: ProjectModel) -> list[ImplementationDetail]:
        """Generate details specific to the scenario type."""
        details = []

        if scenario.type == 'incident':
            details.append(ImplementationDetail(
                component='observability',
                area='monitoring',
                detail='Added custom business metrics: order_completion_rate, payment_latency_p99',
                rationale='Technical metrics alone did not reveal customer impact during incident',
                alternatives_considered=['Generic infrastructure metrics only'],
                tradeoffs=['Metric cardinality increase', 'Dashboard maintenance'],
                evidence_class='simulated',
            ))

        if scenario.type == 'migration':
            details.append(ImplementationDetail(
                component='data_pipeline',
                area='algorithm',
                detail='CDC with Debezium → Kafka → Flink reconciliation → dual-write verification',
                rationale='Ensures zero data loss during migration with automated consistency checks',
                alternatives_considered=['Batch ETL with checksums', 'Application-level dual-write'],
                tradeoffs=['Flink operational complexity', 'Kafka retention costs', 'Latency for verification'],
                evidence_class='simulated',
            ))

        if scenario.type == 'optimization':
            details.append(ImplementationDetail(
                component='caching_layer',
                area='performance',
                detail='Multi-tier: local (Caffeine) → distributed (Redis) → CDN (CloudFront)',
                rationale='Local cache eliminates network for hot keys; Redis for shared; CDN for static',
                alternatives_considered=['Redis only', 'Local only', 'Database query cache'],
                tradeoffs=['Cache invalidation complexity', 'Staleness windows', 'Memory overhead'],
                evidence_class='simulated',
            ))

        return details

    def get_detail_for_question(self, question: str, scenario: Scenario, model: ProjectModel) -> Optional[ImplementationDetail]:
        """Find relevant implementation detail for a specific question."""
        question_lower = question.lower()
        details = self.generate_details(scenario, model)

        # Score details by relevance
        scored = []
        for detail in details:
            score = 0
            # Component match
            if detail.component.lower() in question_lower:
                score += 10
            # Area match
            if detail.area.lower() in question_lower:
                score += 8
            # Keyword match
            keywords = ['config', 'configure', 'setting', 'parameter', 'algorithm', 'implement', 'code',
                        'deploy', 'deployment', 'monitor', 'observability', 'alert', 'security', 'auth',
                        'performance', 'latency', 'throughput', 'optimize', 'bottleneck']
            for kw in keywords:
                if kw in question_lower and kw in detail.detail.lower():
                    score += 5
            if score > 0:
                scored.append((score, detail))

        if scored:
            scored.sort(key=lambda x: x[0], reverse=True)
            return scored[0][1]

        return None