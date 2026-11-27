"""The deterministic evaluator must penalise visibly flawed answers, not score every session ~4.8."""

from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
for p in (str(SRC), str(ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from evaluation.evaluator import InterviewEvaluator, audit_turns  # noqa: E402
from human_interview_engine import HumanInterviewEngine  # noqa: E402

QUESTIONS = [
    "Tell me about yourself.",
    "How many nodes were in the inference cluster?",
    "Tell me about a time you disagreed with your manager.",
    "Design a rate limiter for a public API.",
    "Walk me through how you'd debug a latency spike in production.",
]


class TestEvaluatorPenalties(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        engine = HumanInterviewEngine(root_dir=ROOT, memory_dir=cls._tmp.name)
        resume = (ROOT / "examples" / "resumes" / "senior_ai_infra_resume.md").read_text(encoding="utf-8")
        jd = (ROOT / "examples" / "job-descriptions" / "senior_ai_infra_jd.md").read_text(encoding="utf-8")
        sid = engine.initialize_session(resume=resume, job_description=jd)["session_id"]
        for q in QUESTIONS:
            engine.process_turn(sid, q)
        cls.bundle = engine.memory.load_session_bundle(sid)
        cls.evaluator = InterviewEvaluator(root_dir=ROOT)
        cls.clean = cls.evaluator.evaluate_session(cls.bundle)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def _with_response(self, turn_pos: int, text: str) -> dict:
        bundle = copy.deepcopy(self.bundle)
        bundle["session"]["turns"][turn_pos]["candidate_response"] = text
        return bundle

    def test_clean_session_has_no_audit_findings(self) -> None:
        self.assertEqual(audit_turns(self.bundle["session"]["turns"]), [])
        self.assertEqual(self.clean["hard_failures"], [])
        self.assertGreaterEqual(self.clean["overall_score"], 4.5)

    def test_dismissed_question_is_a_hard_failure_and_lowers_score(self) -> None:
        report = self.evaluator.evaluate_session(self._with_response(3, "Got it."))
        self.assertTrue(any("acknowledgment" in h for h in report["hard_failures"]))
        self.assertIn("dismissed_question", {f["code"] for f in report["findings"]})
        self.assertLessEqual(report["overall_score"], self.clean["overall_score"] - 0.3)
        self.assertLess(report["scores"]["question_relevance"], self.clean["scores"]["question_relevance"])

    def test_repeated_answer_is_penalised(self) -> None:
        turns = self.bundle["session"]["turns"]
        report = self.evaluator.evaluate_session(self._with_response(4, turns[2]["candidate_response"]))
        self.assertIn("repeated_answer", {f["code"] for f in report["findings"]})
        self.assertLess(report["scores"]["information_density"], self.clean["scores"]["information_density"])

    def test_raw_resume_fragment_and_template_seam_are_flagged(self) -> None:
        fragment = (
            "From the metrics I directly tracked, I worked with 97% at MedCloud Platform "
            "(De-escalated P1 reliability incidents and drove 97% annual net customer retention.)."
        )
        report = self.evaluator.evaluate_session(self._with_response(1, fragment))
        codes = {f["code"] for f in report["findings"]}
        self.assertIn("raw_resume_fragment", codes)
        self.assertLess(report["scores"]["evidence_integrity"], self.clean["scores"]["evidence_integrity"])

        seam = self.evaluator.evaluate_session(
            self._with_response(1, "That was 40 nodes across migrated a 40-node cluster for a retail customer.")
        )
        self.assertIn("template_seam", {f["code"] for f in seam["findings"]})

    def test_stacked_opening_and_unanswered_numeric(self) -> None:
        stacked = "In practice, from the work I've done, in practice, that starts with separating synchronous handling from slower work."
        report = self.evaluator.evaluate_session(self._with_response(4, stacked))
        self.assertIn("stacked_opening", {f["code"] for f in report["findings"]})

        vague = self.evaluator.evaluate_session(
            self._with_response(1, "We had a fairly large cluster that scaled with seasonal traffic.")
        )
        self.assertIn("unanswered_numeric", {f["code"] for f in vague["findings"]})
        hedged = self.evaluator.evaluate_session(
            self._with_response(1, "I don't have the exact figure offhand, but I can explain how we sized it.")
        )
        self.assertNotIn("unanswered_numeric", {f["code"] for f in hedged["findings"]})


if __name__ == "__main__":
    unittest.main()
