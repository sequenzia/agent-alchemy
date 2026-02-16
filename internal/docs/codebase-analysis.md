# Codebase Analysis Report

**Analysis Context**: General codebase understanding of the Agent Alchemy monorepo
**Codebase Path**: `/Users/sequenzia/dev/repos/agent-alchemy`
**Date**: 2026-02-15

---

## Executive Summary

Agent Alchemy's defining contribution is its **markdown-as-code plugin system** — a novel approach that treats markdown files as executable agent programs, encoding instructions, workflows, and multi-agent composition in YAML frontmatter + markdown body. The architecture implements a sophisticated hub-and-spoke agent coordination model across 5 plugin groups (20 skills, 12 agents, 33 reference files), supported by a real-time task dashboard and schema-driven VS Code extension. The primary risk is an **inconsistency in cross-plugin reference resolution** (`${CLAUDE_PLUGIN_ROOT}`) that could break skill composition across plugin boundaries, combined with zero test coverage on the VS Code extension that validates plugin authoring.

---

## Architecture Overview

Agent Alchemy is a **single-author pnpm monorepo** (144 commits) built on three interconnected pillars:

**1. Markdown-as-Code Plugin System** (`claude/`) — The core IP. Five plugin groups (core-tools, dev-tools, sdd-tools, tdd-tools, git-tools) contain 20 skills, 12 agents, 33 reference files, and 2 hook configurations. Skills compose at runtime through *prompt injection* — one skill instructs an agent to read another skill's `SKILL.md`, injecting its content into the context. A centralized `marketplace.json` registry defines all plugins with versions and source paths.

**2. Real-Time Task Dashboard** (`apps/task-manager/`) — A Next.js 16 App Router application providing Kanban visualization of Claude Code's native task files. The data pipeline flows: `~/.claude/tasks/*.json` → Chokidar file watcher → SSE endpoint → TanStack Query cache invalidation → React components. An HMR-safe singleton pattern using `globalThis` keeps the watcher alive across hot reloads.

**3. VS Code Extension** (`extensions/vscode/`) — A schema-driven authoring toolchain. Seven JSON schemas define contracts for plugin YAML frontmatter, compiled by Ajv at module load for real-time validation, autocomplete, and hover documentation. Auto-activates on workspaces containing `.claude-plugin/plugin.json`.

The three pillars connect through Claude Code's native task system: plugins create tasks → the dashboard visualizes them in real-time → the extension validates plugin authoring. The design philosophy is **composability through markdown**: complex workflows are built by orchestrating teams of agents with different specializations, not by writing imperative code.

---

## Critical Files

| File | Purpose | Relevance |
|------|---------|-----------|
| `claude/core-tools/skills/deep-analysis/SKILL.md` | 6-phase hub-and-spoke team engine (521 lines) | **Keystone** — loaded by 4 skills across 3 plugins |
| `claude/sdd-tools/skills/create-spec/SKILL.md` | Adaptive interview for spec creation (664 lines) | **High** — largest skill, complex multi-phase |
| `claude/sdd-tools/skills/create-tasks/SKILL.md` | Spec-to-task decomposition (653 lines) | **High** — produces task JSON |
| `claude/tdd-tools/skills/tdd-cycle/SKILL.md` | 7-phase RED-GREEN-REFACTOR workflow (718 lines) | **High** — autonomous TDD |
| `claude/dev-tools/skills/feature-dev/SKILL.md` | 7-phase feature dev lifecycle (271 lines) | **High** — multi-agent orchestration |
| `claude/.claude-plugin/marketplace.json` | Centralized plugin registry (57 lines) | **High** — defines all 5 plugins |
| `apps/task-manager/src/lib/fileWatcher.ts` | HMR-safe Chokidar singleton | **High** — drives all real-time updates |
| `apps/task-manager/src/app/api/events/route.ts` | SSE streaming endpoint | **High** — bridges server → browser |
| `apps/task-manager/src/hooks/useSSE.ts` | Client SSE hook with reconnection | **High** — invalidates TanStack Query cache |
| `extensions/vscode/src/frontmatter/validator.ts` | Ajv-based YAML frontmatter validation | **High** — validates plugin authoring |
| `extensions/vscode/src/extension.ts` | Extension entry point | **Medium** — registers diagnostics, completions, hover |

