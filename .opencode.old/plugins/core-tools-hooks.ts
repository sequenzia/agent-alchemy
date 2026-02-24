/**
 * core-tools-hooks.ts
 *
 * OpenCode plugin — converted from claude/core-tools/hooks/hooks.json
 *
 * Source purpose: Auto-approve file operations for deep-analysis session and
 * cache management (PreToolUse: Write|Edit|Bash on DA session paths).
 *
 * MIGRATION NOTES:
 *
 * Source behavior: The Claude Code hook used a shell script
 * (auto-approve-da-session.sh) that output a JSON permissionDecision payload
 * to stdout, which the Claude Code runtime interpreted as an autonomous
 * "allow" decision — bypassing the user permission prompt entirely for file
 * operations targeting deep-analysis session directories.
 *
 * OpenCode behavior: OpenCode's plugin SDK (tool.execute.before) does NOT
 * support a permission-decision output protocol. There is no equivalent of
 * permissionDecision:"allow" that a plugin can return to suppress the user
 * permission prompt. The tool.execute.before hook can observe and log tool
 * invocations, but cannot grant approvals.
 *
 * WORKAROUND — opencode.json permission config:
 *   Add the following to your .opencode/opencode.json to pre-approve
 *   write and bash operations at the session level (OpenCode v1.2.10+):
 *
 *   {
 *     "permission": {
 *       "write": "allow",
 *       "bash": "allow"
 *     }
 *   }
 *
 *   This grants blanket allow for write and bash tools for all operations,
 *   which is broader than the source hook's path-scoped approval. For
 *   tighter scoping, manually select "Allow for session" when OpenCode
 *   first prompts for a write/edit/bash operation targeting a
 *   .claude/sessions/__da_live__/ path.
 *
 * KNOWN LIMITATION — subagent bypass (issue #5894):
 *   OpenCode's tool.execute.before does NOT fire for subagent tool calls.
 *   The deep-analysis skill spawns subagents (code-explorer, code-synthesizer)
 *   that perform file writes. Those tool calls are NOT intercepted by this
 *   plugin. The opencode.json permission config workaround above applies
 *   session-wide and covers subagents; this plugin hook does not.
 *
 * This plugin provides observability (logging) for the covered tool calls.
 * The auto-approve capability requires the opencode.json permission config.
 */

import type { Plugin } from "@opencode-ai/plugin"

/**
 * Returns true if the given path targets a deep-analysis session directory:
 *   - .claude/sessions/__da_live__/*   (active session)
 *   - .claude/sessions/exploration-cache/*  (exploration cache)
 *   - .claude/sessions/da-*/*          (archived sessions)
 */
function isDaSessionPath(filePath: string): boolean {
  return (
    filePath.includes(".claude/sessions/__da_live__/") ||
    filePath.includes(".claude/sessions/exploration-cache/") ||
    /\.claude\/sessions\/da-[^/]+\//.test(filePath)
  )
}

/**
 * Returns true if the bash command targets a deep-analysis session directory.
 */
function isDaSessionCommand(command: string): boolean {
  return (
    command.includes(".claude/sessions/__da_live__") ||
    command.includes(".claude/sessions/exploration-cache") ||
    command.includes(".claude/sessions/da-")
  )
}

export const CoreToolsHooks: Plugin = async ({ project, client, $, directory }) => {
  return {
    /**
     * tool.execute.before — converted from PreToolUse (Write|Edit|Bash matcher)
     *
     * NOTE: This hook OBSERVES tool calls and logs them. It cannot grant
     * auto-approval. For autonomous session file writes, configure
     * permission.write and permission.bash in opencode.json instead.
     *
     * NOTE: This hook does NOT fire for subagent tool calls (issue #5894).
     * Coverage is primary agent only.
     */
    "tool.execute.before": async (input, output) => {
      const toolName: string = (input as any).tool_name ?? ""
      const toolInput: Record<string, unknown> = (input as any).tool_input ?? {}

      // Only act on write, edit, bash — equivalent to source matcher Write|Edit|Bash
      if (!["write", "edit", "bash"].includes(toolName)) {
        return
      }

      const debugEnabled = process.env["AGENT_ALCHEMY_HOOK_DEBUG"] === "1"

      const debug = (msg: string) => {
        if (debugEnabled) {
          const logPath = process.env["AGENT_ALCHEMY_HOOK_LOG"] ?? "/tmp/agent-alchemy-hook.log"
          // Best-effort async log; errors are swallowed to avoid disrupting tool execution
          $`echo "[core-tools-hooks] ${msg}" >> ${logPath}`.catch(() => {})
        }
      }

      if (toolName === "write" || toolName === "edit") {
        const filePath = (toolInput["file_path"] as string) ?? ""
        if (!filePath) {
          debug("No file_path found")
          return
        }

        debug(`Tool: ${toolName}, file_path: ${filePath}`)

        if (isDaSessionPath(filePath)) {
          debug(`DA session path detected — would auto-approve in Claude Code: ${filePath}`)
          // UNRESOLVED: unsupported_hook:auto_approve_permission_decision | functional | auto-approve permission decision | Configure permission.write=allow in opencode.json; this plugin cannot grant approval
        }
      }

      if (toolName === "bash") {
        const command = (toolInput["command"] as string) ?? ""
        if (!command) {
          debug("No command found")
          return
        }

        debug(`Tool: bash, command: ${command.slice(0, 200)}`)

        if (isDaSessionCommand(command)) {
          debug(`DA session bash command detected — would auto-approve in Claude Code`)
          // UNRESOLVED: unsupported_hook:auto_approve_permission_decision | functional | auto-approve permission decision | Configure permission.bash=allow in opencode.json; this plugin cannot grant approval
        }
      }
    },
  }
}
