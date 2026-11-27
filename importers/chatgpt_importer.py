"""
ChatGPT Importer - Imports ChatGPT conversation exports.
"""

import json
import zipfile
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
from .transcript_importer import InterviewTranscript


@dataclass
class ChatGPTConversation:
    id: str
    title: str
    create_time: float
    update_time: float
    mapping: dict = field(default_factory=dict)
    current_node: str = ""


class ChatGPTImporter:
    """Imports ChatGPT conversation exports."""

    def __init__(self):
        pass

    def import_export(self, file_path: str) -> list[InterviewTranscript]:
        """Import ChatGPT export (JSON or ZIP)."""
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == '.zip':
            return self._import_zip(file_path)
        elif suffix == '.json':
            return self._import_json(file_path)
        else:
            raise ValueError(f"Unsupported format: {suffix}")

    def _import_zip(self, file_path: str) -> list[InterviewTranscript]:
        """Import from ZIP export (standard ChatGPT export format)."""
        transcripts = []

        with zipfile.ZipFile(file_path, 'r') as z:
            # Look for conversations.json
            if 'conversations.json' in z.namelist():
                with z.open('conversations.json') as f:
                    data = json.load(f)
                    return self._parse_conversations(data)

            # Fallback: try any JSON file
            for name in z.namelist():
                if name.endswith('.json'):
                    with z.open(name) as f:
                        try:
                            data = json.load(f)
                            if isinstance(data, list):
                                return self._parse_conversations(data)
                        except:
                            continue

        return transcripts

    def _import_json(self, file_path: str) -> list[InterviewTranscript]:
        """Import from JSON file."""
        with open(file_path) as f:
            data = json.load(f)

        if isinstance(data, list):
            return self._parse_conversations(data)
        elif isinstance(data, dict) and 'conversations' in data:
            return self._parse_conversations(data['conversations'])
        else:
            raise ValueError("Unrecognized ChatGPT JSON format")

    def _parse_conversations(self, conversations: list) -> list[InterviewTranscript]:
        """Parse ChatGPT conversations into transcripts."""
        transcripts = []

        for conv in conversations:
            if not isinstance(conv, dict):
                continue

            transcript = self._convert_conversation(conv)
            if transcript and transcript.messages:
                transcripts.append(transcript)

        return transcripts

    def _convert_conversation(self, conv: dict) -> Optional[InterviewTranscript]:
        """Convert a single ChatGPT conversation to transcript."""
        messages = []

        # ChatGPT format: mapping of nodes with message info
        mapping = conv.get('mapping', {})
        current_node = conv.get('current_node')

        if not mapping:
            return None

        # Traverse conversation tree
        node_ids = self._get_linear_nodes(mapping, current_node)

        for node_id in node_ids:
            node = mapping.get(node_id, {})
            message = node.get('message')

            if not message:
                continue

            author = message.get('author', {})
            role = author.get('role', '')
            content = message.get('content', {})
            parts = content.get('parts', [])

            if not parts:
                continue

            text = parts[0] if parts else ''

            # Map roles
            if role == 'user':
                mapped_role = 'interviewer'
            elif role == 'assistant':
                mapped_role = 'candidate'
            else:
                mapped_role = role

            messages.append({
                'role': mapped_role,
                'content': text,
                'timestamp': message.get('create_time'),
                'metadata': {
                    'node_id': node_id,
                    'original_role': role,
                }
            })

        if not messages:
            return None

        return InterviewTranscript(
            session_id=conv.get('id', 'chatgpt_import'),
            source='chatgpt',
            candidate_name='',
            job_title=conv.get('title', ''),
            date=str(conv.get('create_time', '')),
            messages=messages,
            metadata={
                'original_id': conv.get('id'),
                'title': conv.get('title'),
            }
        )

    def _get_linear_nodes(self, mapping: dict, current_node: str) -> list:
        """Get linear node sequence from conversation tree."""
        if not current_node or current_node not in mapping:
            return []

        nodes = []
        node_id = current_node

        while node_id and node_id in mapping:
            nodes.insert(0, node_id)
            node = mapping[node_id]
            node_id = node.get('parent')

        return nodes

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