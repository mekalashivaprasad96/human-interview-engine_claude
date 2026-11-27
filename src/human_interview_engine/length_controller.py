"""Dynamic Answer-Length Controller — determines spoken duration and word budget per turn."""

from __future__ import annotations

from typing import Any

from .config_loader import EngineConfig


class DynamicLengthController:
    """Computes appropriate response budget based on intent, audience, seniority, and mode."""

    def __init__(self, config: EngineConfig) -> None:
        self.config = config
        self.budgets = config.defaults.get("length_budgets_words", {})

    def determine_budget(
        self,
        interviewer_analysis: dict[str, Any],
        transcription_meta: dict[str, Any],
        operating_mode: str,
        seniority_level: str,
        verbosity_bias: str = "balanced",
    ) -> dict[str, Any]:
        """Select the target length category and word/duration limits."""
        act = interviewer_analysis.get("question_act", "new_question")
        itype = interviewer_analysis.get("interviewer_type", "hiring_manager")
        precision = interviewer_analysis.get("precision_targets", [])

        if act in ("information_only", "closing"):
            category = "acknowledgment"
        elif transcription_meta.get("needs_clarification") or act == "interruption":
            category = "simple_confirmation"
        elif act == "numerical_probe" and interviewer_analysis.get("is_multi_part"):
            category = "technical_concept"
        elif act == "numerical_probe" and "how_calculated" not in precision:
            category = "numerical_clarification"
        elif act == "numerical_probe" and "how_calculated" in precision:
            category = "narrow_technical_followup"
        elif interviewer_analysis.get("is_yes_no_lead") and act in ("depth_probe", "repeated_question"):
            category = "simple_confirmation"
        elif operating_mode == "presentation_followup":
            category = "presentation_followup"
        elif itype == "executive" or operating_mode == "executive":
            category = "executive_followup"
        elif act in ("depth_probe", "repeated_question", "challenge", "correction") and not interviewer_analysis.get("is_multi_part"):
            category = "narrow_technical_followup"
        elif itype == "recruiter" or operating_mode == "recruiter_screening":
            category = "recruiter_question"
        elif act == "system_design_prompt" or operating_mode == "system_design":
            category = "system_design_initial"
        elif act == "troubleshooting_probe":
            category = "troubleshooting_scenario"
        elif act == "behavioral_prompt" or operating_mode == "behavioral":
            category = "behavioral_question"
        elif act == "hypothetical_gca" or operating_mode == "general_cognitive_ability":
            category = "complex_hypothetical"
        elif act in ("implementation_probe", "ownership_probe") or "how" in precision:
            category = "implementation_question"
        else:
            category = "technical_concept"

        base = dict(self.budgets.get(category, {"min": 55, "target": 110, "max": 165, "duration_seconds": [25, 65]}))
        factor = 1.0
        if verbosity_bias == "concise":
            factor = 0.82
        elif verbosity_bias == "detailed":
            factor = 1.15
        if seniority_level in ("executive", "director") and category not in ("system_design_initial",):
            factor *= 0.92

        return {
            "category": category,
            "min_words": max(2, int(base["min"] * factor)),
            "target_words": max(5, int(base["target"] * factor)),
            "max_words": max(12, int(base["max"] * factor)),
            "duration_seconds": base.get("duration_seconds", [30, 60]),
        }
