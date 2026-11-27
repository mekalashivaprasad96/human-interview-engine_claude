"""
Competency Mapper - Maps technical, business, and leadership competencies from resume and experience.
"""

from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict
from .resume_parser import ParsedEmployment, ParsedResume


@dataclass
class CompetencyProfile:
    technical: dict = field(default_factory=dict)  # core, proficient, familiar, domains
    business: dict = field(default_factory=dict)
    leadership: dict = field(default_factory=dict)
    transferable: list = field(default_factory=list)


class CompetencyMapper:
    """Maps competencies from resume and career data."""

    # Technology categories for structured mapping
    TECH_CATEGORIES = {
        'languages': [
            'python', 'java', 'javascript', 'typescript', 'go', 'rust', 'c++', 'c#',
            'ruby', 'scala', 'kotlin', 'swift', 'objective-c', 'php', 'perl', 'r',
            'matlab', 'julia', 'dart', 'elixir', 'clojure', 'haskell', 'f#'
        ],
        'frontend': [
            'react', 'vue', 'angular', 'svelte', 'next.js', 'nuxt', 'remix',
            'webpack', 'vite', 'rollup', 'babel', 'eslint', 'prettier',
            'css', 'sass', 'less', 'tailwind', 'bootstrap', 'material-ui',
            'html', 'dom', 'web components', 'pwa', 'spa'
        ],
        'backend': [
            'node.js', 'express', 'fastify', 'nestjs', 'django', 'flask', 'fastapi',
            'spring', 'spring boot', 'quarkus', 'micronaut', 'gin', 'echo',
            'actix', 'rocket', 'asp.net', 'laravel', 'rails', 'sinatra'
        ],
        'databases': [
            'postgresql', 'mysql', 'sqlite', 'mongodb', 'redis', 'cassandra',
            'dynamodb', 'elasticsearch', 'opensearch', 'couchbase', 'neo4j',
            'snowflake', 'bigquery', 'redshift', 'clickhouse', 'timescaledb',
            'mariadb', 'oracle', 'sql server', 'db2'
        ],
        'cloud': [
            'aws', 'azure', 'gcp', 'cloudflare', 'digitalocean', 'linode',
            'ec2', 'lambda', 's3', 'rds', 'dynamodb', 'cloudfront', 'route53',
            'ecs', 'eks', 'fargate', 'cloudformation', 'cdk', 'terraform',
            'functions', 'app engine', 'cloud run', 'cloud sql', 'firestore',
            'pub/sub', 'dataflow', 'dataproc', 'vertex ai'
        ],
        'containerization': [
            'docker', 'kubernetes', 'k8s', 'helm', 'istio', 'linkerd', 'consul',
            'nomad', 'openshift', 'rancher', 'k3s', 'k0s', 'microk8s',
            'containerd', 'cri-o', 'podman', 'buildah', 'skaffold'
        ],
        'infrastructure': [
            'terraform', 'pulumi', 'ansible', 'chef', 'puppet', 'saltstack',
            'vagrant', 'packer', 'crossplane', 'argocd', 'flux', 'spinnaker',
            'jenkins', 'gitlab ci', 'github actions', 'circleci', 'circleci',
            'teamcity', 'bamboo', 'azure devops', 'bitbucket pipelines'
        ],
        'messaging': [
            'kafka', 'rabbitmq', 'nats', 'pulsar', 'redis streams', 'sqs', 'sns',
            'pub/sub', 'eventbridge', 'grpc', 'protobuf', 'thrift', 'avro',
            'graphql', 'rest', 'websocket', 'server-sent events', 'mqtt'
        ],
        'monitoring': [
            'prometheus', 'grafana', 'datadog', 'new relic', 'elastic', 'splunk',
            'jaeger', 'zipkin', 'opentelemetry', 'honeycomb', 'lightstep',
            'cloudwatch', 'stackdriver', 'appdynamics', 'dynatrace', 'sentry'
        ],
        'ml_ai': [
            'tensorflow', 'pytorch', 'jax', 'keras', 'scikit-learn', 'xgboost',
            'lightgbm', 'catboost', 'hugging face', 'transformers', 'langchain',
            'llama', 'gpt', 'bert', 'stable diffusion', 'mlflow', 'kubeflow',
            'airflow', 'prefect', 'dagster', 'pandas', 'numpy', 'polars',
            'spark', 'flink', 'ray', 'dask', 'modin'
        ],
        'security': [
            'oauth', 'oidc', 'saml', 'jwt', 'bcrypt', 'argon2', 'vault',
            'cert-manager', 'istio', 'kyverno', 'opa', 'gatekeeper',
            'falco', 'sysdig', 'aquasec', 'trivy', 'snyk', 'dependabot'
        ],
        'data': [
            'spark', 'flink', 'kafka', 'airflow', 'dbt', 'snowflake', 'bigquery',
            'redshift', 'databricks', 'hadoop', 'hive', 'presto', 'trino',
            'delta lake', 'iceberg', 'hudi', 'kafka streams', 'ksql'
        ],
    }

    BUSINESS_DOMAINS = [
        'fintech', 'payments', 'banking', 'trading', 'risk', 'compliance',
        'healthcare', 'medical', 'pharma', 'clinical', 'hipaa', 'ehr',
        'ecommerce', 'retail', 'marketplace', 'inventory', 'supply chain',
        'saas', 'b2b', 'enterprise', 'crm', 'erp', 'productivity',
        'social', 'media', 'advertising', 'recommendation', 'content',
        'gaming', 'mobile', 'unity', 'unreal', 'multiplayer',
        'automotive', 'autonomous', 'adas', 'iot', 'manufacturing',
        'telecom', '5g', 'network', 'carrier',
        'government', 'defense', 'public sector',
        'education', 'edtech', 'learning', 'training',
        'logistics', 'transportation', 'delivery', 'fleet'
    ]

    LEADERSHIP_COMPETENCIES = [
        'people_management', 'team_building', 'hiring', 'mentoring',
        'performance_management', 'career_development', 'organizational_design',
        'technical_leadership', 'architecture_review', 'code_review',
        'project_management', 'agile', 'scrum', 'kanban', 'sprint_planning',
        'stakeholder_management', 'cross_functional_collaboration',
        'vendor_management', 'budget_planning', 'resource_allocation',
        'incident_management', 'on_call', 'runbook_development',
        'strategic_planning', 'roadmap_development', 'okr_setting'
    ]

    def map(self, resume: ParsedResume, chronology_entries: list) -> CompetencyProfile:
        """Map all competencies from resume and career chronology."""
        profile = CompetencyProfile()

        # Aggregate all technologies across career
        all_technologies = set()
        for emp in resume.employments:
            all_technologies.update([t.lower() for t in emp.technologies])
        for skill in resume.skills:
            all_technologies.add(skill.lower())

        # Map technical competencies
        profile.technical = self._map_technical(all_technologies, chronology_entries)

        # Map business competencies
        profile.business = self._map_business(resume, chronology_entries)

        # Map leadership competencies
        profile.leadership = self._map_leadership(resume, chronology_entries)

        # Identify transferable skills
        profile.transferable = self._identify_transferable(profile, chronology_entries)

        return profile

    def _map_technical(self, technologies: set, chronology_entries: list) -> dict:
        """Map technical competencies by category and depth."""
        categorized = defaultdict(set)
        technology_years = defaultdict(int)

        # Estimate years of experience per technology
        for entry in chronology_entries:
            for tech in entry.technologies:
                technology_years[tech.lower()] += entry.duration_months / 12

        # Categorize each technology
        for tech in technologies:
            categorized_tech = self._categorize_technology(tech)
            for category in categorized_tech:
                categorized[category].add(tech)

        # Determine proficiency levels
        result = {
            'core': [],
            'proficient': [],
            'familiar': [],
            'domains': list(categorized.keys())
        }

        for tech in technologies:
            years = technology_years.get(tech, 0)
            if years >= 3:
                result['core'].append(tech)
            elif years >= 1:
                result['proficient'].append(tech)
            else:
                result['familiar'].append(tech)

        # Sort each list
        for key in result:
            if isinstance(result[key], list):
                result[key].sort()

        return result

    def _categorize_technology(self, tech: str) -> list:
        """Categorize a technology into one or more categories."""
        tech_lower = tech.lower()
        categories = []

        for category, techs in self.TECH_CATEGORIES.items():
            for t in techs:
                if t in tech_lower or tech_lower in t:
                    categories.append(category)
                    break

        if not categories:
            categories.append('other')

        return categories

    def _map_business(self, resume: ParsedResume, chronology_entries: list) -> dict:
        """Map business domain competencies."""
        domains = set()
        customer_facing = False
        p_l_responsibility = False
        strategic_planning = False
        vendor_management = False

        for entry in chronology_entries:
            # Infer from industry
            if entry.industry in self.BUSINESS_DOMAINS:
                domains.add(entry.industry)
            # Check description for business domain keywords
            text = f"{entry.title} {entry.scope}".lower()
            for domain in self.BUSINESS_DOMAINS:
                if domain in text:
                    domains.add(domain)

            # Check for business responsibilities
            if any(kw in text for kw in ['customer', 'client', 'user', 'stakeholder', 'external']):
                customer_facing = True
            if any(kw in text for kw in ['budget', 'p&l', 'profit', 'loss', 'revenue', 'cost']):
                p_l_responsibility = True
            if any(kw in text for kw in ['strategy', 'roadmap', 'vision', 'planning', 'okr']):
                strategic_planning = True
            if any(kw in text for kw in ['vendor', 'vendor management', 'procurement', 'third party']):
                vendor_management = True

        return {
            'domains': sorted(domains),
            'customer_facing': customer_facing,
            'p_l_responsibility': p_l_responsibility,
            'strategic_planning': strategic_planning,
            'vendor_management': vendor_management
        }

    def _map_leadership(self, resume: ParsedResume, chronology_entries: list) -> dict:
        """Map leadership competencies."""
        people_management = False
        team_size_managed = 0
        technical_leadership = False
        project_leadership = False
        mentoring = False
        hiring = False

        for entry in chronology_entries:
            text = f"{entry.title} {entry.scope}".lower()

            # People management
            if any(kw in text for kw in ['manager', 'director', 'lead', 'head of', 'supervise', 'manage team']):
                people_management = True
                # Try to extract team size
                import re
                size_match = re.search(r'team of (\d+)|(\d+) (?:person|engineer|developer|member)', text)
                if size_match:
                    team_size_managed = max(team_size_managed, int(size_match.group(1) or size_match.group(2)))

            # Technical leadership
            if any(kw in text for kw in ['architect', 'technical lead', 'tech lead', 'principal', 'staff', 'code review', 'architecture']):
                technical_leadership = True

            # Project leadership
            if any(kw in text for kw in ['project lead', 'project manager', 'delivery lead', 'program', 'initiative']):
                project_leadership = True

            # Mentoring
            if any(kw in text for kw in ['mentor', 'coach', 'guide', 'onboard', 'junior']):
                mentoring = True

            # Hiring
            if any(kw in text for kw in ['hiring', 'recruit', 'interview', 'candidate']):
                hiring = True

        return {
            'people_management': people_management,
            'team_size_managed': team_size_managed,
            'technical_leadership': technical_leadership,
            'project_leadership': project_leadership,
            'mentoring': mentoring,
            'hiring': hiring
        }

    def _identify_transferable(self, profile: CompetencyProfile, chronology_entries: list) -> list:
        """Identify transferable skills across domains."""
        transferable = []

        # Cross-domain technical skills
        tech_domains = profile.technical.get('domains', [])
        if len(tech_domains) >= 3:
            transferable.append('polyglot_development')
        if 'cloud' in tech_domains and 'containerization' in tech_domains:
            transferable.append('cloud_native_architecture')
        if 'ml_ai' in tech_domains and 'data' in tech_domains:
            transferable.append('ml_ops')
        if 'monitoring' in tech_domains and 'infrastructure' in tech_domains:
            transferable.append('observability_driven_development')

        # Business + technical combinations
        if profile.business.get('customer_facing') and 'frontend' in tech_domains:
            transferable.append('product_engineering')
        if profile.business.get('strategic_planning') and profile.leadership.get('technical_leadership'):
            transferable.append('technical_strategy')
        if profile.leadership.get('people_management') and technical_leadership:
            transferable.append('engineering_management')

        # Industry transfers
        industries = set(e.industry for e in chronology_entries)
        if len(industries) >= 3:
            transferable.append('cross_industry_adaptability')

        return transferable