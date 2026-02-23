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

## Structured Context Schema

### Purpose

Provide a consistent, section-based format for `execution_context.md` and per-task `context-task-{id}.md` files. Section headers serve as merge anchors during the post-wave merge step, enabling reliable appending, deduplication, and compaction.

### Section Headers (6 Fixed Sections)

All execution context files use these 6 section headers in this order:

| Section | Purpose | Example Entries |
|---------|---------|-----------------|
| `## Project Setup` | Package manager, runtime, frameworks, build tools | `- Runtime: Node.js 22 with pnpm` |
| `## File Patterns` | Test file patterns, component patterns, API route patterns | `- Tests: `__tests__/{name}.test.ts` alongside source` |
| `## Conventions` | Import style, error handling, state management, naming | `- Imports: Named exports preferred, barrel files for public API` |
| `## Key Decisions` | Choices made during execution with task references | `- [Task #5] Used Zod for runtime validation over io-ts` |
| `## Known Issues` | Problems encountered, workarounds, gotchas | `- Vitest mock.calls array resets between tests in same suite` |
| `## Task History` | Compact log: task ID, name, status, key contribution | `- [12] Create API handler — PASS: added /api/users endpoint` |

### Per-Task Context File Format

Each task-executor agent writes `context-task-{id}.md` using the same 6 section headers. Agents **omit sections that have no content** (only include sections with actual entries). This keeps per-task files compact.

```markdown
## Project Setup
- Runtime: Python 3.12, uv for package management

## Conventions
- Error handling: raise specific exception subclasses, catch at API boundary

## Key Decisions
- [Task #7] Chose SQLAlchemy 2.0 async API over raw asyncpg

## Task History
- [7] Implement database layer — PASS: created models, migrations, session factory
```

In this example, `## File Patterns` and `## Known Issues` are omitted because the agent had nothing to report for those sections.

**Entry format conventions**:
- Each entry is a single bullet point (`- `) on one line
- Key Decisions entries start with `[Task #{id}]` to attribute the decision
- Task History entries follow the format: `- [{id}] {subject} — {PASS|PARTIAL|FAIL}: {brief contribution}`
- Entries should be factual and concise (one line per entry)

### Merge Procedure

The orchestrator merges per-task context files into `execution_context.md` in Step 7f using section headers as merge anchors. See Step 7f for the detailed procedure.

### Error Handling for Malformed Context Files

If a per-task context file is missing all `## ` section headers (completely unstructured content):
1. Log a warning: `WARNING: context-task-{id}.md has no section headers — placing content under ## Key Decisions`
2. Treat the entire file content as entries under `## Key Decisions`
3. Proceed with the merge normally

If a per-task context file has some recognized sections and some content outside any section header:
1. Content before the first `## ` header is placed under `## Key Decisions`
2. Content under recognized headers is merged normally

## Upstream Prompt Injection (produces_for)

### Purpose

Enable producer tasks to pass richer context directly to specific dependent tasks beyond what wave-granular `execution_context.md` merging provides. A producer task declares which downstream tasks consume its output via the `produces_for` field, and the orchestrator injects the producer's result file content into the dependent task's prompt at launch time.

### Task JSON Schema Extension

Tasks may include an optional `produces_for` field — an array of task IDs that consume this task's output:

```json
{
  "id": "5",
  "subject": "Implement API handler",
  "description": "...",
  "produces_for": ["8", "12"],
  "blockedBy": ["3"]
}
```

- `produces_for` is **optional**. Tasks without it behave as before (wave-granular context only via `execution_context.md`).
- Values are string task IDs referencing tasks that depend on this task's output.
- A task may appear in multiple producers' `produces_for` arrays (receiving output from multiple upstream tasks).
- `produces_for` is independent of `blockedBy` — a task can produce for a dependent without being in its `blockedBy` list, though they typically overlap.

### Injection Procedure

When launching a dependent task (Step 7c), the orchestrator checks if any **completed** tasks in prior waves have a `produces_for` array that includes the dependent task's ID. If so:

1. **Collect producers**: Find all completed tasks whose `produces_for` contains the current task's ID. Sort by task ID (ascending numeric order).

2. **Read producer result files**: For each producer task, read `.claude/sessions/__live_session__/result-task-{producer_id}.md` (or from the archived session tasks if already cleaned up).

3. **Build injection blocks**: For each producer:

   **If result file exists (producer succeeded):**
   ```markdown
   ## UPSTREAM TASK OUTPUT (Task #{producer_id}: {producer_subject})
   {result file content}
   ---
   ```

   **If result file is missing or producer failed:**
   ```markdown
   ## UPSTREAM TASK #{producer_id} FAILED
   Task: {producer_subject}
   Status: FAIL
   {failure summary from task_log.md if available, otherwise "No failure details available."}
   ---
   ```

4. **Inject into prompt**: Insert all injection blocks into the dependent task's prompt **after** the task description/metadata section and **before** the `CONCURRENT EXECUTION MODE` section. This ensures the agent reads upstream context after understanding the task but before beginning execution.

5. **Log injection**: For each injection, log: `Injecting upstream output from task #{producer_id} into task #{dependent_id}`

### Result File Retention for produces_for

