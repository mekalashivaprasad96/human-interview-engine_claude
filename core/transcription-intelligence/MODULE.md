# Transcription & Speech Intelligence Module

**Python Implementation:** `src/human_interview_engine/transcription_intelligence.py`

## Responsibility
Clean noisy speech-to-text transcripts using domain vocabulary, detect multi-question prompts, recognize non-question acknowledgments, and enforce the one-question clarification protocol.

## Core Rules
1. Normalize phonetic ASR errors (`cube control` -> `kubectl`, `kuberneties` -> `Kubernetes`, `pie torch` -> `PyTorch`, `open telemetry` -> `OpenTelemetry`, `v l l m` -> `vLLM`, `pee ninety nine` -> `p99`, etc.).
2. Collapse repeated stutters (`"the the"`) and verbal hesitation markers without altering core intent.
3. If the interviewer gave an acknowledgment or closing remark with no question, respond briefly (`"Got it."`) rather than fabricating a question.
4. When cut off or materially ambiguous, ask **one** concise clarifying question, set `clarification_pending: true`, and wait—never invent the interviewer's answer.
5. Split compound multi-part transcripts so every meaningful sub-question is answered.
