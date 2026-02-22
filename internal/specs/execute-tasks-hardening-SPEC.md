# execute-tasks-hardening PRD

**Version**: 1.0
**Author**: Stephen Sequenzia
**Date**: 2026-02-22
**Status**: Draft
**Spec Type**: New feature (enhancement to existing product)
**Spec Depth**: Full technical documentation
**Description**: Harden the execute-tasks skill with programmatic enforcement, file conflict prevention, event-driven completion, structured context, and improved UX — addressing all 10 recommendations from the deep analysis report.

---

## 1. Executive Summary

The execute-tasks skill is a wave-based task orchestrator that launches isolated AI agents to execute coding tasks autonomously. While architecturally sound (35/35 tasks passed across two sessions with 0 retries), its coordination protocol relies entirely on AI instruction-following, creating fragility in format compliance, write ordering, concurrent file edits, and completion detection. This spec defines 10 hardening improvements across four phases to add programmatic enforcement, reduce context overhead, prevent file conflicts, and improve user experience during long execution sessions.

## 2. Problem Statement

### 2.1 The Problem

The execute-tasks orchestration protocol has no programmatic enforcement layer. Critical invariants — result file format, write ordering, no direct writes to shared files, and non-overlapping file edits within a wave — are expressed solely as markdown instructions that agents may not follow consistently.

### 2.2 Current State

The system works via a "prompt-as-protocol" pattern:
- **Result file protocol**: Agents are *told* to write ~18-line result files with specific format — no validation
- **Write ordering**: "Context file FIRST, result file LAST" is prose, not enforced
- **Completion detection**: 15-second fixed polling loop wastes time on fast tasks and context on polling output
- **Context sharing**: Free-form markdown appended by agents with varying quality and no schema
- **Progress**: Users see nothing between plan confirmation and final summary (~50+ minutes of silence)
- **Reference loading**: Each agent reads ~845+ lines of instructions before starting work, much of it redundant

### 2.3 Impact Analysis

**Current fragility evidence:**
- Plugin-porting session had concurrent SKILL.md edits across Waves 3a, 3b, and 4 — resolved only by Edit tool's stale-content rejection (fragile)
- Both successful sessions (35/35) were greenfield tasks (new file creation) — modification-heavy workloads remain unproven
- Orchestrator context pressure grows with wave count; waves 5-6 may have degraded decision quality

**What could go wrong without hardening:**
- Malformed result file → orchestrator parsing failure → wave hangs at timeout
- Missing context file → lost learnings for downstream tasks
- Concurrent file edits → silent data loss when one agent overwrites another's changes
- Context growth → orchestrator context exhaustion on large (50+ task) sessions

### 2.4 Business Value

Hardening enables the execute-tasks skill to handle:
- Modification-heavy workloads (editing existing files, refactoring)
- Larger task counts (30-50+ tasks)
- Failure-prone tasks that require retries with escalation
- Better user experience during long autonomous sessions

## 3. Goals & Success Metrics

### 3.1 Primary Goals

1. Add programmatic enforcement for critical protocol invariants (result validation, write ordering)
2. Prevent file conflicts between concurrent agents within a wave
3. Reduce orchestrator context consumption per wave
4. Improve user visibility during execution

### 3.2 Success Metrics

| Metric | Current Baseline | Target | Measurement Method |
|--------|------------------|--------|-------------------|
| Protocol violations caught | 0 (no detection) | 100% of malformed result files caught | Hook validation logs |
| File conflict prevention | 0 (no detection) | Conflicts detected and moved to separate waves | Pre-wave scan logs in task_log.md |
| Completion detection latency | 0-15s (polling interval) | <1s with fswatch, <5s with adaptive polling | Timestamp delta: result file creation vs orchestrator detection |
| Agent startup overhead | ~845 lines read | ~425 lines (embedded rules) | Removed explicit Read calls from agent workflow |
| User silence duration | Full session (~50 min) | Max 1 wave duration (~5-10 min between updates) | Wave completion summaries emitted |
| Retry recovery rate | N/A (0 retries observed) | User escalation after 2 enriched retries | Retry escalation log entries |

### 3.3 Non-Goals

- Updating execute-tdd-tasks to use new infrastructure (separate spec)
- Backward compatibility with old task JSON format (clean break)
- Automated test generation for the orchestrator itself
- Hierarchical orchestration for 100+ task sessions

## 4. User Research

### 4.1 Target Users

#### Primary Persona: Orchestrator Agent
- **Role/Description**: The execute-tasks skill running as the top-level coordinator
- **Goals**: Manage wave execution, process results, merge context, handle failures
- **Pain Points**: Context pressure from polling output and result processing; no enforcement of agent compliance; blind to file conflicts
- **Context**: Runs in a single Claude Code session for 30-60+ minutes
- **Technical Proficiency**: AI agent (Opus model)

#### Secondary Persona: Task-Executor Agent
- **Role/Description**: Spawned background agent executing a single coding task
- **Goals**: Read task description, explore codebase, implement, verify, write results
- **Pain Points**: Reads ~845 lines of instructions before starting; context file is free-form; no validation feedback on result file format

#### Tertiary Persona: Human Operator
- **Role/Description**: Developer who invokes `/execute-tasks` and waits for completion
- **Goals**: Monitor progress, intervene on failures, review final session summary
- **Pain Points**: No progress visibility during execution; no way to provide guidance on stuck tasks

