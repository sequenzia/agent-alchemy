# Integration Guide: dev-tools

## Overview

The dev-tools package provides structured workflows for feature development, debugging, documentation, code review, and release management. It builds on core-tools for codebase exploration and includes specialized agents for code review, bug investigation, changelog management, and documentation writing.

## Component Inventory

| Component | Type | Origin | Parent Skill | Description |
|-----------|------|--------|-------------|-------------|
| architecture-patterns | skill | skill | — | Architectural pattern knowledge (MVC, event-driven, microservices, CQRS) |
| code-quality | skill | skill | — | SOLID, DRY, testing strategies, and code review principles |
| project-learnings | skill | skill | — | Captures project-specific patterns into CLAUDE.md |
| changelog-format | skill | skill | — | Keep a Changelog format guidelines with entry examples |
| document-changes | skill | skill | — | Generates markdown reports of session codebase changes |
| release | skill | skill | — | Python package release workflow with verification steps |
| changelog-manager | agent | agent | release | Reviews git history and updates CHANGELOG.md |
| feature-dev | skill | skill | — | 7-phase feature development lifecycle |
| code-reviewer | agent | agent | feature-dev | Confidence-scored code review for correctness, security, maintainability |
| bug-killer | skill | skill | — | Hypothesis-driven debugging with quick/deep track routing |
| bug-investigator | agent | agent | bug-killer | Diagnostic investigation to test debugging hypotheses |
| docs-manager | skill | skill | — | Documentation management for MkDocs and standalone markdown |
| docs-writer | agent | agent | docs-manager | Generates high-quality markdown documentation |

## Capability Requirements

- **File reading and searching**: All skills and agents
- **File writing and editing**: feature-dev (implementation), bug-killer (fixes), docs-manager (doc files), release (changelog), document-changes (reports), project-learnings (CLAUDE.md), changelog-manager (CHANGELOG.md)
- **Shell command execution**: bug-killer (test running, git history), bug-investigator (diagnostic commands), release (tests, linting, git tags), document-changes (git queries), changelog-manager (git log, gh CLI), docs-manager (mkdocs build)
- **User interaction / prompting**: feature-dev (6 decision points across phases), bug-killer (track selection, fix approval), docs-manager (doc type selection, plan approval), release (version confirmation, changelog update), document-changes (report location)
- **Sub-agent delegation**: feature-dev (2-3 architect agents + 3 reviewer agents), bug-killer (2-3 explorer agents + 1-3 investigator agents), docs-manager (1+ docs-writer agents), release (1 changelog-manager agent)

Note: Agent and hook capabilities have been folded into skills in nested mode. Agent capabilities are documented within their parent skill's Integration Notes under "Sub-agent capabilities."

## Nested Mode Notes

This package was converted in nested mode — agents are embedded within their parent skills as pure markdown instruction files.

### Nesting Map

| Agent | Parent Skill | Role | Purpose |
|-------|-------------|------|---------|
| code-reviewer | feature-dev | reviewer | Reviews implementations for correctness, security, maintainability |
| bug-investigator | bug-killer | investigator | Tests specific debugging hypotheses with diagnostic commands |
| changelog-manager | release | writer | Analyzes git history and generates changelog entries |
| docs-writer | docs-manager | writer | Generates MkDocs or GitHub-flavored markdown documentation |

### Reading Nested Agents

Each parent skill's SKILL.md contains a "Nested Agents" section listing its sub-agents with one-line descriptions. The agent files in `agents/` are pure markdown instructions — read them when spawning the corresponding sub-agent. They have no YAML frontmatter.

### Orphan Agents

No orphan agents — all agents are nested under a parent skill.

### Cross-Skill Agent References

- **feature-dev** references the **code-architect** agent from **codebase-analysis** in the core-tools package
- **bug-killer** references the **code-explorer** agent from **deep-analysis** in the core-tools package
- **docs-manager** references the **code-explorer** agent from **deep-analysis** in the core-tools package

## Per-Component Notes

### architecture-patterns
Pure reference material for architectural patterns. No special integration needed.

### code-quality
Pure reference material for code review standards. Loaded by feature-dev and bug-killer for quality checks.

### project-learnings
Captures project-specific knowledge into the project's CLAUDE.md file. Requires file reading and editing capabilities. Uses user interaction to confirm additions.

### changelog-format
Pure reference material with inlined entry examples. Loaded by feature-dev for changelog updates.

### document-changes
Self-contained workflow that analyzes git state and writes a structured change report. Requires shell execution for git commands and file writing for the report.

### release
Python-specific release workflow (uv, ruff, pytest). Spawns a changelog-manager agent before version calculation. Requires shell execution for tests, linting, builds, and git operations.

### feature-dev
The most complex skill in this package. Seven phases spanning discovery through summary:
1. Discovery → 2. Codebase Exploration (via deep-analysis from core-tools) → 3. Clarifying Questions → 4. Architecture Design (spawns architect agents from core-tools) → 5. Implementation → 6. Quality Review (spawns reviewer agents) → 7. Summary

**External dependencies (from core-tools):** deep-analysis, language-patterns, technical-diagrams, code-architect

### bug-killer
Hypothesis-driven debugging with automatic quick/deep track routing. Quick track investigates directly; deep track spawns parallel explorer and investigator agents.

**External dependencies (from core-tools):** code-explorer (for deep-track exploration)

### docs-manager
Six-phase documentation workflow supporting MkDocs sites and standalone markdown files. Uses deep-analysis from core-tools for codebase understanding, then spawns docs-writer agents for content generation.

**External dependencies (from core-tools):** deep-analysis, code-explorer

## Dependency Map

```
feature-dev
├── deep-analysis (core-tools, Phase 2)
├── architecture-patterns (Phase 4)
├── language-patterns (core-tools, Phase 4)
├── technical-diagrams (core-tools, Phase 4)
├── code-quality (Phase 6)
├── changelog-format (Phase 7)
├── code-architect (core-tools, nested under codebase-analysis)
└── code-reviewer (nested agent, Phase 6)

bug-killer
├── code-quality (deep track Phase 4)
├── project-learnings (Phase 5)
├── code-explorer (core-tools, nested under deep-analysis)
└── bug-investigator (nested agent, Phase 3)

docs-manager
├── deep-analysis (core-tools, Phase 3)
├── code-explorer (core-tools, change-summary path)
└── docs-writer (nested agent, Phase 5)

release
└── changelog-manager (nested agent, Step 5)
```

## Adaptation Checklist

- [ ] Review each skill's instructions and adapt tool-specific language for your harness
- [ ] For skills with nested agents, configure sub-agent spawning to read instructions from the `agents/` directory
- [ ] Review agent-converted skills for role-appropriate context injection
- [ ] Check cross-skill agent references to core-tools and ensure relative paths work in your harness
- [ ] Resolve external dependencies on core-tools (deep-analysis, language-patterns, technical-diagrams, code-explorer, code-architect)
- [ ] Test each component individually before combining
- [ ] For feature-dev and bug-killer, verify the multi-agent workflows function correctly with your harness's delegation mechanism
