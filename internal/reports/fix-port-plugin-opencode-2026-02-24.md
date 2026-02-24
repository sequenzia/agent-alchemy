# Codebase Changes Report

## Metadata

| Field | Value |
|-------|-------|
| **Date** | 2026-02-24 |
| **Time** | 12:05 EST |
| **Branch** | main |
| **Author** | Stephen Sequenzia |
| **Base Commit** | `e54a578` |
| **Latest Commit** | `1e86cc8` |
| **Repository** | git@github.com:sequenzia/agent-alchemy.git |

**Scope**: Fix port-plugin porting infrastructure for OpenCode v1.2.10

**Summary**: Fixed the port-plugin porting infrastructure across 7 files spanning 4 dependency layers (adapter format spec, concrete adapter, converter references, converter agent, orchestrator skill) to produce functional OpenCode v1.2.10 output. The changes address 9 distinct issues that caused the porter to generate broken output — wrong skill file layout, missing config file generation, invalid agent frontmatter, stale converter references, and metadata leaking into converted content.

## Overview

This session fixed the entire port-plugin pipeline that converts Agent Alchemy plugins to OpenCode format. The existing infrastructure generated 34 non-functional components due to structural mismatches between the converter output and OpenCode v1.2.10's expectations.

- **Files affected**: 7
- **Lines added**: +394
- **Lines removed**: -38
- **Commits**: 1

## Files Changed

| File | Status | Lines | Description |
|------|--------|-------|-------------|
| `claude/plugin-tools/references/adapter-format.md` | Modified | +59 / -2 | Added `skill_file_pattern` field and Config File Format section to adapter specification |
| `claude/plugin-tools/references/adapters/opencode.md` | Modified | +77 / -11 | Updated OpenCode adapter to v2.1.0 targeting v1.2.10 with new fields, model IDs, and hook events |
| `claude/plugin-tools/references/agent-converter.md` | Modified | +72 / -18 | Added Agent Mode derived field and rewrote stale OpenCode-specific conversion notes |
| `claude/plugin-tools/references/hook-converter.md` | Modified | +45 / -0 | Added ESM plugin file template for JS/TS platforms |
| `claude/plugin-tools/references/reference-converter.md` | Modified | +34 / -0 | Added instruction-array output strategy for config-based reference injection |
| `claude/plugin-tools/agents/port-converter.md` | Modified | +54 / -1 | Added skill_file_pattern path logic, task command transform, clean output rule, config fragments |
| `claude/plugin-tools/skills/port-plugin/SKILL.md` | Modified | +53 / -6 | Updated skill path prediction, directory creation, and added Step 5.5 config file generation |

## Change Details

### Modified

- **`claude/plugin-tools/references/adapter-format.md`** — Added `skill_file_pattern` field to Directory Structure (Section 2) enabling adapters to specify subdirectory-based skill layouts like `{name}/SKILL.md`. Added new Section 8 (Config File Format) defining optional unified config file support with fields for agent model paths, MCP config keys, instruction arrays, and permission settings. Renumbered subsequent sections (Path Resolution to 9, Adapter Version to 10). Updated the Complete Adapter File Template to include both new features.

- **`claude/plugin-tools/references/adapters/opencode.md`** — Added `skill_file_pattern: {name}/SKILL.md` to Directory Structure. Updated Task tool notes to document `command` parameter for custom agent spawning (`subagent_type: 'plugin:agent'` maps to `command: 'agent-name'`). Updated Model Tier Mappings to use `claude-opus-4-6` and `claude-sonnet-4-6` as primary IDs (keeping 4-5 as alternatives). Added `(subagent indicator) -> mode` row to Agent Frontmatter with `mode: subagent` documentation. Enhanced `tools -> permission` notes with boolean shorthand syntax. Added `tool.definition` (v1.1.65+) and `shell.env` (v1.2.7+) lifecycle events. Added ESM-only requirement note, v1.2.9 MCP tool attachment metadata note, and v1.2.10 localhost sidecar skip note. Added full Config File Format section with concrete `opencode.json` example. Bumped adapter version from 2.0.0 to 2.1.0, target from 1.2.6 to 1.2.10.

- **`claude/plugin-tools/references/agent-converter.md`** — Added "Agent Mode (derived)" subsection to Stage 2 (Map Frontmatter) defining the logic for setting `mode: subagent` on all custom agents when the adapter defines a mode target field. Completely replaced the OpenCode-Specific Conversion Notes section (lines 509-541) which contained stale v1.0.0 era content — previously referenced `.opencode/commands/` (wrong path) and `.opencode.json` (wrong filename). New section documents correct output structure (`.opencode/agents/{name}.md`), proper frontmatter format with description/mode/model/permission fields, config fragment JSON structure, updated expected gaps table, and tool permission mapping guide.

