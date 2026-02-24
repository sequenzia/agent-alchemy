# Skill Template

Annotated starter template for OpenCode skills. Copy this file to `.opencode/skills/{your-skill-name}/SKILL.md` and customize.

---

## Template

````markdown
---
# REQUIRED: Must match the parent directory name. Lowercase alphanumeric + hyphens, 1-64 chars.
name: your-skill-name

# REQUIRED: Description shown in skill listing and used for discovery.
# Be specific about what the skill does and when to use it.
# Include trigger phrases: "use when asked to X, Y, or Z"
description: >-
  [What this skill does]. Use when user says "[trigger phrase 1]",
  "[trigger phrase 2]", or wants to [action].

# OPTIONAL: Set to false for helper skills only loaded by other skills.
# Default: true
user-invocable: true

# OPTIONAL: License identifier
# license: MIT

# OPTIONAL: OpenCode version compatibility range
# compatibility: ">=1.2.0"

# OPTIONAL: Custom string-to-string metadata
# metadata:
#   author: "Your Name"
#   category: "development"
---

# [Skill Name]

[1-2 sentence purpose statement in imperative form. E.g., "Analyze the codebase for security vulnerabilities and report findings."]

## Context

[Optional: What context or background the agent needs to know]

## Phase 1: [Phase Name]

[Instructions for the first phase]

- Use `[tool]` to [action]
- [Specific steps]

## Phase 2: [Phase Name]

[Instructions for the second phase]

## Phase 3: [Phase Name]

[Instructions for the final phase]

**CRITICAL**: Complete ALL [N] phases before finishing.

## Output Format

[Describe what the skill should produce — report format, file output, etc.]

## Guidelines

1. [Guideline 1]
2. [Guideline 2]
3. [Guideline 3]
````

---

## Notes

- **Name**: Required in frontmatter (`name:` field). Must match the parent directory name. Use kebab-case.
- **$VARIABLES**: Add `$VARIABLE_NAME` placeholders in the body for user input.
- **Tool guidance**: Use the experimental `allowed-tools` field or guide tool usage in the body text.
- **Composition**: Invoke other skills with `skill({ name: "skill-name" })` — no file paths.
- **Keep it lean**: The body is injected into the conversation context; avoid unnecessary verbosity.
