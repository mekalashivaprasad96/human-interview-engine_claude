# Scenario Modeling Module

**Python Implementation:** `src/human_interview_engine/scenario_modeling.py`  
**Output Schema:** `schemas/simulated_project.schema.json`

## Responsibility
Construct deep, technically coherent project models anchored to actual employers and employment dates so sustained 20+ turn follow-up questioning remains consistent.

## Core Rules
1. Every project models: business objective, architecture, components, era-valid stack, dependencies, scale metrics, team structure, personal contributions, decisions + alternatives + trade-offs, constraints, failures, testing methodology, rollback plan, and lessons learned.
2. Automatically register all project scale and baseline/final metrics into `NumericalLedger`.
3. Allow candidate overrides/confirmations via `confirm_candidate_detail()` without auto-promoting generated details.
