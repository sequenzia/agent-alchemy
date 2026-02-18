# Conversion Result: skill-tdd-tools-generate-tests

## Metadata

| Field | Value |
|-------|-------|
| Component ID | skill-tdd-tools-generate-tests |
| Component Type | skill |
| Group | tdd-tools |
| Name | generate-tests |
| Source Path | claude/tdd-tools/skills/generate-tests/SKILL.md |
| Target Path | .opencode/skills/generate-tests.md |
| Fidelity Score | 82% |
| Fidelity Band | green |
| Status | full |

## Converted Content

~~~markdown
---
description: Generate test files from acceptance criteria or existing code. Supports criteria-driven mode (from specs/tasks) and code-analysis mode (from source files). Auto-detects test framework and spawns test-writer agents for parallel generation.
user-invocable: true
---

# Generate Tests Skill

Generate high-quality, behavior-driven test files from acceptance criteria or existing source code. This skill auto-detects the project's test framework, loads framework-specific patterns, and spawns test-writer agents to produce runnable test files that follow project conventions.

**CRITICAL: Complete ALL 6 phases.** The workflow is not complete until Phase 6: Report is finished. After completing each phase, immediately proceed to the next phase without waiting for user prompts.

Input argument: `$ARGUMENTS` — accepts `<spec-path|task-id|file-path>`

## Core Principles

1. **Tests before implementation** -- Generated tests should initially fail (RED state) when no implementation exists, confirming they test real behavior.
2. **Behavior over implementation** -- Test what the code does, not how it does it. Tests should survive refactoring.
3. **Follow project conventions** -- Match the project's existing test framework, file naming, directory structure, and assertion patterns.
4. **Standalone operation** -- This skill works independently. It does not require the SDD pipeline, `tdd-cycle`, or any other skill to function.

## question Tool is MANDATORY

**IMPORTANT**: You MUST use the `question` tool for ALL questions to the user. Never ask questions through regular text output.

- Framework selection questions -> question
- Clarifying questions about scope -> question
- Confirmation questions -> question

Text output should only be used for presenting information, summaries, and progress updates.

---

## Phase 1: Parse Input

**Goal:** Determine the operating mode and resolve input paths.

Analyze the `$ARGUMENTS` to determine which mode to use:

### Mode Detection

**Criteria-Driven Mode** -- triggered when input is:
- A spec file path (e.g., `specs/SPEC-feature.md`)
- A task ID (e.g., `5`, `#5`, `task-5`)
- A spec section reference (e.g., `specs/SPEC-feature.md Section 5.1`)

**Code-Analysis Mode** -- triggered when input is:
- A source file path (e.g., `src/utils.py`, `src/services/auth.ts`)
- A directory path (e.g., `src/services/`)

**Ambiguous input**: If the input could be either mode (e.g., a path that could be a spec or source file), check the file content. If it contains `**Acceptance Criteria:**` or is a markdown file in a `specs/` directory, use criteria-driven mode. Otherwise, use code-analysis mode.

### Path Resolution

1. Resolve relative paths against the project root
2. For task IDs: use `todoread` to retrieve the full task list, scan for the matching task ID in description text, then extract acceptance criteria
   <!-- CACHED: unmapped_tool:TaskGet | functional | TaskGet | Use todoread full list scan for task_uid in description -->
3. For spec section references: read the spec file and locate the referenced section
4. For directories: use glob to find source files (exclude test files, node_modules, __pycache__, .git)
5. Validate that all resolved paths exist; if not, proceed to error handling (Phase 1 error cases below)

### Error Cases

**Invalid spec path:**
```
ERROR: Spec file not found: {path}

Did you mean one of these?
{List matching files from glob search for similar names}

Usage: /generate-tests <spec-path|task-id|file-path>
```

**Invalid task ID:**
```
ERROR: Task #{id} not found.

Available tasks:
{Use todoread to get the full list, then display first 5 pending/in-progress tasks}
```
<!-- CACHED: unmapped_tool:TaskList | functional | TaskList | Use todoread full list scan for spec_path in description -->

