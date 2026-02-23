#!/usr/bin/env bash
# watch-for-results.sh — Event-driven result file detection using filesystem events
#
# Usage: watch-for-results.sh <session_dir> <expected_count> [task_ids...]
# Example: watch-for-results.sh .claude/sessions/__live_session__ 5 101 102 103 104 105
#
# Watches for result-task-{id}.md files using fswatch (macOS) or inotifywait (Linux).
# Replaces fixed-interval polling as the primary completion mechanism.
#
# Exit codes:
#   0 - All expected results found
#   1 - Timeout reached or watcher exited unexpectedly
#   2 - Neither fswatch nor inotifywait available
#
# Environment:
#   WATCH_TIMEOUT - Timeout in seconds (default: 2700 = 45 min)

set -uo pipefail

if [ $# -lt 2 ]; then
  echo "Usage: watch-for-results.sh <session_dir> <expected_count> [task_ids...]"
  exit 2
fi

SESSION_DIR="$1"
EXPECTED_COUNT="$2"
shift 2
TASK_IDS="$*"

TIMEOUT="${WATCH_TIMEOUT:-2700}"

# Detect available filesystem watch tool
WATCH_TOOL=""
if command -v fswatch >/dev/null 2>&1; then
  WATCH_TOOL="fswatch"
elif command -v inotifywait >/dev/null 2>&1; then
  WATCH_TOOL="inotifywait"
else
  echo "ERROR: Neither fswatch nor inotifywait available"
  exit 2
fi

FOUND_COUNT=0

# Count pre-existing result files before starting watch
for f in "$SESSION_DIR"/result-task-*.md; do
  [ -f "$f" ] || continue
  BASENAME="$(basename "$f")"
  if [[ "$BASENAME" =~ ^result-task-.*\.md$ ]]; then
    FOUND_COUNT=$((FOUND_COUNT + 1))
    echo "RESULT_FOUND: $BASENAME ($FOUND_COUNT/$EXPECTED_COUNT)"
  fi
done

if [ "$FOUND_COUNT" -ge "$EXPECTED_COUNT" ]; then
  echo "ALL_DONE"
  exit 0
fi

# Set up FIFO for watcher output
FIFO=$(mktemp -u "${TMPDIR:-/tmp}/watch-results-XXXXXX")
mkfifo "$FIFO"

# Track background PIDs for cleanup
WATCHER_PID=""
TIMER_PID=""

# Marker file signals timeout (avoids signal delivery issues during blocking read)
TIMEOUT_MARKER=$(mktemp -u "${TMPDIR:-/tmp}/watch-timeout-XXXXXX")

cleanup() {
  [ -n "$WATCHER_PID" ] && kill "$WATCHER_PID" 2>/dev/null || true
  [ -n "$TIMER_PID" ] && kill "$TIMER_PID" 2>/dev/null || true
  rm -f "$FIFO" "$TIMEOUT_MARKER"
  wait 2>/dev/null || true
}
trap cleanup EXIT

# Launch filesystem watcher writing to FIFO
if [ "$WATCH_TOOL" = "fswatch" ]; then
  fswatch --event Created "$SESSION_DIR" > "$FIFO" 2>/dev/null &
  WATCHER_PID=$!
elif [ "$WATCH_TOOL" = "inotifywait" ]; then
  inotifywait -m -e create --format '%f' "$SESSION_DIR" > "$FIFO" 2>/dev/null &
  WATCHER_PID=$!
fi

# Start timeout timer — creates marker file then kills watcher to unblock the read loop
(sleep "$TIMEOUT" && touch "$TIMEOUT_MARKER" && kill "$WATCHER_PID" 2>/dev/null) &
TIMER_PID=$!

# Read watcher output from FIFO in main shell (preserves variable state)
while IFS= read -r LINE; do
  # Extract just the filename (fswatch gives full path, inotifywait gives filename)
  BASENAME="$(basename "$LINE")"

  # Only process result-task-*.md files (ignore temp files, non-result files)
  if [[ "$BASENAME" =~ ^result-task-.*\.md$ ]]; then
    FOUND_COUNT=$((FOUND_COUNT + 1))
    echo "RESULT_FOUND: $BASENAME ($FOUND_COUNT/$EXPECTED_COUNT)"

    if [ "$FOUND_COUNT" -ge "$EXPECTED_COUNT" ]; then
      echo "ALL_DONE"
      exit 0
    fi
  fi
done < "$FIFO"

# FIFO closed — check if it was a timeout or unexpected watcher exit
if [ -f "$TIMEOUT_MARKER" ]; then
  echo "TIMEOUT: Found $FOUND_COUNT/$EXPECTED_COUNT results"
else
  echo "WATCHER_EXIT: Found $FOUND_COUNT/$EXPECTED_COUNT results"
fi
exit 1
