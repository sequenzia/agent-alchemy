# Coverage Patterns Reference

This reference documents framework-specific coverage tool integration for the `analyze-coverage` skill. It covers tool detection, command execution, report parsing, gap analysis, and spec-to-coverage mapping for Python (pytest-cov) and TypeScript (istanbul/c8) projects.

---

## Installation Detection

Before running coverage tools, detect whether the required packages are installed.

### Python: pytest-cov

Check for `pytest-cov` in the following locations (stop at first match):

```
1. pyproject.toml  --> look for "pytest-cov" in [project.dependencies] or [project.optional-dependencies]
2. requirements.txt / requirements-dev.txt  --> look for "pytest-cov" line
3. setup.py / setup.cfg  --> look for "pytest-cov" in install_requires or extras_require
4. pip list output  --> run `pip list | grep pytest-cov`
```

**Detection commands:**
```bash
# Check pyproject.toml
grep -i "pytest-cov" pyproject.toml

# Check requirements files
grep -i "pytest-cov" requirements*.txt

# Check installed packages
pip list 2>/dev/null | grep -i pytest-cov
```

**If not installed:**
```
pytest-cov is not installed. Install it with:

  pip install pytest-cov

Or add "pytest-cov" to your dev dependencies in pyproject.toml:

  [project.optional-dependencies]
  dev = ["pytest-cov"]
```

### TypeScript: istanbul / c8

Check `package.json` for coverage tool packages:

```
1. package.json devDependencies --> look for "c8", "@vitest/coverage-v8", "@vitest/coverage-istanbul"
2. package.json devDependencies --> look for "jest" (Jest has built-in istanbul coverage)
3. node_modules/.bin/c8         --> check if c8 binary exists
```

**Detection commands:**
```bash
# Check package.json for coverage tools
grep -E '"c8"|"@vitest/coverage-v8"|"@vitest/coverage-istanbul"' package.json

# Check if Jest is present (has built-in coverage)
grep '"jest"' package.json

# Check if c8 binary is available
npx c8 --version 2>/dev/null
```

**If not installed:**

For Vitest projects:
```
Coverage tool not detected. Install the Vitest coverage provider:

  npm install -D @vitest/coverage-v8

Or for istanbul-based coverage:

  npm install -D @vitest/coverage-istanbul
```

For Jest projects:
```
Jest includes istanbul coverage by default. No additional installation required.
Run with: npx jest --coverage
```

For standalone c8:
```
c8 is not installed. Install it with:

  npm install -D c8
```

---

## Python / pytest-cov

### Running Coverage

**Basic command:**
```bash
pytest --cov={package} --cov-report=term-missing --cov-report=json
```

**Flag explanations:**

| Flag | Purpose |
|------|---------|
| `--cov={package}` | Measure coverage for the specified package/directory |
| `--cov-report=term-missing` | Print coverage summary with missed line numbers to terminal |
| `--cov-report=json` | Generate machine-readable JSON report |
| `--cov-branch` | Enable branch coverage measurement (recommended) |
| `--cov-fail-under=80` | Fail if coverage falls below threshold |

**Full recommended command:**
```bash
pytest --cov={package} --cov-report=term-missing --cov-report=json --cov-branch
```

**With specific test directories:**
```bash
pytest tests/ --cov={package} --cov-report=term-missing --cov-report=json --cov-branch
```

**Multiple test directories (aggregate coverage):**
```bash
pytest tests/unit tests/integration --cov={package} --cov-report=term-missing --cov-report=json --cov-branch
```

### Configuration

pytest-cov can be configured in `pyproject.toml` or `.coveragerc`:

**pyproject.toml:**
```toml
[tool.pytest.ini_options]
addopts = "--cov=mypackage --cov-report=term-missing"

[tool.coverage.run]
source = ["mypackage"]
branch = true
omit = [
    "*/tests/*",
    "*/migrations/*",
    "*/__pycache__/*",
]

[tool.coverage.report]
fail_under = 80
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "if __name__ == .__main__.",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
```

**.coveragerc:**
```ini
[run]
source = mypackage
branch = True
omit =
    */tests/*
    */migrations/*

[report]
fail_under = 80
show_missing = True
```

### JSON Report Location

The JSON report is written to `coverage.json` in the current working directory (or as specified by `--cov-report=json:path/to/report.json`).

The binary `.coverage` file is also produced by pytest-cov and can be used by the `coverage` CLI tool for further analysis.

