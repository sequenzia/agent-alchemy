# SDD Tools Deep Dive

A comprehensive walkthrough of the Spec-Driven Development pipeline — from adaptive interview through wave-based autonomous execution. This deep dive covers internal architecture, data flow patterns, execution context sharing, and end-to-end workflow examples that go beyond the [SDD Tools reference page](sdd-tools.md).

**Plugin:** `agent-alchemy-sdd-tools` | **Version:** 0.2.0 | **Skills:** 4 | **Agents:** 4

---

## Executive Summary

The **sdd-tools** plugin implements a complete Spec-Driven Development (SDD) pipeline for Claude Code. It transforms the development process from ad-hoc prompting into a structured workflow: **idea → spec → tasks → execution**. The plugin is fully standalone (no external plugin dependencies) and provides 4 skills, 4 agents, and a lifecycle hook, enabling developers to go from a product idea to working code through an automated, verification-driven pipeline.

---

## What is Spec-Driven Development?

Spec-Driven Development is a methodology where:

1. **Requirements are captured formally** before any code is written
2. **Specifications are structured documents** with testable acceptance criteria
3. **Tasks are derived algorithmically** from specs, with automatic dependency inference
4. **Implementation is verified** against spec-defined acceptance criteria
5. **The spec is the single source of truth** throughout the development lifecycle

This contrasts with the typical AI-assisted development pattern where users describe features in natural language and the AI generates code directly — often losing requirements, skipping edge cases, and producing code that's hard to verify.

```mermaid
graph LR
    A["💡 Idea"] --> B["📋 Spec"]
    B --> C["🔍 Analysis"]
    C --> D["✅ Tasks"]
    D --> E["⚡ Execution"]
    E --> F["✔️ Verified Code"]

    style A fill:#7c4dff,color:#fff
    style B fill:#7c4dff,color:#fff
    style C fill:#f44336,color:#fff
    style D fill:#4caf50,color:#fff
    style E fill:#ff9800,color:#fff
    style F fill:#00bcd4,color:#fff
```

---

## Plugin Architecture

### Directory Structure

```
sdd-tools/
├── agents/
│   ├── codebase-explorer.md    # Codebase exploration (Sonnet)
│   ├── researcher.md           # External research (Opus)
│   ├── spec-analyzer.md        # Spec quality analysis (Opus)
│   └── task-executor.md        # Task implementation (Opus)
├── hooks/
│   ├── hooks.json              # PreToolUse hook configuration
│   └── auto-approve-session.sh # Session directory auto-approve
├── skills/
│   ├── create-spec/
│   │   ├── SKILL.md            # Interview workflow (660 lines)
│   │   └── references/
│   │       ├── codebase-exploration.md
│   │       ├── interview-questions.md
│   │       ├── recommendation-triggers.md
│   │       ├── recommendation-format.md
│   │       └── templates/
│   │           ├── high-level.md
│   │           ├── detailed.md
│   │           └── full-tech.md
│   ├── analyze-spec/
│   │   ├── SKILL.md            # Analysis workflow
│   │   ├── references/
│   │   │   ├── analysis-criteria.md
│   │   │   ├── common-issues.md
│   │   │   ├── html-review-guide.md
│   │   │   └── report-template.md
│   │   └── templates/
│   │       └── review-template.html
│   ├── create-tasks/
│   │   ├── SKILL.md            # Task decomposition (653 lines)
│   │   └── references/
│   │       ├── decomposition-patterns.md
│   │       ├── dependency-inference.md
│   │       └── testing-requirements.md
│   └── execute-tasks/
│       ├── SKILL.md            # Execution orchestrator (262 lines)
│       ├── references/
│       │   ├── execution-workflow.md
│       │   ├── orchestration.md
│       │   └── verification-patterns.md
│       └── scripts/
│           └── poll-for-results.sh
└── README.md
```

### Component Summary

| Component | Count | Description |
|-----------|-------|-------------|
| Skills | 4 | create-spec, analyze-spec, create-tasks, execute-tasks |
| Agents | 4 | codebase-explorer, researcher, spec-analyzer, task-executor |
| Hooks | 1 | auto-approve-session (PreToolUse) |
| Reference files | 14 | Question banks, templates, criteria, patterns |
| Spec templates | 3 | High-level, detailed, full-tech |

---

## The SDD Pipeline

The complete SDD pipeline flows through four skills in sequence. Each skill produces artifacts that feed into the next.

