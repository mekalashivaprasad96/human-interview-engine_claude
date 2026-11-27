"""Persistent Numerical Consistency Ledger — stores, locks, and validates math relationships."""

from __future__ import annotations

from typing import Any

from .models import VERIFIED_EVIDENCE_CATEGORIES, short_id


class NumericalLedger:
    """Tracks all established project/session quantities and enforces mathematical consistency."""

    def __init__(
        self,
        session_id: str,
        candidate_id: str,
        entries: list[dict[str, Any]] | None = None,
        consistency_checks: list[dict[str, Any]] | None = None,
    ) -> None:
        self.session_id = session_id
        self.candidate_id = candidate_id
        self.entries: list[dict[str, Any]] = list(entries or [])
        self.consistency_checks: list[dict[str, Any]] = list(consistency_checks or [])

    def record_metric(
        self,
        project_id: str,
        metric_name: str,
        original_value: float,
        unit: str,
        scope: str,
        measurement_period: str,
        measurement_methodology: str,
        evidence_status: str,
        baseline_value: float | None = None,
        final_value: float | None = None,
        percentage_change: float | None = None,
        derived_from: list[str] | None = None,
        formula: str = "",
        assumptions: list[str] | None = None,
        locked_at_turn: int | None = None,
    ) -> dict[str, Any]:
        """Insert or update a ledger entry for (project_id, metric_name)."""
        existing = self.get_metric(metric_name, project_id)
        if existing is not None:
            return existing

        if percentage_change is None and baseline_value is not None and final_value is not None and baseline_value != 0:
            percentage_change = round(((final_value - baseline_value) / baseline_value) * 100.0, 2)

        entry = {
            "entry_id": short_id("num", f"{project_id}:{metric_name}"),
            "project_id": project_id,
            "metric_name": metric_name,
            "original_value": float(original_value),
            "unit": unit,
            "scope": scope,
            "measurement_period": measurement_period,
            "baseline_value": float(baseline_value) if baseline_value is not None else None,
            "final_value": float(final_value) if final_value is not None else None,
            "percentage_change": float(percentage_change) if percentage_change is not None else None,
            "derived_from": list(derived_from or []),
            "formula": formula,
            "assumptions": list(assumptions or []),
            "measurement_methodology": measurement_methodology,
            "evidence_status": evidence_status,
            "locked_at_turn": locked_at_turn,
        }
        self.entries.append(entry)
        self.validate_all()
        return entry

    def get_metric(self, metric_name: str, project_id: str | None = None) -> dict[str, Any] | None:
        """Retrieve a metric entry by name and optional project_id."""
        for entry in self.entries:
            if entry["metric_name"] == metric_name and (project_id is None or entry["project_id"] == project_id):
                return entry
        return None

    def get_project_metrics(self, project_id: str) -> dict[str, dict[str, Any]]:
        """Return a mapping of metric_name -> entry for a given project."""
        return {e["metric_name"]: e for e in self.entries if e["project_id"] == project_id}

    def confirm_metric(self, entry_id: str, value: float | None = None) -> dict[str, Any] | None:
        """Promote a metric to verified_numerical_information when candidate explicitly confirms it."""
        for entry in self.entries:
            if entry["entry_id"] == entry_id:
                if value is not None:
                    entry["original_value"] = float(value)
                entry["evidence_status"] = "verified_numerical_information"
                self.validate_all()
                return entry
        return None

    def validate_all(self) -> list[dict[str, Any]]:
        """Run mathematical consistency checks across all projects in the ledger."""
        checks: list[dict[str, Any]] = []
        project_ids = sorted({e["project_id"] for e in self.entries})

        for pid in project_ids:
            m = self.get_project_metrics(pid)

            # 1. Node count * GPUs per node == total GPUs
            if {"nodes", "gpus_per_node", "total_gpus"} <= set(m):
                nodes = m["nodes"]["original_value"]
                gpn = m["gpus_per_node"]["original_value"]
                total = m["total_gpus"]["original_value"]
                expected = nodes * gpn
                passed = abs(expected - total) < 1e-6
                checks.append(
                    {
                        "rule_name": f"{pid}:node_gpu_product",
                        "passed": passed,
                        "details": f"{nodes:g} nodes * {gpn:g} GPUs/node = {expected:g} GPUs (ledger={total:g})",
                    }
                )

            # 2. Total GPUs * allocation hours == GPU-hours
            if {"total_gpus", "allocation_hours", "gpu_hours"} <= set(m):
                total = m["total_gpus"]["original_value"]
                hours = m["allocation_hours"]["original_value"]
                gpu_hours = m["gpu_hours"]["original_value"]
                expected = total * hours
                passed = abs(expected - gpu_hours) < 1e-6
                checks.append(
                    {
                        "rule_name": f"{pid}:gpu_hours_product",
                        "passed": passed,
                        "details": f"{total:g} GPUs * {hours:g} hours = {expected:g} GPU-hours (ledger={gpu_hours:g})",
                    }
                )

            # 3. Latency baseline -> final percentage improvement
            if "p99_latency_ms" in m:
                entry = m["p99_latency_ms"]
                b = entry.get("baseline_value")
                f = entry.get("final_value")
                pct = entry.get("percentage_change")
                if b and f is not None and pct is not None:
                    expected_pct = round(((f - b) / b) * 100.0, 2)
                    passed = abs(expected_pct - pct) <= 0.2
                    checks.append(
                        {
                            "rule_name": f"{pid}:p99_latency_delta",
                            "passed": passed,
                            "details": f"({f:g} - {b:g}) / {b:g} = {expected_pct}% (ledger={pct}%)",
                        }
                    )

            # 4. Throughput RPS -> daily request volume
            if {"throughput_rps", "daily_requests"} <= set(m):
                rps = m["throughput_rps"]["original_value"]
                daily = m["daily_requests"]["original_value"]
                expected = rps * 86400
                passed = abs(expected - daily) / max(1.0, expected) < 0.02
                checks.append(
                    {
                        "rule_name": f"{pid}:rps_daily_volume",
                        "passed": passed,
                        "details": f"{rps:g} RPS * 86,400 s/day = {expected:,.0f} req/day (ledger={daily:,.0f})",
                    }
                )

            # 5. Cost savings consistency
            if {"monthly_cost_savings_usd", "annual_cost_savings_usd"} <= set(m):
                mo = m["monthly_cost_savings_usd"]["original_value"]
                yr = m["annual_cost_savings_usd"]["original_value"]
                passed = abs((mo * 12.0) - yr) < 1.0
                checks.append(
                    {
                        "rule_name": f"{pid}:annual_savings",
                        "passed": passed,
                        "details": f"${mo:,.2f}/mo * 12 = ${mo*12:,.2f}/yr (ledger=${yr:,.2f})",
                    }
                )

            # 6. Availability % vs monthly downtime minutes
            if {"availability_pct", "monthly_downtime_minutes"} <= set(m):
                avail = m["availability_pct"]["original_value"]
                down = m["monthly_downtime_minutes"]["original_value"]
                expected = round((1.0 - avail / 100.0) * 43200.0, 2)
                passed = abs(expected - down) <= 1.0
                checks.append(
                    {
                        "rule_name": f"{pid}:availability_downtime",
                        "passed": passed,
                        "details": f"(1 - {avail}/100) * 43,200 min = {expected} min/mo (ledger={down} min)",
                    }
                )

        self.consistency_checks = checks
        return checks

    def verified_only_entries(self) -> list[dict[str, Any]]:
        """Return only entries classified as verified or calculated from verified sources."""
        return [e for e in self.entries if e["evidence_status"] in VERIFIED_EVIDENCE_CATEGORIES]

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "candidate_id": self.candidate_id,
            "entries": self.entries,
            "consistency_checks": self.consistency_checks,
        }
