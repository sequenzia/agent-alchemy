# Adapter Validation Report: OpenCode

**Date:** 2026-02-17
**Health Score:** 31.9% — Critically Outdated
**Adapter Version:** 1.0.0
**Target Platform Version:** 0.0.55 (archived)
**Update Mode:** Disabled

---

## Critical Finding: Two Separate "OpenCode" Projects

The adapter targets `opencode-ai/opencode` (v0.0.55), which was **archived on September 18, 2025**. Two successor/replacement projects now exist:

1. **`anomalyco/opencode` (v1.2.6)** — A completely separate, actively maintained AI coding agent at `opencode.ai`. Different organization (Anomaly Innovations), different codebase. Has a full plugin system with hooks, custom tools, skills, and custom agents.

2. **`charmbracelet/crush`** — The actual spiritual successor to `opencode-ai/opencode`, built by the original author with the Charm team. Has an early-stage, unstable Go module plugin system.

**Decision required:** Which project should the adapter target going forward?

---

## Per-Section Breakdown

| Section | Total Entries | Current | Stale | Missing | Removed | Uncertain |
|---------|-------------|---------|-------|---------|---------|-----------|
| Platform Metadata | 6 | 1 | 5 | 0 | 0 | 0 |
| Directory Structure | 9 | 4 | 5 | 0 | 0 | 0 |
| Tool Name Mappings | 21 | 9 | 8 | 5 | 0 | 2 |
| Model Tier Mappings | 4 | 0 | 4 | 0 | 0 | 0 |
| Frontmatter Translations | 12 | 5 | 5 | 0 | 0 | 0 |
| Hook/Lifecycle Events | 5 | 0 | 5 | 10 | 0 | 0 |
| Composition Mechanism | 6 | 0 | 4 | 0 | 0 | 2 |
| Path Resolution | 5 | 1 | 4 | 0 | 0 | 0 |
| Adapter Version | 5 | 2 | 3 | 0 | 0 | 0 |
| **Totals** | **73** | **22** | **43** | **15** | **0** | **4** |

**Health Score** = 22 / (73 - 4) × 100 = **31.9%**

---

## Stale Entries (43)

### Platform Metadata (5 stale)

| Entry | Current Value | Suggested Value | Source |
|-------|--------------|-----------------|--------|
| name | OpenCode | OpenCode (anomalyco) — or rename adapter to disambiguate | github.com/anomalyco/opencode |
| documentation_url | github.com/opencode-ai/opencode | opencode.ai/docs | opencode.ai/docs |
| repository_url | github.com/opencode-ai/opencode | github.com/anomalyco/opencode | github.com/anomalyco/opencode |
| plugin_docs_url | github.com/opencode-ai/opencode#custom-commands | opencode.ai/docs/plugins | opencode.ai/docs/plugins |
| notes | Mentions archival + Crush | Needs rewrite for new project identity | Research findings |

### Directory Structure (5 stale)

| Entry | Current Value | Suggested Value | Source |
|-------|--------------|-----------------|--------|
| skill_dir | commands/ | commands/ + skills/ + agents/ + tools/ + plugins/ | opencode.ai/docs/config |
| agent_dir | null | agents/ | opencode.ai/docs/agents |
| hook_dir | null | plugins/ (JS/TS plugin files with hooks) | opencode.ai/docs/plugins |
| config_dir | ./ | ./ (config file now `opencode.json`, not `.opencode.json`) | opencode.ai/docs/config |
| notes | Old command-only description | Full directory layout with all subdirs | opencode.ai/docs |

### Tool Name Mappings (8 stale)

| Entry | Current Value | Suggested Value | Source |
|-------|--------------|-----------------|--------|
| Read → view | view | read | opencode.ai/docs/tools |
| Task → agent | agent | task | opencode.ai/docs/tools |
| TaskCreate → null | null | partial:todowrite | opencode.ai/docs/tools |
| TaskUpdate → null | null | partial:todowrite | opencode.ai/docs/tools |
| TaskList → null | null | partial:todoread | opencode.ai/docs/tools |
| TaskGet → null | null | partial:todoread | opencode.ai/docs/tools |
| AskUserQuestion → null | null | question | opencode.ai/docs/tools |
| WebSearch → null | null | websearch (requires OpenCode provider or EXA) | opencode.ai/docs/tools |
| WebFetch → fetch | fetch | webfetch | opencode.ai/docs/tools |

### Model Tier Mappings (4 stale)

