# Orchestration Reference

This reference provides the detailed 10-step orchestration loop for executing Claude Code Tasks in dependency order. The execute-tasks skill uses this procedure to manage the full execution session.

## Step 1: Load Task List

Use `TaskList` to get all tasks and their current state.

If a `--task-group` argument was provided, filter the task list to only tasks where `metadata.task_group` matches the specified group. If no tasks match the group, inform the user and stop.

If a specific `task-id` argument was provided, validate it exists. If it doesn't exist, inform the user and stop.

## Step 2: Validate State

Handle edge cases before proceeding:

- **Empty task list**: Report "No tasks found. Use `/claude-alchemy-sdd:create-tasks` to generate tasks from a spec, or create tasks manually with TaskCreate." and stop.
- **All completed**: Report a summary of completed tasks and stop.
- **Specific task-id is blocked**: Report which tasks are blocking it and stop.
- **No unblocked tasks**: Report which tasks exist and what's blocking them. Detect circular dependencies and report if found.

## Step 3: Build Execution Plan

### 3a: Resolve Max Parallel

Determine the maximum number of concurrent tasks per wave using this precedence:
1. `--max-parallel` CLI argument (highest priority)
2. `max_parallel` setting in `.claude/claude-alchemy.local.md`
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

Break ties by "unblocks most others" -- tasks that appear in the most `blockedBy` lists of other tasks execute first.

If a wave contains more tasks than `max_parallel`, split into sub-waves of `max_parallel` size, maintaining the priority ordering.

### 3e: Circular Dependency Detection

Detect circular dependencies: if any tasks remain unassigned after topological sorting, they form a cycle. Report the cycle to the user and attempt to break at the weakest link (task with fewest blockers).

## Step 4: Check Settings

Read `.claude/claude-alchemy.local.md` if it exists, for any execution preferences.

This is optional -- proceed without settings if not found.

## Step 4.5: Resolve Team Strategy

Determine the team strategy for each task in the execution plan. Strategy resolution uses a four-level cascade with highest-precedence-wins semantics. See `references/team-strategies.md` for strategy definitions.

### 4.5a: Resolve Session Default Strategy

Determine the session-level default strategy using this precedence:
1. `--team-strategy <name>` CLI argument (highest priority)
2. `team_strategy` setting in `.claude/claude-alchemy.local.md`
3. Default: `solo`

**Settings file missing**: If `.claude/claude-alchemy.local.md` does not exist or does not contain a `team_strategy` field, skip to the next level. The default `solo` is used if no higher-priority source provides a value.

**Malformed settings file**: If the settings file exists but cannot be parsed or the `team_strategy` field contains non-string data, log a warning: `WARNING: Could not read team_strategy from .claude/claude-alchemy.local.md -- defaulting to solo` and use `solo`.

### 4.5b: Validate Strategy Name

Validate the resolved session default against the allowed values: `solo`, `review`, `research`, `full`.

If the strategy name is not in the allowed list:
- Log: `WARNING: Invalid team strategy "{name}" -- falling back to solo`
- Fall back to `solo`

Validation is case-sensitive. Only lowercase values are accepted.

### 4.5c: Resolve Per-Task Strategies

For each task in the execution plan, resolve its effective strategy:

1. Check `metadata.team_strategy` on the task
2. If present and valid (`solo`, `review`, `research`, `full`): use it as this task's strategy
3. If present but invalid: log `WARNING: Invalid team strategy "{name}" on task [{id}] -- falling back to session default` and use the session default
4. If absent: use the session default

Each task resolves its strategy independently. A single session may have tasks using different strategies (e.g., some tasks use `solo` while others use `review`).

### 4.5d: Record Resolved Strategies

Store the resolved strategy for each task so it can be:
- Displayed in the execution plan (Step 5)
- Used by the execute loop (Step 7) to determine whether to spawn a solo agent or a team

Record format per task:
```
task_id: {id}
resolved_strategy: {solo|review|research|full}
strategy_source: {default|settings|cli|task_metadata}
```

Where `strategy_source` indicates which cascade level provided the value:
- `default` -- no configuration specified, using built-in default
- `settings` -- from `.claude/claude-alchemy.local.md`
- `cli` -- from `--team-strategy` CLI argument
- `task_metadata` -- from `metadata.team_strategy` on the individual task

