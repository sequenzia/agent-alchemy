# Task Management Tools — Detailed API Breakdown

## Overview

Claude Code provides 6 Task Management tools for tracking work, organizing multi-step operations, managing dependencies, and coordinating agent workflows.

---

## 1. TaskCreate

**Purpose:** Create a new task to track work in the current session.

### When to Use
- Complex multi-step tasks (3+ distinct steps)
- Plan mode — to track planned work
- User provides multiple tasks or explicitly requests a todo list
- Non-trivial tasks that benefit from organized tracking

### When NOT to Use
- Single, straightforward tasks
- Trivial work completable in < 3 steps
- Purely conversational or informational requests

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `subject` | `string` | Yes | Brief, actionable title in imperative form (e.g., "Fix authentication bug in login flow") |
| `description` | `string` | Yes | Detailed description including context and acceptance criteria |
| `activeForm` | `string` | No | Present continuous form shown in spinner when `in_progress` (e.g., "Fixing authentication bug"). Falls back to `subject` if omitted |
| `metadata` | `object` | No | Arbitrary key-value metadata to attach to the task |

### Behavior
- All tasks are created with status `pending`
- No owner is assigned at creation — use `TaskUpdate` to assign
- Use `TaskUpdate` after creation to set up dependencies (`blocks`/`blockedBy`)

---

## 2. TaskGet

**Purpose:** Retrieve full details of a single task by its ID.

### When to Use
- Need full description/context before starting work
- Understanding task dependencies (what it blocks, what blocks it)
- After being assigned a task, to get complete requirements

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `taskId` | `string` | Yes | The ID of the task to retrieve |

### Returns
- `subject` — Task title
- `description` — Detailed requirements and context
- `status` — `pending`, `in_progress`, or `completed`
- `blocks` — Tasks waiting on this one to complete
- `blockedBy` — Tasks that must complete before this one can start

### Tips
- Verify `blockedBy` list is empty before beginning work
- Use `TaskList` first to see all tasks in summary form

---

## 3. TaskList

**Purpose:** List all tasks with summary information.

### When to Use
- See available tasks (status `pending`, no owner, not blocked)
- Check overall project progress
- Find blocked tasks needing dependency resolution
- Before assigning tasks to teammates
- After completing a task, to find the next one

### Parameters

None — takes no parameters.

### Returns (per task)
- `id` — Task identifier (use with `TaskGet`, `TaskUpdate`)
- `subject` — Brief description
- `status` — `pending`, `in_progress`, or `completed`
- `owner` — Agent ID if assigned, empty if available
- `blockedBy` — List of open task IDs that must be resolved first

### Teammate Workflow
1. Call `TaskList` to find available work
2. Look for tasks: `pending` status, no owner, empty `blockedBy`
3. Prefer tasks in ID order (lowest first) — earlier tasks set up context for later ones
4. Claim via `TaskUpdate` (set `owner`)

---

## 4. TaskUpdate

**Purpose:** Update any aspect of an existing task — status, details, ownership, or dependencies.

### When to Use
- **Mark completed:** When work is fully done
- **Mark in progress:** When starting work on a task
- **Delete tasks:** When no longer relevant or created in error
- **Update details:** When requirements change
- **Set dependencies:** Establish task ordering
- **Assign ownership:** Claim or delegate tasks

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `taskId` | `string` | Yes | The ID of the task to update |
| `status` | `string` | No | New status: `pending`, `in_progress`, `completed`, or `deleted` |
| `subject` | `string` | No | New task title (imperative form) |
| `description` | `string` | No | New task description |
| `activeForm` | `string` | No | Present continuous form for spinner (e.g., "Running tests") |
| `owner` | `string` | No | New task owner (agent name) |
| `metadata` | `object` | No | Metadata keys to merge (set a key to `null` to delete it) |
| `addBlocks` | `string[]` | No | Task IDs that cannot start until this one completes |
| `addBlockedBy` | `string[]` | No | Task IDs that must complete before this one can start |

### Status Workflow
```
pending → in_progress → completed
                ↘ deleted (from any state)
```

### Rules
- Only mark `completed` when **fully** accomplished
- If errors/blockers encountered, keep as `in_progress`
- Never mark completed if: tests failing, partial implementation, unresolved errors, missing dependencies
- Always read latest state via `TaskGet` before updating (staleness check)

### Examples
```json
// Start work
{"taskId": "1", "status": "in_progress"}

// Complete work
{"taskId": "1", "status": "completed"}

// Delete task
{"taskId": "1", "status": "deleted"}

// Claim task
{"taskId": "1", "owner": "my-name"}

// Set dependency: task 2 blocked by task 1
{"taskId": "2", "addBlockedBy": ["1"]}
```

---

## 5. TaskOutput

**Purpose:** Retrieve output from a running or completed background task (shell, agent, or remote session).

### When to Use
- Check on background task progress
- Retrieve results from completed background work
- Monitor long-running operations

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `task_id` | `string` | Yes | — | The task ID to get output from |
| `block` | `boolean` | Yes | `true` | Whether to wait for task completion |
| `timeout` | `number` | Yes | `30000` | Max wait time in ms (range: 0–600000) |

### Behavior
- `block: true` — Waits for the task to finish (up to `timeout` ms), then returns output
- `block: false` — Non-blocking check; returns current status and any available output immediately
- Works with all task types: background shells, async agents, and remote sessions

---

## 6. TaskStop

**Purpose:** Stop/terminate a running background task.

### When to Use
- Terminate a long-running task that's no longer needed
- Cancel a background process

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | `string` | No | The ID of the background task to stop |
| `shell_id` | `string` | No | **Deprecated** — use `task_id` instead |

### Returns
- Success or failure status of the stop operation

---

## Task Lifecycle Summary

```
┌──────────┐    TaskUpdate     ┌─────────────┐    TaskUpdate     ┌───────────┐
│ pending  │ ──────────────→  │ in_progress │ ──────────────→  │ completed │
└──────────┘   status:         └─────────────┘   status:         └───────────┘
  TaskCreate   in_progress                       completed
                                    │
                                    │ TaskUpdate status: deleted
                                    ▼
                              ┌───────────┐
                              │  deleted   │
                              └───────────┘
```

### Dependency System
- `addBlocks`: "This task blocks these other tasks"
- `addBlockedBy`: "This task is blocked by these other tasks"
- A task with non-empty `blockedBy` (pointing to open tasks) cannot be started
- When a blocking task completes, downstream tasks become unblocked

### Two Distinct Contexts

| Context | Tools Used | Purpose |
|---------|-----------|---------|
| **Structured tracking** | `TaskCreate`, `TaskGet`, `TaskList`, `TaskUpdate` | Organize work items, track progress, manage dependencies, coordinate agents |
| **Background execution** | `TaskOutput`, `TaskStop` | Monitor and control background processes (shells, agents, remote sessions) |

Both share the task ID namespace but serve different operational needs.