### Parsing the JSON Report

The `coverage.json` file has this structure:

```json
{
  "meta": {
    "version": "7.4.0",
    "timestamp": "2026-01-15T10:30:00",
    "branch_coverage": true,
    "show_contexts": false
  },
  "files": {
    "mypackage/module.py": {
      "executed_lines": [1, 2, 3, 5, 6, 10, 11],
      "summary": {
        "covered_lines": 7,
        "num_statements": 12,
        "percent_covered": 58.33,
        "percent_covered_display": "58%",
        "missing_lines": 5,
        "excluded_lines": 0,
        "num_branches": 4,
        "num_partial_branches": 1,
        "covered_branches": 3,
        "missing_branches": 1
      },
      "missing_lines": [7, 8, 9, 13, 14],
      "excluded_lines": []
    }
  },
  "totals": {
    "covered_lines": 150,
    "num_statements": 200,
    "percent_covered": 75.0,
    "percent_covered_display": "75%",
    "missing_lines": 50,
    "excluded_lines": 5,
    "num_branches": 40,
    "num_partial_branches": 5,
    "covered_branches": 30,
    "missing_branches": 10
  }
}
```

**Key fields to extract per file:**

| Field | Description |
|-------|-------------|
| `summary.num_statements` | Total executable statements |
| `summary.covered_lines` | Statements executed during tests |
| `summary.missing_lines` | Statements not executed |
| `summary.percent_covered` | Coverage percentage (0-100) |
| `summary.num_branches` | Total branches (if branch coverage enabled) |
| `summary.covered_branches` | Branches taken during tests |
| `summary.num_partial_branches` | Branches only partially covered |
| `missing_lines` | Array of line numbers not covered |
| `executed_lines` | Array of line numbers executed |

**Parsing procedure:**
1. Read `coverage.json` from the project root
2. Iterate `files` to get per-file coverage data
3. Extract `totals` for project-wide summary
4. Collect `missing_lines` arrays for gap analysis
5. Compare `totals.percent_covered` against the configured threshold

### Common Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| Package path not matching | `Coverage.py warning: No data was collected` | Verify `--cov={package}` matches the actual importable package name, not the directory path |
| Source not found | `CoverageWarning: Module X was never imported` | Check that the package is importable from the test directory. May need `--cov-config` or `source` setting |
| Missing `__init__.py` | Coverage reports 0% for some modules | Ensure all packages have `__init__.py` (or use `--import-mode=importlib`) |
| Virtual env included | Coverage includes venv/site-packages | Add `omit = ["*/site-packages/*", ".venv/*"]` to config |
| Tests included in coverage | Test files appear in coverage report | Add `omit = ["*/tests/*", "test_*"]` to config |

---

## TypeScript / istanbul (c8)

### Running Coverage

Coverage commands depend on the test runner:

**Vitest with c8 (recommended):**
```bash
npx vitest run --coverage --coverage.reporter=json --coverage.reporter=text
```

**Vitest with explicit c8:**
```bash
npx c8 --reporter=json --reporter=text npx vitest run
```

**Jest (built-in istanbul):**
```bash
npx jest --coverage --coverageReporters=json --coverageReporters=text
```

**Flag explanations:**

| Runner | Flag | Purpose |
|--------|------|---------|
| Vitest | `--coverage` | Enable coverage collection |
| Vitest | `--coverage.reporter=json` | Generate JSON report |
| Vitest | `--coverage.reporter=text` | Print terminal summary |
| c8 | `--reporter=json` | Generate JSON report |
| c8 | `--reporter=text` | Print terminal summary |
| Jest | `--coverage` | Enable istanbul coverage |
| Jest | `--coverageReporters=json` | Generate JSON report |
| Jest | `--coverageReporters=text` | Print terminal summary |

**Multiple test directories (aggregate coverage):**

Vitest:
```bash
npx vitest run --coverage --coverage.reporter=json --coverage.include='src/**/*.ts'
```

Jest:
```bash
npx jest --coverage --coverageReporters=json --roots='["<rootDir>/tests/unit", "<rootDir>/tests/integration"]'
```

### Configuration

