# Integration Guide: dev-tools

## Overview

The dev-tools package provides a comprehensive set of development utilities for feature development, debugging, code review, documentation management, changelog maintenance, and release workflows. It is designed as a composable system where skills orchestrate agents for parallel work, and reference skills provide shared knowledge.

## Component Inventory

| Component | Type | Description |
|-----------|------|-------------|
| feature-dev | Skill | 7-phase feature development workflow: discovery, exploration, architecture design, implementation, review, summary |
| bug-killer | Skill | Hypothesis-driven debugging with quick/deep track routing, parallel investigation agents |
| architecture-patterns | Skill | Reference catalog of architectural patterns (MVC, CQRS, hexagonal, etc.) with Mermaid diagrams |
| code-quality | Skill | SOLID, DRY, KISS, YAGNI principles, testing strategies, code review checklists |
| project-learnings | Skill | Captures project-specific patterns into the project's AI knowledge base |
| changelog-format | Skill | Keep a Changelog format guidelines with good/bad entry examples |
| docs-manager | Skill | 6-phase documentation management for MkDocs sites and standalone markdown files |
| release-python-package | Skill | 9-step Python package release workflow with test/lint/build verification |
| document-changes | Skill | Generates structured markdown reports of codebase changes from git history |
| code-reviewer | Agent | Reviews code with confidence-scored findings (correctness, security, maintainability) |
| bug-investigator | Agent | Tests debugging hypotheses through diagnostic commands and code tracing |
| changelog-manager | Agent | Analyzes git history to produce categorized changelog entries |
| docs-writer | Agent | Generates documentation in MkDocs or GitHub-flavored Markdown |

## Capability Requirements

- **File operations**: Read, write, and edit files. All skills and agents require at minimum file reading. Skills that modify code (feature-dev, bug-killer, release-python-package) also need write/edit. Project-learnings needs edit for updating the knowledge base.
- **Shell execution**: Required by bug-killer (running tests, git commands), release-python-package (uv, ruff, pytest, git), document-changes (git commands), changelog-manager (git, gh CLI), docs-manager (git, mkdocs CLI), and bug-investigator (diagnostic commands).
- **User interaction**: All workflow skills (feature-dev, bug-killer, docs-manager, release-python-package, document-changes) require prompting the user for confirmations, selections, and approvals. Project-learnings requires user approval before writing.
- **Sub-agent delegation**: feature-dev delegates to code-architect (core-tools) and code-reviewer agents. bug-killer delegates to code-explorer (core-tools) and bug-investigator agents. docs-manager delegates to docs-writer and code-explorer (core-tools) agents. release-python-package delegates to changelog-manager agent.
- **File search**: Search for files by pattern (most components) and search file contents by regex (review, investigation, documentation agents).

## Per-Component Notes

### feature-dev
- **Capabilities needed**: File read/write/edit, shell execution, user interaction, sub-agent delegation, file search, content search
- **Adaptation guidance**: The 7-phase structure can be simplified for smaller features. Agent delegation can be replaced with sequential analysis. Deep-analysis (core-tools) is required for Phase 2 -- replace with your platform's codebase exploration if unavailable. ADR and CHANGELOG artifacts are optional.

### bug-killer
- **Capabilities needed**: File read/write/edit, shell execution, user interaction, sub-agent delegation, file search, content search
- **Adaptation guidance**: Quick/deep track routing can be simplified to always use one track. The hypothesis journal format is the core value -- preserve it. Code-explorer agents need only read access; bug-investigator agents need shell access for tests.

### architecture-patterns
- **Capabilities needed**: None (reference-only)
- **Adaptation guidance**: Passive knowledge skill loaded by feature-dev. Mermaid diagrams use dark text on light backgrounds -- adapt for different rendering environments.

### code-quality
- **Capabilities needed**: None (reference-only)
- **Adaptation guidance**: Passive knowledge skill loaded by feature-dev and bug-killer. Code examples use TypeScript but principles are language-agnostic.

### project-learnings
- **Capabilities needed**: File read/edit, user interaction, file search
- **Adaptation guidance**: Target file detection (CLAUDE.md) is platform-specific -- adapt for .cursorrules, copilot-instructions.md, etc. Always invoked by other skills, never directly.

### changelog-format
- **Capabilities needed**: None (reference-only)
- **Adaptation guidance**: Platform-agnostic Keep a Changelog specification. Used by feature-dev, release-python-package, and changelog-manager.

### docs-manager
- **Capabilities needed**: File read/write/edit, shell execution, user interaction, sub-agent delegation, file search, content search
- **Adaptation guidance**: MkDocs scaffolding uses Material theme -- adapt for other static site generators. Deep-analysis (core-tools) required for Phase 3. Docs-writer agents support both MkDocs and basic Markdown modes.

