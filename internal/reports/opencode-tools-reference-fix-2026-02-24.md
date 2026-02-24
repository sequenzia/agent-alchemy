# Codebase Changes Report

## Metadata

| Field | Value |
|-------|-------|
| **Date** | 2026-02-24 |
| **Time** | 14:54 EST |
| **Branch** | main |
| **Author** | Stephen Sequenzia |
| **Base Commit** | `55c0673` chore(marketplace): bump opencode-tools to 0.1.1 |
| **Latest Commit** | `1db771b` fix(opencode-tools): correct skill name field documentation and alignment |
| **Repository** | git@github.com:sequenzia/agent-alchemy.git |

**Scope**: Fix OpenCode tools reference files for accuracy against the Agent Skills specification and official OpenCode documentation.

**Summary**: Corrected 21 inaccuracies across 14 opencode-tools files where reference documentation, templates, validators, generators, and create/update skills contained incorrect information about the OpenCode platform — most critically that the required `name` field was documented as non-existent, causing every generated skill to be missing a required field.

## Overview

This session addressed a cascading documentation error in the `opencode-tools` plugin. A single factual mistake — claiming `name` is not a valid skill frontmatter field — propagated through the entire plugin's reference chain: from the skill-guide reference, into templates, into the validator (which incorrectly flagged `name` for removal), into the generator (which omitted it), and into the create/update skills (which perpetuated the error).

- **Files affected**: 14
- **Lines added**: +118
- **Lines removed**: -38
- **Commits**: 1

## Files Changed

| File | Status | Lines | Description |
|------|--------|-------|-------------|
| `claude/opencode-tools/references/skill-guide.md` | Modified | +27 / -15 | Add `name` as required field, fix `allowed-tools`, fix discovery order, fix reference dirs, update examples and pitfalls |
| `claude/opencode-tools/references/platform-overview.md` | Modified | +8 / -6 | Fix discovery path order, update Key Differences table for `allowed-tools` and reference files |
| `claude/opencode-tools/references/agent-guide.md` | Modified | +3 / -1 | Fix `mode` default to `all`, add `top_p` and `prompt` optional fields |
| `claude/opencode-tools/references/command-guide.md` | Modified | +21 / -0 | Add `agent` and `subtask` fields, shell injection, file references, JSON config discovery |
| `claude/opencode-tools/references/templates/skill-template.md` | Modified | +5 / -2 | Add `name` to template frontmatter, fix notes section |
| `claude/opencode-tools/references/templates/agent-template.md` | Modified | +12 / -0 | Add `top_p` and `prompt` as commented-out optional fields in both templates |
| `claude/opencode-tools/references/templates/command-template.md` | Modified | +6 / -0 | Add `agent` and `subtask` as commented-out optional fields |
| `claude/opencode-tools/agents/oc-validator.md` | Modified | +8 / -3 | Reverse `name` check (must be present), relax `allowed-tools` to Info, add `top_p`/`prompt`/`agent`/`subtask` checks |
| `claude/opencode-tools/agents/oc-generator.md` | Modified | +5 / -4 | Add `name` to skill generation rules, add `top_p`/`prompt` to agent rules, add `agent`/`subtask` to command rules |
| `claude/opencode-tools/skills/oc-update-skill/SKILL.md` | Modified | +4 / -1 | Fix Phase 4: `name` is now checked as required, `allowed-tools` is experimental |
| `claude/opencode-tools/skills/oc-create-skill/SKILL.md` | Modified | +2 / -0 | Add `name` REQUIRED note to Phase 3 generator prompt |
| `claude/opencode-tools/skills/oc-update-agent/SKILL.md` | Modified | +2 / -1 | Add `top_p` range check, fix `mode` default reference to `all` |
| `claude/opencode-tools/skills/oc-create-command/SKILL.md` | Modified | +13 / -0 | Add agent routing question to interview, include `agent`/`subtask` in generator prompt and summary |
| `claude/opencode-tools/skills/oc-update-command/SKILL.md` | Modified | +5 / -2 | Add `agent`/`subtask` frontmatter checks, add shell injection detection |

## Change Details

### Modified

#### Reference Documentation (ground truth)

