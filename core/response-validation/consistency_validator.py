"""
Consistency Validator - Validates consistency with session history.
"""

from dataclasses import dataclass
from typing import Optional
from ..follow_up_intelligence.consistency_maintainer import ConsistencyMaintainer, ConsistencyCheck
from ..numerical_intelligence.ledger import NumericalLedger


@dataclass
class ConsistencyValidationResult:
    passed: bool
    score: float
    issues: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    checks: list = field(default_factory=list)


class ConsistencyValidator:
    """Validates consistency with session history and established facts."""

    def __init__(self, consistency_maintainer: ConsistencyMaintainer):
        self.maintainer = consistency_maintainer

    def validate(self, response: dict, context: dict) -> ConsistencyValidationResult:
        """Validate response consistency."""
        # Run consistency checks
        checks = self.maintainer.check_consistency(response, context)

        issues = []
        warnings = []
        passed_checks = 0

        for check in checks:
            if check.passed:
                passed_checks += 1
            else:
                if check.severity == "error":
                    issues.append(check.message)
                elif check.severity == "warning":
                    warnings.append(check.message)

        total_checks = len(checks)
        score = passed_checks / total_checks if total_checks > 0 else 1.0

        # Overall pass if no errors and score >= 0.8
        passed = len([i for i in issues if "error" in i.lower()]) == 0 and score >= 0.8

        return ConsistencyValidationResult(
            passed=passed,
            score=score,
            issues=issues,
            warnings=warnings,
            checks=[{
                "name": c.check_name,
                "passed": c.passed,
                "message": c.message,
                "severity": c.severity,
            } for c in checks],
        )

    def validate_numerical_consistency(self, response: str, ledger: NumericalLedger) -> ConsistencyValidationResult:
        """Validate numerical consistency against ledger."""
        issues = []
        warnings = []
        score = 1.0

        # Extract numbers from response
        import re
        numbers = re.findall(r'\b\d+(?:,\d{3})*(?:\.\d+)?\b', response)

        # Check each number against ledger if it looks like a claim
        for num_str in numbers:
            value = float(num_str.replace(',', ''))
            # In production, would match context to ledger entries
            # For now, just note if very precise numbers appear
            if '.' in num_str and len(num_str.split('.')[-1]) > 2:
                warnings.append(f"High precision number: {num_str} - verify appropriateness")

        return ConsistencyValidationResult(
            passed=True,
            score=score,
            issues=issues,
            warnings=warnings,
        )

    def validate_architecture_consistency(self, response: str, established_arch: dict) -> ConsistencyValidationResult:
        """Validate architecture claims against established architecture."""
        issues = []
        warnings = []
        score = 1.0
        r_lower = response.lower()

        if not established_arch:
            return ConsistencyValidationResult(passed=True, score=1.0)

        # Check pattern consistency
        established_pattern = established_arch.get('pattern', '')
        if established_pattern:
            if established_pattern == 'microservices':
                if 'monolith' in r_lower and 'modular' not in r_lower and 'strangler' not in r_lower:
                    issues.append("Claims monolith but established architecture is microservices")
                    score = 0.3
            elif established_pattern == 'modular_monolith':
                if 'microservice' in r_lower and 'strangler' not in r_lower:
                    issues.append("Claims microservices but established architecture is modular monolith")
                    score = 0.3

        # Check component consistency
        components = established_arch.get('components', [])
        for comp in components:
            comp_name = comp.get('name', '')
            comp_tech = comp.get('technology', '')
            if comp_name and comp_name.lower() in r_lower:
                # Component mentioned - check tech consistency
                if comp_tech and comp_tech.lower() not in r_lower:
                    warnings.append(f"Component {comp_name} mentioned but technology {comp_tech} not referenced")

        return ConsistencyValidationResult(
            passed=score >= 0.7,
            score=score,
            issues=issues,
            warnings=warnings,
        )

    def validate_ownership_consistency(self, response: str, established_ownership: dict) -> ConsistencyValidationResult:
        """Validate ownership claims."""
        issues = []
        warnings = []
        score = 1.0
        r_lower = response.lower()

        # Check for ownership language
        strong_ownership = ["i solely", "i alone", "i single-handedly", "entirely my"]
        for phrase in strong_ownership:
            if phrase in r_lower:
                # Check if established ownership is different
                for comp, ownership in established_ownership.items():
                    if ownership in ["shared", "advisory", "validation"]:
                        issues.append(f"Claims sole ownership ({phrase}) but established as {ownership}")
                        score = 0.4

        return ConsistencyValidationResult(
            passed=score >= 0.7,
            score=score,
            issues=issues,
            warnings=warnings,
        )

    def validate_timeline_consistency(self, response: str, established_timeline: dict) -> ConsistencyValidationResult:
        """Validate timeline claims."""
        issues = []
        warnings = []
        score = 1.0

        # In production, would extract timeline claims and compare
        return ConsistencyValidationResult(passed=True, score=1.0)


from dataclasses import field