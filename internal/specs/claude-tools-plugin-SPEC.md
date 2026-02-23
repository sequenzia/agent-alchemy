# claude-tools-plugin PRD

**Version**: 1.0
**Author**: Stephen Sequenzia
**Date**: 2026-02-23
**Status**: Draft
**Spec Type**: New feature
**Spec Depth**: Detailed specifications
**Description**: A new plugin for the agent-alchemy project named `claude-tools` that provides reference skills for Claude Code Tasks and Agent Teams features, helping other skills and agents use these features correctly and consistently.

---

## 1. Executive Summary

The `claude-tools` plugin adds two reference skills to the agent-alchemy ecosystem: `cc-tasks` (Claude Code Tasks) and `cc-teams` (Claude Code Agent Teams). These skills serve as shared knowledge bases that other skills and agents load at runtime to ensure correct, consistent usage of Claude Code's task management and multi-agent coordination features. This follows the same composition pattern established by `language-patterns` and `technical-diagrams` in `core-tools`.

## 2. Problem Statement

### 2.1 The Problem

Skills and agents across the agent-alchemy plugin ecosystem interact with Claude Code's Tasks and Agent Teams features in inconsistent, ad-hoc ways. There is no shared reference for correct tool parameters, best-practice patterns, or common pitfalls. Each plugin author must independently discover the correct usage of these features, leading to duplicated effort and inconsistent behavior.

### 2.2 Current State

- Claude Code's Tasks API (TaskCreate, TaskGet, TaskUpdate, TaskList) and Agent Teams features (TeamCreate, SendMessage, etc.) are relatively new and not extensively documented by Anthropic.
- Existing skills like `execute-tasks` (sdd-tools) and `deep-analysis` (core-tools) use these features but embed their own usage patterns directly, with no shared reference.
- New plugin authors have no centralized guide for adopting these features correctly.
- The Tasks and Teams APIs have specific conventions (e.g., imperative subject vs. present-continuous activeForm, DAG dependency management, SendMessage protocol types) that are easy to misuse without guidance.

### 2.3 Impact Analysis

Without a shared reference:
- Each new skill that uses Tasks or Teams must independently research and implement correct patterns, wasting development effort.
- Inconsistent task creation (missing activeForm, poorly structured dependencies, wrong status transitions) leads to degraded UI experience and coordination failures.
- Agent Teams misuse (incorrect shutdown protocols, improper message types, missing idle handling) causes resource leaks and coordination breakdowns.

### 2.4 Business Value

Standardizing Task and Teams usage across all plugins reduces bugs, improves consistency, and lowers the barrier for new skills to adopt these features. This is analogous to how `language-patterns` standardized TypeScript/Python idioms — a small investment in reference material that compounds across every consumer.

## 3. Goals & Success Metrics

### 3.1 Primary Goals
1. Provide a comprehensive, accurate reference for Claude Code Tasks tool usage, patterns, and anti-patterns.
2. Provide a comprehensive, accurate reference for Claude Code Agent Teams lifecycle, messaging, orchestration, and hooks.
3. Enable any skill or agent in the ecosystem to load these references and immediately have access to correct usage patterns.

### 3.2 Success Metrics

| Metric | Current Baseline | Target | Measurement Method |
|--------|------------------|--------|--------------------|
| Reference accuracy | N/A (no reference exists) | 100% of documented tool parameters match actual API | Manual verification against Claude Code system prompts |
| Coverage | 0 reference skills for Tasks/Teams | 2 reference skills with 5 reference files | File count in `claude/claude-tools/` |
| Consumability | N/A | Both skills loadable via `Read` and agent `skills:` frontmatter | Integration test with a consuming skill |

### 3.3 Non-Goals
- Providing user-invocable skills (these are reference skills only)
- Documenting project-specific patterns (e.g., how `execute-tasks` uses wave-based execution)
- Replacing or modifying existing skills that use Tasks/Teams
- Covering Claude Cowork (separate product, different scope)
- Including agents or hooks in v0.1.0

## 4. User Research

### 4.1 Target Users

