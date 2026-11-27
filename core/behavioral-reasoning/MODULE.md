# Behavioral & Cognitive Ability Reasoning Module

**Python Implementation:** `src/human_interview_engine/behavioral_reasoning.py`

## Responsibility
Handle behavioral interviews (implicit STAR without headings) and hypothetical/General Cognitive Ability (GCA) prompts (forward-looking analytical reasoning without forcing past stories).

## Core Rules
1. Behavioral stories rotate across `ExperienceStoryBank` so stories aren't repeated, foreground individual `'I'` ownership, and include real compromises, failures, and lessons learned.
2. Never emit visible `Situation:`, `Task:`, `Action:`, `Result:` headers unless explicitly requested in coaching mode.
3. For hypothetical / GCA prompts, separate immediate containment/triage from long-term fixes, identify hypotheses, check numbers, and define success metrics without forcing STAR.
