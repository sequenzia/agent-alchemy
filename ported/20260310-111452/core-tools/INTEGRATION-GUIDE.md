# Integration Guide: core-tools

## Overview

The core-tools package provides foundational codebase analysis and exploration capabilities for AI agent platforms. It includes a multi-agent deep analysis workflow (hub-and-spoke pattern), structured codebase reporting, language-specific pattern references, project convention discovery, and Mermaid diagram generation guidance.

This is the keystone package in the Agent Alchemy ecosystem. The `deep-analysis` skill is loaded by 3 skills across 2 plugin groups, and `technical-diagrams` is referenced by 8 skills/agents across 4 plugin groups.

## Component Inventory

| Component | Type | Description |
|-----------|------|-------------|
| deep-analysis | Skill | Hub-and-spoke multi-agent exploration and synthesis workflow with dynamic planning, session caching, and checkpointing |
| codebase-analysis | Skill | End-to-end codebase analysis: exploration, structured reporting, and interactive post-analysis actions |
| language-patterns | Skill | Reference catalog of TypeScript, Python, and React patterns and best practices |
| project-conventions | Skill | Systematic process for discovering and applying project-specific conventions |
| technical-diagrams | Skill | Mermaid diagram syntax, styling rules, color palettes, and examples for all supported diagram types |
| code-explorer | Agent | Independent codebase explorer that investigates focus areas and reports structured findings |
| code-architect | Agent | Read-only architect that designs implementation blueprints with diagrams and risk assessment |
| code-synthesizer | Agent | Merges multi-agent exploration findings with shell-based deep investigation and completeness evaluation |

## Capability Requirements

- **File operations**: Read files, search files by name pattern (glob), search file contents (grep). Required by all skills and agents.
- **Shell execution**: Run shell commands (git, npm, pip, cargo, linters). Required by deep-analysis (session management), code-synthesizer (deep investigation), and the auto-approve hook.
- **File writing**: Write and edit files. Required by deep-analysis (session/cache), codebase-analysis (reports, documentation updates).
- **User interaction**: Present choices and collect user input. Required by deep-analysis (approval flow, cache/resume prompts) and codebase-analysis (multi-select actions, file path confirmation).
- **Sub-agent delegation**: Spawn independent worker agents and coordinate via messaging. Required by deep-analysis (explorers + synthesizer) and codebase-analysis (code-architect/code-explorer for actionable insights).
- **Task management**: Create, assign, track, and complete tasks with status (pending/in_progress/completed) and ownership. Required by deep-analysis for the hub-and-spoke coordination pattern.

## Per-Component Notes

### deep-analysis

**What it does:** Orchestrates a multi-agent codebase exploration and synthesis workflow. A lead agent performs reconnaissance, plans focus areas, delegates exploration to independent workers, and coordinates a synthesizer to merge findings.

**Capabilities needed:** File operations, shell execution, sub-agent delegation, task/message coordination, user interaction.

**Adaptation guidance:**
- The hub-and-spoke pattern requires spawning N independent explorer workers + 1 synthesizer. Map to your platform's agent delegation mechanism.
- Task status tracking (pending/in_progress/completed) with ownership is required for duplicate prevention. Implement equivalent coordination if your platform lacks this.
- Session checkpointing writes to `.claude/sessions/` -- adapt the directory path to your platform's session storage.
- The before_action hook auto-approves file writes to session directories. Adapt to your platform's permission model.

**Configurable parameters:**
- `deep-analysis.direct-invocation-approval` (default: `true`)
- `deep-analysis.invocation-by-skill-approval` (default: `false`)
- `deep-analysis.cache-ttl-hours` (default: `24`)
- `deep-analysis.enable-checkpointing` (default: `true`)
- `deep-analysis.enable-progress-indicators` (default: `true`)

### codebase-analysis

**What it does:** Orchestrates end-to-end codebase analysis: runs deep-analysis for exploration, presents a structured report, and offers interactive post-analysis actions including saving reports, updating docs, and addressing actionable insights.

**Capabilities needed:** File operations (read, write, edit, search), shell execution (via deep-analysis), sub-agent delegation, user interaction (multi-select prompts).

**Adaptation guidance:**
- Phase 1 delegates entirely to deep-analysis. Your platform must support that skill's full delegation pattern.
- Phase 3 actionable insights may delegate to code-architect or code-explorer agents. If on-demand agent spawning isn't supported, fall back to direct investigation.
- Multi-select user prompts are used in Steps 1, 2c-1, and 3b. If only single selection is supported, present options sequentially.
- The report template and actionable insights template are embedded in the skill -- no external file references needed.

**Configurable parameters:** None specific. Inherits deep-analysis settings.

### language-patterns

**What it does:** Provides a reference catalog of language-specific patterns and best practices for TypeScript, Python, and React.

