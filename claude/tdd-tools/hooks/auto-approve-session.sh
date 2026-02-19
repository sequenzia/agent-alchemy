#!/bin/bash
# Auto-approve file operations targeting execute-tdd-tasks session directories.
#
# Approves Write/Edit to:
#   - $HOME/.claude/tasks/*/execution_pointer.md
#   - */.claude/sessions/* (session files within any project)
#
# Approves Bash commands targeting .claude/sessions/
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
    echo "[auto-approve-session] $*" >> "${AGENT_ALCHEMY_HOOK_LOG:-/tmp/agent-alchemy-hook.log}"
  fi
}

input=$(cat 2>/dev/null) || input=""

debug "Input received: ${input:0:200}"

tool_name=$(echo "$input" | jq -r '.tool_name // empty' 2>/dev/null) || tool_name=""

debug "Tool name: $tool_name"

approve() {
  debug "APPROVED: $1"
  cat <<'EOF'
{"hookSpecificOutput":{"permissionDecision":"allow","permissionDecisionReason":"Auto-approved: execute-tdd-tasks session file operation"}}
EOF
  exit 0
}

case "$tool_name" in
  Write|Edit)
    file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty' 2>/dev/null) || file_path=""
    [ -z "$file_path" ] && { debug "No file_path found"; exit 0; }

    debug "File path: $file_path"

    # Match execution_pointer.md in ~/.claude/tasks/*/
    if [[ "$file_path" == "$HOME/.claude/tasks/"*/execution_pointer.md ]]; then
      approve "execution_pointer.md"
    fi

    # Match any file inside .claude/sessions/ (absolute or relative paths)
    if [[ "$file_path" == */.claude/sessions/* ]] || [[ "$file_path" == .claude/sessions/* ]]; then
      approve "session file: $file_path"
    fi
    ;;

  Bash)
    command=$(echo "$input" | jq -r '.tool_input.command // empty' 2>/dev/null) || command=""
    [ -z "$command" ] && { debug "No command found"; exit 0; }

    debug "Command: ${command:0:200}"

    # Match any bash command targeting .claude/sessions/
    if [[ "$command" == *".claude/sessions/"* ]]; then
      approve "bash session command"
    fi
    ;;
esac

# No opinion — let normal permission flow handle it
debug "No match — passing through"
exit 0
