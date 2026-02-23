# Execution Workflow Reference

> **Documentation-only**: This file documents the 4-phase task execution workflow for reference purposes. Task-executor agents no longer load this file at startup -- essential rules are embedded directly in `task-executor.md`. This file is retained for onboarding, debugging, and spec traceability.

This reference provides the detailed 4-phase workflow for executing a single Claude Code Task. Each phase has specific procedures depending on whether the task is spec-generated or a general task.

## Phase 1: Understand

Load context and understand the task scope before writing any code.

### Step 1: Read Execution Context

Check for shared execution context from prior tasks in this session:
```
Read: .claude/sessions/__live_session__/execution_context.md
```

The execution context uses a structured 6-section schema. If the file exists, review each section:

| Section | What to Look For |
|---------|-----------------|
| `## Project Setup` | Package manager, runtime, frameworks, build tools |
| `## File Patterns` | Test file patterns, component patterns, API route patterns |
| `## Conventions` | Import style, error handling, state management, naming |
| `## Key Decisions` | Architecture choices made by earlier tasks |
| `## Known Issues` | Problems to avoid, workarounds in place |
| `## Task History` | What earlier tasks accomplished and any issues encountered |

Use this context to inform your approach. If the file does not exist, proceed without it.

#### Context Size Management

If `execution_context.md` has grown large:

- **200+ lines**: Read top sections in full (Project Setup through Known Issues). Keep the last 5 Task History entries in full. Summarize older Task History entries into a brief paragraph.
- **500+ lines**: Read top sections in full (Project Setup through Known Issues). Read only the last 5 Task History entries. Skip older Task History entries entirely.

#### Retry Context Check

If this is a retry attempt:

1. Check Task History in `execution_context.md` for the previous attempt's learnings
2. Assess the current codebase state: run linter and tests to understand what the previous attempt left behind
3. Decide approach: build on the previous attempt's partial work, or revert and try a different strategy

### Step 2: Read Upstream Task Output

If `## UPSTREAM TASK OUTPUT` blocks are present in the agent prompt, these contain result data from producer tasks (via `produces_for`). Read them for:
- Files created or modified by upstream tasks
- Key decisions or conventions established upstream
- Context that informs the implementation approach

Multiple upstream blocks appear in task ID order. If an upstream block shows `## UPSTREAM TASK #{id} FAILED`, note the failure and work around missing dependencies.

### Step 3: Load Task Details

Use `TaskGet` to retrieve the full task details including:
- Subject and description
- Metadata (priority, complexity, source_section, spec_path, feature_name, task_group)
- Dependencies (blockedBy, blocks)

### Step 4: Classify Task

Determine whether this is a spec-generated task or a general task:

1. Check for `**Acceptance Criteria:**` in the description
2. Check for `metadata.spec_path` field
3. Check for `Source:` reference in the description

If any of the above are present, classify as **spec-generated**. Otherwise, classify as **general**.

### Step 5: Parse Requirements

**For spec-generated tasks:**
- Extract each acceptance criterion by category (Functional, Edge Cases, Error Handling, Performance)
- Each `- [ ]` line under a category header is one criterion
- Extract Testing Requirements section
- Note the source spec section for context
- Read the source spec section if referenced for additional context

**For general tasks:**
- Parse the subject line for intent: "Fix X" = bug fix, "Add X" = new feature, "Refactor X" = restructuring, "Update X" = modification
- Extract implicit criteria from description:
  - "should..." / "must..." -> functional requirements
  - "when..." -> scenarios to test
  - "can..." -> capabilities to confirm
  - "handle..." -> error scenarios to check
- Infer completion criteria from the description

### Step 6: Explore Codebase

Understand the affected code before making changes:

1. Read `CLAUDE.md` for project conventions, tech stack, and coding standards
2. Use `Glob` to find files matching the task scope (e.g., `**/*user*.ts` for a user-related task)
3. Use `Grep` to search for related symbols, functions, or patterns
4. Read the key files that will be modified
5. Identify test file locations and patterns

### Step 7: Plan Implementation

Before proceeding to implementation, have a clear plan:
- Which files to create or modify
- What the expected behavior change is
- What tests to write or update
- What project conventions to follow

---

## Phase 2: Implement

Do NOT update `progress.md` -- the orchestrator manages progress tracking.

Execute the implementation following project patterns and best practices.

