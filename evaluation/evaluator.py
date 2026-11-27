"""Interview Evaluation Engine — 21-dimension deterministic scoring + independent judge protocol."""

from __future__ import annotations

import json
import re
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
from human_interview_engine.transcription_intelligence import TranscriptionIntelligence  # noqa: E402

_ACK_ONLY_RE = re.compile(
    r"^(?:got it|okay|ok|sure|sounds good|understood|makes sense|thanks|thank you)[\s,.!—-]*"
    r"(?:thanks for having me|thank you)?[.!\s]*$",
    re.IGNORECASE,
)
_HEDGE_RE = re.compile(r"\b(?:don't have|do not have|not sure|offhand|wouldn't want to guess|can't recall)\b", re.IGNORECASE)
_OPENER_STEMS = ("on that point", "on that", "in practice", "from a practical standpoint", "on that note", "honestly")
_TEMPLATE_SEAM_RE = re.compile(
    r"\bacross (?:migrated|built|led|reduced|managed|owned|designed)\b"
    r"|\ba [AEIO][a-z]+\b"
    r"|\b1 years\b|\bat my current team\b"
)


def _word_set(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9']+", (text or "").lower()))


def audit_turns(turns: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Transcript-level checks that do not rely on the per-turn validator's own verdict.

    Flags real questions answered with a bare acknowledgment, near-duplicate answers to
    different questions, stacked opening stems, raw resume fragments in parentheses,
    template seams, and numeric questions answered without any number or honest hedge.
    """
    issues: list[dict[str, Any]] = []
    prior: list[tuple[str, set[str]]] = []
    for t in turns:
        q = (t.get("cleaned_transcript") or "").strip()
        a = (t.get("candidate_response") or "").strip()
        act = (t.get("interviewer_analysis") or {}).get("question_act", "")
        idx = t.get("turn_index")
        low_a = a.lower()
        is_question = "?" in q or TranscriptionIntelligence._has_question_or_task_cue(q)

        if is_question and act not in ("closing", "interruption") and _ACK_ONLY_RE.match(a):
            issues.append({"turn_index": idx, "code": "dismissed_question", "severity": "error",
                           "detail": f"Question answered only with an acknowledgment: {a!r}."})

        words = _word_set(a)
        if len(words) >= 12:
            for prev_q, prev_words in prior:
                if prev_q.lower() == q.lower():
                    continue
                overlap = len(words & prev_words) / max(1, len(words | prev_words))
                if overlap >= 0.8:
                    issues.append({"turn_index": idx, "code": "repeated_answer", "severity": "warning",
                                   "detail": f"Answer is {overlap:.0%} identical to the answer to {prev_q!r}."})
                    break
            prior.append((q, words))

        head = low_a[:120]
        stems = [st for st in _OPENER_STEMS if head.startswith(st) or f", {st}" in head[:60]]
        first_clause = low_a.split(",", 1)[0]
        if len(stems) >= 2 or (0 < len(first_clause.split()) <= 4 and low_a.count(first_clause + ",") >= 2):
            issues.append({"turn_index": idx, "code": "stacked_opening", "severity": "warning",
                           "detail": "Opening stem is stacked or repeated."})

        for frag in re.findall(r"\(([^)]*)\)", a):
            if len(frag.split()) >= 6:
                issues.append({"turn_index": idx, "code": "raw_resume_fragment", "severity": "error",
                               "detail": f"Spoken answer contains a pasted fragment: ({frag[:80]})."})
                break

        if _TEMPLATE_SEAM_RE.search(a):
            issues.append({"turn_index": idx, "code": "template_seam", "severity": "warning",
                           "detail": f"Template join is visible: {_TEMPLATE_SEAM_RE.search(a).group(0)!r}."})

        if re.search(r"\bhow (?:many|much|long|large|big)\b", q.lower()) and not re.search(r"\d", a) \
                and not _HEDGE_RE.search(a) and act not in ("closing", "interruption"):
            issues.append({"turn_index": idx, "code": "unanswered_numeric", "severity": "warning",
                           "detail": "Numeric question answered without a number or an explicit hedge."})
    return issues


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

        audit = audit_turns(turns)
        findings.extend(audit)
        audit_count = {code: sum(1 for i in audit if i["code"] == code) for code in (
            "dismissed_question", "repeated_answer", "stacked_opening", "raw_resume_fragment",
            "template_seam", "unanswered_numeric",
        )}
        dismissed = audit_count["dismissed_question"]
        repeated = audit_count["repeated_answer"]
        stacked = audit_count["stacked_opening"]
        fragments = audit_count["raw_resume_fragment"]
        seams = audit_count["template_seam"]
        unanswered = audit_count["unanswered_numeric"]
        leak_errors += fragments
        cliche_warnings += stacked + seams
        total_errors += dismissed + fragments
        if dismissed:
            hard_failures.append(f"Real question answered with only an acknowledgment in {dismissed} turn(s).")

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
        # Penalties are scaled by session length so one flaw in a 25-turn session still registers
        # but does not zero the score; a dismissed question costs more than a stylistic slip.
        rate = 10.0 / n_turns
        dis = dismissed * rate
        rep = repeated * rate
        unans = unanswered * rate
        det_scores = {
            "human_naturalness": clamp_float(4.8 - 0.5 * cliche_warnings - 0.8 * leak_errors - 0.3 * rep),
            "conversational_authenticity": clamp_float(4.8 - 0.6 * cliche_warnings - 1.5 * leak_errors - 0.4 * rep),
            "question_relevance": clamp_float(4.8 - 0.5 * total_errors - 1.0 * dis - 0.5 * unans),
            "information_density": clamp_float(4.7 - 0.4 * length_warnings - 0.6 * rep - 0.4 * unans),
            "technical_accuracy": clamp_float(4.8 - 0.7 * chrono_errors - 0.5 * total_errors),
            "implementation_depth": clamp_float(4.7 - 0.4 * total_errors - 0.5 * dis),
            "numerical_accuracy": clamp_float(4.9 - 1.2 * num_errors - 1.0 * len(failed_ledger_checks) - 0.6 * unans),
            "mathematical_consistency": clamp_float(5.0 - 1.5 * num_errors - 1.5 * len(failed_ledger_checks)),
            "professional_credibility": clamp_float(4.8 - 0.6 * chrono_errors - 0.8 * evidence_errors - 0.8 * fragments),
            "employer_alignment": clamp_float(4.8 - 1.0 * chrono_errors),
            "seniority_alignment": clamp_float(4.8 - 0.4 * total_errors),
            "individual_ownership": clamp_float(4.7 - 0.4 * total_errors),
            "business_judgment": clamp_float(4.6 - 0.3 * total_errors),
            "leadership_maturity": clamp_float(4.6 - 0.3 * total_errors),
            "context_awareness": clamp_float(4.8 - 0.5 * total_errors - 0.8 * dis - 0.3 * rep),
            "interviewer_adaptation": clamp_float(4.7 - 0.4 * length_warnings - 0.8 * dis),
            "follow_up_consistency": clamp_float(4.9 - 1.0 * num_errors - 0.5 * total_errors - 0.4 * rep),
            "appropriate_answer_length": clamp_float(4.9 - 0.6 * length_warnings - 0.8 * dis),
            "evidence_integrity": clamp_float(5.0 - 2.0 * evidence_errors - 1.0 * fragments),
            "technical_defensibility": clamp_float(4.8 - 0.5 * total_errors - 0.3 * unans),
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
