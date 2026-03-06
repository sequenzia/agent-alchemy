# Integration Guide: Unified Export

## Overview

This package combines components from 3 Agent Alchemy plugin groups (core-tools, dev-tools, git-tools) into a single unified export. Together they provide a comprehensive AI-assisted development toolkit covering codebase analysis, feature development, debugging, documentation, code review, and git operations.

## Source Groups

| Group | Original Plugin | Version | Skills | Agents | Hooks |
|-------|----------------|---------|--------|--------|-------|
| core-tools | agent-alchemy-core-tools | 0.2.3 | 5 | 3 | 1 |
| dev-tools | agent-alchemy-dev-tools | 0.3.3 | 9 | 4 | 0 |
| git-tools | agent-alchemy-git-tools | 0.1.0 | 1 | 0 | 0 |

## Component Inventory

| Component | Type | Origin Group | Description |
|-----------|------|-------------|-------------|
| deep-analysis | skill | core-tools | Multi-agent exploration and synthesis workflow |
| codebase-analysis | skill | core-tools | Structured codebase analysis with reports |
| language-patterns | skill | core-tools | TypeScript, Python, React coding patterns |
| project-conventions | skill | core-tools | Project convention discovery and application |
| technical-diagrams | skill | core-tools | Mermaid diagram syntax and styling reference |
| feature-dev | skill | dev-tools | 7-phase feature development workflow |
| bug-killer | skill | dev-tools | Hypothesis-driven debugging workflow |
| architecture-patterns | skill | dev-tools | Architectural pattern knowledge base |
| code-quality | skill | dev-tools | Code quality principles and review checklist |
| project-learnings | skill | dev-tools | Project-specific knowledge capture |
| changelog-format | skill | dev-tools | Keep a Changelog formatting guidelines |
| docs-manager | skill | dev-tools | MkDocs and markdown documentation management |
| release | skill | dev-tools | Python package release workflow |
| document-changes | skill | dev-tools | Git change report generation |
| git-commit | skill | git-tools | Conventional commit automation |
| code-explorer | agent | core-tools | Codebase exploration specialist |
| code-synthesizer | agent | core-tools | Exploration findings synthesizer |
| code-architect | agent | core-tools | Implementation blueprint designer |
| code-reviewer | agent | dev-tools | Code quality reviewer |
| bug-investigator | agent | dev-tools | Hypothesis-testing debugger |
| changelog-manager | agent | dev-tools | Git history changelog updater |
| docs-writer | agent | dev-tools | Documentation content generator |

## Capability Requirements

- **File operations**: Most skills and all agents need to read and search files. Skills that produce output (feature-dev, bug-killer, docs-manager, document-changes) also need file writing.
- **Shell execution**: deep-analysis (via code-synthesizer), bug-killer (via bug-investigator), release, document-changes, git-commit, and changelog-manager require shell command execution.
- **User interaction**: feature-dev, bug-killer, codebase-analysis, docs-manager, release, and project-learnings prompt users for decisions.
- **Sub-agent delegation**: deep-analysis, codebase-analysis, feature-dev, bug-killer, docs-manager, and release spawn child agents. Implement as concurrent tasks if supported, or serialize.
- **Web access**: None required.

## Per-Component Notes

### From core-tools

#### deep-analysis (skill)
The keystone workflow skill. Spawns N code-explorer agents in parallel for codebase investigation, then a single code-synthesizer agent to merge findings. Requires sub-agent delegation. Uses `.agents/sessions/__da_live__/` for session state persistence and recovery. The hook (hooks.yaml) auto-approves file operations to these session directories.

#### codebase-analysis (skill)
Wraps deep-analysis with structured reporting and post-analysis actions. Includes embedded report and actionable-insights templates. Spawns code-architect or code-explorer agents for follow-up investigation of actionable insights. Requires user interaction for selecting post-analysis actions.

#### language-patterns (skill)
Reference skill loaded by other skills and agents. Contains TypeScript, Python, and React coding pattern guidance. No sub-agent delegation or shell access needed. Purely informational — loaded into agent context at runtime.

#### project-conventions (skill)
Reference skill for discovering and applying project-specific conventions. No sub-agent delegation needed. Loaded by code-explorer and code-synthesizer agents to guide their exploration.

#### technical-diagrams (skill)
Reference skill providing Mermaid diagram syntax, styling rules, and quick reference. Loaded by 8 skills/agents across the export. Includes reference files for sequence, class, state, and ER diagrams. No sub-agent delegation needed.

#### code-explorer (agent)
Spawned by deep-analysis to explore a specific focus area. Multiple instances run in parallel. Needs file reading and searching. Originally ran on a balanced-reasoning model.

