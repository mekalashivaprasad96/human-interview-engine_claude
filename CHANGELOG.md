# Changelog

All notable changes to **HumanInterview Engine** are documented in this file.

## [4.0.0] - 2026-11-26
### Added
- **Modular Cognitive Architecture (`core/` + `src/human_interview_engine/`):**
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