## Step 5: Present Execution Plan and Confirm

Display the execution plan:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXECUTION PLAN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tasks to execute: {count}
Retry limit: {retries} per task
Max parallel: {max_parallel} per wave
Team strategy: {session_default_strategy}

{If any tasks have per-task overrides:}
Per-task overrides: {count} tasks with non-default strategies

WAVE 1 ({n} tasks):
  1. [{id}] {subject} ({priority}) [{strategy}]
  2. [{id}] {subject} ({priority}) [{strategy}]
  ...

WAVE 2 ({n} tasks):
  3. [{id}] {subject} ({priority}) [{strategy}] -- after [{dep_ids}]
  4. [{id}] {subject} ({priority}) [{strategy}] -- after [{dep_ids}]
  ...

{Additional waves...}

BLOCKED (unresolvable dependencies):
  [{id}] {subject} -- blocked by: {blocker ids}
  ...

COMPLETED:
  {count} tasks already completed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

The `[{strategy}]` tag is shown for each task. When all tasks use the session default, the tag may be omitted from individual task lines for brevity (the header `Team strategy:` line communicates the default). When any tasks differ from the session default, show the `[{strategy}]` tag on every task line to make overrides visible.

After displaying the plan, use AskUserQuestion to confirm:

```yaml
questions:
  - header: "Confirm Execution"
    question: "Ready to execute {count} tasks in {wave_count} waves (max {max_parallel} parallel, strategy: {session_default_strategy}) with up to {retries} retries per task?"
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
1. IF `--task-group` was provided -> `{task_group}-{YYYYMMDD}-{HHMMSS}` (e.g., `user-auth-20260131-143022`)
2. ELSE IF all open tasks (pending + in_progress) share the same non-empty `metadata.task_group` -> `{task_group}-{YYYYMMDD}-{HHMMSS}`
3. ELSE -> `exec-session-{YYYYMMDD}-{HHMMSS}` (e.g., `exec-session-20260131-143022`)

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
     - "Force start (remove lock)" -- delete the lock and proceed
     - "Cancel" -- abort execution
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
6. **`execution_pointer.md`** at `$HOME/.claude/tasks/{CLAUDE_CODE_TASK_LIST_ID}/execution_pointer.md` -- Create immediately with the fully resolved absolute path to the live session directory (e.g., `/Users/sequenzia/dev/repos/my-project/.claude/sessions/__live_session__/`). Construct this by prepending the current working directory to `.claude/sessions/__live_session__/`. This ensures the pointer exists even if the session is interrupted before completing.

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

#### 7a.1: Detect Team Groups

After selecting tasks for the wave, identify tasks that share a `metadata.team_group` value:

1. For each task in the wave, check `metadata.team_group`
2. Group tasks with the same non-empty `team_group` value together
3. Tasks without `team_group` (or with an empty value) are treated as ungrouped -- they follow standard solo or per-task team behavior

**Team group records**: For each detected group, create a group record:
```
group_id: {team_group value}
tasks: [{task_id_1}, {task_id_2}, ...]
resolved_strategy: {most complex strategy among group members}
team_name: group-team-{team_group}-{timestamp}
status: pending
```

**Strategy resolution for groups**: If group members have different `resolved_strategy` values (from Step 4.5), use the most complex strategy for the entire group. Complexity order (highest to lowest):
1. `full`
2. `research`
3. `review`
4. `solo`

For example, if one task resolved to `review` and another to `full`, the group uses `full`. Log the override: `Group "{team_group}": resolved strategy to {strategy} (highest complexity among {n} members)`

**Single-task groups**: If only one task has a particular `team_group` value (no other tasks share it, either in this wave or in later waves), treat it as an ungrouped task -- it follows standard per-task behavior. The `team_group` metadata is effectively ignored when the group contains a single task.

#### 7a.2: Check for Active Cross-Wave Groups

Before forming new groups, check for team groups that were started in a previous wave and still have pending tasks:

1. Scan the active group registry for groups with `status: active` and remaining tasks
2. If any tasks in the current wave belong to an already-active group, assign them to the existing group's team (do NOT create a new team)
3. Update the group record with the newly assigned tasks

This ensures team context carries forward across wave boundaries without re-reading the full codebase.

### 7b: Snapshot Execution Context

Read `.claude/sessions/__live_session__/execution_context.md` and hold it as the baseline for this wave. All agents in this wave will read from this same snapshot. This prevents concurrent agents from seeing partial context writes from sibling tasks.

### 7c: Launch Wave Agents

1. Mark all wave tasks as `in_progress` via `TaskUpdate`
2. Record `wave_start_time`
3. Update `progress.md`:
   ```markdown
   # Execution Progress
   Status: Executing
   Wave: {current_wave} of {total_waves}
   Max Parallel: {max_parallel}
   Updated: {ISO 8601 timestamp}

   ## Active Tasks
   - [{id}] {subject} -- Launching agent
   - [{id}] {subject} -- Launching agent
   ...

   ## Completed This Session
   {accumulated completed tasks from prior waves}
   ```
4. Launch all wave agents simultaneously using **parallel Task tool calls in a single message turn**:

For each task in the wave, look up the task's `resolved_strategy` from Step 4.5d. If the strategy is `solo`, use the `task-executor` agent. For team strategies (`review`, `research`, `full`), use the `team-task-executor` agent. Both agent types are launched via parallel Task tool calls in the same message turn.

**Solo strategy** -- use the Task tool with `task-executor`:

```
Task:
  subagent_type: claude-alchemy-sdd:task-executor
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
    Do NOT write to execution_context.md directly.
    Do NOT update progress.md -- the orchestrator manages it.
    Write your learnings to the Context Write Path above instead.

    {If retry attempt:}
    RETRY ATTEMPT {n} of {max_retries}
    Previous attempt failed with:
    ---
    {previous verification report}
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
    8. Return a structured verification report
    9. Report any token/usage information available from your session
