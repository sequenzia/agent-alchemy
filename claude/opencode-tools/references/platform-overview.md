# OpenCode Platform Overview

Comprehensive reference for the OpenCode platform (anomalyco/opencode). This document covers the extension system, configuration, tools, models, and key differences from Claude Code.

**Target version**: v1.2.10
**Documentation**: https://opencode.ai/docs
**Repository**: https://github.com/anomalyco/opencode

> **Important**: This targets `anomalyco/opencode` (TypeScript/Bun, active project at opencode.ai), NOT `opencode-ai/opencode` (archived Go project that moved to Crush).

---

## Platform Identity

| Field | Value |
|-------|-------|
| Name | OpenCode |
| Runtime | TypeScript / Bun |
| Version | 1.2.10 |
| Website | https://opencode.ai |
| Architecture | Client/server with TUI frontend |
| Config format | JSONC (`opencode.json`) |
| Extension system | Skills, Agents, Commands, Plugins (JS/TS) |

---

## Extension Types

OpenCode provides four complementary extension layers:

### Skills

Markdown files (`SKILL.md`) with YAML frontmatter loaded via the native `skill` tool. Skills are the primary way to inject structured prompts and workflows.

- **Location**: `{discovery-path}/skills/{name}/SKILL.md`
- **Invocation**: `skill({ name: "skill-name" })` or `/skill-name` in the TUI
- **See**: `skill-guide.md` for full format reference

### Agents

Markdown files with YAML frontmatter that define custom agent personas with specific models, permissions, and system prompts.

- **Location**: `.opencode/agents/{name}.md`
- **Invocation**: `@agent-name` in the TUI or via `task` tool with `command: "agent-name"`
- **See**: `agent-guide.md` for full format reference

### Commands

Markdown template files that act as workflow shortcuts with `$VARIABLE` placeholder support and optional per-command model overrides.

- **Location**: `.opencode/commands/{name}.md`
- **Invocation**: `/{name}` in the TUI
- **See**: `command-guide.md` for full format reference

### Plugins (JS/TS)

Event-driven extensions using the `@opencode-ai/plugin` SDK with lifecycle hooks for tool interception, session management, and TUI integration.

- **Location**: `.opencode/plugins/` (project) or `~/.config/opencode/plugins/` (global)
- **Format**: ESM-only TypeScript/JavaScript
- **SDK**: `@opencode-ai/plugin`

---

## Directory Layout

### Project-Level Structure

```
project-root/
├── opencode.json              # Project config (JSONC, at root or .opencode/)
├── .opencode/
│   ├── skills/                # Project skills
│   │   └── {name}/SKILL.md
│   ├── agents/                # Custom agents
│   │   └── {name}.md
│   ├── commands/              # Custom commands
│   │   └── {name}.md
│   ├── plugins/               # JS/TS plugins
│   │   └── {name}.ts
│   └── tools/                 # Custom tools
│       └── {name}.ts
├── AGENTS.md                  # Primary rules file
└── CLAUDE.md                  # Fallback rules file
```

### Skill Discovery Paths (6 locations)

OpenCode discovers skills from these directories, merged into a flat registry:

| Priority | Path | Scope |
|----------|------|-------|
| 1 | `.opencode/skills/` | Project |
| 2 | `.claude/skills/` | Project (Claude Code compat) |
| 3 | `.agents/skills/` | Project |
| 4 | `~/.config/opencode/skills/` | Global |
| 5 | `~/.claude/skills/` | Global (Claude Code compat) |
| 6 | `~/.agents/skills/` | Global |

All skills from all paths are merged into a single registry and accessed by name.

### Agent Discovery

| Path | Scope |
|------|-------|
| `.opencode/agents/` | Project |
| `~/.config/opencode/agents/` | Global |

### Command Discovery

| Path | Scope |
|------|-------|
| `.opencode/commands/` | Project |
| `~/.config/opencode/commands/` | Global |

---

## Configuration Format

OpenCode uses `opencode.json` (JSONC — comments allowed) at the project root or inside `.opencode/`.

### Template Variables

- `{file:./path}` — Inline file contents as a config value
- `{env:VAR_NAME}` — Inject environment variable value

### Key Configuration Sections

```jsonc
{
  // Agent model configuration
  "agent": {
    "coder": {
      "model": "anthropic/claude-sonnet-4-6"
    },
    "task": {
      "model": "anthropic/claude-sonnet-4-6"
    }
  },

  // MCP server configuration
  "mcp": {
    "server-name": {
      "type": "local",           // "local" (stdio) or "remote" (HTTP/SSE)
      "command": ["npx", "..."], // for local
      "url": "https://...",      // for remote
      "env": {
        "API_KEY": "{env:MY_KEY}"
      }
    }
  },

  // Global instruction files (context injection)
  "instructions": [
    "path/to/file.md",
    "path/to/dir/*.md"
  ],

  // Permission settings
  "permission": {
    "read": "allow",
    "glob": "allow",
    "grep": "allow",
    "write": "ask",
    "edit": "ask",
    "bash": "ask"
  }
}
```

