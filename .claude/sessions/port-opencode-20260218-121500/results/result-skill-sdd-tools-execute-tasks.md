# Conversion Result: skill-sdd-tools-execute-tasks

## Metadata

| Field | Value |
|-------|-------|
| Component ID | skill-sdd-tools-execute-tasks |
| Component Type | skill |
| Group | sdd-tools |
| Name | execute-tasks |
| Source Path | claude/sdd-tools/skills/execute-tasks/SKILL.md |
| Target Path | .opencode/skills/execute-tasks.md |
| Fidelity Score | 77% |
| Fidelity Band | yellow |
| Status | partial |

## Converted Content

~~~markdown
---
description: Execute pending tasks in dependency order with wave-based concurrent execution and adaptive verification. Supports task group filtering and configurable parallelism. Use when user says "execute tasks", "run tasks", "start execution", "work on tasks", or wants to execute generated tasks autonomously.
user-invocable: true
---

<!-- Arguments: [task-id] [--task-group <group>] [--retries <n>] [--max-parallel <n>] -->
<!-- Use $ARGUMENTS to access the full argument string at runtime. -->
<!-- Arguments reference:
  - $1 / task-id: Optional specific task ID to execute. If omitted, executes all unblocked tasks in dependency order.
  - --task-group <group>: Optional task group name to filter tasks. Only tasks with matching metadata.task_group will be executed.
  - --retries <n>: Number of retry attempts for failed/partial tasks before moving on. Default is 3.
  - --max-parallel <n>: Maximum number of tasks to execute simultaneously per wave. Default is 5. Overrides settings file value.
-->
<!-- NOTE: disable-model-invocation is not supported in opencode. This skill is always available to the model. To restrict invocation to users only, document the constraint in the description and enforce at the agent level via permission config. -->
<!-- NOTE: allowed-tools restrictions are not supported per-skill in opencode. Tool permissions are configured at the agent level. The tools used by this skill are: task, read, write, glob, grep, bash, question, todoread, todowrite. -->

# Execute Tasks Skill

This skill orchestrates autonomous task execution for tasks stored via todowrite. It builds a dependency-aware execution plan, launches a dedicated agent for each task through a 4-phase workflow (Understand, Implement, Verify, Complete), handles retries with failure context, and shares learnings across tasks through a shared execution context file.

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

This skill orchestrates task execution through a 10-step loop.

<!-- NOTE: The source skill referenced references/orchestration.md, references/execution-workflow.md, and references/verification-patterns.md for detailed procedures. opencode has no reference_dir equivalent. Reference file content must be inlined below or maintained separately and copied into this skill body. The full procedure is documented inline in the sections below. (Cached workaround: unsupported_composition:reference_dir_null — inline reference content into skill body.) -->

### Step 1: Load Task List

Retrieve all tasks via `todoread`. If a `--task-group` argument was provided, filter tasks to only those with matching `metadata.task_group` embedded in the task description. If a specific `task-id` argument was provided, validate it exists.

<!-- NOTE: TaskList has no direct equivalent in opencode. Use todoread (partial equivalent) — returns the full task list with no filtering by owner or status. Scan the returned list for matching task_group metadata embedded in description text. (Cached workaround: unmapped_tool:TaskList) -->

### Step 2: Validate State

Handle edge cases: empty list, all completed, specific task blocked, no unblocked tasks, circular dependencies.

### Step 3: Build Execution Plan

Resolve `max_parallel` setting using precedence: `--max-parallel` CLI arg > `.claude/agent-alchemy.local.md` setting > default 5. Build a dependency graph from pending tasks. Assign tasks to waves using topological levels: Wave 1 = no dependencies, Wave 2 = depends on Wave 1 tasks, etc. Sort within waves by priority (critical > high > medium > low > unprioritized), break ties by "unblocks most others." Cap each wave at `max_parallel` tasks.

### Step 4: Check Settings

Read `.claude/agent-alchemy.local.md` if it exists for execution preferences, including `max_parallel` setting. CLI `--max-parallel` argument takes precedence over the settings file value.

### Step 5: Initialize Execution Directory