#### Primary Persona: Plugin Skill Author
- **Role/Description**: A developer (human or AI) writing new skills that need to orchestrate tasks or coordinate agent teams.
- **Goals**: Quickly understand the correct way to use TaskCreate, TaskUpdate, SendMessage, etc. without researching the undocumented API.
- **Pain Points**: No centralized reference; must read system prompts or unofficial docs; easy to miss required fields or conventions.
- **Context**: Loading the reference skill at a specific workflow phase when their skill needs to interact with Tasks or Teams.

#### Secondary Persona: Agent Definition Author
- **Role/Description**: A developer defining new agents (`.md` files with frontmatter) that participate in task-driven or team-based workflows.
- **Goals**: Ensure agents follow correct task claiming, status updating, messaging, and shutdown protocols.
- **Pain Points**: Agent body instructions for task/team behavior are copy-pasted between agents with no canonical source.

### 4.2 User Journey Map

```
[Skill author needs Tasks/Teams] --> [Loads reference skill via Read] --> [Reads relevant section] --> [Optionally loads references/ for deep-dive] --> [Implements correct patterns in their skill]
```

**Agent binding flow**:
```
[Agent author defines new agent] --> [Adds skill to frontmatter skills: list (if same plugin group)] --> [OR adds Read directive in agent body (if cross-plugin)] --> [Agent has correct patterns in context]
```

## 5. Functional Requirements

### 5.1 Feature: cc-tasks Reference Skill

**Priority**: P0 (Critical)

#### User Stories

**US-001**: As a skill author, I want to load a reference that documents all TaskCreate parameters so that I can create well-formed tasks with correct fields.

**Acceptance Criteria**:
- [ ] SKILL.md documents all four Task tools (TaskCreate, TaskGet, TaskUpdate, TaskList) with complete parameter tables
- [ ] Each parameter includes: name, type, required/optional status, and description
- [ ] Status lifecycle (pending → in_progress → completed) is documented with transition rules
- [ ] activeForm convention is documented (imperative subject vs. present-continuous activeForm)
- [ ] Dependency management via blockedBy/blocks is documented with DAG design guidance
- [ ] Metadata usage conventions are described with common key-value patterns (priority, parent, assignee)

**US-002**: As a skill author, I want access to proven task patterns so that I can design effective task structures for my workflows.

**Acceptance Criteria**:
- [ ] `references/task-patterns.md` includes dependency graph design patterns (linear chain, fan-out, fan-in, diamond)
- [ ] Task right-sizing guidance is provided (optimal granularity: 1-3 files per task)
- [ ] Multi-agent coordination patterns via tasks are documented (self-claim workflow, task-per-teammate ratio)
- [ ] Metadata strategies for categorization and tracking are included

**US-003**: As a skill author, I want to know common mistakes to avoid when using Tasks so that I don't introduce subtle bugs.

**Acceptance Criteria**:
- [ ] `references/anti-patterns.md` documents at least 5 common anti-patterns
- [ ] Each anti-pattern includes: description, why it's problematic, and the correct alternative
- [ ] Anti-patterns cover: circular dependencies, too-granular tasks, missing activeForm, batch status updates, duplicate task creation, and TaskList-only consumption without TaskGet

**Edge Cases**:
- Skill loads cc-tasks but doesn't need dependency management: Sections are organized so consumers can skip to relevant parts
- Tasks feature changes in a future Claude Code version: Version metadata in SKILL.md header indicates when content was last verified

---

### 5.2 Feature: cc-teams Reference Skill

**Priority**: P0 (Critical)

#### User Stories

**US-004**: As a skill author, I want a complete reference for Agent Teams lifecycle so that I can properly create, manage, and tear down teams.

**Acceptance Criteria**:
- [ ] SKILL.md documents TeamCreate and TeamDelete tools with complete parameter tables
- [ ] Team lifecycle is documented: creation → member spawning → coordination → shutdown → cleanup
- [ ] Teammate spawning via Task tool with team_name parameter is documented with all spawn parameters
- [ ] Idle state semantics are explained (idle is normal, not an error; idle teammates can receive messages)
- [ ] Environment variables auto-set in teammates are listed (CLAUDE_CODE_TEAM_NAME, CLAUDE_CODE_AGENT_NAME, etc.)
- [ ] Spawn backends are documented (in-process, tmux, iTerm2) with selection guidance
- [ ] File structure is documented (`~/.claude/teams/`, `~/.claude/tasks/`, config.json, inboxes/)

