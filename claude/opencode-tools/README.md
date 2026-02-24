# OpenCode Tools

Interactive toolkit for creating and maintaining OpenCode-compatible skills, agents, and commands. Provides interview-driven workflows, best-practice enforcement, and automated validation for the OpenCode platform (anomalyco/opencode v1.2.10).

## Skills

| Skill | Description |
|-------|-------------|
| `oc-create-skill` | Interactive skill creation with interview, generation, and validation |
| `oc-update-skill` | Skill update/migration with research, analysis, and best-practice fixes |
| `oc-create-agent` | Interactive agent creation with permission configuration and validation |
| `oc-update-agent` | Agent update/migration with research, analysis, and fixes |
| `oc-create-command` | Interactive command creation with $VARIABLE configuration and validation |
| `oc-update-command` | Command update/migration with research, analysis, and fixes |

## Agents

| Agent | Purpose |
|-------|---------|
| `oc-researcher` | Fetches latest OpenCode docs and changelog to verify compatibility |
| `oc-validator` | Validates generated artifacts against the platform specification |
| `oc-generator` | Generates skill/agent/command files from interview results |

## Reference Files

| File | Description |
|------|-------------|
| `references/platform-overview.md` | OpenCode platform reference: tools, models, config, permissions, key differences from Claude Code |
| `references/skill-guide.md` | SKILL.md format, frontmatter fields, composition, best practices, common pitfalls |
| `references/agent-guide.md` | Agent format, modes, permissions, system prompts, subagent considerations |
| `references/command-guide.md` | Command format, $VARIABLE system, model override, use cases |

## Templates

| File | Description |
|------|-------------|
| `references/templates/skill-template.md` | Annotated starter SKILL.md |
| `references/templates/agent-template.md` | Annotated starter agent .md (primary + subagent variants) |
| `references/templates/command-template.md` | Annotated starter command .md |

## Usage

### Creating Extensions

```
/oc-create-skill    → Interactive interview → generates .opencode/skills/{name}/SKILL.md
/oc-create-agent    → Interactive interview → generates .opencode/agents/{name}.md
/oc-create-command  → Interactive interview → generates .opencode/commands/{name}.md
```

### Updating Extensions

```
/oc-update-skill [path-or-name]    → Research + analysis → applies best-practice fixes
/oc-update-agent [path-or-name]    → Research + analysis → applies best-practice fixes
/oc-update-command [path-or-name]  → Research + analysis → applies best-practice fixes
```

## Workflow Architecture

```
oc-create-* skills:
  Phase 1: Load References → read platform-overview + type-specific guide
  Phase 2: Interview → AskUserQuestion-driven multi-round gathering
  Phase 3: Generate → spawn oc-generator agent with interview results
  Phase 4: Validate → spawn oc-validator agent on generated file
  Phase 5: Present → show result with design decision explanations

oc-update-* skills:
  Phase 1: Load References → read platform-overview + type-specific guide
  Phase 2: Locate → find existing artifact in workspace
  Phase 3: Research → spawn oc-researcher agent for latest docs
  Phase 4: Analyze → compare against current best practices
  Phase 5: Present Findings → show issues by severity
  Phase 6: Apply Updates → edit after user approval
  Phase 7: Validate → spawn oc-validator agent on updated file
```

## Version

- **Plugin version**: 0.1.0
- **Target platform**: OpenCode v1.2.10 (anomalyco/opencode)
- **License**: MIT
