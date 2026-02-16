# Framework Templates Reference

This reference provides the test framework auto-detection chain and copy-pasteable boilerplate templates for supported frameworks (pytest, Jest, Vitest). Used by the `generate-tests` skill to produce correctly structured test files.

---

## Framework Auto-Detection Chain

Detect the project's test framework by checking files in priority order. Stop at the first confident match.

### Detection Priority Order

```
1. Config-file detection (highest confidence)
   ├── pyproject.toml / setup.cfg  --> check for [tool.pytest] or pytest config
   ├── package.json                --> check dependencies for jest/vitest/mocha
   ├── jest.config.*               --> Jest
   ├── vitest.config.*             --> Vitest
   └── conftest.py                 --> pytest

2. Existing test file detection (medium confidence)
   ├── test_*.py / *_test.py       --> pytest
   ├── *.test.ts / *.test.tsx      --> Jest or Vitest (check config to disambiguate)
   ├── *.spec.ts / *.spec.tsx      --> Jest or Vitest (check config to disambiguate)
   └── *.test.js / *.spec.js       --> Jest or Vitest

3. Settings fallback (low confidence)
   └── .claude/agent-alchemy.local.md --> framework setting

4. User prompt (no detection)
   └── AskUserQuestion --> "Which test framework does this project use?"
```

### Step 1: Config-File Detection

#### Python Projects

**Check `pyproject.toml`:**
```
[tool.pytest.ini_options]    --> pytest detected
```

```
[tool.pytest]                --> pytest detected
```

**Check `setup.cfg`:**
```
[tool:pytest]                --> pytest detected
```

**Check `pytest.ini`:**
File exists --> pytest detected

**Check `conftest.py` at project root or in `tests/`:**
File exists --> pytest detected

#### TypeScript/JavaScript Projects

**Check `package.json` dependencies and devDependencies:**
```json
"vitest"    --> Vitest detected (takes priority over Jest if both present)
"jest"      --> Jest detected
"mocha"     --> Mocha detected (unsupported — warn user)
"@jest/core" --> Jest detected
```

**Check for config files via glob:**
```
vitest.config.* (ts, js, mts, mjs)  --> Vitest detected
jest.config.* (ts, js, mjs, cjs)    --> Jest detected
```

**Check `package.json` for inline config:**
```json
"jest": { ... }     --> Jest detected
```

#### Disambiguation: Jest vs Vitest

When `.test.ts` or `.spec.ts` files exist but framework is unclear:
1. Check for `vitest.config.*` --> Vitest
2. Check for `jest.config.*` --> Jest
3. Check `package.json` devDependencies --> whichever is listed
4. Check import statements in existing test files:
   - `import { describe, it, expect } from "vitest"` --> Vitest
   - `import { jest } from "@jest/globals"` --> Jest
   - No explicit imports --> likely Jest (global types)

### Step 2: Test Directory Convention Detection

Scan for standard test directory patterns:

| Directory | Convention | Language |
|-----------|-----------|----------|
| `tests/` | Python standard, also common in TS | Python, TypeScript |
| `test/` | Common in Node.js projects | TypeScript, JavaScript |
| `__tests__/` | Jest default convention | TypeScript, JavaScript |
| `spec/` | RSpec-inspired, used by some JS projects | TypeScript, JavaScript |
| `src/**/__tests__/` | Colocated Jest tests | TypeScript, JavaScript |
| `src/**/*.test.ts` | Colocated Vitest/Jest tests | TypeScript |

**Detection logic:**
1. Glob for test directories at project root: `tests/`, `test/`, `__tests__/`, `spec/`
2. Glob for colocated test files: `src/**/*.test.{ts,tsx,js,jsx}`, `src/**/*.spec.{ts,tsx,js,jsx}`
3. If both exist, note both patterns — the project may use dedicated directories for integration/e2e and colocated files for unit tests

### Step 3: Test File Naming Patterns

