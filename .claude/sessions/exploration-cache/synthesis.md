## Synthesized Analysis: Agent Alchemy

### Architecture Overview

Agent Alchemy is a single-author monorepo (144 commits) extending Claude Code into a structured development platform through three interconnected pillars: a markdown-as-code plugin system (core IP), a real-time task dashboard (visualization), and a VS Code extension (authoring toolchain).

The plugin system treats markdown files as executable code — YAML frontmatter + markdown body encode agent instructions, skill workflows, and composition logic. Five plugin groups (core-tools, dev-tools, sdd-tools, tdd-tools, git-tools) contain 20 skills, 12 agents, 33 reference files, and 2 hook configurations.

### Critical Files

| File | Purpose | Relevance |
|------|---------|-----------|
| claude/core-tools/skills/deep-analysis/SKILL.md | 6-phase hub-and-spoke team engine (521 lines) | Keystone — loaded by 4 skills |
| claude/sdd-tools/skills/create-spec/SKILL.md | Adaptive interview for spec creation (664 lines) | High |
| claude/sdd-tools/skills/create-tasks/SKILL.md | Spec-to-task decomposition (653 lines) | High |
| claude/tdd-tools/skills/tdd-cycle/SKILL.md | 7-phase RED-GREEN-REFACTOR (718 lines) | High |
| claude/dev-tools/skills/feature-dev/SKILL.md | 7-phase feature dev lifecycle (271 lines) | High |
| claude/.claude-plugin/marketplace.json | Centralized plugin registry (57 lines) | High |
| apps/task-manager/src/lib/fileWatcher.ts | HMR-safe Chokidar singleton | High |
| apps/task-manager/src/app/api/events/route.ts | SSE streaming endpoint | High |
| apps/task-manager/src/hooks/useSSE.ts | Client SSE hook with reconnection | High |
| extensions/vscode/src/frontmatter/validator.ts | Ajv-based YAML validation | High |

### Key Patterns

1. Skill Composition via Prompt Injection
2. Hub-and-Spoke Team Coordination
3. Phase Workflows with Completeness Enforcement
4. Progressive Knowledge Loading (33 reference files)
5. Agent Tool Restrictions (read-only vs full-capability)
6. Model Tiering (Opus/Sonnet/Haiku)
7. AskUserQuestion Enforcement
8. GlobalThis Singleton for HMR
9. Schema-Driven Authoring
10. Hook-Based Auto-Approval

### Challenges & Risks

| Challenge | Severity |
|-----------|----------|
| Cross-plugin ${CLAUDE_PLUGIN_ROOT} inconsistency | High |
| Zero test coverage for VS Code extension | High |
| Potential schema drift | Medium |
| Large reference files approaching context limits | Medium |
| Polling overhead in file watcher | Medium |
| No pagination in task manager | Low |
| Execution context uses polling (not SSE) | Low |
| Markdown rendering XSS surface | Low |

### Recommendations

1. Standardize cross-plugin references
2. Add VS Code extension tests
3. Add schema synchronization CI check
4. Consider fsevents for macOS
5. Document the plugin architecture formally

### Completeness: High confidence across all three pillars.
