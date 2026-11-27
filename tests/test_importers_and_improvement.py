"""Tests for historical interview importers (Text, ChatGPT, Claude) and continuous improvement workflow."""

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


class TestImportersAndImprovement(unittest.TestCase):
    def test_import_text_chatgpt_and_claude_exports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            engine = HumanInterviewEngine(root_dir=ROOT, memory_dir=tmp)

            txt_imp = engine.importer.import_file(ROOT / "examples" / "transcripts" / "flawed_historical_transcript.txt")
            self.assertFalse(txt_imp["verified_facts_auto_promoted"])
            self.assertEqual(len(txt_imp["conversations"][0]["turns"]), 3)

            cgpt_imp = engine.importer.import_file(ROOT / "examples" / "transcripts" / "synthetic_chatgpt_export.json")
            self.assertEqual(cgpt_imp["conversations"][0]["source_format"], "chatgpt_export")
            self.assertEqual(len(cgpt_imp["conversations"][0]["turns"]), 2)

            claude_imp = engine.importer.import_file(ROOT / "examples" / "transcripts" / "synthetic_claude_export.json")
            self.assertEqual(claude_imp["conversations"][0]["source_format"], "claude_export")
            self.assertEqual(len(claude_imp["conversations"][0]["turns"]), 2)

    def test_unavailable_file_raises_and_never_fabricates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            engine = HumanInterviewEngine(root_dir=ROOT, memory_dir=tmp)
            with self.assertRaises(FileNotFoundError):
                engine.importer.import_file(Path(tmp) / "missing_transcript.json")

    def test_diagnose_failures_generate_regression_cases_and_gate_rule_updates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            engine = HumanInterviewEngine(root_dir=ROOT, memory_dir=tmp)
            imp = engine.importer.import_file(ROOT / "examples" / "transcripts" / "flawed_historical_transcript.txt")
            diagnosis = engine.improvement_engine.analyze_imported_history(
                imported_bundle=imp,
                explicit_feedback=["Make the answer natural", "Do not make it too long"],
            )

            observed_cats = {item["category"] for item in diagnosis["observed_transcript_evidence"]}
            self.assertIn("robotic_communication", observed_cats)
            self.assertIn("breaking_character_resume_reference", observed_cats)
            self.assertIn("missing_numbers", observed_cats)
            self.assertIn("excessive_agreement", observed_cats)
            self.assertTrue(len(diagnosis["generated_regression_cases"]) >= 4)

            prefs = {
                "candidate_id": "test-cand",
                "preferred_contractions": True,
                "target_wpm": 145,
                "verbosity_bias": "balanced",
                "banned_phrases": [],
                "preferred_terminology": {},
                "learned_rules": [],
            }
            # Regression gate rejects rules if candidate score drops below baseline
            rejected = engine.improvement_engine.apply_validated_rules(
                prefs,
                diagnosis["proposed_rules"],
                baseline_score=4.5,
                candidate_score=4.1,
            )
            self.assertFalse(rejected["applied"])
            self.assertEqual(len(prefs["learned_rules"]), 0)

            # Commits rules when candidate score improves or meets baseline
            accepted = engine.improvement_engine.apply_validated_rules(
                prefs,
                diagnosis["proposed_rules"],
                baseline_score=4.2,
                candidate_score=4.8,
            )
            self.assertTrue(accepted["applied"])
            self.assertGreater(accepted["rules_added"], 0)
            self.assertEqual(prefs["verbosity_bias"], "concise")


if __name__ == "__main__":
    unittest.main()
