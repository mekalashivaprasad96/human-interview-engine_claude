"""Behavioral (implicit STAR) and General Cognitive Ability (GCA) Reasoning Engines."""

from __future__ import annotations

from typing import Any

from .experience_enrichment import ExperienceEnrichmentEngine


class BehavioralReasoningEngine:
    """Generates natural implicit-STAR behavioral answers and forward-looking GCA reasoning."""

    def reason_behavioral(
        self,
        question: str,
        story_bank: dict[str, Any],
        stories_used: list[str],
        operating_mode: str,
        opening_style: str,
        precision_targets: list[str],
    ) -> dict[str, Any]:
        """Select a fresh story and communicate it naturally without STAR headings."""
        low = question.lower()
        keywords: list[str] = []
        if any(k in low for k in ("fail", "mistake", "wrong", "outage", "regret", "setback")):
            keywords.extend(["failure", "mistake", "lessons_learned", "incident"])
        elif any(k in low for k in ("disagree", "conflict", "pushback", "difficult stakeholder", "convince")):
            keywords.extend(["disagreement", "conflict", "stakeholder", "compromise"])
        else:
            keywords.extend(["technical_execution", "ownership", "impact"])

        story = ExperienceEnrichmentEngine.select_story(
            story_bank,
            competency_keywords=keywords,
            exclude_story_ids=set(stories_used),
        )
        if not story:
            return {
                "spoken_draft": (
                    "When I hit a tough trade-off between delivery speed and production safety, I prefer validating the risk with quick empirical data, "
                    "isolating the failure domain cleanly, and being transparent with stakeholders about what we're deferring and why."
                ),
                "story_used": None,
                "evidence_basis": "transferable_professional_knowledge",
            }

        if operating_mode == "authentic_preparation" and story["evidence_status"] == "fictional_simulation_scenario":
            return {
                "spoken_draft": (
                    "In my actual work, I focus on separating what I directly control—like scoping a safe fallback or pulling concrete failure metrics—"
                    "from broader team alignment. If there's a disagreement on timeline versus reliability, I usually run a small data-backed test "
                    "so we're debating measured risk rather than opinions."
                ),
                "story_used": None,
                "evidence_basis": "transferable_professional_knowledge",
            }

        emp = story["employer"]
        ownership = " ".join(story.get("individual_ownership", [])[:2])
        decisions = story.get("decisions_made", [])
        decision_str = f"{decisions[0]} " if decisions else ""

        if "what_differently" in precision_targets:
            spoken = (
                f"Looking back at that {emp} episode, {story['lessons_learned'][0].lower() + story['lessons_learned'][1:]} "
                f"I'd push for that validation gate in staging a week earlier instead of trusting synthetic defaults."
            )
        elif opening_style == "constraint_first":
            spoken = (
                f"One clear example was under tight delivery pressure at {emp}, where {story['challenge'][0].lower() + story['challenge'][1:]} "
                f"{ownership} {decision_str}{story['outcome']} {story['lessons_learned']}"
            )
        else:
            own_s = ownership if (ownership.startswith("I ") or ownership.startswith("We ") or not ownership) else (ownership[0].lower() + ownership[1:])
            spoken = (
                f"At {emp} during {story['period']}, {story['challenge'][0].lower() + story['challenge'][1:]} "
                f"On my end, {own_s} "
                f"{decision_str}{story['outcome']} The takeaway for me was simple: {story['lessons_learned'][0].lower() + story['lessons_learned'][1:]}"
            )

        return {
            "spoken_draft": spoken.strip(),
            "story_used": story["story_id"],
            "project_used": story.get("project_id"),
            "employer_used": emp,
            "evidence_basis": story["evidence_status"],
        }

    def reason_hypothetical_gca(
        self,
        question: str,
        world_model: dict[str, Any],
        jd_analysis: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply forward-looking structured reasoning without forcing STAR or past stories."""
        low = question.lower()
        industry = jd_analysis.get("target_industry", "the business")

        if any(k in low for k in ("latency", "slow", "drop", "spike", "degrad", "outage", "error")):
            spoken = (
                "I'd split the problem into immediate containment versus longer-term root-cause fixes, and first check whether the spike is correlated "
                "with a recent release, a traffic shift, or a single downstream dependency. Before changing code, I'd look at three slices: error rates "
                "by region/tenant, queue depth vs worker saturation, and external dependency latency. Short term, shedding non-critical load or rolling back "
                "a suspect deploy protects users within minutes; long term, I'd measure success by error-budget burn stabilizing and add automated canary gates "
                "so the same regression fails fast in staging."
            )
        elif any(k in low for k in ("adopt", "customer", "onboarding", "churn", "launch", "priority", "prioritize")):
            spoken = (
                f"I'd start by clarifying the primary business objective and the binding constraint—whether we're optimizing for time-to-value, margin, or reliability in {industry}. "
                f"First, I'd segment where users or customers are actually stalling using funnel and support data rather than assuming it's a feature gap. "
                f"In the first 30 days, I'd ship low-risk friction fixes—clearer defaults, pre-flight validation, and automated diagnostics—while deferring "
                f"heavy platform rewrites until telemetry confirms where the highest-ROI bottleneck sits. Success means measurable drop in time-to-first-value "
                f"and fewer repeat escalations."
            )
        else:
            spoken = (
                "I'd start by pinning down the core objective, the hard constraints around budget and timeline, and what metric actually defines success. "
                "From there I'd list the two or three highest-probability bottlenecks, check them with existing telemetry or a quick back-of-the-envelope estimate, "
                "and take a low-risk reversible step immediately while validating the longer-term architectural fix against clear milestones."
            )

        return {
            "spoken_draft": spoken,
            "project_used": None,
            "evidence_basis": "general_technical_knowledge",
        }
