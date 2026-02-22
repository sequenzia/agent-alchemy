# Agent Alchemy Core Tools

Foundational skills and agents for codebase analysis, deep exploration, and language-specific patterns. These are designed as reusable building blocks that other plugins compose into larger workflows.

## Skills

| Skill | Invocable | Description |
|-------|-----------|-------------|
| `/deep-analysis` | Yes | Hub-and-spoke team analysis with dynamic planning. Performs reconnaissance, assembles explorer agents (Sonnet), and synthesizes findings (Opus). Configurable approval via `.claude/agent-alchemy.local.md`. |
| `/codebase-analysis` | Yes | Structured 3-phase workflow: deep analysis, reporting, and post-analysis actions (save report, update docs, address insights). |
| `language-patterns` | No (loaded by agents) | TypeScript, Python, and React patterns, idioms, and best practices. |
| `project-conventions` | No (loaded by agents) | Discovers and applies project-specific conventions (naming, structure, patterns). |
| `technical-diagrams` | No (loaded by agents) | Mermaid diagram syntax, styling, and best practices for flowcharts, sequence, class, state, ER, and C4 diagrams. |

## Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| `code-explorer` | Sonnet | Focused area exploration worker. Reads files, searches patterns, produces structured reports. Used by deep-analysis as parallel workers. |
| `code-synthesizer` | Opus | Merges exploration findings into unified analysis. Has Bash access for git history, dependency trees, and static analysis. Can query explorers for follow-ups. |
| `code-architect` | Opus | Designs implementation blueprints with minimal, flexible, and project-aligned approaches. Read-only agent spawned by feature-dev (dev-tools) for architecture design. |

## How It Works

The **deep-analysis** skill is the core engine:

1. **Reconnaissance**: Rapidly maps the codebase structure using Glob/Grep/Read
2. **Dynamic Planning**: Generates focus areas tailored to the actual codebase (not static templates)
3. **Team Assembly**: Spawns N explorer agents (Sonnet) + 1 synthesizer (Opus)
4. **Parallel Exploration**: Explorers investigate their assigned areas independently
5. **Synthesis**: Synthesizer merges all findings, investigates gaps with Bash, evaluates completeness

This skill is loaded by `feature-dev`, `codebase-analysis`, `docs-manager`, and `create-spec` as a reusable building block.

## Directory Structure

```
core-tools/
├── agents/
│   ├── code-architect.md       # Opus blueprint design agent
│   ├── code-explorer.md        # Sonnet exploration worker
│   └── code-synthesizer.md     # Opus synthesis agent
├── skills/
│   ├── deep-analysis/
│   │   └── SKILL.md            # Team-based analysis (350 lines)
│   ├── codebase-analysis/
│   │   ├── SKILL.md            # 3-phase analysis workflow
│   │   └── references/
│   │       ├── report-template.md
│   │       └── actionable-insights-template.md
│   ├── language-patterns/
│   │   └── SKILL.md            # TS/Python/React patterns
│   ├── project-conventions/
│   │   └── SKILL.md            # Convention discovery
│   └── technical-diagrams/
│       ├── SKILL.md            # Mermaid diagram guidance
│       └── references/
│           ├── flowcharts.md
│           ├── sequence-diagrams.md
│           ├── class-diagrams.md
│           ├── state-diagrams.md
│           ├── er-diagrams.md
│           └── c4-diagrams.md
└── README.md
```
