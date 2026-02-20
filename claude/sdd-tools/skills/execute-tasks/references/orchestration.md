# Orchestration Reference

This reference provides the detailed 10-step orchestration loop for executing Claude Code Tasks in dependency order. The execute-tasks skill uses this procedure to manage the full execution session.

## File Operation Guidelines

All orchestrator writes to session artifacts (`execution_context.md`, `task_log.md`, `progress.md`) MUST use **Write** (full file replacement), never **Edit**. The Edit tool relies on exact string matching which becomes unreliable as these files grow during execution. Instead, use a **read-modify-write** pattern:

1. **Read** the current file contents
2. **Modify** in memory (append rows, update sections, etc.)
3. **Write** the complete updated file

This ensures atomic, reliable updates regardless of file size or content changes.

## Result File Protocol

### Purpose

Reduce orchestrator context consumption by moving agent result data to disk. Instead of embedding full agent output (~100+ lines per task) into the orchestrator's context window, agents write a compact result file (~18 lines) as their **very last action**. The orchestrator reads these files after polling for completion.

### File Format (Standard)

Agents write `result-task-{id}.md` in `.claude/sessions/__live_session__/`:

```markdown
# Task Result: [{id}] {subject}
status: PASS|PARTIAL|FAIL
attempt: {n}/{max}

## Verification
- Functional: {n}/{total}
- Edge Cases: {n}/{total}
- Error Handling: {n}/{total}
- Tests: {passed}/{total} ({failed} failures)

## Files Modified
- {path}: {brief description}

## Issues
{None or brief descriptions}
```

### Ordering Invariant

Agents MUST write files in this order:
1. `context-task-{id}.md` FIRST (learnings for context merge)
2. `result-task-{id}.md` LAST (completion signal for orchestrator polling)

The result file's existence serves as the completion signal. If it exists, the context file is guaranteed to exist (or the agent intentionally skipped it).

### Fallback