#### code-synthesizer (agent)
Spawned by deep-analysis to merge explorer findings. One instance runs after explorers complete. Needs file reading, searching, and shell execution (for git history, dependency trees). Originally ran on a high-reasoning model — may benefit from a more capable model.

#### code-architect (agent)
Spawned by feature-dev to design implementation blueprints. Typically 2-3 instances run in parallel with different design approaches. Needs file reading and searching. Originally ran on a high-reasoning model.

### From dev-tools

#### feature-dev (skill)
7-phase feature development workflow. Loads deep-analysis (Phase 2), architecture-patterns + language-patterns + technical-diagrams (Phase 4), code-quality (Phase 6), and changelog-format (Phase 7). Spawns code-architect agents (2-3) for architecture proposals and code-reviewer agents (3) for quality review. Requires user interaction at multiple decision points.

#### bug-killer (skill)
Hypothesis-driven debugging with triage-based routing into quick or deep tracks. Deep track spawns code-explorer agents (2-3) for investigation and bug-investigator agents (1-3) for hypothesis testing. Loads code-quality for fix validation and project-learnings for knowledge capture. Requires user interaction for hypothesis selection.

#### architecture-patterns (skill)
Reference skill containing architectural pattern knowledge (layered, hexagonal, event-driven, etc.). Loaded by feature-dev in Phase 4. No sub-agent delegation needed.

#### code-quality (skill)
Reference skill with SOLID principles, DRY, testing strategies, and code review checklist. Loaded by feature-dev (Phase 6) and bug-killer (deep track fix validation). No sub-agent delegation needed.

#### project-learnings (skill)
Captures project-specific patterns and anti-patterns into project documentation files. Loaded by bug-killer to record debugging discoveries. Requires file writing and user interaction.

#### changelog-format (skill)
Reference skill with Keep a Changelog format guidelines. Loaded by feature-dev in Phase 7 for changelog entry writing. No sub-agent delegation needed.

#### docs-manager (skill)
Documentation management workflow supporting MkDocs sites and standalone markdown. Loads deep-analysis for codebase exploration (Phase 3). Spawns docs-writer agents for content generation. Requires user interaction for documentation planning.

#### release (skill)
Python package release workflow with verification steps. Spawns changelog-manager agent for changelog updates. Requires shell execution (for build/publish commands) and user interaction (for release confirmation).

#### document-changes (skill)
Generates a markdown report documenting codebase changes from the current git session. Requires shell execution (git commands) and file writing.

#### code-reviewer (agent)
Spawned by feature-dev for quality review. Typically 3 instances run in parallel with different review focuses (correctness, security, maintainability). Needs file reading and searching. Originally ran on a high-reasoning model.

#### bug-investigator (agent)
Spawned by bug-killer to test specific debugging hypotheses. Typically 1-3 instances run in parallel. Needs file reading, searching, and shell execution (for diagnostic tests, git history). Originally ran on a balanced-reasoning model.

#### changelog-manager (agent)
Spawned by release workflow to analyze git history and update CHANGELOG.md. Needs file reading, editing, shell execution (git commands), and user interaction (for approving draft entries). Originally ran on a balanced-reasoning model.

#### docs-writer (agent)
Spawned by docs-manager to generate documentation pages. May run multiple instances for different documentation sections. Needs file reading, searching, and shell execution. Originally ran on a high-reasoning model.

### From git-tools

#### git-commit (skill)
Commits staged changes with a conventional commit message. Requires shell execution (git commands). No sub-agent delegation needed. Standalone skill with no internal dependencies.

## Dependency Map

The key dependency chains:

- feature-dev -> deep-analysis -> code-explorer (x N) + code-synthesizer (x 1)
- feature-dev -> code-architect (x 2-3) -> code-reviewer (x 3)
- bug-killer -> code-explorer (x 2-3) + bug-investigator (x 1-3)
- codebase-analysis -> deep-analysis -> code-explorer + code-synthesizer
- docs-manager -> deep-analysis -> code-explorer + code-synthesizer -> docs-writer (x N)

Reference skills (language-patterns, project-conventions, technical-diagrams, architecture-patterns, code-quality, changelog-format) are loaded on demand by the workflow skills and agents listed above.

## Adaptation Checklist

- [ ] Review each skill's instructions and adapt tool-specific language for your harness
- [ ] Configure agent spawning for components that delegate to sub-agents
- [ ] Set up lifecycle hooks if your harness supports them (hooks merged from 1 group)
- [ ] Test each component individually before combining
- [ ] For components that used team orchestration (now decomposed to sequential/parallel steps), test the simplified workflow to ensure it meets needs
