"""Tests for JSON schemas, SKILL.md specification, and platform adapter constraints."""

from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from adapters.claude.package_claude_skill import build_claude_skill_zip  # noqa: E402
from human_interview_engine.config_loader import EngineConfig  # noqa: E402


class TestSchemasAndAdapters(unittest.TestCase):
    def test_all_configs_and_schemas_valid_json(self) -> None:
        cfg = EngineConfig(ROOT)
        self.assertEqual(cfg.defaults["version"], "4.0.0")
        self.assertGreaterEqual(len(cfg.operating_modes), 11)
        self.assertGreaterEqual(len(cfg.technology_timeline), 50)
        self.assertGreaterEqual(len(cfg.industry_profiles), 10)

        schemas = list((ROOT / "schemas").glob("*.schema.json"))
        self.assertEqual(len(schemas), 10)
        for sp in schemas:
            data = json.loads(sp.read_text(encoding="utf-8"))
            self.assertIn("$schema", data)
            self.assertEqual(data["type"], "object")

    def test_skill_md_frontmatter_conforms_to_agent_skills_spec(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        self.assertIsNotNone(m, "SKILL.md must begin with YAML frontmatter")
        fm = m.group(1)

        name_m = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
        desc_m = re.search(r"^description:\s*(.+)$", fm, re.MULTILINE)
        self.assertIsNotNone(name_m)
        self.assertIsNotNone(desc_m)

        name = name_m.group(1).strip()
        desc = desc_m.group(1).strip()
        self.assertLessEqual(len(name), 64)
        self.assertRegex(name, r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        self.assertNotIn("claude", name)
        self.assertNotIn("anthropic", name)
        self.assertGreater(len(desc), 20)
        self.assertLessEqual(len(desc), 1024)

    def test_custom_gpt_instructions_within_8000_char_limit(self) -> None:
        content = (ROOT / "adapters" / "chatgpt" / "custom-gpt-instructions.md").read_text(encoding="utf-8")
        self.assertLessEqual(len(content), 8000)
        self.assertGreater(len(content), 1500)

    def test_chatgpt_personalization_fields_within_1500_chars(self) -> None:
        content = (ROOT / "adapters" / "chatgpt" / "chatgpt-custom-instructions.md").read_text(encoding="utf-8")
        blocks = re.findall(r"```text\n(.*?)\n```", content, re.DOTALL)
        self.assertEqual(len(blocks), 2)
        for blk in blocks:
            self.assertLessEqual(len(blk.strip()), 1500)

    def test_package_claude_skill_zip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "skill.zip"
            built = build_claude_skill_zip(out)
            self.assertTrue(built.exists())
            with zipfile.ZipFile(built, "r") as zf:
                names = set(zf.namelist())
            self.assertIn("human-interview-engine/SKILL.md", names)
            self.assertIn("human-interview-engine/SYSTEM_PROMPT.md", names)
            self.assertIn("human-interview-engine/config/technology_timeline.json", names)


if __name__ == "__main__":
    unittest.main()
