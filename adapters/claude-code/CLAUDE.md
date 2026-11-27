# CLAUDE.md Integration Snippet

Add the following section to your repository's `CLAUDE.md` (or `AGENTS.md`) if you want project-wide access without relying solely on skill discovery:

```markdown
## HumanInterview Engine 4.0
- Skill entrypoint: `.claude/skills/human-interview-engine/SKILL.md` (or `~/.claude/skills/human-interview-engine/SKILL.md`).
- Initialize sessions with `PYTHONPATH=src python3 -m human_interview_engine init --resume <file> --jd <file>`.
- Process interview turns with `PYTHONPATH=src python3 -m human_interview_engine turn --session-id <id> --question "<text>"`.
- Never echo resume citations, STAR headers, or coaching notes during candidate simulation turns.
```
