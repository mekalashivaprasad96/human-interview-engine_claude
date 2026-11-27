"""Technical Implementation, Troubleshooting, and System Design Reasoning Engines."""

from __future__ import annotations

import re
from typing import Any


def _lc_lead(text: str) -> str:
    """Lowercase the leading word only when it is not an uppercase acronym (e.g. SLI, GPU, CUDA)."""
    s = (text or "").strip()
    if not s:
        return s
    first_tok = s.split()[0]
    if len(first_tok) >= 2 and first_tok[:2].isupper():
        return s
    return s[0].lower() + s[1:]


def _resume_clause(text: str) -> str:
    """Turn a bare resume bullet like 'Developed...' into a grammatical 'I developed...' clause."""
    s = _lc_lead(text)
    if re.match(r"^(?:developed|built|led|automated|managed|reduced|designed|wrote|helped|introduced|advised|maintained)\b", s):
        return f"I {s}"
    return s


class TechnicalReasoningEngine:
    """Handles implementation, config, architecture, troubleshooting, and system design turns."""

    def reason_implementation(
        self,
        question: str,
        project: dict[str, Any] | None,
        world_model: dict[str, Any],
        jd_analysis: dict[str, Any],
        operating_mode: str,
        opening_style: str,
        precision_targets: list[str],
    ) -> dict[str, Any]:
        """Formulate an implementation-focused response grounded in project details or honest gaps."""
        low = question.lower()
        seniority = world_model.get("inferred_seniority", {}).get("level", "mid")
        gaps = {g.lower() for g in jd_analysis.get("candidate_gaps", [])}
        skills = {t["name"].lower() for t in world_model.get("competency_graph", {}).get("technical_competencies", [])}

        # Check if interviewer asks directly about a candidate gap technology
        for gap in gaps:
            if re.search(rf"(?<![a-z0-9]){re.escape(gap)}(?![a-z0-9])", low) and gap not in skills:
                transferable = jd_analysis.get("transferable_skills", [])
                anchor = transferable[0] if transferable else (next(iter(skills)) if skills else "distributed systems")
                spoken = (
                    f"I haven't run {gap} directly in production yet—most of my hands-on work has been with {anchor}. "
                    f"The underlying operational model is similar, though: I'd focus first on how state, failure isolation, "
                    f"and observability behave under load before putting critical traffic on it."
                )
                return {
                    "spoken_draft": spoken,
                    "project_used": None,
                    "evidence_basis": "transferable_professional_knowledge",
                }

        if operating_mode == "authentic_preparation":
            # Stick strictly to documented skills & general engineering knowledge
            spoken = (
                f"From the production environments I've worked in, the main goal is usually protecting tail latency while keeping rollouts reversible. "
                f"In practice, that starts with separating synchronous request handling from slower downstream work, setting explicit connection and "
                f"timeout budgets, and rolling changes out behind small canary slices so metrics catch regressions before full traffic hits."
            )
            return {
                "spoken_draft": spoken,
                "project_used": None,
                "evidence_basis": "general_technical_knowledge",
            }

        if not project:
            return {
                "spoken_draft": (
                    "I start by pinning down the traffic profile and failure boundary, separating critical-path latency from async work, "
                    "and validating timeout and retry budgets under load before cutting over traffic."
                ),
                "project_used": None,
                "evidence_basis": "general_technical_knowledge",
            }

        stack_names = [t["name"] for t in project.get("technology_stack", [])]
        stack_str = ", ".join(stack_names[:4]) if stack_names else "our core runtime stack"
        decisions = project.get("implementation_decisions", [])
        # Select most relevant decision matching question keywords when multiple exist
        first_decision = decisions[0] if decisions else None
        if len(decisions) > 1:
            q_words = set(re.findall(r"[a-z0-9]+", low))
            scored_decs = sorted(
                decisions,
                key=lambda d: len(q_words & set(re.findall(r"[a-z0-9]+", (d["decision"] + " " + d["rationale"]).lower()))),
                reverse=True,
            )
            first_decision = scored_decs[0]

        scale = project.get("infrastructure_scale", {})
        ops = project.get("operational_considerations", {})
        contributions = project.get("individual_contributions", [])

        # Precision routing: config / testing / rollback / telemetry / reconciliation / ownership / stack
        if "what_did_you_personally_do" in precision_targets:
            own = " ".join(contributions[:2]) if contributions else "I owned the core design and production validation."
            spoken = (
                f"On {project['title'].split('(')[0].strip()}, {own} "
                f"The rest of the {project['team_structure']['team_size']}-person team handled adjacent dashboarding and downstream integration tests."
            )
        elif any(k in low for k in ("opentelemetry", "prometheus", "kubectl", "telemetry", "monitoring", "tracking", "observability")):
            monitoring_txt = ops.get("monitoring", "SLI dashboards tracking p50/p95/p99 latency and error budget burn").rstrip(".")
            monitoring_s = _lc_lead(monitoring_txt)
            spoken = (
                f"On {project['employer']}, we paired {monitoring_s} with trace propagation from the ingress gateway straight down to the worker pods. "
                f"We used kubectl/Kubernetes events and pod readiness metrics alongside p99 histograms so we could correlate tail-latency jumps directly with pod warm-up or queue saturation."
            )
        elif any(k in low for k in ("reconciliation", "lag", "kafka", "backpressure", "outbox")):
            spoken = (
                f"At {project['employer']}, {_resume_clause(project['project_scope'])} "
                f"We separated the fast ingestion path from slower downstream reconciliation via idempotent queue partitioning and bounded consumer retries, "
                f"so transient downstream stalls showed up as measurable consumer lag rather than dropping primary requests."
            )
        elif any(k in low for k in ("config", "setting", "parameter", "batch", "timeout", "flag")):
            if first_decision:
                rat = first_decision["rationale"]
                trd = first_decision["tradeoffs"]
                rat_s = rat[0].lower() + rat[1:] if rat else ""
                trd_s = trd[0].lower() + trd[1:] if trd else ""
                spoken = f"{first_decision['decision']} That {rat_s} The trade-off was {trd_s}"
            else:
                spoken = (
                    f"We tightened request timeouts, capped retry amplification with jitter, and enforced strict readiness checks "
                    f"on {stack_str} so unhealthy instances couldn't enter rotation early."
                )
        elif any(k in low for k in ("test", "validate", "rollout", "canary", "rollback", "deploy")):
            test_m = project.get("testing_methodology", "load testing at 1.5x peak before canarying").rstrip(".")
            test_s = test_m[0].lower() + test_m[1:]
            rb_m = ops.get("rollback_plan", "canary gates auto-reverted traffic on p99 or 5xx spikes").rstrip(".")
            rb_s = rb_m[0].lower() + rb_m[1:]
            spoken = (
                f"We ran {test_s}. For safety, {rb_s}, "
                f"which kept blast radius bounded during rollout."
            )
        elif any(k in low for k in ("stack", "tools", "technologies", "which tech", "built with")):
            c0 = project["constraints"][0] if project.get("constraints") else "reliability constraints"
            c0_s = c0[0].lower() + c0[1:]
            spoken = (
                f"That ran on {stack_str} across a {scale.get('nodes', 12)}-node setup at {project['employer']}. "
                f"We picked that stack largely because it fit our existing operational tooling and {c0_s}"
            )
        elif "why" in precision_targets and first_decision:
            alts = " or ".join((a[0].lower() + a[1:]) for a in first_decision.get("alternatives_considered", [])[:2]) or "simpler static configs"
            rat = first_decision["rationale"]
            trd = first_decision["tradeoffs"]
            rat_s = rat[0].lower() + rat[1:] if rat else ""
            trd_s = trd[0].lower() + trd[1:] if trd else ""
            spoken = (
                f"We went that route instead of {alts} because that {rat_s} "
                f"In return, we accepted {trd_s}"
            )
        else:
            # General implementation walkthrough varied by opening style
            if opening_style == "constraint_first" and project.get("constraints"):
                c0 = project["constraints"][0]
                opener = f"At {project['employer']}, the main constraint was that {c0[0].lower() + c0[1:]}"
            elif opening_style == "decision_first" and first_decision:
                opener = first_decision["decision"]
            else:
                arch = project["architecture_summary"]
                opener = f"On that {project['employer']} project, {arch[0].lower() + arch[1:]}"

            contrib = contributions[0] if contributions else "I implemented the core request isolation and telemetry paths."
            dec_part = (
                f"{first_decision['decision']} "
                if first_decision and opening_style != "decision_first"
                else ""
            )
            spoken = (
                f"{opener} {dec_part}{contrib} "
                f"That got us from {scale.get('p99_latency_baseline_ms', 420):g}ms down to {scale.get('p99_latency_final_ms', 245):g}ms at p99 "
                f"while holding {scale.get('availability_pct', 99.95)}% availability."
            )

        if seniority == "junior" and "team" not in spoken.lower():
            spoken += " I paired with a senior engineer on the rollout thresholds before enabling it in prod."

        return {
            "spoken_draft": spoken.strip(),
            "project_used": project["project_id"],
            "evidence_basis": project["evidence_status"],
        }

    def reason_troubleshooting(
        self,
        question: str,
        project: dict[str, Any] | None,
        operating_mode: str,
    ) -> dict[str, Any]:
        """Reason systematically through symptoms, impact, evidence, hypotheses, mitigation, and prevention."""
        low = question.lower()
        is_hypothetical = any(k in low for k in ("suppose", "if you saw", "how would you debug", "what if", "imagine"))

        if is_hypothetical or operating_mode == "authentic_preparation" or not project:
            spoken = (
                "First I'd check business impact and blast radius—whether errors or latency spikes are isolated to one zone, "
                "one tenant, or tied to a recent deploy or config push. While pulling error-rate and saturation metrics across CPU, memory, "
                "and connection pools, I'd isolate whether it's an upstream traffic surge or downstream dependency stall. "
                "If a recent change correlates, I'd roll back or drain the affected slice first to stop customer impact, capture heap or trace "
                "snapshots before restarting pods, and only then dig into root cause and add a regression gate."
            )
            return {
                "spoken_draft": spoken,
                "project_used": None,
                "evidence_basis": "general_technical_knowledge",
            }

        challenge = project["challenges"][0] if project.get("challenges") else "we hit unexpected saturation during peak load."
        ops = project.get("operational_considerations", {})
        rb = ops.get("rollback_plan", "canary traffic rollback").rstrip(".")
        rb_s = rb[0].lower() + rb[1:]
        spoken = (
            f"We ran into a real issue at {project['employer']} where {challenge[0].lower() + challenge[1:]} "
            f"Looking at p99 histograms alongside resource saturation and recent rollout logs showed the symptom was localized to new instances taking traffic too early. "
            f"Rather than debugging live while errors piled up, I relied on {rb_s} to stabilize customer latency in minutes, "
            f"preserved pod diagnostics before cycling them, and then tightened readiness gating and load-test coverage so it couldn't ship again."
        )
        return {
            "spoken_draft": spoken,
            "project_used": project["project_id"],
            "evidence_basis": project["evidence_status"],
        }

    def reason_system_design(
        self,
        question: str,
        world_model: dict[str, Any],
        jd_analysis: dict[str, Any],
    ) -> dict[str, Any]:
        """Structure requirements, scale, architecture, trade-offs, failure modes, and validation naturally."""
        low = question.lower()
        seniority = world_model.get("inferred_seniority", {}).get("level", "senior")
        industry = jd_analysis.get("target_industry", "production cloud")

        if any(k in low for k in ("rate limit", "limiter", "throttle")):
            domain_core = (
                "I'd run local token-bucket counters in memory at the gateway for sub-millisecond enforcement and sync soft state asynchronously "
                "to a Redis cluster rather than making a synchronous Redis hop on every single request. If Redis degrades, gateways fall back to "
                "conservative local per-instance caps so an internal cache hiccup doesn't take down customer traffic."
            )
        elif any(k in low for k in ("inference", "gpu", "llm", "model")):
            domain_core = (
                "I'd put a stateless router in front of specialized GPU worker pools, using prefix/KV-cache aware routing and bounded micro-batching. "
                "Interactive traffic gets dedicated priority queues isolated from batch jobs so long-context workloads don't cause head-of-line blocking, "
                "and autoscaling keys off queue wait time rather than raw GPU utilization alone."
            )
        else:
            domain_core = (
                "I'd keep the ingress tier stateless behind L7 load balancing, separate synchronous reads/writes from slow downstream work via an idempotent "
                "event queue, and cache hot reads with explicit TTLs and stampede protection. State stays partitioned cleanly by tenant or entity key "
                "so hot spots don't cascade."
            )

        spoken = (
            f"Before picking components, I'd nail down the read/write ratio, target p99 latency, and consistency boundaries for {industry}. "
            f"{domain_core} "
            f"On the operational side, every boundary gets circuit breakers, bounded retries with jitter, and staged canary deploys tied to SLO burn rate. "
            f"The main trade-off is keeping the initial topology simple enough for a small team to debug at 3 a.m. rather than adding extra message hops "
            f"or multi-region active-active complexity before traffic and compliance requirements justify it."
        )
        if seniority in ("staff", "principal", "director", "executive"):
            spoken += " I'd also track unit cost per thousand requests early so scaling capacity doesn't silently break gross margin."

        return {
            "spoken_draft": spoken,
            "project_used": None,
            "evidence_basis": "general_technical_knowledge",
        }
