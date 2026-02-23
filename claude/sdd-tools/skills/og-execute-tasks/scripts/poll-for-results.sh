#!/usr/bin/env bash
# poll-for-results.sh — Polls for task result files with progress output
#
# Usage: poll-for-results.sh <session_dir> <id1> [id2] [id3] ...
# Example: poll-for-results.sh .claude/sessions/__live_session__ 1 2 3 4 5
#
# Checks for result-task-{id}.md files every INTERVAL seconds for up to
# ROUND_DURATION seconds. Exits with structured output:
#
#   POLL_RESULT: ALL_DONE  — all result files found (exit 0)
#   POLL_RESULT: PENDING   — round timeout, lists pending IDs (exit 1)
#
# Environment variable overrides (for testing):
#   POLL_ROUND_DURATION — seconds per round (default: 420 = 7 minutes)
#   POLL_INTERVAL       — seconds between checks (default: 15)

set -euo pipefail

if [ $# -lt 2 ]; then
  echo "Usage: poll-for-results.sh <session_dir> <id1> [id2] ..."
  exit 2
fi

SESSION_DIR="$1"
shift
EXPECTED_IDS="$*"

ROUND_DURATION="${POLL_ROUND_DURATION:-420}"
INTERVAL="${POLL_INTERVAL:-15}"
ELAPSED=0

while [ "$ELAPSED" -lt "$ROUND_DURATION" ]; do
  DONE_COUNT=0
  PENDING=""
  TOTAL=0

  for ID in $EXPECTED_IDS; do
    TOTAL=$((TOTAL + 1))
    if [ -f "$SESSION_DIR/result-task-$ID.md" ]; then
      DONE_COUNT=$((DONE_COUNT + 1))
    else
      PENDING="$PENDING $ID"
    fi
  done

  if [ "$DONE_COUNT" -eq "$TOTAL" ]; then
    echo "POLL_RESULT: ALL_DONE"
    echo "Completed: $DONE_COUNT/$TOTAL"
    exit 0
  fi

  sleep "$INTERVAL"
  ELAPSED=$((ELAPSED + INTERVAL))
done

# Round ended without all files found
echo "POLL_RESULT: PENDING"
echo "Completed: $DONE_COUNT/$TOTAL"
echo "Waiting on:$PENDING"
exit 1
