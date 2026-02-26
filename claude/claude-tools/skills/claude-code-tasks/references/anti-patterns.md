# Task Anti-Patterns

Common mistakes when using Claude Code Tasks and their correct alternatives. Each anti-pattern includes what it looks like, why it causes problems, and how to do it right.

---

## AP-01: Circular Dependencies

**Description**: Creating tasks where A is blocked by B, and B is blocked by A (directly or through a chain), causing a deadlock where no task in the cycle can ever start.

```
TaskCreate: subject="Create API routes"       -> Task 5
TaskCreate: subject="Create request handlers"  -> Task 6

TaskUpdate: taskId=5, addBlockedBy=[6]   # 5 waits on 6
TaskUpdate: taskId=6, addBlockedBy=[5]   # 6 waits on 5 -- DEADLOCK
```

Longer chains are harder to spot:

```
Task 5 blockedBy [6]
Task 6 blockedBy [7]
Task 7 blockedBy [5]   # Cycle: 5 -> 6 -> 7 -> 5
```

**Why It's Problematic**: Tasks caught in a cycle will remain `pending` forever. No task in the cycle can transition to `in_progress` because each one is waiting for another task in the same cycle to complete first. Automated orchestrators like `execute-tasks` will detect this as a deadlock and either break the cycle heuristically or halt execution entirely.

**Correct Alternative**: Before adding a dependency, trace the chain to confirm it does not loop back. If two tasks genuinely share information, extract the shared artifact into a third task that both depend on.

```
# Break the mutual dependency with a shared foundation task
TaskCreate: subject="Define shared request/response types"  -> Task 4
TaskCreate: subject="Create API routes"                     -> Task 5
TaskCreate: subject="Create request handlers"               -> Task 6

TaskUpdate: taskId=5, addBlockedBy=[4]   # Routes depend on shared types
TaskUpdate: taskId=6, addBlockedBy=[4]   # Handlers depend on shared types
# Tasks 5 and 6 are now independent peers, both unblocked once Task 4 completes
```

To detect cycles in an existing task list, walk the `blockedBy` chain from each task. If you revisit a task you have already seen, a cycle exists. Break it at the weakest link — the dependency with the least coupling.

---

## AP-02: Too-Granular Tasks

**Description**: Creating a separate task for every minor code change — individual import statements, single type annotations, one-line config edits — instead of grouping related changes into coherent units of work.

```
# Anti-pattern: 5 tasks for what should be 1
TaskCreate: subject="Add import for UserSchema"
TaskCreate: subject="Add type annotation to create_user"
TaskCreate: subject="Add return type to get_user"
TaskCreate: subject="Add UserSchema to __init__.py exports"
TaskCreate: subject="Update type-checking config"
```

**Why It's Problematic**: Each task carries overhead — agent initialization, context loading, file reading, verification, and result reporting. Five trivial tasks consume roughly 5x the resources of one well-scoped task. Overly granular tasks also create unnecessary dependency chains (the import must exist before the type annotation can use it) that serialize work that could be done in a single pass. The task list becomes noisy and harder to track.

**Correct Alternative**: Scope tasks to 1-3 files of cohesive work. A good task represents a logical unit that can be implemented, tested, and verified independently.

```
# One task covering the cohesive unit of work
TaskCreate:
  subject: "Add type annotations to user module"
  description: |
    Add type hints to all public functions in the user module:
    - Import UserSchema and related types
    - Annotate create_user, get_user, update_user, delete_user
    - Export types from __init__.py
    - Update type-checking config if needed
  activeForm: "Adding type annotations to user module"
  metadata:
    task_group: "user-module"
```

**Right-sizing heuristic**: If a task can be described in a single imperative sentence and touches 1-3 files, it is likely the right size. If it requires a bullet list of 10+ changes across 8 files, consider splitting it into 2-3 focused tasks.

---

## AP-03: Missing activeForm

**Description**: Creating tasks without the `activeForm` field, leaving the UI without spinner text while the task is in progress.

