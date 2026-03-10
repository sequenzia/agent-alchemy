# Core Tools Integration Guide

This guide describes how to integrate the core-tools plugin components into a host platform. All components have been converted to platform-agnostic format using **nested mode**, where agents are co-located with their parent skills.

---

## Component Inventory

| Component | Type | Origin | Parent Skill | Description |
|-----------|------|--------|-------------|-------------|
| language-patterns | Skill | skill | — | Language-specific patterns for TypeScript, Python, and React |
| project-conventions | Skill | skill | — | Project-specific convention discovery and application |
| technical-diagrams | Skill | skill | — | Mermaid diagram syntax, styling rules, and best practices |
| deep-analysis | Skill | skill | — | Deep exploration and synthesis workflow with hub-and-spoke coordination |
| code-explorer | Agent | agent | deep-analysis | Explores codebases to find relevant files, trace execution paths, and map architecture |
| code-synthesizer | Agent | agent | deep-analysis | Synthesizes exploration findings into unified analysis with deep investigation |
| codebase-analysis | Skill | skill | — | Structured codebase analysis report with architecture overview and recommendations |
| code-architect | Agent | agent | codebase-analysis | Designs implementation blueprints for features |
| lifecycle-hooks | Skill | hooks | — | Behavioral rules and lifecycle event handlers (converted from hooks) |
| flowcharts | Reference | reference | technical-diagrams | Flowchart diagram syntax and examples |
| sequence-diagrams | Reference | reference | technical-diagrams | Sequence diagram syntax and examples |
| class-diagrams | Reference | reference | technical-diagrams | Class diagram syntax and examples |
| state-diagrams | Reference | reference | technical-diagrams | State diagram syntax and examples |
| er-diagrams | Reference | reference | technical-diagrams | ER diagram syntax and examples |
| c4-diagrams | Reference | reference | technical-diagrams | C4 architecture diagram syntax and examples |
| auto-approve-da-session | Reference | hooks | lifecycle-hooks | Shell script for auto-approving session file operations |

---

## Capability Requirements

### File System

| Capability | Used By | Description |
|-----------|---------|-------------|
| File reading | All skills and agents | Read file contents by path |
| File search (pattern) | deep-analysis, code-explorer, code-synthesizer, codebase-analysis | Find files matching glob patterns |
| Content search | deep-analysis, code-explorer, code-synthesizer, codebase-analysis | Search file contents with regex |
| File writing | deep-analysis, codebase-analysis | Write files (reports, session data, cache) |
| File editing | codebase-analysis | Edit existing files (documentation updates) |
| Directory listing | deep-analysis, project-conventions | List directory contents |

### Shell / Command Execution

| Capability | Used By | Description |
|-----------|---------|-------------|
| Shell commands | deep-analysis, code-explorer, code-synthesizer | Run git, dependency tools, linters |
| Git operations | code-synthesizer | git blame, git log, git diff for history analysis |
| Package managers | code-synthesizer | npm ls, pip show, cargo tree for dependency analysis |

### Agent Coordination

| Capability | Used By | Description |
|-----------|---------|-------------|
| Agent/team creation | deep-analysis | Create named teams and spawn agents |
| Task creation | deep-analysis | Create tasks with dependencies (blocked-by) |
| Task assignment | deep-analysis | Assign tasks to specific agents |
| Task status tracking | deep-analysis, code-explorer, code-synthesizer | Check/update task status |
| Inter-agent messaging | deep-analysis, code-explorer, code-synthesizer, code-architect | Send messages between agents |
| Agent shutdown | deep-analysis | Terminate spawned agents |

### User Interaction

| Capability | Used By | Description |
|-----------|---------|-------------|
| User prompting | deep-analysis, codebase-analysis | Ask users questions with selectable options |
| Multi-select prompting | codebase-analysis | Present multiple options for simultaneous selection |

### Lifecycle / Hooks

| Capability | Used By | Description |
|-----------|---------|-------------|
| Pre-action interceptor | lifecycle-hooks | Inspect file operations before execution and auto-approve |

---

## Nesting Map

| Agent | Nested Under | File Path |
|-------|-------------|-----------|
| code-explorer | deep-analysis | `skills/deep-analysis/agents/code-explorer.md` |
| code-synthesizer | deep-analysis | `skills/deep-analysis/agents/code-synthesizer.md` |
| code-architect | codebase-analysis | `skills/codebase-analysis/agents/code-architect.md` |

