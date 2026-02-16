## Reconnaissance Summary

### Project Overview
Agent Alchemy is a monorepo extending Claude Code into a structured development platform through markdown-as-code plugins, a real-time task dashboard, and a VS Code extension.

### Structure
- `claude/` — 5 plugin groups (core-tools, dev-tools, sdd-tools, tdd-tools, git-tools) with ~60+ markdown files
- `apps/task-manager/` — Next.js 16 real-time Kanban dashboard (~30 source files)
- `extensions/vscode/` — VS Code extension for plugin authoring (6 source files)
- `internal/` — Documentation and analysis files
- `specs/` — Feature specifications
- `scripts/` — Deployment scripts
- `site/` — MkDocs documentation site

### Key Configurations
- pnpm monorepo with Node >=18
- Task manager: Next.js 16, React 19, TanStack Query v5, Tailwind CSS v4, Chokidar v5
- VS Code extension: Ajv-based validation, esbuild bundling
- Conventional Commits, TypeScript strict mode

### Focus Areas Identified
1. Plugin Architecture & Composition Patterns (High complexity)
2. Task Manager Application (Medium complexity)
3. VS Code Extension & Developer Infrastructure (Medium complexity)
