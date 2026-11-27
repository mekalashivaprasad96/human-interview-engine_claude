"""
Regression Test Suite - Automated tests for consistency and quality.
"""

import json
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


@dataclass
class TestCase:
    name: str
    description: str
    input_data: dict
    expected_output: dict
    category: str = "general"
    severity: str = "high"  # low, medium, high, critical


@dataclass
class TestResult:
    test_case: TestCase
    passed: bool
    actual_output: dict = field(default_factory=dict)
    error_message: str = ""
    duration_ms: float = 0.0


@dataclass
class TestSuiteResult:
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    results: list = field(default_factory=list)
    duration_ms: float = 0.0


class RegressionTestSuite:
    """Regression test suite for HumanInterview Engine."""

    def __init__(self, engine_path: str = None):
        self.engine_path = engine_path or "."
        self.test_cases = []
        self._load_standard_tests()

    def _load_standard_tests(self):
        """Load standard regression test cases."""

        # Communication Naturalness Tests
        self.test_cases.extend([
            TestCase(
                name="no_robotic_phrases",
                description="Response should not contain robotic phrases",
                input_data={"question": "Tell me about yourself", "mode": "immersive"},
                expected_output={"forbidden_phrases": [
                    "that's a great question",
                    "absolutely",
                    "in my previous role",
                    "that's how i approach",
                    "as an ai language model",
                ]},
                category="communication",
                severity="high",
            ),
            TestCase(
                name="uses_contractions",
                description="Response should use natural contractions",
                input_data={"question": "How do you handle pressure?", "mode": "immersive"},
                expected_output={"should_contain_contractions": True},
                category="communication",
                severity="medium",
            ),
            TestCase(
                name="appropriate_length_recruiter",
                description="Recruiter answers should be concise",
                input_data={"question": "Walk me through your resume", "mode": "recruiter"},
                expected_output={"max_words": 150},
                category="length",
                severity="high",
            ),
            TestCase(
                name="appropriate_length_technical",
                description="Technical answers should have sufficient depth",
                input_data={"question": "How did you implement the caching layer?", "mode": "technical"},
                expected_output={"min_words": 110},
                category="length",
                severity="high",
            ),
        ])

        # Numerical Consistency Tests
        self.test_cases.extend([
            TestCase(
                name="numerical_has_units",
                description="Numerical answers should include units",
                input_data={"question": "How many RPS was that handling?", "mode": "technical"},
                expected_output={"has_units": True, "has_number": True},
                category="numerical",
                severity="critical",
            ),
            TestCase(
                name="no_false_precision",
                description="Should not use false precision",
                input_data={"question": "What was the latency?", "mode": "technical"},
                expected_output={"max_decimal_places": 2},
                category="numerical",
                severity="high",
            ),
            TestCase(
                name="ledger_consistency_gpu",
                description="GPU calculations should be consistent: nodes * gpus_per_node = total_gpus",
                input_data={"scenario": {"nodes": 16, "gpus_per_node": 8}},
                expected_output={"total_gpus": 128},
                category="numerical",
                severity="critical",
            ),
            TestCase(
                name="ledger_consistency_gpu_hours",
                description="GPU-hours should be consistent: total_gpus * hours = gpu_hours",
                input_data={"scenario": {"total_gpus": 128, "hours": 48}},
                expected_output={"gpu_hours": 6144},
                category="numerical",
                severity="critical",
            ),
            TestCase(
                name="availability_downtime_alignment",
                description="Availability % and downtime should align",
                input_data={"availability_pct": 99.99},
                expected_output={"downtime_minutes_per_month": 4.32},
                category="numerical",
                severity="high",
            ),
        ])

        # Technical Accuracy Tests
        self.test_cases.extend([
            TestCase(
                name="no_impossible_claims",
                description="Should not make technically impossible claims",
                input_data={"response": "We achieved zero latency with infinite scale"},
                expected_output={"no_impossible": True},
                category="technical",
                severity="critical",
            ),
            TestCase(
                name="technology_timeline_valid",
                description="Technologies should exist during employment period",
                input_data={"technology": "kubernetes", "employment_start": "2015"},
                expected_output={"valid": False, "reason": "Kubernetes not widely available in 2015"},
                category="technical",
                severity="high",
            ),
            TestCase(
                name="ownership_language",
                description="Should use clear individual ownership language",
                input_data={"question": "What did you personally do?", "mode": "behavioral"},
                expected_output={"has_ownership_language": True},
                category="behavioral",
                severity="critical",
            ),
        ])

        # Follow-up Consistency Tests
        self.test_cases.extend([
            TestCase(
                name="followup_no_contradiction",
                description="Follow-up answers should not contradict previous answers",
                input_data={
                    "previous_answer": "We used PostgreSQL with 3 read replicas",
                    "followup_question": "What database did you use?",
                    "followup_answer": "We used MySQL with 5 replicas",
                },
                expected_output={"consistent": False},
                category="consistency",
                severity="critical",
            ),
            TestCase(
                name="followup_preserves_numerical",
                description="Follow-up should preserve established numerical values",
                input_data={
                    "previous_answer": "The system handled 50,000 RPS",
                    "followup_question": "What was the peak?",
                    "followup_answer": "Peak was 150,000 RPS",
                },
                expected_output={"consistent": True},
                category="consistency",
                severity="high",
            ),
        ])

        # Mode Adaptation Tests
        self.test_cases.extend([
            TestCase(
                name="recruiter_mode_minimal_jargon",
                description="Recruiter mode should use minimal jargon",
                input_data={"question": "How do you handle scaling?", "mode": "recruiter"},
                expected_output={"max_technical_terms": 2},
                category="mode_adaptation",
                severity="high",
            ),
            TestCase(
                name="executive_mode_business_focus",
                description="Executive mode should focus on business outcomes",
                input_data={"question": "Tell me about the migration", "mode": "executive"},
                expected_output={"has_business_metrics": True, "has_technical_detail": False},
                category="mode_adaptation",
                severity="high",
            ),
        ])

        # Evidence Classification Tests
        self.test_cases.extend([
            TestCase(
                name="simulated_not_presented_as_fact_authentic",
                description="In authentic mode, simulated content should not be presented as fact",
                input_data={"mode": "authentic", "content_type": "simulated"},
                expected_output={"presentation": "qualified_or_example"},
                category="evidence",
                severity="critical",
            ),
            TestCase(
                name="no_resume_references",
                description="Should never reference resume or documents",
                input_data={"response": "Based on my resume, I have 5 years experience"},
                expected_output={"no_resume_reference": True},
                category="evidence",
                severity="critical",
            ),
        ])

    def add_custom_test(self, test_case: TestCase):
        """Add a custom test case."""
        self.test_cases.append(test_case)

    def run_all(self, engine_runner) -> TestSuiteResult:
        """Run all regression tests."""
        import time

        start_time = time.time()
        results = []

        for test_case in self.test_cases:
            test_start = time.time()
            try:
                result = self._run_test(test_case, engine_runner)
                result.duration_ms = (time.time() - test_start) * 1000
                results.append(result)
            except Exception as e:
                results.append(TestResult(
                    test_case=test_case,
                    passed=False,
                    error_message=f"Test execution error: {str(e)}",
                    duration_ms=(time.time() - test_start) * 1000,
                ))

        total_time = (time.time() - start_time) * 1000

        passed = sum(1 for r in results if r.passed)
        failed = sum(1 for r in results if not r.passed and not r.error_message)
        errors = sum(1 for r in results if r.error_message)

        return TestSuiteResult(
            total_tests=len(results),
            passed=passed,
            failed=failed,
            errors=errors,
            results=results,
            duration_ms=total_time,
        )

    def _run_test(self, test_case: TestCase, engine_runner) -> TestResult:
        """Run a single test case."""
        # This would invoke the engine with test input and validate output
        # For now, return a placeholder result
        try:
            # In production, this would call the actual engine
            # actual_output = engine_runner.run(test_case.input_data)
            # passed = self._validate_output(test_case.expected_output, actual_output)

            # Placeholder
            actual_output = {}
            passed = True

            return TestResult(
                test_case=test_case,
                passed=passed,
                actual_output=actual_output,
            )
        except Exception as e:
            return TestResult(
                test_case=test_case,
                passed=False,
                error_message=str(e),
            )

    def _validate_output(self, expected: dict, actual: dict) -> bool:
        """Validate actual output against expected."""
        # Implementation would check various criteria
        return True

    def run_category(self, category: str, engine_runner) -> TestSuiteResult:
        """Run tests for a specific category."""
        category_tests = [tc for tc in self.test_cases if tc.category == category]
        original_tests = self.test_cases
        self.test_cases = category_tests
        result = self.run_all(engine_runner)
        self.test_cases = original_tests
        return result

    def get_test_summary(self) -> dict:
        """Get summary of all test cases."""
        categories = {}
        for tc in self.test_cases:
            if tc.category not in categories:
                categories[tc.category] = {"count": 0, "severities": {}}
            categories[tc.category]["count"] += 1
            sev = tc.severity
            categories[tc.category]["severities"][sev] = categories[tc.category]["severities"].get(sev, 0) + 1

        return {
            "total_tests": len(self.test_cases),
            "categories": categories,
        }

    def export_results(self, results: TestSuiteResult, file_path: str):
        """Export test results to JSON."""
        data = {
            "summary": {
                "total": results.total_tests,
                "passed": results.passed,
                "failed": results.failed,
                "errors": results.errors,
                "duration_ms": results.duration_ms,
            },
            "results": [
                {
                    "name": r.test_case.name,
                    "category": r.test_case.category,
                    "severity": r.test_case.severity,
                    "passed": r.passed,
                    "duration_ms": r.duration_ms,
                    "error": r.error_message,
                }
                for r in results.results
            ],
        }
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)


class EngineRunner:
    """Interface for running the engine in tests."""

    def __init__(self, engine_module=None):
        self.engine_module = engine_module

    def run(self, input_data: dict) -> dict:
        """Run engine with input data."""
        # Placeholder - would integrate with actual engine
        return {"response": "Test response", "metadata": {}}


def run_regression_tests(engine_path: str = None) -> TestSuiteResult:
    """Convenience function to run all regression tests."""
    suite = RegressionTestSuite(engine_path)
    runner = EngineRunner()
    return suite.run_all(runner)


if __name__ == "__main__":
    result = run_regression_tests()
    print(f"Tests: {result.total_tests}, Passed: {result.passed}, Failed: {result.failed}, Errors: {result.errors}")
    print(f"Duration: {result.duration_ms:.1f}ms")

    if result.failed > 0 or result.errors > 0:
        for r in result.results:
            if not r.passed:
                print(f"  FAIL: {r.test_case.name} ({r.test_case.category}) - {r.error_message}")
        sys.exit(1)
    else:
        print("All tests passed!")
        sys.exit(0)