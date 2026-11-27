# ChatGPT Adapters Guide

OpenAI provides three distinct customization layers in ChatGPT, each with different isolation and size limits:

## 1. Custom GPTs (`custom-gpt-instructions.md`)
- **Instruction Limit:** Strictly **8,000 characters**. `adapters/chatgpt/custom-gpt-instructions.md` is verified under 8,000 characters by the automated test suite.
- **Isolation:** Custom GPTs run isolated from global Custom Instructions and global Memory—making them ideal for sharing or keeping candidates separate.
- **Knowledge Upload (up to 20 files):** Upload:
  - `SYSTEM_PROMPT.md`
  - `adapters/universal/PORTABLE_PROMPT_BUNDLE.md`
  - `config/technology_timeline.json`
  - `config/industry_profiles.json`
  - `config/communication_rules.json`
  - Optional: Enable **Code Interpreter** if you also upload `src/human_interview_engine/*.py` for deterministic numerical ledger checks.

## 2. ChatGPT Projects (`chatgpt-project-instructions.md`)
- Create one ChatGPT Project per candidate/role so project memory and uploaded resume/JD stay isolated.
- Paste `adapters/chatgpt/chatgpt-project-instructions.md` into **Project Instructions** and upload knowledge files + resume + JD.

## 3. Global Custom Instructions (`chatgpt-custom-instructions.md`)
- Both fields in `chatgpt-custom-instructions.md` fit under the **1,500-character** Free/Go limit (as well as Plus/Pro 5,000-character limits). Use **Temporary Chat** when switching candidates to avoid cross-candidate memory contamination.
