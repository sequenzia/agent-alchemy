<!-- docs/index.md -->
# Claude Alchemy

A toolkit for AI-assisted software development using [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Claude Alchemy combines two Claude Code plugins with a real-time Task Manager application in a single pnpm monorepo. The three subsystems communicate through a **filesystem-as-message-bus** pattern — no shared runtime code, no database, no IPC.

---

## :material-view-dashboard: Task Manager

A real-time Kanban board for monitoring Claude AI task execution. Server Components fetch task data from `~/.claude/tasks/`, Chokidar watches for changes, and SSE pushes updates to the browser — all without polling.

- **Location:** `apps/task-manager/`
- **Stack:** Next.js 16.1.4, React 19.2.3, TanStack Query v5, Tailwind CSS v4, shadcn/ui
- **Runs on:** `http://localhost:3030`

[Task Manager docs :material-arrow-right:](task-manager/overview.md){ .md-button }

## :material-tools: Tools Plugin

Developer tools for feature development, codebase analysis, documentation generation, code review, and git workflows. Invoked from Claude Code with `/tools:{skill-name}`.

- **Location:** `plugins/tools/` (v0.2.2)
- **10 agents, 13 skills** — including `feature-dev`, `codebase-analysis`, `docs-manager`, `code-quality`, `deep-analysis`, and more

[Tools Plugin docs :material-arrow-right:](plugins/tools-plugin.md){ .md-button }

### :material-file-document-edit: SDD Plugin

Spec-Driven Development: create specifications through guided interviews, analyze them for completeness, decompose them into tasks, and execute those tasks autonomously. Invoked with `/sdd:{skill-name}`.

- **Location:** `plugins/sdd/` (v0.2.6)
- **2 agents, 4 skills** — `create-spec`, `analyze-spec`, `create-tasks`, `execute-tasks`

[SDD Plugin docs :material-arrow-right:](plugins/overview.md){ .md-button }

---

## Quick Start

=== "Full Setup"

    ```bash
    git clone git@github.com:sequenzia/claude-alchemy.git
    cd claude-alchemy
    pnpm install
    pnpm dev:task-manager    # http://localhost:3030
    ```

=== "Plugins Only"

    Plugins are markdown-only with no build step. Install them directly in Claude Code:

    ```bash
    # From the Claude Code REPL
    /install-plugin /path/to/claude-alchemy/plugins/tools
    /install-plugin /path/to/claude-alchemy/plugins/sdd
    ```

!!! tip "Prerequisites"
    - **Node.js** >= 18 and **pnpm** >= 8
    - **Claude Code** installed and configured
    - Plugins require no additional dependencies — they are pure Markdown

---

## Documentation Map

| Section | Description |
|---------|-------------|
| [Getting Started](getting-started.md) | Installation, configuration, and first steps |
| **Architecture** | |
| [Overview](architecture/overview.md) | System design, component relationships, and design decisions |
| [Filesystem Message Bus](architecture/filesystem-message-bus.md) | How subsystems communicate through the filesystem |
| [Data Flow](architecture/data-flow.md) | Request lifecycle and real-time update pipeline |
| **Task Manager** | |
| [Overview](task-manager/overview.md) | App architecture and key patterns |
| [API Reference](task-manager/api-reference.md) | REST and SSE endpoint documentation |
| [Real-Time System](task-manager/real-time-system.md) | Chokidar, SSE, and TanStack Query integration |
| [Components](task-manager/components.md) | React component tree and responsibilities |
| [Security](task-manager/security.md) | Path traversal guards and input validation |
| **Plugins** | |
| [Plugin Overview](plugins/overview.md) | Plugin architecture, skill format, and agent model tiering |
| [Tools Plugin](plugins/tools-plugin.md) | All 13 skills and 10 agents in the developer tools plugin |
| [SDD Plugin](plugins/sdd-plugin.md) | Spec-Driven Development workflow and skills |
| **Development** | |
| [Setup](development/setup.md) | Dev environment, running locally, and project structure |

---

## Tech Stack

| Technology | Version | Role |
|------------|---------|------|
| Next.js | 16.1.4 | App framework (App Router, Server Components) |
| React | 19.2.3 | UI library |
| TypeScript | 5 | Type safety across the monorepo |
| TanStack Query | v5.90.20 | Server state management and cache invalidation |
| Tailwind CSS | v4 | Utility-first styling |
| shadcn/ui | latest | Accessible UI components (Radix primitives) |
| Chokidar | 5 | Filesystem watching for real-time updates |
| pnpm | >= 8 | Workspace-aware package manager |

!!! info "Plugin Runtime"
    The two plugins (`tools` and `sdd`) have **no runtime dependencies**. They are collections of Markdown files — skills with YAML frontmatter and agent system prompts — that Claude Code loads and executes directly. No build step required.

---

## License

Claude Alchemy is released under the [MIT License](https://github.com/sequenzia/claude-alchemy/blob/main/LICENSE).
