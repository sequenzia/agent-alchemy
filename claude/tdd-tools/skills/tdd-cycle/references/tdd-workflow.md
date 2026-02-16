# TDD Workflow Reference

This reference defines the RED-GREEN-REFACTOR phases that guide both the `tdd-cycle` skill and the `tdd-executor` agent. Each phase has explicit entry criteria, procedures, exit criteria, and verification rules.

## Phase Overview

The TDD workflow consists of 6 sequential phases:

```
UNDERSTAND -> WRITE TESTS (RED Setup) -> RED Verification -> IMPLEMENT (GREEN) -> GREEN Verification -> REFACTOR
```

Each phase must complete before the next begins. The workflow is inherently sequential per task — phases cannot be parallelized within a single task.

---

## Phase 1: UNDERSTAND

Load project conventions, identify the test framework, explore relevant codebase areas, and understand requirements before writing any code or tests.

### Entry Criteria

- Task has been assigned (task ID, description, or feature spec available)
- Execution context is accessible (if running within a session)

### Procedure

1. **Load project conventions**: Read `CLAUDE.md`, `.claude/agent-alchemy.local.md` for project-specific rules
2. **Identify test framework**: Auto-detect from config files (`pyproject.toml`, `package.json`, `conftest.py`, `jest.config.*`, `vitest.config.*`). Fall back to `.claude/agent-alchemy.local.md` settings if detection fails
3. **Explore codebase**: Use Glob/Grep to find files related to the feature scope. Read existing code, existing tests, and adjacent modules
4. **Understand requirements**: Parse acceptance criteria (from SDD tasks), feature description, or spec section. Identify what behavior must be tested and implemented
5. **Snapshot existing test state**: Run the existing test suite and record the baseline. Note any pre-existing failures (see Edge Case Handling below)

### Exit Criteria

- Test framework identified and confirmed runnable
- Requirements parsed into testable behaviors
- Existing test baseline recorded (pass count, fail count, specific failures)
- Clear understanding of what files will be created or modified

---

## Phase 2: WRITE TESTS (RED Setup)

Write failing tests from requirements or acceptance criteria before any implementation code exists.

### Entry Criteria

- Phase 1 complete: framework identified, requirements parsed, baseline recorded
- No implementation code has been written yet for this feature

### Procedure

1. **Convert requirements to test cases**: Each acceptance criterion (Functional, Edge Cases, Error Handling) becomes one or more test assertions
2. **Follow project test conventions**: Match existing test file naming, directory structure, assertion style, and fixture patterns
3. **Write behavior-driven tests**: Test what the code should do, not how it does it. Focus on inputs, outputs, and observable side effects
4. **Include edge case tests**: Write tests for boundary conditions, null/empty inputs, and error scenarios from the requirements
5. **Ensure tests are runnable**: Import paths resolve, fixtures exist, test framework can discover the tests

### Exit Criteria

- All new test files are written and saved to disk
- Tests follow project conventions (naming, structure, assertions)
- Tests are syntactically valid and discoverable by the test runner
- No implementation code has been written

---

## Phase 3: RED Verification

Run all tests and confirm that the new tests fail. This verifies that the tests are actually testing new behavior that does not yet exist.

### Entry Criteria

- Phase 2 complete: new tests are written and saved
- No implementation code exists for the tested behavior

### Procedure

1. **Run the full test suite**: Execute the project's test command (e.g., `pytest`, `npm test`)
2. **Separate new test results from baseline**: Compare against the Phase 1 baseline to isolate new test results
3. **Verify ALL new tests fail**: Every test written in Phase 2 should fail with an appropriate error (ImportError, AttributeError, AssertionError, etc.)
4. **Apply strictness level** (see TDD Strictness Levels below):
   - If any new test passes, handle according to the configured strictness
5. **Record RED results**: Log which tests failed, with what errors, and whether any passed unexpectedly

### Exit Criteria

- All new tests have been executed
- RED verification result recorded (all fail = confirmed, some pass = warning/abort per strictness)
- Ready to proceed to implementation (or aborted if strict mode and tests pass)

### Verification Rules

- **ALL new tests MUST fail.** A passing test during RED indicates one of:
  - The implementation already exists (feature was already built)
  - The test is not actually testing new behavior (test is too weak)
  - The test has a bug (always passes regardless of implementation)
- If tests pass, warn the user and verify test completeness before proceeding

---

## Phase 4: IMPLEMENT (GREEN)

Write the minimal code necessary to make all failing tests pass. No over-engineering, no extra features, no premature optimization.

### Entry Criteria

