"""
Employer Context Builder - Builds detailed context for each employer from resume and public knowledge.
"""

from dataclasses import dataclass, field
from typing import Optional
from ..candidate_intelligence.resume_parser import ParsedEmployment
from ..candidate_intelligence.career_chronology import CareerChronologyEntry


@dataclass
class EmployerContext:
    name: str
    industry: str
    business_model: str
    operational_priorities: list = field(default_factory=list)
    technology_context: dict = field(default_factory=dict)
    organizational_complexity: str = "growth"
    regulatory_context: list = field(default_factory=list)
    customer_expectations: list = field(default_factory=list)
    employment_periods: list = field(default_factory=list)
    evidence_status: str = "inferred"
    public_knowledge: dict = field(default_factory=dict)


class EmployerContextBuilder:
    """Builds employer context from resume data and public knowledge."""

    INDUSTRY_PROFILES = {
        'fintech': {
            'business_model': 'Financial services, payments, lending, trading platforms',
            'operational_priorities': ['security', 'compliance', 'reliability', 'auditability', 'low-latency', 'data-integrity'],
            'regulatory_context': ['SOX', 'PCI-DSS', 'GDPR', 'CCPA', 'Basel III', 'MiFID II', 'KYC/AML'],
            'customer_expectations': ['zero-downtime', 'transaction-integrity', 'data-privacy', 'regulatory-compliance', 'real-time-processing'],
            'typical_technologies': ['Java', 'Spring', 'Kafka', 'PostgreSQL', 'Redis', 'Kubernetes', 'Vault', 'Istio'],
            'infrastructure_pattern': 'multi-region, high-availability, encrypted-at-rest-and-transit',
            'scale_indicators': ['transactions-per-second', 'latency-p99', 'availability-slas', 'audit-log-completeness'],
        },
        'healthcare': {
            'business_model': 'Healthcare delivery, medical devices, pharma, health-tech platforms',
            'operational_priorities': ['patient-safety', 'privacy', 'reliability', 'regulatory-compliance', 'data-integrity', 'traceability'],
            'regulatory_context': ['HIPAA', 'HITRUST', 'FDA-21-CFR-Part-11', 'GDPR', 'HITECH'],
            'customer_expectations': ['patient-data-privacy', 'system-availability', 'clinical-accuracy', 'regulatory-compliance', 'interoperability'],
            'typical_technologies': ['Java', 'C#', '.NET', 'FHIR', 'HL7', 'Kubernetes', 'PostgreSQL', 'Encryption'],
            'infrastructure_pattern': 'hybrid-cloud, air-gapped-environments, strict-access-control',
            'scale_indicators': ['patient-records', 'api-response-time', 'uptime', 'compliance-audit-score'],
        },
        'ecommerce': {
            'business_model': 'Online retail, marketplace, digital commerce',
            'operational_priorities': ['availability', 'scalability', 'seasonal-traffic', 'conversion-optimization', 'personalization', 'operational-continuity'],
            'regulatory_context': ['PCI-DSS', 'GDPR', 'CCPA', 'Sales-tax', 'Consumer-protection'],
            'customer_expectations': ['fast-page-loads', 'checkout-reliability', 'inventory-accuracy', 'personalized-experience', 'mobile-performance'],
            'typical_technologies': ['React', 'Node.js', 'Java', 'Kafka', 'Redis', 'Elasticsearch', 'Kubernetes', 'CDN'],
            'infrastructure_pattern': 'multi-region, auto-scaling, edge-caching, feature-flags',
            'scale_indicators': ['requests-per-second', 'conversion-rate', 'cart-abandonment', 'page-load-time', 'black-friday-capacity'],
        },
        'cloud': {
            'business_model': 'Infrastructure/Platform/Software as a Service',
            'operational_priorities': ['distributed-systems', 'customer-impact', 'scalability', 'operational-excellence', 'multi-tenancy', 'security'],
            'regulatory_context': ['SOC2', 'ISO27001', 'FedRAMP', 'GDPR', 'HIPAA', 'PCI-DSS'],
            'customer_expectations': ['sla-commitments', 'global-availability', 'performance-consistency', 'security', 'transparent-pricing'],
            'typical_technologies': ['Go', 'Rust', 'Kubernetes', 'eBPF', 'gRPC', 'etcd', 'Custom-systems'],
            'infrastructure_pattern': 'bare-metal, custom-networking, global-fabric, capacity-planning',
            'scale_indicators': ['regions', 'availability-zones', 'customers', 'api-rps', 'data-center-capacity'],
        },
        'social': {
            'business_model': 'Social media, content platforms, advertising',
            'operational_priorities': ['scale', 'real-time', 'personalization', 'content-moderation', 'ad-delivery', 'engagement'],
            'regulatory_context': ['GDPR', 'CCPA', 'COPPA', 'DSA', 'Section-230', 'Content-moderation-laws'],
            'customer_expectations': ['real-time-feeds', 'low-latency', 'content-relevance', 'platform-stability', 'privacy-controls'],
            'typical_technologies': ['React', 'GraphQL', 'Kafka', 'Flink', 'Cassandra', 'Redis', 'Kubernetes', 'ML-platform'],
            'infrastructure_pattern': 'global-edge, real-time-streaming, ML-inference-at-scale',
            'scale_indicators': ['daily-active-users', 'posts-per-second', 'feed-latency', 'ad-auction-latency', 'moderation-throughput'],
        },
        'gaming': {
            'business_model': 'Video games, live services, mobile gaming, esports',
            'operational_priorities': ['low-latency', 'real-time-sync', 'anti-cheat', 'matchmaking', 'live-ops', 'cross-platform'],
            'regulatory_context': ['GDPR', 'COPPA', 'Age-ratings', 'Gambling-regulations', 'Data-localization'],
            'customer_expectations': ['sub-100ms-latency', 'fair-matchmaking', 'zero-cheating', 'seamless-updates', 'cross-play'],
            'typical_technologies': ['C++', 'C#', 'Unity', 'Unreal', 'gRPC', 'Redis', 'Kubernetes', 'WebRTC'],
            'infrastructure_pattern': 'global-game-servers, edge-compute, dedicated-networking',
            'scale_indicators': ['concurrent-players', 'matchmaking-latency', 'server-tick-rate', 'patch-deployment-time'],
        },
        'enterprise': {
            'business_model': 'B2B SaaS, enterprise software, productivity tools',
            'operational_priorities': ['reliability', 'security', 'compliance', 'integrations', 'customization', 'supportability'],
            'regulatory_context': ['SOC2', 'ISO27001', 'GDPR', 'HIPAA', 'FedRAMP', 'Industry-specific'],
            'customer_expectations': ['uptime-sla', 'data-portability', 'integration-ecosystem', 'admin-controls', 'support-sla'],
            'typical_technologies': ['Java', 'Go', 'PostgreSQL', 'Kubernetes', 'GraphQL', 'REST', 'OAuth', 'SAML'],
            'infrastructure_pattern': 'multi-tenant, configurable, extensible, audit-logging',
            'scale_indicators': ['enterprise-customers', 'api-integrations', 'customization-depth', 'support-ticket-volume'],
        },
        'automotive': {
            'business_model': 'Automotive manufacturing, autonomous driving, mobility services',
            'operational_priorities': ['safety', 'real-time', 'determinism', 'hardware-integration', 'ota-updates', 'regulatory-compliance'],
            'regulatory_context': ['ISO-26262', 'ISO-21434', 'UN-R155', 'UN-R156', 'GDPR', 'Automotive-grade'],
            'customer_expectations': ['functional-safety', 'cybersecurity', 'reliability', 'latency-bounds', 'update-security'],
            'typical_technologies': ['C++', 'Rust', 'ROS', 'QNX', 'Linux', 'Kubernetes', 'eBPF', 'Time-sensitive-networking'],
            'infrastructure_pattern': 'edge-compute, hardware-in-loop, safety-certified',
            'scale_indicators': ['vehicles-connected', 'sensor-data-throughput', 'inference-latency', 'safety-certification-level'],
        },
    }

    def build_all(self, chronology_entries: list[CareerChronologyEntry]) -> list[EmployerContext]:
        """Build context for all unique employers in chronology."""
        employers_seen = {}
        contexts = []

        for entry in chronology_entries:
            if entry.employer not in employers_seen:
                context = self._build_context(entry)
                employers_seen[entry.employer] = context
                contexts.append(context)
            else:
                # Add employment period to existing context
                employers_seen[entry.employer].employment_periods.append({
                    'role': entry.title,
                    'start_date': entry.start_date,
                    'end_date': entry.end_date,
                    'responsibilities': entry.scope,
                    'technologies': entry.technologies,
                })

        return contexts

    def _build_context(self, entry: CareerChronologyEntry) -> EmployerContext:
        """Build context for a single employer."""
        industry = entry.industry.lower()
        profile = self.INDUSTRY_PROFILES.get(industry, self.INDUSTRY_PROFILES['enterprise'])

        context = EmployerContext(
            name=entry.employer,
            industry=entry.industry,
            business_model=profile['business_model'],
            operational_priorities=profile['operational_priorities'].copy(),
            regulatory_context=profile['regulatory_context'].copy(),
            customer_expectations=profile['customer_expectations'].copy(),
            organizational_complexity=self._infer_org_complexity(entry),
            employment_periods=[{
                'role': entry.title,
                'start_date': entry.start_date,
                'end_date': entry.end_date,
                'responsibilities': entry.scope,
                'technologies': entry.technologies,
            }],
            evidence_status='inferred',
        )

        # Build technology context
        context.technology_context = {
            'primary_stack': profile['typical_technologies'],
            'infrastructure': profile['infrastructure_pattern'],
            'scale_indicators': profile['scale_indicators'],
            'candidate_technologies': entry.technologies,
        }

        return context

    def _infer_org_complexity(self, entry: CareerChronologyEntry) -> str:
        """Infer organizational complexity from role and duration."""
        title_lower = entry.title.lower()

        if any(kw in title_lower for kw in ['vp', 'vice president', 'cto', 'cio', 'director', 'head of']):
            return 'enterprise'
        elif any(kw in title_lower for kw in ['manager', 'lead', 'principal', 'staff']):
            if entry.duration_months > 36:
                return 'mature'
            return 'growth'
        elif entry.duration_months > 24:
            return 'growth'
        return 'startup'

    def enrich_with_public_knowledge(self, contexts: list[EmployerContext]) -> list[EmployerContext]:
        """Enrich contexts with public company knowledge (placeholder for integration)."""
        # In production, this would integrate with:
        # - Company websites
        # - LinkedIn company pages
        # - Crunchbase/PitchBook
        # - Glassdoor/Blind
        # - News articles
        # - Technical blogs
        # - Conference presentations
        # - Open source contributions

        for context in contexts:
            context.public_knowledge = {
                'note': 'Public knowledge enrichment would be implemented here',
                'sources': ['company_website', 'linkedin', 'tech_blog', 'conference_talks', 'open_source'],
                'confidence': 'medium',
            }
            context.evidence_status = 'public_knowledge'

        return contexts