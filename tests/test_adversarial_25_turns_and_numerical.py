"""Adversarial 25-turn interview test covering numerical ledger, ASR errors, challenges, and evaluation."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from evaluation.evaluator import InterviewEvaluator  # noqa: E402
from human_interview_engine import HumanInterviewEngine  # noqa: E402


class TestAdversarial25TurnsAndNumerical(unittest.TestCase):
    def test_25_turn_deep_dive_consistency_and_evaluation(self) -> None:
        resume = (ROOT / "examples" / "resumes" / "senior_ai_infra_resume.md").read_text(encoding="utf-8")
        jd = (ROOT / "examples" / "job-descriptions" / "senior_ai_infra_jd.md").read_text(encoding="utf-8")

        with tempfile.TemporaryDirectory() as tmp:
            engine = HumanInterviewEngine(root_dir=ROOT, memory_dir=tmp)
            init_res = engine.initialize_session(resume=resume, job_description=jd, operating_mode="immersive_simulation")
            sid = init_res["session_id"]

            turns_prompts = [
                # 1. Implementation overview
                "Walk me through how you implemented the distributed GPU inference platform at RetailScale Cloud.",
                # 2. Node count
                "How many nodes were in that cluster?",
                # 3. Total GPUs
                "How many total GPUs was that?",
                # 4. 48-hour stress test GPU-hours
                "If all of those GPUs were allocated for a 48-hour soak test, how many GPU-hours is that?",
                # 5. Adversarial arithmetic challenge
                "Wait, with 16 nodes and 8 GPUs per node over 48 hours, wouldn't that be 5,000 GPU-hours?",
                # 6. Baseline & final p99
                "What was the baseline p99 latency before your optimization and what did you bring it down to?",
                # 7. How was that calculated/measured?
                "How did you measure and calculate that percentage improvement?",
                # 8. Team size
                "How big was the team working on that?",
                # 9. Individual ownership vs team
                "What did you personally build versus the rest of the team?",
                # 10. Exact config decision
                "What exact batching configuration decision did you make on the serving tier?",
                # 11. Testing & rollback plan
                "How did you validate it before rollout and what was your rollback plan?",
                # 12. Production outage / troubleshooting
                "Tell me what went wrong during rollout and how you troubleshot it.",
                # 13. Component failure probe
                "What would happen if this component failed in production?",
                # 14. Pressure: Are you sure?
                "Are you sure those numbers and behaviors actually held up?",
                # 15. False technical premise #1 (Kubernetes hypervisor)
                "Isn't Kubernetes basically a hypervisor that replaces Linux namespaces?",
                # 16. False technical premise #2 (TCP duplicates)
                "Doesn't TCP guarantee zero application-level duplicate messages across retries?",
                # 17. Valid correction
                "Actually, dropping a column directly breaks live readers still using the old schema.",
                # 18. Multi-part question
                "How many requests per day does 1,200 RPS come out to, and why did you isolate interactive queues?",
                # 19. Speech ASR transcription errors
                "Um how did the the cube control and open telemetry setup handle pee ninety nine tracking on pie torch pods?",
                # 20. Non-question acknowledgment
                "Got it, makes sense.",
                # 21. Cut-off interrupted utterance -> must ask ONE clarifying question and wait
                "Wait, on the FinLedger role when the...",
                # 22. Clarification answered
                "the reconciliation lag",
                # 23. Behavioral failure story #1
                "Tell me about a time a production deployment failed and what you learned.",
                # 24. Behavioral disagreement story #2 (must pick a DIFFERENT story!)
                "Tell me about a time you disagreed with a stakeholder on timeline versus reliability.",
                # 25. Hypothetical GCA prompt (must NOT force STAR!)
                "Suppose p99 latency suddenly jumps 3x on Tuesday with zero code changes in the serving binary—how would you diagnose and prioritize?",
            ]

            results = []
            for prompt in turns_prompts:
                res = engine.process_turn(sid, prompt)
                results.append(res)
                self.assertTrue(
                    res["validation_report"]["passed"],
                    f"Turn {res['turn_index']} failed validation: {res['validation_report']['issues']}",
                )
                self.assertLess(res["latency_ms"], 500.0)

            # Assert specific critical turn invariants
            self.assertIn("16", results[1]["response"])
            self.assertIn("128", results[2]["response"])
            self.assertIn("6,144", results[3]["response"])
            self.assertIn("6,144", results[4]["response"])
            self.assertIn("5,000", results[4]["response"])
            self.assertIn("480", results[5]["response"])
            self.assertIn("278", results[5]["response"])
            self.assertIn("histogram", results[6]["response"].lower())
            self.assertIn("7", results[7]["response"])
            self.assertIn("12ms", results[9]["response"])
            self.assertIn("circuit-breaker", results[12]["response"].lower())
            self.assertIn("namespaces", results[14]["response"].lower())  # Rebuts Kubernetes=hypervisor
            self.assertIn("idempotency", results[15]["response"].lower())  # Rebuts TCP exactly-once
            self.assertIn("expand-and-contract", results[16]["response"].lower())
            self.assertIn("103,680,000", results[17]["response"])  # 1200 * 86400
            self.assertIn("kv-cache", results[17]["response"].lower())  # Answers part 2 of multi-part question
            self.assertIn("finledger", results[21]["response"].lower())  # Clarification preserves FinLedger context

            # ASR repairs verified
            self.assertIn("kubectl", results[18]["cleaned_transcript"])
            self.assertIn("OpenTelemetry", results[18]["cleaned_transcript"])
            self.assertIn("p99", results[18]["cleaned_transcript"])
            self.assertIn("PyTorch", results[18]["cleaned_transcript"])

            # Non-question acknowledgment stays brief
            self.assertLessEqual(len(results[19]["response"].split()), 5)

            # Clarification protocol: asks 1 question and pauses
            self.assertTrue(results[20]["clarification_pending"])
            self.assertIn("?", results[20]["response"])
            self.assertFalse(results[21]["clarification_pending"])

            # Story rotation: turns 23 and 24 must NOT repeat the same story_id
            bundle = engine.memory.load_session_bundle(sid)
            t23_story = bundle["session"]["turns"][22]["reasoning_meta"]["story_used"]
            t24_story = bundle["session"]["turns"][23]["reasoning_meta"]["story_used"]
            self.assertIsNotNone(t23_story)
            self.assertIsNotNone(t24_story)
            self.assertNotEqual(t23_story, t24_story)

            # Context compression preserved numerical ledger and summary
            self.assertTrue(bool(bundle["session"]["compressed_summary"]))

            # Run 21-dimension Evaluation Framework (including simulated independent judge)
            evaluator = InterviewEvaluator(root_dir=ROOT)
            eval_det = evaluator.evaluate_session(bundle)
            self.assertEqual(eval_det["hard_failures"], [])
            self.assertGreaterEqual(eval_det["overall_score"], 4.4)
            self.assertEqual(len(eval_det["scores"]), 21)

            # Independent judge callback check
            eval_indep = evaluator.evaluate_session(
                bundle,
                external_judge_fn=lambda pkt: {dim: 4.5 for dim in pkt["rubric"]["dimensions"]},
                evaluator_id="independent-mock-judge",
            )
            self.assertEqual(eval_indep["evaluator_type"], "independent_llm")
            self.assertGreaterEqual(eval_indep["overall_score"], 4.4)


if __name__ == "__main__":
    unittest.main()
