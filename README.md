# HumanInterview Engine 4.0

**Universal Human Candidate Cognitive Intelligence System**

An advanced, reusable, portable AI-powered interview intelligence system that simulates the professional reasoning, communication, technical judgment, and conversational behavior of a realistic human candidate.

## What Makes This Different

| Conventional Tools | HumanInterview Engine |
|-------------------|----------------------|
| Generic answer templates | Professional world model from resume + JD |
| Keyword matching | Employer & industry intelligence |
| Static responses | Dynamic numerical ledger with consistency |
| One-size-fits-all | 10 operating modes (recruiter → executive) |
| AI-sounding output | Natural human communication engine |
| No memory | Persistent session memory & follow-up consistency |
| No learning | Historical interview import & regression testing |

## Quick Start

### 1. Install

```bash
# Clone or copy to your preferred location
git clone <repo> human-interview-engine
cd human-interview-engine
```

### 2. Initialize

Provide your resume and target job description:

```
Resume: [paste your resume text or upload file]

Job Description: [paste the target JD text]

Mode: immersive (default) | authentic | technical | recruiter | hiring-manager | behavioral | system-design | executive | cognitive | coaching
```

### 3. Interview

Ask questions naturally:

> "Tell me about a time you had to debug a production issue under pressure."

> "Walk me through the architecture of the payment system you mentioned."

> "How many requests per second was that handling?"

> "What would you do differently if you rebuilt it today?"

The system responds as the candidate — naturally, consistently, with technical depth appropriate to the question and interviewer.

## Operating Modes

| Mode | Use Case | Characteristics |
|------|----------|-----------------|
| `immersive` | Mock interview practice | Full scenario generation, fictional but consistent details |
| `authentic` | Real interview prep | Documented experience only, factual integrity |
| `technical` | Technical deep-dive | Implementation focus, configuration specifics |
| `recruiter` | Phone screens | Concise, qualification-focused |
| `hiring-manager` | Hiring manager rounds | Ownership, decisions, team dynamics |
| `behavioral` | Behavioral interviews | STAR reasoning, failures, growth, diverse stories |
| `system-design` | Architecture interviews | Requirements → design → trade-offs → operations |
| `executive` | Leadership interviews | Business outcomes, strategy, financial impact |
| `cognitive` | Problem-solving rounds | Structured reasoning, calculations, practical recommendations |
| `coaching` | Self-evaluation | Specific feedback, weakness identification |

## Core Capabilities

### Professional World Modeling
Builds a comprehensive model of the candidate's career — not just resume bullets. Infers employer contexts, industry constraints, technology timelines, responsibility scopes, and transferable knowledge.

### Numerical Intelligence
Maintains a persistent numerical ledger. When you say "16 nodes with 8 GPUs each," the system knows that's 128 GPUs, and 128 GPUs × 48 hours = 6,144 GPU-hours. Follow-ups stay mathematically consistent.

### Experience Enrichment
Constructs detailed, technically coherent project scenarios: architecture, stack, scale, decisions, constraints, challenges, testing, operations, metrics, outcomes. Sustains 20+ follow-up questions on the same project without contradiction.

### Human Communication
Speaks like a professional: varied sentences, natural transitions, appropriate contractions, seniority-matched vocabulary, audience adaptation (recruiter ≠ architect ≠ executive). No robotic patterns, no "That's a great question" reflex.

### Interviewer Intelligence
Recognizes interviewer type and intent. Adapts depth, jargon, and focus. Handles pressure, challenges, corrections, interruptions, and multi-question transcripts.

### Evidence Integrity
Tracks every claim's provenance: documented, confirmed, calculated, inferred, simulated. Never presents fictional experience as verified fact in authentic mode. Internal tracking only — never exposed in spoken output.

## Project Structure

```
human-interview-engine/
├── SKILL.md                    # Skill manifest for Claude Code
├── SYSTEM_PROMPT.md            # Portable core instructions
├── README.md                   # This file
├── CHANGELOG.md                # Version history
├── LICENSE                     # MIT License
├── config/
│   └── settings.json           # Runtime configuration
├── core/                       # Intelligence modules
│   ├── candidate-intelligence/
│   ├── professional-world-model/
│   ├── employer-intelligence/
│   ├── job-description-analysis/
│   ├── experience-enrichment/
│   ├── scenario-modeling/
│   ├── numerical-intelligence/
│   ├── human-communication/
│   ├── interviewer-intelligence/
│   ├── transcription-intelligence/
│   ├── technical-reasoning/
│   ├── behavioral-reasoning/
│   ├── business-intelligence/
│   ├── follow-up-intelligence/
│   └── response-validation/
├── memory/                     # Session persistence
├── schemas/                    # JSON schemas
├── adapters/                   # Platform adapters
│   ├── chatgpt/
│   ├── claude/
│   └── claude-code/
├── importers/                  # Historical interview import
├── evaluation/                 # Regression tests & evaluation
├── tests/                      # Automated tests
├── examples/                   # Synthetic examples
└── docs/                       # Additional documentation
```

## Configuration

Edit `config/settings.json`:

```json
{
  "communication": {
    "style": "natural",
    "contractions": true,
    "verbosity": "adaptive",
    "personality": "inferred"
  },
  "numerical": {
    "precision": "appropriate",
    "units": "metric",
    "false_precision_prevention": true
  },
  "evidence": {
    "strict_mode": false,
    "simulation_labeling": "internal_only"
  },
  "session": {
    "memory_retention": "full",
    "context_compression": true
  }
}
```

## Platform Deployment

### Claude Code (Skill)
```bash
cp -r human-interview-engine ~/.claude/skills/human-interview-engine
# Then in Claude Code: /skill human-interview-engine
```

### Claude (Web/Desktop)
Copy `SYSTEM_PROMPT.md` into Custom Instructions or Project Instructions.

### ChatGPT / Custom GPTs
Use `SYSTEM_PROMPT.md` as Custom Instructions. Upload `schemas/*.json` as knowledge files.

### Other Platforms
Use `SYSTEM_PROMPT.md` as the base instruction. Adapt `adapters/<platform>/` as needed.

## Examples

See `examples/`:
- `resumes/` — Junior, mid, senior, staff, principal, manager, executive across industries
- `job-descriptions/` — SWE, SRE, ML, security, data, PM, TAM, SA, EM, director, VP
- `transcripts/` — Sample interview conversations
- `numerical-ledgers/` — Example ledger states

## Testing

```bash
# Run regression tests
cd tests && python run_tests.py

# Run evaluation suite
cd evaluation && python evaluate.py
```

## Historical Learning

Import previous interviews to identify and fix recurring weaknesses:

```
/interview import-history transcript.json
/interview import-history chatgpt-export.zip
/interview import-history claude-export.json
```

The system analyzes: robotic communication, weak numerical reasoning, insufficient technical depth, generic explanations, ownership confusion, consistency failures, etc. — then updates intelligence modules and runs regression tests.

## Privacy

- Local-first processing
- No unauthorized external transmission
- Candidate data isolation
- Deletion controls for profiles/sessions
- No stealth/bypass mechanisms

## Requirements

- Python 3.10+ (validation scripts)
- Node.js 18+ (test runner)
- Compatible LLM platform

## License

MIT License — see `LICENSE` file.

## Contributing

See `CONTRIBUTING.md` for development guidelines.

## Changelog

See `CHANGELOG.md` for version history.

## Support

- Documentation: `docs/`
- Issues: GitHub Issues
- Discussions: GitHub Discussions