Producer task result files that have `produces_for` entries pointing to **not-yet-completed** tasks must be **retained** during the 7f cleanup step (same retention rule as FAIL result files). The orchestrator deletes these retained result files only after all tasks listed in the producer's `produces_for` have completed.

### No-op When Absent

If no tasks in the task set have `produces_for` fields, the injection procedure is skipped entirely — no overhead. The orchestrator simply launches agents with the standard prompt template.

---

## Step 1: Load Task List

Use `TaskList` to get all tasks and their current state.

If a `--task-group` argument was provided, filter the task list to only tasks where `metadata.task_group` matches the specified group. If no tasks match the group, inform the user and stop.

If a `--phase` argument was provided, further filter the task list to only tasks where `metadata.spec_phase` matches one of the specified phase numbers (parsed as comma-separated integers). This filter is applied after `--task-group` filtering (if both are present).

If no tasks match the phase filter after all filters are applied, inform the user: "No tasks found for phase(s) {N}. Available phases in current task set: {sorted list of distinct `metadata.spec_phase` values}." and stop.

Tasks without `metadata.spec_phase` (created before phase-aware `create-tasks`) are excluded when `--phase` filtering is active.

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

Generate a unique `task_execution_id` using a multi-tier resolution that incorporates phase when specified:
1. IF `--task-group` was provided AND `--phase` was provided → `{task_group}-phase{N}-{YYYYMMDD}-{HHMMSS}` (e.g., `user-auth-phase1-20260131-143022`)
2. IF `--task-group` was provided (no phase) → `{task_group}-{YYYYMMDD}-{HHMMSS}` (e.g., `user-auth-20260131-143022`)
3. IF `--phase` was provided (no group) AND all filtered tasks share same `metadata.task_group` → `{task_group}-phase{N}-{YYYYMMDD}-{HHMMSS}`
4. IF `--phase` was provided (no group) → `phase{N}-{YYYYMMDD}-{HHMMSS}` (e.g., `phase1-20260131-143022`)
5. ELSE IF all open tasks (pending + in_progress) share the same non-empty `metadata.task_group` → `{task_group}-{YYYYMMDD}-{HHMMSS}`
6. ELSE → `exec-session-{YYYYMMDD}-{HHMMSS}` (e.g., `exec-session-20260131-143022`)

Where `{N}` is the phase number (or `{N}-{M}` for multiple phases, e.g., `phase1-2`).

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
2. **`execution_context.md`** - Initialize with the 6-section structured template:
   ```markdown
   # Execution Context

   ## Project Setup
   <!-- Package manager, runtime, frameworks, build tools -->

   ## File Patterns
   <!-- Test file patterns, component patterns, API route patterns -->

   ## Conventions
   <!-- Import style, error handling, state management, naming -->

   ## Key Decisions
   <!-- Choices made during execution with task references -->

   ## Known Issues
   <!-- Problems encountered, workarounds, gotchas -->

   ## Task History
   <!-- Compact log: task ID, name, status, key contribution -->
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

If a prior execution session's context exists, look in `.claude/sessions/` for the most recent timestamped subfolder and merge relevant learnings from the prior context's sections (Project Setup, File Patterns, Conventions, Key Decisions, Known Issues) into the corresponding sections of the new execution context. Do NOT merge prior Task History entries directly — they are handled by compaction below.

### Cross-Session Context Compaction

After merging prior learnings, apply per-section compaction:

1. **For each of the first 5 sections** (Project Setup through Known Issues): if a section has 10 or more entries, summarize the older entries into a single paragraph at the top of that section, keeping the 5 most recent entries in full.

2. **For Task History**: if the prior session's Task History has entries, summarize ALL prior session entries into a single "Prior Sessions Summary" paragraph at the top of the Task History section. Do not carry over individual entries from prior sessions.

This per-section compaction prevents any single section from growing unbounded across multiple execution sessions.

## Step 7: Execute Loop

Execute tasks in waves. No user interaction between waves except during Tier 3 retry escalation (see 7e.4).

### 7-pre: Session Start Message

Before entering the wave loop, emit a session start summary as text output visible to the human operator:

```
Execution plan: {total_tasks} tasks across {total_waves} waves (max {max_parallel} parallel)
```

Where:
- `{total_tasks}` = count of all tasks to be executed (pending, not blocked)
- `{total_waves}` = number of waves in the execution plan
- `{max_parallel}` = resolved max parallel value

This gives the operator an immediate confirmation that execution has begun.

### 7a: Initialize Wave

1. Identify all unblocked tasks (pending status, all dependencies completed)
2. Sort by priority (same rules as Step 3d)
3. Take up to `max_parallel` tasks for this wave
4. If no unblocked tasks remain, exit the loop

### 7a.5: Pre-Wave File Conflict Detection

Before launching agents, scan all wave tasks for file path conflicts to prevent concurrent agents from editing the same files.

#### Purpose

When two or more tasks in the same wave reference the same file, concurrent agents may overwrite each other's changes. This step detects such conflicts before launch and defers higher-ID conflicting tasks to the next wave.

#### Procedure

1. **Extract file references**: For each task in the wave, scan the task's `description` and acceptance criteria fields for file path references using these patterns:
   - **Slash paths**: Any token containing `/` (e.g., `src/api/handler.ts`, `claude/sdd-tools/SKILL.md`)
   - **Known extensions**: Tokens ending in `.md`, `.ts`, `.js`, `.json`, `.sh`, or `.py` (e.g., `SKILL.md`, `config.json`)
   - **Glob patterns**: Tokens containing `*` or `?` with `/` or known extensions (e.g., `src/api/*.ts`, `tests/**/*.py`)

   When extracting, strip surrounding markdown formatting (backticks, bold markers, list prefixes) to get clean paths.

2. **Normalize paths**: Convert all extracted paths to a consistent form:
   - Remove leading `./` if present
   - Collapse `//` to `/`
   - Trim trailing whitespace

