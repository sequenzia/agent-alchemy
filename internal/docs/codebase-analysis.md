# Codebase Analysis Report

**Analysis Context**: General codebase understanding of the Agent Alchemy monorepo
**Codebase Path**: `/Users/sequenzia/dev/repos/agent-alchemy`
**Date**: 2026-02-15

---

## Executive Summary

Agent Alchemy is a **"markdown-as-code" development platform** that extends Claude Code with structured workflows through 4 plugin groups (15 skills, 9 agents), a real-time task dashboard, and a VS Code extension. The key architectural insight is that all AI agent behaviors are defined as composable Markdown documents — simultaneously human-readable documentation, LLM-consumable prompts, and version-controllable code. The primary risk is zero test coverage across all TypeScript components, and the primary recommendation is to populate the near-empty project `CLAUDE.md` with the architectural knowledge discovered here.

---

## Architecture Overview

Agent Alchemy is a **pnpm monorepo** with three major components and two supporting areas:

**The Plugin System** (`claude/`) is the project's core — 4 plugin groups (`core-tools`, `dev-tools`, `sdd-tools`, `git-tools`) that define AI workflows entirely in Markdown with YAML frontmatter. Skills orchestrate multi-step workflows (from interactive spec interviews to autonomous task execution), agents define specialized AI workers with model-tier selection (Opus for synthesis/review, Sonnet for exploration), and skills compose by loading other skills at runtime via `${CLAUDE_PLUGIN_ROOT}` references. A `marketplace.json` registry makes all 4 groups installable as independent plugins.

**The Task Manager** (`apps/task-manager/`) is a Next.js 16 real-time Kanban dashboard that bridges the plugin system to the user. It watches `~/.claude/tasks/` via Chokidar, pushes updates through SSE (Server-Sent Events), and uses TanStack Query for client-side cache invalidation — creating a live view of autonomous task execution as it happens.

**The VS Code Extension** (`extensions/vscode/`) provides schema-driven developer tooling for plugin authoring: YAML frontmatter validation, autocompletion, and hover documentation, all powered by 7 JSON Schemas that define the plugin system's contracts.

Supporting areas include a **documentation site** (`site/` — MkDocs-generated static site). JSON Schemas defining the plugin system's contracts live in `extensions/vscode/schemas/`.

The design philosophy is **composability through markdown**: complex workflows are built by orchestrating teams of agents with different specializations, not by writing imperative code.

---

## Critical Files

| File | Purpose | Relevance |
|------|---------|-----------|
| `claude/.claude-plugin/marketplace.json` | Plugin registry for all 4 groups | High |
| `claude/core-tools/skills/deep-analysis/SKILL.md` | Hub-and-spoke team analysis (350 lines) | High |
| `claude/sdd-tools/skills/create-spec/SKILL.md` | Adaptive spec interview (665 lines) | High |
| `claude/sdd-tools/skills/execute-tasks/SKILL.md` | Wave-based task execution orchestrator | High |
| `claude/dev-tools/skills/feature-dev/SKILL.md` | 7-phase feature development (272 lines) | High |
| `claude/sdd-tools/skills/create-tasks/SKILL.md` | Spec-to-tasks decomposition (654 lines) | High |
| `claude/core-tools/agents/code-explorer.md` | Sonnet exploration worker agent | High |
| `claude/core-tools/agents/code-synthesizer.md` | Opus synthesis agent with Bash access | High |
| `apps/task-manager/src/lib/taskService.ts` | Server-side task file reader (313 lines) | High |
| `apps/task-manager/src/lib/fileWatcher.ts` | Chokidar singleton watcher (187 lines) | High |
| `apps/task-manager/src/app/api/events/route.ts` | SSE endpoint via ReadableStream | High |
| `extensions/vscode/src/frontmatter/validator.ts` | Ajv-based frontmatter validator | High |
| `extensions/vscode/schemas/skill-frontmatter.schema.json` | Skill YAML frontmatter contract | High |
| `extensions/vscode/schemas/plugin.schema.json` | Plugin manifest contract | High |

### File Details

#### `claude/core-tools/skills/deep-analysis/SKILL.md`
- **Key exports**: Reusable analysis building block loaded by feature-dev, codebase-analysis, docs-manager, create-spec
- **Core logic**: 6-phase workflow — Settings Check -> Reconnaissance -> Planning -> Team Assembly -> Exploration -> Synthesis. Dynamically generates focus areas based on actual codebase structure
- **Connections**: Spawns `code-explorer` (sonnet) and `code-synthesizer` (opus) agents. Configurable approval via `.claude/agent-alchemy.local.md`

#### `claude/sdd-tools/skills/create-spec/SKILL.md`
- **Key exports**: The SDD pipeline entry point — turns ideas into structured specifications
- **Core logic**: Depth-adaptive interview (high-level: 2-3 rounds, detailed: 3-4, full-tech: 4-5) with proactive recommendation detection, optional codebase exploration, and template-based compilation
- **Connections**: Loads `deep-analysis` for "new feature" specs. Spawns `researcher` agent for technical research. Outputs spec files read by `create-tasks`

