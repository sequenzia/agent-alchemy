# tdd-features PRD

**Version**: 1.0
**Author**: Stephen Sequenzia
**Date**: 2026-02-15
**Status**: Draft
**Spec Type**: New feature
**Spec Depth**: Detailed specifications
**Description**: Add TDD (Test-Driven Development) tools to the Agent Alchemy plugin ecosystem, providing AI agents with test-first workflows, automated test generation, and coverage analysis. Primarily focused on Python/pytest with TypeScript adaptability.

---

## 1. Executive Summary

This spec defines a new `tdd-tools` plugin for Agent Alchemy and extensions to the existing `sdd-tools` plugin that together enable Test-Driven Development workflows for AI agents. The plugin provides three standalone skills (generate-tests, tdd-cycle, analyze-coverage) and three agents (test-writer, tdd-executor, test-reviewer), while sdd-tools gains two new skills (create-tdd-tasks, execute-tdd-tasks) that integrate TDD into the Spec-Driven Development pipeline. The goal is to ensure all agent-written code follows TDD principles with comprehensive, behavior-driven test coverage.

## 2. Problem Statement

### 2.1 The Problem

AI agents using Claude Code currently lack test-first enforcement in their development workflow. Three specific problems exist:

1. **No test-first enforcement**: Agents implement features without writing tests first, violating TDD principles. The existing SDD pipeline follows an implementation-first pattern where tests are the last task layer.
2. **Inconsistent test quality**: When tests are written, they are often shallow, test implementation details rather than behavior, miss edge cases, or are poorly structured.
3. **Manual testing workflow**: Users must manually prompt agents to write and run tests, creating friction and inconsistency in test coverage.

### 2.2 Current State

The existing SDD pipeline (`create-tasks` -> `execute-tasks`) includes testing infrastructure:
- `create-tasks` generates `**Testing Requirements:**` sections in task descriptions based on layer-to-test-type mappings
- `task-executor` writes tests during Phase 2 (Implementation) *after* writing implementation code
- Verification (Phase 3) runs the full test suite and checks acceptance criteria

However, the pipeline assumes `Data -> API -> UI -> Test` dependency ordering. Tests are written last, verified last, and there is no mechanism to enforce that tests exist and fail *before* implementation begins.

### 2.3 Impact Analysis

Without TDD enforcement:
- Agent-generated code has unpredictable test coverage
- Bugs surface later in development when they are more expensive to fix
- Test quality varies widely — some tasks produce comprehensive tests, others produce none
- The lack of automated test-first workflow means users cannot trust that agent output meets quality standards

### 2.4 Business Value

TDD tools would:
- Establish quality guarantees for all agent-written code
- Reduce post-implementation debugging time
- Increase user trust in autonomous agent output
- Position Agent Alchemy as a complete, quality-conscious development platform
- Enable measurable code quality metrics (coverage, test pass rates)

## 3. Goals & Success Metrics

### 3.1 Primary Goals
1. Enforce test-first development for AI agents through RED-GREEN-REFACTOR workflows
2. Achieve measurable, configurable test coverage targets on agent-generated code
3. Reduce bugs and regressions by catching issues through comprehensive, behavior-driven tests

### 3.2 Success Metrics

| Metric | Current Baseline | Target | Measurement Method | Timeline |
|--------|------------------|--------|-------------------|----------|
| Test coverage on generated code | Variable (0-50%) | Configurable (default 80%+) | pytest --cov / istanbul | Per-execution |
| TDD cycle compliance | 0% (no enforcement) | 100% when TDD mode active | RED phase verification (tests fail before implementation) | Per-task |
| Test quality score | Unmeasured | 80%+ on behavior-driven rubric | test-reviewer agent scoring | Per-test-suite |
| Regression rate | Unmeasured | <5% tasks introduce regressions | Post-execution test suite pass rate | Per-session |

