# Claude Alchemy

A monorepo combining Claude Code plugins and applications for an integrated AI-assisted development workflow.

## Overview

| Package | Description |
|---------|-------------|
| **claude-tools** | Claude Code plugins for PRD generation, feature development, and Git workflows |
| **claude-apps/task-manager** | Real-time Kanban board for Claude AI task visualization |

## Quick Install

### Plugins

Add the full plugin collection:

```bash
claude plugins add sequenzia/claude-alchemy
```

Or install individual plugins:

```bash
claude plugins add sequenzia/claude-alchemy/claude-tools/prd-tools
claude plugins add sequenzia/claude-alchemy/claude-tools/dev-tools
```

### Task Manager

```bash
cd claude-apps/task-manager
pnpm install
pnpm dev  # Starts on http://localhost:3030
```

## Plugins

### prd-tools (v0.3.1)

Generate Product Requirements Documents through interactive interviews with depth-aware templates and research capabilities.

| Command | Description |
|---------|-------------|
| `/prd-tools:create` | Start PRD creation workflow |
| `/prd-tools:analyze <path>` | Analyze existing PRD for quality issues |
| `/prd-tools:create-tasks <path>` | Generate Claude Code native Tasks from PRD |

**Features:**
- Three depth levels (high-level, detailed, full technical)
- Adaptive interviews with proactive recommendations
- On-demand research for technical docs and compliance
- PRD quality analysis with interactive resolution
- Native Claude Code Task generation with dependencies

### dev-tools (v0.2.6)

Developer tools for feature development, codebase analysis, Git workflows, and release automation.

| Command | Description |
|---------|-------------|
| `/dev-tools:analyze-codebase [path]` | Generate comprehensive codebase analysis report |
| `/dev-tools:feature-dev <description>` | Feature development workflow (7 phases) |
| `/dev-tools:git-commit` | Stage and commit with conventional message |
| `/dev-tools:git-push` | Push to remote with automatic rebase |
| `/dev-tools:release [version]` | Python package release workflow |
| `/dev-tools:bump-plugin-version` | Bump plugin version in this repository |

**Features:**
- 7-phase feature development workflow
- Codebase exploration with parallel agents
- Architecture design with trade-off analysis
- Code review with confidence scoring
- 9-step release verification pipeline

## Applications

### Task Manager

A Next.js Kanban board that visualizes Claude AI tasks from `~/.claude/tasks/`.

**Features:**
- Three-column board (Pending, In Progress, Completed)
- Real-time updates via Server-Sent Events
- Task filtering and search
- Dependency visualization
- Dark/light theme support

**Tech Stack:** Next.js 16, TanStack Query, shadcn/ui, Tailwind CSS v4

## Workflow Integration

The plugins and apps work together for a complete development workflow:

```
PRD Creation → Task Generation → Task Visualization → Implementation → Release
     ↓               ↓                  ↓                   ↓            ↓
 prd-tools     prd-tools:          task-manager        dev-tools:    dev-tools
              create-tasks              app            feature-dev    (release)
```

## Development

### Prerequisites

- Node.js >= 18
- pnpm >= 8

### Setup

```bash
# Clone the repository
git clone https://github.com/sequenzia/claude-alchemy.git
cd claude-alchemy

# Install dependencies
pnpm install

# Start task-manager
pnpm dev:task-manager
```

### Workspace Commands

```bash
pnpm dev:task-manager     # Start task-manager dev server
pnpm build:task-manager   # Build task-manager for production
pnpm lint                 # Run linting across all workspaces
```

## License

MIT
