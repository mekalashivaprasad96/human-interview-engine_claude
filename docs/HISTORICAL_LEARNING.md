# Historical Interview Learning & Continuous Improvement

## Supported Import Formats
- **ChatGPT `conversations.json`** (traverses `mapping` DAG nodes by timestamp)
- **Claude conversation JSON** (`chat_messages` arrays)
- **Plain Text / Markdown transcripts** (`Interviewer:` / `Candidate:`, `User:` / `Assistant:`, `Q:` / `A:`)
- **Structured JSON session logs** (`turns` or `messages`)

## Failure Diagnosis Rules
- `ContinuousImprovementEngine.analyze_imported_history()` classifies 24 shortcoming types across two strict lists:
  - `observed_transcript_evidence`: Directly quoted defects (e.g., `"based on the resume"`, STAR labels, missed math on quantitative questions, agreeing with false premises, failure to wait after clarifying question).
  - `inferred_weaknesses`: Patterns inferred from context (e.g., probable missing business framing or repeated story theme).
- Unavailable/missing files raise `FileNotFoundError`; the engine never pretends to have analyzed unavailable interviews.
- Imported historical AI answers are tagged `historical_ai_generated_unverified` and are **never** auto-promoted to verified candidate facts.

## Controlled Update Workflow
1. Import transcript + explicit user feedback (`import-history`).
2. Generate executable `regression_cases` and `proposed_rules`.
3. Run regression tests & evaluator against baseline score.
4. Persist rules into `communication_preferences.json` via `apply_validated_rules()` **only** when candidate validation score is >= baseline score.
