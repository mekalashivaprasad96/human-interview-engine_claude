# Changelog

All notable changes to **HumanInterview Engine** are documented in this file.

## [Unreleased]
### Fixed
- Restored `SKILL.md`, `SYSTEM_PROMPT.md`, `README.md`, `CHANGELOG.md`, `evaluation/evaluator.py` and `importers/__init__.py`, which merge `78295f4` had replaced with documentation and code for an unimportable scaffold.
- `delete-session` / `delete-candidate` (and every memory read/write) reject IDs with path separators or `..`, and check the resolved path stays inside the memory root.
- `--mode` is validated against `config/operating_modes.json`; documented short aliases (`authentic`, `immersive`, ...) resolve to canonical modes and unknown modes are errors. Previously `authentic` silently behaved as immersive.
- `init` no longer crashes on resumes with no parseable job history; empty input and missing file paths are reported as errors. The CLI prints `error: ...` and exits 2 instead of a traceback.
- Instructions without a question mark ("Design a rate limiter...", "Introduce yourself.", ASR-style "so how many nodes") are treated as questions instead of acknowledgments.
- Authentic-mode numeric answers: no support-role framing for non-support candidates, no unrelated resume metric or pasted bullet text, and confirmed metrics read cleanly.
- The deterministic evaluator audits the transcript itself and penalises dismissed questions, repeated answers, stacked openings, pasted resume fragments, template seams and unanswered numeric questions.

### Removed
- Unimportable scaffold implementation: `core/*/*.py` (the `core/*/MODULE.md` guides remain), root `importers/*.py` classes, `evaluation/regression_tests.py`, `evaluation/benchmarks.py`, `adapters/{chatgpt,claude,claude_code}/adapter.py`, the hyphenated `schemas/*.json`, and the unused `config/settings.json`.

## [4.0.0] - 2026-11-26
### Added
- **Modular Cognitive Architecture (`core/*/MODULE.md` guides + `src/human_interview_engine/`):**
  - Candidate Intelligence Engine parsing plain-text, Markdown, and JSON resumes (including sparse resumes) without protected-attribute inference.
  - Professional World Model Builder calibrating seniority (`junior` through `executive`), career progression, competency graphs, transferable skills, and gaps.
  - Employer Intelligence Engine with 10 industry profiles and a curated `technology_timeline.json` chronology validator.
  - Job Description Analyzer identifying core vs. preferred skills, business/leadership/customer expectations, strengths, transferable bridges, and gaps.
  - Scenario Modeling & Experience Enrichment Engines generating chronologically valid multi-employer projects, failure/rollback stories, and stakeholder disagreement stories.
  - Numerical Intelligence Engine & Persistent Numerical Consistency Ledger verifying `nodes * gpus_per_node == total_gpus`, `gpu_hours`, baseline-to-final deltas, RPS daily extrapolations, availability downtime, and cost savings.
  - Speech & Transcription Intelligence repairing phonetic ASR errors, splitting multi-part questions, detecting non-question statements, and enforcing the one-question wait protocol.
  - Interviewer Intelligence, Dynamic Length Controller, and Human Communication Engine ensuring spoken-only output, contraction cadence, varied openings, and zero clichés/STAR headings.
  - Specialized Technical, Troubleshooting, System Design, Behavioral, GCA, Business/Executive, and Follow-Up/Pressure reasoning engines.
  - Evidence Classification System separating 10 evidence categories with explicit candidate confirmation promotion and strict `authentic_preparation` guards.
  - Internal Response Validator, Historical Interview Importer (ChatGPT, Claude, Text/Markdown, JSON), and Controlled Continuous Improvement Engine.
  - 21-dimension Evaluation Framework with deterministic scoring, independent-judge protocol, and blind human evaluation worksheet.
  - Platform adapters for Claude Code (`SKILL.md` / `agentskills.io`), Claude Projects/Skills, ChatGPT Custom GPTs (`<= 8,000` chars verified), ChatGPT Projects, ChatGPT Custom Instructions, and Universal Portable Prompt bundle.
  - Comprehensive unittest regression suite covering 25-turn adversarial consistency, sparse resumes, transcription errors, false premises, story diversity, multi-candidate isolation, and continuous improvement loops.