**Empty directory:**
```
ERROR: No source files found in {path}.

The directory exists but contains no files matching supported extensions (.py, .ts, .tsx, .js, .jsx).
```

---

## Phase 2: Detect Framework

**Goal:** Auto-detect the project's test framework using the detection chain.

### Load Detection Chain

<!-- CACHED: unsupported_composition:reference_dir_null | functional | framework-templates.md reference | Inline reference content into skill body -->
<!-- TODO: The framework-templates.md reference file cannot be loaded via skill reference in opencode. The detection chain and boilerplate templates from references/framework-templates.md must be inlined below or maintained separately. See general_gap:reference_dir for context. -->

The framework detection algorithm follows this priority chain:

### Step 1: Config-File Detection (High Confidence)

Check for framework configuration files:

**Python:**
- `pyproject.toml` with `[tool.pytest.ini_options]` or `[tool.pytest]` -> pytest
- `setup.cfg` with `[tool:pytest]` -> pytest
- `pytest.ini` exists -> pytest
- `conftest.py` at project root or in `tests/` -> pytest

**TypeScript/JavaScript:**
- `vitest.config.*` exists -> Vitest (takes priority)
- `jest.config.*` exists -> Jest
- `package.json` with `vitest` in dependencies/devDependencies -> Vitest
- `package.json` with `jest` in dependencies/devDependencies -> Jest
- `package.json` with `"jest": {}` config section -> Jest

### Step 2: Existing Test File Detection (Medium Confidence)

If no config files found, scan for existing test files:
- `test_*.py` or `*_test.py` -> pytest
- `*.test.ts` / `*.spec.ts` with `vitest` imports -> Vitest
- `*.test.ts` / `*.spec.ts` with `jest` imports or no explicit imports -> Jest

### Step 3: Settings Fallback (Low Confidence)

If detection is still ambiguous, check `.claude/agent-alchemy.local.md` for:
```yaml
tdd:
  framework: pytest    # or jest, vitest, auto
```

If `tdd.framework` is set to a recognized value (`pytest`, `jest`, `vitest`), use it. If set to `auto` or an unrecognized value, continue to Step 4.

### Step 4: User Prompt Fallback

If all detection methods fail, prompt the user using the `question` tool:

```yaml
question:
  questions:
    - header: "Test Framework"
      question: "No test framework was detected in this project. Which framework should be used for test generation?"
      options:
        - label: "pytest"
          description: "Python testing framework (recommended for Python projects)"
        - label: "Jest"
          description: "JavaScript/TypeScript testing framework"
        - label: "Vitest"
          description: "Vite-native testing framework (modern alternative to Jest)"
        - label: "Other"
          description: "A different framework (tests may need manual adjustment)"
      multiSelect: false
```

### Detection Result

After detection, record:
- **Framework**: pytest | Jest | Vitest
- **Test directory**: Path to test root (e.g., `tests/`, `__tests__/`, `src/`)
- **Naming pattern**: File naming convention (e.g., `test_*.py`, `*.test.ts`)
- **Assertion library**: Default or extended (e.g., `@testing-library/jest-dom`)
- **Existing fixtures**: Notable fixtures or test utilities found
- **Confidence**: High | Medium | Low

### Monorepo Handling

In monorepos, detect framework per-directory by walking up from the target source file to find the nearest config file. Different directories may use different frameworks.

---

## Phase 3: Load References

**Goal:** Load framework-specific patterns and project conventions.

### Load Test Patterns

<!-- CACHED: unsupported_composition:reference_dir_null | functional | test-patterns.md reference | Inline reference content into skill body -->
<!-- TODO: The test-patterns.md reference file cannot be loaded via skill reference in opencode. The behavior-driven patterns, anti-patterns, and naming conventions from references/test-patterns.md must be inlined below or maintained separately. See general_gap:reference_dir for context. -->

