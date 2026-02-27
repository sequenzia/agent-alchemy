# Orchestration Reference

This reference provides the detailed 7-step orchestration loop for the run-tasks skill. The orchestrator runs Steps 1-3 (planning) and Step 3's confirmation in the user's conversation context. Steps 4-7 (execution, summary, finalize) are covered in the execution section of this reference.

---

## Step 1: Load & Validate

```
Input:  TaskList + CLI args (--task-group, --phase)
Output: Filtered, validated task set
Exit:   If no tasks match filters, all completed, or no unblocked tasks
```

### 1a: Read TaskList

Use `TaskList` to retrieve all tasks and their current state (status, blockedBy, metadata).

### 1b: Apply Filters

Apply filters in order. When both `--task-group` and `--phase` are provided, both apply (intersection).

**Task Group Filter** (`--task-group`):

If `--task-group` was provided, filter the task list to only tasks where `metadata.task_group` matches the specified group name (exact match, case-sensitive).

If no tasks match the group:
```
No tasks found for group '{name}'. Available groups: {sorted distinct task_group values}.
```
Stop execution.

**Phase Filter** (`--phase`):

If `--phase` was provided (one or more comma-separated positive integers):

1. Parse the `--phase` value into a list of integers. If any value is not a positive integer, report:
   ```
   Invalid --phase value: must be comma-separated positive integers (e.g., --phase 1,2).
   ```
   Stop execution.

2. Filter the task list to only tasks where `metadata.spec_phase` matches one of the specified phase numbers.

3. Tasks without `spec_phase` metadata are **excluded** when `--phase` is active — they cannot match any phase number.

4. If no tasks match the phase filter:
   ```
   No tasks found for phase(s) {N}. Available phases: {sorted distinct spec_phase values from all tasks}.
   ```
   Stop execution.

### 1c: Validate Task Set

After filtering, validate the resulting task set against these edge cases in order:

**Empty task list** (no tasks at all, before or after filtering):
```
No tasks found. Use /create-tasks to generate tasks from a spec, or create tasks manually.
```
Stop execution.

**All tasks completed**:

If every task in the filtered set has status `completed`, report a summary:
```
All {count} tasks are already completed.

Completed tasks:
- [{id}] {subject} (completed)
- [{id}] {subject} (completed)
...
```
Stop execution.

**No unblocked tasks**:

If there are pending tasks but none have their dependencies satisfied (all blockedBy tasks are not yet completed), report the blocking chains:
```
No unblocked tasks found. All {count} pending tasks are blocked:
- [{id}] {subject} -- blocked by: [{blocker_id1}], [{blocker_id2}]
- [{id}] {subject} -- blocked by: [{blocker_id1}]
...
```
Stop execution.

**Circular dependencies**:

If after topological analysis, some tasks remain unassignable because they form dependency cycles:

1. **Detect**: Identify the set of tasks involved in cycles (tasks that cannot be assigned to any wave because their blockers are also unassigned).
2. **Break at weakest link**: Find the task in the cycle with the fewest `blockedBy` entries. Remove its `blockedBy` relationships for wave assignment purposes (do NOT modify the actual task — this is a planning-time override only).
3. **Warn the user**: Include a warning in the execution plan output (Step 3):
   ```
   WARNING: Circular dependency detected among tasks: [{id1}], [{id2}], [{id3}]
   Breaking cycle at [{weakest_id}] "{subject}" (fewest blockers: {count}).
   This task will be scheduled without waiting for its blockers.
   ```
4. Continue with wave assignment using the broken cycle.

---

## Step 2: Configure & Plan

```
Input:  Filtered task set, .claude/agent-alchemy.local.md (optional)
Output: Execution plan with wave assignments
```

### 2a: Read Settings

Read `.claude/agent-alchemy.local.md` if it exists. Parse YAML frontmatter between `---` delimiters for settings under the `run-tasks` namespace. If the file is missing or any setting is absent, use the default silently (missing settings file is not an error).

| Setting | Key in YAML | Default | Description |
|---------|-------------|---------|-------------|
| Max Parallel | `run-tasks.max_parallel` | `5` | Hint to wave-lead for executor pacing |
| Max Retries | `run-tasks.max_retries` | `1` | Autonomous retries per tier before escalation |
| Wave Lead Model | `run-tasks.wave_lead_model` | `opus` | Model tier for wave-lead agents |
| Context Manager Model | `run-tasks.context_manager_model` | `sonnet` | Model tier for context manager agents |
| Executor Model | `run-tasks.executor_model` | `opus` | Model tier for task executor agents |

**Parsing procedure**:

1. Attempt to read `.claude/agent-alchemy.local.md`. If the file does not exist, use all defaults and continue silently.
2. Extract YAML frontmatter: find content between the opening `---` and closing `---` delimiters at the top of the file.
3. Parse the extracted YAML. If parsing fails (malformed YAML), log a warning message and use all defaults:
   ```
   Warning: Malformed YAML in .claude/agent-alchemy.local.md — using default settings.
   ```
4. For each of the 5 settings, look up the key (e.g., `run-tasks.max_parallel`) in the parsed YAML:
   - If the key is present and has a valid value, use it.
   - If the key is missing, use the documented default.
5. CLI arguments take precedence over file settings: `--max-parallel` overrides `run-tasks.max_parallel`.

**Edge cases**:
- **No settings file**: All 5 defaults used silently — not an error.
- **Partial settings** (some keys present, others missing): Use parsed values for present keys, defaults for missing keys.
- **Malformed YAML**: Use all defaults, log warning, continue execution.
- **Empty frontmatter** (just `---\n---`): Treated as no settings — all defaults used.

