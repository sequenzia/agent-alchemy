# Agent Alchemy Claude Tools

Shared reference skills for Claude Code Tasks and Agent Teams features, enabling consistent usage across the agent-alchemy ecosystem.

**Version**: 0.2.0

## Purpose

The `claude-tools` plugin provides reference skills for Claude Code's Tasks and Agent Teams features. Other skills and agents load the reference skills at runtime to ensure correct, consistent usage of task management and multi-agent coordination APIs. This follows the same composition pattern established by `language-patterns` and `technical-diagrams` in `core-tools`.

## Skills

| Skill | Description | Type |
|-------|-------------|------|
| `claude-code-tasks` | Claude Code Tasks tool reference | Reference (non-user-invocable) |
| `claude-code-teams` | Claude Code Agent Teams reference | Reference (non-user-invocable) |

## claude-code-tasks

Reference for Claude Code Tasks — tool parameters, status lifecycle, dependency management, and conventions.

### What It Covers

- **Tool Parameters** — TaskCreate, TaskGet, TaskUpdate, TaskList field tables with types, defaults, and usage notes
- **Status Lifecycle** — Valid transitions between pending, in_progress, and completed states
- **Dependency Management** — DAG-based blockedBy/blocks relationships, topological ordering, circular dependency prevention
- **Metadata Conventions** — Structured metadata fields (priority, complexity, spec_path, feature_name, task_group) with naming standards

### Reference Files

| File | Description |
|------|-------------|
| `task-patterns.md` | Dependency graph patterns, task right-sizing, multi-agent coordination, metadata strategies |
| `anti-patterns.md` | Common mistakes with descriptions, explanations, and correct alternatives |

### How to Load

```
Read ${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/claude-code-tasks/SKILL.md
```

The SKILL.md provides progressive loading — reference files are loaded on demand via:

```
Read ${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/claude-code-tasks/references/task-patterns.md
Read ${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/claude-code-tasks/references/anti-patterns.md
```

## claude-code-teams

Reference for Claude Code Agent Teams — lifecycle, messaging, spawning, orchestration, and hooks.

### What It Covers

- **TeamCreate / TeamDelete** — Team creation parameters and teardown protocol
- **Team Lifecycle** — States from creation through active coordination to graceful shutdown
- **Teammate Spawning** — How teammates are added, spawn backends, and task assignment
- **Idle Semantics** — TeammateIdle event handling and idle-state coordination
- **SendMessage Protocol** — All 5 message types (text, tool_result, tool_use, notification, status_update) with field tables and examples
- **Environment Variables** — CLAUDE_TEAM_ID, CLAUDE_TEAMMATE_ID, CLAUDE_CODE_TASK_LIST_ID, and other runtime variables
- **File Structure** — Team workspace layout and shared file conventions

### Reference Files

| File | Description |
|------|-------------|
| `messaging-protocol.md` | All 5 SendMessage types with field tables, usage guidance, and tool call examples |
| `orchestration-patterns.md` | 5+ orchestration pattern templates with team structure, communication flow, and selection guidance |
| `hooks-integration.md` | TeammateIdle and TaskCompleted hook events with input schemas, exit codes, and examples |

### How to Load

```
Read ${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/claude-code-teams/SKILL.md
```

The SKILL.md provides progressive loading — reference files are loaded on demand via:

```
Read ${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/claude-code-teams/references/messaging-protocol.md
Read ${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/claude-code-teams/references/orchestration-patterns.md
Read ${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/claude-code-teams/references/hooks-integration.md
```

## Usage

### Same-Plugin Agents

Agents defined within `claude-tools` can bind skills via `skills:` frontmatter:

```yaml
skills:
  - claude-code-tasks
  - claude-code-teams
```

### Cross-Plugin Skills

Skills in other plugins load these references with a `Read` directive in their SKILL.md:

```
Read ${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/claude-code-tasks/SKILL.md
Read ${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/claude-code-teams/SKILL.md
```

### Cross-Plugin Agents

Agents in other plugins load these references with a `Read` directive in their agent body:

```
Read ${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/claude-code-tasks/SKILL.md
Read ${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/claude-code-teams/SKILL.md
```

## Directory Structure

```
claude-tools/
├── skills/
│   ├── claude-code-tasks/
│   │   ├── SKILL.md                    # Tasks tool reference (main)
│   │   └── references/
│   │       ├── task-patterns.md        # Dependency graphs, right-sizing, coordination
│   │       └── anti-patterns.md        # Common mistakes and correct alternatives
│   └── claude-code-teams/
│       ├── SKILL.md                    # Agent Teams reference (main)
│       └── references/
│           ├── messaging-protocol.md   # SendMessage types and fields
│           ├── orchestration-patterns.md # Team orchestration templates
│           └── hooks-integration.md    # TeammateIdle, TaskCompleted hooks
└── README.md
```
