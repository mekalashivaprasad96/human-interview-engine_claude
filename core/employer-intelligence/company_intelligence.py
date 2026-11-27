"""
Company Intelligence - Deep company-specific intelligence for interview context.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class CompanyProfile:
    name: str
    aliases: list = field(default_factory=list)
    industry: str = ""
    founded_year: Optional[int] = None
    employee_count: Optional[int] = None
    public_company: bool = False
    headquarters: str = ""
    known_technologies: list = field(default_factory=list)
    engineering_blog_url: str = ""
    conference_presence: list = field(default_factory=list)
    open_source_projects: list = field(default_factory=list)
    notable_outages: list = field(default_factory=list)
    architecture_talks: list = field(default_factory=list)
    hiring_practices: dict = field(default_factory=dict)
    interview_process: list = field(default_factory=list)
    culture_signals: list = field(default_factory=list)
    last_updated: str = ""


class CompanyIntelligence:
    """Provides company-specific intelligence for interview preparation."""

    # Known company profiles (sample - would be expanded in production)
    KNOWN_COMPANIES = {
        'google': CompanyProfile(
            name='Google',
            aliases=['alphabet', 'google inc'],
            industry='cloud',
            founded_year=1998,
            employee_count=180000,
            public_company=True,
            headquarters='Mountain View, CA',
            known_technologies=['Go', 'Java', 'C++', 'Python', 'Kubernetes', 'Borg', 'Spanner', 'Bigtable', 'TensorFlow', 'JAX'],
            engineering_blog_url='https://cloud.google.com/blog',
            conference_presence=['KubeCon', 'Google Cloud Next', 'SREcon', 'VLDB', 'SIGMOD'],
            open_source_projects=['Kubernetes', 'TensorFlow', 'JAX', 'Protocol Buffers', 'gRPC', 'Bazel', 'Angular', 'Go'],
            architecture_talks=[
                'Spanner: Globally Distributed Database',
                'Borg: Cluster Management',
                'MapReduce', 'Bigtable', 'Dremel', 'Percolator',
                'F1: Distributed SQL', 'Megastore', 'Chubby'
            ],
            hiring_practices={
                'phone_screen': True,
                'on_site_rounds': 4-5,
                'focus_areas': ['algorithms', 'system_design', 'behavioral', 'domain_knowledge'],
                'hiring_committee': True,
            },
            interview_process=[
                'Recruiter screen',
                'Phone technical screen (1-2)',
                'On-site: coding, system design, behavioral, domain',
                'Hiring committee review',
            ],
            culture_signals=['Data-driven', 'Scale-obsessed', 'Engineering-first', 'Open culture', 'Mobility encouraged'],
            last_updated='2024-01',
        ),
        'amazon': CompanyProfile(
            name='Amazon',
            aliases=['amazon.com', 'amazon web services', 'aws'],
            industry='cloud',
            founded_year=1994,
            employee_count=1500000,
            public_company=True,
            headquarters='Seattle, WA',
            known_technologies=['Java', 'Python', 'C++', 'Rust', 'DynamoDB', 'S3', 'EC2', 'Lambda', 'Kinesis', 'Redshift'],
            engineering_blog_url='https://aws.amazon.com/blogs/',
            conference_presence=['re:Invent', 'KubeCon', 'SREcon', 'OSDI', 'NSDI'],
            open_source_projects=['Firecracker', 'Bottlerocket', 'Smithy', 'CDK', 'SAM', 'App Mesh'],
            architecture_talks=[
                'DynamoDB: Predictable Performance',
                'S3: Design for Durability',
                'Lambda: Serverless Compute',
                'Aurora: Cloud-Native Database',
                'Physalia: Transactional Storage',
            ],
            hiring_practices={
                'phone_screen': True,
                'on_site_rounds': 5-6,
                'focus_areas': ['leadership_principles', 'coding', 'system_design', 'bar_raiser'],
                'bar_raiser': True,
            },
            interview_process=[
                'Recruiter screen',
                'Phone screen (1-2)',
                'On-site: 5-6 rounds (coding, design, LP, bar raiser)',
                'Debrief + bar raiser veto',
            ],
            culture_signals=['Customer obsession', 'Ownership', 'Bias for action', 'Frugality', 'High bar', 'Dive deep'],
            last_updated='2024-01',
        ),
        'meta': CompanyProfile(
            name='Meta',
            aliases=['facebook', 'fb', 'instagram', 'whatsapp'],
            industry='social',
            founded_year=2004,
            employee_count=67000,
            public_company=True,
            headquarters='Menlo Park, CA',
            known_technologies=['PHP/Hack', 'Python', 'C++', 'Rust', 'React', 'GraphQL', 'PyTorch', 'Presto', 'RocksDB', 'Zstandard'],
            engineering_blog_url='https://engineering.fb.com/',
            conference_presence=['@Scale', 'PyTorch Conf', 'React Conf', 'SIGMOD', 'VLDB', 'OSDI'],
            open_source_projects=['React', 'PyTorch', 'GraphQL', 'Presto', 'RocksDB', 'Zstandard', 'Hermes', 'Yoga', 'Detox'],
            architecture_talks=[
                'TAO: Distributed Data Store',
                'Unicorn: Inverted Index',
                'Messenger Architecture',
                'Instagram Infrastructure',
                'Ads Ranking Pipeline',
            ],
            hiring_practices={
                'phone_screen': True,
                'on_site_rounds': 4-5,
                'focus_areas': ['coding', 'system_design', 'behavioral', 'product_sense'],
                'no_whiteboard': True,
            },
            interview_process=[
                'Recruiter screen',
                'Phone screen (coding)',
                'On-site: coding x2, system design, behavioral, product',
                'Debrief',
            ],
            culture_signals=['Move fast', 'Focus on impact', 'Be bold', 'Open', 'Build social value'],
            last_updated='2024-01',
        ),
        'microsoft': CompanyProfile(
            name='Microsoft',
            aliases=['msft', 'azure'],
            industry='cloud',
            founded_year=1975,
            employee_count=220000,
            public_company=True,
            headquarters='Redmond, WA',
            known_technologies=['C#', '.NET', 'TypeScript', 'C++', 'Rust', 'Azure', 'Kubernetes', 'VS Code', 'GitHub', 'Power Platform'],
            engineering_blog_url='https://devblogs.microsoft.com/',
            conference_presence=['Build', 'Ignite', 'KubeCon', '.NET Conf', 'RustConf'],
            open_source_projects=['VS Code', 'TypeScript', '.NET', 'PowerShell', 'GitHub', 'Azure SDKs', 'Playwright', 'Semantic Kernel'],
            architecture_talks=[
                'Azure Architecture',
                'Cosmos DB: Global Distribution',
                'Service Fabric',
                ' Orleans: Virtual Actors',
                'Project Silo',
            ],
            hiring_practices={
                'phone_screen': True,
                'on_site_rounds': 4-5,
                'focus_areas': ['coding', 'system_design', 'behavioral', 'design'],
                'as_aa': True,
            },
            interview_process=[
                'Recruiter screen',
                'Phone screen',
                'On-site: coding, design, behavioral, AA (as appropriate)',
                'Hiring manager + as-aa review',
            ],
            culture_signals=['Growth mindset', 'Customer obsessed', 'Diverse & inclusive', 'One Microsoft', 'Make a difference'],
            last_updated='2024-01',
        ),
        'netflix': CompanyProfile(
            name='Netflix',
            aliases=['nflx'],
            industry='streaming',
            founded_year=1997,
            employee_count=13000,
            public_company=True,
            headquarters='Los Gatos, CA',
            known_technologies=['Java', 'Python', 'Go', 'Kotlin', 'Spring Boot', 'GraphQL', 'Kafka', 'Flink', 'Cassandra', 'AWS'],
            engineering_blog_url='https://netflixtechblog.com/',
            conference_presence=['QCon', 'Strange Loop', 'KubeCon', 'SREcon', 'VLDB'],
            open_source_projects=['Conductor', 'Mantis', 'Hystrix', 'Eureka', 'Ribbon', 'Zuul', 'Atlas', 'Chaos Monkey', 'Spinnaker'],
            architecture_talks=[
                'Microservices at Netflix',
                'Chaos Engineering',
                'Recommendation Systems',
                'Streaming Architecture',
                'Data Platform',
            ],
            hiring_practices={
                'phone_screen': True,
                'on_site_rounds': 4-5,
                'focus_areas': ['coding', 'system_design', 'culture_fit', 'domain'],
                'no_whiteboard': True,
            },
            interview_process=[
                'Recruiter screen',
                'Phone screen (technical)',
                'On-site: coding, system design, culture, domain',
                'Hiring manager review',
            ],
            culture_signals=['Freedom & responsibility', 'High performance', 'Context not control', 'Highly aligned loosely coupled'],
            last_updated='2024-01',
        ),
        'uber': CompanyProfile(
            name='Uber',
            aliases=['uber technologies'],
            industry='transportation',
            founded_year=2009,
            employee_count=30000,
            public_company=True,
            headquarters='San Francisco, CA',
            known_technologies=['Go', 'Java', 'Python', 'Node.js', 'Kafka', 'Cassandra', 'Redis', 'Kubernetes', 'gRPC', 'Protocol Buffers'],
            engineering_blog_url='https://www.uber.com/blog/engineering/',
            conference_presence=['QCon', 'KubeCon', 'Strange Loop', 'SIGMOD', 'VLDB'],
            open_source_projects=['Cadence', 'Jaeger', 'PIP', 'M3', 'Schemaless', 'Cherami', 'uProto'],
            architecture_talks=[
                'Marketplace Architecture',
                'Dispatch System',
                'Real-time Analytics',
                'Microservices Migration',
                'Geospatial Indexing',
            ],
            hiring_practices={
                'phone_screen': True,
                'on_site_rounds': 4-5,
                'focus_areas': ['coding', 'system_design', 'behavioral', 'domain'],
            },
            interview_process=[
                'Recruiter screen',
                'Phone screen',
                'On-site: coding, system design, behavioral, domain',
                'Debrief',
            ],
            culture_signals=['Customer obsession', 'Act like owners', 'Build for the long term', 'Celebrate differences', 'Do the right thing'],
            last_updated='2024-01',
        ),
        'airbnb': CompanyProfile(
            name='Airbnb',
            aliases=['airbnb inc'],
            industry='travel',
            founded_year=2008,
            employee_count=7000,
            public_company=True,
            headquarters='San Francisco, CA',
            known_technologies=['Java', 'Kotlin', 'React', 'GraphQL', 'Kafka', 'Airflow', 'Kubernetes', 'AWS', 'MySQL', 'Redis'],
            engineering_blog_url='https://medium.com/airbnb-engineering',
            conference_presence=['QCon', 'KubeCon', 'Airflow Summit', 'GraphQL Conf'],
            open_source_projects=['Airflow', 'Superset', 'Chronon', 'Minoan', 'Dagster', 'Knowledge Repo'],
            architecture_talks=[
                'Service-Oriented Architecture',
                'Data Platform',
                'Search Ranking',
                'Payments Platform',
                'Trust & Safety',
            ],
            hiring_practices={
                'phone_screen': True,
                'on_site_rounds': 4-5,
                'focus_areas': ['coding', 'system_design', 'behavioral', 'values'],
            },
            interview_process=[
                'Recruiter screen',
                'Phone screen',
                'On-site: coding, system design, behavioral, values',
                'Debrief',
            ],
            culture_signals=['Champion the mission', 'Be a host', 'Embrace the adventure', 'Be a cereal entrepreneur'],
            last_updated='2024-01',
        ),
    }

    def get_company_profile(self, company_name: str) -> Optional[CompanyProfile]:
        """Get company profile by name (fuzzy match)."""
        name_lower = company_name.lower().strip()

        # Direct match
        if name_lower in self.KNOWN_COMPANIES:
            return self.KNOWN_COMPANIES[name_lower]

        # Alias match
        for key, profile in self.KNOWN_COMPANIES.items():
            if name_lower in [a.lower() for a in profile.aliases]:
                return profile
            if name_lower in key or key in name_lower:
                return profile

        return None

    def get_interview_intel(self, company_name: str) -> dict:
        """Get interview-specific intelligence for a company."""
        profile = self.get_company_profile(company_name)

        if not profile:
            return {
                'known': False,
                'process': ['Standard: recruiter screen, phone screen, on-site'],
                'focus_areas': ['coding', 'system_design', 'behavioral'],
                'tips': ['Research company', 'Prepare stories', 'Know your resume'],
            }

        return {
            'known': True,
            'company': profile.name,
            'process': profile.interview_process,
            'focus_areas': profile.hiring_practices.get('focus_areas', []),
            'bar_raiser': profile.hiring_practices.get('bar_raiser', False),
            'as_aa': profile.hiring_practices.get('as_aa', False),
            'culture_signals': profile.culture_signals,
            'technical_focus': profile.known_technologies[:10],
            'architecture_talks': profile.architecture_talks[:5],
            'open_source': profile.open_source_projects[:5],
            'tips': [
                f'Know {profile.name}\'s tech stack: {", ".join(profile.known_technologies[:5])}',
                f'Reference {profile.name} engineering blog: {profile.engineering_blog_url}',
                f'Mention relevant architecture: {profile.architecture_talks[0] if profile.architecture_talks else "N/A"}',
                f'Align with culture: {", ".join(profile.culture_signals[:3])}',
            ],
        }

    def get_all_known_companies(self) -> list[str]:
        """Get list of all known companies."""
        return list(self.KNOWN_COMPANIES.keys())

    def add_company_profile(self, profile: CompanyProfile):
        """Add or update a company profile."""
        self.KNOWN_COMPANIES[profile.name.lower()] = profile