**Capabilities needed:** None -- passive reference skill.

**Adaptation guidance:** Use as-is on any platform. Loaded by code-explorer and code-synthesizer agents for pattern recognition context.

### project-conventions

**What it does:** Provides a systematic process for discovering and applying project-specific conventions through configuration file checks, code pattern analysis, and similar feature study.

**Capabilities needed:** File operations (read config files, list directories, search by pattern, search by content).

**Adaptation guidance:** Methodology guide, not an executable workflow. The discovery steps use generic file operations that work on any platform.

### technical-diagrams

**What it does:** Comprehensive Mermaid diagram syntax, styling rules, and examples. The most widely referenced skill -- loaded by 8 skills/agents across 4 plugin groups.

**Capabilities needed:** None -- passive reference skill.

**Adaptation guidance:** Works on any platform that supports Mermaid rendering. The styling rules (especially `color:#000` for dark text) are universal. Reference files for sequence, class, state, and ER diagrams are in `references/` for advanced use cases.

### code-explorer (agent)

**What it does:** Independently explores a designated focus area of a codebase, finding relevant files, tracing execution paths, and reporting structured findings.

**Capabilities needed:** File operations (read-only), shell execution, inter-agent messaging, task status management.

**Adaptation guidance:**
- Spawned by deep-analysis as a worker in the hub-and-spoke topology. Receives a focus area assignment and works independently.
- Read-only file access only -- does not write or modify code.
- Preloads project-conventions and language-patterns for pattern recognition.
- Map inter-agent communication to your platform's messaging mechanism.

### code-architect (agent)

**What it does:** Designs detailed implementation blueprints with file modifications, architecture diagrams, data flow, error handling, and risk assessment.

**Capabilities needed:** File operations (read-only), inter-agent messaging, task status management.

**Adaptation guidance:**
- Read-only agent -- designs but does not implement. Produces a blueprint document.
- Preloads technical-diagrams for Mermaid diagram generation in blueprints.
- Spawned by codebase-analysis for complex actionable insights, or by feature-dev (external) for architecture design.

### code-synthesizer (agent)

**What it does:** Merges exploration findings from multiple code-explorer agents into a unified analysis. Resolves conflicts, fills gaps via shell-based investigation, and evaluates completeness.

**Capabilities needed:** File operations, shell execution, inter-agent messaging, task status management.

**Adaptation guidance:**
- Most capable worker in the deep-analysis team. Needs both read-only file access and shell execution.
- Preloads project-conventions, language-patterns, and technical-diagrams.
- Follow-up questions to explorers require inter-agent messaging. In recovered sessions, self-investigates using shell commands.

## Dependency Map

```
codebase-analysis
  |
  +--> deep-analysis
  |      |
  |      +--> code-explorer (x N, parallel)
  |      |      |
  |      |      +--> project-conventions (preload)
  |      |      +--> language-patterns (preload)
  |      |
  |      +--> code-synthesizer (x 1)
  |             |
  |             +--> project-conventions (preload)
  |             +--> language-patterns (preload)
  |             +--> technical-diagrams (preload)
  |
  +--> technical-diagrams (Phase 2 reporting)
  |
  +--> code-architect (Phase 3 actionable insights, on-demand)
  +--> code-explorer (Phase 3 actionable insights, on-demand)
```

All dependencies are internal to the core-tools package. No external dependencies.

## Adaptation Checklist

- [ ] **Review each skill's instructions** and map platform-specific tool names (file read, file search, shell execution) to the generic terms used in the converted skills
- [ ] **Configure agent spawning** for the deep-analysis hub-and-spoke pattern -- ensure your platform can spawn N independent workers + 1 synthesizer with messaging between them
- [ ] **Set up task management** with status tracking (pending/in_progress/completed) and ownership for the duplicate-prevention status guard
- [ ] **Set up lifecycle hooks** -- adapt the before_action hook to your platform's permission model for auto-approving session directory writes
- [ ] **Configure session storage** -- adapt `.claude/sessions/` paths to your platform's session directory convention
- [ ] **Map user interaction** -- ensure multi-select prompts, approval flows, and file path confirmation work on your platform
- [ ] **Test each component individually** before testing the full codebase-analysis workflow:
  1. Verify language-patterns and project-conventions load correctly as references
  2. Verify technical-diagrams loads and reference files are accessible
  3. Test code-explorer agent in isolation with a simple focus area
  4. Test code-synthesizer agent with mock explorer findings
  5. Test deep-analysis end-to-end with a small codebase
  6. Test codebase-analysis full workflow
- [ ] **Verify hook behavior** -- test that the auto-approve script correctly approves session directory operations and passes through all other operations
- [ ] **Configure settings** -- set up the configuration store for deep-analysis parameters (approval, cache TTL, checkpointing, progress indicators)
