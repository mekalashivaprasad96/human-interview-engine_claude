"""Professional World Model builder — expands resume signals into a coherent career model."""

from __future__ import annotations

import re
from typing import Any

from .config_loader import EngineConfig
from .employer_intelligence import EmployerIntelligenceEngine
from .models import PROTECTED_CHARACTERISTIC_TERMS, utc_now_iso


class ProfessionalWorldModelBuilder:
    """Constructs the candidate's professional world model from profile + employer intelligence."""

    def __init__(self, config: EngineConfig, employer_engine: EmployerIntelligenceEngine) -> None:
        self.config = config
        self.employer_engine = employer_engine

    def build(
        self,
        profile: dict[str, Any],
        jd_analysis: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a schema-compliant ProfessionalWorldModel."""
        chronology = profile.get("career_chronology", [])
        employer_contexts = [self.employer_engine.infer_employer_context(job) for job in chronology]

        seniority = self._infer_seniority(chronology)
        progression = self._analyze_progression(chronology, seniority["level"])
        competency_graph = self._build_competency_graph(profile, employer_contexts)
        transferable = self._identify_transferable_knowledge(competency_graph, employer_contexts, jd_analysis)
        gaps = self._identify_gaps(competency_graph, seniority, jd_analysis)
        persona = self._build_persona_profile(seniority["level"], employer_contexts, chronology)
        eval_dims = self._select_evaluation_dimensions(seniority["level"], employer_contexts, jd_analysis)

        return {
            "candidate_id": profile["candidate_id"],
            "resume_version": profile["resume_version"],
            "generated_at": utc_now_iso(),
            "inferred_seniority": seniority,
            "career_progression": progression,
            "employer_contexts": employer_contexts,
            "competency_graph": competency_graph,
            "transferable_knowledge": transferable,
            "potential_gaps": gaps,
            "evaluation_dimensions": eval_dims,
            "persona_profile": persona,
        }

    def _infer_seniority(self, chronology: list[dict[str, Any]]) -> dict[str, Any]:
        total_months = sum(job.get("duration_months") or 12 for job in chronology)
        total_years = round(total_months / 12.0, 1) if chronology else 1.0

        latest_title = (chronology[0].get("role_title", "") if chronology else "").lower()
        all_titles = " ".join(j.get("role_title", "") for j in chronology).lower()
        all_bullets = " ".join(" ".join(j.get("highlights", [])) for j in chronology).lower()

        if any(k in latest_title for k in ("vp", "vice president", "chief ", "cto", "cio", "svp", "evp")):
            level = "executive"
            rationale = f"Latest title '{chronology[0].get('role_title')}' reflects executive scope across ~{total_years} years."
        elif "director" in latest_title or "head of" in latest_title:
            level = "director"
            rationale = f"Latest title '{chronology[0].get('role_title')}' reflects multi-team director scope across ~{total_years} years."
        elif "engineering manager" in latest_title or ("manager" in latest_title and "account" not in latest_title):
            level = "manager"
            rationale = f"Latest title '{chronology[0].get('role_title')}' indicates people and delivery management."
        elif "principal" in latest_title:
            level = "principal"
            rationale = f"Latest title '{chronology[0].get('role_title')}' reflects principal-level technical scope."
        elif "staff" in latest_title:
            level = "staff"
            rationale = f"Latest title '{chronology[0].get('role_title')}' reflects staff-level cross-team architecture scope."
        elif any(k in latest_title for k in ("senior", "sr.", "sr ", "lead")) or total_years >= 5.5:
            level = "senior"
            rationale = f"Role progression ({chronology[0].get('role_title', 'Engineer')}) and ~{total_years} years support senior scope."
        elif any(k in latest_title for k in ("junior", "jr", "associate", "intern", "entry")) or (total_years < 2.2 and "senior" not in all_titles):
            level = "junior"
            rationale = f"Early-career history (~{total_years} years, {chronology[0].get('role_title', 'entry role')}) aligns with junior scope; avoids exaggerating seniority."
        else:
            # Check ownership verbs carefully for mid vs senior
            if total_years >= 4.0 and any(v in all_bullets for v in ("architected", "led ", "owned ")):
                level = "senior"
                rationale = f"Ownership scope and ~{total_years} years align with senior level."
            else:
                level = "mid"
                rationale = f"Career span (~{total_years} years) aligns with mid-level individual execution."

        return {
            "level": level,
            "total_years_experience": total_years,
            "rationale": rationale,
        }

    @staticmethod
    def _analyze_progression(chronology: list[dict[str, Any]], level: str) -> dict[str, str]:
        if not chronology:
            return {
                "trajectory_summary": "Early or sparsely documented employment trajectory.",
                "ownership_evolution": "Focus on foundational execution and transferable technical reasoning.",
                "scope_growth": "Single-stage documented scope.",
            }
        ordered = list(reversed(chronology))  # earliest to latest
        titles = [f"{j.get('role_title')} ({j.get('employer')})" for j in ordered]
        summary = " -> ".join(titles)
        ownership_map = {
            "junior": "Focused on guided feature delivery, bug triage, and learning production practices.",
            "mid": "Progressed to independent service ownership, on-call troubleshooting, and peer reviews.",
            "senior": "Grew into end-to-end system design, operational reliability, and mentoring peers.",
            "staff": "Expanded from single-team implementation to cross-team architecture and platform trade-offs.",
            "principal": "Shaped multi-org technical direction, long-horizon standards, and critical incident posture.",
            "manager": "Transitioned from individual engineering execution into team delivery, hiring, and risk management.",
            "director": "Scaled from single-team leadership to multi-team strategy, roadmap governance, and stakeholder alignment.",
            "executive": "Evolved to enterprise strategy, organizational capability building, and business/P&L accountability.",
        }
        return {
            "trajectory_summary": summary,
            "ownership_evolution": ownership_map.get(level, ownership_map["mid"]),
            "scope_growth": f"Spans {len(chronology)} documented role(s) across {len({j.get('employer') for j in chronology})} employer(s).",
        }

    def _build_competency_graph(
        self,
        profile: dict[str, Any],
        employer_contexts: list[dict[str, Any]],
    ) -> dict[str, Any]:
        chronology = profile.get("career_chronology", [])
        tech_comps: list[dict[str, Any]] = []
        for skill in profile.get("explicit_skills", []):
            sources = [
                j["employer"]
                for j in chronology
                if skill.lower() in (j.get("role_title", "") + " " + " ".join(j.get("highlights", []))).lower()
            ]
            earliest = None
            for j in chronology:
                if j["employer"] in sources and j.get("start_year"):
                    earliest = min(earliest, j["start_year"]) if earliest else j["start_year"]
            tech_comps.append(
                {
                    "name": skill,
                    "proficiency_tier": "documented_hands_on" if sources else "listed_skill",
                    "source_employers": sources,
                    "earliest_year": earliest,
                }
            )

        all_text = " ".join(
            [profile.get("headline", "")]
            + [j.get("role_title", "") + " " + " ".join(j.get("highlights", [])) for j in chronology]
        ).lower()

        business_comps: list[str] = []
        for kw, label in (
            ("cost", "cost optimization and cloud efficiency"),
            ("sla", "SLA/SLO governance"),
            ("slo", "reliability budgeting"),
            ("revenue", "revenue and adoption impact"),
            ("renewal", "customer retention and renewals"),
            ("migration", "platform migration execution"),
            ("compliance", "regulatory and audit readiness"),
            ("budget", "budget and capacity planning"),
        ):
            if kw in all_text:
                business_comps.append(label)
        if not business_comps:
            business_comps.append("engineering trade-off and delivery alignment")

        leadership_caps: list[str] = []
        for kw, label in (
            ("mentor", "mentoring engineers"),
            ("led", "technical initiative leadership"),
            ("lead", "technical guidance"),
            ("cross-functional", "cross-functional alignment"),
            ("stakeholder", "stakeholder alignment"),
            ("hired", "hiring and interviewing"),
            ("architected", "architecture decision ownership"),
            ("on-call", "incident leadership"),
        ):
            if kw in all_text:
                leadership_caps.append(label)

        customer_caps: list[str] = []
        for kw, label in (
            ("customer", "customer escalation and solution advisory"),
            ("client", "client technical consultation"),
            ("executive", "executive communication"),
            ("poc", "proof-of-concept delivery"),
            ("workshop", "technical discovery and workshops"),
            ("tam", "technical account management"),
            ("architect", "architecture advisory"),
        ):
            if kw in all_text:
                customer_caps.append(label)

        ops_resps: list[str] = []
        for ctx in employer_contexts:
            ops_resps.extend(ctx.get("operational_priorities", [])[:2])
        for kw, label in (
            ("incident", "production incident triage"),
            ("troubleshoot", "root-cause troubleshooting"),
            ("monitor", "observability and alerting"),
            ("deploy", "safe rollout and deployment"),
            ("ci/cd", "release automation"),
        ):
            if kw in all_text:
                ops_resps.append(label)
        ops_resps = list(dict.fromkeys(ops_resps))

        methodologies: list[str] = []
        for kw, label in (
            ("agile", "Agile iterative delivery"),
            ("scrum", "Scrum execution"),
            ("tdd", "test-driven development"),
            ("canary", "canary deployments"),
            ("gitops", "GitOps workflows"),
            ("terraform", "infrastructure as code"),
            ("postmortem", "blameless postmortems"),
        ):
            if kw in all_text:
                methodologies.append(label)
        if not methodologies:
            methodologies.append("incremental delivery and production verification")

        return {
            "technical_competencies": tech_comps,
            "business_competencies": list(dict.fromkeys(business_comps)),
            "leadership_capabilities": list(dict.fromkeys(leadership_caps)) or ["individual technical accountability"],
            "customer_facing_capabilities": list(dict.fromkeys(customer_caps)),
            "operational_responsibilities": ops_resps,
            "engineering_methodologies": list(dict.fromkeys(methodologies)),
        }

    @staticmethod
    def _identify_transferable_knowledge(
        comp_graph: dict[str, Any],
        employer_contexts: list[dict[str, Any]],
        jd_analysis: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        transfers: list[dict[str, Any]] = []
        tech_names = [t["name"].lower() for t in comp_graph.get("technical_competencies", [])]
        if any(k in tech_names for k in ("kubernetes", "docker", "aws", "eks", "gke", "terraform")):
            transfers.append(
                {
                    "from_domain": "Cloud & container orchestration",
                    "to_target_area": "Distributed workload scheduling and isolation",
                    "rationale": "Control-plane scheduling, resource quotas, and failure isolation patterns transfer across workloads.",
                    "evidence_status": "transferable_professional_knowledge",
                }
            )
        if any(ctx.get("regulatory_environment") for ctx in employer_contexts):
            transfers.append(
                {
                    "from_domain": "Regulated production operations",
                    "to_target_area": "Enterprise security, auditability, and safe change control",
                    "rationale": "Experience operating under strict change gates and auditability applies to any mission-critical environment.",
                    "evidence_status": "transferable_professional_knowledge",
                }
            )
        if jd_analysis:
            for item in jd_analysis.get("transferable_skills", []):
                transfers.append(
                    {
                        "from_domain": "Prior documented domain",
                        "to_target_area": item,
                        "rationale": f"Core engineering/operational principles generalize to {item}.",
                        "evidence_status": "transferable_professional_knowledge",
                    }
                )
        return transfers

    @staticmethod
    def _identify_gaps(
        comp_graph: dict[str, Any],
        seniority: dict[str, Any],
        jd_analysis: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        gaps: list[dict[str, Any]] = []
        if jd_analysis:
            for gap in jd_analysis.get("candidate_gaps", []):
                gaps.append(
                    {
                        "gap_area": gap,
                        "severity": "medium",
                        "bridging_strategy": f"Acknowledge exact scope boundary on {gap}, anchor on adjacent fundamentals, and explain concrete ramp-up plan.",
                    }
                )
        if not comp_graph.get("technical_competencies"):
            gaps.append(
                {
                    "gap_area": "Sparse technical detail in resume",
                    "severity": "medium",
                    "bridging_strategy": "Use reasonable domain inference in simulation or foundational engineering principles in authentic prep.",
                }
            )
        return gaps

    def _build_persona_profile(
        self,
        level: str,
        employer_contexts: list[dict[str, Any]],
        chronology: list[dict[str, Any]],
    ) -> dict[str, Any]:
        voice_cfg = self.config.communication_rules.get("seniority_voice_profiles", {}).get(
            level,
            self.config.communication_rules.get("seniority_voice_profiles", {}).get("senior", {}),
        )
        industries = ", ".join(dict.fromkeys(c["industry"] for c in employer_contexts)) or "software engineering"
        persona = {
            "maturity_level": level,
            "voice_register": f"Grounded {level}-level practitioner shaped by {industries}. {voice_cfg.get('confidence_calibration', '')}".strip(),
            "ownership_framing": voice_cfg.get("ownership_style", "Clearly distinguish personal ownership from team delivery."),
            "humility_markers": [
                "Acknowledge constraints, partial failures, and what teammates contributed.",
                "Explain verification steps when a detail was owned by another team or needs checking.",
            ],
            "protected_attributes_inferred": False,
        }
        # Safety check ensuring no protected attribute phrasing leaks into persona
        serialized = str(persona).lower()
        for term in PROTECTED_CHARACTERISTIC_TERMS:
            if re.search(rf"\b{re.escape(term)}\b", serialized):
                persona["protected_attributes_inferred"] = True
        return persona

    @staticmethod
    def _select_evaluation_dimensions(
        level: str,
        employer_contexts: list[dict[str, Any]],
        jd_analysis: dict[str, Any] | None,
    ) -> list[str]:
        dims = ["technical_accuracy", "individual_ownership", "problem_solving", "communication_clarity"]
        if level in ("senior", "staff", "principal", "manager", "director", "executive"):
            dims.extend(["trade_off_judgment", "operational_realism", "business_awareness"])
        if any(c.get("candidate_role_scope") == "customer_advisory_and_engineering" for c in employer_contexts):
            dims.extend(["customer_empathy", "stakeholder_alignment"])
        if jd_analysis:
            for d in jd_analysis.get("evaluation_dimensions", []):
                if d not in dims:
                    dims.append(d)
        return dims
