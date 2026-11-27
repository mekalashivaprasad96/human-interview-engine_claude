# Interview Memory & Privacy Isolation

This directory stores local-first runtime state isolated per `candidate_id` and `session_id`:

- `candidates/<candidate_id>/` — `candidate_profile.json`, `professional_world_model.json`, `experience_story_bank.json`, `simulated_projects.json`, `communication_preferences.json`
- `sessions/<session_id>/` — `interview_session.json`, `jd_analysis.json`, `numerical_ledger.json`, `evidence_classification.json`

## Privacy Controls
- Candidate data is **strictly isolated**; no cross-candidate leakage occurs across sessions.
- Delete a single session: `PYTHONPATH=src python3 -m human_interview_engine delete-session --session-id <id>`
- Delete a candidate and all linked sessions: `PYTHONPATH=src python3 -m human_interview_engine delete-candidate --candidate-id <id>`
- Private candidate and session subdirectories (`memory/candidates/*`, `memory/sessions/*`) should remain excluded from version control via `.gitignore`.
