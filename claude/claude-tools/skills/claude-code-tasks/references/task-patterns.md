# Task Design Patterns

Proven patterns for structuring Claude Code Tasks in multi-agent and single-agent workflows. This reference covers dependency graph design, task sizing, coordination strategies, and metadata conventions.

---

## Dependency Graph Design Patterns

Tasks form a Directed Acyclic Graph (DAG) via `blockedBy` and `blocks` relationships. These four foundational patterns combine to model any workflow.

### Linear Chain

A sequential pipeline where each task depends on the previous one. Task B cannot start until A completes, C cannot start until B completes.

```
A --> B --> C
```

**When to use:**
- Steps that must happen in strict order (schema first, then service layer, then API endpoints)
- Each task consumes the output of the previous task
- The work cannot be parallelized because each step transforms the prior step's artifact

**Example: Build a REST endpoint**

```
TaskCreate:
  subject: "Create user database schema"
  activeForm: "Creating user database schema"
  metadata:
    priority: "high"
    task_group: "user-api"
    task_uid: "user-api:schema"

TaskCreate:
  subject: "Implement user service layer"
  activeForm: "Implementing user service layer"
  metadata:
    priority: "high"
    task_group: "user-api"
    task_uid: "user-api:service"

TaskCreate:
  subject: "Add user API endpoints"
  activeForm: "Adding user API endpoints"
  metadata:
    priority: "high"
    task_group: "user-api"
    task_uid: "user-api:endpoints"

# Set dependencies after creation
TaskUpdate:
  taskId: 2
  addBlockedBy: [1]

TaskUpdate:
  taskId: 3
  addBlockedBy: [2]
```

**Trade-offs:** Maximum correctness guarantees but zero parallelism. Use only when each step truly depends on the previous one. If steps B and C can run independently from A's output, prefer fan-out instead.

---

### Fan-Out

One task unblocks multiple independent tasks that can run in parallel. Task A produces a shared artifact (schema, config, interface) that B, C, and D all consume independently.

```
      +--> B
      |
A --> +--> C
      |
      +--> D
```

**When to use:**
- A foundational task (shared schema, interface definition, config setup) enables multiple parallel implementation tasks
- The parallel tasks do not depend on each other
- You want to maximize throughput by running independent work concurrently

**Example: Implement features after shared setup**

```
TaskCreate:
  subject: "Define shared TypeScript interfaces"
  activeForm: "Defining shared TypeScript interfaces"
  metadata:
    priority: "critical"
    task_group: "payments"
    task_uid: "payments:interfaces"

TaskCreate:
  subject: "Implement payment processing service"
  activeForm: "Implementing payment processing service"
  metadata:
    priority: "high"
    task_group: "payments"
    task_uid: "payments:processing"

TaskCreate:
  subject: "Implement refund service"
  activeForm: "Implementing refund service"
  metadata:
    priority: "high"
    task_group: "payments"
    task_uid: "payments:refunds"

TaskCreate:
  subject: "Implement payment history query"
  activeForm: "Implementing payment history query"
  metadata:
    priority: "medium"
    task_group: "payments"
    task_uid: "payments:history"

# All three implementation tasks depend on the interfaces task
TaskUpdate:
  taskId: 2
  addBlockedBy: [1]

TaskUpdate:
  taskId: 3
  addBlockedBy: [1]

TaskUpdate:
  taskId: 4
  addBlockedBy: [1]
```

**Trade-offs:** Excellent parallelism but the fan-out root (task A) becomes a bottleneck. If A fails or takes long, all downstream tasks are blocked. Keep A focused and small.

---

### Fan-In

Multiple independent tasks must all complete before a single downstream task can start. Tasks A, B, and C produce separate artifacts that D needs to combine, validate, or integrate.

```
A --+
    |
B --+--> D
    |
C --+
```

**When to use:**
- A merge, integration, or validation step needs outputs from multiple prior tasks
- Writing end-to-end tests that exercise multiple independently-built components
- Generating a summary or report that aggregates results from parallel work

**Example: Integration testing after parallel implementation**

```
TaskCreate:
  subject: "Implement auth module"
  activeForm: "Implementing auth module"
  metadata:
    priority: "high"
    task_group: "platform"
    task_uid: "platform:auth"

TaskCreate:
  subject: "Implement user module"
  activeForm: "Implementing user module"
  metadata:
    priority: "high"
    task_group: "platform"
    task_uid: "platform:user"

TaskCreate:
  subject: "Implement notification module"
  activeForm: "Implementing notification module"
  metadata:
    priority: "high"
    task_group: "platform"
    task_uid: "platform:notifications"

TaskCreate:
  subject: "Write platform integration tests"
  activeForm: "Writing platform integration tests"
  metadata:
    priority: "high"
    task_group: "platform"
    task_uid: "platform:integration-tests"

# Integration tests depend on all three modules
TaskUpdate:
  taskId: 4
  addBlockedBy: [1, 2, 3]
```

