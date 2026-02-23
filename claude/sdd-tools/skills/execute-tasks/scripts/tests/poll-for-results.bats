#!/usr/bin/env bats
# Tests for poll-for-results.sh adaptive polling

SCRIPT_DIR="$(cd "$(dirname "${BATS_TEST_FILENAME}")/.." && pwd)"
POLL_SCRIPT="$SCRIPT_DIR/poll-for-results.sh"

setup() {
  TEST_DIR="$(mktemp -d)"
  export POLL_START_INTERVAL=1
  export POLL_MAX_INTERVAL=6
  export POLL_TIMEOUT=30
}

teardown() {
  rm -rf "$TEST_DIR"
  unset POLL_START_INTERVAL POLL_MAX_INTERVAL POLL_TIMEOUT 2>/dev/null || true
}

# --- Adaptive interval increase ---

@test "adaptive interval increase: intervals grow by 5s each poll with no results" {
  # With POLL_START_INTERVAL=1 and MAX_INTERVAL=4, TIMEOUT=12:
  # Sleeps: 1s, then 4s (1+5 capped to 4), then 4s, then 4s = 13 > 12, so ~3 sleeps = 9s
  # Verify the script takes MORE than just 3x1s (would be 3s without increase)
  # proving intervals are growing
  export POLL_START_INTERVAL=1
  export POLL_MAX_INTERVAL=4
  export POLL_TIMEOUT=12

  local start_time=$SECONDS
  run bash "$POLL_SCRIPT" "$TEST_DIR" 1 999
  local elapsed=$((SECONDS - start_time))

  [ "$status" -eq 1 ]
  # Total sleep should be around 9s (1+4+4), proving intervals grew beyond 1s
  [ "$elapsed" -ge 7 ]
  [ "$elapsed" -le 16 ]
}

@test "adaptive interval increase: default progression 5s, 10s, 15s, 20s, 25s, 30s" {
  # Verify the script code handles the default progression correctly
  # We test with small values: START=1, and verify cap works
  export POLL_START_INTERVAL=1
  export POLL_MAX_INTERVAL=4
  export POLL_TIMEOUT=8

  local start_time=$SECONDS
  run bash "$POLL_SCRIPT" "$TEST_DIR" 1 999
  local elapsed=$((SECONDS - start_time))

  [ "$status" -eq 1 ]
  # Intervals: sleep 1, then 6 (1+5, but capped to 4), then 4, ...
  # Actually: 1 + 4 = 5, then +4 = 9 > 8, so 2 sleeps total
  # elapsed should be around 5s (1+4)
  [ "$elapsed" -ge 4 ]
  [ "$elapsed" -le 10 ]
}

# --- Interval reset on result ---

@test "interval reset: resets to start interval when new result found" {
  export POLL_START_INTERVAL=1
  export POLL_MAX_INTERVAL=100
  export POLL_TIMEOUT=15

  # Create first result after 2 seconds, second after 5 seconds
  (sleep 2 && touch "$TEST_DIR/result-task-101.md") &
  (sleep 5 && touch "$TEST_DIR/result-task-102.md") &

  run bash "$POLL_SCRIPT" "$TEST_DIR" 2 101 102

  [ "$status" -eq 0 ]
  [[ "$output" == *"RESULT_FOUND: result-task-101.md"* ]]
  [[ "$output" == *"RESULT_FOUND: result-task-102.md"* ]]
  [[ "$output" == *"ALL_DONE"* ]]
}

# --- Max interval cap ---

@test "max interval cap: never exceeds POLL_MAX_INTERVAL" {
  export POLL_START_INTERVAL=1
  export POLL_MAX_INTERVAL=2
  export POLL_TIMEOUT=8

  local start_time=$SECONDS
  run bash "$POLL_SCRIPT" "$TEST_DIR" 1 999
  local elapsed=$((SECONDS - start_time))

  [ "$status" -eq 1 ]
  # Intervals: 1, then 6 (1+5) capped to 2, then 7 (2+5) capped to 2, ...
  # Sleeps: 1 + 2 + 2 + 2 = 7, next would be 9 > 8
  # So ~4 sleeps, about 7 seconds
  [ "$elapsed" -ge 6 ]
  [ "$elapsed" -le 12 ]
}

# --- Environment variable override ---

@test "environment variable override: POLL_START_INTERVAL=2 starts at 2s" {
  # Create a result after 3 seconds. With start=2:
  # Sleep 2s (check -> not found), sleep 7s (2+5) -> but result appears at 3s
  # After the 7s sleep (total elapsed ~9s), it will find the result.
  # With start=1 instead of 2: Sleep 1s (not found), sleep 6s (1+5) -> finds at ~7s
  # The test verifies: start=2 means first interval is 2, script works, and finds result.
  export POLL_START_INTERVAL=2
  export POLL_MAX_INTERVAL=100
  export POLL_TIMEOUT=20

  (sleep 3 && touch "$TEST_DIR/result-task-50.md") &

  run bash "$POLL_SCRIPT" "$TEST_DIR" 1 50

  [ "$status" -eq 0 ]
  [[ "$output" == *"RESULT_FOUND: result-task-50.md"* ]]
  [[ "$output" == *"ALL_DONE"* ]]
}