### File Details

#### `claude/core-tools/skills/deep-analysis/SKILL.md`
- **Key exports**: A reusable 6-phase workflow that other skills load via prompt injection
- **Core logic**: Session Setup → Reconnaissance & Planning → Review & Approval → Team Assembly → Focused Exploration → Evaluation & Synthesis → Completion. Features configurable settings (approval mode, cache TTL, checkpointing), session persistence with recovery, and dynamic focus area generation.
- **Connections**: Loaded by `codebase-analysis`, `feature-dev`, `docs-manager`, `create-spec`. Spawns `code-explorer` (Sonnet) and `code-synthesizer` (Opus) agents.

#### `apps/task-manager/src/lib/fileWatcher.ts`
- **Key exports**: `FileWatcher` class, `getFileWatcher()` accessor
- **Core logic**: Uses `globalThis` casting (`globalThis as unknown as { fileWatcher: FileWatcher }`) to survive Next.js HMR. Watches `~/.claude/tasks/` with 300ms polling. Emits `taskEvent` and `executionEvent` events. Supports dynamic execution directory watching via `watchExecutionDir()`.
- **Connections**: Consumed by SSE route (`events/route.ts`), which streams events to the browser via `ReadableStream`.

#### `extensions/vscode/src/frontmatter/validator.ts`
- **Key exports**: `validateDocument()` function
- **Core logic**: Pre-compiles Ajv validators for skill and agent schemas at module load. Detects file kind via path inspection (`skills/` or `agents/` directory). Provides precise line-number mapping for validation errors using regex-based YAML line scanning.
- **Connections**: Called by the extension's `DiagnosticCollection` on open/change/save events. Consumes JSON schemas from `schemas/` directory.

---

## Patterns & Conventions

### Code Patterns

- **Skill Composition via Prompt Injection**: Skills compose by instructing `Read ${CLAUDE_PLUGIN_ROOT}/skills/{name}/SKILL.md`. This is runtime prompt injection — one skill's markdown becomes part of another agent's context. Found in 11 files across all plugin groups.
- **Hub-and-Spoke Team Coordination**: `deep-analysis` creates teams with N explorers (Sonnet, read-only) + 1 synthesizer (Opus, read + Bash). Workers explore independently in parallel; only the synthesizer communicates with workers for follow-ups.
- **Phase Workflows with Completeness Enforcement**: Complex skills use numbered phases with `CRITICAL: Complete ALL N phases` directives. This prevents LLMs from stopping prematurely. Feature-dev (7 phases), create-spec (6 phases), tdd-cycle (7 phases).
- **Progressive Knowledge Loading**: 33 reference files (up to 776 lines each) are loaded on-demand within specific phases rather than upfront, managing context window usage.
- **Agent Tool Restrictions**: Read-only agents (`code-explorer`, `code-architect`, `code-reviewer`) vs full-capability agents (`task-executor`, `tdd-executor`, `test-writer`). Enforces separation of concerns.
- **Hook-Based Auto-Approval**: `PreToolUse` hooks with bash scripts auto-approve file operations targeting session directories, enabling autonomous execution.
- **GlobalThis Singleton**: Task manager persists `FileWatcher` across HMR via `globalThis` — only stored in dev mode.
- **AskUserQuestion Enforcement**: All interactive skills route user interaction through `AskUserQuestion`, never plain text output. Provides structured UI with options.
- **Configurable Approval Gates**: `.claude/agent-alchemy.local.md` controls approval behavior per invocation context.

### Naming Conventions

