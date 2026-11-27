"""Command-line interface for HumanInterview Engine 4.0."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .orchestrator import HumanInterviewEngine


_PATH_LIKE_SUFFIXES = (".md", ".markdown", ".txt", ".json", ".pdf", ".doc", ".docx", ".rtf", ".html")


def _looks_like_path(value: str) -> bool:
    """Heuristic: a single-line value that ends in a document extension or starts like a filesystem path."""
    v = value.strip()
    if not v or "\n" in v or len(v) > 4096:
        return False
    if v.lower().endswith(_PATH_LIKE_SUFFIXES):
        return True
    return v.startswith(("/", "./", "../", "~/", "~"))


def _read_text_or_arg(value: str, label: str) -> str:
    """Read a file if the value is an existing path; treat other values as raw text.

    A value that looks like a path but does not exist is an error, so a typo never
    silently becomes the resume or job-description text.
    """
    p = Path(value).expanduser()
    if p.is_file():
        return p.read_text(encoding="utf-8")
    if _looks_like_path(value):
        raise FileNotFoundError(f"{label} file not found: {value}")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="human-interview-engine", description="HumanInterview Engine 4.0 CLI")
    parser.add_argument("--memory-dir", default=None, help="Override memory directory path")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Initialize an interview session from resume and job description")
    p_init.add_argument("--resume", required=True, help="Path to resume file or raw text")
    p_init.add_argument("--jd", required=True, help="Path to job description file or raw text")
    p_init.add_argument("--mode", default="immersive_simulation", help="Operating mode")
    p_init.add_argument("--company", default=None, help="Target company name override")
    p_init.add_argument("--interviewer", default=None, help="Interviewer type hint")

    p_turn = sub.add_parser("turn", help="Process an interviewer question/utterance")
    p_turn.add_argument("--session-id", required=True, help="Active session ID")
    p_turn.add_argument("--question", required=True, help="Interviewer utterance or transcript")
    p_turn.add_argument("--interviewer", default=None, help="Optional interviewer type hint")
    p_turn.add_argument("--mode", default=None, help="Optional operating mode switch")
    p_turn.add_argument("--json", action="store_true", help="Print full structured turn JSON")

    p_confirm = sub.add_parser("confirm", help="Confirm real candidate experience or metric")
    p_confirm.add_argument("--session-id", required=True)
    p_confirm.add_argument("--claim", required=True)
    p_confirm.add_argument("--metric-name", default=None)
    p_confirm.add_argument("--metric-value", type=float, default=None)
    p_confirm.add_argument("--metric-unit", default=None)

    p_ledger = sub.add_parser("inspect-ledger", help="Inspect numerical and evidence ledgers")
    p_ledger.add_argument("--session-id", required=True)

    p_import = sub.add_parser("import-history", help="Import and diagnose historical interview transcripts")
    p_import.add_argument("--file", required=True, help="Path to transcript or ChatGPT/Claude JSON export")
    p_import.add_argument("--feedback", action="append", default=[], help="Optional explicit user feedback/correction")

    p_del_sess = sub.add_parser("delete-session", help="Delete a single session from memory")
    p_del_sess.add_argument("--session-id", required=True)

    p_del_cand = sub.add_parser("delete-candidate", help="Delete a candidate profile and all linked sessions")
    p_del_cand.add_argument("--candidate-id", required=True)

    args = parser.parse_args(argv)
    try:
        return _dispatch(args)
    except (ValueError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def _dispatch(args: argparse.Namespace) -> int:
    engine = HumanInterviewEngine(memory_dir=args.memory_dir)

    if args.command == "init":
        res = engine.initialize_session(
            resume=_read_text_or_arg(args.resume, "Resume"),
            job_description=_read_text_or_arg(args.jd, "Job description"),
            operating_mode=args.mode,
            company_name=args.company,
            interviewer_type=args.interviewer,
        )
        print(json.dumps(res, indent=2))
        return 0

    if args.command == "turn":
        res = engine.process_turn(
            session_id=args.session_id,
            interviewer_input=args.question,
            interviewer_hint=args.interviewer,
            mode_override=args.mode,
        )
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(res["response"])
        return 0

    if args.command == "confirm":
        res = engine.confirm_candidate_detail(
            session_id=args.session_id,
            claim=args.claim,
            metric_name=args.metric_name,
            metric_value=args.metric_value,
            metric_unit=args.metric_unit,
        )
        print(json.dumps(res, indent=2))
        return 0

    if args.command == "inspect-ledger":
        bundle = engine.memory.load_session_bundle(args.session_id)
        print(
            json.dumps(
                {
                    "numerical_ledger": bundle["numerical_ledger"],
                    "evidence_ledger": bundle["evidence_ledger"],
                },
                indent=2,
            )
        )
        return 0

    if args.command == "import-history":
        imported = engine.importer.import_file(args.file)
        report = engine.improvement_engine.analyze_imported_history(
            imported_bundle=imported,
            explicit_feedback=args.feedback,
        )
        print(json.dumps(report, indent=2))
        return 0

    if args.command == "delete-session":
        deleted = engine.memory.delete_session(args.session_id)
        print(json.dumps({"deleted": deleted, "session_id": args.session_id}, indent=2))
        return 0

    if args.command == "delete-candidate":
        res = engine.memory.delete_candidate(args.candidate_id)
        print(json.dumps(res, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