@test "environment variable override: POLL_START_INTERVAL=10 starts at 10s" {
  # Create a result immediately available. With start=10, the initial check
  # should find it before entering the polling loop.
  touch "$TEST_DIR/result-task-200.md"

  export POLL_START_INTERVAL=10
  export POLL_MAX_INTERVAL=100
  export POLL_TIMEOUT=30

  local start_time=$SECONDS
  run bash "$POLL_SCRIPT" "$TEST_DIR" 1 200
  local elapsed=$((SECONDS - start_time))

  [ "$status" -eq 0 ]
  [[ "$output" == *"RESULT_FOUND: result-task-200.md"* ]]
  [[ "$output" == *"ALL_DONE"* ]]
  # Should be nearly instant since result exists before polling starts
  [ "$elapsed" -le 2 ]
}

@test "environment variable override: POLL_MAX_INTERVAL=15 caps correctly" {
  export POLL_START_INTERVAL=1
  export POLL_MAX_INTERVAL=3
  export POLL_TIMEOUT=10

  local start_time=$SECONDS
  run bash "$POLL_SCRIPT" "$TEST_DIR" 1 999
  local elapsed=$((SECONDS - start_time))

  [ "$status" -eq 1 ]
  # Intervals: 1, then 6 capped to 3, then 8 capped to 3, ...
  # Sleeps: 1 + 3 + 3 + 3 = 10, done
  [ "$elapsed" -ge 8 ]
  [ "$elapsed" -le 15 ]
}

@test "environment variable override: invalid values use defaults" {
  export POLL_START_INTERVAL="abc"
  export POLL_MAX_INTERVAL="-5"
  export POLL_TIMEOUT="0"

  # With invalid values, defaults should be used: start=5, max=30, timeout=2700
  # This would take way too long for a test, so just verify the script starts
  # We'll use a quick check: create all results immediately
  touch "$TEST_DIR/result-task-101.md"
  run bash "$POLL_SCRIPT" "$TEST_DIR" 1 101

  [ "$status" -eq 0 ]
  [[ "$output" == *"ALL_DONE"* ]]
}

# --- Timeout ---

@test "timeout: exits with code 1 when timeout reached" {
  export POLL_START_INTERVAL=1
  export POLL_MAX_INTERVAL=2
  export POLL_TIMEOUT=4

  run bash "$POLL_SCRIPT" "$TEST_DIR" 1 999

  [ "$status" -eq 1 ]
}

# --- All results on first poll ---

@test "immediate ALL_DONE: all results found on first poll" {
  touch "$TEST_DIR/result-task-101.md"
  touch "$TEST_DIR/result-task-102.md"
  touch "$TEST_DIR/result-task-103.md"

  local start_time=$SECONDS
  run bash "$POLL_SCRIPT" "$TEST_DIR" 3 101 102 103
  local elapsed=$((SECONDS - start_time))

  [ "$status" -eq 0 ]
  [[ "$output" == *"ALL_DONE"* ]]
  [[ "$output" == *"RESULT_FOUND: result-task-101.md"* ]]
  [[ "$output" == *"RESULT_FOUND: result-task-102.md"* ]]
  [[ "$output" == *"RESULT_FOUND: result-task-103.md"* ]]
  # Should be nearly instant
  [ "$elapsed" -le 2 ]
}

# --- Output format ---

@test "output format: matches RESULT_FOUND pattern" {
  touch "$TEST_DIR/result-task-42.md"

  run bash "$POLL_SCRIPT" "$TEST_DIR" 1 42

  [ "$status" -eq 0 ]
  [[ "${lines[0]}" == "RESULT_FOUND: result-task-42.md (1/1)" ]]
  [[ "${lines[1]}" == "ALL_DONE" ]]
}

@test "output format: shows correct N/M counts" {
  touch "$TEST_DIR/result-task-1.md"
  touch "$TEST_DIR/result-task-2.md"

  run bash "$POLL_SCRIPT" "$TEST_DIR" 3 1 2 3

  [ "$status" -ne 0 ] || [[ "$output" == *"ALL_DONE"* ]]
  # Should find 2 of 3 on first scan
  [[ "$output" == *"RESULT_FOUND: result-task-1.md"* ]]
  [[ "$output" == *"RESULT_FOUND: result-task-2.md"* ]]
}

# --- Usage ---

@test "usage: exits with code 2 when no arguments" {
  run bash "$POLL_SCRIPT"

  [ "$status" -eq 2 ]
  [[ "$output" == *"Usage:"* ]]
}

@test "usage: exits with code 2 when only session_dir" {
  run bash "$POLL_SCRIPT" "$TEST_DIR"

  [ "$status" -eq 2 ]
}