If an agent crashes before writing its result file, the orchestrator falls back to `TaskOutput` (blocking read of the background task's output) to diagnose the failure. This is the last-resort path and produces the same context pressure as the old foreground approach, but only for crashed agents.

## Step 1: Load Task List

Use `TaskList` to get all tasks and their current state.

If a `--task-group` argument was provided, filter the task list to only tasks where `metadata.task_group` matches the specified group. If no tasks match the group, inform the user and stop.

If a specific `task-id` argument was provided, validate it exists. If it doesn't exist, inform the user and stop.

## Step 2: Validate State

Handle edge cases before proceeding:

- **Empty task list**: Report "No tasks found. Use `/agent-alchemy-sdd:create-tasks` to generate tasks from a spec, or create tasks manually with TaskCreate." and stop.
- **All completed**: Report a summary of completed tasks and stop.
- **Specific task-id is blocked**: Report which tasks are blocking it and stop.
- **No unblocked tasks**: Report which tasks exist and what's blocking them. Detect circular dependencies and report if found.

## Step 3: Build Execution Plan

### 3a: Resolve Max Parallel

Determine the maximum number of concurrent tasks per wave using this precedence:
1. `--max-parallel` CLI argument (highest priority)
2. `max_parallel` setting in `.claude/agent-alchemy.local.md`
3. Default: 5

### 3b: Build Dependency Graph

Collect all tasks and build a dependency graph from `blockedBy` relationships.

If a specific `task-id` was provided, the plan contains only that task (single-task mode, effectively `max_parallel = 1`).

### 3c: Assign Tasks to Waves

Use topological sorting to assign tasks to dependency-based waves:
- **Wave 1**: All pending tasks with empty `blockedBy` list (no dependencies)
- **Wave 2**: Tasks whose dependencies are ALL in Wave 1
- **Wave 3**: Tasks whose dependencies are ALL in Wave 1 or Wave 2
- Continue until all tasks are assigned to waves

If task group filtering is active, only include tasks matching the specified group.

### 3d: Sort Within Waves

Within each wave, sort by priority:
1. `critical` tasks first
2. `high` tasks next
3. `medium` tasks next
4. `low` tasks last
5. Tasks without priority metadata last

Break ties by "unblocks most others" — tasks that appear in the most `blockedBy` lists of other tasks execute first.

If a wave contains more tasks than `max_parallel`, split into sub-waves of `max_parallel` size, maintaining the priority ordering.

### 3e: Circular Dependency Detection

Detect circular dependencies: if any tasks remain unassigned after topological sorting, they form a cycle. Report the cycle to the user and attempt to break at the weakest link (task with fewest blockers).

## Step 4: Check Settings

Read `.claude/agent-alchemy.local.md` if it exists, for any execution preferences.

This is optional — proceed without settings if not found.

## Step 5: Present Execution Plan and Confirm

Display the execution plan:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXECUTION PLAN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tasks to execute: {count}
Retry limit: {retries} per task
Max parallel: {max_parallel} per wave

WAVE 1 ({n} tasks):
  1. [{id}] {subject} ({priority})
  2. [{id}] {subject} ({priority})
  ...

WAVE 2 ({n} tasks):
  3. [{id}] {subject} ({priority}) — after [{dep_ids}]
  4. [{id}] {subject} ({priority}) — after [{dep_ids}]
  ...

{Additional waves...}

BLOCKED (unresolvable dependencies):
  [{id}] {subject} — blocked by: {blocker ids}
  ...

COMPLETED:
  {count} tasks already completed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

After displaying the plan, use AskUserQuestion to confirm:

```yaml
questions:
  - header: "Confirm Execution"
    question: "Ready to execute {count} tasks in {wave_count} waves (max {max_parallel} parallel) with up to {retries} retries per task?"
    options:
      - label: "Yes, start execution"
        description: "Proceed with the execution plan above"
      - label: "Cancel"
        description: "Abort without executing any tasks"
    multiSelect: false
```

If the user selects **"Cancel"**, report "Execution cancelled. No tasks were modified." and stop. Do not proceed to Step 5.5 or any subsequent steps.

## Step 5.5: Initialize Execution Directory

Generate a unique `task_execution_id` using three-tier resolution:
1. IF `--task-group` was provided → `{task_group}-{YYYYMMDD}-{HHMMSS}` (e.g., `user-auth-20260131-143022`)
2. ELSE IF all open tasks (pending + in_progress) share the same non-empty `metadata.task_group` → `{task_group}-{YYYYMMDD}-{HHMMSS}`
3. ELSE → `exec-session-{YYYYMMDD}-{HHMMSS}` (e.g., `exec-session-20260131-143022`)

### Clean Stale Live Session

Before creating new files, check if `.claude/sessions/__live_session__/` contains leftover files from a previous session (e.g., due to interruption):

1. Check if `.claude/sessions/__live_session__/` exists and contains any files
2. If files are found:
   - Create `.claude/sessions/interrupted-{YYYYMMDD}-{HHMMSS}/` using the current timestamp
   - Move all contents from `__live_session__/` to the interrupted archive folder
   - Log: `Archived stale session to .claude/sessions/interrupted-{YYYYMMDD}-{HHMMSS}/`
   - **Recover interrupted tasks**:
     1. Use `TaskList` to get all tasks
     2. Filter to tasks with status `in_progress`
     3. If an archived `task_log.md` exists, cross-reference: only reset tasks that appear in the log (they were part of the interrupted session)
     4. If no `task_log.md` available in the archive, reset ALL `in_progress` tasks (conservative approach)
     5. Reset matched tasks to `pending` via `TaskUpdate`
     6. Log each reset: `Reset interrupted task [{id}] "{subject}" from in_progress to pending`
     7. Log: `Recovered {n} interrupted tasks (reset to pending)`
3. If `__live_session__/` is empty or doesn't exist, proceed normally

### Concurrency Guard

Check for an active execution session before proceeding:

1. Check if `.claude/sessions/__live_session__/.lock` exists
2. If lock exists, read its timestamp:
   - If timestamp is **less than 4 hours old**: another session may be active. Use `AskUserQuestion` with options:
     - "Force start (remove lock)" — delete the lock and proceed
     - "Cancel" — abort execution
   - If timestamp is **more than 4 hours old**: treat as stale, delete the lock, and proceed
3. If no lock exists, proceed normally

### Create Lock File

After the concurrency check passes, create `.claude/sessions/__live_session__/.lock` with:

```markdown
task_execution_id: {task_execution_id}
timestamp: {ISO 8601 timestamp}
pid: orchestrator
```

This lock is automatically cleaned up in Step 8 when `__live_session__/` contents are archived to the timestamped session folder.

### Create Session Files

Create `.claude/sessions/__live_session__/` (and `.claude/sessions/` parent if needed) with:

1. **`execution_plan.md`** - Save the execution plan displayed in Step 5
2. **`execution_context.md`** - Initialize with standard template:
   ```markdown
   # Execution Context

   ## Project Patterns
   <!-- Discovered coding patterns, conventions, tech stack details -->

   ## Key Decisions
   <!-- Architecture decisions, approach choices made during execution -->

   ## Known Issues
   <!-- Problems encountered, workarounds applied, things to watch out for -->

   ## File Map
   <!-- Important files discovered and their purposes -->

   ## Task History
   <!-- Brief log of task outcomes with relevant context -->
   ```
3. **`task_log.md`** - Initialize with table headers:
   ```markdown
   # Task Execution Log

   | Task ID | Subject | Status | Attempts | Duration | Token Usage |
   |---------|---------|--------|----------|----------|-------------|
   ```
4. **`tasks/`** - Empty subdirectory for archiving completed task files
5. **`progress.md`** - Initialize with status template:
   ```markdown
   # Execution Progress
   Status: Initializing
   Wave: 0 of {total_waves}
   Max Parallel: {max_parallel}
   Updated: {ISO 8601 timestamp}

   ## Active Tasks

   ## Completed This Session
   ```
6. **`execution_pointer.md`** at `$HOME/.claude/tasks/{CLAUDE_CODE_TASK_LIST_ID}/execution_pointer.md` — Create immediately with the fully resolved absolute path to the live session directory (e.g., `/Users/sequenzia/dev/repos/my-project/.claude/sessions/__live_session__/`). Construct this by prepending the current working directory to `.claude/sessions/__live_session__/`. This ensures the pointer exists even if the session is interrupted before completing.

## Step 6: Initialize Execution Context

Read `.claude/sessions/__live_session__/execution_context.md` (created in Step 5.5).

If a prior execution session's context exists, look in `.claude/sessions/` for the most recent timestamped subfolder and merge relevant learnings (Project Patterns, Key Decisions, Known Issues, File Map) into the new execution context.

### Context Compaction

After merging prior learnings, check the Task History section. If it has 10 or more entries from merged sessions, compact older entries:

1. Keep the 5 most recent Task History entries in full
2. Summarize all older entries into a single "Prior Sessions Summary" paragraph at the top of the Task History section
3. Replace the old individual entries with this summary

This prevents the execution context from growing unbounded across multiple execution sessions.

## Step 7: Execute Loop

Execute tasks in waves. No user interaction between waves.

### 7a: Initialize Wave

1. Identify all unblocked tasks (pending status, all dependencies completed)
2. Sort by priority (same rules as Step 3d)
3. Take up to `max_parallel` tasks for this wave
4. If no unblocked tasks remain, exit the loop

### 7b: Snapshot Execution Context

Read `.claude/sessions/__live_session__/execution_context.md` and hold it as the baseline for this wave. All agents in this wave will read from this same snapshot. This prevents concurrent agents from seeing partial context writes from sibling tasks.

### 7c: Launch Wave Agents

1. Mark all wave tasks as `in_progress` via `TaskUpdate`
2. Record `wave_start_time`
3. Write the complete `progress.md` using Write (read-modify-write pattern):
   ```markdown
   # Execution Progress
   Status: Executing
   Wave: {current_wave} of {total_waves}
   Max Parallel: {max_parallel}
   Updated: {ISO 8601 timestamp}

   ## Active Tasks
   - [{id}] {subject} — Launching agent
   - [{id}] {subject} — Launching agent
   ...

   ## Completed This Session
   {accumulated completed tasks from prior waves}
   ```
4. Launch all wave agents simultaneously using **parallel Task tool calls in a single message turn** with `run_in_background: true`:

For each task in the wave, use the Task tool:

```
Task:
  subagent_type: task-executor
  mode: bypassPermissions
  run_in_background: true
  prompt: |
    Execute the following task.

    Task ID: {id}
    Task Subject: {subject}
    Task Description:
    ---
    {full description}
    ---

    Task Metadata:
    - Priority: {priority}
    - Complexity: {complexity}
    - Source Section: {source_section}
    - Spec Path: {spec_path}
    - Feature: {feature_name}

    CONCURRENT EXECUTION MODE
    Context Write Path: .claude/sessions/__live_session__/context-task-{id}.md
    Result Write Path: .claude/sessions/__live_session__/result-task-{id}.md
    Do NOT write to execution_context.md directly.
    Do NOT update progress.md — the orchestrator manages it.
    Write your learnings to the Context Write Path above instead.

    RESULT FILE PROTOCOL
    As your VERY LAST action (after writing context-task-{id}.md), write a compact
    result file to the Result Write Path above. Format:

    # Task Result: [{id}] {subject}
    status: PASS|PARTIAL|FAIL
    attempt: {n}/{max}

    ## Verification
    - Functional: {n}/{total}
    - Edge Cases: {n}/{total}
    - Error Handling: {n}/{total}
    - Tests: {passed}/{total} ({failed} failures)

    ## Files Modified
    - {path}: {brief description}

    ## Issues
    {None or brief descriptions}

    After writing the result file, return ONLY this single status line:
    DONE: [{id}] {subject} - {PASS|PARTIAL|FAIL}

    {If retry attempt:}
    RETRY ATTEMPT {n} of {max_retries}
    Previous attempt failed with:
    ---
    {previous failure details from result file}
    ---
    Focus on fixing the specific failures listed above.

    Before implementing fixes:
    1. Read execution_context.md for learnings from the failed attempt
    2. Check for partial changes: incomplete files, broken imports, partial implementations
    3. Run linter and tests to assess codebase state before making changes
    4. Clean up incomplete artifacts before proceeding
    5. If previous approach was fundamentally wrong, consider reverting and trying differently

    Instructions (follow in order):
    1. Read the execute-tasks skill and reference files
    2. Read .claude/sessions/__live_session__/execution_context.md for prior learnings
    3. Understand the task requirements and explore the codebase
    4. Implement the necessary changes
    5. Verify against acceptance criteria (or inferred criteria for general tasks)
    6. Update task status if PASS (mark completed)
    7. Write learnings to .claude/sessions/__live_session__/context-task-{id}.md
    8. Write result to .claude/sessions/__live_session__/result-task-{id}.md
    9. Return: DONE: [{id}] {subject} - {PASS|PARTIAL|FAIL}
```

**Important**: Always include the `CONCURRENT EXECUTION MODE` and `RESULT FILE PROTOCOL` sections regardless of `max_parallel` value. All agents write to per-task context files (`context-task-{id}.md`) and result files (`result-task-{id}.md`), and the orchestrator always performs the merge step in 7f. This unified path eliminates fragile direct writes to `execution_context.md`.

5. **Poll for completion**: After launching all background agents, poll for result files using Bash:

```bash
# Poll for result files with timeout
SESSION_DIR=".claude/sessions/__live_session__"
EXPECTED_IDS="{space-separated task IDs for this wave}"
TIMEOUT=3600
ELAPSED=0
INTERVAL=15

while true; do
  ALL_DONE=true
  for ID in $EXPECTED_IDS; do
    if [ ! -f "$SESSION_DIR/result-task-$ID.md" ]; then
      ALL_DONE=false
      break
    fi
  done

  if $ALL_DONE; then
    sleep 1  # Brief pause to ensure filesystem flush
    break
  fi

  if [ $ELAPSED -ge $TIMEOUT ]; then
    echo "TIMEOUT: Not all result files appeared within ${TIMEOUT}s"
    echo "Missing:"
    for ID in $EXPECTED_IDS; do
      [ ! -f "$SESSION_DIR/result-task-$ID.md" ] && echo "  result-task-$ID.md"
    done
    break
  fi

  sleep $INTERVAL
  ELAPSED=$((ELAPSED + INTERVAL))
done
```

After polling completes, proceed to 7d for batch processing.

### 7d: Process Results (Batch)

After polling completes, process all wave results in a single batch:

1. Calculate `wave_duration = current_time - wave_start_time`. Format: <60s = `{s}s`, <60m = `{m}m {s}s`, >=60m = `{h}h {m}m {s}s`

2. **Read result files**: For each task in the wave, read `.claude/sessions/__live_session__/result-task-{id}.md`. Parse:
   - `status` line → PASS, PARTIAL, or FAIL
   - `attempt` line → attempt number
   - `## Verification` section → criterion pass counts
   - `## Files Modified` section → changed file list
   - `## Issues` section → failure details

3. **Handle missing result files** (agent crash recovery): If a result file is missing after polling:
   - Check if `context-task-{id}.md` exists (agent may have crashed between context and result write)
   - Fall back to `TaskOutput` (blocking read) for the crashed agent to capture any diagnostic output
   - Treat as FAIL with the TaskOutput content as failure details

4. Log a status line for each task: `[{id}] {subject}: {PASS|PARTIAL|FAIL}`

5. **Batch update `task_log.md`**: Read the current file once, append ALL wave rows, Write the complete file once:
   ```markdown
   | {id1} | {subject1} | {PASS/PARTIAL/FAIL} | {attempt}/{max_retries} | {duration} | N/A |
   | {id2} | {subject2} | {PASS/PARTIAL/FAIL} | {attempt}/{max_retries} | {duration} | N/A |
   ...
   ```

6. **Batch update `progress.md`**: Read the current file once, move ALL completed tasks from Active to Completed, Write the complete file once:
   ```markdown
   ## Active Tasks
   {only tasks still running, if any}

   ## Completed This Session
   - [{id1}] {subject1} — PASS ({wave_duration})
   - [{id2}] {subject2} — FAIL ({wave_duration})
   {prior completed entries}
   ```

**Context append fallback**: If a result file is missing but `TaskOutput` contains a `LEARNINGS:` section, manually write those learnings to `.claude/sessions/__live_session__/context-task-{id}.md`.

### 7e: Within-Wave Retry

After batch processing identifies failed tasks:

1. Collect all failed tasks with retries remaining
2. For each retriable task:
   - Read the failure details from `result-task-{id}.md` (Issues section and Verification section)
   - Delete the old `result-task-{id}.md` file before re-launching
   - Launch a new background agent (`run_in_background: true`) with failure context from the result file included in the prompt
   - Update `progress.md` active task entry: `- [{id}] {subject} — Retrying ({n}/{max})`
3. If any retry agents were launched:
   - Enter a new polling round for the retry agents' result files (same Bash polling as 7c step 5)
   - After polling completes, process retry results using the same batch approach as 7d
   - Repeat 7e if any retries still have attempts remaining
4. If retries exhausted for a task:
   - Leave task as `in_progress`
   - Log final failure
   - Retain the result file for post-analysis

### 7f: Merge Context and Clean Up After Wave

After ALL agents in the current wave have completed (including retries):

1. Read `.claude/sessions/__live_session__/execution_context.md`
2. Read all `context-task-{id}.md` files from `.claude/sessions/__live_session__/` in task ID order
3. Append each file's full content to the end of the `## Task History` section
4. Write the complete updated `execution_context.md` using Write
5. Delete the `context-task-{id}.md` files
6. **Clean up result files**: Delete `result-task-{id}.md` for PASS tasks. Retain `result-task-{id}.md` for FAIL tasks (available for post-session analysis in the archived session folder)

### 7g: Rebuild Next Wave and Archive

1. Archive completed task files: for each PASS task in this wave, copy the task's JSON from `~/.claude/tasks/{CLAUDE_CODE_TASK_LIST_ID}/` to `.claude/sessions/__live_session__/tasks/`
2. Use `TaskList` to refresh the full task state
3. Check if any previously blocked tasks are now unblocked
4. If newly unblocked tasks found, form the next wave using priority sort from Step 3d
5. If no unblocked tasks remain, exit the loop
6. Loop back to 7a

## Step 8: Session Summary

Write the complete `progress.md` with final status using Write:
```
# Execution Progress
Status: Complete
Wave: {total_waves} of {total_waves}
Max Parallel: {max_parallel}
Updated: {ISO 8601 timestamp}

## Active Tasks

## Completed This Session
{all completed task entries}
```

After all tasks in the plan have been processed:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXECUTION SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tasks executed: {total attempted}
  Passed: {count}
  Failed: {count} (after {total retries} total retry attempts)

Waves completed: {wave_count}
Max parallel: {max_parallel}
Total execution time: {sum of all task durations}
Token Usage: {total tokens if tracked, otherwise "N/A"}

Remaining:
  Pending: {count}
  In Progress (failed): {count}
  Blocked: {count}

{If any tasks failed:}
FAILED TASKS:
  [{id}] {subject} — {brief failure reason}
  ...

{If newly unblocked tasks were discovered:}
NEWLY UNBLOCKED:
  [{id}] {subject} — unblocked by completion of [{blocker_id}]
  ...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

After displaying the summary:
1. Save `session_summary.md` to `.claude/sessions/__live_session__/` with the full summary content
2. **Archive the session**: Create `.claude/sessions/{task_execution_id}/` and move all contents from `__live_session__/` to the archival folder. The `.lock` file is moved to the archive along with all other session files, releasing the concurrency guard.
3. `__live_session__/` is left as an empty directory (not deleted)
4. `execution_pointer.md` stays pointing to `__live_session__/` (no update needed — it will be empty until the next execution)

## Step 9: Update CLAUDE.md

Review `.claude/sessions/{task_execution_id}/execution_context.md` for project-wide changes that should be reflected in CLAUDE.md.

Update CLAUDE.md if the session introduced:
- New architectural patterns or conventions
- New dependencies or tech stack changes
- New development commands or workflows
- Changes to project structure
- Important design decisions that affect future development

Do NOT update CLAUDE.md for:
- Internal implementation details
- Temporary workarounds
- Task-specific learnings that don't generalize
- If no meaningful project-wide changes occurred, skip this step

Process:
1. Read current CLAUDE.md
2. Identify sections needing updates from execution context
3. Make targeted edits (do not rewrite the entire file)
4. Keep updates concise and factual

## Notes

- Tasks are executed using Claude Code's native task system (TaskGet/TaskUpdate/TaskList)
- Each task is handled by the `agent-alchemy-sdd:task-executor` agent in isolation
- The execution context file enables knowledge sharing across task boundaries
- Failed tasks remain as `in_progress` for manual review or re-execution
- Run the execute-tasks skill again to pick up where you left off — it will execute any remaining unblocked tasks
- All file operations within `.claude/sessions/` (including `__live_session__/` and archival folders) and `execution_pointer.md` are auto-approved by the `auto-approve-session.sh` PreToolUse hook. This includes `result-task-{id}.md` files used by the result file protocol. Task-executor agents are spawned with `mode: bypassPermissions` to enable fully autonomous execution. No user prompts should occur after the initial execution plan confirmation
