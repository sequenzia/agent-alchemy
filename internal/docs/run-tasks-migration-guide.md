# Migration Guide: execute-tasks to run-tasks

This guide documents the transition from the old `/execute-tasks` engine to the new `/run-tasks` engine in the SDD pipeline.

---

## 1. Overview

### What Changed

The execution engine has been rewritten from the ground up. The core change is a shift from **file-based signaling** to **message-based coordination via Agent Teams**.

| Aspect | Old (execute-tasks) | New (run-tasks) |
|--------|---------------------|-----------------|
| Agent coordination | Background agents + file polling (`result-task-{id}.md`, `context-task-{id}.md`) | Native Agent Teams (`TeamCreate`, `SendMessage`, `TaskOutput`) |
| Completion detection | Shell scripts (`watch-for-results.sh`, `poll-for-results.sh`) | Message-based — wave-lead collects results via `SendMessage` |
| Context sharing | Per-task files merged into 6-section schema with deduplication/compaction | Context Manager agent distributes and collects via messages; wave-grouped format |
| Agent hierarchy | Flat — orchestrator spawns N executors directly | 3-tier — Orchestrator -> Wave Lead -> Context Manager + Executors |
| Orchestration | 10-step loop (~1,235 lines) | 7-step loop (~950 lines) |

### Why

1. **Reliability**: File-based signaling via `fswatch`/`inotifywait` missed events, delivered duplicates, and had platform-specific inconsistencies — causing silent hangs and partial wave completion. Message-based coordination eliminates these failure modes entirely.
2. **Simplicity**: The old engine required shell scripts (248 lines combined), a PostToolUse validation hook, and a 6-section context merge pipeline with compaction and deduplication. The new engine replaces all of this with native Claude Code primitives.
3. **Resilience**: The new engine has built-in wave-lead crash recovery (auto-restart on first crash, user escalation on second), per-task timeouts based on complexity, and rate limit backoff. The old engine relied on `TaskOutput` timeouts and manual `TaskStop` calls.

### Coexistence

Both engines are available during the transition period:

- **`/execute-tasks`** — The existing engine, unchanged. Continues to work as before.
- **`/run-tasks`** — The new engine. Use this for new executions going forward.

The old engine will be removed after the new engine has been validated across 10+ stable multi-wave sessions.

---

## 2. CLI Changes

| Old (`/execute-tasks`) | New (`/run-tasks`) | Notes |
|------------------------|--------------------|-------|
| `/execute-tasks` | `/run-tasks` | New skill name |
| `--max-parallel N` | Configured in settings | Moved to `run-tasks.max_parallel` in `.claude/agent-alchemy.local.md`. No CLI override. |
| `--retries N` | Configured in settings | Moved to `run-tasks.max_retries` in `.claude/agent-alchemy.local.md`. Default changed from 3 to 1 per tier. |
| `--task-group <name>` | `--task-group <name>` | Unchanged |
| `--phase <N,M>` | `--phase <N,M>` | Unchanged |
| `<task-id>` (positional) | _(removed)_ | Single-task execution removed; use filters instead |
| _(not available)_ | `--dry-run` | **New** — validates the full plan (load, filter, sort, wave assignment) without spawning agents or creating a session |

### Example Mapping

```
# Old                                          # New
/execute-tasks                                  /run-tasks
/execute-tasks --task-group auth                /run-tasks --task-group auth
/execute-tasks --phase 1,2                      /run-tasks --phase 1,2
/execute-tasks --task-group auth --phase 2      /run-tasks --task-group auth --phase 2
/execute-tasks --max-parallel 3 --retries 1     /run-tasks  (configure in settings file)
/execute-tasks 5                                (no equivalent — use --task-group or --phase to narrow scope)

# New features (no old equivalent)
/run-tasks --dry-run
/run-tasks --task-group payments --dry-run
/run-tasks --phase 2 --dry-run
```

---

## 3. Architecture Changes

### Before: execute-tasks

