"""
Transcript Importer - Imports interview transcripts from various formats.
"""

import json
import re
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


@dataclass
class InterviewTranscript:
    session_id: str
    source: str  # json, chatgpt, claude, text
    candidate_name: str = ""
    job_title: str = ""
    company: str = ""
    date: str = ""
    messages: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class TranscriptImporter:
    """Imports interview transcripts from various formats."""

    def __init__(self):
        pass

    def import_file(self, file_path: str) -> InterviewTranscript:
        """Import transcript from file."""
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == '.json':
            return self._import_json(file_path)
        elif suffix == '.txt':
            return self._import_text(file_path)
        else:
            raise ValueError(f"Unsupported format: {suffix}")

    def _import_json(self, file_path: str) -> InterviewTranscript:
        """Import from JSON format."""
        with open(file_path) as f:
            data = json.load(f)

        # Handle different JSON structures
        if 'messages' in data:
            # Standard format
            return InterviewTranscript(
                session_id=data.get('session_id', 'imported'),
                source='json',
                candidate_name=data.get('candidate_name', ''),
                job_title=data.get('job_title', ''),
                company=data.get('company', ''),
                date=data.get('date', ''),
                messages=data['messages'],
                metadata=data.get('metadata', {}),
            )
        elif 'conversation' in data:
            # Alternative format
            return self._convert_conversation_format(data)
        else:
            # Try to infer
            return self._infer_from_json(data)

    def _import_text(self, file_path: str) -> InterviewTranscript:
        """Import from plain text format."""
        with open(file_path) as f:
            text = f.read()

        # Parse text transcript
        messages = self._parse_text_transcript(text)

        return InterviewTranscript(
            session_id='imported_text',
            source='text',
            messages=messages,
        )

    def _parse_text_transcript(self, text: str) -> list:
        """Parse plain text transcript into messages."""
        messages = []

        # Common patterns for speaker identification
        patterns = [
            r'^(Interviewer|Interviewee|Candidate|User|Assistant|Human|AI):\s*(.+)$',
            r'^\[(Interviewer|Interviewee|Candidate|User|Assistant|Human|AI)\]\s*(.+)$',
            r'^(Q|A):\s*(.+)$',
            r'^(\w+):\s*(.+)$',  # Generic speaker: text
        ]

        lines = text.split('\n')
        current_speaker = None
        current_text = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            matched = False
            for pattern in patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    # Save previous message
                    if current_speaker and current_text:
                        messages.append({
                            'role': current_speaker.lower(),
                            'content': ' '.join(current_text),
                        })

                    current_speaker = match.group(1)
                    current_text = [match.group(2)]
                    matched = True
                    break

            if not matched and current_speaker:
                # Continuation of previous speaker
                current_text.append(line)

        # Save last message
        if current_speaker and current_text:
            messages.append({
                'role': current_speaker.lower(),
                'content': ' '.join(current_text),
            })

        return messages

    def _convert_conversation_format(self, data: dict) -> InterviewTranscript:
        """Convert conversation format to standard."""
        messages = []
        for msg in data.get('conversation', []):
            if 'role' in msg and 'content' in msg:
                messages.append(msg)
            elif 'speaker' in msg and 'text' in msg:
                messages.append({
                    'role': msg['speaker'].lower(),
                    'content': msg['text'],
                })

        return InterviewTranscript(
            session_id=data.get('id', 'imported'),
            source='json',
            candidate_name=data.get('candidate', ''),
            job_title=data.get('role', ''),
            company=data.get('company', ''),
            date=data.get('date', ''),
            messages=messages,
        )

    def _infer_from_json(self, data: dict) -> InterviewTranscript:
        """Try to infer transcript from arbitrary JSON."""
        # Look for array of messages
        for key, value in data.items():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                if 'role' in value[0] or 'speaker' in value[0]:
                    messages = []
                    for msg in value:
                        if 'role' in msg and 'content' in msg:
                            messages.append(msg)
                        elif 'speaker' in msg and 'text' in msg:
                            messages.append({
                                'role': msg['speaker'].lower(),
                                'content': msg['text'],
                            })
                    return InterviewTranscript(
                        session_id=data.get('id', 'imported'),
                        source='json',
                        messages=messages,
                    )

        # Fallback
        return InterviewTranscript(
            session_id='imported',
            source='json',
            messages=[],
            metadata={'raw': data},
        )

    def import_multiple(self, file_paths: list) -> list[InterviewTranscript]:
        """Import multiple transcript files."""
        transcripts = []
        for path in file_paths:
            try:
                transcript = self.import_file(path)
                transcripts.append(transcript)
            except Exception as e:
                print(f"Failed to import {path}: {e}")
        return transcripts

    def export_standard(self, transcript: InterviewTranscript, file_path: str):
        """Export transcript to standard JSON format."""
        data = {
            'session_id': transcript.session_id,
            'source': transcript.source,
            'candidate_name': transcript.candidate_name,
            'job_title': transcript.job_title,
            'company': transcript.company,
            'date': transcript.date,
            'messages': transcript.messages,
            'metadata': transcript.metadata,
        }
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)