| Framework | Primary Pattern | Alternative Pattern |
|-----------|----------------|-------------------|
| pytest | `test_*.py` | `*_test.py` |
| Jest | `*.test.ts` / `*.test.tsx` | `*.spec.ts` / `*.spec.tsx` |
| Vitest | `*.test.ts` / `*.test.tsx` | `*.spec.ts` / `*.spec.tsx` |

**Detection:** Glob for existing test files and use the pattern that matches the majority. If no existing tests, use the primary pattern for the detected framework.

### Step 4: Assertion Library Detection

| Framework | Default Assertions | Alternative |
|-----------|-------------------|-------------|
| pytest | `assert` (native) | `pytest.raises`, `pytest.approx` |
| Jest | `expect()` (built-in) | `@testing-library/jest-dom` (DOM matchers) |
| Vitest | `expect()` (Chai-compatible) | `@testing-library/jest-dom` |

**Detection for TypeScript projects:**
Check `package.json` for:
- `@testing-library/react` --> React Testing Library patterns
- `@testing-library/jest-dom` --> Extended DOM matchers
- `supertest` --> HTTP integration testing
- `nock` or `msw` --> HTTP mocking library

### Step 5: Fixture Detection

**pytest:**
- Scan `conftest.py` files for `@pytest.fixture` definitions
- Note fixture names and scopes for reuse in generated tests
- Check for common fixture libraries: `pytest-factoryboy`, `pytest-asyncio`, `pytest-mock`

**Jest/Vitest:**
- Check for test utility files: `test-utils.ts`, `setup.ts`, `test-helpers.ts`
- Check for `setupFilesAfterSetup` in Jest config
- Check for `setupFiles` in Vitest config
- Scan for factory/builder patterns in test directories

### Step 6: Settings Fallback

When auto-detection fails or is ambiguous, check `.claude/agent-alchemy.local.md`:

```yaml
---
tdd:
  framework: pytest          # or jest, vitest, auto
---
```

If `tdd.framework` is set to a recognized value (`pytest`, `jest`, `vitest`), use it. If set to `auto` or an unrecognized value, fall through to Step 7. If the settings file does not exist or lacks framework configuration, fall through to Step 7.

### Step 7: User Prompt Fallback

When all detection methods fail, prompt the user:

```
AskUserQuestion: "No test framework detected. Which framework does this project use?"
Options: pytest, Jest, Vitest, Other
```

If user selects "Other", warn that generated tests may need manual adjustment and default to the closest supported framework.

---

## Edge Case: Monorepo Detection

In monorepos, different packages may use different frameworks. Detect per-directory:

```
monorepo/
├── packages/
│   ├── api/                 # Python — pytest
│   │   ├── pyproject.toml
│   │   └── tests/
│   ├── web/                 # TypeScript — Vitest
│   │   ├── vitest.config.ts
│   │   └── src/__tests__/
│   └── shared/              # TypeScript — Jest
│       ├── jest.config.ts
│       └── __tests__/
├── package.json             # Root — may list workspace tools
└── pyproject.toml           # Root — may list workspace tools
```

**Monorepo detection logic:**
1. Check if the target file's nearest parent directory has its own config files
2. Walk up the directory tree until a config file is found
3. Use the nearest config, not the root config
4. If generating tests for `packages/web/src/utils.ts`, detect Vitest from `packages/web/vitest.config.ts`

**Workspace indicators:**
- `package.json` with `"workspaces"` field
- `pnpm-workspace.yaml`
- `lerna.json`
- `pyproject.toml` with `[tool.hatch.envs]` or similar workspace config

## Edge Case: No Config Files

When no config files exist and no test files are present:

1. **Check file extensions** in the project:
   - `.py` files present --> default to pytest
   - `.ts`/`.tsx` files present --> default to Vitest (modern default for new TS projects)
   - `.js`/`.jsx` files present --> default to Jest
