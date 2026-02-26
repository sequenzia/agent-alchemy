# Orchestration Patterns

Proven multi-agent workflow patterns for Claude Code Agent Teams. Each pattern defines a team structure, task design, and communication flow for a specific class of problems. Use the [Pattern Selection Guide](#pattern-selection-guide) at the end to choose the right pattern for your use case.

> **Cross-reference**: For SendMessage field tables and delivery mechanics, see `messaging-protocol.md`. For task creation and dependency management, see the `cc-tasks` reference skill.

---

## 1. Parallel Specialists

Multiple agents work independently on different parts of the same problem. Each specialist handles a distinct aspect, and a lead or synthesizer merges results at the end.

### When to Use

- Work is **embarrassingly parallel** — each piece can be done without knowledge of others
- The problem can be decomposed into non-overlapping focus areas
- Speed matters: N agents finish N pieces in roughly the time one agent does one
- Examples: codebase exploration across modules, independent file generation, parallel search across directories, multi-language analysis

### Team Structure

| Role | Count | Model Tier | Responsibility |
|------|-------|-----------|----------------|
| Lead | 1 | Opus | Decomposes problem, spawns specialists, merges results |
| Specialist | 2-8 | Sonnet | Independently explores/generates one focus area |
| Synthesizer | 0-1 | Opus | (Optional) Dedicated agent for merging specialist outputs |

### Task Design

- Lead decomposes the problem into N non-overlapping focus areas
- Each specialist gets one focus area with clear boundaries
- All specialist tasks are independent (no inter-specialist dependencies)
- Specialists write results to files or send messages back to lead
- Lead (or synthesizer) reads all results and produces a merged output

### Communication Flow

```
Lead --> Specialist-1 (spawn with focus area A)
Lead --> Specialist-2 (spawn with focus area B)
Lead --> Specialist-3 (spawn with focus area C)
     ... specialists work independently ...
Specialist-1 --> Lead (results via SendMessage or file)
Specialist-2 --> Lead (results via SendMessage or file)
Specialist-3 --> Lead (results via SendMessage or file)
Lead: merge all results into final output
Lead --> Specialist-1 (shutdown_request)
Lead --> Specialist-2 (shutdown_request)
Lead --> Specialist-3 (shutdown_request)
```

### Practical Example

```
# Phase 1: Create the team
TeamCreate(team_name="analysis-team", description="Parallel codebase analysis across 3 modules")

# Phase 2: Spawn specialists in background
Task(
  description="Explore the authentication module (src/auth/). Analyze all files, document public APIs, identify patterns and issues. Write findings to .claude/sessions/analysis/auth-findings.md",
  team_name="analysis-team",
  name="auth-analyst",
  subagent_type="fast",
  run_in_background=true
)

Task(
  description="Explore the database module (src/db/). Analyze all files, document schemas, identify patterns and issues. Write findings to .claude/sessions/analysis/db-findings.md",
  team_name="analysis-team",
  name="db-analyst",
  subagent_type="fast",
  run_in_background=true
)

Task(
  description="Explore the API module (src/api/). Analyze all files, document endpoints, identify patterns and issues. Write findings to .claude/sessions/analysis/api-findings.md",
  team_name="analysis-team",
  name="api-analyst",
  subagent_type="fast",
  run_in_background=true
)

# Phase 3: Wait for specialists, then merge
# Lead monitors for idle notifications and reads result files
# When all specialists have reported back:

SendMessage(
  type="shutdown_request",
  recipient="auth-analyst",
  content="Analysis complete. Please shut down.",
  request_id="shutdown-auth"
)
# Repeat for each specialist

# Phase 4: Synthesize
# Lead reads all findings files and produces merged analysis
# OR spawn a dedicated synthesizer:
Task(
  description="Read analysis findings from .claude/sessions/analysis/*.md. Synthesize into a unified report covering cross-cutting concerns, contradictions, and recommendations. Write to .claude/sessions/analysis/synthesis.md",
  team_name="analysis-team",
  name="synthesizer",
  subagent_type="default"
)

# Phase 5: Cleanup
TeamDelete(team_name="analysis-team")
```

### Scaling Notes

- **2-3 specialists**: Lead can synthesize results directly without a dedicated synthesizer
- **4-8 specialists**: Consider a dedicated Opus synthesizer to handle the volume of findings
- **8+ specialists**: Batch results into groups and run multiple synthesis passes

---

## 2. Pipeline with Dependencies

Tasks flow through sequential stages where each stage's output feeds the next. Agents specialize in one stage and hand off results through the pipeline.

### When to Use

- Work has a **natural sequential flow** — each stage transforms the prior stage's output
- Different stages require different expertise or tool access
- Quality gates between stages are important
- Examples: research then design then implement then review, ETL pipelines, document processing (draft then edit then format)

### Team Structure

| Role | Count | Model Tier | Responsibility |
|------|-------|-----------|----------------|
| Lead / Orchestrator | 1 | Opus | Manages pipeline flow, triggers each stage, handles failures |
| Stage Agent | 1 per stage | Varies | Executes one pipeline stage and produces output for the next |

Model tier per stage depends on the stage's complexity:

| Stage Type | Recommended Tier | Rationale |
|-----------|-----------------|-----------|
| Research / Search | Sonnet | Broad exploration, parallelizable |
| Design / Architecture | Opus | Complex reasoning, trade-off analysis |
| Implementation | Sonnet or Opus | Depends on complexity |
| Review / Validation | Opus | Critical judgment, quality assessment |

### Task Design

- Create tasks with explicit dependencies using `blockedBy` to enforce ordering
- Each task reads the output of its predecessor (via file or task description)
- Tasks are created upfront but execute sequentially due to dependency chain
- Lead monitors progress and triggers the next stage when the current one completes

### Communication Flow

```
Lead: Create all pipeline tasks with dependency chain
Lead --> Stage-1 Agent (spawn: research)
Stage-1 Agent: writes research-output.md
Stage-1 Agent --> Lead (SendMessage: "Research complete")
Lead --> Stage-2 Agent (spawn: design, reads research-output.md)
Stage-2 Agent: writes design-output.md
Stage-2 Agent --> Lead (SendMessage: "Design complete")
Lead --> Stage-3 Agent (spawn: implement, reads design-output.md)
... continues through all stages ...
```

### Practical Example

```
# Phase 1: Create the team
TeamCreate(team_name="feature-pipeline", description="Sequential feature development pipeline")

# Phase 2: Create the task dependency chain
TaskCreate(
  subject="Research authentication patterns",
  description="Research OAuth2 and JWT patterns for our tech stack. Document findings in .claude/pipeline/research.md",
  status="pending"
)
# Returns task_id: "task-1"

TaskCreate(
  subject="Design authentication architecture",
  description="Read .claude/pipeline/research.md. Design the auth architecture. Write design to .claude/pipeline/design.md",
  status="pending",
  blockedBy=["task-1"]
)
# Returns task_id: "task-2"

TaskCreate(
  subject="Implement authentication",
  description="Read .claude/pipeline/design.md. Implement the auth module following the design. Create files in src/auth/.",
  status="pending",
  blockedBy=["task-2"]
)
# Returns task_id: "task-3"

TaskCreate(
  subject="Review authentication implementation",
  description="Review the auth implementation in src/auth/ against the design in .claude/pipeline/design.md. Write review to .claude/pipeline/review.md",
  status="pending",
  blockedBy=["task-3"]
)
# Returns task_id: "task-4"

# Phase 3: Execute pipeline stages sequentially
# Stage 1: Research (Sonnet for broad exploration)
TaskUpdate(taskId="task-1", status="in_progress")
Task(
  description="Execute task-1: Research authentication patterns. Write findings to .claude/pipeline/research.md",
  team_name="feature-pipeline",
  name="researcher",
  subagent_type="fast"
)
# Wait for completion, then update task status
TaskUpdate(taskId="task-1", status="completed")

# Stage 2: Design (Opus for architecture decisions)
TaskUpdate(taskId="task-2", status="in_progress")
Task(
  description="Execute task-2: Design authentication architecture based on .claude/pipeline/research.md. Write to .claude/pipeline/design.md",
  team_name="feature-pipeline",
  name="architect",
  subagent_type="default"
)
TaskUpdate(taskId="task-2", status="completed")

# Stage 3: Implement (Sonnet for straightforward coding)
TaskUpdate(taskId="task-3", status="in_progress")
Task(
  description="Execute task-3: Implement authentication following .claude/pipeline/design.md",
  team_name="feature-pipeline",
  name="implementer",
  subagent_type="fast"
)
TaskUpdate(taskId="task-3", status="completed")

# Stage 4: Review (Opus for quality judgment)
TaskUpdate(taskId="task-4", status="in_progress")
Task(
  description="Execute task-4: Review auth implementation against design",
  team_name="feature-pipeline",
  name="reviewer",
  subagent_type="default"
)
TaskUpdate(taskId="task-4", status="completed")

# Phase 4: Cleanup
TeamDelete(team_name="feature-pipeline")
```

### Scaling Notes

- **2-3 stages**: Simple pipeline; lead can manage directly
- **4-6 stages**: Consider intermediate checkpoints where lead validates output before passing to next stage
- **Parallel branches**: If two stages are independent (e.g., frontend and backend implementation), spawn them as parallel specialists within the pipeline

---

## 3. Swarm / Self-Organizing Pool

Multiple identical agents claim and execute tasks from a shared pool. An orchestrator manages the task list and dispatches work, while workers process tasks independently and report results.

### When to Use

- Large **backlog of well-defined, independent tasks** that need processing
- Tasks are uniform enough that any worker can handle any task
- Throughput matters more than specialization
- Examples: executing a generated task list, bulk file migrations, running tests across modules, processing a queue of code reviews

### Team Structure

| Role | Count | Model Tier | Responsibility |
|------|-------|-----------|----------------|
| Orchestrator / Lead | 1 | Opus | Manages task pool, dispatches work, tracks progress, handles retries |
| Worker | 2-10 | Sonnet or Opus | Claims and executes tasks from the pool, reports results |

Workers are typically the same model tier, but can be mixed if some tasks require more reasoning (Opus) while others are straightforward (Sonnet).

### Task Design

- All tasks are created upfront in the shared task list (using `TaskCreate`)
- Tasks use dependency management (`blockedBy`) to form waves — tasks at the same dependency level can run in parallel
- Orchestrator assigns tasks to workers in waves: Wave 1 = no dependencies, Wave 2 = depends on Wave 1 tasks, etc.
- Workers execute one task at a time, report results, then receive the next assignment
- Failed tasks can be retried by the same or a different worker

### Communication Flow

```
Orchestrator: Create all tasks in the task list
Orchestrator: Group tasks into waves by dependency level

Wave 1:
  Orchestrator --> Worker-1 (SendMessage: "Execute task-1")
  Orchestrator --> Worker-2 (SendMessage: "Execute task-2")
  Orchestrator --> Worker-3 (SendMessage: "Execute task-3")
  Worker-1 --> Orchestrator (SendMessage: "task-1 complete")
  Worker-2 --> Orchestrator (SendMessage: "task-2 complete")
  Worker-3 --> Orchestrator (SendMessage: "task-3 failed")
  Orchestrator: retry task-3 with Worker-3

Wave 2 (tasks unblocked by Wave 1 completions):
  Orchestrator --> Worker-1 (SendMessage: "Execute task-4")
  Orchestrator --> Worker-2 (SendMessage: "Execute task-5")
  ... continues until all tasks done ...

Orchestrator --> all workers (shutdown_request)
```

### Practical Example

```
# Phase 1: Create the team
TeamCreate(team_name="execution-pool", description="Swarm execution of task backlog")

# Phase 2: Create tasks (or they already exist from a prior planning step)
TaskCreate(subject="Implement user model", description="Create src/models/user.ts ...", status="pending")
TaskCreate(subject="Implement auth service", description="Create src/services/auth.ts ...", status="pending", blockedBy=["task-1"])
TaskCreate(subject="Implement user service", description="Create src/services/user.ts ...", status="pending", blockedBy=["task-1"])
TaskCreate(subject="Implement auth routes", description="Create src/routes/auth.ts ...", status="pending", blockedBy=["task-2"])
TaskCreate(subject="Write user model tests", description="Test src/models/user.ts ...", status="pending", blockedBy=["task-1"])

# Phase 3: Spawn worker pool
Task(
  description="You are a task worker in a swarm pool. Wait for task assignments via messages. For each assigned task: read the task details via TaskGet, execute the work, update the task status, and report results back to the lead. Continue until you receive a shutdown request.",
  team_name="execution-pool",
  name="worker-1",
  subagent_type="fast",
  run_in_background=true
)

Task(
  description="You are a task worker in a swarm pool. Wait for task assignments via messages. For each assigned task: read the task details via TaskGet, execute the work, update the task status, and report results back to the lead. Continue until you receive a shutdown request.",
  team_name="execution-pool",
  name="worker-2",
  subagent_type="fast",
  run_in_background=true
)

Task(
  description="You are a task worker in a swarm pool. Wait for task assignments via messages. For each assigned task: read the task details via TaskGet, execute the work, update the task status, and report results back to the lead. Continue until you receive a shutdown request.",
  team_name="execution-pool",
  name="worker-3",
  subagent_type="fast",
  run_in_background=true
)

# Phase 4: Dispatch Wave 1 (tasks with no dependencies)
SendMessage(
  type="message",
  recipient="worker-1",
  content="Execute task task-1: Implement user model. Read TaskGet(taskId='task-1') for full details. Report results when done.",
  summary="Assigned task-1 to worker-1"
)

SendMessage(
  type="message",
  recipient="worker-2",
  content="Execute task task-5: Write user model tests. Read TaskGet(taskId='task-5') for full details. Report results when done.",
  summary="Assigned task-5 to worker-2"
)

# Worker-3 stays idle until Wave 1 tasks unblock Wave 2 tasks
# Lead monitors for completion messages and idle notifications

# When worker-1 reports task-1 complete:
TaskUpdate(taskId="task-1", status="completed")
# Tasks task-2, task-3 are now unblocked — dispatch to available workers

SendMessage(
  type="message",
  recipient="worker-1",
  content="Execute task task-2: Implement auth service. Report results when done.",
  summary="Assigned task-2 to worker-1"
)

SendMessage(
  type="message",
  recipient="worker-3",
  content="Execute task task-3: Implement user service. Report results when done.",
  summary="Assigned task-3 to worker-3"
)

# Continue dispatching until all tasks are completed

# Phase 5: Shutdown and cleanup
SendMessage(type="shutdown_request", recipient="worker-1", content="All tasks complete.", request_id="shutdown-w1")
SendMessage(type="shutdown_request", recipient="worker-2", content="All tasks complete.", request_id="shutdown-w2")
SendMessage(type="shutdown_request", recipient="worker-3", content="All tasks complete.", request_id="shutdown-w3")

TeamDelete(team_name="execution-pool")
```

### Scaling Notes

- **2-3 workers**: Good for small task lists (5-10 tasks); low coordination overhead
- **4-6 workers**: Optimal for medium backlogs (10-30 tasks); balance of throughput and coordination cost
- **7-10 workers**: For large backlogs (30+ tasks); requires careful wave management to avoid lead bottleneck
- **Alternative dispatch**: Instead of message-based dispatch, workers can use `TaskList` to self-claim the next pending task (self-organizing variant)

---

## 4. Research then Implement

A two-phase workflow where the first phase explores and researches, and the second phase implements based on the findings. The research phase produces understanding; the implementation phase produces code.

### When to Use

- The task requires **understanding before action** — you cannot implement without first exploring
- The codebase is unfamiliar or the problem domain is complex
- Research can be parallelized (multiple exploration angles) while implementation is sequential
- Examples: feature development in a large codebase, refactoring with unknown scope, adding functionality to an unfamiliar module, migrating to a new library

### Team Structure

| Role | Count | Model Tier | Responsibility |
|------|-------|-----------|----------------|
| Lead | 1 | Opus | Coordinates both phases, plans research, directs implementation |
| Researcher | 2-4 | Sonnet | Explores specific aspects of the codebase or problem domain |
| Synthesizer | 0-1 | Opus | (Optional) Merges research findings into actionable summary |
| Implementer | 1-3 | Opus or Sonnet | Implements based on research findings |

### Task Design

**Phase 1: Research** (parallel)
- Lead identifies 2-4 research questions or exploration angles
- Each researcher explores one angle independently
- Researchers write findings to shared files
- Lead (or synthesizer) merges findings into an implementation plan

**Phase 2: Implementation** (sequential or parallel)
- Lead creates implementation tasks based on the research findings
- Implementation tasks reference the research output
- If implementation is decomposable, multiple implementers can work in parallel

### Communication Flow

```
=== Phase 1: Research ===
Lead: Identify research questions
Lead --> Researcher-1 (spawn: "Explore current auth module")
Lead --> Researcher-2 (spawn: "Research OAuth2 best practices")
Lead --> Researcher-3 (spawn: "Analyze integration points")
Researcher-1 --> Lead (findings via file or message)
Researcher-2 --> Lead (findings via file or message)
Researcher-3 --> Lead (findings via file or message)
Lead: shutdown researchers
Lead: synthesize findings into implementation plan

=== Phase 2: Implementation ===
Lead --> Implementer-1 (spawn: "Implement based on plan")
Implementer-1 --> Lead (results)
Lead: shutdown implementer, cleanup
```

### Practical Example

```
# Phase 1: Create the team
TeamCreate(team_name="feature-team", description="Research and implement OAuth2 authentication")

# Phase 2: Spawn researchers (Sonnet for broad exploration)
Task(
  description="Explore the existing authentication code in src/auth/. Document: file structure, public APIs, middleware chain, session management approach. Write findings to .claude/research/current-auth.md",
  team_name="feature-team",
  name="auth-researcher",
  subagent_type="fast",
  run_in_background=true
)

Task(
  description="Research OAuth2 implementation patterns for Express.js with Passport.js. Document: recommended strategy, required dependencies, configuration patterns. Write findings to .claude/research/oauth2-patterns.md",
  team_name="feature-team",
  name="oauth-researcher",
  subagent_type="fast",
  run_in_background=true
)

Task(
  description="Analyze integration points that would be affected by adding OAuth2: routes, middleware, session store, environment variables, test setup. Write findings to .claude/research/integration-points.md",
  team_name="feature-team",
  name="integration-researcher",
  subagent_type="fast",
  run_in_background=true
)

# Lead waits for all researchers to complete
# When all idle notifications received and files written:
SendMessage(type="shutdown_request", recipient="auth-researcher", content="Research phase complete.", request_id="sd-1")
SendMessage(type="shutdown_request", recipient="oauth-researcher", content="Research phase complete.", request_id="sd-2")
SendMessage(type="shutdown_request", recipient="integration-researcher", content="Research phase complete.", request_id="sd-3")

# Phase 3: Synthesize (lead does this directly for small teams)
# Lead reads all .claude/research/*.md files
# Lead produces implementation plan at .claude/research/implementation-plan.md

# Phase 4: Implement (Opus for complex implementation)
Task(
  description="Read the implementation plan at .claude/research/implementation-plan.md and all research files in .claude/research/. Implement OAuth2 authentication following the plan. Create/modify files as specified in the plan.",
  team_name="feature-team",
  name="implementer",
  subagent_type="default"
)

# Phase 5: Cleanup
TeamDelete(team_name="feature-team")
```

### Scaling Notes

- **2 researchers**: Sufficient for focused investigations with clear separation
- **3-4 researchers**: Good when the problem space has multiple distinct dimensions to explore
- **Multiple implementers**: Only if the implementation decomposes cleanly (e.g., separate frontend and backend work)
- **Hybrid**: Combine with Pipeline pattern — research phase feeds into a multi-stage implementation pipeline

---

## 5. Plan Approval Gate

An agent works in plan mode, producing a proposed plan that must be approved by the lead (or human) before execution begins. This pattern is critical for high-risk changes where review before implementation prevents costly mistakes.

### When to Use

- Changes are **high-risk** — mistakes are expensive to undo (database migrations, API changes, infrastructure)
- Human oversight is required for compliance or safety reasons
- The lead wants to review and potentially redirect the agent's approach before code is written
- Multiple valid approaches exist and the lead wants to choose
- Examples: architecture proposals, destructive operations, dependency upgrades, schema migrations

### Team Structure

| Role | Count | Model Tier | Responsibility |
|------|-------|-----------|----------------|
| Lead / Approver | 1 | Opus (or human) | Reviews plans, approves/rejects with feedback |
| Planner / Worker | 1-3 | Opus | Produces plan, waits for approval, then implements |

Workers operate with `plan_mode_required` semantics — they must produce a plan and wait for approval before executing.

### Task Design

- Worker receives a task description and is instructed to produce a plan first
- Worker analyzes the problem, produces a structured plan, and sends it to the lead
- Lead reviews the plan and responds with `plan_approval_response` (approve or reject with feedback)
- If approved: worker implements the plan
- If rejected: worker revises the plan based on feedback and resubmits

### Communication Flow

```
Lead --> Worker (spawn: "Plan and implement X")
Worker: analyzes problem, produces plan
Worker --> Lead (SendMessage: plan proposal)
Lead: reviews plan
  If approved:
    Lead --> Worker (plan_approval_response: approved)
    Worker: implements the plan
    Worker --> Lead (SendMessage: implementation complete)
  If rejected:
    Lead --> Worker (plan_approval_response: rejected, feedback="Change X to Y")
    Worker: revises plan based on feedback
    Worker --> Lead (SendMessage: revised plan)
    Lead: reviews again (loop until approved)
Lead --> Worker (shutdown_request)
```

### Practical Example

```
# Phase 1: Create the team
TeamCreate(team_name="migration-team", description="Database migration with plan approval")

# Phase 2: Spawn the planner
Task(
  description="You are tasked with designing and implementing a database migration to add OAuth2 support. IMPORTANT: Before making any changes, you MUST first produce a detailed migration plan and send it to the team lead for approval. Include: 1) Tables to create/modify, 2) Column definitions, 3) Index strategy, 4) Data migration steps, 5) Rollback plan. Send your plan via SendMessage and wait for approval before implementing.",
  team_name="migration-team",
  name="migration-planner",
  subagent_type="default",
  run_in_background=true
)

# Phase 3: Lead receives the plan via message
# The planner sends something like:
#   SendMessage(
#     type="message",
#     recipient="lead",
#     content="## Migration Plan\n1. Create oauth_tokens table...\n2. Add provider column to users...\n3. Create indexes on...\n4. Rollback: DROP TABLE oauth_tokens...",
#     summary="Migration plan ready for review"
#   )

# Phase 4: Lead reviews and responds
# If the plan looks good:
SendMessage(
  type="plan_approval_response",
  recipient="migration-planner",
  content="Plan approved. Proceed with implementation. One note: use UUID for the token_id column instead of auto-increment.",
  approved=true
)

# If the plan needs changes:
SendMessage(
  type="plan_approval_response",
  recipient="migration-planner",
  content="Plan needs revision: 1) Add a refresh_token_expires_at column, 2) Include a unique constraint on (user_id, provider), 3) Add the rollback migration file too.",
  approved=false
)
# Planner revises and resubmits — lead reviews again

# Phase 5: After implementation completes
SendMessage(
  type="shutdown_request",
  recipient="migration-planner",
  content="Migration complete. Shutting down.",
  request_id="shutdown-planner"
)

TeamDelete(team_name="migration-team")
```

### Scaling Notes

- **Single planner**: Most common; one agent plans, one lead approves
- **2-3 planners**: When you want competing proposals — each planner produces an independent plan, lead picks the best one
- **Cascading gates**: Chain multiple approval gates for multi-stage high-risk work (plan architecture, approve, plan migration, approve, implement)
- **Human-in-the-loop**: The lead can be a human using Claude Code's interactive mode; the planner sends the plan and waits for the human's response

---

## 6. Hub-and-Spoke with Follow-Ups

A central synthesizer receives findings from multiple exploration agents and can send targeted follow-up questions to specific agents for clarification. This extends the Parallel Specialists pattern with a feedback loop.

### When to Use

- Exploration results need **cross-referencing** — findings from one specialist may raise questions for another
- The synthesizer needs to resolve contradictions or fill gaps in specialist reports
- Deep understanding requires iterative refinement, not just one-pass exploration
- Examples: comprehensive codebase analysis, security audits, architecture reviews

### Team Structure

| Role | Count | Model Tier | Responsibility |
|------|-------|-----------|----------------|
| Lead | 1 | Opus | Coordinates overall workflow, manages team lifecycle |
| Explorer | 2-6 | Sonnet | Explores assigned focus area, answers follow-up questions |
| Synthesizer | 1 | Opus | Reads all findings, identifies gaps, sends follow-ups, produces final report |

### Task Design

- Lead spawns explorers (parallel, background) and one synthesizer
- Explorers investigate their focus areas and write findings
- Synthesizer reads all findings, identifies gaps or contradictions
- Synthesizer sends targeted follow-up messages to specific explorers
- Explorers respond to follow-ups with additional investigation
- Synthesizer produces the final merged report

### Communication Flow

```
Lead --> Explorer-1 (spawn: focus area A)
Lead --> Explorer-2 (spawn: focus area B)
Lead --> Explorer-3 (spawn: focus area C)
Lead --> Synthesizer (spawn: waits for findings)

Explorer-1: writes findings to file, goes idle
Explorer-2: writes findings to file, goes idle
Explorer-3: writes findings to file, goes idle

Synthesizer: reads all findings files
Synthesizer --> Explorer-1 (SendMessage: "Clarify the auth middleware chain you found")
Synthesizer --> Explorer-3 (SendMessage: "How does component X connect to module Y?")
Explorer-1 --> Synthesizer (SendMessage: clarification)
Explorer-3 --> Synthesizer (SendMessage: clarification)
Synthesizer: produces final report

Lead: shutdown all agents, cleanup
```

### Practical Example

```
# Phase 1: Create the team
TeamCreate(team_name="audit-team", description="Security audit with follow-up investigation")

# Phase 2: Spawn explorers
Task(
  description="Explore authentication and authorization code. Document: auth flows, token handling, permission checks, session management. Write to .claude/audit/auth-findings.md. Stay available for follow-up questions from the synthesizer.",
  team_name="audit-team",
  name="auth-explorer",
  subagent_type="fast",
  run_in_background=true
)

Task(
  description="Explore input validation and data sanitization. Document: validation patterns, SQL injection protection, XSS prevention, file upload handling. Write to .claude/audit/input-findings.md. Stay available for follow-up questions from the synthesizer.",
  team_name="audit-team",
  name="input-explorer",
  subagent_type="fast",
  run_in_background=true
)

Task(
  description="Explore dependency security and configuration. Document: known vulnerable dependencies, environment variable handling, secrets management, CORS configuration. Write to .claude/audit/config-findings.md. Stay available for follow-up questions from the synthesizer.",
  team_name="audit-team",
  name="config-explorer",
  subagent_type="fast",
  run_in_background=true
)

# Phase 3: Spawn synthesizer (waits for findings)
Task(
  description="You are the security audit synthesizer. Wait for all explorer findings to be written, then: 1) Read all files in .claude/audit/. 2) Cross-reference findings for contradictions or gaps. 3) Send follow-up questions to specific explorers via SendMessage if clarification is needed. 4) Produce the final audit report at .claude/audit/security-report.md with severity ratings and remediation priorities.",
  team_name="audit-team",
  name="synthesizer",
  subagent_type="default",
  run_in_background=true
)

# The synthesizer might send follow-ups like:
#   SendMessage(
#     type="message",
#     recipient="auth-explorer",
#     content="The config-explorer found that JWT_SECRET is loaded from .env but you noted tokens are validated in middleware. Is the secret rotation handled? Check if there's a key rotation mechanism.",
#     summary="Follow-up: JWT secret rotation"
#   )

# Phase 4: When synthesizer completes the report, shutdown all
SendMessage(type="shutdown_request", recipient="auth-explorer", content="Audit complete.", request_id="sd-auth")
SendMessage(type="shutdown_request", recipient="input-explorer", content="Audit complete.", request_id="sd-input")
SendMessage(type="shutdown_request", recipient="config-explorer", content="Audit complete.", request_id="sd-config")
SendMessage(type="shutdown_request", recipient="synthesizer", content="Audit complete.", request_id="sd-synth")

TeamDelete(team_name="audit-team")
```

### Scaling Notes

- **2-3 explorers + 1 synthesizer**: Standard configuration for most analysis tasks
- **4-6 explorers**: Useful for large codebases; synthesizer may need multiple follow-up rounds
- **Multiple synthesizers**: Rare; consider only for very broad analyses where the synthesis itself can be partitioned

---

## Pattern Selection Guide

Use this decision matrix to choose the right orchestration pattern for your use case.

### Quick Decision Tree

```
Is the work parallelizable with no inter-task dependencies?
  YES --> Are results independent (no cross-referencing needed)?
    YES --> Pattern 1: Parallel Specialists
    NO  --> Pattern 6: Hub-and-Spoke with Follow-Ups
  NO  --> Does the work flow through sequential stages?
    YES --> Pattern 2: Pipeline with Dependencies
    NO  --> Is there a large backlog of similar tasks?
      YES --> Pattern 3: Swarm / Self-Organizing Pool
      NO  --> Does understanding need to precede implementation?
        YES --> Pattern 4: Research then Implement
        NO  --> Is the change high-risk requiring review?
          YES --> Pattern 5: Plan Approval Gate
          NO  --> Pattern 1: Parallel Specialists (default)
```

### Comparison Matrix

| Criterion | Parallel Specialists | Pipeline | Swarm | Research-Implement | Plan Approval | Hub-and-Spoke |
|-----------|---------------------|----------|-------|-------------------|--------------|---------------|
| **Parallelism** | High | Low (sequential) | High | Medium (research parallel, impl sequential) | Low | High (with feedback) |
| **Coordination overhead** | Low | Medium | Medium-High | Medium | Low-Medium | Medium-High |
| **Best team size** | 3-8 | 2-5 | 3-10 | 3-5 | 2-3 | 3-7 |
| **Task uniformity** | Low (specialists) | Low (stage-specific) | High (workers interchangeable) | Low (phase-specific) | Low | Low (specialists) |
| **Risk management** | Low | Medium (gates between stages) | Low | Medium | High | Medium |
| **Feedback loops** | None | Forward only | Retry on failure | Research informs impl | Approve/reject cycle | Synthesizer follow-ups |

### Pattern Combinations

Patterns can be combined for complex workflows:

- **Research then Pipeline**: Research phase (Pattern 4) feeds into a multi-stage pipeline (Pattern 2)
- **Swarm with Approval Gates**: Workers in a pool (Pattern 3) but high-risk tasks require lead approval (Pattern 5) before implementation
- **Pipeline with Parallel Stages**: Some pipeline stages use Parallel Specialists (Pattern 1) internally for parallel subtask execution
- **Hub-and-Spoke then Implement**: Deep analysis via Hub-and-Spoke (Pattern 6) followed by implementation tasks dispatched to a Swarm (Pattern 3)

### Anti-Patterns to Avoid

| Anti-Pattern | Problem | Use Instead |
|-------------|---------|-------------|
| Single-agent-does-everything | Wastes parallelism opportunity; context overload | Any multi-agent pattern |
| All agents same model tier | Wastes Opus tokens on simple exploration | Match model tier to task complexity |
| No coordination mechanism | Agents duplicate work or produce conflicting outputs | Use SendMessage or shared task list |
| Spawning without background | Lead blocks waiting for each agent sequentially | Use `run_in_background=true` for parallel agents |
| Immediate shutdown on idle | Wastes spawning cost; prevents reuse | Keep idle agents for follow-up work |
| Broadcasting everything | N messages for N members per broadcast; context noise | Use targeted `message` type for specific recipients |
