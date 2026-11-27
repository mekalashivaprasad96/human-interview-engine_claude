"""
Numerical Calculator - Performs calculations and derivations from ledger entries.
"""

from dataclasses import dataclass
from typing import Optional
from .ledger import NumericalLedger, LedgerEntry


@dataclass
class CalculationResult:
    value: float
    unit: str
    formula: str
    inputs: list
    confidence: float
    assumptions: list


class NumericalCalculator:
    """Performs numerical calculations with proper unit handling and validation."""

    def __init__(self, ledger: NumericalLedger):
        self.ledger = ledger

    def calculate_gpu_hours(self, nodes: int, gpus_per_node: int, hours: float) -> CalculationResult:
        """Calculate total GPU-hours."""
        total_gpus = nodes * gpus_per_node
        gpu_hours = total_gpus * hours

        # Record in ledger
        self.ledger.add_entry(
            quantity="total_gpus",
            value=total_gpus,
            unit="gpus",
            calculation_method="nodes * gpus_per_node",
            derived_from=[]
        )
        self.ledger.add_entry(
            quantity="gpu_hours",
            value=gpu_hours,
            unit="gpu_hours",
            calculation_method="total_gpus * hours",
            derived_from=[]
        )

        return CalculationResult(
            value=gpu_hours,
            unit="gpu_hours",
            formula=f"{nodes} nodes × {gpus_per_node} GPUs/node × {hours} hours",
            inputs=[{"nodes": nodes}, {"gpus_per_node": gpus_per_node}, {"hours": hours}],
            confidence=1.0,
            assumptions=["All GPUs allocated for full duration"]
        )

    def calculate_throughput(self, requests: int, duration_seconds: float) -> CalculationResult:
        """Calculate requests per second."""
        rps = requests / duration_seconds if duration_seconds > 0 else 0

        return CalculationResult(
            value=rps,
            unit="requests/second",
            formula=f"{requests:,} requests / {duration_seconds}s",
            inputs=[{"requests": requests}, {"duration_seconds": duration_seconds}],
            confidence=0.9,
            assumptions=["Uniform request distribution"]
        )

    def calculate_latency_improvement(self, baseline_ms: float, final_ms: float) -> CalculationResult:
        """Calculate latency improvement percentage."""
        if baseline_ms <= 0:
            return CalculationResult(0, "%", "", [], 0, ["Invalid baseline"])

        improvement = ((baseline_ms - final_ms) / baseline_ms) * 100

        return CalculationResult(
            value=round(improvement, 1),
            unit="%",
            formula=f"({baseline_ms} - {final_ms}) / {baseline_ms} × 100",
            inputs=[{"baseline_ms": baseline_ms}, {"final_ms": final_ms}],
            confidence=1.0,
            assumptions=["Same measurement methodology", "Same load conditions"]
        )

    def calculate_availability_downtime(self, availability_pct: float) -> CalculationResult:
        """Calculate downtime from availability percentage."""
        minutes_per_month = 43200  # 30 days * 24 hours * 60 minutes
        downtime = (100 - availability_pct) / 100 * minutes_per_month

        return CalculationResult(
            value=round(downtime, 1),
            unit="minutes/month",
            formula=f"(100 - {availability_pct}) / 100 × 43,200",
            inputs=[{"availability_pct": availability_pct}],
            confidence=1.0,
            assumptions=["30-day month", "Continuous operation"]
        )

    def calculate_cost_per_request(self, monthly_cost_usd: float, monthly_requests: int) -> CalculationResult:
        """Calculate cost per request."""
        if monthly_requests <= 0:
            return CalculationResult(0, "USD/request", "", [], 0, ["Invalid request count"])

        cost = monthly_cost_usd / monthly_requests

        return CalculationResult(
            value=cost,
            unit="USD/request",
            formula=f"${monthly_cost_usd:,.2f} / {monthly_requests:,} requests",
            inputs=[{"monthly_cost_usd": monthly_cost_usd}, {"monthly_requests": monthly_requests}],
            confidence=0.9,
            assumptions=["Stable monthly traffic", "All costs attributed to requests"]
        )

    def calculate_percentage_change(self, baseline: float, final: float) -> CalculationResult:
        """Calculate percentage change with direction."""
        if baseline == 0:
            return CalculationResult(0, "%", "", [], 0, ["Zero baseline"])

        change = ((final - baseline) / baseline) * 100
        direction = "increase" if change > 0 else "decrease"

        return CalculationResult(
            value=round(abs(change), 1),
            unit="%",
            formula=f"({final} - {baseline}) / {baseline} × 100 = {change:+.1f}% ({direction})",
            inputs=[{"baseline": baseline}, {"final": final}],
            confidence=1.0,
            assumptions=["Same measurement context"]
        )

    def calculate_compound_growth(self, initial: float, rate: float, periods: int) -> CalculationResult:
        """Calculate compound growth."""
        final = initial * (1 + rate) ** periods
        total_growth = ((final - initial) / initial) * 100

        return CalculationResult(
            value=round(final, 2),
            unit="absolute",
            formula=f"{initial} × (1 + {rate})^{periods} = {final:.2f}",
            inputs=[{"initial": initial}, {"rate": rate}, {"periods": periods}],
            confidence=0.95,
            assumptions=["Constant growth rate", "Compounding per period"]
        )

    def calculate_team_capacity(self, team_size: int, focus_factor: float = 0.6,
                                 hours_per_week: int = 40, weeks: int = 4) -> CalculationResult:
        """Calculate team capacity in person-hours."""
        capacity = team_size * focus_factor * hours_per_week * weeks

        return CalculationResult(
            value=capacity,
            unit="person-hours/month",
            formula=f"{team_size} people × {focus_factor} focus × {hours_per_week}h/week × {weeks} weeks",
            inputs=[{"team_size": team_size}, {"focus_factor": focus_factor}],
            confidence=0.8,
            assumptions=["Consistent team size", "Standard focus factor", "No major holidays"]
        )

    def calculate_mttr(self, total_downtime_minutes: float, incident_count: int) -> CalculationResult:
        """Calculate Mean Time To Recovery."""
        if incident_count <= 0:
            return CalculationResult(0, "minutes", "", [], 0, ["No incidents"])

        mttr = total_downtime_minutes / incident_count

        return CalculationResult(
            value=round(mttr, 1),
            unit="minutes",
            formula=f"{total_downtime_minutes} min / {incident_count} incidents",
            inputs=[{"total_downtime": total_downtime_minutes}, {"incidents": incident_count}],
            confidence=0.9,
            assumptions=["Equal weight per incident", "Accurate downtime tracking"]
        )

    def calculate_error_budget(self, availability_target: float, period_days: int = 30) -> CalculationResult:
        """Calculate error budget in minutes."""
        minutes = period_days * 24 * 60
        budget = minutes * (1 - availability_target / 100)

        return CalculationResult(
            value=round(budget, 1),
            unit="minutes",
            formula=f"{minutes} min × (1 - {availability_target}/100)",
            inputs=[{"availability_target": availability_target}, {"period_days": period_days}],
            confidence=1.0,
            assumptions=["Constant error rate", "No planned maintenance"]
        )

    def calculate_scaling_factor(self, current_rps: float, target_rps: float,
                                  current_resources: int) -> CalculationResult:
        """Calculate required scaling factor and resources."""
        if current_rps <= 0:
            return CalculationResult(0, "x", "", [], 0, ["Invalid current RPS"])

        factor = target_rps / current_rps
        required_resources = int(current_resources * factor * 1.2)  # 20% headroom

        return CalculationResult(
            value=round(factor, 2),
            unit="x",
            formula=f"{target_rps} / {current_rps} = {factor:.2f}x → {required_resources} resources (with 20% headroom)",
            inputs=[{"current_rps": current_rps}, {"target_rps": target_rps}, {"current_resources": current_resources}],
            confidence=0.85,
            assumptions=["Linear scaling", "Same architecture", "No new bottlenecks"]
        )

    def estimate_infrastructure_cost(self, nodes: int, instance_type: str = "m5.xlarge",
                                      hours_per_month: int = 730) -> CalculationResult:
        """Estimate infrastructure cost (rough approximations)."""
        # Rough hourly rates (USD) - would be configurable in production
        rates = {
            "m5.xlarge": 0.192,
            "m5.2xlarge": 0.384,
            "m5.4xlarge": 0.768,
            "r5.xlarge": 0.252,
            "r5.2xlarge": 0.504,
            "c5.xlarge": 0.17,
            "c5.2xlarge": 0.34,
            "p3.2xlarge": 3.06,  # GPU
            "g4dn.xlarge": 0.526,  # GPU
        }

        hourly_rate = rates.get(instance_type, 0.20)
        monthly = nodes * hourly_rate * hours_per_month

        return CalculationResult(
            value=round(monthly, 2),
            unit="USD/month",
            formula=f"{nodes} × ${hourly_rate:.3f}/hr × {hours_per_month} hrs",
            inputs=[{"nodes": nodes}, {"instance_type": instance_type}],
            confidence=0.7,
            assumptions=["On-demand pricing", "100% utilization", "No reserved instances", "US-East-1 pricing"]
        )

    def derive_from_ledger(self, target_quantity: str) -> Optional[CalculationResult]:
        """Attempt to derive a quantity from existing ledger entries."""
        entries = self.ledger.entries

        # Common derivations
        if target_quantity == "total_gpus":
            nodes_entry = next((e for e in entries.values() if "node" in e.quantity.lower() and "count" in e.quantity.lower()), None)
            gpu_entry = next((e for e in entries.values() if "gpu" in e.quantity.lower() and "per" in e.quantity.lower()), None)
            if nodes_entry and gpu_entry:
                return self.calculate_gpu_hours(int(nodes_entry.value), int(gpu_entry.value), 1)

        if target_quantity == "gpu_hours":
            total_gpu_entry = next((e for e in entries.values() if e.quantity.lower() == "total_gpus"), None)
            hours_entry = next((e for e in entries.values() if "hour" in e.quantity.lower() and "duration" in e.quantity.lower()), None)
            if total_gpu_entry and hours_entry:
                return self.calculate_gpu_hours(1, int(total_gpu_entry.value), hours_entry.value)

        if target_quantity == "daily_requests":
            rps_entry = next((e for e in entries.values() if "request" in e.quantity.lower() and "second" in e.unit.lower()), None)
            if rps_entry:
                return self.calculate_throughput(int(rps_entry.value * 86400 * 0.3), 86400)

        return None