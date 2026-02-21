# CLAUDE.md

## Project Overview

Agent Alchemy is a monorepo that extends Claude Code into a structured development platform through markdown-as-code plugins, a real-time task dashboard, and a VS Code extension.

## Repository Structure

```
agent-alchemy/
├── claude/                    # Claude Code plugins (markdown-as-code)
│   ├── .claude-plugin/        # Plugin marketplace registry
│   ├── core-tools/            # Codebase analysis, deep exploration, language patterns (includes hooks/)
│   ├── dev-tools/             # Feature dev, debugging, code review, docs, changelog
│   ├── sdd-tools/             # Spec-Driven Development pipeline
│   ├── tdd-tools/             # TDD workflows: test generation, RED-GREEN-REFACTOR, coverage
│   ├── git-tools/             # Git commit automation
│   └── plugin-tools/          # Plugin porting, adapter validation, ported plugin maintenance, ecosystem health
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
- **Agent Tool Restrictions**: Architect (core-tools) and reviewer (dev-tools) agents are read-only (Glob, Grep, Read only); executor agents can write — enforces separation of concerns
- **AskUserQuestion Enforcement**: All interactive skills route user interaction through `AskUserQuestion`, never plain text output

### Cross-Plugin Dependencies

`deep-analysis` (core-tools) is the keystone skill, loaded by 3 skills across 2 plugin groups:
- `codebase-analysis` (core-tools) — wraps deep-analysis with reporting + post-analysis actions
- `feature-dev` (dev-tools) — loads in Phase 2 for codebase exploration
- `docs-manager` (dev-tools) — loads for codebase understanding before doc generation

**Cross-plugin reference convention:** Always use `${CLAUDE_PLUGIN_ROOT}/../{source-dir-name}/` for cross-plugin references, where `{source-dir-name}` is the directory name under `claude/` (e.g., `core-tools`, `tdd-tools`). Same-plugin references use `${CLAUDE_PLUGIN_ROOT}/` directly. Never use full marketplace names (e.g., `agent-alchemy-core-tools`) in path references — use the short source directory name.

### Model Tiering

- **Opus**: Synthesis, architecture, review (high-reasoning tasks)
- **Sonnet**: Exploration, worker tasks (parallelizable broad search)
- **Haiku**: Simple/quick tasks (git commit)

### Key Skill Composition Chains

```
feature-dev -> deep-analysis -> code-explorer (sonnet) x N + code-synthesizer (opus) x 1
feature-dev -> code-architect (core-tools, opus) x 2-3 -> code-reviewer (opus) x 3

create-spec -> codebase-explorer (sonnet) x 2-3 (optional, for "new feature" type)
create-spec -> researcher agent (for technical research)

create-tasks -> reads spec -> generates task JSON
execute-tasks -> task-executor agent x N per wave -> writes execution context

tdd-cycle -> tdd-executor (opus) x 1 per feature (6-phase RED-GREEN-REFACTOR)
generate-tests -> test-writer (sonnet) x N parallel (criteria-driven or code-analysis)
create-tdd-tasks (tdd-tools) -> reads existing tasks -> generates TDD pairs (test blocks impl)
execute-tdd-tasks (tdd-tools) -> tdd-executor for TDD tasks, task-executor (sdd-tools, soft dep) for non-TDD tasks

port-plugin -> researcher (sonnet) x 1 -> port-converter (sonnet) x N per wave -> orchestrator resolves incompatibilities between waves
validate-adapter -> researcher (sonnet) x 1 -> compare adapter sections against research
update-ported-plugin -> validate-adapter (phases 1-3) + git diff -> incremental re-conversion

dependency-checker -> reads all plugin groups -> builds dependency graph -> 7 analysis passes + doc drift checks

