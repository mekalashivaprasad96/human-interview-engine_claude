# Candidate Intelligence Module

**Python Implementation:** `src/human_interview_engine/candidate_intelligence.py`  
**Output Schema:** `schemas/candidate_profile.schema.json`

## Responsibility
Parse structured or unstructured candidate resumes (even sparse 5-line resumes) into a normalized `CandidateProfile` without inventing employers, dates, degrees, certifications, or verified metrics.

## Core Rules
1. Extract career chronology, role titles, date ranges, duration months, explicit skills, education, certifications, and documented quantitative metrics.
2. Flag sparse resumes (`is_sparse_resume: true`) automatically rather than refusing initialization or asking exhaustive questionnaires.
3. Never infer protected personal characteristics (race, gender, age, religion, nationality, disability).
4. Tag every resume-extracted accomplishment as `documented_candidate_experience` or `verified_numerical_information`.
