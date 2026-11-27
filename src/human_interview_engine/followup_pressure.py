"""Follow-Up Intelligence and Pressure / Challenge / Correction Handler."""

from __future__ import annotations

import re
from typing import Any

from .numerical_engine import NumericalEngine
from .numerical_ledger import NumericalLedger


_FALSE_PREMISE_RULES: tuple[tuple[str, str], ...] = (
    (
        r"kubernetes.*hypervisor|hypervisor.*kubernetes",
        "Not quite—Kubernetes isn't a hypervisor. It schedules containers using Linux namespaces and cgroups on the host kernel, unless you explicitly layer something like Kata Containers or Firecracker underneath.",
    ),
    (
        r"tcp.*(?:guarantee|prevents?).*duplicate|tcp.*exactly[- ]once",
        "TCP prevents duplicates within a single live byte stream, but it doesn't guarantee exactly-once processing across application-level retries or reconnects—you still need idempotency keys at the application or storage layer.",
    ),
    (
        r"stateless.*(?:eliminates|means no).*(?:database|persistence)",
        "Stateless compute just means individual app pods don't hold durable session state locally; the underlying state still lives in an external store, cache, or queue that has to scale cleanly.",
    ),
    (
        r"99\.9%.*zero downtime|three nines.*no downtime",
        "Three nines still allows about 43 minutes of downtime a month—so while it's solid for many services, critical checkout or control-plane paths usually budget tighter.",
    ),
)