bug-killer (quick) -> reads error location, targeted investigation, fix + regression test -> project-learnings
bug-killer (deep) -> code-explorer (core-tools, sonnet) x 2-3 + bug-investigator (sonnet) x 1-3 -> code-quality (same plugin) for fix validation -> project-learnings
```

### Task Manager (apps/task-manager/)

- Next.js 16 App Router with Server Components + Client Components
- Real-time: Chokidar watches `~/.claude/tasks/` -> SSE -> TanStack Query invalidation
- Global FileWatcher singleton survives HMR via `globalThis`

### VS Code Extension (extensions/vscode/)

- Ajv-based YAML frontmatter validation for skills and agents
- JSON schema validation for plugin.json, hooks.json, .mcp.json, .lsp.json, marketplace.json
- 7 JSON schemas total in `extensions/vscode/schemas/` (skill-frontmatter, agent-frontmatter, plugin, hooks, mcp, lsp, marketplace)
- Schema-driven autocompletion and hover documentation
- Auto-activates on workspaces containing `.claude-plugin/plugin.json`

## Conventions

- **Git**: Conventional Commits (`type(scope): description`)
- **TypeScript**: Strict mode, functional patterns preferred
- **Styling**: Tailwind CSS v4 with shadcn/ui components (task manager)
- **Schemas**: JSON schemas live in `extensions/vscode/schemas/` (bundled with the VS Code extension)

## Plugin Inventory

| Group | Skills | Agents | Version |
|-------|--------|--------|---------|
| core-tools | deep-analysis, codebase-analysis, language-patterns, project-conventions | code-explorer, code-synthesizer, code-architect | 0.2.0 |
| dev-tools | feature-dev, bug-killer, architecture-patterns, code-quality, project-learnings, changelog-format, docs-manager, release-python-package, document-changes | code-reviewer, bug-investigator, changelog-manager, docs-writer | 0.3.0 |
| sdd-tools | create-spec, analyze-spec, create-tasks, execute-tasks | codebase-explorer, researcher, spec-analyzer, task-executor | 0.2.0 |
| tdd-tools | generate-tests, tdd-cycle, analyze-coverage, create-tdd-tasks, execute-tdd-tasks | test-writer, tdd-executor, test-reviewer | 0.2.0 |
| git-tools | git-commit | — | 0.1.0 |
| plugin-tools | port-plugin, validate-adapter, update-ported-plugin, dependency-checker, bump-plugin-version | researcher, port-converter | 0.1.1 |

## Critical Plugin Files

| File | Lines | Role |
|------|-------|------|
| `claude/core-tools/skills/deep-analysis/SKILL.md` | 521 | Keystone skill — hub-and-spoke team engine loaded by 4 other skills |
| `claude/plugin-tools/skills/port-plugin/SKILL.md` | ~2575 | Largest skill — cross-platform plugin porting with 7-phase (+4.5) workflow, wave-based agent team conversion |
| `claude/plugin-tools/skills/validate-adapter/SKILL.md` | 625 | Adapter validation against live platform docs (4 phases) |
| `claude/plugin-tools/skills/update-ported-plugin/SKILL.md` | 793 | Incremental ported plugin updates with dual-track change detection (5 phases) |
| `claude/sdd-tools/skills/create-spec/SKILL.md` | 664 | Adaptive interview with depth-aware questioning |
| `claude/sdd-tools/skills/create-tasks/SKILL.md` | 653 | Spec-to-task decomposition with `task_uid` merge mode |
| `claude/sdd-tools/skills/execute-tasks/SKILL.md` | 262 | Wave-based parallel execution with session management |
| `claude/dev-tools/skills/feature-dev/SKILL.md` | 273 | 7-phase lifecycle spawning architect + reviewer agent teams |
| `claude/dev-tools/skills/bug-killer/SKILL.md` | ~480 | Hypothesis-driven debugging — triage-based quick/deep track with agent investigation |
| `claude/tdd-tools/skills/tdd-cycle/SKILL.md` | 727 | 7-phase RED-GREEN-REFACTOR TDD workflow |
| `claude/tdd-tools/skills/generate-tests/SKILL.md` | 524 | Test generation from acceptance criteria or source code |
| `claude/tdd-tools/skills/create-tdd-tasks/SKILL.md` | 687 | SDD-to-TDD task pair transformation |
| `claude/tdd-tools/skills/execute-tdd-tasks/SKILL.md` | 630 | TDD-aware wave execution with agent routing |
| `claude/plugin-tools/skills/dependency-checker/SKILL.md` | 651 | Ecosystem dependency analysis with 7 detection passes + doc drift |

## Known Challenges

| Challenge | Severity | Notes |
|-----------|----------|-------|
| Cross-plugin `${CLAUDE_PLUGIN_ROOT}` inconsistency | Resolved | Standardized to `/../{source-dir-name}/` pattern. Convention documented above in Cross-Plugin Dependencies. |
| Zero test coverage for VS Code extension | High | Validator is the most critical component — Ajv compilation, path detection, and line-number mapping are all untested. |
| Schema drift risk | Medium | JSON schemas manually maintained. No CI validation ensures schemas match actual plugin frontmatter usage. |
| Large reference files | Medium | plugin-tools has 6 reference files totaling ~3,300 lines + port-plugin SKILL.md (~2,575 lines) + port-converter agent (~390 lines) + session-format.md (~200 lines). Largest single reference is mcp-converter.md (713 lines). Context isolation via wave-based agents mitigates the port-plugin context pressure. |

## Settings

User preferences are stored in `.claude/agent-alchemy.local.md` (not committed):
- `deep-analysis.direct-invocation-approval`: Whether to require plan approval when user invokes directly (default: true)
- `deep-analysis.invocation-by-skill-approval`: Whether to require approval when loaded by another skill (default: false)
- `deep-analysis.cache-ttl-hours`: Hours before exploration cache expires; 0 disables caching (default: 24)
- `deep-analysis.enable-checkpointing`: Write session checkpoints at phase boundaries for recovery (default: true)
- `deep-analysis.enable-progress-indicators`: Display `[Phase N/6]` progress messages during execution (default: true)
- `tdd.framework`: Override test framework auto-detection (`auto` | `pytest` | `jest` | `vitest`, default: `auto`)
- `tdd.coverage-threshold`: Target coverage percentage for analyze-coverage (0-100, default: `80`)
- `tdd.strictness`: RED phase enforcement level (`strict` | `normal` | `relaxed`, default: `normal`)
- `tdd.test-review-threshold`: Minimum test quality score (0-100, default: `70`)
- `tdd.test-review-on-generate`: Auto-run test-reviewer after generate-tests (default: `false`)
- `plugin-tools.dependency-checker.severity-threshold`: Minimum severity to show (`critical` | `high` | `medium` | `low`, default: `low`)
- `plugin-tools.dependency-checker.check-docs-drift`: Run Phase 4 CLAUDE.md/README cross-referencing (default: `true`)
- `plugin-tools.dependency-checker.line-count-tolerance`: Percentage tolerance for line count drift in CLAUDE.md tables (default: `10`)