- Phase 3 complete: RED verification confirmed (all new tests fail)
- Clear understanding of what each test expects

### Procedure

1. **Implement minimally**: Write only the code needed to make the current failing tests pass. Do not add features, optimizations, or abstractions beyond what the tests require
2. **Follow existing patterns**: Match the codebase's coding style, error handling approach, and module organization
3. **Work incrementally**: Address one test (or small group of related tests) at a time when possible
4. **No test modifications**: Do not change the tests written in Phase 2 to make them pass. If a test is genuinely wrong, document the issue and fix it explicitly
5. **Handle errors at boundaries**: Add error handling that the tests verify, but do not add speculative error handling

### Exit Criteria

- Implementation code is written and saved to disk
- Code follows project conventions and patterns
- Implementation is minimal — no extra features beyond what tests require

---

## Phase 5: GREEN Verification

Run all tests and confirm they ALL pass. This includes both the new tests from Phase 2 and the entire existing test suite.

### Entry Criteria

- Phase 4 complete: implementation code is written
- All test files from Phase 2 are unchanged

### Procedure

1. **Run the full test suite**: Execute the project's test command
2. **Verify ALL new tests pass**: Every test written in Phase 2 must now pass
3. **Verify NO regressions**: Compare against the Phase 1 baseline. No previously-passing test should now fail
4. **If any test fails**:
   - Identify the failing test and the root cause
   - Fix the implementation (not the tests) to make it pass
   - Re-run the full suite
   - Repeat until all tests pass or report FAIL if unable to resolve
5. **Record GREEN results**: Log pass/fail counts, any iteration needed

### Exit Criteria

- ALL new tests pass
- ALL previously-passing tests still pass (zero regressions)
- GREEN verification confirmed

### Verification Rules

- **ALL tests (new + existing) MUST pass.** Zero tolerance for regressions
- If an existing test fails that was passing in the Phase 1 baseline, the implementation introduced a regression — fix it before proceeding
- If a new test cannot be made to pass after reasonable iteration, report FAIL with the specific test and error details

---

## Phase 6: REFACTOR

Clean up the implementation code while keeping all tests green. Improve code quality, reduce duplication, and improve readability without changing behavior.

### Entry Criteria

- Phase 5 complete: GREEN verification confirmed (all tests pass)

### Procedure

1. **Identify refactoring opportunities**: Look for code duplication, unclear naming, overly complex logic, missing abstractions
2. **Make one refactoring change at a time**: Small, focused changes that can be individually verified
3. **Run tests after EACH change**: Execute the full test suite after every refactoring step
4. **If tests break, revert immediately**: Undo the refactoring change that broke tests. Do not try to fix both the refactor and the test simultaneously
5. **Common refactoring targets**:
   - Extract repeated logic into helper functions
   - Improve variable and function naming
   - Simplify conditional logic
   - Add type annotations if the project uses them
   - Remove dead code or unused imports

### Exit Criteria

- All tests still pass (same pass count as Phase 5)
- Code is cleaner, more readable, and follows project conventions
- No behavior changes — only structural improvements

### Verification Rules

- **ALL tests MUST remain green after each refactoring change**
- If a refactoring change breaks any test, revert that specific change immediately
- The refactored code must produce identical test results to the pre-refactor code
- If refactoring cannot be completed without breaking tests, report PARTIAL with the passing but unrefactored code

---

## Phase Verification Rules Summary

| Phase | Rule | On Violation |
|-------|------|-------------|
| **RED** | ALL new tests MUST fail | Warn user, verify test completeness (or abort in strict mode) |
| **GREEN** | ALL tests (new + existing) MUST pass | Iterate on implementation; report FAIL if unresolvable |
| **REFACTOR** | ALL tests MUST remain green after each change | Revert the breaking refactor change immediately |

---

## TDD Strictness Levels

The strictness level controls how the RED phase handles tests that pass before implementation. Configure via `.claude/agent-alchemy.local.md` under `tdd.strictness`.

### Strict

RED phase failure is mandatory. If any new test passes before implementation, the workflow aborts.

- **RED behavior**: Run tests. If ANY new test passes, abort the workflow immediately
- **Rationale**: Guarantees true test-first development. Tests that pass before implementation indicate either pre-existing code or weak tests
- **Use when**: Enforcing rigorous TDD discipline; greenfield development where no implementation should exist

### Normal (default)

RED phase failure is expected. If tests pass, warn but continue.

- **RED behavior**: Run tests. If any new test passes, log a warning with details of which tests passed and why. Verify test completeness (are the passing tests actually testing meaningful behavior?). Continue to implementation
- **Rationale**: Balances TDD principles with practical reality. Some tests may pass due to partial implementations, shared utilities, or framework defaults
- **Use when**: Standard development; iterating on existing features; most projects

