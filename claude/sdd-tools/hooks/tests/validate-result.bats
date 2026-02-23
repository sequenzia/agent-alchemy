#!/usr/bin/env bats
# Tests for validate-result.sh PostToolUse hook

SCRIPT_DIR="$(cd "$(dirname "${BATS_TEST_FILENAME}")/.." && pwd)"
HOOK_SCRIPT="$SCRIPT_DIR/validate-result.sh"
FIXTURES_DIR="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../../tests/fixtures" && pwd)"

setup() {
  TEST_DIR="$(mktemp -d)"
  SESSION_DIR="$TEST_DIR/project/.claude/sessions/__live_session__"
  mkdir -p "$SESSION_DIR"
  unset AGENT_ALCHEMY_HOOK_DEBUG 2>/dev/null || true
}

teardown() {
  rm -rf "$TEST_DIR"
}

# Helper: create a valid result file
create_valid_result() {
  local task_id="${1:-42}"
  local file="$SESSION_DIR/result-task-${task_id}.md"
  cat > "$file" <<'RESULT'
status: PASS
task_id: 42
duration: 1m 30s

## Summary
Implemented the feature successfully.

## Files Modified
- src/foo.ts -- added new function

## Context Contribution
Discovered that the project uses ESM imports.

## Verification
Functional: 3/3, Edge Cases: 2/2, Tests: 5/5 (0 failures)
RESULT
  echo "$file"
}

# Helper: build hook JSON input
build_input() {
  local tool_name="$1"
  local file_path="$2"
  jq -n --arg tool "$tool_name" --arg path "$file_path" \
    '{"tool_name": $tool, "tool_input": {"file_path": $path}}'
}

# --- Valid result files accepted ---

@test "valid PASS result file is accepted unchanged" {
  local file
  file=$(create_valid_result 42)
  # Create context file (write-ordering invariant)
  echo "### Task [42]: learnings" > "$SESSION_DIR/context-task-42.md"

  run bash -c "echo '$(build_input Write "$file")' | bash '$HOOK_SCRIPT'"

  [ "$status" -eq 0 ]
  # File should still exist (not renamed)
  [ -f "$file" ]
  [ ! -f "${file}.invalid" ]
}

@test "valid FAIL result file is accepted unchanged" {
  local file="$SESSION_DIR/result-task-10.md"
  cat > "$file" <<'RESULT'
status: FAIL
task_id: 10
duration: 0m 45s

## Summary
Failed to implement due to missing dependency.

## Files Modified
- none

## Context Contribution
None.

## Verification
Functional: 1/3
RESULT
  echo "### Task [10]: learnings" > "$SESSION_DIR/context-task-10.md"

  run bash -c "echo '$(build_input Write "$file")' | bash '$HOOK_SCRIPT'"

  [ "$status" -eq 0 ]
  [ -f "$file" ]
  [ ! -f "${file}.invalid" ]
}

@test "valid PARTIAL result file is accepted unchanged" {
  local file="$SESSION_DIR/result-task-7.md"
  cat > "$file" <<'RESULT'
status: PARTIAL
task_id: 7
duration: 2m 10s

## Summary
Partial implementation.

## Files Modified
- src/bar.ts -- partial changes

## Context Contribution
None.

## Verification
Functional: 3/3, Edge: 1/2
RESULT
  echo "### Task [7]: learnings" > "$SESSION_DIR/context-task-7.md"

  run bash -c "echo '$(build_input Write "$file")' | bash '$HOOK_SCRIPT'"

  [ "$status" -eq 0 ]
  [ -f "$file" ]
  [ ! -f "${file}.invalid" ]
}

# --- Missing status line ---

@test "missing status line causes .invalid rename" {
  local file="$SESSION_DIR/result-task-5.md"
  cat > "$file" <<'RESULT'
# Task Result: [5] Some task

## Summary
Did stuff.

## Files Modified
- none

## Context Contribution
None.
RESULT
  echo "### Task [5]: learnings" > "$SESSION_DIR/context-task-5.md"

  run bash -c "echo '$(build_input Write "$file")' | bash '$HOOK_SCRIPT'"

  [ "$status" -eq 0 ]
  [ ! -f "$file" ]
  [ -f "${file}.invalid" ]
}

# --- Invalid status value ---