### 3.3 Non-Goals
- Performance or load testing (out of scope for initial release)
- CI/CD pipeline configuration generation
- Replacing or modifying the existing SDD task-executor agent
- Supporting every possible test framework (focused on pytest + Jest/Vitest)

## 4. User Research

### 4.1 Target Users

#### Primary Persona: Solo Developer
- **Role/Description**: Individual developer using Claude Code for personal or small projects
- **Goals**: Write well-tested code efficiently without manual test management
- **Pain Points**: Agents skip tests, or write superficial tests; manually prompting for tests breaks flow
- **Context**: Working on Python or TypeScript projects, wants autonomous TDD workflow

#### Secondary Persona: Dev Team Lead
- **Role/Description**: Team lead integrating Claude Code into team development workflow
- **Goals**: Ensure consistent code quality standards across agent-generated output
- **Pain Points**: Cannot enforce test coverage targets; inconsistent quality across agent sessions
- **Context**: Managing Python/TypeScript projects with CI requirements, needs measurable quality metrics

### 4.2 User Journey Map

**Standalone TDD Usage:**
```
User has code to write --> /generate-tests or /tdd-cycle --> Tests generated (RED) --> Implementation (GREEN) --> Refactor --> Coverage report
```

**SDD Pipeline Integration:**
```
/create-spec --> /create-tasks --> /create-tdd-tasks --> /execute-tdd-tasks --> Coverage analysis
```

**Retrofit Testing:**
```
User has existing code --> /generate-tests (code-analysis mode) --> Tests generated --> /analyze-coverage --> Gap report
```

## 5. Functional Requirements

### 5.1 Feature: Generate Tests (`/generate-tests`)

**Priority**: P0 (Critical)

#### User Stories

**US-001**: As a developer, I want to generate test files from acceptance criteria so that I have comprehensive tests before writing implementation code.

**Acceptance Criteria**:
- [ ] Accepts a spec file path, task ID, or file path as input
- [ ] When given acceptance criteria (from SDD tasks), converts Functional, Edge Cases, Error Handling, and Performance criteria into executable test assertions
- [ ] When given a source file (code-analysis mode), analyzes the code structure and generates tests for public functions/methods
- [ ] Auto-detects the project's test framework from config files (pyproject.toml, package.json, conftest.py, jest.config.*, vitest.config.*)
- [ ] Falls back to `.claude/agent-alchemy.local.md` settings if auto-detection fails
- [ ] Generates tests following the project's existing test file naming conventions and directory structure
- [ ] Spawns test-writer agents (sonnet) in parallel when generating tests for multiple features
- [ ] Generated tests are runnable and initially fail (RED state) when no implementation exists
- [ ] Works standalone — does not require the SDD pipeline to function

**Edge Cases**:
- No test framework detected: Prompt user to specify framework via AskUserQuestion
- Empty acceptance criteria: Generate basic smoke tests from function signatures
- Mixed language project: Detect primary language per-directory, generate appropriate tests

---

**US-002**: As a developer, I want to generate tests for existing code so that I can retrofit test coverage onto untested modules.

**Acceptance Criteria**:
- [ ] Accepts a file path or directory as input for code-analysis mode
- [ ] Analyzes function signatures, class methods, and module structure
- [ ] Generates tests that verify current behavior (characterization tests)
- [ ] Identifies untested edge cases and generates tests for them
- [ ] Preserves existing test files (does not overwrite)

---

### 5.2 Feature: TDD Cycle (`/tdd-cycle`)

**Priority**: P0 (Critical)

#### User Stories

**US-003**: As a developer, I want to run a full RED-GREEN-REFACTOR workflow so that my features are developed test-first with verified coverage.

