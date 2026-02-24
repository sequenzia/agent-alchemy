# Conversion Knowledge

## Target Platform
- **Platform:** OpenCode
- **Platform version:** 1.2.10
- **Adapter version:** 2.1.1
- **Confidence basis:** adapter+research

## Tool Name Mappings

| Claude Code Tool | Target Equivalent | Notes | Confidence |
|------------------|-------------------|-------|------------|
| Read | read | File contents with line range support. Supports `file_path`, `offset`, `limit`. | high |
| Write | write | Creates/overwrites files. Requires `file_path` and `content`. Requires user permission approval. | high |
| Edit | edit | String replacement edits. Supports replace/insert/delete. Legacy aliases: `patch`, `multiedit`. Requires user permission. | high |
| Glob | glob | File discovery by pattern. Accepts `pattern` (required) and `path` (optional). Supports exclude patterns. | high |
| Grep | grep | Regex content search. Accepts `pattern` (required), `path` (optional), `include` (optional glob filter), `literal_text` (optional boolean). | high |
| Bash | bash | PTY shell execution. Accepts `command` (required), `cwd` (optional), `env` (optional), `timeout` (optional). Requires user permission. | high |
| Task | task | Spawns subagent in isolated context. Accepts `prompt` (required), `description` (optional), `subagent_type` (optional: `build`/`plan`), `command` (optional: custom agent name), `task_id` (optional: resume previous task). Subagents cannot use `question` tool by default. Subagents cannot spawn other subagents. | high |
| WebSearch | websearch | Exa AI search. Requires `OPENCODE_ENABLE_EXA=1` env flag. | high |
| WebFetch | webfetch | URL retrieval. Accepts `url` (required), `format` (required: `text`/`markdown`/`html`), `timeout` (optional). Max 5MB. | high |
| AskUserQuestion | question | Single/multi-select dialogs. Primary agents only by default permission. Subagents cannot use unless explicitly configured with `permission: { question: "allow" }`. Header max 30 chars. | medium |
| NotebookEdit | null | No Jupyter notebook editing tool. | high |
| TeamCreate | null | No team/multi-agent orchestration. Restructure as orchestrated `task` tool calls with explicit context passing. | high |
| TeamDelete | null | No team management. | high |
| TaskCreate | partial:todowrite | Simple session-scoped scratchpad. No dependencies, owners, or structured statuses. | high |
| TaskUpdate | partial:todowrite | Same `todowrite` tool. Limited to simple status changes. | high |
| TaskList | partial:todoread | Reads full todo list. No filtering by owner/status. | high |
| TaskGet | partial:todoread | Same `todoread`. No per-task retrieval by ID. | high |
| SendMessage | null | No inter-agent messaging. Subagents are isolated. Context passed via `task` tool prompt only. | high |
| mcp__context7__resolve-library-id | context7_resolve-library-id | Single underscore separator: `{mcpName}_{toolName}`. | high |
| mcp__context7__query-docs | context7_query-docs | Same naming pattern. | high |
| mcp__* (generic) | {mcpName}_{toolName} | All MCP tools follow `{mcpName}_{toolName}` format. Configured in `opencode.json` under `mcp` key. | high |

## Model Tier Mappings

| Claude Tier | Target Equivalent | Notes | Confidence |
|-------------|-------------------|-------|------------|
| opus | anthropic/claude-opus-4-6 | Current flagship. Configured per agent in `opencode.json` under `agent.{name}.model`. | high |
| sonnet | anthropic/claude-sonnet-4-6 | Current balanced tier. Adaptive thinking supported (v1.2.7+). | high |
| haiku | anthropic/claude-haiku-4-5 | Full ID: `anthropic/claude-haiku-4-5-20251001`. Fastest tier. | high |
| default | anthropic/claude-sonnet-4-6 | Default to Sonnet. Built-in agent types: `coder` (main), `task` (subagent), `title`, `summarizer`. | high |

## Skill Frontmatter Mappings