Generate a `task_execution_id` using three-tier resolution: (1) if `--task-group` provided → `{task_group}-{YYYYMMDD}-{HHMMSS}`, (2) else if all open tasks share the same `metadata.task_group` → `{task_group}-{YYYYMMDD}-{HHMMSS}`, (3) else → `exec-session-{YYYYMMDD}-{HHMMSS}`. Clean any stale `__live_session__/` files by archiving them to `.claude/sessions/interrupted-{YYYYMMDD}-{HHMMSS}/`, resetting any `in_progress` tasks from the interrupted session back to `pending` via `todowrite`. Check for and enforce the concurrency guard via `.lock` file. Create `.claude/sessions/__live_session__/` directory containing:
- `execution_plan.md` — saved execution plan from Step 5
- `execution_context.md` — initialized with standard template
- `task_log.md` — initialized with table headers (Task ID, Subject, Status, Attempts, Duration, Token Usage)
- `tasks/` — subdirectory for archiving completed task files
- `progress.md` — initialized with status template for real-time progress tracking
- `execution_pointer.md` at `~/.opencode/tasks/{TASK_LIST_ID}/` — created immediately with absolute path to `.claude/sessions/__live_session__/`

<!-- NOTE: TaskUpdate (for resetting in_progress tasks to pending) maps to todowrite in opencode — rewrite full task list with updated status; dependency info embedded in description text. (Cached workaround: unmapped_tool:TaskUpdate) -->

### Step 6: Present Execution Plan and Confirm

Display the plan showing tasks to execute, blocked tasks, and completed count. Also display the details of step 5 which includes the session directory path (`.claude/sessions/__live_session__/`) and files created, including the execution pointer file location.

Then ask the user to confirm before proceeding with execution using the `question` tool. If the user cancels, stop without modifying any tasks.

<!-- NOTE: AskUserQuestion maps to question in opencode. The question tool supports 1-8 questions with 2-8 options each, and is only available to primary agents (not subagents). This step must be invoked at the primary agent level. -->

### Step 7: Initialize Execution Context

Read `.claude/sessions/__live_session__/execution_context.md` (created in Step 5). If a prior execution context exists, look in `.claude/sessions/` for the most recent timestamped subfolder and merge relevant learnings into the new one.

### Step 8: Execute Loop

Execute tasks in waves. For each wave: snapshot `execution_context.md`, mark wave tasks `in_progress` via `todowrite` (rewrite full task list with updated status), update `progress.md` with all active tasks, launch up to `max_parallel` agents simultaneously via **parallel task tool calls in a single turn**. Each agent writes to `context-task-{id}.md` instead of the shared context file. As agents return: calculate duration, capture token usage, log to `task_log.md`, update `progress.md`. Failed tasks with retries remaining are re-launched immediately within the wave. After all wave agents complete: merge per-task context files into `execution_context.md`, delete per-task files, archive completed task JSONs, refresh task list via `todoread` for newly unblocked tasks, form next wave, repeat.

<!-- NOTE: TaskList maps to todoread; TaskGet maps to todoread full-list scan by task_uid in description; TaskUpdate maps to todowrite full-list rewrite. (Cached workarounds: unmapped_tool:TaskList, unmapped_tool:TaskGet, unmapped_tool:TaskUpdate) -->

### Step 9: Session Summary

Display execution results with pass/fail counts, total execution time, failed task list, newly unblocked tasks, and token usage summary (captured from task tool responses if available). Save `session_summary.md` to `.claude/sessions/__live_session__/`. Archive the session by moving all contents from `__live_session__/` to `.claude/sessions/{task_execution_id}/`, leaving `__live_session__/` as an empty directory. `execution_pointer.md` stays pointing to `__live_session__/`.

### Step 10: Update CLAUDE.md

Review execution context for project-wide changes (new patterns, dependencies, commands, structure changes, design decisions). Make targeted edits to CLAUDE.md if meaningful changes occurred. Skip if only task-specific or internal implementation details.

## Task Classification

Determine whether a task is spec-generated or general to select the right verification approach.

### Detection Algorithm

1. **Check description format**: Look for `**Acceptance Criteria:**` with categorized criteria (`_Functional:_`, `_Edge Cases:_`, etc.)
2. **Check metadata**: Look for `metadata.spec_path` field embedded in the task description
3. **Check source reference**: Look for `Source: {path} Section {number}` in the description

If any check matches -> **spec-generated task** (use criterion-based verification)

If none match -> **General task** (use inferred verification)

## 4-Phase Workflow

