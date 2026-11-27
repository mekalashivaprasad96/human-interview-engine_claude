# Response Validation & Evidence Classification Module

**Python Implementation:** `src/human_interview_engine/validators.py`, `src/human_interview_engine/evidence_classifier.py`

## Responsibility
Enforce internal quality gates before any response leaves the engine and strictly isolate the 10 evidence categories.

## Hard Gates
- Zero resume/document/AI leaks (`"based on the resume"`, `"as an AI"`, `"you uploaded"`).
- Zero spoken STAR headers or coaching meta-text during interview simulation/prep.
- Zero contradictions with `NumericalLedger`.
- Zero technology timeline anachronisms relative to project `end_year`.
- Strict `authentic_preparation` boundary: simulated details remain `fictional_simulation_scenario` unless explicitly confirmed by the candidate.
- Clarifying question wait rule: ask one concise question and stop.
