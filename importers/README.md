# Historical Interview Importer

The importer module (`src/human_interview_engine/importers.py`) ingests historical practice interviews, user corrections, and post-interview evaluations without auto-promoting unverified AI-generated scenarios into verified candidate history.

## Supported Sources
- **ChatGPT Exports** (`conversations.json` using the `mapping` node graph)
- **Claude Exports** (conversation JSON objects or arrays containing `chat_messages`)
- **Plain Text / Markdown Transcripts** (`Interviewer:` / `Candidate:`, `Q:` / `A:`, `User:` / `Assistant:`)
- **Structured JSON Session Logs** (`turns` or `messages` arrays)

## CLI Usage
```bash
PYTHONPATH=src python3 -m human_interview_engine import-history \
  --file examples/transcripts/flawed_historical_transcript.txt \
  --feedback "Make the answer natural" \
  --feedback "Do not make it too long"
```
