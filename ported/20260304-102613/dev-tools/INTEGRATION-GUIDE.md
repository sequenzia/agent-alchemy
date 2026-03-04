# Integration Guide: dev-tools

## Overview

The dev-tools package provides structured development workflows: feature implementation with multi-phase architecture design, hypothesis-driven debugging, code quality review, documentation generation, changelog management, and Python package release automation. It builds on core-tools for exploration and synthesis capabilities.

## Component Inventory

| Component | Type | Origin | Description |
|-----------|------|--------|-------------|
| feature-dev | skill | skill | 7-phase feature development workflow (discovery → implementation → review) |
| bug-killer | skill | skill | Hypothesis-driven debugging with quick/deep track routing |
| code-quality | skill | skill | SOLID, DRY, testing strategies, and code review checklist |
| architecture-patterns | skill | skill | MVC, event-driven, microservices, CQRS pattern knowledge |
| docs-manager | skill | skill | MkDocs and standalone markdown documentation management |
| changelog-format | skill | skill | Keep a Changelog format guidelines with examples |
| project-learnings | skill | skill | Captures project-specific patterns into documentation |
| document-changes | skill | skill | Generates change reports from git history |
| release | skill | skill | Python package release workflow with uv/ruff |
| code-reviewer | skill | agent | Confidence-scored code review for correctness, security, maintainability |
| bug-investigator | skill | agent | Diagnostic investigation for testing debugging hypotheses |
| docs-writer | skill | agent | MkDocs and GitHub-flavored Markdown documentation generation |
| changelog-manager | skill | agent | Git history analysis and CHANGELOG.md update automation |

## Capability Requirements

### File operations
- **All skills**: Need to read files and search codebases
- **feature-dev**, **bug-killer**, **docs-manager**, **document-changes**: Need file writing/editing
- **project-learnings**: Needs file editing (modifies project documentation)

### Shell execution
- **bug-killer**: Runs tests, git commands for investigation
- **docs-manager**: Runs git commands, optionally `mkdocs build`
- **document-changes**: Runs git commands for change data collection
- **release**: Runs pytest, ruff, uv build, git tag/push
- **changelog-manager**: Runs git log, git diff, optionally `gh` CLI
- **bug-investigator**: Runs tests, git blame, diagnostic commands

### User interaction
- **feature-dev**: Prompts at discovery, architecture selection, implementation approval, review actions
- **bug-killer**: Prompts for track selection, investigation direction, fix options
- **docs-manager**: Prompts for doc type, scope, plan approval, file locations
- **release**: Prompts for changelog update, version confirmation
- **project-learnings**: Prompts for learning confirmation before writing

### Sub-agent delegation
- **feature-dev**: Delegates to code-architect (2-3 instances), code-reviewer (3 instances), plus deep-analysis
- **bug-killer**: Delegates to code-explorer (2-3 instances, deep track), bug-investigator (1-3 instances)
- **docs-manager**: Delegates to deep-analysis, docs-writer (parallel for independent pages)
- **release**: Delegates to changelog-manager for pre-release changelog update

## Per-Component Notes

### feature-dev
The most complex workflow — 7 phases from discovery to summary. Phase 2 loads deep-analysis (from core-tools) for exploration. Phase 4 spawns parallel architects for competing design proposals. Phase 6 spawns parallel reviewers with different focus areas. Inlined templates: ADR template and changelog entry template.

### bug-killer
Two-track system: quick track (1-2 files, obvious fix) and deep track (multi-file, parallel investigation agents). Auto-escalates from quick to deep after 2 rejected hypotheses. Inlined: general debugging reference. Separate references: python-debugging.md and typescript-debugging.md in `references/`.

### docs-manager
Supports three documentation types: MkDocs sites, standalone markdown files, and change summaries. Inlined templates: MkDocs config and change summary templates. Separate: markdown-file-templates.md in `references/`. Uses deep-analysis (core-tools) for codebase understanding.

### code-quality / architecture-patterns / changelog-format
Pure reference skills — no orchestration, no tool use. Loaded by other skills as knowledge bases. changelog-format includes inlined entry examples.

### project-learnings
Lightweight skill that evaluates debugging/development discoveries against project-specific criteria and optionally writes them to project documentation.

### document-changes / release
Standalone workflow skills. document-changes generates reports from git data. release automates Python package release with pre-flight checks, changelog management, and tag creation.

### code-reviewer / bug-investigator / docs-writer / changelog-manager
Originally sub-agents with structured output formats. code-reviewer uses confidence scoring (only reports issues ≥80%). bug-investigator follows a structured investigation report format. docs-writer supports both MkDocs and basic Markdown output modes. changelog-manager follows Keep a Changelog with conventional commit parsing.

## Dependency Map

```
feature-dev
├── deep-analysis (core-tools) — codebase exploration
├── architecture-patterns — design guidance
├── language-patterns (core-tools) — language-specific patterns
├── technical-diagrams (core-tools) — architecture diagrams
├── code-quality — implementation review
├── code-architect (core-tools) × 2-3 — parallel design proposals
├── code-reviewer × 3 — parallel quality review
└── changelog-format — changelog entry writing

bug-killer
├── code-quality — fix quality validation
├── project-learnings — capture discoveries
├── code-explorer (core-tools) × 2-3 — deep track exploration
└── bug-investigator × 1-3 — hypothesis testing

docs-manager
├── deep-analysis (core-tools) — codebase understanding
└── docs-writer × N — parallel content generation
    └── technical-diagrams (core-tools) — diagram generation

release
└── changelog-manager — pre-release changelog update
```

## Flatten Mode Notes

This package was converted in flatten mode — all components are skills.

### Agent-Converted Skills
- **code-reviewer** — Originally an Opus-tier review agent (read-only). Focus areas: correctness, security, maintainability.
- **bug-investigator** — Originally a Sonnet-tier investigation agent with shell access. Tests hypotheses via diagnostic commands.
- **docs-writer** — Originally an Opus-tier writing agent with shell access. Generates documentation from codebase analysis.
- **changelog-manager** — Originally a Sonnet-tier agent with file editing and shell access. Parses git history and updates CHANGELOG.md.

### Capability Notes
- code-reviewer was read-only — no file modification capability
- bug-investigator had shell access but no file modification — investigate only, don't fix
- docs-writer and changelog-manager could both read and modify files

## Adaptation Checklist
- [ ] Review each skill's instructions and adapt tool-specific language for your harness
- [ ] Review agent-converted skills for role-appropriate context injection
- [ ] Resolve external dependencies on core-tools (deep-analysis, technical-diagrams, language-patterns, code-explorer, code-architect)
- [ ] Test feature-dev end-to-end: discovery → exploration → architecture → implementation → review
- [ ] Test bug-killer with both quick and deep tracks
- [ ] Test each component individually before combining
