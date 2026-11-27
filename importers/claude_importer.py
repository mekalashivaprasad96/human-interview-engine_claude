"""
Claude Importer - Imports Claude conversation exports.
"""

import json
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
from .transcript_importer import InterviewTranscript


class ClaudeImporter:
    """Imports Claude conversation exports."""

    def __init__(self):
        pass

    def import_export(self, file_path: str) -> list[InterviewTranscript]:
        """Import Claude export (JSON)."""
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == '.json':
            return self._import_json(file_path)
        else:
            raise ValueError(f"Unsupported format: {suffix}")

    def _import_json(self, file_path: str) -> list[InterviewTranscript]:
        """Import from JSON file."""
        with open(file_path) as f:
            data = json.load(f)

        transcripts = []

        # Handle different possible formats
        if isinstance(data, list):
            # Array of conversations
            for conv in data:
                transcript = self._convert_conversation(conv)
                if transcript:
                    transcripts.append(transcript)
        elif isinstance(data, dict):
            if 'conversations' in data:
                for conv in data['conversations']:
                    transcript = self._convert_conversation(conv)
                    if transcript:
                        transcripts.append(transcript)
            elif 'uuid' in data or 'id' in data:
                # Single conversation
                transcript = self._convert_conversation(data)
                if transcript:
                    transcripts.append(transcript)

        return transcripts

    def _convert_conversation(self, conv: dict) -> Optional[InterviewTranscript]:
        """Convert a single Claude conversation to transcript."""
        messages = []

        # Try different possible structures
        chat_messages = []

        if 'chat_messages' in conv:
            chat_messages = conv['chat_messages']
        elif 'messages' in conv:
            chat_messages = conv['messages']
        elif 'conversation' in conv:
            chat_messages = conv['conversation']

        if not chat_messages:
            return None

        for msg in chat_messages:
            if not isinstance(msg, dict):
                continue

            role = msg.get('role') or msg.get('sender') or msg.get('author', '')
            content = msg.get('content') or msg.get('text') or msg.get('message', '')

            if not content:
                continue

            # Map roles
            role_lower = role.lower()
            if role_lower in ['user', 'human']:
                mapped_role = 'interviewer'
            elif role_lower in ['assistant', 'claude', 'model', 'ai']:
                mapped_role = 'candidate'
            else:
                mapped_role = role_lower

            messages.append({
                'role': mapped_role,
                'content': content,
                'timestamp': msg.get('timestamp') or msg.get('created_at') or msg.get('time'),
                'metadata': {
                    'original_role': role,
                }
            })

        if not messages:
            return None

        return InterviewTranscript(
            session_id=conv.get('uuid') or conv.get('id') or 'claude_import',
            source='claude',
            candidate_name='',
            job_title=conv.get('title') or conv.get('name', ''),
            date=str(conv.get('created_at') or conv.get('created') or ''),
            messages=messages,
            metadata={
                'original_id': conv.get('uuid') or conv.get('id'),
                'title': conv.get('title') or conv.get('name'),
            }
        )

    def filter_interview_conversations(self, transcripts: list[InterviewTranscript],
                                        keywords: list = None) -> list[InterviewTranscript]:
        """Filter conversations that appear to be interview-related."""
        if keywords is None:
            keywords = [
                'interview', 'resume', 'job', 'position', 'role',
                'experience', 'project', 'technical', 'behavioral',
                'system design', 'coding', 'algorithm', 'debug',
            ]

        filtered = []
        for t in transcripts:
            # Check title
            title = t.metadata.get('title', '').lower()
            if any(kw in title for kw in keywords):
                filtered.append(t)
                continue

            # Check first few messages
            for msg in t.messages[:5]:
                content = msg.get('content', '').lower()
                if any(kw in content for kw in keywords):
                    filtered.append(t)
                    break

        return filtered