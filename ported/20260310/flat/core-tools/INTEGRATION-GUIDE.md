# Integration Guide: core-tools

## Overview
Core utilities and essential agent capabilities — codebase exploration, analysis, architectural design, and diagram generation. This package provides the foundational skills that other packages (dev-tools, sdd-tools) build upon.

## Component Inventory
| Component | Type | Origin | Description |
|-----------|------|--------|-------------|
| language-patterns | skill | skill | Language-specific patterns for TypeScript, Python, and React |
| project-conventions | skill | skill | Discovery and application of project-specific conventions |
| deep-analysis | skill | skill | Deep exploration and synthesis using parallel agents |
| technical-diagrams | skill | skill | Mermaid diagram syntax, styling rules, and reference material |
| codebase-analysis | skill | skill | Structured codebase analysis with reporting and actionable insights |
| code-explorer | skill | agent | Codebase exploration — file discovery, execution tracing, architecture mapping |
| code-architect | skill | agent | Implementation blueprint design with architectural best practices |
| code-synthesizer | skill | agent | Synthesis of exploration findings with deep investigation |
| lifecycle-hooks | skill | hooks | Auto-approval rules for deep-analysis session file operations |

## Capability Requirements

- **File operations**: `deep-analysis`, `codebase-analysis`, `code-explorer`, `code-architect`, `code-synthesizer` need to read and search files
- **Shell execution**: `deep-analysis`, `code-explorer`, `code-synthesizer` run shell commands (git history, dependency analysis)
- **User interaction**: `deep-analysis`, `codebase-analysis` prompt users for configuration and approval
- **Sub-agent delegation**: `deep-analysis` delegates to multiple parallel explorer agents and a synthesizer; `codebase-analysis` delegates to deep-analysis and may delegate to code-architect/code-explorer for actionable insights

## Per-Component Notes

### language-patterns
A reference skill providing TypeScript, Python, and React coding patterns. No external dependencies. Loaded by code-explorer and code-synthesizer as foundational knowledge.

### project-conventions
A reference skill guiding discovery of project-specific conventions. No external dependencies. Loaded by code-explorer and code-synthesizer.

### deep-analysis
The keystone skill — orchestrates parallel codebase exploration using a hub-and-spoke pattern. Originally assembled a team of Sonnet-model explorers and an Opus-model synthesizer. In the ported version, the team orchestration is described as sequential/parallel workflow steps. The harness should implement concurrent agent delegation if supported. Configurable parameters: cache TTL (default: 24h), checkpointing (default: enabled), progress indicators (default: enabled).

### technical-diagrams
Provides Mermaid diagram syntax and styling conventions. Contains 5 reference files for advanced diagram types (flowcharts, sequence, class, state, ER). The c4-diagrams reference is inlined. Referenced by 8+ components across the ecosystem.

### codebase-analysis
A 3-phase workflow: explore (via deep-analysis), report (structured analysis), and post-analysis actions (save reports, update docs, address insights). Depends on deep-analysis and technical-diagrams.

### code-explorer
Originally a Sonnet-model read-only agent for parallel codebase exploration. Converted to a skill with exploration strategies, search techniques, and structured output format. Depends on project-conventions and language-patterns.

### code-architect
Originally an Opus-model agent for designing implementation blueprints. Provides minimal, flexible, and project-aligned design approaches. Depends on technical-diagrams for architecture visualizations.

### code-synthesizer
Originally an Opus-model agent that merges findings from multiple explorers. Has deep investigation capabilities (git history, dependency analysis). Can ask follow-up questions to explorers and evaluate completeness. Depends on project-conventions, language-patterns, and technical-diagrams.

### lifecycle-hooks
Auto-approval rules for deep-analysis session file operations. The original hook auto-approved Write/Edit/Bash operations targeting `.agents/sessions/` directories. Implement as middleware or skip if your harness doesn't require per-operation approval.

## Dependency Map

```
codebase-analysis
├── deep-analysis
│   ├── (delegates to) code-explorer [x N]
│   │   ├── project-conventions
│   │   └── language-patterns
│   └── (delegates to) code-synthesizer [x 1]
│       ├── project-conventions
│       ├── language-patterns
│       └── technical-diagrams
└── technical-diagrams

code-architect
└── technical-diagrams
```

## Flatten Mode Notes

This package was converted in flatten mode — all components are skills.

### Agent-Converted Skills
- **code-explorer**: Originally a Sonnet-model agent for parallel exploration. Multiple instances were spawned concurrently, each assigned a different focus area.
- **code-architect**: Originally an Opus-model agent for architecture design. Multiple instances spawned with different design approaches (minimal, flexible, project-aligned).
- **code-synthesizer**: Originally an Opus-model agent for merging exploration findings. Single instance with Bash access for deep investigation.

### Lifecycle Hooks Skill
Contains 1 behavioral rule: auto-approve file operations targeting deep-analysis session directories. Originally fired as a `PreToolUse` hook on Write, Edit, and Bash actions.

### Capability Notes
- code-explorer was originally read-only (Read, Glob, Grep, Bash) — no file modification capability
- code-architect was originally read-only (Read, Glob, Grep) — no file modification or shell access
- code-synthesizer had read + Bash access but no file modification capability

## Adaptation Checklist
- [ ] Review each skill's instructions and adapt tool-specific language for your harness
- [ ] Review agent-converted skills for role-appropriate context injection
- [ ] For deep-analysis, implement concurrent agent delegation if your harness supports it (or serialize the exploration steps)
- [ ] Implement lifecycle-hooks rules as middleware, event handlers, or manual checks
- [ ] Test the exploration → synthesis pipeline end-to-end
