"""
Industry Model - Provides detailed industry-specific intelligence for interview context.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class IndustryProfile:
    name: str
    characteristics: list = field(default_factory=list)
    typical_priorities: list = field(default_factory=list)
    common_technologies: list = field(default_factory=list)
    regulatory_environment: list = field(default_factory=list)
    operational_constraints: list = field(default_factory=list)
    interview_focus_areas: list = field(default_factory=list)
    typical_metrics: list = field(default_factory=list)
    candidate_experience_years: float = 0.0


class IndustryModel:
    """Provides industry-specific intelligence for interview preparation."""

    PROFILES = {
        'fintech': IndustryProfile(
            name='fintech',
            characteristics=[
                'Highly regulated', 'Transaction-heavy', 'Low-latency requirements',
                'Audit-critical', 'Security-first', 'Compliance-driven'
            ],
            typical_priorities=[
                'Transaction integrity', 'Regulatory compliance', 'Security', 'Auditability',
                'Low latency', 'High availability', 'Data consistency', 'Fraud prevention'
            ],
            common_technologies=[
                'Java/Kotlin', 'Spring Boot', 'Kafka', 'PostgreSQL', 'Redis',
                'Kubernetes', 'Vault', 'Istio', 'gRPC', 'Protocol Buffers'
            ],
            regulatory_environment=[
                'SOX', 'PCI-DSS', 'GDPR', 'CCPA', 'Basel III', 'MiFID II',
                'KYC/AML', 'PSD2', 'Open Banking'
            ],
            operational_constraints=[
                'Change control boards', 'Audit trails', 'Data residency',
                'Encryption requirements', 'Access logging', 'Disaster recovery testing'
            ],
            interview_focus_areas=[
                'Distributed transactions', 'Eventual consistency', 'Idempotency',
                'Audit logging', 'Security architecture', 'Compliance automation',
                'Latency optimization', 'Disaster recovery', 'Capacity planning'
            ],
            typical_metrics=[
                'Transactions per second (TPS)', 'Latency p50/p95/p99',
                'Availability (99.99%+)', 'Error rate', 'Fraud detection rate',
                'Settlement time', 'Audit log completeness'
            ]
        ),
        'healthcare': IndustryProfile(
            name='healthcare',
            characteristics=[
                'Life-critical systems', 'PHI protection', 'Interoperability standards',
                'Regulatory validation', 'Long data retention', 'Clinical workflow integration'
            ],
            typical_priorities=[
                'Patient safety', 'Data privacy (HIPAA)', 'System reliability',
                'Regulatory compliance', 'Clinical accuracy', 'Interoperability'
            ],
            common_technologies=[
                'Java/C#', '.NET', 'FHIR', 'HL7', 'DICOM', 'Kubernetes',
                'PostgreSQL', 'Encryption', 'Message queues', 'API gateways'
            ],
            regulatory_environment=[
                'HIPAA', 'HITRUST', 'FDA 21 CFR Part 11', 'GDPR', 'HITECH',
                'State privacy laws', 'Clinical trial regulations'
            ],
            operational_constraints=[
                'Validated environments', 'Change control', 'Audit trails',
                'Data provenance', 'Access controls', 'Business associate agreements'
            ],
            interview_focus_areas=[
                'FHIR/HL7 integration', 'PHI de-identification', 'Clinical decision support',
                'Audit trails', 'Disaster recovery', 'Validation testing',
                'Interoperability', 'Consent management'
            ],
            typical_metrics=[
                'System uptime', 'API response time', 'Data accuracy',
                'Compliance audit score', 'Incident response time', 'Data breach incidents'
            ]
        ),
        'ecommerce': IndustryProfile(
            name='ecommerce',
            characteristics=[
                'Seasonal traffic spikes', 'Conversion-focused', 'Real-time inventory',
                'Personalization', 'Multi-channel', 'Global scale'
            ],
            typical_priorities=[
                'Availability', 'Scalability', 'Page load speed', 'Checkout reliability',
                'Search relevance', 'Recommendation quality', 'Mobile experience'
            ],
            common_technologies=[
                'React/Next.js', 'Node.js', 'Java/Go', 'Kafka', 'Redis',
                'Elasticsearch', 'Kubernetes', 'CDN', 'GraphQL', 'Feature flags'
            ],
            regulatory_environment=[
                'PCI-DSS', 'GDPR', 'CCPA', 'Sales tax nexus', 'Consumer protection',
                'Accessibility (WCAG)'
            ],
            operational_constraints=[
                'Black Friday scaling', 'Flash sale handling', 'Inventory consistency',
                'Payment processing', 'Third-party integrations', 'A/B testing'
            ],
            interview_focus_areas=[
                'Auto-scaling architecture', 'Cache strategies', 'Search architecture',
                'Checkout flow reliability', 'Event-driven architecture',
                'Feature flagging', 'Personalization at scale', 'CDN optimization'
            ],
            typical_metrics=[
                'Requests per second', 'Page load time (Core Web Vitals)',
                'Conversion rate', 'Cart abandonment rate', 'Revenue per visit',
                'Availability during peak', 'Order processing latency'
            ]
        ),
        'cloud': IndustryProfile(
            name='cloud',
            characteristics=[
                'Multi-tenant', 'Global infrastructure', 'API-first',
                'Operational excellence', 'Customer isolation', 'Capacity planning'
            ],
            typical_priorities=[
                'SLA compliance', 'Security', 'Performance consistency',
                'Operational automation', 'Cost optimization', 'Innovation velocity'
            ],
            common_technologies=[
                'Go/Rust', 'Kubernetes', 'eBPF', 'gRPC', 'etcd', 'Custom systems',
                'Linux kernel', 'Networking', 'Storage', 'Virtualization'
            ],
            regulatory_environment=[
                'SOC 2', 'ISO 27001', 'FedRAMP', 'GDPR', 'HIPAA', 'PCI-DSS',
                'Data sovereignty laws'
            ],
            operational_constraints=[
                'Multi-region deployment', 'Customer data isolation', 'Noisy neighbor prevention',
                'Control plane stability', 'Upgrade safety', 'Incident transparency'
            ],
            interview_focus_areas=[
                'Control plane design', 'Data plane performance', 'Multi-tenancy isolation',
                'Capacity planning', 'Failure domain design', 'Observability',
                'Safe deployment', 'Customer communication during incidents'
            ],
            typical_metrics=[
                'API availability (99.99%+)', 'Latency p99', 'Provisioning time',
                'Incident MTTR', 'Customer-impacting incidents', 'Capacity headroom',
                'Cost per unit', 'Feature release frequency'
            ]
        ),
        'social': IndustryProfile(
            name='social',
            characteristics=[
                'Massive scale', 'Real-time feeds', 'ML-driven personalization',
                'Content moderation', 'Ad targeting', 'Network effects'
            ],
            typical_priorities=[
                'Engagement', 'Feed latency', 'Content relevance', 'Platform stability',
                'Ad revenue', 'User growth', 'Safety', 'Privacy'
            ],
            common_technologies=[
                'React/GraphQL', 'Kafka/Flink', 'Cassandra/ScyllaDB', 'Redis',
                'Kubernetes', 'ML Platform', 'Custom storage', 'Edge computing'
            ],
            regulatory_environment=[
                'GDPR', 'CCPA', 'COPPA', 'DSA', 'Online Safety Act',
                'Content moderation laws', 'Political advertising'
            ],
            operational_constraints=[
                'Real-time consistency', 'Massive fan-out', 'ML inference latency',
                'Content moderation scale', 'Global edge deployment', 'A/B testing'
            ],
            interview_focus_areas=[
                'Feed ranking architecture', 'Real-time fan-out', 'ML feature stores',
                'Content moderation pipeline', 'Ad auction systems', 'Graph processing',
                'Edge caching', 'Privacy-preserving analytics'
            ],
            typical_metrics=[
                'DAU/MAU', 'Feed latency p99', 'Posts per second',
                'Ad auction latency', 'Moderation throughput', 'Model freshness',
                'Edge cache hit rate', 'Experiment velocity'
            ]
        ),
        'gaming': IndustryProfile(
            name='gaming',
            characteristics=[
                'Ultra-low latency', 'Real-time state sync', 'Anti-cheat',
                'Live operations', 'Cross-platform', 'Deterministic simulation'
            ],
            typical_priorities=[
                'Player experience', 'Fair play', 'Server performance', 'Matchmaking quality',
                'Live content delivery', 'Cross-platform parity', 'Security'
            ],
            common_technologies=[
                'C++/C#', 'Unity/Unreal', 'gRPC', 'Redis', 'Kubernetes',
                'WebRTC', 'Custom networking', 'ECS', 'Deterministic physics'
            ],
            regulatory_environment=[
                'GDPR', 'COPPA', 'Age ratings', 'Gambling regulations',
                'Loot box laws', 'Data localization'
            ],
            operational_constraints=[
                'Tick rate consistency', 'State synchronization', 'Cheat detection',
                'Patch deployment', 'Server fleet management', 'Matchmaking fairness'
            ],
            interview_focus_areas=[
                'Game server architecture', 'State synchronization', 'Anti-cheat systems',
                'Matchmaking algorithms', 'Live ops pipeline', 'Cross-platform networking',
                'Load testing', 'Replay/debugging systems'
            ],
            typical_metrics=[
                'Concurrent players', 'Server tick rate', 'Matchmaking latency',
                'Packet loss', 'Cheat detection rate', 'Patch deployment time',
                'Player retention', 'Revenue per user'
            ]
        ),
        'enterprise': IndustryProfile(
            name='enterprise',
            characteristics=[
                'Multi-tenant SaaS', 'Complex customization', 'Integration-heavy',
                'Long sales cycles', 'High-touch support', 'Compliance requirements'
            ],
            typical_priorities=[
                'Reliability', 'Security', 'Customizability', 'Integration ecosystem',
                'Admin controls', 'Supportability', 'Upgrade safety', 'Data governance'
            ],
            common_technologies=[
                'Java/Go', 'PostgreSQL', 'Kubernetes', 'GraphQL/REST',
                'OAuth/SAML/SCIM', 'Feature flags', 'Event streaming', 'CDC'
            ],
            regulatory_environment=[
                'SOC 2', 'ISO 27001', 'GDPR', 'HIPAA', 'FedRAMP',
                'Industry-specific (FINRA, etc.)'
            ],
            operational_constraints=[
                'Tenant isolation', 'Schema migration safety', 'Backward compatibility',
                'Custom field support', 'Audit logging', 'Role-based access',
                'Data residency'
            ],
            interview_focus_areas=[
                'Multi-tenancy architecture', 'Extensibility platform', 'Integration framework',
                'Schema evolution', 'Tenant isolation', 'Admin APIs', 'Migration tooling',
                'Support diagnostics'
            ],
            typical_metrics=[
                'API uptime', 'Tenant onboarding time', 'Customization adoption',
                'Integration count', 'Support ticket volume', 'Upgrade success rate',
                'Data export completeness', 'Security audit findings'
            ]
        ),
    }

    def get_profile(self, industry: str) -> IndustryProfile:
        """Get industry profile by name."""
        return self.PROFILES.get(industry.lower(), self.PROFILES['enterprise'])

    def get_all_industries(self) -> list[str]:
        """Get list of all known industries."""
        return list(self.PROFILES.keys())

    def get_interview_focus(self, industry: str) -> list[str]:
        """Get key interview focus areas for an industry."""
        return self.get_profile(industry).interview_focus_areas

    def get_typical_metrics(self, industry: str) -> list[str]:
        """Get typical metrics for an industry."""
        return self.get_profile(industry).typical_metrics

    def get_regulatory_context(self, industry: str) -> list[str]:
        """Get regulatory environment for an industry."""
        return self.get_profile(industry).regulatory_environment