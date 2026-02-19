# Agent Alchemy TDD Tools

Test-Driven Development tools for AI agents — test generation, RED-GREEN-REFACTOR workflows, and coverage analysis. Works standalone on any project or integrates with the SDD pipeline via `sdd-tools`.

## Skills

| Skill | Invocable | Description |
|-------|-----------|-------------|
| `/generate-tests` | Yes | Test generation from specs, acceptance criteria, or existing code. Spawns test-writer agents (Sonnet) to produce framework-specific test files. |
| `/tdd-cycle` | Yes | RED-GREEN-REFACTOR workflow orchestrator. Drives the 6-phase TDD cycle: write failing test, verify red, implement minimally, verify green, refactor, confirm green. |
| `/analyze-coverage` | Yes | Coverage analysis and gap detection. Runs coverage tools (pytest-cov, istanbul/c8), identifies untested paths, and recommends additional tests. |
| `/create-tdd-tasks` | Yes | Transform SDD tasks into test-first TDD task pairs. Reads existing tasks from `/create-tasks` and generates paired test tasks with RED-GREEN dependencies. |
| `/execute-tdd-tasks` | Yes | Execute TDD task pairs autonomously with RED-GREEN-REFACTOR verification. Routes TDD tasks to `tdd-executor` and non-TDD tasks to `task-executor` (from sdd-tools). |

## Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| `test-writer` | Sonnet | Parallel test generation worker. Produces framework-specific test files following project conventions. |
| `tdd-executor` | Opus | 6-phase RED-GREEN-REFACTOR executor. Manages the full TDD cycle for a single unit of work. |
| `test-reviewer` | Opus | Behavior-driven test quality reviewer. Evaluates tests for clarity, coverage, and alignment with acceptance criteria. |

## How It Works

The TDD tools provide three complementary capabilities:

1. **Test Generation** (`generate-tests`): Analyzes specs or code and spawns test-writer agents to produce test files. Supports pytest, Jest, and Vitest.
2. **TDD Cycle** (`tdd-cycle`): Orchestrates the RED-GREEN-REFACTOR loop, ensuring tests fail before implementation and pass after.
3. **Coverage Analysis** (`analyze-coverage`): Runs coverage tools, parses reports, identifies gaps, and suggests targeted tests for uncovered paths.

### SDD Pipeline Integration

When used with `sdd-tools`, the TDD workflow extends the spec-to-implementation pipeline:

```
/create-spec  -->  specs/SPEC-{name}.md          (sdd-tools)
                        |
/create-tasks -->  Implementation tasks           (sdd-tools)
                        |
/create-tdd-tasks --> Test-first task pairs        (tdd-tools)
                        |
/execute-tdd-tasks --> TDD-aware execution         (tdd-tools)
        |
        +-- tdd-executor -----> RED-GREEN-REFACTOR (tdd-tools)
        +-- task-executor -----> Non-TDD tasks     (sdd-tools, soft dependency)
        +-- generate-tests ----> Test files         (tdd-tools)
        +-- analyze-coverage --> Coverage reports   (tdd-tools)
```

> **Soft dependency on sdd-tools:** `/execute-tdd-tasks` routes non-TDD tasks to the `task-executor` agent from `sdd-tools`. Since TDD tasks are always generated from SDD tasks via `/create-tasks`, `sdd-tools` is expected to be installed when these skills run.

## Settings

TDD behavior is configurable via `.claude/agent-alchemy.local.md` YAML frontmatter. All settings live under the `tdd:` key.

```yaml
tdd:
  framework: auto                    # auto | pytest | jest | vitest
  coverage-threshold: 80             # Minimum coverage percentage (0-100)
  strictness: normal                 # strict | normal | relaxed
  test-review-threshold: 70          # Minimum test quality score (0-100)
  test-review-on-generate: false     # Run test-reviewer after generate-tests
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `tdd.framework` | `string` | `auto` | Override auto-detection with explicit framework selection. Valid values: `auto`, `pytest`, `jest`, `vitest`. Invalid values fall back to `auto` (auto-detection chain). |
| `tdd.coverage-threshold` | `integer` | `80` | Target coverage percentage for `analyze-coverage` reports. Values outside 0-100 are clamped to the nearest bound. |
| `tdd.strictness` | `string` | `normal` | TDD strictness level affecting RED phase behavior in `tdd-cycle`. `strict`: RED phase failure is mandatory -- abort if tests pass before implementation. `normal`: RED phase failure is expected -- warn but continue. `relaxed`: RED phase is informational -- proceed regardless. |
| `tdd.test-review-threshold` | `integer` | `70` | Minimum score for test quality evaluation by `test-reviewer`. Tests scoring below this threshold are flagged for improvement. |
| `tdd.test-review-on-generate` | `boolean` | `false` | Whether to automatically run `test-reviewer` after `/generate-tests` completes. When enabled, generated tests are evaluated for quality before the report phase. |

**Defaults and error handling:**
- If `.claude/agent-alchemy.local.md` does not exist, all skills use the defaults listed above.
- If the YAML frontmatter is malformed, all skills use defaults and log a warning.
- If `tdd.framework` is set to an unrecognized value, skills fall back to auto-detection.
- If `tdd.coverage-threshold` is out of range, skills clamp it to 0-100.

**Which skills use which settings:**

| Setting | `tdd-cycle` | `generate-tests` | `analyze-coverage` |
|---------|:-----------:|:-----------------:|:-------------------:|
| `tdd.framework` | Yes | Yes | Yes |
| `tdd.coverage-threshold` | Yes | -- | Yes |
| `tdd.strictness` | Yes | -- | -- |
| `tdd.test-review-threshold` | -- | Yes | -- |
| `tdd.test-review-on-generate` | -- | Yes | -- |

## Hooks

| Hook | Event | Purpose |
|------|-------|---------|
| `auto-approve-session.sh` | `PreToolUse` (Write, Edit, Bash) | Auto-approves file operations within execution session directories. Timeout: 5s. Required by `/execute-tdd-tasks`. |

## Directory Structure

```
tdd-tools/
├── agents/
│   ├── test-writer.md             # Sonnet test generation worker
│   ├── tdd-executor.md            # Opus TDD cycle executor
│   └── test-reviewer.md           # Opus test quality reviewer
├── hooks/
│   ├── hooks.json                 # PreToolUse hook config
│   └── auto-approve-session.sh    # Session auto-approve script
├── skills/
│   ├── generate-tests/
│   │   ├── SKILL.md               # Test generation skill
│   │   └── references/
│   │       ├── test-patterns.md   # Framework-specific test patterns
│   │       └── framework-templates.md  # pytest, Jest, Vitest templates
│   ├── tdd-cycle/
│   │   ├── SKILL.md               # RED-GREEN-REFACTOR workflow
│   │   └── references/
│   │       └── tdd-workflow.md    # TDD phase definitions
│   ├── analyze-coverage/
│   │   ├── SKILL.md               # Coverage analysis skill
│   │   └── references/
│   │       └── coverage-patterns.md  # Coverage tool integration
│   ├── create-tdd-tasks/
│   │   ├── SKILL.md               # SDD-to-TDD transformation (687 lines)
│   │   └── references/
│   │       ├── tdd-decomposition-patterns.md
│   │       └── tdd-dependency-rules.md
│   └── execute-tdd-tasks/
│       ├── SKILL.md               # TDD-aware execution (630 lines)
│       └── references/
│           ├── tdd-execution-workflow.md
│           └── tdd-verification-patterns.md
└── README.md
```