### Pre-Implementation Reads

Always read target files before modifying them:
- Read every file you plan to edit (never edit blind)
- Read related test files to understand test patterns
- Read adjacent files for consistency (same directory, same module)

### Implementation Order

Follow a dependency-aware implementation order:

```
1. Data layer (models, schemas, types)
2. Service layer (business logic, utilities)
3. API/Interface layer (endpoints, handlers, UI)
4. Test layer (unit tests, integration tests)
5. Configuration (env vars, config files)
```

### Coding Standards

Apply these standards during implementation:

- **Follow existing patterns**: Match the coding style, naming conventions, and patterns already in the codebase
- **Read CLAUDE.md conventions**: Apply any project-specific rules
- **Minimal changes**: Only modify what the task requires; do not refactor surrounding code
- **Self-documenting code**: Use clear naming; add comments only when the "why" isn't obvious
- **Error handling**: Handle errors at appropriate boundaries, not everywhere
- **Type safety**: Follow the project's type conventions (TypeScript strict mode, Python type hints, etc.)

### Mid-Implementation Checks

After completing the core implementation (before tests):
1. Run any existing linter (`npm run lint`, `ruff check`, etc.) to catch style issues early
2. Run existing tests to make sure nothing is broken (`npm test`, `pytest`, etc.)
3. Fix any issues before proceeding to write new tests

### Test Writing

If the task specifies testing requirements or the project has test patterns:

1. Follow the existing test framework and patterns
2. Write tests for the behavior specified in acceptance criteria
3. Test edge cases listed in the acceptance criteria
4. Ensure tests are independent and can run in any order
5. Use descriptive test names that explain the expected behavior

---

## Phase 3: Verify

Do NOT update `progress.md` -- the orchestrator manages progress tracking.

Verify the implementation against task requirements. The verification approach is adaptive based on task classification.

### Spec-Generated Task Verification

Walk through each acceptance criteria category systematically:

**Functional** (ALL must pass -- any failure means FAIL):
- For each criterion, locate the code that satisfies it
- Verify correctness by reading the code
- Run relevant tests that exercise the behavior
- Record PASS/FAIL per criterion

