## Reconnaissance Summary

### Project Overview
- **Name**: Agent Alchemy
- **Type**: Monorepo — Claude Code plugin platform + companion applications
- **Primary languages**: TypeScript (apps, VS Code extension), Markdown-as-code (plugins)
- **Package manager**: pnpm (workspaces), uv (Python for MkDocs)

### Directory Structure
- `claude/` — 6 plugin groups with skills (SKILL.md), agents (.md), hooks (hooks.json), references
  - core-tools (v0.2.0), dev-tools (v0.3.0), git-tools (v0.1.0), sdd-tools (v0.2.0), tdd-tools (v0.2.0), plugin-tools (v0.1.1)
  - Marketplace registry at `claude/.claude-plugin/marketplace.json`
- `apps/task-manager/` — Next.js 16 real-time Kanban dashboard (36 TS/TSX files)
- `extensions/vscode/` — VS Code extension (6 TS source files, 7 JSON schemas)
- `docs/` + `site/` — MkDocs documentation site
- `internal/` — Internal documentation and analysis

### Key Observations
- Plugin system uses markdown-as-code: skills = SKILL.md with YAML frontmatter, agents = name.md
- Hub-and-spoke agent team pattern is the keystone architecture (deep-analysis skill)
- Cross-plugin composition via `${CLAUDE_PLUGIN_ROOT}/../{source-dir-name}/`
- Task Manager uses SSE for real-time updates: Chokidar watches ~/.claude/tasks/ → SSE → TanStack Query
- VS Code extension provides Ajv-based YAML frontmatter validation + JSON schema validation
- ~90+ markdown files across the claude/ directory (skills, agents, references)
