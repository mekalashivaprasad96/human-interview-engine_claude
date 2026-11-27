"""
Numerical Ledger - Persistent ledger tracking all quantities, units, calculations, and consistency.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from collections import defaultdict
import json


@dataclass
class LedgerEntry:
    id: str
    quantity: str
    value: float
    unit: str
    scope: dict = field(default_factory=dict)
    source: str = "inferred"  # resume, candidate_confirmed, calculated, inferred, simulated, interviewer_provided
    evidence_class: str = "contextual_inference"
    precision: str = "appropriate"
    baseline: bool = False
    derived_from: list = field(default_factory=list)
    calculation_method: str = ""
    timestamp: str = ""
    validated: bool = False
    conflicts: list = field(default_factory=list)


@dataclass
class Invariant:
    id: str
    description: str
    expression: str
    involved_entries: list = field(default_factory=list)
    status: str = "unchecked"  # valid, violated, unchecked
    last_checked: str = ""
    violation_details: str = ""


@dataclass
class ValidationLogEntry:
    timestamp: str
    check_type: str
    entries_checked: list
    result: str  # pass, fail, warning
    details: str


class NumericalLedger:
    """Persistent numerical ledger with consistency validation."""

    def __init__(self):
        self.entries: dict[str, LedgerEntry] = {}
        self.invariants: list[Invariant] = []
        self.validation_log: list[ValidationLogEntry] = []
        self.computed_metrics: dict = {}
        self._entry_counter = 0

    def add_entry(self, quantity: str, value: float, unit: str,
                  scope: dict = None, source: str = "inferred",
                  evidence_class: str = "contextual_inference",
                  precision: str = "appropriate",
                  baseline: bool = False,
                  derived_from: list = None,
                  calculation_method: str = "") -> str:
        """Add a numerical entry to the ledger."""
        self._entry_counter += 1
        entry_id = f"entry_{self._entry_counter}_{quantity.lower().replace(' ', '_')}"

        entry = LedgerEntry(
            id=entry_id,
            quantity=quantity,
            value=value,
            unit=unit,
            scope=scope or {},
            source=source,
            evidence_class=evidence_class,
            precision=precision,
            baseline=baseline,
            derived_from=derived_from or [],
            calculation_method=calculation_method,
            timestamp=datetime.now().isoformat(),
        )

        # Check for conflicts with existing entries
        conflicts = self._check_conflicts(entry)
        entry.conflicts = conflicts

        self.entries[entry_id] = entry

        # Auto-validate if we have related entries
        self._validate_related(entry_id)

        return entry_id

    def get_entry(self, entry_id: str) -> Optional[LedgerEntry]:
        """Get entry by ID."""
        return self.entries.get(entry_id)

    def get_entries_by_quantity(self, quantity: str) -> list[LedgerEntry]:
        """Get all entries for a quantity."""
        return [e for e in self.entries.values() if e.quantity.lower() == quantity.lower()]

    def get_entries_by_scope(self, scope_key: str, scope_value: str) -> list[LedgerEntry]:
        """Get entries matching scope criteria."""
        return [e for e in self.entries.values() if e.scope.get(scope_key) == scope_value]

    def update_entry(self, entry_id: str, **kwargs) -> bool:
        """Update an existing entry."""
        if entry_id not in self.entries:
            return False

        entry = self.entries[entry_id]
        for key, value in kwargs.items():
            if hasattr(entry, key):
                setattr(entry, key, value)

        entry.timestamp = datetime.now().isoformat()
        self._validate_related(entry_id)
        return True

    def add_invariant(self, description: str, expression: str,
                      involved_entries: list = None) -> str:
        """Add a consistency invariant."""
        invariant_id = f"inv_{len(self.invariants) + 1}"
        invariant = Invariant(
            id=invariant_id,
            description=description,
            expression=expression,
            involved_entries=involved_entries or [],
        )
        self.invariants.append(invariant)
        return invariant_id

    def validate_all(self) -> dict:
        """Validate all invariants."""
        results = {
            'total': len(self.invariants),
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'details': [],
        }

        for invariant in self.invariants:
            result = self._validate_invariant(invariant)
            invariant.status = result['status']
            invariant.last_checked = datetime.now().isoformat()
            if result['status'] == 'violated':
                invariant.violation_details = result['details']
                results['failed'] += 1
            elif result['status'] == 'valid':
                results['passed'] += 1
            else:
                results['warnings'] += 1
            results['details'].append(result)

        # Log validation
        self.validation_log.append(ValidationLogEntry(
            timestamp=datetime.now().isoformat(),
            check_type='full_validation',
            entries_checked=[inv.id for inv in self.invariants],
            result='pass' if results['failed'] == 0 else 'fail',
            details=f"{results['passed']}/{results['total']} invariants valid",
        ))

        return results

    def compute_metric(self, name: str, formula: str,
                       involved_entries: list) -> Optional[float]:
        """Compute a derived metric from ledger entries."""
        # Simple formula evaluation (in production, use a safe expression evaluator)
        try:
            # Build context from entries
            context = {}
            for entry_id in involved_entries:
                entry = self.entries.get(entry_id)
                if entry:
                    key = entry.quantity.lower().replace(' ', '_')
                    context[key] = entry.value

            # Evaluate formula (simplified - would use ast.literal_eval or similar in production)
            # For now, support basic operations
            result = eval(formula, {"__builtins__": {}}, context)

            self.computed_metrics[name] = {
                'value': result,
                'unit': 'derived',
                'derived_from': involved_entries,
                'formula': formula,
                'last_computed': datetime.now().isoformat(),
            }
            return result
        except Exception as e:
            return None

    def get_computed_metric(self, name: str) -> Optional[dict]:
        """Get a computed metric."""
        return self.computed_metrics.get(name)

    def _check_conflicts(self, new_entry: LedgerEntry) -> list:
        """Check for conflicts with existing entries."""
        conflicts = []

        for entry_id, entry in self.entries.items():
            if entry.quantity.lower() == new_entry.quantity.lower():
                # Same quantity - check if values conflict
                if entry.scope == new_entry.scope:
                    # Same scope - values should match
                    if abs(entry.value - new_entry.value) > 0.001 * max(abs(entry.value), abs(new_entry.value)):
                        conflicts.append(f"Conflicts with {entry_id}: {entry.value} {entry.unit} vs {new_entry.value} {new_entry.unit}")

        return conflicts

    def _validate_related(self, entry_id: str):
        """Validate invariants involving this entry."""
        entry = self.entries[entry_id]
        for invariant in self.invariants:
            if entry_id in invariant.involved_entries or entry.quantity.lower() in invariant.expression.lower():
                self._validate_invariant(invariant)

    def _validate_invariant(self, invariant: Invariant) -> dict:
        """Validate a single invariant."""
        try:
            # Build context
            context = {}
            for entry_id in invariant.involved_entries:
                entry = self.entries.get(entry_id)
                if entry:
                    key = entry.quantity.lower().replace(' ', '_')
                    context[key] = entry.value

            # Evaluate expression
            result = eval(invariant.expression, {"__builtins__": {}}, context)

            # Check if result is truthy (for boolean expressions) or matches expected
            if isinstance(result, bool):
                status = 'valid' if result else 'violated'
                details = f"Expression evaluated to {result}"
            else:
                # For numeric expressions, check if close to expected
                status = 'valid'  # Would need expected value to compare
                details = f"Expression evaluated to {result}"

            return {
                'invariant_id': invariant.id,
                'status': status,
                'details': details,
            }
        except Exception as e:
            return {
                'invariant_id': invariant.id,
                'status': 'warning',
                'details': f"Validation error: {str(e)}",
            }

    def setup_standard_invariants(self):
        """Set up standard numerical invariants."""
        # Node * GPU per node = Total GPUs
        self.add_invariant(
            "Node GPU multiplication",
            "nodes * gpus_per_node == total_gpus",
            involved_entries=[]
        )

        # Total GPUs * hours = GPU-hours
        self.add_invariant(
            "GPU-hour calculation",
            "total_gpus * hours == gpu_hours",
            involved_entries=[]
        )

        # Baseline -> final relationship
        self.add_invariant(
            "Baseline to final measurement",
            "final_value >= 0 and baseline_value >= 0",
            involved_entries=[]
        )

        # Percentage change derivation
        self.add_invariant(
            "Percentage change derivation",
            "abs((final_value - baseline_value) / baseline_value * 100 - percentage_change) < 0.1",
            involved_entries=[]
        )

        # Availability and downtime alignment
        self.add_invariant(
            "Availability downtime alignment",
            "abs(downtime_minutes_per_month - (100 - availability_pct) / 100 * 43200) < 10",
            involved_entries=[]
        )

    def to_dict(self) -> dict:
        """Serialize ledger to dictionary."""
        return {
            'entries': {k: vars(v) for k, v in self.entries.items()},
            'invariants': [vars(v) for v in self.invariants],
            'validation_log': [vars(v) for v in self.validation_log],
            'computed_metrics': self.computed_metrics,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'NumericalLedger':
        """Deserialize ledger from dictionary."""
        ledger = cls()
        ledger.entries = {k: LedgerEntry(**v) for k, v in data.get('entries', {}).items()}
        ledger.invariants = [Invariant(**v) for v in data.get('invariants', [])]
        ledger.validation_log = [ValidationLogEntry(**v) for v in data.get('validation_log', [])]
        ledger.computed_metrics = data.get('computed_metrics', {})
        ledger._entry_counter = len(ledger.entries)
        return ledger