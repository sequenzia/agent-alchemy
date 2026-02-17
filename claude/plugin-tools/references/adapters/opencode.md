# OpenCode Adapter

Platform adapter for converting Claude Code plugins to OpenCode format.

OpenCode is a Go-based terminal AI coding assistant that provides an interactive TUI for working with multiple AI providers. It does not have a formal plugin system comparable to Claude Code's skill/agent/hook architecture. The closest equivalents are custom commands (markdown files), the `.opencode.json` configuration file, and the `OpenCode.md` project context file. This adapter maps Claude Code constructs to OpenCode's available mechanisms, with many features requiring flattening, inlining, or documenting as conversion gaps.

**Research sources**: OpenCode GitHub repository (github.com/opencode-ai/opencode), README.md, source code analysis of `internal/config/`, `internal/llm/agent/`, `internal/llm/tools/`, `internal/llm/prompt/`, `internal/tui/components/dialog/custom_commands.go`. Confidence: High for tool mappings and configuration (based on source code); Medium for best-practice patterns (limited community examples due to early-stage project).

**Important note**: OpenCode has been archived and the project has moved to "Crush" (github.com/charmbracelet/crush) by the original author and the Charm team. This adapter is based on OpenCode v0.0.55 (the final release). Future updates should evaluate whether to target Crush instead.

---

## Platform Metadata

| Field | Value |
|-------|-------|
| name | OpenCode |
| slug | opencode |
| documentation_url | https://github.com/opencode-ai/opencode |
| repository_url | https://github.com/opencode-ai/opencode |
| plugin_docs_url | https://github.com/opencode-ai/opencode#custom-commands |
| notes | OpenCode does not have a formal plugin system. The closest equivalents are custom commands (markdown files in `.opencode/commands/`), the `.opencode.json` configuration file, and the `OpenCode.md` project context file. The project has been archived and moved to Crush (github.com/charmbracelet/crush). |

## Directory Structure

| Field | Value |
|-------|-------|
| plugin_root | .opencode/ |
| skill_dir | commands/ |
| agent_dir | null |
| hook_dir | null |
| reference_dir | null |
| config_dir | ./ |
| file_extension | .md |
| naming_convention | kebab-case |
| notes | OpenCode custom commands are markdown files stored in `.opencode/commands/` (project-level, prefixed `project:`) or `~/.config/opencode/commands/` (user-level, prefixed `user:`). Subdirectories create colon-separated command IDs (e.g., `commands/git/commit.md` becomes `project:git:commit`). There is no separate agent or hook directory. Reference files have no dedicated location; content must be inlined into command files or placed in OpenCode.md. The config file `.opencode.json` lives at the project root (or `$HOME` or `$XDG_CONFIG_HOME/opencode/`). |

## Tool Name Mappings

### File Operations

| Claude Code Tool | Target Equivalent | Notes |
|-----------------|-------------------|-------|
| Read | view | OpenCode's `view` tool reads file contents. Supports `file_path`, `offset`, and `limit` parameters. Same core functionality as Claude Code's Read. |
| Write | write | OpenCode's `write` tool writes content to files. Requires `file_path` and `content` parameters. Requires user permission approval. |
| Edit | edit | OpenCode's `edit` tool modifies files. Requires user permission approval. |
| Glob | glob | OpenCode's `glob` tool finds files by pattern. Accepts `pattern` (required) and `path` (optional) parameters. |
| Grep | grep | OpenCode's `grep` tool searches file contents. Accepts `pattern` (required), `path` (optional), `include` (optional glob filter), and `literal_text` (optional boolean) parameters. |
| NotebookEdit | null | OpenCode has no Jupyter notebook editing tool. |

### Execution

| Claude Code Tool | Target Equivalent | Notes |
|-----------------|-------------------|-------|
| Bash | bash | OpenCode's `bash` tool executes shell commands. Accepts `command` (required) and `timeout` (optional) parameters. Requires user permission approval. Shell is configurable in `.opencode.json`. |
| Task | agent | OpenCode's `agent` tool spawns a read-only sub-agent with access to glob, grep, ls, view, and sourcegraph tools. Accepts a `prompt` parameter. The sub-agent cannot modify files (no bash, edit, write, patch). More limited than Claude Code's Task tool which supports full tool access and structured task management. |

### Agent Coordination

| Claude Code Tool | Target Equivalent | Notes |
|-----------------|-------------------|-------|
| TeamCreate | null | OpenCode has no team/multi-agent orchestration system. Its `agent` tool spawns a single read-only sub-agent per invocation. |
| TeamDelete | null | No team management in OpenCode. |
| TaskCreate | null | OpenCode has no task management system. The `agent` tool is fire-and-forget with a single prompt/response cycle. |
| TaskUpdate | null | No task state management. |
| TaskList | null | No task listing capability. |
| TaskGet | null | No task retrieval capability. |
| SendMessage | null | No inter-agent messaging. The `agent` sub-tool returns its result as a single response. |

