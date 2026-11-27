# Claude Code & Open Agent Skills Adapter

Claude Code skills conform to the open **Agent Skills** (`agentskills.io`) specification with progressive disclosure:

- **Personal skill location:** `~/.claude/skills/human-interview-engine/SKILL.md`
- **Project skill location:** `.claude/skills/human-interview-engine/SKILL.md`
- **Open Agent Skills / Codex / Antigravity location:** `.agents/skills/human-interview-engine/SKILL.md`

## Installation
```bash
bash adapters/claude-code/install.sh personal   # ~/.claude/skills/human-interview-engine
bash adapters/claude-code/install.sh project    # ./.claude/skills/human-interview-engine
bash adapters/claude-code/install.sh agents     # ./.agents/skills/human-interview-engine
```

Once installed, invoke directly via `/human-interview-engine` or trigger naturally by sharing a resume and job description for interview simulation or preparation.