### 4.2 User Workflows

#### Workflow: Hardened Execution Pipeline

```
User invokes /execute-tasks
        |
        v
[Orchestrator] ── Loads tasks, builds dependency graph
        |          Topological sort → waves
        |          NEW: Scan for file conflicts → adjust waves
        |
        v
[Wave N] ── Launches agents with embedded rules (no ref file reads)
        |    NEW: Agents write structured context sections
        |    NEW: Agents write result files → PostToolUse hook validates
        |    NEW: fswatch detects result files immediately
        |
        v
[Detect] ── NEW: fswatch/inotifywait or adaptive polling fallback
        |
        v
[Process] ── Read validated result files
        |    NEW: Inject producer task results into dependent prompts
        |    Reap agents, extract duration/tokens
        |    Retry failed tasks with escalation
        |
        v
[Merge] ── Merge structured context sections
        |    NEW: Post-merge validation
        |    NEW: Emit wave completion summary to user
        |
        v
[Next Wave] or [Session Summary + Archive]
```

## 5. Functional Requirements

### 5.1 Feature: File Conflict Detection

**Priority**: P0 (Critical)
**Complexity**: Medium

#### User Stories

**US-001**: As the orchestrator, I want to detect when two tasks in the same wave reference the same files so that I can prevent concurrent edit conflicts by moving one task to a later wave.

**Acceptance Criteria**:
- [ ] Before launching each wave, scan all wave tasks' `description` and `acceptance_criteria` fields for file path references
- [ ] File paths detected via pattern matching: paths containing `/`, ending in known extensions (`.md`, `.ts`, `.js`, `.json`, `.sh`, `.py`), or matching glob patterns
- [ ] When two or more tasks reference the same file path, flag a conflict
- [ ] Conflicting tasks are moved to the next wave by inserting an artificial dependency
- [ ] The original task (lower ID) stays in the current wave; higher-ID tasks are deferred
- [ ] Conflict detection results logged in `execution_plan.md` under a "Conflict Resolution" section
- [ ] If no conflicts detected, wave proceeds as normal with no overhead

**Technical Notes**:
- Detection is description-based only (not heuristic or static analysis)
- Implemented as a pre-wave step in the orchestrator's wave planning logic
- Uses Grep to scan task JSON descriptions for file path patterns

**Edge Cases**:
| Scenario | Input | Expected Behavior |
|----------|-------|-------------------|
| No file paths in descriptions | Generic descriptions like "implement feature X" | No conflicts detected, wave unchanged |
| All tasks conflict on same file | 3 tasks all mention `SKILL.md` | Task with lowest ID stays, others sequentialized |
| Glob patterns in descriptions | "modify `src/api/*.ts`" | Treat glob as a file path reference; overlapping globs = conflict |
| Cross-reference in acceptance criteria | File path only in AC, not description | AC is scanned alongside description |

**Error Handling**:
| Error Condition | System Action |
|-----------------|---------------|
| Path pattern regex fails | Log warning, proceed without conflict detection for this wave |
| All tasks in wave conflict | Sequentialize: one task per "sub-wave" |

---

### 5.2 Feature: Result File Validation Hook

**Priority**: P0 (Critical)
**Complexity**: Medium

#### User Stories

**US-002**: As the orchestrator, I want result files to be validated automatically after agents write them so that malformed output is caught before I process it.

**US-003**: As the orchestrator, I want the write-ordering invariant enforced so that context files are always written before result files.

**Acceptance Criteria**:
- [ ] PostToolUse hook triggers on Write operations targeting `result-task-*.md` files in the session directory
- [ ] Hook validates: first line matches `status: (PASS|PARTIAL|FAIL)` pattern
- [ ] Hook validates: required sections present (`## Summary`, `## Files Modified`, `## Context Contribution`)
- [ ] Hook validates: corresponding `context-task-{id}.md` file exists (write-ordering invariant)
- [ ] If context file is missing, hook creates a stub: `### Task [{id}]: No learnings captured`
- [ ] Hook NEVER exits non-zero (falls through to normal permission flow on any error)
- [ ] Hook logs validation results to stderr for debugging (optional via `AGENT_ALCHEMY_HOOK_DEBUG=1`)
- [ ] Malformed result files are renamed to `result-task-{id}.md.invalid` with error description appended

**Technical Notes**:
- Hook is a shell script in `hooks/` directory, registered in `hooks/hooks.json`
- Pattern matching uses grep, not regex libraries, for portability
- Hook must be fast (<100ms) to not slow down agent execution
- Follows existing `auto-approve-session.sh` patterns: defensive, trap on ERR

**Edge Cases**:
| Scenario | Input | Expected Behavior |
|----------|-------|-------------------|
| Agent writes result before context | result-task-5.md exists, context-task-5.md missing | Create context stub, allow result write |
| Agent writes partial result file | Missing status line | Rename to `.invalid`, orchestrator treats as incomplete |
| Agent writes extra text after result | Result file >25 lines | Accept first 18 lines, log warning about extra content |
| Hook script itself errors | Unexpected input format | Trap catches error, falls through to normal flow |

---

### 5.3 Feature: Progress Streaming

**Priority**: P0 (Critical)
**Complexity**: Low

#### User Stories

**US-004**: As a human operator, I want to see wave completion summaries during execution so that I know the session is progressing and can identify issues early.

