# Troubleshooting Guide

## `ModuleNotFoundError: No module named 'human_interview_engine'`
Run commands with `PYTHONPATH=src` from the `human-interview-engine/` root directory:
```bash
PYTHONPATH=src python3 -m human_interview_engine --help
```

## `FileNotFoundError: Session '...' not found`
Check that you are passing the exact `--session-id` printed by `init`, and if using a custom `--memory-dir`, pass the same `--memory-dir` to both `init` and `turn`.

## Unexpected `authentic_preparation` Refusal to State Metrics
In `authentic_preparation` mode, simulated project metrics are intentionally blocked from being stated as personal historical facts. Confirm real numbers explicitly using:
```bash
PYTHONPATH=src python3 -m human_interview_engine confirm --session-id <ID> --claim "..." --metric-name nodes --metric-value 12 --metric-unit nodes
```

## Custom GPT Save Fails Due to Character Limit
Ensure you copy **only** `adapters/chatgpt/custom-gpt-instructions.md` into the Custom GPT Instructions box (verified under 8,000 characters) and upload `SYSTEM_PROMPT.md`, `PORTABLE_PROMPT_BUNDLE.md`, and `config/*.json` into the **Knowledge** files section rather than pasting them into Instructions.