### User Interaction

| Claude Code Tool | Target Equivalent | Notes |
|-----------------|-------------------|-------|
| AskUserQuestion | null | OpenCode has no structured user interaction tool. The AI communicates with the user through direct text output in the TUI. Permission requests are handled by the built-in permission system (allow/deny dialog), but there is no programmatic way to ask freeform questions and receive structured responses. Skill prompts that use AskUserQuestion should convert to instructional text directing the user to provide input via the chat interface. |

### Web & Research

| Claude Code Tool | Target Equivalent | Notes |
|-----------------|-------------------|-------|
| WebSearch | null | OpenCode has no web search tool. The `sourcegraph` tool can search public code repositories but does not perform general web searches. The `fetch` tool can retrieve content from URLs but requires knowing the URL in advance. |
| WebFetch | fetch | OpenCode's `fetch` tool retrieves content from URLs. Accepts `url` (required), `format` (required: `text`, `markdown`, or `html`), and `timeout` (optional) parameters. Maximum response size is 5MB. Requires user permission approval. |

### MCP Tools

| Claude Code Tool | Target Equivalent | Notes |
|-----------------|-------------------|-------|
| mcp__context7__resolve-library-id | context7_resolve-library-id | OpenCode uses `{mcpName}_{toolName}` naming convention for MCP tools (underscore separator instead of double-underscore). MCP servers are configured in `.opencode.json` under the `mcpServers` key. Both stdio and SSE transport types are supported. |
| mcp__context7__query-docs | context7_query-docs | Same naming pattern: `{mcpName}_{toolName}`. |
| mcp__* (generic pattern) | {mcpName}_{toolName} | OpenCode discovers MCP tools at startup by connecting to each configured MCP server and calling `ListTools`. Tool names follow `{mcpName}_{toolName}` format. All MCP tool invocations require user permission approval. |

## Model Tier Mappings

| Claude Code Model | Target Equivalent | Notes |
|------------------|-------------------|-------|
| opus | claude-4-opus | OpenCode supports specific model IDs from multiple providers. For Anthropic, use `claude-4-opus` (or `claude-3-opus` for older). Models are configured per agent type in `.opencode.json` under `agents.{agentName}.model`. OpenCode supports Anthropic, OpenAI, Google, Groq, AWS Bedrock, Azure, OpenRouter, GitHub Copilot, and self-hosted providers. |
| sonnet | claude-4-sonnet | Use `claude-4-sonnet` (or `claude-3.7-sonnet`, `claude-3.5-sonnet` for older). The `task` agent type (sub-agent) maps naturally to Sonnet-tier usage since it has restricted tools. |
| haiku | claude-3.5-haiku | Use `claude-3.5-haiku` (or `claude-3-haiku` for older). Suitable for lightweight tasks. Note: OpenCode's `title` agent is hardcoded to 80 max tokens regardless of model. |
| default | claude-4-sonnet | Default to Sonnet-tier for general use. OpenCode has 4 built-in agent types: `coder` (main), `task` (sub-agent), `title` (session naming), `summarizer` (context compaction). |

## Frontmatter Translations

### Skill Frontmatter

| Claude Code Field | Target Field | Notes |
|------------------|-------------|-------|
| name | embedded:filename | OpenCode custom commands derive their name from the filename (without `.md` extension). Subdirectory paths become colon-separated prefixes (e.g., `commands/git/commit.md` becomes `project:git:commit`). No frontmatter metadata system exists. |
| description | null | OpenCode auto-generates descriptions as "Custom command from {relPath}". There is no way to provide a custom description in the command file itself. |
| argument-hint | embedded:body | Named arguments use `$NAME` placeholders in the markdown body (e.g., `$ISSUE_NUMBER`). OpenCode auto-detects these and prompts the user for values. Pattern: uppercase letters, numbers, underscores, must start with a letter. |
| user-invocable | embedded:presence | All custom command files are user-invocable by definition. There is no equivalent to disabling user invocation. If a command file exists, it appears in the Ctrl+K command dialog. |
| disable-model-invocation | null | OpenCode has no concept of model-invocable commands. Custom commands can only be triggered by users through the command dialog (Ctrl+K). The AI model cannot invoke custom commands. |
| allowed-tools | null | OpenCode does not support per-command tool restrictions. All tools available to the agent type are always accessible. Tool restrictions are only enforced at the agent-type level (e.g., `task` agent has read-only tools). |
| model | null | OpenCode does not support per-command model overrides. Models are configured per agent type globally in `.opencode.json`. The user can switch models at runtime via Ctrl+O. |