**Acceptance Criteria**:
- [ ] Accepts a feature description, task ID, or spec section as input
- [ ] Phase 1 (Understand): Loads project conventions, identifies test framework, explores relevant codebase areas
- [ ] Phase 2 (RED): Writes failing tests from requirements, runs tests to confirm they fail
- [ ] Phase 3 (GREEN): Implements minimal code to make tests pass, runs tests to confirm they pass
- [ ] Phase 4 (REFACTOR): Cleans up code while keeping tests green, runs final test suite
- [ ] Fully autonomous execution — confirm plan once, then runs without interruption
- [ ] Works standalone or integrated with SDD task pipeline
- [ ] Reports final test results with pass/fail counts and coverage percentage

**Edge Cases**:
- Tests pass immediately (no RED phase): Warn user that implementation may already exist, proceed to verify completeness
- Implementation cannot make tests pass: Report FAIL with specific failing tests and recommendations
- Refactor breaks tests: Revert refactor changes, report PARTIAL with passing but unrefactored code

---

### 5.3 Feature: Analyze Coverage (`/analyze-coverage`)

**Priority**: P1 (High)

#### User Stories

**US-004**: As a developer, I want to analyze test coverage and identify gaps so that I know what areas need additional testing.

**Acceptance Criteria**:
- [ ] Runs real coverage tools (pytest --cov, istanbul/c8) via Bash
- [ ] Parses coverage output and generates a structured report
- [ ] Maps coverage results against spec requirements (if spec path provided)
- [ ] Identifies untested acceptance criteria and coverage gaps
- [ ] Reports coverage percentage against configurable threshold
- [ ] Works on any project — not tied to the SDD pipeline
- [ ] Suggests specific tests to write for uncovered areas

**Edge Cases**:
- Coverage tool not installed: Detect and inform user, suggest installation command
- No tests exist: Report 0% coverage with recommendations to use `/generate-tests`
- Multiple test directories: Aggregate coverage across all test locations

---

### 5.4 Feature: Create TDD Tasks (`/create-tdd-tasks`) — sdd-tools Extension

**Priority**: P0 (Critical)

#### User Stories

**US-005**: As a developer, I want to transform SDD tasks into test-first task pairs so that the execution pipeline follows TDD principles.

**Acceptance Criteria**:
- [ ] Reads existing tasks from the task list (generated by `/create-tasks`)
- [ ] For each implementation task, generates a paired test task that must complete first
- [ ] Test tasks contain: test file path, test framework, acceptance criteria converted to test descriptions
- [ ] Sets dependencies: test task blocks its paired implementation task
- [ ] Adds TDD-specific metadata: `tdd_phase` ("red"/"green"/"refactor"), `paired_task_id`, `tdd_mode: true`
- [ ] Supports `--task-group` filtering to convert only specific groups
- [ ] Preserves existing task dependencies — TDD pairs are inserted into the dependency chain
- [ ] Requires `tdd-tools` plugin to be installed (uses test-writer agent)

**Edge Cases**:
- Tasks already have TDD pairs: Detect and skip (merge mode)
- Tasks without acceptance criteria: Generate basic test tasks from task subject/description
- Circular dependencies after TDD pair insertion: Detect and break at weakest link

---

### 5.5 Feature: Execute TDD Tasks (`/execute-tdd-tasks`) — sdd-tools Extension

**Priority**: P0 (Critical)

#### User Stories

**US-006**: As a developer, I want to execute TDD task pairs autonomously so that implementation follows the RED-GREEN-REFACTOR cycle at scale.

**Acceptance Criteria**:
- [ ] Orchestrates wave-based execution of TDD task pairs
- [ ] Launches tdd-executor agents (from tdd-tools) with 6-phase workflow
- [ ] Strategic parallelism: parallelizes test generation (multiple test-writers per wave), keeps RED-GREEN-REFACTOR sequential per task
- [ ] Reuses execution context, session management, and wave infrastructure from execute-tasks
- [ ] Supports `--task-group` and `--max-parallel` arguments
- [ ] Reports per-task TDD compliance (RED verified, GREEN verified, refactored)
- [ ] Requires `tdd-tools` plugin to be installed (uses tdd-executor and test-writer agents)

