# OpenCode Agent Guide

Complete reference for creating OpenCode-compatible custom agents. Agents define personas with specific models, permissions, and system prompts that can be invoked interactively or as subagents.

---

## File Format

Agents are markdown files with YAML frontmatter:

```
.opencode/agents/{name}.md
```

The agent name is derived from the filename (without `.md` extension).

### YAML Frontmatter

```yaml
---
description: Clear description of what this agent does
mode: primary
model: anthropic/claude-sonnet-4-6
temperature: 0.7
steps: 50
color: "#4A90D9"
hidden: false
disable: false
tools: true
permission:
  read: allow
  glob: allow
  grep: allow
  write: ask
  edit: ask
  bash: ask
---
```

### Frontmatter Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `description` | string | **Yes** | — | Agent description. Shown in agent selection UI and `@`-mention list. |
| `mode` | string | No | `primary` | `primary` (interactive), `subagent` (spawned via `task`), or `all` (both). |
| `model` | string | No | Inherited | Model in `provider/model-id` format (e.g., `anthropic/claude-sonnet-4-6`). |
| `temperature` | number | No | Provider default | 0.0-1.0. Lower = more deterministic. |
| `steps` | number | No | — | Maximum agentic iterations before stopping. |
| `color` | string | No | — | Hex color (e.g., `#4A90D9`) or theme color for TUI display. |
| `hidden` | boolean | No | `false` | Hide from `@`-mention list. Agent is still accessible by name. |
| `disable` | boolean | No | `false` | Completely disable the agent. |
| `tools` | boolean/object | No | `true` | Boolean shorthand to enable/disable all tools, or use `permission` for granular control. |
| `permission` | object | No | — | Per-tool permission rules (see Permission System below). |

### Fields That DO NOT Exist

| Claude Code Field | Why Not | Alternative |
|-------------------|---------|-------------|
| `name` | Derived from filename | Name your file correctly |
| `skills` | Skills not assigned to agents | All skills accessible via `skill` tool at runtime |

---

## Agent Name Format

Names are derived from the filename and should use kebab-case:

```
^[a-z0-9]+(-[a-z0-9]+)*$
```

**Valid**: `code-explorer.md`, `test-runner.md`, `my-agent.md`
**Invalid**: `Code_Explorer.md`, `my agent.md`, `myAgent.md`

---

## Agent Modes

### Primary Mode (`mode: primary`)

Primary agents are interactive — the user can switch to them via `@agent-name` in the TUI.

- Full access to all tools including `question`
- Persistent across the session
- User can switch between primary agents freely

### Subagent Mode (`mode: subagent`)

Subagents are spawned via the `task` tool and run in isolated contexts.

- **Cannot use the `question` tool** — must receive all needed info in the prompt
- Each invocation starts fresh — no persistent state between calls
- Model determined by agent config, not per-task
- Spawned via: `task({ prompt: "...", command: "agent-name" })`

### All Mode (`mode: all`)

The agent works in both primary and subagent contexts. Use when the same persona should be available interactively and via `task` calls.

---

## Permission System

The `permission` field controls per-tool access with three levels:

| Level | Meaning |
|-------|---------|
| `allow` | Auto-approved, no user prompt |
| `ask` | Requires user approval each time |
| `deny` | Blocked entirely |

### Boolean Shorthand

```yaml
permission:
  write: false    # Equivalent to "deny"
  bash: true      # Equivalent to "allow"
  read: allow     # Explicit string form
```

### Glob Pattern Rules

Add file-specific or command-specific rules:

```yaml
permission:
  write: ask                    # Default: ask for writes
  "write:src/**": allow         # Auto-allow writes in src/
  "write:node_modules/**": deny # Block writes to node_modules/
  bash: ask                     # Default: ask for bash
  "bash:npm test": allow        # Auto-allow npm test
  "bash:rm -rf *": deny         # Block destructive commands
```

**Resolution**: Last-match-wins when multiple patterns match.

### Read-Only Agent Example

```yaml
permission:
  read: allow
  glob: allow
  grep: allow
  write: deny
  edit: deny
  bash: deny
  webfetch: deny
```

### Full-Access Agent Example

```yaml
permission:
  read: allow
  glob: allow
  grep: allow
  write: allow
  edit: allow
  bash: allow
  websearch: allow
  webfetch: allow
```

---

## JSON Config Alternative

Agents can also be configured in `opencode.json` under the `agent` key:

```jsonc
{
  "agent": {
    "my-agent": {
      "model": "anthropic/claude-sonnet-4-6",
      "description": "My custom agent",
      "temperature": 0.7,
      "steps": 50
    }
  }
}
```

The markdown file and JSON config are complementary:
- **Markdown file**: Full system prompt + frontmatter (preferred for custom agents)
- **JSON config**: Model overrides and basic settings (useful for built-in agent types)

---

## System Prompt (Body)

