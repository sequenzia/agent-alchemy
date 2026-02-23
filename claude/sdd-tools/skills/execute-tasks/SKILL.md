---
name: execute-tasks
description: Execute pending Claude Code Tasks in dependency order with wave-based concurrent execution and adaptive verification. Supports task group filtering and configurable parallelism. Use when user says "execute tasks", "run tasks", "start execution", "work on tasks", or wants to execute generated tasks autonomously.
argument-hint: "[task-id] [--task-group <group>] [--phase <phases>] [--retries <n>] [--max-parallel <n>]"
user-invocable: true
disable-model-invocation: false
allowed-tools:
  - Task
  - TaskOutput
  - TaskStop
  - Read
  - Write
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
  - TaskList
  - TaskGet
  - TaskUpdate
arguments:
  - name: task-id
    description: Optional specific task ID to execute. If omitted, executes all unblocked tasks in dependency order.
    required: false
  - name: task-group
    description: Optional task group name to filter tasks. Only tasks with matching metadata.task_group will be executed.
    required: false
  - name: phase
    description: Comma-separated phase numbers to filter tasks by spec_phase metadata (e.g., "1,2"). Only tasks with matching metadata.spec_phase will be executed.
    required: false
  - name: retries
    description: Number of retry attempts for failed/partial tasks before moving on. Default is 3.
    required: false
  - name: max-parallel
    description: Maximum number of tasks to execute simultaneously per wave. Default is 5. Overrides settings file value.
    required: false
---

# Execute Tasks Skill

This skill orchestrates autonomous task execution for Claude Code Tasks. It builds a dependency-aware execution plan, launches a dedicated agent for each task through a 4-phase workflow (Understand, Implement, Verify, Complete), handles retries with failure context, and shares learnings across tasks through a shared execution context file.

## Core Principles

### 1. Understand Before Implementing

Never write code without first understanding:
- What the task requires (acceptance criteria or inferred requirements)
- What code already exists (read before modify)
- What conventions the project follows (CLAUDE.md, existing patterns)
- What earlier tasks discovered (shared execution context)

### 2. Follow Existing Patterns

Match the codebase's established patterns:
- Coding style, naming conventions, file organization
- Error handling approach, logging patterns
- Test framework, test structure, assertion style
- Import ordering, module organization

### 3. Verify Against Criteria

Do not assume implementation is correct. Verify by:
- Walking through each acceptance criterion for spec-generated tasks
- Running tests and linters for all tasks
- Confirming the core change works as intended
- Checking for regressions in existing functionality

### 4. Report Honestly

Produce accurate verification results:
- PASS only when all Functional criteria pass and tests pass
- PARTIAL when non-critical criteria fail but core works
- FAIL when Functional criteria or tests fail
- Never mark a task complete if verification fails

## Orchestration Workflow

This skill orchestrates task execution through a 10-step loop. See `references/orchestration.md` for the full detailed procedure.

### Step 1: Load Task List
Retrieve all tasks via `TaskList`. If a `--task-group` argument was provided, filter tasks to only those with matching `metadata.task_group`. If a `--phase` argument was provided, further filter the task list to only tasks where `metadata.spec_phase` matches one of the specified phase numbers. If no tasks match the phase filter, inform the user: "No tasks found for phase(s) {N}. Available phases in current task set: {sorted list of distinct `metadata.spec_phase` values}." and stop. When both `--task-group` and `--phase` are provided, both filters apply (intersection). Tasks without `spec_phase` metadata are excluded when `--phase` is active. If a specific `task-id` argument was provided, validate it exists.

### Step 2: Validate State
Handle edge cases: empty list, all completed, specific task blocked, no unblocked tasks, circular dependencies.

### Step 3: Build Execution Plan
Resolve `max_parallel` setting using precedence: `--max-parallel` CLI arg > `.claude/agent-alchemy.local.md` setting > default 5. Build a dependency graph from pending tasks. Assign tasks to waves using topological levels: Wave 1 = no dependencies, Wave 2 = depends on Wave 1 tasks, etc. Sort within waves by priority (critical > high > medium > low > unprioritized), break ties by "unblocks most others." Cap each wave at `max_parallel` tasks.