**Edge Cases**:
- tdd-tools not installed: Clear error message explaining the dependency
- Mixed TDD and non-TDD tasks in same group: Execute non-TDD tasks with standard task-executor, TDD tasks with tdd-executor
- Test-writer agent fails: Retry with different approach, fall back to tdd-executor writing its own tests

---

### 5.6 Feature: Behavior-Driven Test Rubric

**Priority**: P1 (High)

#### User Stories

**US-007**: As a developer, I want AI-generated tests to be validated against quality standards so that tests verify behavior, not implementation details.

**Acceptance Criteria**:
- [ ] test-reviewer agent scores tests on 4 dimensions: meaningful assertions, edge case coverage, test independence, readability
- [ ] Tests that check implementation details (mocking internals, asserting call counts) are flagged
- [ ] Each dimension scored 0-100; overall score is weighted average
- [ ] Tests scoring below configurable threshold are flagged for improvement
- [ ] Rubric is applied automatically during TDD cycle and optionally for generate-tests
- [ ] Review results included in execution reports

**Edge Cases**:
- Test relies on implementation detail by necessity (e.g., verifying a specific algorithm): Allow with explicit justification
- All tests score low: Provide concrete improvement suggestions rather than just rejecting

---

### 5.7 Feature: Test Framework Auto-Detection

**Priority**: P1 (High)

#### User Stories

**US-008**: As a developer, I want the plugin to automatically detect my test framework so that generated tests work without manual configuration.

**Acceptance Criteria**:
- [ ] Detection chain: `pyproject.toml`/`setup.cfg` -> pytest config, `package.json` -> jest/vitest/mocha, `conftest.py` -> pytest, `jest.config.*` -> Jest, `vitest.config.*` -> Vitest
- [ ] Detects test directory conventions (tests/, __tests__/, test/, spec/)
- [ ] Detects test file naming patterns (test_*.py, *_test.py, *.test.ts, *.spec.ts)
- [ ] Detects assertion library and fixtures in use
- [ ] Falls back to `.claude/agent-alchemy.local.md` framework setting if detection fails
- [ ] Caches detection results for the session to avoid repeated file reads

**Edge Cases**:
- Multiple frameworks in monorepo: Detect per-directory, support different frameworks for different modules
- No config files: Infer from existing test files, or prompt user

## 6. Non-Functional Requirements

### 6.1 Performance
- Test generation for a single feature should complete within the same time budget as a standard task-executor run
- Coverage analysis should complete within 60 seconds for projects under 10,000 lines
- Strategic parallelism should recover at least 50% of the time overhead from doubled task counts

### 6.2 Security
- Generated test files must not contain hardcoded secrets or credentials
- Coverage tool execution is sandboxed to the project directory
- Auto-approve hooks (if any) are limited to test file directories only

### 6.3 Reliability
- Framework auto-detection should succeed for >90% of standard Python and TypeScript projects
- Graceful degradation: if a TDD phase fails, report partial results rather than losing all progress
- Execution context sharing must handle concurrent test-writer agents without write contention

## 7. Technical Considerations

### 7.1 Architecture Overview

The TDD tools follow a dual-plugin architecture:

- **`tdd-tools` (new plugin)**: Self-contained TDD capabilities — test generation, TDD cycle execution, and coverage analysis. Works standalone on any project.
- **`sdd-tools` (extended)**: Pipeline integration skills that bridge SDD task management with TDD execution. Requires `tdd-tools` to be installed.

Both plugins follow the markdown-as-code pattern: skills as `SKILL.md` with YAML frontmatter, agents as `{name}.md`, hooks as JSON configs.