#### `apps/task-manager/src/lib/fileWatcher.ts`
- **Key exports**: `getFileWatcher()` singleton, `watchExecutionDir()` dynamic watcher
- **Core logic**: Chokidar watcher using polling mode (300ms) on `~/.claude/tasks/`. Emits typed events (`task:created`, `task:updated`, `task:deleted`, `execution:updated`). Uses `globalThis` to survive Next.js HMR
- **Connections**: Consumed by SSE route handler -> pushes to `useSSE` hook -> invalidates TanStack Query

---

## Patterns & Conventions

### Code Patterns

- **Markdown-as-Code**: All AI behaviors defined in `.md` files with YAML frontmatter — simultaneously docs, prompts, and code
- **Skill Composition**: Skills load other skills at runtime via `Read ${CLAUDE_PLUGIN_ROOT}/skills/{name}/SKILL.md`
- **Model Tiering**: Opus for synthesis/architecture/review, Sonnet for exploration/workers, Haiku for simple tasks
- **Hub-and-Spoke Coordination**: Central lead spawns workers + synthesizer; workers don't peer-communicate
- **References Pattern**: Complex skills use `references/` subdirectories for domain knowledge (question banks, templates, criteria)
- **AskUserQuestion Mandate**: Interactive skills enforce structured input via `AskUserQuestion` tool — never plain text questions
- **Configurable Approval Gates**: `.claude/agent-alchemy.local.md` controls approval behavior per invocation context

### Naming Conventions

- **Skills**: `SKILL.md` in `skills/{skill-name}/` directories
- **Agents**: `{agent-name}.md` in `agents/` directories
- **Plugin groups**: `{group-name}/` under `claude/` with `README.md`
- **Git commits**: Conventional Commits format (`type(scope): description`)

### Project Structure

- **Monorepo**: pnpm workspace with `apps/*` as packages
- **Plugin system**: `claude/` top-level with 4 independently installable groups
- **Schemas**: `extensions/vscode/schemas/` contains 7 JSON schemas bundled with the VS Code extension

---

## Relationship Map

**SDD Pipeline (end-to-end):**

`create-spec` -> spec file -> `analyze-spec` -> quality report -> `create-tasks` -> task JSON -> `execute-tasks` -> implementation

**Plugin Composition:**

- `feature-dev` -> loads -> `deep-analysis` -> spawns -> `code-explorer` x N + `code-synthesizer` x 1
- `feature-dev` -> spawns -> `code-architect` x 2-3 (parallel design) -> `code-reviewer` x 3 (parallel review)
- `feature-dev` -> loads -> `architecture-patterns`, `language-patterns`, `code-quality`, `changelog-format`

**Real-time Integration:**

- `execute-tasks` writes task JSON to `~/.claude/tasks/` -> `fileWatcher` detects -> SSE -> `useSSE` invalidates -> TanStack Query refetches -> KanbanBoard re-renders
- `execute-tasks` writes `execution_pointer.md` -> task manager reads pointer -> watches execution dir -> ExecutionDialog + ExecutionProgressBar update

**Schema Chain:**

- `extensions/vscode/schemas/` -> consumed by `validator.ts` via Ajv -> real-time diagnostics in VS Code

---

## Challenges & Risks

| Challenge | Severity | Impact |
|-----------|----------|--------|
| No automated tests | High | Zero test files across the entire monorepo. Task manager parsing logic, VS Code extension validation, and schema contracts are untested. Regressions can go unnoticed. |
| Plugin system depends on Claude Code internals | Medium | Skills reference `$ARGUMENTS`, `$CLAUDE_PLUGIN_ROOT`, Claude Code Task/Team tools — recently-introduced features with potentially unstable API surfaces. |
| Deep skill loading chains | Medium | `feature-dev` -> `deep-analysis` -> agents -> agents load skills. Multiple levels of indirection consume context window and make debugging difficult. |
| execute-tasks state machine complexity | Medium | Wave-based parallelism, session recovery, context isolation described entirely in markdown with no programmatic enforcement. |
| Near-empty project CLAUDE.md | Low | No conventions, setup instructions, or architecture docs for AI tools and contributors. |
| Chokidar polling mode | Low | `usePolling: true` with 300ms interval is reliable but resource-intensive compared to native OS watchers. |

---

## Recommendations

1. **Populate project CLAUDE.md**: Add project structure, development commands, architectural conventions, and skill composition chain.
2. **Add tests for TypeScript components**: Priority: `taskService.ts`, `fileWatcher.ts`, `validator.ts`, SSE endpoint.
3. **Document skill composition chain**: Visual map of which skills load which skills and which agents they spawn.
4. **Unify monorepo tooling**: Add `extensions/*` to pnpm workspace for consistency.

---

## Analysis Methodology

- **Exploration agents**: 3 agents with focus areas: Claude plugin system, Task Manager app, VS Code extension & schemas
- **Synthesis**: Findings merged by Opus-powered synthesizer with git history and dependency analysis
- **Scope**: All source files excluding `node_modules/`, `.venv/`, `.next/`, `site/` (generated docs)