class FollowUpAndPressureHandler:
    """Handles deep follow-ups, numerical challenges, false premises, corrections, and uncertainty."""

    def __init__(self, numerical_engine: NumericalEngine) -> None:
        self.numerical_engine = numerical_engine

    def handle_numerical_probe(
        self,
        question: str,
        ledger: NumericalLedger,
        project_id: str | None,
        operating_mode: str,
        profile: dict[str, Any],
    ) -> dict[str, Any]:
        """Answer numerical questions directly using ledger values, derivations, and methodology."""
        analysis = self.numerical_engine.analyze_numerical_query(
            question=question,
            ledger=ledger,
            project_id=project_id,
            operating_mode=operating_mode,
        )
        entry = analysis["entry"]
        dyn = analysis["dynamic_calculation"]
        discrepancy = analysis["challenge_discrepancy"]

        # 1. Check for interviewer math discrepancy challenge first
        if discrepancy is not None:
            proposed = discrepancy["proposed_value"]
            actual = discrepancy["ledger_value"]
            unit = discrepancy["unit"]
            expl = discrepancy["explanation"]
            spoken = (
                f"Actually it comes out to {actual:,.0f} {unit}, not {proposed:,.0f}—{expl}. "
                f"So with the exact scope we used, {actual:,.0f} {unit} is the right capacity figure."
            )
            return {
                "spoken_draft": spoken,
                "project_used": project_id,
                "evidence_basis": entry["evidence_status"] if entry else "calculated_numerical_information",
            }

        # 2. Authentic preparation protection against inventing unverified metrics
        if analysis["authentic_restriction"]:
            verified = [
                m for m in profile.get("documented_metrics", [])
            ]
            if verified:
                vm = verified[0]
                spoken = (
                    f"From my verified numbers, I can speak directly to {vm['raw_text']} at {vm['employer']} ({vm['context']}). "
                    f"I don't have the exact raw breakdown for that specific metric in front of me without guessing, though I can walk through how I'd measure and calculate it."
                )
            else:
                spoken = (
                    "I don't want to guess an exact historical figure I didn't directly log, though I can walk through the exact calculation methodology—multiplying active node/unit capacity by the measurement window and validating against ingress telemetry."
                )
            return {
                "spoken_draft": spoken,
                "project_used": None,
                "evidence_basis": "general_technical_knowledge",
            }

        # 3. Dynamic GPU-hours or composite derivation
        if dyn is not None:
            spoken = (
                f"That's {dyn['value']:,.0f} GPU-hours—{dyn['formula']}."
            )
            return {
                "spoken_draft": spoken,
                "project_used": project_id,
                "evidence_basis": "calculated_numerical_information",
            }

        if entry is not None:
            val = entry["original_value"]
            unit = entry["unit"]
            metric_name = entry["metric_name"]
            if analysis["asked_how_calculated"]:
                if entry.get("baseline_value") is not None and entry.get("final_value") is not None:
                    b = entry["baseline_value"]
                    f = entry["final_value"]
                    pct = abs(entry.get("percentage_change") or 0)
                    spoken = (
                        f"We measured a baseline of {b:g} {unit} and got it down to {f:g} {unit}, which is a {pct:g}% reduction. "
                        f"Specifically, {entry['measurement_methodology'][0].lower() + entry['measurement_methodology'][1:]}"
                    )
                elif entry.get("formula"):
                    spoken = (
                        f"That comes from {entry['formula']}, which gives {val:,.0f} {unit}. "
                        f"{entry['measurement_methodology']}"
                    )
                else:
                    spoken = (
                        f"It was {val:g} {unit}. {entry['measurement_methodology']}"
                    )
            else:
                if metric_name == "total_gpus":
                    nodes_e = analysis["all_project_metrics"].get("nodes")
                    gpn_e = analysis["all_project_metrics"].get("gpus_per_node")
                    if nodes_e and gpn_e:
                        spoken = (
                            f"That was {val:,.0f} GPUs total—{nodes_e['original_value']:g} nodes with {gpn_e['original_value']:g} GPUs per node."
                        )
                    else:
                        spoken = f"We ran {val:,.0f} {unit} in that cluster."
                elif metric_name == "p99_latency_ms" and entry.get("baseline_value") is not None:
                    b = entry["baseline_value"]
                    f = entry["final_value"]
                    pct = abs(entry.get("percentage_change") or 0)
                    spoken = f"Baseline p99 was {b:g}ms, and after the changes we brought it down to {f:g}ms—about a {pct:g}% drop."
                elif metric_name == "team_size":
                    spoken = f"There were {val:g} engineers on the squad—I owned the core service/reliability path while teammates handled telemetry and downstream integration."
                elif metric_name == "daily_requests":
                    spoken = f"At sustained peak, that works out to roughly {val:,.0f} {unit} ({entry['formula']})."
                else:
                    scope_s = entry["scope"][0].lower() + entry["scope"][1:] if entry.get("scope") else "that workload"
                    spoken = f"That was {val:,.0f} {unit} across {scope_s}."
            return {
                "spoken_draft": spoken,
                "project_used": entry["project_id"],
                "evidence_basis": entry["evidence_status"],
            }

        return {
            "spoken_draft": (
                "We tracked baseline versus post-change metrics across matched traffic windows—specifically ingress p99 histograms, "
                "saturation, and error rates—so we could isolate the actual capacity delta."
            ),
            "project_used": project_id,
            "evidence_basis": "general_technical_knowledge",
        }

    def handle_pressure_or_correction(
        self,
        question: str,
        question_act: str,
        project: dict[str, Any] | None,
        previous_turns: list[dict[str, Any]],
        ledger: NumericalLedger,
    ) -> dict[str, Any]:
        """Handle false premises, valid corrections, 'are you sure?', and failure-mode probes."""
        low = question.lower()

        # 1. Check false technical premises — do NOT blindly agree!
        for pat, rebuttal in _FALSE_PREMISE_RULES:
            if re.search(pat, low):
                return {
                    "spoken_draft": rebuttal,
                    "project_used": project["project_id"] if project else None,
                    "evidence_basis": "general_technical_knowledge",
                }

        # 2. Check numerical challenge inside a pressure question
        if any(k in low for k in ("gpu", "node", "latency", "rps", "team", "cost", "4096", "5000", "256")):
            num_res = self.handle_numerical_probe(
                question=question,
                ledger=ledger,
                project_id=project["project_id"] if project else None,
                operating_mode="immersive_simulation",
                profile={},
            )
            if num_res and num_res.get("spoken_draft"):
                return num_res

        # 3. Legitimate correction acknowledgment
        if question_act == "correction" or any(k in low for k in ("breaks live", "backward compat", "drop column", "would fail")):
            return {
                "spoken_draft": (
                    "You're right—doing that in a single step breaks live readers still on the old contract. "
                    "In practice, you have to use an expand-and-contract pattern: add the new path backward-compatibly, drain old readers, and clean up in a second deploy."
                ),
                "project_used": project["project_id"] if project else None,
                "evidence_basis": "general_technical_knowledge",
            }

        # 4. "What would happen if X failed?"
        if any(k in low for k in ("if this component failed", "if that failed", "single point of failure", "went down")):
            ops = project.get("operational_considerations", {}) if project else {}
            spoken = (
                f"If that tier dropped, traffic would shed or fail over at the gateway within our circuit-breaker window rather than hanging upstream threads. "
                f"{ops.get('failure_modes', 'We kept the state store decoupled and used automated health checks to isolate degraded nodes quickly.')}"
            )
            return {
                "spoken_draft": spoken,
                "project_used": project["project_id"] if project else None,
                "evidence_basis": project["evidence_status"] if project else "general_technical_knowledge",
            }

        # 5. "Are you sure?" / skepticism — hold ground calmly with validation method
        if "are you sure" in low or "really" in low:
            last_ans = previous_turns[-1].get("candidate_response", "") if previous_turns else ""
            if last_ans:
                return {
                    "spoken_draft": (
                        "Yes—though in production I'd never take a number or behavior on faith without checking the actual histogram, "
                        "config diff, and canary error budget in telemetry first."
                    ),
                    "project_used": project["project_id"] if project else None,
                    "evidence_basis": "general_technical_knowledge",
                }

        # 6. Fallback calm technical defense using active project decisions
        if project and project.get("implementation_decisions"):
            d = project["implementation_decisions"][0]
            spoken = (
                f"Fair pushback—{d['tradeoffs'][0].lower() + d['tradeoffs'][1:]} "
                f"We still went with it because {d['rationale'].lower()} and we could verify it cleanly in canary metrics."
            )
            return {
                "spoken_draft": spoken,
                "project_used": project["project_id"],
                "evidence_basis": project["evidence_status"],
            }

        return {
            "spoken_draft": (
                "That's a fair trade-off to pressure-test. My bias is keeping the failure boundary explicit and verifying behavior under synthetic load "
                "so we know how it degrades before live traffic finds out."
            ),
            "project_used": project["project_id"] if project else None,
            "evidence_basis": "general_technical_knowledge",
        }
