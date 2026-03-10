# Integration Guide: dev-tools

## Overview

The dev-tools package provides development workflow capabilities: feature development lifecycle, hypothesis-driven debugging, code review, documentation management, changelog automation, and release tooling. It depends heavily on core-tools for codebase exploration and diagram generation.

## Component Inventory

| Component | Type | Description |
|-----------|------|-------------|
| feature-dev | Skill | 7-phase feature development: discovery, exploration, design, implementation, review, summary |
| bug-killer | Skill | Hypothesis-driven debugging with triage-based quick/deep track routing |
| architecture-patterns | Skill | Architectural pattern reference: MVC, event-driven, CQRS, hexagonal, microservices |
| code-quality | Skill | SOLID, DRY, KISS, YAGNI principles and code review checklists |
| project-learnings | Skill | Captures project-specific patterns and anti-patterns into project configuration |
| changelog-format | Skill | Keep a Changelog format guidelines and entry writing best practices |
| docs-manager | Skill | Documentation management for MkDocs sites and standalone markdown files |
| release | Skill | Python package release workflow with tests, linting, changelog, and tagging |
| document-changes | Skill | Generate markdown reports documenting codebase changes from git history |
| code-reviewer | Agent | Reviews code for correctness, security, maintainability with confidence scoring |
| bug-investigator | Agent | Diagnostic investigation agent that tests debugging hypotheses |
| changelog-manager | Agent | Analyzes git history and updates CHANGELOG.md |
| docs-writer | Agent | Generates MkDocs or GitHub-flavored Markdown documentation |

## Capability Requirements

- **File operations**: Read, search, and browse files. Required by all skills and agents.
- **File writing**: Create and modify files. Required by feature-dev (implementation), bug-killer (fixes), docs-manager (docs), release (changelog), document-changes (reports), project-learnings (CLAUDE.md updates), changelog-manager (CHANGELOG.md).
- **Shell execution**: Run git, test runners, linters, build tools. Required by bug-killer (tests), release (pytest, ruff, uv, git), document-changes (git), changelog-manager (git), docs-writer (git, mkdocs), docs-manager (git, mkdocs).
- **User interaction**: Present choices and collect input. Required by feature-dev (approvals at each phase), bug-killer (track selection, hypothesis review), docs-manager (format selection, plan approval), release (version confirmation), project-learnings (learning confirmation).
- **Sub-agent delegation**: Spawn worker agents. Required by feature-dev (code-architect x2-3, code-reviewer x3), bug-killer (code-explorer x2-3, bug-investigator x1-3), docs-manager (docs-writer x N).

## Per-Component Notes

### feature-dev

**What it does:** End-to-end feature development from requirements through implementation and review.

**Capabilities needed:** File operations, file writing, shell execution, sub-agent delegation, user interaction.

**Adaptation guidance:**
- Phase 2 delegates to deep-analysis (core-tools). This cross-package dependency must be resolved.
- Phase 4 spawns 2-3 code-architect agents (core-tools) with different design approaches. Map to your agent spawning mechanism.
- Phase 6 spawns 3 code-reviewer agents with different review focuses.
- ADR template and changelog entry template are embedded in the skill.

### bug-killer

**What it does:** Systematic debugging with hypothesis journals, evidence gathering, and root cause analysis.

**Capabilities needed:** File operations, file writing, shell execution, sub-agent delegation, user interaction.

**Adaptation guidance:**
- Quick track uses direct investigation (no agents). Deep track spawns code-explorer and bug-investigator agents.
- Language-specific debugging references for Python and TypeScript are in `references/`. General debugging is embedded.
- The hypothesis journal format is the core artifact — maintain it through all phases regardless of platform.

### docs-manager

**What it does:** Interactive documentation workflow supporting MkDocs sites, standalone markdown, and change summaries.

**Capabilities needed:** File operations, file writing, shell execution, sub-agent delegation, user interaction.

**Adaptation guidance:**
- Phase 3 delegates to deep-analysis (core-tools) for codebase understanding.
- Phase 5 spawns docs-writer agents for parallel content generation.
- The markdown-file-templates reference is in `references/`. MkDocs config template and change summary templates are embedded.

