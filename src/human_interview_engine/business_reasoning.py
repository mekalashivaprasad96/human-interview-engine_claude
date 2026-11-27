"""Business, Customer, Recruiter, and Executive Intelligence Engine."""

from __future__ import annotations

from typing import Any


class BusinessIntelligenceEngine:
    """Frames answers for recruiters, executives, customer stakeholders, and business outcomes."""

    def reason_recruiter(
        self,
        question: str,
        profile: dict[str, Any],
        world_model: dict[str, Any],
        jd_analysis: dict[str, Any],
    ) -> dict[str, Any]:
        """Deliver crisp, natural career narrative and role motivation."""
        low = question.lower()
        chronology = profile.get("career_chronology", [])
        latest = chronology[0] if chronology else {"role_title": "Engineer", "employer": "my current team"}
        seniority = world_model.get("inferred_seniority", {})
        strengths = jd_analysis.get("candidate_strengths", [])[:3]
        strength_str = ", ".join(strengths) if strengths else "building reliable production systems"
        target_role = jd_analysis.get("target_role", "this role")
        target_company = jd_analysis.get("target_company", "your team")

        if any(k in low for k in ("why are you", "why this role", "why our company", "looking to leave", "motivated")):
            spoken = (
                f"I've enjoyed the ownership I've had as a {latest.get('role_title')} at {latest.get('employer')}, especially around {strength_str}. "
                f"What stood out about {target_role} at {target_company} is the chance to apply that directly to {jd_analysis.get('target_industry', 'production scale')} "
                f"challenges where reliability and practical execution really move the needle."
            )
        else:
            years = seniority.get("total_years_experience", 4)
            industries = ", ".join(dict.fromkeys(c["industry"] for c in world_model.get("employer_contexts", []))) or "software engineering"
            spoken = (
                f"I've spent about {years:g} years working across {industries}, most recently as a {latest.get('role_title')} at {latest.get('employer')}. "
                f"Most of my hands-on focus has been around {strength_str}—taking ambiguous reliability or delivery problems from root cause to stable production. "
                f"At this stage, I'm looking for a {target_role} scope where I can combine deep technical ownership with strong cross-team impact."
            )

        return {
            "spoken_draft": spoken,
            "project_used": None,
            "evidence_basis": "documented_candidate_experience",
        }

    def reason_business_or_executive(
        self,
        question: str,
        project: dict[str, Any] | None,
        world_model: dict[str, Any],
        jd_analysis: dict[str, Any],
        operating_mode: str,
    ) -> dict[str, Any]:
        """Respond with executive brevity: business outcome, ROI/risk, customer trust, no low-level sprawl."""
        low = question.lower()
        if project and operating_mode != "authentic_preparation":
            scale = project.get("infrastructure_scale", {})
            savings = scale.get("monthly_cost_savings_usd", 12000)
            avail = scale.get("availability_pct", 99.95)
            spoken = (
                f"The business goal at {project['employer']} wasn't just faster services—it was protecting customer trust and infrastructure margin at the same time. "
                f"By isolating high-priority traffic and tightening autoscaling thresholds, we held {avail}% availability and cut run-rate infrastructure spend by "
                f"roughly ${savings:,.0f} a month without slowing feature delivery."
            )
            if "customer" in low or "stakeholder" in low:
                spoken += " Keeping stakeholders aligned came down to agreeing upfront on clear cutover criteria and sharing live canary metrics before switching production."
            return {
                "spoken_draft": spoken,
                "project_used": project["project_id"],
                "evidence_basis": project["evidence_status"],
            }

        spoken = (
            f"I tie technical decisions directly to three business levers: customer time-to-value, SLA risk exposure, and unit cost. "
            f"Rather than pitching broad rewrites, I anchor proposals on measurable operational risk reduction or run-rate savings, stage rollouts "
            f"with clear rollback gates, and align product and finance stakeholders around concrete milestone metrics."
        )
        return {
            "spoken_draft": spoken,
            "project_used": None,
            "evidence_basis": "transferable_professional_knowledge",
        }