### 7.2 Tech Stack
- **Plugin format**: Markdown-as-code (SKILL.md, agent .md files, hooks.json)
- **Primary test framework**: Python/pytest
- **Secondary test framework**: TypeScript (Jest, Vitest)
- **Coverage tools**: pytest-cov (Python), istanbul/c8 (TypeScript)
- **Execution**: Bash tool for running tests and coverage tools
- **Cross-plugin references**: `${CLAUDE_PLUGIN_ROOT}` for skill composition

### 7.3 Integration Points

| System | Integration Type | Purpose |
|--------|-----------------|---------|
| `sdd-tools/create-tasks` | Downstream pipeline | `create-tdd-tasks` reads tasks generated by `create-tasks` |
| `sdd-tools/execute-tasks` | Parallel orchestrator | `execute-tdd-tasks` reuses wave/session infrastructure |
| `core-tools/language-patterns` | Skill composition | Test-writer and tdd-executor load language-specific patterns |
| `core-tools/project-conventions` | Skill composition | Test framework detection and test file naming |
| `core-tools/deep-analysis` | Optional exploration | TDD cycle can explore codebase before test generation |
| `.claude/agent-alchemy.local.md` | Settings | Coverage thresholds, framework selection, TDD strictness |

### 7.4 Technical Constraints
- `${CLAUDE_PLUGIN_ROOT}` must resolve correctly for cross-plugin skill references between tdd-tools and sdd-tools — this is an open question requiring empirical validation
- TDD executor's 6-phase workflow is inherently sequential per task (cannot parallelize RED-GREEN within a single task)
- Coverage tool availability depends on user's project setup (pytest-cov, istanbul must be installed)

## 7.5 Codebase Context

### Existing Architecture

The Agent Alchemy plugin system is organized into 4 plugin groups under `claude/`:
- `core-tools`: Codebase analysis, deep exploration (code-explorer/synthesizer agents), language patterns
- `dev-tools`: Feature development, code review, docs, changelog
- `sdd-tools`: Spec-Driven Development pipeline (create-spec, analyze-spec, create-tasks, execute-tasks)
- `git-tools`: Git commit automation

All plugins are registered in `claude/.claude-plugin/marketplace.json` with naming pattern `agent-alchemy-{group}`.

### Integration Points

| File/Module | Purpose | How TDD Connects |
|------------|---------|-------------------|
| `sdd-tools/skills/create-tasks/SKILL.md` | Spec-to-task decomposition | `create-tdd-tasks` reads its output to generate TDD task pairs |
| `sdd-tools/skills/create-tasks/references/testing-requirements.md` | Test type mappings | TDD inverts the layer ordering (tests first, not last) |
| `sdd-tools/skills/execute-tasks/SKILL.md` | Wave-based execution orchestrator | `execute-tdd-tasks` reuses session/context infrastructure |
| `sdd-tools/skills/execute-tasks/references/verification-patterns.md` | PASS/PARTIAL/FAIL rules | TDD adds RED phase verification (tests must fail before GREEN) |
| `sdd-tools/agents/task-executor.md` | 4-phase implementation agent | `tdd-executor` extends to 6-phase RED-GREEN-REFACTOR |
| `core-tools/skills/language-patterns/SKILL.md` | Language-specific idioms | Loaded by test-writer for framework-specific test patterns |
| `core-tools/skills/project-conventions/SKILL.md` | Project patterns | Used for test file naming, directory structure detection |

### Patterns to Follow
- **Skill frontmatter**: YAML with name, description, argument-hint, user-invocable, allowed-tools — used across all plugins
- **Agent frontmatter**: YAML with name, description, model, tools, skills — consistent across all 9 existing agents
- **Reference files**: Supporting knowledge in `skills/{name}/references/*.md` — loaded during skill execution
- **Cross-plugin composition**: `Read ${CLAUDE_PLUGIN_ROOT}/skills/{name}/SKILL.md` — used by feature-dev, deep-analysis, and others
- **Model tiering**: Opus for reasoning/synthesis (tdd-executor, test-reviewer), Sonnet for parallel workers (test-writer)
- **Settings pattern**: `.claude/agent-alchemy.local.md` with YAML frontmatter for per-user configuration

