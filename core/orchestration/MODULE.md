# Central Orchestration & Continuous Improvement Module

**Python Implementation:** `src/human_interview_engine/orchestrator.py`, `src/human_interview_engine/improvement_engine.py`, `src/human_interview_engine/session_memory.py`

## Responsibility
Coordinate session initialization (silent initialization waiting for Q1), per-turn routing, context compression, isolated memory persistence, historical failure importing, and gated regression rule updates.

## Controlled Improvement Loop
1. Import historical transcript or export (`importers.py`).
2. Separate `observed_transcript_evidence` from `inferred_weaknesses` across 24 failure modes.
3. Generate executable regression cases and candidate communication rules.
4. Commit rules to `communication_preferences.json` ONLY when validation scores meet or exceed baseline.