**Vitest (`vitest.config.ts`):**
```typescript
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    coverage: {
      provider: "v8",          // or "istanbul"
      reporter: ["text", "json", "html"],
      include: ["src/**/*.ts"],
      exclude: [
        "**/*.test.ts",
        "**/*.spec.ts",
        "**/node_modules/**",
        "**/dist/**",
      ],
      thresholds: {
        statements: 80,
        branches: 80,
        functions: 80,
        lines: 80,
      },
    },
  },
});
```

**Jest (`package.json` or `jest.config.ts`):**

In `package.json`:
```json
{
  "jest": {
    "collectCoverageFrom": [
      "src/**/*.{ts,tsx}",
      "!src/**/*.test.{ts,tsx}",
      "!src/**/*.spec.{ts,tsx}"
    ],
    "coverageThreshold": {
      "global": {
        "statements": 80,
        "branches": 80,
        "functions": 80,
        "lines": 80
      }
    },
    "coverageReporters": ["text", "json", "lcov"]
  }
}
```

In `jest.config.ts`:
```typescript
export default {
  collectCoverageFrom: [
    "src/**/*.{ts,tsx}",
    "!src/**/*.test.{ts,tsx}",
  ],
  coverageThreshold: {
    global: {
      statements: 80,
      branches: 80,
      functions: 80,
      lines: 80,
    },
  },
  coverageReporters: ["text", "json", "lcov"],
};
```

### JSON Report Location

| Tool | Default Location |
|------|-----------------|
| Vitest (v8/istanbul) | `coverage/coverage-final.json` |
| Jest | `coverage/coverage-final.json` |
| c8 (standalone) | `coverage/coverage-final.json` |

The location can be customized:
- Vitest: `coverage.reportsDirectory` in `vitest.config.ts`
- Jest: `coverageDirectory` in Jest config
- c8: `--reports-dir` flag

### Parsing the JSON Report

The `coverage-final.json` file uses the istanbul format:

```json
{
  "/absolute/path/to/src/module.ts": {
    "path": "/absolute/path/to/src/module.ts",
    "statementMap": {
      "0": { "start": { "line": 1, "column": 0 }, "end": { "line": 1, "column": 35 } },
      "1": { "start": { "line": 3, "column": 0 }, "end": { "line": 5, "column": 1 } }
    },
    "s": {
      "0": 1,
      "1": 5
    },
    "branchMap": {
      "0": {
        "type": "if",
        "locations": [
          { "start": { "line": 4, "column": 2 }, "end": { "line": 4, "column": 20 } },
          { "start": { "line": 6, "column": 2 }, "end": { "line": 6, "column": 20 } }
        ],
        "line": 4
      }
    },
    "b": {
      "0": [3, 2]
    },
    "fnMap": {
      "0": {
        "name": "calculateTotal",
        "decl": { "start": { "line": 3, "column": 16 }, "end": { "line": 3, "column": 30 } },
        "loc": { "start": { "line": 3, "column": 45 }, "end": { "line": 10, "column": 1 } },
        "line": 3
      }
    },
    "f": {
      "0": 5
    }
  }
}
```

**Key fields to extract per file:**

| Field | Description |
|-------|-------------|
| `s` | Statement execution counts (key = statement ID, value = execution count) |
| `statementMap` | Maps statement IDs to source locations |
| `b` | Branch execution counts (key = branch ID, value = array of counts per branch path) |
| `branchMap` | Maps branch IDs to source locations and types |
| `f` | Function execution counts (key = function ID, value = execution count) |
| `fnMap` | Maps function IDs to name and source location |

**Computing coverage metrics from istanbul format:**

```
Statements:
  total     = Object.keys(s).length
  covered   = Object.values(s).filter(count => count > 0).length
  percent   = (covered / total) * 100

Branches:
  total     = sum of all b[id].length
  covered   = sum of all b[id].filter(count => count > 0).length
  percent   = (covered / total) * 100

Functions:
  total     = Object.keys(f).length
  covered   = Object.values(f).filter(count => count > 0).length
  percent   = (covered / total) * 100

Lines:
  Derive from statementMap — group statements by line number
  total     = unique line count from statementMap
  covered   = lines where all statements on that line have count > 0
  percent   = (covered / total) * 100
```

**Parsing procedure:**
1. Read `coverage/coverage-final.json` from the project root
2. Iterate file entries (keys are absolute file paths)
3. For each file, compute statement, branch, function, and line coverage from `s`, `b`, `f` maps
4. Identify uncovered lines by finding statements where `s[id] === 0`
5. Identify uncovered functions by finding entries where `f[id] === 0`
6. Sum across all files for project-wide totals

