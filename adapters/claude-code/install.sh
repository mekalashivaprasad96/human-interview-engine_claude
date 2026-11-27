#!/usr/bin/env bash
set -euo pipefail

# Install HumanInterview Engine 4.0 as a portable Agent Skill (Claude Code / Codex / Antigravity)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

TARGET_SCOPE="${1:-personal}"
case "${TARGET_SCOPE}" in
  personal)
    DEST="${HOME}/.claude/skills/human-interview-engine"
    ;;
  project)
    DEST="${PWD}/.claude/skills/human-interview-engine"
    ;;
  agents)
    DEST="${PWD}/.agents/skills/human-interview-engine"
    ;;
  *)
    DEST="${TARGET_SCOPE}"
    ;;
esac

mkdir -p "${DEST}"
cp "${REPO_ROOT}/SKILL.md" "${DEST}/"
cp "${REPO_ROOT}/SYSTEM_PROMPT.md" "${DEST}/"
cp -R "${REPO_ROOT}/config" "${DEST}/"
cp -R "${REPO_ROOT}/schemas" "${DEST}/"
cp -R "${REPO_ROOT}/core" "${DEST}/"
cp -R "${REPO_ROOT}/src" "${DEST}/"
cp -R "${REPO_ROOT}/evaluation" "${DEST}/"
cp -R "${REPO_ROOT}/importers" "${DEST}/"
mkdir -p "${DEST}/memory/candidates" "${DEST}/memory/sessions" "${DEST}/memory/backups"

echo "Installed HumanInterview Engine skill to: ${DEST}"
echo "Test runtime with: PYTHONPATH=${DEST}/src python3 -m human_interview_engine --help"