### release

**What it does:** Python package release with pre-flight checks, tests, linting, version calculation, changelog update, and git tagging.

**Capabilities needed:** Shell execution (git, uv, ruff, pytest), file writing (CHANGELOG.md), user interaction.

**Adaptation guidance:**
- Tightly coupled to Python tooling (uv, ruff, pytest). Adapt tool commands for other ecosystems.
- Optionally spawns changelog-manager agent before release.
- The 9-step workflow is sequential with fail-fast behavior.

### document-changes

**What it does:** Generates a structured markdown report from git history showing files changed, commits, and diffs.

**Capabilities needed:** Shell execution (git), file writing, user interaction.

**Adaptation guidance:** Git-dependent — requires a git repository. Self-contained workflow with no agent delegation.

### code-reviewer (agent)

**What it does:** Reviews code with confidence-scored findings (only reports issues >= 80 confidence).

**Capabilities needed:** File operations (read-only), inter-agent messaging.

**Adaptation guidance:** Spawned by feature-dev in Phase 6 with specific review focuses. Read-only — does not modify code.

### bug-investigator (agent)

**What it does:** Tests debugging hypotheses through code tracing, diagnostic testing, git history analysis.

**Capabilities needed:** File operations (read-only), shell execution (git, test runners), inter-agent messaging.

**Adaptation guidance:** Spawned by bug-killer in Phase 3 (deep track). Investigates and reports — does not fix code.

### changelog-manager (agent)

**What it does:** Analyzes git commits, categorizes changes, synthesizes changelog entries, updates CHANGELOG.md.

**Capabilities needed:** Shell execution (git, gh), file operations, file writing, user interaction.

**Adaptation guidance:** Self-contained agent. Can be spawned by release skill or used independently.

### docs-writer (agent)

**What it does:** Generates documentation pages from codebase analysis findings in MkDocs or GitHub-flavored Markdown.

**Capabilities needed:** File operations, shell execution, inter-agent messaging.

**Adaptation guidance:** Preloads technical-diagrams (core-tools) for Mermaid diagram generation. Supports two output modes (MkDocs vs Basic Markdown).

## Dependency Map

```
feature-dev
  |
  +--> deep-analysis (core-tools, Phase 2)
  +--> architecture-patterns (Phase 4)
  +--> language-patterns (core-tools, Phase 4)
  +--> technical-diagrams (core-tools, Phase 4)
  +--> code-architect (core-tools, Phase 4, x2-3)
  +--> code-quality (Phase 6)
  +--> code-reviewer (Phase 6, x3)
  +--> changelog-format (Phase 7)

bug-killer
  |
  +--> code-explorer (core-tools, Phase 2 deep track, x2-3)
  +--> bug-investigator (Phase 3 deep track, x1-3)
  +--> code-quality (Phase 4 deep track)
  +--> project-learnings (Phase 5)

docs-manager
  |
  +--> deep-analysis (core-tools, Phase 3)
  +--> docs-writer (Phase 5, x N)
        |
        +--> technical-diagrams (core-tools, preload)

release --> changelog-manager (optional, Step 5)
```

**External dependencies (from core-tools package):**
deep-analysis, language-patterns, technical-diagrams, code-explorer, code-architect

## Adaptation Checklist

- [ ] Review each skill's instructions and adapt tool-specific language for your harness
- [ ] Configure agent spawning for feature-dev (architects + reviewers), bug-killer (explorers + investigators), and docs-manager (docs-writers)
- [ ] Resolve cross-package dependencies on core-tools (deep-analysis, technical-diagrams, language-patterns, code-explorer, code-architect)
- [ ] Set up lifecycle hooks if your harness supports them (session_start for dependency resolution)
- [ ] Resolve external dependencies listed in manifest.yaml
- [ ] Test each component individually before combining:
  1. Start with standalone skills: architecture-patterns, code-quality, changelog-format, project-learnings
  2. Test document-changes and release (git-dependent but no agent delegation)
  3. Test bug-killer quick track (no agents needed)
  4. Test feature-dev and bug-killer deep track with agent delegation
  5. Test docs-manager end-to-end
