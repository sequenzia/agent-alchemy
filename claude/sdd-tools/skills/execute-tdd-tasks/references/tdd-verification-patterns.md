# TDD Verification Patterns Reference

This reference documents TDD-specific verification rules for the `execute-tdd-tasks` skill. It extends the standard `verification-patterns.md` from `execute-tasks` with RED, GREEN, and REFACTOR phase verification, TDD compliance reporting, and TDD-specific failure handling.

---

## Phase Verification Overview

Each TDD phase has explicit PASS, PARTIAL/WARN, and FAIL states. The phase verification rules align with the `tdd-workflow.md` reference in `tdd-tools` but are evaluated from the orchestrator's perspective (the `execute-tdd-tasks` skill reviewing agent results) rather than the agent's internal perspective.

| Phase | PASS | WARN / PARTIAL | FAIL |
|-------|------|----------------|------|
| **RED** | All new tests fail as expected | Some tests pass unexpectedly | Tests cannot be run |
| **GREEN** | All tests pass, zero regressions | New tests pass but regressions exist | New tests still failing |
| **REFACTOR** | All tests green after cleanup | Tests broke, reverted to pre-refactor | Tests broke, cannot recover |

---

## RED Phase Verification

The RED phase verifies that newly written tests fail before any implementation exists. This confirms the tests are genuinely testing new behavior.

### PASS: All New Tests Fail

**Condition**: Every test written in the RED phase fails with an expected error type (ImportError, AttributeError, AssertionError, NameError, ModuleNotFoundError).

**Evidence required**:
- Test runner output showing all new tests as FAILED or ERROR
- Failure reasons are implementation-related (not syntax errors or configuration issues)
- Pre-existing tests are unaffected (same pass/fail counts as baseline)

**Orchestrator action**: Record `red_verified: true` in TDD compliance. Proceed to GREEN phase.

### WARN: Some Tests Pass Unexpectedly

**Condition**: One or more new tests pass before any implementation is written.

**Evidence required**:
- Test runner output identifying which specific tests passed
- Analysis of why they passed (pre-existing implementation, weak test, wrong import)

**Possible causes**:

| Cause | Diagnosis | Response |
|-------|-----------|----------|
| Implementation already exists | Feature was built previously or by another task | Skip to REFACTOR if all tests pass; verify test completeness if partial |
| Test is too weak | Test asserts trivially true conditions | Strengthen the test and re-run RED |
| Wrong import | Test imports existing module instead of new module | Fix import paths and re-run RED |
| Framework default behavior | Framework provides default responses that satisfy test | Make test more specific |

**Orchestrator action by strictness level**:

| Strictness | Action |
|-----------|--------|
| **Strict** | Record `red_verified: false`. Mark task as FAIL. Do not proceed to GREEN |
| **Normal** (default) | Record `red_verified: false` with warning. Log which tests passed and why. Proceed to GREEN |
| **Relaxed** | Record `red_verified: false` (informational). Log results. Proceed to GREEN |

### FAIL: Tests Cannot Be Run

**Condition**: The test runner cannot execute the new tests at all.

**Error types**:

| Error Type | Example | Likely Cause |
|-----------|---------|--------------|
| Syntax error | `SyntaxError: invalid syntax` | Test file has a coding error |
| Missing dependency | `ModuleNotFoundError: No module named 'pytest_asyncio'` | Test requires uninstalled package |
| Configuration error | `ERROR: not found: conftest.py` | Test framework misconfigured |
| Discovery failure | `no tests ran` | Tests not discoverable (wrong naming, wrong directory) |

**Orchestrator action**: Record `red_verified: false`. Mark task as FAIL. Include the specific error in the retry context so the agent can fix the test file.

---

## GREEN Phase Verification

The GREEN phase verifies that the implementation makes all tests pass without breaking existing tests.

### PASS: All Tests Pass, Zero Regressions

**Condition**: The full test suite passes — both new tests from the RED phase and all previously-passing tests.

**Evidence required**:
- Test runner output showing all tests PASSED
- New test count matches the count from the RED phase (no tests were removed)
- Pre-existing test results match or exceed the baseline (no regressions)
- No skipped tests that were previously running

