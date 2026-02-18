javascript
/**
 * sdd-tools-auto-approve-session.js
 *
 * OpenCode plugin: auto-approve Write/Edit/Bash tool operations targeting
 * execute-tasks session directories and execution pointer files.
 *
 * Ported from: claude/sdd-tools/hooks/hooks.json
 * Source hook: PreToolUse (Write|Edit|Bash matcher) -> auto-approve-session.sh
 *
 * Migration notes:
 * - Source was a PreToolUse shell command hook running auto-approve-session.sh
 * - OpenCode uses JS/TS plugins (tool.execute.before event) instead of shell hooks
 * - Logic from auto-approve-session.sh has been ported to JavaScript
 * - Path matching patterns are preserved exactly from the shell script
 * - OpenCode plugin API uses return { decision: "allow" } instead of JSON stdout
 *
 * RESOLVED: PreToolUse_shell_to_js — Shell hook ported to JS plugin using tool.execute.before. Workaround applied globally.
 */

const os = require("os");
const path = require("path");
const HOME = os.homedir();

/**
 * Determines whether a Write or Edit tool call targets an auto-approvable path.
 * Mirrors the shell script's path-matching logic exactly.
 *
 * @param {string} filePath - The file_path from tool input
 * @returns {boolean}
 */
function isApprovedFilePath(filePath) {
  if (!filePath) return false;

  // Match execution_pointer.md in ~/.claude/tasks/*/
  // Shell: [[ "$file_path" == "$HOME/.claude/tasks/"*/execution_pointer.md ]]
  const execPointerPattern = path.join(HOME, ".claude", "tasks");
  if (
    filePath.startsWith(execPointerPattern + path.sep) &&
    filePath.endsWith(path.join("execution_pointer.md"))
  ) {
    const relative = filePath.slice(execPointerPattern.length + 1);
    // Must be exactly one directory deep: <task-dir>/execution_pointer.md
    const parts = relative.split(path.sep);
    if (parts.length === 2 && parts[1] === "execution_pointer.md") {
      return true;
    }
  }

  // Match any file inside .claude/sessions/ (absolute or relative paths)
  // Shell: [[ "$file_path" == */.claude/sessions/* ]] || [[ "$file_path" == .claude/sessions/* ]]
  if (
    filePath.includes("/.claude/sessions/") ||
    filePath.startsWith(".claude/sessions/")
  ) {
    return true;
  }

  return false;
}

/**
 * Determines whether a Bash command targets .claude/sessions/.
 * Mirrors the shell script's command-matching logic.
 *
 * @param {string} command - The command from tool input
 * @returns {boolean}
 */
function isApprovedBashCommand(command) {
  if (!command) return false;
  // Shell: [[ "$command" == *".claude/sessions/"* ]]
  return command.includes(".claude/sessions/");
}

/**
 * tool.execute.before hook handler.
 *
 * OpenCode calls this before each tool execution. Return { decision: "allow" }
 * to auto-approve, or undefined/null to pass through to normal permission flow.
 *
 * Note: This hook does NOT fire for subagent tool calls (opencode limitation).
 * For subagent session file operations, users must approve manually per session.
 */
export default {
  name: "sdd-tools-auto-approve-session",
  description:
    "Auto-approve Write/Edit/Bash operations targeting execute-tasks session directories",

  hooks: {
    "tool.execute.before": async ({ tool, input }) => {
      try {
        switch (tool) {
          case "write":
          case "edit": {
            const filePath = input?.file_path ?? input?.path ?? "";
            if (isApprovedFilePath(filePath)) {
              return {
                decision: "allow",
                reason: "Auto-approved: execute-tasks session file operation",
              };
            }
            break;
          }

          case "bash": {
            const command = input?.command ?? "";
            if (isApprovedBashCommand(command)) {
              return {
                decision: "allow",
                reason: "Auto-approved: bash session command",
              };
            }
            break;
          }

          default:
            // No opinion for other tools — fall through to normal permission flow
            break;
        }
      } catch (_err) {
        // Any unexpected error: no opinion, let normal flow handle it
        // Mirrors the shell script's `trap 'exit 0' ERR` behavior
      }

      return undefined;
    },
  },
};