- **`claude/plugin-tools/references/hook-converter.md`** — Added "Plugin File Template for JS/TS Platforms" subsection after Step 6 (Generate Conversion Output). Documents ESM-only requirement (no `require()`), provides canonical plugin template using `@opencode-ai/plugin` SDK's `Plugin` type with `{ project, client, $, directory, worktree }` context parameters, and includes conversion guidance (plugin naming, auto-approve → permission config preference, `tool.definition` event usage).

- **`claude/plugin-tools/references/reference-converter.md`** — Added "Instruction-Array Strategy" as a third output strategy in Stage 4, alongside copy and flatten. Triggered when composition mechanism is `reference`, `reference_dir` is `null`, and the adapter's Config File Format has a non-null `instruction_key`. Documents the workflow: write references to `{plugin_root}/references/`, register in config file instruction array (individual paths for <5 files, glob for >=5), update skill loading patterns to remove `Read` directives, and note shared reference deduplication benefit.

- **`claude/plugin-tools/agents/port-converter.md`** — Updated Step 4f (Assemble Converted Skill) to check `MAPPINGS.directory_structure.skill_file_pattern` and expand `{name}` placeholder for subdirectory paths. Added Step 4b-2 (Transform Task Tool Invocation Patterns) to detect and convert `subagent_type: "{plugin}:{agent-name}"` to `command: "{agent-name}"` while preserving built-in types (`build`, `plan`). Added clean output rule to Step 5 Resolution Protocol requiring that `resolution_mode`, `group_key`, and internal metadata stay in result file tables only, not in converted content. Added "Config Fragments" section to Step 7 (Write Result File) for collecting agent model configs, MCP configs, instruction entries, and permission entries into JSON fragments that the orchestrator aggregates.

- **`claude/plugin-tools/skills/port-plugin/SKILL.md`** — Updated Phase 4.5 Step 2a skill path prediction to check for `skill_file_pattern` and expand patterns. Updated Phase 6 Step 4 directory creation to handle per-skill subdirectories when `skill_file_pattern` contains a directory separator, and to create references directories for instruction-array strategies. Added Phase 6 Step 5.5 (Generate Config File) — a new step between file writing and migration guide generation that aggregates config fragments from all converter result files, deep-merges them into a unified config object, handles existing config file merging, and writes the final config file.

## Session Commits

| Hash | Message | Author | Date |
|------|---------|--------|------|
| `1e86cc8` | fix(plugin-tools): fix port-plugin infrastructure for OpenCode v1.2.10 | Stephen Sequenzia | 2026-02-24 |

## Architecture Impact

### Dependency Wave Structure

The changes follow a strict 4-wave dependency chain through the porting infrastructure:

```
Wave 1 (Foundation)
├── adapter-format.md       ← Defines schema (skill_file_pattern, Config File Format)
└── opencode.md             ← Implements schema for OpenCode v1.2.10

Wave 2 (Converter References)
├── agent-converter.md      ← Uses adapter schema for agent conversion logic
├── hook-converter.md       ← Uses adapter schema for hook conversion templates
└── reference-converter.md  ← Uses adapter schema for reference output strategy

Wave 3 (Converter Agent)
└── port-converter.md       ← Reads adapter + references at runtime during conversion

Wave 4 (Orchestrator)
└── port-plugin/SKILL.md    ← Orchestrates converters + writes final output
```

### Issues Resolved

| # | Issue | Root Cause | Fix |
|---|-------|-----------|-----|
| 1 | Skills used flat files instead of subdirectories | No `skill_file_pattern` field in adapter format | Added field to spec + adapter + converter + orchestrator |
| 2 | No `opencode.json` generated | No Config File Format concept in adapter spec | Added section to spec + adapter + converters + orchestrator Step 5.5 |
| 3 | Agent frontmatter used invalid `tools:` field | Stale OpenCode section in agent-converter | Rewrote section with correct `permission` field |
| 4 | Agents missing `mode: subagent` | No mode concept in conversion pipeline | Added derived field logic to agent-converter + adapter |
| 5 | Reference files inlined or lost | No instruction-array strategy | Added third strategy to reference-converter |
| 6 | Custom agent spawning broken | `subagent_type` not converted to `command` | Added Step 4b-2 to port-converter |
| 7 | Internal metadata in converted output | No clean output enforcement | Added clean output rule to port-converter Step 5 |
| 8 | Model IDs outdated | Adapter still using 4-5 as primary | Updated to claude-opus-4-6 / claude-sonnet-4-6 |
| 9 | Plugin hooks used wrong format | No ESM template guidance | Added plugin file template to hook-converter |
