# SDD Tools: End-to-End Workflow

The sdd-tools pipeline takes you from idea to working implementation in three steps:

```
/sdd-tools:create-spec  →  /sdd-tools:create-tasks  →  /sdd-tools:execute-tasks
     (Spec)                    (Task List)                  (Implementation)
```

Each step produces artifacts that feed into the next, and you can re-enter the pipeline at any point.

## Step 1: Create a Spec (`/sdd-tools:create-spec`)

The spec creation skill launches an adaptive interview that builds a structured specification from your answers.

**Initial Gathering** — You provide four pieces of context:
1. **Spec name** — identifies the output file
2. **Product type** — "new product" or "new feature" (new feature enables codebase exploration)
3. **Depth level** — controls interview length and spec detail
4. **Description** — free-form context that shapes the interview

**Adaptive Interview** — The interview agent walks through four categories, adjusting question count and depth based on your chosen level:

| Category | Covers |
|----------|--------|
| Problem & Goals | Problem statement, success metrics, user personas, business value |
| Functional Requirements | Must-have features, user stories, acceptance criteria, edge cases |
| Technical Specifications | Architecture, tech stack, data models, APIs, performance, security |
| Implementation Planning | Phases, milestones, dependencies, risks, out-of-scope items |

High-level interviews focus on the first two categories with broad questions. Detailed and full-tech interviews go deeper into all four, adding follow-up questions on metrics baselines, secondary personas, data models, and deployment plans.

**Proactive Recommendations** — As you answer, the agent detects patterns (e.g., mentioning "login", "millions of users", "GDPR") and offers best-practice recommendations inline. For compliance topics (HIPAA, GDPR, PCI, WCAG), it can automatically research current requirements without you asking.

**Pre-Compilation Summary** — Before generating the spec, the agent presents a summary of everything gathered for your review. You can add, correct, or remove information at this stage.

**Output** — The final spec is written to `specs/SPEC-{name}.md` (configurable via settings). The template used depends on your depth level — high-level, detailed, or full-tech.

## Step 2: Generate Tasks (`/sdd-tools:create-tasks`)

The task generation skill decomposes a spec into Claude Code native Tasks with metadata, dependencies, and acceptance criteria.

```
/sdd-tools:create-tasks specs/SPEC-User-Authentication.md
```

**Task Metadata** — Each generated task includes:

| Field | Description |
|-------|-------------|
| `priority` | P0 (critical) through P3 (low) |
| `complexity` | XS, S, M, L, XL — estimates implementation scope |
| `prd_path` | Link back to the source spec |
| `source_section` | Which spec section this task implements |
| `feature_name` | Logical feature grouping |

Tasks also include acceptance criteria extracted from the spec (functional requirements, edge cases, error handling, performance targets) and testing requirements.

**Dependency Inference** — Dependencies are automatically inferred from layer relationships. The general order follows: data layer → service layer → API/interface layer → UI layer → tests. Tasks that set up foundational code block tasks that consume it.

**Preview & Confirmation** — Before creating tasks, the agent presents a preview summary showing the task breakdown, dependency graph, and metadata. You confirm before any tasks are written.

**Merge Mode** — Re-running `create-tasks` on the same spec merges intelligently with existing tasks:
- **Completed tasks** are never modified
- **Pending/in-progress tasks** merge with the new generation
- A summary reports how many existing tasks were found and their statuses

**Storage** — Tasks are written to `~/.claude/tasks/` as JSON files, the standard Claude Code task format.

## Step 3: Execute Tasks (`/sdd-tools:execute-tasks`)

The execution skill runs each task autonomously in its own subagent, following a structured 4-phase workflow.

```
/sdd-tools:execute-tasks           # execute all pending tasks
/sdd-tools:execute-tasks 5         # execute a specific task
/sdd-tools:execute-tasks --retries 1  # limit retries per task
```

**Orchestration** — The orchestrator loads the task list, builds an execution plan sorted by priority (critical → high → medium → low), and breaks ties by choosing tasks that unblock the most others. After each task completes, the dependency graph is refreshed and newly unblocked tasks are dynamically added to the plan.

**4-Phase Execution** — Each task runs through:

| Phase | What Happens |
|-------|-------------|
| **Understand** | Reads execution context and CLAUDE.md, loads task details, classifies the task, explores affected files, summarizes scope |
| **Implement** | Reads all target files before modifying, follows data → service → interface → test order, matches existing patterns, runs mid-implementation checks |
| **Verify** | Spec-generated tasks: walks each acceptance criterion by category. General tasks: infers checklist from description. Runs tests and linter |
| **Complete** | Determines PASS/PARTIAL/FAIL, updates task status, appends learnings to execution context |

**Execution Context** — Tasks share learnings through `.claude/execution-context.md`. This file accumulates:
- **Project Patterns** — coding patterns, conventions, tech stack details
- **Key Decisions** — architecture choices and approach rationale
- **Known Issues** — problems encountered and workarounds
- **File Map** — important files and their purposes
- **Task History** — brief log of outcomes

Each task reads this file before starting and writes to it after finishing, regardless of outcome. The file persists across sessions, so you can resume execution where you left off.

**Adaptive Verification** — Verification adjusts based on task type:

| Task Type | Verification Method | Pass Threshold |
|-----------|-------------------|----------------|
| Spec-generated (has acceptance criteria) | Criterion-by-criterion evaluation across Functional, Edge Cases, Error Handling, Performance | All Functional criteria + tests pass |
| General (no acceptance criteria) | Inferred checklist from task description | Core change implemented + tests pass |

PARTIAL status means non-functional criteria failed but functional criteria passed. FAIL means functional criteria or tests failed.

**Retry Mechanism** — Failed tasks retry up to 3 times by default (configurable with `--retries`). Each retry includes the previous attempt's failure details so the agent can try a different approach. After retries are exhausted, the task remains `in_progress` and execution continues to the next task.

**Session Summary** — After all tasks are processed, you get a summary showing pass/fail counts, failed task details with failure reasons, and any tasks that were newly unblocked during the session.

## Monitoring with Task Manager

The [task-manager app](../../claude-apps/task-manager/) provides a real-time Kanban board that visualizes task execution as it happens.

```bash
# In one terminal — start the dashboard
pnpm dev:task-manager    # opens on http://localhost:3030

# In another terminal — run task execution
/sdd-tools:execute-tasks
```

The board watches `~/.claude/tasks/` for file changes using Chokidar and pushes updates via Server-Sent Events. As `execute-tasks` moves tasks through pending → in_progress → completed, the Kanban board updates in near real-time:

- **Three columns** — Pending, In Progress, Completed
- **Active badge** — shows which task is currently executing
- **Dependency tracking** — blocked tasks display their blockers
- **Completion stats** — progress counts update as tasks finish
- **Search & filter** — find specific tasks across all columns
