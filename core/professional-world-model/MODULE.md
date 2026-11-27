# Professional World Model Module

**Python Implementation:** `src/human_interview_engine/world_model.py`  
**Output Schema:** `schemas/professional_world_model.schema.json`

## Responsibility
Expand compressed resume signals into a coherent professional world model representing career trajectory, competency relationships, seniority calibration, transferable expertise, and realistic gaps.

## Core Rules
1. Calibrate seniority strictly (`junior`, `mid`, `senior`, `staff`, `principal`, `manager`, `director`, `executive`) from tenure, title progression, and ownership scope. Never inflate a junior candidate into staff/architect speech.
2. Separate technical, business, leadership, customer-facing, and operational competencies with source-employer traceability.
3. Construct a persistent `persona_profile` (maturity, voice register, ownership framing, humility markers) that remains stable across the entire session.
4. Explicitly set `protected_attributes_inferred: false`.