**US-005**: As a skill author, I want to understand the SendMessage protocol so that I can implement correct inter-agent communication.

**Acceptance Criteria**:
- [ ] `references/messaging-protocol.md` documents all 5 message types with field tables
- [ ] message type: recipient, content, summary fields and usage
- [ ] broadcast type: content, summary fields with cost warning (N messages for N members)
- [ ] shutdown_request/shutdown_response types: full lifecycle including request_id handling
- [ ] plan_approval_response type: approve/reject with feedback
- [ ] Peer DM visibility for team leads is documented
- [ ] Automatic message delivery mechanism is explained (not polling-based)

**US-006**: As a skill author, I want access to orchestration pattern templates so that I can design effective multi-agent workflows.

**Acceptance Criteria**:
- [ ] `references/orchestration-patterns.md` includes at least 5 orchestration patterns
- [ ] Each pattern includes: name, description, when to use, team structure, task design, and communication flow
- [ ] Patterns covered: Parallel Specialists, Pipeline with Dependencies, Swarm/Self-Organizing Pool, Research then Implement, Plan Approval Gate
- [ ] Each pattern includes a practical example with pseudocode showing tool calls
- [ ] Pattern selection guidance helps consumers choose the right pattern for their use case

**US-007**: As a skill author, I want to understand how to use hooks for team quality enforcement so that I can build reliable multi-agent workflows.

**Acceptance Criteria**:
- [ ] `references/hooks-integration.md` documents TeammateIdle and TaskCompleted hook events
- [ ] Hook input schemas are documented with field descriptions
- [ ] Exit code behavior is explained (exit 2 = block action with feedback)
- [ ] Practical examples of quality-gate hooks are provided
- [ ] Hook type support matrix is included (command/prompt/agent per event)

**Edge Cases**:
- Consumer needs only messaging, not orchestration: SKILL.md organized with clear sections; references/ files are independently loadable
- Agent Teams feature changes or stabilizes: Version metadata tracks when content was last verified
- Cross-reference to cc-tasks: Optional Read directive provided, not mandatory

---

### 5.3 Feature: Plugin Structure & Marketplace Registration

**Priority**: P0 (Critical)

#### User Stories

**US-008**: As the plugin ecosystem, I want `claude-tools` properly registered and structured so that skills are discoverable and loadable by other plugins.

**Acceptance Criteria**:
- [ ] Plugin directory exists at `claude/claude-tools/` with correct structure
- [ ] Both skills have valid YAML frontmatter with `user-invocable: false` and `disable-model-invocation: false`
- [ ] Marketplace entry added to `claude/.claude-plugin/marketplace.json` with name `agent-alchemy-claude-tools`
- [ ] Cross-plugin load path works: `${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/cc-tasks/SKILL.md`
- [ ] README.md documents the plugin's purpose, skills, and reference files
- [ ] CLAUDE.md Plugin Inventory table updated with new plugin entry

## 6. Non-Functional Requirements

### 6.1 Context Efficiency
- Main SKILL.md files should be under 400 lines each to minimize context cost when loaded
- Reference files should be independently loadable — consumers only pay context cost for what they need
- Self-referential loading instructions in SKILL.md tell consumers how to load references/ files

### 6.2 Accuracy
- All tool parameter documentation must match Claude Code's actual system prompts as of February 2026
- Include a `Last Verified` date in each SKILL.md header for tracking currency
- Flag any information sourced from unofficial documentation as such

### 6.3 Maintainability
- Content organized in clear sections with consistent heading hierarchy
- Reference files are self-contained — updating one doesn't require changes to others
- Version metadata enables easy identification of stale content

## 7. Technical Considerations

### 7.1 Architecture Overview

The plugin follows the **reference skill pattern** established by `language-patterns` and `technical-diagrams` in `core-tools`. Each skill is a markdown file (`SKILL.md`) with YAML frontmatter and a `references/` subdirectory for deep-dive content. Skills are loaded at runtime via `Read` directives or agent frontmatter `skills:` bindings.

### 7.2 Tech Stack
- **Format**: Markdown-as-code (YAML frontmatter + markdown body)
- **Registry**: JSON entry in `marketplace.json`
- **No runtime dependencies**: Pure reference content, no executable code

### 7.3 Integration Points

