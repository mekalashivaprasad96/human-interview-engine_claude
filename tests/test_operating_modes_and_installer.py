"""Tests for all operating modes, yes/no precision, repeated questions, and Claude Code installer."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from human_interview_engine import HumanInterviewEngine  # noqa: E402


class TestOperatingModesAndInstaller(unittest.TestCase):
    def test_recruiter_executive_system_design_presentation_and_coaching_modes(self) -> None:
        resume = (ROOT / "examples" / "resumes" / "staff_solutions_architect_resume.md").read_text(encoding="utf-8")
        jd = (ROOT / "examples" / "job-descriptions" / "staff_solutions_architect_jd.md").read_text(encoding="utf-8")

        with tempfile.TemporaryDirectory() as tmp:
            engine = HumanInterviewEngine(root_dir=ROOT, memory_dir=tmp)
            sid = engine.initialize_session(resume, jd, operating_mode="recruiter_screening")["session_id"]

            r_rec = engine.process_turn(sid, "Walk me through your background and why you're interested in Sentinel Cloud.")
            self.assertEqual(r_rec["interviewer_analysis"]["interviewer_type"], "recruiter")
            self.assertTrue(r_rec["validation_report"]["passed"])
            self.assertLessEqual(r_rec["validation_report"]["word_count"], 150)

            r_exec = engine.process_turn(
                sid,
                "What was the business impact and ROI of that migration program?",
                mode_override="executive",
            )
            self.assertEqual(r_exec["length_budget"]["category"], "executive_followup")
            self.assertIn("$", r_exec["response"])

            r_sd = engine.process_turn(
                sid,
                "How would you design a distributed rate limiter for multi-tenant API traffic?",
                mode_override="system_design",
            )
            self.assertEqual(r_sd["length_budget"]["category"], "system_design_initial")
            self.assertIn("redis", r_sd["response"].lower())

            r_pres = engine.process_turn(
                sid,
                "Why did you stage the pilot cutovers over two extra weeks?",
                mode_override="presentation_followup",
            )
            self.assertEqual(r_pres["length_budget"]["category"], "presentation_followup")
            self.assertLessEqual(r_pres["validation_report"]["word_count"], 125)

            r_coach = engine.process_turn(
                sid,
                "Evaluate my session and show evidence status.",
                mode_override="coaching_evaluation",
            )
            self.assertIn("Coaching Assessment:", r_coach["response"])
            self.assertIn("Numerical ledger status:", r_coach["response"])

    def test_yes_no_direct_answer_and_repeated_question(self) -> None:
        resume = (ROOT / "examples" / "resumes" / "senior_ai_infra_resume.md").read_text(encoding="utf-8")
        jd = (ROOT / "examples" / "job-descriptions" / "senior_ai_infra_jd.md").read_text(encoding="utf-8")

        with tempfile.TemporaryDirectory() as tmp:
            engine = HumanInterviewEngine(root_dir=ROOT, memory_dir=tmp)
            sid = engine.initialize_session(resume, jd)["session_id"]

            r_yn = engine.process_turn(sid, "Did you personally build the load-test harness and canary rollout?")
            first_word = r_yn["response"].lower().split()[0].strip("—,-.")
            self.assertIn(first_word, {"yes", "no", "not"})

            r_rep = engine.process_turn(sid, "Did you personally build the load-test harness and canary rollout?")
            self.assertEqual(r_rep["interviewer_analysis"]["question_act"], "repeated_question")
            self.assertTrue(r_rep["validation_report"]["passed"])

    def test_claude_code_install_script_to_temp_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "installed-skill"
            subprocess.run(
                ["bash", str(ROOT / "adapters" / "claude-code" / "install.sh"), str(dest)],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertTrue((dest / "SKILL.md").exists())
            self.assertTrue((dest / "SYSTEM_PROMPT.md").exists())
            self.assertTrue((dest / "src" / "human_interview_engine" / "orchestrator.py").exists())
            self.assertTrue((dest / "core" / "numerical-intelligence" / "MODULE.md").exists())


if __name__ == "__main__":
    unittest.main()
