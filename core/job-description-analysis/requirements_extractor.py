"""
Requirements Extractor - Extracts detailed requirements and expectations from parsed JD.
"""

from dataclasses import dataclass, field
from typing import Optional
from .jd_parser import ParsedJD


@dataclass
class JobRequirements:
    required_technical: list = field(default_factory=list)
    preferred_technical: list = field(default_factory=list)
    required_experience_years: int = 0
    preferred_experience_years: int = 0
    required_education: list = field(default_factory=list)
    required_certifications: list = field(default_factory=list)
    business_domains: list = field(default_factory=list)
    soft_skills: list = field(default_factory=list)
    leadership_expectations: dict = field(default_factory=dict)
    scale_expectations: dict = field(default_factory=dict)
    team_size: Optional[int] = None
    customer_facing: bool = False
    strategic_planning: bool = False
    p_l_responsibility: bool = False
    vendor_management: bool = False
    domain_experience: list = field(default_factory=list)
    evaluation_focus: list = field(default_factory=list)
    interview_format: list = field(default_factory=list)


class RequirementsExtractor:
    """Extracts detailed requirements from parsed job description."""

    def extract(self, parsed_jd: ParsedJD) -> JobRequirements:
        """Extract all requirements from parsed JD."""
        req = JobRequirements()

        # Technical requirements
        req.required_technical = parsed_jd.required_technical
        req.preferred_technical = parsed_jd.preferred_technical

        # Experience years
        req.required_experience_years = self._extract_years(parsed_jd.required_qualifications, 'required')
        req.preferred_experience_years = self._extract_years(parsed_jd.preferred_qualifications, 'preferred')

        # Education
        req.required_education = self._extract_education(parsed_jd.required_qualifications)

        # Certifications
        req.required_certifications = self._extract_certifications(parsed_jd.required_qualifications)

        # Business domains
        req.business_domains = parsed_jd.business_domains

        # Soft skills
        req.soft_skills = parsed_jd.soft_skills

        # Leadership expectations
        req.leadership_expectations = self._extract_leadership(parsed_jd)

        # Scale expectations
        req.scale_expectations = self._extract_scale(parsed_jd)

        # Team size
        req.team_size = self._extract_team_size(parsed_jd.team_info, parsed_jd.responsibilities)

        # Customer facing
        req.customer_facing = self._check_customer_facing(parsed_jd)

        # Strategic planning
        req.strategic_planning = self._check_strategic(parsed_jd)

        # P&L responsibility
        req.p_l_responsibility = self._check_pnl(parsed_jd)

        # Vendor management
        req.vendor_management = self._check_vendor(parsed_jd)

        # Domain experience
        req.domain_experience = self._extract_domain_exp(parsed_jd)

        # Evaluation focus
        req.evaluation_focus = self._determine_evaluation_focus(parsed_jd)

        # Interview format
        req.interview_format = self._infer_interview_format(parsed_jd)

        return req

    def _extract_years(self, qualifications: list, req_type: str) -> int:
        """Extract years of experience requirement."""
        text = ' '.join(qualifications).lower()

        patterns = [
            r'(\d+)[\+\-]\s*years?',
            r'(\d+)\s*to\s*(\d+)\s*years?',
            r'at least (\d+)\s*years?',
            r'minimum (\d+)\s*years?',
            r'(\d+)\s*years? experience',
        ]

        years = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    years.extend([int(m) for m in match if m.isdigit()])
                elif match.isdigit():
                    years.append(int(match))

        if years:
            return max(years) if req_type == 'required' else max(years)
        return 0

    def _extract_education(self, qualifications: list) -> list:
        """Extract education requirements."""
        text = ' '.join(qualifications).lower()
        education = []

        degrees = [
            'bachelor', 'master', 'phd', 'doctorate', 'associate',
            'bs', 'ms', 'm.s.', 'b.s.', 'mba', 'm.s.', 'b.a.', 'm.a.',
            "bachelor's", "master's", 'degree',
        ]

        for degree in degrees:
            if degree in text:
                education.append(degree)

        fields = [
            'computer science', 'cs', 'engineering', 'software engineering',
            'electrical', 'mechanical', 'math', 'mathematics', 'physics',
            'information systems', 'information technology', 'it',
            'data science', 'machine learning', 'artificial intelligence',
        ]

        for field in fields:
            if field in text:
                education.append(field)

        return list(set(education))

    def _extract_certifications(self, qualifications: list) -> list:
        """Extract certification requirements."""
        text = ' '.join(qualifications).lower()
        certs = []

        known_certs = [
            'aws certified', 'aws solutions architect', 'aws developer', 'aws sysops',
            'azure certified', 'azure administrator', 'azure developer', 'azure architect',
            'gcp certified', 'google cloud certified', 'cloud architect', 'data engineer',
            'kubernetes', 'cka', 'ckad', 'cks',
            'pmp', 'scrum master', 'csm', 'psm', 'safe',
            'cissp', 'cisa', 'cism', 'security+', 'ceh',
            'terraform', 'hashicorp',
            'kafka', 'confluent',
            'snowflake', 'databricks',
        ]

        for cert in known_certs:
            if cert in text:
                certs.append(cert)

        return certs

    def _extract_leadership(self, parsed_jd: ParsedJD) -> dict:
        """Extract leadership expectations."""
        text = ' '.join(parsed_jd.responsibilities + parsed_jd.required_qualifications).lower()

        expectations = {
            'people_management': False,
            'team_size': None,
            'technical_leadership': False,
            'project_leadership': False,
            'mentoring': False,
            'hiring': False,
            'architectural_decision_making': False,
        }

        if any(kw in text for kw in ['manage', 'lead', 'supervise', 'direct reports', 'team of']):
            expectations['people_management'] = True
            # Extract team size
            import re
            match = re.search(r'team of (\d+)|(\d+) (?:person|engineer|developer|member|direct report)', text)
            if match:
                expectations['team_size'] = int(match.group(1) or match.group(2))

        if any(kw in text for kw in ['technical lead', 'tech lead', 'architecture', 'technical decisions', 'design review']):
            expectations['technical_leadership'] = True

        if any(kw in text for kw in ['project lead', 'project manage', 'delivery lead', 'program manage', 'initiative']):
            expectations['project_leadership'] = True

        if any(kw in text for kw in ['mentor', 'coach', 'develop talent', 'grow team', 'onboard']):
            expectations['mentoring'] = True

        if any(kw in text for kw in ['hire', 'recruit', 'interview', 'build team']):
            expectations['hiring'] = True

        if any(kw in text for kw in ['architect', 'architecture', 'technical strategy', 'roadmap', 'technical vision']):
            expectations['architectural_decision_making'] = True

        return expectations

    def _extract_scale(self, parsed_jd: ParsedJD) -> dict:
        """Extract scale expectations."""
        text = ' '.join(parsed_jd.responsibilities + parsed_jd.required_qualifications).lower()

        scale = {
            'requests_per_second': None,
            'data_volume': None,
            'users': None,
            'transactions_per_second': None,
            'servers_nodes': None,
            'team_size': None,
            'geographic_regions': None,
        }

        import re

        # Requests per second
        rps_match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?)\s*[km]?\s*requests?\s*per\s*second|(\d+(?:,\d+)*(?:\.\d+)?)\s*[km]?\s*rps', text)
        if rps_match:
            val = rps_match.group(1) or rps_match.group(2)
            scale['requests_per_second'] = self._parse_number(val)

        # TPS
        tps_match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?)\s*[km]?\s*transactions?\s*per\s*second|(\d+(?:,\d+)*(?:\.\d+)?)\s*[km]?\s*tps', text)
        if tps_match:
            val = tps_match.group(1) or tps_match.group(2)
            scale['transactions_per_second'] = self._parse_number(val)

        # Users
        users_match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?)\s*[km]?\s*(?:active )?users?|(\d+(?:,\d+)*(?:\.\d+)?)\s*[km]?\s*(?:dau|mau)', text)
        if users_match:
            val = users_match.group(1) or users_match.group(2)
            scale['users'] = self._parse_number(val)

        # Data volume
        data_match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?)\s*[kmg]?\s*(?:tb|pb|gb)\s*(?:per day|daily|per month|monthly)?', text)
        if data_match:
            scale['data_volume'] = data_match.group(0)

        # Team size
        team_match = re.search(r'team of (\d+)|(\d+) (?:person|engineer|developer|member)', text)
        if team_match:
            scale['team_size'] = int(team_match.group(1) or team_match.group(2))

        return scale

    def _extract_team_size(self, team_info: str, responsibilities: list) -> Optional[int]:
        """Extract team size from various sources."""
        import re
        text = team_info + ' ' + ' '.join(responsibilities)

        match = re.search(r'team of (\d+)|(\d+) (?:person|engineer|developer|member|direct report)', text, re.I)
        if match:
            return int(match.group(1) or match.group(2))
        return None

    def _check_customer_facing(self, parsed_jd: ParsedJD) -> bool:
        """Check if role is customer-facing."""
        text = ' '.join(parsed_jd.responsibilities + parsed_jd.required_qualifications).lower()
        return any(kw in text for kw in [
            'customer facing', 'client facing', 'external customer', 'client interaction',
            'customer success', 'account management', 'sales engineer', 'solutions engineer',
            'professional services', 'consulting', 'pre-sales', 'post-sales'
        ])

    def _check_strategic(self, parsed_jd: ParsedJD) -> bool:
        """Check if role involves strategic planning."""
        text = ' '.join(parsed_jd.responsibilities + parsed_jd.required_qualifications).lower()
        return any(kw in text for kw in [
            'strategic', 'roadmap', 'vision', 'long.term', 'direction',
            'okr', 'kpi', 'business strategy', 'technical strategy',
            'architecture strategy', 'investment', 'portfolio'
        ])

    def _check_pnl(self, parsed_jd: ParsedJD) -> bool:
        """Check if role has P&L responsibility."""
        text = ' '.join(parsed_jd.responsibilities + parsed_jd.required_qualifications).lower()
        return any(kw in text for kw in [
            'p&l', 'profit and loss', 'budget', 'revenue', 'cost optimization',
            'financial ownership', 'business outcomes', 'roi', 'investment decisions'
        ])

    def _check_vendor(self, parsed_jd: ParsedJD) -> bool:
        """Check if role involves vendor management."""
        text = ' '.join(parsed_jd.responsibilities + parsed_jd.required_qualifications).lower()
        return any(kw in text for kw in [
            'vendor', 'third party', 'procurement', 'outsourcing',
            'partner management', 'supplier', 'contract negotiation'
        ])

    def _extract_domain_exp(self, parsed_jd: ParsedJD) -> list:
        """Extract required domain experience."""
        domains = parsed_jd.business_domains.copy()

        text = ' '.join(parsed_jd.required_qualifications).lower()
        domain_keywords = [
            'fintech', 'payments', 'banking', 'healthcare', 'ecommerce',
            'saas', 'enterprise', 'social', 'gaming', 'automotive',
            'telecom', 'government', 'education', 'logistics', 'streaming',
        ]

        for domain in domain_keywords:
            if domain in text and domain not in domains:
                domains.append(domain)

        return domains

    def _determine_evaluation_focus(self, parsed_jd: ParsedJD) -> list:
        """Determine likely interview evaluation focus areas."""
        focus = []

        text = ' '.join(parsed_jd.responsibilities + parsed_jd.required_qualifications + parsed_jd.preferred_qualifications).lower()

        focus_map = {
            'coding': ['code', 'programming', 'algorithm', 'data structure', 'leetcode'],
            'system_design': ['system design', 'architecture', 'scalability', 'distributed systems', 'high availability'],
            'behavioral': ['leadership', 'collaboration', 'conflict', 'failure', 'mistake', 'difficult', 'challenge'],
            'domain_knowledge': ['domain', 'industry', 'fintech', 'healthcare', 'payments', 'compliance'],
            'debugging': ['debug', 'troubleshoot', 'incident', 'production issue', 'root cause', 'on-call'],
            'ml_ai': ['machine learning', 'ml', 'ai', 'model', 'training', 'inference', 'pytorch', 'tensorflow'],
            'data': ['data engineering', 'etl', 'pipeline', 'spark', 'flink', 'kafka', 'warehouse'],
            'security': ['security', 'vulnerability', 'compliance', 'audit', 'encryption', 'authentication'],
            'devops': ['ci/cd', 'deployment', 'kubernetes', 'infrastructure', 'terraform', 'ansible'],
            'frontend': ['frontend', 'ui', 'ux', 'react', 'vue', 'angular', 'web', 'mobile'],
            'backend': ['backend', 'api', 'microservice', 'service', 'database', 'sql'],
        }

        for area, keywords in focus_map.items():
            if any(kw in text for kw in keywords):
                focus.append(area)

        # Default focus areas if none detected
        if not focus:
            focus = ['coding', 'system_design', 'behavioral']

        return focus

    def _infer_interview_format(self, parsed_jd: ParsedJD) -> list:
        """Infer interview format from JD."""
        formats = []

        text = ' '.join(parsed_jd.raw_text).lower()

        if any(kw in text for kw in ['whiteboard', 'coding challenge', 'leetcode', 'hackerrank', 'codility']):
            formats.append('coding_challenge')
        if any(kw in text for kw in ['system design', 'architecture review', 'design exercise']):
            formats.append('system_design')
        if any(kw in text for kw in ['behavioral', 'competency', 'star', 'leadership principles', 'culture']):
            formats.append('behavioral')
        if any(kw in text for kw in ['take.home', 'take home', 'homework', 'project']):
            formats.append('take_home')
        if any(kw in text for kw in ['pair programming', 'pairing', 'collaborative coding']):
            formats.append('pair_programming')
        if any(kw in text for kw in ['presentation', 'case study', 'technical presentation']):
            formats.append('presentation')
        if any(kw in text for kw in ['debugging', 'troubleshooting', 'incident response']):
            formats.append('debugging_exercise')

        return formats if formats else ['coding', 'system_design', 'behavioral']

    def _parse_number(self, val: str) -> float:
        """Parse number with k/m suffixes."""
        val = val.replace(',', '').lower()
        if val.endswith('k'):
            return float(val[:-1]) * 1000
        elif val.endswith('m'):
            return float(val[:-1]) * 1000000
        return float(val)