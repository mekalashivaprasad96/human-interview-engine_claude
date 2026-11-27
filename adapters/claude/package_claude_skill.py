"""Package HumanInterview Engine as a portable Claude Skill .zip archive."""

from __future__ import annotations

import zipfile
from pathlib import Path


def build_claude_skill_zip(output_path: str | Path | None = None) -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    dist_dir = repo_root / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)
    out = Path(output_path) if output_path else (dist_dir / "human-interview-engine-skill.zip")

    include_files = ["SKILL.md", "SYSTEM_PROMPT.md", "README.md", "CHANGELOG.md"]
    include_dirs = ["config", "schemas", "core", "src", "importers", "evaluation"]

    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        prefix = Path("human-interview-engine")
        for fname in include_files:
            fpath = repo_root / fname
            if fpath.exists():
                zf.write(fpath, prefix / fname)
        for dname in include_dirs:
            dpath = repo_root / dname
            if not dpath.exists():
                continue
            for item in sorted(dpath.rglob("*")):
                if item.is_file() and "__pycache__" not in item.parts and not item.name.endswith(".pyc"):
                    zf.write(item, prefix / item.relative_to(repo_root))
    return out


if __name__ == "__main__":
    archive = build_claude_skill_zip()
    print(f"Built Claude skill package: {archive}")