**Model settings are applied in Step 5** when spawning agents. See the claude-code-teams reference for model tier semantics (Opus for complex reasoning, Sonnet for parallel work).

**Example `.claude/agent-alchemy.local.md`**:
```yaml
---
run-tasks.max_parallel: 3
run-tasks.max_retries: 2
run-tasks.wave_lead_model: opus
run-tasks.context_manager_model: sonnet
run-tasks.executor_model: opus
---
```

### 2b: Topological Wave Assignment

Build a dependency graph from the filtered task set and assign tasks to waves using topological sorting:

**Algorithm**:

1. Collect all non-completed tasks from the filtered set.
2. For each task, determine its `blockedBy` dependencies. Treat already-completed blockers as satisfied (ignore them).
3. **Wave 1**: All tasks with no unsatisfied `blockedBy` dependencies (empty blockedBy list, or all blockers already completed).
4. **Wave 2**: Tasks whose ALL unsatisfied blockers are assigned to Wave 1.
5. **Wave N**: Tasks whose ALL unsatisfied blockers are assigned to waves 1 through N-1.
6. Continue until all tasks are assigned to a wave, or remaining tasks form circular dependencies (handled in Step 1c).

**Wave capping**: If a wave contains more tasks than `max_parallel`, split into sub-waves of `max_parallel` size, maintaining priority ordering. Sub-waves execute sequentially within the logical wave boundary. For display purposes, sub-waves are shown as `Wave N.1`, `Wave N.2`, etc.

### 2c: Within-Wave Priority Sort

Within each wave (or sub-wave), sort tasks by:

1. **Priority tier** (descending importance):
   - `critical` — first
   - `high` — second
   - `medium` — third
   - `low` — fourth
   - Tasks without `metadata.priority` or with unrecognized values — last

2. **Tie-breaking — "unblocks most others"**: Among tasks with the same priority, sort by the number of other tasks that list this task in their `blockedBy` field (descending). Tasks that unblock more downstream work execute first.

3. **Final tie-breaking — task ID**: If priority and unblock count are equal, lower task ID goes first (stable ordering).

### 2d: Build Execution Plan

Assemble the complete execution plan with:

- Total task count (pending tasks to execute)
- Wave count (number of waves, including sub-waves)
- Per-wave task list with: task ID, subject, priority, dependencies (if any)
- Already-completed task count (for context)
- Blocked task list (tasks that cannot be scheduled due to unresolved external dependencies)
- Settings summary (max_parallel, max_retries, model tiers)
- Any circular dependency warnings from Step 1c

---

## Step 3: Confirm

```
Input:  Execution plan from Step 2
Output: User confirmation, --dry-run exit, or user cancellation
```

### 3a: Display Execution Plan

Present the execution plan to the user. Include all information needed for an informed decision:

```
EXECUTION PLAN
==============
Tasks to execute: {count}
Completed: {completed_count} (already done)
Blocked: {blocked_count} (unresolvable dependencies)

Settings:
  Max parallel: {max_parallel}
  Max retries: {max_retries}
  Wave lead model: {wave_lead_model}
  Context manager model: {context_manager_model}
  Executor model: {executor_model}

{If circular dependency warnings exist:}
WARNINGS:
  {circular dependency warning from Step 1c}

WAVE 1 ({n} tasks, team: 1 wave-lead + 1 context-mgr + {n} executors):
  1. [{id}] {subject} ({priority})
  2. [{id}] {subject} ({priority})
  ...

WAVE 2 ({n} tasks, team: 1 wave-lead + 1 context-mgr + {n} executors):
  3. [{id}] {subject} ({priority}) -- after [{dep_ids}]
  4. [{id}] {subject} ({priority}) -- after [{dep_ids}]
  ...

{Additional waves...}

{If blocked tasks exist:}
BLOCKED (cannot be scheduled):
  [{id}] {subject} -- blocked by: [{blocker_ids}]
  ...
```

### 3b: Handle --dry-run

If `--dry-run` was specified:

1. Display the full execution plan (same format as 3a).
2. Report: `Dry run complete. No tasks were modified and no session was created.`
3. Exit immediately. Do NOT:
   - Call `TaskUpdate` on any task
   - Create any session directory or files
   - Spawn any agents or teams

### 3c: Request User Confirmation

If NOT `--dry-run`, present the plan via `AskUserQuestion` and ask for confirmation:

```yaml
questions:
  - header: "Confirm Execution"
    question: "Ready to execute {count} tasks in {wave_count} waves?"
    options:
      - label: "Yes, start execution"
        description: "Proceed with the execution plan above. {wave_count} wave teams will be spawned ({wave_lead_model} wave-leads, {context_manager_model} context managers, {executor_model} executors)."
      - label: "Cancel"
        description: "Abort without executing or modifying any tasks"
    multiSelect: false
```

**If the user selects "Cancel"**:
```
Execution cancelled. No tasks were modified.
```
Stop execution. Do not proceed to Step 4 or any subsequent steps.

**If the user selects "Yes, start execution"**:
Proceed to Step 4 (Initialize Session).

---

## Step 4: Initialize Session

```
Input:  Task group name (from --task-group or inferred), timestamp
Output: Session directory with initial files, session ID
```

### 4a: Generate Session ID

Build the session ID from the task group and current timestamp:

- If `--task-group` was provided: `{task-group}-{YYYYMMDD}-{HHMMSS}`
- If no `--task-group` but all open tasks share the same `metadata.task_group`: use that group name with the same format
- Otherwise: `exec-session-{YYYYMMDD}-{HHMMSS}`

Store the session ID for use in Step 6 (archive path).

**Examples**:
```
--task-group auth-feature  →  auth-feature-20260223-143022
(all tasks share group "payments")  →  payments-20260223-143022
(mixed groups, no --task-group)  →  exec-session-20260223-143022
```

### 4b: Check for Existing Session

Check whether `.claude/sessions/__live_session__/` exists and contains files. Detection is based on directory content presence — there is no `.lock` file in the new engine.

**If `__live_session__/` has content** (interrupted session detected):

Present the user with a choice via `AskUserQuestion`:

```yaml
questions:
  - header: "Interrupted Session Detected"
    question: "An existing session was found in __live_session__/. How would you like to proceed?"
    options:
      - label: "Resume"
        description: "Reset any in_progress tasks to pending and continue from the next unblocked wave."
      - label: "Fresh start"
        description: "Archive the interrupted session and start a new one."
    multiSelect: false
```

**If the user selects "Resume"**:

1. Read the existing `execution_context.md` and `task_log.md` to understand prior progress.
2. Find all tasks with status `in_progress` via `TaskList`.
3. Reset each `in_progress` task to `pending` via `TaskUpdate`.
4. Log the reset:
   ```
   Resumed interrupted session. Reset {count} in_progress task(s) to pending:
   - [{id}] {subject}
   - [{id}] {subject}
   ```
5. Continue to Step 5 (Execute Waves) — the existing session directory and files are reused.

**If the user selects "Fresh start"**:

1. Generate an archive timestamp: `YYYYMMDD-HHMMSS` (current time).
2. Move all contents of `.claude/sessions/__live_session__/` to `.claude/sessions/interrupted-{timestamp}/`.
3. Reset any `in_progress` tasks from the interrupted session to `pending` via `TaskUpdate`.
4. Log the archival:
   ```
   Archived interrupted session to .claude/sessions/interrupted-{timestamp}/.
   Reset {count} in_progress task(s) to pending.
   ```
5. Continue to Step 4c (create fresh session files).

**If `__live_session__/` is empty or does not exist**:

Continue to Step 4c.

### 4c: Create Session Directory

Create `.claude/sessions/__live_session__/` (if it does not already exist) and populate it with the initial session files:

**1. `execution_context.md`** — Empty template:

```markdown
# Execution Context
```

This file will be populated by the orchestrator after each wave with learnings from wave-lead summaries.

**2. `task_log.md`** — Header row only:

```markdown
# Task Log

| Task | Subject | Wave | Status | Attempts | Duration |
|------|---------|------|--------|----------|----------|
```

Updated by the orchestrator after each wave with per-task results from the wave summary.

**3. `execution_plan.md`** — Populated from the Step 2 plan:

```markdown
# Execution Plan

**Task Group**: {task_group or "mixed"}
**Total Tasks**: {count}
**Total Waves**: {wave_count}
**Max Parallel**: {max_parallel}
**Generated**: {ISO 8601 timestamp}

## Wave 1 ({n} tasks)
| Task | Subject | Priority | Complexity |
|------|---------|----------|------------|
| #{id} | {subject} | {priority} | {complexity} |
...

## Wave 2 ({n} tasks)
| Task | Subject | Priority | Complexity | Blocked By |
|------|---------|----------|------------|------------|
| #{id} | {subject} | {priority} | {complexity} | #{dep_ids} |
...
```

**4. `progress.jsonl`** — Session start event:

```jsonl
{"ts":"{ISO 8601 timestamp}","event":"session_start","task_group":"{task_group}","total_tasks":{count},"total_waves":{wave_count}}
```

**Progress event writing is best-effort** — failures do not affect execution flow. All event writes throughout the orchestration loop (session_start, wave_start, task_complete, wave_complete, session_complete) follow this principle: if an append to `progress.jsonl` fails for any reason (permissions, disk full, etc.), log a warning and continue execution normally. Progress events are informational — they must never interrupt the execution pipeline.

### 4d: Emit Session Start

Report the session initialization:

```
Session initialized: .claude/sessions/__live_session__/
Session ID: {session_id}
Files created: execution_context.md, task_log.md, execution_plan.md, progress.jsonl

Execution plan: {total_tasks} tasks across {total_waves} waves (max {max_parallel} parallel)
```

Proceed to Step 5.

---

## Step 5: Execute Waves

```
Input:  Execution plan, session directory, settings (max_parallel, max_retries, model tiers)
Output: Per-wave results in task_log.md, updated execution_context.md
Loop:   Repeats until no more unblocked tasks remain
```

### 5a: Identify Unblocked Tasks

Before each wave iteration, refresh the task list via `TaskList` to pick up status changes from prior waves. Identify unblocked tasks: tasks whose status is `pending` and whose `blockedBy` dependencies are all `completed`.

**Wave with 0 unblocked tasks after filtering**: If all remaining non-completed tasks are blocked (and no circular dependency can be broken), the wave loop terminates. This can happen if prior wave failures left downstream tasks permanently blocked.

### 5b: Write Wave Start Event

Append a `wave_start` event to `progress.jsonl`:

```jsonl
{"ts":"{ISO 8601 timestamp}","event":"wave_start","wave":{N},"task_count":{count}}
```

Emit a human-readable progress message:

```
Starting Wave {N}/{total_waves}: {count} tasks...
```

### 5c: Create Wave Team

Create a wave team via `TeamCreate` following the claude-code-teams lifecycle (Creation → Member Spawning → Coordination → Shutdown → Cleanup). Team name: `wave-{N}-{session_id}`.

Team composition: 1 wave-lead (foreground, `wave_lead_model` tier) + N task executors (managed by wave-lead, `executor_model` tier). The orchestrator does not directly interact with executors.

**TeamCreate failure handling**:

If `TeamCreate` fails:
1. Retry once after a brief pause (3-5 seconds).
2. If the retry also fails, mark all wave tasks as `failed` via `TaskUpdate` with reason "team creation failed."
3. Present the failure to the user via `AskUserQuestion`:

```yaml
questions:
  - header: "Wave Team Creation Failed"
    question: "Failed to create agent team for Wave {N} after retry. {count} tasks affected."
    options:
      - label: "Retry wave"
        description: "Attempt to create the wave team again"
      - label: "Skip wave"
        description: "Skip these tasks and continue with the next wave"
      - label: "Abort session"
        description: "Stop execution entirely"
    multiSelect: false
```

Handle the user's choice accordingly:
- **Retry wave**: Go back to 5c (create team again).
- **Skip wave**: Log the skipped tasks in `task_log.md`, proceed to next wave iteration.
- **Abort session**: Proceed directly to Step 6 (Summarize & Archive) with partial results.

### 5d: Launch Wave Lead

Spawn the wave-lead as a foreground Task with the `team_name` parameter (see claude-code-teams spawning conventions). The wave-lead runs to completion, managing all executors and collecting results before reporting back.

Construct the wave-lead prompt using the **Protocol 1: Orchestrator to Wave Lead** format from `communication-protocols.md`:

```
WAVE ASSIGNMENT
Wave: {N} of {total_waves}
Max Parallel: {max_parallel}
Max Retries: {max_retries}
Session Dir: {absolute path to .claude/sessions/__live_session__/}
Context Manager Model: {context_manager_model}
Executor Model: {executor_model}

TASKS:
- Task #{id}: {subject}
  Description: {full task description including acceptance criteria}
  Priority: {priority}
  Complexity: {complexity or "not specified"}
  Metadata: {key=value pairs for spec_path, task_group, spec_phase if present}

- Task #{id}: {subject}
  ...

CROSS-WAVE CONTEXT:
{Summary of execution_context.md content from prior waves.
 For Wave 1: omit this section entirely if no prior context exists.
 For Wave 2+: include wave-by-wave learnings, key decisions, and known issues.}
```

**Cross-Wave Context Bridge** (bridges knowledge between waves):

The Context Manager handles within-wave context distribution; the orchestrator is responsible for bridging context across waves. Before spawning each wave-lead, the orchestrator constructs the `CROSS-WAVE CONTEXT` section:

1. Read `.claude/sessions/__live_session__/execution_context.md`.
2. **Wave 1 (no prior context)**: If the file contains only the `# Execution Context` header or is empty, omit the `CROSS-WAVE CONTEXT` section entirely from the wave-lead prompt.
3. **Wave 2+ (prior context exists)**: If the file contains content beyond the header (wave sections from prior waves), construct a concise summary:
   - **Per-wave task outcomes**: For each prior wave, list task IDs with their statuses (e.g., `Wave 1: #1 (PASS), #2 (PASS), #3 (FAIL)`).
   - **Accumulated learnings**: Merge the `### Learnings` subsections from all prior waves into a deduplicated bullet list. Prioritize learnings relevant to the current wave's tasks (file patterns, conventions, tech stack details).
   - **Key decisions**: Merge the `### Key Decisions` subsections from all prior waves. Include the task ID that made each decision for traceability.
   - **Known issues**: Merge the `### Issues` subsections from all prior waves. Exclude issues that were subsequently resolved (i.e., a later wave's learnings explicitly note resolution).
   - **Keep the summary concise**: Target 30-60 lines total. If prior waves produced extensive context, summarize aggressively — the Context Manager within the wave will provide full detail to individual executors.
4. Include the summary in the `CROSS-WAVE CONTEXT` section of the wave-lead prompt.

**Example cross-wave context for Wave 3**:

```
CROSS-WAVE CONTEXT:
Wave 1 completed: #1 (PASS), #2 (PASS), #3 (FAIL), #4 (PASS)
Wave 2 completed: #5 (PASS), #6 (PASS)

Learnings:
- Runtime: Node.js 22 with pnpm
- Tests: vitest with `__tests__/{name}.test.ts` pattern
- Middleware pattern: `src/middleware/{name}.ts` with co-located tests
- API routes follow `src/api/{resource}/route.ts` pattern

Key Decisions:
- [Task #1] Used Zod for runtime validation
- [Task #2] Shared types in `src/types/` directory
- [Task #4] Used middleware pattern for auth validation

Issues:
- Vitest mock.calls behavior differs from Jest -- reset between tests
```

### 5e: Wait for Wave Lead Completion

The wave-lead runs as a foreground `Task`, so the orchestrator blocks until it completes. The wave-lead sends its results via `SendMessage` using the **Protocol 2: Wave Lead to Orchestrator** format from `communication-protocols.md`.

The orchestrator receives the wave summary containing:
- Per-task results (status, duration, summary, files modified)
- Failed task details for escalation (if any)
- Context updates from this wave

**Wave-Lead Crash Recovery**:

"Crash" includes: agent timeout, unexpected termination, Task tool returning an error, or malformed/unparseable response that does not conform to Protocol 2.

**First crash — automatic recovery (no user intervention)**:

1. **Identify affected tasks**: Read `TaskList` to find tasks assigned to this wave. Categorize each:
   - **Completed**: Tasks with status `completed` — these are preserved as-is. The wave-lead called `TaskUpdate` to mark them completed before the crash occurred.
   - **In-progress**: Tasks with status `in_progress` — these need reset.
   - **Pending**: Tasks with status `pending` that were assigned to this wave but never started — these are included in the retry.
2. **Reset in-progress tasks**: For each `in_progress` task, call `TaskUpdate` to set status back to `pending`.
3. **Build retry task list**: Collect all tasks that are now `pending` (reset tasks + tasks that were never started). If all wave tasks were already completed before the crash, skip retry — there is nothing to retry.
4. **Clean up failed team** (aggressive — skip cooperative shutdown in crash scenarios):
   a. Read `~/.claude/teams/{wave-team-name}/config.json` to enumerate all team members.
   b. Force-stop ALL members via `TaskStop` immediately (in crash scenarios, agents are likely unresponsive — go directly to force-stop without attempting cooperative shutdown).
   c. Wait 3 seconds for terminations to propagate.
   d. Call `TeamDelete`.
   e. If `TeamDelete` fails: force-stop ALL members via `TaskStop` again, wait 5 seconds, retry `TeamDelete`.
   f. If `TeamDelete` still fails after 2 attempts: log a warning and proceed. The new wave team (Step 6) will use a different team name, so lingering agents from the crashed team should not interfere. Log the failure in `progress.jsonl`:
      ```jsonl
      {"ts":"{ISO 8601}","event":"crash_cleanup_failed","wave":{N},"team":"{wave-team-name}"}
      ```
   g. If config.json cannot be read (team directory already gone): skip member enumeration, attempt `TeamDelete` directly, proceed if it fails (team may already be cleaned up).
5. **Log the crash**: Append a note to `task_log.md`:
   ```
   | -- | Wave {N} lead crashed | {N} | CRASH | -- | -- |
   ```
   Write a `wave_lead_crash` event to `progress.jsonl`:
   ```jsonl
   {"ts":"{ISO 8601}","event":"wave_lead_crash","wave":{N},"completed_preserved":{count},"tasks_reset":{count},"retry":true}
   ```
6. **Spawn new wave team**: Go back to Step 5c with the retry task list (not the original wave — only unfinished tasks). This is a fresh team with a new wave-lead.

**Second crash — user escalation**:

If the retry wave-lead also crashes (same detection criteria), the orchestrator does NOT retry again automatically. Instead:

1. Reset any `in_progress` tasks to `pending` (same as first crash).
2. Clean up the failed retry team using the same aggressive procedure as the first crash (item 4 above): read config.json, force-stop ALL members via `TaskStop`, wait 3 seconds, `TeamDelete`, retry once if needed.
3. Escalate to the user via `AskUserQuestion`:

```yaml
questions:
  - header: "Wave Lead Crash"
    question: "Wave {N} lead agent crashed twice. {count} task(s) are affected.\nCompleted before crash: {completed_list or 'none'}\nUnfinished tasks: {pending_list}"
    options:
      - label: "Retry wave"
        description: "Attempt one more time with a fresh wave team"
      - label: "Skip wave"
        description: "Skip these tasks and continue with remaining waves (dependent tasks may be blocked)"
      - label: "Abort session"
        description: "Stop execution entirely"
    multiSelect: false
```

Handle the user's choice:

- **Retry wave**: Go back to Step 5c with the pending task list. If this third attempt also crashes, escalate to the user again with the same 3 options (no automatic retry limit on user-initiated retries).
- **Skip wave**: Mark all pending wave tasks as `failed` via `TaskUpdate` with reason "skipped (wave-lead crash)". Log each in `task_log.md`. Continue to Step 5g (delete team) and Step 5h (loop). Downstream tasks that depend on skipped tasks will remain blocked — the orchestrator will detect this in 5h and report stalled execution if no other unblocked tasks exist.
- **Abort session**: Proceed directly to Step 6 (Summarize & Archive) with partial results.

**TeamCreate failure during crash recovery**:

If `TeamCreate` fails while attempting to spawn a replacement wave team (Step 5c retry after crash):

1. Do not retry `TeamCreate` again (the standard 5c retry already handles one `TeamCreate` retry).
2. Escalate to the user immediately via `AskUserQuestion` with the same 3 options as the second crash (Retry wave / Skip wave / Abort session).

### 5f: Process Wave Summary

After receiving the wave summary from the wave-lead:

**1. Update `task_log.md`**:

Read the current `task_log.md`, then append a row for each task in the wave summary:

```markdown
| #{id} | {subject} | {wave_number} | {status} | {attempts} | {duration} |
```

Write the complete updated file (read-modify-write pattern).

**2. Write `task_complete` events to `progress.jsonl`**:

For each task in the wave summary, append a `task_complete` event:

```jsonl
{"ts":"{ISO 8601 timestamp}","event":"task_complete","wave":{N},"task_id":"{id}","status":"{PASS|FAIL|PARTIAL}","duration_s":{seconds}}
```

Write one event per task, in the order they appear in the wave summary. Best-effort — if a write fails, log a warning and continue processing the remaining tasks.

**3. Write `wave_complete` event to `progress.jsonl`**:

```jsonl
{"ts":"{ISO 8601 timestamp}","event":"wave_complete","wave":{N},"tasks_passed":{count},"tasks_failed":{count},"duration_s":{seconds}}
```

**4. Update `execution_context.md`**:

If the wave summary includes a `CONTEXT UPDATES` section, append a new wave section to `execution_context.md`:

```markdown
---

## Wave {N}
**Completed**: {ISO 8601 timestamp}
**Tasks**: #{id1} ({status}), #{id2} ({status}), ...

### Learnings
{learnings from the wave summary CONTEXT UPDATES}

### Key Decisions
{decisions from the wave summary, if any}

### Issues
{issues from the wave summary, if any — or "None"}
```

Write the complete updated file (read-modify-write pattern).

**5. Emit wave completion summary**:

```
Wave {N}/{total_waves} complete: {passed} passed, {failed} failed ({duration})
  - #{id} {subject}: {status} ({duration})
  - #{id} {subject}: {status} ({duration})
  ...
```

**6. Handle Tier 3 escalations**:

If the wave summary includes a `FAILED TASKS (for escalation)` section, these are tasks that exhausted Tier 1 and Tier 2 retries within the wave-lead. The orchestrator must present each failed task to the user individually.

**Multiple failed tasks**: If the wave has multiple failed tasks, escalate each one sequentially via separate `AskUserQuestion` calls. Process them in task ID order (lowest first). The user's decision on one task does not affect the options for other tasks — except "Abort session", which immediately terminates and skips remaining escalations.

For each escalated task, use `AskUserQuestion`:

```yaml
questions:
  - header: "Task Failed After Retries"
    question: "Task #{id} '{subject}' failed after {attempts} attempts.\n\nFailure reason: {failure_reason}\nTier 1 retry: {tier1_outcome}\nTier 2 retry: {tier2_outcome}\n\n{If task has downstream dependents:}\nNote: {count} downstream task(s) depend on this task: [{dependent_ids}]"
    options:
      - label: "Fix manually and continue"
        description: "I'll fix the issue myself. Mark the task as completed (manual) after I confirm."
      - label: "Skip this task"
        description: "Skip this task and continue with remaining execution."
      - label: "Provide guidance"
        description: "I'll provide instructions for a guided retry."
      - label: "Abort session"
        description: "Stop execution entirely."
    multiSelect: false
```

Handle the user's choice:

**Option 1: Fix manually and continue**

1. Present a follow-up `AskUserQuestion` to confirm the fix:

```yaml
questions:
  - header: "Manual Fix Confirmation"
    question: "Task #{id} '{subject}' -- confirm when your manual fix is complete."
    options:
      - label: "Fix is done"
        description: "Mark the task as completed and continue execution."
      - label: "Cancel"
        description: "Go back to the escalation options for this task."
    multiSelect: false
```

2. If the user selects "Fix is done": mark the task as `completed` via `TaskUpdate`. Log in `task_log.md` as status `PASS (manual)`. Continue to the next escalated task (or proceed to 5g if no more escalations).
3. If the user selects "Cancel": re-present the original 4-option escalation for this task.

**Option 2: Skip this task**

1. Mark the task as `failed` via `TaskUpdate` (it remains in failed status).
2. Log in `task_log.md` as status `SKIPPED (user)`.
3. **Warn about dependent tasks**: Check the full task list for tasks whose `blockedBy` includes the skipped task ID. If any exist, warn the user:
   ```
   Skipped task #{id}. The following downstream tasks are now blocked and cannot execute:
   - [{dep_id}] {dep_subject}
   - [{dep_id}] {dep_subject}
   These tasks will remain pending unless their other dependencies are met through alternative means.
   ```
   This is informational only — do not ask for additional confirmation. Continue to the next escalated task.
4. Continue execution with remaining waves. Downstream tasks that exclusively depend on the skipped task will remain blocked and will be reported as stalled in Step 5h.

**Option 3: Provide guidance**

1. Prompt the user for guidance text via `AskUserQuestion`:

```yaml
questions:
  - header: "Provide Guidance for Task #{id}"
    question: "Enter your guidance for retrying task #{id} '{subject}'.\n\nOriginal failure: {failure_reason}\nInclude any specific instructions, hints, or approaches the executor should try."
    options:
      - label: "Submit guidance"
        description: "Launch a guided retry with the instructions above."
    freeformLabel: "Guidance"
    multiSelect: false
```

2. Spawn a new single-task executor agent (not through the wave-lead, since the wave has already completed) with an enriched prompt containing:
   - The original task description and acceptance criteria
   - The failure context from the original attempt (failure reason, tier outcomes)
   - The user's guidance text
   - The current `execution_context.md` content (for project context)

   Use a fresh `Task` call (foreground, not background) to run the guided executor. The executor follows the standard 4-phase workflow (Understand, Implement, Verify, Report).

3. **If the guided retry succeeds** (executor reports PASS): Mark the task as `completed` via `TaskUpdate`. Log in `task_log.md` as status `PASS (guided)`. Continue to the next escalated task.

4. **If the guided retry fails** (executor reports FAIL or PARTIAL): Re-prompt the user with the same 4-option escalation, but include the guided retry outcome in the question:

```yaml
questions:
  - header: "Guided Retry Also Failed"
    question: "Task #{id} '{subject}' failed again after guided retry.\n\nOriginal failure: {original_failure_reason}\nGuided retry failure: {guided_failure_reason}\nYour guidance was: {user_guidance_summary}"
    options:
      - label: "Fix manually and continue"
        description: "I'll fix the issue myself."
      - label: "Skip this task"
        description: "Skip this task and continue."
      - label: "Provide guidance"
        description: "I'll provide new instructions for another retry."
      - label: "Abort session"
        description: "Stop execution entirely."
    multiSelect: false
```

   This creates a loop: the user can keep providing guidance (each attempt spawns a new executor), switch to manual fix, skip, or abort at any point. There is no automatic limit on guided retry attempts — the user controls when to stop.

**Option 4: Abort session**

1. If there are remaining escalated tasks in the queue (multiple failures in this wave), skip them — do not present further escalation prompts.
2. Mark all remaining non-completed tasks as `failed` via `TaskUpdate` with reason "session aborted by user".
3. Log each as `ABORTED` in `task_log.md`.
4. Proceed directly to Step 6 (Summarize & Archive) with partial results. Do not execute any remaining waves.

**Abort during crash recovery**: If the user selects "Abort session" during a crash recovery escalation (from Step 5e), the same abort procedure applies: mark remaining tasks as failed, proceed to Step 6.

### 5g: Cleanup and Delete Wave Team

After processing the wave summary (Step 5f), execute the full team cleanup lifecycle. This step ensures ALL agents from the wave are terminated before proceeding, regardless of whether the wave-lead's internal cleanup (Step 6b) succeeded. Do NOT trust the wave-lead's self-reported cleanup — verify independently.

#### 5g-1: Shutdown the Wave-Lead

1. Send `shutdown_request` to the wave-lead via `SendMessage`.
2. Wait up to 10 seconds for a `shutdown_response` with `approve: true`.
3. If the wave-lead does not respond within 10 seconds, force-stop it via `TaskStop`.

The wave-lead should respond quickly since it has already sent its WAVE SUMMARY and is in Step 9 (awaiting shutdown). The 10-second timeout accounts for message delivery latency and any final processing.

#### 5g-2: Verify All Sub-Agents Are Stopped (Defense in Depth)

After the wave-lead is terminated, verify that ALL sub-agents are also stopped. The wave-lead's Step 6b may have partially or fully succeeded — this step catches any survivors.

1. Read the team config file at `~/.claude/teams/{wave-team-name}/config.json`.
2. Extract the `members` array to get all registered team members (names and agent IDs).
3. For each member that is NOT the wave-lead (i.e., task executors, retry executors, and the context manager):
   a. Send a `shutdown_request` via `SendMessage`.
   b. Wait 5 seconds total for all responses (batch wait, not 5 seconds per agent).
   c. For any agent that did not respond with `approve: true` within 5 seconds, force-stop it via `TaskStop`.
4. Log the cleanup results:
   - How many agents responded cooperatively (wave-lead already handled them or they responded to orchestrator's request)
   - How many agents required force-stop by the orchestrator
   - How many agents could not be contacted (SendMessage failed — likely already terminated)

**Handling SendMessage failures during cleanup:**
- If `SendMessage` fails for an agent (inbox already cleaned up, agent already terminated), this is expected — the agent is likely already gone. Proceed to `TaskStop` for safety. If `TaskStop` also fails (agent not found), count that agent as already terminated.
- Do not treat SendMessage/TaskStop errors on already-terminated agents as failures.

**Handling config.json read failure:**
- If the team config file cannot be read (deleted, corrupted, or team directory already cleaned up), skip the member enumeration and proceed directly to Step 5g-3 (TeamDelete). If TeamDelete also fails, fall through to the retry logic.

#### 5g-3: Delete the Wave Team

After all agents are verified stopped:

1. Call `TeamDelete`.
2. If `TeamDelete` succeeds: proceed to Step 5g-4.
3. If `TeamDelete` fails (active members still detected):
   a. **Round 2**: Force-stop ALL members via `TaskStop` (re-read config.json if needed, or use the member list from 5g-2). Wait 3 seconds for terminations to propagate. Retry `TeamDelete`.
   b. **Round 3**: Wait 5 seconds. Force-stop ALL members via `TaskStop` one more time. Retry `TeamDelete`.
   c. **Escalation**: If `TeamDelete` still fails after 3 total attempts, escalate to the user:

```yaml
questions:
  - header: "Wave Cleanup Failed"
    question: "Failed to delete the Wave {N} team after 3 cleanup attempts. Some agents may still be active."
    options:
      - label: "Force retry"
        description: "Attempt one more aggressive cleanup (force-stop all agents + delete team)"
      - label: "Skip cleanup and continue"
        description: "Proceed to the next wave without deleting this team (next wave uses a different team name)"
      - label: "Abort session"
        description: "Stop execution entirely and archive partial results"
    multiSelect: false
```

Handle the user's choice:
- **Force retry**: Repeat the full 5g-2 + 5g-3 sequence one more time. If it still fails after this final attempt, abort the session (proceed to Step 6).
- **Skip cleanup and continue**: Log a warning in `task_log.md` and `progress.jsonl`. Proceed to Step 5h. The next wave uses a different team name, so lingering agents from the old team will not interfere with the new team's communication. However, they will consume resources until they eventually time out or are cleaned up externally.
- **Abort session**: Proceed to Step 6 (Summarize & Archive).

#### 5g-4: Log Cleanup Results

Write a `wave_cleanup` event to `progress.jsonl`:

```jsonl
{"ts":"{ISO 8601}","event":"wave_cleanup","wave":{N},"agents_cooperative":{count},"agents_forced":{count},"agents_already_stopped":{count},"team_deleted":{true|false}}
```

### 5h: Inter-Wave Transition

Before checking for remaining work, verify the previous wave is fully cleaned up:

1. **Verify team is gone**: Confirm that `~/.claude/teams/{previous-wave-team-name}/` directory no longer exists (or `config.json` is absent). If it still exists:
   - Log a warning: "Previous wave team directory still exists after cleanup."
   - Attempt one final `TeamDelete`. If it fails, proceed anyway — the next wave uses a different team name.

2. **Brief cooldown**: Wait 2 seconds between waves. This ensures any asynchronous cleanup (inbox file deletion, process termination) has time to complete before the next wave's `TeamCreate`.

3. **Check for remaining work**:
   a. Refresh the task list via `TaskList`.
   b. Identify newly unblocked tasks (tasks that were blocked by wave tasks that just completed).
   c. If unblocked tasks exist: return to Step 5a for the next wave.
   d. If no unblocked tasks remain:
      - If all non-completed tasks are blocked (dependencies not met): log that execution is stalled due to failed dependencies and exit the loop.
      - If all tasks are completed: exit the loop normally.

Proceed to Step 6.

---

## Step 6: Summarize & Archive

```
Input:  task_log.md, execution_context.md, progress.jsonl
Output: session_summary.md, archived session directory
```

### 6a: Generate Session Summary

Read `task_log.md` and `execution_context.md` to build a comprehensive session report. Write `session_summary.md` to `.claude/sessions/__live_session__/`:

```markdown
# Session Summary

**Session ID**: {session_id}
**Task Group**: {task_group or "mixed"}
**Started**: {ISO 8601 timestamp from session_start event}
**Completed**: {ISO 8601 timestamp now}
**Total Duration**: {human-readable duration}

## Results

| Metric | Count |
|--------|-------|
| Total Tasks | {total} |
| Passed | {pass_count} |
| Failed | {fail_count} |
| Partial | {partial_count} |
| Skipped | {skipped_count} |

## Per-Wave Breakdown

### Wave 1
- Duration: {duration}
- Tasks: {passed} passed, {failed} failed
- #{id} {subject}: {status} ({duration})
- #{id} {subject}: {status} ({duration})

### Wave 2
- Duration: {duration}
- Tasks: {passed} passed, {failed} failed
- #{id} {subject}: {status} ({duration})

{Additional waves...}

## Failed Tasks

{If no failures: "None -- all tasks passed."}

{If failures exist:}
| Task | Subject | Wave | Reason |
|------|---------|------|--------|
| #{id} | {subject} | {wave} | {failure reason} |

## Key Decisions

{Extracted from execution_context.md Key Decisions sections across all waves.
 If none: "No significant decisions recorded."}

## Learnings

{Extracted from execution_context.md Learnings sections across all waves.
 If none: "No significant learnings recorded."}
```

### 6b: Write Session Complete Event

Append the final event to `progress.jsonl`:

```jsonl
{"ts":"{ISO 8601 timestamp}","event":"session_complete","total_passed":{pass_count},"total_failed":{fail_count},"total_duration_s":{seconds}}
```

### 6c: Display Summary

Present the session results to the user:

```
SESSION COMPLETE
================
Session: {session_id}
Duration: {total_duration}
Results: {pass_count} passed, {fail_count} failed, {partial_count} partial, {skipped_count} skipped

{If failures:}
Failed tasks:
- [{id}] {subject}: {reason}
```

### 6d: Archive Session

Move the completed session from the live directory to its permanent archive:

1. Create the archive directory: `.claude/sessions/{session-id}/`
2. Move all files from `.claude/sessions/__live_session__/` to `.claude/sessions/{session-id}/`.
3. Leave `.claude/sessions/__live_session__/` as an empty directory (ready for the next session).

**Archive race condition**: If `.claude/sessions/{session-id}/` already exists (extremely unlikely — would require two sessions with the same timestamp), append a counter: `{session-id}-2`, `{session-id}-3`, etc.

---

## Step 7: Finalize

```
Input:  execution_context.md (from archived session), CLAUDE.md
Output: CLAUDE.md edits (if warranted)
```

### 7a: Review Execution Context

Read the archived `execution_context.md` from `.claude/sessions/{session-id}/execution_context.md` and evaluate whether any learnings represent **project-wide changes** that should be reflected in `CLAUDE.md`.

**Changes that warrant CLAUDE.md updates**:
- New dependencies added to the project (e.g., new libraries installed)
- New patterns established that other developers or agents should follow
- Architecture decisions that affect the project structure
- New commands or build steps discovered
- New configuration requirements
- Structural changes to the repository (new directories, renamed files)

**Changes that do NOT warrant CLAUDE.md updates**:
- Task-specific implementation details
- Internal agent learnings (file locations for a specific feature)
- Workarounds for one-time issues
- Test-specific patterns that are obvious from the test files themselves

### 7b: Update CLAUDE.md

If meaningful changes were identified:

1. Read the current `CLAUDE.md`.
2. Identify the appropriate sections to update (e.g., Development Commands, Architecture Patterns, Conventions).
3. Make targeted edits — add or modify only the specific entries that changed.
4. Do not rewrite unrelated sections.

Report what was updated:
```
Updated CLAUDE.md:
- Added {description of change}
- Updated {description of change}
```

If no meaningful changes were identified:
```
No CLAUDE.md updates needed. All learnings were task-specific.
```

### 7c: Final Report

Report that execution is fully complete:

```
Execution complete. Session archived to .claude/sessions/{session-id}/.
```
