# HumanInterview Engine 4.0

**Universal Human Candidate Cognitive Intelligence System**

HumanInterview Engine is a modular, portable, local-first AI interview intelligence runtime and skill package designed to simulate the lived technical reasoning, numerical consistency, conversational adaptability, and natural first-person speech of an authentic human candidate.

Unlike template libraries or resume-reading chatbots, HumanInterview Engine separates **structured professional world modeling, numerical consistency ledgers, chronology validation, and evidence integrity** from **natural spoken delivery**.

---

## Core Capabilities

- **Minimum-Input Initialization:** Starts cleanly from just a candidate resume and target job description (supports optional notes, company, interviewer persona, and operating mode), initializing silently and waiting for Question 1.
- **Professional World Model:** Expands compressed resume bullets into career trajectory, employer industry context, calibrated seniority (`junior`–`executive`), competency graphs, transferable skills, and honest experience gaps—without inferring protected personal characteristics.
- **Employer & Technology Chronology Intelligence:** Models industry realities (Retail, Fintech, Healthcare, Cloud, AI/ML, Semiconductor, Mobile, Cybersecurity, Telecom, Enterprise TAM/SA) and rejects anachronistic technology claims against employment dates.
- **Persistent Numerical Consistency Ledger:** Enforces exact arithmetic relationships (`nodes * gpus_per_node = total_gpus`, `total_gpus * hours = gpu_hours`, baseline-to-final deltas, `RPS * 86,400`, availability downtime budgets, annualized cost savings) across 20+ consecutive follow-up turns.
- **Strict Evidence Classification:** Separates documented/candidate-confirmed experience and verified/calculated metrics from fictional simulation scenarios and illustrative estimates. Never auto-promotes simulated details into verified facts.
- **Speech & Transcription Repair + Interviewer Adaptation:** Normalizes phonetic ASR errors (`cube control` -> `kubectl`, `pie torch` -> `PyTorch`, `open telemetry` -> `OpenTelemetry`), handles non-question acknowledgments, executes the one-question clarification wait protocol, answers multi-part prompts, and politely challenges false interviewer premises.
- **Historical Transcript Importer & Continuous Improvement:** Ingests ChatGPT exports, Claude exports, Markdown/text transcripts, and JSON session logs; diagnoses 24 failure modes (distinguishing direct transcript evidence from inferred weaknesses); generates regression tests; and commits rule updates only after regression validation passes.
- **21-Dimension Evaluation Framework:** Deterministic rubric checks, response latency tracking, independent-judge protocol, and blind human evaluation worksheets.

---

## Quick Start

### 1. Run via Python CLI (Zero External Dependencies, Python 3.9+)

```bash
# Initialize an isolated session (waits for first question)
PYTHONPATH=src python3 -m human_interview_engine init \
  --resume examples/resumes/senior_ai_infra_resume.md \
  --jd examples/job-descriptions/senior_ai_infra_jd.md \
  --mode immersive_simulation

# Ask interview questions
PYTHONPATH=src python3 -m human_interview_engine turn \
  --session-id <SESSION_ID> \
  --question "Walk me through how you reduced p99 latency on the GPU inference platform."

# Follow up numerically
PYTHONPATH=src python3 -m human_interview_engine turn \
  --session-id <SESSION_ID> \
  --question "How many nodes and GPUs did that cluster run, and what does 48 hours of stress testing equal in GPU-hours?"

# Inspect persisted numerical and evidence ledgers
PYTHONPATH=src python3 -m human_interview_engine inspect-ledger --session-id <SESSION_ID>
```

### 2. Run the Automated Regression & Evaluation Suite

```bash
python3 -m unittest discover -s tests -v
```

### 3. Deploy to Your Platform
- **Claude Code / Open Agent Skills:** `bash adapters/claude-code/install.sh personal` (or `project` / `agents`)
- **Claude.ai Projects / Claude Skills API:** See `adapters/claude/README.md` (`python3 adapters/claude/package_claude_skill.py`)
- **ChatGPT Custom GPTs / Projects / Custom Instructions:** See `adapters/chatgpt/README.md` (`custom-gpt-instructions.md` strictly <= 8,000 chars)
- **Universal Portable Prompt Bundle:** `adapters/universal/PORTABLE_PROMPT_BUNDLE.md`

---

## Documentation Index
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Installation Guide](docs/INSTALLATION.md)
- [Usage Guide](docs/USAGE_GUIDE.md)
- [Platform Compatibility Matrix](docs/PLATFORM_COMPATIBILITY.md)
- [Historical Learning & Regression Workflow](docs/HISTORICAL_LEARNING.md)
- [Evaluation Guide](docs/EVALUATION_GUIDE.md)
- [Privacy & Authorized Use](docs/PRIVACY_AND_ETHICS.md)
- [Known Limitations](docs/KNOWN_LIMITATIONS.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