| Entry | Current Value | Suggested Value | Source |
|-------|--------------|-----------------|--------|
| opus → claude-4-opus | claude-4-opus | anthropic/claude-opus-4 | opencode.ai/docs/config |
| sonnet → claude-4-sonnet | claude-4-sonnet | anthropic/claude-sonnet-4-20250514 | opencode.ai/docs/config |
| haiku → claude-3.5-haiku | claude-3.5-haiku | anthropic/claude-haiku-3-5 | opencode.ai/docs/config |
| default → claude-4-sonnet | claude-4-sonnet | anthropic/claude-sonnet-4-20250514 | opencode.ai/docs/config |

### Frontmatter Translations (5 stale)

| Entry | Current Value | Suggested Value | Source |
|-------|--------------|-----------------|--------|
| Skill: description → null | null | description (frontmatter field) | opencode.ai/docs/commands |
| Skill: model → null | null | model (frontmatter field) | opencode.ai/docs/commands |
| Agent: name → embedded:config-key | 4 fixed agent types | embedded:filename (.opencode/agents/{name}.md) | opencode.ai/docs/agents |
| Agent: description → null | null | description (frontmatter field) | opencode.ai/docs/agents |
| Agent: tools → null | Hardcoded per agent type | Configurable per agent via `permission` field | deepwiki.com config reference |

### Hook/Lifecycle Events (5 stale)

| Entry | Current Value | Suggested Value | Source |
|-------|--------------|-----------------|--------|
| PreToolUse → null | null | tool.execute.before (via @opencode-ai/plugin) | opencode.ai/docs/plugins |
| PostToolUse → null | null | tool.execute.after (via @opencode-ai/plugin) | opencode.ai/docs/plugins |
| Stop → null | null | session.deleted (via @opencode-ai/plugin) | opencode.ai/docs/plugins |
| SessionStart → null | null | session.created (via @opencode-ai/plugin) | opencode.ai/docs/plugins |
| Notification → null | null | tui.toast.show (via @opencode-ai/plugin) | opencode.ai/docs/plugins |

### Composition Mechanism (4 stale)

| Entry | Current Value | Suggested Value | Source |
|-------|--------------|-----------------|--------|
| mechanism | none | reference (native `skill` tool loads by name) | opencode.ai/docs/skills |
| syntax | N/A | `skill({ name: "skill-name" })` at runtime | opencode.ai/docs/skills |
| supports_cross_plugin | false | true (all discovery paths pooled) | opencode.ai/docs/skills |
| notes | Self-contained, no composition | Skill tool + `instructions` config for context | opencode.ai/docs |

### Path Resolution (4 stale)

| Entry | Current Value | Suggested Value | Source |
|-------|--------------|-----------------|--------|
| resolution_strategy | relative | registry (skills resolve by name) | opencode.ai/docs/skills |
| same_plugin_pattern | .opencode/commands/{name}.md | By name via `skill` tool for skills | opencode.ai/docs/skills |
| cross_plugin_pattern | null | By name (all paths pooled) | opencode.ai/docs/skills |
| notes | No cross-reference possible | Skills walk up from cwd to git root | opencode.ai/docs/skills |

### Adapter Version (3 stale)

| Entry | Current Value | Suggested Value | Source |
|-------|--------------|-----------------|--------|
| adapter_version | 1.0.0 | 2.0.0 (major rewrite scope) | — |
| target_platform_version | 0.0.55 | 1.2.6 (anomalyco/opencode) | github.com/anomalyco/opencode/releases |
| changelog | Initial adapter | Needs rewrite entry | — |

---

## Missing Entries (15)

Features present on the new platform with no adapter mapping:

### Missing Tools (5)

| Feature | Description | Suggested Mapping |
|---------|-------------|-------------------|
| `skill` tool | Native tool for loading SKILL.md content by name | No direct Claude Code equivalent (closest: `Read` of SKILL.md) |
| `lsp` tool | LSP code intelligence (definitions, references, hover) | No Claude Code equivalent |
| `todowrite` tool | Task/TODO creation and management | Partial equivalent of TaskCreate/TaskUpdate |
| `todoread` tool | Task/TODO reading and listing | Partial equivalent of TaskList/TaskGet |
| `patch` tool | Apply diffs/patches to files | No direct Claude Code equivalent |

### Missing Hook Events (10)

