## Team Plan: Deep Analysis

### Analysis Context
General codebase understanding

### Reconnaissance Summary
- **Project:** Agent Alchemy — monorepo extending Claude Code into a structured development platform
- **Primary language/framework:** TypeScript (Next.js 16, VS Code Extension API), Markdown-as-code (plugins)
- **Codebase size:** ~90+ markdown files in claude/, 36 TS/TSX files in task-manager, 6 TS files in VS Code extension
- **Key observations:**
  - Plugin system is the core innovation — markdown-as-code with skills/agents/hooks
  - Hub-and-spoke agent teams are the keystone architecture pattern
  - Cross-plugin composition chains create deep dependency relationships

### Focus Areas

#### Focus Area 1: Plugin System Architecture (claude/)
- **Directories:** claude/core-tools/, claude/dev-tools/, claude/sdd-tools/, claude/tdd-tools/, claude/plugin-tools/, claude/git-tools/
- **Starting files:** claude/.claude-plugin/marketplace.json, claude/core-tools/skills/deep-analysis/SKILL.md, claude/dev-tools/skills/feature-dev/SKILL.md
- **Search patterns:** SKILL.md, ${CLAUDE_PLUGIN_ROOT}, subagent_type, allowed-tools
- **Complexity:** High
- **Assigned to:** explorer-1 (sonnet)

#### Focus Area 2: Task Manager Application (apps/task-manager/)
- **Directories:** apps/task-manager/src/
- **Starting files:** apps/task-manager/src/lib/fileWatcher.ts, apps/task-manager/src/app/api/events/route.ts, apps/task-manager/src/components/KanbanBoard.tsx
- **Search patterns:** chokidar, ReadableStream, useSSE, TanStack, invalidate
- **Complexity:** Medium
- **Assigned to:** explorer-2 (sonnet)

#### Focus Area 3: VS Code Extension, Tooling & Infrastructure
- **Directories:** extensions/vscode/src/, extensions/vscode/schemas/, docs/, scripts/
- **Starting files:** extensions/vscode/src/extension.ts, extensions/vscode/src/frontmatter/validator.ts, mkdocs.yml
- **Search patterns:** activate, Ajv, validate, schema, CompletionItem
- **Complexity:** Medium
- **Assigned to:** explorer-3 (sonnet)

### Agent Composition
| Role | Count | Model | Purpose |
|------|-------|-------|---------|
| Explorer | 3 | sonnet | Independent focus area exploration |
| Synthesizer | 1 | opus | Merge findings, deep investigation |

### Task Dependencies
- Exploration Tasks 1-3: parallel (no dependencies)
- Synthesis Task: blocked by all exploration tasks