### Related Features
- **execute-tasks**: The closest reference implementation for `execute-tdd-tasks`. Same wave-based orchestration, session management, execution context sharing. TDD version adds RED/GREEN phase verification.
- **task-executor**: The closest reference for `tdd-executor`. Same autonomous 4-phase workflow, extended to 6 phases for TDD.
- **code-reviewer**: Reference for `test-reviewer`. Same confidence-scored evaluation pattern, applied to test quality instead of code quality.

## 8. Scope Definition

### 8.1 In Scope
- New `tdd-tools` plugin with 3 skills and 3 agents
- Extensions to `sdd-tools` with 2 new skills (`create-tdd-tasks`, `execute-tdd-tasks`)
- Python/pytest as primary framework
- TypeScript (Jest, Vitest) as secondary framework
- Test framework auto-detection
- Behavior-driven test quality rubric
- Coverage analysis via real tools (pytest-cov, istanbul)
- Configurable settings (coverage thresholds, framework, TDD strictness)
- Standalone usage (each skill works independently)
- SDD pipeline integration (parallel pipeline pattern)
- Marketplace registration for `tdd-tools`

### 8.2 Out of Scope
- **Performance/load testing**: Complex infrastructure requirements, better as a separate future plugin
- **CI/CD pipeline configuration**: Users manage their own CI/CD; this plugin focuses on local development
- **Modifying existing sdd-tools agents**: The existing `task-executor` is not changed; a new `tdd-executor` is created
- **Test frameworks beyond pytest/Jest/Vitest**: Initial release focuses on the most popular frameworks
- **Visual/snapshot testing**: UI-specific testing patterns are excluded from initial release

### 8.3 Future Considerations
- Additional test framework support (Go testing, Rust, Java JUnit)
- Performance and load testing plugin
- CI/CD configuration generation
- Visual regression testing
- Mutation testing integration
- Test data factory generation

## 9. Implementation Plan

### 9.1 Phase 1: Foundation - Generate Tests + Test Writer

**Completion Criteria**: Users can run `/generate-tests` to produce quality test files from acceptance criteria or existing code.

| Deliverable | Description | Dependencies |
|-------------|-------------|--------------|
| `tdd-tools/` plugin structure | Directory layout, README, marketplace registration | None |
| Test framework auto-detection | Detection chain for pytest, Jest, Vitest with settings fallback | None |
| `generate-tests` skill | SKILL.md with criteria-driven and code-analysis modes | Framework detection |
| `test-writer` agent | Sonnet agent for parallel test generation | generate-tests skill |
| Test pattern references | Framework-specific templates for pytest, Jest, Vitest | None |
| Settings support | `.claude/agent-alchemy.local.md` entries for framework and coverage threshold | None |

**Checkpoint Gate**: Generated tests are runnable, follow project conventions, and cover acceptance criteria. Review test quality manually before proceeding.

---

### 9.2 Phase 2: Core TDD - TDD Cycle + Pipeline Integration

**Completion Criteria**: Users can run `/tdd-cycle` for standalone TDD and `/create-tdd-tasks` + `/execute-tdd-tasks` for pipeline-integrated TDD.

| Deliverable | Description | Dependencies |
|-------------|-------------|--------------|
| `tdd-cycle` skill | Full RED-GREEN-REFACTOR workflow skill | Phase 1 (generate-tests, framework detection) |
| `tdd-executor` agent | 6-phase Opus agent (Understand, Write Tests, RED, Implement, GREEN, Complete) | Phase 1 (test patterns) |
| `create-tdd-tasks` skill (sdd-tools) | Test-first task pair generation from SDD tasks | Phase 1 (test-writer agent) |
| `execute-tdd-tasks` skill (sdd-tools) | TDD-aware execution orchestrator with strategic parallelism | tdd-cycle skill, tdd-executor agent |
| TDD decomposition patterns | References for test-first task ordering and dependency inference | None |
| TDD verification patterns | RED/GREEN phase verification rules | None |

