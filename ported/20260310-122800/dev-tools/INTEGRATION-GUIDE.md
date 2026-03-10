# Integration Guide: dev-tools

## Overview
Development workflow skills — feature development, debugging, code review, documentation management, changelog automation, and release management. Many components in this package depend on core-tools for codebase exploration and analysis.

## Component Inventory
| Component | Type | Origin | Description |
|-----------|------|--------|-------------|
| changelog-format | skill | skill | Keep a Changelog format guidelines and entry writing best practices |
| code-quality | skill | skill | Code quality principles (SOLID, DRY, testing strategies) |
| release | skill | skill | Python package release workflow with verification steps |
| document-changes | skill | skill | Generate markdown reports documenting codebase changes |
| project-learnings | skill | skill | Capture project-specific patterns into project documentation |
| bug-killer | skill | skill | Hypothesis-driven debugging with triage-based track routing |
| docs-manager | skill | skill | Documentation management for MkDocs sites and standalone markdown |
| architecture-patterns | skill | skill | Architectural pattern knowledge (MVC, event-driven, CQRS, etc.) |
| feature-dev | skill | skill | 7-phase feature development workflow |
| changelog-manager | skill | agent | Git history analysis and CHANGELOG.md updates |
| code-reviewer | skill | agent | Code review with confidence-scored findings |
| bug-investigator | skill | agent | Diagnostic investigation to test debugging hypotheses |
| docs-writer | skill | agent | MkDocs and GitHub-flavored Markdown documentation generation |
| lifecycle-hooks | skill | hooks | Cross-plugin dependency resolution at session start |

## Capability Requirements

- **File operations**: Most skills need file reading and searching. `feature-dev`, `bug-killer`, `docs-manager`, `release`, `document-changes` also need file writing/editing.
- **Shell execution**: `bug-killer`, `release`, `document-changes`, `changelog-manager`, `bug-investigator`, `docs-writer` run shell commands (git, test runners, linters, build tools).
- **User interaction**: `feature-dev`, `bug-killer`, `docs-manager`, `release`, `document-changes`, `project-learnings` prompt users for decisions and approval.
- **Sub-agent delegation**: `feature-dev` delegates to code-architect and code-reviewer agents. `bug-killer` delegates to code-explorer and bug-investigator agents. `docs-manager` delegates to docs-writer agents. `release` delegates to changelog-manager.

## Per-Component Notes

### changelog-format
A reference skill providing Keep a Changelog format guidelines. No external dependencies. Used by feature-dev during the summary phase.

### code-quality
A reference skill providing SOLID, DRY, and testing best practices. No external dependencies. Used by bug-killer (deep track) and feature-dev (review phase).

### release
A 9-step Python package release workflow using `uv` and `ruff`. Stages: pre-flight checks, tests, linting, build verification, changelog update, version calculation, commit, and tag creation. Can delegate to changelog-manager for CHANGELOG.md updates.

### document-changes
Generates structured markdown reports from git history — files changed, commits, and a human-readable summary. Writes to `internal/reports/` by default.

### project-learnings
Evaluates debugging discoveries for project-specific knowledge and captures qualifying findings into the project's documentation file. Loaded by bug-killer and feature-dev when they discover project-specific patterns.

### bug-killer
A 5-phase debugging workflow: triage, investigation, root cause analysis, fix & verify, wrap-up. Routes bugs to quick or deep tracks based on complexity signals. Deep track uses parallel code-explorer agents (from core-tools) for investigation and bug-investigator agents for hypothesis testing. Depends on code-quality and project-learnings. Has 3 language-specific debugging reference files (Python, TypeScript, general).

### docs-manager
A 6-phase documentation workflow supporting MkDocs sites and standalone markdown. Uses deep-analysis (from core-tools) for codebase exploration, then delegates to docs-writer agents for content generation. Contains reference templates for MkDocs config, change summaries, and markdown files.

