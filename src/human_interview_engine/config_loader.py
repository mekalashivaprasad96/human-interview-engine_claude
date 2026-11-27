"""Configuration and schema loader for HumanInterview Engine."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def find_package_root(start: Path | None = None) -> Path:
    """Locate the root directory of human-interview-engine."""
    if start is not None:
        return Path(start).resolve()
    # src/human_interview_engine/config_loader.py -> parents[2] is package root
    return Path(__file__).resolve().parents[2]


# Short names used in SKILL.md, README.md and the prompt adapters, mapped to canonical mode IDs.
MODE_ALIASES: dict[str, str] = {
    "immersive": "immersive_simulation",
    "simulation": "immersive_simulation",
    "authentic": "authentic_preparation",
    "preparation": "authentic_preparation",
    "technical": "technical_deep_dive",
    "deep_dive": "technical_deep_dive",
    "recruiter": "recruiter_screening",
    "screening": "recruiter_screening",
    "manager": "hiring_manager",
    "behavioural": "behavioral",
    "design": "system_design",
    "exec": "executive",
    "cognitive": "general_cognitive_ability",
    "gca": "general_cognitive_ability",
    "presentation": "presentation_followup",
    "coaching": "coaching_evaluation",
    "evaluation": "coaching_evaluation",
}


class EngineConfig:
    """Loads and exposes static engine configuration registries."""

    def __init__(self, root_dir: Path | None = None) -> None:
        self.root_dir = find_package_root(root_dir)
        self.config_dir = self.root_dir / "config"
        self.schemas_dir = self.root_dir / "schemas"

        self.defaults = self._load_json(self.config_dir / "engine.default.json")
        self.operating_modes = self._load_json(self.config_dir / "operating_modes.json").get("modes", {})
        self.technology_timeline = self._load_json(self.config_dir / "technology_timeline.json").get("technologies", {})
        self.industry_profiles = self._load_json(self.config_dir / "industry_profiles.json").get("industries", {})
        self.communication_rules = self._load_json(self.config_dir / "communication_rules.json")

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def load_schema(self, schema_name: str) -> dict[str, Any]:
        """Load a JSON schema by base filename or full filename."""
        filename = schema_name if schema_name.endswith(".json") else f"{schema_name}.schema.json"
        return self._load_json(self.schemas_dir / filename)

    def resolve_mode(self, mode: str | None) -> str:
        """Return the canonical operating mode ID for a name or alias; raise ValueError if unknown."""
        if mode is None or not str(mode).strip():
            return self.defaults.get("default_operating_mode", "immersive_simulation")
        key = str(mode).strip().lower().replace("-", "_").replace(" ", "_")
        key = MODE_ALIASES.get(key, key)
        if key not in self.operating_modes:
            valid = ", ".join(sorted(self.operating_modes))
            aliases = ", ".join(sorted(MODE_ALIASES))
            raise ValueError(f"Unknown operating mode {mode!r}. Valid modes: {valid}. Aliases: {aliases}.")
        return key

    def get_mode_config(self, mode: str) -> dict[str, Any]:
        """Return operating mode configuration, falling back to default mode."""
        if mode in self.operating_modes:
            return self.operating_modes[mode]
        default_mode = self.defaults.get("default_operating_mode", "immersive_simulation")
        return self.operating_modes[default_mode]