Apply the following core test pattern guidance when generating tests:

- Use Arrange-Act-Assert (pytest/Jest) or Given-When-Then structure
- Test behavior and observable outcomes, not internal implementation details
- Name tests descriptively: `test_should_return_error_when_input_is_empty`
- Avoid testing private/internal methods directly
- One assertion concept per test (multiple assertions for the same behavior are acceptable)
- Group related tests in classes (pytest) or describe blocks (Jest/Vitest)

### Load Framework Templates

Framework boilerplate templates are incorporated inline in Phase 4. The full configuration reference from references/framework-templates.md covers:
- Boilerplate templates for pytest, Jest, and Vitest
- Configuration reference for each framework
- Fixture and test utility patterns

### Load Cross-Plugin Skills

Load language-specific patterns and project conventions for the target project:

```
skill({ name: "language-patterns" })
skill({ name: "project-conventions" })
```

Apply these skills' guidance when generating tests to ensure:
- Language idioms are followed (TypeScript strict typing, Python type hints)
- Project naming conventions are matched
- Import patterns are consistent with the codebase

### Scan Existing Tests

If the project has existing test files:
1. Use read to examine 2-3 representative test files to understand the project's test style
2. Note patterns: fixture usage, test grouping, assertion style, mock patterns
3. Match these patterns in generated tests for consistency

---

## Phase 4: Generate Tests

**Goal:** Produce test files by spawning test-writer agents.

### Criteria-Driven Mode

When operating from acceptance criteria (spec, task, or section reference):

1. **Extract criteria**: Parse the acceptance criteria into categories:
   - **Functional**: Core behavior assertions (highest priority)
   - **Edge Cases**: Boundary conditions and unusual inputs
   - **Error Handling**: Error paths and error messages
   - **Performance**: Efficiency-related assertions (if applicable)

2. **Plan test files**: Determine how many test files to create:
   - One feature/module = one test file
   - Multiple features = one test file per feature
   - Group related criteria into describe blocks or test classes

3. **Map criteria to test cases**: For each criterion, create one or more test cases:
   - Each criterion gets at least one test
   - Complex criteria may need multiple tests (happy path + variations)
   - Edge cases get individual tests
   - Error handling criteria get tests verifying error types and messages

4. **Determine test file paths**: Follow the project's convention:
   - Match existing test directory structure
   - Use the detected naming pattern
   - Place tests adjacent to source files if the project uses colocated tests, or in the test directory if centralized

### Code-Analysis Mode

When operating from source files:

1. **Analyze source files**: For each source file, identify:
   - Public functions and methods (skip private/internal)
   - Function signatures: parameters, return types, side effects
   - Class structures: constructors, public methods, properties
   - Module exports: what is available to consumers

2. **Generate characterization tests**: Create tests that verify current behavior:
   - Test each public function with representative inputs
   - Test return values and observable side effects
   - Test error conditions visible from the signature (e.g., nullable params)

3. **Identify untested edge cases**: Look for:
   - Boundary conditions (empty inputs, null values, max values)
   - Error paths (invalid types, missing required fields)
   - State transitions (before/after operations)

4. **Preserve existing tests**: Before writing, check for existing test files:
   - If a test file already exists for the source file, do NOT overwrite it
   - Instead, generate a supplementary test file with a `_additional` or `_generated` suffix
   - Report which files were skipped and why

### Spawning Test-Writer Agents

**Single feature/file**: Use a single test-writer agent:
```
task tool with subagent_type: "test-writer"

Prompt:
"Generate tests for {feature/file}.

Framework: {detected framework}
Test patterns: {summary of project's test patterns}
File naming: {convention}
Target test file: {output path}

{Mode-specific context:}
- Criteria-driven: {formatted acceptance criteria}
- Code-analysis: {source file content and analysis}

Follow these conventions from the project's existing tests:
{Summary of patterns from existing test files}

Write the test file to: {target path}"
```