```
Orchestrator (10-step loop, ~1,235 lines)
  |
  |-- Step 1-6: Load, validate, plan, settings, init session, confirm
  |-- Step 7: Launch background agents (Task with run_in_background: true)
  |     |
  |     |-- watch-for-results.sh (fswatch/inotifywait, 116 lines)
  |     |-- poll-for-results.sh (adaptive 5s-30s polling fallback, 134 lines)
  |     |-- Each agent writes result-task-{id}.md + context-task-{id}.md
  |     |
  |     |-- Orchestrator reads result files, calls TaskOutput to reap agents
  |     |-- 6-section context merge (parse, deduplicate, compact at 10+ entries)
  |     |-- 3-tier retry (Standard -> Context Enrichment -> User Escalation)
  |     |
  |-- Step 8: Execute loop (waves)
  |-- Step 9-10: Session summary, CLAUDE.md update
```

Key characteristics:
- Orchestrator manages everything directly in the user's context window
- Agents are independent background processes with no direct communication
- File system is the sole coordination mechanism
- Shell scripts handle completion detection with platform-specific tool dependencies

### After: run-tasks

```
Orchestrator (7-step loop, ~950 lines)
  |
  |-- Steps 1-3: Load & validate, configure & plan, confirm
  |-- Step 4: Initialize session
  |-- Step 5: Per wave:
  |     |
  |     |-- TeamCreate (wave-lead + context-manager + N executors)
  |     |-- Wave Lead (foreground Task, Opus)
  |     |     |
  |     |     |-- SendMessage: WAVE ASSIGNMENT to wave-lead
  |     |     |-- Wave-lead spawns context-manager + executors via SendMessage
  |     |     |-- Context Manager distributes session context to each executor
  |     |     |-- Executors implement tasks, send TASK RESULT + CONTEXT CONTRIBUTION
  |     |     |-- Context Manager collects contributions, writes execution_context.md
  |     |     |-- Wave-lead handles Tier 1/2 retries internally
  |     |     |-- Wave-lead sends WAVE SUMMARY back to orchestrator
  |     |     |
  |     |-- TeamDelete
  |     |-- Orchestrator handles Tier 3 escalation if needed
  |     |
  |-- Steps 6-7: Summarize & archive, finalize (CLAUDE.md update)
```

Key characteristics:
- Wave-lead manages executor coordination, freeing the orchestrator
- All communication via `SendMessage` — no file watchers, no shell scripts
- Context Manager handles knowledge distribution and collection as a dedicated agent
- Wave-lead runs as a foreground Task (orchestrator blocks until wave completes)
- Each wave is a self-contained team that is created and deleted per wave

---

## 4. Session Directory Changes

The session directory remains at `.claude/sessions/__live_session__/` during execution and is archived to `.claude/sessions/{session-id}/` upon completion.

### Removed

| File/Directory | Old Purpose | Why Removed |
|----------------|-------------|-------------|
| `.lock` | Concurrency guard (prevent parallel sessions) | Single-session enforced via `__live_session__/` content detection + user prompt |
| `context-task-{id}.md` | Per-task context isolation (written by each executor) | Context Manager collects contributions via `SendMessage` |
| `result-task-{id}.md` | Completion signal + compact result (polled by orchestrator) | Wave-lead receives `TASK RESULT` messages directly from executors |
| `progress.md` | Human-readable progress tracking (markdown format) | Replaced by `progress.jsonl` (structured events) |
| `tasks/` | Subdirectory for archiving completed task JSON files | Archival handled differently |

### Added

| File | Purpose |
|------|---------|
| `progress.jsonl` | Structured event log with JSONL entries: `session_start`, `wave_start`, `task_start`, `task_complete`, `wave_complete`, `session_complete`. Machine-parseable for dashboards and tooling. |

### Changed

| File | Old Format | New Format |
|------|-----------|------------|
| `execution_context.md` | 6-section schema (Project Patterns, Key Decisions, Known Issues, File Map, Task History) with deduplication and compaction | Wave-grouped format — each wave's learnings appended as a section. No deduplication/compaction pipeline. |
| `session_summary.md` | Generated at Step 9 | Generated at Step 6 with updated metrics format |
| `task_log.md` | Table with columns: Task ID, Subject, Status, Attempts, Duration, Token Usage | Same purpose, format updated to match new engine metrics |

### Unchanged

| File | Purpose |
|------|---------|
| `execution_plan.md` | Wave plan showing task-to-wave assignments, priorities, and dependency graph |

---

## 5. Configuration

### Settings Namespace

Configuration has moved from `execute-tasks.*` to `run-tasks.*` in `.claude/agent-alchemy.local.md`.

### Setting Migration

| Old Setting | New Setting | Default | Notes |
|-------------|-------------|---------|-------|
| `execute-tasks.max_parallel` | `run-tasks.max_parallel` | `5` | Same purpose: max concurrent executors per wave |
| _(CLI `--retries N`)_ | `run-tasks.max_retries` | `1` | **New** — autonomous retries per tier before escalation. Old default was 3 total attempts via CLI. |
| _(not configurable)_ | `run-tasks.wave_lead_model` | `opus` | **New** — model tier for wave-lead agents |
| _(not configurable)_ | `run-tasks.context_manager_model` | `sonnet` | **New** — model tier for context manager agents |
| _(not configurable)_ | `run-tasks.executor_model` | `opus` | **New** — model tier for task executor agents |

### Example Settings File

```yaml
# .claude/agent-alchemy.local.md (YAML frontmatter section)
---
run-tasks.max_parallel: 3
run-tasks.max_retries: 2
run-tasks.wave_lead_model: opus
run-tasks.context_manager_model: sonnet
run-tasks.executor_model: opus
---
```

### Key Differences

- **No CLI override for retries**: The old `--retries N` CLI argument is gone. Configure `run-tasks.max_retries` in the settings file instead.
- **No CLI override for max-parallel**: The old `--max-parallel N` CLI argument is gone. Configure `run-tasks.max_parallel` in the settings file instead.
- **Model selection**: All three agent tiers (wave-lead, context-manager, executor) have independently configurable model tiers. This allows cost optimization (e.g., Sonnet for context managers, Opus for executors).
- **Missing settings are not errors**: If the settings file is missing or partially configured, defaults are used silently.

---

## 6. When to Switch

### Recommended Transition Path

1. **Start with dry-run**: Run `/run-tasks --dry-run` on an existing task set to verify plan generation works correctly. Compare the wave assignments against what `/execute-tasks` would produce.

2. **Small specs first**: Begin with small specs (1-2 waves, 3-5 tasks) before attempting complex multi-wave executions. This validates the full lifecycle: team creation, executor coordination, context flow, and session archival.

3. **Compare results**: For your first few runs, compare the output quality and session artifacts against what the old engine produced. The new engine should produce equivalent code quality with better reliability.

4. **Gradually increase complexity**: Move to multi-wave specs (3+ waves) and specs with complex dependency chains once single-wave executions are stable.

5. **Monitor for issues**: Pay attention to:
   - Wave-lead crash recovery behavior
   - Context quality from the Context Manager
   - Per-task timeout handling
   - Rate limit backoff during large waves

### Fallback

The old engine remains fully functional at `/execute-tasks` throughout the transition. If you encounter issues with `/run-tasks`, switch back to `/execute-tasks` for that session and report the issue.

### Retirement Criteria

The old `/execute-tasks` engine will be removed when:

- 10+ stable multi-wave sessions have completed successfully with `/run-tasks`
- No regressions in code quality or task pass rates compared to the old engine
- Wave-lead crash recovery has been validated in at least one real session
- Context flow between waves produces equivalent or better learnings

### What Stays the Same

Regardless of which engine you use:

- **Task format**: Tasks produced by `/create-tasks` work with both engines. No task modifications needed.
- **Spec format**: Specs produced by `/create-spec` are engine-agnostic.
- **Verification logic**: The 4-phase task executor workflow (Understand, Implement, Verify, Complete) and acceptance criteria evaluation are the same in both engines.
- **CLAUDE.md updates**: Both engines review execution context and update CLAUDE.md when meaningful project-wide changes occur.
