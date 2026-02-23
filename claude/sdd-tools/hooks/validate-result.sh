#!/bin/bash
# Validate result files written by task-executor agents (PostToolUse hook).
#
# Triggers on Write operations targeting result-task-*.md in session directories.
# Validates: status line, required sections, context file write-ordering invariant.
#
# If invalid: renames to result-task-{id}.md.invalid with error appended.
# If context file missing: creates a stub, result still accepted.
#
# IMPORTANT: This hook must NEVER exit non-zero. A non-zero exit in PostToolUse
# hooks causes unexpected behavior. Trap on ERR falls through cleanly.

trap 'exit 0' ERR

# Optional debug logging: set AGENT_ALCHEMY_HOOK_DEBUG=1 to enable
debug() {
  if [ "${AGENT_ALCHEMY_HOOK_DEBUG:-}" = "1" ]; then
    echo "[validate-result] $*" >&2
  fi
}

input=$(cat 2>/dev/null) || input=""

debug "Input received: ${input:0:200}"

# Extract tool name and file path from hook input
tool_name=$(echo "$input" | jq -r '.tool_name // empty' 2>/dev/null) || tool_name=""

# Only act on Write operations
[ "$tool_name" = "Write" ] || { debug "Not a Write operation ($tool_name), skipping"; exit 0; }

file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty' 2>/dev/null) || file_path=""
[ -n "$file_path" ] || { debug "No file_path found"; exit 0; }

debug "File path: $file_path"

# Only act on result-task-*.md files in session directories
case "$file_path" in
  */.claude/sessions/*/result-task-*.md) ;;
  *) debug "Not a session result file, skipping"; exit 0 ;;
esac

# Extract task ID from filename: result-task-{id}.md
basename_file=$(basename "$file_path")
task_id="${basename_file#result-task-}"
task_id="${task_id%.md}"

debug "Validating result file for task $task_id"

# Check the file exists and is readable
[ -f "$file_path" ] || { debug "File does not exist yet: $file_path"; exit 0; }

content=$(cat "$file_path" 2>/dev/null) || { debug "Cannot read file"; exit 0; }

errors=""

# Validate first line: must match status: (PASS|PARTIAL|FAIL)
first_line=$(echo "$content" | head -n1)
if ! echo "$first_line" | grep -qE '^status: (PASS|PARTIAL|FAIL)$'; then
  errors="${errors}Invalid or missing status line (expected 'status: PASS|PARTIAL|FAIL', got '${first_line}')\n"
fi

# Validate required sections
for section in "## Summary" "## Files Modified" "## Context Contribution"; do
  if ! echo "$content" | grep -qF "$section"; then
    errors="${errors}Missing required section: $section\n"
  fi
done

# Warn on large result files (>25 lines) but don't reject
line_count=$(echo "$content" | wc -l | tr -d ' ')
if [ "$line_count" -gt 25 ]; then
  debug "WARNING: Result file has $line_count lines (expected ~18), extra content present"
fi

# If validation errors found, rename to .invalid
if [ -n "$errors" ]; then
  debug "Validation failed: $(echo -e "$errors")"
  {
    cat "$file_path"
    echo ""
    echo "--- VALIDATION ERRORS ---"
    echo -e "$errors"
  } > "${file_path}.invalid" 2>/dev/null
  rm -f "$file_path" 2>/dev/null
  debug "Renamed to ${file_path}.invalid"
  exit 0
fi

# Check write-ordering invariant: context-task-{id}.md should exist
session_dir=$(dirname "$file_path")
context_file="${session_dir}/context-task-${task_id}.md"

if [ ! -f "$context_file" ]; then
  debug "Context file missing, creating stub: $context_file"
  echo "### Task [${task_id}]: No learnings captured" > "$context_file" 2>/dev/null
fi

debug "Validation passed for task $task_id"
exit 0
