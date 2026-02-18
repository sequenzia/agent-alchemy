# Conversion Knowledge

## Target Platform
- **Platform:** opencode
- **Platform version:** 1.2.6
- **Adapter version:** 2.1.0
- **Confidence basis:** adapter+research

## Tool Name Mappings

| Claude Code Tool | Target Equivalent | Notes | Confidence |
|------------------|-------------------|-------|------------|
| Read | read | Supports file_path, offset, limit parameters | high |
| Write | write | Requires file_path and content. Permission approval required | high |
| Edit | edit | Supports replace/insert/delete. Legacy aliases: patch, multiedit | high |
| Glob | glob | Accepts pattern (required) and path (optional) | high |
| Grep | grep | Accepts pattern, path, include, literal_text | high |
| Bash | bash | PTY sessions. Accepts command, cwd, env, timeout | high |
| Task | task | Spawns subagent. Accepts prompt, description, subagent_type (build/plan), command (custom agent name). Subagents cannot spawn subagents. | high |
| TeamCreate | null | No team/multi-agent orchestration. Restructure as sequential/parallel task calls. | high |
| TeamDelete | null | No team management | high |
| TaskCreate | partial:todowrite | Session-scoped scratchpad. No dependencies, owners, or structured statuses. | high |
| TaskUpdate | partial:todowrite | Same todowrite tool. Limited status changes. | high |
| TaskList | partial:todoread | Returns full list, no filtering by owner or status | high |
| TaskGet | partial:todoread | No per-task retrieval by ID | high |
| SendMessage | null | No inter-agent messaging. Context passed only through task prompt. | high |
| AskUserQuestion | question | 1-8 questions, 2-8 options. Only available to primary agents, not subagents. Must be explicitly enabled in agent tools config. | high |
| WebSearch | websearch | Uses Exa AI | high |
| WebFetch | webfetch | Accepts url, format (text/markdown/html), timeout. 5MB max | high |
| NotebookEdit | null | No Jupyter notebook support | high |
| mcp__context7__resolve-library-id | context7_resolve-library-id | Single underscore separator | high |
| mcp__context7__query-docs | context7_query-docs | Same pattern | high |
| mcp__* (generic) | {mcpName}_{toolName} | Server name + single underscore + tool name. Config in opencode.json under mcp key. Environment variables use `environment` key (not `env`). | high |

## Model Tier Mappings

| Claude Tier | Target Equivalent | Notes | Confidence |
|-------------|-------------------|-------|------------|
| opus | anthropic/claude-opus-4-6 | API ID: claude-opus-4-6. Current Anthropic flagship Feb 2026. | high |
| sonnet | anthropic/claude-sonnet-4-6 | API ID: claude-sonnet-4-6. Released 2026-02-17. | high |
| haiku | anthropic/claude-haiku-4-5 | Full ID: claude-haiku-4-5-20251001. Also via small_model config. | high |
| default | anthropic/claude-sonnet-4-6 | Sonnet 4.6 now recommended default. | high |

## Skill Frontmatter Mappings

| Claude Field | Target Field | Notes | Confidence |
|-------------|-------------|-------|------------|
| name | embedded:filename | Derived from directory name containing SKILL.md | high |
| description | description | Required. Shown when listing skills. | high |
| argument-hint | embedded:body | Use $ARGUMENTS, $1, $2 placeholders in skill body. Auto-detected. | high |
| user-invocable | user-invocable | Default: true. Controls command dialog visibility. | high |
| disable-model-invocation | null | Not supported. skill tool always available to model. | high |
| allowed-tools | null | No per-skill tool restrictions. Agent-level permission only. | high |
| model | null | No per-skill model overrides. Agent-level or opencode.json only. Commands support model field. | high |

## Agent Frontmatter Mappings

| Claude Field | Target Field | Notes | Confidence |
|-------------|-------------|-------|------------|
| name | embedded:filename | Derived from .md filename in .opencode/agents/ | high |
| description | description | Required. Shown in agent selection UI. | high |
| model | model | Format: anthropic/claude-opus-4-6 (provider/model-id) | high |
| tools | permission | Per-tool allow/ask/deny with glob patterns. Boolean shorthand. permission.task for subagent control. | high |
| skills | null | Skills invoked dynamically via skill tool at runtime. Not assigned in frontmatter. | high |
| — | hidden | hidden: true hides from @ autocomplete. Useful for internal subagents. | high |
| — | steps | Maximum agentic iterations. | high |
| — | temperature | Model temperature parameter. | high |
| — | top_p | Model top_p parameter. | high |
| — | color | Cosmetic UI color. | high |

## Hook Event Mappings

| Claude Event | Target Event | Notes | Confidence |
|-------------|-------------|-------|------------|
| PreToolUse | tool.execute.before | JS/TS plugin. Does NOT fire for subagent calls. For auto-approve, use permission config instead. | high |
| PostToolUse | tool.execute.after | Same subagent limitation. | high |
| Stop | partial:session.deleted | Not exact match. session.idle may be closer. | medium |
| SessionStart | session.created | Direct equivalent. | high |
| Notification | partial:tui.toast.show | Not direct equivalent. | medium |

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

## Known Limitations

- **No TeamCreate/SendMessage**: Hub-and-spoke patterns must be restructured as orchestrated task calls with context passing via prompts.
- **Subagents cannot spawn subagents**: Nested agent delegation chains must be flattened to single-level task calls from primary agent.
- **question tool not in subagents**: AskUserQuestion equivalent only works for primary agents. Skills invoked via task that need user input must structure questions into initial prompt.
- **Plugin hooks bypass subagents**: tool.execute.before/after do NOT fire for subagent tool calls. Use permission config for auto-approve.
- **No per-skill tool restrictions**: allowed-tools field maps to null. Tool restrictions only at agent level via permission.
- **No per-skill model overrides**: model field maps to null for skills. Only configurable per agent.
- **No reference_dir**: Reference files must be inlined into skill bodies or loaded via instructions config array in opencode.json.
- **No Stop hook re-activation**: Claude Code's Stop hook can re-inject feedback and resume. OpenCode has no equivalent.
