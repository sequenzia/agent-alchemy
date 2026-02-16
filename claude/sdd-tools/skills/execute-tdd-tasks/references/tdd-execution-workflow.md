# TDD Execution Workflow Reference

This reference documents the TDD-aware execution workflow for the `execute-tdd-tasks` skill. It extends the standard `execute-tasks` orchestration with TDD-specific wave grouping, strategic parallelism, agent routing, and context sharing between RED and GREEN phases.

---

## Wave-Based TDD Execution

### Overview

TDD execution adapts the standard wave-based execution model to enforce RED-GREEN-REFACTOR sequencing within each task pair while maximizing parallelism across independent pairs. The key difference from standard execution: test tasks (RED phase) and their paired implementation tasks (GREEN phase) are NEVER in the same wave.

```
Standard execute-tasks:    Wave 1: [A, B, C]  ->  Wave 2: [D, E]  ->  Wave 3: [F]

TDD execute-tdd-tasks:     Wave 1: [Test-A, Test-B, Test-C]  ->  Wave 2: [A, B, C]  ->  Wave 3: [Test-D, Test-E]  ->  Wave 4: [D, E]
```

### Wave Assignment Rules

TDD tasks follow the same topological sorting as standard execution, but the dependency graph already encodes the RED-before-GREEN ordering (test tasks block their paired implementation tasks). The wave assignment algorithm from `execute-tasks` works unchanged — the TDD dependency structure naturally produces alternating test/implementation waves.

**Wave formation process:**

1. Build the full dependency graph from all tasks (TDD pairs + non-TDD tasks)
2. Run topological sort to assign dependency levels
3. Assign tasks to waves by dependency level (same as standard `execute-tasks`)
4. Sort within waves by priority, break ties by "unblocks most others"
5. Cap each wave at `max_parallel` tasks

The dependency structure created by `create-tdd-tasks` ensures:

- Test tasks inherit upstream dependencies from their paired implementation task
- Implementation tasks are blocked by their paired test task
- Downstream tasks still depend on the implementation task (not the test task)

This means test tasks naturally land in earlier waves than their paired implementation tasks.

### Strategic Parallelism

TDD execution follows two parallelism rules that apply simultaneously:

#### PARALLEL: Test generation across features

Multiple test-writer agents can generate tests simultaneously for different features. Test tasks at the same dependency level run in parallel within a single wave.

```
Wave N: [Test-UserModel, Test-OrderModel, Test-ProductModel]
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
         All three run in parallel (up to max_parallel)
```

This is the primary mechanism for recovering execution time lost to the doubled task count. With N independent features, test generation runs at the same speed as a single test task.

#### SEQUENTIAL: RED-GREEN-REFACTOR within a task pair

Within a single TDD pair, the phases are strictly sequential. The test task (RED) must complete before the implementation task (GREEN) can start. This is enforced by the dependency chain — the implementation task is `blockedBy` the test task.

```
Test-UserModel (Wave N)  -->  UserModel (Wave N+1)
     RED phase                 GREEN + REFACTOR phases
     Must complete first       Cannot start until RED is done
```

### Wave Grouping Pattern

In the ideal case, waves alternate between test and implementation tasks:

```
Wave 1: Test tasks for root-level features     (RED phase, parallel)
Wave 2: Implementation tasks for Wave 1 tests  (GREEN phase, parallel)
Wave 3: Test tasks for next dependency level    (RED phase, parallel)
Wave 4: Implementation tasks for Wave 3 tests  (GREEN phase, parallel)
...
```

In practice, waves may contain a mix of test and implementation tasks when the dependency graph has multiple depth levels or non-TDD tasks interspersed.

---

## Session Management

### Reuse from execute-tasks

The `execute-tdd-tasks` skill reuses the entire session management infrastructure from `execute-tasks`:

| Component | Behavior | Notes |
|-----------|----------|-------|
| Session ID (`task_execution_id`) | Same three-tier resolution | `--task-group`, shared group, or `exec-session-` prefix |
| Session directory | `.claude/sessions/__live_session__/` | Same structure and lifecycle |
| Execution context | `execution_context.md` with standard sections | Same template, same merge behavior |
| Task log | `task_log.md` with standard table format | Same columns, same append pattern |
| Progress tracking | `progress.md` with active/completed sections | Same update pattern |
| Execution plan | `execution_plan.md` | Same format with TDD-specific annotations |
| Execution pointer | `~/.claude/tasks/{TASK_LIST_ID}/execution_pointer.md` | Same location and format |
| Concurrency guard | `.lock` file in `__live_session__/` | Same lock mechanism |
| Stale session cleanup | Archive to `interrupted-{timestamp}/` | Same recovery procedure |
| Per-task context files | `context-task-{id}.md` per agent | Same isolation pattern |
| Context merge | Orchestrator merges after each wave | Same merge procedure |

### TDD-Specific Session Extensions

The execution plan includes TDD-specific annotations:

```markdown
EXECUTION PLAN (TDD Mode)

Tasks to execute: {count} ({tdd_pairs} TDD pairs, {non_tdd} non-TDD tasks)
Retry limit: {retries} per task
Max parallel: {max_parallel} per wave
TDD Strictness: {strict|normal|relaxed}

WAVE 1 ({n} tasks — RED phase):
  1. [{id}] Write tests for {subject} (RED, paired: #{impl_id})
  2. [{id}] Write tests for {subject} (RED, paired: #{impl_id})

WAVE 2 ({n} tasks — GREEN phase):
  3. [{id}] {subject} (GREEN, paired: #{test_id})
  4. [{id}] {subject} (GREEN, paired: #{test_id})

WAVE 3 ({n} tasks — mixed):
  5. [{id}] {subject} (non-TDD)
  6. [{id}] Write tests for {subject} (RED, paired: #{impl_id})
```

The execution context gains a TDD compliance summary section:

```markdown
## TDD Compliance
| Task Pair | RED Verified | GREEN Verified | Refactored | Coverage Delta |
|-----------|-------------|----------------|------------|----------------|
```

---

## Agent Spawning

### Agent Routing

The `execute-tdd-tasks` skill routes tasks to different agent types based on metadata:

| Task Type | Detection | Agent | Plugin |
|-----------|-----------|-------|--------|
| TDD test task | `metadata.tdd_mode == true` AND `metadata.tdd_phase == "red"` | `tdd-executor` | tdd-tools |
| TDD implementation task | `metadata.tdd_mode == true` AND `metadata.tdd_phase == "green"` | `tdd-executor` | tdd-tools |
| Non-TDD task | No `tdd_mode` metadata or `tdd_mode == false` | `task-executor` | sdd-tools |

### Agent Spawning for TDD Tasks

TDD tasks are launched using the `tdd-executor` agent from `tdd-tools`:

```
Task:
  subagent_type: tdd-executor
  mode: bypassPermissions
  prompt: |
    Execute the following TDD task.

    Task ID: {id}
    Task Subject: {subject}
    Task Description:
    ---
    {full description}
    ---

    Task Metadata:
    - Priority: {priority}
    - Complexity: {complexity}
    - TDD Phase: {tdd_phase}
    - Paired Task ID: {paired_task_id}
    - TDD Strictness: {strictness}

    CONCURRENT EXECUTION MODE
    Context Write Path: .claude/sessions/__live_session__/context-task-{id}.md
    Do NOT write to execution_context.md directly.
    Do NOT update progress.md — the orchestrator manages it.
    Write your learnings to the Context Write Path above instead.

    {If GREEN phase, include test task output:}
    PAIRED TEST TASK OUTPUT:
    ---
    {test task verification report and context}
    ---
    The tests written by the paired test task are already on disk.
    Your job is to implement code that makes these tests pass (GREEN phase),
    then refactor while keeping tests green (REFACTOR phase).
```

### Agent Spawning for Non-TDD Tasks

Non-TDD tasks use the standard `task-executor` agent from `sdd-tools`, with the same prompt format as standard `execute-tasks`.

---

## Context Sharing Between TDD Phases

### Test-to-Implementation Context Flow

When a test task (RED phase) completes, its output informs the paired implementation task (GREEN phase). This context flows through two channels:

#### Channel 1: Per-Task Context File