**Trade-offs:** The fan-in task (D) must wait for the slowest upstream task. If one of A, B, or C takes much longer than the others, agents assigned to the faster tasks sit idle. Aim for roughly equal effort across the fan-out tasks.

---

### Diamond

A combination of fan-out and fan-in. One task fans out to multiple parallel tasks, which then fan back in to a single downstream task. This is the most common pattern in real-world workflows.

```
      +--> B --+
      |        |
A --> +        +--> D
      |        |
      +--> C --+
```

**When to use:**
- A setup task enables parallel work, and a final task integrates or validates the results
- Feature development where a schema task enables parallel service and UI work, followed by an integration task
- Any workflow that naturally has a "setup, parallel work, combine" structure

**Example: Full feature with parallel tracks**

```
TaskCreate:
  subject: "Create order data model and migrations"
  activeForm: "Creating order data model and migrations"
  metadata:
    priority: "critical"
    task_group: "orders"
    task_uid: "orders:data-model"

TaskCreate:
  subject: "Implement order service and business logic"
  activeForm: "Implementing order service and business logic"
  metadata:
    priority: "high"
    task_group: "orders"
    task_uid: "orders:service"

TaskCreate:
  subject: "Build order API endpoints"
  activeForm: "Building order API endpoints"
  metadata:
    priority: "high"
    task_group: "orders"
    task_uid: "orders:api"

TaskCreate:
  subject: "Add order validation and error handling tests"
  activeForm: "Adding order validation and error handling tests"
  metadata:
    priority: "high"
    task_group: "orders"
    task_uid: "orders:tests"

# Service and API both depend on data model
TaskUpdate:
  taskId: 2
  addBlockedBy: [1]

TaskUpdate:
  taskId: 3
  addBlockedBy: [1]

# Tests depend on both service and API
TaskUpdate:
  taskId: 4
  addBlockedBy: [2, 3]
```

**Trade-offs:** Balances parallelism with correctness. The diamond shape is natural for most features but adds one more wave of execution compared to a pure fan-out. Ensure the fan-in task (D) genuinely needs all upstream tasks — if it only needs B, do not add C as a dependency.

---

### Combining Patterns

Real workflows combine these patterns. A complex feature might use:

```
A --> [B, C] --> D --> [E, F, G] --> H
```

This is a diamond (A -> B,C -> D) followed by a fan-out from D to E,F,G, followed by a fan-in to H.

**Execution waves for the above graph:**
- Wave 1: A (no dependencies)
- Wave 2: B, C (both depend on A, run in parallel)
- Wave 3: D (depends on B and C)
- Wave 4: E, F, G (all depend on D, run in parallel)
- Wave 5: H (depends on E, F, and G)

---

## Task Right-Sizing Guidance

### Optimal Granularity

**Target: 1-3 files per task.** This balances meaningful progress per task with manageable scope for a single agent.

| Task Size | Files | Typical Duration | Assessment |
|-----------|-------|------------------|------------|
| Too small | <1 file (partial) | <5 minutes | Merge with a related task |
| Optimal | 1-3 files | 10-30 minutes | Good size for one agent |
| Acceptable | 4-5 files | 30-60 minutes | Acceptable if files are tightly coupled |
| Too large | >5 files | >60 minutes | Split into smaller tasks |

### When to Split a Task

Split a task into multiple tasks when:

- **File count exceeds 5**: The task touches too many files for reliable single-agent execution. Split by layer (data, service, API) or by module.
- **Estimated effort exceeds 2 hours**: Large tasks increase the risk of agent confusion, context overflow, and partial failures. Break into phases.
- **Crosses system boundaries**: A task that spans both frontend and backend, or both the database layer and the API layer, should be split at the boundary. Each side becomes its own task with a dependency relationship.
- **Multiple independent features**: If a task implements two unrelated features, split them so they can be prioritized and tracked independently.
- **Complex testing requirements**: If the task requires both the implementation and extensive test writing, consider separating the implementation task from the test-writing task (with the test task depending on the implementation task).

### When to Merge Tasks

Merge tasks into a single task when:

- **Trivially small**: Each task is under 10 lines of changes. The overhead of separate task management exceeds the benefit.
- **Always done together**: Two tasks that are never executed independently (e.g., "create type definition" and "export type from index file") should be one task.
- **Same file, same section**: Two tasks that modify the same small file in the same area should be merged to avoid merge conflicts.
- **Configuration pairs**: A config change and its corresponding code change (e.g., "add env var" and "read env var in config module") are better as one task.

### Right-Sizing Examples

**Too granular (merge these):**
```
Task: "Create UserType interface"           # ~5 lines
Task: "Export UserType from types/index.ts"  # ~1 line
Task: "Add UserType import to service.ts"    # ~1 line
```
Better: One task "Define and integrate UserType interface"

**Too broad (split this):**
```
Task: "Implement complete user authentication system"
# Touches: schema, migrations, service, controller, middleware, routes, tests, config
```
Better: Split into "Create auth schema", "Implement auth service", "Add auth middleware", "Create auth endpoints", "Write auth tests"

---

## Multi-Agent Coordination Patterns

These patterns describe how multiple agents coordinate work through the task system.

### Self-Claim Workflow

Agents autonomously find and claim available tasks without a central dispatcher assigning work.

**How it works:**
1. Agent calls `TaskList` to see all tasks
2. Agent filters for tasks where `status == "pending"` and all `blockedBy` tasks are `completed`
3. Agent selects the highest-priority unblocked task
4. Agent claims the task by setting `status: "in_progress"` and `owner` to its identifier
5. Agent executes the task
6. Agent marks the task `completed` (or leaves it `in_progress` on failure)
7. Agent repeats from step 1

**Example: Agent claiming a task**

```
# Step 1: List all tasks
TaskList
# Returns tasks with status, blockedBy, metadata

# Step 2: Find unblocked pending tasks
# Filter: status == "pending" AND all blockedBy tasks have status == "completed"
# Sort by: priority (critical > high > medium > low > unprioritized)

# Step 3: Claim the task
TaskUpdate:
  taskId: 7
  status: "in_progress"
  owner: "agent-worker-1"

# Step 4: Execute the task
# ... (implementation work) ...

# Step 5: Mark complete
TaskUpdate:
  taskId: 7
  status: "completed"
```

**When to use:**
- Decentralized execution where agents work independently
- Heterogeneous agents that can handle different task types
- Single-agent sequential execution (agent picks up one task at a time)

### Orchestrator-Dispatched Workflow

A central orchestrator assigns tasks to agents. This is the pattern used by `execute-tasks` in sdd-tools.

**How it works:**
1. Orchestrator calls `TaskList` and builds a dependency graph
2. Orchestrator groups tasks into waves by topological level
3. For each wave, orchestrator launches agents and assigns specific tasks
4. Agents execute their assigned tasks and report results
5. Orchestrator collects results, updates shared context, and forms the next wave

**When to use:**
- Controlled parallel execution with configurable concurrency
- Wave-based workflows where all tasks in a wave share the same context snapshot
- Retry handling where the orchestrator can re-dispatch failed tasks

### Task-Per-Teammate Ratio

**Target: 2-3 tasks per agent per wave.** This balances agent utilization with responsiveness.

| Ratio | Assessment | Risk |
|-------|------------|------|
| 1 task per agent | Underutilized agents; high overhead per task | Agents sit idle between waves |
| 2-3 tasks per agent | Optimal utilization; agents stay productive | Balanced |
| 4+ tasks per agent | Risk of context overflow; long execution time per agent | Agent may lose track or hit context limits |

In practice, the ratio depends on task complexity:
- **Trivial tasks** (config changes, small edits): 3-4 per agent is fine
- **Medium tasks** (1-3 file implementations): 2-3 per agent is optimal
- **Complex tasks** (multi-file features, integration work): 1 per agent is safest

### Wave-Based Execution

Tasks grouped by their dependency level form waves. All tasks in a wave have their dependencies satisfied and can run in parallel.

**How waves are formed:**
- **Wave 1**: Tasks with no dependencies (no `blockedBy`, or all blockers already completed)
- **Wave 2**: Tasks whose blockers are all in Wave 1
- **Wave N**: Tasks whose blockers are all in waves 1 through N-1

**Example wave assignment:**

```
Given tasks:
  Task 1: "Create schema"           blockedBy: []
  Task 2: "Create types"            blockedBy: []
  Task 3: "Implement service"       blockedBy: [1, 2]
  Task 4: "Implement controller"    blockedBy: [1, 2]
  Task 5: "Write integration tests" blockedBy: [3, 4]

Wave assignment:
  Wave 1: [Task 1, Task 2]         # No dependencies, run in parallel
  Wave 2: [Task 3, Task 4]         # Both depend on Wave 1 tasks
  Wave 3: [Task 5]                 # Depends on Wave 2 tasks
```

