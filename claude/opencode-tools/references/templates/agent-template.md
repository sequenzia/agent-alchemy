# Agent Template

Annotated starter template for OpenCode agents. Copy this file to `.opencode/agents/{your-agent-name}.md` and customize.

---

## Template: Primary Agent

For interactive agents the user switches to via `@agent-name`.

````markdown
---
# REQUIRED: Shown in @-mention list and agent selection UI.
description: [What this agent specializes in]

# Agent mode: "primary" (interactive), "subagent" (spawned by task), "all" (both)
mode: primary

# Model in provider/model-id format. Omit to inherit session default.
model: anthropic/claude-sonnet-4-6

# OPTIONAL: Response randomness (0.0 = deterministic, 1.0 = creative)
# temperature: 0.7

# OPTIONAL: Max agentic iterations
# steps: 50

# OPTIONAL: TUI display color (hex or theme)
# color: "#4A90D9"

# OPTIONAL: Hide from @-mention list (still accessible by name)
# hidden: false

# Per-tool permissions: allow / ask / deny
# Boolean shorthand: true = allow, false = deny
permission:
  read: allow
  glob: allow
  grep: allow
  write: ask
  edit: ask
  bash: ask
---

# [Agent Name]

[1-2 sentence purpose statement]

## Context

[What this agent knows, its area of expertise, and constraints]

## Process

### Step 1: [Name]
[Instructions]

### Step 2: [Name]
[Instructions]

### Step 3: [Name]
[Instructions]

## Output Format

[What the agent should produce]

## Guidelines

1. [Guideline 1]
2. [Guideline 2]

## Constraints

- [What the agent should NOT do]
- [Boundaries and limitations]
````

---

## Template: Subagent

For agents spawned via `task({ command: "agent-name" })`.

````markdown
---
description: [What this subagent does when spawned]
mode: subagent
model: anthropic/claude-sonnet-4-6

# Read-only subagent example:
permission:
  read: allow
  glob: allow
  grep: allow
  write: deny
  edit: deny
  bash: deny
---

# [Subagent Name]

[Purpose statement — what this agent does when spawned]

## Input

You receive:
- [What's passed in the task prompt]
- [Expected parameters or context]

## Process

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Output

Return a structured report:
- **Summary**: [Key findings]
- **Details**: [Detailed analysis]
- **Recommendations**: [Suggested next steps]

## Important

- You are running as a subagent — you cannot ask the user questions
- All needed context must be in your prompt
- Be thorough but concise — your output goes back to the calling agent
````

---

## Notes

- **Name**: Derived from the filename (without `.md`). Use kebab-case.
- **Skills**: Not assignable to agents. All skills are available via the `skill` tool.
- **Question tool**: Only available in `primary` mode. Subagents must receive all info upfront.
- **Model config**: Can also be set in `opencode.json` under `agent.{name}.model`.
- **Permissions**: Last-match-wins for glob patterns. Be specific with deny rules.
