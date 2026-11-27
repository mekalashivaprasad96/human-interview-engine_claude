"""
Consistency Validator - Validates mathematical relationships and consistency across numerical data.
"""

from dataclasses import dataclass
from typing import Optional
from .ledger import NumericalLedger, LedgerEntry


@dataclass
class ValidationResult:
    check_name: str
    passed: bool
    message: str
    severity: str  # error, warning, info
    involved_entries: list
    expected: Optional[float] = None
    actual: Optional[float] = None


class ConsistencyValidator:
    """Validates numerical consistency across ledger entries and project models."""

    def __init__(self, ledger: NumericalLedger):
        self.ledger = ledger
        self.checks = [
            self._check_node_gpu_consistency,
            self._check_gpu_hour_calculation,
            self._check_baseline_final_relationship,
            self._check_percentage_change_derivation,
            self._check_availability_downtime_alignment,
            self._check_throughput_consistency,
            self._check_latency_improvement_consistency,
            self._check_cost_per_request,
            self._check_team_size_ownership_alignment,
            self._check_scale_consistency,
        ]

    def run_all_checks(self) -> list[ValidationResult]:
        """Run all consistency checks."""
        results = []
        for check in self.checks:
            try:
                result = check()
                results.append(result)
            except Exception as e:
                results.append(ValidationResult(
                    check_name=check.__name__,
                    passed=False,
                    message=f"Check failed with error: {str(e)}",
                    severity="error",
                    involved_entries=[],
                ))
        return results

    def _check_node_gpu_consistency(self) -> ValidationResult:
        """Check: nodes × gpus_per_node = total_gpus"""
        nodes_entry = self._find_entry("node", "count")
        gpu_per_node_entry = self._find_entry("gpu", "per_node")
        total_gpu_entry = self._find_entry("total_gpu", "")

        if nodes_entry and gpu_per_node_entry and total_gpu_entry:
            expected = nodes_entry.value * gpu_per_node_entry.value
            actual = total_gpu_entry.value
            passed = abs(expected - actual) < 0.001

            return ValidationResult(
                check_name="node_gpu_multiplication",
                passed=passed,
                message=f"Nodes ({nodes_entry.value}) × GPUs/node ({gpu_per_node_entry.value}) = {expected}, recorded total_gpus = {actual}",
                severity="error" if not passed else "info",
                involved_entries=[nodes_entry.id, gpu_per_node_entry.id, total_gpu_entry.id],
                expected=expected,
                actual=actual,
            )

        return ValidationResult(
            check_name="node_gpu_multiplication",
            passed=True,
            message="Insufficient data to validate",
            severity="info",
            involved_entries=[],
        )

    def _check_gpu_hour_calculation(self) -> ValidationResult:
        """Check: total_gpus × hours = gpu_hours"""
        total_gpu_entry = self._find_entry("total_gpu", "")
        hours_entry = self._find_entry("hour", "duration")
        gpu_hours_entry = self._find_entry("gpu_hour", "")

        if total_gpu_entry and hours_entry and gpu_hours_entry:
            expected = total_gpu_entry.value * hours_entry.value
            actual = gpu_hours_entry.value
            passed = abs(expected - actual) < 0.01 * max(expected, actual)

            return ValidationResult(
                check_name="gpu_hour_calculation",
                passed=passed,
                message=f"Total GPUs ({total_gpu_entry.value}) × Hours ({hours_entry.value}) = {expected:.0f}, recorded GPU-hours = {actual:.0f}",
                severity="error" if not passed else "info",
                involved_entries=[total_gpu_entry.id, hours_entry.id, gpu_hours_entry.id],
                expected=expected,
                actual=actual,
            )

        return ValidationResult(
            check_name="gpu_hour_calculation",
            passed=True,
            message="Insufficient data to validate",
            severity="info",
            involved_entries=[],
        )

    def _check_baseline_final_relationship(self) -> ValidationResult:
        """Check: baseline and final measurements are logically consistent"""
        baseline_entries = [e for e in self.ledger.entries.values() if e.baseline]
        final_entries = [e for e in self.ledger.entries.values() if not e.baseline and e.quantity in [b.quantity for b in baseline_entries]]

        issues = []
        for baseline in baseline_entries:
            for final in final_entries:
                if baseline.quantity == final.quantity and baseline.scope == final.scope:
                    # Check logical relationship based on quantity type
                    if "latency" in baseline.quantity.lower() or "response_time" in baseline.quantity.lower():
                        # Latency should improve (decrease) or stay same
                        if final.value > baseline.value * 1.5:  # Allow some variance
                            issues.append(f"{baseline.quantity}: baseline {baseline.value} → final {final.value} (unexpected increase)")
                    elif "throughput" in baseline.quantity.lower() or "rps" in baseline.quantity.lower():
                        # Throughput should improve (increase) or stay same
                        if final.value < baseline.value * 0.5:
                            issues.append(f"{baseline.quantity}: baseline {baseline.value} → final {final.value} (unexpected decrease)")
                    elif "cost" in baseline.quantity.lower():
                        # Cost should decrease or stay same
                        if final.value > baseline.value * 1.2:
                            issues.append(f"{baseline.quantity}: baseline {baseline.value} → final {final.value} (unexpected increase)")
                    elif "availability" in baseline.quantity.lower():
                        # Availability should improve or stay same
                        if final.value < baseline.value - 0.1:
                            issues.append(f"{baseline.quantity}: baseline {baseline.value}% → final {final.value}% (unexpected decrease)")

        passed = len(issues) == 0
        return ValidationResult(
            check_name="baseline_final_relationship",
            passed=passed,
            message="; ".join(issues) if issues else "All baseline-final relationships consistent",
            severity="warning" if not passed else "info",
            involved_entries=[e.id for e in baseline_entries + final_entries],
        )

    def _check_percentage_change_derivation(self) -> ValidationResult:
        """Check: percentage changes derive correctly from baseline and final"""
        pct_entries = [e for e in self.ledger.entries.values() if "percent" in e.unit.lower() or "%" in e.unit or "change" in e.quantity.lower() or "improvement" in e.quantity.lower()]

        issues = []
        for pct_entry in pct_entries:
            # Find corresponding baseline and final
            baseline = next((e for e in self.ledger.entries.values()
                           if e.baseline and e.quantity == pct_entry.quantity.replace("percent_", "").replace("change_", "").replace("improvement_", "")
                           and e.scope == pct_entry.scope), None)
            final = next((e for e in self.ledger.entries.values()
                         if not e.baseline and e.quantity == pct_entry.quantity.replace("percent_", "").replace("change_", "").replace("improvement_", "")
                         and e.scope == pct_entry.scope), None)

            if baseline and final and baseline.value != 0:
                expected_pct = ((final.value - baseline.value) / baseline.value) * 100
                actual_pct = pct_entry.value
                if abs(expected_pct - actual_pct) > 1.0:  # Allow 1% tolerance
                    issues.append(f"{pct_entry.quantity}: expected {expected_pct:.1f}%, got {actual_pct:.1f}%")

        passed = len(issues) == 0
        return ValidationResult(
            check_name="percentage_change_derivation",
            passed=passed,
            message="; ".join(issues) if issues else "All percentage changes correctly derived",
            severity="error" if not passed else "info",
            involved_entries=[e.id for e in pct_entries],
        )

    def _check_availability_downtime_alignment(self) -> ValidationResult:
        """Check: availability % and downtime minutes align"""
        avail_entry = self._find_entry("availability", "pct")
        downtime_entry = self._find_entry("downtime", "minutes")

        if avail_entry and downtime_entry:
            expected_downtime = (100 - avail_entry.value) / 100 * 43200  # minutes per 30-day month
            actual_downtime = downtime_entry.value
            passed = abs(expected_downtime - actual_downtime) < 10  # 10 minute tolerance

            return ValidationResult(
                check_name="availability_downtime_alignment",
                passed=passed,
                message=f"Availability {avail_entry.value}% → expected downtime {expected_downtime:.1f} min/month, recorded {actual_downtime:.1f} min/month",
                severity="error" if not passed else "info",
                involved_entries=[avail_entry.id, downtime_entry.id],
                expected=expected_downtime,
                actual=actual_downtime,
            )

        return ValidationResult(
            check_name="availability_downtime_alignment",
            passed=True,
            message="Insufficient data to validate",
            severity="info",
            involved_entries=[],
        )

    def _check_throughput_consistency(self) -> ValidationResult:
        """Check: RPS × seconds = daily requests (roughly)"""
        rps_entry = self._find_entry("request", "second")
        daily_entry = self._find_entry("daily_request", "")

        if rps_entry and daily_entry:
            expected_daily = rps_entry.value * 86400 * 0.3  # 30% average utilization
            actual_daily = daily_entry.value
            ratio = actual_daily / expected_daily if expected_daily > 0 else 0
            passed = 0.1 <= ratio <= 10  # Within order of magnitude

            return ValidationResult(
                check_name="throughput_consistency",
                passed=passed,
                message=f"RPS {rps_entry.value:,.0f} × 86400 × 0.3 = {expected_daily:,.0f} daily, recorded {actual_daily:,.0f} (ratio: {ratio:.1f}x)",
                severity="warning" if not passed else "info",
                involved_entries=[rps_entry.id, daily_entry.id],
                expected=expected_daily,
                actual=actual_daily,
            )

        return ValidationResult(
            check_name="throughput_consistency",
            passed=True,
            message="Insufficient data to validate",
            severity="info",
            involved_entries=[],
        )

    def _check_latency_improvement_consistency(self) -> ValidationResult:
        """Check: latency improvements are plausible"""
        baseline_latency = self._find_entry("latency", "baseline")
        final_latency = self._find_entry("latency", "final")
        improvement_entry = self._find_entry("latency_improvement", "pct")

        if baseline_latency and final_latency and improvement_entry:
            expected_improvement = ((baseline_latency.value - final_latency.value) / baseline_latency.value) * 100
            actual_improvement = improvement_entry.value
            passed = abs(expected_improvement - actual_improvement) < 5  # 5% tolerance

            return ValidationResult(
                check_name="latency_improvement_consistency",
                passed=passed,
                message=f"Latency {baseline_latency.value}ms → {final_latency.value}ms = {expected_improvement:.1f}% improvement, recorded {actual_improvement:.1f}%",
                severity="error" if not passed else "info",
                involved_entries=[baseline_latency.id, final_latency.id, improvement_entry.id],
                expected=expected_improvement,
                actual=actual_improvement,
            )

        return ValidationResult(
            check_name="latency_improvement_consistency",
            passed=True,
            message="Insufficient data to validate",
            severity="info",
            involved_entries=[],
        )

    def _check_cost_per_request(self) -> ValidationResult:
        """Check: monthly_cost / monthly_requests = cost_per_request"""
        cost_entry = self._find_entry("monthly_cost", "usd")
        request_entry = self._find_entry("monthly_request", "")
        cost_per_req_entry = self._find_entry("cost_per_request", "usd")

        if cost_entry and request_entry and cost_per_req_entry and request_entry.value > 0:
            expected = cost_entry.value / request_entry.value
            actual = cost_per_req_entry.value
            passed = abs(expected - actual) < 0.0001

            return ValidationResult(
                check_name="cost_per_request",
                passed=passed,
                message=f"${cost_entry.value:,.2f} / {request_entry.value:,.0f} = ${expected:.6f}/req, recorded ${actual:.6f}/req",
                severity="error" if not passed else "info",
                involved_entries=[cost_entry.id, request_entry.id, cost_per_req_entry.id],
                expected=expected,
                actual=actual,
            )

        return ValidationResult(
            check_name="cost_per_request",
            passed=True,
            message="Insufficient data to validate",
            severity="info",
            involved_entries=[],
        )

    def _check_team_size_ownership_alignment(self) -> ValidationResult:
        """Check: team size aligns with ownership claims"""
        team_entry = self._find_entry("team", "size")
        # Would need to cross-reference with scenario data in practice
        # This is a placeholder for the concept

        if team_entry:
            return ValidationResult(
                check_name="team_size_ownership_alignment",
                passed=True,
                message=f"Team size recorded: {team_entry.value}",
                severity="info",
                involved_entries=[team_entry.id],
            )

        return ValidationResult(
            check_name="team_size_ownership_alignment",
            passed=True,
            message="No team size data",
            severity="info",
            involved_entries=[],
        )

    def _check_scale_consistency(self) -> ValidationResult:
        """Check: scale metrics are internally consistent"""
        # Check that services count aligns with team size
        services_entry = self._find_entry("service", "count")
        team_entry = self._find_entry("team", "size")

        if services_entry and team_entry:
            ratio = services_entry.value / team_entry.value
            # Typical ratio: 2-5 services per engineer
            passed = 0.5 <= ratio <= 10

            return ValidationResult(
                check_name="scale_consistency",
                passed=passed,
                message=f"{services_entry.value:.0f} services / {team_entry.value:.0f} engineers = {ratio:.1f} services/engineer",
                severity="warning" if not passed else "info",
                involved_entries=[services_entry.id, team_entry.id],
            )

        return ValidationResult(
            check_name="scale_consistency",
            passed=True,
            message="Insufficient data to validate",
            severity="info",
            involved_entries=[],
        )

    def _find_entry(self, quantity_keyword: str, qualifier: str) -> Optional[LedgerEntry]:
        """Find ledger entry matching keywords."""
        for entry in self.ledger.entries.values():
            q_lower = entry.quantity.lower()
            if quantity_keyword in q_lower:
                if not qualifier or qualifier in q_lower:
                    return entry
        return None

    def validate_project_model(self, project_model) -> list[ValidationResult]:
        """Validate a project model's numerical consistency."""
        results = []

        # Check numerical model internal consistency
        num_model = project_model.numerical_model

        # Compute consistency
        compute = num_model.get('compute', {})
        if compute.get('nodes') and compute.get('gpus_per_node') and compute.get('total_gpus'):
            expected = compute['nodes'] * compute['gpus_per_node']
            actual = compute['total_gpus']
            results.append(ValidationResult(
                check_name="project_compute_gpu_consistency",
                passed=abs(expected - actual) < 0.001,
                message=f"Nodes × GPUs/node = {expected}, total_gpus = {actual}",
                severity="error" if expected != actual else "info",
                involved_entries=[],
                expected=expected,
                actual=actual,
            ))

        # Throughput consistency
        throughput = num_model.get('throughput', {})
        if throughput.get('requests_per_second') and throughput.get('daily_requests'):
            expected_daily = throughput['requests_per_second'] * 86400 * 0.3
            actual_daily = throughput['daily_requests']
            ratio = actual_daily / expected_daily if expected_daily > 0 else 0
            results.append(ValidationResult(
                check_name="project_throughput_consistency",
                passed=0.1 <= ratio <= 10,
                message=f"RPS implies {expected_daily:,.0f} daily, model has {actual_daily:,.0f}",
                severity="warning" if not (0.1 <= ratio <= 10) else "info",
                involved_entries=[],
                expected=expected_daily,
                actual=actual_daily,
            ))

        # Availability consistency
        avail = num_model.get('availability', {})
        if avail.get('target_pct') and avail.get('downtime_minutes_per_month'):
            expected_downtime = (100 - avail['target_pct']) / 100 * 43200
            actual_downtime = avail['downtime_minutes_per_month']
            results.append(ValidationResult(
                check_name="project_availability_consistency",
                passed=abs(expected_downtime - actual_downtime) < 10,
                message=f"Target {avail['target_pct']}% → {expected_downtime:.1f} min downtime, model has {actual_downtime:.1f}",
                severity="error" if abs(expected_downtime - actual_downtime) >= 10 else "info",
                involved_entries=[],
                expected=expected_downtime,
                actual=actual_downtime,
            ))

        # Latency consistency
        latency = num_model.get('latency', {})
        if latency.get('baseline_p50_ms') and latency.get('p50_ms') and latency.get('improvement_pct'):
            expected_improvement = ((latency['baseline_p50_ms'] - latency['p50_ms']) / latency['baseline_p50_ms']) * 100
            actual_improvement = latency['improvement_pct']
            results.append(ValidationResult(
                check_name="project_latency_consistency",
                passed=abs(expected_improvement - actual_improvement) < 5,
                message=f"Baseline {latency['baseline_p50_ms']}ms → {latency['p50_ms']}ms = {expected_improvement:.1f}%, model has {actual_improvement:.1f}%",
                severity="error" if abs(expected_improvement - actual_improvement) >= 5 else "info",
                involved_entries=[],
                expected=expected_improvement,
                actual=actual_improvement,
            ))

        return results