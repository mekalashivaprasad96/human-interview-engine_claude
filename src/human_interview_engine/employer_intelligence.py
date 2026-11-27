"""Employer-Specific Professional Intelligence & Technology Chronology Validator."""

from __future__ import annotations

import re
from typing import Any

from .config_loader import EngineConfig


class EmployerIntelligenceEngine:
    """Infers employer industry context and validates technology chronology."""

    def __init__(self, config: EngineConfig) -> None:
        self.config = config

    def infer_employer_context(self, job_entry: dict[str, Any]) -> dict[str, Any]:
        """Build employer business, operational, regulatory, and security profile."""
        employer = job_entry.get("employer", "Employer")
        role_title = job_entry.get("role_title", "")
        industry_hint = job_entry.get("industry", "")
        combined = " ".join(
            [
                employer,
                role_title,
                industry_hint,
                " ".join(job_entry.get("highlights", [])),
                " ".join(job_entry.get("domain_tags", [])),
            ]
        ).lower()

        best_key = "enterprise_saas_customer"
        best_score = 0
        for key, profile in self.config.industry_profiles.items():
            score = sum(
                1
                for kw in profile.get("keywords", [])
                if re.search(rf"(?<![a-z0-9]){re.escape(kw.lower())}(?![a-z0-9])", combined)
            )
            if score > best_score:
                best_score = score
                best_key = key

        selected = self.config.industry_profiles.get(best_key, {})
        if best_score == 0:
            # Default conservatively for generic software/engineering employers
            selected = self.config.industry_profiles.get("cloud_infrastructure", selected)
            best_key = "cloud_infrastructure"

        role_scope = self._classify_role_scope(role_title)
        return {
            "employer": employer,
            "industry": selected.get("label", best_key),
            "industry_key": best_key,
            "business_model": self._infer_business_model(best_key),
            "regulatory_environment": list(selected.get("regulatory", [])),
            "operational_priorities": list(selected.get("priorities", [])),
            "security_posture": selected.get("security_posture", ""),
            "change_management": selected.get("change_management", ""),
            "candidate_role_scope": role_scope,
            "start_year": job_entry.get("start_year"),
            "end_year": job_entry.get("end_year"),
        }

    @staticmethod
    def _infer_business_model(industry_key: str) -> str:
        models = {
            "retail_ecommerce": "High-volume consumer transactions and omni-channel fulfillment",
            "financial_services": "Regulated financial transactions, ledger accuracy, and risk control",
            "healthcare": "Clinical/patient workflows and regulated health-data exchange",
            "cloud_infrastructure": "Multi-tenant cloud platform services under strict SLOs",
            "ai_ml_platform": "Accelerated compute, model training, and low-latency inference services",
            "semiconductor": "Silicon design, hardware validation, and manufacturing yield engineering",
            "mobile_applications": "Consumer/enterprise mobile products across heterogeneous devices",
            "cybersecurity": "Threat prevention, detection, identity governance, and risk reduction",
            "networking_telecom": "High-throughput packet transport, routing reliability, and edge delivery",
            "enterprise_saas_customer": "B2B enterprise software delivery, customer adoption, and retention",
        }
        return models.get(industry_key, "Technology product and service delivery")

    @staticmethod
    def _classify_role_scope(role_title: str) -> str:
        low = (role_title or "").lower()
        if any(tok in low for tok in ("vp", "chief", "cto", "cio", "svp", "evp", "head of")):
            return "executive_leadership"
        if any(tok in low for tok in ("director", "manager", "engineering manager")):
            return "management_leadership"
        if any(tok in low for tok in ("principal", "staff")):
            return "staff_plus_architecture"
        if any(tok in low for tok in ("architect", "solutions architect")):
            return "architecture_and_advisory"
        if any(tok in low for tok in ("tam", "technical account", "customer engineer", "sales engineer", "consultant")):
            return "customer_advisory_and_engineering"
        if any(tok in low for tok in ("support", "operations", "sysadmin")):
            return "support_and_operations"
        if any(tok in low for tok in ("senior", "sr", "lead")):
            return "senior_implementation_and_design"
        return "individual_implementation"

    def validate_technology_chronology(
        self,
        technologies: list[str],
        start_year: int | None,
        end_year: int | None,
    ) -> list[dict[str, Any]]:
        """Flag technologies whose public introduction year postdates the project's end_year."""
        if end_year is None:
            return []
        violations: list[dict[str, Any]] = []
        alias_index: dict[str, tuple[str, dict[str, Any]]] = {}
        for canonical, meta in self.config.technology_timeline.items():
            alias_index[canonical.lower()] = (canonical, meta)
            for alias in meta.get("aliases", []):
                alias_index[alias.lower()] = (canonical, meta)

        for tech in technologies:
            key = tech.strip().lower()
            if key not in alias_index:
                continue
            canonical, meta = alias_index[key]
            introduced = int(meta["introduced_year"])
            if end_year < introduced:
                violations.append(
                    {
                        "technology": canonical,
                        "mentioned_as": tech,
                        "introduced_year": introduced,
                        "project_end_year": end_year,
                        "project_start_year": start_year,
                        "reason": (
                            f"'{canonical}' was introduced in {introduced}, which postdates "
                            f"the employment/project end year ({end_year})."
                        ),
                    }
                )
        return violations

    def detect_technologies_in_text(self, text: str) -> list[str]:
        """Detect known timeline-tracked technologies mentioned in free text."""
        low = (text or "").lower()
        found: list[str] = []
        seen: set[str] = set()
        for canonical, meta in self.config.technology_timeline.items():
            terms = [canonical] + list(meta.get("aliases", []))
            for term in terms:
                if len(term) <= 2 and term not in ("go", "c"):
                    continue
                if re.search(rf"(?<![a-z0-9]){re.escape(term.lower())}(?![a-z0-9])", low):
                    if canonical not in seen:
                        seen.add(canonical)
                        found.append(canonical)
                    break
        return found