**Edge Cases** (flagged but don't block -- failures mean PARTIAL):
- Check guard clauses, boundary checks, null guards, validation
- Find tests that exercise the edge case
- Verify the edge case produces correct results
- Record PASS/FAIL/SKIP per criterion

**Error Handling** (flagged but don't block -- failures mean PARTIAL):
- Check error paths (try/catch, error returns, validation errors)
- Verify error messages are clear and informative
- Confirm the system recovers gracefully
- Record PASS/FAIL per criterion

**Performance** (flagged but don't block -- failures mean PARTIAL):
- Check that the implementation uses an efficient approach
- Look for obvious issues: N+1 queries, unbounded loops, missing indexes
- Run benchmarks if test infrastructure supports it
- Record PASS/FAIL per criterion

**Testing Requirements:**
- Parse the `**Testing Requirements:**` section from description
- For each test requirement, find or create the corresponding test
- Run full test suite; verify all tests pass; check for regressions

### General Task Verification

For tasks without structured acceptance criteria:

1. **Infer "done" from description**: What does success look like based on the task subject and description?
2. **Run existing tests**: Ensure no regressions
3. **Run linter**: Check code quality
4. **Verify core change**: Confirm the primary change works as intended
5. **Spot check**: Read through the changes and verify they make sense

### Pass Threshold Rules

**Spec-generated tasks:**

| Category | Requirement | Failure Impact |
|----------|-------------|----------------|
| Functional | ALL must pass | Any failure -> FAIL |
| Edge Cases | Flagged, don't block | PARTIAL if Functional passes |
| Error Handling | Flagged, don't block | PARTIAL if Functional passes |
| Performance | Flagged, don't block | PARTIAL if Functional passes |
| Tests | ALL must pass | Any failure -> FAIL |

**General tasks:**

| Check | Requirement | Failure Impact |
|-------|-------------|----------------|
| Core change | Must be implemented | Missing -> FAIL |
| Tests pass | Existing tests must pass | Test failure -> FAIL |
| Linter | No new violations | New violations -> PARTIAL |
| No regressions | Nothing else broken | Regression -> FAIL |

**Status determination:**

| Condition | Status |
|-----------|--------|
| All Functional pass + Tests pass | **PASS** |
| All Functional pass + Tests pass + Edge/Error/Perf issues | **PARTIAL** |
| Any Functional fail | **FAIL** |
| Any test failure | **FAIL** |
| Core change missing (general task) | **FAIL** |

---

## Phase 4: Complete

Report results and update task status.

### Determine Status

Based on verification results:

| Result | Status | Action |
|--------|--------|--------|
| All Functional criteria pass, tests pass | **PASS** | Mark task as `completed` |
| Some Edge/Error/Performance criteria fail but Functional passes | **PARTIAL** | Leave as `in_progress`, report what failed |
| Any Functional criteria fail, or tests fail | **FAIL** | Leave as `in_progress`, report failures |

### Update Task Status

**If PASS:**
```
TaskUpdate: taskId={id}, status=completed
```

**If PARTIAL or FAIL:**
Leave task as `in_progress`. Do NOT mark as completed. The orchestrating skill will decide whether to retry.

### Write Context File

Write structured learnings to your per-task context file at the `Context Write Path` specified in the agent prompt (e.g., `.claude/sessions/__live_session__/context-task-{id}.md`). Do NOT write to `execution_context.md` directly -- the orchestrator merges per-task files after each wave.

Use the 6-section structured context schema. Only include sections where there is content to contribute -- omit empty sections:

```markdown
## Project Setup
- {discovery about package manager, runtime, frameworks, build tools}

## File Patterns
- {discovered test file patterns, component patterns, API route patterns}

## Conventions
- {discovered import style, error handling, state management, naming}

## Key Decisions
- [Task #{id}] {decision made and rationale}

## Known Issues
- {issues encountered, workarounds applied}
```

**Entry format conventions**:
- Each entry is a single bullet point (`- `) on one line
- Key Decisions entries start with `[Task #{id}]` to attribute the decision
- Entries should be factual and concise (one line per entry)

**Note**: Task History is managed by the orchestrator from result files. Do not include a Task History section in the context file.

#### Error Resilience

If the write to the per-task context file fails:

1. **Do not crash** -- continue the workflow normally
2. Log a `WARNING: Failed to write learnings to context file` line in the result file Issues section
3. Include the learnings in the result file Issues section as fallback
4. The orchestrator will pick up the fallback learnings from the result file

### Write Result File

As your **VERY LAST action** (after writing the context file), write a compact result file to the `Result Write Path` specified in the agent prompt (e.g., `.claude/sessions/__live_session__/result-task-{id}.md`):

```markdown
status: PASS|PARTIAL|FAIL
task_id: {id}
duration: {Xm Ys}

## Summary
{1-3 sentence summary of what was done}

## Files Modified
- {file path 1} -- {what changed}
- {file path 2} -- {what changed}

## Context Contribution
{Key learnings for downstream tasks: conventions discovered, patterns established, decisions made}

## Verification
{What was checked and the result: criteria counts, test results, issues found}
```

**Ordering**: Context file FIRST, result file LAST. The result file's existence signals completion to the orchestrator.

**Error resilience**: If the result file write fails, fall back to returning the full structured report (see Fallback Report Format below) so the orchestrator can parse it from `TaskOutput`.

### Return Status Line

After writing the result file, return ONLY a single minimal status line:

```
DONE: [{id}] {subject} - {PASS|PARTIAL|FAIL}
```

This keeps the orchestrator's context minimal (~3 lines per background agent launch + ~1 line return).

### Fallback Report Format

Only used when the result file write fails. Return the full report so the orchestrator can parse it from `TaskOutput`:

```
TASK RESULT: {PASS|PARTIAL|FAIL}
Task: [{id}] {subject}

VERIFICATION:
  Functional: {n}/{total} passed
  Edge Cases: {n}/{total} passed
  Error Handling: {n}/{total} passed
  Tests: {passed}/{total} ({failed} failures)

ISSUES:
  - {criterion}: {what went wrong}

FILES MODIFIED:
  - {file path}: {brief description}

CONTEXT CONTRIBUTION:
  - {key learnings for downstream tasks}

{If context file write also failed:}
LEARNINGS:
  ## Project Setup
  - {discoveries}
  ## Conventions
  - {discoveries}
  ## Key Decisions
  - [Task #{id}] {decision}
  ## Known Issues
  - {issues}
```