3. **Detect conflicts**: Build a map of `{file_path → [task_ids]}`. A conflict exists when any file path maps to two or more task IDs.

   For glob pattern conflicts:
   - Two glob patterns conflict if they could match the same file. Use conservative overlap detection:
     - Globs sharing the same directory prefix and overlapping extensions conflict (e.g., `src/api/*.ts` and `src/api/handler.ts`)
     - A concrete path conflicts with a glob if the path's directory starts with the glob's directory prefix (e.g., `src/api/handler.ts` conflicts with `src/api/*.ts`)
   - When in doubt, treat ambiguous overlaps as conflicts (false positives are safer than false negatives)

4. **Resolve conflicts**: For each conflicting file path:
   - The task with the **lowest ID** stays in the current wave
   - All higher-ID tasks referencing that file are **deferred** to the next wave by inserting an artificial dependency on the lowest-ID task
   - If a task conflicts on multiple files, it is deferred if it loses on any of them

5. **Handle all-conflict case**: If all tasks in the wave conflict on the same file(s), sequentialize them: keep only the lowest-ID task in this wave, defer all others. The deferred tasks will form subsequent sub-waves of one task each.

6. **Log results**: Append a "Conflict Resolution" section to `execution_plan.md` using the read-modify-write pattern:

   ```markdown
   ## Conflict Resolution — Wave {N}

   {If conflicts found:}
   Detected {count} file conflict(s):
   - `{file_path}`: Tasks [{id1}], [{id2}], [{id3}]
     → [{id1}] stays (lowest ID), [{id2}] and [{id3}] deferred to next wave

   {If no conflicts:}
   No file conflicts detected. Wave proceeds unchanged.
   ```

7. **No conflicts**: If no conflicts are detected, proceed immediately with no overhead. Do not log anything to `execution_plan.md` for clean waves (skip step 6).

#### Error Handling

If the file path pattern matching fails (e.g., unexpected description format causes a parsing error):
- Log a warning: `WARNING: File conflict detection failed for wave {N} — proceeding without detection`
- Proceed with the wave as-is (no tasks deferred)
- Do not block execution due to detection failures

### 7b: Snapshot Execution Context

Read `.claude/sessions/__live_session__/execution_context.md` and hold it as the baseline for this wave. All agents in this wave will read from this same snapshot. This prevents concurrent agents from seeing partial context writes from sibling tasks.

### 7c: Launch Wave Agents

1. Mark all wave tasks as `in_progress` via `TaskUpdate`
2. Record `wave_start_time`
3. **Emit "Starting Wave" message** as text output visible to the human operator:
   ```
   Starting Wave {current_wave}/{total_waves}: {count} tasks...
   ```
   Where `{count}` is the number of tasks in this wave. This is emitted before launching any agents, giving the operator a real-time progress indicator.
4. Write the complete `progress.md` using Write (read-modify-write pattern):
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
5. **Build upstream injection blocks (produces_for)**: Before launching agents, check if any completed tasks from prior waves have `produces_for` arrays that reference tasks in the current wave. For each wave task, follow the injection procedure defined in the "Upstream Prompt Injection (produces_for)" section above:

   a. Scan all completed tasks for `produces_for` entries containing this task's ID
   b. If producers found, sort by task ID (ascending numeric order)
   c. For each producer, build an injection block:
      - **Producer succeeded** (result file exists): Read `result-task-{producer_id}.md` and format as:
        ```
        ## UPSTREAM TASK OUTPUT (Task #{producer_id}: {producer_subject})
        {result file content}
        ---
        ```
      - **Producer failed** (result file missing or task status is FAIL): Format as:
        ```
        ## UPSTREAM TASK #{producer_id} FAILED
        Task: {producer_subject}
        Status: FAIL
        {failure summary from task_log.md if available, otherwise "No failure details available."}
        ---
        ```
   d. Log each injection: `Injecting upstream output from task #{producer_id} into task #{task_id}`
   e. If no producers found for this task, skip injection (no overhead)

   Concatenate all injection blocks for a task into a single `{upstream_injection}` string. If empty, the `CONTEXT FROM COMPLETED DEPENDENCIES` section in the prompt template below is omitted entirely.

6. Launch all wave agents simultaneously using **parallel Task tool calls in a single message turn** with `run_in_background: true`.

**Record the background task_id mapping**: After the Task tool returns for each agent, record the mapping `{task_list_id → background_task_id}` from each response. The `background_task_id` (returned in the Task tool result when `run_in_background: true`) is needed later to call `TaskOutput` for process reaping and usage extraction.

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

    {If upstream_injection is non-empty:}
    CONTEXT FROM COMPLETED DEPENDENCIES:
    {upstream_injection}

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

