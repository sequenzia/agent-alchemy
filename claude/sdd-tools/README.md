# Agent Alchemy SDD Tools

Spec-Driven Development — turn ideas into structured specifications, decompose them into executable tasks, and run autonomous implementation with wave-based parallelism.

> **Standalone plugin** — sdd-tools has no external plugin dependencies. Codebase exploration for "new feature" specs uses a built-in `codebase-explorer` agent instead of cross-plugin references.

## Skills

| Skill | Invocable | Description |
|-------|-----------|-------------|
| `/create-spec` | Yes | Adaptive interview process that generates structured specifications. Supports 3 depth levels (high-level, detailed, full-tech) with proactive recommendations, optional codebase exploration, and external research. |
| `/analyze-spec` | Yes | Spec quality analysis that checks for inconsistencies, ambiguities, and missing requirements. Generates HTML and markdown reports. |
| `/create-tasks` | Yes | Decomposes specs into dependency-ordered Claude Code Tasks with acceptance criteria. Supports merge mode for incremental updates via `task_uid`. |
| `/execute-tasks` | Yes | Wave-based task execution orchestrator with session management, per-task context isolation, concurrent agent execution, and interrupted session recovery. |

> **Note:** TDD task creation and execution skills (`/create-tdd-tasks`, `/execute-tdd-tasks`) have moved to the `tdd-tools` plugin as of v0.1.3.

## Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| `codebase-explorer` | sonnet | Explores codebases to discover architecture, patterns, and feature-relevant code. Spawned in parallel by `/create-spec` for "new feature" type specs. |
| `researcher` | — | Technical and domain research for spec creation. Searches external sources for architecture decisions and best practices. |
| `spec-analyzer` | — | Quality analysis agent that reviews specs against criteria and generates structured reports. |
| `task-executor` | — | Autonomous implementation agent with 4-phase workflow. Writes execution context and progress updates consumed by the Task Manager. Also used by `tdd-tools` `/execute-tdd-tasks` for non-TDD tasks. |

## The SDD Pipeline

```
/create-spec  -->  specs/SPEC-{name}.md
                        |
/analyze-spec -->  {name}.analysis.md + .analysis.html
                        |
/create-tasks -->  ~/.claude/tasks/{list}/*.json
                        |
/execute-tasks --> Wave-based autonomous execution
                        |
                   Task Manager (real-time monitoring)
```

### Depth Levels

| Level | Interview Rounds | Questions | Tasks per Feature |
|-------|-----------------|-----------|-------------------|
| High-level | 2-3 | 6-10 | 1-2 |
| Detailed | 3-4 | 12-18 | 3-5 |
| Full-tech | 4-5 | 18-25 | 5-10 |

### Task Merge Mode

When re-running `/create-tasks` on an updated spec, the skill uses `task_uid` metadata to intelligently merge:
- **Completed** tasks: preserved (never modified)
- **Pending** tasks: updated if spec changed
- **In-progress** tasks: skipped
- **New requirements**: created as new tasks

## Hooks

| Hook | Event | Purpose |
|------|-------|---------|
| `auto-approve-session.sh` | `PreToolUse` (Write, Edit, Bash) | Auto-approves file operations within execution session directories. Timeout: 5s. |

## Directory Structure

```
sdd-tools/
├── agents/
│   ├── codebase-explorer.md    # Codebase exploration agent (sonnet)
│   ├── researcher.md           # Research agent
│   ├── spec-analyzer.md        # Spec quality agent
│   └── task-executor.md        # Implementation agent
├── hooks/
│   ├── hooks.json              # PreToolUse hook config
│   └── auto-approve-session.sh # Session auto-approve script
├── skills/
│   ├── create-spec/
│   │   ├── SKILL.md            # Interview workflow (665 lines)
│   │   └── references/
│   │       ├── codebase-exploration.md
│   │       ├── interview-questions.md
│   │       ├── recommendation-triggers.md
│   │       ├── recommendation-format.md
│   │       └── templates/
│   │           ├── high-level.md
│   │           ├── detailed.md
│   │           └── full-tech.md
│   ├── analyze-spec/
│   │   ├── SKILL.md            # Analysis workflow
│   │   └── references/
│   │       ├── analysis-criteria.md
│   │       ├── common-issues.md
│   │       ├── html-review-guide.md
│   │       └── report-template.md
│   ├── create-tasks/
│   │   ├── SKILL.md            # Task decomposition (654 lines)
│   │   └── references/
│   │       ├── decomposition-patterns.md
│   │       ├── dependency-inference.md
│   │       └── testing-requirements.md
│   └── execute-tasks/
│       ├── SKILL.md            # Execution orchestrator
│       └── references/
│           ├── execution-workflow.md
│           ├── orchestration.md
│           └── verification-patterns.md
└── README.md
```