### Common Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| Source maps misconfigured | Coverage mapped to wrong lines | Ensure `sourceMaps: true` in tsconfig and the coverage tool supports source map resolution |
| Monorepo path resolution | File paths in report are absolute and don't match project structure | Normalize paths relative to project root before analysis |
| TypeScript not transpiled | Coverage on compiled JS, not TS source | Use `@vitest/coverage-v8` which handles TS natively, or ensure Jest `transform` config is correct |
| `node_modules` included | Coverage report includes dependencies | Add `exclude` patterns: `["**/node_modules/**"]` |
| Test files in coverage | Test files appear in coverage report | Exclude test patterns: `["**/*.test.ts", "**/*.spec.ts"]` |

---

## Coverage Report Parsing

### Standard Fields

Regardless of framework, extract these fields for each file in the coverage report:

| Field | Python (pytest-cov) | TypeScript (istanbul) |
|-------|--------------------|-----------------------|
| File path | `files` key | Top-level key |
| Total lines/statements | `summary.num_statements` | `Object.keys(s).length` |
| Covered lines | `summary.covered_lines` | `Object.values(s).filter(n => n > 0).length` |
| Missed lines | `missing_lines` array | Statements where `s[id] === 0`, mapped via `statementMap` |
| Coverage percentage | `summary.percent_covered` | Computed: `(covered / total) * 100` |
| Branch total | `summary.num_branches` | Sum of `b[id].length` for all branches |
| Branch covered | `summary.covered_branches` | Sum of `b[id].filter(n => n > 0).length` |
| Functions total | N/A (not in default JSON) | `Object.keys(f).length` |
| Functions covered | N/A | `Object.values(f).filter(n => n > 0).length` |

### Gap Detection

Identify areas with zero or low coverage:

1. **Uncovered functions/methods**: Functions where execution count is 0
   - Python: Lines in `missing_lines` that correspond to function definitions
   - TypeScript: Entries in `f` where count is 0, mapped to names via `fnMap`

2. **Uncovered branches**: Branch paths never taken
   - Python: `summary.missing_branches` count, or `num_partial_branches > 0`
   - TypeScript: Entries in `b` where any element is 0

3. **Uncovered line ranges**: Contiguous blocks of missed lines indicate untested code paths
   - Group consecutive `missing_lines` into ranges for readable reporting
   - Example: `[15, 16, 17, 22, 23]` becomes `lines 15-17, 22-23`

### Threshold Comparison

Compare coverage against the configured threshold:

```
Default threshold: 80% (configurable via .claude/agent-alchemy.local.md under tdd.coverage-threshold)

Per-file check:
  file.percent_covered >= threshold  --> PASS
  file.percent_covered < threshold   --> BELOW THRESHOLD

Project-wide check:
  totals.percent_covered >= threshold  --> PASS
  totals.percent_covered < threshold   --> BELOW THRESHOLD
```

Report files below threshold sorted by coverage (lowest first) to prioritize improvements.

---

## Coverage Gap Analysis

### Mapping Coverage to Spec Acceptance Criteria

When a spec path is provided, map coverage results against acceptance criteria to identify untested requirements:

**Procedure:**

1. **Parse the spec**: Read the spec file and extract acceptance criteria by category (Functional, Edge Cases, Error Handling, Performance)

2. **Map criteria to code locations**: For each criterion, identify the source files and functions that implement it. Use:
   - Grep for keywords from the criterion in the source code
   - Function/class names that match the criterion's subject
   - Comments or docstrings referencing the criterion

3. **Check coverage for mapped locations**: For each criterion-to-code mapping:
   - Look up the file in the coverage report
   - Check if the mapped lines/functions have coverage > 0
   - If all mapped locations are covered: criterion is **tested**
   - If any mapped locations are uncovered: criterion is **untested** or **partially tested**

4. **Report untested criteria**: List acceptance criteria where the implementing code has no coverage, indicating tests are missing for that requirement

**Example mapping output:**
```
Spec: user-auth-SPEC.md

Functional Criteria:
  [TESTED]   "User can register with email and password"
             -> src/auth/register.py:register_user (92% covered)
  [UNTESTED] "User receives email verification link"
             -> src/auth/email.py:send_verification (0% covered)
  [PARTIAL]  "User can login with valid credentials"
             -> src/auth/login.py:authenticate (65% covered, missing error paths)

Edge Cases:
  [UNTESTED] "Duplicate email returns 409 Conflict"
             -> src/auth/register.py:register_user lines 45-52 (not covered)
```

