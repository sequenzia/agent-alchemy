## Synthesized Analysis: Agent Alchemy Codebase

### Architecture Overview

Agent Alchemy is a monorepo that transforms Claude Code from an ad-hoc AI assistant into a **structured development platform** through three interconnected systems: a markdown-as-code plugin framework (`claude/`), a real-time task visualization dashboard (`apps/task-manager/`), and an IDE authoring extension (`extensions/vscode/`). The project has 189 commits from a single author and is actively evolving — 6 plugin groups, 28 skills, 16 agents, and growing.

The architectural philosophy is **"prompts as software"** — skills, agents, and hooks are defined entirely in markdown and JSON, composed at runtime through prompt injection (`Read ${CLAUDE_PLUGIN_ROOT}/...`), and validated by JSON schemas. There is no traditional code compilation for the plugin system; the "build artifact" is the markdown file itself, and Claude Code's runtime is the execution engine.

The three systems form a loose triangle: plugins define workflows that create task files in `~/.claude/tasks/`, the task manager watches those files in real-time, and the VS Code extension validates plugin authoring. The connection between plugins and the task manager is through the filesystem (JSON task files), not through any API — making the task manager a pure read-only observer of Claude Code's native task system.

### Critical Files

| File | Purpose | Relevance |
|------|---------|-----------|
| claude/core-tools/skills/deep-analysis/SKILL.md | Keystone skill — 6-phase hub-and-spoke team engine (521 lines) | Critical |
| claude/dev-tools/skills/feature-dev/SKILL.md | 7-phase feature development lifecycle (273 lines) | Critical |
| claude/plugin-tools/skills/port-plugin/SKILL.md | Cross-platform plugin porting (2,572 lines — largest) | High |
| claude/sdd-tools/skills/create-spec/SKILL.md | Adaptive interview spec generation (659 lines) | High |
| claude/sdd-tools/skills/create-tasks/SKILL.md | Spec-to-task decomposition (653 lines) | High |
| claude/tdd-tools/skills/tdd-cycle/SKILL.md | 7-phase RED-GREEN-REFACTOR TDD (727 lines) | High |
| claude/dev-tools/skills/bug-killer/SKILL.md | Hypothesis-driven debugging (470 lines) | High |
| apps/task-manager/src/lib/fileWatcher.ts | Chokidar filesystem watcher singleton (187 lines) | Critical |
| apps/task-manager/src/app/api/events/route.ts | SSE endpoint for real-time updates (91 lines) | High |
| apps/task-manager/src/lib/taskService.ts | Server-side task file reader (313 lines) | High |
| extensions/vscode/src/frontmatter/validator.ts | Ajv-based YAML validation (157 lines) | High |
| claude/.claude-plugin/marketplace.json | Centralized plugin registry | High |

### Patterns & Conventions

- Markdown-as-Code: Skills, agents, hooks as version-controlled documents
- Hub-and-Spoke Agent Teams: Lead → N Sonnet workers + 1 Opus synthesizer
- Phase Workflow with Completeness Enforcement
- Progressive Reference Loading (45 files, ~15,500 lines)
- Model Tiering: Opus (reasoning), Sonnet (parallel), Haiku (simple)
- Auto-Approval Hooks for session writes
- Schema-Driven Authoring in VS Code

### Challenges & Risks

| Challenge | Severity |
|-----------|----------|
| Zero test coverage for VS Code extension | High |
| Schema drift risk | Medium |
| Context pressure from large skills | Medium |
| Polling overhead in FileWatcher | Low |
| No task pagination | Low |

### Recommendations

1. Prioritize VS Code extension testing
2. Add schema-plugin drift detection to CI
3. Consider fsevents for macOS
4. Document the plugin runtime model
5. Monitor context consumption