```mermaid
flowchart TD
    subgraph Phase1["Phase 1: Specification"]
        CS["/create-spec"]
        CS -->|"writes"| SPEC["specs/SPEC-{name}.md"]
    end

    subgraph Phase2["Phase 2: Quality Gate"]
        AS["/analyze-spec"]
        SPEC -->|"reads"| AS
        AS -->|"writes"| REPORT["specs/{name}.analysis.md"]
        AS -->|"writes"| HTML["specs/{name}.analysis.html"]
        AS -->|"may update"| SPEC
    end

    subgraph Phase3["Phase 3: Decomposition"]
        CT["/create-tasks"]
        SPEC -->|"reads"| CT
        CT -->|"creates"| TASKS["~/.claude/tasks/{list}/*.json"]
    end

    subgraph Phase4["Phase 4: Execution"]
        ET["/execute-tasks"]
        TASKS -->|"reads"| ET
        ET -->|"spawns"| AGENTS["task-executor agents × N"]
        AGENTS -->|"writes"| CODE["Implementation + Tests"]
        AGENTS -->|"writes"| CTX[".claude/sessions/__live_session__/"]
        ET -->|"updates"| TASKS
    end

    subgraph External["External: Real-Time Monitoring"]
        TASKS -->|"watched by"| TM["Task Manager Dashboard"]
    end

    style CS fill:#7c4dff,color:#fff
    style SPEC fill:#00bcd4,color:#fff
    style AS fill:#7c4dff,color:#fff
    style REPORT fill:#00bcd4,color:#fff
    style HTML fill:#00bcd4,color:#fff
    style CT fill:#7c4dff,color:#fff
    style TASKS fill:#00bcd4,color:#fff
    style ET fill:#7c4dff,color:#fff
    style AGENTS fill:#ff9800,color:#fff
    style CODE fill:#4caf50,color:#fff
    style CTX fill:#4caf50,color:#fff
    style TM fill:#00bcd4,color:#fff
```

### Pipeline Artifacts

| Phase | Input | Output | Format |
|-------|-------|--------|--------|
| create-spec | User interview answers | `specs/SPEC-{name}.md` | Structured markdown PRD |
| analyze-spec | Spec file | `.analysis.md` + `.analysis.html` | Report + interactive HTML |
| create-tasks | Spec file | Task JSON files | Claude Code native tasks |
| execute-tasks | Task list | Code changes + session artifacts | Source code + execution logs |

---

## Skill 1: create-spec -- Adaptive Interview

### Purpose

Transforms a product idea into a structured specification through an adaptive, multi-round interview process. The skill adjusts its questioning depth, provides proactive recommendations, and can explore the existing codebase for context.

### Workflow (6 Phases)

```mermaid
flowchart TD
    P1["Phase 1: Settings Check"] --> P2["Phase 2: Initial Inputs"]
    P2 --> |"Name, Type, Depth, Description"| P3["Phase 3: Adaptive Interview"]

    P3 --> |"For 'new feature' type"| CE["Codebase Exploration"]
    CE --> |"findings"| P3

    P3 --> |"Trigger detected"| RES["External Research"]
    RES --> |"findings"| P3

    P3 --> |"2-5 rounds"| P4["Phase 4: Recommendations Round"]
    P4 --> P5["Phase 5: Pre-Compilation Summary"]
    P5 --> |"User confirms"| P6["Phase 6: Spec Compilation"]
    P6 --> SPEC["specs/SPEC-{name}.md"]

    style P3 fill:#7c4dff,color:#fff
    style CE fill:#ff9800,color:#fff
    style RES fill:#7c4dff,color:#fff
    style SPEC fill:#4caf50,color:#fff
```

### Depth Levels

The interview adapts based on the requested depth level:

| Level | Rounds | Questions | Focus | Output |
|-------|--------|-----------|-------|--------|
| **High-level overview** | 2-3 | 6-10 | Problem, goals, key features, success metrics | Executive summary |
| **Detailed specifications** | 3-4 | 12-18 | Balanced coverage, acceptance criteria, technical constraints | Standard PRD |
| **Full technical documentation** | 4-5 | 18-25 | Deep probing, API endpoints, data models, performance | Comprehensive tech spec |

### Question Categories

Each interview round covers four categories (depth-adjusted):

1. **Problem & Goals** -- Problem statement, success metrics, user personas, business value
2. **Functional Requirements** -- Features, user stories, acceptance criteria, workflows
3. **Technical Specs** -- Architecture, tech stack, data models, APIs, constraints
4. **Implementation** -- Phases, dependencies, risks, out-of-scope items

### Proactive Features

- **Recommendation triggers**: Scans user responses for patterns that suggest best-practice recommendations (e.g., mentioning "auth" triggers authentication pattern suggestions)
- **External research**: Can invoke the `researcher` agent for technical documentation, competitive analysis, or compliance requirements
- **Codebase exploration**: For "new feature" type specs, spawns `codebase-explorer` agents (Sonnet) in parallel to discover existing architecture, patterns, and integration points
- **Early exit support**: Users can wrap up early; spec is marked as `Draft (Partial)`

!!! tip "Recommendation Triggers"
    The interview skill monitors user responses for keyword patterns (e.g., "authentication", "scale", "real-time", "compliance") and proactively surfaces best-practice recommendations. This bridges the gap between user intent and implementation knowledge.

### Spec Templates

Three templates matched to depth levels:

| Template | File | Use Case |
|----------|------|----------|
| High-level | `references/templates/high-level.md` | Executive summaries, stakeholder alignment |
| Detailed | `references/templates/detailed.md` | Standard development specs |
| Full-tech | `references/templates/full-tech.md` | API specs, data models, architecture |

