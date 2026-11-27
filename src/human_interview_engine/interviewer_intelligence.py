"""Interviewer Intelligence Analyzer — classifies persona, intent, question precision, and pressure."""

from __future__ import annotations

import re
from typing import Any


class InterviewerIntelligence:
    """Interprets who is asking, what competency is tested, and exact question precision."""

    def analyze(
        self,
        cleaned_transcript: str,
        transcription_meta: dict[str, Any],
        interviewer_hint: str | None = None,
        operating_mode: str = "immersive_simulation",
        previous_turns: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Classify interviewer type, conversational act, precision focus, and observable tone."""
        q = (cleaned_transcript or "").strip()
        low = q.lower()
        prev_turns = previous_turns or []

        interviewer_type = self._infer_interviewer_type(low, interviewer_hint, operating_mode)
        question_act = self._classify_act(low, transcription_meta, prev_turns)
        precision_targets = self._detect_precision(low, transcription_meta.get("sub_questions", []))
        competency_evaluated = self._infer_competency(low, question_act, operating_mode)
        observable_tone = self._infer_observable_tone(low, question_act)

        return {
            "interviewer_type": interviewer_type,
            "question_act": question_act,
            "precision_targets": precision_targets,
            "competency_evaluated": competency_evaluated,
            "observable_tone": observable_tone,
            "is_yes_no_lead": bool(re.match(r"^(?:is|are|was|were|do|does|did|have|has|had|can|could|would|should|will)\b", low)),
            "is_multi_part": len(transcription_meta.get("sub_questions", [])) > 1,
            "is_coaching_request": self._is_explicit_coaching_request(low, operating_mode),
        }

    @staticmethod
    def _infer_interviewer_type(low: str, hint: str | None, mode: str) -> str:
        if hint:
            h = hint.lower().strip().replace(" ", "_")
            if h:
                return h
        mode_map = {
            "recruiter_screening": "recruiter",
            "technical_deep_dive": "technical_specialist",
            "behavioral": "behavioral_interviewer",
            "system_design": "system_design_interviewer",
            "executive": "executive",
            "hiring_manager": "hiring_manager",
        }
        if any(k in low for k in ("salary", "compensation", "notice period", "relocate", "why are you looking", "walk me through your background", "tell me about yourself")):
            return "recruiter"
        if any(k in low for k in ("design a ", "how would you architect", "scale to ", "system design")):
            return "system_design_interviewer"
        if any(k in low for k in ("roi", "revenue", "board", "margin", "executive", "p&l", "quarterly business")):
            return "executive"
        if any(k in low for k in ("are you sure", "prove", "doesn't that break", "isn't that wrong", "why didn't you")):
            return "skeptical_interviewer"
        if any(k in low for k in ("tell me about a time", "disagreement", "conflict", "mistake", "failed")):
            return "behavioral_interviewer"
        if any(k in low for k in ("config", "flag", "kernel", "kubectl", "query", "latency", "p99", "gpu", "rollback", "log", "metric")):
            return "technical_specialist"
        return mode_map.get(mode, "hiring_manager")

    @staticmethod
    def _classify_act(
        low: str,
        meta: dict[str, Any],
        prev_turns: list[dict[str, Any]],
    ) -> str:
        if meta.get("is_non_question"):
            if any(k in low for k in ("wrap up", "end of our time", "that's all my questions", "thanks for joining")):
                return "closing"
            return "information_only"
        if meta.get("is_incomplete"):
            return "interruption"
        if any(k in low for k in ("actually,", "that's not quite right", "Wait, wouldn't", "breaks live")):
            return "correction"
        if any(
            k in low
            for k in (
                "are you sure",
                "isn't that",
                "wouldn't that be",
                "why didn't you",
                "i thought ",
                "if this component failed",
                "if that failed",
                "single point of failure",
                "hypervisor",
                "duplicate",
                "exactly-once",
                "zero downtime",
            )
        ) or re.match(r"^(?:isn't|doesn't|wouldn't|don't)\b", low):
            return "challenge"
        if any(k in low for k in ("what did you personally", "your own contribution", "did you build", "vs the team")):
            return "ownership_probe"
        if any(k in low for k in ("how many", "how much", "how big was the team", "how big is the team", "team size", "how did you calculate", "what was the baseline", "gpu-hour", "percentage")):
            return "numerical_probe"
        if any(k in low for k in ("exact config", "in more detail", "dig deeper", "walk through the implementation", "how was that implemented")):
            return "implementation_probe"
        if any(k in low for k in ("outage", "incident", "debug", "troubleshoot", "went wrong", "failed in production")):
            return "troubleshooting_probe"
        if any(k in low for k in ("design a", "architect", "how would you build", "scale from")):
            return "system_design_prompt"
        if any(k in low for k in ("suppose ", "imagine ", "what if ", "hypothetically", "if a customer")):
            return "hypothetical_gca"
        if any(k in low for k in ("tell me about a time", "give me an example", "describe a situation")):
            return "behavioral_prompt"

        # Detect repeated question
        if prev_turns:
            last_q = (prev_turns[-1].get("cleaned_transcript") or "").lower()
            if last_q and (low == last_q or (len(low) > 20 and low in last_q)):
                return "repeated_question"

        if prev_turns and any(k in low for k in ("earlier", "that", "it", "those", "why", "how did that")):
            return "depth_probe"

        return "new_question"

    @staticmethod
    def _detect_precision(low: str, sub_questions: list[str]) -> list[str]:
        targets: list[str] = []
        checks = (
            ("what_did_you_personally_do", r"\b(?:what did you personally|personally do|your specific role|did you write|did you build)\b"),
            ("what_went_wrong", r"\b(?:went wrong|failed|broke|mistake|outage|incident)\b"),
            ("what_differently", r"\b(?:do differently|change next time|in hindsight)\b"),
            ("what_was_outcome", r"\b(?:outcome|result|impact|effect)\b"),
            ("how_many", r"\bhow many\b"),
            ("how_much", r"\bhow much\b"),
            ("how_calculated", r"\b(?:how did you calculate|how was .* calculated|how did you measure|baseline)\b"),
            ("why", r"\bwhy\b"),
            ("how", r"\bhow\b"),
            ("when", r"\bwhen\b"),
            ("which", r"\bwhich\b"),
            ("what", r"\bwhat\b"),
        )
        for label, pat in checks:
            if re.search(pat, low):
                targets.append(label)
        if len(sub_questions) > 1:
            targets.append("multi_part")
        if re.match(r"^(?:is|are|was|were|do|does|did|have|has|can|could|would|should)\b", low):
            targets.append("yes_no_first")
        return targets or ["what"]

    @staticmethod
    def _infer_competency(low: str, act: str, mode: str) -> str:
        if act == "numerical_probe":
            return "numerical_reasoning_and_consistency"
        if act == "ownership_probe":
            return "individual_ownership"
        if act == "troubleshooting_probe":
            return "production_troubleshooting"
        if act == "system_design_prompt":
            return "system_design_and_tradeoffs"
        if act == "hypothetical_gca":
            return "general_cognitive_ability"
        if act == "behavioral_prompt":
            return "behavioral_judgment_and_leadership"
        if act in ("challenge", "correction"):
            return "pressure_handling_and_defensibility"
        if any(k in low for k in ("customer", "stakeholder", "roi", "cost", "business", "adoption")):
            return "business_and_customer_judgment"
        if mode == "recruiter_screening" or any(k in low for k in ("background", "tell me about yourself", "why this role")):
            return "career_fit_and_communication"
        return "technical_implementation_and_reasoning"

    @staticmethod
    def _infer_observable_tone(low: str, act: str) -> str:
        if act in ("challenge", "correction") or any(k in low for k in ("are you sure", "really?", "doesn't make sense")):
            return "skeptical_or_probing"
        if act == "interruption":
            return "fast_paced_or_cut_off"
        return "neutral_conversational"

    @staticmethod
    def _is_explicit_coaching_request(low: str, operating_mode: str) -> bool:
        if operating_mode == "coaching_evaluation":
            return True
        return any(
            phrase in low
            for phrase in (
                "evaluate my answer",
                "coach me",
                "give me feedback on",
                "critique that response",
                "switch to coaching",
            )
        )
