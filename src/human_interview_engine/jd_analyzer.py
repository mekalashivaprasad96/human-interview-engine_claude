"""Job Description Intelligence Analyzer — extracts competencies, gaps, and likely probes."""

from __future__ import annotations

import re
from typing import Any

from .config_loader import EngineConfig
from .employer_intelligence import EmployerIntelligenceEngine
from .models import short_id


class JobDescriptionAnalyzer:
    """Analyzes target job description relative to candidate profile."""

    def __init__(self, config: EngineConfig, employer_engine: EmployerIntelligenceEngine) -> None:
        self.config = config
        self.employer_engine = employer_engine

    def analyze(
        self,
        jd_text: str,
        profile: dict[str, Any],
        company_override: str | None = None,
    ) -> dict[str, Any]:
        """Extract structured target role expectations, strengths, gaps, and interview topics."""
        raw = (jd_text or "").strip()
        low = raw.lower()
        lines = [l.strip() for l in raw.splitlines() if l.strip()]

        target_role = self._extract_role(lines)
        target_company = company_override or self._extract_company(lines)
        target_industry = self._infer_industry(low, target_company)
        expected_seniority = self._infer_expected_seniority(target_role, low)

        detected_tech = self.employer_engine.detect_technologies_in_text(raw)
        core_tech, preferred_tech = self._split_core_vs_preferred(raw, detected_tech)

        business_resps = self._extract_dimensions(
            low,
            {
                "cost": "Cloud/infrastructure cost and efficiency ownership",
                "sla": "Service availability and SLA compliance",
                "slo": "SLO definition and error-budget management",
                "customer": "Customer impact and technical adoption",
                "revenue": "Business and revenue enablement",
                "roadmap": "Technical roadmap prioritization",
                "compliance": "Security and regulatory compliance",
            },
        )
        leadership_exps = self._extract_dimensions(
            low,
            {
                "mentor": "Mentoring and elevating peer engineers",
                "cross-functional": "Cross-functional partnership with product/ops",
                "architecture": "Leading architectural design reviews",
                "lead": "Driving ambiguous technical initiatives end-to-end",
                "manage": "People management and hiring ownership",
                "stakeholder": "Aligning executive or business stakeholders",
            },
        )
        customer_exps = self._extract_dimensions(
            low,
            {
                "customer": "Direct customer troubleshooting or solution design",
                "escalation": "Executive/customer escalation management",
                "workshop": "Customer technical workshops and architecture briefings",
                "adoption": "Driving production workload adoption",
                "poc": "Proof-of-concept and pilot validation",
            },
        )

        candidate_skills = {s.lower() for s in profile.get("explicit_skills", [])}
        strengths: list[str] = []
        gaps: list[str] = []
        transferable: list[str] = []

        for tech in core_tech + preferred_tech:
            if tech.lower() in candidate_skills:
                strengths.append(tech)
            else:
                if self._has_adjacent_skill(tech.lower(), candidate_skills):
                    transferable.append(tech)
                else:
                    gaps.append(tech)

        likely_tech_topics = self._build_likely_technical_topics(core_tech, target_industry, low)
        likely_behavioral = self._build_likely_behavioral_topics(expected_seniority, customer_exps, leadership_exps)
        deep_dives = [f"Production implementation and failure modes for {t}" for t in core_tech[:4]] or [
            "End-to-end production system ownership and debugging"
        ]

        eval_dims = ["technical_depth", "problem_solving", "individual_ownership"]
        if business_resps:
            eval_dims.append("business_judgment")
        if leadership_exps:
            eval_dims.append("leadership_maturity")
        if customer_exps:
            eval_dims.append("customer_communication")

        return {
            "jd_id": short_id("jd", raw),
            "target_role": target_role,
            "target_company": target_company,
            "target_industry": target_industry,
            "expected_seniority": expected_seniority,
            "core_technical_competencies": core_tech,
            "preferred_technical_competencies": preferred_tech,
            "business_responsibilities": business_resps,
            "leadership_expectations": leadership_exps,
            "customer_facing_expectations": customer_exps,
            "likely_technical_topics": likely_tech_topics,
            "likely_behavioral_topics": likely_behavioral,
            "potential_deep_dives": deep_dives,
            "evaluation_dimensions": eval_dims,
            "candidate_strengths": strengths,
            "candidate_gaps": gaps,
            "transferable_skills": transferable,
        }

    @staticmethod
    def _extract_role(lines: list[str]) -> str:
        for line in lines[:5]:
            m = re.match(r"^(?:role|title|position)\s*:\s*(.+)$", line, re.IGNORECASE)
            if m:
                return m.group(1).strip()
        if lines:
            first = re.sub(r"^#+\s*", "", lines[0]).strip()
            if len(first.split()) <= 12:
                return first
        return "Senior Engineer"

    @staticmethod
    def _extract_company(lines: list[str]) -> str:
        for line in lines[:6]:
            m = re.match(r"^(?:company|organization|employer)\s*:\s*(.+)$", line, re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return "Target Company"

    def _infer_industry(self, low_text: str, company: str) -> str:
        combined = f"{company.lower()} {low_text}"
        best_label = "Technology / Enterprise"
        best_hits = 0
        for profile in self.config.industry_profiles.values():
            hits = sum(
                1
                for kw in profile.get("keywords", [])
                if re.search(rf"(?<![a-z0-9]){re.escape(kw.lower())}(?![a-z0-9])", combined)
            )
            if hits > best_hits:
                best_hits = hits
                best_label = profile.get("label", best_label)
        return best_label

    @staticmethod
    def _infer_expected_seniority(role: str, low_text: str) -> str:
        r = role.lower()
        if any(k in r for k in ("vp", "chief", "cto", "cio", "executive")):
            return "executive"
        if "director" in r or "head of" in r:
            return "director"
        if "engineering manager" in r or "manager" in r and "account" not in r:
            return "manager"
        if "principal" in r:
            return "principal"
        if "staff" in r:
            return "staff"
        if any(k in r for k in ("senior", "sr", "lead")):
            return "senior"
        if any(k in r for k in ("junior", "jr", "associate", "entry")):
            return "junior"
        if "10+ years" in low_text or "8+ years" in low_text:
            return "staff"
        if "5+ years" in low_text or "6+ years" in low_text:
            return "senior"
        return "mid"

    @staticmethod
    def _split_core_vs_preferred(raw: str, detected: list[str]) -> tuple[list[str], list[str]]:
        pref_match = re.search(r"(?:preferred|nice to have|bonus|plus)\s*:?(.*)", raw, re.IGNORECASE | re.DOTALL)
        pref_section = pref_match.group(1).lower() if pref_match else ""
        req_section = raw[: pref_match.start()].lower() if pref_match else raw.lower()

        core: list[str] = []
        preferred: list[str] = []
        for tech in detected:
            if tech.lower() in pref_section and tech.lower() not in req_section:
                preferred.append(tech)
            else:
                core.append(tech)
        return core, preferred

    @staticmethod
    def _extract_dimensions(low_text: str, mapping: dict[str, str]) -> list[str]:
        return [label for kw, label in mapping.items() if kw in low_text]

    @staticmethod
    def _has_adjacent_skill(target_tech: str, candidate_skills: set[str]) -> bool:
        adjacency = {
            "kubernetes": {"docker", "eks", "gke", "aks", "aws", "microservices"},
            "eks": {"kubernetes", "gke", "aks", "docker"},
            "gke": {"kubernetes", "eks", "aks", "docker"},
            "pytorch": {"tensorflow", "jax", "python", "cuda"},
            "tensorflow": {"pytorch", "python", "cuda"},
            "opentelemetry": {"prometheus", "grafana", "jaeger", "datadog"},
            "terraform": {"ansible", "aws", "kubernetes"},
            "kafka": {"rabbitmq", "flink", "spark"},
            "clickhouse": {"postgresql", "snowflake", "bigquery"},
            "vllm": {"triton inference server", "pytorch", "cuda", "gpu"},
            "grpc": {"rest", "api", "graphql", "go", "java"},
        }
        related = adjacency.get(target_tech, set())
        return bool(related & candidate_skills)

    @staticmethod
    def _build_likely_technical_topics(core_tech: list[str], industry: str, low_text: str) -> list[str]:
        topics: list[str] = []
        if core_tech:
            topics.append(f"Hands-on implementation and trade-offs with {', '.join(core_tech[:4])}")
        if any(k in low_text for k in ("scale", "distributed", "latency", "throughput", "high availability")):
            topics.append("Scalability, tail latency, and failure-mode architecture")
        if any(k in low_text for k in ("troubleshoot", "incident", "debug", "on-call", "reliability")):
            topics.append("Production incident debugging and root-cause isolation")
        if any(k in low_text for k in ("security", "compliance", "iam", "zero trust", "privacy")):
            topics.append(f"Security, access control, and compliance in {industry}")
        return topics or ["System implementation, debugging, and engineering trade-offs"]

    @staticmethod
    def _build_likely_behavioral_topics(
        seniority: str,
        customer_exps: list[str],
        leadership_exps: list[str],
    ) -> list[str]:
        topics = [
            "Handling production failures and lessons learned",
            "Technical disagreement and stakeholder trade-offs",
            "Ambiguous problem ownership under constraints",
        ]
        if customer_exps:
            topics.append("De-escalating frustrated customers while protecting delivery trust")
        if leadership_exps or seniority in ("senior", "staff", "principal", "manager", "director", "executive"):
            topics.append("Influencing technical direction without direct authority and mentoring")
        return topics
