"""Regression tests converted directly from user-reported live ChatGPT interview failures."""

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


class TestUserReportedASRAndPersonaRegressions(unittest.TestCase):
    def test_asr_notes_to_nodes_and_authentic_aws_support_scope(self) -> None:
        aws_support_resume = """# Alex Mercer
Cloud Support Engineer (Compute & GPU)

## Experience
Cloud Support Engineer | AWS | 2022 - Present
- Troubleshoot EC2 Linux and GPU-backed instances (g4dn.8xlarge, p4d.24xlarge) for enterprise customers.
- Isolated host hardware failures, NVIDIA driver issues, and EKS node-group boot bottlenecks.

## Skills
AWS, EC2, Linux, EKS, Kubernetes, CUDA, Python, Troubleshooting
"""
        jd = """Role: Senior Technical Support Engineer
Company: CloudCompute
Requirements:
- Experience troubleshooting GPU-backed Linux compute nodes and Kubernetes workloads.
"""
        with tempfile.TemporaryDirectory() as tmp:
            engine = HumanInterviewEngine(root_dir=ROOT, memory_dir=tmp)
            sid = engine.initialize_session(
                resume=aws_support_resume,
                job_description=jd,
                operating_mode="authentic_preparation",
            )["session_id"]

            # Q1: Voice ASR typo "notes" instead of "nodes" + broken grammar
            r1 = engine.process_turn(sid, "How many notes does those GPU contains?")
            self.assertIn("nodes", r1["cleaned_transcript"].lower())
            self.assertTrue(r1["validation_report"]["passed"], r1["validation_report"]["issues"])
            low1 = r1["response"].lower()
            self.assertNotIn("the question doesn't specify", low1)
            self.assertNotIn("interview scenario", low1)
            self.assertNotIn("verified node count", low1)
            self.assertFalse(r1["response"].startswith(('"', "“")))

            # Q2: Multi-part "How large are the notes... And how many notes does that large cluster contain?"
            r2 = engine.process_turn(
                sid,
                "How large are the notes that you have worked on? And how many notes does that large cluster contain?",
            )
            self.assertNotIn("notes", r2["cleaned_transcript"].lower())
            self.assertTrue(r2["validation_report"]["passed"], r2["validation_report"]["issues"])
            low2 = r2["response"].lower()
            self.assertIn("g4dn.8xlarge", low2)
            self.assertIn("p4d.24xlarge", low2)
            self.assertIn("support", low2)
            self.assertNotIn("interview scenario", low2)
            self.assertNotIn("verified node count", low2)
            self.assertFalse(r2["response"].startswith(('"', "“")))

    def test_immersive_simulation_answers_node_size_and_count_without_meta_leaks(self) -> None:
        resume = (ROOT / "examples" / "resumes" / "senior_ai_infra_resume.md").read_text(encoding="utf-8")
        jd = (ROOT / "examples" / "job-descriptions" / "senior_ai_infra_jd.md").read_text(encoding="utf-8")

        with tempfile.TemporaryDirectory() as tmp:
            engine = HumanInterviewEngine(root_dir=ROOT, memory_dir=tmp)
            sid = engine.initialize_session(resume=resume, job_description=jd, operating_mode="immersive_simulation")["session_id"]

            r1 = engine.process_turn(sid, "How many notes does those GPU contains?")
            self.assertIn("8", r1["response"])
            self.assertIn("16", r1["response"])
            self.assertTrue(r1["validation_report"]["passed"])
            self.assertNotIn("the question doesn't specify", r1["response"].lower())

            r2 = engine.process_turn(
                sid,
                "How large are the notes that you have worked on? And how many notes does that large cluster contain?",
            )
            self.assertIn("8", r2["response"])
            self.assertIn("16", r2["response"])
            self.assertTrue(r2["validation_report"]["passed"])

    def test_validator_and_importer_catch_chatgpt_transcript_leaks(self) -> None:
        bad_transcript = """Interviewer: How many notes does those GPU contains?
Candidate: The cluster has 8 nodes. The question doesn't specify how many GPUs are in each node.

Interviewer: How large are the notes that you have worked on?
Candidate: "In my AWS role, I don't have a verified node count. The eight-node cluster we just discussed is the interview scenario."
"""
        with tempfile.TemporaryDirectory() as tmp:
            engine = HumanInterviewEngine(root_dir=ROOT, memory_dir=tmp)
            imp = engine.importer.import_text_transcript(bad_transcript, "user_chatgpt_failure.txt")
            diag = engine.improvement_engine.analyze_imported_history(imp)
            cats = {item["category"] for item in diag["observed_transcript_evidence"]}
            self.assertIn("breaking_character_resume_reference", cats)


if __name__ == "__main__":
    unittest.main()
