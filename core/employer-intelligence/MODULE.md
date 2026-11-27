# Employer Intelligence Module

**Python Implementation:** `src/human_interview_engine/employer_intelligence.py`  
**Registry Config:** `config/industry_profiles.json`, `config/technology_timeline.json`

## Responsibility
Ground every role in its employer's actual industry constraints, regulatory requirements, security posture, change management expectations, and technology era.

## Core Rules
1. Map industries accurately: Retail (seasonal traffic/checkout availability), Fintech (SOX/PCI/ledger determinism), Healthcare (HIPAA/PHI safety), Cloud (multi-tenant blast radius/SLOs), Semiconductors (silicon/UVM/timing precision), Mobile (cold start/frame budget/offline sync), Enterprise Customer/TAM (adoption/SLA trust).
2. Validate every technology claim against `config/technology_timeline.json` and the project's `end_year`. Reject anachronisms (e.g., Kubernetes prior to 2014, OpenTelemetry prior to 2019, vLLM prior to 2023).
3. Distinguish company-wide public technology from confirmed individual candidate hands-on usage.
4. Align role scope (`support`, `implementation`, `architecture`, `advisory`, `management`, `executive`).
