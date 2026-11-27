"""Interview Evaluation Engine — 21-dimension deterministic scoring + independent judge protocol."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from human_interview_engine.config_loader import EngineConfig  # noqa: E402
from human_interview_engine.models import clamp_float, short_id, utc_now_iso  # noqa: E402
from human_interview_engine.numerical_ledger import NumericalLedger  # noqa: E402
from human_interview_engine.schema_validator import assert_valid_schema  # noqa: E402


class InterviewEvaluator:
    """Evaluates interview sessions using deterministic checks and optional independent external judges."""

    def __init__(self, root_dir: Path | None = None) -> None:
        self.config = EngineConfig(root_dir)
        rubric_path = self.config.root_dir / "evaluation" / "rubric.json"
        self.rubric = json.loads(rubric_path.read_text(encoding="utf-8"))

    def evaluate_session(
        self,
        session_bundle: dict[str, Any],
        external_judge_fn: Callable[[dict[str, Any]], dict[str, float]] | None = None,
        evaluator_id: str = "deterministic-rubric-v4",
    ) -> dict[str, Any]:
        """Score a full session bundle across all 21 dimensions and validate against schema."""
        session = session_bundle["session"]
        turns = session.get("turns", [])
        ledger = NumericalLedger(
            session_id=session["session_id"],
            candidate_id=session["candidate_id"],
            entries=session_bundle["numerical_ledger"].get("entries", []),
            consistency_checks=session_bundle["numerical_ledger"].get("consistency_checks", []),
        )
        checks = ledger.validate_all()

        hard_failures: list[str] = []
        findings: list[dict[str, Any]] = []
        latencies: list[float] = []

        total_errors = 0
        total_warnings = 0
        leak_errors = 0
        num_errors = 0
        chrono_errors = 0
        evidence_errors = 0
        length_warnings = 0
        cliche_warnings = 0

        for t in turns:
            latencies.append(float(t.get("latency_ms", 0.0)))
            vr = t.get("validation_report", {})
            total_errors += vr.get("error_count", 0)
            total_warnings += vr.get("warning_count", 0)
            for issue in vr.get("issues", []):
                code = issue["code"]
                findings.append({"turn_index": t["turn_index"], **issue})
                if code == "persona_resume_leak":
                    leak_errors += 1
                elif code == "numerical_contradiction":
                    num_errors += 1
                elif code == "technology_chronology_error":
                    chrono_errors += 1
                elif code == "evidence_integrity_violation":
                    evidence_errors += 1
                elif code == "excessive_length":
                    length_warnings += 1
                elif code in ("cliche_detected", "repetitive_opening"):
                    cliche_warnings += 1

        failed_ledger_checks = [c for c in checks if not c["passed"]]
        if failed_ledger_checks:
            for fc in failed_ledger_checks:
                hard_failures.append(f"Numerical ledger failure: {fc['details']}")

        if leak_errors > 0:
            hard_failures.append(f"Character/resume leak detected in {leak_errors} turn(s).")
        if evidence_errors > 0:
            hard_failures.append(f"Evidence integrity violation in {evidence_errors} turn(s).")
        if chrono_errors > 0:
            hard_failures.append(f"Technology chronology error in {chrono_errors} turn(s).")

        n_turns = max(1, len(turns))
        avg_lat = round(sum(latencies) / n_turns, 2) if latencies else 0.0
        max_lat = round(max(latencies), 2) if latencies else 0.0

        # Deterministic score calculation on 1.0 - 5.0 scale
        det_scores = {
            "human_naturalness": clamp_float(4.8 - 0.5 * cliche_warnings - 0.8 * leak_errors),
            "conversational_authenticity": clamp_float(4.8 - 0.6 * cliche_warnings - 1.5 * leak_errors),
            "question_relevance": clamp_float(4.8 - 0.5 * total_errors),
            "information_density": clamp_float(4.7 - 0.4 * length_warnings),
            "technical_accuracy": clamp_float(4.8 - 0.7 * chrono_errors - 0.5 * total_errors),
            "implementation_depth": clamp_float(4.7 - 0.4 * total_errors),
            "numerical_accuracy": clamp_float(4.9 - 1.2 * num_errors - 1.0 * len(failed_ledger_checks)),
            "mathematical_consistency": clamp_float(5.0 - 1.5 * num_errors - 1.5 * len(failed_ledger_checks)),
            "professional_credibility": clamp_float(4.8 - 0.6 * chrono_errors - 0.8 * evidence_errors),
            "employer_alignment": clamp_float(4.8 - 1.0 * chrono_errors),
            "seniority_alignment": clamp_float(4.8 - 0.4 * total_errors),
            "individual_ownership": clamp_float(4.7 - 0.4 * total_errors),
            "business_judgment": clamp_float(4.6 - 0.3 * total_errors),
            "leadership_maturity": clamp_float(4.6 - 0.3 * total_errors),
            "context_awareness": clamp_float(4.8 - 0.5 * total_errors),
            "interviewer_adaptation": clamp_float(4.7 - 0.4 * length_warnings),
            "follow_up_consistency": clamp_float(4.9 - 1.0 * num_errors - 0.5 * total_errors),
            "appropriate_answer_length": clamp_float(4.9 - 0.6 * length_warnings),
            "evidence_integrity": clamp_float(5.0 - 2.0 * evidence_errors),
            "technical_defensibility": clamp_float(4.8 - 0.5 * total_errors),
            "response_latency": clamp_float(5.0 if avg_lat < 100.0 else (4.2 if avg_lat < 500.0 else 3.0)),
        }

        eval_type = "deterministic"
        if external_judge_fn is not None:
            judge_scores = external_judge_fn(
                {
                    "session_id": session["session_id"],
                    "turns": turns,
                    "rubric": self.rubric,
                }
            )
            for dim, val in judge_scores.items():
                if dim in det_scores:
                    # Blend deterministic invariant checks with independent judge score
                    det_scores[dim] = clamp_float((det_scores[dim] + float(val)) / 2.0)
            eval_type = "independent_llm"

        weights = {k: v["weight"] for k, v in self.rubric["dimensions"].items()}
        weighted_sum = sum(det_scores[d] * weights.get(d, 1.0) for d in det_scores)
        total_weight = sum(weights.get(d, 1.0) for d in det_scores)
        overall = clamp_float(weighted_sum / max(1.0, total_weight))

        report = {
            "report_id": short_id("eval", session["session_id"]),
            "session_id": session["session_id"],
            "evaluator_type": eval_type,
            "evaluator_id": evaluator_id,
            "rubric_version": self.rubric["rubric_version"],
            "scores": det_scores,
            "overall_score": overall,
            "hard_failures": hard_failures,
            "findings": findings,
            "latency_stats": {"avg_ms": avg_lat, "max_ms": max_lat, "turns_evaluated": len(turns)},
            "created_at": utc_now_iso(),
        }
        assert_valid_schema(report, self.config.load_schema("evaluation_report"), "evaluation_report")
        return report

    def generate_blind_evaluation_packet(self, session_bundle: dict[str, Any]) -> str:
        """Export an anonymized transcript packet for blind human or independent-model evaluation."""
        turns = session_bundle["session"].get("turns", [])
        lines = [
            "# Blind Interview Evaluation Packet",
            f"Session Reference: {session_bundle['session']['session_id']}",
            "Candidate Identity: [REDACTED FOR BLIND EVALUATION]",
            "",
        ]
        for t in turns:
            lines.append(f"## Turn {t['turn_index']}")
            lines.append(f"**Interviewer:** {t['cleaned_transcript']}")
            lines.append(f"**Candidate:** {t['candidate_response']}")
            lines.append("")
        return "\n".join(lines)