### architecture-patterns
A reference skill providing architectural pattern knowledge (layered, MVC, repository, service layer, event-driven, CQRS, hexagonal, microservices). Includes Mermaid diagrams following technical-diagrams conventions.

### feature-dev
A 7-phase feature development lifecycle: discovery, codebase exploration (via deep-analysis from core-tools), clarifying questions, architecture design (delegates to code-architect agents from core-tools), implementation, quality review (delegates to code-reviewer agents), and summary with changelog update. The most dependency-heavy skill in this package.

### changelog-manager
Originally a Sonnet-model agent. Analyzes git history with deep diff analysis, PR/issue enrichment, and breaking change detection. Produces categorized changelog entries following Keep a Changelog format.

### code-reviewer
Originally an Opus-model agent. Reviews code for correctness, security, and maintainability with confidence-scored findings (only reports issues >= 80% confidence). Supports three review focuses: correctness/edge cases, security/error handling, and maintainability/quality.

### bug-investigator
Originally a Sonnet-model agent. Tests specific debugging hypotheses through code tracing, diagnostic testing, git history analysis, and state/configuration checks. Reports structured evidence-based findings with a verdict (confirmed/rejected/inconclusive).

### docs-writer
Originally an Opus-model agent. Generates documentation in MkDocs-flavored or standard GitHub-flavored Markdown. Supports API references, architecture guides, how-to guides, and change summaries. Depends on technical-diagrams (from core-tools) for Mermaid conventions.

### lifecycle-hooks
Cross-plugin dependency resolution script that creates symlinks for cross-package references at session start. In the ported context, this behavior is likely unnecessary since ported files use named references instead of filesystem paths.

## Dependency Map

```
feature-dev
├── architecture-patterns
├── code-quality
├── changelog-format
├── (external) deep-analysis [core-tools]
├── (external) language-patterns [core-tools]
├── (external) technical-diagrams [core-tools]
├── (external) code-architect [core-tools]
└── (delegates to) code-reviewer

bug-killer
├── code-quality
├── project-learnings
├── (external) code-explorer [core-tools]
└── (delegates to) bug-investigator

docs-manager
├── (external) deep-analysis [core-tools]
└── (delegates to) docs-writer
    └── (external) technical-diagrams [core-tools]

release
└── (delegates to) changelog-manager
```

## Flatten Mode Notes

This package was converted in flatten mode — all components are skills.

### Agent-Converted Skills
- **changelog-manager**: Originally a Sonnet-model agent for git history analysis and changelog updates. Spawned by the release skill.
- **code-reviewer**: Originally an Opus-model agent for code review. Multiple instances spawned with different review focuses (correctness, security, maintainability).
- **bug-investigator**: Originally a Sonnet-model agent for hypothesis testing. Multiple instances spawned in parallel, each testing a different debugging hypothesis.
- **docs-writer**: Originally an Opus-model agent for documentation generation. Multiple instances spawned for independent documentation pages.

### Lifecycle Hooks Skill
Contains 1 behavioral rule: cross-plugin dependency resolution at session start. The original script created filesystem symlinks for cross-package references — likely unnecessary in the ported format since references use named dependencies instead of paths.

### Capability Notes
- changelog-manager had shell + file read/write access (Bash, Read, Edit, Glob, Grep)
- code-reviewer was read-only (Read, Glob, Grep) — no file modification or shell access
- bug-investigator had read + Bash access but no file modification (Read, Glob, Grep, Bash)
- docs-writer had read + Bash access but no file modification (Read, Glob, Grep, Bash)

## Adaptation Checklist
- [ ] Review each skill's instructions and adapt tool-specific language for your harness
- [ ] Review agent-converted skills for role-appropriate context injection
- [ ] Resolve external dependencies on core-tools (deep-analysis, code-explorer, code-architect, technical-diagrams, language-patterns)
- [ ] Implement lifecycle-hooks rules as middleware, event handlers, or manual checks
- [ ] For feature-dev and bug-killer, configure sub-agent delegation for multi-agent workflows
- [ ] Test each component individually before combining
