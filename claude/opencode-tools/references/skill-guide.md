# OpenCode Skill Guide

Complete reference for creating OpenCode-compatible skills. Skills are the primary extension mechanism — markdown files with YAML frontmatter that inject structured prompts and workflows.

---

## File Format

Skills are `SKILL.md` files inside a named directory:

```
.opencode/skills/{skill-name}/SKILL.md
```

The skill name is specified in the `name` frontmatter field and must match the directory name.

### YAML Frontmatter

```yaml
---
name: my-skill-name
description: >-
  Clear, concise description of what the skill does and when to use it.
  This is shown when listing available skills.
user-invocable: true
license: MIT
compatibility: ">=1.2.0"
metadata:
  author: "Your Name"
  category: "development"
---
```

### Frontmatter Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | string | **Yes** | — | 1-64 chars. Lowercase alphanumeric + hyphens (`^[a-z0-9]+(-[a-z0-9]+)*$`). Must match the parent directory name. |
| `description` | string | **Yes** | — | 1-1024 chars. Shown in skill listing and used for discovery. |
| `user-invocable` | boolean | No | `true` | Controls whether the skill appears in the command dialog. Set `false` for helper skills loaded only by other skills. |
| `license` | string | No | — | License identifier (e.g., `MIT`, `Apache-2.0`). |
| `compatibility` | string | No | — | Semver range for OpenCode version compatibility. |
| `metadata` | map | No | — | String-to-string key-value pairs for custom metadata. |
| `allowed-tools` | string | No | — | **(Experimental)** Space-delimited list of allowed tools. Per-skill tool restrictions via the Agent Skills spec. |

### Fields That DO NOT Exist

These Claude Code frontmatter fields are **not supported** in OpenCode:

| Field | Why Not | Alternative |
|-------|---------|-------------|
| `model` | No per-skill model override | Configure in `opencode.json` agent settings |
| `disable-model-invocation` | No concept of preventing auto-invocation | The `skill` tool is always available |
| `argument-hint` | No dedicated hint field | Use descriptive `description` instead |
| `arguments` | No structured argument definitions | Use `$VARIABLE` placeholders in body |

---

## Skill Name Format

The `name` frontmatter field must match the parent directory name and conform to:

```
^[a-z0-9]+(-[a-z0-9]+)*$
```

**Valid**: `deep-analysis`, `code-review`, `my-skill`
**Invalid**: `Deep_Analysis`, `my skill`, `mySkill`, `my.skill`

---

## Skill Body

The markdown body below the frontmatter is the skill's prompt content. It is injected into the agent's conversation when invoked.

### $VARIABLE Argument System

Use uppercase `$NAME` patterns as placeholders in the body. OpenCode auto-detects them and prompts the user for values when invoked as a command.

```markdown
---
name: code-quality-check
description: Analyze a specific file for code quality issues
---

# Code Quality Check

Analyze the file at `$FILE_PATH` for:

1. Code style issues
2. Potential bugs
3. Performance concerns

Focus on: $FOCUS_AREA
```

**Built-in placeholders**:
- `$ARGUMENTS` — The full argument string passed to the skill
- `$1`, `$2`, `$3`... — Positional arguments (space-separated)

**Auto-detected placeholders**:
- Any uppercase `$NAME` pattern (letters, numbers, underscores) is detected and prompted
- Example: `$FILE_PATH`, `$TARGET_BRANCH`, `$OUTPUT_FORMAT`

---

## Skill Discovery

Skills are discovered from 6 directory paths (grouped by convention type, interleaving project/global) and merged into a flat registry:

| Priority | Path | Scope |
|----------|------|-------|
| 1 | `.opencode/skills/` | Project |
| 2 | `~/.config/opencode/skills/` | Global |
| 3 | `.claude/skills/` | Project (Claude Code compat) |
| 4 | `~/.claude/skills/` | Global (Claude Code compat) |
| 5 | `.agents/skills/` | Project |
| 6 | `~/.agents/skills/` | Global |

All discovered skills are accessible by name regardless of which directory they live in. If two skills have the same name, the first-discovered one wins (priority order above).

---

## Skill Composition

### Invoking Other Skills

Skills invoke other skills via the `skill` tool by name:

```markdown
Now load the code review checklist:

Use the `skill` tool to invoke the `code-review-checklist` skill.
```

The agent calls `skill({ name: "code-review-checklist" })` which loads that skill's content into the conversation.

### Key Differences from Claude Code Composition