```

**Team strategies** (`review`, `research`, `full`) -- use the Task tool with `team-task-executor`:

Each team task is delegated to a `team-task-executor` agent that manages the full team lifecycle independently. The orchestrator does NOT call TeamCreate, TeamDelete, or SendMessage -- these are handled internally by each `team-task-executor` instance.

```
Task:
  subagent_type: claude-alchemy-sdd:team-task-executor
  prompt: |
    Execute task [{id}] using the {strategy} team strategy.

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

    Team Strategy: {review|research|full}

    CONCURRENT EXECUTION MODE
    Context Write Path: .claude/sessions/__live_session__/context-task-{id}.md
    Team Activity Path: .claude/sessions/__live_session__/team_activity_task-{id}.md
    Do NOT write to execution_context.md directly.
    Do NOT update progress.md -- the orchestrator manages it.

    Execution Context Snapshot:
    ---
    {snapshot content}
    ---

    {If retry attempt:}
    RETRY ATTEMPT {n} of {max_retries}
    Previous attempt failed with:
    ---
    {previous verification report}
    ---

    {If degradation history from previous attempts:}
    DEGRADATION HISTORY:
    {degradation history entries}

    Instructions:
    1. Read the execute-tasks skill and team-strategies reference
    2. Create a team and coordinate the {strategy} workflow
    3. Handle degradation if agents fail (Full -> Review -> Solo)
    4. Write team activity updates to .claude/sessions/__live_session__/team_activity_task-{id}.md
    5. Write learnings to .claude/sessions/__live_session__/context-task-{id}.md
    6. Clean up the team (TeamDelete) on all exit paths
    7. Return a structured verification report
