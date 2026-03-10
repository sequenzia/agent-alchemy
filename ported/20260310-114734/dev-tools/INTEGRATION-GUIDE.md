# Dev-Tools Integration Guide

This guide covers integrating the dev-tools package into your agent platform. The package was converted from Claude Code plugin format (agent-alchemy-dev-tools v0.3.4) to platform-agnostic nested mode on 2026-03-10.

## Component Inventory

| Component | Type | Path | Nested Agents | Dependencies |
|-----------|------|------|---------------|--------------|
| code-quality | Leaf skill | `skills/code-quality/SKILL.md` | -- | None |
| changelog-format | Leaf skill | `skills/changelog-format/SKILL.md` | -- | None |
| architecture-patterns | Leaf skill | `skills/architecture-patterns/SKILL.md` | -- | None |
| document-changes | Leaf skill | `skills/document-changes/SKILL.md` | -- | None |
| project-learnings | Leaf skill | `skills/project-learnings/SKILL.md` | -- | None |
| release (release-python-package) | Parent skill | `skills/release-python-package/SKILL.md` | changelog-manager | None |
| bug-killer | Parent skill | `skills/bug-killer/SKILL.md` | bug-investigator | code-quality, project-learnings, core-tools:code-explorer |
| feature-dev | Parent skill | `skills/feature-dev/SKILL.md` | code-reviewer | architecture-patterns, code-quality, changelog-format, core-tools:deep-analysis, core-tools:language-patterns, core-tools:technical-diagrams, core-tools:code-architect |
| docs-manager | Parent skill | `skills/docs-manager/SKILL.md` | docs-writer | core-tools:deep-analysis, core-tools:code-explorer |
| lifecycle-hooks | Leaf skill | `skills/lifecycle-hooks/SKILL.md` | -- | None |

**Total: 10 skills, 4 nested agents, 1 shell script reference, 3 markdown references**

## Capability Requirements

Each component requires certain platform capabilities. Map these to your platform's equivalents:

### File Operations
- **File reading**: All skills and agents that analyze code or documentation
- **File writing**: document-changes, release, bug-killer (fix phase), feature-dev (implementation phase), docs-manager (finalization phase)
- **File editing**: project-learnings, release (changelog update), bug-killer (fix phase), feature-dev (implementation phase)
- **File/pattern search**: bug-killer, feature-dev, docs-manager, code-reviewer, bug-investigator, docs-writer

### Shell Execution
- **Git commands**: document-changes, release, bug-killer, feature-dev, changelog-manager, bug-investigator, docs-manager
- **Test runners**: release (pytest), bug-killer (test runners), feature-dev (test runners)
- **Build tools**: release (uv build, ruff)
- **MkDocs CLI**: docs-manager (optional validation)

### User Interaction
- **Prompts with options**: document-changes, release, bug-killer, feature-dev, docs-manager, project-learnings
- **Free-text input**: docs-manager (custom pages), release (version override)

### Sub-Agent Spawning
- **Within same package**: bug-killer -> bug-investigator, feature-dev -> code-reviewer, release -> changelog-manager, docs-manager -> docs-writer
- **Cross-package (core-tools)**: bug-killer -> code-explorer, feature-dev -> code-architect, feature-dev -> deep-analysis, docs-manager -> deep-analysis, docs-manager -> code-explorer

## Nesting Map

