# CLAUDE.md

## Project Overview

Agent Alchemy is a monorepo that extends Claude Code into a structured development platform through markdown-as-code plugins, a real-time task dashboard, and a VS Code extension.

## Repository Structure

```
agent-alchemy/
├── claude/                    # Claude Code plugins (markdown-as-code)
│   ├── .claude-plugin/        # Plugin marketplace registry
│   ├── core-tools/            # Codebase analysis, deep exploration, language patterns
│   ├── dev-tools/             # Feature dev, code review, docs, changelog
│   ├── sdd-tools/             # Spec-Driven Development pipeline
│   └── git-tools/             # Git commit automation
├── apps/
│   └── task-manager/          # Next.js 16 real-time Kanban dashboard
├── extensions/
│   └── vscode/                # VS Code extension for plugin authoring
├── schemas/                   # JSON Schemas (source of truth for plugin contracts)
├── internal/docs/             # Internal documentation and analysis
└── site/                      # MkDocs documentation site (generated)
```

## Development Commands

```bash
# Task Manager
pnpm dev:task-manager          # Start dev server on port 3030
pnpm build:task-manager        # Production build

# VS Code Extension
cd extensions/vscode
npm install
npm run build                  # Build with esbuild
npm run watch                  # Watch mode
npm run package                # Package VSIX

# Linting
pnpm lint                      # Lint all packages
```

## Architecture Patterns

### Plugin System (claude/)

- **Skills** are defined in `SKILL.md` with YAML frontmatter and markdown body
- **Agents** are defined in `{name}.md` with YAML frontmatter (model, tools, skills)
- **Hooks** are JSON configs in `hooks/hooks.json` for lifecycle events
- Skills compose by loading other skills: `Read ${CLAUDE_PLUGIN_ROOT}/skills/{name}/SKILL.md`
- Complex skills use `references/` subdirectories for supporting materials

### Model Tiering

- **Opus**: Synthesis, architecture, review (high-reasoning tasks)
- **Sonnet**: Exploration, worker tasks (parallelizable broad search)
- **Haiku**: Simple/quick tasks (git commit)

### Key Skill Composition Chains

```
feature-dev -> deep-analysis -> code-explorer (sonnet) x N + code-synthesizer (opus) x 1
feature-dev -> code-architect (opus) x 2-3 -> code-reviewer (opus) x 3

create-spec -> deep-analysis (optional, for "new feature" type)
create-spec -> researcher agent (for technical research)

create-tasks -> reads spec -> generates task JSON
execute-tasks -> task-executor agent x N per wave -> writes execution context
```

### Task Manager (apps/task-manager/)

- Next.js 16 App Router with Server Components + Client Components
- Real-time: Chokidar watches `~/.claude/tasks/` -> SSE -> TanStack Query invalidation
- Global FileWatcher singleton survives HMR via `globalThis`

### VS Code Extension (extensions/vscode/)

- Ajv-based YAML frontmatter validation for skills and agents
- JSON schema validation for plugin.json, hooks.json, .mcp.json
- Schema-driven autocompletion and hover documentation

## Conventions

- **Git**: Conventional Commits (`type(scope): description`)
- **TypeScript**: Strict mode, functional patterns preferred
- **Styling**: Tailwind CSS v4 with shadcn/ui components (task manager)
- **Schemas**: `schemas/` is source of truth; `extensions/vscode/schemas/` is a copy for VSIX bundling

## Plugin Inventory

| Group | Skills | Agents | Version |
|-------|--------|--------|---------|
| core-tools | deep-analysis, codebase-analysis, language-patterns, project-conventions | code-explorer, code-synthesizer | 0.1.0 |
| dev-tools | feature-dev, architecture-patterns, code-quality, changelog-format, docs-manager, release-python-package | code-architect, code-reviewer, changelog-manager, docs-writer | 0.1.0 |
| sdd-tools | create-spec, analyze-spec, create-tasks, execute-tasks | researcher, spec-analyzer, task-executor | 0.1.0 |
| git-tools | git-commit | — | 0.1.0 |

## Settings

User preferences are stored in `.claude/agent-alchemy.local.md` (not committed):
- `deep-analysis.direct-invocation-approval`: Whether to require plan approval when user invokes directly (default: true)
- `deep-analysis.invocation-by-skill-approval`: Whether to require approval when loaded by another skill (default: false)