2. **Check for build tools** that hint at ecosystem:
   - `vite.config.*` present --> Vitest (strong signal)
   - `webpack.config.*` or `next.config.*` --> Jest
   - `tsconfig.json` without bundler hints --> default to Vitest
3. **Document the inference** in test file headers:
   ```python
   # Framework: pytest (inferred — no config file detected)
   # To configure explicitly, add [tool.pytest.ini_options] to pyproject.toml
   ```

## Edge Case: Mixed Language Projects

Projects with both Python and TypeScript code:

1. Detect framework independently for each language
2. Generate tests in the appropriate framework for the source file's language
3. Common patterns:
   - Python backend + TypeScript frontend: pytest for `api/`, Vitest/Jest for `web/`
   - Python CLI + TypeScript extension: pytest for Python, framework from config for TypeScript
4. Use the nearest config file to the target source file to determine framework

---

## Boilerplate Templates

### pytest Template

```python
"""Tests for {module_name}.

Tests cover the public API of {module_name}, verifying behavior
described in the acceptance criteria.
"""

import pytest
from {import_path} import {class_or_function}


# --- Fixtures ---

@pytest.fixture
def {fixture_name}():
    """Create a {description} for testing."""
    return {factory_or_constructor}


# --- Functional Tests ---

class TestClassName:
    """Tests for {ClassName}."""

    def test_{behavior_description}(self, {fixture_name}):
        """Verify that {expected behavior}."""
        # Arrange
        {setup_code}

        # Act
        result = {action}

        # Assert
        assert result == {expected}

    def test_{another_behavior}(self, {fixture_name}):
        """Verify that {expected behavior}."""
        # Arrange
        {setup_code}

        # Act
        result = {action}

        # Assert
        assert result == {expected}


# --- Edge Case Tests ---

class TestClassNameEdgeCases:
    """Edge case tests for {ClassName}."""

    def test_{edge_case_description}(self, {fixture_name}):
        """Verify behavior when {edge condition}."""
        # Arrange
        {setup_code}

        # Act
        result = {action}

        # Assert
        assert result == {expected}

    @pytest.mark.parametrize("input_val,expected", [
        ({input_1}, {expected_1}),
        ({input_2}, {expected_2}),
        ({input_3}, {expected_3}),
    ])
    def test_{parameterized_behavior}(self, input_val, expected):
        """Verify {behavior} across multiple inputs."""
        result = {function}(input_val)
        assert result == expected


# --- Error Handling Tests ---

class TestClassNameErrors:
    """Error handling tests for {ClassName}."""

    def test_{error_scenario}(self, {fixture_name}):
        """Verify that {error condition} raises {ErrorType}."""
        with pytest.raises({ErrorType}, match="{error_message_pattern}"):
            {action_that_raises}

    def test_{another_error_scenario}(self):
        """Verify that {error condition} is handled gracefully."""
        result = {action_with_invalid_input}
        assert result.is_error
        assert "{expected_message}" in result.message
```

### Jest Template