```
# Anti-pattern: no activeForm
TaskCreate:
  subject: "Implement rate limiting middleware"
  description: "Add rate limiting to all API endpoints..."
  # activeForm is missing
```

When this task transitions to `in_progress`, the task list UI falls back to displaying the `subject` as static text instead of showing an active progress indicator with descriptive text.

**Why It's Problematic**: The `activeForm` field provides real-time feedback in the task list UI. Without it, users and orchestrators see a generic status instead of a description of what is actively happening. In multi-task executions with many concurrent tasks, missing activeForm text makes it difficult to distinguish which tasks are actively progressing and what each one is doing.

**Correct Alternative**: Always provide `activeForm` as the present-continuous form of the imperative `subject`.

```
TaskCreate:
  subject: "Implement rate limiting middleware"
  description: "Add rate limiting to all API endpoints..."
  activeForm: "Implementing rate limiting middleware"
```

The pattern is mechanical — convert the imperative verb to its `-ing` form:

| subject | activeForm |
|---------|------------|
| "Create user schema" | "Creating user schema" |
| "Fix login timeout bug" | "Fixing login timeout bug" |
| "Add JWT authentication" | "Adding JWT authentication" |
| "Refactor payment module" | "Refactoring payment module" |

---

## AP-04: Batch Status Updates

**Description**: Marking multiple tasks as `in_progress` simultaneously, either by looping through a list or by updating several tasks before starting work on any of them.

```
# Anti-pattern: claiming all tasks at once
TaskUpdate: taskId=5, status="in_progress"
TaskUpdate: taskId=6, status="in_progress"
TaskUpdate: taskId=7, status="in_progress"
# Now work on... which one?
```

**Why It's Problematic**: The `in_progress` status signals that a task is actively being worked on. If a single agent marks three tasks as `in_progress` but can only work on one at a time, the other two are falsely reporting active progress. This confuses orchestrators that use status to track which tasks are occupied, misleads the task UI, and makes it impossible to tell which task is actually being worked on. If the agent crashes, all three tasks are left in a dirty `in_progress` state that requires manual cleanup.

**Correct Alternative**: Follow the sequential claim-work-complete pattern. Only mark a task `in_progress` when you are about to start working on it. Complete it (or reset it) before claiming the next one.

```
# Correct: sequential claim-work-complete
TaskUpdate: taskId=5, status="in_progress"
# ... do the work for task 5 ...
TaskUpdate: taskId=5, status="completed"

TaskUpdate: taskId=6, status="in_progress"
# ... do the work for task 6 ...
TaskUpdate: taskId=6, status="completed"

TaskUpdate: taskId=7, status="in_progress"
# ... do the work for task 7 ...
TaskUpdate: taskId=7, status="completed"
```

The exception is multi-agent orchestration (e.g., `execute-tasks` launching parallel agents), where each agent claims exactly one task. Even in that case, each individual agent only marks one task `in_progress` at a time.

---

## AP-05: Duplicate Task Creation

**Description**: Running TaskCreate without first checking whether an equivalent task already exists, resulting in duplicate tasks that cause double work or conflicting changes.

```
# First run of task creation
TaskCreate: subject="Create user schema", metadata: { task_uid: "user:create-schema" }
# -> Task 5 created

# Second run (e.g., re-running create-tasks after a spec update)
TaskCreate: subject="Create user schema", metadata: { task_uid: "user:create-schema" }
# -> Task 12 created -- DUPLICATE of Task 5
```

**Why It's Problematic**: Duplicate tasks waste execution resources — two agents may work on the same change simultaneously, producing merge conflicts or overwriting each other's work. If the duplicates have slightly different descriptions (e.g., from a spec update), agents may implement conflicting versions of the same feature. Completed status on one duplicate does not affect the other, so orchestrators may re-execute already-finished work.

