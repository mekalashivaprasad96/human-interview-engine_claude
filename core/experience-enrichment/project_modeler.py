"""
Project Modeler - Builds detailed project models with consistent architecture and numerical data.
"""

from dataclasses import dataclass, field
from typing import Optional
from ..candidate_intelligence.career_chronology import CareerChronologyEntry
from .scenario_generator import ScenarioGenerator


@dataclass
class ProjectModel:
    project_id: str
    name: str
    employer: str
    period: str
    scenario_type: str
    architecture: dict = field(default_factory=dict)
    numerical_model: dict = field(default_factory=dict)
    timeline: list = field(default_factory=list)
    team: dict = field(default_factory=dict)
    technologies: dict = field(default_factory=dict)
    outcomes: dict = field(default_factory=dict)
    consistency_rules: list = field(default_factory=list)


class ProjectModeler:
    """Builds detailed, consistent project models from scenarios."""

    def __init__(self):
        self.scenario_generator = ScenarioGenerator()

    def build_from_scenario(self, scenario, entry: CareerChronologyEntry) -> ProjectModel:
        """Build a detailed project model from a scenario."""
        model = ProjectModel(
            project_id=scenario.id,
            name=scenario.title,
            employer=scenario.employer,
            period=scenario.period,
            scenario_type=scenario.type,
        )

        # Architecture (from scenario)
        model.architecture = scenario.architecture

        # Numerical model (enhanced with consistency)
        model.numerical_model = self._build_numerical_model(scenario, entry)

        # Timeline
        model.timeline = self._build_timeline(scenario, entry)

        # Team
        model.team = self._build_team_model(scenario, entry)

        # Technologies
        model.technologies = self._build_technology_model(scenario, entry)

        # Outcomes
        model.outcomes = scenario.outcomes

        # Consistency rules
        model.consistency_rules = self._derive_consistency_rules(model)

        return model

    def _build_numerical_model(self, scenario, entry: CareerChronologyEntry) -> dict:
        """Build consistent numerical model for project."""
        arch = scenario.architecture
        tech_env = scenario.technical_environment
        scale = tech_env.get('scale', {})

        # Base scale from architecture
        services = len(arch.get('components', []))
        base_rps = scale.get('requests_per_second', 10000)
        base_data_tb = scale.get('data_volume_tb', 10)

        # Compute model
        compute = self._build_compute_model(entry, services, base_rps)

        # Throughput model
        throughput = {
            'requests_per_second': base_rps,
            'peak_rps': int(base_rps * 3),
            'daily_requests': int(base_rps * 86400 * 0.3),  # 30% utilization average
            'data_volume_tb_per_day': base_data_tb / 30,
        }

        # Latency model
        latency = {
            'p50_ms': 50,
            'p95_ms': 200,
            'p99_ms': 500,
            'baseline_p50_ms': 150,
            'improvement_pct': 67,
        }

        # Availability model
        availability = {
            'target_pct': 99.99,
            'actual_pct': 99.95,
            'downtime_minutes_per_month': 4.3,
            'incidents_per_month': 2,
            'mttr_minutes': 30,
        }

        # Cost model
        cost = {
            'monthly_usd': compute['nodes'] * 500,  # Rough estimate
            'cost_per_request': 0.00001,
            'optimization_savings_pct': 30,
        }

        # Team metrics
        team_metrics = {
            'team_size': scenario.team_structure.get('size', 5),
            'on_call_rotation': max(3, scenario.team_structure.get('size', 5) // 2),
            'deploys_per_week': 10,
            'lead_time_hours': 4,
        }

        return {
            'compute': compute,
            'throughput': throughput,
            'latency': latency,
            'availability': availability,
            'cost': cost,
            'team_metrics': team_metrics,
        }

    def _build_compute_model(self, entry: CareerChronologyEntry, services: int, base_rps: int) -> dict:
        """Build compute infrastructure model."""
        # Determine node count based on scale and seniority
        if entry.level in ['staff', 'principal', 'director']:
            nodes = 50
        elif entry.level in ['senior', 'manager']:
            nodes = 20
        else:
            nodes = 10

        # GPUs for ML workloads
        gpus_per_node = 0
        if any('ml' in t.lower() or 'ai' in t.lower() or 'gpu' in t.lower() for t in entry.technologies):
            gpus_per_node = 4 if nodes > 20 else 8

        return {
            'nodes': nodes,
            'cpus_per_node': 32,
            'memory_per_node_gb': 128,
            'gpus_per_node': gpus_per_node,
            'total_gpus': nodes * gpus_per_node,
            'gpu_type': 'A100' if gpus_per_node > 0 else 'N/A',
        }

    def _build_timeline(self, scenario, entry: CareerChronologyEntry) -> list:
        """Build project timeline."""
        duration_weeks = entry.duration_months * 4
        if scenario.type == 'incident':
            duration_weeks = 1  # Incident response is short
        elif scenario.type == 'migration':
            duration_weeks = max(duration_weeks, 24)

        phases = []
        if scenario.type == 'project':
            phases = [
                {'name': 'Design & Planning', 'duration_weeks': max(2, duration_weeks // 6), 'deliverables': ['Architecture doc', 'API contracts', 'Task breakdown']},
                {'name': 'Core Implementation', 'duration_weeks': max(4, duration_weeks // 2), 'deliverables': ['Core services', 'Database schema', 'Basic tests']},
                {'name': 'Integration & Testing', 'duration_weeks': max(2, duration_weeks // 4), 'deliverables': ['Integration tests', 'Load tests', 'Documentation']},
                {'name': 'Rollout & Stabilization', 'duration_weeks': max(2, duration_weeks // 6), 'deliverables': ['Canary deployment', 'Full rollout', 'Runbooks']},
            ]
        elif scenario.type == 'migration':
            phases = [
                {'name': 'Assessment & Planning', 'duration_weeks': 4, 'deliverables': ['Migration plan', 'Risk assessment', 'Tooling']},
                {'name': 'Parallel Run Setup', 'duration_weeks': 6, 'deliverables': ['Dual-write', 'CDC pipeline', 'Reconciliation']},
                {'name': 'Gradual Migration', 'duration_weeks': max(8, duration_weeks - 10), 'deliverables': ['Service-by-service cutover', 'Validation']},
                {'name': 'Decommission', 'duration_weeks': 2, 'deliverables': ['Legacy shutdown', 'Cost savings verification']},
            ]
        elif scenario.type == 'optimization':
            phases = [
                {'name': 'Profiling & Analysis', 'duration_weeks': 2, 'deliverables': ['Bottleneck report', 'Baseline metrics']},
                {'name': 'Quick Wins', 'duration_weeks': 2, 'deliverables': ['Config tuning', 'Index fixes', 'Cache fixes']},
                {'name': 'Deep Optimization', 'duration_weeks': max(4, duration_weeks - 4), 'deliverables': ['Architecture changes', 'Algorithm improvements']},
                {'name': 'Validation', 'duration_weeks': 2, 'deliverables': ['Load tests', 'Regression tests', 'Documentation']},
            ]
        else:
            phases = [
                {'name': 'Phase 1', 'duration_weeks': duration_weeks // 2, 'deliverables': ['Milestone 1']},
                {'name': 'Phase 2', 'duration_weeks': duration_weeks - duration_weeks // 2, 'deliverables': ['Milestone 2']},
            ]

        # Add candidate ownership
        for phase in phases:
            phase['candidate_ownership'] = 'primary' if 'Lead' in scenario.candidate_role or 'Architect' in scenario.candidate_role else 'shared'

        return phases

    def _build_team_model(self, scenario, entry: CareerChronologyEntry) -> dict:
        """Build detailed team model."""
        size = scenario.team_structure.get('size', 5)

        return {
            'total_size': size,
            'composition': {
                'backend_engineers': max(2, size // 2),
                'frontend_engineers': max(1, size // 3),
                'devops': max(1, size // 5),
                'qa': max(1, size // 6),
                'product_manager': 1,
                'designer': 1 if size > 6 else 0,
            },
            'candidate_role': scenario.candidate_role,
            'candidate_level': entry.level,
            'reporting_structure': 'flat' if size < 8 else 'hierarchical',
        }

    def _build_technology_model(self, scenario, entry: CareerChronologyEntry) -> dict:
        """Build detailed technology model."""
        tech_env = scenario.technical_environment

        return {
            'languages': self._extract_by_category(entry.technologies, 'languages'),
            'frameworks': self._extract_by_category(entry.technologies, 'frameworks'),
            'databases': self._extract_by_category(entry.technologies, 'databases'),
            'messaging': self._extract_by_category(entry.technologies, 'messaging'),
            'infrastructure': self._extract_by_category(entry.technologies, 'infrastructure'),
            'monitoring': self._extract_by_category(entry.technologies, 'monitoring'),
            'ci_cd': self._extract_by_category(entry.technologies, 'ci_cd'),
            'versions': self._infer_versions(entry.technologies, entry.period),
        }

    def _extract_by_category(self, technologies: list, category: str) -> list:
        """Extract technologies by category."""
        categories = {
            'languages': ['python', 'java', 'javascript', 'typescript', 'go', 'rust', 'c++', 'c#', 'ruby', 'scala', 'kotlin', 'swift', 'php'],
            'frameworks': ['react', 'vue', 'angular', 'django', 'flask', 'fastapi', 'spring', 'express', 'nestjs', 'gin', 'rails'],
            'databases': ['postgresql', 'mysql', 'mongodb', 'redis', 'cassandra', 'dynamodb', 'elasticsearch', 'snowflake', 'bigquery'],
            'messaging': ['kafka', 'rabbitmq', 'nats', 'pulsar', 'grpc', 'graphql', 'rest', 'websocket'],
            'infrastructure': ['aws', 'azure', 'gcp', 'kubernetes', 'docker', 'terraform', 'ansible', 'helm'],
            'monitoring': ['prometheus', 'grafana', 'datadog', 'new relic', 'jaeger', 'zipkin', 'opentelemetry'],
            'ci_cd': ['jenkins', 'gitlab', 'github actions', 'circleci', 'argocd', 'flux', 'spinnaker'],
        }

        cat_techs = categories.get(category, [])
        return [t for t in technologies if any(ct in t.lower() for ct in cat_techs)]

    def _infer_versions(self, technologies: list, period: str) -> dict:
        """Infer likely versions based on employment period."""
        # Extract end year
        import re
        year_match = re.search(r'(20\d{2})', period)
        end_year = int(year_match.group(1)) if year_match else 2024

        versions = {}
        version_map = {
            'python': {2018: '3.6', 2020: '3.8', 2022: '3.10', 2024: '3.12'},
            'java': {2018: '11', 2020: '11/14', 2022: '17', 2024: '21'},
            'node.js': {2018: '10', 2020: '14', 2022: '18', 2024: '20'},
            'go': {2018: '1.11', 2020: '1.15', 2022: '1.19', 2024: '1.22'},
            'kubernetes': {2018: '1.11', 2020: '1.18', 2022: '1.24', 2024: '1.29'},
            'react': {2018: '16', 2020: '17', 2022: '18', 2024: '18'},
        }

        for tech in technologies:
            tech_lower = tech.lower()
            for key, version_timeline in version_map.items():
                if key in tech_lower:
                    # Find closest version
                    closest_year = max([y for y in version_timeline.keys() if y <= end_year], default=min(version_timeline.keys()))
                    versions[tech] = version_timeline[closest_year]
                    break

        return versions

    def _derive_consistency_rules(self, model: ProjectModel) -> list:
        """Derive consistency rules for this project model."""
        rules = []

        # Compute rules
        compute = model.numerical_model.get('compute', {})
        if compute.get('nodes') and compute.get('gpus_per_node'):
            rules.append(f"total_gpus = nodes * gpus_per_node = {compute['nodes']} * {compute['gpus_per_node']} = {compute['nodes'] * compute['gpus_per_node']}")

        # Throughput rules
        throughput = model.numerical_model.get('throughput', {})
        if throughput.get('requests_per_second') and throughput.get('daily_requests'):
            expected_daily = throughput['requests_per_second'] * 86400 * 0.3
            actual_daily = throughput['daily_requests']
            if abs(expected_daily - actual_daily) / expected_daily < 0.5:
                rules.append(f"daily_requests ≈ rps * 86400 * 0.3 = {expected_daily:,.0f}")

        # Availability rules
        avail = model.numerical_model.get('availability', {})
        if avail.get('target_pct') and avail.get('downtime_minutes_per_month'):
            expected_downtime = (100 - avail['target_pct']) / 100 * 43200  # minutes per month
            rules.append(f"target_availability {avail['target_pct']}% → max {expected_downtime:.1f} min/month downtime")

        # Team rules
        team = model.team
        if team.get('total_size') and team.get('composition'):
            comp_sum = sum(v for v in team['composition'].values() if isinstance(v, int))
            if comp_sum == team['total_size']:
                rules.append(f"Team composition sums to total: {comp_sum}")

        return rules