### Step 4: Check Settings
Read `.claude/agent-alchemy.local.md` if it exists for execution preferences, including `max_parallel` setting. CLI `--max-parallel` argument takes precedence over the settings file value.

### Step 5: Initialize Execution Directory
Generate a `task_execution_id` using multi-tier resolution: (1) if `--task-group` AND `--phase` provided → `{task_group}-phase{N}-{YYYYMMDD}-{HHMMSS}`, (2) if `--task-group` provided (no phase) → `{task_group}-{YYYYMMDD}-{HHMMSS}`, (3) if `--phase` provided (no group) AND all filtered tasks share same group → `{task_group}-phase{N}-{YYYYMMDD}-{HHMMSS}`, else `phase{N}-{YYYYMMDD}-{HHMMSS}`, (4) else if all open tasks share the same `metadata.task_group` → `{task_group}-{YYYYMMDD}-{HHMMSS}`, (5) else → `exec-session-{YYYYMMDD}-{HHMMSS}`. Where `{N}` is the phase number (or `{N}-{M}` for multiple phases, e.g., `phase1-2`). Clean any stale `__live_session__/` files by archiving them to `.claude/sessions/interrupted-{YYYYMMDD}-{HHMMSS}/`, resetting any `in_progress` tasks from the interrupted session back to `pending`. Check for and enforce the concurrency guard via `.lock` file. Create `.claude/sessions/__live_session__/` directory containing:
- `execution_plan.md` — saved execution plan from Step 5
- `execution_context.md` — initialized with standard template
- `task_log.md` — initialized with table headers (Task ID, Subject, Status, Attempts, Duration, Token Usage)
- `tasks/` — subdirectory for archiving completed task files
- `progress.md` — initialized with status template for real-time progress tracking
- `execution_pointer.md` at `~/.claude/tasks/{CLAUDE_CODE_TASK_LIST_ID}/` — created immediately with absolute path to `.claude/sessions/__live_session__/`

### Step 6: Present Execution Plan and Confirm
Display the plan showing tasks to execute, blocked tasks, and completed count. Also display the details of step 5 which includes the session directory path (`.claude/sessions/__live_session__/`) and files created, including the execution pointer file location.

Then ask the user to confirm before proceeding with execution. If the user cancels, stop without modifying any tasks.

### Step 7: Initialize Execution Context
Read `.claude/sessions/__live_session__/execution_context.md` (created in Step 5). If a prior execution context exists, look in `.claude/sessions/` for the most recent timestamped subfolder and merge relevant learnings into the new one.

### Step 8: Execute Loop
Before entering the wave loop, emit a session start summary: `Execution plan: {total_tasks} tasks across {total_waves} waves (max {max_parallel} parallel)`. Execute tasks in waves. Before each wave, run a **pre-wave file conflict scan**: parse all wave tasks' descriptions and acceptance criteria for file path references (paths with `/`, known extensions like `.md`/`.ts`/`.js`/`.json`/`.sh`/`.py`, and glob patterns); if two or more tasks reference the same file, defer the higher-ID task(s) to the next wave (lowest ID stays) and log conflicts to `execution_plan.md`. See `references/orchestration.md` Step 7a.5 for the full procedure. Then emit: `Starting Wave {N}/{total}: {count} tasks...`. Before launching agents, build **upstream injection blocks** for tasks with `produces_for` dependencies: read producer result files and inject as `CONTEXT FROM COMPLETED DEPENDENCIES` in the agent prompt (see `references/orchestration.md` for the injection procedure). For each wave: snapshot `execution_context.md`, mark wave tasks `in_progress`, update `progress.md` with all active tasks, launch up to `max_parallel` background agents simultaneously via **parallel Task tool calls with `run_in_background: true`**, recording the `{task_list_id → background_task_id}` mapping from each Task tool response. Each agent writes to `context-task-{id}.md` and a compact `result-task-{id}.md` (completion signal). The orchestrator detects completion via `watch-for-results.sh` (event-driven, primary) with fallback to `poll-for-results.sh` (adaptive polling) if filesystem watch tools are unavailable, then batch-reads results to process outcomes — avoiding full agent output in context. After detection, the orchestrator calls `TaskOutput` on each background task_id to reap the process and extract per-task `duration_ms` and `total_tokens` usage metadata for the task log. If `TaskOutput` times out (agent stuck), `TaskStop` is called to force-terminate the agent. After processing results, emit a wave completion summary showing pass/fail count, wave duration, and per-task breakdown (ID, name, status, duration, token count). Failed tasks are retried using a **3-tier escalation strategy**: Tier 1 (Standard) re-launches with failure context, Tier 2 (Context Enrichment) adds full execution context + related results, Tier 3 (User Escalation) pauses for user input via AskUserQuestion with options to fix manually, skip, provide guidance, or abort. See `references/orchestration.md` Step 7e for details. After all wave agents complete: merge per-task context files into `execution_context.md`, clean up result and context files, archive completed task JSONs, refresh TaskList for newly unblocked tasks, form next wave, repeat.