### Agent Frontmatter

| Claude Code Field | Target Field | Notes |
|------------------|-------------|-------|
| name | embedded:config-key | OpenCode has 4 fixed agent types: `coder`, `task`, `title`, `summarizer`. These are defined in Go code, not in configuration files. There is no user-defined agent mechanism. Custom agents would need to be approximated as custom commands with specific instructions in the prompt body. |
| description | null | Agent descriptions are hardcoded in OpenCode's Go source code (system prompts). No configurable description field exists. |
| model | agents.{name}.model | Model is configurable per agent type in `.opencode.json` (e.g., `"agents": {"coder": {"model": "claude-4-sonnet"}}`). Supports full model ID strings. |
| tools | null | Tool sets are hardcoded per agent type in Go source code. The `coder` agent gets all tools; the `task` agent gets read-only tools (glob, grep, ls, view, sourcegraph). No user-configurable tool lists. |
| skills | null | OpenCode has no concept of skills assigned to agents. The closest equivalent is the `contextPaths` config which loads markdown files as system prompt context (e.g., `CLAUDE.md`, `OpenCode.md`). |

## Hook/Lifecycle Event Mappings

### Event Mappings

| Claude Code Event | Target Event | Notes |
|------------------|-------------|-------|
| PreToolUse | null | OpenCode has no hook/lifecycle event system. The permission system provides tool-level approval (allow/deny per invocation or per session) but does not support custom scripts or actions before tool execution. |
| PostToolUse | null | No post-tool hooks. OpenCode logs tool results internally but does not expose hooks for custom post-processing. |
| Stop | null | No session-end hooks. OpenCode supports auto-compact (summarization when context window fills) but this is not a hookable event. |
| SessionStart | null | No session-start hooks. OpenCode's `contextPaths` config auto-loads specified files at startup, which is the closest equivalent (loading `OpenCode.md`, `CLAUDE.md`, etc.). |
| Notification | null | No notification hooks. |

### Hook Configuration

OpenCode has no hook/lifecycle configuration system. The permission system is the closest concept, providing allow/deny/allow-for-session controls on tool invocations, but it cannot execute custom scripts or commands in response to events.

The `contextPaths` configuration in `.opencode.json` provides a limited form of session-start behavior by automatically loading specified markdown files into the system prompt context:

```json
{
  "contextPaths": [
    "OpenCode.md",
    "OpenCode.local.md",
    "CLAUDE.md",
    ".cursorrules"
  ]
}
```

This is not a true hook system but can be used to inject project-specific instructions at session start.

## Composition Mechanism

| Field | Value |
|-------|-------|
| mechanism | none |
| syntax | N/A |
| supports_cross_plugin | false |
| supports_recursive | false |
| max_depth | 0 |
| notes | OpenCode custom commands are self-contained markdown files with no import, include, or reference mechanism. There is no way for one command to load or invoke another command. The `agent` tool can spawn a sub-agent with a text prompt, but this is a runtime tool call, not a static composition mechanism. Skills that rely on Claude Code's `Read ${CLAUDE_PLUGIN_ROOT}/...` composition pattern must be flattened: all referenced content should be inlined into a single command file. For large reference materials, consider placing content in `OpenCode.md` (project context) which is automatically loaded into the system prompt, rather than trying to include it in individual commands. |

## Path Resolution

| Field | Value |
|-------|-------|
| root_variable | null |
| resolution_strategy | relative |
| same_plugin_pattern | .opencode/commands/{command-name}.md |
| cross_plugin_pattern | null |
| notes | OpenCode has no path variable equivalent to `${CLAUDE_PLUGIN_ROOT}`. Custom command files are located by directory convention (`.opencode/commands/` for project-level, `~/.config/opencode/commands/` for user-level). File paths within tool calls use absolute paths or paths relative to the working directory. There is no mechanism for one command to reference another command's file path. The working directory is set at startup via `-c` flag or defaults to the current directory. Cross-plugin references are not possible; each project has its own `.opencode/commands/` directory. |

## Adapter Version

| Field | Value |
|-------|-------|
| adapter_version | 1.0.0 |
| target_platform_version | 0.0.55 |
| last_updated | 2026-02-17 |
| author | research-agent |
| changelog | Initial adapter created from source code analysis of OpenCode v0.0.55 (final release before archival). Research included README.md, internal/config/, internal/llm/agent/, internal/llm/tools/, internal/llm/prompt/, and internal/tui/components/dialog/custom_commands.go. Note: OpenCode has been archived and moved to Crush (github.com/charmbracelet/crush); future adapter versions should evaluate targeting Crush instead. |