| System | Integration Type | Purpose |
|--------|-----------------|---------|
| `marketplace.json` | Registry entry | Makes plugin discoverable |
| Agent frontmatter `skills:` | Static binding | Agents in same group can bind these skills |
| `Read ${CLAUDE_PLUGIN_ROOT}/../claude-tools/...` | Runtime loading | Cross-plugin skills load these at specific phases |
| CLAUDE.md | Documentation | Plugin Inventory and Cross-Plugin Dependencies tables |

### 7.4 Technical Constraints
- Agent frontmatter `skills:` bindings are group-local only — agents in other plugin groups must use `Read` in their body to load `claude-tools` skills
- The `disable-model-invocation` field must be `false` for the model to follow the skill's instructions when loaded
- Cross-plugin reference paths use the short directory name (`claude-tools`), never the full marketplace name (`agent-alchemy-claude-tools`)

## 7.5 Codebase Context

### Existing Architecture

The agent-alchemy project uses a markdown-as-code plugin system where skills, agents, and hooks are defined as markdown/JSON files under `claude/`. Six plugin groups currently exist (core-tools, dev-tools, sdd-tools, tdd-tools, git-tools, plugin-tools). Reference skills are a proven pattern — `language-patterns`, `technical-diagrams`, and `project-conventions` in core-tools all use `user-invocable: false` with `disable-model-invocation: false`.

### Integration Points

| File/Module | Purpose | How This Plugin Connects |
|------------|---------|---------------------------|
| `claude/.claude-plugin/marketplace.json` | Central plugin registry | New entry for `agent-alchemy-claude-tools` |
| `claude/core-tools/skills/language-patterns/SKILL.md` | Existing reference skill | Structural template for cc-tasks and cc-teams |
| `claude/core-tools/skills/technical-diagrams/SKILL.md` | Reference skill with `references/` | Pattern for progressive loading with self-referential Read instructions |
| `CLAUDE.md` | Project documentation | Plugin Inventory table needs new row |

### Patterns to Follow
- **Reference skill frontmatter**: `user-invocable: false`, `disable-model-invocation: false` — used in `language-patterns`, `technical-diagrams`, `project-conventions`
- **Self-referential loading**: SKILL.md contains `Read ${CLAUDE_PLUGIN_ROOT}/skills/{name}/references/{file}.md` instructions — used in `technical-diagrams`
- **Phase-gated loading**: Cross-plugin `Read` placed at the specific workflow phase where content is needed — used in `feature-dev`, `tdd-cycle`, `codebase-analysis`
- **Agent body loading for cross-plugin**: `Read ${CLAUDE_PLUGIN_ROOT}/../{plugin-dir}/skills/{name}/SKILL.md` — used in `port-converter`, `tdd-executor`

### Related Features
- **`execute-tasks` (sdd-tools)**: Uses Tasks for wave-based execution; could potentially consume cc-tasks for consistent task creation patterns in future versions
- **`deep-analysis` (core-tools)**: Uses Agent Teams patterns (hub-and-spoke); could consume cc-teams for orchestration reference in future versions

## 8. Scope Definition

### 8.1 In Scope
- `cc-tasks` SKILL.md with complete Claude Code Tasks reference (tool parameters, lifecycle, conventions)
- `cc-tasks` references: `task-patterns.md`, `anti-patterns.md`
- `cc-teams` SKILL.md with complete Agent Teams reference (lifecycle, messaging, configuration, spawning)
- `cc-teams` references: `orchestration-patterns.md`, `messaging-protocol.md`, `hooks-integration.md`
- Plugin structure: `claude/claude-tools/` directory with proper layout
- Marketplace registration in `marketplace.json`
- Plugin README.md
- CLAUDE.md updates (Plugin Inventory table, Repository Structure)

### 8.2 Out of Scope
- **Agents**: No agent definitions in v0.1.0 — pure reference skills only
- **Hooks**: No lifecycle hooks for this plugin
- **Claude Cowork**: Separate product with different API surface; out of scope for this version
- **Project-specific patterns**: Not documenting how existing skills (execute-tasks, deep-analysis) use Tasks/Teams internally
- **Migration guides**: Not providing guidance on migrating existing skills to use these reference skills
- **User-invocable skills**: Both skills are reference-only, not directly callable by users

