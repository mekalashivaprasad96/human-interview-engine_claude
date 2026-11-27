"""End-to-end CLI tests verifying subprocess invocation and exit codes."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestCLIEndToEnd(unittest.TestCase):
    def _run_cli(self, args: list[str], memory_dir: str) -> subprocess.CompletedProcess[str]:
        env = dict(os.environ)
        env["PYTHONPATH"] = str(ROOT / "src")
        cmd = [sys.executable, "-m", "human_interview_engine", "--memory-dir", memory_dir, *args]
        return subprocess.run(cmd, cwd=str(ROOT), env=env, capture_output=True, text=True, check=True)

    def test_cli_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            init_proc = self._run_cli(
                [
                    "init",
                    "--resume",
                    "examples/resumes/senior_ai_infra_resume.md",
                    "--jd",
                    "examples/job-descriptions/senior_ai_infra_jd.md",
                    "--mode",
                    "technical_deep_dive",
                ],
                tmp,
            )
            init_data = json.loads(init_proc.stdout)
            sid = init_data["session_id"]
            cid = init_data["candidate_id"]

            turn_proc = self._run_cli(
                ["turn", "--session-id", sid, "--question", "How many GPUs were in the cluster?", "--json"],
                tmp,
            )
            turn_data = json.loads(turn_proc.stdout)
            self.assertIn("128", turn_data["response"])
            self.assertTrue(turn_data["validation_report"]["passed"])

            ledger_proc = self._run_cli(["inspect-ledger", "--session-id", sid], tmp)
            ledger_data = json.loads(ledger_proc.stdout)
            self.assertGreaterEqual(len(ledger_data["numerical_ledger"]["entries"]), 5)

            imp_proc = self._run_cli(
                ["import-history", "--file", "examples/transcripts/flawed_historical_transcript.txt"],
                tmp,
            )
            imp_data = json.loads(imp_proc.stdout)
            self.assertGreaterEqual(len(imp_data["observed_transcript_evidence"]), 3)

            del_proc = self._run_cli(["delete-candidate", "--candidate-id", cid], tmp)
            del_data = json.loads(del_proc.stdout)
            self.assertTrue(del_data["candidate_deleted"])


if __name__ == "__main__":
    unittest.main()
