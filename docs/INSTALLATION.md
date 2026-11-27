# Installation Guide

## Prerequisites
- **Python 3.9 or higher** (uses Python standard library only—no `pip install` dependencies required).

## Option A: Local Repository / CLI Usage
```bash
cd /path/to/human-interview-engine
python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m human_interview_engine --help
```

## Option B: Claude Code / Open Agent Skills (`agentskills.io`)
Install as a personal skill (`~/.claude/skills/human-interview-engine`), project skill (`.claude/skills/human-interview-engine`), or `.agents/skills/` bundle:
```bash
bash adapters/claude-code/install.sh personal
```

## Option C: Claude.ai Projects & Claude Skills API
- For **Claude Projects**, follow `adapters/claude/README.md` and `adapters/claude/claude-project-instructions.md`.
- For **Claude Skills ZIP**, run `python3 adapters/claude/package_claude_skill.py` to build `dist/human-interview-engine-skill.zip`.

## Option D: ChatGPT (Custom GPT, Projects, Custom Instructions)
- See `adapters/chatgpt/README.md` for exact character-limited templates and Knowledge file upload instructions.