**Acceptance Criteria**:
- [ ] After each wave completes, orchestrator emits a summary via text output (visible to user)
- [ ] Summary includes: wave number (N/total), tasks completed, pass/fail count, wave duration
- [ ] Per-task breakdown: task ID, task name, status (PASS/PARTIAL/FAIL), duration, token count
- [ ] Before starting next wave, emit: "Starting Wave {N}/{total}: {count} tasks..."
- [ ] On session start, emit: "Execution plan: {total_tasks} tasks across {total_waves} waves (max {max_parallel} parallel)"
- [ ] Summary format is structured but human-readable (not JSON)
- [ ] Wave-level granularity only (no per-task streaming during a wave)

**Technical Notes**:
- Summaries are regular text output between tool calls
- Data sourced from result files and TaskOutput reaping (already collected)
- No additional file I/O required; this is a presentation change

**Format Example**:
```
Wave 2/6 complete: 3/3 tasks passed (2m 34s)
  [3] Create test-writer agent — PASS (1m 52s, 48K tokens)
  [5] Create tdd-workflow reference — PASS (2m 22s, 54K tokens)
  [7] Create test patterns reference — PASS (2m 34s, 61K tokens)

Starting Wave 3/6: 2 tasks...
```

---

### 5.4 Feature: Event-Driven Completion Detection

**Priority**: P1 (High)
**Complexity**: Medium

#### User Stories

**US-005**: As the orchestrator, I want to be notified immediately when result files appear so that I can process completed tasks without polling delays.