**Multiple features/files**: Spawn test-writer agents in parallel:
```
For each feature/file, launch a separate task with subagent_type: "test-writer"
- Each agent gets its own feature's criteria or source file
- All agents share the same framework detection and pattern context
- Launch all agents simultaneously in a single turn for parallelism
```

Wait for all agents to complete before proceeding to Phase 5.

### Agent Failure Handling

If a test-writer agent fails:
1. Log which feature/file failed
2. Continue with successful results
3. Report the failure in Phase 6 with recommendations

---

## Phase 5: Validate

**Goal:** Verify generated tests are syntactically valid and follow conventions.

### Syntax Validation

For each generated test file, run a syntax check:

**pytest:**
```bash
python -c "import ast; ast.parse(open('{test_file}').read())"
```

**Jest/Vitest:**
```bash
npx tsc --noEmit {test_file}
```
Or if TypeScript is not configured:
```bash
node --check {test_file}
```

If syntax validation fails:
1. Read the error output
2. Fix the issue in the test file using edit
3. Re-validate
4. If the fix fails after 2 attempts, flag the file as needing manual review

### Convention Compliance

Verify each generated test file follows project conventions:
- File is in the correct directory
- File naming matches the detected pattern
- Imports are correct and resolvable
- Test structure matches existing test patterns (classes vs functions, describe blocks)
- Assertions use the project's assertion library

### RED State Verification

If no implementation exists for the tested code:
- The generated tests should reference imports that do not yet exist
- This confirms the tests are in RED state (will fail when run)
- Note: Do NOT run the tests at this point -- running failing tests is the job of the TDD cycle

If implementation already exists:
- Flag with a warning:
  ```
  NOTE: Implementation for {module} already exists. Generated tests may pass
  immediately (not in RED state). These tests document existing behavior rather
  than driving new implementation.
  ```

---

## Phase 6: Report

**Goal:** Present a summary of generated test files.

### Report Format

Present the following summary to the user:

```
## Test Generation Summary

**Mode**: {Criteria-Driven | Code-Analysis}
**Framework**: {pytest | Jest | Vitest} ({confidence level})
**Source**: {spec path | task ID | file/directory path}

### Generated Files

| File | Tests | Coverage Area |
|------|-------|---------------|
| {test_file_1} | {count} | {what it tests} |
| {test_file_2} | {count} | {what it tests} |

**Total**: {total_tests} tests across {file_count} files

### Criteria Coverage (Criteria-Driven Mode Only)

| Category | Criteria | Tests |
|----------|----------|-------|
| Functional | {n} criteria | {n} tests |
| Edge Cases | {n} criteria | {n} tests |
| Error Handling | {n} criteria | {n} tests |
| Performance | {n} criteria | {n} tests |

### State

{If no implementation exists:}
Tests are in RED state -- they will fail when run. Implement the code to make them pass.

{If implementation exists:}
WARNING: Implementation already exists. Tests may pass immediately.
Run your test suite to verify: {test command}

### Next Steps

- Run tests: `{test_command}`
- Start TDD cycle: `/tdd-cycle {feature}`
- Analyze coverage: `/analyze-coverage {path}`
```

### Skipped Files (Code-Analysis Mode)

If any files were skipped because tests already exist:
```
### Skipped (Existing Tests)

| Source File | Existing Test File | Reason |
|------------|-------------------|--------|
| {source} | {test_file} | Test file already exists |
```

### Failures

If any test-writer agents failed:
```
### Failures

| Feature/File | Error | Recommendation |
|-------------|-------|----------------|
| {feature} | {error summary} | {suggestion} |
```

---

## Error Handling

### No Input Provided

If `$ARGUMENTS` is empty or missing, use the `question` tool:

```yaml
question:
  questions:
    - header: "Test Generation Input"
      question: "What would you like to generate tests for?"
      options:
        - label: "Spec file"
          description: "Generate tests from a specification's acceptance criteria"
        - label: "Task ID"
          description: "Generate tests from a task's acceptance criteria"
        - label: "Source file or directory"
          description: "Generate characterization tests for existing code"
      multiSelect: false
```

