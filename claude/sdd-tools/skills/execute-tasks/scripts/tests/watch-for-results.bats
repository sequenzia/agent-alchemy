#!/usr/bin/env bats
# Tests for watch-for-results.sh event-driven result file detection

SCRIPT_DIR="$(cd "$(dirname "${BATS_TEST_FILENAME}")/.." && pwd)"
WATCH_SCRIPT="$SCRIPT_DIR/watch-for-results.sh"

setup() {
  TEST_DIR="$(mktemp -d)"
  export WATCH_TIMEOUT=10
}

teardown() {
  rm -rf "$TEST_DIR"
  unset WATCH_TIMEOUT 2>/dev/null || true
}

# --- All results found ---

@test "all results found: pre-existing files produce ALL_DONE and exit 0" {
  touch "$TEST_DIR/result-task-1.md"
  touch "$TEST_DIR/result-task-2.md"
  touch "$TEST_DIR/result-task-3.md"

  run bash "$WATCH_SCRIPT" "$TEST_DIR" 3 1 2 3

  [ "$status" -eq 0 ]
  [[ "$output" == *"RESULT_FOUND: result-task-1.md"* ]]
  [[ "$output" == *"RESULT_FOUND: result-task-2.md"* ]]
  [[ "$output" == *"RESULT_FOUND: result-task-3.md"* ]]
  [[ "$output" == *"ALL_DONE"* ]]
}

@test "all results found: dynamically created files produce ALL_DONE and exit 0" {
  # Create result files after a delay
  (sleep 1 && touch "$TEST_DIR/result-task-1.md") &
  (sleep 2 && touch "$TEST_DIR/result-task-2.md") &

  run bash "$WATCH_SCRIPT" "$TEST_DIR" 2 1 2

  [ "$status" -eq 0 ]
  [[ "$output" == *"RESULT_FOUND: result-task-1.md"* ]]
  [[ "$output" == *"RESULT_FOUND: result-task-2.md"* ]]
  [[ "$output" == *"ALL_DONE"* ]]
}

@test "all results found: output format matches RESULT_FOUND pattern with counts" {
  touch "$TEST_DIR/result-task-42.md"

  run bash "$WATCH_SCRIPT" "$TEST_DIR" 1 42

  [ "$status" -eq 0 ]
  [[ "${lines[0]}" == "RESULT_FOUND: result-task-42.md (1/1)" ]]
  [[ "${lines[1]}" == "ALL_DONE" ]]
}

# --- Timeout with no files ---

@test "timeout: exits with code 1 when no files created" {
  export WATCH_TIMEOUT=3

  run bash "$WATCH_SCRIPT" "$TEST_DIR" 2 1 2

  [ "$status" -eq 1 ]
  [[ "$output" == *"Found 0/2 results"* ]]
}

# --- No fswatch available ---

@test "no fswatch available: exits with code 2 when tools unavailable" {
  # Override PATH to exclude fswatch and inotifywait
  run env PATH=/usr/bin:/bin bash "$WATCH_SCRIPT" "$TEST_DIR" 3 1 2 3

  [ "$status" -eq 2 ]
  [[ "$output" == *"Neither fswatch nor inotifywait available"* ]]
}

# --- Pre-existing results detected and counted ---

@test "pre-existing results: counted before watch starts" {
  touch "$TEST_DIR/result-task-1.md"
  touch "$TEST_DIR/result-task-2.md"

  # Expect 3 but only 2 exist; create the third after a delay
  (sleep 1 && touch "$TEST_DIR/result-task-3.md") &

  run bash "$WATCH_SCRIPT" "$TEST_DIR" 3 1 2 3

  [ "$status" -eq 0 ]
  [[ "$output" == *"RESULT_FOUND: result-task-1.md (1/3)"* ]]
  [[ "$output" == *"RESULT_FOUND: result-task-2.md (2/3)"* ]]
  [[ "$output" == *"RESULT_FOUND: result-task-3.md (3/3)"* ]]
  [[ "$output" == *"ALL_DONE"* ]]
}

# --- Partial completion ---

@test "partial completion: reports found results and exits code 1 on timeout" {
  export WATCH_TIMEOUT=3
  touch "$TEST_DIR/result-task-1.md"

  run bash "$WATCH_SCRIPT" "$TEST_DIR" 3 1 2 3

  [ "$status" -eq 1 ]
  [[ "$output" == *"RESULT_FOUND: result-task-1.md (1/3)"* ]]
  [[ "$output" == *"Found 1/3 results"* ]]
}

# --- Non-result files ignored ---

@test "filtering: ignores non-result files in session directory" {
  # Create non-result files, then the actual result
  (sleep 1 && touch "$TEST_DIR/context-task-1.md" && touch "$TEST_DIR/other.txt" && touch "$TEST_DIR/result-task-1.md.tmp" && sleep 0.5 && touch "$TEST_DIR/result-task-1.md") &

  run bash "$WATCH_SCRIPT" "$TEST_DIR" 1 1

  [ "$status" -eq 0 ]
  # Only result-task-1.md should appear in output (not context, txt, or tmp)
  local result_count=0
  for line in "${lines[@]}"; do
    if [[ "$line" == RESULT_FOUND:* ]]; then
      result_count=$((result_count + 1))
    fi
  done
  [ "$result_count" -eq 1 ]
  [[ "$output" == *"RESULT_FOUND: result-task-1.md (1/1)"* ]]
  [[ "$output" == *"ALL_DONE"* ]]
}

# --- Usage ---

@test "usage: exits with code 2 when no arguments" {
  run bash "$WATCH_SCRIPT"

  [ "$status" -eq 2 ]
  [[ "$output" == *"Usage:"* ]]
}

@test "usage: exits with code 2 when only session_dir" {
  run bash "$WATCH_SCRIPT" "$TEST_DIR"

  [ "$status" -eq 2 ]
  [[ "$output" == *"Usage:"* ]]
}

# --- Watcher exit ---

@test "watcher exit: exits with code 1 when fswatch exits unexpectedly" {
  # Watch a non-existent directory to make fswatch fail immediately
  export WATCH_TIMEOUT=5
  NONEXISTENT_DIR="$(mktemp -u)"

  run bash "$WATCH_SCRIPT" "$NONEXISTENT_DIR" 1 1

  [ "$status" -eq 1 ]
}