**Acceptance Criteria**:
- [ ] New script `watch-for-results.sh` uses `fswatch` (macOS) or `inotifywait` (Linux) to watch the session directory
- [ ] Script emits one line per result file detected: `RESULT_FOUND: result-task-{id}.md ({found}/{expected})`
- [ ] Script emits `ALL_DONE` when all expected result files are present
- [ ] Script accepts: session directory path, expected result count, and list of expected task IDs
- [ ] Script has a configurable timeout (default: 45 minutes, matching current behavior)
- [ ] If neither `fswatch` nor `inotifywait` is available, script exits with code 2 (not-available signal)
- [ ] Orchestrator detects exit code 2 and falls back to adaptive polling (Rec #8)
- [ ] Zero-latency detection: result files are reported within 1 second of creation

**Technical Notes**:
- `fswatch` is available via Homebrew on macOS; `inotifywait` is from `inotify-tools` on Linux
- Script checks for tool availability at startup: `command -v fswatch` / `command -v inotifywait`
- Watches for `Created` events only (not `Modified`) to avoid duplicate signals
- Replaces `poll-for-results.sh` as the primary completion mechanism

**Edge Cases**:
| Scenario | Input | Expected Behavior |
|----------|-------|-------------------|
| Result file already exists at watch start | Pre-existing result-task-3.md | Detect existing files before starting watch, count toward expected |
| fswatch exits unexpectedly | Process killed, permission error | Orchestrator falls back to adaptive polling |
| Agent creates temp file then renames | result-task-5.md.tmp → result-task-5.md | Watch triggers on final filename only |
| Timeout reached | 45 minutes elapsed | Script exits with code 1, orchestrator handles as wave timeout |

---

### 5.5 Feature: Generalized Prompt Injection

**Priority**: P1 (High)
**Complexity**: Medium

#### User Stories

**US-006**: As the orchestrator, I want to inject result data from producer tasks directly into dependent task prompts so that downstream agents get richer context than wave-granular merging alone provides.

**Acceptance Criteria**:
- [ ] New `produces_for` field in task JSON schema: array of task IDs that consume this task's output
- [ ] When launching a dependent task, orchestrator reads the producer's result file and injects it into the task prompt
- [ ] Injection format: `## UPSTREAM TASK OUTPUT (Task #{id}: {name})\n{result file content}\n---`
- [ ] Multiple producers are injected in task ID order
- [ ] Injection happens after execution context loading but before codebase exploration
- [ ] If producer result file is missing (task failed), inject a notice: `## UPSTREAM TASK #{id} FAILED\n{failure summary from task_log.md}`
- [ ] `produces_for` field is optional; tasks without it behave as before (wave-granular context only)

**Technical Notes**:
- Requires `/create-tasks` to emit `produces_for` field when task relationships are detected
- Clean break: new task JSON format required (old format not supported)
- Pattern inspired by execute-tdd-tasks' `PAIRED TEST TASK OUTPUT` mechanism
- Injection adds ~18 lines per producer task to the dependent task's prompt

**Data Model: Task JSON Extension**:
```json
{
  "id": "5",
  "subject": "Implement API handler",
  "description": "...",
  "acceptance_criteria": ["..."],
  "produces_for": ["8", "12"],
  "blockedBy": ["3"]
}
```

---

### 5.6 Feature: Embedded Agent Rules

**Priority**: P1 (High)
**Complexity**: Low

#### User Stories

**US-007**: As a task-executor agent, I want critical verification and execution rules embedded in my agent definition so that I don't need to read 574 lines of separate reference files at startup.

**Acceptance Criteria**:
- [ ] Essential rules from `execution-workflow.md` and `verification-patterns.md` are distilled and embedded in `task-executor.md` body
- [ ] Agent no longer instructed to explicitly Read `execution-workflow.md`, `verification-patterns.md`, or `orchestration.md`
- [ ] Embedded rules cover: 4-phase execution workflow, verification classification (spec vs general tasks), result file format, context contribution format
- [ ] Agent definition grows from ~325 lines to ~425 lines (+100 lines of embedded rules)
- [ ] Reference files remain in `references/` directory for documentation purposes but are not loaded by agents
- [ ] The `skills: [execute-tasks]` frontmatter continues to auto-load `SKILL.md` (no change)
- [ ] Agent startup overhead reduced by ~574 lines of file reads per agent

**Technical Notes**:
- The task-executor agent is defined in `claude/sdd-tools/agents/task-executor.md`
- Rules should be concise and action-oriented (not explanatory prose from references)
- `orchestration.md` was never needed by executors (it's for the orchestrator)

---

### 5.7 Feature: Structured Context Schema

**Priority**: P1 (High)
**Complexity**: Medium

#### User Stories

**US-008**: As a task-executor agent, I want to write learnings into specific structured sections so that my contributions are consistently formatted and useful to downstream agents.

**US-009**: As the orchestrator, I want to merge per-task context files into a structured schema so that the execution context stays organized and within size limits.

**Acceptance Criteria**:
- [ ] `execution_context.md` uses 6 fixed section headers: `## Project Setup`, `## File Patterns`, `## Conventions`, `## Key Decisions`, `## Known Issues`, `## Task History`
- [ ] Per-task `context-task-{id}.md` files use the same 6 section headers
- [ ] Agents write entries under the appropriate sections (not free-form prose)
- [ ] Orchestrator merges per-task files by appending entries under matching section headers
- [ ] Duplicate entries within a section are deduplicated during merge
- [ ] Compaction at 10+ entries per section: older entries summarized into a paragraph
- [ ] Empty sections in per-task files are omitted (agents only write sections with content)
- [ ] Initial `execution_context.md` is created with all 6 headers and empty content

**Structured Context Template**:
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

**Technical Notes**:
- Structured markdown chosen over YAML/JSON for agent authoring tolerance
- Section headers serve as merge anchors — orchestrator splits on `## ` markers
- Compaction uses AI summarization (same as current approach, but per-section)

---

### 5.8 Feature: Adaptive Polling (Fallback)

**Priority**: P2 (Medium)
**Complexity**: Low

#### User Stories

**US-010**: As the orchestrator falling back to polling (no fswatch/inotifywait), I want the polling interval to adapt so that fast tasks are detected quickly and slow tasks don't waste context.

**Acceptance Criteria**:
- [ ] Modified `poll-for-results.sh` starts with 5-second interval
- [ ] Interval increases by 5 seconds after each poll round with no new results
- [ ] Maximum interval caps at 30 seconds
- [ ] When a new result is found, interval resets to 5 seconds
- [ ] Cumulative timeout remains 45 minutes (matching current behavior)
- [ ] Interval progression: 5s → 10s → 15s → 20s → 25s → 30s → 30s → ...
- [ ] Environment variable `POLL_START_INTERVAL` overrides starting interval (default: 5)
- [ ] Environment variable `POLL_MAX_INTERVAL` overrides maximum interval (default: 30)

**Technical Notes**:
- Modification to existing `scripts/poll-for-results.sh`
- Only used when `watch-for-results.sh` reports exit code 2 (tools unavailable)

---

### 5.9 Feature: Retry Escalation

**Priority**: P2 (Medium)
**Complexity**: Medium

#### User Stories

**US-011**: As the orchestrator, I want failed task retries to escalate through strategies so that persistent failures get progressively more help rather than repeating the same approach.

**Acceptance Criteria**:
- [ ] **Retry #1 (Standard)**: Re-launch agent with failure context from previous attempt (existing behavior)
- [ ] **Retry #2 (Context Enrichment)**: Inject full `execution_context.md` content + result files from related tasks (tasks sharing dependencies or same wave) into the retry prompt
- [ ] **Retry #3 (User Escalation)**: Pause execution, present failure details to user via AskUserQuestion, ask for guidance: "Fix manually and continue" / "Skip this task" / "Provide guidance" / "Abort session"
- [ ] If user selects "Provide guidance", capture their text input and inject it into a final retry attempt
- [ ] If user selects "Skip this task", mark as FAIL in task_log.md and continue with remaining waves
- [ ] If user selects "Abort session", clean up session and present partial summary
- [ ] Retry escalation level tracked in `task_log.md` per task
- [ ] Retry count resets for each new task (not cumulative across tasks)

**Edge Cases**:
| Scenario | Input | Expected Behavior |
|----------|-------|-------------------|
| Task fails all 3 retries without user skip | Unlikely with user escalation | User must choose action at retry #3 |
| User provides guidance but retry still fails | Retry #4 with user guidance | Present same AskUserQuestion again with updated failure |
| Multiple tasks fail in same wave | 2 of 5 tasks fail | Each gets independent retry escalation |
| Retry #2 discovers the real issue | Context enrichment helps | Task passes, escalation stops |

---

### 5.10 Feature: Post-Wave Merge Validation

**Priority**: P2 (Medium)
**Complexity**: Low

#### User Stories

**US-012**: As the orchestrator, I want to validate `execution_context.md` after each merge so that corruption or unbounded growth is caught early.

**Acceptance Criteria**:
- [ ] After merging per-task context files, validate all 6 section headers are present
- [ ] Check total file size: warn if >500 lines, error if >1000 lines
- [ ] Check for malformed sections: content outside of any section header
- [ ] If validation fails: log warning in `task_log.md`, attempt auto-repair (re-insert missing headers)
- [ ] If size exceeds 1000 lines: force compaction of all sections before proceeding
- [ ] Validation results included in wave completion summary (Rec #3)

**Technical Notes**:
- Implemented as a shell script or inline orchestrator logic
- Runs after context merge, before next wave launch
- Leverages the structured schema (Rec #7) for reliable header detection

---

## 6. Non-Functional Requirements

### 6.1 Performance Requirements

| Metric | Requirement | Measurement Method |
|--------|-------------|-------------------|
| Hook validation latency | < 100ms per invocation | Time delta in hook debug logs |
| fswatch detection latency | < 1s from file creation | Timestamp comparison |
| Adaptive poll first check | 5s after wave launch | Script timing |
| Agent startup reduction | ~574 fewer lines read | Diff of agent Read calls |
| Orchestrator context per wave | < current baseline | Token count comparison |

### 6.2 Reliability Requirements

- Hook must NEVER exit non-zero (defensive programming)
- fswatch script must gracefully handle tool unavailability (exit code 2)
- Polling fallback must work on all POSIX systems
- Retry escalation must eventually reach user (no infinite automated retries)

### 6.3 Portability Requirements

- Shell scripts must work on macOS (zsh/bash) and Linux (bash)
- `fswatch` dependency is optional (fallback to polling)
- `inotifywait` dependency is optional (fallback to polling)
- No new dependencies beyond standard POSIX utilities for core functionality

## 7. Technical Architecture

### 7.1 System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Orchestrator (SKILL.md + orchestration.md)   │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Wave Planner │  │  Conflict    │  │  Context Merger      │  │
│  │ (topo sort)  │  │  Detector    │  │  (structured schema) │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Result       │  │  Retry       │  │  Progress            │  │
│  │ Processor    │  │  Escalator   │  │  Streamer            │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
         │                    │                     │
         ▼                    ▼                     ▼
┌─────────────────┐  ┌──────────────┐  ┌───────────────────────┐
│  Task-Executor  │  │   Hooks      │  │   Scripts             │
│  Agents (Opus)  │  │              │  │                       │
│                 │  │ validate-    │  │ watch-for-results.sh  │
│ Embedded rules  │  │ result.sh    │  │ poll-for-results.sh   │
│ Structured ctx  │  │ (PostToolUse)│  │ (adaptive fallback)   │
│ produces_for    │  │              │  │                       │
└─────────────────┘  └──────────────┘  └───────────────────────┘
         │                    │                     │
         ▼                    ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Session Directory                            │
│                                                                  │
│  execution_context.md (structured: 6 sections)                  │
│  execution_plan.md (+ conflict resolution section)              │
│  task_log.md (+ retry escalation tracking)                      │
│  progress.md                                                     │
│  context-task-{id}.md (structured sections)                     │
│  result-task-{id}.md (validated by hook)                        │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Component Inventory

| Component | File | Current Lines | Change Type |
|-----------|------|---------------|-------------|
| Orchestrator skill | `skills/execute-tasks/SKILL.md` | 271 | Modify (add conflict detection, progress streaming, retry escalation, prompt injection) |
| Orchestration reference | `references/orchestration.md` | 611 | Modify (structured context merge, conflict detection procedures, retry escalation logic) |
| Execution workflow reference | `references/execution-workflow.md` | 318 | Modify (structured context writing, embedded rule references) |
| Verification patterns reference | `references/verification-patterns.md` | 256 | No change (becomes documentation-only, not agent-loaded) |
| Task-executor agent | `agents/task-executor.md` | 325 | Modify → ~425 lines (embed verification rules, structured context, produces_for handling) |
| Polling script | `scripts/poll-for-results.sh` | 61 | Modify (adaptive intervals) |
| Auto-approve hook | `hooks/auto-approve-session.sh` | 75 | No change |
| Hooks config | `hooks/hooks.json` | ~20 | Modify (add validate-result hook registration) |
| **New**: Result validation hook | `hooks/validate-result.sh` | ~50 (new) | New file |
| **New**: Filesystem watch script | `scripts/watch-for-results.sh` | ~60 (new) | New file |

### 7.3 File Format Specifications

#### Result File Format (Validated by Hook)

```markdown
status: PASS|PARTIAL|FAIL
task_id: {id}
duration: {Xm Ys}

## Summary
{1-3 sentence summary of what was done}

## Files Modified
- {file path 1} — {what changed}
- {file path 2} — {what changed}

## Context Contribution
{Key learnings for downstream tasks}

## Verification
{What was checked and the result}
```

#### Per-Task Context File Format

```markdown
## Project Setup
- {discovery about project setup, if any}

## File Patterns
- {discovered file patterns, if any}

## Conventions
- {discovered conventions, if any}

## Key Decisions
- [Task #{id}] {decision made and rationale}

## Known Issues
- {issues encountered, if any}
```

#### Task JSON Schema Extension

```json
{
  "id": "string (required)",
  "subject": "string (required)",
  "description": "string (required)",
  "acceptance_criteria": ["string"],
  "produces_for": ["string (task IDs)"],
  "blockedBy": ["string (task IDs)"],
  "priority": "string (P0|P1|P2|P3)",
  "task_uid": "string (composite key for merge mode)"
}
```

### 7.4 Hook Configuration

#### hooks.json Extension

```json
{
  "hooks": [
    {
      "event": "PostToolUse",
      "type": "command",
      "pattern": "Write",
      "command": "${CLAUDE_PLUGIN_ROOT}/hooks/validate-result.sh",
      "timeout": 5000
    }
  ]
}
```

#### validate-result.sh Behavior

```
Input: PostToolUse event data (tool name, parameters including file path)
Filter: Only triggers when file path matches */result-task-*.md
Validate:
  1. First line matches "status: (PASS|PARTIAL|FAIL)"
  2. Contains "## Summary" section
  3. Contains "## Files Modified" section
  4. Contains "## Context Contribution" section
  5. Corresponding context-task-{id}.md exists
If invalid:
  - Rename to result-task-{id}.md.invalid
  - Log error to stderr
  - Exit 0 (NEVER exit non-zero)
If context missing:
  - Create stub context file
  - Allow result write
  - Log warning to stderr
```

### 7.5 Script Specifications

#### watch-for-results.sh

```
Usage: watch-for-results.sh <session_dir> <expected_count> [task_ids...]
Exit codes:
  0 - All expected results found
  1 - Timeout reached
  2 - Neither fswatch nor inotifywait available
Output (stdout):
  RESULT_FOUND: result-task-{id}.md (1/5)
  RESULT_FOUND: result-task-{id}.md (2/5)
  ALL_DONE
Environment:
  WATCH_TIMEOUT - Timeout in seconds (default: 2700 = 45 min)
```

#### poll-for-results.sh (Modified)

```
Usage: poll-for-results.sh <session_dir> <expected_count> [task_ids...]
Exit codes:
  0 - All expected results found
  1 - Timeout reached
Output (stdout): Same as watch-for-results.sh
Environment:
  POLL_START_INTERVAL - Starting interval in seconds (default: 5)
  POLL_MAX_INTERVAL - Maximum interval in seconds (default: 30)
  POLL_TIMEOUT - Cumulative timeout in seconds (default: 2700)
Behavior:
  - Start at POLL_START_INTERVAL
  - Increase by 5s after each poll with no new results
  - Reset to POLL_START_INTERVAL when a new result is found
  - Cap at POLL_MAX_INTERVAL
```

### 7.6 Codebase Context

#### Existing Architecture
The execute-tasks skill is in `claude/sdd-tools/` and consists of a skill definition, 3 reference files, 1 agent definition, 1 polling script, and 1 auto-approve hook. Total: ~1,917 lines of markdown + 136 lines of shell.

#### Integration Points
| File/Module | Purpose | How This Feature Connects |
|------------|---------|---------------------------|
| `claude/sdd-tools/skills/execute-tasks/SKILL.md` | Top-level 10-step orchestration workflow | Modified to add conflict detection, progress streaming, retry escalation, prompt injection |
| `claude/sdd-tools/references/orchestration.md` | Detailed orchestrator procedures | Modified for structured context merge, conflict detection, retry logic |
| `claude/sdd-tools/references/execution-workflow.md` | 4-phase task execution for agents | Modified for structured context writing |
| `claude/sdd-tools/agents/task-executor.md` | Agent executing single tasks | Modified to embed rules and structured context |
| `claude/sdd-tools/scripts/poll-for-results.sh` | Polling for result files | Modified for adaptive intervals |
| `claude/sdd-tools/hooks/hooks.json` | Hook registration | Modified to add validate-result hook |
| `claude/sdd-tools/hooks/auto-approve-session.sh` | Auto-approve session writes | No change (model for new hooks) |
| `claude/sdd-tools/skills/create-tasks/SKILL.md` | Task generation from specs | Must emit `produces_for` field in task JSON |

#### Patterns to Follow
- **Defensive hook design**: Never exit non-zero, trap on ERR, debug logging via env var — established by `auto-approve-session.sh`
- **File-based coordination**: All inter-agent communication via files in session directory — established pattern
- **Compact result files**: ~18 lines, standardized format — established by result file protocol

#### Key Dependencies
- `create-tasks` skill must be updated to emit `produces_for` field (clean break, new task JSON format)
- `execute-tdd-tasks` shares `poll-for-results.sh` — changes must not break TDD variant (or TDD variant must be updated separately)

### 7.7 Technical Constraints

| Constraint | Impact | Mitigation |
|------------|--------|------------|
| AI instruction-following for structured context | Agents may not populate sections correctly | PostToolUse hook could validate context file format too |
| `fswatch`/`inotifywait` not universally available | Some environments lose zero-latency detection | Adaptive polling fallback ensures functionality |
| Agent definition size after embedding | ~425 lines may affect model attention | Keep embedded rules concise and action-oriented |
| Clean break on task JSON | Existing task JSONs incompatible | `create-tasks` regeneration required before execution |
| Shared scripts with TDD variant | Modifying poll-for-results.sh may break execute-tdd-tasks | Test with both variants; TDD update is separate spec |

## 8. Scope Definition

### 8.1 In Scope
- All 10 recommendations from the deep analysis report
- Modifications to: SKILL.md, orchestration.md, execution-workflow.md, task-executor.md, poll-for-results.sh, hooks.json
- New files: validate-result.sh, watch-for-results.sh
- Shell script unit tests (bats) for new and modified scripts
- Update to create-tasks for `produces_for` field emission

### 8.2 Out of Scope
- **execute-tdd-tasks updates**: Separate spec — though shared script changes are considered for compatibility
- **Backward compatibility**: Clean break — old task JSONs need regeneration
- **Hierarchical orchestration**: For 100+ task sessions — future consideration
- **Per-task real-time streaming**: Wave-level granularity is sufficient
- **Context file hook validation**: Only result files are validated by hook; context files are trusted
- **create-tasks prompt injection metadata**: The `produces_for` field emission logic in create-tasks is in scope, but a full create-tasks redesign is not

### 8.3 Future Considerations
- Update execute-tdd-tasks to use new infrastructure (filesystem watching, structured context, adaptive polling)
- Hierarchical orchestration for large (50+ task) sessions
- Per-task real-time progress streaming (leverage fswatch for individual task updates)
- Context file validation hook (extend validate-result.sh pattern)
- Task-level file locking for concurrent edit protection beyond description-based detection

## 9. Implementation Plan

### 9.1 Phase 1: Foundation

**Completion Criteria**: Structured context schema is operational and agent definition is streamlined.

| Deliverable | Description | Technical Tasks | Dependencies |
|-------------|-------------|-----------------|--------------|
| Structured context schema | Define 6-section template for execution_context.md and context-task-{id}.md | Update orchestration.md with merge procedures; create initial template | None |
| Embedded agent rules | Distill essential rules from execution-workflow.md and verification-patterns.md into task-executor.md | Identify critical rules; embed in agent body; remove explicit Read instructions | None |
| Updated execution workflow | Modify execution-workflow.md to reference structured context and embedded rules | Update Phase 1 (context reading) and Phase 4 (context writing) procedures | Structured context schema |

**Checkpoint Gate**:
- [ ] task-executor.md contains embedded verification rules (~425 lines)
- [ ] execution_context.md template with 6 sections is defined
- [ ] Agent no longer reads reference files explicitly

---

### 9.2 Phase 2: Enforcement

**Completion Criteria**: Programmatic validation and event-driven completion are operational.

| Deliverable | Description | Technical Tasks | Dependencies |
|-------------|-------------|-----------------|--------------|
| Result validation hook | `validate-result.sh` PostToolUse hook | Write hook script; register in hooks.json; add defensive patterns | Phase 1 (knows result file format) |
| Filesystem watch script | `watch-for-results.sh` with fswatch/inotifywait support | Write script; add tool detection; implement timeout | None |
| Adaptive polling | Modify `poll-for-results.sh` for progressive intervals | Add interval logic; add environment variable support | None |
| Orchestrator integration | Update orchestration.md to use watch → poll fallback | Add fallback logic; update completion detection procedures | Watch script, adaptive polling |
| Shell script tests | bats tests for validate-result.sh, watch-for-results.sh, poll-for-results.sh | Write test fixtures; test happy path, edge cases, error handling | All scripts |

**Checkpoint Gate**:
- [ ] validate-result.sh catches malformed result files
- [ ] watch-for-results.sh detects result files within 1 second
- [ ] poll-for-results.sh adaptive intervals work correctly
- [ ] Fallback from fswatch to polling works when tools unavailable
- [ ] All shell script tests pass

---

### 9.3 Phase 3: Intelligence

**Completion Criteria**: Conflict detection, prompt injection, and retry escalation are operational.

| Deliverable | Description | Technical Tasks | Dependencies |
|-------------|-------------|-----------------|--------------|
| File conflict detection | Pre-wave scan and wave adjustment | Add conflict scanning logic to orchestration.md; define file path detection patterns | Phase 1 (wave planning exists) |
| Prompt injection | `produces_for` field and result injection | Extend task JSON schema; add injection logic to orchestration.md; update create-tasks skill | Phase 2 (result files are validated) |
| Retry escalation | 3-tier retry strategy | Add escalation logic to orchestration.md; add AskUserQuestion for user escalation | Phase 1 (context enrichment depends on structured context) |
| create-tasks update | Emit `produces_for` field | Update create-tasks SKILL.md to detect and emit producer-consumer relationships | None |

**Checkpoint Gate**:
- [ ] File conflicts detected and tasks rearranged across waves
- [ ] Producer task results injected into dependent task prompts
- [ ] Retry escalation reaches user after 2 automated retries
- [ ] create-tasks emits `produces_for` for identified relationships

---

### 9.4 Phase 4: Polish

**Completion Criteria**: Progress streaming and merge validation are operational. Full pipeline tested end-to-end.

| Deliverable | Description | Technical Tasks | Dependencies |
|-------------|-------------|-----------------|--------------|
| Progress streaming | Wave completion summaries to user | Add summary output logic to orchestration.md between waves | Phase 2 (result processing) |
| Post-wave merge validation | Validate execution_context.md after merge | Add validation step; auto-repair for missing headers; forced compaction at size limits | Phase 1 (structured context schema) |
| End-to-end validation | Run a test execution session with all features | Execute a real task set; verify all 10 features work together | All phases |
| Documentation update | Update CLAUDE.md and session directory layout docs | Document new files, hooks, scripts, and structured context format | All phases |

**Checkpoint Gate**:
- [ ] Wave completion summaries visible to user during execution
- [ ] Post-merge validation catches malformed context
- [ ] End-to-end execution session completes with all features active
- [ ] Documentation reflects all changes

## 10. Testing Strategy

### 10.1 Test Levels

| Level | Scope | Tools | Coverage Target |
|-------|-------|-------|-----------------|
| Unit (shell) | Individual shell scripts | bats (Bash Automated Testing System) | All scripts: validate-result.sh, watch-for-results.sh, poll-for-results.sh |

### 10.2 Shell Script Test Scenarios

#### validate-result.sh Tests
| Test | Input | Expected Result |
|------|-------|-----------------|
| Valid PASS result | Well-formed result file with status: PASS | No action (file preserved) |
| Valid FAIL result | Well-formed result file with status: FAIL | No action (file preserved) |
| Missing status line | Result file without first-line status | File renamed to .invalid |
| Invalid status value | status: UNKNOWN | File renamed to .invalid |
| Missing required section | No "## Summary" section | File renamed to .invalid |
| Missing context file | result-task-5.md without context-task-5.md | Stub context created, result accepted |
| Non-session file | Write to unrelated path | Hook ignores (no action) |
| Hook error | Malformed input | Trap catches, exit 0 |

#### watch-for-results.sh Tests
| Test | Input | Expected Result |
|------|-------|-----------------|
| All results found | Create N result files | ALL_DONE output |
| Timeout | No files created within timeout | Exit code 1 |
| No fswatch available | fswatch not in PATH | Exit code 2 |
| Pre-existing results | Result files created before watch starts | Detected and counted |
| Partial completion | Some results found, timeout for rest | Reports found results, exits code 1 |

#### poll-for-results.sh Tests
| Test | Input | Expected Result |
|------|-------|-----------------|
| Adaptive interval increase | No results over time | Intervals: 5s, 10s, 15s, 20s, 25s, 30s |
| Interval reset on result | New result during polling | Interval resets to 5s |
| Max interval cap | Long polling without results | Never exceeds 30s |
| Environment variable override | POLL_START_INTERVAL=10 | Starts at 10s |
| Timeout | No results within cumulative timeout | Exit code 1 |

### 10.3 Integration Validation

End-to-end validation with a real execution session:
1. Generate tasks from an existing spec using `/create-tasks` (with `produces_for` field)
2. Run `/execute-tasks` with all hardening features active
3. Verify: conflict detection logged, result files validated by hook, fswatch used, wave summaries displayed, structured context merged, retry escalation triggered (via intentionally failing task if needed)

## 11. Dependencies

### 11.1 Technical Dependencies

| Dependency | Status | Risk if Delayed |
|------------|--------|-----------------|
| `fswatch` (macOS) or `inotifywait` (Linux) | Optional (fallback to polling) | Low — polling works without it |
| `bats` testing framework | Required for shell tests | Low — installable via Homebrew/apt |
| `/create-tasks` update for `produces_for` | Required for Rec #5 | Medium — prompt injection won't work without it |

### 11.2 Cross-Skill Dependencies

| Skill | Dependency | Impact |
|-------|------------|--------|
| `create-tasks` (sdd-tools) | Must emit `produces_for` field | Required for Phase 3 prompt injection |
| `execute-tdd-tasks` (tdd-tools) | Shares `poll-for-results.sh` | Separate spec; test for compatibility |

## 12. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation Strategy |
|------|--------|------------|---------------------|
| Hook complexity — validation hook bug breaks autonomous execution | High | Low | Defensive design: never exit non-zero, trap on ERR, extensive bats tests |
| fswatch availability — not all environments have it | Medium | Medium | Adaptive polling fallback is always available |
| Agent definition bloat — ~425 lines affects model attention | Medium | Low | Keep embedded rules concise; measure token usage before/after |
| TDD variant scope creep — shared script changes break execute-tdd-tasks | Medium | Medium | Test with both variants; pin poll-for-results.sh interface |
| Structured context compliance — agents don't follow schema | Medium | Medium | Clear section headers with instructions; consider context validation hook in future |
| Conflict detection false negatives — agents edit files not in descriptions | Low | High | Known limitation of description-based approach; documented as future enhancement |

## 13. Open Questions

| # | Question | Resolution |
|---|----------|------------|
| — | All questions resolved during interview | — |

## 14. Appendix

### 14.1 Glossary

| Term | Definition |
|------|------------|
| Wave | A group of tasks with no unresolved dependencies, executed in parallel |
| Result file | Compact (~18 line) markdown file written by task-executor as completion signal |
| Context file | Per-task markdown file containing learnings for downstream tasks |
| Execution context | Shared markdown file merging all task learnings across waves |
| Prompt injection | Inserting producer task output directly into dependent task prompts |
| Topological sort | Algorithm for ordering tasks by dependencies into parallelizable waves |

### 14.2 References

- Deep Analysis Report: `internal/reports/execute-tasks-deep-analysis-2026-02-22.md`
- Current execute-tasks skill: `claude/sdd-tools/skills/execute-tasks/`
- execute-tdd-tasks skill (comparison): `claude/tdd-tools/skills/execute-tdd-tasks/`
- Existing hook model: `claude/sdd-tools/hooks/auto-approve-session.sh`
- bats testing framework: https://github.com/bats-core/bats-core

### 14.3 Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-22 | Stephen Sequenzia | Initial version |

---

*Document generated by SDD Tools*