```

**Solo tasks do not create any team infrastructure** -- no TeamCreate, no team_activity file, zero overhead compared to existing behavior.

#### Delegation Architecture

The orchestrator delegates all team management to `team-task-executor` agents. Each `team-task-executor` instance is a separate agent process that:

- Creates its own team via `TeamCreate` (the one-team-per-leader constraint applies per agent, not globally)
- Spawns role agents (`team-explorer`, `team-implementer`, `team-reviewer`) into its team
- Coordinates the sequential workflow (explorer -> implementer -> reviewer) via `SendMessage`
- Handles strategy degradation internally (Full -> Review -> Solo)
- Writes `team_activity_task-{id}.md` to the session directory
- Falls back to direct implementation when degradation reaches Solo (it has Write/Edit tools)
- Cleans up via `TeamDelete` on all exit paths
- Returns a structured verification report in the same format as `task-executor`

This delegation solves the concurrent team execution problem: the orchestrator is no longer the team leader for all teams, so multiple teams can run simultaneously without hitting the "one team per leader" constraint.

**The orchestrator never calls**: `TeamCreate`, `TeamDelete`, or `SendMessage`. These tools are used exclusively by `team-task-executor` agents.

#### Graceful Degradation

Degradation is handled entirely within each `team-task-executor` agent. The orchestrator does not need to manage degradation -- it simply receives the final result (PASS/PARTIAL/FAIL) and the degradation history from the agent's report.

Each `team-task-executor` follows these degradation chains internally:

| Starting Strategy | Chain | Terminal Fallback |
|-------------------|-------|-------------------|
| **Full** | Full -> Review -> Solo | Returns FAIL to orchestrator |
| **Review** | Review -> Solo | Returns FAIL to orchestrator |
| **Research** | Research -> Solo | Returns FAIL to orchestrator |

**Degradation does not count against the task retry limit.** If a `team-task-executor` exhausts all degradation options and reaches Solo, it attempts Solo execution directly (using its own Read/Write/Edit tools). If Solo also fails, it returns a FAIL result to the orchestrator. The orchestrator then handles retries using the standard retry flow (Step 7e).

**Retry interaction:** When retrying a task that previously degraded, the orchestrator includes the degradation history in the retry prompt. All retries after initial degradation use `task-executor` (solo) -- team strategies are not re-attempted during retries.

**Recording the final strategy:** The `team-task-executor` includes the final strategy, original strategy, and degradation count in its verification report. The orchestrator records these in `task_log.md`:
```markdown
| {id} | {subject} | {PASS/PARTIAL/FAIL} | {attempt}/{max} [{final_strategy}] | {duration} | {token_usage} |
```

Degradation events are also logged by the `team-task-executor` to `task_log.md` if they have write access, or included in the verification report for the orchestrator to log:
```markdown
| {id} | {subject} | DEGRADED | {original} -> {new} | {reason} | {timestamp} |
```

#### Concurrent Teams

Multiple `team-task-executor` instances run in parallel within a wave, each creating its own independent team. Since each `team-task-executor` is a separate agent process acting as its own team leader, there is no "one team per leader" constraint violation.

- Each `team-task-executor` creates its own team with a unique name: `task-team-{task-id}-{timestamp}`
- Each team has its own `team_activity_task-{id}.md` file -- no file write contention
- Teams do not interact with each other
- The orchestrator tracks results as they return from each `team-task-executor`
- A wave completes when ALL Task tool calls (both `task-executor` and `team-task-executor`) have returned

Example: A wave with 3 tasks might look like:
```
Parallel Task tool calls:
- [15] Fix typo in README -- task-executor (solo)
- [42] Add user authentication -- team-task-executor (review strategy)
- [99] Implement payment flow -- team-task-executor (full strategy)
```

All three launch concurrently as parallel Task tool calls in a single message turn. Task 15 returns first (simple solo task). Tasks 42 and 99 each manage their own team lifecycle independently and return when complete.

**Important**: When `max_parallel` is 1, omit the `CONCURRENT EXECUTION MODE` section from the solo agent prompt. The agent will write directly to `execution_context.md` as in the original sequential behavior. Team tasks always use `team_activity_task-{id}.md` regardless of `max_parallel`.

#### Cross-Task Team Groups

When tasks share a `metadata.team_group` value (detected in Step 7a.1), they are assigned to a single `team-task-executor` instance that executes them sequentially within one team. This allows agents to maintain context (explored files, patterns, codebase understanding) across task boundaries.

##### Group Execution via team-task-executor

When a group of tasks is detected in a wave, the orchestrator launches a single `team-task-executor` with all group task details:

```
Task:
  subagent_type: claude-alchemy-sdd:team-task-executor
  prompt: |
    Execute the following group of tasks using the {strategy} team strategy.

    Group: {team_group}
    Tasks:
    ---
    Task [{id_1}]: {subject_1}
    {description_1}
    ---
    Task [{id_2}]: {subject_2}
    {description_2}
    ---
    ...

    Team Strategy: {resolved group strategy}

    CONCURRENT EXECUTION MODE
    Context Write Path prefix: .claude/sessions/__live_session__/context-task-
    Team Activity Path: .claude/sessions/__live_session__/team_activity_group-{team_group}.md
    ...