@test "invalid status value causes .invalid rename" {
  local file="$SESSION_DIR/result-task-8.md"
  cat > "$file" <<'RESULT'
status: SUCCESS
task_id: 8

## Summary
Done.

## Files Modified
- none

## Context Contribution
None.
RESULT
  echo "### Task [8]: learnings" > "$SESSION_DIR/context-task-8.md"

  run bash -c "echo '$(build_input Write "$file")' | bash '$HOOK_SCRIPT'"

  [ "$status" -eq 0 ]
  [ ! -f "$file" ]
  [ -f "${file}.invalid" ]
  # Error description should be appended
  grep -q "VALIDATION ERRORS" "${file}.invalid"
  grep -q "Invalid or missing status line" "${file}.invalid"
}

@test "invalid status value UNKNOWN causes .invalid rename" {
  local file="$SESSION_DIR/result-task-20.md"
  cp "$FIXTURES_DIR/invalid-result-unknown-status.md" "$file"
  echo "### Task [20]: learnings" > "$SESSION_DIR/context-task-20.md"

  run bash -c "echo '$(build_input Write "$file")' | bash '$HOOK_SCRIPT'"

  [ "$status" -eq 0 ]
  [ ! -f "$file" ]
  [ -f "${file}.invalid" ]
  grep -q "VALIDATION ERRORS" "${file}.invalid"
  grep -q "Invalid or missing status line" "${file}.invalid"
}

# --- Fixture-based valid result ---

@test "fixture: valid PASS result file from fixtures directory is accepted" {
  local file="$SESSION_DIR/result-task-100.md"
  cp "$FIXTURES_DIR/valid-result-pass.md" "$file"
  echo "### Task [100]: learnings" > "$SESSION_DIR/context-task-100.md"

  run bash -c "echo '$(build_input Write "$file")' | bash '$HOOK_SCRIPT'"

  [ "$status" -eq 0 ]
  [ -f "$file" ]
  [ ! -f "${file}.invalid" ]
}

@test "fixture: invalid result without summary from fixtures directory is rejected" {
  local file="$SESSION_DIR/result-task-101.md"
  cp "$FIXTURES_DIR/invalid-result-no-summary.md" "$file"
  echo "### Task [101]: learnings" > "$SESSION_DIR/context-task-101.md"

  run bash -c "echo '$(build_input Write "$file")' | bash '$HOOK_SCRIPT'"

  [ "$status" -eq 0 ]
  [ ! -f "$file" ]
  [ -f "${file}.invalid" ]
  grep -q "Missing required section: ## Summary" "${file}.invalid"
}

# --- Missing required section ---

@test "missing Summary section causes .invalid rename" {
  local file="$SESSION_DIR/result-task-11.md"
  cat > "$file" <<'RESULT'
status: PASS
task_id: 11

## Files Modified
- none

## Context Contribution
None.
RESULT
  echo "### Task [11]: learnings" > "$SESSION_DIR/context-task-11.md"

  run bash -c "echo '$(build_input Write "$file")' | bash '$HOOK_SCRIPT'"

  [ "$status" -eq 0 ]
  [ ! -f "$file" ]
  [ -f "${file}.invalid" ]
  grep -q "Missing required section: ## Summary" "${file}.invalid"
}

@test "missing Files Modified section causes .invalid rename" {
  local file="$SESSION_DIR/result-task-12.md"
  cat > "$file" <<'RESULT'
status: PASS
task_id: 12

## Summary
Done.

## Context Contribution
None.
RESULT
  echo "### Task [12]: learnings" > "$SESSION_DIR/context-task-12.md"

  run bash -c "echo '$(build_input Write "$file")' | bash '$HOOK_SCRIPT'"

  [ "$status" -eq 0 ]
  [ ! -f "$file" ]
  [ -f "${file}.invalid" ]
  grep -q "Missing required section: ## Files Modified" "${file}.invalid"
}

@test "missing Context Contribution section causes .invalid rename" {
  local file="$SESSION_DIR/result-task-13.md"
  cat > "$file" <<'RESULT'
status: PASS
task_id: 13

## Summary
Done.

## Files Modified
- none
RESULT
  echo "### Task [13]: learnings" > "$SESSION_DIR/context-task-13.md"

  run bash -c "echo '$(build_input Write "$file")' | bash '$HOOK_SCRIPT'"

  [ "$status" -eq 0 ]
  [ ! -f "$file" ]
  [ -f "${file}.invalid" ]
  grep -q "Missing required section: ## Context Contribution" "${file}.invalid"
}

