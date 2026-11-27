"""
Seniority Assessor - Determines candidate seniority level from multiple signals.
"""

from dataclasses import dataclass
from typing import Optional
from .resume_parser import ParsedResume
from .career_chronology import CareerChronology, CareerChronologyEntry
from .competency_mapper import CompetencyProfile


@dataclass
class SeniorityAssessment:
    level: str
    confidence: float
    signals: dict
    years_experience: float
    scope_indicators: list


class SeniorityAssessor:
    """Assesses candidate seniority from multiple signals."""

    LEVEL_ORDER = ['junior', 'mid', 'senior', 'staff', 'principal', 'manager', 'director', 'vp']

    TITLE_LEVEL_MAP = {
        'junior': [
            'junior', 'entry', 'associate i', 'engineer i', 'developer i',
            'analyst i', 'programmer i', 'intern', 'trainee', 'graduate'
        ],
        'mid': [
            'engineer ii', 'developer ii', 'software engineer', 'full stack engineer',
            'backend engineer', 'frontend engineer', 'systems engineer',
            'devops engineer', 'sre', 'platform engineer', 'data engineer',
            'ml engineer', 'analyst ii', 'consultant', 'associate'
        ],
        'senior': [
            'senior', 'sr.', 'lead engineer', 'technical lead', 'team lead',
            'staff engineer', 'principal engineer', 'architect', 'technical architect',
            'solutions architect', 'lead developer', 'lead analyst'
        ],
        'staff': [
            'staff', 'principal', 'distinguished', 'fellow', 'technical fellow',
            'chief architect', 'chief engineer'
        ],
        'manager': [
            'engineering manager', 'development manager', 'software development manager',
            'technical manager', 'manager, engineering', 'manager, software'
        ],
        'director': [
            'director', 'director of engineering', 'director of technology',
            'head of engineering', 'head of technology', 'vp engineering', 'vice president engineering'
        ],
        'vp': [
            'vp', 'vice president', 'svp', 'evp', 'cto', 'cio', 'chief technology',
            'chief information', 'chief engineering'
        ],
    }

    SCOPE_INDICATORS = {
        'task': ['task', 'ticket', 'bug fix', 'feature', 'story', 'assignment'],
        'feature': ['feature', 'module', 'component', 'service', 'api', 'subsystem'],
        'system': ['system', 'platform', 'architecture', 'infrastructure', 'pipeline', 'framework'],
        'platform': ['platform', 'ecosystem', 'organization-wide', 'cross-team', 'enterprise'],
        'organization': ['organization', 'company', 'business', 'strategy', 'transformation'],
    }

    def assess(self, resume: ParsedResume, chronology: CareerChronology,
               competencies: CompetencyProfile) -> SeniorityAssessment:
        """Assess seniority from all available signals."""
        signals = {}

        # Signal 1: Title analysis
        title_signal = self._analyze_titles(resume, chronology)
        signals['title'] = title_signal

        # Signal 2: Tenure/experience years
        tenure_signal = self._analyze_tenure(chronology)
        signals['tenure'] = tenure_signal

        # Signal 3: Scope of responsibility
        scope_signal = self._analyze_scope(chronology, competencies)
        signals['scope'] = scope_signal

        # Signal 4: Leadership indicators
        leadership_signal = self._analyze_leadership(competencies)
        signals['leadership'] = leadership_signal

        # Signal 5: Technical depth
        tech_signal = self._analyze_technical_depth(competencies, chronology)
        signals['technical_depth'] = tech_signal

        # Signal 6: Business impact
        business_signal = self._analyze_business_impact(competencies, chronology)
        signals['business_impact'] = business_signal

        # Combine signals with weights
        weights = {
            'title': 0.25,
            'tenure': 0.20,
            'scope': 0.20,
            'leadership': 0.15,
            'technical_depth': 0.10,
            'business_impact': 0.10,
        }

        level_scores = {level: 0.0 for level in self.LEVEL_ORDER}

        for signal_name, signal_data in signals.items():
            weight = weights.get(signal_name, 0)
            for level, score in signal_data.get('level_scores', {}).items():
                if level in level_scores:
                    level_scores[level] += score * weight

        # Determine final level
        final_level = max(level_scores, key=level_scores.get)
        confidence = level_scores[final_level]

        # Collect scope indicators
        scope_indicators = scope_signal.get('indicators', [])

        return SeniorityAssessment(
            level=final_level,
            confidence=min(confidence, 1.0),
            signals=signals,
            years_experience=chronology.total_years,
            scope_indicators=scope_indicators
        )

    def _analyze_titles(self, resume: ParsedResume, chronology: CareerChronology) -> dict:
        """Analyze job titles for seniority signals."""
        level_scores = {level: 0.0 for level in self.LEVEL_ORDER}
        title_evidence = []

        # Check current/most recent title
        if chronology.entries:
            latest = chronology.entries[-1]
            title = latest.title.lower()
            for level, keywords in self.TITLE_LEVEL_MAP.items():
                for kw in keywords:
                    if kw in title:
                        level_scores[level] += 1.0
                        title_evidence.append(f"Title '{latest.title}' matches {level}")
                        break

        # Check all titles
        for entry in chronology.entries:
            title = entry.title.lower()
            for level, keywords in self.TITLE_LEVEL_MAP.items():
                for kw in keywords:
                    if kw in title:
                        level_scores[level] += 0.3
                        break

        return {'level_scores': level_scores, 'evidence': title_evidence}

    def _analyze_tenure(self, chronology: CareerChronology) -> dict:
        """Analyze years of experience."""
        level_scores = {level: 0.0 for level in self.LEVEL_ORDER}
        years = chronology.total_years

        # Map years to likely level
        if years < 2:
            level_scores['junior'] = 1.0
        elif years < 4:
            level_scores['mid'] = 1.0
            level_scores['junior'] = 0.3
        elif years < 7:
            level_scores['senior'] = 1.0
            level_scores['mid'] = 0.5
        elif years < 10:
            level_scores['staff'] = 1.0
            level_scores['senior'] = 0.5
        elif years < 13:
            level_scores['principal'] = 1.0
            level_scores['staff'] = 0.5
        elif years < 16:
            level_scores['director'] = 1.0
            level_scores['principal'] = 0.5
        else:
            level_scores['vp'] = 1.0
            level_scores['director'] = 0.5

        return {'level_scores': level_scores, 'evidence': [f"Total experience: {years:.1f} years"]}

    def _analyze_scope(self, chronology: CareerChronology, competencies: CompetencyProfile) -> dict:
        """Analyze scope of responsibility."""
        level_scores = {level: 0.0 for level in self.LEVEL_ORDER}
        indicators = []

        # Check scope from chronology entries
        max_scope = 'task'
        for entry in chronology.entries:
            scope = entry.scope.lower()
            for level, keywords in self.SCOPE_INDICATORS.items():
                for kw in keywords:
                    if kw in scope:
                        scope_order = ['task', 'feature', 'system', 'platform', 'organization']
                        if scope_order.index(level) > scope_order.index(max_scope):
                            max_scope = level
                        indicators.append(f"Scope keyword '{kw}' in {entry.employer}")

        # Map max scope to level
        scope_to_level = {
            'task': 'junior',
            'feature': 'mid',
            'system': 'senior',
            'platform': 'staff',
            'organization': 'principal',
        }
        if max_scope in scope_to_level:
            level_scores[scope_to_level[max_scope]] = 1.0

        # Leadership scope
        if competencies.leadership.get('people_management'):
            team_size = competencies.leadership.get('team_size_managed', 0)
            if team_size >= 20:
                level_scores['director'] = max(level_scores['director'], 0.8)
            elif team_size >= 10:
                level_scores['manager'] = max(level_scores['manager'], 0.8)
            elif team_size >= 5:
                level_scores['senior'] = max(level_scores['senior'], 0.6)
            else:
                level_scores['mid'] = max(level_scores['mid'], 0.4)

        return {'level_scores': level_scores, 'indicators': indicators, 'evidence': indicators}

    def _analyze_leadership(self, competencies: CompetencyProfile) -> dict:
        """Analyze leadership indicators."""
        level_scores = {level: 0.0 for level in self.LEVEL_ORDER}
        evidence = []

        leadership = competencies.leadership
        if leadership.get('people_management'):
            level_scores['manager'] += 0.8
            evidence.append("People management experience")
        if leadership.get('technical_leadership'):
            level_scores['senior'] += 0.5
            level_scores['staff'] += 0.3
            evidence.append("Technical leadership")
        if leadership.get('project_leadership'):
            level_scores['senior'] += 0.3
            evidence.append("Project leadership")
        if leadership.get('mentoring'):
            level_scores['senior'] += 0.2
            evidence.append("Mentoring")
        if leadership.get('hiring'):
            level_scores['senior'] += 0.2
            evidence.append("Hiring involvement")

        return {'level_scores': level_scores, 'evidence': evidence}

    def _analyze_technical_depth(self, competencies: CompetencyProfile, chronology: CareerChronology) -> dict:
        """Analyze technical depth and breadth."""
        level_scores = {level: 0.0 for level in self.LEVEL_ORDER}
        evidence = []

        tech = competencies.technical
        core_count = len(tech.get('core', []))
        proficient_count = len(tech.get('proficient', []))
        domains = len(tech.get('domains', []))

        # Depth from core technologies
        if core_count >= 5:
            level_scores['staff'] += 0.4
            level_scores['senior'] += 0.6
            evidence.append(f"{core_count} core technologies")
        elif core_count >= 3:
            level_scores['senior'] += 0.5
            level_scores['mid'] += 0.3
            evidence.append(f"{core_count} core technologies")
        elif core_count >= 1:
            level_scores['mid'] += 0.4
            evidence.append(f"{core_count} core technologies")

        # Breadth from domains
        if domains >= 6:
            level_scores['principal'] += 0.3
            level_scores['staff'] += 0.4
            evidence.append(f"Breadth across {domains} technical domains")
        elif domains >= 4:
            level_scores['senior'] += 0.3
            evidence.append(f"Breadth across {domains} technical domains")

        return {'level_scores': level_scores, 'evidence': evidence}

    def _analyze_business_impact(self, competencies: CompetencyProfile, chronology: CareerChronology) -> dict:
        """Analyze business impact indicators."""
        level_scores = {level: 0.0 for level in self.LEVEL_ORDER}
        evidence = []

        business = competencies.business
        if business.get('strategic_planning'):
            level_scores['director'] += 0.5
            level_scores['principal'] += 0.3
            evidence.append("Strategic planning")
        if business.get('p_l_responsibility'):
            level_scores['director'] += 0.6
            level_scores['vp'] += 0.3
            evidence.append("P&L responsibility")
        if business.get('customer_facing'):
            level_scores['senior'] += 0.2
            evidence.append("Customer-facing role")
        if business.get('vendor_management'):
            level_scores['manager'] += 0.2
            evidence.append("Vendor management")

        return {'level_scores': level_scores, 'evidence': evidence}