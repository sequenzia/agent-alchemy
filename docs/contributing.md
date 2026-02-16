# Contributing

Thank you for your interest in contributing to Agent Alchemy! This guide covers the development setup, conventions, and workflow.

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- Node.js >= 18.0.0
- pnpm >= 8.0.0
- Python 3.x (for MkDocs documentation site)

## Repository Setup

```bash
git clone https://github.com/sequenzia/agent-alchemy.git
cd agent-alchemy
pnpm install
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
npm run watch                  # Watch mode for development
npm run package                # Package VSIX

# Linting
pnpm lint                      # Lint all packages

# Documentation
mkdocs serve                   # Preview docs site locally
mkdocs build --strict          # Build with strict validation
```

## Project Structure

| Directory | What Lives Here |
|-----------|----------------|
| `claude/core-tools/` | Core analysis and exploration plugins |
| `claude/dev-tools/` | Development lifecycle plugins |
| `claude/sdd-tools/` | Spec-Driven Development plugins |
| `claude/tdd-tools/` | Test-Driven Development plugins |
| `claude/git-tools/` | Git automation plugins |
| `apps/task-manager/` | Next.js real-time dashboard |
| `extensions/vscode/` | VS Code extension |
| `docs/` | MkDocs documentation source |
| `internal/` | Internal documentation and analysis |

## Conventions

### Git Commits

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description
```

| Type | When to Use |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Code style (formatting, not CSS) |
| `refactor` | Code restructuring without behavior change |
| `test` | Adding or updating tests |
| `chore` | Build process, tooling, dependencies |

**Examples:**

```bash
feat(sdd-tools): add TDD task pair generation
fix(task-manager): resolve SSE reconnection on network drop
docs(core-tools): update deep-analysis phase descriptions
chore(vscode): bump Ajv to v8.17
```

!!! tip "Use the Plugin"
    You can use `/git-commit` to auto-generate conventional commit messages from your staged changes.

### Code Style

- **TypeScript:** Strict mode, functional patterns preferred
- **Styling:** Tailwind CSS v4 with shadcn/ui components
- **Naming:** Self-documenting names over comments
- **Comments:** Only when the "why" isn't obvious from the code

### Plugin Development

When creating or modifying plugins:

- **Skills** are defined in `skills/{name}/SKILL.md` with YAML frontmatter
- **Agents** are defined in `agents/{name}.md` with YAML frontmatter
- **Hooks** are configured in `hooks/hooks.json`
- Cross-plugin references use `${CLAUDE_PLUGIN_ROOT}/../{source-dir-name}/`
- Same-plugin references use `${CLAUDE_PLUGIN_ROOT}/`

See the [Plugin Overview](plugins/index.md) for detailed architecture guidance.

## Making Changes

1. **Create a branch** from `main`
2. **Make your changes** following the conventions above
3. **Test your changes** — run linting, build checks, and manual testing
4. **Commit** with a conventional commit message
5. **Open a pull request** against `main`

## Areas Where Help is Needed

| Area | Priority | Details |
|------|----------|---------|
| VS Code extension tests | High | Zero test coverage — Ajv compilation, path detection, and line-number mapping need tests |
| Schema synchronization | Medium | No CI validation ensures JSON schemas match actual plugin frontmatter usage |
| Documentation improvements | Medium | Always welcome — typos, clarity, examples |
