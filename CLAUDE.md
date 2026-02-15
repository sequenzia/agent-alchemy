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

### Plugin Composition Patterns

- **Skill Loading**: Skills compose at runtime via `Read ${CLAUDE_PLUGIN_ROOT}/skills/{name}/SKILL.md` — prompt injection, not function calls
- **Hub-and-Spoke Teams**: `deep-analysis` spawns N explorer agents (Sonnet) + 1 synthesizer (Opus); explorers work independently, synthesizer merges with follow-ups + Bash investigation
- **Phase Workflows**: Complex skills use numbered phases with `"CRITICAL: Complete ALL N phases"` directives to prevent premature stopping
- **Reference Materials**: Large knowledge bases externalized into `references/` subdirectories (~6,000 lines total), loaded progressively when needed
- **Agent Tool Restrictions**: Architect/reviewer agents are read-only (Glob, Grep, Read only); executor agents can write — enforces separation of concerns
- **AskUserQuestion Enforcement**: All interactive skills route user interaction through `AskUserQuestion`, never plain text output

### Cross-Plugin Dependencies

`deep-analysis` (core-tools) is the keystone skill, loaded by 4 skills across 3 plugin groups:
- `codebase-analysis` (core-tools) — wraps deep-analysis with reporting + post-analysis actions
- `feature-dev` (dev-tools) — loads in Phase 2 for codebase exploration
- `docs-manager` (dev-tools) — loads for codebase understanding before doc generation
- `create-spec` (sdd-tools) — optionally loads for "new feature" type specs

These cross-plugin references resolve via `${CLAUDE_PLUGIN_ROOT}` — the resolution mechanism is implicit.

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
- **Schemas**: JSON schemas live in `extensions/vscode/schemas/` (bundled with the VS Code extension)

## Plugin Inventory

| Group | Skills | Agents | Version |
|-------|--------|--------|---------|
| core-tools | deep-analysis, codebase-analysis, language-patterns, project-conventions | code-explorer, code-synthesizer | 0.1.0 |
| dev-tools | feature-dev, architecture-patterns, code-quality, changelog-format, docs-manager, release-python-package | code-architect, code-reviewer, changelog-manager, docs-writer | 0.1.0 |
| sdd-tools | create-spec, analyze-spec, create-tasks, execute-tasks | researcher, spec-analyzer, task-executor | 0.1.0 |
| git-tools | git-commit | — | 0.1.0 |

## Critical Plugin Files

| File | Lines | Role |
|------|-------|------|
| `claude/core-tools/skills/deep-analysis/SKILL.md` | 350 | Keystone skill — hub-and-spoke team engine loaded by 4 other skills |
| `claude/sdd-tools/skills/create-spec/SKILL.md` | 664 | Largest skill — adaptive interview with depth-aware questioning |
| `claude/sdd-tools/skills/create-tasks/SKILL.md` | 653 | Spec-to-task decomposition with `task_uid` merge mode |
| `claude/sdd-tools/skills/execute-tasks/SKILL.md` | 262 | Wave-based parallel execution with session management |
| `claude/dev-tools/skills/feature-dev/SKILL.md` | 271 | 7-phase lifecycle spawning architect + reviewer agent teams |

## Settings

User preferences are stored in `.claude/agent-alchemy.local.md` (not committed):
- `deep-analysis.direct-invocation-approval`: Whether to require plan approval when user invokes directly (default: true)
- `deep-analysis.invocation-by-skill-approval`: Whether to require approval when loaded by another skill (default: false)