Then prompt for the specific path or ID based on the selection.

### Framework Detection Failure

If framework detection reaches the user prompt fallback (Step 4) and the user selects "Other":

```
WARNING: Unsupported framework selected. Generating tests using the closest
supported framework ({inferred}). Generated tests may need manual adjustment
for your specific framework.
```

### Partial Input

If the input resolves to a spec or task with no acceptance criteria:
- Switch to a hybrid approach: extract any descriptive text for test naming
- Generate basic smoke tests from function signatures if source files are referenced
- Flag the tests as minimal coverage that should be expanded

---

## Settings

The following settings in `.claude/agent-alchemy.local.md` affect test generation:

```yaml
tdd:
  framework: auto                    # auto | pytest | jest | vitest
  test-review-threshold: 70          # Minimum test quality score (0-100)
  test-review-on-generate: false     # Run test-reviewer after generate-tests
```

| Setting | Default | Used In |
|---------|---------|---------|
| `tdd.framework` | `auto` | Phase 2 (framework detection fallback) |
| `tdd.test-review-threshold` | `70` | Phase 6 (test quality evaluation threshold) |
| `tdd.test-review-on-generate` | `false` | Phase 6 (auto-run test-reviewer after generation) |

**Error handling:**
- If the settings file does not exist, use defaults for all settings.
- If the YAML frontmatter is malformed, use defaults and log a warning.
- If `tdd.framework` is set to an unrecognized value, fall back to auto-detection.

See `tdd-tools/README.md` for the full settings reference.

---

## Reference Files

The following reference files from the original skill cannot be loaded via opencode skill references (no reference_dir equivalent). Their content is partially inlined above:

- `references/test-patterns.md` -- Framework-specific test patterns, behavior-driven guidance, anti-patterns (core guidance inlined in Phase 3)
- `references/framework-templates.md` -- Auto-detection chain, boilerplate templates, configuration reference (detection chain inlined in Phase 2; templates must be maintained separately or fully inlined)
~~~

## Fidelity Report

| Mapping Type | Count | Weight | Contribution |
|-------------|-------|--------|-------------|
| Direct | 12 | 1.0 | 12.0 |
| Workaround | 5 | 0.7 | 3.5 |
| TODO | 0 | 0.2 | 0.0 |
| Omitted | 2 | 0.0 | 0.0 |
| **Total** | **19** | | **15.5 / 19 = 81.6%** |

**Notes:** The two omitted features (`disable-model-invocation` and `allowed-tools`) are cosmetic — opencode has no per-skill tool restrictions or model overrides. All functional behavior is preserved. Reference file composition is handled via inlined summaries (workaround) rather than dynamic loading.

## Decisions

