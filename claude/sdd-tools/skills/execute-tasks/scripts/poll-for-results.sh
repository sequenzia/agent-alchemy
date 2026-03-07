#!/usr/bin/env bash
# poll-for-results.sh — Polls for task result files until all found or timeout
#
# Usage: poll-for-results.sh <session_dir> <id1> [id2] [id3] ...
# Example: poll-for-results.sh .claude/sessions/__live_session__ 1 2 3 4 5
#
# Checks for result-task-{id}.md files every INTERVAL seconds for up to
# TOTAL_TIMEOUT seconds. Prints progress lines periodically. Exits with
# structured output:
#
#   POLL_RESULT: ALL_DONE  — all result files found (exit 0)
#   POLL_RESULT: TIMEOUT   — total timeout reached (exit 0)
#
# Always exits 0 for ALL_DONE and TIMEOUT so the Bash tool does not
# frame the output as an error. Exit 2 for usage errors only.
#
# Environment variable overrides (for testing):
#   POLL_TOTAL_TIMEOUT     — total seconds before giving up (default: 2700 = 45 minutes)
#   POLL_INTERVAL          — seconds between file checks (default: 15)
#   POLL_PROGRESS_INTERVAL — seconds between progress lines (default: 60)

set -euo pipefail

if [ $# -lt 2 ]; then
  echo "Usage: poll-for-results.sh <session_dir> <id1> [id2] ..."
  exit 2
fi

SESSION_DIR="$1"
shift
EXPECTED_IDS="$*"

TOTAL_TIMEOUT="${POLL_TOTAL_TIMEOUT:-2700}"
INTERVAL="${POLL_INTERVAL:-15}"
PROGRESS_INTERVAL="${POLL_PROGRESS_INTERVAL:-60}"
ELAPSED=0
LAST_PROGRESS=0

while [ "$ELAPSED" -lt "$TOTAL_TIMEOUT" ]; do
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
    echo "Elapsed: ${ELAPSED}s"
    exit 0
  fi

  # Print progress at regular intervals
  SINCE_PROGRESS=$((ELAPSED - LAST_PROGRESS))
  if [ "$SINCE_PROGRESS" -ge "$PROGRESS_INTERVAL" ]; then
    echo "POLL_PROGRESS: $DONE_COUNT/$TOTAL complete, waiting on:$PENDING (${ELAPSED}s elapsed)"
    LAST_PROGRESS=$ELAPSED
  fi

  sleep "$INTERVAL"
  ELAPSED=$((ELAPSED + INTERVAL))
done

# Total timeout reached
echo "POLL_RESULT: TIMEOUT"
echo "Completed: $DONE_COUNT/$TOTAL"
echo "Waiting on:$PENDING"
echo "Elapsed: ${ELAPSED}s"
exit 0
