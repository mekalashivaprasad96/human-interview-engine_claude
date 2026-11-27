"""
Claude Code Adapter - Integrates HumanInterview Engine with Claude Code skills system.
"""

import json
import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class SkillConfig:
    name: str = "human-interview-engine"
    version: str = "4.0.0"
    description: str = "Universal Human Candidate Cognitive Intelligence System"
    entry_point: str = "main.py"
    memory_path: str = "memory"
    config_path: str = "config/settings.json"


class ClaudeCodeAdapter:
    """Adapter for Claude Code skill system."""

    def __init__(self, skill_root: str):
        self.skill_root = Path(skill_root)
        self.memory_path = self.skill_root / "memory"
        self.config_path = self.skill_root / "config" / "settings.json"

    def install(self, target_path: str = "~/.claude/skills/human-interview-engine") -> bool:
        """Install skill to Claude Code skills directory."""
        target = Path(target_path).expanduser()
        target.parent.mkdir(parents=True, exist_ok=True)

        # Copy skill directory
        import shutil
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(self.skill_root, target)

        # Initialize memory directory
        (target / "memory").mkdir(exist_ok=True)

        return True

    def initialize_session(self, resume_text: str, jd_text: str, mode: str = "immersive") -> dict:
        """Initialize interview session."""
        # This would be called from the skill's main entry point
        # Returns session configuration for the skill runtime
        return {
            "resume": resume_text,
            "job_description": jd_text,
            "mode": mode,
            "config": self._load_config(),
            "memory_path": str(self.memory_path),
        }

    def _load_config(self) -> dict:
        """Load configuration."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return json.load(f)
        return {}

    def save_session(self, session_data: dict, session_id: str):
        """Save session to memory."""
        session_file = self.memory_path / f"session_{session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)

    def load_session(self, session_id: str) -> Optional[dict]:
        """Load session from memory."""
        session_file = self.memory_path / f"session_{session_id}.json"
        if session_file.exists():
            with open(session_file) as f:
                return json.load(f)
        return None

    def list_sessions(self) -> list:
        """List all saved sessions."""
        sessions = []
        for f in self.memory_path.glob("session_*.json"):
            session_id = f.stem.replace("session_", "")
            sessions.append(session_id)
        return sessions

    def export_session(self, session_id: str, export_path: str) -> bool:
        """Export session to file."""
        session = self.load_session(session_id)
        if session:
            with open(export_path, 'w') as f:
                json.dump(session, f, indent=2)
            return True
        return False

    def import_session(self, import_path: str) -> Optional[str]:
        """Import session from file."""
        with open(import_path) as f:
            session = json.load(f)
        session_id = session.get("session_id", f"imported_{len(self.list_sessions())}")
        self.save_session(session, session_id)
        return session_id


class SkillEntryPoint:
    """Main entry point for the skill when invoked in Claude Code."""

    def __init__(self):
        self.adapter = None
        self.engine = None

    def run(self, args: list):
        """Run skill with command-line arguments."""
        import sys

        if len(args) < 2:
            self._print_usage()
            return

        command = args[1]

        if command == "init":
            self._cmd_init(args[2:])
        elif command == "question":
            self._cmd_question(args[2:])
        elif command == "mode":
            self._cmd_mode(args[2:])
        elif command == "session":
            self._cmd_session(args[2:])
        elif command == "evidence":
            self._cmd_evidence(args[2:])
        elif command == "ledger":
            self._cmd_ledger(args[2:])
        elif command == "import":
            self._cmd_import(args[2:])
        elif command == "evaluate":
            self._cmd_evaluate(args[2:])
        else:
            print(f"Unknown command: {command}")
            self._print_usage()

    def _print_usage(self):
        print("""
HumanInterview Engine 4.0 - Claude Code Skill

Usage:
  /skill human-interview-engine init --resume <text> --jd <text> [--mode immersive]
  /skill human-interview-engine question "Your question here"
  /skill human-interview-engine mode <mode>
  /skill human-interview-engine session <list|save|load|export> [session_id]
  /skill human-interview-engine evidence
  /skill human-interview-engine ledger
  /skill human-interview-engine import <file_path>
  /skill human-interview-engine evaluate

Modes: immersive, authentic, technical, recruiter, hiring-manager, behavioral, system-design, executive, cognitive, coaching
        """)

    def _cmd_init(self, args: list):
        print("Initializing HumanInterview Engine...")
        # Parse args
        resume = ""
        jd = ""
        mode = "immersive"

        i = 0
        while i < len(args):
            if args[i] == "--resume" and i + 1 < len(args):
                resume = args[i + 1]
                i += 2
            elif args[i] == "--jd" and i + 1 < len(args):
                jd = args[i + 1]
                i += 2
            elif args[i] == "--mode" and i + 1 < len(args):
                mode = args[i + 1]
                i += 2
            else:
                i += 1

        if not resume or not jd:
            print("Error: Both --resume and --jd are required")
            return

        # Initialize engine
        print(f"Mode: {mode}")
        print("Engine initialized. Ready for questions.")
        print("Use: /skill human-interview-engine question \"Your question\"")

    def _cmd_question(self, args: list):
        if not args:
            print("Error: Question text required")
            return
        question = " ".join(args)
        print(f"Q: {question}")
        print("A: [Engine would generate response here]")

    def _cmd_mode(self, args: list):
        if not args:
            print("Current mode: immersive (default)")
            return
        mode = args[0]
        valid_modes = ["immersive", "authentic", "technical", "recruiter", "hiring-manager",
                       "behavioral", "system-design", "executive", "cognitive", "coaching"]
        if mode in valid_modes:
            print(f"Mode changed to: {mode}")
        else:
            print(f"Invalid mode. Valid modes: {', '.join(valid_modes)}")

    def _cmd_session(self, args: list):
        if not args:
            print("Session commands: list, save, load, export")
            return
        subcmd = args[0]
        print(f"Session {subcmd}: [Not fully implemented in adapter]")

    def _cmd_evidence(self, args: list):
        print("Evidence status: [Engine would show evidence classification]")

    def _cmd_ledger(self, args: list):
        print("Numerical ledger: [Engine would show ledger contents]")

    def _cmd_import(self, args: list):
        if not args:
            print("Error: File path required")
            return
        print(f"Importing from {args[0]}: [Not fully implemented]")

    def _cmd_evaluate(self, args: list):
        print("Running evaluation: [Not fully implemented]")


if __name__ == "__main__":
    import sys
    entry = SkillEntryPoint()
    entry.run(sys.argv)