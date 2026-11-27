"""
Technology Timeline Validator - Validates technology availability against employment dates.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import re


@dataclass
class TechnologyEra:
    name: str
    start_year: int
    end_year: Optional[int]
    key_technologies: list
    paradigm_shifts: list


class TechnologyTimelineValidator:
    """Validates that claimed technologies existed during employment periods."""

    # Major technology eras and their key technologies
    ERAS = [
        TechnologyEra(
            name='mainframe',
            start_year=1960,
            end_year=1990,
            key_technologies=['COBOL', 'Fortran', 'CICS', 'IMS', 'DB2', 'JCL', 'VSAM'],
            paradigm_shifts=['Batch processing', 'Time-sharing']
        ),
        TechnologyEra(
            name='client_server',
            start_year=1985,
            end_year=2000,
            key_technologies=['C', 'C++', 'Visual Basic', 'PowerBuilder', 'Delphi', 'Oracle', 'Sybase', 'Windows NT', 'Novell NetWare'],
            paradigm_shifts=['Client-server architecture', 'GUI applications', 'Relational databases']
        ),
        TechnologyEra(
            name='web_1',
            start_year=1995,
            end_year=2005,
            key_technologies=['HTML', 'CSS', 'JavaScript', 'Perl', 'PHP', 'ASP', 'JSP', 'Apache', 'IIS', 'MySQL', 'PostgreSQL', 'Java Servlets', 'EJB'],
            paradigm_shifts=['World Wide Web', 'E-commerce', 'Dynamic web pages']
        ),
        TechnologyEra(
            name='web_2_soa',
            start_year=2000,
            end_year=2012,
            key_technologies=['AJAX', 'jQuery', 'Ruby on Rails', 'Django', 'Spring', 'Hibernate', 'SOAP', 'WSDL', 'ESB', 'SOA', 'Tomcat', 'JBoss', 'WebLogic', 'WebSphere', 'Oracle DB', 'SQL Server', 'Subversion', 'CVS', 'Ant', 'Maven'],
            paradigm_shifts=['Rich web apps', 'SOA', 'MVC frameworks', 'ORM', 'Agile']
        ),
        TechnologyEra(
            name='cloud_mobile',
            start_year=2008,
            end_year=2016,
            key_technologies=['AWS EC2/S3', 'iOS SDK', 'Android SDK', 'Objective-C', 'Swift', 'Java Android', 'Node.js', 'Express', 'AngularJS', 'Backbone', 'Ember', 'MongoDB', 'Redis', 'Cassandra', 'Hadoop', 'Hive', 'Pig', 'Git', 'GitHub', 'Jenkins', 'Chef', 'Puppet', 'Vagrant', 'Docker (2013+)'],
            paradigm_shifts=['Cloud computing', 'Mobile apps', 'NoSQL', 'Big Data', 'DevOps', 'Git/GitHub', 'CI/CD']
        ),
        TechnologyEra(
            name='microservices_k8s',
            start_year=2014,
            end_year=2020,
            key_technologies=['Kubernetes', 'Docker', 'Microservices', 'gRPC', 'Protocol Buffers', 'Istio', 'Linkerd', 'Envoy', 'Prometheus', 'Grafana', 'Helm', 'ArgoCD', 'Flux', 'Spinnaker', 'Terraform', 'Go', 'Rust', 'React', 'Vue', 'TypeScript', 'GraphQL', 'Kafka', 'etcd', 'Consul', 'Vault'],
            paradigm_shifts=['Container orchestration', 'Service mesh', 'GitOps', 'Observability', 'Infrastructure as Code']
        ),
        TechnologyEra(
            name='serverless_edge_ai',
            start_year=2018,
            end_year=None,
            key_technologies=['AWS Lambda', 'Cloud Functions', 'Cloud Run', 'Knative', 'Cloudflare Workers', 'Fastly Compute@Edge', 'Vercel', 'Next.js', 'Remix', 'Svelte', 'Solid', 'Deno', 'Bun', 'WebAssembly', 'TensorFlow', 'PyTorch', 'Transformers', 'Hugging Face', 'LangChain', 'Llama', 'GPT', 'Stable Diffusion', 'Vector DBs', 'Feature Stores', 'MLflow', 'Kubeflow'],
            paradigm_shifts=['Serverless', 'Edge computing', 'Generative AI', 'LLMs', 'Vector databases', 'MLOps']
        ),
    ]

    def validate_technology_availability(self, technology: str, employment_start: str,
                                          employment_end: str = None) -> dict:
        """Validate if a technology was available during employment period."""
        start_year = self._extract_year(employment_start)
        end_year = self._extract_year(employment_end) if employment_end else datetime.now().year

        if not start_year:
            return {'valid': True, 'confidence': 'unknown', 'reason': 'Could not parse dates'}

        tech_lower = technology.lower()
        available_in_eras = []

        for era in self.ERAS:
            era_end = era.end_year or datetime.now().year
            # Check if employment overlaps with era
            if start_year <= era_end and end_year >= era.start_year:
                # Check if technology belongs to this era
                for key_tech in era.key_technologies:
                    if key_tech.lower() in tech_lower or tech_lower in key_tech.lower():
                        available_in_eras.append(era.name)

        if available_in_eras:
            return {
                'valid': True,
                'confidence': 'high',
                'eras': available_in_eras,
                'reason': f'Available in eras: {", ".join(available_in_eras)}'
            }

        # Check if it's a foundational technology that spans eras
        foundational = ['linux', 'unix', 'sql', 'http', 'tcp/ip', 'dns', 'ssh', 'git', 'c', 'c++', 'java', 'python', 'javascript', 'html', 'css']
        if any(f in tech_lower for f in foundational):
            return {
                'valid': True,
                'confidence': 'high',
                'eras': ['foundational'],
                'reason': 'Foundational technology spanning multiple eras'
            }

        return {
            'valid': False,
            'confidence': 'medium',
            'eras': [],
            'reason': f'Technology "{technology}" may not have been widely available during {start_year}-{end_year}'
        }

    def validate_project_stack(self, technologies: list, employment_start: str,
                                employment_end: str = None) -> dict:
        """Validate an entire project technology stack."""
        results = {}
        all_valid = True

        for tech in technologies:
            validation = self.validate_technology_availability(tech, employment_start, employment_end)
            results[tech] = validation
            if not validation['valid']:
                all_valid = False

        return {
            'all_valid': all_valid,
            'validations': results,
            'summary': f"{sum(1 for v in results.values() if v['valid'])}/{len(results)} technologies validated",
        }

    def get_era_for_year(self, year: int) -> Optional[TechnologyEra]:
        """Get the technology era for a given year."""
        for era in self.ERAS:
            era_end = era.end_year or datetime.now().year
            if era.start_year <= year <= era_end:
                return era
        return None

    def get_technologies_for_era(self, era_name: str) -> list:
        """Get key technologies for a named era."""
        for era in self.ERAS:
            if era.name == era_name:
                return era.key_technologies
        return []

    def suggest_contemporary_alternatives(self, technology: str, target_year: int) -> list:
        """Suggest contemporary alternatives for an anachronistic technology."""
        era = self.get_era_for_year(target_year)
        if not era:
            return []

        tech_lower = technology.lower()

        # Known anachronisms and their contemporary alternatives
        anachronisms = {
            'kubernetes': ['docker swarm', 'mesos', 'nomad', 'manual orchestration'],
            'docker': ['vagrant', 'lxc', 'manual deployment', 'configuration management'],
            'terraform': ['cloudformation', 'ansible', 'chef', 'puppet', 'manual provisioning'],
            'kafka': ['rabbitmq', 'activemq', 'ibm mq', 'custom messaging'],
            'redis': ['memcached', 'ehcache', 'custom caching'],
            'graphql': ['rest', 'soap', 'rpc', 'custom apis'],
            'react': ['angularjs', 'backbone', 'ember', 'knockout', 'jquery', 'vanilla js'],
            'typescript': ['javascript', 'flow', 'coffeescript'],
            'grpc': ['rest', 'thrift', 'protobuf over http', 'custom rpc'],
            'prometheus': ['nagios', 'zabbix', 'datadog', 'new relic', 'custom monitoring'],
            'tensorflow': ['theano', 'caffe', 'torch', 'scikit-learn', 'custom ml'],
            'pytorch': ['tensorflow', 'theano', 'caffe', 'custom ml'],
            'aws lambda': ['ec2', 'elastic beanstalk', 'app engine', 'heroku', 'self-hosted'],
        }

        for key, alternatives in anachronisms.items():
            if key in tech_lower:
                # Filter to only include alternatives that existed in the target era
                era_techs = [t.lower() for t in era.key_technologies]
                valid_alts = [alt for alt in alternatives if any(et in alt for et in era_techs)]
                return valid_alts[:5]

        return []

    def _extract_year(self, date_str: str) -> Optional[int]:
        """Extract year from date string."""
        if not date_str:
            return None

        # Try various formats
        patterns = [
            r'\b(20\d{2}|19\d{2})\b',  # 4-digit year
            r'\b(\d{2})/\d{4}\b',      # MM/YYYY
            r'\b\d{4}-\d{2}\b',         # YYYY-MM
        ]

        for pattern in patterns:
            match = re.search(pattern, date_str)
            if match:
                year_str = match.group(1) if match.groups() else match.group(0)
                try:
                    year = int(year_str[:4])
                    if 1950 <= year <= datetime.now().year + 5:
                        return year
                except ValueError:
                    continue

        # Try month name + year
        months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        for month in months:
            if month in date_str.lower():
                parts = date_str.split()
                for part in parts:
                    if part.isdigit() and len(part) == 4:
                        return int(part)

        return None