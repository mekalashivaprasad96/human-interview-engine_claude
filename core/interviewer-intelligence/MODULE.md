# Interviewer Intelligence Module

**Python Implementation:** `src/human_interview_engine/interviewer_intelligence.py`

## Responsibility
Identify interviewer persona, conversational act, exact question precision, and observable tone without hallucinating private emotions or hiring outcomes.

## Recognizes
- **Personas:** `recruiter`, `hiring_manager`, `technical_specialist`, `senior_engineer`, `architect`, `executive`, `customer_stakeholder`, `behavioral_interviewer`, `system_design_interviewer`, `skeptical_interviewer`, `collaborative_interviewer`, `panel_member`.
- **Acts:** `new_question`, `clarification_request`, `depth_probe`, `implementation_probe`, `ownership_probe`, `numerical_probe`, `challenge`, `correction`, `information_only`, `rhetorical`, `interruption`, `repeated_question`, `topic_switch`, `closing`.
- **Precision Targets:** `what`, `why`, `how`, `when`, `how_many`, `how_much`, `which`, `what_did_you_personally_do`, `what_was_outcome`, `what_went_wrong`, `what_differently`, `yes_no_first`, `multi_part`.