| Claude Code | OpenCode |
|-------------|----------|
| `Read ${CLAUDE_PLUGIN_ROOT}/skills/{name}/SKILL.md` | `skill({ name: "{name}" })` |
| File-path based loading | Name-based registry lookup |
| Relative path resolution | Flat namespace (all skills accessible) |
| Cross-plugin needs path hacks | Cross-project works automatically |

### Reference Content

The Agent Skills spec supports optional subdirectories within each skill directory for supplementary content:

- **`references/`** — Supporting documentation, data files, or lookup tables
- **`scripts/`** — Executable scripts the skill can reference
- **`assets/`** — Images, diagrams, or other binary assets

These directories enable progressive disclosure — the skill body references them as needed rather than inlining everything.

For project-wide reference materials (not tied to a specific skill), use the `instructions` config:

```jsonc
{
  "instructions": [
    ".opencode/references/*.md"
  ]
}
```

Alternatively, create a non-user-invocable helper skill (`user-invocable: false`) to encapsulate reusable reference content.

---

## Best Practices

### Description Quality

The `description` field is critical for skill discovery and model invocation:

- **Be specific**: "Analyze Python code for type safety issues and suggest fixes" (good)
- **Be vague**: "Code analysis tool" (bad)
- **Include trigger phrases**: Mention the key actions and contexts
- **Keep it under 200 chars** for readability in listings

### Skill Body Structure

1. **Start with a clear purpose statement** — What is the skill doing?
2. **Use imperative form** — "Analyze the code", not "This skill analyzes"
3. **Structure with phases** — Number your phases for complex workflows
4. **Progressive disclosure** — Start with high-level instructions, add detail as needed
5. **Lean body** — Don't over-explain; the model understands concise instructions

### Tool Usage Guidance

While `allowed-tools` is available as an experimental field, you can also guide tool usage directly in the body:

```markdown
## Tools to Use

For this analysis, use:
- `read` to examine source files
- `grep` to search for patterns
- `glob` to find relevant files

Do NOT use `write` or `edit` — this is a read-only analysis.
```

### Complex Workflows

For multi-phase skills, use explicit phase markers:

```markdown
## Phase 1: Discovery
{instructions}

## Phase 2: Analysis
{instructions}

## Phase 3: Report
{instructions}

**CRITICAL**: Complete ALL 3 phases before finishing.
```

---

## Common Pitfalls

| Mistake | Why It Fails | Fix |
|---------|-------------|-----|
| Omitting `name:` from frontmatter | Required field; must match directory name | Add `name:` matching the directory |
| `name` doesn't match directory | Validation will fail — names must be identical | Ensure `name:` value equals the parent directory name |
| Adding `model:` to skill frontmatter | Not supported for skills | Configure per-agent in `opencode.json` |
| Using file-path references | `Read path/to/skill.md` won't work reliably | Use `skill({ name: "..." })` |
| Assuming `question` works in subagents | `question` tool is primary-agent-only | Structure questions into the initial `task` prompt |
| Very long skill bodies | Context pressure on smaller models | Split into multiple skills or use `instructions` |
| Non-kebab-case directory names | Won't match the name regex | Use `lowercase-with-dashes` |

---

## Example: Minimal Skill

```
.opencode/skills/greet-user/SKILL.md
```

```yaml
---
name: greet-user
description: Greet the user with a friendly message and ask how to help
user-invocable: true
---
```

```markdown
# Greet User

Say hello to the user and ask what they'd like help with today.
Be friendly and concise.
```

---

## Example: Multi-Phase Skill with Arguments

```
.opencode/skills/review-pr/SKILL.md
```

```yaml
---
name: review-pr
description: >-
  Review a pull request for code quality, security issues, and best practices.
  Use when asked to "review PR", "check PR", or "review pull request".
user-invocable: true
metadata:
  category: "code-review"
---
```

```markdown
# PR Review

Review the pull request in $PR_BRANCH against the base branch.

## Phase 1: Gather Changes

Use `bash` to run:
```
git diff main...$PR_BRANCH --name-only
```

Read each changed file.

## Phase 2: Analysis

For each file, check:
1. Code style consistency
2. Potential bugs or edge cases
3. Security vulnerabilities
4. Test coverage

## Phase 3: Report

Present findings organized by severity:
- **Critical**: Must fix before merge
- **Warning**: Should fix, but not blocking
- **Info**: Suggestions for improvement

**CRITICAL**: Complete ALL 3 phases.
```