```typescript
/**
 * Tests for {ModuleName}.
 *
 * Tests cover the public API of {ModuleName}, verifying behavior
 * described in the acceptance criteria.
 */

import { {ClassOrFunction} } from "../{import_path}";

// --- Mocks ---

jest.mock("../{dependency_path}", () => ({
  {MockedDependency}: jest.fn().mockImplementation(() => ({
    {method}: jest.fn(),
  })),
}));

// --- Test Data ---

function create{EntityName}(overrides: Partial<{EntityType}> = {}): {EntityType} {
  return {
    id: "test-id",
    name: "Test Name",
    createdAt: new Date("2026-01-01"),
    ...overrides,
  };
}

// --- Tests ---

describe("{ClassOrModuleName}", () => {
  let {instanceName}: {ClassOrType};

  beforeEach(() => {
    jest.clearAllMocks();
    {instanceName} = new {ClassOrFunction}({dependencies});
  });

  // --- Functional Tests ---

  describe("{methodName}", () => {
    it("{behavior description}", async () => {
      // Arrange
      const input = create{EntityName}({overrides});

      // Act
      const result = await {instanceName}.{methodName}(input);

      // Assert
      expect(result).toBeDefined();
      expect(result.{property}).toBe({expected});
    });

    it("{another behavior}", () => {
      // Arrange
      const input = {setupData};

      // Act
      const result = {instanceName}.{methodName}(input);

      // Assert
      expect(result).toEqual({expected});
    });
  });

  // --- Edge Case Tests ---

  describe("edge cases", () => {
    it("handles empty input", () => {
      const result = {instanceName}.{methodName}({emptyInput});
      expect(result).toEqual({expectedDefault});
    });

    it("handles null values gracefully", () => {
      const result = {instanceName}.{methodName}(null as any);
      expect(result).toBeNull();
    });

    it.each([
      [{input1}, {expected1}],
      [{input2}, {expected2}],
      [{input3}, {expected3}],
    ])("handles %s correctly", (input, expected) => {
      const result = {instanceName}.{methodName}(input);
      expect(result).toBe(expected);
    });
  });

  // --- Error Handling Tests ---

  describe("error handling", () => {
    it("throws on invalid input", () => {
      expect(() => {
        {instanceName}.{methodName}({invalidInput});
      }).toThrow({ExpectedError});
    });

    it("throws descriptive error for {scenario}", async () => {
      await expect(
        {instanceName}.{methodName}({badInput})
      ).rejects.toThrow("{expected error message}");
    });

    it("returns error result when {condition}", async () => {
      const result = await {instanceName}.{methodName}({input});
      expect(result.ok).toBe(false);
      expect(result.error).toContain("{expected message}");
    });
  });
});
```

### Vitest Template

```typescript
/**
 * Tests for {ModuleName}.
 *
 * Tests cover the public API of {ModuleName}, verifying behavior
 * described in the acceptance criteria.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { {ClassOrFunction} } from "../{import_path}";

// --- Mocks ---

vi.mock("../{dependency_path}", () => ({
  {MockedDependency}: vi.fn().mockImplementation(() => ({
    {method}: vi.fn(),
  })),
}));

// --- Test Data ---

function create{EntityName}(overrides: Partial<{EntityType}> = {}): {EntityType} {
  return {
    id: "test-id",
    name: "Test Name",
    createdAt: new Date("2026-01-01"),
    ...overrides,
  };
}

// --- Tests ---

describe("{ClassOrModuleName}", () => {
  let {instanceName}: {ClassOrType};

  beforeEach(() => {
    vi.clearAllMocks();
    {instanceName} = new {ClassOrFunction}({dependencies});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  // --- Functional Tests ---

  describe("{methodName}", () => {
    it("{behavior description}", async () => {
      // Arrange
      const input = create{EntityName}({overrides});

      // Act
      const result = await {instanceName}.{methodName}(input);

      // Assert
      expect(result).toBeDefined();
      expect(result.{property}).toBe({expected});
    });

    it("{another behavior}", () => {
      // Arrange
      const input = {setupData};

      // Act
      const result = {instanceName}.{methodName}(input);

      // Assert
      expect(result).toEqual({expected});
    });
  });

  // --- Edge Case Tests ---

  describe("edge cases", () => {
    it("handles empty input", () => {
      const result = {instanceName}.{methodName}({emptyInput});
      expect(result).toEqual({expectedDefault});
    });

    it("handles null values gracefully", () => {
      const result = {instanceName}.{methodName}(null as any);
      expect(result).toBeNull();
    });

    it.each([
      [{input1}, {expected1}],
      [{input2}, {expected2}],
      [{input3}, {expected3}],
    ])("handles %s correctly", (input, expected) => {
      const result = {instanceName}.{methodName}(input);
      expect(result).toBe(expected);
    });
  });

  // --- Error Handling Tests ---

  describe("error handling", () => {
    it("throws on invalid input", () => {
      expect(() => {
        {instanceName}.{methodName}({invalidInput});
      }).toThrow({ExpectedError});
    });

    it("throws descriptive error for {scenario}", async () => {
      await expect(
        {instanceName}.{methodName}({badInput})
      ).rejects.toThrow("{expected error message}");
    });

    it("returns error result when {condition}", async () => {
      const result = await {instanceName}.{methodName}({input});
      expect(result.ok).toBe(false);
      expect(result.error).toContain("{expected message}");
    });
  });
});
```