The markdown body below the frontmatter is the agent's system prompt. It defines the agent's behavior, personality, and instructions.

### Structure Best Practices

```markdown
# {Agent Name}

{1-2 sentence purpose statement}

## Context

{What this agent knows and what it's designed for}

## Process

### Phase 1: {Name}
{Instructions}

### Phase 2: {Name}
{Instructions}

## Output Format

{What the agent should produce}

## Guidelines

1. {Guideline 1}
2. {Guideline 2}

## Constraints

- {What the agent should NOT do}
```

### System Prompt Best Practices

1. **Clear purpose statement** — Start with what the agent does and why
2. **Structured phases** — For complex workflows, number your phases
3. **Tool usage guidance** — Tell the agent which tools to prefer
4. **Output format** — Specify what the result should look like
5. **Constraints** — Explicitly state what the agent should avoid
6. **Be concise** — The system prompt consumes context; keep it lean

---

## Subagent Considerations

When creating agents intended for `mode: subagent`:

### No Question Tool

Subagents cannot use the `question` tool. All user interaction must happen in the calling agent before spawning the subagent.

**Pattern**: The parent skill/agent gathers all needed info via `question`, then passes it in the `task` prompt:

```markdown
Use the `task` tool to spawn the analyzer:
- prompt: "Analyze {file_path} for {criteria}. User preferences: {preferences}"
- command: "code-analyzer"
```

### Isolated Context

Each `task` invocation starts a fresh context. Subagents cannot:
- Access previous conversation history
- Share state with other subagents
- Remember across invocations

**Pattern**: Pass all needed context in the prompt. For cross-agent context, the orchestrating skill must relay information.

### Model Selection

The subagent uses the model from its agent config, not from the `task` call. Configure per-agent models in `opencode.json`:

```jsonc
{
  "agent": {
    "code-explorer": {
      "model": "anthropic/claude-sonnet-4-6"
    }
  }
}
```

### Spawning Custom Agents

To spawn a custom agent via `task`:

```
task({
  prompt: "Your instructions here",
  command: "agent-name"
})
```

The `command` field specifies which agent definition to use. Without it, the default `task` agent type is used.

---

## Model Selection Guide

| Tier | Model ID | Use When |
|------|----------|----------|
| Opus | `anthropic/claude-opus-4-6` | Complex reasoning, synthesis, architecture review |
| Sonnet | `anthropic/claude-sonnet-4-6` | General exploration, code generation, analysis |
| Haiku | `anthropic/claude-haiku-4-5` | Quick tasks, simple transformations, summaries |

Configure per-agent:

```jsonc
{
  "agent": {
    "architect": { "model": "anthropic/claude-opus-4-6" },
    "explorer": { "model": "anthropic/claude-sonnet-4-6" },
    "formatter": { "model": "anthropic/claude-haiku-4-5" }
  }
}
```

---

## Discovery

### Project Agents

Place in `.opencode/agents/{name}.md` — available only in that project.

### Global Agents

Place in `~/.config/opencode/agents/{name}.md` — available in all projects.

---

## Example: Primary Agent

```
.opencode/agents/code-reviewer.md
```

```yaml
---
description: Reviews code for quality, security, and best practices
mode: primary
model: anthropic/claude-sonnet-4-6
color: "#E74C3C"
permission:
  read: allow
  glob: allow
  grep: allow
  write: deny
  edit: deny
  bash: deny
---
```

```markdown
# Code Reviewer

You are a code review specialist. Your job is to thoroughly review code for quality issues, security vulnerabilities, and adherence to best practices.

## Process

1. Read the files to review
2. Check for common issues (OWASP top 10, code smells, complexity)
3. Present findings organized by severity

## Output

Present findings as:
- **Critical**: Security vulnerabilities, data loss risks
- **Warning**: Code quality issues, potential bugs
- **Info**: Style suggestions, minor improvements

Always explain WHY something is an issue, not just WHAT.
```

---

## Example: Subagent

```
.opencode/agents/file-analyzer.md
```

```yaml
---
description: Analyzes individual files for structure and patterns (subagent)
mode: subagent
model: anthropic/claude-sonnet-4-6
permission:
  read: allow
  glob: allow
  grep: allow
  write: deny
  edit: deny
  bash: deny
---
```

```markdown
# File Analyzer

You are a file analysis specialist. Given a file path and analysis criteria, you thoroughly examine the file and report your findings.

## Input

You receive:
- A file path to analyze
- Specific analysis criteria or questions

## Process

1. Read the target file
2. Analyze according to the criteria
3. Check for related files (imports, tests, config)
4. Report structured findings

## Output

Return a structured analysis:
- **File summary**: What the file does
- **Key patterns**: Coding patterns used
- **Dependencies**: What it imports/requires
- **Issues found**: Based on the analysis criteria
- **Recommendations**: Suggested improvements
```