### Prioritizing Coverage Gaps

When multiple gaps exist, prioritize by:

| Priority | Criteria | Rationale |
|----------|----------|-----------|
| **P0 - Critical** | Functional acceptance criteria with 0% coverage | Core features completely untested |
| **P1 - High** | Functions/methods with 0% coverage in critical paths | Dead or untested code in important areas |
| **P2 - Medium** | Branch coverage gaps (partial branches) | Happy path tested but error/edge paths missed |
| **P3 - Low** | Files below threshold but above 50% | Some coverage exists, needs improvement |

**Prioritization factors:**
- **Criticality**: P0 features and functional acceptance criteria first
- **Risk**: Complex code (high cyclomatic complexity, many branches) is more likely to contain bugs
- **Frequency**: Hot paths (code executed on every request) should have higher coverage
- **Blast radius**: Code shared by many callers should be well-tested

### Suggesting Tests for Uncovered Areas

For each coverage gap, suggest specific tests to write:

1. **Uncovered function**: Suggest a test that calls the function with typical inputs and verifies outputs
2. **Uncovered branch**: Identify the condition and suggest a test that triggers the untaken branch path
3. **Uncovered error path**: Suggest a test that triggers the error condition and verifies error handling
4. **Uncovered edge case**: Suggest a test with boundary inputs (empty, null, max values)

**Example suggestions:**
```
Gap: src/auth/email.py:send_verification (0% coverage)
Suggested tests:
  - test_send_verification_sends_email_with_correct_link
  - test_send_verification_raises_on_invalid_email
  - test_send_verification_handles_smtp_failure

Gap: src/auth/login.py:authenticate lines 30-35 (branch not covered)
  Branch condition: `if user.is_locked`
Suggested tests:
  - test_authenticate_rejects_locked_account
  - test_authenticate_returns_lockout_message
```

When the `/generate-tests` skill is available, recommend using it to automatically generate the suggested tests.

---

## Edge Cases

### Multiple Test Directories

Some projects split tests across multiple directories (e.g., `tests/unit/`, `tests/integration/`, `tests/e2e/`).

**Python:**
```bash
# Run all test directories with aggregated coverage
pytest tests/unit tests/integration --cov={package} --cov-report=json --cov-branch

# Or use pytest.ini / pyproject.toml to configure testpaths
# [tool.pytest.ini_options]
# testpaths = ["tests/unit", "tests/integration"]
```

**TypeScript (Vitest):**
```bash
# Vitest discovers tests based on include patterns in config
# Configure in vitest.config.ts:
# test: { include: ["tests/**/*.test.ts"] }
npx vitest run --coverage
```

**TypeScript (Jest):**
```bash
# Configure roots in jest.config.ts:
# roots: ["<rootDir>/tests/unit", "<rootDir>/tests/integration"]
npx jest --coverage
```

Coverage is automatically aggregated across all test files when run in a single command. Do not run separate coverage commands per directory as this produces separate reports that would need manual merging.

### No Tests Exist

When no test files are found in the project:

1. Run the coverage command anyway to confirm 0% coverage
2. Report: `No test files detected. Coverage: 0%`
3. Recommend: `Use /generate-tests to create an initial test suite based on your source code and acceptance criteria`
4. If a spec is provided, report all acceptance criteria as **untested**

**Detection:**
```bash
# Python
find . -name "test_*.py" -o -name "*_test.py" | head -1

# TypeScript
find . -name "*.test.ts" -o -name "*.spec.ts" -o -name "*.test.tsx" -o -name "*.spec.tsx" | head -1
```

If no test files are found, skip the coverage tool execution and report directly.

### Coverage Tool Not Installed

When the coverage tool is not detected (see Installation Detection above):

1. Report: `Coverage tool not detected for this project type`
2. Identify the project type (Python/TypeScript) from project files
3. Suggest the appropriate installation command
4. Do not attempt to run coverage commands without the tool installed
5. If other analysis is possible (e.g., static analysis of test file existence), provide that as a fallback

**Fallback analysis when tool is unavailable:**
- Count test files and estimate test coverage breadth
- Check for test files corresponding to each source file
- Report which source files have no corresponding test file
- Note: This is a rough heuristic, not a substitute for actual coverage measurement
