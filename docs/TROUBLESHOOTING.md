# Troubleshooting Guide

## `ModuleNotFoundError: No module named 'human_interview_engine'`
Run commands with `PYTHONPATH=src` from the `human-interview-engine/` root directory:
```bash
PYTHONPATH=src python3 -m human_interview_engine --help
```

## `error: Unknown operating mode '...'`
`--mode` must be one of the IDs in `config/operating_modes.json` (for example `authentic_preparation`) or a short alias such as `authentic`, `immersive`, `technical`, `hiring-manager` or `coaching`. The error message lists every valid value.

## `error: Resume file not found` / `error: Resume is empty`
`--resume` and `--jd` accept a file path or the raw text. A value that looks like a path (ends in `.md`, `.txt`, `.json`, ... or starts with `/`, `./`, `~`) must exist; pass the text itself if you do not have a file.

## `error: Invalid session_id` / `Invalid candidate_id`
Session and candidate IDs may only contain letters, digits, `-` and `_`. Path separators and `..` are rejected so commands can never read or delete outside the memory directory.

## `FileNotFoundError: Session '...' not found`
Check that you are passing the exact `--session-id` printed by `init`, and if using a custom `--memory-dir`, pass the same `--memory-dir` to both `init` and `turn`.

## Unexpected `authentic_preparation` Refusal to State Metrics
In `authentic_preparation` mode, simulated project metrics are intentionally blocked from being stated as personal historical facts. Confirm real numbers explicitly using:
```bash
PYTHONPATH=src python3 -m human_interview_engine confirm --session-id <ID> --claim "..." --metric-name nodes --metric-value 12 --metric-unit nodes
```

## Custom GPT Save Fails Due to Character Limit
Ensure you copy **only** `adapters/chatgpt/custom-gpt-instructions.md` into the Custom GPT Instructions box (verified under 8,000 characters) and upload `SYSTEM_PROMPT.md`, `PORTABLE_PROMPT_BUNDLE.md`, and `config/*.json` into the **Knowledge** files section rather than pasting them into Instructions.
