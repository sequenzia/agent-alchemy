# Plugin Ecosystem Dependency Report

**Ecosystem:** Agent Alchemy
**Date:** 2026-02-20
**Health Score:** 95% — Healthy
**Mode:** Verbose (includes passing checks)

---

## Inventory Summary

| Group | Skills | Agents | Shared Refs | Skill Refs | Hooks | Scripts |
|-------|--------|--------|-------------|------------|-------|---------|
| core-tools | 4 | 3 | 0 | 2 | 1 | 1 |
| dev-tools | 6 | 3 | 0 | 7 | 0 | 0 |
| git-tools | 1 | 0 | 0 | 0 | 0 | 0 |
| sdd-tools | 4 | 3 | 0 | 13 | 1 | 1 |
| tdd-tools | 5 | 3 | 0 | 7 | 1 | 1 |
| plugin-tools | 5 | 2 | 7 | 5 | 0 | 0 |
| **Total** | **25** | **14** | **7** | **34** | **3** | **3** |

**Total components:** 86

---

## Dependency Graph Statistics

| Metric | Count |
|--------|-------|
| Nodes | 86 |
| Total edges | 90 |
| skill-loads-skill (same-plugin) | 5 |
| skill-loads-skill (cross-plugin) | 8 |
| skill-loads-shared-ref | 10 |
| skill-loads-local-ref | 32 |
| skill-loads-cross-ref | 3 |
| skill-spawns-agent | 16 |
| skill-reads-registry | 3 |
| agent-binds-skill | 10 |
| hook-runs-script | 3 |

### Cross-Plugin Skill Loading (8 edges)

| Source Skill | Target Skill | Source Group | Target Group |
|-------------|-------------|-------------|-------------|
| feature-dev | deep-analysis | dev-tools | core-tools |
| feature-dev | language-patterns | dev-tools | core-tools |
| docs-manager | deep-analysis | dev-tools | core-tools |
| create-spec | deep-analysis | sdd-tools | core-tools |
| generate-tests | language-patterns | tdd-tools | core-tools |
| generate-tests | project-conventions | tdd-tools | core-tools |
| tdd-cycle | language-patterns | tdd-tools | core-tools |
| tdd-cycle | project-conventions | tdd-tools | core-tools |

### Cross-Plugin Agent Spawning (3 edges)

| Source Skill | Target Agent | Source Group | Target Group |
|-------------|-------------|-------------|-------------|
| feature-dev | code-architect | dev-tools | core-tools |
| execute-tdd-tasks | task-executor | tdd-tools | sdd-tools |
| (3 plugin-tools skills) | researcher | plugin-tools | plugin-tools |

---

## Analysis Results

### Pass 1: Circular Dependencies — 0 findings (Critical)

No circular dependencies detected. The skill-to-skill dependency graph forms a clean DAG.

### Pass 2: Missing Dependencies — 0 findings (High)

All dependency targets verified on disk:
- 13 skill-to-skill references: all resolved
- 45 reference file loads: all resolved
- 16 agent spawning references: all agents found
- 3 registry reads: marketplace.json accessible
- 3 hook script references: all scripts found

### Pass 3: Broken Cross-Plugin Paths — 0 findings (Medium)

No anti-patterns detected:
- No marketplace names in file paths (all use short source-dir names)
- No hardcoded absolute paths (all use `${CLAUDE_PLUGIN_ROOT}`)
- No incorrect nesting depth (maximum `../../` for registry access)

### Pass 4: Orphaned Components — 1 finding (Low)

#### 4.1 — Orphaned Agent: test-reviewer

- **Component:** `tdd-tools/agents/test-reviewer`
- **Severity:** Low
- **Issue:** Agent has zero `skill-spawns-agent` inbound edges. No skill spawns `test-reviewer` via `subagent_type`.
- **Expected:** At least one skill should spawn this agent
- **Actual:** Referenced only in `generate-tests` settings documentation (`tdd.test-review-on-generate`, default: `false`), but no actual spawning code exists in the skill's Phase 6
- **Fix:** Implement the `tdd.test-review-on-generate` feature in `generate-tests` Phase 6, or document that `test-reviewer` is an API-only agent invoked directly via the Task tool

#### Healthy components (verbose)

**Non-invocable skills with inbound edges (not orphaned):**
- `language-patterns` (core-tools): bound by code-explorer, code-synthesizer; loaded by feature-dev, generate-tests, tdd-cycle
- `project-conventions` (core-tools): bound by code-explorer, code-synthesizer; loaded by generate-tests, tdd-cycle
- `architecture-patterns` (dev-tools): loaded by feature-dev
- `code-quality` (dev-tools): loaded by feature-dev
- `changelog-format` (dev-tools): loaded by feature-dev (line 229)

