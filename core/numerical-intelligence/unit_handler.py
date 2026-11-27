"""
Unit Handler - Handles unit validation, conversion, and appropriate precision.
"""

from dataclasses import dataclass
from typing import Optional
import re


@dataclass
class UnitInfo:
    unit: str
    base_unit: str
    dimension: str  # time, count, data, throughput, latency, percentage, currency, memory, cpu
    conversion_factor: float = 1.0
    precision: str = "appropriate"  # exact, significant_figures, one_decimal, two_decimals, appropriate_granularity


class UnitHandler:
    """Handles unit validation, conversion, and precision determination."""

    # Unit definitions with base units and dimensions
    UNITS = {
        # Count units
        "nodes": UnitInfo("nodes", "count", "count", 1.0, "exact"),
        "servers": UnitInfo("servers", "count", "count", 1.0, "exact"),
        "instances": UnitInfo("instances", "count", "count", 1.0, "exact"),
        "containers": UnitInfo("containers", "count", "count", 1.0, "exact"),
        "pods": UnitInfo("pods", "count", "count", 1.0, "exact"),
        "services": UnitInfo("services", "count", "count", 1.0, "exact"),
        "teams": UnitInfo("teams", "count", "count", 1.0, "exact"),
        "engineers": UnitInfo("engineers", "count", "count", 1.0, "exact"),
        "developers": UnitInfo("developers", "count", "count", 1.0, "exact"),
        "gpus": UnitInfo("gpus", "count", "count", 1.0, "exact"),
        "gpu_per_node": UnitInfo("gpus/node", "count", "count", 1.0, "exact"),
        "total_gpus": UnitInfo("gpus", "count", "count", 1.0, "exact"),

        # Time units
        "seconds": UnitInfo("seconds", "seconds", "time", 1.0, "appropriate_granularity"),
        "minutes": UnitInfo("minutes", "seconds", "time", 60.0, "appropriate_granularity"),
        "hours": UnitInfo("hours", "seconds", "time", 3600.0, "appropriate_granularity"),
        "days": UnitInfo("days", "seconds", "time", 86400.0, "appropriate_granularity"),
        "weeks": UnitInfo("weeks", "seconds", "time", 604800.0, "appropriate_granularity"),
        "months": UnitInfo("months", "seconds", "time", 2592000.0, "appropriate_granularity"),
        "years": UnitInfo("years", "seconds", "time", 31536000.0, "appropriate_granularity"),
        "milliseconds": UnitInfo("ms", "seconds", "time", 0.001, "one_decimal"),
        "microseconds": UnitInfo("µs", "seconds", "time", 0.000001, "one_decimal"),

        # Data units
        "bytes": UnitInfo("bytes", "bytes", "data", 1.0, "exact"),
        "kb": UnitInfo("KB", "bytes", "data", 1024.0, "one_decimal"),
        "mb": UnitInfo("MB", "bytes", "data", 1024**2, "one_decimal"),
        "gb": UnitInfo("GB", "bytes", "data", 1024**3, "one_decimal"),
        "tb": UnitInfo("TB", "bytes", "data", 1024**4, "one_decimal"),
        "pb": UnitInfo("PB", "bytes", "data", 1024**5, "one_decimal"),

        # Throughput units
        "requests_per_second": UnitInfo("req/s", "req/s", "throughput", 1.0, "appropriate_granularity"),
        "rps": UnitInfo("req/s", "req/s", "throughput", 1.0, "appropriate_granularity"),
        "transactions_per_second": UnitInfo("txn/s", "req/s", "throughput", 1.0, "appropriate_granularity"),
        "tps": UnitInfo("txn/s", "req/s", "throughput", 1.0, "appropriate_granularity"),
        "daily_requests": UnitInfo("req/day", "req/s", "throughput", 1/86400, "appropriate_granularity"),
        "monthly_requests": UnitInfo("req/month", "req/s", "throughput", 1/2592000, "appropriate_granularity"),
        "gb_per_day": UnitInfo("GB/day", "bytes/s", "throughput", 1024**3/86400, "one_decimal"),
        "tb_per_day": UnitInfo("TB/day", "bytes/s", "throughput", 1024**4/86400, "one_decimal"),

        # Latency units
        "milliseconds": UnitInfo("ms", "ms", "latency", 1.0, "one_decimal"),
        "ms": UnitInfo("ms", "ms", "latency", 1.0, "one_decimal"),
        "seconds": UnitInfo("s", "ms", "latency", 1000.0, "one_decimal"),

        # Percentage units
        "percent": UnitInfo("%", "%", "percentage", 1.0, "one_decimal"),
        "percentage": UnitInfo("%", "%", "percentage", 1.0, "one_decimal"),
        "pct": UnitInfo("%", "%", "percentage", 1.0, "one_decimal"),

        # Currency units
        "usd": UnitInfo("USD", "USD", "currency", 1.0, "two_decimals"),
        "dollars": UnitInfo("USD", "USD", "currency", 1.0, "two_decimals"),
        "usd_per_month": UnitInfo("USD/month", "USD", "currency", 1.0, "two_decimals"),
        "usd_per_request": UnitInfo("USD/req", "USD", "currency", 1.0, "six_decimals"),
        "cost_per_request": UnitInfo("USD/req", "USD", "currency", 1.0, "six_decimals"),

        # Memory units
        "gb": UnitInfo("GB", "GB", "memory", 1.0, "exact"),
        "memory_gb": UnitInfo("GB", "GB", "memory", 1.0, "exact"),

        # CPU units
        "cpu_cores": UnitInfo("cores", "cores", "cpu", 1.0, "exact"),
        "cpus_per_node": UnitInfo("cores", "cores", "cpu", 1.0, "exact"),

        # GPU hours
        "gpu_hours": UnitInfo("GPU-hours", "GPU-hours", "compute", 1.0, "one_decimal"),
        "gpu_hour": UnitInfo("GPU-hours", "GPU-hours", "compute", 1.0, "one_decimal"),

        # Availability
        "availability_pct": UnitInfo("%", "%", "percentage", 1.0, "two_decimals"),
        "downtime_minutes_per_month": UnitInfo("min/month", "min", "time", 1.0, "one_decimal"),
        "mttr_minutes": UnitInfo("minutes", "min", "time", 1.0, "one_decimal"),

        # Team metrics
        "deploys_per_week": UnitInfo("deploys/week", "count/time", "frequency", 1.0, "one_decimal"),
        "lead_time_hours": UnitInfo("hours", "hours", "time", 1.0, "one_decimal"),
        "on_call_rotation": UnitInfo("people", "count", "count", 1.0, "exact"),
    }

    # Aliases for common variations
    ALIASES = {
        "req/s": "requests_per_second",
        "rps": "requests_per_second",
        "txn/s": "transactions_per_second",
        "tps": "transactions_per_second",
        "gpus/node": "gpu_per_node",
        "gb": "gb",
        "tb": "tb",
        "ms": "milliseconds",
        "%": "percent",
        "pct": "percent",
        "usd": "usd",
        "$": "usd",
    }

    def __init__(self):
        pass

    def normalize_unit(self, unit: str) -> str:
        """Normalize unit to canonical form."""
        unit_lower = unit.lower().strip()
        return self.ALIASES.get(unit_lower, unit_lower)

    def get_unit_info(self, unit: str) -> Optional[UnitInfo]:
        """Get unit information."""
        normalized = self.normalize_unit(unit)
        return self.UNITS.get(normalized)

    def validate_unit(self, quantity: str, unit: str) -> tuple[bool, str]:
        """Validate if unit is appropriate for quantity."""
        quantity_lower = quantity.lower()
        unit_info = self.get_unit_info(unit)

        if not unit_info:
            return False, f"Unknown unit: {unit}"

        # Check dimension compatibility
        quantity_dimensions = {
            "node": "count", "server": "count", "instance": "count", "container": "count",
            "pod": "count", "service": "count", "team": "count", "engineer": "count",
            "developer": "count", "gpu": "count",
            "time": "time", "duration": "time", "latency": "latency", "response": "latency",
            "hour": "time", "minute": "time", "second": "time", "day": "time", "week": "time",
            "throughput": "throughput", "rps": "throughput", "tps": "throughput",
            "request": "throughput", "transaction": "throughput",
            "data": "data", "volume": "data", "storage": "data",
            "memory": "memory", "ram": "memory",
            "cpu": "cpu", "core": "cpu",
            "percent": "percentage", "percentage": "percentage", "change": "percentage", "improvement": "percentage",
            "availability": "percentage", "downtime": "time",
            "cost": "currency", "price": "currency", "budget": "currency",
            "deploy": "frequency", "lead": "time",
            "compute": "compute", "gpu_hour": "compute",
        }

        expected_dimension = None
        for key, dim in quantity_dimensions.items():
            if key in quantity_lower:
                expected_dimension = dim
                break

        if expected_dimension and unit_info.dimension != expected_dimension:
            # Special cases where cross-dimension is valid
            valid_cross = {
                ("time", "latency"),  # ms is time but used for latency
                ("throughput", "count"),  # requests can be count
                ("count", "time"),  # gpu-hours is compute but involves time
            }
            if (unit_info.dimension, expected_dimension) not in valid_cross and \
               (expected_dimension, unit_info.dimension) not in valid_cross:
                return False, f"Unit {unit} (dimension: {unit_info.dimension}) not appropriate for {quantity} (expected: {expected_dimension})"

        return True, "Valid"

    def convert(self, value: float, from_unit: str, to_unit: str) -> Optional[float]:
        """Convert value between compatible units."""
        from_info = self.get_unit_info(from_unit)
        to_info = self.get_unit_info(to_unit)

        if not from_info or not to_info:
            return None

        if from_info.dimension != to_info.dimension:
            return None  # Incompatible dimensions

        # Convert to base unit, then to target
        base_value = value * from_info.conversion_factor
        target_value = base_value / to_info.conversion_factor

        return target_value

    def format_value(self, value: float, unit: str, precision: str = None) -> str:
        """Format value with appropriate precision for unit."""
        unit_info = self.get_unit_info(unit)
        if not unit_info:
            return f"{value} {unit}"

        precision = precision or unit_info.precision

        if precision == "exact":
            if value == int(value):
                return f"{int(value):,} {unit}"
            return f"{value:,.0f} {unit}"
        elif precision == "significant_figures":
            return f"{value:.3g} {unit}"
        elif precision == "one_decimal":
            return f"{value:,.1f} {unit}"
        elif precision == "two_decimals":
            return f"{value:,.2f} {unit}"
        elif precision == "six_decimals":
            return f"{value:.6f} {unit}"
        elif precision == "appropriate_granularity":
            # Choose based on magnitude
            abs_val = abs(value)
            if abs_val >= 1_000_000:
                return f"{value/1_000_000:.1f}M {unit}"
            elif abs_val >= 1_000:
                return f"{value/1_000:.1f}K {unit}"
            elif abs_val >= 100:
                return f"{value:,.0f} {unit}"
            elif abs_val >= 10:
                return f"{value:,.1f} {unit}"
            elif abs_val >= 1:
                return f"{value:,.2f} {unit}"
            else:
                return f"{value:.3f} {unit}"
        else:
            return f"{value} {unit}"

    def parse_value_with_unit(self, text: str) -> Optional[tuple[float, str]]:
        """Parse a value with unit from text (e.g., '500ms', '10K rps', '$2.5M')."""
        # Patterns for value + unit
        patterns = [
            # Currency
            r'\$([\d,]+\.?\d*)\s*([kmbt])?',
            r'([\d,]+\.?\d*)\s*(usd|dollars?)',
            # With units
            r'([\d,]+\.?\d*)\s*(ms|milliseconds?|seconds?|s\b|minutes?|mins?|hours?|hrs?|days?|weeks?|months?|years?)',
            r'([\d,]+\.?\d*)\s*(kb|mb|gb|tb|pb)',
            r'([\d,]+\.?\d*)\s*(rps|req/s|tps|txn/s|requests?/second|transactions?/second)',
            r'([\d,]+\.?\d*)\s*(%|percent|pct)',
            r'([\d,]+\.?\d*)\s*(nodes?|servers?|instances?|containers?|pods?|services?|teams?|engineers?|developers?|gpus?)',
            r'([\d,]+\.?\d*)\s*(gpu.hours?|gpu_hours?)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                value_str = match.group(1).replace(',', '')
                try:
                    value = float(value_str)
                except ValueError:
                    continue

                # Handle K/M/B/T multipliers
                if len(match.groups()) >= 2 and match.group(2):
                    multiplier = match.group(2).lower()
                    multipliers = {'k': 1_000, 'm': 1_000_000, 'b': 1_000_000_000, 't': 1_000_000_000_000}
                    if multiplier in multipliers:
                        value *= multipliers[multiplier]

                unit = match.group(2) if len(match.groups()) >= 2 else ""
                if not unit and len(match.groups()) >= 3:
                    unit = match.group(3)

                return value, unit

        return None

    def suggest_appropriate_unit(self, quantity: str, value: float) -> str:
        """Suggest the most appropriate unit for a quantity given its value."""
        quantity_lower = quantity.lower()

        # For large counts, use K/M suffixes in display but base unit in storage
        if any(k in quantity_lower for k in ['request', 'transaction', 'user', 'event']):
            if value >= 1_000_000:
                return "requests_per_second"  # Store as RPS, display as M RPS
            elif value >= 1_000:
                return "requests_per_second"

        # For data volumes
        if any(k in quantity_lower for k in ['data', 'volume', 'storage', 'traffic']):
            if value >= 1024**4:
                return "tb"
            elif value >= 1024**3:
                return "gb"

        # For latency
        if 'latency' in quantity_lower or 'response' in quantity_lower:
            if value >= 1000:
                return "seconds"
            return "milliseconds"

        # For time durations
        if any(k in quantity_lower for k in ['duration', 'time', 'hour', 'uptime', 'downtime', 'mttr']):
            if value >= 86400:
                return "days"
            elif value >= 3600:
                return "hours"
            elif value >= 60:
                return "minutes"
            return "seconds"

        return self.normalize_unit(quantity_lower)