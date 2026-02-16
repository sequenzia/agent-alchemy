# Getting Started

This guide walks you through installing Agent Alchemy's plugins, running the Task Manager, and trying your first workflow.

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI installed and authenticated
- Node.js >= 18.0.0
- pnpm >= 8.0.0

## Install Plugins

Install the plugin groups you want to use. Each plugin is independent — pick only what you need, or install them all:

```bash
# The SDD pipeline (specs → tasks → execution)
claude plugins install agent-alchemy/agent-alchemy-sdd-tools

# Codebase analysis and exploration
claude plugins install agent-alchemy/agent-alchemy-core-tools

# Feature dev, code review, docs, changelog
claude plugins install agent-alchemy/agent-alchemy-dev-tools

# TDD workflows (RED-GREEN-REFACTOR)
claude plugins install agent-alchemy/agent-alchemy-tdd-tools

# Git commit automation
claude plugins install agent-alchemy/agent-alchemy-git-tools
```

Verify your installation:

```bash
claude plugins list
```

You should see the installed plugins with their versions and skill counts.

!!! tip "Plugin Dependencies"
    Most plugins work independently. The exceptions: SDD Tools' TDD variant skills (`/create-tdd-tasks`, `/execute-tdd-tasks`) require TDD Tools to be installed. Several skills across dev-tools and sdd-tools optionally use Core Tools' `/deep-analysis` for codebase exploration.

## Run the Task Manager

The Task Manager provides a real-time Kanban view of task execution. To use it, clone the repository and start the dev server:

```bash
git clone https://github.com/sequenzia/agent-alchemy.git
cd agent-alchemy
pnpm install
pnpm dev:task-manager
```

Open [http://localhost:3030](http://localhost:3030) in your browser. The dashboard automatically picks up task files from `~/.claude/tasks/` and displays them in real time via SSE.

For details on the dashboard features and API, see the [Task Manager](task-manager.md) guide.

## Your First Workflow

### Option 1: Explore a Codebase

Navigate to any project and run deep analysis:

```
/deep-analysis
```

This launches a multi-agent exploration team that maps architecture, traces execution paths, and produces a structured synthesis of the codebase. Results are cached for 24 hours.

See [Core Tools](plugins/core-tools.md) for full details.

### Option 2: Create a Spec and Execute It

The SDD pipeline is Agent Alchemy's core workflow. Start by creating a spec:

```
/create-spec
```

This launches an adaptive interview that gathers requirements and produces a structured specification. Then decompose it into tasks and execute:

```
/create-tasks specs/SPEC-My-Feature.md
/execute-tasks --task-group my-feature
```

The executor launches autonomous agents in dependency-ordered waves. Open the Task Manager to watch progress in real time.

See [SDD Tools](plugins/sdd-tools.md) for the full pipeline guide.

### Option 3: Generate Tests

Point the test generator at acceptance criteria or source files:

```
/generate-tests
```

It auto-detects your test framework (pytest, Jest, or Vitest) and spawns parallel test-writer agents. For a full RED-GREEN-REFACTOR cycle on a specific feature, use:

```
/tdd-cycle
```

See [TDD Tools](plugins/tdd-tools.md) for all TDD workflows.

## Configuration

Plugin behavior is customized via `.claude/agent-alchemy.local.md` in your project root. This file is not committed to version control, so each project (or developer) can have different settings.

Common settings to configure first:

| Setting | Default | What It Controls |
|---------|---------|-----------------|
| `deep-analysis.cache-ttl-hours` | `24` | How long exploration cache lasts |
| `tdd.framework` | `auto` | Override test framework detection |
| `execute-tasks.max_parallel` | `5` | Max concurrent agents per wave |

See [Configuration](configuration.md) for the full settings reference.

## VS Code Extension

If you're building your own Claude Code plugins, install the VS Code extension for schema validation and autocomplete:

1. Clone the repo and build the VSIX:
    ```bash
    cd extensions/vscode
    npm install
    npm run package
    ```
2. Install in VS Code: `Extensions → Install from VSIX...`
3. Open any workspace with a `.claude-plugin/plugin.json` file — the extension activates automatically

See [VS Code Extension](vscode-extension.md) for details.

## Next Steps

| Want to... | Go to... |
|-----------|----------|
| Understand the system design | [Architecture](architecture.md) |
| Browse all plugins and skills | [Plugin Overview](plugins/index.md) |
| Build a feature with agent teams | [Dev Tools → `/feature-dev`](plugins/dev-tools.md) |
| Contribute to Agent Alchemy | [Contributing](contributing.md) |
