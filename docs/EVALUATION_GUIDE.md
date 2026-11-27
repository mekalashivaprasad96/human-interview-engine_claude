# Evaluation Guide

HumanInterview Engine evaluates sessions across **21 transparent dimensions** defined in `evaluation/rubric.json`.

## Three Complementary Evaluation Layers
1. **Deterministic Verification (`evaluation/evaluator.py`):**
   - Verifies numerical ledger invariants, response-vs-ledger consistency, technology chronology, evidence integrity, dynamic answer-length adherence, zero resume leaks, zero STAR headings, and measured latency (`avg_ms` / `max_ms`).
2. **Independent Model Evaluation (`evaluation/independent_evaluator_prompt.md`):**
   - Pass an anonymized transcript (`generate_blind_evaluation_packet()`) to a *different* model or external judge callback (`external_judge_fn`) so the generating model never grades itself unchallenged.
3. **Blind Human Evaluation (`evaluation/blind_human_eval_template.md`):**
   - Reviewers grade anonymized transcripts blind to system version or candidate identity.

## Important Boundaries
- Evaluation measures conversational realism, technical consistency, and factual discipline. It **never** claims guaranteed interview passage or superiority over other candidates.
