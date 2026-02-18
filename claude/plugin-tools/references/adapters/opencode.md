# OpenCode Adapter

Platform adapter for converting Claude Code plugins to OpenCode format.

OpenCode (anomalyco/opencode) is a TypeScript/Bun-based AI coding agent with a client/server architecture and TUI frontend. It provides a rich extension system with four complementary layers: skills (SKILL.md files loaded via the native `skill` tool), custom agents (markdown files with YAML frontmatter), commands (slash-command templates), and JS/TS plugins (event-driven extensions with lifecycle hooks). OpenCode natively discovers `.claude/skills/` directories, making Agent Alchemy skill files partially compatible out of the box.

**Research sources**: OpenCode official documentation (opencode.ai/docs), GitHub repository (github.com/anomalyco/opencode), DeepWiki analysis, GitHub issues/PRs (#5958, #5894, #6177, #6252). Confidence: High for tool mappings, directory structure, and configuration (based on official docs and source code); Medium for plugin hook edge cases (subagent hook bypass documented in issue #5894).

**Important note**: This adapter targets `anomalyco/opencode` (the active TypeScript project at opencode.ai), NOT `opencode-ai/opencode` (an archived Go project that moved to Crush). The previous adapter v1.0.0 incorrectly targeted the archived project.

---

## Platform Metadata

| Field | Value |
|-------|-------|
| name | OpenCode |
| slug | opencode |
| documentation_url | https://opencode.ai/docs |
| repository_url | https://github.com/anomalyco/opencode |
| plugin_docs_url | https://opencode.ai/docs/plugins |
| notes | OpenCode has a full extension system with skills, agents, commands, plugins, and custom tools. Skills use SKILL.md files and are discovered from 6 directory paths including `.claude/skills/`. The `@opencode-ai/plugin` SDK provides lifecycle hooks via JS/TS plugins. |

## Directory Structure

| Field | Value |
|-------|-------|
| plugin_root | .opencode/ |
| skill_dir | skills/ |
| agent_dir | agents/ |
| hook_dir | plugins/ |
| reference_dir | null |
| config_dir | ./ |
| file_extension | .md |
| naming_convention | kebab-case |
| notes | Skills are SKILL.md files in `.opencode/skills/{name}/SKILL.md` (project-level) or `~/.config/opencode/skills/` (user-level). OpenCode also discovers skills from `.claude/skills/`, `.agents/skills/`, `~/.claude/skills/`, and `~/.agents/skills/`. Agents are markdown files in `.opencode/agents/{name}.md`. Commands are markdown files in `.opencode/commands/{name}.md`. Plugins (JS/TS hooks) go in `.opencode/plugins/`. Custom tools go in `.opencode/tools/`. Config file is `opencode.json` (NOT `.opencode.json`) at project root or `.opencode/opencode.json`. Reference files have no dedicated directory — content should be inlined into skill bodies or loaded via the `instructions` config array in `opencode.json`. |

## Tool Name Mappings

### File Operations

| Claude Code Tool | Target Equivalent | Notes |
|-----------------|-------------------|-------|
| Read | read | OpenCode's `read` tool reads file contents. Supports `file_path`, `offset`, and `limit` parameters. |
| Write | write | OpenCode's `write` tool writes content to files. Requires `file_path` and `content` parameters. Requires user permission approval. |
| Edit | edit | OpenCode's `edit` tool modifies files. Supports replace/insert/delete operations. Legacy aliases: `patch`, `multiedit`. Requires user permission approval. |
| Glob | glob | OpenCode's `glob` tool finds files by pattern. Accepts `pattern` (required) and `path` (optional) parameters. Supports exclude patterns. |
| Grep | grep | OpenCode's `grep` tool searches file contents. Accepts `pattern` (required), `path` (optional), `include` (optional glob filter), and `literal_text` (optional boolean) parameters. |
| NotebookEdit | null | OpenCode has no Jupyter notebook editing tool. |

### Execution

| Claude Code Tool | Target Equivalent | Notes |
|-----------------|-------------------|-------|
| Bash | bash | OpenCode's `bash` tool executes shell commands using PTY sessions. Accepts `command` (required), `cwd` (optional), `env` (optional), and `timeout` (optional) parameters. Requires user permission approval. Shell is configurable in `opencode.json`. |
| Task | task | OpenCode's `task` tool spawns a subagent in an isolated session context. Accepts `prompt` (required), `description` (optional), `subagent_type` (optional: `build` or `plan`), and `command` (optional: name of a custom agent to use). Each invocation starts a fresh isolated context — no persistent cross-call state. Subagents cannot use the `question` tool. Model is determined by the agent's static config, not per-task. |

### Agent Coordination

| Claude Code Tool | Target Equivalent | Notes |
|-----------------|-------------------|-------|
| TeamCreate | null | OpenCode has no team/multi-agent orchestration system. The closest approach is sequential or parallel `task` tool calls with explicit context passing in prompts. Hub-and-spoke patterns (like deep-analysis) must be restructured as orchestrated `task` calls. |
| TeamDelete | null | No team management in OpenCode. |
| TaskCreate | partial:todowrite | OpenCode's `todowrite` tool creates/updates todo items. Not a structured task management system — more like a session-scoped scratchpad. Cannot set task dependencies, owners, or statuses beyond basic completion. |
| TaskUpdate | partial:todowrite | Same `todowrite` tool handles updates. Limited to simple status changes. |
| TaskList | partial:todoread | OpenCode's `todoread` tool reads current todo list state. Returns all items, no filtering by owner or status. |
| TaskGet | partial:todoread | Same `todoread` tool. No per-task retrieval by ID — reads the full list. |
| SendMessage | null | No inter-agent messaging. Subagents are isolated. The only way to pass context between agents is through the `task` tool's prompt parameter. |

### User Interaction

| Claude Code Tool | Target Equivalent | Notes |
|-----------------|-------------------|-------|
| AskUserQuestion | question | OpenCode's `question` tool (merged in v1.1.8) supports single-select, multi-select, and confirm dialogs with 1-8 questions and 2-8 options each. **Only available to primary agents, not subagents.** Free-text input is not supported through `question`. Skills invoked via `task` tool that need user interaction must structure questions into their initial prompt. |

### Web & Research

| Claude Code Tool | Target Equivalent | Notes |
|-----------------|-------------------|-------|
| WebSearch | websearch | OpenCode's `websearch` tool uses Exa AI for web searching. Accepts query parameters. |
| WebFetch | webfetch | OpenCode's `webfetch` tool retrieves content from URLs. Accepts `url` (required), `format` (required: `text`, `markdown`, or `html`), and `timeout` (optional) parameters. Maximum response size is 5MB. Requires user permission approval. |

### MCP Tools

| Claude Code Tool | Target Equivalent | Notes |
|-----------------|-------------------|-------|
| mcp__context7__resolve-library-id | context7_resolve-library-id | OpenCode uses `{mcpName}_{toolName}` naming convention for MCP tools (single underscore separator instead of double-underscore). MCP servers are configured in `opencode.json` under the `mcp` key (NOT `mcpServers`). Both `local` (stdio) and `remote` (HTTP/SSE) transport types are supported. OAuth support available. |
| mcp__context7__query-docs | context7_query-docs | Same naming pattern: `{mcpName}_{toolName}`. |
| mcp__* (generic pattern) | {mcpName}_{toolName} | OpenCode discovers MCP tools at startup by connecting to each configured MCP server and calling `ListTools`. Tool names follow `{mcpName}_{toolName}` format. All MCP tool invocations require user permission approval. Config supports `{env:VAR_NAME}` for secrets. |

## Model Tier Mappings

| Claude Code Model | Target Equivalent | Notes |
|------------------|-------------------|-------|
| opus | anthropic/claude-opus-4-5 | OpenCode uses `provider/model-id` format. Full ID with date: `anthropic/claude-opus-4-5-20251101`. Also available: `anthropic/claude-opus-4-6`. Models are configured per agent type in `opencode.json` under `agents.{agentName}.model`. OpenCode supports Anthropic, OpenAI, Google, Groq, AWS Bedrock, Azure, OpenRouter, GitHub Copilot, and self-hosted providers. |
| sonnet | anthropic/claude-sonnet-4-5 | Full ID with date: `anthropic/claude-sonnet-4-5-20250929`. Also available: `anthropic/claude-sonnet-4-20250514`. The `task` subagent type maps naturally to Sonnet-tier usage. |
| haiku | anthropic/claude-haiku-4-5 | Full ID: `anthropic/claude-haiku-4-5-20251001`. Also available: `anthropic/claude-3-5-haiku`. Suitable for lightweight tasks. |
| default | anthropic/claude-sonnet-4-5 | Default to Sonnet-tier for general use. OpenCode has built-in agent types: `coder` (main), `task` (sub-agent), `title` (session naming), `summarizer` (context compaction). Use `/models` command at runtime to list available model IDs. |

## Frontmatter Translations

### Skill Frontmatter

| Claude Code Field | Target Field | Notes |
|------------------|-------------|-------|
| name | embedded:filename | OpenCode skills derive their name from the directory name containing SKILL.md (e.g., `skills/deep-analysis/SKILL.md` becomes skill `deep-analysis`). The `skill` tool loads skills by name from a merged registry of 6 directory paths. |
| description | description | Supported in SKILL.md frontmatter. Required for skill discovery and shown when listing available skills. |
| argument-hint | embedded:body | Use `$ARGUMENTS`, `$1`, `$2` etc. as placeholders in the skill body. OpenCode auto-detects `$NAME` placeholders (uppercase letters, numbers, underscores) and prompts the user for values when invoked as a command. |
| user-invocable | user-invocable | Supported in SKILL.md frontmatter. Controls whether the skill appears in the command dialog. Default: true. |
| disable-model-invocation | null | OpenCode has no concept of preventing model auto-invocation of skills. The `skill` tool is always available to the model. |
| allowed-tools | null | OpenCode does not support per-skill tool restrictions. Tool restrictions are only configurable at the agent level via the `permission` frontmatter field in agent definitions. |
| model | null | OpenCode does not support per-skill model overrides. Models are configured per agent type in `opencode.json`. Commands (not skills) support a `model` frontmatter field for per-command model override. |

### Agent Frontmatter

| Claude Code Field | Target Field | Notes |
|------------------|-------------|-------|
| name | embedded:filename | Agent name derived from `.md` filename in `.opencode/agents/`. |
| description | description | Required field in agent frontmatter. Shown in agent selection UI. |
| model | model | Supported. Format: `anthropic/claude-sonnet-4-5` (provider/model-id). |
| tools | permission | Tool access controlled via `permission` field with per-tool allow/ask/deny values and glob patterns for file restrictions. Boolean shorthand supported (e.g., `write: false` to deny write access). |
| skills | null | Skills are not assigned to agents in frontmatter. Agents invoke skills dynamically at runtime via the native `skill` tool. All skills in the merged registry are accessible to any agent. |

## Hook/Lifecycle Event Mappings

### Event Mappings

| Claude Code Event | Target Event | Notes |
|------------------|-------------|-------|
| PreToolUse | tool.execute.before | JS/TS plugin hook. Can intercept and modify tool execution. **Known limitation**: Does not fire for subagent tool calls (issue #5894). For auto-approve behavior, prefer the `permission` config in `opencode.json` with `"allow"` value instead of a plugin hook. |
| PostToolUse | tool.execute.after | JS/TS plugin hook. Processes results after tool execution. Same subagent limitation as PreToolUse. |
| Stop | partial:session.deleted | JS/TS plugin hook. Fires when a session is deleted. Not an exact match for Claude Code's Stop event (which fires at end of each response). `session.idle` may be closer for some use cases. |
| SessionStart | session.created | JS/TS plugin hook. Fires when a new session begins. |
| Notification | partial:tui.toast.show | JS/TS plugin hook. Can trigger TUI toast notifications. Not a direct equivalent — Claude Code's Notification is a system event, OpenCode's is a display action. |

### Hook Configuration

OpenCode hooks are implemented as JS/TS plugins using the `@opencode-ai/plugin` SDK. Plugin files are placed in `.opencode/plugins/` (project-level) or `~/.config/opencode/plugins/` (user-level).

Example plugin implementing PreToolUse and PostToolUse hooks:

```typescript
import type { Plugin } from "@opencode-ai/plugin"

export const MyPlugin: Plugin = async ({ project, client, $, directory, worktree }) => {
  return {
    "tool.execute.before": async (event) => {
      // Intercept/modify tool execution before it runs
      // event contains tool name, parameters, session info
    },
    "tool.execute.after": async (event) => {
      // Process results after tool execution completes
      // event contains tool name, result, session info
    },
    "session.created": async (event) => {
      // Handle session start
    }
  }
}
```

Full event list: `command.executed`, `file.edited`, `file.watcher.updated`, `installation.updated`, `lsp.client.diagnostics`, `lsp.updated`, `message.part.removed`, `message.part.updated`, `message.removed`, `message.updated`, `permission.asked`, `permission.replied`, `server.connected`, `session.created`, `session.compacted`, `session.deleted`, `session.diff`, `session.error`, `session.idle`, `session.status`, `session.updated`, `shell.env`, `todo.updated`, `tool.execute.before`, `tool.execute.after`, `tui.prompt.append`, `tui.command.execute`, `tui.toast.show`.

For Claude Code's auto-approve PreToolUse hooks, the recommended OpenCode equivalent is setting the `permission` config in `opencode.json` rather than implementing a plugin:

```json
{
  "permission": {
    "bash": "allow",
    "write": "allow",
    "edit": "allow"
  }
}
```

## Composition Mechanism

| Field | Value |
|-------|-------|
| mechanism | reference |
| syntax | skill({ name: "skill-name" }) |
| supports_cross_plugin | true |
| supports_recursive | true |
| max_depth | unlimited |
| notes | OpenCode agents use the native `skill` tool to load SKILL.md content by name from a merged registry of 6 directory paths (`.opencode/skills/`, `.claude/skills/`, `.agents/skills/`, and their `~/.config/` or `~/` global equivalents). Skills are resolved by name — no file path references needed. Loaded skill content is injected into the conversation and protected from context compaction pruning. Claude Code's `Read ${CLAUDE_PLUGIN_ROOT}/skills/{name}/SKILL.md` pattern should be converted to skill tool invocations by name. Cross-plugin composition is natively supported since all skills from all discovery paths are merged into a single registry. For reference files that cannot be separate skills, use the `instructions` config array in `opencode.json` to inject files as global context, or inline content into the skill body. |

## Path Resolution

| Field | Value |
|-------|-------|
| root_variable | null |
| resolution_strategy | registry |
| same_plugin_pattern | skill({ name: "{skill-name}" }) |
| cross_plugin_pattern | skill({ name: "{skill-name}" }) |
| notes | OpenCode resolves skills by name from a merged registry — no file path variables exist. Skills from any discovery directory (`.opencode/skills/`, `.claude/skills/`, etc.) are all accessible by name regardless of origin. For file references within tool calls (e.g., `read`, `bash`), use absolute paths or paths relative to the working directory. The working directory is set at startup via `-c` flag or defaults to the current directory. The `instructions` config array in `opencode.json` accepts file paths and glob patterns for global context injection. Template variables `{file:./path}` and `{env:VAR_NAME}` are supported in `opencode.json` config values. |

## Adapter Version

| Field | Value |
|-------|-------|
| adapter_version | 2.0.0 |
| target_platform_version | 1.2.6 |
| last_updated | 2026-02-17 |
| author | research-agent |
| changelog | v2.0.0: Complete adapter rewrite targeting anomalyco/opencode (TypeScript, active project at opencode.ai) instead of opencode-ai/opencode (Go, archived). The previous adapter v1.0.0 targeted the wrong project entirely. Major changes: Read→read (was view), Task→task (was agent), WebFetch→webfetch (was fetch), AskUserQuestion→question (was null), WebSearch→websearch (was null), all hooks now supported via JS/TS plugin SDK (were null), composition mechanism changed from none to reference (skill tool), agents now supported via .opencode/agents/ (was null), model IDs require anthropic/ prefix, config file is opencode.json (was .opencode.json), MCP config key is mcp (was mcpServers), task management via todoread/todowrite (was null). 43+ stale mappings corrected, 15+ new features added. |
