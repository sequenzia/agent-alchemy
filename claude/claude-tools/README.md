# Agent Alchemy Claude Tools

Shared reference skills for Claude Code Tasks and Agent Teams features, enabling consistent usage across the agent-alchemy ecosystem.

**Version**: 0.1.0

## Purpose

The `claude-tools` plugin provides reference skills for Claude Code's Tasks and Agent Teams features, plus a user-invocable `create-team` skill that demonstrates team coordination with dual independent explorers. Other skills and agents load the reference skills at runtime to ensure correct, consistent usage of task management and multi-agent coordination APIs. This follows the same composition pattern established by `language-patterns` and `technical-diagrams` in `core-tools`.

## Skills

| Skill | Description | Type |
|-------|-------------|------|
| `cc-tasks` | Claude Code Tasks tool reference | Reference (non-user-invocable) |
| `cc-teams` | Claude Code Agent Teams reference | Reference (non-user-invocable) |
| `create-team` | Dual explorer team that independently explores a directory and compares findings | User-invocable |

## cc-tasks

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
Read ${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/cc-tasks/SKILL.md
```

The SKILL.md provides progressive loading — reference files are loaded on demand via:

```
Read ${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/cc-tasks/references/task-patterns.md
Read ${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/cc-tasks/references/anti-patterns.md
```

## cc-teams

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
Read ${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/cc-teams/SKILL.md
```

The SKILL.md provides progressive loading — reference files are loaded on demand via:

```
Read ${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/cc-teams/references/messaging-protocol.md
Read ${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/cc-teams/references/orchestration-patterns.md
Read ${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/cc-teams/references/hooks-integration.md
```

## create-team

Spawns an Agent Team with two `code-explorer` agents (from `core-tools`) that independently explore a user-specified directory, then compares their findings into a structured report highlighting differences, coverage gaps, and combined insights.

### Workflow

1. **Phase 1: Setup & Spawning** — Validates target directory, creates team with `TeamCreate`, spawns 2 explorer agents (Sonnet) via `Task` tool, creates and assigns exploration tasks with status-guarded assignment
2. **Phase 2: Monitor & Compare** — Monitors exploration progress via `TaskGet`, collects findings from both explorers, produces comparison report with key differences table, unique discoveries, different interpretations, and coverage gaps
3. **Phase 3: Cleanup** — Sends `shutdown_request` to both explorers, calls `TeamDelete`

### Usage

```
/create-team claude/core-tools
/create-team apps/task-manager/src
```

### Cross-Plugin Dependencies

- **`code-explorer`** from `core-tools` — Used as the explorer agent type. Has `SendMessage`, `TaskUpdate`, and `TaskGet` tools required for team coordination.
- **`cc-teams`** and **`cc-tasks`** — Loaded at skill start for correct tool parameter documentation.

## Usage

### Same-Plugin Agents

Agents defined within `claude-tools` can bind skills via `skills:` frontmatter:

```yaml
skills:
  - cc-tasks
  - cc-teams
```

### Cross-Plugin Skills

Skills in other plugins load these references with a `Read` directive in their SKILL.md:

```
Read ${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/cc-tasks/SKILL.md
Read ${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/cc-teams/SKILL.md
```

### Cross-Plugin Agents

Agents in other plugins load these references with a `Read` directive in their agent body:

```
Read ${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/cc-tasks/SKILL.md
Read ${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/cc-teams/SKILL.md
```

## Directory Structure

```
claude-tools/
├── skills/
│   ├── cc-tasks/
│   │   ├── SKILL.md                    # Tasks tool reference (main)
│   │   └── references/
│   │       ├── task-patterns.md        # Dependency graphs, right-sizing, coordination
│   │       └── anti-patterns.md        # Common mistakes and correct alternatives
│   ├── cc-teams/
│   │   ├── SKILL.md                    # Agent Teams reference (main)
│   │   └── references/
│   │       ├── messaging-protocol.md   # SendMessage types and fields
│   │       ├── orchestration-patterns.md # Team orchestration templates
│   │       └── hooks-integration.md    # TeammateIdle, TaskCompleted hooks
│   └── create-team/
│       └── SKILL.md                    # Dual explorer comparison skill
└── README.md
```
