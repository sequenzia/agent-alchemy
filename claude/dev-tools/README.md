# Agent Alchemy Dev Tools

Developer agents and skills for the full feature development lifecycle — from exploration and architecture through implementation, review, and documentation.

## Skills

| Skill | Invocable | Description |
|-------|-----------|-------------|
| `/feature-dev` | Yes | 7-phase feature development: Discovery, Exploration (via deep-analysis), Questions, Architecture (code-architect agents), Implementation, Review (code-reviewer agents), Summary. |
| `/bug-killer` | Yes | Hypothesis-driven debugging: Triage & Reproduction, Investigation (code-explorer agents on deep track), Root Cause Analysis (bug-investigator agents), Fix & Verify, Wrap-up & Report. Supports `--deep` flag. |
| `/docs-manager` | Yes | Documentation updates with MkDocs integration. Generates markdown files, updates navigation, handles change summaries. |
| `/release-python-package` | Yes | Python package release automation workflow. |
| `/document-changes` | Yes | Generate a markdown report documenting session changes — files affected, change details, and commit history. |
| `architecture-patterns` | No (loaded by feature-dev) | Design patterns and architectural approaches for the implementation phase. |
| `code-quality` | No (loaded by feature-dev, bug-killer) | Quality criteria and review guidelines for the review phase. |
| `project-learnings` | No (loaded by bug-killer) | Captures project-specific patterns and anti-patterns into the project's CLAUDE.md for future sessions. |
| `changelog-format` | No (loaded by feature-dev) | Keep a Changelog format guidelines with entry examples. |

## Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| `code-reviewer` | Opus | Quality review with confidence-scored findings. Spawned 3x in parallel by feature-dev for independent review perspectives. |
| `bug-investigator` | Sonnet | Diagnostic investigation agent for testing debugging hypotheses. Runs tests, traces execution, checks git history, reports evidence. Spawned by bug-killer in deep track. |
| `changelog-manager` | — | Manages CHANGELOG.md entries following Keep a Changelog format. |
| `docs-writer` | — | Generates and updates documentation files. |

> **Note:** `code-architect` (Opus) is now provided by **core-tools** and spawned cross-plugin by feature-dev using the fully-qualified name `agent-alchemy-core-tools:code-architect`.

## Feature Development Workflow

The **feature-dev** skill orchestrates a complete development lifecycle:

1. **Discovery**: Understand requirements and scope
2. **Exploration**: Load deep-analysis to explore relevant codebase areas
3. **Questions**: Clarify requirements with the user via AskUserQuestion
4. **Architecture**: Spawn 2-3 code-architect agents (from core-tools) in parallel for competing designs
5. **Implementation**: Apply the selected architectural approach
6. **Review**: Spawn 3 code-reviewer agents for independent quality assessment
7. **Summary**: Present results with changelog entry

## Directory Structure

```
dev-tools/
├── agents/
│   ├── code-reviewer.md        # Opus review agent
│   ├── bug-investigator.md     # Sonnet investigation agent
│   ├── changelog-manager.md    # Changelog automation
│   └── docs-writer.md          # Documentation agent
├── skills/
│   ├── feature-dev/
│   │   └── SKILL.md            # 7-phase workflow (272 lines)
│   ├── bug-killer/
│   │   ├── SKILL.md            # 5-phase debugging workflow (~480 lines)
│   │   └── references/
│   │       ├── python-debugging.md
│   │       ├── typescript-debugging.md
│   │       └── general-debugging.md
│   ├── project-learnings/
│   │   └── SKILL.md            # Internal skill for CLAUDE.md learnings
│   ├── architecture-patterns/
│   │   └── SKILL.md            # Design patterns
│   ├── code-quality/
│   │   └── SKILL.md            # Quality criteria
│   ├── changelog-format/
│   │   ├── SKILL.md            # Format guidelines
│   │   └── references/
│   │       └── entry-examples.md
│   ├── docs-manager/
│   │   ├── SKILL.md            # Docs workflow
│   │   └── references/
│   │       ├── change-summary-templates.md
│   │       ├── markdown-file-templates.md
│   │       └── mkdocs-config-template.md
│   ├── release-python-package/
│   │   └── SKILL.md            # Python release workflow
│   └── document-changes/
│       └── SKILL.md            # Change report generator
└── README.md
```