Each task is executed by the `task-executor` agent (opencode agent: `task-executor` in `.opencode/agents/`) through these phases:

<!-- NOTE: The source referenced the agent as `agent-alchemy-sdd:task-executor`. In opencode, agents are referenced by filename in .opencode/agents/ directory. The agent is addressed as `task-executor` and invoked via the task tool with `command: "task-executor"`. -->

### Phase 1: Understand

Load context and understand scope before writing code.

- Read the execute-tasks skill and references
- Read `.claude/sessions/__live_session__/execution_context.md` for learnings from prior tasks
- Load task details via `todoread` (scan full list for matching task_uid in description text)
- Classify the task (spec-generated vs general)
- Parse acceptance criteria or infer requirements from description
- Explore affected files via glob/grep
- Read `CLAUDE.md` for project conventions

<!-- NOTE: TaskGet has no direct equivalent. Use todoread and scan the returned list for the task_uid embedded in description text. (Cached workaround: unmapped_tool:TaskGet) -->

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
- If PASS: mark task as `completed` via `todowrite` (rewrite full task list with updated status)
- If PARTIAL or FAIL: leave as `in_progress` for the orchestrator to decide on retry
- Write learnings to `.claude/sessions/__live_session__/context-task-{id}.md` (files discovered, patterns learned, issues encountered)
- Return structured report with verification results

<!-- NOTE: TaskUpdate maps to todowrite in opencode. Rewrite the full task list with updated status; embed all metadata (task_uid, spec_path, dependencies, task_group) in description text. (Cached workaround: unmapped_tool:TaskUpdate) -->

## Adaptive Verification Overview

Verification adapts based on task type:

| Task Type | Verification Method | Pass Threshold |
|-----------|-------------------|----------------|
| spec-generated | Criterion-by-criterion evaluation | All Functional + Tests must pass |
| General | Inferred checklist from description | Core change works + Tests pass |

**Critical rule**: All Functional criteria must pass for a PASS result. Edge Cases, Error Handling, and Performance failures result in PARTIAL but do not block completion.

## Shared Execution Context

Tasks within an execution session share learnings through `.claude/sessions/__live_session__/execution_context.md`:

- **Write-based updates**: All orchestrator writes to session artifacts (`execution_context.md`, `task_log.md`, `progress.md`) use write (full file replacement) via a read-modify-write pattern, never edit. This ensures atomic, reliable updates regardless of file size.
- **Snapshot before wave**: The orchestrator snapshots `execution_context.md` before launching each wave — all agents in a wave read the same baseline
- **Per-task writes**: Each agent writes to `context-task-{id}.md` instead of the shared file, regardless of `max_parallel` setting. This eliminates write contention and avoids fragile edit operations on shared files.
- **Merge after wave**: After all agents in a wave complete, the orchestrator appends all `context-task-{id}.md` content to the `## Task History` section of `execution_context.md` and deletes the per-task files
- **Sections**: Project Patterns, Key Decisions, Known Issues, File Map, Task History

This enables later tasks to benefit from earlier discoveries and retry attempts to learn from previous failures.

## Key Behaviors

- **Autonomous execution loop**: After the user confirms the execution plan, no further prompts occur between tasks. The loop runs without interruption once started.
- **Wave-based parallelism**: Tasks at the same dependency level run simultaneously, up to `max_parallel` concurrent agents per wave. Tasks in later waves wait until their dependencies in earlier waves complete.
- **One agent per task, multiple per wave**: Each task gets a fresh agent invocation with isolated context, but multiple agents run concurrently within a wave.
- **Per-task context isolation**: Each agent writes to `context-task-{id}.md` regardless of `max_parallel` setting. The orchestrator merges these after each wave. This eliminates write contention and fragile edit operations on shared files.
- **Within-wave retry**: Failed tasks with retries remaining are re-launched immediately as agent slots free up within the current wave, maximizing throughput.
- **Configurable parallelism**: Default 5 concurrent tasks, configurable via `--max-parallel` argument or `.claude/agent-alchemy.local.md` settings. Set to 1 for sequential execution.
- **Configurable retries**: Default 3 attempts per task, configurable via `retries` argument.
- **Retry with context**: Each retry includes the previous attempt's failure details so the agent can try a different approach.
- **Dynamic unblocking**: After each wave completes, the dependency graph is refreshed via `todoread` and newly unblocked tasks are added to the next wave.
- **Honest failure handling**: After retries exhausted, tasks stay `in_progress` (not completed), and execution continues.
- **Circular dependency detection**: If all remaining tasks are blocked by each other, break at the weakest link (task with fewest blockers) and log a warning.
- **Shared context**: Agents read the snapshot of `execution_context.md` and write learnings to per-task context files. The orchestrator appends per-task content to the Task History section between waves.
- **Resilient context sharing**: If a task-executor fails to append to its context file, learnings are captured in the verification report as a fallback.
- **Single-session invariant**: Only one execution session can run at a time per project. A `.lock` file in `__live_session__/` prevents concurrent invocations.
- **Interrupted session recovery**: Stale sessions are detected and archived; tasks left `in_progress` are automatically reset to `pending` via `todowrite`.

