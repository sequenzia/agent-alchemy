<!-- docs/development/setup.md -->
# Development Setup

This guide walks through setting up a local development environment for the Claude Alchemy monorepo, including the Task Manager app, Claude Code plugins, and the VS Code extension.

## Prerequisites

Before you begin, make sure you have the following installed:

| Requirement | Minimum Version | Check Command |
|-------------|-----------------|---------------|
| Node.js     | 18.0.0          | `node -v`     |
| pnpm        | 8.0.0           | `pnpm -v`     |
| Git         | Any recent      | `git --version` |

!!! tip "Installing pnpm"
    If you have Node.js but not pnpm, install it with `corepack enable` (Node 16.13+) or `npm install -g pnpm`.

## Installation

Clone the repository and install dependencies:

```bash
git clone git@github.com:sequenzia/claude-alchemy.git
cd claude-alchemy
pnpm install
```

`pnpm install` resolves dependencies for all workspace packages defined in `pnpm-workspace.yaml`. Only packages under `apps/*` are part of the pnpm workspace — plugins are markdown-only and have no dependencies to install.

## Monorepo Layout

```
claude-alchemy/
├── apps/
│   └── task-manager/        # Next.js 16 app (workspace package)
├── plugins/
│   ├── tools/               # Developer tools plugin (markdown-only)
│   └── sdd/                 # Spec-driven development plugin (markdown-only)
├── extensions/
│   └── vscode/              # VS Code extension (separate npm project)
├── internal/
│   └── docs/                # Internal documentation and cheatsheets
├── .claude/
│   └── settings.json        # Claude Code environment settings
├── .claude-plugin/
│   └── marketplace.json     # Plugin registry
├── package.json             # Root monorepo scripts & engine constraints
└── pnpm-workspace.yaml      # Workspace config (apps/* only)
```

## Running the Task Manager

The Task Manager is a Next.js 16 application that provides a real-time Kanban board for visualizing Claude AI task files.

### Development Server

```bash
pnpm dev:task-manager
```

This starts the Next.js dev server at **<http://localhost:3030>** with hot module replacement enabled.

!!! note "Port Configuration"
    The Task Manager runs on port **3030** by default, configured in `apps/task-manager/package.json` via `next dev -p 3030`.

### Production Build

```bash
pnpm build:task-manager
```

This runs `next build` for the Task Manager, producing an optimized production bundle.

### Task Data Directory

The Task Manager reads task files from `~/.claude/tasks/`. The specific task list directory is controlled by the `CLAUDE_CODE_TASK_LIST_ID` environment variable set in `.claude/settings.json`:

```json title=".claude/settings.json"
{
  "env": {
    "CLAUDE_CODE_TASK_LIST_ID": "claude-alchemy"
  }
}
```

This means tasks are read from `~/.claude/tasks/claude-alchemy/`. If you want to work with a different task list, update this value.

## Linting

Run linting across all workspace packages:

```bash
pnpm lint
```

This executes `pnpm -r lint`, which recursively runs the `lint` script in every workspace package. Currently this runs ESLint for the Task Manager.

## Plugin Development

Claude Alchemy includes two Claude Code plugins:

| Plugin | Invoke Prefix | Description |
|--------|---------------|-------------|
| `claude-alchemy-tools` (v0.2.2) | `/tools:{skill}` | Developer tools — 10 skills, 5 agents |
| `claude-alchemy-sdd` (v0.2.6)   | `/sdd:{skill}`   | Spec-driven development — 4 skills, 2 agents |

### Editing Plugins

Plugins are **markdown-only** — there is no build step, no compilation, and no dependencies to install. To modify a plugin:

1. Edit the skill or agent `.md` files directly under `plugins/tools/` or `plugins/sdd/`
2. Changes take effect immediately — Claude Code reads plugin files at runtime

!!! info "Plugin File Conventions"
    - **Skills** are named `SKILL.md` with YAML frontmatter, located under `skills/{skill-name}/`
    - **Agents** are named `{agent-name}.md` (kebab-case), located under `agents/`
    - Reference materials live in `skills/{skill-name}/references/` and are loaded at runtime

