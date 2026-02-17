# Agent Alchemy Plugin Tools

Plugin lifecycle tools for AI agents -- cross-platform porting, adapter validation, and ported plugin maintenance with an extensible adapter framework, real-time platform research, and interactive workflows.

## Skills

| Skill | Invocable | Description |
|-------|-----------|-------------|
| `/port-plugin` | Yes | Guided conversion wizard that ports plugins to target platforms. Uses adapter framework for mappings, spawns research agent for live documentation, and interactively resolves incompatibilities. |
| `/validate-adapter` | Yes | Validates adapter files against live platform documentation to detect stale mappings, missing features, and outdated version information. Can optionally apply updates in-place. |
| `/update-ported-plugin` | Yes | Updates previously-ported plugins when source plugins change or the target platform evolves. Detects source diffs and platform changes, applies incremental updates, and refreshes metadata. |

## Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| `researcher` | Sonnet | Investigates target platform plugin architectures using web search, documentation fetching, and context7. Produces structured platform profiles for the conversion engine. |

## Skill Workflows

### port-plugin

Multi-phase conversion workflow:

1. **Configuration** -- Parse arguments, load settings, validate adapter, load marketplace registry
2. **Plugin Selection Wizard** -- Choose plugin groups and individual components to convert
3. **Dependency Validation** -- Build dependency graph, detect cross-plugin references, alert on missing deps
4. **Platform Research** -- Spawn research agent to investigate the target platform's latest plugin architecture
5. **Interactive Conversion** -- Convert components one at a time, pausing on incompatibilities for user decisions
6. **Output & Reporting** -- Write converted files, migration guide (with PORT-METADATA), and gap report
7. **Summary** -- Display conversion results, fidelity scores, and next steps

### validate-adapter

4-phase adapter validation:

1. **Load & Parse** -- Read adapter file, extract all 9 sections, display summary
2. **Platform Research** -- Spawn researcher agent to fetch live docs and compare against adapter
3. **Compare & Analyze** -- Diff each section, classify findings as Current/Stale/Missing/Removed/Uncertain
4. **Report & Apply** -- Present validation report, optionally apply updates to adapter file

### update-ported-plugin

5-phase incremental update:

1. **Load Context** -- Parse MIGRATION-GUIDE.md PORT-METADATA, locate ported files, validate metadata
2. **Detect Changes** -- Dual-track: source diffs (git) + platform changes (via validate-adapter)
3. **Apply Source Changes** -- Re-convert modified components, handle new/deleted components
4. **Apply Platform Changes** -- Update ported files for stale mappings, apply additive features
5. **Output & Refresh** -- Write updated files, refresh PORT-METADATA, update gap report

## Shared References

| File | Description |
|------|-------------|
| `references/adapter-format.md` | Adapter file format specification (9 mapping sections) |
| `references/agent-converter.md` | Agent conversion logic (frontmatter mapping, body transformation) |
| `references/hook-converter.md` | Hook conversion logic (event mapping, behavioral classification) |
| `references/reference-converter.md` | Reference file conversion logic (discovery, path transformation) |
| `references/mcp-converter.md` | MCP config conversion logic (server mapping, transport types) |
| `references/incompatibility-resolver.md` | Incompatibility detection, interactive resolution, decision tracking |
| `references/adapters/` | Per-platform adapter files (one markdown file per target platform) |

## Directory Structure

```
plugin-tools/
├── .claude-plugin/
│   └── plugin.json             # Plugin manifest
├── agents/
│   └── researcher.md           # Platform research agent
├── references/                 # Shared reference files (used by all skills)
│   ├── adapter-format.md
│   ├── agent-converter.md
│   ├── hook-converter.md
│   ├── incompatibility-resolver.md
│   ├── mcp-converter.md
│   ├── reference-converter.md
│   └── adapters/
│       └── opencode.md         # OpenCode platform adapter
├── skills/
│   ├── port-plugin/
│   │   └── SKILL.md            # Conversion wizard (~2,750 lines)
│   ├── validate-adapter/
│   │   └── SKILL.md            # Adapter validation (~350 lines)
│   └── update-ported-plugin/
│       └── SKILL.md            # Incremental updater (~700 lines)
└── README.md
```

## MVP Target

The initial release targets **OpenCode** as the first supported conversion target.
