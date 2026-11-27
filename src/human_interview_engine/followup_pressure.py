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

    _SUPPORT_TITLE_RE = re.compile(
        r"\b(?:support|tse|sysadmin|technical account manager|customer engineer|site operations)\b"
    )
    _SUPPORT_EVIDENCE_RE = re.compile(
        r"\b(?:support tickets?|customer tickets?|ticket queues?|escalations?)\b"
        r"|\b(?:g4dn|g5|p3|p4d|p5|inf1|inf2|trn1)\.[a-z0-9]+\b"
    )
    # Which documented-metric units/keywords can honestly answer a given ledger metric question.
    _METRIC_MATCH_KEYWORDS: dict[str, tuple[str, ...]] = {
        "nodes": ("node", "host", "server", "instance", "machine"),
        "gpus_per_node": ("gpu",),
        "total_gpus": ("gpu",),
        "gpu_hours": ("gpu-hour", "gpu hour"),
        "team_size": ("engineer", "people", "person", "developer", "report"),
        "p99_latency_ms": ("latency", "p99", "ms"),
        "throughput_rps": ("rps", "requests per second", "qps", "throughput"),
        "daily_requests": ("requests", "transactions"),
        "availability_pct": ("availability", "uptime"),
        "monthly_downtime_minutes": ("downtime",),
        "monthly_cost_savings_usd": ("usd", "cost", "spend", "saving"),
        "annual_cost_savings_usd": ("usd", "cost", "spend", "saving"),
        "project_duration_months": ("month", "week"),
    }

    @classmethod
    def _is_support_scope(cls, profile: dict[str, Any], world_model: dict[str, Any] | None) -> bool:
        """True only when the candidate's current role is support/TSE/TAM-style work.

        Matches whole words in the latest role title (not 'supporting' or 'instance' anywhere in the
        resume), the latest employer context's role scope, or explicit ticket/instance-type evidence
        in the latest role's bullets.
        """
        chronology = profile.get("career_chronology", [])
        if not chronology:
            return False
        latest = chronology[0]
        if cls._SUPPORT_TITLE_RE.search((latest.get("role_title") or "").lower()):
            return True
        contexts = (world_model or {}).get("employer_contexts", [])
        if contexts and contexts[0].get("candidate_role_scope") in (
            "support_and_operations",
            "customer_advisory_and_engineering",
        ):
            return True
        return bool(cls._SUPPORT_EVIDENCE_RE.search(" ".join(latest.get("highlights", [])).lower()))

    @classmethod
    def _match_documented_metric(
        cls, target_metric: str | None, metrics: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        """Return a documented resume metric that actually answers the asked metric, else None."""
        keywords = cls._METRIC_MATCH_KEYWORDS.get(target_metric or "")
        if not keywords:
            return None
        for m in metrics:
            unit = str(m.get("unit") or "").lower()
            raw = str(m.get("raw_text") or "").lower()
            ctx = str(m.get("context") or "").lower()
            if any(k in unit or k in raw for k in keywords):
                return m
            # Percentages and counts only qualify when their own bullet names the same quantity.
            if target_metric in ("p99_latency_ms", "availability_pct") and any(k in ctx for k in keywords) and "%" in raw:
                if target_metric == "availability_pct" or "latency" in ctx:
                    return m
        return None

    @staticmethod
    def _spoken_unit(unit: str, value: float) -> str:
        """Pluralize/singularize simple count units so '1 nodes' and 'units' don't reach spoken output."""
        u = (unit or "").strip()
        if not u or u.lower() in ("units", "count"):
            return "in total" if value != 1 else ""
        if value == 1 and u.endswith("s") and not u.endswith("ss"):
            return u[:-1]
        return u

    def handle_numerical_probe(
        self,
        question: str,
        ledger: NumericalLedger,
        project_id: str | None,
        operating_mode: str,
        profile: dict[str, Any],
        world_model: dict[str, Any] | None = None,
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
        low_q = (question or "").lower()

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
            verified = [m for m in profile.get("documented_metrics", [])]
            chron_text = " ".join(
                f"{j.get('role_title', '')} {' '.join(j.get('highlights', []))}"
                for j in profile.get("career_chronology", [])
            ).lower()
            is_support_scope = self._is_support_scope(profile, world_model)

            if is_support_scope and analysis["target_metric"] in ("gpus_per_node", "nodes", "total_gpus"):
                # Extract concrete documented instance types from resume if present
                inst_matches = re.findall(r"\b(?:g4dn|g5|p3|p4d|p5|inf1|inf2|trn1)\.[a-z0-9]+\b", chron_text)
                inst_desc = ", ".join(dict.fromkeys(inst_matches)) if inst_matches else "GPU-backed compute instances"
                if "how large" in low_q:
                    spoken = (
                        f"Most of my hands-on work was troubleshooting individual hosts like {inst_desc}—"
                        f"ranging from single-GPU instances up to multi-GPU nodes depending on the customer workload."
                    )
                elif analysis["target_metric"] == "gpus_per_node":
                    spoken = (
                        f"It depends on the instance family—across {inst_desc}, that ranges from a single GPU per host up to 8 GPUs on larger accelerated nodes."
                    )
                else:
                    spoken = (
                        "On the support side, my visibility was usually scoped to the customer's unhealthy instances or specific node group in a ticket—"
                        "typically one host up to a handful of affected nodes—rather than the customer's full cluster inventory."
                    )
            elif self._match_documented_metric(analysis["target_metric"], verified) is not None:
                vm = self._match_documented_metric(analysis["target_metric"], verified)
                where = f" at {vm['employer']}" if vm.get("employer") else ""
                spoken = (
                    f"The number I can stand behind{where} is {vm['raw_text']}. "
                    f"I don't have the exact breakdown for that figure offhand, though I can walk through how we measured it."
                )
            else:
                spoken = (
                    "I don't have the exact historical figure offhand without pulling the original telemetry, though I can walk through "
                    "how we sized node capacity and validated bottlenecks at the instance level."
                )
            return {
                "spoken_draft": spoken,
                "project_used": None,
                "evidence_basis": "documented_candidate_experience" if is_support_scope else "general_technical_knowledge",
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
                elif metric_name == "gpus_per_node":
                    nodes_e = analysis["all_project_metrics"].get("nodes")
                    total_e = analysis["all_project_metrics"].get("total_gpus")
                    if nodes_e and total_e:
                        spoken = (
                            f"Each node carried {val:g} GPUs, across {nodes_e['original_value']:g} nodes for {total_e['original_value']:,.0f} GPUs total."
                        )
                    else:
                        spoken = f"Each node had {val:g} GPUs."
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
                    spoken = f"That was {val:,.0f} {self._spoken_unit(unit, val)}".rstrip()
                    formula = (entry.get("formula") or "").strip()
                    spoken += f"—{formula}." if formula else "."
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