### Versioning Plugins

Plugin versions are tracked in **two** places that must stay in sync:

- `plugins/{name}/.claude-plugin/plugin.json` — the plugin's own manifest
- `.claude-plugin/marketplace.json` — the root-level plugin registry

Use the built-in skill to bump versions consistently:

```bash
# From within a Claude Code session
/tools:bump-plugin-version
```

### Plugin Directory Structure

```
plugins/tools/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest (name, version, metadata)
├── agents/
│   └── {agent-name}.md      # Agent definitions (kebab-case)
├── skills/
│   └── {skill-name}/
│       ├── SKILL.md          # Skill definition with YAML frontmatter
│       └── references/       # Reference materials loaded at runtime
├── hooks/                    # PreToolUse / PostToolUse hooks (if any)
└── rules/                    # Project rules applied by Claude Code
```

## VS Code Extension

The repository includes a VS Code extension (`claude-code-schemas`) that provides schema validation, autocomplete, and hover documentation for Claude Code plugin files.

### Setup

```bash
cd extensions/vscode
npm install
```

!!! warning "Separate Package Manager"
    The VS Code extension uses **npm**, not pnpm. It is a standalone project and is not part of the pnpm workspace.

### Build

```bash
cd extensions/vscode
npm run build
```

This runs esbuild to bundle the extension into `dist/extension.js`.

### Package

```bash
cd extensions/vscode
npm run package
```

This creates a `.vsix` file that can be installed in VS Code via **Extensions > Install from VSIX**.

### What It Validates

The extension provides JSON schema validation for:

| File Pattern | Schema |
|-------------|--------|
| `.claude-plugin/plugin.json` | Plugin manifest |
| `hooks/hooks.json` | Hook configuration |
| `.mcp.json` | MCP server configuration |
| `.lsp.json` | LSP configuration |
| `marketplace.json` | Plugin marketplace registry |

## Configuration Reference

| File | Purpose |
|------|---------|
| `package.json` (root) | Monorepo scripts (`dev:task-manager`, `build:task-manager`, `lint`) and engine constraints (Node >= 18, pnpm >= 8) |
| `pnpm-workspace.yaml` | Declares workspace packages — only `apps/*`; plugins are excluded |
| `.claude/settings.json` | Claude Code environment: sets `CLAUDE_CODE_TASK_LIST_ID`, enables experimental agent teams, configures MCP servers |
| `.claude-plugin/marketplace.json` | Root plugin registry listing both `claude-alchemy-tools` and `claude-alchemy-sdd` |
| `apps/task-manager/package.json` | Task Manager dependencies (Next.js 16, React 19, TanStack Query, Chokidar, shadcn/ui) |
| `apps/task-manager/tsconfig.json` | TypeScript strict mode, bundler module resolution, `@/*` path alias mapping to `./src/*` |

## Environment Variables

The following environment variables are configured in `.claude/settings.json` and are available to Claude Code sessions:

| Variable | Value | Purpose |
|----------|-------|---------|
| `CLAUDE_CODE_TASK_LIST_ID` | `claude-alchemy` | Determines which task list directory to use under `~/.claude/tasks/` |
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | `1` | Enables experimental agent teams feature in Claude Code |

## Troubleshooting

!!! question "pnpm install fails with engine errors"
    Verify your Node.js version is 18+ and pnpm version is 8+. The root `package.json` enforces these minimums via the `engines` field.

!!! question "Task Manager shows no tasks"
    Ensure the directory `~/.claude/tasks/claude-alchemy/` exists and contains `.json` task files. The Task Manager reads from this path based on the `CLAUDE_CODE_TASK_LIST_ID` setting.

!!! question "Port 3030 is already in use"
    Either stop the other process using port 3030, or modify the dev script in `apps/task-manager/package.json` to use a different port: `"dev": "next dev -p <new-port>"`.

!!! question "Plugin changes not taking effect"
    Claude Code reads plugin files at the start of each session. If you modified a plugin mid-session, start a new Claude Code session to pick up the changes.