Each wave runs up to `max_parallel` agents concurrently. After all agents in a wave finish, the orchestrator merges learnings, refreshes the task list, and forms the next wave.

---

## Metadata Strategies

Metadata key-value pairs on tasks enable filtering, tracking, deduplication, and producer-consumer relationships.

### Categorization Metadata

Use these keys to group and filter tasks.

| Key | Purpose | Example Values |
|-----|---------|----------------|
| `task_group` | Group tasks for filtered execution (`--task-group payments`) | `"user-auth"`, `"payments"`, `"onboarding"` |
| `feature_name` | Associate tasks with a feature for tracking | `"user-authentication"`, `"order-management"` |
| `source_section` | Link to the spec section that defined this task | `"Section 5.1"`, `"Section 3.2 (US-004)"` |

**Example: Categorized task**
```
TaskCreate:
  subject: "Add password hashing to auth service"
  metadata:
    task_group: "user-auth"
    feature_name: "user-authentication"
    source_section: "Section 5.1 (US-001)"
```

### Tracking Metadata

Use these keys for prioritization, effort estimation, and deduplication.

| Key | Purpose | Example Values |
|-----|---------|----------------|
| `priority` | Execution order within a wave | `"critical"`, `"high"`, `"medium"`, `"low"`, `"unprioritized"` |
| `complexity` | Effort estimate for planning | `"trivial"`, `"low"`, `"medium"`, `"high"` |
| `task_uid` | Composite key for idempotent merge mode | `"auth:create-schema"`, `"payments:refund-service"` |

**task_uid for deduplication:** When re-running task generation, the `task_uid` acts as a composite key. If a task with the same `task_uid` already exists, it is updated instead of duplicated. Format convention: `{group}:{action}` or `{feature}:{component}`.

**Example: Trackable task with UID**
```
TaskCreate:
  subject: "Create payment refund service"
  metadata:
    priority: "high"
    complexity: "medium"
    task_uid: "payments:refund-service"
    task_group: "payments"
```

### Phase Tracking Metadata

Use these keys for incremental spec-to-task generation across implementation phases.

| Key | Purpose | Example Values |
|-----|---------|----------------|
| `spec_phase` | Which spec phase generated this task | `"phase-1"`, `"phase-2"` |
| `spec_phase_name` | Human-readable phase name | `"Plugin Foundation"`, `"Integration Layer"` |
| `spec_path` | Path to the source specification | `"internal/specs/auth-SPEC.md"` |

**Example: Phase-tracked task**
```
TaskCreate:
  subject: "Create auth database schema"
  metadata:
    spec_phase: "phase-1"
    spec_phase_name: "Authentication Foundation"
    spec_path: "internal/specs/auth-SPEC.md"
    task_uid: "auth:schema"
    task_group: "user-auth"
```

### Producer-Consumer Metadata

Use the `produces_for` key to document which downstream tasks consume this task's output. This is informational — it does not replace `blockedBy`/`blocks` dependencies but helps agents understand the data flow.

| Key | Purpose | Example Values |
|-----|---------|----------------|
| `produces_for` | Downstream task UIDs that consume this task's output | `"auth:service,auth:middleware"` |

**Example: Producer task**
```
TaskCreate:
  subject: "Define auth TypeScript interfaces"
  metadata:
    task_uid: "auth:interfaces"
    produces_for: "auth:service,auth:middleware,auth:controller"
    task_group: "user-auth"
```

### Combining Metadata Strategies

A well-annotated task uses metadata from multiple categories:

```
TaskCreate:
  subject: "Implement JWT token refresh endpoint"
  description: "Add POST /auth/refresh endpoint that validates refresh tokens and issues new access tokens."
  activeForm: "Implementing JWT token refresh endpoint"
  metadata:
    priority: "high"
    complexity: "medium"
    task_group: "user-auth"
    feature_name: "user-authentication"
    task_uid: "auth:token-refresh"
    spec_path: "internal/specs/auth-SPEC.md"
    spec_phase: "phase-1"
    spec_phase_name: "Authentication Foundation"
    source_section: "Section 5.1 (US-003)"
    produces_for: "auth:integration-tests"
```

This task is:
- **Prioritized**: `high` priority, executed early in its wave
- **Estimated**: `medium` complexity, appropriate for one agent
- **Grouped**: Part of `user-auth` for filtered execution
- **Traceable**: Linked to spec section 5.1, phase 1
- **Deduplicated**: `task_uid` prevents duplicate creation on re-run
- **Connected**: Documents that integration tests consume its output
