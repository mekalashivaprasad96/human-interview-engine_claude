# Job Description Analysis Module

**Python Implementation:** `src/human_interview_engine/jd_analyzer.py`  
**Output Schema:** `schemas/jd_analysis.schema.json`

## Responsibility
Analyze target job descriptions beyond surface keyword matching to surface expected seniority, business/customer/leadership expectations, deep-dive topics, strengths, transferable adjacent skills, and genuine gaps.

## Core Rules
1. Separate `core_technical_competencies` from `preferred_technical_competencies`.
2. Distinguish `candidate_strengths` (verified overlap), `transferable_skills` (adjacent fundamentals, e.g., Docker/EKS -> Kubernetes, Prometheus/Jaeger -> OpenTelemetry), and `candidate_gaps`.
3. Never claim the candidate possesses a JD-listed gap skill merely because the JD asks for it.
4. Do not stuff JD buzzwords artificially into spoken responses.
