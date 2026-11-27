"""
Job Description Parser - Extracts structured information from job description text.
"""

import re
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class ParsedJD:
    title: str = ""
    company: str = ""
    location: str = ""
    employment_type: str = ""
    seniority: str = ""
    summary: str = ""
    responsibilities: list = field(default_factory=list)
    required_qualifications: list = field(default_factory=list)
    preferred_qualifications: list = field(default_factory=list)
    required_technical: list = field(default_factory=list)
    preferred_technical: list = field(default_factory=list)
    business_domains: list = field(default_factory=list)
    soft_skills: list = field(default_factory=list)
    benefits: list = field(default_factory=list)
    salary_range: str = ""
    team_info: str = ""
    reporting_line: str = ""
    travel_requirements: str = ""
    raw_text: str = ""


class JDParser:
    """Parses job description text into structured data."""

    def __init__(self):
        self.section_patterns = {
            'responsibilities': [
                r'responsibilities', r'what you.{0,3}ll do', r'role overview',
                r'key responsibilities', r'duties', r'accountabilities'
            ],
            'required': [
                r'required qualifications', r'requirements', r'must have',
                r'basic qualifications', r'minimum qualifications', r'you have'
            ],
            'preferred': [
                r'preferred qualifications', r'nice to have', r'bonus',
                r'preferred skills', r'desired qualifications', r'plus'
            ],
            'benefits': [
                r'benefits', r'perks', r'what we offer', r'compensation',
                r'we offer', r'package includes'
            ],
        }

    def parse(self, text: str) -> ParsedJD:
        """Parse job description text into structured ParsedJD object."""
        jd = ParsedJD(raw_text=text)
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        # Extract title (usually first line)
        jd.title = self._extract_title(lines)

        # Extract company
        jd.company = self._extract_company(text)

        # Extract location
        jd.location = self._extract_location(text)

        # Extract employment type
        jd.employment_type = self._extract_employment_type(text)

        # Split into sections
        sections = self._split_sections(lines)

        # Parse each section
        jd.responsibilities = self._parse_bullets(sections.get('responsibilities', []))
        jd.required_qualifications = self._parse_bullets(sections.get('required', []))
        jd.preferred_qualifications = self._parse_bullets(sections.get('preferred', []))
        jd.benefits = self._parse_bullets(sections.get('benefits', []))

        # Extract technical skills from all sections
        all_text = ' '.join(lines)
        jd.required_technical = self._extract_technical_skills(
            sections.get('required', []), 'required'
        )
        jd.preferred_technical = self._extract_technical_skills(
            sections.get('preferred', []), 'preferred'
        )

        # Extract business domains
        jd.business_domains = self._extract_business_domains(all_text)

        # Extract soft skills
        jd.soft_skills = self._extract_soft_skills(all_text)

        # Extract salary
        jd.salary_range = self._extract_salary(text)

        # Extract team info
        jd.team_info = self._extract_team_info(text)

        # Extract reporting line
        jd.reporting_line = self._extract_reporting_line(text)

        # Extract travel requirements
        jd.travel_requirements = self._extract_travel(text)

        # Determine seniority
        jd.seniority = self._determine_seniority(jd)

        # Extract summary
        jd.summary = self._extract_summary(sections, lines)

        return jd

    def _extract_title(self, lines: list) -> str:
        """Extract job title from first few lines."""
        for line in lines[:5]:
            if len(line) > 5 and len(line) < 100:
                # Skip obvious non-titles
                if not re.search(r'^(about|we are|company|location|remote|full.time|part.time|contract)', line, re.I):
                    return line
        return ""

    def _extract_company(self, text: str) -> str:
        """Extract company name."""
        # Look for "at [Company]" or "Company is hiring"
        patterns = [
            r'at\s+([A-Z][A-Za-z0-9\s&\.]+)(?:\s+is|\s+hiring|\s+seeks|\n)',
            r'([A-Z][A-Za-z0-9\s&\.]+)\s+is\s+hiring',
            r'join\s+([A-Z][A-Za-z0-9\s&\.]+)',
            r'careers?\s+at\s+([A-Z][A-Za-z0-9\s&\.]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                return match.group(1).strip()
        return ""

    def _extract_location(self, text: str) -> str:
        """Extract location."""
        patterns = [
            r'location[:\s]+([^\n]+)',
            r'based in ([^\n,]+)',
            r'(remote|hybrid|on.site|onsite)',
            r'([A-Z][a-z]+,\s*[A-Z]{2})',  # City, State
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                return match.group(1).strip()
        return ""

    def _extract_employment_type(self, text: str) -> str:
        """Extract employment type."""
        types = ['full.time', 'full.time', 'part.time', 'contract', 'temporary', 'internship', 'permanent']
        text_lower = text.lower()
        for t in types:
            if t.replace('.', '') in text_lower.replace('-', ''):
                return t.replace('.', '-')
        return ""

    def _split_sections(self, lines: list) -> dict:
        """Split JD into sections."""
        sections = {}
        current_section = 'header'
        section_lines = []

        for line in lines:
            lower_line = line.lower()
            matched = False

            for section_name, patterns in self.section_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, lower_line) and len(line) < 80:
                        if section_lines:
                            sections[current_section] = section_lines
                        current_section = section_name
                        section_lines = []
                        matched = True
                        break
                if matched:
                    break

            if not matched:
                section_lines.append(line)

        if section_lines:
            sections[current_section] = section_lines

        return sections

    def _parse_bullets(self, lines: list) -> list:
        """Parse bullet points from lines."""
        bullets = []
        for line in lines:
            # Remove bullet markers
            clean = re.sub(r'^[•\-\*\►→\d\.)\]]+\s*', '', line).strip()
            if clean and len(clean) > 10:
                bullets.append(clean)
        return bullets

    def _extract_technical_skills(self, lines: list, req_type: str) -> list:
        """Extract technical skills from requirement sections."""
        text = ' '.join(lines).lower()

        # Comprehensive technology list
        technologies = [
            # Languages
            'python', 'java', 'javascript', 'typescript', 'go', 'golang', 'rust',
            'c++', 'c#', 'c sharp', 'ruby', 'scala', 'kotlin', 'swift', 'php',
            'perl', 'r', 'matlab', 'julia', 'dart', 'elixir', 'clojure', 'haskell', 'f#',
            # Frontend
            'react', 'vue', 'angular', 'svelte', 'next.js', 'nextjs', 'nuxt', 'remix',
            'webpack', 'vite', 'rollup', 'babel', 'eslint', 'prettier',
            'css', 'sass', 'scss', 'less', 'tailwind', 'bootstrap', 'material.ui', 'mui',
            'html', 'dom', 'web components', 'pwa', 'spa',
            # Backend
            'node.js', 'nodejs', 'express', 'fastify', 'nestjs', 'django', 'flask', 'fastapi',
            'spring', 'spring boot', 'quarkus', 'micronaut', 'gin', 'echo',
            'actix', 'rocket', 'asp.net', 'laravel', 'rails', 'sinatra',
            # Databases
            'postgresql', 'postgres', 'mysql', 'sqlite', 'mongodb', 'mongo', 'redis',
            'cassandra', 'dynamodb', 'elasticsearch', 'opensearch', 'couchbase', 'neo4j',
            'snowflake', 'bigquery', 'redshift', 'clickhouse', 'timescaledb',
            'mariadb', 'oracle', 'sql server', 'db2',
            # Cloud
            'aws', 'amazon web services', 'azure', 'gcp', 'google cloud', 'cloudflare',
            'digitalocean', 'linode', 'ec2', 'lambda', 's3', 'rds', 'dynamodb',
            'cloudfront', 'route53', 'ecs', 'eks', 'fargate', 'cloudformation', 'cdk',
            'terraform', 'functions', 'app engine', 'cloud run', 'cloud sql', 'firestore',
            'pub/sub', 'dataflow', 'dataproc', 'vertex ai',
            # Containerization
            'docker', 'kubernetes', 'k8s', 'helm', 'istio', 'linkerd', 'consul',
            'nomad', 'openshift', 'rancher', 'k3s', 'k0s', 'microk8s',
            'containerd', 'cri-o', 'podman', 'buildah', 'skaffold',
            # Infrastructure
            'ansible', 'chef', 'puppet', 'saltstack', 'vagrant', 'packer',
            'crossplane', 'argocd', 'flux', 'spinnaker', 'jenkins', 'gitlab ci',
            'github actions', 'circleci', 'teamcity', 'bamboo', 'azure devops',
            'bitbucket pipelines',
            # Messaging
            'kafka', 'rabbitmq', 'nats', 'pulsar', 'redis streams', 'sqs', 'sns',
            'pub/sub', 'eventbridge', 'grpc', 'protobuf', 'thrift', 'avro',
            'graphql', 'rest', 'websocket', 'server.sent events', 'mqtt',
            # Monitoring
            'prometheus', 'grafana', 'datadog', 'new relic', 'elastic', 'splunk',
            'jaeger', 'zipkin', 'opentelemetry', 'honeycomb', 'lightstep',
            'cloudwatch', 'stackdriver', 'appdynamics', 'dynatrace', 'sentry',
            # ML/AI
            'tensorflow', 'pytorch', 'jax', 'keras', 'scikit.learn', 'sklearn',
            'xgboost', 'lightgbm', 'catboost', 'hugging face', 'transformers',
            'langchain', 'llama', 'gpt', 'bert', 'stable diffusion', 'mlflow',
            'kubeflow', 'airflow', 'prefect', 'dagster', 'pandas', 'numpy', 'polars',
            'spark', 'flink', 'ray', 'dask', 'modin',
            # Security
            'oauth', 'oidc', 'saml', 'jwt', 'bcrypt', 'argon2', 'vault',
            'cert.manager', 'kyverno', 'opa', 'gatekeeper', 'falco', 'sysdig',
            'aquasec', 'trivy', 'snyk', 'dependabot',
            # Data
            'dbt', 'hadoop', 'hive', 'presto', 'trino', 'delta lake', 'iceberg', 'hudi',
            'kafka streams', 'ksql',
        ]

        found = []
        for tech in technologies:
            # Use word boundaries for more accurate matching
            pattern = r'\b' + re.escape(tech) + r'\b'
            if re.search(pattern, text, re.I):
                found.append(tech)

        return list(set(found))

    def _extract_business_domains(self, text: str) -> list:
        """Extract business domains from text."""
        text_lower = text.lower()
        domains = [
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
            'logistics', 'transportation', 'delivery', 'fleet',
            'streaming', 'media', 'entertainment', 'video',
            'crypto', 'blockchain', 'web3', 'defi', 'nft',
            'ai', 'ml', 'machine learning', 'data science', 'analytics',
        ]

        found = []
        for domain in domains:
            if domain in text_lower:
                found.append(domain)

        return list(set(found))

    def _extract_soft_skills(self, text: str) -> list:
        """Extract soft skills from text."""
        text_lower = text.lower()
        skills = [
            'communication', 'collaboration', 'teamwork', 'leadership', 'mentoring',
            'problem.solving', 'critical thinking', 'analytical', 'adaptability',
            'time management', 'prioritization', 'ownership', 'accountability',
            'customer focus', 'user empathy', 'stakeholder management',
            'influence', 'negotiation', 'conflict resolution', 'decision making',
            'strategic thinking', 'innovation', 'creativity', 'learning agility',
            'emotional intelligence', 'eq', 'cultural awareness', 'inclusion',
        ]

        found = []
        for skill in skills:
            pattern = skill.replace('.', r'\.?')
            if re.search(pattern, text_lower):
                found.append(skill.replace('.', ' '))

        return list(set(found))

    def _extract_salary(self, text: str) -> str:
        """Extract salary range."""
        patterns = [
            r'\$[\d,]+\s*[-–]\s*\$[\d,]+',
            r'\$[\d,]+k\s*[-–]\s*\$[\d,]+k',
            r'salary[:\s]+\$[\d,\s\-–]+',
            r'compensation[:\s]+\$[\d,\s\-–]+',
            r'base pay[:\s]+\$[\d,\s\-–]+',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                return match.group(0).strip()
        return ""

    def _extract_team_info(self, text: str) -> str:
        """Extract team information."""
        patterns = [
            r'team of \d+',
            r'\d+ person team',
            r'\d+ engineer team',
            r'team size',
            r'reports to',
            r'manage a team',
            r'lead a team',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                return match.group(0).strip()
        return ""

    def _extract_reporting_line(self, text: str) -> str:
        """Extract reporting line."""
        patterns = [
            r'reports? to (?:the )?([^\n,]+)',
            r'reporting to (?:the )?([^\n,]+)',
            r'manager[:\s]+([^\n,]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                return match.group(1).strip()
        return ""

    def _extract_travel(self, text: str) -> str:
        """Extract travel requirements."""
        patterns = [
            r'travel[:\s]+([^\n]+)',
            r'(\d+% travel)',
            r'(no travel)',
            r'(remote)',
            r'(hybrid)',
            r'(on.site)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                return match.group(1).strip()
        return ""

    def _determine_seniority(self, jd: ParsedJD) -> str:
        """Determine seniority level from JD."""
        text = f"{jd.title} {' '.join(jd.required_qualifications)} {' '.join(jd.responsibilities)}".lower()

        seniority_keywords = {
            'junior': ['junior', 'entry', 'associate i', 'engineer i', 'developer i', 'new grad', 'recent graduate', '0-2 years', '0-3 years'],
            'mid': ['mid.level', 'mid level', 'engineer ii', 'developer ii', 'software engineer', '2-4 years', '3-5 years', '4-6 years'],
            'senior': ['senior', 'sr.', 'lead', 'principal', 'staff', 'architect', '5+ years', '7+ years', '8+ years', '10+ years'],
            'manager': ['manager', 'engineering manager', 'development manager', 'technical manager', 'team lead'],
            'director': ['director', 'head of', 'vp', 'vice president'],
        }

        scores = {}
        for level, keywords in seniority_keywords.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[level] = score

        if scores:
            return max(scores, key=scores.get)
        return "mid"

    def _extract_summary(self, sections: dict, lines: list) -> str:
        """Extract job summary."""
        # Check for summary/about section
        for key in ['summary', 'about', 'overview', 'description']:
            if key in sections:
                return ' '.join(sections[key][:5])

        # Fallback: first paragraph after title
        in_title = True
        summary_lines = []
        for line in lines:
            if in_title and len(line) < 100:
                in_title = False
            elif not in_title and line:
                summary_lines.append(line)
            if len(summary_lines) >= 3:
                break

        return ' '.join(summary_lines)