**Checkpoint Gate**: Full RED-GREEN-REFACTOR cycle completes autonomously. SDD pipeline integration works end-to-end with test-first task ordering.

---

### 9.3 Phase 3: Quality - Coverage Analysis + Test Review

**Completion Criteria**: Users can analyze coverage gaps and validate test quality with automated scoring.

| Deliverable | Description | Dependencies |
|-------------|-------------|--------------|
| `analyze-coverage` skill | Coverage tool execution, parsing, gap detection, reporting | Phase 1 (framework detection) |
| `test-reviewer` agent | Opus agent scoring tests on behavior-driven rubric | Phase 1 (test patterns) |
| Behavior-driven test rubric | Reference file with scoring dimensions and thresholds | None |
| Coverage pattern references | Framework-specific coverage tool integration guides | None |
| TDD strictness settings | Configurable RED phase enforcement levels | Phase 2 (tdd-cycle) |

**Checkpoint Gate**: Coverage analysis produces accurate reports. Test reviewer correctly identifies implementation-detail tests vs behavior tests.

## 10. Dependencies

### 10.1 Technical Dependencies

| Dependency | Owner | Status | Risk if Delayed |
|------------|-------|--------|-----------------|
| `sdd-tools` plugin (create-tasks, execute-tasks) | Agent Alchemy | Available | Cannot build pipeline integration (Phase 2) |
| `core-tools` plugin (language-patterns, project-conventions) | Agent Alchemy | Available | Test generation quality reduced |
| pytest-cov (Python coverage) | User project | User-installed | Coverage analysis unavailable for Python |
| istanbul/c8 (TypeScript coverage) | User project | User-installed | Coverage analysis unavailable for TypeScript |
| `${CLAUDE_PLUGIN_ROOT}` cross-plugin resolution | Claude Code | Needs validation | Cross-plugin skill composition may not work as expected |

### 10.2 Cross-Plugin Dependencies

| Plugin | Dependency | Status |
|--------|------------|--------|
| `tdd-tools` | `core-tools` (language-patterns, project-conventions) | Available — skill composition |
| `sdd-tools` extensions | `tdd-tools` (test-writer, tdd-executor agents) | New — requires tdd-tools installed |
| `sdd-tools` extensions | `sdd-tools` (create-tasks, execute-tasks) | Available — same plugin |

## 11. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation Strategy |
|------|--------|------------|---------------------|
| AI-generated tests are superficial or test implementation details | High | High | Behavior-driven test rubric + test-reviewer agent validates quality; reference patterns guide test-writer |
| Test framework compatibility issues across Python and TypeScript | Medium | Medium | Auto-detection chain with settings fallback; focused on pytest + Jest/Vitest initially |
| Pipeline complexity makes TDD hard to understand | Medium | Medium | All skills work standalone; SDD integration is optional; clear documentation |
| TDD doubles task count, slowing execution | Medium | High | Strategic parallelism: parallel test generation, sequential RED-GREEN-REFACTOR per task |
| `${CLAUDE_PLUGIN_ROOT}` doesn't resolve across plugins | High | Low | Validate early in Phase 1; if broken, use explicit path references as workaround |
| RED phase verification unreliable (tests may pass unexpectedly) | Medium | Medium | Configurable TDD strictness; warn user when tests pass during RED phase |
| Coverage tools not available in user's project | Low | Medium | Detect and inform user; suggest installation; degrade gracefully to static analysis |

## 12. Open Questions

