# Integration Guide: core-tools

## Overview

The core-tools package provides foundational AI agent capabilities: deep codebase exploration with multi-agent coordination, structured analysis reporting, Mermaid diagram generation, language-specific coding patterns, and project convention discovery. It serves as the backbone for higher-level workflows in other packages (dev-tools, sdd-tools).

## Component Inventory

| Component | Type | Origin | Description |
|-----------|------|--------|-------------|
| deep-analysis | skill | skill | Hub-and-spoke exploration workflow — coordinates parallel explorers and a synthesizer |
| codebase-analysis | skill | skill | Structured 3-phase analysis report with post-analysis actions |
| technical-diagrams | skill | skill | Mermaid diagram syntax, styling rules, and reference examples |
| language-patterns | skill | skill | TypeScript, Python, React patterns and best practices |
| project-conventions | skill | skill | Convention discovery and application guide |
| code-explorer | skill | agent | Codebase exploration specialist for focus-area investigation |
| code-architect | skill | agent | Architecture blueprint designer for feature implementations |
| code-synthesizer | skill | agent | Merges exploration findings into unified analysis with deep investigation |
| lifecycle-hooks | skill | hooks | Auto-approval rules for session file operations |

## Capability Requirements

### File operations
- **deep-analysis**, **codebase-analysis**, **code-explorer**, **code-architect**, **code-synthesizer**: Need to read files, search by pattern (glob), and search content (grep)
- **codebase-analysis**: Also needs file writing for report generation

### Shell execution
- **deep-analysis**: Needs shell access for timestamp generation and directory management
- **code-synthesizer**: Needs shell access for git history analysis, dependency trees, and static analysis
- **code-explorer**: Needs shell access for supplementary investigation

### User interaction
- **deep-analysis**: Prompts for team plan approval, cache decisions, session recovery
- **codebase-analysis**: Prompts for post-analysis actions, report location, actionable insights

### Sub-agent delegation
- **deep-analysis**: Delegates to 2-4 explorer workers + 1 synthesizer (parallel exploration, sequential synthesis)
- **codebase-analysis**: Delegates to deep-analysis, plus optional architect/explorer for actionable insights

### Lifecycle hooks
- **lifecycle-hooks**: Auto-approves file operations targeting session directories — implement as middleware or event handler

## Per-Component Notes

### deep-analysis
The keystone orchestration skill. Coordinates parallel exploration workers and a synthesizer in a hub-and-spoke pattern. The original used Agent Teams with TeamCreate/SendMessage — adapt to your harness's agent coordination mechanism. Supports caching of exploration results, session checkpointing, and interrupted session recovery. Configurable parameters: cache TTL (default 24h), checkpointing (default on), progress indicators (default on).

### codebase-analysis
Wraps deep-analysis with structured reporting and post-analysis actions. The report template and actionable insights template are inlined in the skill body. Uses Mermaid diagrams (via technical-diagrams) for architecture visualization in reports.

### technical-diagrams
Pure reference material — no orchestration or tool use. Provides Mermaid syntax, styling rules (critical: always use dark text `color:#000`), and diagram type references. Four advanced reference files are in `references/` for complex diagram types.

### language-patterns / project-conventions
Pure reference skills with no dependencies or tool requirements. Loaded by other skills and agents as knowledge prerequisites.

### code-explorer / code-architect / code-synthesizer
Originally sub-agents spawned by deep-analysis and feature-dev. Each has structured output formats and team communication patterns that have been converted to workflow prose. The synthesizer is the most capable — it can investigate using shell commands (git history, dependency analysis).

### lifecycle-hooks
Contains one rule: auto-approve file operations targeting session directories. The original shell script is in `references/auto-approve-da-session.sh`. If your harness has a permission/approval system, configure it to auto-approve operations on `.agents/sessions/` paths.

## Dependency Map

```
codebase-analysis
├── deep-analysis (exploration engine)
│   ├── code-explorer × N (parallel workers)
│   │   ├── project-conventions (knowledge)
│   │   └── language-patterns (knowledge)
│   └── code-synthesizer × 1 (merges findings)
│       ├── project-conventions (knowledge)
│       ├── language-patterns (knowledge)
│       └── technical-diagrams (knowledge)
└── technical-diagrams (report diagrams)

code-architect
└── technical-diagrams (blueprint diagrams)

lifecycle-hooks (standalone)
```

## Flatten Mode Notes

This package was converted in flatten mode — all components are skills.

### Agent-Converted Skills
- **code-explorer** — Originally a Sonnet-tier exploration agent with read-only file access plus shell. Spawned in parallel (2-4 instances) by deep-analysis.
- **code-architect** — Originally an Opus-tier architecture agent with read-only access. Spawned by feature-dev for blueprint design.
- **code-synthesizer** — Originally an Opus-tier synthesis agent with shell access for git/dependency investigation. Single instance per analysis run.

### Lifecycle Hooks Skill
Contains 1 behavioral rule (before_action) that auto-approves file operations targeting `.agents/sessions/` directories. Originally enforced via a shell script hook on the PreToolUse event.

### Capability Notes
- code-explorer and code-architect were read-only agents (no file modification) — consumers should scope capabilities accordingly
- code-synthesizer had shell access for deep investigation (git blame, dependency trees) — broader capability than explorers

## Adaptation Checklist
- [ ] Review each skill's instructions and adapt tool-specific language for your harness
- [ ] Review agent-converted skills for role-appropriate context injection
- [ ] Implement lifecycle-hooks rules as middleware, event handlers, or manual checks
- [ ] Configure session directory paths (`.agents/sessions/`) for your environment
- [ ] Test deep-analysis workflow end-to-end: reconnaissance → exploration → synthesis
- [ ] Test each component individually before combining