```
dev-tools/
├── skills/
│   ├── code-quality/            [leaf]
│   │   └── SKILL.md
│   ├── changelog-format/        [leaf, 1 inlined reference]
│   │   └── SKILL.md
│   ├── architecture-patterns/   [leaf]
│   │   └── SKILL.md
│   ├── document-changes/        [leaf]
│   │   └── SKILL.md
│   ├── project-learnings/       [leaf]
│   │   └── SKILL.md
│   ├── release-python-package/  [parent]
│   │   ├── SKILL.md
│   │   └── agents/
│   │       └── changelog-manager.md
│   ├── bug-killer/              [parent, 2 separate refs, 1 inlined ref]
│   │   ├── SKILL.md
│   │   ├── agents/
│   │   │   └── bug-investigator.md
│   │   └── references/
│   │       ├── python-debugging.md
│   │       └── typescript-debugging.md
│   ├── feature-dev/             [parent, 2 inlined refs]
│   │   ├── SKILL.md
│   │   └── agents/
│   │       └── code-reviewer.md
│   ├── docs-manager/            [parent, 1 separate ref, 2 inlined refs]
│   │   ├── SKILL.md
│   │   ├── agents/
│   │   │   └── docs-writer.md
│   │   └── references/
│   │       └── markdown-file-templates.md
│   └── lifecycle-hooks/         [leaf, converted from hook]
│       ├── SKILL.md
│       └── references/
│           └── resolve-cross-plugins.sh
├── manifest.yaml
└── INTEGRATION-GUIDE.md
```

## Cross-Skill Agent References

These agents are referenced from outside their parent skill:

| Agent | Home Package | Home Skill | Referenced By |
|-------|-------------|------------|---------------|
| code-explorer | core-tools | deep-analysis | bug-killer (Phase 2), docs-manager (Phase 3) |
| code-architect | core-tools | codebase-analysis | feature-dev (Phase 4) |
| code-synthesizer | core-tools | deep-analysis | (via deep-analysis invocation) |

## External Dependency References

This package depends on the following components from the **core-tools** package:

| Component | Type | Used By | Purpose |
|-----------|------|---------|---------|
| deep-analysis | Skill | feature-dev (Phase 2), docs-manager (Phase 3) | Hub-and-spoke codebase exploration with parallel explorer agents and synthesis |
| language-patterns | Skill | feature-dev (Phase 4) | Language-specific coding patterns for architecture design |
| technical-diagrams | Skill | feature-dev (Phase 4), docs-writer (preloaded) | Mermaid diagram styling conventions |
| code-explorer | Agent | bug-killer (Phase 2), docs-manager (Phase 3) | Read-only codebase exploration sub-agent |
| code-architect | Agent | feature-dev (Phase 4) | Architecture design proposal sub-agent |

When integrating, ensure the core-tools package is available or substitute equivalent capabilities.

## Adaptation Checklist

### Skill Loading
- [ ] Map `dependencies` in YAML frontmatter to your platform's skill composition mechanism
- [ ] For leaf skills with no dependencies, they can be loaded independently
- [ ] For parent skills, ensure nested agents can be spawned as sub-tasks

### Agent Spawning
- [ ] Map nested agent definitions to your platform's sub-agent/sub-task mechanism
- [ ] Agents have no YAML frontmatter -- they are pure markdown process descriptions
- [ ] Each agent document specifies Role, Inputs, Process, Output Format, and Guidelines
- [ ] Cross-package agent references (core-tools) require the core-tools package or equivalent

### User Interaction
- [ ] All user prompts use a "prompt the user:" pattern with bullet-point options
- [ ] Map to your platform's dialog/prompt system
- [ ] Some skills require multi-step user interaction (docs-manager has 3-4 questions in Phase 1)

### Path References
- [ ] The `.agents/` directory convention is used for agent configuration paths
- [ ] Project-level configuration files (CLAUDE.md equivalent) may need path adjustment
- [ ] The lifecycle-hooks script references `$HOME/.agents/plugins/installed_plugins.json`

### Reference Files
- [ ] Separate reference files (`references/` directories) are loaded on-demand by their parent skill
- [ ] Inlined references have been merged into the skill body with transformations applied
- [ ] The shell script in lifecycle-hooks/references/ should be adapted to your platform's plugin caching mechanism

### Knowledge Skills
- [ ] code-quality, changelog-format, architecture-patterns are pure knowledge skills (no tools needed)
- [ ] They can be loaded as context/reference material by any workflow
- [ ] No adaptation needed beyond making them discoverable to your platform

### Hook Conversion
- [ ] The lifecycle-hooks skill was converted from a SessionStart hook
- [ ] If your platform has a session/startup hook mechanism, register the script accordingly
- [ ] If not, the SKILL.md documents the problem and solution for manual adaptation