### Relaxed

RED phase is informational only. Proceed regardless of test results.

- **RED behavior**: Run tests. Record results for reporting purposes. Proceed to implementation regardless of pass/fail outcome
- **Rationale**: Useful for retrofitting tests onto existing code, or when generating characterization tests where passing is expected
- **Use when**: Adding tests to existing untested code; characterization testing; exploratory TDD on legacy code

### Strictness Comparison

| Behavior | Strict | Normal | Relaxed |
|----------|--------|--------|---------|
| New tests all fail | Continue | Continue | Continue |
| Some new tests pass | **Abort** | Warn + continue | Log + continue |
| All new tests pass | **Abort** | Warn + verify completeness | Log + continue |
| Report RED results | Yes | Yes | Yes |

---

## Edge Case Handling

### Tests Pass Immediately During RED

**Scenario**: Some or all new tests pass before any implementation is written.

**Diagnosis**:
1. Check if implementation already exists (feature was built previously or by another task)
2. Check if tests are too weak (testing trivial behavior, always-true assertions)
3. Check if tests are importing the wrong module (testing existing code instead of new code)

**Response by strictness level**:
- **Strict**: Abort workflow. Report which tests passed and likely cause
- **Normal**: Log warning with details. Verify each passing test is meaningfully testing new behavior. If implementation exists, skip to REFACTOR phase. If tests are weak, strengthen them and re-run RED
- **Relaxed**: Log results and continue

### Implementation Cannot Make Tests Pass

**Scenario**: After reasonable iteration in Phase 4, some tests still fail and the implementation cannot satisfy them.

**Diagnosis**:
1. Check if the test expectations are contradictory (two tests expect mutually exclusive behavior)
2. Check if the test relies on unavailable infrastructure (database, external service, missing dependency)
3. Check if the requirement itself is ambiguous or impossible

**Response**:
- Report **FAIL** with the specific failing tests and their error messages
- Include recommendations: which tests are unsatisfiable, potential requirement clarifications needed, suggested approach changes
- Do not modify tests to make them pass (that defeats TDD) — instead, document the issue for the user

### Refactor Breaks Tests

**Scenario**: A refactoring change in Phase 6 causes one or more tests to fail.

**Response**:
1. **Revert** the specific refactoring change that broke tests immediately
2. Run tests again to confirm they pass after reverting
3. If the refactoring is important, try a different approach that preserves test behavior
4. If no safe refactoring is possible, report **PARTIAL** — the code works (GREEN verified) but was not refactored
5. Document which refactoring was attempted and why it broke tests

### Pre-Existing Test Failures

**Scenario**: The existing test suite has failures before TDD begins (discovered during Phase 1 baseline).

**Response**:
1. **Snapshot the failures**: Record every failing test name, error message, and file location during the Phase 1 baseline
2. **Isolate new results**: During RED and GREEN verification, compare against the baseline. Only evaluate new tests and previously-passing tests
3. **Do not fix pre-existing failures**: These are outside the scope of the current task. Fixing them risks introducing unrelated changes
4. **Track regressions separately**: If a test that was passing in the baseline starts failing after implementation, that is a regression and must be fixed
5. **Report baseline in results**: Include the pre-existing failure count in the final report so the user is aware

### Partial Implementation

**Scenario**: The implementation partially satisfies the requirements — some new tests pass, others fail.

**Response**:
1. Continue iterating in Phase 4 (GREEN) to make remaining tests pass
2. If some tests are fundamentally unsatisfiable (see "Implementation Cannot Make Tests Pass"), document which ones
3. If the passing tests represent a useful partial feature:
   - Report **PARTIAL** with clear breakdown of passing vs failing tests
   - Include recommendations for completing the remaining implementation
   - Do not proceed to REFACTOR — only refactor code that is fully GREEN
4. If no tests pass, report **FAIL**

---

## Workflow Status Determination

| Condition | Status | Notes |
|-----------|--------|-------|
| All phases complete, all tests pass | **PASS** | Full TDD cycle successful |
| GREEN verified, REFACTOR failed (reverted) | **PARTIAL** | Code works but is unrefactored |
| GREEN verified, some edge/error criteria issues | **PARTIAL** | Core behavior works, non-critical gaps |
| Some new tests fail after implementation | **FAIL** | Implementation incomplete |
| RED phase abort (strict mode) | **FAIL** | Tests did not fail as expected |
| Implementation cannot make tests pass | **FAIL** | Requirements may need clarification |