| Feature | Description |
|---------|-------------|
| `session.compacted` | Context window compaction triggered |
| `session.idle` | Session becomes idle |
| `message.updated` | Message content updated |
| `message.removed` | Message removed from session |
| `command.executed` | Custom command was executed |
| `file.edited` | File modified by a tool |
| `file.watcher.updated` | External file change detected |
| `tui.prompt.append` | Append text to TUI prompt |
| `lsp.client.diagnostics` | LSP diagnostics available |
| `lsp.updated` | LSP state updated |

---

## Uncertain Entries (4)

Research confidence was insufficient to classify definitively:

| Section | Entry | Reason |
|---------|-------|--------|
| Tool Mappings | mcp__context7__resolve-library-id → context7_resolve-library-id | MCP naming convention likely unchanged but config key changed (`mcpServers` → `mcp`); needs verification |
| Tool Mappings | mcp__context7__query-docs → context7_query-docs | Same uncertainty as above |
| Composition | supports_recursive: false | Unknown if skills can invoke other skills via the `skill` tool |
| Composition | max_depth: 0 | Unknown nesting depth for skill-to-skill invocations |

---

## Current Entries (22)

Summary by section:

| Section | Current Entries |
|---------|----------------|
| Platform Metadata | 1 (slug) |
| Directory Structure | 4 (plugin_root, reference_dir, file_extension, naming_convention) |
| Tool Name Mappings | 9 (Write, Edit, Glob, Grep, NotebookEdit, Bash, TeamCreate, TeamDelete, SendMessage, mcp__* pattern) |
| Frontmatter Translations | 5 (name, argument-hint, user-invocable, disable-model-invocation, allowed-tools) |
| Path Resolution | 1 (root_variable) |
| Adapter Version | 2 (last_updated, author) |

---

## Research Sources Consulted

| Source | Type | Confidence |
|--------|------|------------|
| [opencode-ai/opencode GitHub (archived)](https://github.com/opencode-ai/opencode) | Official | High |
| [anomalyco/opencode GitHub](https://github.com/anomalyco/opencode) | Official | High |
| [opencode.ai/docs](https://opencode.ai/docs/) | Official | High |
| [opencode.ai/docs/plugins](https://opencode.ai/docs/plugins) | Official | High |
| [opencode.ai/docs/commands](https://opencode.ai/docs/commands) | Official | High |
| [opencode.ai/docs/agents](https://opencode.ai/docs/agents) | Official | High |
| [opencode.ai/docs/skills](https://opencode.ai/docs/skills/) | Official | High |
| [opencode.ai/docs/tools](https://opencode.ai/docs/tools/) | Official | High |
| [opencode.ai/docs/config](https://opencode.ai/docs/config/) | Official | High |
| [opencode.ai/docs/mcp-servers](https://opencode.ai/docs/mcp-servers/) | Official | High |
| [deepwiki.com/anomalyco/opencode](https://deepwiki.com/anomalyco/opencode) | Community | High |
| [deepwiki.com/anomalyco/opencode/16-configuration-reference](https://deepwiki.com/anomalyco/opencode/16-configuration-reference) | Community | High |
| [deepwiki.com/anomalyco/opencode/12.1-built-in-tools](https://deepwiki.com/anomalyco/opencode/12.1-built-in-tools) | Community | High |
| [charmbracelet/crush GitHub](https://github.com/charmbracelet/crush) | Official | High |
| [deepwiki.com/charmbracelet/crush](https://deepwiki.com/charmbracelet/crush) | Community | Medium |
| [deepwiki.com/charmbracelet/crush/6-tool-system](https://deepwiki.com/charmbracelet/crush/6-tool-system) | Community | Medium |
| [anomalyco/opencode releases](https://github.com/anomalyco/opencode/releases) | Official | High |

---

## Recommendation

**This adapter requires a major rewrite, not a patch update.** The recommended path forward:

1. **Decide on the target platform**: `anomalyco/opencode` v1.2.6 is the strongest candidate (actively maintained, has a full plugin/hook/skill system). `charmbracelet/crush` is too early-stage for a stable adapter.

2. **If targeting `anomalyco/opencode`**: Re-run `/port-plugin --target opencode` to regenerate the adapter from scratch using live research against the new platform. The scope of changes (43 stale + 15 missing entries) exceeds what incremental updates can reasonably address.

3. **Consider renaming**: To avoid future ambiguity, consider using a more specific slug (e.g., `opencode-anomaly`) if both projects might be adapter targets.

4. **Archive the current adapter**: Keep the current v1.0.0 adapter as `opencode-legacy.md` for reference against the archived `opencode-ai/opencode` project.
