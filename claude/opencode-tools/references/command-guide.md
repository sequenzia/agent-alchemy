# OpenCode Command Guide

Reference for creating OpenCode commands. Commands are markdown template files that act as workflow shortcuts with `$VARIABLE` placeholders and optional per-command model overrides.

---

## File Format

Commands are markdown files in the commands directory:

```
.opencode/commands/{name}.md
```

The command name is derived from the filename (without `.md` extension). Commands are invoked as `/{name}` in the TUI.

### Optional YAML Frontmatter

```yaml
---
model: anthropic/claude-opus-4-6
description: Brief description of what this command does
---
```

### Frontmatter Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `model` | string | No | Session model | Per-command model override in `provider/model-id` format. Unique to commands — not available for skills. |
| `description` | string | No | — | Brief description shown in the command list. |

> **Note**: Commands are the only extension type that supports per-invocation `model` overrides. Skills and agents configure models at the agent level.

---

## $VARIABLE System

Commands use uppercase `$NAME` patterns as placeholders. OpenCode auto-detects them and prompts the user for input values.

### Syntax

```
$VARIABLE_NAME
```

- Must be uppercase letters, numbers, and underscores
- Auto-detected in the command body
- User is prompted for each unique variable when the command is invoked

### Built-in Variables

| Variable | Description |
|----------|-------------|
| `$ARGUMENTS` | Full argument string passed after the command name |
| `$1`, `$2`, `$3`... | Positional arguments (space-separated) |

### Custom Variables

Any `$UPPERCASE_NAME` pattern is treated as a variable:

```markdown
Review the file at `$FILE_PATH` and focus on `$REVIEW_TYPE` issues.
Output format: $OUTPUT_FORMAT
```

When invoked, the user is prompted for:
1. `FILE_PATH`
2. `REVIEW_TYPE`
3. `OUTPUT_FORMAT`

---

## Command Discovery

| Path | Scope |
|------|-------|
| `.opencode/commands/` | Project — available only in that project |
| `~/.config/opencode/commands/` | Global — available in all projects |

Commands are invoked as `/{filename}` (without `.md`). For example, `.opencode/commands/review.md` is invoked as `/review`.

---

## Use Cases

### Workflow Shortcuts

Frequently used multi-step processes packaged as a single command:

```markdown
---
description: Run the full CI pipeline locally
---

Run the following steps in order:

1. Run linting: `npm run lint`
2. Run type checking: `npm run typecheck`
3. Run tests: `npm test`
4. Build the project: `npm run build`

Report any failures with the specific error and suggested fix.
```

### Template-Driven Tasks

Structured prompts with variable placeholders:

```markdown
---
description: Generate a new component with tests
---

Create a new React component named `$COMPONENT_NAME` in `$DIRECTORY`:

1. Create the component file with TypeScript and proper types
2. Create a test file with basic render and interaction tests
3. Create a Storybook story file
4. Export from the directory index

Follow the existing patterns in the project.
```

### Model-Specific Operations

Commands that benefit from a specific model:

```markdown
---
model: anthropic/claude-opus-4-6
description: Perform deep architectural analysis
---

Analyze the architecture of $TARGET_DIRECTORY:

1. Map all modules and their dependencies
2. Identify circular dependencies
3. Evaluate coupling and cohesion
4. Suggest refactoring opportunities

Present findings with Mermaid diagrams.
```

### Scripted Operations

Commands that execute specific tool sequences:

```markdown
---
description: Clean up and prepare for release
---

Prepare the project for release:

1. Run `npm run lint -- --fix` to auto-fix lint issues
2. Run `npm test` to ensure tests pass
3. Run `npm run build` to verify build succeeds
4. Check for uncommitted changes with `git status`
5. If everything passes, report "Ready for release"
6. If anything fails, report what needs fixing
```

---

## Best Practices

### Naming

- Use kebab-case for filenames: `review-pr.md`, `create-component.md`
- Keep names short and descriptive
- Avoid generic names that conflict with built-in commands

### Content

- **Be specific** — Commands should produce predictable results
- **Use variables** for parts that change between invocations
- **Include context** — Tell the model what patterns to follow
- **Specify output format** — What should the result look like?

### Variable Design

- Use descriptive variable names: `$FILE_PATH` not `$F`
- Minimize required variables — each one is a prompt for the user
- Use `$ARGUMENTS` for simple single-value commands
- Use named variables for multi-input commands

### When to Use Commands vs Skills

| Use Command When | Use Skill When |
|------------------|----------------|
| Simple templates with variables | Complex multi-phase workflows |
| Need per-command model override | Reusable across different agents |
| Quick one-off workflows | Needs `user-invocable: false` option |
| User-facing shortcuts | Composed by other skills |

---

## Example: Minimal Command

```
.opencode/commands/hello.md
```

```markdown
Say hello to $NAME and ask how their day is going.
```

Invoked as `/hello` — user is prompted for `NAME`.

---

## Example: Full-Featured Command

```
.opencode/commands/migrate-api.md
```

```yaml
---
model: anthropic/claude-opus-4-6
description: Migrate an API endpoint from v1 to v2 format
---
```

```markdown
Migrate the API endpoint at `$ENDPOINT_PATH` from v1 to v2 format:

1. Read the current v1 endpoint implementation
2. Identify the request/response schemas
3. Apply v2 conventions:
   - Use camelCase for JSON fields
   - Add pagination support
   - Include proper error response format
4. Update the route registration
5. Update related tests
6. Verify the migration doesn't break existing tests

Target directory for v2: $TARGET_DIR
```
