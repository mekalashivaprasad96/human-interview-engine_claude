"""Evidence Classification System — enforces strict factual boundaries."""

from __future__ import annotations

from typing import Any

from .models import EVIDENCE_CATEGORIES, VERIFIED_EVIDENCE_CATEGORIES, short_id, utc_now_iso


class EvidenceClassifier:
    """Tracks and classifies every claim and metric without auto-promoting fictional/inferred items."""

    def __init__(self, candidate_id: str, session_id: str, initial_items: list[dict[str, Any]] | None = None) -> None:
        self.candidate_id = candidate_id
        self.session_id = session_id
        self.items: list[dict[str, Any]] = list(initial_items or [])

    def add_item(
        self,
        claim: str,
        category: str,
        source_reference: str,
        confirmed_by_candidate: bool = False,
        item_id: str | None = None,
    ) -> dict[str, Any]:
        """Register a classified claim."""
        if category not in EVIDENCE_CATEGORIES:
            raise ValueError(f"Unsupported evidence category: {category}")
        is_verified_cat = category in VERIFIED_EVIDENCE_CATEGORIES
        record = {
            "item_id": item_id or short_id("ev", f"{claim}:{category}"),
            "claim": claim,
            "category": category,
            "source_reference": source_reference,
            "confirmed_by_candidate": bool(confirmed_by_candidate or is_verified_cat),
            "confirmed_at": utc_now_iso() if (confirmed_by_candidate or is_verified_cat) else None,
        }
        self.items.append(record)
        return record

    def confirm_item(self, item_id: str, new_claim: str | None = None, is_numerical: bool = False) -> dict[str, Any] | None:
        """Promote an unconfirmed/simulated/inferred item ONLY via explicit candidate confirmation."""
        for item in self.items:
            if item["item_id"] == item_id:
                if new_claim:
                    item["claim"] = new_claim
                item["confirmed_by_candidate"] = True
                item["confirmed_at"] = utc_now_iso()
                item["category"] = (
                    "verified_numerical_information"
                    if is_numerical
                    else "candidate_confirmed_experience"
                )
                return item
        return None

    def get_by_category(self, category: str) -> list[dict[str, Any]]:
        """Filter items by evidence category."""
        return [item for item in self.items if item["category"] == category]

    def can_present_as_personal_fact(self, category: str, operating_mode: str) -> bool:
        """Determine whether a claim category can be spoken as personal experience in the active mode."""
        if category in VERIFIED_EVIDENCE_CATEGORIES:
            return True
        if operating_mode == "authentic_preparation":
            # In authentic preparation, NEVER present fictional/unconfirmed/illustrative items as personal history.
            return category in {"general_technical_knowledge", "transferable_professional_knowledge"}
        if operating_mode == "general_cognitive_ability":
            return category in {"general_technical_knowledge", "transferable_professional_knowledge"}
        # In simulation modes, fictional simulation scenarios are explicitly permitted
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "session_id": self.session_id,
            "items": self.items,
        }
