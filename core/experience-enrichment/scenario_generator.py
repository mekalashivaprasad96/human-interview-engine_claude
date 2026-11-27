"""
Scenario Generator - Generates detailed professional practice scenarios for interview responses.
"""

from dataclasses import dataclass, field
from typing import Optional
from ..candidate_intelligence.career_chronology import CareerChronologyEntry
from ..candidate_intelligence.competency_mapper import CompetencyProfile
from ..professional_world_model.employer_context import EmployerContext
from ..professional_world_model.industry_model import IndustryModel


@dataclass
class Scenario:
    id: str
    title: str
    type: str  # project, incident, migration, optimization, leadership, customer, failure, innovation, process-improvement
    employer: str
    period: str
    business_objective: str
    scope: str
    technical_environment: dict = field(default_factory=dict)
    architecture: dict = field(default_factory=dict)
    candidate_role: str = ""
    individual_contributions: list = field(default_factory=list)
    team_structure: dict = field(default_factory=dict)
    implementation_details: dict = field(default_factory=dict)
    challenges: list = field(default_factory=list)
    outcomes: dict = field(default_factory=dict)
    evidence_classification: dict = field(default_factory=dict)
    followup_resilience: float = 0.0
    status: str = "enriched"  # documented, enriched, simulated, confirmed


class ScenarioGenerator:
    """Generates detailed scenarios from career data."""

    SCENARIO_TEMPLATES = {
        'project': {
            'business_objectives': [
                'Build new customer-facing feature to increase conversion',
                'Modernize legacy system to reduce maintenance burden',
                'Implement new integration to expand market reach',
                'Build internal platform to accelerate team velocity',
                'Migrate to new technology stack for scalability',
            ],
            'scopes': [
                'End-to-end feature delivery across frontend, backend, and infrastructure',
                'Backend API and data pipeline for new product line',
                'Infrastructure migration with zero-downtime requirement',
                'Platform capability enabling 10+ team consumption',
                'Cross-service refactoring affecting 5+ services',
            ],
        },
        'incident': {
            'business_objectives': [
                'Resolve production outage affecting customer transactions',
                'Investigate and fix performance degradation',
                'Recover from data corruption incident',
                'Mitigate security vulnerability in production',
                'Debug cascading failure across microservices',
            ],
            'scopes': [
                'Multi-service outage with revenue impact',
                'Database performance issue affecting all users',
                'Cache invalidation bug causing stale data',
                'Deployment rollback gone wrong',
                'Third-party dependency failure cascade',
            ],
        },
        'migration': {
            'business_objectives': [
                'Migrate from monolith to microservices',
                'Move from on-premise to cloud',
                'Upgrade major framework version',
                'Consolidate multiple databases',
                'Transition to new CI/CD platform',
            ],
            'scopes': [
                'Phased migration of 20+ services over 12 months',
                'Database migration with zero data loss',
                'Infrastructure lift-and-shift with modernization',
                'CI/CD migration for 50+ pipelines',
                'Data platform migration with backward compatibility',
            ],
        },
        'optimization': {
            'business_objectives': [
                'Reduce infrastructure costs by 40%',
                'Improve API latency from 500ms to 100ms',
                'Increase throughput to handle 10x traffic',
                'Reduce build/deploy time by 60%',
                'Optimize database query performance',
            ],
            'scopes': [
                'Full-stack performance optimization across 10 services',
                'Database indexing and query rewrite initiative',
                'Caching strategy overhaul',
                'Resource right-sizing and auto-scaling tuning',
                'Frontend bundle optimization and lazy loading',
            ],
        },
    }

    def __init__(self):
        self.industry_model = IndustryModel()

    def generate_scenarios(self, chronology_entries: list[CareerChronologyEntry],
                           employer_contexts: list[EmployerContext],
                           competencies: CompetencyProfile,
                           mode: str = "immersive") -> list[Scenario]:
        """Generate scenarios for each significant role/project."""
        scenarios = []

        for entry in chronology_entries:
            # Generate 1-3 scenarios per role based on duration and seniority
            num_scenarios = self._determine_scenario_count(entry)

            employer_context = next(
                (ec for ec in employer_contexts if ec.name == entry.employer), None
            )

            for i in range(num_scenarios):
                scenario_type = self._select_scenario_type(entry, i, competencies)
                scenario = self._generate_scenario(
                    entry, employer_context, scenario_type, i, competencies, mode
                )
                scenarios.append(scenario)

        return scenarios

    def _determine_scenario_count(self, entry: CareerChronologyEntry) -> int:
        """Determine how many scenarios to generate for a role."""
        base = 1
        if entry.duration_months >= 24:
            base += 1
        if entry.duration_months >= 48:
            base += 1
        if entry.level in ['senior', 'staff', 'principal', 'manager', 'director']:
            base += 1
        return min(base, 3)

    def _select_scenario_type(self, entry: CareerChronologyEntry, index: int,
                               competencies: CompetencyProfile) -> str:
        """Select appropriate scenario type for this role and index."""
        # Primary type based on role
        if entry.role_type == 'management':
            types = ['leadership', 'project', 'process-improvement']
        elif entry.role_type == 'architecture':
            types = ['project', 'migration', 'optimization']
        elif entry.level in ['staff', 'principal']:
            types = ['project', 'optimization', 'innovation', 'migration']
        else:
            types = ['project', 'incident', 'optimization']

        # Add variety based on index
        if index == 1 and 'incident' not in types:
            types.insert(0, 'incident')
        if index == 2 and 'optimization' not in types:
            types.insert(0, 'optimization')

        return types[index % len(types)]

    def _generate_scenario(self, entry: CareerChronologyEntry,
                           employer_context: Optional[EmployerContext],
                           scenario_type: str, index: int,
                           competencies: CompetencyProfile,
                           mode: str) -> Scenario:
        """Generate a single detailed scenario."""
        template = self.SCENARIO_TEMPLATES.get(scenario_type, self.SCENARIO_TEMPLATES['project'])

        # Select business objective and scope
        biz_obj = template['business_objectives'][index % len(template['business_objectives'])]
        scope = template['scopes'][index % len(template['scopes'])]

        # Build technical environment
        tech_env = self._build_technical_environment(entry, employer_context)

        # Build architecture
        architecture = self._build_architecture(entry, employer_context, scenario_type, tech_env)

        # Determine candidate role
        candidate_role = self._determine_candidate_role(entry, scenario_type)

        # Generate individual contributions
        contributions = self._generate_contributions(entry, scenario_type, architecture, competencies)

        # Build team structure
        team_structure = self._build_team_structure(entry, scenario_type)

        # Generate implementation details
        impl_details = self._generate_implementation_details(entry, scenario_type, architecture, tech_env)

        # Generate challenges
        challenges = self._generate_challenges(entry, scenario_type, architecture)

        # Generate outcomes
        outcomes = self._generate_outcomes(entry, scenario_type, challenges, mode)

        # Evidence classification
        evidence = self._classify_evidence(entry, scenario_type, mode)

        scenario = Scenario(
            id=f"{entry.employer}_{scenario_type}_{index}",
            title=f"{scenario_type.title()}: {biz_obj[:50]}",
            type=scenario_type,
            employer=entry.employer,
            period=f"{entry.start_date} - {entry.end_date}",
            business_objective=biz_obj,
            scope=scope,
            technical_environment=tech_env,
            architecture=architecture,
            candidate_role=candidate_role,
            individual_contributions=contributions,
            team_structure=team_structure,
            implementation_details=impl_details,
            challenges=challenges,
            outcomes=outcomes,
            evidence_classification=evidence,
            followup_resilience=self._calculate_resilience(scenario_type, architecture),
            status="simulated" if mode == "immersive" else "enriched",
        )

        return scenario

    def _build_technical_environment(self, entry: CareerChronologyEntry,
                                      employer_context: Optional[EmployerContext]) -> dict:
        """Build technical environment for scenario."""
        env = {
            'primary_technologies': entry.technologies[:10],
            'infrastructure': 'cloud',
            'scale': {},
            'dependencies': [],
            'legacy_constraints': [],
        }

        if employer_context:
            env['infrastructure'] = employer_context.technology_context.get('infrastructure', 'cloud')
            env['primary_technologies'] = list(set(
                entry.technologies + employer_context.technology_context.get('primary_stack', [])[:5]
            ))[:10]

        # Infer scale from role and industry
        industry_profile = self.industry_model.get_profile(entry.industry)
        env['scale'] = self._infer_scale(entry, industry_profile)

        return env

    def _infer_scale(self, entry: CareerChronologyEntry, industry_profile) -> dict:
        """Infer scale metrics from role and industry."""
        scale = {}

        # Base scale by seniority and industry
        if entry.level in ['staff', 'principal', 'director', 'vp']:
            scale = {
                'services': 20,
                'team_size': 15,
                'requests_per_second': 50000,
                'data_volume_tb': 100,
                'regions': 3,
            }
        elif entry.level in ['senior', 'manager']:
            scale = {
                'services': 10,
                'team_size': 8,
                'requests_per_second': 10000,
                'data_volume_tb': 20,
                'regions': 2,
            }
        else:
            scale = {
                'services': 5,
                'team_size': 5,
                'requests_per_second': 5000,
                'data_volume_tb': 5,
                'regions': 1,
            }

        # Adjust for industry
        if entry.industry in ['cloud', 'social', 'fintech']:
            scale['requests_per_second'] *= 5
            scale['data_volume_tb'] *= 3

        return scale

    def _build_architecture(self, entry: CareerChronologyEntry,
                            employer_context: Optional[EmployerContext],
                            scenario_type: str, tech_env: dict) -> dict:
        """Build architecture for scenario."""
        # Select architecture pattern based on scenario type and industry
        patterns = {
            'project': ['microservices', 'modular_monolith', 'event_driven'],
            'incident': ['microservices', 'distributed_monolith'],
            'migration': ['strangler_fig', 'parallel_run', 'big_bang'],
            'optimization': ['microservices', 'layered_architecture'],
        }

        pattern = patterns.get(scenario_type, ['microservices'])[0]

        # Build components
        components = self._build_components(entry, pattern, tech_env)

        return {
            'pattern': pattern,
            'components': components,
            'data_flow': self._describe_data_flow(pattern, components),
            'key_decisions': self._generate_key_decisions(pattern, entry, tech_env),
            'tradeoffs': self._generate_tradeoffs(pattern, entry),
        }

    def _build_components(self, entry: CareerChronologyEntry, pattern: str, tech_env: dict) -> list:
        """Build architecture components."""
        components = []

        # Core service components based on pattern
        if pattern == 'microservices':
            component_types = [
                ('api_gateway', 'API Gateway', 'Kong/Envoy/AWS API Gateway', 'Traffic routing, auth, rate limiting'),
                ('auth_service', 'Auth Service', 'Go/Node.js', 'Authentication, authorization, token management'),
                ('user_service', 'User Service', 'Java/Go', 'User profiles, preferences, account management'),
                ('core_service', 'Core Business Service', entry.technologies[0] if entry.technologies else 'Java', 'Primary business logic'),
                ('data_service', 'Data Service', 'Python/Go', 'Data processing, analytics, reporting'),
                ('notification_service', 'Notification Service', 'Node.js/Go', 'Email, push, SMS notifications'),
            ]
        elif pattern == 'modular_monolith':
            component_types = [
                ('web_module', 'Web Module', entry.technologies[0] if entry.technologies else 'Python', 'HTTP handlers, routing'),
                ('domain_module', 'Domain Module', entry.technologies[0] if entry.technologies else 'Java', 'Business logic, rules'),
                ('data_module', 'Data Module', 'Python/Go', 'Database access, repositories'),
                ('integration_module', 'Integration Module', 'Java/Go', 'External API integrations'),
            ]
        else:  # event_driven
            component_types = [
                ('event_producer', 'Event Producer', 'Go/Java', 'Publishes domain events'),
                ('event_bus', 'Event Bus', 'Kafka/Pulsar', 'Event streaming backbone'),
                ('event_consumer', 'Event Consumer', 'Python/Go', 'Processes events, updates projections'),
                ('projection_service', 'Projection Service', 'Go', 'Materialized views, read models'),
            ]

        for name, comp_type, tech, responsibility in component_types:
            components.append({
                'name': name,
                'type': comp_type,
                'technology': tech,
                'responsibility': responsibility,
                'scale': self._infer_component_scale(name, tech_env),
                'dependencies': self._infer_dependencies(name, component_types),
                'configuration': self._infer_configuration(name, tech),
            })

        return components

    def _infer_component_scale(self, name: str, tech_env: dict) -> dict:
        """Infer scale for a component."""
        base_rps = tech_env.get('scale', {}).get('requests_per_second', 10000)

        scale_map = {
            'api_gateway': base_rps,
            'auth_service': base_rps * 0.3,
            'user_service': base_rps * 0.5,
            'core_service': base_rps * 0.8,
            'data_service': base_rps * 0.2,
            'notification_service': base_rps * 0.1,
            'web_module': base_rps,
            'domain_module': base_rps * 0.7,
            'data_module': base_rps * 0.3,
            'integration_module': base_rps * 0.2,
            'event_producer': base_rps,
            'event_bus': base_rps * 10,
            'event_consumer': base_rps * 2,
            'projection_service': base_rps * 0.5,
        }

        rps = scale_map.get(name, base_rps * 0.3)
        return {
            'requests_per_second': int(rps),
            'instances': max(3, int(rps / 1000)),
            'cpu_cores': 4,
            'memory_gb': 8,
        }

    def _infer_dependencies(self, name: str, all_components: list) -> list:
        """Infer component dependencies."""
        dep_map = {
            'api_gateway': ['auth_service', 'core_service'],
            'auth_service': [],
            'user_service': ['auth_service'],
            'core_service': ['user_service', 'data_service', 'notification_service'],
            'data_service': [],
            'notification_service': [],
            'web_module': ['domain_module'],
            'domain_module': ['data_module', 'integration_module'],
            'data_module': [],
            'integration_module': [],
            'event_producer': ['event_bus'],
            'event_bus': [],
            'event_consumer': ['event_bus'],
            'projection_service': ['event_bus'],
        }
        return dep_map.get(name, [])

    def _infer_configuration(self, name: str, tech: str) -> dict:
        """Infer component configuration."""
        configs = {
            'api_gateway': {'rate_limit': '10000/min', 'timeout': '30s', 'circuit_breaker': True},
            'auth_service': {'token_ttl': '1h', 'refresh_ttl': '7d', 'algorithm': 'RS256'},
            'core_service': {'thread_pool': '200', 'db_pool': '50', 'cache_ttl': '5m'},
            'data_service': {'batch_size': '1000', 'parallelism': '8', 'checkpoint_interval': '1m'},
        }
        return configs.get(name, {})

    def _describe_data_flow(self, pattern: str, components: list) -> str:
        """Describe data flow for architecture."""
        if pattern == 'microservices':
            return "Client → API Gateway → Auth Service → Core Service → (Data Service / Notification Service) → Response"
        elif pattern == 'modular_monolith':
            return "HTTP Request → Web Module → Domain Module → Data Module → Database → Response"
        else:
            return "Event Producer → Event Bus → Event Consumers → Projection Services → Read Models"

    def _generate_key_decisions(self, pattern: str, entry: CareerChronologyEntry, tech_env: dict) -> list:
        """Generate key architectural decisions."""
        decisions = []

        # Pattern-specific decisions
        if pattern == 'microservices':
            decisions.append({
                'decision': 'Adopted microservices over modular monolith',
                'alternatives': ['Modular monolith', 'Serverless functions'],
                'rationale': 'Independent deployability and team autonomy required for scaling',
                'tradeoffs': ['Operational complexity', 'Network latency', 'Distributed debugging'],
            })

        # Technology decisions
        if entry.technologies:
            primary = entry.technologies[0]
            decisions.append({
                'decision': f'Selected {primary} as primary language',
                'alternatives': ['Go', 'Java', 'Node.js', 'Python'],
                'rationale': f'Team expertise and ecosystem fit for {entry.industry} domain',
                'tradeoffs': ['Hiring pool', 'Library maturity', 'Performance characteristics'],
            })

        # Infrastructure decisions
        decisions.append({
            'decision': 'Deployed on Kubernetes with GitOps',
            'alternatives': ['ECS', 'VMs', 'Serverless', 'Bare metal'],
            'rationale': 'Portability, ecosystem, and team familiarity',
            'tradeoffs': ['Complexity', 'Learning curve', 'Resource overhead'],
        })

        return decisions

    def _generate_tradeoffs(self, pattern: str, entry: CareerChronologyEntry) -> list:
        """Generate architectural tradeoffs."""
        tradeoffs = [
            'Consistency vs Availability: Chose eventual consistency for write-heavy paths',
            'Latency vs Cost: Accepted 10ms overhead for managed services',
            'Build vs Buy: Used managed Kafka vs self-hosted for operational simplicity',
            'Sync vs Async: Moved notification paths to async for resilience',
        ]
        return tradeoffs

    def _determine_candidate_role(self, entry: CareerChronologyEntry, scenario_type: str) -> str:
        """Determine candidate's role in scenario."""
        role_map = {
            ('project', 'junior'): 'Implementing engineer',
            ('project', 'mid'): 'Feature lead engineer',
            ('project', 'senior'): 'Technical lead',
            ('project', 'staff'): 'Architect/Tech lead',
            ('project', 'principal'): 'Principal architect',
            ('incident', 'junior'): 'On-call responder',
            ('incident', 'mid'): 'Incident commander',
            ('incident', 'senior'): 'Incident commander / Root cause owner',
            ('incident', 'staff'): 'Incident commander / Cross-team coordination',
            ('migration', 'junior'): 'Migration engineer',
            ('migration', 'mid'): 'Migration lead',
            ('migration', 'senior'): 'Migration architect',
            ('migration', 'staff'): 'Program lead',
            ('optimization', 'junior'): 'Performance engineer',
            ('optimization', 'mid'): 'Optimization lead',
            ('optimization', 'senior'): 'Performance architect',
            ('optimization', 'staff'): 'Platform optimization lead',
        }
        return role_map.get((scenario_type, entry.level), 'Contributing engineer')

    def _generate_contributions(self, entry: CareerChronologyEntry,
                                 scenario_type: str, architecture: dict,
                                 competencies: CompetencyProfile) -> list:
        """Generate individual contributions."""
        contributions = []
        role = self._determine_candidate_role(entry, scenario_type)

        # Core contributions based on role
        if 'lead' in role.lower() or 'architect' in role.lower():
            contributions.extend([
                {'action': 'Designed system architecture and component interfaces', 'ownership': 'primary', 'impact': 'Enabled parallel development by 3 teams'},
                {'action': 'Defined API contracts and data schemas', 'ownership': 'sole', 'impact': 'Reduced integration bugs by 80%'},
                {'action': 'Led technical design reviews and decision-making', 'ownership': 'primary', 'impact': 'Aligned 10+ engineers on approach'},
            ])
        else:
            contributions.extend([
                {'action': f'Implemented core {scenario_type} functionality', 'ownership': 'primary', 'impact': 'Delivered on schedule with 95% test coverage'},
                {'action': 'Wrote comprehensive integration tests', 'ownership': 'sole', 'impact': 'Caught 3 critical bugs pre-production'},
                {'action': 'Optimized critical path performance', 'ownership': 'shared', 'impact': 'Reduced p99 latency by 40%'},
            ])

        # Add scenario-specific contributions
        if scenario_type == 'incident':
            contributions.append({
                'action': 'Led incident response and root cause analysis',
                'ownership': 'primary',
                'impact': 'Restored service in 45 minutes; prevented recurrence'
            })
        elif scenario_type == 'migration':
            contributions.append({
                'action': 'Designed and executed zero-downtime migration strategy',
                'ownership': 'primary',
                'impact': 'Migrated 2TB data with zero data loss'
            })
        elif scenario_type == 'optimization':
            contributions.append({
                'action': 'Identified and resolved top 5 performance bottlenecks',
                'ownership': 'primary',
                'impact': 'Reduced infrastructure cost by 35%'
            })

        return contributions

    def _build_team_structure(self, entry: CareerChronologyEntry, scenario_type: str) -> dict:
        """Build team structure for scenario."""
        base_size = 5 if entry.level in ['junior', 'mid'] else 8
        if entry.level in ['staff', 'principal']:
            base_size = 12

        return {
            'size': base_size,
            'roles': ['Backend Engineers', 'Frontend Engineers', 'DevOps', 'QA', 'Product Manager'],
            'candidate_position': self._determine_candidate_role(entry, scenario_type),
        }

    def _generate_implementation_details(self, entry: CareerChronologyEntry,
                                          scenario_type: str, architecture: dict,
                                          tech_env: dict) -> dict:
        """Generate implementation details."""
        primary_tech = entry.technologies[0] if entry.technologies else 'Java'

        return {
            'key_configurations': [
                f'{primary_tech} service config: thread pools, connection pools, timeouts',
                'Kubernetes: resource limits, HPA, pod disruption budgets',
                'Database: connection pooling, read replicas, partitioning',
                'Cache: TTL strategies, invalidation patterns, warming',
            ],
            'algorithms_approaches': [
                'Circuit breaker pattern for downstream resilience',
                'Idempotency keys for safe retries',
                'Event sourcing for audit trail',
                'CQRS for read/write separation',
            ],
            'testing_strategy': 'Unit (80%+), Integration (contract tests), Load (k6), Chaos (Litmus)',
            'deployment_approach': 'Blue-green with canary analysis, feature flags',
            'monitoring_observability': ['Distributed tracing (Jaeger)', 'Metrics (Prometheus/Grafana)', 'Logging (ELK)', 'Alerting (PagerDuty)'],
            'security_measures': ['mTLS between services', 'OAuth2/OIDC', 'Secrets in Vault', 'Regular SAST/DAST'],
        }

    def _generate_challenges(self, entry: CareerChronologyEntry,
                              scenario_type: str, architecture: dict) -> list:
        """Generate realistic challenges."""
        challenges = []

        if scenario_type == 'project':
            challenges.extend([
                {'description': 'Integration with legacy system lacking APIs', 'root_cause': 'No documentation, original team gone', 'resolution': 'Built adapter layer with contract tests', 'candidate_involvement': 'Designed and implemented adapter'},
                {'description': 'Cross-team dependency blocking delivery', 'root_cause': 'Misaligned priorities and timelines', 'resolution': 'Negotiated API-first contract, parallel development with mocks', 'candidate_involvement': 'Led negotiation and technical solution'},
            ])
        elif scenario_type == 'incident':
            challenges.extend([
                {'description': 'Cascading failure from database connection leak', 'root_cause': 'Connection pool exhaustion under retry storm', 'resolution': 'Implemented circuit breaker, fixed leak, added pool monitoring', 'candidate_involvement': 'Identified root cause, implemented fix'},
                {'description': 'Insufficient observability during incident', 'root_cause': 'Missing distributed tracing and custom metrics', 'resolution': 'Added OpenTelemetry instrumentation, created runbook', 'candidate_involvement': 'Championed observability investment'},
            ])
        elif scenario_type == 'migration':
            challenges.extend([
                {'description': 'Data consistency during dual-write phase', 'root_cause': 'Race conditions between old and new systems', 'resolution': 'Implemented change data capture with reconciliation jobs', 'candidate_involvement': 'Designed CDC pipeline and verification'},
                {'description': 'Performance regression in new system', 'root_cause': 'Unoptimized queries and missing indexes', 'resolution': 'Query optimization, index tuning, caching layer', 'candidate_involvement': 'Led performance investigation and tuning'},
            ])
        elif scenario_type == 'optimization':
            challenges.extend([
                {'description': 'Identifying true bottlenecks in distributed system', 'root_cause': 'Symptoms appeared in downstream services', 'resolution': 'Distributed tracing revealed upstream latency', 'candidate_involvement': 'Analyzed traces, identified root cause'},
                {'description': 'Balancing optimization with feature delivery', 'root_cause': 'Product pressure to ship features', 'resolution': 'Allocated 20% capacity for tech debt, measured ROI', 'candidate_involvement': 'Negotiated capacity, tracked metrics'},
            ])

        return challenges

    def _generate_outcomes(self, entry: CareerChronologyEntry,
                            scenario_type: str, challenges: list, mode: str) -> dict:
        """Generate outcomes with metrics."""
        outcomes = {
            'metrics': [],
            'business_impact': '',
            'technical_improvements': [],
            'lessons_learned': [],
        }

        # Generate metrics based on scenario type
        if scenario_type == 'project':
            outcomes['metrics'] = [
                'Delivered on schedule (12 weeks)',
                '99.9% uptime in first month',
                'p99 latency < 200ms',
                'Zero critical bugs post-launch',
            ]
            outcomes['business_impact'] = 'Enabled new revenue stream projecting $2M ARR'
            outcomes['technical_improvements'] = ['Improved deployment frequency 5x', 'Reduced MTTR from 60min to 15min']
            outcomes['lessons_learned'] = ['Invest in contract testing early', 'Cross-team alignment requires explicit contracts']

        elif scenario_type == 'incident':
            outcomes['metrics'] = [
                'MTTR: 45 minutes (target < 60)',
                'Zero data loss',
                'RCA completed within 24 hours',
                'Preventive measures deployed in 1 week',
            ]
            outcomes['business_impact'] = 'Prevented estimated $500K revenue loss per incident'
            outcomes['technical_improvements'] = ['Added circuit breakers', 'Improved observability', 'Created runbooks']
            outcomes['lessons_learned'] = ['Observability is not optional', 'Retry storms need circuit breakers', 'Runbooks must be tested']

        elif scenario_type == 'migration':
            outcomes['metrics'] = [
                'Zero-downtime migration completed',
                'Data consistency verified: 99.999%',
                'Performance improved 2x',
                'Cost reduced 30%',
            ]
            outcomes['business_impact'] = 'Enabled cloud-native capabilities, reduced ops burden'
            outcomes['technical_improvements'] = ['Modern stack', 'Auto-scaling', 'Better observability']
            outcomes['lessons_learned'] = ['Parallel run is essential', 'Invest in verification tooling', 'Communicate aggressively']

        elif scenario_type == 'optimization':
            outcomes['metrics'] = [
                'Latency reduced 60% (p99: 500ms → 200ms)',
                'Throughput increased 3x',
                'Infrastructure cost reduced 35%',
                'Error rate reduced 80%',
            ]
            outcomes['business_impact'] = 'Supported 10x traffic growth without proportional cost increase'
            outcomes['technical_improvements'] = ['Caching strategy', 'Query optimization', 'Resource right-sizing']
            outcomes['lessons_learned'] = ['Measure before optimizing', 'Focus on highest ROI changes', 'Automate performance regression detection']

        return outcomes

    def _classify_evidence(self, entry: CareerChronologyEntry,
                           scenario_type: str, mode: str) -> dict:
        """Classify evidence for scenario elements."""
        if mode == "authentic":
            return {
                'documented_elements': [f'{scenario_type} at {entry.employer}'],
                'confirmed_elements': [],
                'inferred_elements': ['Specific technical details', 'Exact metrics', 'Challenge descriptions'],
                'simulated_elements': [],
            }
        else:
            return {
                'documented_elements': [f'{entry.title} at {entry.employer}'],
                'confirmed_elements': [],
                'inferred_elements': ['Technology choices based on resume', 'Scale inferred from role'],
                'simulated_elements': [
                    'Specific architecture details',
                    'Exact numerical metrics',
                    'Challenge narratives',
                    'Implementation specifics',
                    'Conversation details',
                ],
            }

    def _calculate_resilience(self, scenario_type: str, architecture: dict) -> float:
        """Calculate followup resilience score (0-1)."""
        base = 0.7
        # More components = more followup depth possible
        component_count = len(architecture.get('components', []))
        base += min(component_count * 0.02, 0.2)
        # Complex patterns = more depth
        if architecture.get('pattern') in ['microservices', 'event_driven']:
            base += 0.1
        return min(base, 1.0)