---

## Skill 2: analyze-spec -- Quality Gate

### Purpose

Performs systematic quality analysis on an existing spec, identifying inconsistencies, missing information, ambiguities, and structure issues. Provides both a markdown report and an interactive HTML review interface.

### Analysis Categories

| Category | What It Catches | Example |
|----------|----------------|---------|
| **Inconsistencies** | Internal contradictions | Feature named "Search" in one section, "Find" in another |
| **Missing Information** | Expected content absent for depth level | Full-tech spec with no API definitions |
| **Ambiguities** | Vague or multi-interpretable statements | "Users should be able to search quickly" |
| **Structure Issues** | Formatting and organization problems | Missing required sections, orphaned references |

### Severity Levels

| Severity | Definition | Example |
|----------|-----------|---------|
| **Critical** | Would cause implementation failure | Circular dependencies, undefined core requirements |
| **Warning** | Could cause confusion or problems | Vague acceptance criteria, unnamed dependencies |
| **Suggestion** | Quality improvement, not blocking | Inconsistent formatting, missing glossary |

### Output Formats

1. **Markdown report** (`{name}.analysis.md`) -- Structured findings with severity, location, and recommendations
2. **Interactive HTML review** (`{name}.analysis.html`) -- Browser-based UI for approving/rejecting findings with copy-prompt workflow

### Review Modes

```mermaid
flowchart TD
    A["Spec Analyzed"] --> B{"Choose Review Mode"}
    B --> C["Interactive HTML Review"]
    B --> D["CLI Update Mode"]
    B --> E["Reports Only"]

    C --> F["Open in Browser"]
    F --> G["Approve/Reject Findings"]
    G --> H["Copy Prompt"]
    H --> I["Paste Back → Apply Changes"]

    D --> J["Walk Through Each Finding"]
    J --> K{"Apply / Modify / Skip"}
    K --> |"Apply"| L["Edit spec directly"]
    K --> |"Modify"| M["User provides text → Edit"]
    K --> |"Skip"| N["Record reason, move on"]

    E --> O["Keep reports as-is"]

    style C fill:#7c4dff,color:#fff
    style D fill:#ff9800,color:#fff
    style E fill:#455a64,color:#fff
```

!!! info "Depth-Aware Analysis"
    The analyzer detects the spec's depth level (high-level, detailed, or full-tech) and only flags issues appropriate to that level. A high-level spec is never penalized for missing API specifications.

---

## Skill 3: create-tasks -- Spec Decomposition

### Purpose

Transforms a specification into a dependency-ordered set of Claude Code native Tasks, each with categorized acceptance criteria, testing requirements, and metadata for tracking.

### Workflow (8 Phases)

```mermaid
flowchart TD
    P1["Phase 1: Validate & Load"] --> P2["Phase 2: Detect Depth & Check Existing"]
    P2 --> P3["Phase 3: Analyze Spec"]
    P3 --> P4["Phase 4: Decompose Tasks"]
    P4 --> P5["Phase 5: Infer Dependencies"]
    P5 --> P6["Phase 6: Preview & Confirm"]
    P6 --> |"User approves"| P7{"Existing tasks?"}
    P7 --> |"No"| P7A["Phase 7a: Fresh Create"]
    P7 --> |"Yes"| P7B["Phase 7b: Merge Mode"]
    P7A --> P8["Phase 8: Report"]
    P7B --> P8

    style P4 fill:#7c4dff,color:#fff
    style P5 fill:#ff9800,color:#fff
    style P7B fill:#f44336,color:#fff
```

### Task Decomposition Pattern

Each feature is decomposed using a standard layer pattern:

```mermaid
flowchart TD
    F["Feature from Spec"] --> DM["1. Data Model Tasks"]
    F --> API["2. API/Service Tasks"]
    F --> BL["3. Business Logic Tasks"]
    F --> UI["4. UI/Frontend Tasks"]
    F --> TEST["5. Test Tasks"]

    DM --> |"blocks"| API
    API --> |"blocks"| UI
    BL --> |"blocks"| TEST

    style DM fill:#4caf50,color:#fff
    style API fill:#7c4dff,color:#fff
    style BL fill:#ff9800,color:#fff
    style UI fill:#f44336,color:#fff
    style TEST fill:#00bcd4,color:#fff
```

### Depth-Based Granularity

| Spec Depth | Tasks per Feature | Granularity | Example |
|-----------|-------------------|-------------|---------|
| High-level | 1-2 | Feature-level | "Implement user authentication" |
| Detailed | 3-5 | Functional decomposition | "Implement login endpoint", "Add password validation" |
| Full-tech | 5-10 | Technical decomposition | "Create User model", "Implement POST /auth/login", "Add auth middleware" |

### Task Structure

Each generated task includes:

```markdown
subject: "Create User data model"              # Imperative mood
description: |
  {What needs to be done}

  **Acceptance Criteria:**

  _Functional:_
  - [ ] Core behavior criteria

  _Edge Cases:_
  - [ ] Boundary condition criteria

  _Error Handling:_
  - [ ] Error scenario criteria

  _Performance:_ (if applicable)
  - [ ] Performance target criteria

  **Testing Requirements:**
  - Unit: Schema validation
  - Integration: Database persistence

  Source: specs/SPEC-Auth.md Section 7.3
activeForm: "Creating User data model"
metadata:
  priority: critical|high|medium|low
  complexity: XS|S|M|L|XL
  spec_path: "specs/SPEC-Auth.md"
  feature_name: "User Authentication"
  task_uid: "specs/SPEC-Auth.md:user-auth:model:001"
  task_group: "user-authentication"
```

!!! warning "task_group is Required"
    The `task_group` field must be set on every task. The `/execute-tasks` skill relies on `metadata.task_group` for `--task-group` filtering and session ID generation. Tasks without `task_group` will be invisible to group-filtered execution runs.

### Merge Mode

When re-running on an updated spec, tasks are intelligently merged:

```mermaid
flowchart TD
    RE["Re-run /create-tasks"] --> MATCH{"Match by task_uid"}
    MATCH --> |"Match found"| STATUS{"Task status?"}
    STATUS --> |"completed"| PRESERVE["Preserve — never modify"]
    STATUS --> |"in_progress"| SKIP["Preserve status, optionally update description"]
    STATUS --> |"pending"| UPDATE["Update description if changed"]
    MATCH --> |"No match (new)"| CREATE["Create new task"]
    MATCH --> |"No match (existing)"| OBSOLETE{"Potentially obsolete"}
    OBSOLETE --> KEEP["Keep if user confirms"]
    OBSOLETE --> MARK["Mark completed if user confirms"]

    style PRESERVE fill:#4caf50,color:#fff
    style SKIP fill:#ff9800,color:#fff
    style UPDATE fill:#7c4dff,color:#fff
    style CREATE fill:#1565c0,color:#fff
    style OBSOLETE fill:#f44336,color:#fff
```

### Dependency Inference

Dependencies are automatically inferred from three sources:

1. **Layer dependencies**: Data Model → API → UI → Tests
2. **Phase dependencies**: Phase 2 tasks blocked by Phase 1 completion
3. **Explicit spec dependencies**: Section 10 of spec ("requires X" → blockedBy X)
4. **Cross-feature dependencies**: Shared data models, services, auth

