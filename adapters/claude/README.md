# Claude Projects & Claude Skills Adapter

## Option 1: Claude.ai Projects
Claude Projects maintain persistent instructions and uploaded knowledge files isolated from other projects.
1. Create a new Claude Project per candidate/target role (maintains candidate isolation).
2. Copy `adapters/claude/claude-project-instructions.md` into the Project's **Instructions**.
3. Upload `SYSTEM_PROMPT.md`, `adapters/universal/PORTABLE_PROMPT_BUNDLE.md`, `config/technology_timeline.json`, and `config/industry_profiles.json` to Project Knowledge.
4. Paste or attach the candidate's resume and job description to initialize.

## Option 2: Claude Skills / Claude API (`POST /v1/skills`)
Build a clean skill archive containing `SKILL.md` and progressive module files:
```bash
python3 adapters/claude/package_claude_skill.py
```
This outputs `dist/human-interview-engine-skill.zip` structured with `human-interview-engine/SKILL.md` at the archive root.
