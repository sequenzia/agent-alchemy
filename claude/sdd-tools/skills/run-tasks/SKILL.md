---
name: run-tasks
description: Execute pending tasks in dependency order with wave-based concurrent execution via Agent Teams
argument-hint: "[--task-group <name>] [--phase <N,M>] [--dry-run]"
allowed-tools:
  - TaskList
  - TaskGet
  - TaskUpdate
  - TaskCreate
  - TeamCreate
  - TeamDelete
  - SendMessage
  - TaskOutput
  - TaskStop
  - Task
  - AskUserQuestion
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---

# Run Tasks Skill

This skill orchestrates autonomous task execution using Claude Code's native Agent Team system. It takes tasks produced by `/create-tasks`, builds a dependency-aware execution plan, and executes them in waves via a 3-tier agent hierarchy: Orchestrator (this skill) plans and coordinates waves, Wave Leads manage parallel executors within each wave, and Context Managers handle knowledge flow between tasks.

All inter-agent coordination uses message-based primitives (`TeamCreate`, `SendMessage`, `TaskOutput`) rather than file-based signaling.

## Load Reference Skills

Before executing any step, load the foundational references for task management and team orchestration:

### Tasks Reference
```
Read ${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/claude-code-tasks/SKILL.md
```

### Teams Reference
```
Read ${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/claude-code-teams/SKILL.md
```

These references provide tool parameters, lifecycle rules, messaging protocols, and orchestration patterns. The SDD-specific execution procedures are in the orchestration reference below.

### Orchestration Reference
```
Read ${CLAUDE_PLUGIN_ROOT}/skills/run-tasks/references/orchestration.md
```

If any reference file cannot be read, stop and report: "ERROR: Cannot load required reference. Verify the plugin installation is complete."

## Argument Parsing

Parse the following arguments from the user's invocation:

| Argument | Format | Default | Description |
|----------|--------|---------|-------------|
| `--task-group` | `<name>` | _(none — all tasks)_ | Filter tasks to those with matching `metadata.task_group` |
| `--phase` | `<N>` or `<N,M,...>` | _(none — all phases)_ | Comma-separated integers. Filter tasks by `metadata.spec_phase`. Tasks without `spec_phase` are excluded when active. |
| `--dry-run` | _(flag)_ | `false` | Complete Steps 1-3 only: load, plan, display. No agents spawned, no session directory created. |

When both `--task-group` and `--phase` are provided, both filters apply (intersection).

**Validation:**
- `--phase` values must be positive integers. If a non-integer value is provided (e.g., `--phase abc`), report: "Invalid --phase value: must be comma-separated positive integers (e.g., --phase 1,2)." and stop.
- If no tasks match the applied filters, report the available values. For `--phase`: "No tasks found for phase(s) {N}. Available phases: {sorted distinct spec_phase values}." For `--task-group`: "No tasks found for group '{name}'. Available groups: {sorted distinct task_group values}."

## 7-Step Orchestration Loop

### Step 1: Load & Validate

Load the full task list via `TaskList`. Apply `--task-group` and `--phase` filters if provided. Validate the resulting task set:

- **Empty task list**: Suggest running `/create-tasks` first.
- **All tasks completed**: Report summary with completion counts and stop.
- **No unblocked tasks**: Report the blocking chains preventing progress.
- **Circular dependencies**: Detect cycles, break at the weakest link (task with fewest blockers), and warn the user in the execution plan.

See `references/orchestration.md` Step 1 for the full procedure.

### Step 2: Configure & Plan

Read settings from `.claude/agent-alchemy.local.md` (use defaults if the file is missing). Build the execution plan:

1. **Topological sort**: Assign tasks to waves based on dependency levels. Wave 1 = tasks with no unmet dependencies. Wave N = tasks whose blockers are all in earlier waves or already completed.
2. **Priority ordering within waves**: Sort by priority (critical > high > medium > low > unprioritized), break ties by "unblocks most others."
3. **Wave capping**: Each wave limited to `max_parallel` tasks (default: 5, configurable via settings).

See `references/orchestration.md` Step 2 for settings and the full planning procedure.

### Step 3: Confirm

Present the execution plan to the user via `AskUserQuestion`:

- Total task count, wave count, and estimated team composition per wave (1 wave-lead + 1 context-manager + N executors).
- Per-wave breakdown with task subjects, priorities, and model tiers.
- Any circular dependency warnings or broken links.

**If `--dry-run`**: Display the full plan details (wave breakdown, task assignments, model tiers, timeout estimates) and exit. No `TaskUpdate` calls, no session directory created, no agents spawned.

**If the user cancels**: Clean exit with no tasks modified.

See `references/orchestration.md` Step 3 for display format details.

### Step 4: Initialize Session

Create the session directory and handle interrupted session recovery:

1. **Generate session ID**: `{task-group}-{YYYYMMDD}-{HHMMSS}` (or `exec-session-{YYYYMMDD}-{HHMMSS}` if no group).
2. **Check for existing `__live_session__/` content**: If found, offer the user a choice via `AskUserQuestion`: resume (reset `in_progress` tasks to `pending`) or fresh start (archive to `.claude/sessions/interrupted-{timestamp}/`).
3. **Create session artifacts** in `.claude/sessions/__live_session__/`:
   - `execution_context.md` — empty template
   - `task_log.md` — header row only
   - `execution_plan.md` — populated from Step 2
   - `progress.jsonl` — `session_start` event

See `references/orchestration.md` Step 4 for the full initialization procedure and session ID generation rules.

### Step 5: Execute Waves

For each wave in the execution plan:

1. **Refresh unblocked tasks** via `TaskList` (dynamic unblocking after prior wave completions).
2. **Create wave team** via `TeamCreate` with a wave-lead agent (foreground `Task`) and team members (context-manager + executors).
3. **Launch wave-lead** with the wave assignment (task list, max_parallel, max_retries, wave number) and cross-wave context from `execution_context.md`.
4. **Wait for wave-lead summary** — the wave-lead manages all executor coordination, retries (Tier 1 immediate, Tier 2 context-enriched), and reports results via `SendMessage`.
5. **Process wave summary**: Update `task_log.md`, write `wave_complete` event to `progress.jsonl`, handle Tier 3 escalations (present failures to user via `AskUserQuestion` with options: Fix manually, Skip, Provide guidance, Abort).
6. **Delete wave team** via `TeamDelete`.
7. **Repeat** until no more unblocked tasks remain.

See `references/orchestration.md` Step 5 for the full wave execution procedure, retry escalation flow, and wave-lead crash recovery.

### Step 6: Summarize & Archive

Generate a session summary and archive the session:

- Write `session_summary.md` with pass/fail/partial/skipped counts, total execution time, per-wave breakdown, failed task list with reasons, and key decisions made during execution.
- Write `session_complete` event to `progress.jsonl`.
- Archive: Move `__live_session__/` contents to `.claude/sessions/{session-id}/`.

See `references/orchestration.md` Step 6 for the summary format and archival procedure.

### Step 7: Finalize

Review `execution_context.md` for project-wide changes and update `CLAUDE.md` if warranted:

- New dependencies added to the project
- New patterns established during execution
- Architecture decisions made
- New commands or build steps discovered

Skip updates if only task-specific or internal implementation details were recorded.

See `references/orchestration.md` Step 7 for the CLAUDE.md update criteria.

## Key Behaviors

- **Orchestration pattern**: Based on the Swarm pattern from claude-code-teams (wave-based parallel execution with dependency ordering), extended with a 3-tier agent hierarchy for context management and retry intelligence. See `claude-code-teams/references/orchestration-patterns.md` for the base pattern.
- **3-tier agent hierarchy**: Orchestrator (this skill) handles planning and user interaction. Wave Leads coordinate executors within a wave. Context Managers distribute and collect execution context.
- **Agent Team coordination**: All inter-agent communication uses `TeamCreate`, `SendMessage`, and `TaskOutput` following the claude-code-teams lifecycle. No file-based signaling.
- **Wave-based parallelism**: Tasks at the same dependency level run simultaneously via the wave-lead's executor team. Tasks in later waves wait until their dependencies complete.
- **3-tier retry model**: Tier 1 (Immediate) — wave-lead retries failed executor with failure context. Tier 2 (Context-Enriched) — wave-lead requests additional context from Context Manager and retries. Tier 3 (User Escalation) — persistent failures reported to orchestrator for user decision.
- **Wave-lead crash recovery**: If a wave-lead crashes or times out, the orchestrator resets in-progress tasks to pending and spawns a new wave team. If the retry also fails, the user is escalated.
- **Per-task timeouts**: Complexity-based (XS/S: 5 min, M: 10 min, L/XL: 20 min). Override via `metadata.timeout_minutes`.
- **Dry-run mode**: `--dry-run` completes Steps 1-3 only. Displays the full execution plan without spawning agents or creating a session.
- **Autonomous after confirmation**: After the user confirms at Step 3, no further prompts occur unless a Tier 3 escalation is triggered by persistent failures.
- **Single-session invariant**: Only one execution session at a time per project. Existing sessions must be resolved before starting a new one.
- **Phase and group filtering**: `--phase` and `--task-group` can be combined (AND logic). Filters narrow the task set before planning.

## Quality Gate Hooks

This skill uses Claude Code hooks for automated quality gates during execution:

- **TaskCompleted**: When a task executor marks a task completed, the `verify-task-completion.sh` hook runs the project's test suite. If tests fail, the completion is blocked and the task reverts to in_progress with feedback to the executor.
- **TeammateIdle**: When a task executor goes idle, a prompt-based hook verifies it has sent both required messages (TASK RESULT to wave-lead, CONTEXT CONTRIBUTION to context manager) before resting.

Hook definitions are in `${CLAUDE_PLUGIN_ROOT}/hooks/hooks.json`. For hook event documentation, see `claude-code-teams/references/hooks-integration.md`.

## Example Usage

### Execute all pending tasks
```
/run-tasks
```

### Execute tasks for a specific group
```
/run-tasks --task-group user-authentication
```

### Execute a specific phase
```
/run-tasks --phase 1
```

### Execute multiple phases within a group
```
/run-tasks --task-group payments --phase 1,2
```

### Preview the execution plan without running
```
/run-tasks --dry-run
```

### Dry-run with filters
```
/run-tasks --task-group payments --phase 2 --dry-run
```

## Reference Files

- `references/orchestration.md` — Detailed 7-step orchestration procedures, wave execution, retry escalation, session management, and CLAUDE.md update criteria
- `references/communication-protocols.md` — SDD-specific message schemas for the 3-tier hierarchy (6 protocols)
- `references/verification-patterns.md` — Verification logic for spec-generated vs general tasks
- `${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/claude-code-tasks/SKILL.md` — Task tool parameters and conventions (loaded at init)
- `${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/claude-code-teams/SKILL.md` — Team lifecycle, messaging, and orchestration patterns (loaded at init)
- `${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/claude-code-teams/references/orchestration-patterns.md` — 6 orchestration patterns (optional, for reference)