**Orchestrator action**: Record `green_verified: true`. Proceed to REFACTOR phase.

### PARTIAL: New Tests Pass but Existing Tests Regressed

**Condition**: All new tests pass, but one or more previously-passing tests now fail.

**Evidence required**:
- Test runner output showing failures
- Cross-reference with Phase 1 baseline to identify regressions
- Regressions are in tests that were PASSING before implementation

**Orchestrator action**: Record `green_verified: false`. The agent should attempt to fix the regressions:

1. Identify the regressing tests and their failure messages
2. Determine if the regression is caused by the new implementation
3. Fix the implementation to resolve regressions without breaking new tests
4. Re-run the full suite

If the agent cannot resolve regressions after iteration, mark as FAIL with regression details.

### FAIL: New Tests Still Failing

**Condition**: After implementation, one or more new tests from the RED phase still fail.

**Evidence required**:
- Test runner output showing specific failures
- Which new tests fail and with what errors
- Confirmation that the implementation was attempted (code was written)

**Failure subtypes**:

| Subtype | Description | Recommendation |
|---------|-------------|----------------|
| Partial implementation | Some tests pass, others fail | Continue implementing; retry with focus on failing tests |
| Wrong approach | Implementation does not satisfy test expectations | Re-read test assertions and try a different implementation strategy |
| Contradictory tests | Two tests expect mutually exclusive behavior | Report as FAIL — tests may need review (but agent must NOT modify tests) |
| Missing infrastructure | Tests depend on database, service, or fixture not available | Report as FAIL with infrastructure requirements |

**Orchestrator action**: Record `green_verified: false`. Mark task as FAIL. Include failing test names and error messages in retry context.

---

## REFACTOR Phase Verification

The REFACTOR phase verifies that code cleanup does not break any tests.

### PASS: All Tests Green After Cleanup

**Condition**: Refactoring was performed and all tests still pass afterward.

**Evidence required**:
- Test runner output showing all tests PASSED after refactoring
- Test count is unchanged (no tests were added or removed during refactoring)
- Code changes are structural only (naming, extraction, simplification) — no behavior changes

**Orchestrator action**: Record `refactored: true`. Mark task as PASS (full TDD cycle complete).

### PARTIAL: Tests Broke, Reverted to Pre-Refactor State

**Condition**: A refactoring change broke one or more tests. The agent reverted the change and all tests pass again in the pre-refactor state.

**Evidence required**:
- Test failure during refactoring (captured in agent report)
- Successful revert (all tests pass after undo)
- Agent report explains what refactoring was attempted and why it broke tests

**Orchestrator action**: Record `refactored: false`. Mark task as PARTIAL — the implementation works (GREEN verified) but was not successfully refactored. This does not block downstream tasks.

### FAIL: Tests Broke and Cannot Be Recovered

**Condition**: Refactoring broke tests and the agent was unable to revert to a working state.

**Evidence required**:
- Test failures after refactoring
- Revert was attempted but failed (or was not attempted)
- Current test state shows failures

**Orchestrator action**: Record `refactored: false`, `green_verified: false` (since tests are now failing). Mark task as FAIL. Include the test failures in retry context.

**Note**: This state should be rare. The tdd-executor agent is instructed to revert immediately when refactoring breaks tests. If it cannot revert, the implementation may need to be recovered from the pre-refactor state.

---

## Per-Task TDD Compliance Reporting

### Compliance Fields

Each TDD task pair produces a compliance report with these fields:

| Field | Type | Description |
|-------|------|-------------|
| `red_verified` | boolean | Whether all tests failed before implementation (RED phase passed) |
| `green_verified` | boolean | Whether all tests pass after implementation (GREEN phase passed) |
| `refactored` | boolean | Whether cleanup was performed while maintaining green tests |
| `coverage_delta` | string | Percentage change in test coverage from pre to post (e.g., `+12.3%`) |

### Compliance Report Format

The tdd-executor agent includes a TDD compliance section in its verification report:

```
TDD COMPLIANCE:
  RED Verified: true/false
    Tests written: {count}
    Tests failed as expected: {count}
    Tests passed unexpectedly: {count} {list if any}
  GREEN Verified: true/false
    New tests passing: {count}/{total_new}
    Existing tests passing: {count}/{total_existing}
    Regressions: {count} {list if any}
  Refactored: true/false
    Changes made: {brief description or "none"}
    Tests after refactor: {pass_count}/{total}
  Coverage Delta: {+/-percentage} ({before}% -> {after}%)
```

### Session-Level TDD Compliance Summary

The orchestrator aggregates per-task compliance into a session-level summary in `execution_context.md`:

```markdown
## TDD Compliance
| Task Pair | Test Task | Impl Task | RED | GREEN | Refactored | Coverage Delta |
|-----------|-----------|-----------|-----|-------|------------|----------------|
| User Model | #5 (PASS) | #1 (PASS) | Yes | Yes | Yes | +15.2% |
| Login API | #6 (PASS) | #2 (PASS) | Yes | Yes | No | +8.7% |
| Dashboard UI | #7 (PASS) | #3 (FAIL) | Yes | No | N/A | N/A |
```

This summary is also included in the `session_summary.md` at the end of execution.

### Coverage Delta Calculation

Coverage delta measures the change in project test coverage caused by the TDD pair:

1. **Before**: Capture coverage percentage at the start of the test task (Phase 1 baseline)
2. **After**: Capture coverage percentage after GREEN verification passes
3. **Delta**: `after - before` as a signed percentage

If coverage tools are not available or not configured, report `N/A` for coverage delta.

Coverage tool detection follows the `coverage-patterns.md` reference in `tdd-tools`:
- Python: `pytest-cov` (look for `pytest --cov` in project config)
- TypeScript: `istanbul` / `c8` (look for coverage config in `package.json` or `vitest.config.*`)

---

## Status Determination Matrix

### TDD Task Status (Single Task)

| Condition | Status | Notes |
|-----------|--------|-------|
| RED pass + GREEN pass + REFACTOR pass | **PASS** | Full TDD cycle successful |
| RED pass + GREEN pass + REFACTOR partial (reverted) | **PARTIAL** | Code works but unrefactored |
| RED pass + GREEN pass + some edge/error criteria issues | **PARTIAL** | Core behavior works, non-critical gaps |
| RED warn (normal/relaxed mode) + GREEN pass | **PARTIAL** | TDD discipline not fully verified |
| RED fail (strict mode) | **FAIL** | Tests did not fail as expected |
| RED fail (tests cannot run) | **FAIL** | Test file has errors |
| GREEN fail (new tests still failing) | **FAIL** | Implementation incomplete |
| GREEN fail (regressions unresolved) | **FAIL** | Implementation broke existing code |
| REFACTOR fail (cannot recover) | **FAIL** | Tests broken after refactoring |

### TDD Pair Status (Two Related Tasks)

The orchestrator tracks the pair status by combining the test task and implementation task results:

| Test Task | Impl Task | Pair Status | Notes |
|-----------|-----------|-------------|-------|
| PASS | PASS | **Complete** | Full TDD cycle for this pair |
| PASS | PARTIAL | **Partial** | Implementation works but has issues |
| PASS | FAIL | **Blocked** | Implementation failed; may retry |
| FAIL | Not started | **Blocked** | Tests failed; implementation cannot start |
| PARTIAL | PASS | **Complete (with warnings)** | Some RED phase warnings |
| PARTIAL | FAIL | **Blocked** | Both phases have issues |

---

## Integration with Standard Verification

### Non-TDD Tasks in TDD Sessions

Non-TDD tasks within a `execute-tdd-tasks` session use the standard verification patterns from `execute-tasks`:

- Spec-generated tasks: criterion-by-criterion evaluation (Functional, Edge Cases, Error Handling, Performance)
- General tasks: inferred verification checklist

These tasks are NOT included in the TDD compliance summary. They appear in the standard task log and session summary.

### Acceptance Criteria Verification for TDD Tasks

TDD tasks still have acceptance criteria from the original SDD spec. These are verified in addition to TDD phase verification:

1. **Test task (RED)**: Verify that tests cover all acceptance criteria from the original task. Criteria are evaluated as test descriptions, not as implemented behavior
2. **Implementation task (GREEN)**: Verify that acceptance criteria are satisfied by the implementation. This is the same verification as standard `execute-tasks`, but occurs within the GREEN phase

The TDD status determination takes BOTH TDD phase results and acceptance criteria results into account:

```
TDD Phase: PASS + Acceptance Criteria: ALL Functional pass  ->  PASS
TDD Phase: PASS + Acceptance Criteria: Some non-Functional fail  ->  PARTIAL
TDD Phase: PASS + Acceptance Criteria: Any Functional fail  ->  FAIL
TDD Phase: FAIL (any phase)  ->  FAIL (regardless of criteria)
```

---

## Failure Reporting Format

### TDD Task Failure Report

When a TDD task fails, the verification report includes TDD-specific sections:

```
TASK RESULT: FAIL
Task: [{id}] {subject}

TDD PHASE: {RED|GREEN|REFACTOR}
TDD COMPLIANCE:
  RED Verified: {true|false}
  GREEN Verified: {true|false}
  Refactored: {true|false|N/A}
  Coverage Delta: {percentage|N/A}

VERIFICATION:
  Functional: {n}/{total} passed
  Edge Cases: {n}/{total} passed
  Error Handling: {n}/{total} passed
  Tests: {passed}/{total} ({failed} failures)

PHASE FAILURE DETAILS:
  Phase: {RED|GREEN|REFACTOR}
  Error: {specific error message}
  Failing tests:
    - {test_name}: {error message}
    - {test_name}: {error message}
  Cause: {diagnosis of why the phase failed}

RECOMMENDATIONS:
  - {specific action to fix the failure}
  - {alternative approach if primary fix is complex}

FILES MODIFIED:
  - {file path}: {brief description}
```

### Retry Context for TDD Tasks

When retrying a TDD task, the orchestrator includes TDD-specific context:

```
RETRY ATTEMPT {n} of {max_retries}
Previous TDD phase that failed: {RED|GREEN|REFACTOR}
Previous attempt failed with:
---
{previous verification report including TDD COMPLIANCE section}
---

TDD-specific retry guidance:
- If RED failed (tests cannot run): Check test syntax, imports, and framework config
- If RED warned (tests passed unexpectedly): Verify tests target new behavior, not existing code
- If GREEN failed (tests still failing): Re-read test assertions, try different implementation approach
- If GREEN failed (regressions): Identify regression cause, fix without breaking new tests
- If REFACTOR failed: Revert to pre-refactor state, try smaller refactoring steps
```

---

## Edge Case Handling

### Pre-Existing Test Failures in TDD Context

When the project has test failures before TDD execution begins:

1. **Baseline capture**: The tdd-executor agent records all pre-existing failures during Phase 1 (UNDERSTAND)
2. **RED isolation**: During RED verification, only new tests are evaluated. Pre-existing failures are excluded
3. **GREEN isolation**: During GREEN verification, regressions are determined by comparing against the baseline. A test that was already failing before TDD began is NOT counted as a regression
4. **Reporting**: Pre-existing failures are reported separately in the compliance report:
   ```
   BASELINE: {n} pre-existing test failures (excluded from TDD verification)
   ```

### Test Task Produces No Tests

If the tdd-executor agent completes the RED phase but produces zero tests:

1. Mark the test task as FAIL with reason: "No tests were generated"
2. The paired implementation task remains blocked
3. Retry with explicit instructions to generate at least one test per acceptance criterion

### Implementation Task Cannot Find Test Files

If the tdd-executor agent during the GREEN phase cannot locate the tests written by the paired test task:

1. Check the test task's context file for test file paths
2. Check the test task's verification report for file locations
3. If test files genuinely do not exist (deleted, wrong path), mark as FAIL
4. Include the expected test file paths in the retry context

### Partial Test Coverage

If the test task writes tests for some but not all acceptance criteria:

- During RED: PASS (tests that exist all fail) with a warning about missing coverage
- During GREEN: The implementation must satisfy all acceptance criteria, not just the tested ones
- The missing test coverage is flagged in the compliance report but does not block execution
