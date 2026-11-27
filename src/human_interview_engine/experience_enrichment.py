"""Experience Enrichment Engine — builds a diverse, non-repetitive experience story bank."""

from __future__ import annotations

from typing import Any

from .models import short_id


class ExperienceEnrichmentEngine:
    """Builds and rotates multi-employer stories covering implementation, failures, and disagreements."""

    def build_story_bank(
        self,
        profile: dict[str, Any],
        project_catalog: dict[str, Any],
        world_model: dict[str, Any],
    ) -> dict[str, Any]:
        """Create diverse behavioral & technical experience stories linked to projects and employers."""
        stories: list[dict[str, Any]] = []
        projects = project_catalog.get("projects", [])
        chronology = profile.get("career_chronology", [])

        # Primary documented / simulated stories per project
        for idx, proj in enumerate(projects):
            emp = proj["employer"]
            period = proj["employment_period"]
            # Story A: Architecture & technical delivery
            stories.append(
                {
                    "story_id": short_id("st", f"{emp}:delivery:{idx}"),
                    "title": f"Technical Delivery: {proj['title']}",
                    "employer": emp,
                    "period": period,
                    "project_id": proj["project_id"],
                    "competencies_demonstrated": ["technical_execution", "architecture", "ownership", "impact"],
                    "summary": proj["architecture_summary"],
                    "challenge": proj["business_objective"],
                    "individual_ownership": list(proj["individual_contributions"]),
                    "team_context": f"Worked in a {proj['team_structure']['team_size']}-person team while directly owning the core architecture and validation work.",
                    "decisions_made": [d["decision"] for d in proj.get("implementation_decisions", [])],
                    "obstacles_or_failures": proj["challenges"][0] if proj.get("challenges") else "Managed legacy schema and latency constraints.",
                    "outcome": proj["outcomes"],
                    "lessons_learned": proj["lessons_learned"],
                    "evidence_status": proj["evidence_status"],
                    "times_used": 0,
                    "last_used_turn": None,
                }
            )

            # Story B: Production failure / rollback / mistake story
            stories.append(
                {
                    "story_id": short_id("st", f"{emp}:failure:{idx}"),
                    "title": f"Production Setback & Recovery at {emp}",
                    "employer": emp,
                    "period": period,
                    "project_id": proj["project_id"],
                    "competencies_demonstrated": ["failure", "mistake", "troubleshooting", "incident", "lessons_learned"],
                    "summary": proj["challenges"][0] if proj.get("challenges") else "Handled an unexpected canary regression under load.",
                    "challenge": "A deployment assumption didn't hold under real production burst traffic, elevating error rates during canary.",
                    "individual_ownership": [
                        "I triggered an immediate traffic rollback to restore SLO health within minutes.",
                        "I captured heap and trace diagnostics before recycling pods so root cause wasn't lost.",
                        "I added a pre-deployment soak check and readiness gating so the failure mode couldn't recur.",
                    ],
                    "team_context": "Coordinated mitigation with the on-call SRE while owning the postmortem action items personally.",
                    "decisions_made": ["I prioritized rapid rollback over live hot-patching under degraded SLO."],
                    "obstacles_or_failures": proj["challenges"][0] if proj.get("challenges") else "Premature readiness probe passed under cold-start memory allocation.",
                    "outcome": "We contained impact to the 5% canary slice, restored full baseline in under 8 minutes, and prevented repeat incidents.",
                    "lessons_learned": "Never trust synthetic readiness checks unless they exercise realistic cold-start resource allocation.",
                    "evidence_status": proj["evidence_status"],
                    "times_used": 0,
                    "last_used_turn": None,
                }
            )

        # Story C: Stakeholder disagreement / cross-functional compromise (anchored on earliest or second employer if present)
        disagree_job = chronology[1] if len(chronology) > 1 else (chronology[0] if chronology else None)
        if disagree_job:
            emp = disagree_job.get("employer", "Employer")
            period = f"{disagree_job.get('start_date', '')} - {disagree_job.get('end_date', '')}".strip(" -")
            stories.append(
                {
                    "story_id": short_id("st", f"{emp}:disagreement"),
                    "title": f"Cross-Functional Trade-off & Disagreement at {emp}",
                    "employer": emp,
                    "period": period,
                    "project_id": projects[1]["project_id"] if len(projects) > 1 else (projects[0]["project_id"] if projects else None),
                    "competencies_demonstrated": ["disagreement", "conflict", "stakeholder", "leadership", "compromise"],
                    "summary": f"Resolved an architectural disagreement at {emp} between shipping fast on a synchronous path vs isolating brittle downstream dependencies.",
                    "challenge": "Product/stakeholders wanted immediate single-sprint launch by tightly coupling a new sync call; I believed that risked cascading outages.",
                    "individual_ownership": [
                        "I built a small load test demonstrating downstream timeout exhaustion in 20 minutes rather than arguing abstractly.",
                        "I proposed a minimal async outbox fallback that kept the launch date intact while protecting core request threads.",
                    ],
                    "team_context": "Worked with product lead and two peer engineers to scope the lightweight circuit-breaker boundary.",
                    "decisions_made": ["We agreed to defer full event-schema generalization until Q2 in exchange for keeping async isolation at launch."],
                    "obstacles_or_failures": "I had to drop my preferred full-refactor proposal because timeline pressure made a 2-day isolation shim the pragmatic win.",
                    "outcome": "We shipped on the original target date and survived two downstream blips without dropping core traffic.",
                    "lessons_learned": "Data from a quick spike settles design disagreements faster than architectural purity, and meeting halfway builds durable trust.",
                    "evidence_status": "documented_candidate_experience" if disagree_job.get("highlights") else "fictional_simulation_scenario",
                    "times_used": 0,
                    "last_used_turn": None,
                }
            )

        return {
            "candidate_id": profile["candidate_id"],
            "stories": stories,
        }

    @staticmethod
    def select_story(
        story_bank: dict[str, Any],
        competency_keywords: list[str],
        exclude_story_ids: set[str] | None = None,
    ) -> dict[str, Any] | None:
        """Select the best matching unused (or least-used) story to prevent story repetition."""
        stories = story_bank.get("stories", [])
        if not stories:
            return None
        excluded = exclude_story_ids or set()
        kw_set = {k.lower() for k in competency_keywords}

        def score_story(story: dict[str, Any]) -> tuple[int, int, int]:
            not_excluded = 1 if story["story_id"] not in excluded else 0
            least_used = -int(story.get("times_used", 0))
            overlap = len(kw_set & {c.lower() for c in story.get("competencies_demonstrated", [])})
            return (not_excluded, least_used, overlap)

        ranked = sorted(stories, key=score_story, reverse=True)
        return ranked[0] if ranked else None
