"""Shared constants, enumerations, and utility helpers for HumanInterview Engine."""

from __future__ import annotations

import hashlib
import re
import uuid
from datetime import datetime, timezone
from typing import Any

EVIDENCE_CATEGORIES = (
    "documented_candidate_experience",
    "candidate_confirmed_experience",
    "verified_numerical_information",
    "calculated_numerical_information",
    "general_technical_knowledge",
    "transferable_professional_knowledge",
    "reasonable_contextual_inference",
    "unconfirmed_implementation_detail",
    "illustrative_estimate",
    "fictional_simulation_scenario",
)

VERIFIED_EVIDENCE_CATEGORIES = {
    "documented_candidate_experience",
    "candidate_confirmed_experience",
    "verified_numerical_information",
    "calculated_numerical_information",
}

SENIORITY_LEVELS = (
    "junior",
    "mid",
    "senior",
    "staff",
    "principal",
    "manager",
    "director",
    "executive",
)

OPERATING_MODES = (
    "immersive_simulation",
    "authentic_preparation",
    "technical_deep_dive",
    "recruiter_screening",
    "hiring_manager",
    "behavioral",
    "system_design",
    "executive",
    "general_cognitive_ability",
    "presentation_followup",
    "coaching_evaluation",
)

SHORTCOMING_CATEGORIES = (
    "robotic_communication",
    "excessive_length",
    "insufficient_depth",
    "missing_numbers",
    "weak_numerical_reasoning",
    "unsupported_metrics",
    "inadequate_technical_implementation",
    "generic_textbook",
    "weak_individual_ownership",
    "repeated_stories",
    "employer_misalignment",
    "technology_timeline_errors",
    "identity_contamination",
    "unnecessary_clarifying_questions",
    "failure_to_wait_for_clarification",
    "misunderstood_interviewer_intent",
    "transcription_errors",
    "follow_up_contradictions",
    "incorrect_technical_assumptions",
    "excessive_agreement",
    "weak_pressure_handling",
    "missing_business_impact",
    "unnatural_conclusions",
    "breaking_character_resume_reference",
)

PROTECTED_CHARACTERISTIC_TERMS = (
    "race",
    "ethnicity",
    "religion",
    "gender",
    "sexual orientation",
    "marital status",
    "nationality",
    "national origin",
    "disability",
    "pregnancy",
    "age bracket",
    "political affiliation",
)


def utc_now_iso() -> str:
    """Return an ISO-8601 UTC timestamp string."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def current_year_utc() -> int:
    """Return the current calendar year in UTC."""
    return datetime.now(timezone.utc).year


def slugify(value: str, fallback: str = "item") -> str:
    """Convert text into a clean lowercase filesystem-safe slug."""
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", (value or "").strip().lower()).strip("-")
    return cleaned[:48] or fallback


def short_id(prefix: str, seed: str | None = None) -> str:
    """Generate a compact deterministic (if seeded) or random identifier."""
    if seed:
        digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:8]
        return f"{prefix}-{digest}"
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def clamp_float(value: float, low: float = 1.0, high: float = 5.0) -> float:
    """Clamp a numeric score into [low, high] rounded to 2 decimal places."""
    return round(max(low, min(high, float(value))), 2)


def word_count(text: str) -> int:
    """Count spoken words in text."""
    return len(re.findall(r"\b[\w'-]+\b", text or ""))


def safe_get(mapping: dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Safely traverse nested dicts."""
    cur: Any = mapping
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur
