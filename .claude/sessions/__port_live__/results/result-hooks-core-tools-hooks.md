# Conversion Result: hooks-core-tools-hooks

## Metadata

| Field | Value |
|-------|-------|
| Component ID | hooks-core-tools-hooks |
| Component Type | hooks |
| Group | core-tools |
| Name | hooks |
| Source Path | claude/core-tools/hooks/hooks.json |
| Target Path | .opencode/plugins/core-tools-hooks.ts |
| Fidelity Score | 85% |
| Fidelity Band | green |
| Status | full |

## Converted Content

~~~typescript
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
~~~

## Fidelity Report

| Mapping Type | Count | Weight | Contribution |
|-------------|-------|--------|-------------|
| Direct | 3 | 1.0 | 3.0 |
| Workaround | 3 | 0.7 | 2.1 |
| TODO | 0 | 0.2 | 0.0 |
| Omitted | 0 | 0.0 | 0.0 |
| **Total** | **6** | | **5.1 / 6.0 = 85%** |

**Notes:** Direct mappings are the three matcher tools (Write->write, Edit->edit, Bash->bash). Workaround mappings cover: (1) event type PreToolUse->tool.execute.before with subagent bypass caveat, (2) script path ${CLAUDE_PLUGIN_ROOT} resolved to relative paths in TypeScript module, (3) auto-approve permission decision behavior approximated via opencode.json permission config recommendation. The core auto-approve capability cannot be replicated in the plugin hook itself; it requires a static config change.

## Decisions

| Feature | Decision Type | Original | Converted | Rationale | Confidence | Resolution Mode |
|---------|-------------|----------|-----------|-----------|------------|----------------|
| Event type: PreToolUse | workaround | PreToolUse | tool.execute.before | Direct event mapping exists in conversion knowledge (high confidence). Subagent bypass (issue #5894) is a known limitation — hook fires for primary agent only. Converted with caveat documented in plugin header. | high | individual |
| Matcher tool: Write | direct | Write | write | Direct tool name mapping from conversion_knowledge.md. | high | individual |
| Matcher tool: Edit | direct | Edit | edit | Direct tool name mapping from conversion_knowledge.md. | high | individual |
| Matcher tool: Bash | direct | Bash | bash | Direct tool name mapping from conversion_knowledge.md. | high | individual |
| Script path: ${CLAUDE_PLUGIN_ROOT}/hooks/auto-approve-da-session.sh | workaround | bash ${CLAUDE_PLUGIN_ROOT}/hooks/auto-approve-da-session.sh | TypeScript module with inlined path logic | root_variable is null for OpenCode; no path variable equivalent. Shell script logic (is_da_session_path, case/match on tool_name) ported to TypeScript functions isDaSessionPath() and isDaSessionCommand(). Script internal tool name references (Write, Edit, Bash case labels) updated to OpenCode tool names (write, edit, bash). | high | individual |
| Auto-approve permission decision behavior | workaround | Outputs {"hookSpecificOutput":{"permissionDecision":"allow"}} to grant autonomous approval | opencode.json permission config recommendation (permission.write=allow, permission.bash=allow) documented in plugin header | OpenCode tool.execute.before cannot output permission decisions. The hook-converter.md explicitly states: "Auto-approve hooks should be converted to permission config entries in opencode.json rather than plugin hooks". Permission config is broader (session-wide, not path-scoped) but achieves the same autonomous execution goal. | high | individual |

## Gaps

| Feature | Reason | Severity | Workaround | User Acknowledged |
|---------|--------|----------|------------|-------------------|
| Path-scoped auto-approve (permissionDecision protocol) | OpenCode's tool.execute.before plugin hook has no mechanism to output a permission decision. The Claude Code permissionDecision:"allow" JSON protocol is Claude Code-specific. OpenCode's permission system is configured statically in opencode.json or interactively at runtime, not dynamically via hook output. | functional | Add `"permission": { "write": "allow", "bash": "allow" }` to .opencode/opencode.json to pre-grant write and bash tool operations at the session level. This is broader than the source's path-scoped approval but achieves autonomous execution. For tighter control, manually select "Allow for session" when OpenCode first prompts on a .claude/sessions/__da_live__/ path. | false |
| Subagent tool call coverage (issue #5894) | OpenCode's tool.execute.before does NOT fire for subagent tool calls. The deep-analysis skill spawns code-explorer and code-synthesizer subagents that perform writes to session directories — these writes are not covered by the plugin hook. | functional | The opencode.json permission config workaround (permission.write=allow) applies session-wide and covers subagent writes. The plugin hook alone is insufficient for full coverage. | false |

## Unresolved Incompatibilities

| Group Key | Feature | Severity | Category | Reason | Suggested Workaround | Confidence | Affected Locations |
|-----------|---------|----------|----------|--------|---------------------|------------|-------------------|
| unsupported_hook:auto_approve_permission_decision | Auto-approve permission decision (permissionDecision protocol) | functional | unsupported_hook | OpenCode plugin hooks cannot output permission decisions. tool.execute.before is observability-only — it cannot grant or deny tool invocations programmatically. | Add `"permission": { "write": "allow", "bash": "allow" }` to .opencode/opencode.json. This pre-approves write and bash tools at the session level, replacing the path-scoped auto-approve with a broader session-level grant. Alternatively, use "Allow for session" at first prompt each session. | high | 2 locations (write/edit path check, bash command check) |
| unsupported_hook:subagent_bypass_5894 | Subagent tool call coverage | functional | unsupported_hook | tool.execute.before does not fire for subagent tool calls (OpenCode issue #5894, still open as of v1.2.10). The deep-analysis skill spawns subagents that write to session directories; those writes bypass the plugin entirely. | Use opencode.json permission config (permission.write=allow) as the primary auto-approve mechanism. This applies session-wide including subagents, unlike the plugin hook which covers primary agent only. | high | 1 location (plugin header documentation) |
