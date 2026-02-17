# Plugin Ecosystem Dependency Health Report

**Date**: 2026-02-17
**Health Score**: 93.8% (76/81 components clean)
**Health Indicator**: Healthy
**Scope**: All 6 plugin groups

---

## Inventory Summary

| Group | Skills | Agents | Shared Refs | Skill Refs | Hooks | Scripts | Total |
|-------|--------|--------|-------------|------------|-------|---------|-------|
| core-tools | 4 | 2 | 0 | 2 | 1 | 1 | 10 |
| dev-tools | 6 | 4 | 0 | 6 | 0 | 0 | 16 |
| git-tools | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| sdd-tools | 6 | 3 | 0 | 20 | 1 | 1 | 31 |
| tdd-tools | 3 | 3 | 0 | 5 | 0 | 0 | 11 |
| plugin-tools | 4 | 1 | 7 | 0 | 0 | 0 | 12 |
| **Total** | **24** | **13** | **7** | **33** | **2** | **2** | **81** |

## Dependency Graph Statistics

| Metric | Count |
|--------|-------|
| Total nodes | 81 |
| Total edges | 67 |
| skill-loads-skill (same-plugin) | 4 |
| skill-loads-skill (cross-plugin) | 8 |
| skill-loads-shared-ref | 11 |
| skill-loads-local-ref | 15 |
| skill-loads-cross-ref | 0 |
| skill-spawns-agent | 15 |
| skill-reads-registry | 2 |
| agent-binds-skill | 10 |
| hook-runs-script | 2 |

### Key Dependency Hubs

- **deep-analysis** (core-tools): 4 inbound skill loads (codebase-analysis, feature-dev, docs-manager, create-spec) + 2 outbound agent spawns (code-explorer, code-synthesizer)
- **language-patterns** (core-tools): 4 inbound skill loads + 4 agent bindings (code-explorer, code-synthesizer, tdd-executor*, test-writer*)
- **project-conventions** (core-tools): 3 inbound skill loads + 4 agent bindings (code-explorer, code-synthesizer, tdd-executor*, test-writer*)

*Denotes broken bindings (see findings 5.1-5.4)

---

## Analysis Results

| Pass | Check | Severity | Findings |
|------|-------|----------|----------|
| 1 | Circular dependencies | Critical | 0 |
| 2 | Missing dependencies | High | 4 |
| 3 | Broken cross-plugin paths | Medium | 0 |
| 4 | Orphaned components | Low | 2 |
| 5 | Agent-skill mismatches | High | 5 |
| 6 | Marketplace consistency | Medium | 0 |
| 7 | Hook integrity | Low | 0 |
| **Phase 3 Total** | | | **11** |

## Documentation Cross-Reference Results

| Source | Check | Findings |
|--------|-------|----------|
| CLAUDE.md | Plugin Inventory | 0 |
| CLAUDE.md | Composition Chains | 1 |
| CLAUDE.md | Critical Files | 2 |
| README files | Skill/Agent tables | 1 |
| **Phase 4 Total** | | **4** |

---

## Findings

### Severity Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 9 (5 unique — 4 overlap between Pass 2 and Pass 5) |
| Medium | 2 |
| Low | 4 |
| **Total** | **15** |

---

### HIGH — Agent-Skill Mismatches (Pass 5)

#### 5.1: tdd-executor binds "language-patterns" — skill not in tdd-tools

