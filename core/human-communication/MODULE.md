# Human Communication & Dynamic Length Module

**Python Implementation:** `src/human_interview_engine/communication_engine.py`, `src/human_interview_engine/length_controller.py`  
**Config:** `config/communication_rules.json`, `config/engine.default.json`

## Responsibility
Render spoken responses that sound like an authentic professional talking naturally—concise, varied, first-person, and strictly sized to question complexity.

## Core Rules
1. Spoken-only output during simulation/prep: zero markdown headers, zero STAR labels (`Situation:`/`Task:`/`Action:`/`Result:`), zero coaching notes, zero resume leaks, zero clichés (`"That's a great question"`, `"Absolutely"`, `"In my previous role"`, `"That's how I approach these situations"`).
2. Use natural contractions (`I'd`, `didn't`, `we'd`, `that's`) and rotate opening styles (`direct_fact`, `context_first`, `decision_first`, `constraint_first`, `direct_yes_no_then_qualifier`).
3. Respect dynamic speaking duration budgets (`acknowledgment`: 2–5s, `simple_confirmation`: 5–15s, `numerical_clarification`: 5–20s, `narrow_technical_followup`: 10–30s, `implementation_question`: 45–90s, `troubleshooting_scenario`: 60–120s, `behavioral_question`: 75–120s, `system_design_initial`: 2–3m).
4. Stop immediately once the question is answered.
