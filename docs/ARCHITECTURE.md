# System Architecture

HumanInterview Engine 4.0 uses a **dual-layer modular architecture**:

1. **Portable Cognitive Modules (`core/*/MODULE.md` + `config/*.json` + `SYSTEM_PROMPT.md`):**
   Self-contained progressive-disclosure cognitive modules usable directly by LLMs across Claude Code, Claude Projects, ChatGPT Custom GPTs, and standalone prompt runtimes.
2. **Deterministic Runtime & State Engine (`src/human_interview_engine/` + `schemas/*.schema.json`):**
   Zero-dependency Python 3.9+ modules enforcing JSON Schema validity, mathematical ledger invariants, technology timeline checks, ASR normalization, session memory isolation, historical transcript diagnosis, and automated regression testing.

## Initialization Flow
1. `CandidateIntelligenceEngine.parse_resume` -> `CandidateProfile`
2. `JobDescriptionAnalyzer.analyze` -> `JobDescriptionAnalysis`
3. `EmployerIntelligenceEngine` + `ProfessionalWorldModelBuilder.build` -> `ProfessionalWorldModel`
4. `ScenarioModelingEngine.build_project_scenarios` -> `SimulatedProjectCatalog` + `NumericalLedger`
5. `ExperienceEnrichmentEngine.build_story_bank` -> `ExperienceStoryBank`
6. `EvidenceClassifier` + `SessionMemoryManager` persist isolated artifacts under `memory/candidates/<candidate_id>/` and `memory/sessions/<session_id>/`.

## Turn Pipeline
1. `TranscriptionIntelligence.interpret` -> cleans stutters/phonetic ASR terms, splits multi-questions, detects non-questions & material ambiguity.
2. `InterviewerIntelligence.analyze` -> classifies persona, conversational act, precision targets, and observable tone.
3. `DynamicLengthController.determine_budget` -> selects spoken duration & word budget.
4. Domain Router (`TechnicalReasoningEngine`, `BehavioralReasoningEngine`, `BusinessIntelligenceEngine`, `FollowUpAndPressureHandler`) -> builds grounded response using active project, story rotation, and ledger.
5. `HumanCommunicationEngine.humanize_spoken_text` -> enforces contractions, varied openings, spoken-only format, and word budget.
6. `ResponseValidator.validate` -> gates against resume leaks, STAR labels, numerical drift, chronology errors, and evidence violations before persisting state.
