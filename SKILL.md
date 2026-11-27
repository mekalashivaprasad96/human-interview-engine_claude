---
name: human-interview-engine
description: Universal Human Candidate Cognitive Intelligence System - Advanced AI-powered interview simulation engine
version: 4.0.0
author: HumanInterview Engine Team
license: MIT
tags: [interview, simulation, career, ai-assistant, preparation]
platforms: [claude-code, claude, chatgpt, custom-gpts]
---

# HumanInterview Engine 4.0 Skill

## Overview

HumanInterview Engine is a sophisticated AI-powered interview intelligence system that simulates realistic human candidate behavior during technical and professional interviews. Unlike conventional interview answer generators, this system builds a comprehensive professional world model from a candidate's resume and job description, then reasons and communicates like an experienced professional.

## Capabilities

- **Professional World Modeling**: Constructs comprehensive candidate profile from resume + job description
- **Employer Intelligence**: Understands industry context, business models, and technical environments
- **Experience Enrichment**: Builds coherent, technically detailed project scenarios with numerical consistency
- **Numerical Intelligence**: Maintains persistent numerical ledger with mathematical validation
- **Human Communication**: Natural spoken-language responses with appropriate personality and seniority
- **Interviewer Intelligence**: Adapts to recruiter, hiring manager, technical, executive, and panel interviews
- **Multi-Mode Operation**: Immersive simulation, authentic preparation, technical deep-dive, behavioral, system design, executive
- **Evidence Classification**: Tracks documented vs. inferred vs. simulated information
- **Session Memory**: Maintains consistency across extended interview conversations
- **Historical Learning**: Imports previous interviews to identify and fix recurring weaknesses

## Installation

### Claude Code
```bash
# Place the human-interview-engine folder in your .claude/skills/ directory
cp -r human-interview-engine ~/.claude/skills/human-interview-engine
```

### Claude (Web/Desktop)
Copy `SYSTEM_PROMPT.md` content into a Custom Instruction or Project Instruction.

### ChatGPT / Custom GPTs
Use `SYSTEM_PROMPT.md` as the Custom Instructions. Upload schema files as knowledge files.

## Usage

### Quick Start
1. Provide your resume (paste text or upload file)
2. Provide the target job description
3. Select operating mode (default: immersive simulation)
4. Begin asking interview questions

### Operating Modes
- `immersive` - Full fictional simulation for mock interviews
- `authentic` - Documented experience only for real preparation
- `technical` - Deep technical implementation focus
- `recruiter` - Screening-appropriate responses
- `hiring-manager` - Ownership and decision-making focus
- `behavioral` - STAR-based behavioral responses
- `system-design` - Architecture and scalability focus
- `executive` - Business outcomes and strategy focus
- `cognitive` - Problem-solving and reasoning focus
- `coaching` - Evaluation and feedback mode

### Commands
```
/interview init --resume <text> --jd <text> --mode immersive
/interview question "Tell me about a time you..."
/interview followup "What was the exact configuration?"
/interview mode technical
/interview evidence-status
/interview numerical-ledger
/interview import-history <transcript>
/interview evaluate
```

## Configuration

Edit `config/settings.json` to customize:
- Communication preferences
- Numerical precision defaults
- Evidence classification thresholds
- Answer length guidelines
- Platform-specific adapters

## Data Schemas

All structured data follows JSON schemas in `schemas/`:
- `candidate-profile.json`
- `professional-world-model.json`
- `experience-story-bank.json`
- `simulated-project.json`
- `numerical-ledger.json`
- `interview-session.json`
- `evidence-classification.json`
- `communication-preferences.json`

## Architecture

```
human-interview-engine/
├── SKILL.md                    # This file
├── SYSTEM_PROMPT.md            # Portable core instructions
├── README.md                   # Documentation
├── CHANGELOG.md                # Version history
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
├── importers/                  # Historical interview import
├── evaluation/                 # Regression tests & evaluation
├── tests/                      # Automated tests
├── examples/                   # Synthetic examples
└── docs/                       # Additional documentation
```

## Core Intelligence Modules

### Candidate Intelligence (`core/candidate-intelligence/`)
- Resume parsing and career chronology extraction
- Seniority determination and progression analysis
- Technical competency mapping
- Business competency identification
- Communication style inference

### Professional World Model (`core/professional-world-model/`)
- Employer timeline construction
- Industry context modeling
- Responsibility scope inference
- Transferable knowledge mapping
- Knowledge gap identification

### Employer Intelligence (`core/employer-intelligence/`)
- Industry-specific operational priorities
- Technology adoption timelines
- Regulatory and compliance context
- Organizational complexity modeling
- Customer expectation patterns

### Experience Enrichment (`core/experience-enrichment/`)
- Project scenario generation
- Technical architecture modeling
- Implementation detail synthesis
- Constraint and challenge modeling
- Outcome and metric generation

### Numerical Intelligence (`core/numerical-intelligence/`)
- Numerical ledger management
- Unit validation and conversion
- Derived metric calculation
- Consistency validation
- Precision appropriateness

### Human Communication (`core/human-communication/`)
- Natural language generation
- Personality-consistent phrasing
- Seniority-appropriate terminology
- Conversational rhythm control
- Audience adaptation

## Requirements

- Python 3.10+ (for validation scripts)
- Node.js 18+ (for test runner)
- Compatible LLM platform (Claude Code, Claude, ChatGPT, etc.)

## Testing

```bash
# Run regression tests
cd tests && python run_tests.py

# Run evaluation suite
cd evaluation && python evaluate.py
```

## Examples

See `examples/` for:
- Synthetic resumes (junior, mid, senior, staff, principal, manager, executive)
- Synthetic job descriptions across industries
- Sample interview transcripts
- Numerical ledger examples

## Version History

See `CHANGELOG.md` for detailed version history.

## License

MIT License - See LICENSE file for details.

## Contributing

See `CONTRIBUTING.md` for development guidelines.

## Support

- Documentation: `docs/`
- Issues: GitHub Issues
- Discussions: GitHub Discussions