```

The `team-task-executor` handles the group lifecycle internally:
1. Creates one team for the entire group
2. Runs the explorer (if applicable) only for the first task
3. Executes tasks sequentially within the team, reusing agent context
4. Writes a shared `team_activity_group-{team_group}.md` file
5. Writes per-task `context-task-{id}.md` files for each completed task
6. Cleans up the team after all group tasks complete
7. Returns a combined report covering all group tasks

##### Cross-Wave Group Handling

Groups whose tasks span multiple waves are handled with fresh `team-task-executor` instances per wave:

1. Each wave's group tasks are launched in a new `team-task-executor` (team recreated each wave)
2. Group context continuity comes from `execution_context.md` merge between waves -- the orchestrator merges all `context-task-{id}.md` files from the previous wave before launching the next wave
3. The new `team-task-executor` receives the merged execution context snapshot, which includes learnings from the group's previous wave
4. No persistent background team slots or complex lifecycle management required

**Wave boundary note**: The `team_activity_group-{team_group}.md` file from the previous wave is preserved (not deleted during merge). The new wave's `team-task-executor` creates a new activity file with a different timestamp if needed, or continues the existing one.

##### Wave Slot Accounting for Groups

Since grouped tasks are sent to a single `team-task-executor` instance, they occupy a single concurrent slot in the wave (not one slot per task):

- A group of 3 tasks counts as 1 slot against `max_parallel`
- Other solo tasks and independent team tasks can run concurrently alongside the group
- The group `team-task-executor` finishes when all its tasks complete

##### progress.md Display for Groups

Active groups are displayed in `progress.md` with group context:

```markdown
## Active Tasks
- [Group: {team_group}] Team: {strategy} -- Task [{id}] {subject} (2/4 tasks complete)
- [15] Fix typo in README -- Solo
- [42] Add user authentication -- Team: review (executing)
```

### 7d: Process Results

As each task completes (whether via `task-executor` return or `team-task-executor` return):

1. Calculate `duration = current_time - task_start_time`. Format: <60s = `{s}s`, <60m = `{m}m {s}s`, >=60m = `{h}h {m}m {s}s`
2. Capture token usage from the Task tool response if available, otherwise `N/A`
3. Append a row to `.claude/sessions/__live_session__/task_log.md`:
   ```markdown
   | {id} | {subject} | {PASS/PARTIAL/FAIL} | {attempt_number}/{max_retries} | {duration} | {token_usage or N/A} |
   ```
   For team tasks, duration includes the full `team-task-executor` lifecycle (all agent phases). Token usage is the sum across all agents in the team if available (reported by the `team-task-executor` in its verification report).
4. Log a brief status line: `[{id}] {subject}: {PASS|PARTIAL|FAIL}`
   For team tasks, append the strategy: `[{id}] {subject}: {PASS|PARTIAL|FAIL} (strategy: {strategy})`
5. Update `progress.md` -- move the task from Active Tasks to Completed This Session:
   ```markdown
   ## Active Tasks
   - [{other_id}] {subject} -- Phase 2 -- Implementing
   ...

   ## Completed This Session
   - [{id}] {subject} -- PASS ({duration})
   - [{id}] {subject} -- Team: {strategy} -- PASS ({duration})
   {prior completed entries}
   ```
   Solo tasks show the standard format. Team tasks include the strategy name.

**Context append fallback**: If an agent's report contains a `LEARNINGS:` section (indicating the agent failed to write to its context file), manually write those learnings to `.claude/sessions/__live_session__/context-task-{id}.md`.

**Team context**: For team tasks, the `team-task-executor` writes learnings to `context-task-{id}.md` directly. The orchestrator does not need to extract team learnings -- they are already in the per-task context file when the `team-task-executor` returns.

### 7e: Within-Wave Retry

After processing a failed result:

1. Check retry count for the failed task
2. If retries remaining:
   - Re-launch the agent immediately with failure context included in the prompt
   - Update `progress.md` active task entry: `- [{id}] {subject} -- Retrying ({n}/{max})`
   - Do NOT wait for other wave agents to complete -- retry occupies an existing slot
3. If retries exhausted:
   - Leave task as `in_progress`
   - Log final failure
   - The slot is freed for any remaining retries

### 7f: Merge Context After Wave

After ALL tasks in the current wave have completed (including retries and team lifecycles):

1. Read all `context-task-{id}.md` files from `.claude/sessions/__live_session__/`
2. Append their contents to `.claude/sessions/__live_session__/execution_context.md` in task ID order
3. Delete the `context-task-{id}.md` files
4. For team tasks: the `team-task-executor` already wrote learnings to `context-task-{id}.md`, so no special extraction from `team_activity_task-{id}.md` files is needed

**Skip merge when `max_parallel` is 1** -- agents already wrote directly to `execution_context.md`.

**Team activity files are NOT deleted during merge** -- they persist in `__live_session__/` for the Task Manager to read and are archived with the session in Step 8.

**Cross-task group activity files**: `team_activity_group-{team_group}.md` files are also NOT deleted during merge. If the group is still active (has remaining tasks in later waves), the file persists and continues to accumulate entries. If the group completed during this wave, the file stays for archival.

### 7g: Rebuild Next Wave and Archive

1. Archive completed task files: for each PASS task in this wave, copy the task's JSON from `~/.claude/tasks/{CLAUDE_CODE_TASK_LIST_ID}/` to `.claude/sessions/__live_session__/tasks/`
2. **Team group cleanup**: Team groups are cleaned up internally by their `team-task-executor` instances. The orchestrator does not need to call TeamDelete for groups -- the `team-task-executor` handles this before returning
3. Use `TaskList` to refresh the full task state
4. Check if any previously blocked tasks are now unblocked
5. If newly unblocked tasks found, form the next wave using priority sort from Step 3d
6. If no unblocked tasks remain, exit the loop
7. Loop back to 7a

## Step 8: Session Summary

Update `progress.md` with final status:
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

{If any team strategies were used:}
Team Strategies:
  Solo: {count} tasks
  Review: {count} tasks
  Research: {count} tasks
  Full: {count} tasks
  Degradations: {count} (e.g., Full -> Review: {n}, Review -> Solo: {n})

Remaining:
  Pending: {count}
  In Progress (failed): {count}
  Blocked: {count}

{If any tasks failed:}
FAILED TASKS:
  [{id}] {subject} [{strategy}] -- {brief failure reason}
  ...

{If newly unblocked tasks were discovered:}
NEWLY UNBLOCKED:
  [{id}] {subject} -- unblocked by completion of [{blocker_id}]
  ...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

The `Team Strategies:` section is only included when at least one task used a non-solo strategy. If all tasks used solo, this section is omitted to keep the summary concise.

After displaying the summary:
1. Save `session_summary.md` to `.claude/sessions/__live_session__/` with the full summary content
2. **Archive the session**: Create `.claude/sessions/{task_execution_id}/` and move all contents from `__live_session__/` to the archival folder. The `.lock` file is moved to the archive along with all other session files (including `team_activity_task-*.md` and `team_activity_group-*.md` files), releasing the concurrency guard. All team cleanup is handled by `team-task-executor` agents before they return, so no team cleanup is needed at archival time.
3. `__live_session__/` is left as an empty directory (not deleted)
4. `execution_pointer.md` stays pointing to `__live_session__/` (no update needed -- it will be empty until the next execution)

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
- Each task is handled by the `claude-alchemy-sdd:task-executor` agent (Solo strategy) or by the `claude-alchemy-sdd:team-task-executor` agent (Review, Research, Full strategies)
- The execution context file enables knowledge sharing across task boundaries
- Failed tasks remain as `in_progress` for manual review or re-execution
- Run the execute-tasks skill again to pick up where you left off -- it will execute any remaining unblocked tasks
- All file operations within `.claude/sessions/` (including `__live_session__/` and archival folders) and `execution_pointer.md` are auto-approved by the `auto-approve-session.sh` PreToolUse hook and should never prompt for user confirmation