- **Plugins**: `agent-alchemy-{group}-tools` (e.g., `agent-alchemy-core-tools`)
- **Skills**: `SKILL.md` in `skills/{skill-name}/` directories; verb-noun or concept names (`deep-analysis`, `create-spec`, `tdd-cycle`)
- **Agents**: `{agent-name}.md` in `agents/` directories; role-based names (`code-explorer`, `code-architect`, `task-executor`)
- **Commits**: Conventional Commits format (`type(scope): description`). Distribution: feat (30), chore (24), refactor (12), docs (12), fix (7)

### Project Structure

- **Monorepo**: pnpm workspace with `apps/`, `claude/`, `extensions/` top-level directories
- **Plugin groups**: Each in `claude/{group}-tools/` with `skills/`, `agents/`, `hooks/` subdirectories
- **Schemas**: `extensions/vscode/schemas/` contains 7 JSON schemas bundled with the VS Code extension
- **References**: Complex skills use `references/` subdirectories for domain knowledge (question banks, templates, rubrics)

---

## Relationship Map

```
Plugin System (claude/)
─────────────────────────────────────────────
marketplace.json ──registers──→ 5 plugin groups
    ├── core-tools/
    │   ├── deep-analysis ◄──loaded-by── codebase-analysis, feature-dev,
    │   │                                docs-manager, create-spec
    │   ├── language-patterns ◄──loaded-by── tdd-cycle, generate-tests, feature-dev
    │   ├── project-conventions ◄──loaded-by── tdd-cycle, generate-tests
    │   ├── code-explorer (Sonnet) ←spawned-by── deep-analysis
    │   └── code-synthesizer (Opus) ←spawned-by── deep-analysis
    │
    ├── dev-tools/
    │   ├── feature-dev ──spawns──→ code-architect (Opus) x2-3, code-reviewer (Opus) x3
    │   ├── docs-manager ──spawns──→ docs-writer (Opus)
    │   └── release-python-package ──spawns──→ changelog-manager
    │
    ├── sdd-tools/
    │   ├── create-spec ──spawns──→ researcher (Sonnet)
    │   ├── analyze-spec ──spawns──→ spec-analyzer
    │   ├── execute-tasks ──spawns──→ task-executor x N (wave-based)
    │   ├── create-tdd-tasks ──depends-on──→ tdd-tools plugin
    │   └── execute-tdd-tasks ──spawns──→ tdd-executor + task-executor
    │
    ├── tdd-tools/
    │   ├── tdd-cycle (7-phase autonomous RED-GREEN-REFACTOR)
    │   ├── generate-tests ──spawns──→ test-writer (Sonnet) x N
    │   └── analyze-coverage
    │
    └── git-tools/
        └── git-commit (Haiku, standalone)

Task Manager (apps/task-manager/)
─────────────────────────────────────────────
~/.claude/tasks/*.json ──watched-by──→ FileWatcher (Chokidar, 300ms polling)
    → emits taskEvent / executionEvent
    → SSE route (/api/events) streams via ReadableStream
    → useSSE hook invalidates TanStack Query cache
    → KanbanBoard renders 3 columns (pending / in_progress / completed)

VS Code Extension (extensions/vscode/)
─────────────────────────────────────────────
7 JSON schemas ──compiled-by──→ Ajv validators
    → validateDocument() on open/change/save
    → FrontmatterCompletionProvider → autocomplete
    → FrontmatterHoverProvider → hover docs
```

### SDD Pipeline (end-to-end)

```
create-spec → spec file → analyze-spec → quality report → create-tasks → task JSON
    → execute-tasks → implementation (wave-based parallel execution)
    → create-tdd-tasks → TDD pairs → execute-tdd-tasks → RED-GREEN-REFACTOR
```

### Key Skill Composition Chains