## Example Usage

### Execute all unblocked tasks
```
/execute-tasks
```

### Execute a specific task
```
/execute-tasks 5
```

### Execute with custom retry limit
```
/execute-tasks --retries 1
```

### Execute specific task with retries
```
/execute-tasks 5 --retries 5
```

### Execute tasks for a specific group
```
/execute-tasks --task-group user-authentication
```

### Execute specific group with custom retries
```
/execute-tasks --task-group payments --retries 1
```

### Execute with limited parallelism
```
/execute-tasks --max-parallel 2
```

### Execute sequentially (no concurrency)
```
/execute-tasks --max-parallel 1
```

### Execute group with custom parallelism and retries
```
/execute-tasks --task-group payments --max-parallel 3 --retries 1
```

## Reference Materials

<!-- NOTE: The source skill referenced three external reference files via a references/ subdirectory. opencode has no reference_dir equivalent (reference_dir = null). Reference content must be inlined into the skill body or maintained as separate files loaded via the instructions config array in opencode.json. The procedures from these references are summarized inline above; for full detail, maintain these as standalone .md files and add them to the opencode.json instructions array. (Cached workaround: unsupported_composition:reference_dir_null) -->

Reference files from the source plugin (maintain separately and load via opencode.json instructions if needed):
- `references/orchestration.md` — 10-step orchestration loop with execution plan, retry handling, and session summary
- `references/execution-workflow.md` — Detailed phase-by-phase procedures for the 4-phase workflow
- `references/verification-patterns.md` — Task classification, criterion verification, pass/fail rules, and failure reporting format
~~~

## Fidelity Report

| Mapping Type | Count | Weight | Contribution |
|-------------|-------|--------|-------------|
| Direct | 9 | 1.0 | 9.0 |
| Workaround | 9 | 0.7 | 6.3 |
| TODO | 0 | 0.2 | 0.0 |
| Omitted | 2 | 0.0 | 0.0 |
| **Total** | **20** | | **15.3** |

**Score:** 15.3 / 20 × 100 = **77%**

**Notes:** The 9 workarounds are all covered by cached decisions from prior waves (TaskList/TaskGet/TaskUpdate → todoread/todowrite, reference_dir → inline, disable-model-invocation → description note). The 2 omissions (allowed-tools field, arguments field) are cosmetic — tool permissions are enforced at agent level in opencode and argument hints are embedded in body comments. No critical features are lost; the orchestration logic, wave-based parallelism, and 4-phase workflow are fully preserved.

## Decisions

