"""Historical Interview Importer — parses ChatGPT, Claude, Markdown, Text, and JSON transcripts."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .models import short_id, utc_now_iso


class HistoricalInterviewImporter:
    """Imports historical interview transcripts, exports, evaluations, and corrections safely."""

    def import_file(self, path: str | Path) -> dict[str, Any]:
        """Parse an interview export or transcript file into normalized Q&A turn pairs."""
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Unavailable interview source: {p}")

        raw = p.read_text(encoding="utf-8")
        if p.suffix.lower() == ".json" or raw.lstrip().startswith(("{", "[")):
            try:
                payload = json.loads(raw)
                return self.import_json_payload(payload, source_name=str(p))
            except json.JSONDecodeError:
                pass
        return self.import_text_transcript(raw, source_name=str(p))

    def import_json_payload(self, payload: Any, source_name: str = "inline.json") -> dict[str, Any]:
        """Support ChatGPT exports, Claude exports, and structured engine session JSONs."""
        conversations: list[dict[str, Any]] = []

        # Case 1: ChatGPT export list of conversations with `mapping`
        if isinstance(payload, list) and payload and isinstance(payload[0], dict) and "mapping" in payload[0]:
            for conv in payload:
                msgs = self._extract_chatgpt_mapping(conv.get("mapping", {}))
                conversations.append(
                    {
                        "conversation_id": conv.get("id") or short_id("cgpt"),
                        "title": conv.get("title", "ChatGPT Export"),
                        "source_format": "chatgpt_export",
                        "turns": self._pair_messages(msgs),
                    }
                )
        elif isinstance(payload, dict) and "mapping" in payload:
            msgs = self._extract_chatgpt_mapping(payload.get("mapping", {}))
            conversations.append(
                {
                    "conversation_id": payload.get("id") or short_id("cgpt"),
                    "title": payload.get("title", "ChatGPT Export"),
                    "source_format": "chatgpt_export",
                    "turns": self._pair_messages(msgs),
                }
            )
        # Case 2: Claude export (list or dict with `chat_messages`)
        elif isinstance(payload, list) and payload and isinstance(payload[0], dict) and "chat_messages" in payload[0]:
            for conv in payload:
                msgs = [
                    {
                        "role": "interviewer" if m.get("sender") in ("human", "user") else "candidate",
                        "text": m.get("text") or self._join_claude_content(m.get("content")),
                    }
                    for m in conv.get("chat_messages", [])
                ]
                conversations.append(
                    {
                        "conversation_id": conv.get("uuid") or short_id("claude"),
                        "title": conv.get("name", "Claude Export"),
                        "source_format": "claude_export",
                        "turns": self._pair_messages(msgs),
                    }
                )
        elif isinstance(payload, dict) and "chat_messages" in payload:
            msgs = [
                {
                    "role": "interviewer" if m.get("sender") in ("human", "user") else "candidate",
                    "text": m.get("text") or self._join_claude_content(m.get("content")),
                }
                for m in payload.get("chat_messages", [])
            ]
            conversations.append(
                {
                    "conversation_id": payload.get("uuid") or short_id("claude"),
                    "title": payload.get("name", "Claude Export"),
                    "source_format": "claude_export",
                    "turns": self._pair_messages(msgs),
                }
            )
        # Case 3: Structured turns or messages
        elif isinstance(payload, dict) and ("turns" in payload or "messages" in payload):
            if "turns" in payload:
                turns = [
                    {
                        "turn_index": t.get("turn_index", idx + 1),
                        "question": t.get("question") or t.get("raw_input") or t.get("cleaned_transcript", ""),
                        "answer": t.get("answer") or t.get("candidate_response", ""),
                        "feedback": t.get("feedback", ""),
                        "evidence_status": "historical_ai_generated_unverified",
                    }
                    for idx, t in enumerate(payload.get("turns", []))
                ]
            else:
                msgs = [
                    {
                        "role": "interviewer" if m.get("role") in ("user", "interviewer", "human") else "candidate",
                        "text": str(m.get("content") or m.get("text") or ""),
                    }
                    for m in payload.get("messages", [])
                ]
                turns = self._pair_messages(msgs)
            conversations.append(
                {
                    "conversation_id": payload.get("session_id") or short_id("json"),
                    "title": payload.get("title", source_name),
                    "source_format": "structured_json",
                    "turns": turns,
                }
            )
        else:
            raise ValueError(f"Unrecognized JSON interview export format in {source_name}")

        return {
            "import_id": short_id("imp", source_name),
            "source_name": source_name,
            "imported_at": utc_now_iso(),
            "conversations": conversations,
            "verified_facts_auto_promoted": False,
        }

    def import_text_transcript(self, text: str, source_name: str = "transcript.txt") -> dict[str, Any]:
        """Parse plain-text or Markdown transcripts labeled Interviewer/Candidate or User/Assistant."""
        speaker_re = re.compile(
            r"^\s*(?:\*{0,2})(Interviewer|Question|Q|User|Human|Candidate|Answer|A|Assistant)(?:\*{0,2})\s*:\s*(.*)$",
            re.IGNORECASE,
        )
        messages: list[dict[str, str]] = []
        current_role: str | None = None
        buffer: list[str] = []

        def flush() -> None:
            if current_role and buffer:
                messages.append({"role": current_role, "text": "\n".join(buffer).strip()})

        for line in (text or "").splitlines():
            m = speaker_re.match(line)
            if m:
                flush()
                label = m.group(1).lower()
                current_role = "interviewer" if label in ("interviewer", "question", "q", "user", "human") else "candidate"
                rest = m.group(2).strip()
                buffer = [rest] if rest else []
            elif current_role is not None:
                buffer.append(line)
        flush()

        turns = self._pair_messages(messages)
        return {
            "import_id": short_id("imp", source_name),
            "source_name": source_name,
            "imported_at": utc_now_iso(),
            "conversations": [
                {
                    "conversation_id": short_id("txt", source_name),
                    "title": Path(source_name).stem,
                    "source_format": "text_transcript",
                    "turns": turns,
                }
            ],
            "verified_facts_auto_promoted": False,
        }

    @staticmethod
    def _extract_chatgpt_mapping(mapping: dict[str, Any]) -> list[dict[str, str]]:
        nodes: list[tuple[float, dict[str, str]]] = []
        for idx, node in enumerate(mapping.values()):
            msg = node.get("message") if isinstance(node, dict) else None
            if not msg:
                continue
            role = (msg.get("author") or {}).get("role")
            if role not in ("user", "assistant"):
                continue
            parts = (msg.get("content") or {}).get("parts") or []
            text = "\n".join(str(p) for p in parts if isinstance(p, str)).strip()
            if not text:
                continue
            ts = float(msg.get("create_time") or idx)
            nodes.append((ts, {"role": "interviewer" if role == "user" else "candidate", "text": text}))
        nodes.sort(key=lambda item: item[0])
        return [item[1] for item in nodes]

    @staticmethod
    def _join_claude_content(content: Any) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "\n".join(str(c.get("text", "")) for c in content if isinstance(c, dict)).strip()
        return ""

    @staticmethod
    def _pair_messages(messages: list[dict[str, str]]) -> list[dict[str, Any]]:
        turns: list[dict[str, Any]] = []
        pending_q: str | None = None
        turn_num = 1
        for msg in messages:
            if msg["role"] == "interviewer":
                if pending_q is not None:
                    turns.append(
                        {
                            "turn_index": turn_num,
                            "question": pending_q,
                            "answer": "",
                            "evidence_status": "historical_ai_generated_unverified",
                        }
                    )
                    turn_num += 1
                pending_q = msg["text"]
            elif msg["role"] == "candidate" and pending_q is not None:
                turns.append(
                    {
                        "turn_index": turn_num,
                        "question": pending_q,
                        "answer": msg["text"],
                        "evidence_status": "historical_ai_generated_unverified",
                    }
                )
                turn_num += 1
                pending_q = None
        return turns
