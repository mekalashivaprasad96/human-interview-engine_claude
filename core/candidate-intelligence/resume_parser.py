"""
Resume Parser - Extracts structured information from candidate resume text.
"""

import re
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class ParsedEmployment:
    employer: str
    title: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration_months: Optional[int] = None
    location: Optional[str] = None
    description: str = ""
    technologies: list = field(default_factory=list)
    accomplishments: list = field(default_factory=list)
    raw_text: str = ""


@dataclass
class ParsedEducation:
    institution: str
    degree: str
    field: str
    graduation_date: Optional[str] = None
    honors: list = field(default_factory=list)


@dataclass
class ParsedCertification:
    name: str
    issuer: str
    date: Optional[str] = None
    expiry: Optional[str] = None


@dataclass
class ParsedResume:
    name: str = ""
    contact: dict = field(default_factory=dict)
    summary: str = ""
    employments: list = field(default_factory=list)
    education: list = field(default_factory=list)
    certifications: list = field(default_factory=list)
    skills: list = field(default_factory=list)
    projects: list = field(default_factory=list)
    raw_text: str = ""


class ResumeParser:
    """Parses resume text into structured data."""

    DATE_PATTERNS = [
        r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}',
        r'\d{1,2}/\d{4}',
        r'\d{4}-\d{2}',
        r'\d{4}',
        r'Present|Current',
    ]

    def __init__(self):
        self.employment_section_headers = [
            'experience', 'employment', 'work history', 'professional experience',
            'career', 'positions', 'roles'
        ]
        self.education_section_headers = [
            'education', 'academic', 'degrees', 'qualifications'
        ]
        self.skills_section_headers = [
            'skills', 'technologies', 'technical skills', 'competencies',
            'tools', 'languages', 'frameworks', 'platforms'
        ]

    def parse(self, text: str) -> ParsedResume:
        """Parse resume text into structured ParsedResume object."""
        resume = ParsedResume(raw_text=text)
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        # Extract name (first non-empty line, typically)
        resume.name = self._extract_name(lines)

        # Extract contact info
        resume.contact = self._extract_contact(text)

        # Split into sections
        sections = self._split_sections(lines)

        # Parse each section
        if 'experience' in sections:
            resume.employments = self._parse_employments(sections['experience'])

        if 'education' in sections:
            resume.education = self._parse_education(sections['education'])

        if 'skills' in sections:
            resume.skills = self._parse_skills(sections['skills'])

        # Extract summary/objective
        resume.summary = self._extract_summary(sections, lines)

        # Extract projects if present
        if 'projects' in sections:
            resume.projects = self._parse_projects(sections['projects'])

        return resume

    def _extract_name(self, lines: list) -> str:
        """Extract candidate name from first few lines."""
        for line in lines[:5]:
            # Skip lines that look like headers or contact info
            if not re.search(r'[@\d]|resume|cv|curriculum', line, re.I):
                if 2 <= len(line.split()) <= 4:
                    return line
        return ""

    def _extract_contact(self, text: str) -> dict:
        """Extract contact information."""
        contact = {}
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match:
            contact['email'] = email_match.group()

        phone_match = re.search(r'[\+]?[(]?\d{1,3}[)]?[-\s\.]?\d{3}[-\s\.]?\d{4}', text)
        if phone_match:
            contact['phone'] = phone_match.group()

        linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', text)
        if linkedin_match:
            contact['linkedin'] = linkedin_match.group()

        github_match = re.search(r'github\.com/[\w-]+', text)
        if github_match:
            contact['github'] = github_match.group()

        return contact

    def _split_sections(self, lines: list) -> dict:
        """Split resume lines into sections based on headers."""
        sections = {}
        current_section = 'header'
        section_lines = []

        for line in lines:
            lower_line = line.lower()
            is_header = False

            for header in self.employment_section_headers:
                if header in lower_line and len(line) < 50:
                    if section_lines:
                        sections[current_section] = section_lines
                    current_section = 'experience'
                    section_lines = []
                    is_header = True
                    break

            if not is_header:
                for header in self.education_section_headers:
                    if header in lower_line and len(line) < 50:
                        if section_lines:
                            sections[current_section] = section_lines
                        current_section = 'education'
                        section_lines = []
                        is_header = True
                        break

            if not is_header:
                for header in self.skills_section_headers:
                    if header in lower_line and len(line) < 50:
                        if section_lines:
                            sections[current_section] = section_lines
                        current_section = 'skills'
                        section_lines = []
                        is_header = True
                        break

            if not is_header:
                if 'project' in lower_line and len(line) < 50:
                    if section_lines:
                        sections[current_section] = section_lines
                    current_section = 'projects'
                    section_lines = []
                    is_header = True

            if not is_header:
                section_lines.append(line)

        if section_lines:
            sections[current_section] = section_lines

        return sections

    def _parse_employments(self, lines: list) -> list:
        """Parse employment entries."""
        employments = []
        current_emp = None

        for line in lines:
            # Check if this looks like a new job entry (company + title pattern)
            if self._looks_like_job_header(line):
                if current_emp:
                    employments.append(current_emp)
                current_emp = self._parse_job_header(line)
            elif current_emp:
                current_emp.description += " " + line
                # Extract technologies from description
                techs = self._extract_technologies(line)
                current_emp.technologies.extend(techs)
                # Extract accomplishments (bullet points)
                if line.startswith(('•', '-', '*', '►', '→')):
                    current_emp.accomplishments.append(line.lstrip('•-*►→ '))

        if current_emp:
            employments.append(current_emp)

        return employments

    def _looks_like_job_header(self, line: str) -> bool:
        """Heuristic to detect job header lines."""
        # Company | Title | Dates pattern
        if re.search(r'\d{4}\s*[-–]\s*(?:\d{4}|Present|Current)', line):
            return True
        # Title at Company pattern
        if re.search(r'(?:Senior|Lead|Principal|Staff|Manager|Director|VP|Engineer|Developer|Architect|Scientist|Analyst)', line, re.I):
            if re.search(r'\b(at|@|,)\b', line):
                return True
        return False

    def _parse_job_header(self, line: str) -> ParsedEmployment:
        """Parse a job header line into ParsedEmployment."""
        emp = ParsedEmployment(raw_text=line)

        # Extract dates
        date_match = re.search(r'(\w+\s+\d{4}|\d{1,2}/\d{4}|\d{4})\s*[-–]\s*(\w+\s+\d{4}|\d{1,2}/\d{4}|\d{4}|Present|Current)', line, re.I)
        if date_match:
            emp.start_date = date_match.group(1)
            emp.end_date = date_match.group(2)

        # Try to split company and title
        parts = re.split(r'\s+\|\s+|\s+at\s+|\s+@\s+|,\s+', line)
        if len(parts) >= 2:
            # Heuristic: longer part is company, shorter is title (or vice versa)
            emp.employer = parts[0].strip()
            emp.title = parts[1].strip()
        else:
            emp.employer = line

        return emp

    def _parse_education(self, lines: list) -> list:
        """Parse education entries."""
        education = []
        current = None

        for line in lines:
            if any(kw in line.lower() for kw in ['bachelor', 'master', 'phd', 'doctorate', 'associate', 'degree', 'university', 'college', 'institute']):
                if current:
                    education.append(current)
                current = ParsedEducation(institution="", degree="", field="")
                # Simple parsing - in reality would be more sophisticated
                current.institution = line
            elif current:
                current.field += " " + line

        if current:
            education.append(current)

        return education

    def _parse_skills(self, lines: list) -> list:
        """Parse skills list."""
        skills = []
        for line in lines:
            # Split by common delimiters
            parts = re.split(r'[,;|•\-\*]', line)
            for part in parts:
                skill = part.strip()
                if skill and len(skill) > 1:
                    skills.append(skill)
        return list(set(skills))  # Deduplicate

    def _parse_projects(self, lines: list) -> list:
        """Parse project entries."""
        projects = []
        current = None

        for line in lines:
            if line and not line.startswith((' ', '\t', '•', '-', '*')):
                if current:
                    projects.append(current)
                current = {'name': line, 'description': '', 'technologies': []}
            elif current:
                current['description'] += " " + line
                techs = self._extract_technologies(line)
                current['technologies'].extend(techs)

        if current:
            projects.append(current)

        return projects

    def _extract_summary(self, sections: dict, lines: list) -> str:
        """Extract professional summary."""
        # Check for summary/objective section
        for key in ['summary', 'objective', 'profile', 'about']:
            if key in sections:
                return ' '.join(sections[key])

        # Fallback: first paragraph after name/contact
        in_header = True
        summary_lines = []
        for line in lines:
            if in_header and len(line) > 50:
                in_header = False
            if not in_header and line:
                summary_lines.append(line)
            if len(summary_lines) >= 3:
                break

        return ' '.join(summary_lines)

    def _extract_technologies(self, text: str) -> list:
        """Extract technology mentions from text."""
        # Common technology patterns
        tech_patterns = [
            r'\b(AWS|GCP|Azure|Kubernetes|Docker|Terraform|Ansible)\b',
            r'\b(Python|Java|Go|Rust|TypeScript|JavaScript|C\+\+|C#|Ruby|Scala|Kotlin)\b',
            r'\b(React|Vue|Angular|Node\.js|Django|Flask|Spring|FastAPI)\b',
            r'\b(PostgreSQL|MySQL|MongoDB|Redis|Cassandra|DynamoDB|Snowflake)\b',
            r'\b(Kafka|RabbitMQ|gRPC|REST|GraphQL|Protobuf)\b',
            r'\b(TensorFlow|PyTorch|Scikit-learn|Pandas|NumPy|Spark|Airflow)\b',
            r'\b(Git|GitHub|GitLab|Jenkins|CircleCI|ArgoCD|Spinnaker)\b',
            r'\b(Linux|Ubuntu|CentOS|RHEL|Windows Server)\b',
        ]

        found = []
        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.I)
            found.extend(matches)

        return list(set(found))