### Merge Semantics

- Project `opencode.json` merges with global `~/.config/opencode/opencode.json`
- Project settings take precedence
- Agent configs merge at the agent-name level

---

## Built-in Tools

### File Operations

| Tool | Purpose | Permission |
|------|---------|------------|
| `read` | Read file contents (supports `file_path`, `offset`, `limit`) | None |
| `write` | Write content to files (`file_path`, `content`) | Required |
| `edit` | Modify files (replace/insert/delete operations) | Required |
| `glob` | Find files by pattern (`pattern`, optional `path`) | None |
| `grep` | Search file contents (`pattern`, optional `path`, `include`, `literal_text`) | None |
| `patch` | Alias for `edit` (legacy) | Required |
| `multiedit` | Alias for `edit` (legacy) | Required |

### Execution

| Tool | Purpose | Permission |
|------|---------|------------|
| `bash` | Execute shell commands via PTY (`command`, optional `cwd`, `env`, `timeout`) | Required |
| `task` | Spawn subagent in isolated context (`prompt`, optional `description`, `subagent_type`, `command`) | None |

### User Interaction

| Tool | Purpose | Permission |
|------|---------|------------|
| `question` | Interactive dialogs: single-select, multi-select, confirm (1-8 questions, 2-8 options) | None |
| `skill` | Load and execute a skill by name | None |

### Task Management

| Tool | Purpose | Permission |
|------|---------|------------|
| `todowrite` | Create/update todo items (session-scoped scratchpad) | None |
| `todoread` | Read current todo list state | None |

### Web & Research

| Tool | Purpose | Permission |
|------|---------|------------|
| `websearch` | Web search via Exa AI | None |
| `webfetch` | Fetch URL content (`url`, `format`: text/markdown/html, optional `timeout`; max 5MB) | Required |

### Development

| Tool | Purpose | Permission |
|------|---------|------------|
| `lsp` | Language Server Protocol integration | None |
| `list` | List available tools and their parameters | None |

### MCP Tools

MCP tools use `{mcpName}_{toolName}` naming (single underscore separator):
- Example: `context7_resolve-library-id`, `context7_query-docs`
- All MCP tool invocations require user permission approval

---

## Model System

### Provider/Model Format

Models use `provider/model-id` format. Example: `anthropic/claude-sonnet-4-6`

### 75+ Supported Providers

Including: Anthropic, OpenAI, Google, Groq, AWS Bedrock, Azure, OpenRouter, GitHub Copilot, and self-hosted providers.

Use `/models` at runtime to list available model IDs.

### Built-in Agent Types

| Agent Type | Purpose | Default Model |
|------------|---------|---------------|
| `coder` | Main interactive agent | Configurable |
| `task` | Subagent for `task` tool calls | Configurable |
| `title` | Session title generation | Lightweight |
| `summarizer` | Context compaction | Lightweight |

### Model Tiers

| Tier | Recommended Model ID | Use Case |
|------|---------------------|----------|
| Opus | `anthropic/claude-opus-4-6` | Synthesis, architecture, review |
| Sonnet | `anthropic/claude-sonnet-4-6` | General use, exploration |
| Haiku | `anthropic/claude-haiku-4-5` | Lightweight, quick tasks |

---

## Permission System

Three permission levels with per-tool granular control:

| Level | Meaning |
|-------|---------|
| `allow` | Auto-approved, no user prompt |
| `ask` | Requires user approval each time |
| `deny` | Blocked entirely |

### Glob Pattern Matching

Permissions support glob patterns for file-specific rules:

```jsonc
{
  "permission": {
    "write": "ask",
    "write:src/**": "allow",      // Auto-allow writes in src/
    "write:node_modules/**": "deny", // Block writes to node_modules
    "bash": "ask",
    "bash:npm test": "allow"       // Auto-allow specific commands
  }
}
```

**Resolution**: Last-match-wins when multiple patterns match.

### Permission Scopes

- **Global**: `~/.config/opencode/opencode.json` → `permission` key
- **Project**: `opencode.json` → `permission` key
- **Agent-level**: Agent frontmatter → `permission` field (overrides project)

---

## MCP Integration

Configure MCP servers in `opencode.json` under the `mcp` key:

```jsonc
{
  "mcp": {
    "context7": {
      "type": "remote",
      "url": "https://mcp.context7.com/mcp"
    },
    "my-local-server": {
      "type": "local",
      "command": ["npx", "-y", "@my-org/mcp-server"],
      "env": {
        "API_KEY": "{env:MY_API_KEY}"
      }
    }
  }
}
```

- **Tool naming**: `{mcpName}_{toolName}` (single underscore)
- **Transport**: `local` (stdio) and `remote` (HTTP/SSE)
- **OAuth**: Supported for remote servers
- **Discovery**: Tools discovered at startup via `ListTools`

---

## Rules System

### Primary Rules File

`AGENTS.md` at project root (primary) or `CLAUDE.md` (fallback).

### Additional Instructions

The `instructions` config array in `opencode.json` injects additional files as global context:

```jsonc
{
  "instructions": [
    "docs/coding-standards.md",
    ".opencode/references/*.md"
  ]
}
```

Files and globs are resolved relative to the project root and injected into the agent's context.

---

## Key Differences from Claude Code

| Feature | Claude Code | OpenCode |
|---------|------------|----------|
| Team orchestration | Full (TeamCreate, SendMessage, etc.) | None — use sequential/parallel `task` calls |
| Per-skill tool restrictions | `allowed-tools` frontmatter | Not supported — tool restrictions only at agent level |
| Per-skill model override | Not supported | Not supported (commands support `model` frontmatter) |
| Skill composition | File-path loading (`Read ${CLAUDE_PLUGIN_ROOT}/...`) | Name-based registry (`skill({ name: "..." })`) |
| Question tool in subagents | Available | Not available — primary agent only |
| Plugin SDK | None (hooks are JSON config) | `@opencode-ai/plugin` (ESM JS/TS) |
| Free-text input via question | Supported (via "Other" option) | Not supported |
| Reference files | Dedicated directory | No dedicated dir — inline in body or use `instructions` config |
| Config format | JSON (settings.json, .mcp.json) | JSONC (`opencode.json` — single file) |
| Hook format | JSON config in `hooks.json` | JS/TS plugin files with event handlers |
| Rules file | `CLAUDE.md` | `AGENTS.md` (primary), `CLAUDE.md` (fallback) |

---

## Lifecycle Events (Plugin Hooks)

Full event list for JS/TS plugins:

| Event | Description | Version |
|-------|-------------|---------|
| `tool.execute.before` | Intercept before tool execution | All |
| `tool.execute.after` | Process after tool execution | All |
| `tool.definition` | Modify tool definitions at startup | v1.1.65+ |
| `session.created` | New session started | All |
| `session.compacted` | Context compaction occurred | All |
| `session.deleted` | Session removed | All |
| `session.idle` | Session became idle | All |
| `session.status` | Session status changed | All |
| `session.updated` | Session data updated | All |
| `session.diff` | Session diff available | All |
| `session.error` | Session error occurred | All |
| `shell.env` | Shell environment setup | v1.2.7+ |
| `message.updated` | Message content changed | All |
| `message.removed` | Message deleted | All |
| `message.part.updated` | Message part changed | All |
| `message.part.removed` | Message part deleted | All |
| `file.edited` | File was modified | All |
| `file.watcher.updated` | File watcher triggered | All |
| `todo.updated` | Todo list changed | All |
| `permission.asked` | Permission prompt shown | All |
| `permission.replied` | User responded to permission | All |
| `command.executed` | Command was executed | All |
| `installation.updated` | Installation state changed | All |
| `lsp.updated` | LSP state changed | All |
| `lsp.client.diagnostics` | LSP diagnostics received | All |
| `server.connected` | Server connection established | All |
| `tui.prompt.append` | Text appended to TUI prompt | All |
| `tui.command.execute` | TUI command executed | All |
| `tui.toast.show` | Toast notification displayed | All |

**Known limitation**: `tool.execute.before` and `tool.execute.after` do NOT fire for subagent tool calls (issue #5894).

---

## Plugin SDK Example

```typescript
import type { Plugin } from "@opencode-ai/plugin"

export const MyPlugin: Plugin = async ({ project, client, $, directory, worktree }) => {
  return {
    "tool.execute.before": async (event) => {
      // Intercept/modify tool execution before it runs
    },
    "tool.execute.after": async (event) => {
      // Process results after tool execution
    },
    "session.created": async (event) => {
      // Handle new session
    }
  }
}
```

**Requirements**:
- ESM only (`import`, not `require`)
- v1.2.9+: MCP tool attachment metadata available in tool events
- v1.2.10+: Localhost sidecar processes auto-skipped during plugin discovery
