# Command Template

Annotated starter template for OpenCode commands. Copy this file to `.opencode/commands/{your-command-name}.md` and customize.

---

## Template: Simple Command

For quick workflow shortcuts with minimal variables.

````markdown
[Instructions for what to do with $ARGUMENTS]
````

---

## Template: Full-Featured Command

For structured commands with multiple variables and model override.

````markdown
---
# OPTIONAL: Per-command model override in provider/model-id format.
# This is unique to commands — not available for skills or agents.
# Omit to use the session's current model.
# model: anthropic/claude-opus-4-6

# OPTIONAL: Shown in command list.
description: [What this command does]

# OPTIONAL: Which agent executes this command (by name).
# agent: my-agent-name

# OPTIONAL: Force execution as a subagent task.
# subtask: true
---

# [Command Name]

[Instructions for the task]

## Inputs

- Target: `$TARGET_PATH`
- Options: $OPTIONS

## Steps

1. [Step 1 using $TARGET_PATH]
2. [Step 2]
3. [Step 3]

## Output

[Describe expected output format]
````

---

## Notes

- **Name**: Derived from the filename (without `.md`). Invoked as `/{name}`.
- **$VARIABLES**: Any uppercase `$NAME` pattern auto-prompts the user for a value.
- **Model override**: Commands are the only extension type with per-invocation model control.
- **Keep it focused**: Commands should do one thing well.
- **Discovery**: Project commands in `.opencode/commands/`, global in `~/.config/opencode/commands/`.
