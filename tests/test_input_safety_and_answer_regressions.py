"""Regression tests for issues found in the 2026-11-27 end-to-end test report.

Covers: storage-ID path traversal, operating-mode validation and aliases, sparse/empty resume
handling and missing input paths, imperative questions without '?', and authentic-mode answer
templates (support-role inference, raw resume bullets, confirmed-metric phrasing).
"""

from __future__ import annotations

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from human_interview_engine import HumanInterviewEngine  # noqa: E402
from human_interview_engine.cli import main as cli_main  # noqa: E402
from human_interview_engine.session_memory import SessionMemoryManager  # noqa: E402
from human_interview_engine.transcription_intelligence import TranscriptionIntelligence  # noqa: E402

INFRA_RESUME = ROOT / "examples" / "resumes" / "senior_ai_infra_resume.md"
INFRA_JD = ROOT / "examples" / "job-descriptions" / "senior_ai_infra_jd.md"
SA_RESUME = ROOT / "examples" / "resumes" / "staff_solutions_architect_resume.md"
SA_JD = ROOT / "examples" / "job-descriptions" / "staff_solutions_architect_jd.md"


def _run_cli(*argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = cli_main(list(argv))
    return code, out.getvalue(), err.getvalue()


class TestStorageIdSafety(unittest.TestCase):
    def test_delete_session_rejects_traversal_and_leaves_outside_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mem = Path(tmp) / "mem"
            victim = Path(tmp) / "victim"
            victim.mkdir()
            (victim / "keep.txt").write_text("x", encoding="utf-8")
            manager = SessionMemoryManager(mem)
            for bad in ("../../victim", "../candidates", "..", "a/b", "/etc", "", "sess\\x", "sess.1"):
                with self.assertRaises(ValueError, msg=bad):
                    manager.delete_session(bad)
                with self.assertRaises(ValueError, msg=bad):
                    manager.delete_candidate(bad)
            self.assertTrue((victim / "keep.txt").exists())

    def test_cli_reports_invalid_id_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, out, err = _run_cli("--memory-dir", tmp, "delete-session", "--session-id", "../../x")
            self.assertEqual(code, 2)
            self.assertIn("Invalid session_id", err)
            self.assertEqual(out, "")

    def test_valid_generated_ids_still_work(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            engine = HumanInterviewEngine(root_dir=ROOT, memory_dir=tmp)
            res = engine.initialize_session(resume=INFRA_RESUME.read_text(), job_description=INFRA_JD.read_text())
            self.assertTrue(engine.memory.delete_session(res["session_id"]))
            self.assertTrue(engine.memory.delete_candidate(res["candidate_id"])["candidate_deleted"])


class TestOperatingModeValidation(unittest.TestCase):
    def test_aliases_resolve_and_unknown_modes_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            engine = HumanInterviewEngine(root_dir=ROOT, memory_dir=tmp)
            cfg = engine.config
            self.assertEqual(cfg.resolve_mode("authentic"), "authentic_preparation")
            self.assertEqual(cfg.resolve_mode("hiring-manager"), "hiring_manager")
            self.assertEqual(cfg.resolve_mode("System-Design"), "system_design")
            self.assertEqual(cfg.resolve_mode("coaching"), "coaching_evaluation")
            self.assertEqual(cfg.resolve_mode("immersive_simulation"), "immersive_simulation")
            with self.assertRaises(ValueError):
                cfg.resolve_mode("banana")

    def test_authentic_alias_blocks_fictional_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            engine = HumanInterviewEngine(root_dir=ROOT, memory_dir=tmp)
            res = engine.initialize_session(
                resume=INFRA_RESUME.read_text(), job_description=INFRA_JD.read_text(), operating_mode="authentic"
            )
            self.assertEqual(res["operating_mode"], "authentic_preparation")
            turn = engine.process_turn(res["session_id"], "How many GPUs were in the inference cluster?")
            self.assertNotIn("128", turn["response"])

    def test_unknown_mode_rejected_on_init_and_turn(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, _, err = _run_cli(
                "--memory-dir", tmp, "init", "--resume", str(INFRA_RESUME), "--jd", str(INFRA_JD), "--mode", "banana"
            )
            self.assertEqual(code, 2)
            self.assertIn("Unknown operating mode 'banana'", err)
            engine = HumanInterviewEngine(root_dir=ROOT, memory_dir=tmp)
            sid = engine.initialize_session(resume=INFRA_RESUME.read_text(), job_description=INFRA_JD.read_text())[
                "session_id"
            ]
            with self.assertRaises(ValueError):
                engine.process_turn(sid, "Tell me about yourself.", mode_override="banana")


class TestResumeInputHandling(unittest.TestCase):
    def test_one_line_resume_initializes_and_answers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            engine = HumanInterviewEngine(root_dir=ROOT, memory_dir=tmp)
            res = engine.initialize_session(resume="Jane Doe, engineer", job_description="Backend engineer")
            self.assertEqual(res["status"], "initialized_waiting_for_question")
            self.assertEqual(res["inferred_seniority"]["level"], "junior")
            intro = engine.process_turn(res["session_id"], "Tell me about yourself.")["response"]
            self.assertNotIn("1 years", intro)
            self.assertNotIn("a Engineer", intro)

    def test_empty_resume_and_missing_path_are_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, _, err = _run_cli("--memory-dir", tmp, "init", "--resume", "", "--jd", "Backend engineer")
            self.assertEqual(code, 2)
            self.assertIn("Resume is empty", err)
            code, _, err = _run_cli("--memory-dir", tmp, "init", "--resume", "/nope/resume.md", "--jd", str(INFRA_JD))
            self.assertEqual(code, 2)
            self.assertIn("Resume file not found", err)
            code, _, err = _run_cli("--memory-dir", tmp, "init", "--resume", str(INFRA_RESUME), "--jd", "missing_jd.txt")
            self.assertEqual(code, 2)
            self.assertIn("Job description file not found", err)


class TestImperativeQuestions(unittest.TestCase):
    TASKS = [
        "Design a rate limiter for a public API.",
        "Give me an example of a failure.",
        "Compare Kafka and RabbitMQ.",
        "Estimate the cost per inference request.",
        "Calculate the GPU-hours for that run.",
        "Talk me through your last project.",
        "Introduce yourself.",
        "Please describe the architecture.",
        "So, how many nodes",
        "and what was the p99 after that",
    ]
    NON_QUESTIONS = ["Okay.", "Got it, thanks.", "Interesting.", "We use Kafka here.", "I heard you were at RetailScale."]

    def test_transcription_classifies_tasks_and_acknowledgments(self) -> None:
        ti = TranscriptionIntelligence()
        for q in self.TASKS:
            self.assertFalse(ti.interpret(q)["is_non_question"], q)
        for q in self.NON_QUESTIONS:
            self.assertTrue(ti.interpret(q)["is_non_question"], q)

    def test_design_prompt_after_behavioral_turn_gets_real_answer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            engine = HumanInterviewEngine(root_dir=ROOT, memory_dir=tmp)
            sid = engine.initialize_session(resume=INFRA_RESUME.read_text(), job_description=INFRA_JD.read_text())[
                "session_id"
            ]
            engine.process_turn(sid, "Tell me about a time you disagreed with your manager.")
            design = engine.process_turn(sid, "Design a rate limiter for a public API.")
            self.assertNotEqual(design["response"].strip(), "Got it.")
            self.assertEqual(design["interviewer_analysis"]["question_act"], "system_design_prompt")
            nodes = engine.process_turn(sid, "So, how many nodes")
            self.assertIn("16", nodes["response"])
            closing = engine.process_turn(sid, "Thanks, that's all from me.")
            self.assertIn("thanks for having me", closing["response"].lower())


class TestAuthenticModeTemplates(unittest.TestCase):
    def test_infra_engineer_is_not_framed_as_support(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            engine = HumanInterviewEngine(root_dir=ROOT, memory_dir=tmp)
            sid = engine.initialize_session(
                resume=INFRA_RESUME.read_text(),
                job_description=INFRA_JD.read_text(),
                operating_mode="authentic_preparation",
            )["session_id"]
            resp = engine.process_turn(sid, "How many GPUs were in the inference cluster?")["response"]
            self.assertNotIn("support side", resp.lower())
            self.assertNotIn("ticket", resp.lower())

    def test_no_unrelated_metric_or_raw_bullet_and_confirmed_metric_reads_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            engine = HumanInterviewEngine(root_dir=ROOT, memory_dir=tmp)
            sid = engine.initialize_session(
                resume=SA_RESUME.read_text(),
                job_description=SA_JD.read_text(),
                operating_mode="authentic_preparation",
            )["session_id"]
            q = "How many nodes did your largest customer deployment have?"
            resp = engine.process_turn(sid, q)["response"]
            self.assertNotIn("97%", resp)
            self.assertNotIn("(", resp)
            self.assertNotIn("De-escalated", resp)
            self.assertNotIn("support side", resp.lower())

            engine.confirm_candidate_detail(
                session_id=sid,
                claim="Migrated a 40-node cluster for a retail customer",
                metric_name="nodes",
                metric_value=40,
                metric_unit="nodes",
            )
            confirmed = engine.process_turn(sid, q)["response"]
            self.assertIn("40 nodes", confirmed)
            self.assertNotIn("across migrated", confirmed)
            self.assertNotIn("Migrated a 40-node", confirmed)

    def test_real_support_role_keeps_support_framing(self) -> None:
        resume = """# Alex Mercer
Cloud Support Engineer

## Experience
Cloud Support Engineer | AWS | 2022 - Present
- Resolved customer tickets for EC2 GPU instances (g4dn.8xlarge, p4d.24xlarge).
"""
        with tempfile.TemporaryDirectory() as tmp:
            engine = HumanInterviewEngine(root_dir=ROOT, memory_dir=tmp)
            sid = engine.initialize_session(
                resume=resume,
                job_description="Role: Senior Technical Support Engineer\nCompany: CloudCompute\n",
                operating_mode="authentic_preparation",
            )["session_id"]
            resp = engine.process_turn(sid, "How many nodes did those customers run?")["response"]
            self.assertIn("support side", resp.lower())


if __name__ == "__main__":
    unittest.main()
