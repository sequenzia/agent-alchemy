#!/bin/bash
# Auto-approve file operations targeting deep-analysis session and cache directories.
#
# Approves Write/Edit to:
#   - */.claude/sessions/__da_live__/* (active session files)
#   - */.claude/sessions/exploration-cache/* (exploration cache)
#   - */.claude/sessions/da-*/* (archived sessions)
#
# Approves Bash commands targeting these directories.
#
# All other operations: exit 0 with no output (no opinion, normal permission flow).
#
# IMPORTANT: This hook must NEVER exit non-zero. A non-zero exit causes Claude Code
# to fall through to the normal permission prompt, breaking autonomous execution.

# Any unexpected error exits cleanly as "no opinion" (exit 0, no output)
trap 'exit 0' ERR

# Optional debug logging: set AGENT_ALCHEMY_HOOK_DEBUG=1 to enable
debug() {
  if [ "${AGENT_ALCHEMY_HOOK_DEBUG:-}" = "1" ]; then
    echo "[auto-approve-da-session] $*" >> "${AGENT_ALCHEMY_HOOK_LOG:-/tmp/agent-alchemy-hook.log}"
  fi
}

input=$(cat 2>/dev/null) || input=""

debug "Input received: ${input:0:200}"

tool_name=$(echo "$input" | jq -r '.tool_name // empty' 2>/dev/null) || tool_name=""

debug "Tool name: $tool_name"

approve() {
  debug "APPROVED: $1"
  cat <<'EOF'
{"hookSpecificOutput":{"permissionDecision":"allow","permissionDecisionReason":"Auto-approved: deep-analysis session file operation"}}
EOF
  exit 0
}

# Match deep-analysis session paths:
#   __da_live__     - active session
#   exploration-cache - cached results
#   da-*            - archived sessions (da-1707300000, da-interrupted-1707300000)
is_da_session_path() {
  local path="$1"
  if [[ "$path" == */.claude/sessions/__da_live__/* ]] || [[ "$path" == .claude/sessions/__da_live__/* ]]; then
    return 0
  fi
  if [[ "$path" == */.claude/sessions/exploration-cache/* ]] || [[ "$path" == .claude/sessions/exploration-cache/* ]]; then
    return 0
  fi
  if [[ "$path" == */.claude/sessions/da-*/* ]] || [[ "$path" == .claude/sessions/da-*/* ]]; then
    return 0
  fi
  return 1
}

case "$tool_name" in
  Write|Edit)
    file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty' 2>/dev/null) || file_path=""
    [ -z "$file_path" ] && { debug "No file_path found"; exit 0; }

    debug "File path: $file_path"

    if is_da_session_path "$file_path"; then
      approve "session file: $file_path"
    fi
    ;;

  Bash)
    command=$(echo "$input" | jq -r '.tool_input.command // empty' 2>/dev/null) || command=""
    [ -z "$command" ] && { debug "No command found"; exit 0; }

    debug "Command: ${command:0:200}"

    # Match bash commands targeting DA session directories
    if [[ "$command" == *".claude/sessions/__da_live__"* ]] || \
       [[ "$command" == *".claude/sessions/exploration-cache"* ]] || \
       [[ "$command" == *".claude/sessions/da-"* ]]; then
      approve "bash session command"
    fi
    ;;
esac

# No opinion — let normal permission flow handle it
debug "No match — passing through"
exit 0
