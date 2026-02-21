# Codebase Analysis Report

**Analysis Context**: General codebase understanding
**Codebase Path**: `/Users/sequenzia/dev/repos/agent-alchemy`
**Date**: 2026-02-21

---

## Table of Contents

- [Executive Summary](#executive-summary)
- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Critical Files](#critical-files)
- [Patterns & Conventions](#patterns--conventions)
- [Relationship Map](#relationship-map)
- [Challenges & Risks](#challenges--risks)
- [Recommendations](#recommendations)
- [Analysis Methodology](#analysis-methodology)

---

## Executive Summary

Agent Alchemy is a **"prompts as software"** platform — a monorepo where markdown files *are* the code, Claude Code's runtime is the execution engine, and JSON schemas enforce correctness. The most critical architectural insight is that the three subsystems (plugin framework, task dashboard, VS Code extension) connect through the filesystem rather than APIs, making the system loosely coupled but potentially brittle to file format changes. The primary risk is zero test coverage on the VS Code extension's validator, which is the only safety net for plugin authors.

---

## Architecture Overview

Agent Alchemy transforms Claude Code from an ad-hoc AI assistant into a **structured development platform** through three interconnected systems:

1. **Plugin Framework** (`claude/`) — 6 plugin groups containing 28 skills, 16 agents, and lifecycle hooks, all defined in markdown and JSON. Skills compose at runtime through prompt injection (`Read ${CLAUDE_PLUGIN_ROOT}/...`), not function calls. The "build artifact" is the markdown file itself.

2. **Task Dashboard** (`apps/task-manager/`) — A Next.js 16 App Router application providing a real-time Kanban board. It watches `~/.claude/tasks/` via Chokidar, streams changes over SSE, and uses TanStack Query for client-side cache invalidation. It is a **pure read-only observer** — it never writes task files.

3. **IDE Extension** (`extensions/vscode/`) — An Ajv-based validation layer for plugin authoring. It validates YAML frontmatter in skill and agent files against JSON schemas, providing autocompletion and hover documentation. It auto-activates on workspaces containing `.claude-plugin/plugin.json`.

The three systems form a loose triangle connected through the filesystem: plugins create task JSON files → task manager watches and displays them → VS Code extension validates plugin authoring. There is no shared API layer.

---

## Tech Stack

| Category | Technology | Version | Role |
|----------|-----------|---------|------|
| Language | TypeScript | 5.x | Primary language (apps, extension) |
| Language | Markdown + YAML | — | Plugin definitions (skills, agents) |
| Framework | Next.js | 16.1.4 | Task dashboard web framework |
| Runtime | React | 19.2.3 | UI component library |
| State | TanStack Query | 5.x | Client-side cache + invalidation |
| Styling | Tailwind CSS | v4 | Utility-first CSS |
| UI Components | shadcn/ui (Radix) | — | Accessible primitives |
| File Watching | Chokidar | 5.0.0 | Filesystem observation |
| Validation | Ajv | — | JSON Schema validation (VS Code) |
| Build (Extension) | esbuild | — | VS Code extension bundler |
| Package Manager | pnpm | 8+ | Workspace management |
| Docs | MkDocs | — | Documentation site (Python/uv) |

---

## Critical Files

| File | Purpose | Relevance |
|------|---------|-----------|
| `claude/core-tools/skills/deep-analysis/SKILL.md` | Keystone skill — 6-phase hub-and-spoke team engine (521 lines) | **Critical** |
| `claude/dev-tools/skills/feature-dev/SKILL.md` | 7-phase feature development lifecycle (273 lines) | **Critical** |
| `apps/task-manager/src/lib/fileWatcher.ts` | Chokidar filesystem watcher singleton (187 lines) | **Critical** |
| `claude/plugin-tools/skills/port-plugin/SKILL.md` | Cross-platform plugin porting — largest file (2,572 lines) | **High** |
| `claude/sdd-tools/skills/create-spec/SKILL.md` | Adaptive interview spec generation (659 lines) | **High** |
| `claude/sdd-tools/skills/create-tasks/SKILL.md` | Spec-to-task decomposition with merge mode (653 lines) | **High** |
| `claude/tdd-tools/skills/tdd-cycle/SKILL.md` | 7-phase RED-GREEN-REFACTOR TDD workflow (727 lines) | **High** |
| `claude/dev-tools/skills/bug-killer/SKILL.md` | Hypothesis-driven debugging with triage routing (~470 lines) | **High** |
| `apps/task-manager/src/app/api/events/route.ts` | SSE endpoint for real-time updates (91 lines) | **High** |
| `apps/task-manager/src/lib/taskService.ts` | Server-side task file reader with path traversal protection (313 lines) | **High** |
| `extensions/vscode/src/frontmatter/validator.ts` | Ajv-based YAML validation (157 lines) | **High** |
| `claude/.claude-plugin/marketplace.json` | Centralized plugin registry — single source of truth for versions | **High** |

### File Details

#### `claude/core-tools/skills/deep-analysis/SKILL.md`
- **Key exports**: Hub-and-spoke agent team orchestration
- **Core logic**: 6-phase workflow — reconnaissance → team planning → approval → team assembly → parallel exploration (N Sonnet code-explorers) → synthesis (1 Opus code-synthesizer)
- **Connections**: Loaded by `codebase-analysis`, `feature-dev`, `docs-manager`; spawns `code-explorer` and `code-synthesizer` agents

#### `apps/task-manager/src/lib/fileWatcher.ts`
- **Key exports**: `FileWatcher` singleton class, `getWatcher()` factory
- **Core logic**: Chokidar watches `~/.claude/tasks/` with 300ms polling; emits events via `EventEmitter`; survives HMR via `globalThis` caching
- **Connections**: Feeds `api/events/route.ts` (SSE) → `useSSE.ts` (client) → TanStack Query invalidation

#### `extensions/vscode/src/frontmatter/validator.ts`
- **Key exports**: `FrontmatterValidator` class
- **Core logic**: Compiles Ajv validators from JSON schemas, extracts YAML frontmatter from markdown files, validates against skill/agent schemas, maps errors to line numbers
- **Connections**: Consumed by `DiagnosticProvider`; reads schemas from `extensions/vscode/schemas/`

---

## Patterns & Conventions

### Code Patterns

- **Markdown-as-Code**: Skills defined in `SKILL.md` with YAML frontmatter, agents in `{name}.md` — the markdown *is* the runtime code
- **Hub-and-Spoke Agent Teams**: A lead orchestrator spawns N Sonnet workers for parallel exploration + 1 Opus synthesizer for merging findings
- **Phase Workflows with Completeness Enforcement**: Complex skills use numbered phases with `"CRITICAL: Complete ALL N phases"` directives to prevent Claude from stopping early
- **Progressive Reference Loading**: ~45 reference files totaling ~15,500 lines, loaded on-demand rather than upfront to manage context pressure
- **Model Tiering**: Opus for reasoning/synthesis, Sonnet for parallel workers, Haiku for simple tasks (git commits)
- **Agent Tool Restrictions**: Architect and reviewer agents are read-only (Glob, Grep, Read only); executor agents have write access — enforces separation of concerns
- **AskUserQuestion Enforcement**: All interactive skills route user decisions through `AskUserQuestion`, never plain text prompts

### Naming Conventions

- **Plugin Groups**: kebab-case directory names (`core-tools`, `dev-tools`, `sdd-tools`)
- **Skills**: `SKILL.md` in a named directory (e.g., `skills/deep-analysis/SKILL.md`)
- **Agents**: `{role-name}.md` (e.g., `code-explorer.md`, `bug-investigator.md`)
- **Cross-plugin refs**: `${CLAUDE_PLUGIN_ROOT}/../{source-dir-name}/` — never full marketplace names
- **Git**: Conventional Commits (`type(scope): description`)

### Project Structure

- **Monorepo with pnpm workspaces**: `apps/`, `extensions/`, `claude/` at root level
- **Plugin groups are independent**: Each has its own `plugin.json`, can be installed separately
- **Reference materials externalized**: Large knowledge bases in `references/` subdirectories, not inline in skills
- **Marketplace registry**: `claude/.claude-plugin/marketplace.json` is the single source of truth for plugin versions

---

## Relationship Map

### Plugin Composition Chain (the core data flow)

```
deep-analysis (core-tools)
  ├── loaded by → codebase-analysis (core-tools)
  ├── loaded by → feature-dev (dev-tools)
  └── loaded by → docs-manager (dev-tools)
       ↓
  spawns → code-explorer (Sonnet) × N + code-synthesizer (Opus) × 1
```

### Feature Development Chain

```
feature-dev
  ├── Phase 2 → deep-analysis → explorer/synthesizer team
  ├── Phase 4 → code-architect (core-tools, Opus) × 2-3
  └── Phase 6 → code-reviewer (dev-tools, Opus) × 3
```

### SDD Pipeline

```
create-spec → codebase-explorer (optional)
    ↓
create-tasks → reads spec → generates task JSON
    ↓
execute-tasks → task-executor agent × N per wave → writes context
    ↓
~/.claude/tasks/*.json ← watched by → FileWatcher
```

### Task Manager Real-Time Flow

```
~/.claude/tasks/ (JSON files)
    ↓ chokidar watch
FileWatcher (globalThis singleton)
    ↓ EventEmitter
api/events/route.ts (SSE ReadableStream)
    ↓ SSE
useSSE.ts (client hook)
    ↓ invalidateQueries
TanStack Query → React re-render → KanbanBoard
```

### VS Code Validation Flow

```
SKILL.md / agent.md (user edits)
    ↓ onDidChangeTextDocument
DiagnosticProvider → FrontmatterValidator → Ajv
    ↓ validates against
schemas/*.json (7 JSON schemas)
    ↓ maps errors to
VS Code Diagnostics (red squiggles)
```

### Cross-Plugin Dependencies

- `deep-analysis` (core-tools) ← loaded by 3 skills across 2 plugins (keystone)
- `language-patterns` (core-tools) ← loaded by `tdd-cycle`, `feature-dev`
- `project-conventions` (core-tools) ← loaded by `tdd-cycle`
- `code-quality` (dev-tools) ← loaded by `bug-killer` for fix validation
- `project-learnings` (dev-tools) ← loaded by `bug-killer` for knowledge encoding

---

## Challenges & Risks

| Challenge | Severity | Impact |
|-----------|----------|--------|
| Zero test coverage for VS Code extension | **High** | Validator regression would silently break validation for all plugin authors. Ajv compilation, path detection, and line-number mapping are all untested. |
| Schema drift risk | **Medium** | JSON schemas manually maintained in `extensions/vscode/schemas/`. New frontmatter fields in skills/agents won't be caught as unknown. No CI validation ensures schemas match actual plugin usage. |
| Context pressure from large skills | **Medium** | `port-plugin` + references = ~6,000 lines. Mitigated by wave-based agent isolation, but still risks context window exhaustion on complex ports. |
| Polling overhead in FileWatcher | **Low** | Chokidar configured with 300ms CPU-bound polling. macOS supports native fsevents which would be more efficient. |
| No task pagination | **Low** | Large task lists (100+ tasks) could cause UI sluggishness in the Kanban board. |

---

## Recommendations

1. **Prioritize VS Code extension testing** _(addresses: Zero test coverage)_: The validator is the only safety net for plugin authors. Focus on Ajv schema compilation, frontmatter extraction edge cases, and line-number mapping accuracy.

2. **Add schema-plugin drift detection to CI** _(addresses: Schema drift risk)_: Parse actual YAML frontmatter from all `SKILL.md` and agent `.md` files and compare against JSON schema `properties` — fail CI on unknown fields.

3. **Switch to native fsevents on macOS** _(addresses: Polling overhead)_: Chokidar v5 supports `usePolling: false` which uses native OS events. This would eliminate the 300ms polling loop on macOS.

4. **Document the plugin runtime model** _(addresses: project onboarding)_: The "prompts as software" paradigm is unique. A brief architecture guide explaining how markdown becomes executable behavior would help new contributors.

5. **Monitor context consumption in large workflows** _(addresses: Context pressure)_: Add instrumentation to track token usage in port-plugin and deep-analysis workflows to identify when context pressure becomes critical.

---

## Analysis Methodology

- **Exploration agents**: 3 agents with focus areas: Plugin Architecture & Composition Patterns, Task Manager Application, VS Code Extension & Developer Infrastructure
- **Synthesis**: Findings merged by code-synthesizer agent; critical files read in depth
- **Scope**: Full monorepo — `claude/` (6 plugin groups), `apps/task-manager/`, `extensions/vscode/`, configuration and documentation
- **Cache status**: Cached results from 2026-02-21 22:55 UTC
- **Config files detected**: `package.json`, `apps/task-manager/package.json`, `pnpm-workspace.yaml`, `tsconfig.json`, `marketplace.json`, `plugin.json` (×6)
- **Gap-filling**: Verified tech stack versions from `package.json` files; confirmed no new commits since cache creation
