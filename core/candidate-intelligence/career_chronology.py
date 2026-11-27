"""
Career Chronology - Builds timeline and progression analysis from parsed employment history.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from .resume_parser import ParsedEmployment


@dataclass
class CareerChronologyEntry:
    employer: str
    title: str
    start_date: str
    end_date: str
    duration_months: int
    industry: str = ""
    role_type: str = "engineering"
    technologies: list = field(default_factory=list)
    scope: str = ""
    level: str = ""  # junior, mid, senior, staff, principal, manager, director, vp
    progression_marker: str = ""  # promotion, lateral, step-up, new-domain


@dataclass
class CareerChronology:
    entries: list = field(default_factory=list)
    total_years: float = 0.0
    trajectory: str = "steady"
    promotions: list = field(default_factory=list)
    current_level: str = "mid"
    gaps: list = field(default_factory=list)


class CareerChronologyBuilder:
    """Builds career chronology from parsed employments."""

    LEVEL_INDICATORS = {
        'junior': ['junior', 'entry', 'associate i', 'engineer i', 'developer i', 'analyst i'],
        'mid': ['engineer ii', 'developer ii', 'software engineer', 'full stack', 'backend', 'frontend', 'analyst ii'],
        'senior': ['senior', 'sr.', 'lead', 'staff', 'principal', 'architect', 'technical lead', 'team lead'],
        'manager': ['manager', 'engineering manager', 'development manager', 'technical manager'],
        'director': ['director', 'head of', 'vp engineering', 'vice president'],
        'vp': ['vp', 'vice president', 'svp', 'evp', 'c-level', 'cto', 'cio'],
    }

    ROLE_TYPE_KEYWORDS = {
        'engineering': ['engineer', 'developer', 'programmer', 'coding', 'software', 'backend', 'frontend', 'fullstack', 'full-stack', 'devops', 'sre', 'platform', 'infrastructure'],
        'architecture': ['architect', 'architecture', 'system design', 'technical strategy'],
        'management': ['manager', 'director', 'lead', 'head', 'supervisor', 'team lead'],
        'support': ['support', 'operations', 'ops', 'production', 'reliability', 'incident', 'on-call'],
        'consulting': ['consultant', 'consulting', 'advisory', 'professional services', 'solutions engineer', 'solutions architect'],
        'sales-engineering': ['sales engineer', 'solutions engineer', 'pre-sales', 'se ', 'sales engineering'],
        'product': ['product manager', 'product owner', 'technical product', 'pm '],
        'research': ['research', 'scientist', 'ml engineer', 'machine learning', 'data scientist', 'ai researcher'],
    }

    INDUSTRY_KEYWORDS = {
        'fintech': ['finance', 'banking', 'fintech', 'payments', 'trading', 'capital markets', 'insurance'],
        'healthcare': ['healthcare', 'medical', 'pharma', 'biotech', 'clinical', 'hospital', 'ehr', 'hipaa'],
        'ecommerce': ['ecommerce', 'retail', 'marketplace', 'shopping', 'merchandise', 'inventory'],
        'cloud': ['cloud', 'aws', 'azure', 'gcp', 'infrastructure', 'hosting', 'saas', 'paas', 'iaas'],
        'social': ['social', 'media', 'content', 'advertising', 'ads', 'feed', 'recommendation'],
        'gaming': ['gaming', 'game', 'unity', 'unreal', 'multiplayer', 'mobile game'],
        'enterprise': ['enterprise', 'b2b', 'saas', 'crm', 'erp', 'workflow', 'productivity'],
        'automotive': ['automotive', 'vehicle', 'autonomous', 'adas', 'tesla', 'ford', 'gm'],
        'telecom': ['telecom', 'telecommunications', '5g', 'network', 'isp', 'carrier'],
        'government': ['government', 'federal', 'defense', 'public sector', 'contractor'],
        'education': ['education', 'edtech', 'university', 'learning', 'course', 'training'],
        'manufacturing': ['manufacturing', 'industrial', 'iot', 'supply chain', 'logistics', 'factory'],
    }

    def build(self, employments: list[ParsedEmployment]) -> CareerChronology:
        """Build complete career chronology from parsed employments."""
        chronology = CareerChronology()

        # Sort employments by start date
        sorted_employments = self._sort_by_date(employments)

        previous_level = None
        previous_end = None

        for i, emp in enumerate(sorted_employments):
            entry = self._create_entry(emp, i, sorted_employments)
            chronology.entries.append(entry)

            # Track progression
            if previous_level and entry.level != previous_level:
                self._record_progression(chronology, previous_level, entry.level, emp.employer)

            previous_level = entry.level
            previous_end = emp.end_date

        # Calculate totals
        chronology.total_years = sum(e.duration_months for e in chronology.entries) / 12
        chronology.current_level = chronology.entries[-1].level if chronology.entries else "mid"
        chronology.trajectory = self._determine_trajectory(chronology)
        chronology.gaps = self._identify_gaps(sorted_employments)

        return chronology

    def _sort_by_date(self, employments: list[ParsedEmployment]) -> list[ParsedEmployment]:
        """Sort employments by start date."""
        def parse_date(date_str: str) -> datetime:
            if not date_str:
                return datetime.min
            # Try multiple formats
            for fmt in ['%b %Y', '%B %Y', '%m/%Y', '%Y-%m', '%Y']:
                try:
                    return datetime.strptime(date_str.strip(), fmt)
                except ValueError:
                    continue
            return datetime.min

        return sorted(employments, key=lambda e: parse_date(e.start_date or ""))

    def _create_entry(self, emp: ParsedEmployment, index: int, all_employments: list) -> CareerChronologyEntry:
        """Create a chronology entry from parsed employment."""
        entry = CareerChronologyEntry(
            employer=emp.employer,
            title=emp.title,
            start_date=emp.start_date or "",
            end_date=emp.end_date or "",
            technologies=emp.technologies,
        )

        # Calculate duration
        entry.duration_months = self._calculate_duration(emp.start_date, emp.end_date)

        # Infer industry
        entry.industry = self._infer_industry(emp.employer, emp.description, emp.technologies)

        # Infer role type
        entry.role_type = self._infer_role_type(emp.title, emp.description)

        # Infer level
        entry.level = self._infer_level(emp.title, emp.description, entry.duration_months)

        # Determine progression marker
        if index > 0:
            prev = all_employments[index - 1]
            entry.progression_marker = self._determine_progression(prev, emp, entry.level)

        return entry

    def _calculate_duration(self, start: Optional[str], end: Optional[str]) -> int:
        """Calculate duration in months."""
        if not start:
            return 0

        def parse(date_str: str) -> Optional[datetime]:
            if not date_str or date_str.lower() in ['present', 'current']:
                return datetime.now()
            for fmt in ['%b %Y', '%B %Y', '%m/%Y', '%Y-%m', '%Y']:
                try:
                    return datetime.strptime(date_str.strip(), fmt)
                except ValueError:
                    continue
            return None

        start_dt = parse(start)
        end_dt = parse(end) if end else datetime.now()

        if not start_dt or not end_dt:
            return 0

        months = (end_dt.year - start_dt.year) * 12 + (end_dt.month - start_dt.month)
        return max(0, months)

    def _infer_industry(self, employer: str, description: str, technologies: list) -> str:
        """Infer industry from employer name, description, and technologies."""
        text = f"{employer} {description} {' '.join(technologies)}".lower()

        scores = {}
        for industry, keywords in self.INDUSTRY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[industry] = score

        if scores:
            return max(scores, key=scores.get)
        return "technology"

    def _infer_role_type(self, title: str, description: str) -> str:
        """Infer role type from title and description."""
        text = f"{title} {description}".lower()

        scores = {}
        for role_type, keywords in self.ROLE_TYPE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[role_type] = score

        if scores:
            return max(scores, key=scores.get)
        return "engineering"

    def _infer_level(self, title: str, description: str, duration_months: int) -> str:
        """Infer seniority level from title, description, and tenure."""
        text = f"{title} {description}".lower()

        # Check explicit level indicators
        for level, keywords in self.LEVEL_INDICATORS.items():
            for kw in keywords:
                if kw in text:
                    return level

        # Infer from tenure if no explicit indicator
        if duration_months >= 96:  # 8+ years
            return "senior"
        elif duration_months >= 48:  # 4+ years
            return "mid"
        elif duration_months >= 12:
            return "junior"
        return "junior"

    def _determine_progression(self, prev: ParsedEmployment, curr: ParsedEmployment, curr_level: str) -> str:
        """Determine progression type between roles."""
        prev_level = self._infer_level(prev.title, prev.description, self._calculate_duration(prev.start_date, prev.end_date))

        level_order = ['junior', 'mid', 'senior', 'staff', 'principal', 'manager', 'director', 'vp']
        prev_idx = level_order.index(prev_level) if prev_level in level_order else 1
        curr_idx = level_order.index(curr_level) if curr_level in level_order else 1

        if curr_idx > prev_idx:
            return "promotion"
        elif curr_idx < prev_idx:
            return "step-down"
        else:
            # Check if different domain
            prev_industry = self._infer_industry(prev.employer, prev.description, prev.technologies)
            curr_industry = self._infer_industry(curr.employer, curr.description, curr.technologies)
            if prev_industry != curr_industry:
                return "domain-switch"
            return "lateral"

    def _record_progression(self, chronology: CareerChronology, from_level: str, to_level: str, employer: str):
        """Record a progression event."""
        level_order = ['junior', 'mid', 'senior', 'staff', 'principal', 'manager', 'director', 'vp']
        if level_order.index(to_level) > level_order.index(from_level):
            chronology.promotions.append(f"{from_level} → {to_level} at {employer}")

    def _determine_trajectory(self, chronology: CareerChronology) -> str:
        """Determine overall career trajectory."""
        if not chronology.entries:
            return "steady"

        levels = [e.level for e in chronology.entries]
        level_order = ['junior', 'mid', 'senior', 'staff', 'principal', 'manager', 'director', 'vp']

        # Count promotions
        promotions = 0
        for i in range(1, len(levels)):
            if level_order.index(levels[i]) > level_order.index(levels[i-1]):
                promotions += 1

        total_roles = len(levels)
        if promotions >= total_roles * 0.5:
            return "accelerated"
        elif promotions == 0:
            # Check for domain switches
            domain_switches = sum(1 for e in chronology.entries if e.progression_marker == "domain-switch")
            if domain_switches >= total_roles * 0.3:
                return "lateral"
            return "steady"
        return "mixed"

    def _identify_gaps(self, employments: list[ParsedEmployment]) -> list:
        """Identify employment gaps."""
        gaps = []
        sorted_emps = self._sort_by_date(employments)

        for i in range(1, len(sorted_emps)):
            prev_end = sorted_emps[i-1].end_date
            curr_start = sorted_emps[i].start_date

            if prev_end and curr_start:
                prev_dt = self._parse_date(prev_end)
                curr_dt = self._parse_date(curr_start)

                if prev_dt and curr_dt:
                    gap_months = (curr_dt.year - prev_dt.year) * 12 + (curr_dt.month - prev_dt.month)
                    if gap_months > 3:  # Gap > 3 months
                        gaps.append({
                            "period": f"{prev_end} - {curr_start}",
                            "duration_months": gap_months,
                            "between": f"{sorted_emps[i-1].employer} → {sorted_emps[i].employer}"
                        })

        return gaps

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime."""
        if not date_str or date_str.lower() in ['present', 'current']:
            return datetime.now()
        for fmt in ['%b %Y', '%B %Y', '%m/%Y', '%Y-%m', '%Y']:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return None