The test task writes its learnings to `context-task-{test_id}.md`. After the test wave completes, the orchestrator merges this into `execution_context.md`. The implementation task reads the merged context in the next wave.

**Information captured by test tasks:**

- Test file locations and paths
- Test framework and conventions used
- Number of tests written and their descriptions
- Expected import paths and module structure
- Fixtures or test utilities created
- Pre-existing test baseline (pass/fail counts)

#### Channel 2: Direct Prompt Injection

The orchestrator includes the test task's verification report directly in the implementation task's prompt (see `PAIRED TEST TASK OUTPUT` above). This provides:

- Which tests were written and where
- RED verification results (all tests failed as expected)
- Any warnings or anomalies from the RED phase
- Specific error messages from test failures (useful for understanding what needs to be implemented)

### Context Flow Diagram

```
Wave N (RED phase):
  Test-Task-A writes:  context-task-{A}.md
  Test-Task-B writes:  context-task-{B}.md

  Orchestrator merges: context-task-{A}.md + context-task-{B}.md -> execution_context.md

Wave N+1 (GREEN phase):
  Impl-Task-A reads:   execution_context.md (contains A's and B's learnings)
  Impl-Task-A receives: Test-Task-A's verification report in prompt
  Impl-Task-B reads:   execution_context.md (contains A's and B's learnings)
  Impl-Task-B receives: Test-Task-B's verification report in prompt
```

### What Implementation Tasks Learn from Test Tasks

The paired test task output tells the implementation agent:

1. **What to implement**: Test assertions define the expected behavior
2. **Where tests live**: File paths for running targeted tests
3. **What the interface should look like**: Import paths and function signatures implied by tests
4. **What errors to handle**: Error-scenario tests define expected error behavior
5. **Baseline state**: Pre-existing test pass/fail counts for regression detection

---

## Mixed TDD and Non-TDD Tasks

### Detection

A task group may contain both TDD pairs and non-TDD tasks. The orchestrator detects task types via metadata:

- `metadata.tdd_mode == true` indicates a TDD task (either `red` or `green` phase)
- Tasks without `tdd_mode` metadata or with `tdd_mode == false` are non-TDD

### Execution Strategy

Mixed groups are handled naturally by the wave-based execution model:

1. **Wave assignment**: All tasks (TDD and non-TDD) are assigned to waves based on dependency level
2. **Agent routing**: Each task is routed to the appropriate agent based on its type
3. **No special ordering**: Non-TDD tasks run whenever their dependencies are satisfied, regardless of TDD wave patterns

```
Example mixed execution:
  Wave 1: [Test-Model (TDD/RED), Config-Setup (non-TDD)]     -- parallel
  Wave 2: [Model-Impl (TDD/GREEN)]                           -- depends on Test-Model
  Wave 3: [Test-API (TDD/RED), Migration-Script (non-TDD)]   -- parallel
  Wave 4: [API-Impl (TDD/GREEN)]                             -- depends on Test-API
```

### Non-TDD Task Handling

Non-TDD tasks within a TDD execution session:

- Use the standard `task-executor` agent (not `tdd-executor`)
- Follow the standard 4-phase workflow (Understand, Implement, Verify, Complete)
- Write to per-task context files like all other tasks
- Are included in the session summary and task log
- Do NOT appear in the TDD compliance summary

---

## Max Parallel Configuration

### Setting Resolution

The `max_parallel` setting follows the same precedence as standard `execute-tasks`:

1. `--max-parallel` CLI argument (highest priority)
2. `max_parallel` in `.claude/agent-alchemy.local.md` (settings file)
3. Default: **5**

### Impact on TDD Execution

With `max_parallel = 5` and 8 independent test tasks:

```
Wave N (RED phase):
  Sub-wave N.1: [Test-1, Test-2, Test-3, Test-4, Test-5]  -- 5 parallel
  Sub-wave N.2: [Test-6, Test-7, Test-8]                   -- 3 parallel (remaining)

Wave N+1 (GREEN phase):
  Sub-wave (N+1).1: [Impl-1, Impl-2, Impl-3, Impl-4, Impl-5]  -- 5 parallel
  Sub-wave (N+1).2: [Impl-6, Impl-7, Impl-8]                   -- 3 parallel
```

