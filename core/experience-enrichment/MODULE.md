# Experience Enrichment Module

**Python Implementation:** `src/human_interview_engine/experience_enrichment.py`  
**Output Schema:** `schemas/experience_story_bank.schema.json`

## Responsibility
Build and rotate a diverse multi-employer story bank spanning delivery successes, production failures/rollbacks, and cross-functional disagreements.

## Core Rules
1. Maintain explicit `individual_ownership` vs `team_context` on every story.
2. Include realistic setbacks, compromises, and lessons learned—never craft spotless superhero narratives.
3. Track `times_used` and `last_used_turn` to prevent repeating the same story across unrelated behavioral prompts.
4. Keep `evidence_status` distinct; never surface `fictional_simulation_scenario` items as personal history in `authentic_preparation` mode.
