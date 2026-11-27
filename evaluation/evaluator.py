"""
Evaluator - Evaluates response quality across multiple dimensions.
"""

from dataclasses import dataclass, field
from typing import Optional
from ..core.response_validation.quality_validator import QualityValidator
from ..core.response_validation.technical_validator import TechnicalValidator
from ..core.response_validation.consistency_validator import ConsistencyValidator
from ..core.follow_up_intelligence.consistency_maintainer import ConsistencyMaintainer
from ..core.numerical_intelligence.ledger import NumericalLedger
from ..experience_enrichment.scenario_generator import Scenario
from ..experience_enrichment.project_modeler import ProjectModel


@dataclass
class EvaluationResult:
    overall_score: float
    dimension_scores: dict = field(default_factory=dict)
    passed: bool = False
    strengths: list = field(default_factory=list)
    weaknesses: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)


class Evaluator:
    """Evaluates response quality across multiple dimensions."""

    DIMENSIONS = [
        "human_naturalness",
        "conversational_authenticity",
        "question_relevance",
        "information_density",
        "technical_accuracy",
        "implementation_depth",
        "numerical_accuracy",
        "mathematical_consistency",
        "professional_credibility",
        "employer_alignment",
        "seniority_alignment",
        "individual_ownership",
        "business_judgment",
        "leadership_maturity",
        "context_awareness",
        "interviewer_adaptation",
        "followup_consistency",
        "appropriate_answer_length",
        "evidence_integrity",
        "technical_defensibility",
        "response_latency",
    ]

    def __init__(self):
        self.quality_validator = QualityValidator()
        self.technical_validator = TechnicalValidator()
        self.consistency_maintainer = ConsistencyMaintainer()
        self.consistency_validator = ConsistencyValidator(self.consistency_maintainer)

    def evaluate(self, response: str, context: dict,
                  scenario: Scenario = None, model: ProjectModel = None,
                  ledger: NumericalLedger = None) -> EvaluationResult:
        """Evaluate a response across all dimensions."""

        dimension_scores = {}
        all_strengths = []
        all_weaknesses = []
        all_recommendations = []

        # Run quality validation
        quality_result = self.quality_validator.validate(response, context)
        dimension_scores["human_naturalness"] = quality_result.score
        dimension_scores["conversational_authenticity"] = quality_result.score
        dimension_scores["question_relevance"] = 1.0 if not any("question" in i.lower() for i in quality_result.issues) else 0.5
        dimension_scores["appropriate_answer_length"] = 1.0 if not any("length" in i.lower() for i in quality_result.issues) else 0.7

        if quality_result.issues:
            all_weaknesses.extend(quality_result.issues)
        if quality_result.warnings:
            all_weaknesses.extend(quality_result.warnings)
        if quality_result.suggestions:
            all_recommendations.extend(quality_result.suggestions)

        # Technical validation (if scenario provided)
        if scenario and model and ledger:
            tech_result = self.technical_validator.validate(response, scenario, model, ledger, context)
            dimension_scores["technical_accuracy"] = tech_result.score
            dimension_scores["implementation_depth"] = tech_result.score
            dimension_scores["technical_defensibility"] = tech_result.score

            if tech_result.issues:
                all_weaknesses.extend(tech_result.issues)
            if tech_result.warnings:
                all_weaknesses.extend(tech_result.warnings)
            if tech_result.corrected_claims:
                all_recommendations.extend([f"Corrected: {c}" for c in tech_result.corrected_claims])

        # Consistency validation
        consistency_result = self.consistency_validator.validate({}, context)
        dimension_scores["followup_consistency"] = consistency_result.score
        dimension_scores["mathematical_consistency"] = consistency_result.score
        dimension_scores["evidence_integrity"] = consistency_result.score

        # Calculate derived dimensions
        dimension_scores["information_density"] = self._estimate_information_density(response, context)
        dimension_scores["professional_credibility"] = self._estimate_professional_credibility(response, context)
        dimension_scores["individual_ownership"] = self._estimate_ownership(response, context)
        dimension_scores["interviewer_adaptation"] = self._estimate_interviewer_adaptation(response, context)

        # Overall score
        scores = list(dimension_scores.values())
        overall_score = sum(scores) / len(scores) if scores else 0.0

        # Determine pass/fail
        passed = overall_score >= 0.75 and all(score >= 0.6 for score in dimension_scores.values())

        # Generate summary
        strengths, weaknesses, recommendations = self._generate_summary(dimension_scores, all_weaknesses)

        return EvaluationResult(
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            passed=passed,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
        )

    def _estimate_information_density(self, response: str, context: dict) -> float:
        """Estimate information density of response."""
        word_count = len(response.split())
        question_type = context.get("question_type", "factual")

        # Target words per question type
        targets = {
            "numerical": 30,
            "simple_confirmation": 20,
            "technical_concept": 80,
            "implementation_question": 150,
            "troubleshooting_scenario": 200,
            "behavioral_question": 180,
            "system_design_initial": 300,
        }

        target = targets.get(context.get("question_type"), 100)
        ratio = word_count / target

        if 0.7 <= ratio <= 1.3:
            return 1.0
        elif 0.5 <= ratio <= 1.5:
            return 0.8
        else:
            return 0.5

    def _estimate_professional_credibility(self, response: str, context: dict) -> float:
        """Estimate professional credibility."""
        score = 1.0
        r_lower = response.lower()

        # Positive indicators
        positive = ["i led", "i designed", "i implemented", "we measured", "baseline was",
                    "tradeoff was", "root cause", "postmortem", "runbook"]
        for p in positive:
            if p in response.lower():
                score = min(score + 0.05, 1.0)

        # Negative indicators
        negative = ["i think maybe", "probably", "i guess", "not sure", "whatever works"]
        for n in negative:
            if n in response.lower():
                score = max(score - 0.1, 0.0)

        return score

    def _estimate_ownership(self, response: str, context: dict) -> float:
        """Estimate individual ownership clarity."""
        r_lower = response.lower()

        # Check for ownership language
        ownership_phrases = ["i led", "i designed", "i implemented", "i owned", "my responsibility",
                             "i drove", "i architected", "i decided", "my decision"]
        ownership_count = sum(1 for p in ownership_phrases if p in r_lower)

        # Check for only "we" language
        we_count = r_lower.count(" we ")

        if ownership_count >= 2:
            return 1.0
        elif ownership_count == 1:
            return 0.8
        elif ownership_count == 0 and we_count > 2:
            return 0.4
        else:
            return 0.6

    def _estimate_interviewer_adaptation(self, response: str, context: dict) -> float:
        """Estimate interviewer adaptation."""
        interviewer_type = context.get("interviewer_type", "technical_specialist")
        r_lower = response.lower()

        if interviewer_type == "recruiter":
            # Should avoid deep jargon
            jargon = ["kubernetes", "istio", "ebpf", "grpc", "protobuf", "circuit breaker"]
            jargon_count = sum(1 for t in jargon if t in r_lower)
            return max(1.0 - jargon_count * 0.15, 0.5)

        elif interviewer_type == "executive":
            # Should have business focus
            biz_words = ["revenue", "cost", "risk", "roi", "strategy", "customer", "market"]
            biz_count = sum(1 for w in biz_words if w in r_lower)
            return min(0.5 + biz_count * 0.1, 1.0)

        return 0.8

    def _generate_summary(self, dimension_scores: dict, all_weaknesses: list) -> tuple:
        """Generate strengths, weaknesses, recommendations from scores."""
        strengths = []
        weaknesses = []
        recommendations = []

        for dim, score in dimension_scores.items():
            if score >= 0.9:
                strengths.append(f"Excellent {dim.replace('_', ' ')}")
            elif score >= 0.75:
                strengths.append(f"Good {dim.replace('_', ' ')}")
            elif score < 0.6:
                weaknesses.append(f"Needs improvement: {dim.replace('_', ' ')} (score: {score:.2f})")

        # Add specific recommendations based on weaknesses
        for weakness in all_weaknesses:
            if "robotic" in weakness.lower():
                recommendations.append("Practice natural language with contractions and varied sentence structure")
            elif "numerical" in weakness.lower():
                recommendations.append("Maintain numerical ledger; always provide units, baselines, and methodology")
            elif "ownership" in weakness.lower():
                recommendations.append("Use 'I led', 'I designed', 'I implemented' to clarify individual contribution")
            elif "technical" in weakness.lower():
                recommendations.append("Add implementation specifics: configurations, algorithms, tradeoffs, metrics")
            elif "length" in weakness.lower():
                recommendations.append("Calibrate answer length to question type using duration guidelines")

        # Deduplicate
        strengths = list(dict.fromkeys(strengths))
        weaknesses = list(dict.fromkeys(weaknesses))
        recommendations = list(dict.fromkeys(recommendations))

        return strengths, weaknesses, recommendations

    def evaluate_session(self, session_history: list[dict]) -> dict:
        """Evaluate an entire interview session."""
        results = []

        for turn in session_history:
            response = turn.get("candidate_response", "")
            context = turn.get("context", {})
            result = self.evaluate(response, context)
            results.append({
                "turn": turn.get("turn", 0),
                "score": result.overall_score,
                "passed": result.passed,
            })

        avg_score = sum(r["score"] for r in results) / len(results) if results else 0
        pass_rate = sum(1 for r in results if r["passed"]) / len(results) if results else 0

        return {
            "total_turns": len(results),
            "average_score": avg_score,
            "pass_rate": pass_rate,
            "turn_results": results,
        }


def create_evaluator() -> Evaluator:
    """Factory function to create evaluator."""
    return Evaluator()