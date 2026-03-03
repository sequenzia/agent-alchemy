# Integration Guide: core-tools

## Overview

Core-tools provides a multi-agent codebase analysis system with reusable building blocks. The centerpiece is a hub-and-spoke exploration workflow where independent explorer agents investigate different parts of a codebase in parallel, and a synthesizer agent merges their findings into a unified analysis. Supporting skills provide language patterns, project convention discovery, and Mermaid diagram guidance.

## Component Inventory

| Component | Type | Description |
|-----------|------|-------------|
| deep-analysis | skill | Multi-agent exploration + synthesis with dynamic planning |
| codebase-analysis | skill | Full codebase analysis workflow with reporting and follow-up actions |
| language-patterns | skill | TypeScript, Python, React patterns and best practices |
| project-conventions | skill | Guide for discovering and applying project conventions |
| technical-diagrams | skill | Mermaid diagram syntax, styling, and examples |
| code-explorer | agent | Independent codebase exploration worker |
| code-synthesizer | agent | Finding merger with shell-command investigation |
| code-architect | agent | Implementation blueprint designer |
| before_action hook | hook | Auto-approve session file operations |

## Capability Requirements

### File operations
- **All components** need file reading and searching (Glob, Grep, Read equivalent)
- **codebase-analysis** needs file writing (for saving reports and documentation updates)
- **deep-analysis** needs file writing (for session checkpoints and cache)

### Shell execution
- **deep-analysis** needs shell commands for reconnaissance
- **code-synthesizer** needs shell commands for git history, dependency analysis, static analysis
- **project-conventions** uses shell command examples illustratively (not required at runtime)
- The **before_action hook** script (`auto-approve-session.sh`) requires `bash` and `jq`

### User interaction
- **deep-analysis** prompts the user for plan approval, cache decisions, and error recovery
- **codebase-analysis** prompts for action selection, file paths, documentation review, and insight processing
- **language-patterns**, **project-conventions**, **technical-diagrams** do not prompt the user

### Sub-agent delegation
- **deep-analysis** spawns N code-explorer agents + 1 code-synthesizer agent
- **codebase-analysis** spawns code-architect and code-explorer agents during actionable insight processing
- **code-explorer**, **code-synthesizer**, **code-architect** are leaf agents (they don't spawn sub-agents)

### Web access
- No components require web access

## Per-Component Notes

### deep-analysis
- The keystone skill — loaded by codebase-analysis and potentially by other workflows (feature development, documentation generation)
- Hub-and-spoke pattern: lead does reconnaissance, spawns N parallel explorers, then 1 synthesizer
- Session checkpointing and caching are optional — disable both for simplicity in initial integration
- The approval flow can be bypassed by setting `approval-required: false`
- Uses balanced-tier models for explorers and high-reasoning for synthesis — adapt to your model strategy

### codebase-analysis
- Composes deep-analysis for exploration, then adds reporting + interactive follow-up
- The report template and actionable insights template are embedded directly in the skill
- Phase 3 (Post-Analysis Actions) requires multiple rounds of user interaction
- Agent delegation in the actionable insights step is optional — direct investigation works as fallback

### language-patterns
- Passive knowledge reference — no runtime capabilities needed
- Loaded by code-explorer and code-synthesizer as context
- Contains TypeScript, Python, and React patterns with code examples

### project-conventions
- Passive knowledge reference with illustrative shell command examples
- Loaded by code-explorer and code-synthesizer as context
- Guides convention discovery through config files, code patterns, and similar features

### technical-diagrams
- Passive knowledge reference for Mermaid diagram syntax
- Loaded by codebase-analysis, code-synthesizer, and code-architect
- Includes inline flowchart and C4 references; separate files for sequence, class, state, and ER diagrams
- The critical styling rule (always `color:#000` on nodes) should be enforced across all diagram output

### code-explorer
- Independent exploration worker — spawned multiple times in parallel
- Communicates via hub-and-spoke messaging (reports to lead, responds to synthesizer)
- Read-only plus shell commands — does not write files

### code-synthesizer
- Runs after all explorers complete — synthesis depends on exploration findings
- Can ask explorers follow-up questions if inter-agent messaging is supported
- Has shell command access for git history, dependency trees, and static analysis
- Produces Mermaid architecture diagrams in output

### code-architect
- Read-only agent — designs but does not implement
- Produces implementation blueprints with file change plans, diagrams, and risk analysis
- Used by codebase-analysis for complex actionable insights and by feature-dev workflows

### before_action hook
- Bash script that reads JSON from stdin and approves operations targeting session directories
- Requires `jq` for JSON parsing
- Exits 0 with no output for non-matching operations (passes through to normal permission flow)
- Adapt the JSON input format to match your harness's hook protocol

## Dependency Map

```
codebase-analysis
├── deep-analysis
│   ├── code-explorer (×N, parallel)
│   │   ├── project-conventions (knowledge)
│   │   └── language-patterns (knowledge)
│   └── code-synthesizer (×1)
│       ├── project-conventions (knowledge)
│       ├── language-patterns (knowledge)
│       └── technical-diagrams (knowledge)
├── technical-diagrams (knowledge)
│   ├── references/sequence-diagrams.md
│   ├── references/class-diagrams.md
│   ├── references/state-diagrams.md
│   └── references/er-diagrams.md
├── code-explorer (for actionable insights)
└── code-architect (for actionable insights)
    └── technical-diagrams (knowledge)
```

## Adaptation Checklist

- [ ] Review each skill's instructions and adapt tool-specific language for your harness
- [ ] Configure agent spawning for deep-analysis (N explorers + 1 synthesizer)
- [ ] Implement inter-agent messaging (hub-and-spoke: lead ↔ workers, synthesizer ↔ workers)
- [ ] Set up task tracking for exploration and synthesis tasks with dependency support
- [ ] Configure the before_action hook if your harness supports lifecycle hooks
- [ ] Ensure `jq` is available for the hook script (or rewrite in your harness's hook format)
- [ ] Test each component individually before combining:
  1. Start with language-patterns, project-conventions, technical-diagrams (passive, no dependencies)
  2. Then code-explorer (single agent, needs file operations)
  3. Then code-synthesizer (needs shell commands + messaging)
  4. Then deep-analysis (full orchestration)
  5. Finally codebase-analysis (composes everything)
- [ ] Configure model tiers: balanced for explorers, high-reasoning for synthesizer and architect