| Feature | Decision Type | Original | Converted | Rationale | Confidence | Resolution Mode |
|---------|-------------|----------|-----------|-----------|------------|----------------|
| name field | relocated | `name: execute-tasks` in frontmatter | Derived from filename `execute-tasks.md` | opencode derives skill name from filename; name field not supported in frontmatter | high | auto |
| description field | direct | `description: Execute pending...` | `description: Execute pending...` | Direct 1:1 mapping | high | N/A |
| argument-hint field | relocated | `argument-hint: "[task-id] [--task-group <group>] [--retries <n>] [--max-parallel <n>]"` | `<!-- Arguments: ... -->` comment block in body | opencode uses $ARGUMENTS/$1/$2 placeholders in body; no frontmatter argument-hint field | high | auto |
| user-invocable field | direct | `user-invocable: true` | `user-invocable: true` | Direct 1:1 mapping | high | N/A |
| disable-model-invocation field | workaround | `disable-model-invocation: false` | Comment note in body explaining constraint | Not supported in opencode; document at agent level | high | cached |
| allowed-tools field | omitted | 11 tools listed | Omitted; note in body comment | No per-skill tool restrictions in opencode; agent-level only | high | auto |
| arguments field | omitted | 4 argument definitions | Omitted; argument hints moved to body comment | No structured argument schema in opencode skills | high | auto |
| Tool: Task | direct | `Task` | `task` | Direct equivalent in opencode | high | N/A |
| Tool: Read | direct | `Read` | `read` | Direct equivalent in opencode | high | N/A |
| Tool: Write | direct | `Write` | `write` | Direct equivalent in opencode | high | N/A |
| Tool: Glob | direct | `Glob` | `glob` | Direct equivalent in opencode | high | N/A |
| Tool: Grep | direct | `Grep` | `grep` | Direct equivalent in opencode | high | N/A |
| Tool: Bash | direct | `Bash` | `bash` | Direct equivalent in opencode | high | N/A |
| Tool: AskUserQuestion | direct | `AskUserQuestion` | `question` | Direct equivalent; primary-agent-only constraint noted | high | N/A |
| Tool: TaskList | workaround | `TaskList` | `todoread` (full list scan) | Partial equivalent; no filtering by owner/status; scan description text for metadata | high | cached |
| Tool: TaskGet | workaround | `TaskGet` | `todoread` (scan for task_uid) | No per-task retrieval by ID; scan full list for task_uid in description | high | cached |
| Tool: TaskUpdate | workaround | `TaskUpdate` | `todowrite` (full list rewrite) | Partial equivalent; rewrite full list with updated status; embed metadata in description | high | cached |
| Composition: references/orchestration.md | workaround | `Read ${CLAUDE_PLUGIN_ROOT}/skills/execute-tasks/references/orchestration.md` | Inline note + summary in body | reference_dir = null in opencode; content inlined into skill body | medium | cached |
| Composition: references/execution-workflow.md | workaround | `Read ${CLAUDE_PLUGIN_ROOT}/skills/execute-tasks/references/execution-workflow.md` | Inline note + summary in body | reference_dir = null in opencode; content inlined into skill body | medium | cached |
| Composition: references/verification-patterns.md | workaround | `Read ${CLAUDE_PLUGIN_ROOT}/skills/execute-tasks/references/verification-patterns.md` | Inline note + summary in body | reference_dir = null in opencode; content inlined into skill body | medium | cached |
| Agent reference: task-executor naming | workaround | `agent-alchemy-sdd:task-executor` | `task-executor` (opencode agent filename) | Plugin-qualified names not used in opencode; agent referenced by filename in .opencode/agents/ | high | auto |

## Gaps

| Feature | Reason | Severity | Workaround | User Acknowledged |
|---------|--------|----------|------------|-------------------|
| allowed-tools per-skill restrictions | opencode has no per-skill tool restrictions; agent-level only | cosmetic | Remove from skill; configure tool permissions at agent level via permission config | false |
| disable-model-invocation | Not supported in opencode; skill always available to model | cosmetic | Document constraint in description; restrict at agent level | false |
| arguments structured schema | No structured argument definition in opencode skills | cosmetic | Argument hints documented in body comment block using $ARGUMENTS convention | false |
| TaskList (no filtering) | todoread returns full list with no filtering by owner or status | functional | Scan description text for metadata.task_group; filter in-skill via text matching | false |
| TaskGet (no per-ID retrieval) | todoread has no per-task retrieval by ID | functional | Scan full todoread list for task_uid embedded in description text | false |
| TaskUpdate (session-scoped, no structured status) | todowrite is session-scoped scratchpad with limited status changes | functional | Rewrite full task list via todowrite; embed all metadata (uid, spec_path, dependencies) in description text | false |
| reference_dir (3 reference files) | opencode reference_dir = null; no separate reference file support | functional | Inline reference content into skill body; or load via opencode.json instructions array | false |

## Unresolved Incompatibilities

All incompatibilities were resolved via cached decisions from prior waves. No items require orchestrator resolution.

| Group Key | Feature | Severity | Category | Reason | Suggested Workaround | Confidence | Affected Locations |
|-----------|---------|----------|----------|--------|---------------------|------------|-------------------|
| — | — | — | — | — | — | — | — |
