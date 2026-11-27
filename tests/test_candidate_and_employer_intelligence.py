"""Tests for candidate intelligence, sparse resumes, employer contexts, and technology chronology."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from human_interview_engine import HumanInterviewEngine  # noqa: E402


class TestCandidateAndEmployerIntelligence(unittest.TestCase):
    def test_sparse_resume_initializes_silently_with_junior_calibration(self) -> None:
        resume = (ROOT / "examples" / "resumes" / "sparse_junior_cloud_resume.md").read_text(encoding="utf-8")
        jd = (ROOT / "examples" / "job-descriptions" / "junior_cloud_engineer_jd.md").read_text(encoding="utf-8")

        with tempfile.TemporaryDirectory() as tmp:
            engine = HumanInterviewEngine(root_dir=ROOT, memory_dir=tmp)
            init_res = engine.initialize_session(resume=resume, job_description=jd)
            self.assertEqual(init_res["status"], "initialized_waiting_for_question")
            self.assertEqual(init_res["inferred_seniority"]["level"], "junior")

            bundle = engine.memory.load_session_bundle(init_res["session_id"])
            self.assertTrue(bundle["profile"]["is_sparse_resume"])
            self.assertFalse(bundle["world_model"]["persona_profile"]["protected_attributes_inferred"])
            self.assertEqual(len(bundle["session"]["turns"]), 0)

            # Answer should remain grounded as junior without claiming org-wide architecture
            turn = engine.process_turn(init_res["session_id"], "How did you handle staging deployments?")
            self.assertTrue(turn["validation_report"]["passed"])
            self.assertNotIn("based on the resume", turn["response"].lower())

    def test_technology_chronology_blocks_anachronisms(self) -> None:
        resume = (ROOT / "examples" / "resumes" / "senior_ai_infra_resume.md").read_text(encoding="utf-8")
        jd = (ROOT / "examples" / "job-descriptions" / "senior_ai_infra_jd.md").read_text(encoding="utf-8")

        with tempfile.TemporaryDirectory() as tmp:
            engine = HumanInterviewEngine(root_dir=ROOT, memory_dir=tmp)
            init_res = engine.initialize_session(resume=resume, job_description=jd)
            bundle = engine.memory.load_session_bundle(init_res["session_id"])

            # Verify LegacyCorp IT (2012-2013) project contains zero post-2013 tools (no Kubernetes 2014, no OpenTelemetry 2019)
            legacy_proj = [p for p in bundle["project_catalog"]["projects"] if p["employer"] == "LegacyCorp IT"][0]
            stack_names = [t["name"].lower() for t in legacy_proj["technology_stack"]]
            self.assertNotIn("kubernetes", stack_names)
            self.assertNotIn("opentelemetry", stack_names)
            self.assertNotIn("vllm", stack_names)

            # Direct validator test: citing vLLM (2023) inside a 2012-2013 project fails chronology validation
            violations = engine.employer_engine.validate_technology_chronology(
                ["kubernetes", "opentelemetry", "vllm", "python"],
                start_year=2012,
                end_year=2013,
            )
            bad = {v["technology"] for v in violations}
            self.assertEqual(bad, {"kubernetes", "opentelemetry", "vllm"})

    def test_diverse_industries_and_honest_gap_handling(self) -> None:
        sa_resume = (ROOT / "examples" / "resumes" / "staff_solutions_architect_resume.md").read_text(encoding="utf-8")
        sa_jd = (ROOT / "examples" / "job-descriptions" / "staff_solutions_architect_jd.md").read_text(encoding="utf-8")

        with tempfile.TemporaryDirectory() as tmp:
            engine = HumanInterviewEngine(root_dir=ROOT, memory_dir=tmp)
            init_res = engine.initialize_session(resume=sa_resume, job_description=sa_jd)
            self.assertEqual(init_res["inferred_seniority"]["level"], "staff")

            bundle = engine.memory.load_session_bundle(init_res["session_id"])
            industries = [c["industry"] for c in bundle["world_model"]["employer_contexts"]]
            self.assertTrue(any("Healthcare" in ind or "Enterprise" in ind for ind in industries))

            # Probe gap skill ("Snowflake" is in preferred JD, absent from Devon Patel's resume)
            turn = engine.process_turn(init_res["session_id"], "How have you tuned Snowflake data pipelines in production?")
            low = turn["response"].lower()
            self.assertTrue("haven't" in low or "not directly" in low)
            self.assertNotIn("based on the resume", low)

    def test_semiconductor_and_mobile_world_models(self) -> None:
        semi_resume = (ROOT / "examples" / "resumes" / "semiconductor_validation_lead_resume.md").read_text(encoding="utf-8")
        mob_resume = (ROOT / "examples" / "resumes" / "mobile_engineering_manager_resume.md").read_text(encoding="utf-8")
        jd = "Senior Engineering Role requiring reliability and cross-team delivery."

        with tempfile.TemporaryDirectory() as tmp:
            engine = HumanInterviewEngine(root_dir=ROOT, memory_dir=tmp)
            r1 = engine.initialize_session(resume=semi_resume, job_description=jd)
            b1 = engine.memory.load_session_bundle(r1["session_id"])
            self.assertEqual(b1["world_model"]["employer_contexts"][0]["industry_key"], "semiconductor")

            r2 = engine.initialize_session(resume=mob_resume, job_description=jd)
            b2 = engine.memory.load_session_bundle(r2["session_id"])
            self.assertEqual(b2["world_model"]["inferred_seniority"]["level"], "manager")
            self.assertEqual(b2["world_model"]["employer_contexts"][0]["industry_key"], "mobile_applications")


if __name__ == "__main__":
    unittest.main()