```
feature-dev → deep-analysis → code-explorer (Sonnet) x N + code-synthesizer (Opus) x 1
feature-dev → code-architect (Opus) x 2-3 → code-reviewer (Opus) x 3

create-spec → deep-analysis (optional, for "new feature" type)
create-spec → researcher agent (for technical research)

tdd-cycle → tdd-executor (Opus) x 1 per feature (6-phase RED-GREEN-REFACTOR)
generate-tests → test-writer (Sonnet) x N parallel (criteria-driven or code-analysis)
```

---

## Challenges & Risks

| Challenge | Severity | Impact |
|-----------|----------|--------|
| **Cross-plugin `${CLAUDE_PLUGIN_ROOT}` inconsistency** | **High** | Two competing patterns: direct path (Pattern A, used by dev-tools/sdd-tools) and explicit relative `/../core-tools/` (Pattern B, used by tdd-tools). If resolution is per-plugin, Pattern A breaks for cross-plugin references. |
| **Zero test coverage for VS Code extension** | **High** | Validation bugs could silently accept malformed plugins or reject valid ones. The validator is the authoring toolchain's most critical component. |
| **Schema drift risk** | **Medium** | JSON schemas are manually maintained. Changes to plugin conventions require manual updates with no CI verification. |
| **Large reference files approaching context limits** | **Medium** | Largest reference (776 lines) + skill (718 lines) can exceed 1,500 lines before adding codebase context. |
| **File watcher polling overhead** | **Medium** | 300ms polling on macOS where native fsevents is available. Cross-platform reliability was likely the design rationale. |
| **No task list pagination** | **Low** | All tasks loaded at once. Virtual scrolling needed for >100 tasks. |
| **Markdown rendering XSS surface** | **Low** | Task artifacts rendered via react-markdown. Risk minimal since data comes from local task files. |

---

## Recommendations

1. **Standardize cross-plugin references**: Establish a single convention for `${CLAUDE_PLUGIN_ROOT}` cross-plugin resolution. Either document the implicit mechanism or migrate all cross-plugin references to the explicit `/../{plugin}/` pattern used by tdd-tools.
2. **Add VS Code extension tests**: At minimum, unit tests for the validator — Ajv compilation, path-based file detection, and line-number mapping are testable without VS Code test infrastructure.
3. **Add schema synchronization CI**: A CI step scanning all SKILL.md and agent .md frontmatter against JSON schemas would prevent drift.
4. **Document the plugin architecture**: The markdown-as-code system is novel and the core IP. A formal architecture document would help onboarding and reduce knowledge concentration risk.
5. **Consider platform-aware file watching**: Use fsevents on macOS/Linux for lower overhead, falling back to polling on other platforms.

---

## Analysis Methodology

- **Exploration agents**: 3 Sonnet agents with focus areas: plugin architecture (High complexity), task manager application (Medium), VS Code extension & infrastructure (Medium)
- **Synthesis**: 1 Opus agent merged findings with git history analysis (144 commits) and cross-referenced architectural patterns
- **Scope**: All source code in `claude/`, `apps/task-manager/src/`, `extensions/vscode/src/`, `scripts/`, `internal/`, `specs/`. Excluded: `node_modules/`, `.next/` build artifacts

---

## Plugin Inventory

| Group | Skills | Agents | Version |
|-------|--------|--------|---------|
| core-tools | deep-analysis, codebase-analysis, language-patterns, project-conventions | code-explorer, code-synthesizer | 0.1.1 |
| dev-tools | feature-dev, architecture-patterns, code-quality, changelog-format, docs-manager, release-python-package | code-architect, code-reviewer, changelog-manager, docs-writer | 0.1.1 |
| sdd-tools | create-spec, analyze-spec, create-tasks, execute-tasks, create-tdd-tasks, execute-tdd-tasks | researcher, spec-analyzer, task-executor | 0.1.2 |
| tdd-tools | generate-tests, tdd-cycle, analyze-coverage | test-writer, tdd-executor, test-reviewer | 0.1.0 |
| git-tools | git-commit | — | 0.1.0 |

**Totals**: 20 skills, 12 agents, 33 reference files, 2 hook configurations, 7 JSON schemas
