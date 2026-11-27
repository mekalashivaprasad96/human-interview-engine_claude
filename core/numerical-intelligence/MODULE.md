# Numerical Intelligence & Consistency Ledger Module

**Python Implementation:** `src/human_interview_engine/numerical_engine.py`, `src/human_interview_engine/numerical_ledger.py`  
**Output Schema:** `schemas/numerical_ledger.schema.json`

## Responsibility
Understand mathematical relationships, answer quantitative questions directly with units and scope, explain calculation methodology, and enforce zero contradictions across turns.

## Core Invariants
1. Enforce deterministic relationships:
   - `nodes * gpus_per_node == total_gpus`
   - `total_gpus * allocation_hours == gpu_hours`
   - `((final_ms - baseline_ms) / baseline_ms) * 100 == latency_reduction_pct`
   - `throughput_rps * 86400 == daily_requests`
   - `(1 - availability_pct / 100) * 43200 == monthly_downtime_minutes`
   - `monthly_cost_savings_usd * 12 == annual_cost_savings_usd`
2. When asked "how did you calculate/measure that?", state the formula, baseline, final value, and telemetry method—never merely repeat the output figure.
3. In `authentic_preparation` mode, separate `verified_numerical_information` and `calculated_numerical_information` from `illustrative_estimate` and refuse to invent historical numbers.
4. Catch and politely correct inconsistent interviewer math challenges (e.g., 16 nodes * 8 GPUs * 48h = 6,144 GPU-hours, not 5,000).