**Agents with inbound edges (not orphaned):**
- `code-explorer` (core-tools): spawned by deep-analysis
- `code-synthesizer` (core-tools): spawned by deep-analysis
- `code-architect` (core-tools): spawned by feature-dev (cross-plugin)
- `code-reviewer` (dev-tools): spawned by feature-dev
- `changelog-manager` (dev-tools): spawned by release-python-package
- `docs-writer` (dev-tools): spawned by docs-manager
- `researcher` (sdd-tools): spawned by create-spec
- `spec-analyzer` (sdd-tools): spawned by analyze-spec
- `task-executor` (sdd-tools): spawned by execute-tasks, execute-tdd-tasks
- `test-writer` (tdd-tools): spawned by generate-tests
- `tdd-executor` (tdd-tools): spawned by execute-tdd-tasks
- `researcher` (plugin-tools): spawned by validate-adapter, update-ported-plugin, port-plugin
- `port-converter` (plugin-tools): spawned by port-plugin

**Shared references with inbound edges (not orphaned):**
All 7 plugin-tools shared references have inbound edges from validate-adapter, update-ported-plugin, or port-plugin.

**Hook scripts with inbound edges (not orphaned):**
All 3 hook scripts referenced by their corresponding hooks.json files.

### Pass 5: Agent-Skill Mismatches — 4 findings (High)

#### 5.1 — test-writer binds unresolvable skill: language-patterns

- **Component:** `tdd-tools/agents/test-writer`
- **Severity:** High
- **Issue:** Agent `skills:` list includes `language-patterns`, which does not exist in `tdd-tools/skills/`
- **Expected:** Skill should resolve within the same plugin group (`tdd-tools`)
- **Actual:** No `tdd-tools/skills/language-patterns/` directory exists
- **Fix:** The skill exists at `core-tools/skills/language-patterns/`. Either (a) move/symlink the skill into tdd-tools, or (b) use a cross-plugin qualified binding if supported, or (c) document that Claude Code resolves agent skill bindings globally across all installed plugins

#### 5.2 — test-writer binds unresolvable skill: project-conventions

- **Component:** `tdd-tools/agents/test-writer`
- **Severity:** High
- **Issue:** Agent `skills:` list includes `project-conventions`, which does not exist in `tdd-tools/skills/`
- **Expected:** Skill should resolve within the same plugin group
- **Actual:** No `tdd-tools/skills/project-conventions/` directory exists
- **Fix:** Same as 5.1 — skill exists at `core-tools/skills/project-conventions/`

#### 5.3 — tdd-executor binds unresolvable skill: language-patterns

- **Component:** `tdd-tools/agents/tdd-executor`
- **Severity:** High
- **Issue:** Agent `skills:` list includes `language-patterns`, which does not exist in `tdd-tools/skills/`
- **Expected:** Skill should resolve within the same plugin group
- **Actual:** No `tdd-tools/skills/language-patterns/` directory exists
- **Fix:** Same as 5.1

#### 5.4 — tdd-executor binds unresolvable skill: project-conventions

- **Component:** `tdd-tools/agents/tdd-executor`
- **Severity:** High
- **Issue:** Agent `skills:` list includes `project-conventions`, which does not exist in `tdd-tools/skills/`
- **Expected:** Skill should resolve within the same plugin group
- **Actual:** No `tdd-tools/skills/project-conventions/` directory exists
- **Fix:** Same as 5.1

**Note:** These bindings work at runtime because Claude Code resolves agent `skills:` bindings globally across all installed plugins, not just within the same plugin group. However, the dependency checker's model treats `skills:` bindings as plugin-group-local, which is the safer assumption for portability. If a plugin group were installed without core-tools, these bindings would fail.

### Pass 6: Marketplace Consistency — 0 findings (Medium)

All 6 plugin groups have matching registry entries. No stale or missing entries.

### Pass 7: Hook Integrity — 0 findings (Low)

All 3 hooks.json files validated:
- Matchers: `Write|Edit|Bash` — all recognized tool names
- Types: all `command` — valid
- Timeouts: all `5` — positive integers
- Script paths: all use `${CLAUDE_PLUGIN_ROOT}/hooks/` standard pattern

---

## Documentation Cross-Reference

### Check 1: CLAUDE.md Plugin Inventory — 0 findings

All 6 plugin groups match between CLAUDE.md table, marketplace.json, and actual discovery:
- Skill counts: all match
- Agent counts: all match
- Versions: all match (core-tools 0.1.1, dev-tools 0.1.1, sdd-tools 0.1.5, tdd-tools 0.1.3, git-tools 0.1.0, plugin-tools 0.1.1)

### Check 2: CLAUDE.md Composition Chains — 1 finding

#### D.1 — Documented chain does not match dependency graph