---

## Dependency Graph

```
codebase-analysis
├── deep-analysis (loaded for exploration)
│   ├── code-explorer (N instances)
│   │   ├── project-conventions (knowledge)
│   │   └── language-patterns (knowledge)
│   └── code-synthesizer (1 instance)
│       ├── project-conventions (knowledge)
│       ├── language-patterns (knowledge)
│       └── technical-diagrams (knowledge)
├── technical-diagrams (loaded for report diagrams)
│   └── references/ (6 diagram type files)
└── code-architect (launched on-demand)
    └── technical-diagrams (knowledge)

lifecycle-hooks (standalone, no dependencies)
```

---

## Skill Loading Patterns

### Knowledge Skills (Passive)
**language-patterns**, **project-conventions**, **technical-diagrams**: These are loaded by agents as knowledge references. They contain no orchestration logic and require only file reading capability (for reference file loading in the case of technical-diagrams).

### Orchestration Skills (Active)
**deep-analysis**: Full agent team orchestration with 6 phases. Requires agent creation, task management, messaging, and session management.

**codebase-analysis**: 3-phase workflow that delegates exploration to deep-analysis and adds reporting + interactive post-analysis actions.

### Lifecycle Skills (Event-Driven)
**lifecycle-hooks**: Defines pre-action interceptors. Requires a hook/middleware system on the host platform.

---

## Configuration Parameters

All configurable parameters are read from a settings file. The following parameters are available:

| Parameter | Default | Scope | Description |
|-----------|---------|-------|-------------|
| `deep-analysis.direct-invocation-approval` | `true` | deep-analysis | Require plan approval on direct invocation |
| `deep-analysis.invocation-by-skill-approval` | `false` | deep-analysis | Require plan approval when loaded by another skill |
| `deep-analysis.cache-ttl-hours` | `24` | deep-analysis | Hours before exploration cache expires; 0 disables |
| `deep-analysis.enable-checkpointing` | `true` | deep-analysis | Write session checkpoints at phase boundaries |
| `deep-analysis.enable-progress-indicators` | `true` | deep-analysis | Display progress messages during execution |

---

## Session Directory Layout

Deep-analysis creates and manages session directories under `.agents/sessions/`:

```
.agents/sessions/
├── __da_live__/               # Active session (one at a time)
│   ├── checkpoint.md          # Phase progress and recovery state
│   ├── progress.md            # Human-readable progress log
│   ├── team_plan.md           # Approved team plan
│   ├── recon_summary.md       # Reconnaissance findings
│   ├── explorer-{N}-findings.md  # Per-explorer results
│   └── synthesis.md           # Synthesizer output
├── exploration-cache/          # Cached results (reused across runs)
│   ├── manifest.md            # Cache metadata and validity
│   ├── synthesis.md           # Cached synthesis
│   ├── recon_summary.md       # Cached reconnaissance
│   └── explorer-{N}-findings.md  # Cached explorer findings
└── da-{timestamp}/            # Archived completed sessions
```

---

## Adaptation Checklist

### Minimum Viable Integration
- [ ] File reading, searching (pattern + content), and writing
- [ ] Shell command execution
- [ ] User prompting with option selection
- [ ] Load knowledge skills as context for agents

### Full Integration
- [ ] Agent team creation and lifecycle management
- [ ] Task creation with dependency tracking (blocked-by)
- [ ] Task assignment and status monitoring
- [ ] Inter-agent messaging (hub-and-spoke pattern)
- [ ] Multi-select user prompting
- [ ] Pre-action hook/interceptor system
- [ ] Session directory management (create, archive, cache)
- [ ] Checkpoint-based session recovery

### Knowledge-Only Integration
If the host platform does not support multi-agent orchestration, the knowledge skills can still be used independently:
- [ ] **language-patterns** — Load as context for any code generation task
- [ ] **project-conventions** — Load as context for any codebase exploration
- [ ] **technical-diagrams** — Load as context for any diagram generation task

---

## Source Information

| Field | Value |
|-------|-------|
| Source platform | Claude Code |
| Source plugin | agent-alchemy-core-tools |
| Source version | 0.2.3 |
| Conversion date | 2026-03-10 |
| Conversion mode | Nested |
