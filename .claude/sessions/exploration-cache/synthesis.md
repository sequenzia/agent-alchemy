## Synthesized Analysis: Agent Alchemy Codebase

### Architecture Overview

Agent Alchemy is a monorepo that transforms Claude Code from an ad-hoc AI assistant into a **structured development platform** through three interconnected systems: a markdown-as-code plugin framework (`claude/`), a real-time task visualization dashboard (`apps/task-manager/`), and an IDE authoring extension (`extensions/vscode/`). The project has 189 commits from a single author and is actively evolving — 6 plugin groups, 28 skills, 16 agents, and growing.

The architectural philosophy is **"prompts as software"** — skills, agents, and hooks are defined entirely in markdown and JSON, composed at runtime through prompt injection (`Read ${CLAUDE_PLUGIN_ROOT}/...`), and validated by JSON schemas. There is no traditional code compilation for the plugin system; the "build artifact" is the markdown file itself, and Claude Code's runtime is the execution engine.

The three systems form a loose triangle: plugins define workflows that create task files in `~/.claude/tasks/`, the task manager watches those files in real-time, and the VS Code extension validates plugin authoring. The connection between plugins and the task manager is through the filesystem (JSON task files), not through any API — making the task manager a pure read-only observer of Claude Code's native task system.

### Critical Files

| File | Purpose | Relevance | Connections |
|------|---------|-----------|-------------|
| `claude/core-tools/skills/deep-analysis/SKILL.md` | Keystone skill — 6-phase hub-and-spoke team engine (521 lines) | **Critical** | Loaded by codebase-analysis, feature-dev, docs-manager; spawns code-explorer + code-synthesizer agents |
| `claude/dev-tools/skills/feature-dev/SKILL.md` | 7-phase feature development lifecycle (273 lines) | **Critical** | Loads deep-analysis (Phase 2), language-patterns, architecture-patterns; spawns code-architect + code-reviewer agents |
| `claude/plugin-tools/skills/port-plugin/SKILL.md` | Cross-platform plugin porting (2,572 lines — largest) | **High** | 7-phase workflow with wave-based converter team; spawns researcher + port-converter agents |
| `claude/sdd-tools/skills/create-spec/SKILL.md` | Adaptive interview spec generation (659 lines) | **High** | Independent since refactoring removed core-tools dependency; spawns codebase-explorer agents |
| `claude/sdd-tools/skills/create-tasks/SKILL.md` | Spec-to-task decomposition (653 lines) | **High** | Reads specs, generates JSON task files consumed by task-manager |
| `claude/tdd-tools/skills/tdd-cycle/SKILL.md` | 7-phase RED-GREEN-REFACTOR TDD (727 lines) | **High** | Loads language-patterns + project-conventions from core-tools; spawns tdd-executor agent |
| `claude/dev-tools/skills/bug-killer/SKILL.md` | Hypothesis-driven debugging (470 lines) | **High** | Newest skill (added 2026-02-21); triage-routes to quick or deep track |
| `apps/task-manager/src/lib/fileWatcher.ts` | Chokidar filesystem watcher singleton (187 lines) | **Critical** | globalThis HMR pattern; feeds SSE route + EventEmitter |
| `apps/task-manager/src/app/api/events/route.ts` | SSE endpoint for real-time updates (91 lines) | **High** | Consumes FileWatcher events, streams to useSSE hook |
| `apps/task-manager/src/lib/taskService.ts` | Server-side task file reader (313 lines) | **High** | Reads/parses JSON tasks; path traversal protection; execution context resolution |
| `apps/task-manager/src/hooks/useSSE.ts` | Client-side SSE + TanStack Query invalidation (63 lines) | **High** | Bridges SSE events to React Query cache invalidation + router.refresh() |
| `extensions/vscode/src/frontmatter/validator.ts` | Ajv-based YAML validation (157 lines) | **High** | Validates SKILL.md and agent .md files against JSON schemas |
| `claude/.claude-plugin/marketplace.json` | Centralized plugin registry | **High** | Single source of truth for all 6 plugin versions |

### Key Patterns

1. **Markdown-as-Code**: Skills (SKILL.md + YAML frontmatter), Agents (.md + YAML), Hooks (hooks.json)
2. **Hub-and-Spoke Agent Teams**: Lead → N Sonnet workers + 1 Opus synthesizer
3. **Phase Workflow with Completeness Enforcement** ("CRITICAL: Complete ALL N phases")
4. **Progressive Reference Loading** (45 files, ~15,500 lines, loaded on-demand)
5. **Model Tiering**: Opus (reasoning), Sonnet (parallel), Haiku (simple)
6. **Auto-Approval Hooks** for session writes (core-tools, sdd-tools, tdd-tools)
7. **AskUserQuestion Enforcement** for all interactive decisions
8. **Schema-Driven Authoring** in VS Code
9. **Server/Client Component Boundary** (Next.js 16 App Router)
10. **globalThis Singleton** for FileWatcher HMR survival
11. **Agent Tool Restrictions** enforce separation of concerns (read-only vs full-capability)

### Challenges & Risks

| Challenge | Severity | Impact |
|-----------|----------|--------|
| Zero test coverage for VS Code extension | High | Validator regression would silently break validation for all plugin authors |
| Schema drift risk | Medium | New frontmatter fields not caught as unknown; manual maintenance |
| Context pressure from large skills | Medium | port-plugin + references = ~6,000 lines; mitigated by wave-based isolation |
| Polling overhead in FileWatcher | Low | 300ms CPU-bound polling vs native fsevents on macOS |
| No task pagination | Low | Large task lists (100+) could cause UI sluggishness |

### Recommendations

1. **Prioritize VS Code extension testing** _(addresses: Zero test coverage)_
2. **Add schema-plugin drift detection to CI** _(addresses: Schema drift risk)_
3. **Consider fsevents for macOS** _(addresses: Polling overhead)_
4. **Document the plugin runtime model** _(addresses: project onboarding)_
5. **Monitor context consumption** _(addresses: Context pressure)_

### Completeness Assessment

**Coverage confidence: High.** All three major subsystems explored in depth. 189 commits analyzed. Cross-plugin dependency graph verified via direct Grep. Critical files read directly by synthesizer. Recent additions (bug-killer, document-changes, sdd-tools standalone refactor) accounted for.
