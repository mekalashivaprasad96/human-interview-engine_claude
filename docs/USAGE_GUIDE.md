# Usage Guide

## Step 1: Initialize Session
Provide a resume file (`.md`, `.txt`, or `.json`) and a target job description:
```bash
PYTHONPATH=src python3 -m human_interview_engine init \
  --resume examples/resumes/senior_ai_infra_resume.md \
  --jd examples/job-descriptions/senior_ai_infra_jd.md \
  --mode immersive_simulation
```
Notice the engine outputs only initialization status and waits for Question 1 without generating unsolicited answers.

## Step 2: Conduct Interview Turns
```bash
PYTHONPATH=src python3 -m human_interview_engine turn \
  --session-id <SESSION_ID> \
  --question "How did you verify rollback safety on the inference cluster?"
```

### Switching Modes Mid-Session
```bash
PYTHONPATH=src python3 -m human_interview_engine turn \
  --session-id <SESSION_ID> \
  --mode coaching_evaluation \
  --question "Evaluate my last answer and show any unverified simulation details."
```

## Step 3: Confirm Real Candidate Facts (`authentic_preparation`)
Promote simulated or newly confirmed metrics/experiences only when explicitly verified by the candidate:
```bash
PYTHONPATH=src python3 -m human_interview_engine confirm \
  --session-id <SESSION_ID> \
  --claim "Operated a 12-node Triton cluster in production" \
  --metric-name nodes \
  --metric-value 12 \
  --metric-unit nodes
```

## Step 4: Inspect Ledgers & Delete Data
```bash
PYTHONPATH=src python3 -m human_interview_engine inspect-ledger --session-id <SESSION_ID>
PYTHONPATH=src python3 -m human_interview_engine delete-session --session-id <SESSION_ID>
PYTHONPATH=src python3 -m human_interview_engine delete-candidate --candidate-id <CANDIDATE_ID>
```