Setting `max_parallel = 1` produces fully sequential execution: one task at a time, alternating test and implementation.

---

## Error Handling

### tdd-tools Not Installed

If the `tdd-executor` agent or `test-writer` agent cannot be resolved (tdd-tools plugin not installed):

1. **Detection**: The orchestrator checks for the `tdd-tools` plugin availability before starting execution
2. **Error message**:
   ```
   ERROR: tdd-tools plugin is required for TDD task execution.

   The following agents are needed but not available:
   - tdd-executor (from tdd-tools) — executes TDD task pairs
   - test-writer (from tdd-tools) — generates tests in parallel

   Install tdd-tools:
   1. Add tdd-tools to your .mcp.json plugin configuration
   2. Restart Claude Code to load the plugin
   3. Re-run /execute-tdd-tasks

   Alternatively, use /execute-tasks to run tasks without TDD enforcement.
   ```
3. **Behavior**: Abort execution before launching any agents. Do not fall back to standard execution — the user explicitly requested TDD execution

### Agent Spawn Failures

When a `tdd-executor` agent fails to spawn or crashes during execution:

| Failure Type | Behavior |
|-------------|----------|
| Agent spawn timeout | Retry with the same prompt (counts as a retry attempt) |
| Agent crashes mid-execution | Capture any partial output, retry with failure context |
| Agent returns malformed report | Log the raw output, treat as FAIL, retry with explicit format instructions |
| All retries exhausted | Leave task as `in_progress`, log final failure, continue with other tasks |

### Test-Writer Agent Failure (RED Phase)

When a test-writer or tdd-executor agent fails during the RED phase:

1. **First retry**: Re-launch the `tdd-executor` agent with the failure context
2. **Second retry**: Re-launch with additional diagnostic instructions (check test framework config, validate import paths, verify test directory exists)
3. **Fallback strategy**: If all retries fail, mark the test task as FAIL and skip the paired implementation task (it remains blocked). Log both tasks in the session summary
4. **No silent degradation**: Do not fall back to running the implementation task without tests — this defeats TDD

### Pre-Existing Test Failures

When the test baseline (from Phase 1 of the TDD workflow) reveals pre-existing test failures:

1. **Snapshot failures**: The tdd-executor records all pre-existing failures during its UNDERSTAND phase
2. **Isolate new results**: RED and GREEN verification compare only against the baseline — pre-existing failures are excluded from pass/fail determination
3. **Do not fix pre-existing failures**: They are outside the scope of the current task
4. **Report in context**: Include pre-existing failure count in the per-task context file so subsequent tasks are aware
5. **Track regressions**: If a previously-passing test starts failing after implementation, that IS a regression and blocks GREEN verification

---

## Execution Loop Integration

### Complete TDD Execution Loop

The TDD execution loop follows the same 10-step orchestration as `execute-tasks`, with TDD-specific behavior in Steps 3, 5, 7, and 8:

| Step | Standard Behavior | TDD Extension |
|------|------------------|---------------|
| 1. Load Tasks | `TaskList` | Same — filter by `--task-group` if provided |
| 2. Validate State | Check edge cases | Also check: tdd-tools installed, TDD pairs have valid cross-references |
| 3. Build Plan | Topological sort into waves | Annotate waves with RED/GREEN phase labels |
| 4. Check Settings | Read local settings | Also read `tdd.strictness` setting |
| 5. Present Plan | Display and confirm | Show TDD pair count, strictness level, phase annotations |
| 5.5. Init Session | Create session directory | Add TDD compliance section to execution context |
| 6. Init Context | Merge prior learnings | Same |
| 7. Execute Loop | Launch agents per wave | Route to tdd-executor or task-executor based on metadata |
| 7d. Process Results | Log results | Also update TDD compliance summary |
| 7f. Merge Context | Merge per-task files | Include test task output for GREEN phase prompt injection |
| 8. Session Summary | Display results | Include TDD compliance summary (RED/GREEN/REFACTOR per pair) |
| 9. Update CLAUDE.md | Review for changes | Same |