### 8.3 Future Considerations
- **Claude Cowork skill**: A third reference skill covering Claude Cowork could be added in a future version
- **Helper agent**: A diagnostic agent that validates team/task configurations could be added if demand exists
- **Hooks for quality gates**: The plugin could include example hook configurations for TeammateIdle and TaskCompleted enforcement
- **Integration with existing skills**: Future versions of `execute-tasks`, `deep-analysis`, and `feature-dev` could load these reference skills for consistency
- **Auto-update mechanism**: A script or skill that fetches latest Claude Code system prompts to verify reference accuracy

## 9. Implementation Plan

### 9.1 Phase 1: Plugin Foundation & Both Skills
**Completion Criteria**: Both skills are created, reference files are populated, plugin is registered, and CLAUDE.md is updated.

| Deliverable | Description | Dependencies |
|-------------|-------------|--------------|
| Plugin directory structure | Create `claude/claude-tools/` with `skills/cc-tasks/`, `skills/cc-teams/`, and their `references/` subdirectories | None |
| `cc-tasks/SKILL.md` | Main reference skill with tool parameter tables, status lifecycle, dependency management, metadata conventions, activeForm guidance | Research findings on Tasks API |
| `cc-tasks/references/task-patterns.md` | Dependency graph patterns, right-sizing guidance, multi-agent coordination, metadata strategies | cc-tasks SKILL.md |
| `cc-tasks/references/anti-patterns.md` | Common mistakes with descriptions, explanations, and correct alternatives | cc-tasks SKILL.md |
| `cc-teams/SKILL.md` | Main reference skill with TeamCreate/Delete, lifecycle, spawning, idle semantics, env vars, spawn backends, file structure | Research findings on Agent Teams |
| `cc-teams/references/orchestration-patterns.md` | 5+ orchestration pattern templates with examples and selection guidance | cc-teams SKILL.md |
| `cc-teams/references/messaging-protocol.md` | All 5 SendMessage types with field tables, usage guidance, and examples | cc-teams SKILL.md |
| `cc-teams/references/hooks-integration.md` | TeammateIdle and TaskCompleted hooks with schemas, exit codes, and examples | cc-teams SKILL.md |
| `marketplace.json` entry | Add `agent-alchemy-claude-tools` to the marketplace registry | Plugin directory structure |
| `README.md` | Plugin overview documenting purpose, skills, and reference files | All skills complete |
| CLAUDE.md updates | Update Plugin Inventory table, Repository Structure section | All skills complete |

**Checkpoint Gate**: Review SKILL.md files for accuracy against Claude Code system prompts. Verify cross-plugin load paths resolve correctly. Confirm marketplace registration is valid.

## 10. Dependencies

### 10.1 Technical Dependencies

| Dependency | Owner | Status | Risk if Delayed |
|------------|-------|--------|-----------------|
| Claude Code Tasks API documentation | Anthropic | Available (system prompts + unofficial docs) | Low — research already completed |
| Claude Code Agent Teams API documentation | Anthropic | Available (system prompts + unofficial docs) | Low — research already completed |
| Agent-alchemy plugin system conventions | Project maintainer | Stable | None — well-established patterns |

### 10.2 Information Dependencies

| Source | Content | Status |
|--------|---------|--------|
| Claude Code system prompts (TaskCreate, TaskUpdate, etc.) | Authoritative tool parameter specs | Gathered via research agents |
| `shcv/claude-investigations` repo | Unofficial feature documentation | Gathered; accuracy needs verification |
| Anthropic official docs (`code.claude.com/docs`) | Agent Teams official docs | Gathered via research agents |
| Existing agent-alchemy reference skills | Structural patterns to follow | Gathered via codebase exploration |

## 11. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation Strategy |
|------|--------|------------|---------------------|
| API instability — Tasks/Teams features change in future Claude Code versions | High | Medium | Include `Last Verified` date in each SKILL.md; design content for easy section-level updates; monitor Claude Code changelogs |
| Inaccurate research findings — unofficial docs may contain errors | Medium | Low | Cross-reference multiple sources; verify against Claude Code system prompts (most authoritative source); flag uncertain information |
| Low adoption — other plugin authors don't know to load these skills | Medium | Medium | Document in CLAUDE.md; update Cross-Plugin Dependencies section; reference in plugin development guides |
| Context bloat — loading both skills + references consumes too much context | Medium | Low | Progressive loading via `references/` subdirectories; main SKILL.md kept under 400 lines; consumers only load what they need |
| Naming collision — `cc-tasks` or `cc-teams` conflicts with future Claude Code features | Low | Low | Prefix with `cc-` is distinctive; if collision occurs, rename with clear migration path |