---

## Framework-Specific Configuration Reference

### pytest Configuration (pyproject.toml)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks integration tests",
    "e2e: marks end-to-end tests",
]
```

### Jest Configuration (jest.config.ts)

```typescript
import type { Config } from "jest";

const config: Config = {
  preset: "ts-jest",
  testEnvironment: "node",
  roots: ["<rootDir>/src", "<rootDir>/tests"],
  testMatch: ["**/*.test.ts", "**/*.spec.ts"],
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/src/$1",
  },
  coverageDirectory: "coverage",
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};

export default config;
```

### Vitest Configuration (vitest.config.ts)

```typescript
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    environment: "node",
    include: ["src/**/*.test.ts", "tests/**/*.test.ts"],
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      thresholds: {
        branches: 80,
        functions: 80,
        lines: 80,
        statements: 80,
      },
    },
  },
});
```

---

## Detection Chain Summary

This table summarizes the complete detection chain from highest to lowest confidence:

| Priority | Check | Detects | Confidence |
|----------|-------|---------|------------|
| 1 | `pyproject.toml` has `[tool.pytest]` | pytest | High |
| 2 | `setup.cfg` has `[tool:pytest]` | pytest | High |
| 3 | `pytest.ini` exists | pytest | High |
| 4 | `vitest.config.*` exists | Vitest | High |
| 5 | `jest.config.*` exists | Jest | High |
| 6 | `package.json` has `vitest` in devDependencies | Vitest | High |
| 7 | `package.json` has `jest` in devDependencies | Jest | High |
| 8 | `package.json` has `"jest": {}` config section | Jest | High |
| 9 | `conftest.py` exists | pytest | Medium |
| 10 | `test_*.py` files exist | pytest | Medium |
| 11 | `*.test.ts` files with vitest imports | Vitest | Medium |
| 12 | `*.test.ts` files with jest imports | Jest | Medium |
| 13 | `*.test.ts` files exist (no clear imports) | Jest/Vitest | Low |
| 14 | `.claude/agent-alchemy.local.md` setting | Per config | Low |
| 15 | `vite.config.*` exists (no vitest config) | Vitest (inferred) | Low |
| 16 | Project has `.py` files only | pytest (inferred) | Low |
| 17 | Project has `.ts` files only | Vitest (inferred) | Low |
| 18 | AskUserQuestion prompt | Per user | Fallback |

---

## Fallback Strategy

When auto-detection fails completely (no config files, no test files, no settings):

1. **Check source language** of the file being tested:
   - Python file --> use pytest defaults
   - TypeScript/JavaScript file --> use Vitest defaults (modern default)
2. **Generate tests with a framework comment header:**
   ```python
   # Test framework: pytest (auto-detected from source language)
   # If this is incorrect, configure your framework in .claude/agent-alchemy.local.md
   ```
3. **Use conservative defaults:**
   - pytest: `tests/` directory, `test_*.py` naming, function-based tests (no class)
   - Vitest: `tests/` directory, `*.test.ts` naming, explicit imports from `vitest`
   - Jest: `__tests__/` directory, `*.test.ts` naming, global expect/describe/it
4. **Log the detection result** for debugging:
   ```
   Framework detection: pytest (source: pyproject.toml [tool.pytest.ini_options])
   Test directory: tests/ (source: existing directory)
   Naming pattern: test_*.py (source: existing files)
   ```
