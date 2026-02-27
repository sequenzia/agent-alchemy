#!/usr/bin/env bash
# verify-task-completion.sh — TaskCompleted hook for SDD execution quality gate
#
# Runs the project's test suite when an SDD task (has metadata.spec_path) is marked
# completed. Blocks completion if tests fail, allowing the executor to fix regressions.
#
# Exit codes:
#   0 — Tests pass (or non-SDD task, skip check)
#   2 — Tests fail, completion blocked with feedback
set -euo pipefail

INPUT=$(cat)
TASK_ID=$(echo "$INPUT" | jq -r '.task_id')
TASK_SUBJECT=$(echo "$INPUT" | jq -r '.task_subject')
SPEC_PATH=$(echo "$INPUT" | jq -r '.metadata.spec_path // empty')

# Only gate SDD tasks (those with spec_path metadata)
if [ -z "$SPEC_PATH" ]; then
  exit 0
fi

# Detect and run test suite
if [ -f "pnpm-lock.yaml" ] || [ -f "pnpm-workspace.yaml" ]; then
  TEST_OUTPUT=$(pnpm test 2>&1) || {
    echo "Task #$TASK_ID '$TASK_SUBJECT': Tests failed after completion. Fix failing tests before proceeding." >&2
    echo "${TEST_OUTPUT:0:1000}" >&2
    exit 2
  }
elif [ -f "package-lock.json" ] || [ -f "package.json" ]; then
  TEST_OUTPUT=$(npm test 2>&1) || {
    echo "Task #$TASK_ID '$TASK_SUBJECT': Tests failed after completion. Fix failing tests before proceeding." >&2
    echo "${TEST_OUTPUT:0:1000}" >&2
    exit 2
  }
elif [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
  TEST_OUTPUT=$(python -m pytest 2>&1) || {
    echo "Task #$TASK_ID '$TASK_SUBJECT': Tests failed after completion. Fix failing tests before proceeding." >&2
    echo "${TEST_OUTPUT:0:1000}" >&2
    exit 2
  }
fi

# No recognized test framework — pass through
exit 0
