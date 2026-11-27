# Privacy & Authorized Use

## Local-First Processing & Isolation
- All runtime processing executes locally in Python with `allow_external_network: false` in `config/engine.default.json`.
- Each candidate's profile, world model, scenarios, and communication preferences reside strictly in `memory/candidates/<candidate_id>/`.
- Each interview session resides strictly in `memory/sessions/<session_id>/` and validates `candidate_id` ownership before loading state.
- Protected personal characteristics are never inferred (`protected_attributes_inferred: false`).

## Deletion Controls
- Delete one session: `PYTHONPATH=src python3 -m human_interview_engine delete-session --session-id <SESSION_ID>`
- Delete a candidate and every linked session: `PYTHONPATH=src python3 -m human_interview_engine delete-candidate --candidate-id <CANDIDATE_ID>`

## Authorized Use Boundary
HumanInterview Engine is built strictly for **mock interview practice, authentic interview preparation, coaching, and authorized accessibility/preparation workflows**. It deliberately contains **zero** stealth proctoring-bypass hooks, hidden overlays, covert audio capture, or disclosure evasion mechanisms.
