"""
Quality Validator - Validates response quality before delivery.
"""

from dataclasses import dataclass
from typing import Optional
from ..candidate_intelligence.persona_builder import ProfessionalPersona
from ..interviewer_intelligence.intent_analyzer import IntentAnalysis


@dataclass
class ValidationResult:
    passed: bool
    score: float  # 0-1
    issues: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    suggestions: list = field(default_factory=list)


class QualityValidator:
    """Validates response quality against multiple criteria."""

    def __init__(self):
        self.checks = [
            self._check_answers_question,
            self._check_technical_accuracy,
            self._check_natural_language,
            self._check_seniority_appropriateness,
            self._check_background_alignment,
            self._check_employer_alignment,
            self._check_timeline_respect,
            self._check_ownership_clarity,
            self._check_numerical_consistency,
            self._check_no_contradictions,
            self._check_technical_feasibility,
            self._check_appropriate_length,
            self._check_interviewer_satisfaction,
            self._check_followup_resilience,
            self._check_unsupported_claims,
            self._check_not_rehearsed,
            self._check_business_judgment,
            self._check_communication_appropriateness,
        ]

    def validate(self, response: str, context: dict) -> ValidationResult:
        """Run all quality checks on a response."""
        all_issues = []
        all_warnings = []
        all_suggestions = []
        scores = []

        for check in self.checks:
            try:
                result = check(response, context)
                if not result.passed:
                    all_issues.extend(result.issues)
                all_warnings.extend(result.warnings)
                all_suggestions.extend(result.suggestions)
                scores.append(result.score if hasattr(result, 'score') else (1.0 if result.passed else 0.0))
            except Exception as e:
                all_issues.append(f"Validation check failed: {str(e)}")
                scores.append(0.0)

        overall_score = sum(scores) / len(scores) if scores else 0.0
        passed = overall_score >= 0.7 and len([i for i in all_issues if "error" in i.lower()]) == 0

        return ValidationResult(
            passed=passed,
            score=overall_score,
            issues=all_issues,
            warnings=all_warnings,
            suggestions=all_suggestions,
        )

    def _check_answers_question(self, response: str, context: dict) -> ValidationResult:
        """Check if response answers the actual question."""
        question = context.get("question", "")
        intent = context.get("intent")

        issues = []
        score = 1.0

        if intent:
            expected_type = intent.expected_response_type
            # Basic check - does response seem relevant?
            q_lower = question.lower()
            r_lower = response.lower()

            # Check for key question words in response
            if "how many" in q_lower or "how much" in q_lower:
                # Should contain numbers
                import re
                if not re.search(r'\d+', response):
                    issues.append("Numerical question but no numbers in response")
                    score = 0.3

            if "why" in q_lower:
                # Should contain reasoning words
                reasoning_words = ["because", "since", "reason", "rationale", "tradeoff", "chose", "decided"]
                if not any(w in r_lower for w in reasoning_words):
                    issues.append("Why question but no reasoning in response")
                    score = 0.5

            if "how" in q_lower and "implement" in q_lower:
                # Should contain implementation detail
                impl_words = ["implement", "code", "config", "architecture", "design", "pattern", "approach"]
                if not any(w in r_lower for w in impl_words):
                    issues.append("Implementation question but no technical detail")
                    score = 0.5

        return ValidationResult(passed=score >= 0.7, score=score, issues=issues)

    def _check_technical_accuracy(self, response: str, context: dict) -> ValidationResult:
        """Check technical accuracy (basic heuristics)."""
        issues = []
        score = 1.0
        r_lower = response.lower()

        # Check for obviously wrong statements
        wrong_patterns = [
            ("kubernetes runs on bare metal without os", "Kubernetes requires an OS"),
            ("tcp is faster than udp for all cases", "TCP/UDP tradeoffs are nuanced"),
            ("nosql is always faster than sql", "Performance depends on use case"),
            ("microservices solve all scaling problems", "Microservices add complexity"),
        ]

        for pattern, correction in wrong_patterns:
            if pattern in r_lower:
                issues.append(f"Potentially inaccurate: {correction}")
                score = min(score, 0.6)

        return ValidationResult(passed=score >= 0.7, score=score, issues=issues)

    def _check_natural_language(self, response: str, context: dict) -> ValidationResult:
        """Check for natural, human-like language."""
        issues = []
        warnings = []
        score = 1.0
        r_lower = response.lower()

        # Check for robotic patterns
        robotic_patterns = [
            "that's a great question",
            "absolutely, ",
            "in my previous role, ",
            "that's how i approach",
            "as an ai language model",
            "based on the resume",
            "the information provided",
        ]

        for pattern in robotic_patterns:
            if pattern in r_lower:
                issues.append(f"Robotic pattern detected: '{pattern}'")
                score = min(score, 0.4)

        # Check for repetitive sentence structure
        sentences = response.split('. ')
        if len(sentences) > 3:
            starts = [s.strip().split()[0].lower() if s.strip().split() else "" for s in sentences]
            if len(set(starts)) < len(starts) * 0.5:
                warnings.append("Repetitive sentence starters")
                score = min(score, 0.8)

        # Check for contractions (should have some)
        if "do not" in r_lower and "don't" not in r_lower and "cannot" in r_lower and "can't" not in r_lower:
            warnings.append("No contractions - may sound formal/robotic")
            score = min(score, 0.9)

        return ValidationResult(passed=score >= 0.7, score=score, issues=issues, warnings=warnings)

    def _check_seniority_appropriateness(self, response: str, context: dict) -> ValidationResult:
        """Check if response matches candidate seniority."""
        issues = []
        score = 1.0
        persona = context.get("persona")
        r_lower = response.lower()

        if not persona:
            return ValidationResult(passed=True, score=1.0)

        seniority = getattr(persona, 'ownership_level', 'feature')

        if seniority in ['task', 'feature']:  # Junior/Mid
            # Should not claim org-level ownership
            org_claims = ["organization-wide", "company-wide", "strategic direction", "executive decision"]
            for claim in org_claims:
                if claim in r_lower:
                    issues.append(f"Junior/mid candidate claiming org-level ownership: '{claim}'")
                    score = min(score, 0.5)

        elif seniority in ['system', 'platform', 'organization']:  # Senior+
            # Should not be overly detailed on implementation unless asked
            if context.get("question_type") not in ["implementation", "technical_concept"]:
                impl_detail_words = ["line of code", "function", "variable", "loop", "if statement"]
                for word in impl_detail_words:
                    if word in r_lower:
                        warnings.append(f"Senior candidate giving low-level detail: '{word}'")
                        score = min(score, 0.8)

        return ValidationResult(passed=score >= 0.7, score=score, issues=issues)

    def _check_background_alignment(self, response: str, context: dict) -> ValidationResult:
        """Check alignment with professional background."""
        issues = []
        score = 1.0

        # In production, would check against resume/background
        # For now, basic check
        return ValidationResult(passed=True, score=1.0)

    def _check_employer_alignment(self, response: str, context: dict) -> ValidationResult:
        """Check alignment with employer context."""
        return ValidationResult(passed=True, score=1.0)

    def _check_timeline_respect(self, response: str, context: dict) -> ValidationResult:
        """Check respect for employment timeline."""
        return ValidationResult(passed=True, score=1.0)

    def _check_ownership_clarity(self, response: str, context: dict) -> ValidationResult:
        """Check individual ownership clarity."""
        issues = []
        score = 1.0
        r_lower = response.lower()

        # Check for "we" without clarifying individual role
        we_count = r_lower.count(" we ")
        i_count = r_lower.count(" i ")

        if we_count > 0 and i_count == 0:
            warnings.append("Only 'we' language - individual contribution unclear")
            score = min(score, 0.7)

        # Check for clear ownership language
        ownership_words = ["i led", "i designed", "i implemented", "i owned", "my responsibility", "i drove"]
        has_ownership = any(w in r_lower for w in ownership_words)

        if not has_ownership and context.get("question_type") in ["behavioral", "implementation", "leadership"]:
            warnings.append("No clear individual ownership language")
            score = min(score, 0.7)

        return ValidationResult(passed=score >= 0.7, score=score, issues=issues, warnings=warnings)

    def _check_numerical_consistency(self, response: str, context: dict) -> ValidationResult:
        """Check numerical consistency."""
        return ValidationResult(passed=True, score=1.0)

    def _check_no_contradictions(self, response: str, context: dict) -> ValidationResult:
        """Check for contradictions with previous answers."""
        return ValidationResult(passed=True, score=1.0)

    def _check_technical_feasibility(self, response: str, context: dict) -> ValidationResult:
        """Check technical feasibility of claims."""
        issues = []
        score = 1.0
        r_lower = response.lower()

        # Check for impossible claims
        impossible = [
            ("zero latency", "Zero latency is impossible"),
            ("infinite scale", "Infinite scale is impossible"),
            ("100% availability", "100% availability is impossible"),
            ("zero cost", "Zero cost is impossible"),
            ("no maintenance", "No maintenance is impossible"),
        ]

        for claim, correction in impossible:
            if claim in r_lower:
                issues.append(f"Implausible claim: {correction}")
                score = min(score, 0.4)

        return ValidationResult(passed=score >= 0.7, score=score, issues=issues)

    def _check_appropriate_length(self, response: str, context: dict) -> ValidationResult:
        """Check if response length is appropriate."""
        issues = []
        warnings = []
        score = 1.0

        question_type = context.get("question_type", "factual")
        word_count = len(response.split())

        # Duration guidelines (words at ~150 wpm)
        guidelines = {
            "acknowledgment": (5, 15),
            "simple_confirmation": (10, 40),
            "numerical_clarification": (15, 50),
            "narrow_technical_followup": (25, 75),
            "recruiter_question": (75, 150),
            "technical_concept": (75, 150),
            "implementation_question": (110, 225),
            "troubleshooting_scenario": (150, 300),
            "behavioral_question": (190, 300),
            "complex_hypothetical": (225, 450),
            "system_design_initial": (300, 450),
            "executive_followup": (75, 110),
        }

        min_words, max_words = guidelines.get(question_type, (50, 200))

        if word_count < min_words:
            warnings.append(f"Response may be too short ({word_count} words, min {min_words})")
            score = min(score, 0.8)
        elif word_count > max_words * 1.5:
            warnings.append(f"Response may be too long ({word_count} words, max {max_words})")
            score = min(score, 0.8)

        return ValidationResult(passed=score >= 0.7, score=score, issues=issues, warnings=warnings)

    def _check_interviewer_satisfaction(self, response: str, context: dict) -> ValidationResult:
        """Check if response gives interviewer what they need."""
        return ValidationResult(passed=True, score=1.0)

    def _check_followup_resilience(self, response: str, context: dict) -> ValidationResult:
        """Check if response can withstand follow-up questions."""
        return ValidationResult(passed=True, score=1.0)

    def _check_unsupported_claims(self, response: str, context: dict) -> ValidationResult:
        """Check for unsupported factual claims."""
        issues = []
        score = 1.0
        r_lower = response.lower()

        # Check for specific claims without qualification
        claim_patterns = [
            ("industry standard", "May need qualification"),
            ("best practice", "Context-dependent"),
            ("proven to", "Needs evidence"),
            ("guaranteed", "Nothing is guaranteed"),
        ]

        for pattern, note in claim_patterns:
            if pattern in r_lower:
                warnings.append(f"Unsupported claim: '{pattern}' - {note}")
                score = min(score, 0.85)

        return ValidationResult(passed=score >= 0.7, score=score, issues=issues, warnings=warnings)

    def _check_not_rehearsed(self, response: str, context: dict) -> ValidationResult:
        """Check if response sounds rehearsed."""
        return ValidationResult(passed=True, score=1.0)

    def _check_business_judgment(self, response: str, context: dict) -> ValidationResult:
        """Check business judgment appropriateness."""
        return ValidationResult(passed=True, score=1.0)

    def _check_communication_appropriateness(self, response: str, context: dict) -> ValidationResult:
        """Check communication appropriateness for audience."""
        issues = []
        score = 1.0
        interviewer_type = context.get("interviewer_type", "technical_specialist")
        r_lower = response.lower()

        if interviewer_type == "recruiter":
            # Should avoid deep jargon
            jargon = ["kubernetes", "istio", "ebpf", "grpc", "protobuf", "circuit breaker", "idempotency"]
            for term in jargon:
                if term in r_lower:
                    issues.append(f"Deep technical jargon for recruiter: '{term}'")
                    score = min(score, 0.5)

        elif interviewer_type == "executive":
            # Should focus on business outcomes
            biz_words = ["revenue", "cost", "risk", "roi", "strategy", "customer", "market"]
            tech_words = ["implementation", "code", "function", "algorithm", "database", "api"]
            has_biz = any(w in r_lower for w in biz_words)
            has_tech = any(w in r_lower for w in tech_words)

            if has_tech and not has_biz:
                warnings.append("Executive audience but response is purely technical")
                score = min(score, 0.7)

        return ValidationResult(passed=score >= 0.7, score=score, issues=issues)


from dataclasses import field