# --- Missing context file ---

@test "missing context file triggers stub creation, result still accepted" {
  local file
  file=$(create_valid_result 99)
  # Deliberately do NOT create context-task-99.md

  run bash -c "echo '$(build_input Write "$file")' | bash '$HOOK_SCRIPT'"

  [ "$status" -eq 0 ]
  # Result file should still be accepted
  [ -f "$file" ]
  [ ! -f "${file}.invalid" ]
  # Context stub should be created
  [ -f "$SESSION_DIR/context-task-99.md" ]
  grep -q "No learnings captured" "$SESSION_DIR/context-task-99.md"
}

# --- Non-session file writes ignored ---

@test "non-session file write is ignored" {
  local file="$TEST_DIR/some-other/result-task-1.md"
  mkdir -p "$(dirname "$file")"
  echo "status: INVALID" > "$file"

  run bash -c "echo '$(build_input Write "$file")' | bash '$HOOK_SCRIPT'"

  [ "$status" -eq 0 ]
  # File should be untouched (not renamed, hook skipped)
  [ -f "$file" ]
  [ ! -f "${file}.invalid" ]
}

@test "non-result file in session directory is ignored" {
  local file="$SESSION_DIR/execution_context.md"
  echo "some content" > "$file"

  run bash -c "echo '$(build_input Write "$file")' | bash '$HOOK_SCRIPT'"

  [ "$status" -eq 0 ]
  [ -f "$file" ]
}

# --- Result files >25 lines accepted ---

@test "result file with >25 lines is accepted with extra content" {
  local file="$SESSION_DIR/result-task-50.md"
  {
    echo "status: PASS"
    echo "task_id: 50"
    echo "duration: 3m 0s"
    echo ""
    echo "## Summary"
    echo "Lots of work done."
    echo ""
    echo "## Files Modified"
    echo "- file1.ts -- change1"
    echo "- file2.ts -- change2"
    echo ""
    echo "## Context Contribution"
    echo "Many learnings."
    echo ""
    echo "## Verification"
    echo "All passed."
    # Add extra lines to exceed 25
    for i in $(seq 1 20); do
      echo "Extra detail line $i"
    done
  } > "$file"
  echo "### Task [50]: learnings" > "$SESSION_DIR/context-task-50.md"

  run bash -c "echo '$(build_input Write "$file")' | bash '$HOOK_SCRIPT'"

  [ "$status" -eq 0 ]
  [ -f "$file" ]
  [ ! -f "${file}.invalid" ]
}

# --- Hook error handling ---

@test "hook error: trap catches malformed JSON input, exits 0" {
  run bash -c "echo 'not json at all' | bash '$HOOK_SCRIPT'"

  [ "$status" -eq 0 ]
}

@test "hook error: empty input exits 0" {
  run bash -c "echo '' | bash '$HOOK_SCRIPT'"

  [ "$status" -eq 0 ]
}

@test "hook error: non-Write tool exits 0" {
  run bash -c "echo '$(build_input Read "/some/file")' | bash '$HOOK_SCRIPT'"

  [ "$status" -eq 0 ]
}

# --- Debug logging ---

@test "debug logging only when AGENT_ALCHEMY_HOOK_DEBUG=1" {
  local file
  file=$(create_valid_result 42)
  echo "### Task [42]: learnings" > "$SESSION_DIR/context-task-42.md"

  # Without debug: no stderr output
  local stderr_output
  stderr_output=$(echo "$(build_input Write "$file")" | AGENT_ALCHEMY_HOOK_DEBUG=0 bash "$HOOK_SCRIPT" 2>&1 1>/dev/null)
  [ -z "$stderr_output" ]

  # With debug: stderr should have output
  stderr_output=$(echo "$(build_input Write "$file")" | AGENT_ALCHEMY_HOOK_DEBUG=1 bash "$HOOK_SCRIPT" 2>&1 1>/dev/null)
  [[ "$stderr_output" == *"[validate-result]"* ]]
}
