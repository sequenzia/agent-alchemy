# Configuration

Plugin behavior is configured via `.claude/agent-alchemy.local.md` — a YAML frontmatter file that is **not committed** to version control, allowing per-project or per-user settings.

## File Location

```
your-project/
└── .claude/
    └── agent-alchemy.local.md    # Plugin settings (gitignored)
```

## File Format

The file uses YAML frontmatter with nested key-value pairs:

```yaml
---
author: Your Name
spec-output-path: specs/
deep-analysis:
  - direct-approval: true
  - cross-skill-approval: false
execute-tasks:
  - max_parallel: 5
tdd:
  framework: auto
  coverage-threshold: 80
  strictness: normal
  test-review-threshold: 70
  test-review-on-generate: false
---
```

## Settings Reference

### Global Settings

| Setting | Used By | Default | Description |
|---------|---------|---------|-------------|
| `author` | sdd-tools | — | Author name for spec attribution and task metadata |
| `spec-output-path` | sdd-tools | `specs/` | Default directory for spec file output |

### Deep Analysis Settings

Under the `deep-analysis` key:

| Setting | Default | Description |
|---------|---------|-------------|
| `direct-approval` | `true` | Require user approval of the team plan when invoking `/deep-analysis` directly |
| `cross-skill-approval` | `false` | Require approval when deep-analysis is loaded by another skill |
| `cache-ttl-hours` | `24` | Hours before exploration cache expires. Set to `0` to disable caching. |
| `enable-checkpointing` | `true` | Write session checkpoints at phase boundaries for recovery |
| `enable-progress-indicators` | `true` | Display `[Phase N/6]` progress messages during execution |

### Task Execution Settings

Under the `execute-tasks` key:

| Setting | Default | Description |
|---------|---------|-------------|
| `max_parallel` | `5` | Maximum concurrent task-executor agents per wave. CLI `--max-parallel` takes precedence. Set to `1` for sequential execution. |

### TDD Settings

Under the `tdd` key:

| Setting | Default | Options | Description |
|---------|---------|---------|-------------|
| `framework` | `auto` | `auto`, `pytest`, `jest`, `vitest` | Override test framework auto-detection |
| `coverage-threshold` | `80` | `0`-`100` | Target coverage percentage for `/analyze-coverage` |
| `strictness` | `normal` | `strict`, `normal`, `relaxed` | RED phase enforcement level in TDD cycle |
| `test-review-threshold` | `70` | `0`-`100` | Minimum test quality score |
| `test-review-on-generate` | `false` | `true`, `false` | Auto-run test-reviewer after `/generate-tests` |

## Precedence Rules

Settings follow this precedence order (highest to lowest):

1. **CLI arguments** — e.g., `--max-parallel 3` overrides `execute-tasks.max_parallel`
2. **`.claude/agent-alchemy.local.md`** — project/user settings
3. **Built-in defaults** — hardcoded in each skill

!!! tip "Per-Project Customization"
    Since the settings file is gitignored, each developer can have their own preferences without affecting the team. This is useful for adjusting parallelism, approval requirements, or TDD strictness.

## Example Configurations

=== "Minimal"

    ```yaml
    ---
    author: Jane Smith
    ---
    ```

=== "Full Control"

    ```yaml
    ---
    author: Jane Smith
    spec-output-path: docs/specs/
    deep-analysis:
      - direct-approval: true
      - cross-skill-approval: true
      - cache-ttl-hours: 48
      - enable-checkpointing: true
    execute-tasks:
      - max_parallel: 3
    tdd:
      framework: vitest
      coverage-threshold: 90
      strictness: strict
      test-review-on-generate: true
    ---
    ```

=== "CI/Headless"

    ```yaml
    ---
    deep-analysis:
      - direct-approval: false
      - cross-skill-approval: false
      - enable-progress-indicators: false
    execute-tasks:
      - max_parallel: 1
    ---
    ```