| Claude Field | Target Field | Notes | Confidence |
|-------------|-------------|-------|------------|
| name | embedded:filename | Derived from directory name: `skills/{name}/SKILL.md`. | high |
| description | description | Required in SKILL.md frontmatter. Shown in skill listing. | high |
| argument-hint | embedded:body | Use `$ARGUMENTS`, `$1`, `$2` etc. as placeholders. OpenCode auto-detects `$NAME` placeholders. | high |
| user-invocable | user-invocable | Controls appearance in command dialog. Default: true. | high |
| disable-model-invocation | null | No concept of preventing model auto-invocation. `skill` tool is always available. | high |
| allowed-tools | null | No per-skill tool restrictions. Tool restrictions only at agent level via `permission` frontmatter. | high |
| model | null | No per-skill model overrides. Models configured per agent type in `opencode.json`. Commands (not skills) support `model` frontmatter. | high |

## Agent Frontmatter Mappings

| Claude Field | Target Field | Notes | Confidence |
|-------------|-------------|-------|------------|
| name | embedded:filename | Derived from `.md` filename in `.opencode/agents/`. | high |
| description | description | Required. Shown in agent selection UI. | high |
| model | model | Format: `anthropic/claude-sonnet-4-6` (provider/model-id). | high |
| tools | permission | Per-tool `allow`/`ask`/`deny` with glob patterns. Boolean shorthand: `write: false`, `bash: true`. | high |
| (subagent indicator) | mode | Values: `primary`, `subagent`, `all` (default: `all`). Use `mode: subagent` for agents spawned via task tool. | high |
| skills | null | Skills not assigned to agents in frontmatter. Agents invoke skills dynamically via native `skill` tool at runtime. All skills accessible from merged registry. | high |

## Hook Event Mappings

| Claude Event | Target Event | Notes | Confidence |
|-------------|-------------|-------|------------|
| PreToolUse | tool.execute.before | JS/TS plugin hook. Does NOT fire for subagent tool calls (issue #5894, still open). | high |
| PostToolUse | tool.execute.after | Same subagent limitation. | high |
| Stop | partial:session.deleted | Not exact match. `session.idle` may be closer for some use cases. | high |
| SessionStart | session.created | Direct equivalent. | high |
| Notification | partial:tui.toast.show | Display action, not system event. | high |

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
| skill_file_pattern | {name}/SKILL.md |

## Composition Mechanism

| Field | Value |
|-------|-------|
| mechanism | reference |
| syntax | skill({ name: "skill-name" }) |
| supports_cross_plugin | true |
| supports_recursive | true |
| max_depth | unlimited |

## Path Resolution

| Field | Value |
|-------|-------|
| root_variable | null |
| resolution_strategy | registry |
| same_plugin_pattern | skill({ name: "{skill-name}" }) |
| cross_plugin_pattern | skill({ name: "{skill-name}" }) |

## Config File Format

| Field | Value |
|-------|-------|
| config_file | opencode.json |
| config_format | jsonc |
| agent_config_path | agent.{name}.model |
| mcp_config_key | mcp |
| instruction_key | instructions |
| permission_key | permission |

## Known Limitations

- **Hook subagent bypass (issue #5894)**: `tool.execute.before`/`tool.execute.after` only fire for primary agent. Subagents bypass plugin hooks entirely.
- **No native Claude Code hooks.json**: OpenCode does not read `hooks.json` format. Must convert to JS/TS plugins.
- **Question tool nesting (issue #7654)**: Questions from grandchild subagents don't appear in TUI.
- **No per-skill tool restrictions**: `allowed-tools` maps to null. Agent-level `permission` is the only alternative.
- **No team orchestration**: TeamCreate/SendMessage/TeamDelete map to null. Hub-and-spoke patterns must be restructured as sequential/parallel `task` calls.
- **No inter-agent messaging**: Subagents are fully isolated. Context passing only via `task` prompt parameter.
- **Subagent-to-subagent blocked**: Subagents cannot spawn other subagents (`task: false` hardcoded).
- **No reference directory**: Content must be inlined into skill body or loaded via `instructions` array in `opencode.json`.
- **`disable-model-invocation` unsupported**: Skills are always discoverable by the model via `skill` tool.
