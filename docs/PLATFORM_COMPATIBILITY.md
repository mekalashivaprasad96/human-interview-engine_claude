# Platform Compatibility Matrix

Capabilities verified against current platform specifications:

| Platform | Deployment Mechanism | Persistent Memory / State | Tool Execution | Key Constraints & Adapter Notes |
|---|---|---|---|---|
| **Claude Code** | `SKILL.md` in `~/.claude/skills/` or `.claude/skills/` | Local filesystem (`memory/`) + `CLAUDE.md` | Full bash + Python CLI | Progressive disclosure loads `SKILL.md` body and `core/*/MODULE.md` on demand. |
| **Open Agent Skills (`agentskills.io`, Codex, Antigravity)** | `SKILL.md` in `.agents/skills/` | Local workspace / `AGENTS.md` | Agent-dependent | Strictly conforms to `name` (<=64 chars) & `description` (<=1024 chars) frontmatter spec. |
| **Claude.ai Projects** | Project Instructions + Knowledge files | Project-scoped RAG & isolated workspace | Artifact/code per tier | Keep one Project per candidate to guarantee zero cross-candidate contamination. |
| **Claude Skills / API (`/v1/skills`)** | Zipped `SKILL.md` bundle (`package_claude_skill.py`) | Session/container scope | Code execution where enabled | Packaged cleanly via `adapters/claude/package_claude_skill.py`. |
| **ChatGPT Custom GPTs** | `custom-gpt-instructions.md` + up to 20 Knowledge files | Isolated from global Memory & Custom Instructions | Optional Code Interpreter | Instructions strictly **<= 8,000 characters** (ours is ~4,650 chars). |
| **ChatGPT Projects** | `chatgpt-project-instructions.md` + Knowledge files | Project-level memory & RAG | Optional | Isolate one Project per candidate/target role. |
| **ChatGPT Custom Instructions** | Two Personalization fields | Global Memory (use Temporary Chat to isolate) | Standard ChatGPT tools | Sized **<= 1,500 chars** per field so Free/Go and Plus/Pro tiers work uniformly. |
| **Browser Extensions / Standalone Apps** | `PORTABLE_PROMPT_BUNDLE.md` or Python JSON engine | Local JSON files (`schemas/*.schema.json`) | Embedded Python or API | Deterministic JSON state schemas simplify native UI/extension integration. |