## 12. Open Questions

| # | Question | Owner | Resolution |
|---|----------|-------|------------|
| 1 | Should the `disable-model-invocation` field be `false` (model can auto-load) or `true` (explicit load only)? | Spec author | Set to `false` to match existing reference skills (`language-patterns`, `technical-diagrams`) — allows model to recognize and follow instructions when loaded |
| 2 | As Agent Teams stabilizes and exits experimental status, should the skill content be restructured? | Plugin maintainer | Monitor Anthropic releases; update content incrementally as APIs stabilize |

## 13. Appendix

### 13.1 Glossary

| Term | Definition |
|------|------------|
| Reference skill | A non-user-invocable skill (`user-invocable: false`) designed to be loaded by other skills and agents as a shared knowledge base |
| Progressive loading | Pattern where the main SKILL.md contains essentials and a `references/` subdirectory holds deep-dive files loaded on demand |
| Phase-gated loading | Placing `Read` directives at the specific workflow phase where content is needed, rather than loading everything upfront |
| DAG | Directed Acyclic Graph — the dependency structure used by Tasks (blockedBy/blocks) to determine execution order |
| Idle state | Normal state for a teammate between turns; does not indicate error or completion |
| Self-referential loading | A skill containing `Read` instructions pointing to its own `references/` files, teaching consumers how to load deeper content |

### 13.2 Directory Structure

```
claude/claude-tools/
├── skills/
│   ├── cc-tasks/
│   │   ├── SKILL.md                    # Tasks tool reference, patterns, conventions
│   │   └── references/
│   │       ├── task-patterns.md        # Dependency design, right-sizing, metadata
│   │       └── anti-patterns.md        # Common mistakes and correct alternatives
│   └── cc-teams/
│       ├── SKILL.md                    # Teams lifecycle, spawning, config, file structure
│       └── references/
│           ├── orchestration-patterns.md  # 5+ pattern templates with examples
│           ├── messaging-protocol.md      # SendMessage types and conventions
│           └── hooks-integration.md       # TeammateIdle/TaskCompleted hooks
└── README.md                           # Plugin overview
```

### 13.3 Research Sources

**Claude Code Tasks**:
- [Anthropic Official Docs: Agent Teams](https://code.claude.com/docs/en/agent-teams)
- [Anthropic Official Docs: Interactive Mode (Task List UI)](https://code.claude.com/docs/en/interactive-mode)
- [Claude Code System Prompts: TaskCreate Tool Description](https://github.com/Piebald-AI/claude-code-system-prompts)
- [shcv/claude-investigations: Task Management](https://github.com/shcv/claude-investigations/blob/main/features/task-management.org)
- [dplooy: Claude Code Tasks Complete Guide](https://www.dplooy.com/blog/claude-code-tasks-complete-guide-to-ai-agent-workflow)

**Claude Code Agent Teams**:
- [Orchestrate teams of Claude Code sessions - Official Docs](https://code.claude.com/docs/en/agent-teams)
- [Hooks reference - Official Docs](https://code.claude.com/docs/en/hooks)
- [shcv/claude-investigations: Agent Teams](https://github.com/shcv/claude-investigations/blob/main/features/agent-teams.org)
- [shcv/claude-investigations: Agent Mailbox](https://github.com/shcv/claude-investigations/blob/main/features/agent-mailbox.org)
- [Claude Code Agent Teams: The Complete Guide 2026](https://claudefa.st/blog/guide/agents/agent-teams)

### 13.4 Marketplace Entry

```json
{
  "name": "agent-alchemy-claude-tools",
  "version": "0.1.0",
  "description": "Reference skills for Claude Code Tasks and Agent Teams features",
  "source": "./claude-tools",
  "homepage": "https://github.com/sequenzia/agent-alchemy/tree/main/claude/claude-tools",
  "repository": "https://github.com/sequenzia/agent-alchemy/tree/main/claude/claude-tools",
  "license": "MIT"
}
```

---

*Document generated by SDD Tools*
