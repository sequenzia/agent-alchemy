# Agent Alchemy Port Tools

Cross-platform plugin conversion tools -- convert Agent Alchemy plugins into formats compatible with other AI coding platforms using an extensible adapter framework, real-time platform research, and interactive conversion workflows.

## Skills

| Skill | Invocable | Description |
|-------|-----------|-------------|
| `/plugin-porter` | Yes | Guided conversion wizard that ports plugins to target platforms. Uses adapter framework for mappings, spawns research agent for live documentation, and interactively resolves incompatibilities. |

## Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| `researcher` | Sonnet | Investigates target platform plugin architectures using web search, documentation fetching, and context7. Produces structured platform profiles for the conversion engine. |

## How It Works

The **plugin-porter** skill orchestrates a multi-phase conversion workflow:

1. **Selection Wizard**: Choose plugin groups and individual components to convert
2. **Dependency Validation**: Build dependency graph, detect cross-plugin references, alert on missing deps
3. **Platform Research**: Spawn research agent to investigate the target platform's latest plugin architecture
4. **Interactive Conversion**: Convert components one at a time, pausing on incompatibilities for user decisions
5. **Output**: Write converted files, migration guide, gap report, and fidelity scores

## Adapter Framework

Target platforms are represented by markdown-based adapter files in `skills/plugin-porter/references/adapters/`. Each adapter defines mappings between Claude Code constructs and the target platform's equivalents. Adding a new target platform requires only creating a new adapter file.

## MVP Target

The initial release targets **OpenCode** as the first supported conversion target.

## Directory Structure

```
port-tools/
├── .claude-plugin/
│   └── plugin.json             # Plugin manifest
├── agents/
│   └── researcher.md           # Platform research agent
├── skills/
│   └── plugin-porter/
│       ├── SKILL.md            # Conversion wizard (placeholder)
│       └── references/
│           └── adapters/       # Platform adapter files
└── README.md
```