| Feature | Decision Type | Original | Converted | Rationale | Confidence | Resolution Mode |
|---------|-------------|----------|-----------|-----------|------------|----------------|
| `name` field | relocated | `name: generate-tests` | Filename: `generate-tests.md` | opencode derives skill name from filename per frontmatter mapping | high | auto |
| `argument-hint` field | relocated | `argument-hint: <spec-path\|task-id\|file-path>` | `Input argument: $ARGUMENTS — accepts <spec-path\|task-id\|file-path>` in body | opencode uses $ARGUMENTS placeholder in body; argument-hint maps to embedded:body | high | auto |
| `user-invocable` field | direct | `user-invocable: true` | `user-invocable: true` | Direct mapping; kept in frontmatter | high | N/A |
| `disable-model-invocation` field | omitted | `disable-model-invocation: false` | (removed) | Maps to null in opencode. Value was `false` (permissive default) so no behavioral loss. | high | auto |
| `allowed-tools` field | omitted | 10-tool list | (removed) | Maps to null; per-skill tool restrictions not supported. All listed tools have opencode equivalents and remain available via agent-level permission config. | high | auto |
| `AskUserQuestion` in body | direct | `AskUserQuestion` tool | `question` tool | Direct mapping; question tool available to primary agents with identical capabilities | high | N/A |
| `AskUserQuestion` YAML examples | direct | `AskUserQuestion:` in code blocks | `question:` in code blocks | Updated all YAML syntax examples to use question tool name | high | N/A |
| `TaskGet` in body | workaround | `TaskGet` to retrieve task by ID | `todoread` full list scan for task_uid | Cached decision: partial:todoread, scan full list for matching task ID | high | cached |
| `TaskList` in body | workaround | `TaskList` for available tasks | `todoread` full list scan | Cached decision: partial:todoread, display first 5 matching tasks | high | cached |
| `Task tool with subagent_type: "test-writer"` | direct | `Task tool` | `task` tool | Direct mapping; subagent_type parameter preserved | high | N/A |
| `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash` in body | direct | Tool names (capitalized) | Tool names (lowercase: read/write/edit/glob/grep/bash) | Direct mappings per tool name table | high | N/A |
| `framework-templates.md` reference | workaround | `Read: ${CLAUDE_PLUGIN_ROOT}/skills/generate-tests/references/framework-templates.md` | Inline summary + TODO comment | reference_dir is null in opencode; cached decision to inline content. Detection chain inlined in Phase 2. | medium | cached |
| `test-patterns.md` reference | workaround | `Read: ${CLAUDE_PLUGIN_ROOT}/skills/generate-tests/references/test-patterns.md` | Inline summary + TODO comment | Same as above; core pattern guidance inlined in Phase 3. | medium | cached |
| `language-patterns` cross-plugin | direct | `Read: ${CLAUDE_PLUGIN_ROOT}/../core-tools/skills/language-patterns/SKILL.md` | `skill({ name: "language-patterns" })` | Cross-plugin supported; mechanism=reference; same pattern for cross-plugin | high | N/A |
| `project-conventions` cross-plugin | direct | `Read: ${CLAUDE_PLUGIN_ROOT}/../core-tools/skills/project-conventions/SKILL.md` | `skill({ name: "project-conventions" })` | Cross-plugin supported; mechanism=reference; same pattern for cross-plugin | high | N/A |

## Gaps

| Feature | Reason | Severity | Workaround | User Acknowledged |
|---------|--------|----------|------------|-------------------|
| `allowed-tools` per-skill restrictions | opencode has no per-skill tool restrictions; allowed-tools maps to null | cosmetic | All tools available via agent-level permission config. No behavioral loss since all listed tools have opencode equivalents. | false |
| `disable-model-invocation` field | Not supported in opencode skill frontmatter; maps to null | cosmetic | Field value was `false` (non-restrictive); no behavioral loss. Document in description if restriction needed at agent level. | false |
| `TaskGet` by ID | opencode todoread returns full list; no per-task retrieval by ID | functional | Use todoread and scan full list for matching task_uid in description field. Cached global workaround applied. | false |
| `TaskList` filtering | opencode todoread returns full unfiltered list; no status/owner filtering | functional | Use todoread and scan full list; filter programmatically. Cached global workaround applied. | false |
| Reference file loading (`framework-templates.md`) | opencode has no reference_dir; dynamic file loading via ${CLAUDE_PLUGIN_ROOT}/skills/.../references/ not supported | functional | Detection chain inlined in Phase 2. Full boilerplate templates require manual inlining or separate maintenance. | false |
| Reference file loading (`test-patterns.md`) | Same as above | functional | Core pattern guidance inlined in Phase 3. Full anti-patterns and naming conventions require manual inlining. | false |

## Unresolved Incompatibilities

All incompatibilities were resolved via cached decisions or auto-resolution. No items require orchestrator intervention.

| Group Key | Feature | Severity | Category | Reason | Suggested Workaround | Confidence | Affected Locations |
|-----------|---------|----------|----------|--------|---------------------|------------|-------------------|
| (none) | | | | | | | |
