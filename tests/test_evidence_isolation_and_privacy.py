"""Tests for evidence integrity, multi-candidate isolation, session recovery, and privacy deletion."""

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


class TestEvidenceIsolationAndPrivacy(unittest.TestCase):
    def test_authentic_preparation_blocks_fictional_metrics_unless_confirmed(self) -> None:
        resume = (ROOT / "examples" / "resumes" / "senior_ai_infra_resume.md").read_text(encoding="utf-8")
        jd = (ROOT / "examples" / "job-descriptions" / "senior_ai_infra_jd.md").read_text(encoding="utf-8")

        with tempfile.TemporaryDirectory() as tmp:
            engine = HumanInterviewEngine(root_dir=ROOT, memory_dir=tmp)
            init_res = engine.initialize_session(
                resume=resume,
                job_description=jd,
                operating_mode="authentic_preparation",
            )
            sid = init_res["session_id"]

            # Unconfirmed node/GPU figure should NOT be asserted as verified personal history
            res1 = engine.process_turn(sid, "How many GPUs were in your production cluster?")
            self.assertNotIn("128 gpus", res1["response"].lower())
            self.assertTrue(res1["validation_report"]["passed"])

            # Verify no fictional scenario items were auto-promoted
            bundle = engine.memory.load_session_bundle(sid)
            fictional_items = [
                i for i in bundle["evidence_ledger"]["items"]
                if i["category"] == "fictional_simulation_scenario"
            ]
            self.assertTrue(all(not i["confirmed_by_candidate"] for i in fictional_items))

            # Candidate explicitly confirms real node count -> now permitted and verified!
            engine.confirm_candidate_detail(
                session_id=sid,
                claim="Operated 12 production GPU nodes",
                metric_name="nodes",
                metric_value=12,
                metric_unit="nodes",
            )
            res2 = engine.process_turn(sid, "How many nodes did you operate?")
            self.assertIn("12", res2["response"])

    def test_multi_candidate_isolation_and_session_recovery(self) -> None:
        maya = (ROOT / "examples" / "resumes" / "senior_ai_infra_resume.md").read_text(encoding="utf-8")
        devon = (ROOT / "examples" / "resumes" / "staff_solutions_architect_resume.md").read_text(encoding="utf-8")
        jd_ai = (ROOT / "examples" / "job-descriptions" / "senior_ai_infra_jd.md").read_text(encoding="utf-8")
        jd_sa = (ROOT / "examples" / "job-descriptions" / "staff_solutions_architect_jd.md").read_text(encoding="utf-8")

        with tempfile.TemporaryDirectory() as tmp:
            engine1 = HumanInterviewEngine(root_dir=ROOT, memory_dir=tmp)
            s_maya = engine1.initialize_session(maya, jd_ai)["session_id"]
            s_devon = engine1.initialize_session(devon, jd_sa)["session_id"]

            engine1.process_turn(s_maya, "How many GPUs were in your cluster?")
            r_devon = engine1.process_turn(s_devon, "How did you manage enterprise customer cutovers?")
            self.assertNotIn("RetailScale", r_devon["response"])
            self.assertIn("MedCloud", r_devon["response"])

            # Simulate fresh engine restart & session recovery from disk
            engine2 = HumanInterviewEngine(root_dir=ROOT, memory_dir=tmp)
            recovered = engine2.process_turn(s_maya, "And what was the GPU-hours total for 48 hours?")
            self.assertIn("6,144", recovered["response"])

    def test_privacy_deletion_controls(self) -> None:
        maya = (ROOT / "examples" / "resumes" / "senior_ai_infra_resume.md").read_text(encoding="utf-8")
        jd_ai = (ROOT / "examples" / "job-descriptions" / "senior_ai_infra_jd.md").read_text(encoding="utf-8")

        with tempfile.TemporaryDirectory() as tmp:
            engine = HumanInterviewEngine(root_dir=ROOT, memory_dir=tmp)
            init_res = engine.initialize_session(maya, jd_ai)
            sid = init_res["session_id"]
            cid = init_res["candidate_id"]

            self.assertIn(sid, engine.memory.list_sessions())
            self.assertIn(cid, engine.memory.list_candidates())

            del_res = engine.memory.delete_candidate(cid)
            self.assertTrue(del_res["candidate_deleted"])
            self.assertIn(sid, del_res["sessions_deleted"])
            self.assertEqual(engine.memory.list_sessions(), [])
            self.assertEqual(engine.memory.list_candidates(), [])


if __name__ == "__main__":
    unittest.main()