!!! note "Circular Dependency Handling"
    If a circular dependency is detected during task creation, the system breaks the cycle at the weakest link (scored by relationship type) and flags the affected task with `needs_review: true` in metadata. See the [SDD Tools reference](sdd-tools.md#dependency-inference) for the full inference rules.

---

## Skill 4: execute-tasks -- Autonomous Execution

### Purpose

Orchestrates autonomous task execution with wave-based parallelism, session management, shared execution context, and adaptive verification. After user confirmation, it runs without further interaction until all tasks are complete.

### Core Principles

1. **Understand before implementing** -- Read context, conventions, and earlier task learnings
2. **Follow existing patterns** -- Match the codebase's coding style and conventions
3. **Verify against criteria** -- Walk through each acceptance criterion, run tests
4. **Report honestly** -- PASS only when all Functional criteria and tests pass

### Orchestration Loop (10 Steps)

```mermaid
flowchart TD
    S1["Step 1: Load Task List"] --> S2["Step 2: Validate State"]
    S2 --> S3["Step 3: Build Execution Plan"]
    S3 --> S4["Step 4: Check Settings"]
    S4 --> S5["Step 5: Initialize Session"]
    S5 --> S6["Step 6: Present Plan & Confirm"]
    S6 --> |"User confirms"| S7["Step 7: Initialize Context"]
    S7 --> S8["Step 8: Execute Loop"]
    S8 --> S9["Step 9: Session Summary"]
    S9 --> S10["Step 10: Update CLAUDE.md"]

    subgraph ExecuteLoop["Step 8: Wave Execution Loop"]
        W1["Snapshot execution_context.md"] --> W2["Mark tasks in_progress"]
        W2 --> W3["Launch N background agents"]
        W3 --> W4["Poll for result files"]
        W4 --> W5{"All complete?"}
        W5 --> |"No"| W4
        W5 --> |"Yes"| W6["Batch-read results"]
        W6 --> W7["Reap agents via TaskOutput"]
        W7 --> W8{"Failed tasks with retries?"}
        W8 --> |"Yes"| W9["Re-launch as background agents"]
        W9 --> W4
        W8 --> |"No"| W10["Merge context files"]
        W10 --> W11["Refresh TaskList"]
        W11 --> W12{"More waves?"}
        W12 --> |"Yes"| W1
        W12 --> |"No"| DONE["Exit loop"]
    end

    S8 --> ExecuteLoop

    style W3 fill:#7c4dff,color:#fff
    style W9 fill:#f44336,color:#fff
    style DONE fill:#4caf50,color:#fff
```

### Wave-Based Parallelism

Tasks are organized into waves using topological sort:

```mermaid
flowchart LR
    subgraph Wave1["Wave 1 (No Dependencies)"]
        T1["Task 1: Create User model"]
        T2["Task 2: Create Config model"]
    end

    subgraph Wave2["Wave 2 (Depends on Wave 1)"]
        T3["Task 3: Implement /auth/login"]
        T4["Task 4: Implement /auth/register"]
    end

    subgraph Wave3["Wave 3 (Depends on Wave 2)"]
        T5["Task 5: Build Login UI"]
        T6["Task 6: Add auth middleware"]
    end

    subgraph Wave4["Wave 4 (Depends on Wave 3)"]
        T7["Task 7: Integration tests"]
    end

    T1 --> T3
    T1 --> T4
    T2 --> T3
    T3 --> T5
    T3 --> T6
    T4 --> T5
    T5 --> T7
    T6 --> T7

    style T1 fill:#4caf50,color:#fff
    style T2 fill:#4caf50,color:#fff
    style T3 fill:#7c4dff,color:#fff
    style T4 fill:#7c4dff,color:#fff
    style T5 fill:#ff9800,color:#fff
    style T6 fill:#ff9800,color:#fff
    style T7 fill:#00bcd4,color:#fff
```

!!! tip "Wave Scheduling"
    Tasks within a wave run in parallel (up to `max_parallel` concurrent agents). After each wave completes, newly unblocked tasks form the next wave. Within waves, tasks are sorted by priority (critical > high > medium > low).

### Task Executor 4-Phase Workflow

Each task is executed by a `task-executor` agent (Opus) through:

```mermaid
flowchart LR
    P1["Phase 1\nUnderstand"] --> P2["Phase 2\nImplement"]
    P2 --> P3["Phase 3\nVerify"]
    P3 --> P4["Phase 4\nComplete"]

    P1 -.- N1["Read context\nClassify task\nExplore codebase\nPlan implementation"]
    P2 -.- N2["Read target files\nWrite code\nWrite tests\nRun linter"]
    P3 -.- N3["Check criteria\nRun tests\nDetermine status"]
    P4 -.- N4["Update task status\nWrite learnings\nWrite result file"]

    style P1 fill:#7c4dff,color:#fff
    style P2 fill:#4caf50,color:#fff
    style P3 fill:#ff9800,color:#fff
    style P4 fill:#00bcd4,color:#fff
```

### Verification Status

| Condition | Status | What Happens |
|-----------|--------|--------------|
| All Functional criteria pass + Tests pass | **PASS** | Task marked `completed` |
| All Functional pass + Tests pass + Edge/Error/Perf issues | **PARTIAL** | Task stays `in_progress`, may retry |
| Any Functional criterion fails | **FAIL** | Task stays `in_progress`, retry with failure context |
| Any test failure | **FAIL** | Task stays `in_progress`, retry with failure context |

!!! info "Adaptive Verification"
    The executor detects whether a task is **spec-generated** (has `**Acceptance Criteria:**` sections, `metadata.spec_path`, or `Source:` references) or a **general task**. Spec-generated tasks are verified criterion-by-criterion. General tasks use an inferred checklist based on the description.

### Session Management

```mermaid
flowchart TD
    INIT["Initialize Session"] --> DIR[".claude/sessions/__live_session__/"]
    DIR --> EP["execution_plan.md"]
    DIR --> EC["execution_context.md"]
    DIR --> TL["task_log.md"]
    DIR --> PR["progress.md"]
    DIR --> TD["tasks/ (archived JSONs)"]
    DIR --> LOCK[".lock (concurrency guard)"]

    POINTER["~/.claude/tasks/{list}/execution_pointer.md"] --> DIR

    COMPLETE["Session Complete"] --> ARCHIVE[".claude/sessions/{execution_id}/"]
    DIR --> |"move contents"| ARCHIVE

    style DIR fill:#7c4dff,color:#fff
    style POINTER fill:#ff9800,color:#fff
    style ARCHIVE fill:#4caf50,color:#fff
```

### Key Execution Features

| Feature | Description |
|---------|-------------|
| **Background agents** | Agents run via `run_in_background: true`, returning ~3 lines instead of full output |
| **Result file protocol** | Each agent writes a compact `result-task-{id}.md` (~18 lines) as completion signal |
| **Per-task context isolation** | Each agent writes to `context-task-{id}.md`, orchestrator merges after wave |
| **Configurable parallelism** | Default 5 concurrent agents; overridable via `--max-parallel` |
| **Configurable retries** | Default 3 attempts; overridable via `--retries` |
| **Retry with context** | Failed tasks include previous failure details for different approach |
| **Interrupted session recovery** | Stale sessions archived; in_progress tasks reset to pending |
| **Concurrency guard** | `.lock` file prevents concurrent execution sessions |
| **Token usage tracking** | Per-task `duration_ms` and `total_tokens` extracted via TaskOutput |

!!! tip "Result File Protocol"
    The result file protocol is a key optimization. Instead of consuming the full agent output (which can be thousands of tokens), the orchestrator polls for compact `result-task-{id}.md` files (~18 lines each). This achieves a **79% context reduction per wave** — critical for keeping the orchestrator within its context window across many waves.

---

## Agent Inventory

```mermaid
flowchart TD
    subgraph Agents["SDD Tools Agents"]
        CE["codebase-explorer\n(Sonnet)"]
        R["researcher\n(Opus)"]
        SA["spec-analyzer\n(Opus)"]
        TE["task-executor\n(Opus)"]
    end

    CS["/create-spec"] --> |"spawns for 'new feature'"| CE
    CS --> |"spawns for research"| R
    AS["/analyze-spec"] --> |"launches"| SA
    ET["/execute-tasks"] --> |"launches × N per wave"| TE

    CE --> |"Read, Glob, Grep, Bash"| CODEBASE["Codebase"]
    R --> |"WebSearch, WebFetch, Context7"| WEB["External Sources"]
    SA --> |"AskUserQuestion, Read, Write, Edit"| SPEC["Spec Files"]
    TE --> |"Read, Write, Edit, Glob, Grep, Bash"| CODE["Source Code"]

    style CE fill:#7c4dff,color:#fff
    style R fill:#00bcd4,color:#fff
    style SA fill:#f44336,color:#fff
    style TE fill:#4caf50,color:#fff
```

| Agent | Model | Tools | Role | Spawned By |
|-------|-------|-------|------|------------|
| **codebase-explorer** | Sonnet | Read, Glob, Grep, Bash | Explores codebase for patterns and architecture | `/create-spec` (parallel, for "new feature" type) |
| **researcher** | Opus | WebSearch, WebFetch, Context7 | Technical and domain research for specs | `/create-spec` (on-demand or proactive) |
| **spec-analyzer** | Opus | AskUserQuestion, Read, Write, Edit, Glob, Grep | Quality analysis with interactive resolution | `/analyze-spec` |
| **task-executor** | Opus | Read, Write, Edit, Glob, Grep, Bash, TaskGet/Update/List | Autonomous 4-phase task implementation | `/execute-tasks` (N per wave, background) |

!!! note "Model Tiering Rationale"
    **Sonnet for codebase-explorer**: These agents perform broad, parallelizable search work. Sonnet is cost-effective for exploration where reasoning depth is less critical than breadth. **Opus for researcher, spec-analyzer, task-executor**: These agents require deep reasoning — synthesizing research findings, analyzing spec quality, and implementing code with verification.

---

## Hooks & Automation

### auto-approve-session.sh

| Property | Value |
|----------|-------|
| **Event** | `PreToolUse` |
| **Triggers** | Write, Edit, Bash operations |
| **Purpose** | Auto-approves file operations within `.claude/sessions/` directories |
| **Timeout** | 5 seconds |

!!! info "Why This Hook Exists"
    This hook enables task-executor agents to write execution context files, result files, and session artifacts without requiring user approval for each operation. Without it, every file write during autonomous execution would pause for user confirmation — breaking the autonomous execution loop.

---

## End-to-End Workflow Walkthrough

### Example: Building a User Authentication Feature

```mermaid
sequenceDiagram
    participant U as Developer
    participant CS as /create-spec
    participant CE as codebase-explorer
    participant AS as /analyze-spec
    participant SA as spec-analyzer
    participant CT as /create-tasks
    participant ET as /execute-tasks
    participant TE as task-executor × N
    participant TM as Task Manager

    Note over U,TM: Phase 1: Specification

    U->>CS: /create-spec
    CS->>U: What type? "New feature"
    CS->>U: What depth? "Detailed"
    CS->>CE: Explore auth patterns (Sonnet × 2)
    CE-->>CS: Architecture findings
    CS->>U: Interview rounds (3-4 rounds, 12-18 questions)
    CS->>U: Recommendations round
    CS->>U: Pre-compilation summary — confirm?
    U->>CS: Confirmed
    CS-->>U: specs/SPEC-User-Auth.md created

    Note over U,TM: Phase 2: Quality Gate (Optional)

    U->>AS: /analyze-spec specs/SPEC-User-Auth.md
    AS->>SA: Analyze spec (Opus)
    SA-->>AS: 8 findings (2 critical, 4 warning, 2 suggestion)
    AS->>U: Choose review mode
    U->>AS: CLI Update Mode
    AS->>U: Walk through each finding
    U->>AS: Apply 6, Skip 2
    AS-->>U: Spec updated, report saved

    Note over U,TM: Phase 3: Decomposition

    U->>CT: /create-tasks specs/SPEC-User-Auth.md
    CT->>CT: Detect depth: Detailed
    CT->>CT: Extract features, decompose, infer dependencies
    CT->>U: Preview: 15 tasks, 22 dependencies
    U->>CT: Confirmed
    CT-->>U: 15 tasks created with dependency chains
    CT-->>TM: Tasks visible in Kanban board

    Note over U,TM: Phase 4: Execution

    U->>ET: /execute-tasks --task-group user-authentication
    ET->>ET: Build wave plan: Wave 1 (3 tasks), Wave 2 (5), Wave 3 (4), Wave 4 (3)
    ET->>U: Execution plan — confirm?
    U->>ET: Confirmed

    loop Each Wave
        ET->>TE: Launch N background agents
        TE->>TE: Understand → Implement → Verify → Complete
        TE-->>ET: result-task-{id}.md (PASS/PARTIAL/FAIL)
        ET->>ET: Merge context, form next wave
        ET-->>TM: Task status updates (real-time)
    end

    ET-->>U: Session summary: 14 PASS, 1 PARTIAL
```

### Step-by-Step

1. **`/create-spec`** -- Developer initiates spec creation. The skill asks about type ("new feature"), depth ("detailed"), and runs a 3-4 round interview. For new features, it spawns codebase explorers to understand existing patterns. It produces `specs/SPEC-User-Auth.md`.

2. **`/analyze-spec specs/SPEC-User-Auth.md`** (optional but recommended) -- The spec is analyzed for quality issues. The developer reviews findings via CLI or HTML interface, fixing critical issues before task generation.

3. **`/create-tasks specs/SPEC-User-Auth.md`** -- The spec is decomposed into 15 dependency-ordered tasks. Each task has categorized acceptance criteria (Functional, Edge Cases, Error Handling, Performance), testing requirements, and metadata. The developer previews and confirms.

4. **`/execute-tasks --task-group user-authentication`** -- The orchestrator builds a wave plan and launches background task-executor agents in parallel. Each agent reads the execution context, implements the task, verifies against acceptance criteria, and reports results. The [Task Manager dashboard](../task-manager.md) shows real-time progress.

---

## Data Flow Diagrams

### Artifact Flow Through the Pipeline

```mermaid
flowchart TD
    subgraph Inputs
        USER["User's Idea"]
        CODEBASE["Existing Codebase"]
    end

    subgraph SpecPhase["Specification Phase"]
        INTERVIEW["Interview Answers"]
        EXPLORE["Exploration Findings"]
        RESEARCH["Research Findings"]
        RECS["Recommendations"]
    end

    subgraph Artifacts
        SPEC["SPEC-{name}.md"]
        ANALYSIS["Analysis Report + HTML"]
        TASKS["Task JSON Files"]
        CONTEXT["Execution Context"]
        CODE["Implemented Code"]
        LOGS["Session Logs"]
    end

    USER --> INTERVIEW
    CODEBASE --> EXPLORE
    INTERVIEW --> SPEC
    EXPLORE --> SPEC
    RESEARCH --> SPEC
    RECS --> SPEC
    SPEC --> ANALYSIS
    ANALYSIS --> |"fixes"| SPEC
    SPEC --> TASKS
    TASKS --> CONTEXT
    CONTEXT --> CODE
    CODE --> LOGS

    style SPEC fill:#7c4dff,color:#fff,stroke-width:3px
    style TASKS fill:#4caf50,color:#fff,stroke-width:3px
    style CODE fill:#ff9800,color:#fff,stroke-width:3px
```

### Execution Context Sharing

```mermaid
flowchart TD
    subgraph Wave1["Wave 1"]
        A1["Agent 1"] --> |"writes"| C1["context-task-1.md"]
        A2["Agent 2"] --> |"writes"| C2["context-task-2.md"]
    end

    subgraph Merge1["Between Waves"]
        C1 --> EC["execution_context.md"]
        C2 --> EC
    end

    subgraph Wave2["Wave 2"]
        EC --> |"snapshot read"| A3["Agent 3"]
        EC --> |"snapshot read"| A4["Agent 4"]
        A3 --> |"writes"| C3["context-task-3.md"]
        A4 --> |"writes"| C4["context-task-4.md"]
    end

    subgraph Merge2["After Wave 2"]
        C3 --> EC2["execution_context.md\n(merged)"]
        C4 --> EC2
    end

    style EC fill:#7c4dff,color:#fff,stroke-width:2px
    style EC2 fill:#7c4dff,color:#fff,stroke-width:2px
```

!!! tip "Context Isolation Pattern"
    Each agent writes to an isolated `context-task-{id}.md` file during execution. After all agents in a wave complete, the orchestrator merges per-task files into the shared `execution_context.md`. This eliminates write contention while letting later tasks benefit from earlier discoveries — a pattern also used by the [core-tools deep-analysis](core-tools.md) skill.

---

## Use Cases & Benefits

### Use Cases

| Use Case | How SDD Tools Helps |
|----------|-------------------|
| **Greenfield feature development** | Structured spec → decomposed tasks → parallel autonomous execution |
| **Complex multi-component features** | Dependency inference ensures correct build order; wave parallelism maximizes throughput |
| **Team alignment** | Spec serves as single source of truth; analyze-spec catches ambiguities before coding starts |
| **Iterative spec refinement** | Merge mode preserves completed work when specs evolve; analyze-spec provides quality gate |
| **Compliance-sensitive projects** | Research agent gathers regulatory requirements; specs document acceptance criteria for audit |
| **Reducing rework** | Verification against acceptance criteria catches issues before they compound |
| **Onboarding new team members** | Specs document the "why" behind features; execution context captures implementation decisions |

### Benefits for Developers

| Benefit | Without SDD Tools | With SDD Tools |
|---------|-------------------|----------------|
| **Requirements capture** | Ad-hoc prompts, lost context | Structured spec with testable criteria |
| **Task planning** | Manual decomposition | Automatic dependency-aware decomposition |
| **Parallel execution** | Sequential, one task at a time | Wave-based concurrent agent execution |
| **Verification** | Manual review or trust | Automated criterion-by-criterion verification |
| **Knowledge sharing** | Each task starts from scratch | Shared execution context across tasks |
| **Progress visibility** | Checking git log | Real-time [Task Manager](../task-manager.md) dashboard |
| **Spec evolution** | Start over or manual diff | Merge mode preserves completed work |
| **Quality assurance** | Post-hoc review | Pre-implementation spec analysis |

---

## Integration with Other Plugins

### Standalone Design

sdd-tools is a **standalone plugin** -- it has no external plugin dependencies. This was achieved by giving sdd-tools its own `codebase-explorer` agent instead of relying on core-tools.

### Consumed By Other Plugins

| Plugin | How It Uses sdd-tools |
|--------|---------------------|
| **[tdd-tools](tdd-tools.md)** | `/execute-tdd-tasks` routes non-TDD tasks to the `task-executor` agent from sdd-tools |
| **[tdd-tools](tdd-tools.md)** | `/create-tdd-tasks` reads tasks created by `/create-tasks` and generates TDD pairs |

!!! tip "TDD Extension"
    The SDD pipeline integrates seamlessly with the [TDD Tools](tdd-tools.md) plugin. After `/create-tasks`, run `/create-tdd-tasks` to generate RED-GREEN test pairs, then `/execute-tdd-tasks` for TDD-aware execution. See the [TDD Tools documentation](tdd-tools.md) for the full TDD workflow.

### Integration with Task Manager

The [Task Manager dashboard](../task-manager.md) provides real-time visualization:

```mermaid
flowchart LR
    ET["/execute-tasks"] --> |"creates/updates"| JSON["~/.claude/tasks/*.json"]
    JSON --> |"Chokidar watches"| FW["FileWatcher"]
    FW --> |"EventEmitter"| SSE["SSE Route"]
    SSE --> |"stream"| CLIENT["Browser"]
    CLIENT --> |"invalidateQueries"| TQ["TanStack Query"]
    TQ --> KB["Kanban Board"]

    style ET fill:#ff9800,color:#fff
    style JSON fill:#4caf50,color:#fff
    style KB fill:#7c4dff,color:#fff
```

---

## Configuration & Settings

Settings are configured in `.claude/agent-alchemy.local.md` (not committed):

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `execute-tasks.max-parallel` | number | 5 | Maximum concurrent agents per wave |
| Custom output path | string | `specs/` | Directory for spec output |
| Author name | string | -- | Attribution in spec metadata |

### Command-Line Arguments

| Skill | Arguments | Description |
|-------|-----------|-------------|
| `/create-spec` | (none) | Starts interactive interview |
| `/analyze-spec` | `[spec-path]` | Path to spec file |
| `/create-tasks` | `[spec-path]` | Path to spec file |
| `/execute-tasks` | `[task-id] [--task-group <group>] [--retries <n>] [--max-parallel <n>]` | Flexible execution control |

---

## Reference File Inventory

| Skill | File | Purpose | Contents |
|-------|------|---------|----------|
| create-spec | `interview-questions.md` | Question bank | Questions organized by category and depth |
| create-spec | `recommendation-triggers.md` | Trigger patterns | Keyword patterns for proactive recommendations |
| create-spec | `recommendation-format.md` | Recommendation templates | How to present recommendations to users |
| create-spec | `codebase-exploration.md` | Exploration procedure | 4-step codebase exploration workflow |
| create-spec | `templates/high-level.md` | Spec template | Streamlined executive overview |
| create-spec | `templates/detailed.md` | Spec template | Standard PRD with all sections |
| create-spec | `templates/full-tech.md` | Spec template | Extended with API specs, data models |
| analyze-spec | `analysis-criteria.md` | Depth checklists | What to check at each depth level |
| analyze-spec | `common-issues.md` | Issue patterns | Known issue patterns with examples |
| analyze-spec | `report-template.md` | Report format | Markdown report structure |
| analyze-spec | `html-review-guide.md` | HTML generation | Instructions for HTML review output |
| create-tasks | `decomposition-patterns.md` | Decomposition rules | Feature-to-task decomposition patterns |
| create-tasks | `dependency-inference.md` | Dependency rules | Automatic dependency inference logic |
| create-tasks | `testing-requirements.md` | Test mappings | Task type → test type mappings |
| execute-tasks | `orchestration.md` | Orchestration loop | Full 10-step execution procedure |
| execute-tasks | `execution-workflow.md` | Phase workflow | 4-phase agent workflow details |
| execute-tasks | `verification-patterns.md` | Verification rules | Task classification and pass/fail criteria |