7. **Detect completion (watch → poll fallback)**: After launching all background agents, detect result file completion using `watch-for-results.sh` as the primary mechanism, falling back to `poll-for-results.sh` (adaptive) if filesystem watch tools are unavailable.

**IMPORTANT**: Always specify `timeout: 480000` (8 minutes) on each Bash invocation. The default Bash timeout of 2 minutes is NOT enough for completion detection. Both scripts handle their own internal timeout (default 45 minutes via `WATCH_TIMEOUT` / `POLL_TIMEOUT` environment variables).

#### Primary: Filesystem Watch

Launch `watch-for-results.sh` as a single Bash invocation (with `timeout: 480000`):

   ```bash
   bash ${CLAUDE_PLUGIN_ROOT}/skills/execute-tasks/scripts/watch-for-results.sh \
     .claude/sessions/__live_session__ {expected_count} {task_id_1} {task_id_2} {task_id_3}
   ```

   Replace `{expected_count}` with the number of tasks in this wave and `{task_id_N}` with their actual task IDs.

#### Interpreting Watch Output

The watch script emits incremental progress lines on stdout. Parse each line as it appears:

   - **`RESULT_FOUND: result-task-{id}.md (N/M)`** — One result file detected. Log incremental progress (e.g., "Wave 2: result 3/5 found (task {id})").
   - **`ALL_DONE`** — All expected result files found. Proceed to 7d.
   - **`TIMEOUT: Found N/M results`** — The watch timed out (exit code 1). Handle as wave timeout (see below).
   - **`WATCHER_EXIT: Found N/M results`** — The underlying watcher process (fswatch/inotifywait) exited unexpectedly before all results were found (exit code 1). Fall back to polling for the remaining results.

#### Handling Watch Exit Codes

After the Bash invocation completes, check the exit code:

   | Exit Code | Meaning | Action |
   |-----------|---------|--------|
   | **0** | All results found (`ALL_DONE` emitted) | Proceed to 7d for batch processing |
   | **1** | Timeout or unexpected watcher exit | Check last output line: if `TIMEOUT:` → handle as wave timeout; if `WATCHER_EXIT:` → fall back to polling for remaining results |
   | **2** | Neither `fswatch` nor `inotifywait` available | Fall back to polling immediately |
   | **Bash timeout** | Bash tool `timeout: 480000` reached before script exited | Fall back to polling (re-invoke with remaining task IDs) |

#### Fallback: Adaptive Polling

If the watch script exits with code 2 (tools unavailable), the watcher exits unexpectedly (`WATCHER_EXIT`), or the Bash tool times out, fall back to `poll-for-results.sh`:

   ```bash
   bash ${CLAUDE_PLUGIN_ROOT}/skills/execute-tasks/scripts/poll-for-results.sh \
     .claude/sessions/__live_session__ {remaining_count} {remaining_task_ids...}
   ```

   When falling back after a partial watch (some results already found via `RESULT_FOUND:` lines), pass only the **remaining** task IDs and adjust `{remaining_count}` accordingly.

   Log the transition: `"Watch unavailable/failed — falling back to adaptive polling for {remaining_count} remaining results"`

#### Polling Output Parsing

The poll script uses the same output format as the watch script:

   - **`RESULT_FOUND: result-task-{id}.md (N/M)`** — Incremental detection. Log progress.
   - **`ALL_DONE`** — All results found. Proceed to 7d.
   - Exit code **0** — All results found.
   - Exit code **1** — Timeout reached. Handle as wave timeout.

#### Multi-Round Fallback (Polling)