### release-python-package
- **Capabilities needed**: File read/edit, shell execution, user interaction, sub-agent delegation
- **Adaptation guidance**: Python-specific (uv, ruff, pytest) -- adapt commands for other ecosystems. Steps 8-9 push to main and create tags; ensure this matches your release process.

### document-changes
- **Capabilities needed**: File read/write, shell execution, user interaction
- **Adaptation guidance**: Entirely git-based with no external dependencies. The report template and output path convention are customizable.

### code-reviewer (agent)
- **Capabilities needed**: File read, file search, content search
- **Adaptation guidance**: Read-only agent. Confidence threshold (80+) can be adjusted. Spawned by feature-dev with 3 instances, each with a different focus.

### bug-investigator (agent)
- **Capabilities needed**: File read, shell execution, file search, content search
- **Adaptation guidance**: Investigate-only agent (no writes). Spawned by bug-killer with 1-3 instances. Diagnostic examples show Python/Node.js -- adapt for your stack.

### changelog-manager (agent)
- **Capabilities needed**: File read/edit, shell execution, user interaction, file search, content search
- **Adaptation guidance**: Spawned by release-python-package or used standalone. PR enrichment via gh CLI is optional. Conventional commit categorization table is extensible.

### docs-writer (agent)
- **Capabilities needed**: File read, shell execution (optional), file search, content search
- **Adaptation guidance**: Dual-mode output (MkDocs vs Basic Markdown). Technical-diagrams dependency is for Mermaid styling -- works without it using basic Mermaid.

## Dependency Map

```
Internal Dependencies:
  feature-dev ──> architecture-patterns (Phase 4 design guidance)
  feature-dev ──> code-quality (Phase 6 review guidance)
  feature-dev ──> changelog-format (Phase 7 entry writing)
  feature-dev ──> code-reviewer agent (Phase 6, 3 instances)
  bug-killer ──> code-quality (Phase 4.5 deep track)
  bug-killer ──> project-learnings (Phase 5 knowledge capture)
  bug-killer ──> bug-investigator agent (Phase 3 deep track, 1-3 instances)
  docs-manager ──> docs-writer agent (Phase 5 content generation)
  docs-manager ──> changelog-format (change summary templates)
  release-python-package ──> changelog-manager agent (Step 5)
  changelog-manager agent ──> changelog-format (entry guidelines)

External Dependencies (from core-tools):
  feature-dev ──> deep-analysis (Phase 2 exploration)
  feature-dev ──> language-patterns (Phase 4 design)
  feature-dev ──> technical-diagrams (Phase 4 diagrams)
  feature-dev ──> code-architect agent (Phase 4, 2-3 instances)
  bug-killer ──> code-explorer agent (Phase 2 deep track, 2-3 instances)
  docs-manager ──> deep-analysis (Phase 3 exploration)
  docs-manager ──> code-explorer agent (Phase 3 change summary)
  docs-writer agent ──> technical-diagrams (diagram styling)
```

## External Dependencies

The following components from the **core-tools** package are referenced but not included in this conversion:

| Component | Type | Used By | Purpose |
|-----------|------|---------|---------|
| deep-analysis | Skill | feature-dev, docs-manager | Hub-and-spoke codebase exploration with parallel agents |
| language-patterns | Skill | feature-dev | Language-specific coding patterns and conventions |
| technical-diagrams | Skill | feature-dev, docs-writer | Mermaid diagram styling conventions |
| code-architect | Agent | feature-dev | Designs implementation blueprints for architecture proposals |
| code-explorer | Agent | bug-killer, docs-manager | Read-only codebase exploration agent |

To use the full feature set of dev-tools, convert the core-tools package separately and ensure these components are available.

## Adaptation Checklist

- [ ] Review each skill's Integration Notes section for platform-specific adaptation guidance
- [ ] Configure agent spawning/delegation for your platform (replace parallel agent patterns if not supported)
- [ ] Resolve external dependencies from core-tools (convert separately or substitute with equivalent capabilities)
- [ ] Adapt project-learnings target file detection for your AI platform (CLAUDE.md -> .cursorrules, etc.)
- [ ] Adapt release-python-package commands if not using Python with uv/ruff
- [ ] Test each component individually before testing composed workflows
- [ ] Verify user interaction patterns (prompts, multi-choice, confirmations) work with your platform's UI
- [ ] Check Mermaid diagram rendering in your documentation target (MkDocs, GitHub, etc.)
- [ ] Configure shell execution permissions for agents that need them (bug-investigator, changelog-manager)
- [ ] Validate the hypothesis journal format in bug-killer works with your note-taking/tracking system