### Step 9: Session Summary
Display execution results with pass/fail counts, total execution time (sum of per-task `duration_ms`), failed task list, newly unblocked tasks, and total token usage (sum of per-task `total_tokens` captured via `TaskOutput`). Save `session_summary.md` to `.claude/sessions/__live_session__/`. Archive the session by moving all contents from `__live_session__/` to `.claude/sessions/{task_execution_id}/`, leaving `__live_session__/` as an empty directory. `execution_pointer.md` stays pointing to `__live_session__/`.

### Step 10: Update CLAUDE.md
Review execution context for project-wide changes (new patterns, dependencies, commands, structure changes, design decisions). Make targeted edits to CLAUDE.md if meaningful changes occurred. Skip if only task-specific or internal implementation details.

## Task Classification

Determine whether a task is spec-generated or general to select the right verification approach.

### Detection Algorithm

1. **Check description format**: Look for `**Acceptance Criteria:**` with categorized criteria (`_Functional:_`, `_Edge Cases:_`, etc.)
2. **Check metadata**: Look for `metadata.spec_path` field
3. **Check source reference**: Look for `Source: {path} Section {number}` in the description

If any check matches -> **spec-generated task** (use criterion-based verification)

If none match -> **General task** (use inferred verification)

## 4-Phase Workflow

Each task is executed by the `agent-alchemy-sdd:task-executor` agent through these phases:

### Phase 1: Understand

Load context and understand scope before writing code.

- Read the execute-tasks skill and references
- Read `.claude/sessions/__live_session__/execution_context.md` for learnings from prior tasks
- Read upstream task output if `## UPSTREAM TASK OUTPUT` blocks are present in the prompt (injected via `produces_for` — see `references/orchestration.md`)
- Load task details via `TaskGet`
- Classify the task (spec-generated vs general)
- Parse acceptance criteria or infer requirements from description
- Explore affected files via Glob/Grep
- Read `CLAUDE.md` for project conventions

### Phase 2: Implement

Execute the code changes following project patterns.

- Read all target files before modifying them
- Follow the project's implementation order (data -> service -> interface -> tests)
- Match existing coding patterns and conventions
- Write tests if specified in testing requirements
- Run mid-implementation checks (linter, existing tests) to catch issues early

### Phase 3: Verify

Verify implementation against task requirements using the adaptive approach.

- **spec-generated tasks**: Walk each acceptance criteria category (Functional, Edge Cases, Error Handling, Performance), check testing requirements, run tests
- **General tasks**: Infer "done" from description, run existing tests, run linter, verify core change is implemented

### Phase 4: Complete

Report results and share learnings.

- Determine status (PASS/PARTIAL/FAIL) based on verification results
- If PASS: mark task as `completed` via `TaskUpdate`
- If PARTIAL or FAIL: leave as `in_progress` for the orchestrator to decide on retry
- Write learnings to `.claude/sessions/__live_session__/context-task-{id}.md` (files discovered, patterns learned, issues encountered)
- Write compact result to `.claude/sessions/__live_session__/result-task-{id}.md` (status, verification summary, files modified, issues) — this is the **last** file written and signals completion to the orchestrator
- Return minimal status line: `DONE: [{id}] {subject} - {PASS|PARTIAL|FAIL}`

## Adaptive Verification Overview

Verification adapts based on task type:

| Task Type | Verification Method | Pass Threshold |
|-----------|-------------------|----------------|
| spec-generated | Criterion-by-criterion evaluation | All Functional + Tests must pass |
| General | Inferred checklist from description | Core change works + Tests pass |