- **Component**: `tdd-tools/agents/tdd-executor`
- **Issue**: Agent frontmatter `skills:` list includes "language-patterns", but no skill by that name exists in `tdd-tools/skills/`. The skill exists in `core-tools/skills/language-patterns/`.
- **Expected**: `tdd-tools/skills/language-patterns/SKILL.md`
- **Actual**: File does not exist; skill is at `core-tools/skills/language-patterns/SKILL.md`
- **Impact**: At runtime, the agent's skill binding silently fails to resolve, meaning the agent doesn't receive the language-patterns prompt.
- **Fix**: Add a `language-patterns` skill to tdd-tools (either a proxy that loads core-tools' version, or a copy), or remove the binding if the agent doesn't need it.

#### 5.2: tdd-executor binds "project-conventions" — skill not in tdd-tools

- **Component**: `tdd-tools/agents/tdd-executor`
- **Issue**: Agent frontmatter `skills:` list includes "project-conventions", but no skill by that name exists in `tdd-tools/skills/`.
- **Expected**: `tdd-tools/skills/project-conventions/SKILL.md`
- **Actual**: File does not exist; skill is at `core-tools/skills/project-conventions/SKILL.md`
- **Impact**: Same as 5.1 — binding silently fails.
- **Fix**: Same approach as 5.1.

#### 5.3: test-writer binds "language-patterns" — skill not in tdd-tools

- **Component**: `tdd-tools/agents/test-writer`
- **Issue**: Identical to 5.1, affecting the test-writer agent.
- **Expected**: `tdd-tools/skills/language-patterns/SKILL.md`
- **Actual**: File does not exist; skill is at `core-tools/skills/language-patterns/SKILL.md`
- **Fix**: Same approach as 5.1.

#### 5.4: test-writer binds "project-conventions" — skill not in tdd-tools

- **Component**: `tdd-tools/agents/test-writer`
- **Issue**: Identical to 5.2, affecting the test-writer agent.
- **Expected**: `tdd-tools/skills/project-conventions/SKILL.md`
- **Actual**: File does not exist; skill is at `core-tools/skills/project-conventions/SKILL.md`
- **Fix**: Same approach as 5.2.

#### 5.5: port-plugin spawns "researcher" — ambiguous bare name

- **Component**: `plugin-tools/skills/port-plugin`
- **Issue**: At line 700, port-plugin instructs spawning `subagent_type: "researcher"`. Two agents share this bare name: `agent-alchemy-sdd-tools:researcher` (Opus) and `agent-alchemy-plugin-tools:researcher` (Sonnet). The intended target is the plugin-tools researcher.
- **Expected**: Qualified name `"agent-alchemy-plugin-tools:researcher"`
- **Actual**: Bare name `"researcher"`
- **Impact**: May resolve to the wrong agent at runtime depending on plugin registration order.
- **Fix**: Use qualified name `"agent-alchemy-plugin-tools:researcher"` (consistent with validate-adapter line 217 and update-ported-plugin line 226).

### HIGH — Missing Dependencies (Pass 2)

*Findings 2.1-2.4 are the same underlying issues as 5.1-5.4 above, detected independently by the missing dependency pass.*

#### 2.1: tdd-executor — "language-patterns" not found in tdd-tools/skills/
#### 2.2: tdd-executor — "project-conventions" not found in tdd-tools/skills/
#### 2.3: test-writer — "language-patterns" not found in tdd-tools/skills/
#### 2.4: test-writer — "project-conventions" not found in tdd-tools/skills/

---

### MEDIUM — Documentation Drift (Phase 4)

#### D.1: CLAUDE.md composition chain "tdd-cycle -> tdd-executor" doesn't exist

- **Component**: `CLAUDE.md` (Composition Chains section)
- **Issue**: The documented chain `tdd-cycle -> tdd-executor (opus) x 1 per feature (6-phase RED-GREEN-REFACTOR)` implies tdd-cycle spawns tdd-executor. In the actual dependency graph, tdd-cycle has zero `subagent_type` references — it doesn't spawn any agents. The tdd-executor is spawned by `execute-tdd-tasks` (sdd-tools), not tdd-cycle.
- **Expected**: tdd-cycle spawns tdd-executor
- **Actual**: tdd-cycle loads language-patterns, project-conventions, and references only — no agent spawning
- **Fix**: Update CLAUDE.md to either:
  - Remove the "tdd-cycle -> tdd-executor" chain
  - Replace with: `execute-tdd-tasks -> tdd-executor (opus) x 1 per TDD task`

#### D.2: sdd-tools README missing 2 skills

- **Component**: `sdd-tools/README.md` (Skills table)
- **Issue**: The Skills table lists 4 skills (create-spec, analyze-spec, create-tasks, execute-tasks) but the plugin group actually contains 6 skills. Missing: `create-tdd-tasks` and `execute-tdd-tasks`.
- **Expected**: 6 skills listed in README
- **Actual**: 4 skills listed
- **Fix**: Add entries for `/create-tdd-tasks` and `/execute-tdd-tasks` to the sdd-tools README Skills table. Also add them to the SDD Pipeline diagram and Directory Structure section.

---

### LOW — Orphaned Components (Pass 4)

#### 4.1: test-reviewer agent — never spawned

- **Component**: `tdd-tools/agents/test-reviewer`
- **Issue**: No skill spawns this agent via `subagent_type`. The agent is referenced only as a setting name (`test-review-on-generate`) in generate-tests (line 503) and tdd-cycle (line 171), but no actual spawning code exists.
- **Impact**: The agent file exists but is never used. The settings infrastructure anticipates its use but the implementation is incomplete.
- **Fix**: Implement the spawning logic in `generate-tests` (Phase 6, when `test-review-on-generate` is `true`) to spawn `subagent_type: "agent-alchemy-tdd-tools:test-reviewer"`, or mark it as planned-but-unimplemented in the README.

#### 4.2: test-rubric.md — never referenced

- **Component**: `tdd-tools/skills/tdd-cycle/references/test-rubric.md`
- **Issue**: No file in the codebase references `test-rubric`. Searched all SKILL.md files, agent files, and other references — zero matches.
- **Impact**: The file occupies space but is never loaded. Likely intended as the rubric for the test-reviewer agent (finding 4.1).
- **Fix**: Wire it into test-reviewer's workflow or tdd-cycle's test quality evaluation phase. If truly unused, remove it.

### LOW — Critical Files Line Count Drift (Phase 4, Check 3)

#### D.3: validate-adapter SKILL.md — 78.6% larger than documented

- **Component**: `plugin-tools/skills/validate-adapter/SKILL.md`
- **Documented**: ~350 lines (CLAUDE.md Critical Files table + plugin-tools README)
- **Actual**: 625 lines
- **Drift**: +275 lines (+78.6%) — far exceeds 10% tolerance
- **Fix**: Update CLAUDE.md Critical Files table to `~625` and plugin-tools README directory tree to `(~625 lines)`

#### D.4: update-ported-plugin SKILL.md — 13.3% larger than documented

- **Component**: `plugin-tools/skills/update-ported-plugin/SKILL.md`
- **Documented**: ~700 lines (CLAUDE.md Critical Files table + plugin-tools README)
- **Actual**: 793 lines
- **Drift**: +93 lines (+13.3%) — exceeds 10% tolerance
- **Fix**: Update CLAUDE.md Critical Files table to `~793` and plugin-tools README directory tree to `(~793 lines)`

---

## Dependency Graph

### core-tools/

```
skills/
  deep-analysis
    -> spawns: code-explorer (core-tools), code-synthesizer (core-tools)
    <- loaded by: codebase-analysis (core-tools), feature-dev (dev-tools),
                  docs-manager (dev-tools), create-spec (sdd-tools)
  codebase-analysis
    -> loads: deep-analysis (core-tools)
    -> loads ref: report-template.md, actionable-insights-template.md
  language-patterns
    <- loaded by: feature-dev (dev-tools), generate-tests (tdd-tools),
                  tdd-cycle (tdd-tools)
    <- bound by: code-explorer (core-tools), code-synthesizer (core-tools),
                 tdd-executor* (tdd-tools), test-writer* (tdd-tools)
  project-conventions
    <- loaded by: generate-tests (tdd-tools), tdd-cycle (tdd-tools)
    <- bound by: code-explorer (core-tools), code-synthesizer (core-tools),
                 tdd-executor* (tdd-tools), test-writer* (tdd-tools)
agents/
  code-explorer
    -> binds: project-conventions, language-patterns
    <- spawned by: deep-analysis (core-tools), docs-manager (dev-tools)
  code-synthesizer
    -> binds: project-conventions, language-patterns
    <- spawned by: deep-analysis (core-tools)
  code-architect
    <- spawned by: feature-dev (dev-tools)
hooks/
  hooks.json (PreToolUse: Write|Edit|Bash)
    -> runs: auto-approve-da-session.sh
```

*Bindings marked with * are broken (skill not in same plugin group)

### dev-tools/

```
skills/
  feature-dev
    -> loads: deep-analysis (core-tools), language-patterns (core-tools),
              architecture-patterns (dev-tools), code-quality (dev-tools)
    -> spawns: code-architect (core-tools), code-reviewer (dev-tools)
    -> loads ref: adr-template.md, changelog-entry-template.md
  docs-manager
    -> loads: deep-analysis (core-tools)
    -> spawns: code-explorer (core-tools), docs-writer (dev-tools)
    -> loads ref: mkdocs-config-template.md, change-summary-templates.md,
                  markdown-file-templates.md
  architecture-patterns
    <- loaded by: feature-dev (dev-tools)
  code-quality
    <- loaded by: feature-dev (dev-tools)
  changelog-format
    -> loads ref: entry-examples.md
  release-python-package
    -> spawns: changelog-manager (dev-tools)
agents/
  code-reviewer
    <- spawned by: feature-dev
  changelog-manager
    <- spawned by: release-python-package
  docs-writer
    <- spawned by: docs-manager
```

### git-tools/

```
skills/
  git-commit
    (no dependencies)
```

### sdd-tools/

```
skills/
  create-spec
    -> loads: deep-analysis (core-tools)
    -> spawns: researcher (sdd-tools)
    -> loads ref: interview-questions.md, recommendation-triggers.md,
                  recommendation-format.md, templates/high-level.md,
                  templates/detailed.md, templates/full-tech.md
  analyze-spec
    -> spawns: spec-analyzer (sdd-tools)
    -> loads ref: analysis-criteria.md, common-issues.md,
                  html-review-guide.md, report-template.md
  create-tasks
    -> loads ref: decomposition-patterns.md, dependency-inference.md,
                  testing-requirements.md
  execute-tasks
    -> loads ref: orchestration.md, execution-workflow.md,
                  verification-patterns.md
  create-tdd-tasks
    -> loads ref: tdd-decomposition-patterns.md, tdd-dependency-rules.md
  execute-tdd-tasks
    -> spawns: tdd-executor (tdd-tools), task-executor (sdd-tools)
    -> loads ref: tdd-execution-workflow.md, tdd-verification-patterns.md
agents/
  researcher
    <- spawned by: create-spec
  spec-analyzer
    -> binds: analyze-spec
    <- spawned by: analyze-spec
  task-executor
    -> binds: execute-tasks
    <- spawned by: execute-tdd-tasks
hooks/
  hooks.json (PreToolUse: Write|Edit|Bash)
    -> runs: auto-approve-session.sh
```

### tdd-tools/

```
skills/
  tdd-cycle
    -> loads: language-patterns (core-tools), project-conventions (core-tools)
    -> loads ref: test-patterns.md (generate-tests), framework-templates.md (generate-tests),
                  tdd-workflow.md (tdd-cycle)
    [!] ORPHAN: references/test-rubric.md (not referenced by any file)
  generate-tests
    -> loads: language-patterns (core-tools), project-conventions (core-tools)
    -> spawns: test-writer (tdd-tools)
    -> loads ref: framework-templates.md, test-patterns.md
  analyze-coverage
    -> loads ref: coverage-patterns.md
agents/
  test-writer
    -> binds: language-patterns*, project-conventions* (BROKEN — skills in core-tools)
    <- spawned by: generate-tests
  tdd-executor
    -> binds: language-patterns*, project-conventions* (BROKEN — skills in core-tools)
    <- spawned by: execute-tdd-tasks (sdd-tools)
  test-reviewer
    [!] ORPHAN: no skill spawns this agent
```

### plugin-tools/

```
skills/
  port-plugin
    -> spawns: researcher (bare name — AMBIGUOUS)
    -> reads registry: marketplace.json
    -> loads ref: adapter-format.md, agent-converter.md, hook-converter.md,
                  reference-converter.md, mcp-converter.md,
                  incompatibility-resolver.md, adapters/{dynamic}.md
  validate-adapter
    -> spawns: agent-alchemy-plugin-tools:researcher
    -> loads ref: adapter-format.md, adapters/{dynamic}.md
    <- loaded by: update-ported-plugin (plugin-tools)
  update-ported-plugin
    -> loads: validate-adapter (plugin-tools)
    -> spawns: agent-alchemy-plugin-tools:researcher
    -> loads ref: adapters/{dynamic}.md, incompatibility-resolver.md
  dependency-checker
    -> reads registry: marketplace.json
agents/
  researcher
    <- spawned by: port-plugin, validate-adapter, update-ported-plugin
references/
  adapter-format.md       <- port-plugin, validate-adapter
  agent-converter.md      <- port-plugin
  hook-converter.md       <- port-plugin
  reference-converter.md  <- port-plugin
  mcp-converter.md        <- port-plugin
  incompatibility-resolver.md <- port-plugin, update-ported-plugin
  adapters/opencode.md    <- port-plugin, validate-adapter, update-ported-plugin (dynamic)
```

---

## Recommendations

### Priority 1: Fix tdd-tools agent-skill bindings (High)

Both `tdd-executor` and `test-writer` agents bind `language-patterns` and `project-conventions`, but those skills only exist in `core-tools`. Options:

1. **Create proxy skills in tdd-tools** — Minimal SKILL.md files that load the core-tools originals via `Read ${CLAUDE_PLUGIN_ROOT}/../core-tools/skills/{name}/SKILL.md`
2. **Remove the bindings** — If the agents don't actually need these skills at runtime (they may receive the context through other means)
3. **Wait for cross-plugin skill binding support** — If Claude Code adds cross-plugin `skills:` resolution in agent frontmatter

### Priority 2: Fix port-plugin researcher ambiguity (High)

Change line 700 of `port-plugin/SKILL.md` from `subagent_type: "researcher"` to `subagent_type: "agent-alchemy-plugin-tools:researcher"`. This is a one-line fix.

### Priority 3: Update documentation (Medium)

- Update CLAUDE.md composition chains: fix "tdd-cycle -> tdd-executor" chain
- Update sdd-tools README: add create-tdd-tasks and execute-tdd-tasks
- Update CLAUDE.md Critical Files table: validate-adapter ~625, update-ported-plugin ~793

### Priority 4: Wire up test-reviewer (Low)

Implement test-reviewer spawning in `generate-tests` Phase 6 when `test-review-on-generate` is true. Connect `test-rubric.md` as the reviewer's rubric input.