If a single poll invocation times out (Bash tool timeout, not the script's internal timeout), re-invoke the poll script with only the remaining (undetected) task IDs. Track already-found results from `RESULT_FOUND:` lines across invocations to avoid counting duplicates.

   If cumulative elapsed time across all detection attempts (watch + poll rounds) exceeds **45 minutes**, stop and report:
   ```
   TIMEOUT: Not all result files appeared within 45 minutes.
   Missing: {list of task IDs still without result files}
   ```
   Then proceed to 7d, which handles missing result files via the TaskOutput fallback.

#### Wave Timeout Handling

When either the watch or poll script signals timeout (exit code 1):
1. Parse the final output line for the count of found vs expected results
2. Log: `"Wave {N} timeout: {found}/{expected} results detected"`
3. Proceed to 7d — missing result files are handled via the TaskOutput fallback in 7d step 3

**Note**: The 45-minute cumulative timeout is **per completion detection instance** (i.e., per wave). Each time the orchestrator starts detection for a new wave (Step 7c) or for retry agents (Step 7e), the timeout budget resets. This gives each wave a full 45-minute window for its agents to complete.

After detection completes (all done or timeout), proceed to 7d for batch processing.

### 7d: Process Results (Batch)

After detection completes (watch or poll), process all wave results in a single batch:

1. **Reap background agents and extract usage**: For each task in the wave, call `TaskOutput(task_id=<background_task_id>, block=true, timeout=60000)` using the mapping recorded in 7c. This serves two purposes:
   - **Process reaping**: Terminates the background agent process (prevents lingering subagents)
   - **Usage extraction**: Returns metadata with `duration_ms` and `total_tokens` per agent

   Extract per-task values:
   - `task_duration`: From `duration_ms` in TaskOutput metadata. Format: <60s = `{s}s`, <60m = `{m}m {s}s`, >=60m = `{h}h {m}m {s}s`
   - `task_tokens`: From `total_tokens` in TaskOutput metadata. Format with comma separators (e.g., `45,230`)

   If `TaskOutput` times out (agent truly stuck), call `TaskStop(task_id=<background_task_id>)` to force-terminate the process, then set `task_duration = "N/A"` and `task_tokens = "N/A"`.

2. **Read result files**: For each task in the wave, read `.claude/sessions/__live_session__/result-task-{id}.md`. Parse:
   - `status` line → PASS, PARTIAL, or FAIL
   - `attempt` line → attempt number
   - `## Verification` section → criterion pass counts
   - `## Files Modified` section → changed file list
   - `## Issues` section → failure details

3. **Handle missing result files** (agent crash recovery): If a result file is missing after detection:
   - Check if `context-task-{id}.md` exists (agent may have crashed between context and result write)
   - The `TaskOutput` call in step 1 already captured diagnostic output for the crashed agent
   - Treat as FAIL with the TaskOutput content as failure details

4. Log a status line for each task: `[{id}] {subject}: {PASS|PARTIAL|FAIL}`

5. **Batch update `task_log.md`**: Read the current file once, append ALL wave rows, Write the complete file once:
   ```markdown
   | {id1} | {subject1} | {PASS/PARTIAL/FAIL} | {attempt}/{max_retries} | {task_duration} | {task_tokens} |
   | {id2} | {subject2} | {PASS/PARTIAL/FAIL} | {attempt}/{max_retries} | {task_duration} | {task_tokens} |
   ...
   ```
   Where `{task_duration}` and `{task_tokens}` come from the TaskOutput metadata extracted in step 1.

6. **Batch update `progress.md`**: Read the current file once, move ALL completed tasks from Active to Completed, Write the complete file once:
   ```markdown
   ## Active Tasks
   {only tasks still running, if any}

   ## Completed This Session
   - [{id1}] {subject1} — PASS ({task_duration})
   - [{id2}] {subject2} — FAIL ({task_duration})
   {prior completed entries}
   ```

**Context append fallback**: If a result file is missing but `TaskOutput` contains a `LEARNINGS:` section, manually write those learnings to `.claude/sessions/__live_session__/context-task-{id}.md`.

### 7d-post: Emit Wave Completion Summary

After processing all results in 7d (and before retries in 7e), emit a structured wave completion summary as text output visible to the human operator. This is the primary progress mechanism — wave-level granularity only, no per-task streaming during a wave.

**Summary format:**

```
Wave {current_wave}/{total_waves} complete: {pass_count}/{total_count} tasks passed ({wave_duration})
  [{id1}] {subject1} — {STATUS} ({task_duration}, {task_tokens} tokens)
  [{id2}] {subject2} — {STATUS} ({task_duration}, {task_tokens} tokens)
  [{id3}] {subject3} — {STATUS} ({task_duration}, {task_tokens} tokens)
```

Where:
- `{current_wave}/{total_waves}` = wave number and total wave count from the execution plan
- `{pass_count}/{total_count}` = number of PASS tasks vs total tasks in this wave
- `{wave_duration}` = elapsed time since `wave_start_time` (recorded in 7c step 2), formatted as `{m}m {s}s`
- Per-task lines are indented with 2 spaces and include:
  - `{id}` = task ID
  - `{subject}` = task subject (truncated to 50 chars if needed)
  - `{STATUS}` = PASS, PARTIAL, or FAIL
  - `{task_duration}` = from TaskOutput metadata (step 7d.1), e.g., `1m 52s`
  - `{task_tokens}` = from TaskOutput metadata (step 7d.1), formatted as compact (e.g., `48K`). If token count unavailable (TaskOutput timeout), omit the tokens portion: `— PASS (1m 52s)`

**Token count formatting**: Format token counts compactly:
- Under 1,000 → exact number (e.g., `823`)
- 1,000-999,999 → `{N}K` (e.g., `48K` for 48,230)
- 1,000,000+ → `{N.N}M` (e.g., `1.2M`)

**Wave with failures example:**

```
Wave 3/6 complete: 2/4 tasks passed (4m 12s)
  [8] Implement API handler — PASS (2m 10s, 52K tokens)
  [9] Create database schema — PASS (3m 01s, 67K tokens)
  [10] Update routing config — FAIL (4m 12s, 71K tokens)
  [11] Add validation middleware — PARTIAL (3m 45s, 59K tokens)
```

**Single-wave session**: Even if only one wave exists, the summary is still emitted (shows `Wave 1/1 complete: ...`).

**Data source**: All data comes from the result file parsing (step 7d.2) and TaskOutput reaping (step 7d.1) already performed. No additional file I/O is required.

### 7e: Within-Wave Retry (3-Tier Escalation)

After batch processing identifies failed tasks, apply a progressive retry escalation strategy. Each task tracks its own `escalation_level` (1, 2, or 3), which resets to 0 for every new task. The escalation level determines how much additional help the retry agent receives.

#### Escalation Tiers

| Tier | Escalation Level | Strategy | User Interaction |
|------|-----------------|----------|------------------|
| **Retry #1** | 1 — Standard | Failure context from previous result file | None (autonomous) |
| **Retry #2** | 2 — Context Enrichment | Full `execution_context.md` + related task result files | None (autonomous) |
| **Retry #3** | 3 — User Escalation | Pause execution, present failure to user | AskUserQuestion with 4 options |

#### 7e.1: Collect Failed Tasks

1. Collect all failed tasks (FAIL or PARTIAL) from the current wave's batch processing (7d)
2. For each failed task, determine its current `escalation_level`:
   - First failure → `escalation_level = 1`
   - Second failure → `escalation_level = 2`
   - Third failure → `escalation_level = 3`
3. Group tasks by escalation level for batch processing

#### 7e.2: Tier 1 — Standard Retry (escalation_level = 1)

For tasks at escalation level 1 (first retry):

1. Read the failure details from `result-task-{id}.md` (Issues section and Verification section)
2. Delete the old `result-task-{id}.md` file before re-launching
3. Launch a new background agent (`run_in_background: true`) with failure context from the result file included in the prompt (existing retry prompt format from 7c)
4. **Record the new `background_task_id`** from each Task tool response (same mapping as 7c)
5. Update `progress.md` active task entry: `- [{id}] {subject} — Retrying (1/{max}) [Standard]`

#### 7e.3: Tier 2 — Context Enrichment Retry (escalation_level = 2)

For tasks at escalation level 2 (second retry):

1. Read the failure details from `result-task-{id}.md`
2. **Gather enrichment context**:
   - Read the full `.claude/sessions/__live_session__/execution_context.md` (not just the snapshot — the latest merged version)
   - Collect `result-task-{id}.md` files from **related tasks**: tasks that share dependencies with the failing task (same `blockedBy` entries) or tasks from the same wave. Read up to 5 related result files to avoid prompt bloat.
3. Delete the old `result-task-{id}.md` file before re-launching
4. Launch a new background agent with **enriched prompt** that includes:
   - All standard retry context (failure details, retry instructions)
   - Additional section: `CONTEXT ENRICHMENT (Retry #2):`
     ```
     CONTEXT ENRICHMENT (Retry #2):
     The following additional context is provided because the standard retry failed.

     Full execution context:
     ---
     {full execution_context.md content}
     ---

     Related task results:
     ---
     {content of related result-task-{id}.md files}
     ---
     ```
5. **Record the new `background_task_id`** from each Task tool response
6. Update `progress.md` active task entry: `- [{id}] {subject} — Retrying (2/{max}) [Context Enrichment]`

#### 7e.4: Tier 3 — User Escalation (escalation_level = 3)

For tasks at escalation level 3 (third retry), **pause autonomous execution** and involve the user:

1. Read the failure details from the most recent `result-task-{id}.md`
2. Present failure details to the user via `AskUserQuestion`:

```yaml
questions:
  - header: "Task Failed: [{id}] {subject}"
    question: |
      This task has failed 2 automated retries. Here are the failure details:

      Attempt 1 (Standard): {brief failure summary from attempt 1}
      Attempt 2 (Context Enrichment): {brief failure summary from attempt 2}

      Issues: {issues section from latest result file}

      How would you like to proceed?
    options:
      - label: "Fix manually and continue"
        description: "You will fix the issue externally. Execution resumes when you confirm."
      - label: "Skip this task"
        description: "Mark as FAIL in task_log.md and continue with remaining tasks."
      - label: "Provide guidance"
        description: "Give the agent specific guidance for one more retry attempt."
      - label: "Abort session"
        description: "Stop execution, clean up, and show partial summary."
    multiSelect: false
```

3. **Handle user response**:

   **"Fix manually and continue"**:
   - Present a follow-up `AskUserQuestion`:
     ```yaml
     questions:
       - header: "Manual Fix: [{id}] {subject}"
         question: "Make your changes externally, then confirm to continue execution."
         options:
           - label: "Done — continue execution"
             description: "I've fixed the issue. Resume task execution."
           - label: "Cancel — abort session"
             description: "Abort the execution session."
         multiSelect: false
     ```
   - If user selects "Done": Mark the task as `completed` via `TaskUpdate`. Log in `task_log.md` with status `PASS (manual)`. Continue with remaining waves.
   - If user selects "Cancel": Proceed to abort (same as "Abort session" below).

   **"Skip this task"**:
   - Leave task as `in_progress` (not completed)
   - Log in `task_log.md` with status `FAIL (skipped)` and escalation level 3
   - Retain the result file for post-analysis
   - Continue with remaining waves (other tasks may still be unblocked)

   **"Provide guidance"**:
   - Present a follow-up `AskUserQuestion` to capture guidance text:
     ```yaml
     questions:
       - header: "Guidance for [{id}] {subject}"
         question: "Provide specific guidance for the retry agent. What should it try differently?"
         allowFreeText: true
     ```
   - Delete the old `result-task-{id}.md` file
   - Launch a new background agent with **guidance-enriched prompt** that includes:
     - All standard retry context (failure details)
     - Full `execution_context.md` content (same as Tier 2)
     - Additional section: `USER GUIDANCE (Retry #3):`
       ```
       USER GUIDANCE (Retry #3):
       The user has reviewed the failure and provided the following guidance:
       ---
       {user's guidance text}
       ---
       Apply this guidance when implementing the fix. This is your final automated attempt.
       ```
   - **Record the new `background_task_id`**
   - Update `progress.md`: `- [{id}] {subject} — Retrying (3/{max}) [User Guidance]`
   - Detect completion using the same watch → poll fallback pattern
   - Reap the agent via `TaskOutput` (same as 7d step 1)
   - Process the result:
     - If PASS: Task passes normally. Log success.
     - If FAIL: **Re-present `AskUserQuestion`** with updated failure details (same 4 options as above, but with the new failure information). The user can choose to provide more guidance (which triggers another retry with the new guidance), fix manually, skip, or abort. This loop continues until the user selects an option other than "Provide guidance" or a guided retry succeeds.

   **"Abort session"**:
   - Log all remaining in-progress tasks with status `FAIL (aborted)` in `task_log.md`
   - Leave all in-progress tasks as `in_progress` (not completed, not reset to pending)
   - Skip directly to Step 8 (Session Summary) to generate and display the partial summary
   - The session summary should note: `Session aborted by user at Wave {N} after task [{id}] failed escalation`

#### 7e.5: Retry Execution and Detection

For all tiers that launch background agents (Tier 1, Tier 2, and Tier 3 "Provide guidance"):

1. After launching retry agents, detect completion using the same **watch → poll fallback** pattern as 7c step 7, with only the retry task IDs and their count as arguments. Launch `watch-for-results.sh` first; if exit code 2 or watcher fails, fall back to `poll-for-results.sh`. Always use `timeout: 480000` on each Bash invocation.
2. After detection completes (all retry result files found or cumulative timeout reached), **reap retry agents**: call `TaskOutput` on each retry `background_task_id` to extract `duration_ms` and `total_tokens` (same pattern as 7d step 1). If `TaskOutput` times out, call `TaskStop` to force-terminate.
3. Process retry results using the same batch approach as 7d (using the freshly extracted per-task duration and token values for task_log rows)

#### 7e.6: Post-Retry Processing

After all retry tiers for the current wave are processed:

1. Tasks that passed at any tier: Mark as `completed`, log success
2. Tasks still failing after Tier 1 or 2: Increment `escalation_level` and repeat 7e with the next tier
3. Tasks resolved by user action (manual fix, skip, abort): Already handled in 7e.4
4. Update `task_log.md` with the final escalation level for each task:
   ```markdown
   | {id} | {subject} | {status} | {attempt}/{max} (T{escalation_level}) | {duration} | {tokens} |
   ```
   The `(T{escalation_level})` suffix in the Attempts column indicates which tier was reached: `T1` = standard, `T2` = context enrichment, `T3` = user escalation.

#### Escalation Flow Summary

```
Task fails (attempt 1)
  -> Retry #1: Standard (failure context only)
    -> PASS? Done.
    -> FAIL? Continue to Retry #2

Task fails (attempt 2)
  -> Retry #2: Context Enrichment (full context + related results)
    -> PASS? Done.
    -> FAIL? Continue to Retry #3

Task fails (attempt 3)
  -> Retry #3: User Escalation (AskUserQuestion)
    -> "Fix manually" -> user fixes -> mark complete -> continue
    -> "Skip" -> mark FAIL (skipped) -> continue
    -> "Provide guidance" -> retry with guidance
      -> PASS? Done.
      -> FAIL? Re-present AskUserQuestion (loop)
    -> "Abort" -> partial summary -> end session
```

**Important**: Each task has an independent escalation path. If multiple tasks fail in the same wave, each gets its own escalation sequence. Tier 1 and Tier 2 retries for all tasks in a wave are batched together (launched and detected in parallel). Tier 3 (user escalation) is handled sequentially per task since it requires user interaction.

### 7f: Merge Context and Clean Up After Wave

After ALL agents in the current wave have completed (including retries):

#### Section-Based Merge Procedure

1. **Read current context**: Read `.claude/sessions/__live_session__/execution_context.md`
2. **Parse into sections**: Split the file on `## ` markers. Each `## {Header}` through the next `## ` (or EOF) is one section. Store as a map: `{header_name → list_of_entries}`.
3. **Read per-task files**: Read all `context-task-{id}.md` files from `.claude/sessions/__live_session__/` in task ID order. Parse each file into sections using the same `## ` splitting.
4. **Merge by section**: For each per-task file, for each section present in that file:
   - Find the matching section header in `execution_context.md`
   - Append the per-task entries under the matching section header
   - If a per-task section header does not match any of the 6 defined headers, place its content under `## Key Decisions` with a note: `(from unrecognized section)`
5. **Deduplicate within sections**: After appending all per-task entries, deduplicate within each section:
   - Compare entries by their full text (trimmed of leading/trailing whitespace)
   - Keep the first occurrence, remove exact duplicates
   - Near-duplicates (same content, different wording) are NOT deduplicated — only exact matches
6. **Write merged context**: Reassemble the full `execution_context.md` with all 6 section headers (in order) and Write the complete file

#### Within-Session Compaction

After the merge, check each section's entry count. If any section has 10 or more entries:

1. **For sections 1-5** (Project Setup through Known Issues): Keep the 5 most recent entries in full. Summarize all older entries into a single paragraph at the top of the section.
2. **For Task History**: Keep the 10 most recent entries in full. Summarize older entries into a "Wave Summary" paragraph at the top of the section.

This prevents individual sections from growing unbounded during a single execution session.

#### Post-Merge Validation

After compaction completes (or is skipped), validate the merged `execution_context.md` before proceeding to cleanup. This catches corruption or unbounded growth introduced during the merge. The validation leverages the 6-section structured schema for reliable header detection.

**Validation checks** (run in order):

1. **Header validation**: Verify all 6 required section headers are present in the file:
   - `## Project Setup`
   - `## File Patterns`
   - `## Conventions`
   - `## Key Decisions`
   - `## Known Issues`
   - `## Task History`

   Scan the file for lines matching `^## ` and compare against the canonical set. If any headers are missing, record them in `missing_headers`.

2. **Malformed content detection**: Check for non-empty, non-comment content lines that appear before the first `## ` header (after the `# Execution Context` title line). These indicate malformed structure from a bad merge. Record the count as `orphaned_lines`.

3. **Size check**: Count the total lines in the file.
   - If >500 lines: record `size_level = warn`
   - If >1000 lines: record `size_level = error`
   - Otherwise: record `size_level = normal`

**Validation result**: Store the outcome as:
```
validation_status: OK | WARN | ERROR
missing_headers: [] (list of missing header names, empty if all present)
orphaned_lines: 0 (count of content lines outside any section)
total_lines: N
size_level: normal | warn | error
```

Determine `validation_status`:
- `OK` — all 6 headers present, 0 orphaned lines, size normal
- `WARN` — all headers present but size >500, or orphaned lines detected
- `ERROR` — any headers missing, or size >1000

**Auto-repair** (if `missing_headers` is non-empty):

1. Re-read the current `execution_context.md`
2. For each missing header, insert it (with an empty line below) in the correct position according to the canonical section order:
   - Place it immediately before the next section header that IS present
   - If no subsequent headers exist, append it at the end of the file
3. Write the repaired file using Write
4. If the repair write succeeds, update `validation_status` to `REPAIRED` and log:
   ```
   Context validation: auto-repaired missing headers: {list of re-inserted headers}
   ```
5. If the repair write fails, log the error in `task_log.md` and continue with best-effort context:
   ```
   Append to task_log.md: | — | Context validation | ERROR | Wave {N} | — | Auto-repair failed: {error details} |
   ```

**Force compaction** (if `size_level` is `error`, i.e., >1000 lines):

After auto-repair (if needed), apply aggressive compaction to ALL sections:

1. **Sections 1-5** (Project Setup through Known Issues): Keep the 3 most recent entries. Summarize all older entries into a single paragraph at the top of the section.
2. **Task History**: Keep the 5 most recent entries. Summarize all older entries into a single "Session Summary" paragraph at the top of the section.
3. Write the compacted file using Write
4. Re-check line count after compaction. If still >1000 lines, log a warning but proceed — the content is legitimately large:
   ```
   Context validation: file still >1000 lines ({N}) after force compaction — content is legitimately large
   ```

**Log validation results**:

- If `validation_status` is `OK`: no logging needed, no `task_log.md` entry
- If any issues detected (`WARN`, `ERROR`, or `REPAIRED`): append a diagnostic row to `task_log.md` using the read-modify-write pattern:
  ```markdown
  | — | Context validation | {WARN/ERROR/REPAIRED} | Wave {N} | — | {summary} |
  ```
  Where `{summary}` combines all findings, e.g.: `"Missing: ## File Patterns (repaired); 523 lines (warn); 3 orphaned lines"`

**Include in wave completion summary**: After validation completes, append a `## Context Health` section to `progress.md` as part of the wave status update (same read-modify-write cycle as the 7d.6 batch update). Add it after the `## Completed This Session` entries:

```markdown
## Context Health (Wave {N})
- Headers: {6/6 | 5/6 — repaired | N/6 — repair failed}
- Size: {total_lines} lines {(OK) | (WARN: >500) | (ERROR: >1000, compacted)}
- Orphaned content: {0 lines | N lines flagged}
```

If validation status is `OK` (all headers present, no orphaned content, size normal), emit a compact form:
```markdown
## Context Health (Wave {N})
- Status: OK
```

Each wave's Context Health section replaces the previous wave's section (only the latest wave's health is shown in `progress.md`).

#### Cleanup

7. Delete the `context-task-{id}.md` files
8. **Clean up result files**: Delete `result-task-{id}.md` for PASS tasks, **unless** the task has a `produces_for` field with entries pointing to not-yet-completed tasks (retain for upstream injection in later waves). Retain `result-task-{id}.md` for FAIL tasks (available for post-session analysis in the archived session folder). Delete retained `produces_for` result files only after all tasks listed in the producer's `produces_for` have completed.

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
Total execution time: {sum of all task duration_ms values, formatted}
Token Usage: {sum of all task total_tokens values, formatted with commas}

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
