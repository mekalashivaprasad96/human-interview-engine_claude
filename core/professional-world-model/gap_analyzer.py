"""
Gap Analyzer - Identifies knowledge and experience gaps relative to target role.
"""

from dataclasses import dataclass, field
from typing import Optional
from ..candidate_intelligence.career_chronology import CareerChronologyEntry
from ..candidate_intelligence.competency_mapper import CompetencyProfile
from .industry_model import IndustryModel


@dataclass
class GapAnalysis:
    technical_gaps: list = field(default_factory=list)
    business_gaps: list = field(default_factory=list)
    leadership_gaps: list = field(default_factory=list)
    scale_gaps: list = field(default_factory=list)
    domain_gaps: list = field(default_factory=list)
    mitigation_strategies: dict = field(default_factory=dict)


class GapAnalyzer:
    """Analyzes gaps between candidate profile and target role requirements."""

    def __init__(self):
        self.industry_model = IndustryModel()

    def analyze(self, chronology_entries: list[CareerChronologyEntry],
                competencies: CompetencyProfile,
                jd_requirements: dict,
                target_industry: str = None) -> GapAnalysis:
        """Analyze gaps between candidate and job requirements."""
        gaps = GapAnalysis()

        # Technical gaps
        gaps.technical_gaps = self._analyze_technical_gaps(
            competencies, jd_requirements
        )

        # Business domain gaps
        gaps.business_gaps = self._analyze_business_gaps(
            competencies, jd_requirements, target_industry
        )

        # Leadership gaps
        gaps.leadership_gaps = self._analyze_leadership_gaps(
            competencies, jd_requirements
        )

        # Scale gaps
        gaps.scale_gaps = self._analyze_scale_gaps(
            chronology_entries, jd_requirements
        )

        # Domain/industry gaps
        gaps.domain_gaps = self._analyze_domain_gaps(
            chronology_entries, jd_requirements, target_industry
        )

        # Generate mitigation strategies
        gaps.mitigation_strategies = self._generate_mitigations(gaps, competencies)

        return gaps

    def _analyze_technical_gaps(self, competencies: CompetencyProfile,
                                 jd_requirements: dict) -> list:
        """Analyze technical skill gaps."""
        gaps = []

        required_technical = jd_requirements.get('required_technical', [])
        preferred_technical = jd_requirements.get('preferred_technical', [])

        candidate_core = set(competencies.technical.get('core', []))
        candidate_proficient = set(competencies.technical.get('proficient', []))
        candidate_familiar = set(competencies.technical.get('familiar', []))
        candidate_all = candidate_core | candidate_proficient | candidate_familiar

        # Check required
        for req in required_technical:
            req_lower = req.lower()
            if not any(req_lower in c or c in req_lower for c in candidate_all):
                gaps.append({
                    'skill': req,
                    'type': 'required',
                    'gap_type': 'technology',
                    'relevance': 'critical',
                    'candidate_level': 'none',
                    'mitigation': self._suggest_tech_mitigation(req, competencies),
                })
            elif any(req_lower in c or c in req_lower for c in candidate_familiar):
                gaps.append({
                    'skill': req,
                    'type': 'required',
                    'gap_type': 'technology',
                    'relevance': 'critical',
                    'candidate_level': 'familiar',
                    'mitigation': 'Deepen to proficient through project work',
                })

        # Check preferred
        for pref in preferred_technical:
            pref_lower = pref.lower()
            if not any(pref_lower in c or c in pref_lower for c in candidate_all):
                gaps.append({
                    'skill': pref,
                    'type': 'preferred',
                    'gap_type': 'technology',
                    'relevance': 'important',
                    'candidate_level': 'none',
                    'mitigation': self._suggest_tech_mitigation(pref, competencies),
                })

        return gaps

    def _analyze_business_gaps(self, competencies: CompetencyProfile,
                                jd_requirements: dict, target_industry: str) -> list:
        """Analyze business domain gaps."""
        gaps = []

        required_domains = jd_requirements.get('business_domains', [])
        candidate_domains = set(competencies.business.get('domains', []))

        for domain in required_domains:
            domain_lower = domain.lower()
            if domain_lower not in [d.lower() for d in candidate_domains]:
                gaps.append({
                    'domain': domain,
                    'gap_type': 'domain',
                    'relevance': 'critical' if 'required' in str(jd_requirements).lower() else 'important',
                    'mitigation': f'Leverage transferable skills from {list(candidate_domains)[:3]}; study {domain} fundamentals',
                })

        # Check for customer-facing requirement
        if jd_requirements.get('customer_facing') and not competencies.business.get('customer_facing'):
            gaps.append({
                'domain': 'customer-facing experience',
                'gap_type': 'business',
                'relevance': 'critical',
                'mitigation': 'Highlight stakeholder management, internal customer work, or consulting experience',
            })

        # Check for P&L/strategic requirement
        if jd_requirements.get('strategic_planning') and not competencies.business.get('strategic_planning'):
            gaps.append({
                'domain': 'strategic planning',
                'gap_type': 'business',
                'relevance': 'important',
                'mitigation': 'Emphasize roadmap contribution, OKR setting, or initiative leadership',
            })

        return gaps

    def _analyze_leadership_gaps(self, competencies: CompetencyProfile,
                                  jd_requirements: dict) -> list:
        """Analyze leadership experience gaps."""
        gaps = []

        leadership = competencies.leadership

        if jd_requirements.get('people_management') and not leadership.get('people_management'):
            gaps.append({
                'area': 'people management',
                'gap_type': 'leadership',
                'relevance': 'critical',
                'mitigation': 'Emphasize technical leadership, mentoring, project leadership; prepare for "how would you manage" questions',
            })

        if jd_requirements.get('technical_leadership') and not leadership.get('technical_leadership'):
            gaps.append({
                'area': 'technical leadership',
                'gap_type': 'leadership',
                'relevance': 'critical',
                'mitigation': 'Highlight architecture decisions, code review leadership, technical mentoring',
            })

        if jd_requirements.get('project_leadership') and not leadership.get('project_leadership'):
            gaps.append({
                'area': 'project leadership',
                'gap_type': 'leadership',
                'relevance': 'important',
                'mitigation': 'Frame feature ownership as project leadership; emphasize cross-functional coordination',
            })

        return gaps

    def _analyze_scale_gaps(self, chronology_entries: list[CareerChronologyEntry],
                             jd_requirements: dict) -> list:
        """Analyze scale/experience gaps."""
        gaps = []

        # Determine max scale from career
        max_team_size = 0
        max_rps = 0
        max_data_volume = 0

        for entry in chronology_entries:
            # Extract scale indicators from scope/description
            scope_lower = entry.scope.lower()

            import re
            team_match = re.search(r'team of (\d+)|(\d+) (?:engineer|developer|person)', scope_lower)
            if team_match:
                size = int(team_match.group(1) or team_match.group(2))
                max_team_size = max(max_team_size, size)

        jd_team = jd_requirements.get('team_size')
        if jd_team and max_team_size < jd_team:
            gaps.append({
                'metric': 'team size',
                'candidate_max': max_team_size,
                'target': jd_team,
                'gap_type': 'scale',
                'relevance': 'important',
                'mitigation': f'Discuss scaling patterns, delegation, processes used at {max_team_size} that transfer to {jd_team}',
            })

        jd_rps = jd_requirements.get('requests_per_second')
        if jd_rps and max_rps < jd_rps:
            gaps.append({
                'metric': 'request throughput',
                'candidate_max': max_rps,
                'target': jd_rps,
                'gap_type': 'scale',
                'relevance': 'important',
                'mitigation': 'Explain architecture patterns for horizontal scaling, caching, async processing',
            })

        return gaps

    def _analyze_domain_gaps(self, chronology_entries: list[CareerChronologyEntry],
                              jd_requirements: dict, target_industry: str) -> list:
        """Analyze industry/domain experience gaps."""
        gaps = []

        candidate_industries = set(e.industry.lower() for e in chronology_entries)

        if target_industry and target_industry.lower() not in candidate_industries:
            gaps.append({
                'domain': target_industry,
                'gap_type': 'domain',
                'relevance': 'important',
                'mitigation': self._suggest_domain_mitigation(target_industry, candidate_industries),
            })

        # Check for specific domain requirements
        required_domains = jd_requirements.get('domain_experience', [])
        for domain in required_domains:
            if domain.lower() not in candidate_industries:
                gaps.append({
                    'domain': domain,
                    'gap_type': 'domain',
                    'relevance': 'critical',
                    'mitigation': self._suggest_domain_mitigation(domain, candidate_industries),
                })

        return gaps

    def _suggest_tech_mitigation(self, tech: str, competencies: CompetencyProfile) -> str:
        """Suggest mitigation for technology gap."""
        # Find related technologies candidate knows
        all_techs = (competencies.technical.get('core', []) +
                     competencies.technical.get('proficient', []) +
                     competencies.technical.get('familiar', []))

        tech_lower = tech.lower()

        # Known relationships
        relations = {
            'kubernetes': ['docker', 'containerization', 'cloud'],
            'aws': ['cloud', 'gcp', 'azure', 'terraform'],
            'kafka': ['messaging', 'event-driven', 'rabbitmq', 'pulsar'],
            'postgresql': ['sql', 'databases', 'mysql', 'relational'],
            'redis': ['caching', 'in-memory', 'key-value'],
            'react': ['frontend', 'javascript', 'vue', 'angular', 'typescript'],
            'python': ['programming', 'data', 'ml', 'backend'],
            'go': ['backend', 'microservices', 'cloud-native', 'rust'],
            'terraform': ['iac', 'infrastructure', 'cloud', 'ansible', 'pulumi'],
        }

        related = relations.get(tech_lower, [])
        known_related = [t for t in all_techs if any(r in t.lower() for r in related)]

        if known_related:
            return f'Strong in related: {", ".join(known_related[:3])}; transferable concepts apply directly'
        return f'Adjacent experience in {", ".join(all_techs[:3])}; fast learning curve expected'

    def _suggest_domain_mitigation(self, target_domain: str, candidate_domains: set) -> str:
        """Suggest mitigation for domain gap."""
        domain_transfers = {
            'fintech': ['ecommerce', 'enterprise', 'cloud'],
            'healthcare': ['enterprise', 'cloud', 'government'],
            'ecommerce': ['fintech', 'social', 'cloud'],
            'cloud': ['fintech', 'ecommerce', 'enterprise'],
            'social': ['ecommerce', 'gaming', 'cloud'],
            'gaming': ['social', 'cloud', 'automotive'],
            'automotive': ['cloud', 'manufacturing', 'iot'],
            'enterprise': ['fintech', 'healthcare', 'cloud'],
        }

        related = domain_transfers.get(target_domain.lower(), [])
        candidate_related = [d for d in candidate_domains if d in related]

        if candidate_related:
            return f'Directly transferable from {", ".join(candidate_related)}: similar {target_domain} priorities (scale, reliability, compliance)'
        return f'Core engineering skills transfer; {target_domain} specifics learnable via {", ".join(related[:2]) or "domain study"}'

    def _generate_mitigations(self, gaps: GapAnalysis, competencies: CompetencyProfile) -> dict:
        """Generate overall mitigation strategies."""
        strategies = {}

        # Collect all critical gaps
        all_gaps = (gaps.technical_gaps + gaps.business_gaps + gaps.leadership_gaps +
                    gaps.scale_gaps + gaps.domain_gaps)

        critical_gaps = [g for g in all_gaps if g.get('relevance') == 'critical']

        if critical_gaps:
            strategies['critical'] = [
                f"Prepare specific talking points for {g.get('skill') or g.get('domain') or g.get('area')}"
                for g in critical_gaps[:5]
            ]

        # Transferable skills narrative
        transferable = competencies.transferable
        if transferable:
            strategies['transferable_narrative'] = [
                f"Emphasize {t.replace('_', ' ')} as bridge to target requirements"
                for t in transferable[:3]
            ]

        # Learning agility evidence
        strategies['learning_agility'] = [
            "Highlight rapid technology adoption in past roles",
            "Provide examples of learning new domains under deadline",
            "Mention self-directed learning projects"
        ]

        return strategies