| # | Question | Owner | Due Date | Resolution |
|---|----------|-------|----------|------------|
| 1 | How does `${CLAUDE_PLUGIN_ROOT}` resolve for cross-plugin skill references? Does it work when tdd-tools references sdd-tools skills? | Dev Team | Phase 1 | Needs empirical validation |
| 2 | Should TDD tasks and SDD tasks coexist in the same task list, or use separate lists? | Dev Team | Phase 2 | Impacts `create-tdd-tasks` design |
| 3 | How aggressive should the REFACTOR phase be? Current task-executor applies "minimal changes" — should TDD refactor have broader latitude? | Dev Team | Phase 2 | Impacts tdd-executor system prompt |
| 4 | Should `analyze-coverage` run actual coverage tools or fall back to static analysis when tools are unavailable? | Dev Team | Phase 3 | Decided: run real tools, degrade gracefully |

## 13. Appendix

### 13.1 Glossary

| Term | Definition |
|------|------------|
| TDD | Test-Driven Development — write failing tests first, then implement to make them pass, then refactor |
| RED phase | The first step of TDD: write a test that fails because the implementation doesn't exist yet |
| GREEN phase | The second step of TDD: write the minimum implementation to make the failing test pass |
| REFACTOR phase | The third step: clean up the code while keeping all tests passing |
| SDD | Spec-Driven Development — Agent Alchemy's pipeline for turning specs into autonomous implementation |
| Parallel pipeline | Architecture where TDD tools run alongside (not inside) the SDD pipeline |
| Behavior-driven test | A test that verifies what code does (behavior) rather than how it does it (implementation) |
| Characterization test | A test written for existing code that documents its current behavior |
| test-writer | Sonnet-tier agent that generates test files in parallel |
| tdd-executor | Opus-tier agent that runs the 6-phase RED-GREEN-REFACTOR workflow per task |
| test-reviewer | Opus-tier agent that validates test quality using the behavior-driven rubric |

### 13.2 References
- Agent Alchemy CLAUDE.md — Project conventions and architecture
- `sdd-tools/skills/create-tasks/references/testing-requirements.md` — Existing test type mappings
- `sdd-tools/skills/execute-tasks/references/verification-patterns.md` — Existing PASS/FAIL rules
- `sdd-tools/agents/task-executor.md` — Reference implementation for tdd-executor
- `dev-tools/agents/code-reviewer.md` — Reference implementation for test-reviewer

### 13.3 Proposed Plugin Structure

```
tdd-tools/                              # NEW PLUGIN
├── agents/
│   ├── test-writer.md                  # Sonnet — parallel test generation
│   ├── tdd-executor.md                 # Opus — 6-phase RED-GREEN-REFACTOR
│   └── test-reviewer.md               # Opus — behavior-driven quality review
├── skills/
│   ├── generate-tests/
│   │   ├── SKILL.md                    # Test generation skill (standalone)
│   │   └── references/
│   │       ├── test-patterns.md        # Framework-specific test patterns
│   │       └── framework-templates.md  # pytest, Jest, Vitest templates
│   ├── tdd-cycle/
│   │   ├── SKILL.md                    # RED-GREEN-REFACTOR workflow
│   │   └── references/
│   │       └── tdd-workflow.md         # TDD phase definitions
│   └── analyze-coverage/
│       ├── SKILL.md                    # Coverage analysis skill
│       └── references/
│           └── coverage-patterns.md    # Coverage tool integration
└── README.md

sdd-tools/ (EXTENDED)
├── skills/
│   ├── create-tdd-tasks/
│   │   ├── SKILL.md                    # Test-first task pair generation
│   │   └── references/
│   │       ├── tdd-decomposition-patterns.md
│   │       └── tdd-dependency-rules.md
│   └── execute-tdd-tasks/
│       ├── SKILL.md                    # TDD-aware execution orchestrator
│       └── references/
│           ├── tdd-execution-workflow.md
│           └── tdd-verification-patterns.md
```

---

*Document generated by SDD Tools*
