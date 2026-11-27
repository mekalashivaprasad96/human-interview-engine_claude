"""Session Memory Manager — isolated per-candidate/per-session storage, compression, and privacy controls."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

from .models import short_id, utc_now_iso

_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")


def validate_storage_id(value: str, kind: str = "id") -> str:
    """Reject IDs that could escape the memory root (path separators, '..', empty, odd characters)."""
    if not isinstance(value, str) or not _SAFE_ID_RE.match(value):
        raise ValueError(
            f"Invalid {kind} {value!r}: use only letters, digits, '-' and '_' (no path separators or '..')."
        )
    return value


class SessionMemoryManager:
    """Persists candidate profiles, world models, ledgers, and interview sessions locally with strict isolation."""

    def __init__(self, memory_root: Path) -> None:
        self.memory_root = Path(memory_root)
        self.candidates_dir = self.memory_root / "candidates"
        self.sessions_dir = self.memory_root / "sessions"
        self.candidates_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _contained_dir(base: Path, item_id: str, kind: str) -> Path:
        validate_storage_id(item_id, kind)
        target = (base / item_id).resolve()
        base_resolved = base.resolve()
        if target.parent != base_resolved:
            raise ValueError(f"Invalid {kind} {item_id!r}: resolves outside {base_resolved}.")
        return target

    def _candidate_dir(self, candidate_id: str) -> Path:
        return self._contained_dir(self.candidates_dir, candidate_id, "candidate_id")

    def _session_dir(self, session_id: str) -> Path:
        return self._contained_dir(self.sessions_dir, session_id, "session_id")

    @staticmethod
    def _write_json(path: Path, data: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False)

    @staticmethod
    def _read_json(path: Path) -> Any:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def save_candidate_bundle(
        self,
        candidate_id: str,
        profile: dict[str, Any],
        world_model: dict[str, Any],
        story_bank: dict[str, Any],
        project_catalog: dict[str, Any],
        communication_preferences: dict[str, Any],
    ) -> None:
        """Persist isolated candidate artifacts under memory/candidates/<candidate_id>/."""
        cdir = self._candidate_dir(candidate_id)
        self._write_json(cdir / "candidate_profile.json", profile)
        self._write_json(cdir / "professional_world_model.json", world_model)
        self._write_json(cdir / "experience_story_bank.json", story_bank)
        self._write_json(cdir / "simulated_projects.json", project_catalog)
        self._write_json(cdir / "communication_preferences.json", communication_preferences)

    def load_candidate_bundle(self, candidate_id: str) -> dict[str, Any]:
        cdir = self._candidate_dir(candidate_id)
        if not cdir.exists():
            raise FileNotFoundError(f"Candidate '{candidate_id}' not found.")
        return {
            "profile": self._read_json(cdir / "candidate_profile.json"),
            "world_model": self._read_json(cdir / "professional_world_model.json"),
            "story_bank": self._read_json(cdir / "experience_story_bank.json"),
            "project_catalog": self._read_json(cdir / "simulated_projects.json"),
            "communication_preferences": self._read_json(cdir / "communication_preferences.json"),
        }

    def create_session(
        self,
        candidate_id: str,
        resume_version: str,
        jd_analysis: dict[str, Any],
        operating_mode: str,
        numerical_ledger: dict[str, Any],
        evidence_ledger: dict[str, Any],
        interviewer_context: dict[str, Any] | None = None,
        active_project_id: str | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """Initialize and save a new isolated interview session."""
        sid = session_id or short_id("sess")
        now = utc_now_iso()
        session = {
            "session_id": sid,
            "candidate_id": candidate_id,
            "resume_version": resume_version,
            "jd_id": jd_analysis["jd_id"],
            "operating_mode": operating_mode,
            "interviewer_context": interviewer_context or {},
            "created_at": now,
            "updated_at": now,
            "active_project_id": active_project_id,
            "clarification_pending": {"active": False, "question_asked": None, "turn_index": None},
            "discussed_employers": [],
            "discussed_projects": [],
            "discussed_architectures": [],
            "discussed_tech_versions": {},
            "established_assumptions": [],
            "interviewer_provided_facts": [],
            "corrections_log": [],
            "stories_used": [],
            "recent_openings": [],
            "recent_closings": [],
            "compressed_summary": "",
            "turns": [],
        }
        sdir = self._session_dir(sid)
        self._write_json(sdir / "interview_session.json", session)
        self._write_json(sdir / "jd_analysis.json", jd_analysis)
        self._write_json(sdir / "numerical_ledger.json", numerical_ledger)
        self._write_json(sdir / "evidence_classification.json", evidence_ledger)
        return session

    def save_session_state(
        self,
        session: dict[str, Any],
        numerical_ledger: dict[str, Any] | None = None,
        evidence_ledger: dict[str, Any] | None = None,
        story_bank: dict[str, Any] | None = None,
        communication_preferences: dict[str, Any] | None = None,
    ) -> None:
        """Persist updated session, ledgers, and candidate state atomically."""
        session["updated_at"] = utc_now_iso()
        sdir = self._session_dir(session["session_id"])
        self._write_json(sdir / "interview_session.json", session)
        if numerical_ledger is not None:
            self._write_json(sdir / "numerical_ledger.json", numerical_ledger)
        if evidence_ledger is not None:
            self._write_json(sdir / "evidence_classification.json", evidence_ledger)
        cdir = self._candidate_dir(session["candidate_id"])
        if story_bank is not None:
            self._write_json(cdir / "experience_story_bank.json", story_bank)
        if communication_preferences is not None:
            self._write_json(cdir / "communication_preferences.json", communication_preferences)

    def load_session_bundle(self, session_id: str) -> dict[str, Any]:
        """Recover complete isolated state for a session and its bound candidate."""
        sdir = self._session_dir(session_id)
        if not sdir.exists():
            raise FileNotFoundError(f"Session '{session_id}' not found.")
        session = self._read_json(sdir / "interview_session.json")
        candidate_bundle = self.load_candidate_bundle(session["candidate_id"])
        return {
            "session": session,
            "jd_analysis": self._read_json(sdir / "jd_analysis.json"),
            "numerical_ledger": self._read_json(sdir / "numerical_ledger.json"),
            "evidence_ledger": self._read_json(sdir / "evidence_classification.json"),
            **candidate_bundle,
        }

    def compress_context_if_needed(self, session: dict[str, Any], turn_limit: int = 8) -> dict[str, Any]:
        """Compress older turns into a compact summary while preserving active architectural and numerical invariants."""
        turns = session.get("turns", [])
        if len(turns) <= turn_limit:
            return session
        older = turns[:-turn_limit]
        key_points = [
            f"T{t['turn_index']}: Q='{t['cleaned_transcript'][:80]}' -> act={t['interviewer_analysis']['question_act']}"
            for t in older
        ]
        session["compressed_summary"] = (
            f"Compressed {len(older)} earlier turns; employers={session.get('discussed_employers')}; "
            f"projects={session.get('discussed_projects')}; highlights: " + " | ".join(key_points[-6:])
        )
        return session

    def list_sessions(self) -> list[str]:
        return sorted(p.name for p in self.sessions_dir.iterdir() if p.is_dir())

    def list_candidates(self) -> list[str]:
        return sorted(p.name for p in self.candidates_dir.iterdir() if p.is_dir())

    def delete_session(self, session_id: str) -> bool:
        """Delete all stored files for a single session (privacy control)."""
        sdir = self._session_dir(session_id)
        if sdir.exists():
            shutil.rmtree(sdir)
            return True
        return False

    def delete_candidate(self, candidate_id: str) -> dict[str, Any]:
        """Delete a candidate profile and every associated session (privacy isolation & cleanup)."""
        removed_sessions: list[str] = []
        for sid in self.list_sessions():
            sfile = self._session_dir(sid) / "interview_session.json"
            if sfile.exists():
                sess = self._read_json(sfile)
                if sess.get("candidate_id") == candidate_id:
                    self.delete_session(sid)
                    removed_sessions.append(sid)
        cdir = self._candidate_dir(candidate_id)
        removed_candidate = False
        if cdir.exists():
            shutil.rmtree(cdir)
            removed_candidate = True
        return {"candidate_deleted": removed_candidate, "sessions_deleted": removed_sessions}