- **Source:** CLAUDE.md, "Key Skill Composition Chains" section
- **Severity:** Medium
- **Type:** docs-drift
- **Issue:** Chain `tdd-cycle -> tdd-executor (opus) x 1 per feature` is documented, but `tdd-cycle` has no `subagent_type` reference to `tdd-executor`. Grep of the full 727-line skill confirms zero matches for "tdd-executor" or "subagent_type".
- **Expected:** If documented as a composition chain, an edge should exist in the dependency graph
- **Actual:** `tdd-cycle` runs the TDD phases directly as a self-contained skill. `tdd-executor` is an agent spawned by `execute-tdd-tasks`, not by `tdd-cycle`.
- **Fix:** Update CLAUDE.md to remove the `tdd-cycle -> tdd-executor` chain, or clarify the distinction: `tdd-cycle` is a standalone TDD workflow, while `execute-tdd-tasks` orchestrates `tdd-executor` agents

**Verified chains (all edges confirmed):**
- `feature-dev -> deep-analysis -> code-explorer x N + code-synthesizer x 1` ✓
- `feature-dev -> code-architect (core-tools) x 2-3 -> code-reviewer x 3` ✓
- `create-spec -> deep-analysis (optional)` ✓
- `create-spec -> researcher agent` ✓
- `execute-tasks -> task-executor agent x N per wave` ✓
- `generate-tests -> test-writer x N parallel` ✓
- `execute-tdd-tasks -> tdd-executor + task-executor (sdd-tools)` ✓
- `port-plugin -> researcher x 1 -> port-converter x N per wave` ✓
- `validate-adapter -> researcher x 1` ✓
- `update-ported-plugin -> validate-adapter + researcher` ✓
- `dependency-checker -> reads all plugin groups -> 7 analysis passes` ✓

### Check 3: CLAUDE.md Critical Files — 0 findings

All 13 files verified. Line counts within 10% tolerance:

| File | Documented | Actual | Diff |
|------|-----------|--------|------|
| deep-analysis/SKILL.md | 521 | 521 | 0 |
| port-plugin/SKILL.md | ~2575 | 2572 | -3 |
| validate-adapter/SKILL.md | 625 | 623 | -2 |
| update-ported-plugin/SKILL.md | 793 | 791 | -2 |
| create-spec/SKILL.md | 664 | 666 | +2 |
| create-tasks/SKILL.md | 653 | 653 | 0 |
| execute-tasks/SKILL.md | 262 | 267 | +5 |
| feature-dev/SKILL.md | 273 | 273 | 0 |
| tdd-cycle/SKILL.md | 727 | 727 | 0 |
| generate-tests/SKILL.md | 524 | 524 | 0 |
| create-tdd-tasks/SKILL.md | 687 | 656 | -31 |
| execute-tdd-tasks/SKILL.md | 630 | 642 | +12 |
| dependency-checker/SKILL.md | 651 | 647 | -4 |

### Check 4: Plugin README Files — 1 finding

#### D.2 — Missing agent in plugin-tools README

- **Source:** `claude/plugin-tools/README.md`
- **Severity:** Medium
- **Type:** docs-drift
- **Issue:** Agents table lists only `researcher` (1 agent), but plugin-tools has 2 agents
- **Expected:** Both `researcher` and `port-converter` should be listed
- **Actual:** `port-converter` is missing from the agents table
- **Fix:** Add `port-converter` row to the plugin-tools README agents table:
  ```
  | `port-converter` | Sonnet | Converts individual plugin components to target platform format. Spawned by port-plugin in wave-based teams. |
  ```

**Verified README tables (all match):**
- core-tools: 4 skills, 3 agents ✓
- dev-tools: 6 skills, 3 agents ✓
- sdd-tools: 4 skills, 3 agents ✓
- tdd-tools: 5 skills, 3 agents ✓
- git-tools: 1 skill, 0 agents ✓

---

## Health Score

**Score:** 95% (82 of 86 components clean)

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 4 |
| Medium | 2 |
| Low | 1 |
| **Total** | **7** |

**Components with issues (4):**
- `tdd-tools/agents/test-reviewer` — orphaned (Low)
- `tdd-tools/agents/test-writer` — agent-skill mismatch x2 (High)
- `tdd-tools/agents/tdd-executor` — agent-skill mismatch x2 (High)
- `plugin-tools/agents/port-converter` — missing from README (Medium)

**Recommendation:** The ecosystem is healthy with no critical issues. The 4 High-severity agent-skill mismatch findings all stem from the same root cause: `tdd-tools` agents binding `core-tools` skills (`language-patterns`, `project-conventions`) without cross-plugin qualification. These work at runtime due to Claude Code's global skill resolution, but represent a portability risk. Consider either (a) documenting that agent skill bindings resolve globally, or (b) adding the skills to tdd-tools (via symlink or copy) for explicit resolution.
