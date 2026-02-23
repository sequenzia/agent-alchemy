#!/usr/bin/env bash
# poll-for-results.sh — Adaptive polling for task result files
#
# Usage: poll-for-results.sh <session_dir> <expected_count> [task_ids...]
# Example: poll-for-results.sh .claude/sessions/__live_session__ 5 101 102 103 104 105
#
# Polls for result-task-{id}.md files with adaptive intervals. Used as fallback
# when watch-for-results.sh reports tools unavailable (exit code 2).
#
# Exit codes:
#   0 - All expected results found
#   1 - Timeout reached
#
# Output (stdout):
#   RESULT_FOUND: result-task-{id}.md (N/M)
#   ALL_DONE
#
# Environment:
#   POLL_START_INTERVAL - Starting interval in seconds (default: 5)
#   POLL_MAX_INTERVAL   - Maximum interval in seconds (default: 30)
#   POLL_TIMEOUT        - Cumulative timeout in seconds (default: 2700 = 45 min)

set -euo pipefail

if [ $# -lt 2 ]; then
  echo "Usage: poll-for-results.sh <session_dir> <expected_count> [task_ids...]"
  exit 2
fi

SESSION_DIR="$1"
EXPECTED_COUNT="$2"
shift 2
TASK_IDS="$*"

# Parse environment variables with defaults, falling back on invalid values
parse_positive_int() {
  local val="$1"
  local default="$2"
  if [[ "$val" =~ ^[0-9]+$ ]] && [ "$val" -gt 0 ]; then
    echo "$val"
  else
    echo "$default"
  fi
}

START_INTERVAL=$(parse_positive_int "${POLL_START_INTERVAL:-5}" 5)
MAX_INTERVAL=$(parse_positive_int "${POLL_MAX_INTERVAL:-30}" 30)
TIMEOUT=$(parse_positive_int "${POLL_TIMEOUT:-2700}" 2700)

INTERVAL="$START_INTERVAL"
ELAPSED=0
FOUND_COUNT=0
PREV_FOUND=0

# Build list of IDs to check; if task_ids provided use those, otherwise scan directory
check_results() {
  FOUND_COUNT=0
  if [ -n "$TASK_IDS" ]; then
    for ID in $TASK_IDS; do
      if [ -f "$SESSION_DIR/result-task-$ID.md" ]; then
        FOUND_COUNT=$((FOUND_COUNT + 1))
      fi
    done
  else
    for f in "$SESSION_DIR"/result-task-*.md; do
      [ -f "$f" ] || continue
      FOUND_COUNT=$((FOUND_COUNT + 1))
    done
  fi
}

# Track which results have been announced to avoid duplicates
declare -A ANNOUNCED 2>/dev/null || true

emit_new_results_tracked() {
  if [ -n "$TASK_IDS" ]; then
    for ID in $TASK_IDS; do
      if [ -f "$SESSION_DIR/result-task-$ID.md" ] && [ -z "${ANNOUNCED[$ID]:-}" ]; then
        ANNOUNCED[$ID]=1
        echo "RESULT_FOUND: result-task-$ID.md ($FOUND_COUNT/$EXPECTED_COUNT)"
      fi
    done
  else
    for f in "$SESSION_DIR"/result-task-*.md; do
      [ -f "$f" ] || continue
      local BASENAME
      BASENAME="$(basename "$f")"
      if [ -z "${ANNOUNCED[$BASENAME]:-}" ]; then
        ANNOUNCED[$BASENAME]=1
        echo "RESULT_FOUND: $BASENAME ($FOUND_COUNT/$EXPECTED_COUNT)"
      fi
    done
  fi
}

# Initial check before entering the polling loop
check_results
PREV_FOUND=$FOUND_COUNT
emit_new_results_tracked

if [ "$FOUND_COUNT" -ge "$EXPECTED_COUNT" ]; then
  echo "ALL_DONE"
  exit 0
fi

# Adaptive polling loop
while [ "$ELAPSED" -lt "$TIMEOUT" ]; do
  sleep "$INTERVAL"
  ELAPSED=$((ELAPSED + INTERVAL))

  PREV_FOUND=$FOUND_COUNT
  check_results
  emit_new_results_tracked

  if [ "$FOUND_COUNT" -ge "$EXPECTED_COUNT" ]; then
    echo "ALL_DONE"
    exit 0
  fi

  if [ "$FOUND_COUNT" -gt "$PREV_FOUND" ]; then
    # New result found — reset interval to start
    INTERVAL="$START_INTERVAL"
  else
    # No new results — increase interval by 5s up to max
    INTERVAL=$((INTERVAL + 5))
    if [ "$INTERVAL" -gt "$MAX_INTERVAL" ]; then
      INTERVAL="$MAX_INTERVAL"
    fi
  fi
done

# Timeout reached
exit 1
