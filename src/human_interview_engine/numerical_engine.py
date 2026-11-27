"""Numerical Intelligence Engine — deterministic calculation, retrieval, and math challenge defense."""

from __future__ import annotations

import re
from typing import Any

from .numerical_ledger import NumericalLedger


class NumericalEngine:
    """Resolves quantitative questions using the ledger and mathematical derivation."""

    @staticmethod
    def extract_numbers_in_text(text: str) -> list[float]:
        """Extract numeric literals from text (handling commas and optional decimals)."""
        matches = re.findall(r"(?<![a-zA-Z])(\d[\d,]*(?:\.\d+)?)(?![a-zA-Z])", text or "")
        values: list[float] = []
        for raw in matches:
            try:
                values.append(float(raw.replace(",", "")))
            except ValueError:
                continue
        return values

    def analyze_numerical_query(
        self,
        question: str,
        ledger: NumericalLedger,
        project_id: str | None = None,
        operating_mode: str = "immersive_simulation",
    ) -> dict[str, Any]:
        """Identify the exact metric asked, retrieve/derive it, and detect interviewer math discrepancies."""
        q = (question or "").lower()
        entries = ledger.get_project_metrics(project_id) if project_id else {
            e["metric_name"]: e for e in ledger.entries
        }
        asked_how_calculated = any(
            phrase in q
            for phrase in (
                "how did you calculate",
                "how was that calculated",
                "how did you measure",
                "walk me through the math",
                "how do you get",
                "where does that number come from",
                "what was the baseline",
            )
        )

        target_metric: str | None = None
        if any(k in q for k in ("gpu-hour", "gpu hour", "gpu hours")):
            target_metric = "gpu_hours"
        elif any(k in q for k in ("per node", "gpus per node", "how large", "node size", "instance size")) or re.search(
            r"(?:do|does)\s+(?:those|that|each)\s+(?:gpu|node|server)s?.*\bcontains?\b", q
        ):
            target_metric = "gpus_per_node"
        elif "how many gpu" in q or "total gpu" in q or ("gpus" in q and "node" not in q):
            target_metric = "total_gpus"
        elif "node" in q or "server" in q or "host" in q or "cluster" in q:
            target_metric = "nodes"
        elif "team size" in q or "how many engineers" in q or "how big was the team" in q or "people on the team" in q:
            target_metric = "team_size"
        elif "daily request" in q or "requests per day" in q or "traffic volume" in q:
            target_metric = "daily_requests"
        elif "rps" in q or "qps" in q or "throughput" in q or "requests per second" in q:
            target_metric = "throughput_rps"
        elif "latency" in q or "p99" in q or "p95" in q or "baseline" in q:
            target_metric = "p99_latency_ms"
        elif "availability" in q or "uptime" in q or "slo" in q or "downtime" in q:
            target_metric = "availability_pct"
        elif "cost" in q or "savings" in q or "spend" in q or "budget" in q:
            target_metric = "monthly_cost_savings_usd"
        elif "duration" in q or "how long" in q or "months" in q or "weeks" in q:
            target_metric = "project_duration_months"

        # Derive missing composite metric on the fly if primitives exist
        derived_note = None
        if target_metric == "gpu_hours" and "gpu_hours" not in entries:
            if {"total_gpus", "allocation_hours"} <= set(entries):
                val = entries["total_gpus"]["original_value"] * entries["allocation_hours"]["original_value"]
                base_verified = (
                    entries["total_gpus"]["evidence_status"] in {"verified_numerical_information", "calculated_numerical_information"}
                    and entries["allocation_hours"]["evidence_status"] in {"verified_numerical_information", "calculated_numerical_information"}
                )
                entry = ledger.record_metric(
                    project_id=project_id or entries["total_gpus"]["project_id"],
                    metric_name="gpu_hours",
                    original_value=val,
                    unit="GPU-hours",
                    scope=entries["total_gpus"]["scope"],
                    measurement_period=entries["allocation_hours"]["measurement_period"],
                    measurement_methodology="Calculated by multiplying total allocated GPUs by run duration hours.",
                    evidence_status="calculated_numerical_information" if base_verified else "fictional_simulation_scenario",
                    derived_from=["total_gpus", "allocation_hours"],
                    formula=f"{entries['total_gpus']['original_value']:g} GPUs * {entries['allocation_hours']['original_value']:g} hours",
                )
                entries["gpu_hours"] = entry
                derived_note = entry["formula"]

        # Handle dynamic hour multiplication in question e.g. "if allocated for 48 hours"
        hours_match = re.search(r"(\d+(?:\.\d+)?)\s*hours?", q)
        dynamic_calculation = None
        if hours_match and "total_gpus" in entries and ("gpu" in q or "capacity" in q):
            hrs = float(hours_match.group(1))
            gpus = entries["total_gpus"]["original_value"]
            computed_gpu_hrs = gpus * hrs
            dynamic_calculation = {
                "metric": "gpu_hours",
                "value": computed_gpu_hrs,
                "formula": f"{gpus:g} GPUs * {hrs:g} hours = {computed_gpu_hrs:,.0f} GPU-hours",
            }
            if "gpu_hours" not in entries:
                base_ev = entries["total_gpus"]["evidence_status"]
                is_verified = base_ev in {"verified_numerical_information", "calculated_numerical_information"}
                ledger.record_metric(
                    project_id=project_id or entries["total_gpus"]["project_id"],
                    metric_name="allocation_hours",
                    original_value=hrs,
                    unit="hours",
                    scope=entries["total_gpus"]["scope"],
                    measurement_period=f"{hrs:g}-hour window",
                    measurement_methodology="Window specified during interview.",
                    evidence_status="calculated_numerical_information" if is_verified else "fictional_simulation_scenario",
                )
                ledger.record_metric(
                    project_id=project_id or entries["total_gpus"]["project_id"],
                    metric_name="gpu_hours",
                    original_value=computed_gpu_hrs,
                    unit="GPU-hours",
                    scope=entries["total_gpus"]["scope"],
                    measurement_period=f"{hrs:g}-hour window",
                    measurement_methodology="Product of total active GPUs and allocation duration.",
                    evidence_status="calculated_numerical_information" if is_verified else "fictional_simulation_scenario",
                    derived_from=["total_gpus", "allocation_hours"],
                    formula=f"{gpus:g} GPUs * {hrs:g} hours",
                )
                entries = ledger.get_project_metrics(project_id) if project_id else {
                    e["metric_name"]: e for e in ledger.entries
                }

        entry = entries.get(target_metric) if target_metric else None
        challenge_discrepancy = None
        if entry is not None:
            nums_in_q = self.extract_numbers_in_text(question)
            expected_val = (
                dynamic_calculation["value"]
                if dynamic_calculation
                else entry["original_value"]
            )
            # Check if interviewer asserts an inconsistent number (e.g. "wouldn't that be 5,000?")
            if any(k in q for k in ("isn't that", "wouldn't that be", "wasn't it", "you said")) and nums_in_q:
                asserted_m = re.search(
                    r"(?:isn't that|wouldn't that be|wasn't it)\s+(\d[\d,]*(?:\.\d+)?)",
                    q,
                )
                candidates = (
                    [float(asserted_m.group(1).replace(",", ""))]
                    if asserted_m
                    else list(reversed(nums_in_q))
                )
                primitive_vals = {
                    entries[k]["original_value"]
                    for k in ("nodes", "gpus_per_node", "total_gpus", "allocation_hours")
                    if k in entries and k != target_metric
                }
                for candidate_num in candidates:
                    if hours_match and abs(candidate_num - float(hours_match.group(1))) < 1e-6:
                        continue
                    if not asserted_m and any(abs(candidate_num - pv) < 1e-6 for pv in primitive_vals):
                        continue
                    if abs(candidate_num - expected_val) > max(1.0, 0.02 * expected_val):
                        challenge_discrepancy = {
                            "proposed_value": candidate_num,
                            "ledger_value": expected_val,
                            "unit": entry["unit"],
                            "explanation": entry.get("formula") or entry.get("measurement_methodology"),
                        }
                        break

        authentic_restriction = (
            operating_mode == "authentic_preparation"
            and entry is not None
            and entry["evidence_status"] not in {"verified_numerical_information", "calculated_numerical_information"}
        )

        return {
            "target_metric": target_metric,
            "entry": entry,
            "asked_how_calculated": asked_how_calculated,
            "dynamic_calculation": dynamic_calculation,
            "derived_note": derived_note,
            "challenge_discrepancy": challenge_discrepancy,
            "authentic_restriction": authentic_restriction,
            "all_project_metrics": entries,
        }

    @staticmethod
    def validate_response_numbers(
        response_text: str,
        ledger: NumericalLedger,
        project_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Check whether numbers mentioned for known quantities contradict the ledger."""
        violations: list[dict[str, Any]] = []
        metrics = ledger.get_project_metrics(project_id) if project_id else {
            e["metric_name"]: e for e in ledger.entries
        }
        low = (response_text or "").lower()

        patterns = [
            ("nodes", r"\b(\d[\d,]*)\s+(?:worker\s+|gpu\s+|compute\s+)?nodes?\b"),
            ("gpus_per_node", r"\b(\d[\d,]*)\s+gpus?\s+per\s+node\b"),
            ("total_gpus", r"\b(\d[\d,]*)\s+total\s+gpus?\b"),
            ("gpu_hours", r"\b(\d[\d,]*)\s+gpu[- ]hours?\b"),
            ("team_size", r"\bteam\s+of\s+(\d[\d,]*)\b"),
        ]
        for metric_name, pattern in patterns:
            if metric_name not in metrics:
                continue
            expected = metrics[metric_name]["original_value"]
            for m in re.finditer(pattern, low):
                found = float(m.group(1).replace(",", ""))
                if abs(found - expected) > 1e-6:
                    violations.append(
                        {
                            "metric_name": metric_name,
                            "found_value": found,
                            "expected_value": expected,
                            "reason": f"Response mentions {found:g} for '{metric_name}', contradicting ledger value {expected:g}.",
                        }
                    )
        return violations