**Critical rule**: All Functional criteria must pass for a PASS result. Edge Cases, Error Handling, and Performance failures result in PARTIAL but do not block completion.

## Shared Execution Context

Tasks within an execution session share learnings through `.claude/sessions/__live_session__/execution_context.md`:

- **Write-based updates**: All orchestrator writes to session artifacts (`execution_context.md`, `task_log.md`, `progress.md`) use Write (full file replacement) via a read-modify-write pattern, never Edit. This ensures atomic, reliable updates regardless of file size.
- **Snapshot before wave**: The orchestrator snapshots `execution_context.md` before launching each wave — all agents in a wave read the same baseline
- **Per-task writes**: Each agent writes to `context-task-{id}.md` instead of the shared file, regardless of `max_parallel` setting. This eliminates write contention and avoids fragile Edit operations on shared files.
- **Result file protocol**: Each agent writes a compact `result-task-{id}.md` (~18 lines) as its very last action. The orchestrator polls for these files and reads them instead of consuming full agent output, reducing context consumption by ~79% per wave.
- **Merge after wave**: After all agents in a wave complete, the orchestrator appends all `context-task-{id}.md` content to the `## Task History` section of `execution_context.md` and deletes the per-task files. Result files for PASS tasks are also deleted; FAIL result files are retained for post-analysis.
- **Sections**: Project Patterns, Key Decisions, Known Issues, File Map, Task History

This enables later tasks to benefit from earlier discoveries and retry attempts to learn from previous failures.

## Key Behaviors

- **Autonomous execution loop**: After the user confirms the execution plan, no further prompts occur between tasks — except during Tier 3 retry escalation, when persistent failures are presented to the user via AskUserQuestion. The loop runs without interruption once started.
- **Progress streaming**: The orchestrator emits human-readable progress summaries at wave boundaries: a session start message with task/wave counts, "Starting Wave N" before each wave launch, and a wave completion summary with per-task breakdown (status, duration, token count) after each wave completes. Wave-level granularity only — no per-task streaming during a wave.
- **Background agent execution**: Agents run as background tasks (`run_in_background: true`), returning ~3 lines (task_id + output_file) instead of ~100+ lines of full output. This reduces orchestrator context consumption by ~79% per wave.
- **Agent process reaping**: After completion detection confirms result files exist, the orchestrator calls `TaskOutput` on each background task_id to reap the process and extract per-task `duration_ms` and `total_tokens` usage metadata. If `TaskOutput` times out, `TaskStop` force-terminates the stuck agent. This prevents lingering background processes.
- **Event-driven completion detection**: Each agent writes a compact `result-task-{id}.md` (~18 lines) as its very last action. The orchestrator detects these files via `watch-for-results.sh` (fswatch/inotifywait, <1s latency) as primary, falling back to `poll-for-results.sh` (adaptive 5s-30s intervals) if watch tools are unavailable (exit code 2). Both scripts emit `RESULT_FOUND:` lines for incremental progress and `ALL_DONE` on completion. The result file doubles as a completion signal.
- **Batched session file updates**: Instead of per-task read-modify-write on `task_log.md` and `progress.md`, all updates are batched into a single read-modify-write cycle per file per wave.
- **Upstream prompt injection (produces_for)**: Tasks with `produces_for` fields declare which downstream tasks consume their output. When launching a dependent task, the orchestrator reads the producer's result file and injects it into the agent prompt as `CONTEXT FROM COMPLETED DEPENDENCIES`. Multiple producers are injected in task ID order. Failed producers inject a failure notice instead. Tasks without `produces_for` behave unchanged (wave-granular context only). See `references/orchestration.md` for the full injection procedure.
- **File conflict detection**: Before each wave launch, task descriptions and acceptance criteria are scanned for file path references. If two tasks reference the same file, the lower-ID task stays and higher-ID tasks are deferred to the next wave, preventing concurrent edit conflicts. Conflicts are logged in `execution_plan.md`. No overhead when no conflicts are found.
- **Wave-based parallelism**: Tasks at the same dependency level run simultaneously, up to `max_parallel` concurrent agents per wave. Tasks in later waves wait until their dependencies in earlier waves complete.
- **One agent per task, multiple per wave**: Each task gets a fresh agent invocation with isolated context, but multiple agents run concurrently within a wave.
- **Per-task context isolation**: Each agent writes to `context-task-{id}.md` regardless of `max_parallel` setting. The orchestrator merges these after each wave. This eliminates write contention and fragile Edit operations on shared files.
- **3-tier retry escalation**: Failed tasks progress through escalating retry strategies: Tier 1 (Standard) re-launches with failure context, Tier 2 (Context Enrichment) injects full `execution_context.md` + related task results, and Tier 3 (User Escalation) pauses to ask the user via AskUserQuestion with 4 options: "Fix manually and continue", "Skip this task", "Provide guidance", or "Abort session". If the user provides guidance, a guided retry is launched; if that also fails, the user is re-prompted. Each task has an independent escalation path; Tier 1/2 retries are batched per wave, Tier 3 is sequential. Escalation level is tracked in `task_log.md` per task. See `references/orchestration.md` Step 7e for the full procedure.
- **Phase-based filtering**: When `--phase N` is provided, only tasks with `metadata.spec_phase` matching the specified phase number(s) are included. This combines with `--task-group` filtering (both are ANDed). Tasks without `spec_phase` metadata are excluded when `--phase` is active.
- **Configurable parallelism**: Default 5 concurrent tasks, configurable via `--max-parallel` argument or `.claude/agent-alchemy.local.md` settings. Set to 1 for sequential execution.
- **Configurable retries**: Default 3 attempts per task, configurable via `retries` argument. Each retry tier maps to one attempt.
- **Dynamic unblocking**: After each wave completes, the dependency graph is refreshed and newly unblocked tasks are added to the next wave.
- **Honest failure handling**: After all automated retries exhausted, the user must choose an action at Tier 3. Tasks left unresolved stay `in_progress` (not completed).
- **Circular dependency detection**: If all remaining tasks are blocked by each other, break at the weakest link (task with fewest blockers) and log a warning.
- **Shared context**: Agents read the snapshot of `execution_context.md` and write learnings to per-task context files. The orchestrator appends per-task content to the Task History section between waves.
- **Resilient context sharing**: If a task-executor fails to write its context or result file, the orchestrator falls back to `TaskOutput` to capture diagnostic output.
- **Single-session invariant**: Only one execution session can run at a time per project. A `.lock` file in `__live_session__/` prevents concurrent invocations.
- **Interrupted session recovery**: Stale sessions are detected and archived; tasks left `in_progress` are automatically reset to `pending`.

