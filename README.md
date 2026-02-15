# Agent Alchemy

A plugin suite and developer toolkit that extends Claude Code into a structured development platform — from specs to tasks to autonomous execution.

## What is Agent Alchemy?

Agent Alchemy is an open-source toolkit for AI and software engineers who use Claude Code. It adds structured development workflows on top of Claude Code through four plugins, a real-time task manager, and a VS Code extension — all designed to work together as an integrated pipeline.

Everything is built with Claude Code for Claude Code. The plugins are plain markdown — readable, editable, and version-controlled like any other code.

## Components

### Claude Code Plugins

Four plugin groups providing 15 skills and 9 agents:

| Plugin | Description |
|--------|-------------|
| **[SDD Tools](claude/sdd-tools/)** | Spec-Driven Development — turn ideas into specs, specs into tasks, and tasks into autonomous execution |
| **[Dev Tools](claude/dev-tools/)** | Feature development, code review, architecture patterns, documentation, and changelog management |
| **[Core Tools](claude/core-tools/)** | Codebase analysis, deep exploration with multi-agent teams, and language patterns |
| **[Git Tools](claude/git-tools/)** | Conventional Commits automation |

### [Task Manager](apps/task-manager/)

A Next.js real-time Kanban dashboard for monitoring autonomous task execution. Tasks update live via filesystem watching and Server-Sent Events.

### [VS Code Extension](extensions/vscode/)

Schema validation, YAML frontmatter autocomplete, and hover documentation for Claude Code plugin development.

## Getting Started

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI installed
- Node.js >= 18.0.0
- pnpm >= 8.0.0

### Install Plugins

```bash
# Install from the Claude Code marketplace
claude plugins install agent-alchemy/agent-alchemy-sdd-tools
claude plugins install agent-alchemy/agent-alchemy-dev-tools
claude plugins install agent-alchemy/agent-alchemy-core-tools
claude plugins install agent-alchemy/agent-alchemy-git-tools
```

### Run Task Manager

```bash
pnpm install
pnpm dev:task-manager
# Open http://localhost:3030
```

### Build VS Code Extension

```bash
cd extensions/vscode
npm install
npm run build
npm run package
```

## Architecture

Agent Alchemy follows a **markdown-as-code** philosophy where AI agent behaviors, workflows, and domain knowledge are defined entirely in Markdown with YAML frontmatter. Skills compose by loading other skills at runtime, and complex workflows orchestrate teams of specialized agents with different model tiers (Opus for synthesis, Sonnet for exploration).

```
claude/                          # Plugins (markdown-as-code)
├── core-tools/                  # Analysis & exploration
├── dev-tools/                   # Development lifecycle
├── sdd-tools/                   # Spec-Driven Development
└── git-tools/                   # Git automation

apps/task-manager/               # Real-time dashboard
├── src/lib/fileWatcher.ts       # Chokidar -> SSE
├── src/app/api/events/route.ts  # SSE endpoint
└── src/components/              # React UI

extensions/vscode/               # Developer tooling
├── src/frontmatter/             # YAML validation
└── schemas/                     # JSON Schemas for plugin contracts
```

## License

MIT
