# Integration Guide: core-tools

## Overview

The core-tools package provides foundational capabilities for AI-assisted codebase exploration, analysis, and visualization. It includes a hub-and-spoke deep analysis engine, a structured codebase analysis workflow with actionable insights, language-specific pattern references, project convention discovery, and Mermaid diagram expertise.

## Component Inventory

| Component | Type | Origin | Parent Skill | Description |
|-----------|------|--------|-------------|-------------|
| language-patterns | skill | skill | — | Language-specific patterns for TypeScript, Python, and React |
| project-conventions | skill | skill | — | Discovery and application of project-specific conventions |
| technical-diagrams | skill | skill | — | Mermaid diagram syntax, styling rules, and reference examples |
| deep-analysis | skill | skill | — | Hub-and-spoke codebase exploration and synthesis engine |
| code-explorer | agent | agent | deep-analysis | Independent focus-area codebase explorer |
| code-synthesizer | agent | agent | deep-analysis | Merges exploration findings with deep investigation |
| codebase-analysis | skill | skill | — | Structured 3-phase analysis report with post-analysis actions |
| code-architect | agent | agent | codebase-analysis | Designs implementation blueprints from exploration findings |
| lifecycle-hooks | skill | hooks | — | Auto-approval rules for session file operations |

## Capability Requirements

- **File reading and searching**: language-patterns, project-conventions, technical-diagrams, deep-analysis, codebase-analysis, code-explorer, code-synthesizer, code-architect
- **Shell command execution**: deep-analysis (session management), code-explorer (search), code-synthesizer (git history, dependency trees, static analysis)
- **File writing and editing**: deep-analysis (session files, cache), codebase-analysis (reports, documentation updates)
- **User interaction / prompting**: deep-analysis (plan approval, cache decisions), codebase-analysis (post-analysis actions, documentation drafts)
- **Sub-agent delegation**: deep-analysis (spawns 2-N explorers + 1 synthesizer), codebase-analysis (spawns architect for fix proposals, delegates to deep-analysis for exploration)

## Nested Mode Notes

This package was converted in nested mode — agents are embedded within their parent skills as pure markdown instruction files.

### Nesting Map

| Agent | Parent Skill | Role | Purpose |
|-------|-------------|------|---------|
| code-explorer | deep-analysis | explorer | Independently explores assigned focus areas of a codebase |
| code-synthesizer | deep-analysis | synthesizer | Merges exploration findings, investigates gaps, evaluates completeness |
| code-architect | codebase-analysis | architect | Designs implementation blueprints for features or fixes |

### Reading Nested Agents

Each parent skill's SKILL.md contains a "Nested Agents" section listing its sub-agents with one-line descriptions. The agent files in `agents/` are pure markdown instructions — read them when spawning the corresponding sub-agent. They have no YAML frontmatter.

### Orphan Agents

No orphan agents — all agents are nested under a parent skill.

### Cross-Skill Agent References

- **codebase-analysis** references the **code-explorer** agent from **deep-analysis** (for actionable insight investigation)

### Lifecycle Hooks Skill

The `lifecycle-hooks` skill contains one behavioral rule converted from a `PreToolUse` hook:
- **before_action** (Write|Edit|Bash): Auto-approves file operations targeting deep-analysis session and cache directories. The implementation script is in `skills/lifecycle-hooks/references/auto-approve-da-session.sh`.

## Per-Component Notes

### language-patterns
Pure reference material. No special integration needed — load when implementing features in TypeScript, Python, or React.

### project-conventions
Pure reference material with a discovery process. The bash command examples are illustrative patterns for convention discovery, not executable requirements.

### technical-diagrams
Reference skill for Mermaid diagram creation. Four advanced reference files are in `references/` for complex diagram types (sequence, class, state, ER). Flowchart and C4 references are inlined in the main skill.

### deep-analysis
The most complex skill. It orchestrates a multi-agent exploration workflow:
1. Performs rapid codebase reconnaissance
2. Generates dynamic focus areas
3. Delegates exploration to N independent workers (parallel if supported)
4. Has a synthesizer merge findings with deep investigation
5. Supports session caching, checkpointing, and interrupted session recovery

**Configurable parameters:**
- `cache-ttl-hours` (default: 24) — Hours before exploration cache expires
- `enable-checkpointing` (default: true) — Write session checkpoints at phase boundaries
- `enable-progress-indicators` (default: true) — Display phase progress messages
- `direct-invocation-approval` (default: true) — Require plan approval when invoked directly
- `invocation-by-skill-approval` (default: false) — Require approval when loaded by another skill

### codebase-analysis
Wraps deep-analysis with structured reporting and post-analysis actions (save reports, update documentation, address actionable insights). Can spawn code-architect agents for complex fix proposals.

### lifecycle-hooks
Implements auto-approval for session directory file operations. If the target harness has a lifecycle hook system, wire this to the `before_action` event. Otherwise, the behavior can be implemented as a permission policy or simply grant write access to `.agents/sessions/` directories.

## Dependency Map

```
deep-analysis
├── code-explorer (nested agent, uses: project-conventions, language-patterns)
└── code-synthesizer (nested agent, uses: project-conventions, language-patterns, technical-diagrams)

codebase-analysis
├── deep-analysis (loads for exploration)
├── technical-diagrams (loads for report diagrams)
└── code-architect (nested agent, uses: technical-diagrams)

technical-diagrams
└── references/ (4 separate Mermaid syntax files)

lifecycle-hooks
└── references/ (1 shell script)
```

## Adaptation Checklist

- [ ] Review each skill's instructions and adapt tool-specific language for your harness
- [ ] For skills with nested agents, configure sub-agent spawning to read instructions from the `agents/` directory
- [ ] Check cross-skill agent references (codebase-analysis → deep-analysis/code-explorer) and ensure relative paths work in your harness
- [ ] Implement lifecycle-hooks rules as middleware, event handlers, or permission policies
- [ ] Configure the session directory path (`.agents/sessions/`) for deep-analysis caching and checkpointing
- [ ] Test deep-analysis with a simple codebase first — it's the most complex workflow
- [ ] Test each component individually before combining