**Correct Alternative**: Before creating tasks, call TaskList to check for existing tasks. Use the `task_uid` metadata key as a composite identifier for idempotent task creation. If a task with a matching `task_uid` already exists, update it instead of creating a new one.

```
# Step 1: Check for existing tasks
TaskList
# -> Returns all tasks; scan metadata.task_uid for "user:create-schema"

# Step 2a: If no match found, create the task
TaskCreate:
  subject: "Create user schema"
  metadata:
    task_uid: "user:create-schema"
    task_group: "user-module"

# Step 2b: If match found (e.g., Task 5 exists with this task_uid), update it
TaskUpdate:
  taskId: 5
  description: "Updated description from latest spec revision..."
  metadata:
    task_uid: "user:create-schema"
    task_group: "user-module"
    priority: "high"
```

Skills like `create-tasks` use this merge mode automatically — matching `task_uid` values trigger updates to existing tasks while preserving their completion status.

---

## AP-06: TaskList-Only Consumption

**Description**: Using TaskList alone to understand task requirements before starting work. TaskList returns summary objects that include `subject`, `status`, `metadata`, and dependency fields — but not the full `description`.

```
# Anti-pattern: reading only the summary
TaskList
# -> Returns: [{ id: 5, subject: "Create user schema", status: "pending", ... }]

# Agent starts working based only on the subject line "Create user schema"
# Misses: acceptance criteria, implementation notes, testing requirements,
#         and the full description with context
```

**Why It's Problematic**: The `subject` field is a short imperative title (5-10 words). The `description` field contains the full specification: acceptance criteria, implementation instructions, edge cases, testing requirements, and context from the source spec. Working from the subject alone leads to incomplete implementations that miss key requirements, fail verification, and require retries — wasting tokens and time.

**Correct Alternative**: Use the two-step pattern: TaskList for overview, then TaskGet for full details before starting work on any task.

```
# Step 1: Get the overview of all tasks
TaskList
# -> Returns summary objects with id, subject, status, blockedBy, metadata

# Step 2: Before starting work on a specific task, get its full details
TaskGet: taskId=5
# -> Returns the complete task object including the full description
#    with acceptance criteria, testing requirements, context, etc.

# Step 3: Now work on the task with full context
TaskUpdate: taskId=5, status="in_progress"
# ... implement based on the full description from TaskGet ...
```

This pattern is especially important in orchestration skills where the orchestrator uses TaskList to plan waves and determine ordering, but each executor agent must call TaskGet to get the complete task specification before implementing.

---

## AP-07: Missing task_group Metadata

**Description**: Creating tasks without the `task_group` metadata key, making them invisible to group-filtered execution and harder to organize in multi-feature projects.

```
# Anti-pattern: no task_group
TaskCreate:
  subject: "Create user schema"
  metadata:
    priority: "high"
    complexity: "medium"
    # task_group is missing
```

**Why It's Problematic**: The `task_group` key enables filtered execution via `execute-tasks --task-group`. Without it, tasks cannot be selectively executed as a group. In projects with multiple features in flight, ungrouped tasks are either executed with every run (wasting resources on unrelated work) or must be manually identified and filtered. The `task_group` also drives the `task_execution_id` naming convention (`{task_group}-{timestamp}`), providing meaningful session names instead of generic `exec-session-{timestamp}` labels.

**Correct Alternative**: Always include `task_group` in metadata when creating tasks that belong to a feature or work stream.

```
TaskCreate:
  subject: "Create user schema"
  metadata:
    priority: "high"
    complexity: "medium"
    task_group: "user-auth"

TaskCreate:
  subject: "Add login endpoint"
  metadata:
    priority: "high"
    complexity: "medium"
    task_group: "user-auth"
```

With `task_group` set, these tasks can be executed together:

```
/execute-tasks --task-group user-auth
```

This runs only tasks where `metadata.task_group` equals `user-auth`, leaving other tasks untouched. The execution session is named `user-auth-20260223-143000` instead of `exec-session-20260223-143000`, making session archives easier to identify.