- **`references/skill-guide.md`** — The most critical fix. Added `name` as a required frontmatter field (1-64 chars, must match directory). Moved `allowed-tools` from "Does NOT Exist" table to optional fields with (Experimental) note. Fixed discovery path order to official: `.opencode/` → `~/.config/opencode/` → `.claude/` → `~/.claude/` → `.agents/` → `~/.agents/`. Documented Agent Skills spec support for `references/`, `scripts/`, `assets/` directories. Updated all YAML examples to include `name`. Replaced "Adding `name:` to frontmatter" pitfall with "Omitting `name:` from frontmatter" pitfall.

- **`references/platform-overview.md`** — Fixed skill discovery path order to match official docs (same correction as skill-guide). Updated Key Differences table: `allowed-tools` is now noted as experimental (not unsupported), and reference files now note Agent Skills spec directory support.

- **`references/agent-guide.md`** — Changed `mode` default from `primary` to `all` and marked as required per official docs. Added `top_p` (number, 0.0-1.0) and `prompt` (string, file path) as optional frontmatter fields.

- **`references/command-guide.md`** — Added `agent` (which agent executes) and `subtask` (force subagent) frontmatter fields. Added shell injection (`` !`command` ``) and file reference (`@filepath`) features to the $VARIABLE system section. Added JSON config option (`command` object in `opencode.json`) to discovery paths.

#### Templates

- **`references/templates/skill-template.md`** — Added `name` as the first required field in the template frontmatter with comment explaining format. Updated Notes section: changed "Derived from directory name" to "Required in frontmatter, must match directory name".

- **`references/templates/agent-template.md`** — Added `top_p` and `prompt` as commented-out optional fields in both the primary agent and subagent templates.

- **`references/templates/command-template.md`** — Added `agent` and `subtask` as commented-out optional fields in the full-featured command template.

#### Validator & Generator Agents

- **`agents/oc-validator.md`** — Reversed the `name` check for skills: now validates that `name` IS present, is valid format (1-64 chars, lowercase alphanumeric + hyphens), and matches the parent directory name. Changed `allowed-tools` from Error to Info (experimental). Added `top_p` range check, `prompt` path check, `agent` string check, and `subtask` boolean check.

- **`agents/oc-generator.md`** — Added `name` as REQUIRED in skill generation rules (previously listed in "Do NOT include"). Added `top_p` and `prompt` to valid agent fields. Added `agent` and `subtask` to valid command fields.

#### Create/Update Skills

- **`skills/oc-update-skill/SKILL.md`** — Fixed Phase 4 analysis table: `name` field missing is now an error (was "name present → remove it"). `allowed-tools` is now noted as experimental, not flagged for removal.

- **`skills/oc-create-skill/SKILL.md`** — Added explicit `IMPORTANT: The name field is REQUIRED in frontmatter` note to the Phase 3 generator prompt.

- **`skills/oc-update-agent/SKILL.md`** — Added `top_p` out-of-range check to Phase 4 frontmatter issues table. Fixed `mode` detection to reference correct default value of `all`.

- **`skills/oc-create-command/SKILL.md`** — Added agent routing interview question to Round 2. Added `Agent` field to interview summary. Added `agent`, `subtask`, and NOTE about new fields to Phase 3 generator prompt.

- **`skills/oc-update-command/SKILL.md`** — Added `agent` and `subtask` frontmatter checks to Phase 4 analysis. Added shell injection detection to body issues table.

## Session Commits

| Hash | Message | Author | Date |
|------|---------|--------|------|
| `1db771b` | fix(opencode-tools): correct skill name field documentation and alignment | Stephen Sequenzia | 2026-02-24 |

## Error Cascade Analysis

The root cause was a single incorrect claim in `skill-guide.md` line 49: "`name` — Derived from directory name — Name your directory correctly". This propagated through the plugin's architecture:

```
skill-guide.md (ground truth)
  ├── skill-template.md (inherited the error)
  ├── platform-overview.md (repeated the claim)
  ├── oc-validator.md (enforced incorrect rule: "name must NOT exist")
  ├── oc-generator.md (excluded name from valid fields)
  ├── oc-create-skill (generator prompt omitted name)
  └── oc-update-skill (Phase 4 flagged name for removal)
```

Every skill generated by `oc-create-skill` was missing the required `name` field. Every skill updated by `oc-update-skill` had its `name` field incorrectly flagged and potentially removed. The fix required updating all 6 downstream consumers to match the corrected reference.