## Example Usage

### Execute all unblocked tasks
```
/agent-alchemy-sdd:execute-tasks
```

### Execute a specific task
```
/agent-alchemy-sdd:execute-tasks 5
```

### Execute with custom retry limit
```
/agent-alchemy-sdd:execute-tasks --retries 1
```

### Execute specific task with retries
```
/agent-alchemy-sdd:execute-tasks 5 --retries 5
```

### Execute tasks for a specific group
```
/agent-alchemy-sdd:execute-tasks --task-group user-authentication
```

### Execute specific group with custom retries
```
/agent-alchemy-sdd:execute-tasks --task-group payments --retries 1
```

### Execute tasks for a specific phase
```
/agent-alchemy-sdd:execute-tasks --phase 1
```

### Execute specific phase within a task group
```
/agent-alchemy-sdd:execute-tasks --task-group user-authentication --phase 2
```

### Execute multiple phases
```
/agent-alchemy-sdd:execute-tasks --phase 1,2
```

### Execute with limited parallelism
```
/agent-alchemy-sdd:execute-tasks --max-parallel 2
```

### Execute sequentially (no concurrency)
```
/agent-alchemy-sdd:execute-tasks --max-parallel 1
```

### Execute group with custom parallelism and retries
```
/agent-alchemy-sdd:execute-tasks --task-group payments --max-parallel 3 --retries 1
```

## Reference Files

- `references/orchestration.md` - 10-step orchestration loop with execution plan, retry handling, and session summary
- `references/execution-workflow.md` - Detailed phase-by-phase procedures for the 4-phase workflow
- `references/verification-patterns.md` - Task classification, criterion verification, pass/fail rules, and failure reporting format
