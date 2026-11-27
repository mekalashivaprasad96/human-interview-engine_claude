"""Internal Quality, Realism, and Technical Consistency Validators."""

from __future__ import annotations

import re
from typing import Any

from .config_loader import EngineConfig
from .employer_intelligence import EmployerIntelligenceEngine
from .models import word_count
from .numerical_engine import NumericalEngine
from .numerical_ledger import NumericalLedger


class ResponseValidator:
    """Validates candidate responses for realism, consistency, protocol, and factual integrity."""

    def __init__(
        self,
        config: EngineConfig,
        employer_engine: EmployerIntelligenceEngine,
        numerical_engine: NumericalEngine,
    ) -> None:
        self.config = config
        self.employer_engine = employer_engine
        self.numerical_engine = numerical_engine
        self.rules = config.communication_rules

    def validate(
        self,
        response_text: str,
        session: dict[str, Any],
        profile: dict[str, Any],
        ledger: NumericalLedger,
        active_project: dict[str, Any] | None,
        length_budget: dict[str, Any],
        operating_mode: str,
        needs_clarification: bool = False,
        banned_extra: list[str] | None = None,
    ) -> dict[str, Any]:
        """Run all consistency, realism, chronology, numerical, and spoken-protocol checks."""
        issues: list[dict[str, str]] = []
        low = (response_text or "").lower()

        if operating_mode != "coaching_evaluation":
            # 1. Resume / AI / internal engine meta character leak check
            leak_patterns = (
                "based on the resume",
                "based on your resume",
                "not mentioned in the resume",
                "not mentioned in your resume",
                "the candidate did not provide",
                "according to the provided documents",
                "as an ai",
                "language model",
                "you uploaded",
                "the question doesn't specify",
                "question does not specify",
                "the interview scenario",
                "interview scenario",
                "verified node count",
                "unverified metric",
                "i'd answer in your voice",
                "here's how i'd answer",
                "here is how you could answer",
            )
            for pat in leak_patterns:
                if pat in low:
                    issues.append({"code": "persona_resume_leak", "severity": "error", "detail": f"Contains character-breaking phrase '{pat}'."})

            stripped_resp = (response_text or "").strip()
            if (stripped_resp.startswith('"') and stripped_resp.endswith('"')) or (
                stripped_resp.startswith("“") and stripped_resp.endswith("”")
            ):
                issues.append(
                    {
                        "code": "spoken_protocol_violation",
                        "severity": "error",
                        "detail": "Spoken output must not be wrapped in outer quotation marks.",
                    }
                )

            # 2. Spoken structure / STAR heading leak check
            for marker in self.rules.get("forbidden_spoken_structure_markers", []):
                if marker in low:
                    issues.append({"code": "spoken_protocol_violation", "severity": "error", "detail": f"Contains forbidden meta/STAR marker '{marker}'."})

            # 3. Banned cliché check
            all_banned = list(self.rules.get("banned_ai_and_cliche_phrases", [])) + list(banned_extra or [])
            for phrase in all_banned:
                if re.search(rf"\b{re.escape(phrase.lower())}\b", low):
                    issues.append({"code": "cliche_detected", "severity": "warning", "detail": f"Contains discouraged phrase '{phrase}'."})

            # 4. Consecutive opening repetition check
            recent_openings = session.get("recent_openings", [])
            current_open = " ".join(response_text.strip().split()[:4]).lower()
            if recent_openings and current_open and current_open == recent_openings[-1]:
                issues.append({"code": "repetitive_opening", "severity": "warning", "detail": "Repeats exact opening stem of previous turn."})

            # 5. Clarifying question wait rule
            if needs_clarification:
                # Must ask a concise question and NOT immediately answer it in the same turn
                if "?" not in response_text or word_count(response_text) > 45:
                    issues.append(
                        {
                            "code": "clarification_wait_violation",
                            "severity": "error",
                            "detail": "Clarifying turn must ask one concise question and wait rather than inventing the rest of the answer.",
                        }
                    )

        # 6. Numerical consistency check against ledger
        pid = active_project["project_id"] if active_project else None
        num_violations = self.numerical_engine.validate_response_numbers(response_text, ledger, pid)
        for v in num_violations:
            issues.append({"code": "numerical_contradiction", "severity": "error", "detail": v["reason"]})

        # 7. Technology chronology validation if an active or referenced employer period is bounded
        mentioned_tech = self.employer_engine.detect_technologies_in_text(response_text)
        if active_project and mentioned_tech:
            chrono_violations = self.employer_engine.validate_technology_chronology(
                mentioned_tech,
                active_project.get("start_year"),
                active_project.get("end_year"),
            )
            for cv in chrono_violations:
                issues.append({"code": "technology_chronology_error", "severity": "error", "detail": cv["reason"]})

        # 8. Length check
        wc = word_count(response_text)
        max_allowed = int(length_budget.get("max_words", 300) * 1.15)
        if wc > max_allowed and operating_mode != "coaching_evaluation":
            issues.append(
                {
                    "code": "excessive_length",
                    "severity": "warning",
                    "detail": f"Word count {wc} exceeds dynamic budget max ({max_allowed}).",
                }
            )

        # 9. Authentic preparation guard against fictional scenario leakage
        if operating_mode == "authentic_preparation":
            if active_project and active_project.get("evidence_status") == "fictional_simulation_scenario":
                # Ensure simulated project title/metrics weren't claimed as real history
                scale = active_project.get("infrastructure_scale", {})
                if scale.get("total_gpus") and f"{int(scale['total_gpus'])} gpus" in low:
                    issues.append(
                        {
                            "code": "evidence_integrity_violation",
                            "severity": "error",
                            "detail": "Fictional simulation metric surfaced as personal experience in authentic_preparation mode.",
                        }
                    )

        error_count = sum(1 for i in issues if i["severity"] == "error")
        return {
            "passed": error_count == 0,
            "error_count": error_count,
            "warning_count": len(issues) - error_count,
            "word_count": wc,
            "issues": issues,
        }
