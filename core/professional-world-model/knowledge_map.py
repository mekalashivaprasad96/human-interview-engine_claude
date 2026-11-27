"""
Knowledge Map Builder - Maps candidate's technical and business knowledge across domains.
"""

from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict
from ..candidate_intelligence.career_chronology import CareerChronologyEntry
from ..candidate_intelligence.competency_mapper import CompetencyProfile


@dataclass
class KnowledgeMap:
    technical_domains: dict = field(default_factory=dict)
    business_domains: dict = field(default_factory=dict)
    cross_domain_connections: list = field(default_factory=list)


class KnowledgeMapBuilder:
    """Builds comprehensive knowledge map from career and competency data."""

    DEPTH_LEVELS = ['surface', 'working', 'deep', 'expert']
    SOURCE_TYPES = ['direct_experience', 'adjacent_experience', 'study', 'transferable']

    def build(self, chronology_entries: list[CareerChronologyEntry],
              competencies: CompetencyProfile) -> KnowledgeMap:
        """Build knowledge map from career and competency data."""
        knowledge_map = KnowledgeMap()

        # Build technical domains
        knowledge_map.technical_domains = self._build_technical_domains(
            chronology_entries, competencies
        )

        # Build business domains
        knowledge_map.business_domains = self._build_business_domains(
            chronology_entries, competencies
        )

        # Build cross-domain connections
        knowledge_map.cross_domain_connections = self._build_cross_domain_connections(
            knowledge_map.technical_domains, knowledge_map.business_domains, chronology_entries
        )

        return knowledge_map

    def _build_technical_domains(self, chronology_entries: list[CareerChronologyEntry],
                                  competencies: CompetencyProfile) -> dict:
        """Build technical domain knowledge map."""
        domains = {}

        # Aggregate technology usage across career
        tech_usage = defaultdict(lambda: {
            'total_months': 0,
            'contexts': set(),
            'roles': set(),
            'recency_months': 0,
        })

        current_time = 0  # Would be actual current time in months
        for entry in chronology_entries:
            for tech in entry.technologies:
                tech_lower = tech.lower()
                tech_usage[tech_lower]['total_months'] += entry.duration_months
                tech_usage[tech_lower]['contexts'].add(entry.employer)
                tech_usage[tech_lower]['roles'].add(entry.title)
                # Recency: months since last used (simplified)
                tech_usage[tech_lower]['recency_months'] = min(
                    tech_usage[tech_lower]['recency_months'] or 999,
                    0  # Current role
                )

        # Also include skills from competencies
        for level in ['core', 'proficient', 'familiar']:
            for tech in competencies.technical.get(level, []):
                tech_lower = tech.lower()
                if tech_lower not in tech_usage:
                    tech_usage[tech_lower] = {
                        'total_months': 0,
                        'contexts': set(),
                        'roles': set(),
                        'recency_months': 0,
                    }
                # Boost based on declared proficiency
                if level == 'core':
                    tech_usage[tech_lower]['total_months'] += 36
                elif level == 'proficient':
                    tech_usage[tech_lower]['total_months'] += 18

        # Determine depth for each technology
        for tech, data in tech_usage.items():
            domain = self._categorize_technology(tech)
            if domain not in domains:
                domains[domain] = {}

            depth = self._calculate_depth(data)
            source = self._determine_source(data, chronology_entries)

            domains[domain][tech] = {
                'depth': depth,
                'source': source,
                'last_used': 'current' if data['recency_months'] == 0 else f"{data['recency_months']} months ago",
                'project_contexts': list(data['contexts']),
                'total_experience_months': data['total_months'],
            }

        return domains

    def _build_business_domains(self, chronology_entries: list[CareerChronologyEntry],
                                 competencies: CompetencyProfile) -> dict:
        """Build business domain knowledge map."""
        domains = {}

        # From competencies
        for domain in competencies.business.get('domains', []):
            depth = 'working'
            if competencies.business.get('strategic_planning'):
                depth = 'deep'
            if competencies.business.get('p_l_responsibility'):
                depth = 'expert'

            domains[domain] = {
                'depth': depth,
                'source': 'direct_experience',
                'customer_facing': competencies.business.get('customer_facing', False),
                'contexts': list(set(e.industry for e in chronology_entries if e.industry.lower() == domain.lower())),
            }

        # From industry experience
        industry_exposure = defaultdict(int)
        for entry in chronology_entries:
            industry_exposure[entry.industry.lower()] += entry.duration_months

        for industry, months in industry_exposure.items():
            if industry not in domains:
                depth = 'awareness'
                if months >= 36:
                    depth = 'deep'
                elif months >= 12:
                    depth = 'working'

                domains[industry] = {
                    'depth': depth,
                    'source': 'direct_experience',
                    'customer_facing': False,
                    'contexts': [e.employer for e in chronology_entries if e.industry.lower() == industry],
                }

        return domains

    def _build_cross_domain_connections(self, tech_domains: dict, business_domains: dict,
                                         chronology_entries: list[CareerChronologyEntry]) -> list:
        """Build connections between technical and business domains."""
        connections = []

        # Known strong connections
        known_connections = {
            ('cloud', 'fintech'): ('cloud_native_finance', 'strong'),
            ('cloud', 'healthcare'): ('compliant_cloud', 'strong'),
            ('ml_ai', 'ecommerce'): ('personalization_ml', 'strong'),
            ('ml_ai', 'fintech'): ('fraud_detection_ml', 'strong'),
            ('data', 'fintech'): ('financial_data_platform', 'strong'),
            ('data', 'healthcare'): ('clinical_data_platform', 'strong'),
            ('security', 'fintech'): ('financial_security', 'strong'),
            ('security', 'healthcare'): ('hipaa_security', 'strong'),
            ('frontend', 'ecommerce'): ('conversion_optimization', 'moderate'),
            ('messaging', 'cloud'): ('event_driven_architecture', 'moderate'),
            ('monitoring', 'cloud'): ('observability_platform', 'moderate'),
        }

        candidate_tech_domains = set(tech_domains.keys())
        candidate_biz_domains = set(business_domains.keys())

        for (tech, biz), (conn_type, strength) in known_connections.items():
            if tech in candidate_tech_domains and biz in candidate_biz_domains:
                connections.append({
                    'from_domain': tech,
                    'to_domain': biz,
                    'connection_type': conn_type,
                    'strength': strength,
                })

        # Infer from actual projects
        for entry in chronology_entries:
            tech_doms = set()
            for tech in entry.technologies:
                cat = self._categorize_technology(tech.lower())
                tech_doms.add(cat)

            biz_dom = entry.industry.lower()

            for tech_dom in tech_doms:
                if tech_dom in candidate_tech_domains and biz_dom in candidate_biz_domains:
                    # Check if already exists
                    exists = any(c['from_domain'] == tech_dom and c['to_domain'] == biz_dom
                                 for c in connections)
                    if not exists:
                        connections.append({
                            'from_domain': tech_dom,
                            'to_domain': biz_dom,
                            'connection_type': f'{tech_dom}_for_{biz_dom}',
                            'strength': 'moderate',
                        })

        return connections

    def _categorize_technology(self, tech: str) -> str:
        """Categorize technology into domain."""
        tech_lower = tech.lower()

        categories = {
            'languages': ['python', 'java', 'javascript', 'typescript', 'go', 'rust', 'c++', 'c#', 'ruby', 'scala', 'kotlin'],
            'frontend': ['react', 'vue', 'angular', 'svelte', 'next.js', 'webpack', 'vite', 'css', 'html', 'tailwind'],
            'backend': ['node.js', 'django', 'flask', 'fastapi', 'spring', 'gin', 'express', 'nestjs'],
            'databases': ['postgresql', 'mysql', 'mongodb', 'redis', 'cassandra', 'dynamodb', 'elasticsearch', 'snowflake'],
            'cloud': ['aws', 'azure', 'gcp', 'cloudflare', 'ec2', 'lambda', 's3', 'rds', 'fargate', 'cloudformation'],
            'containerization': ['docker', 'kubernetes', 'k8s', 'helm', 'istio', 'openshift', 'containerd', 'podman'],
            'infrastructure': ['terraform', 'ansible', 'pulumi', 'argocd', 'flux', 'jenkins', 'github actions', 'gitlab ci'],
            'messaging': ['kafka', 'rabbitmq', 'nats', 'pulsar', 'grpc', 'protobuf', 'graphql', 'rest', 'websocket'],
            'monitoring': ['prometheus', 'grafana', 'datadog', 'new relic', 'elastic', 'jaeger', 'zipkin', 'opentelemetry'],
            'ml_ai': ['tensorflow', 'pytorch', 'scikit-learn', 'xgboost', 'hugging face', 'transformers', 'langchain', 'mlflow', 'spark'],
            'security': ['oauth', 'oidc', 'saml', 'jwt', 'vault', 'cert-manager', 'opa', 'falco', 'trivy', 'snyk'],
            'data': ['spark', 'flink', 'airflow', 'dbt', 'kafka', 'hadoop', 'hive', 'presto', 'trino', 'delta lake'],
        }

        for category, techs in categories.items():
            for t in techs:
                if t in tech_lower or tech_lower in t:
                    return category

        return 'other'

    def _calculate_depth(self, data: dict) -> str:
        """Calculate depth level from usage data."""
        months = data['total_months']
        contexts = len(data['contexts'])

        if months >= 36 and contexts >= 2:
            return 'expert'
        elif months >= 24 or (months >= 12 and contexts >= 2):
            return 'deep'
        elif months >= 6 or contexts >= 2:
            return 'working'
        return 'surface'

    def _determine_source(self, data: dict, chronology_entries: list) -> str:
        """Determine knowledge source."""
        if data['total_months'] >= 12:
            return 'direct_experience'
        elif len(data['contexts']) >= 2:
            return 'adjacent_experience'
        elif data['total_months'] > 0:
            return 'direct_experience'
        return 'study'