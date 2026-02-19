# Migration Guide: Agent Alchemy to OpenCode

**Generated:** 2026-02-18
**Source:** Agent Alchemy (34 components from 5 plugin groups)
**Target platform:** OpenCode
**Overall fidelity:** 72% (Yellow -- Moderate fidelity)

---

## Conversion Fidelity

**Overall score:** 72% -- Yellow (Moderate fidelity)

### Per-Component Scores

| Component | Type | Group | Score | Band | Direct | Workaround | TODO | Omitted | Total |
|-----------|------|-------|-------|------|--------|------------|------|---------|-------|
| test-reviewer | agent | tdd-tools | 100% | Green | 10 | 0 | 0 | 0 | 10 |
| researcher | agent | sdd-tools | 100% | Green | 11 | 0 | 0 | 0 | 11 |
| docs-writer | agent | dev-tools | 97% | Green | 11 | 0 | 0 | 0 | 11 |
| changelog-manager | agent | dev-tools | 95% | Green | 12 | 0 | 0 | 0 | 12 |
| codebase-analysis | skill | core-tools | 87% | Green | 21 | 12 | 0 | 1 | 34 |
| tdd-executor | agent | tdd-tools | 87% | Green | 9 | 8 | 0 | 0 | 17 |
| hooks-sdd-tools | hooks | sdd-tools | 85% | Green | 2 | 2 | 0 | 0 | 4 |
| spec-analyzer | agent | sdd-tools | 84% | Green | 11 | 6 | 0 | 0 | 17 |
| generate-tests | skill | tdd-tools | 82% | Green | 8 | 5 | 2 | 0 | 15 |
| task-executor | agent | sdd-tools | 82% | Green | 11 | 10 | 0 | 1 | 22 |
| docs-manager | skill | dev-tools | 80% | Green | 15 | 6 | 3 | 0 | 24 |
| test-writer | agent | tdd-tools | 79% | Yellow | 11 | 0 | 0 | 3 | 15 |
| code-reviewer | agent | dev-tools | 77% | Yellow | 8 | 4 | 0 | 2 | 14 |
| execute-tasks | skill | sdd-tools | 77% | Yellow | 12 | 8 | 2 | 0 | 22 |
| code-synthesizer | agent | core-tools | 76% | Yellow | 11 | 8 | 0 | 3 | 23 |
| code-architect | agent | core-tools | 75% | Yellow | 8 | 6 | 0 | 2 | 16 |
| feature-dev | skill | dev-tools | 72% | Yellow | 12 | 8 | 2 | 0 | 22 |
| language-patterns | skill | core-tools | 68% | Yellow | 3 | 1 | 0 | 1 | 5 |
| project-conventions | skill | core-tools | 68% | Yellow | 3 | 1 | 0 | 1 | 5 |
| architecture-patterns | skill | dev-tools | 68% | Yellow | 3 | 1 | 0 | 1 | 5 |
| code-quality | skill | dev-tools | 68% | Yellow | 3 | 1 | 0 | 1 | 5 |
| changelog-format | skill | dev-tools | 68% | Yellow | 3 | 1 | 0 | 1 | 5 |
| tdd-cycle | skill | tdd-tools | 68% | Yellow | 10 | 8 | 6 | 0 | 24 |
| execute-tdd-tasks | skill | tdd-tools | 68% | Yellow | 12 | 7 | 4 | 0 | 23 |
| release-python-package | skill | dev-tools | 67% | Yellow | 6 | 2 | 0 | 3 | 12 |
| deep-analysis | skill | core-tools | 66% | Yellow | 9 | 11 | 6 | 1 | 27 |
| create-tdd-tasks | skill | tdd-tools | 62% | Yellow | 6 | 9 | 4 | 2 | 21 |
| create-spec | skill | sdd-tools | 59% | Yellow | 6 | 8 | 6 | 0 | 20 |
| create-tasks | skill | sdd-tools | 57% | Yellow | 5 | 6 | 5 | 0 | 16 |
| code-explorer | agent | core-tools | 56% | Yellow | 9 | 4 | 4 | 4 | 21 |
| analyze-coverage | skill | tdd-tools | 56% | Yellow | 4 | 3 | 3 | 0 | 10 |
| analyze-spec | skill | sdd-tools | 54% | Yellow | 6 | 3 | 5 | 3 | 18 |
| hooks-core-tools | hooks | core-tools | 48% | Red | 0 | 1 | 0 | 1 | 3 |
| git-commit | skill | git-tools | 39% | Red | 2 | 1 | 0 | 4 | 7 |

### Score Legend

| Band | Range | Meaning |
|------|-------|---------|
| Green | 80-100% | High fidelity -- minimal manual work needed |
| Yellow | 50-79% | Moderate fidelity -- some manual work needed |
| Red | 0-49% | Low fidelity -- significant manual work needed |

---

## Platform Adapter Status

| Field | Value |
|-------|-------|
| Staleness check performed | yes |
| Adapter version | 1.0.0 |
| Adapter target platform version | 0.0.55 |
| Research-reported platform version | 0.0.55 |
| Status | current |
| User decision | N/A |
| Stale mappings found | 0 |
| New features discovered | 0 |

---

## Conversion Summary

| Metric | Value |
|--------|-------|
| Components converted | 34 / 34 |
| Skills | 20 |
| Agents | 12 |
| Hooks | 2 |
| Waves executed | 4 |
| Resolution cache entries | 19 |
| Total decisions | 517 |
| Total gaps | 171 |
| Green band (80%+) | 11 components |
| Yellow band (50-79%) | 21 components |
| Red band (<50%) | 2 components |

---

## Per-Component Details

> This conversion included 34 components. Details are shown in table format for readability. Components with Red fidelity bands have expanded detail sections below.

### All Components

| Component | Type | Group | Score | Source | Target |
|-----------|------|-------|-------|--------|--------|
| test-reviewer | agent | tdd-tools | 100% Green | claude/tdd-tools/agents/test-reviewer.md | .opencode/agents/test-reviewer.md |
| researcher | agent | sdd-tools | 100% Green | claude/sdd-tools/agents/researcher.md | .opencode/agents/researcher.md |
| docs-writer | agent | dev-tools | 97% Green | claude/dev-tools/agents/docs-writer.md | .opencode/agents/docs-writer.md |
| changelog-manager | agent | dev-tools | 95% Green | claude/dev-tools/agents/changelog-manager.md | .opencode/agents/changelog-manager.md |
| codebase-analysis | skill | core-tools | 87% Green | claude/core-tools/skills/codebase-analysis/SKILL.md | .opencode/skills/codebase-analysis.md |
| tdd-executor | agent | tdd-tools | 87% Green | claude/tdd-tools/agents/tdd-executor.md | .opencode/agents/tdd-executor.md |
| hooks-sdd-tools | hooks | sdd-tools | 85% Green | claude/sdd-tools/hooks/hooks.json | .opencode/hooks/sdd-tools-hooks.js |
| spec-analyzer | agent | sdd-tools | 84% Green | claude/sdd-tools/agents/spec-analyzer.md | .opencode/agents/spec-analyzer.md |
| generate-tests | skill | tdd-tools | 82% Green | claude/tdd-tools/skills/generate-tests/SKILL.md | .opencode/skills/generate-tests.md |
| task-executor | agent | sdd-tools | 82% Green | claude/sdd-tools/agents/task-executor.md | .opencode/agents/task-executor.md |
| docs-manager | skill | dev-tools | 80% Green | claude/dev-tools/skills/docs-manager/SKILL.md | .opencode/skills/docs-manager.md |
| test-writer | agent | tdd-tools | 79% Yellow | claude/tdd-tools/agents/test-writer.md | .opencode/agents/test-writer.md |
| code-reviewer | agent | dev-tools | 77% Yellow | claude/dev-tools/agents/code-reviewer.md | .opencode/agents/code-reviewer.md |
| execute-tasks | skill | sdd-tools | 77% Yellow | claude/sdd-tools/skills/execute-tasks/SKILL.md | .opencode/skills/execute-tasks.md |
| code-synthesizer | agent | core-tools | 76% Yellow | claude/core-tools/agents/code-synthesizer.md | .opencode/agents/code-synthesizer.md |
| code-architect | agent | core-tools | 75% Yellow | claude/core-tools/agents/code-architect.md | .opencode/agents/code-architect.md |
| feature-dev | skill | dev-tools | 72% Yellow | claude/dev-tools/skills/feature-dev/SKILL.md | .opencode/skills/feature-dev.md |
| language-patterns | skill | core-tools | 68% Yellow | claude/core-tools/skills/language-patterns/SKILL.md | .opencode/skills/language-patterns.md |
| project-conventions | skill | core-tools | 68% Yellow | claude/core-tools/skills/project-conventions/SKILL.md | .opencode/skills/project-conventions.md |
| architecture-patterns | skill | dev-tools | 68% Yellow | claude/dev-tools/skills/architecture-patterns/SKILL.md | .opencode/skills/architecture-patterns.md |
| code-quality | skill | dev-tools | 68% Yellow | claude/dev-tools/skills/code-quality/SKILL.md | .opencode/skills/code-quality.md |
| changelog-format | skill | dev-tools | 68% Yellow | claude/dev-tools/skills/changelog-format/SKILL.md | .opencode/skills/changelog-format.md |
| tdd-cycle | skill | tdd-tools | 68% Yellow | claude/tdd-tools/skills/tdd-cycle/SKILL.md | .opencode/skills/tdd-cycle.md |
| execute-tdd-tasks | skill | tdd-tools | 68% Yellow | claude/tdd-tools/skills/execute-tdd-tasks/SKILL.md | .opencode/skills/execute-tdd-tasks.md |
| release-python-package | skill | dev-tools | 67% Yellow | claude/dev-tools/skills/release-python-package/SKILL.md | .opencode/skills/release-python-package.md |
| deep-analysis | skill | core-tools | 66% Yellow | claude/core-tools/skills/deep-analysis/SKILL.md | .opencode/skills/deep-analysis.md |
| create-tdd-tasks | skill | tdd-tools | 62% Yellow | claude/tdd-tools/skills/create-tdd-tasks/SKILL.md | .opencode/skills/create-tdd-tasks.md |
| create-spec | skill | sdd-tools | 59% Yellow | claude/sdd-tools/skills/create-spec/SKILL.md | .opencode/skills/create-spec.md |
| create-tasks | skill | sdd-tools | 57% Yellow | claude/sdd-tools/skills/create-tasks/SKILL.md | .opencode/skills/create-tasks.md |
| code-explorer | agent | core-tools | 56% Yellow | claude/core-tools/agents/code-explorer.md | .opencode/agents/code-explorer.md |
| analyze-coverage | skill | tdd-tools | 56% Yellow | claude/tdd-tools/skills/analyze-coverage/SKILL.md | .opencode/skills/analyze-coverage.md |
| analyze-spec | skill | sdd-tools | 54% Yellow | claude/sdd-tools/skills/analyze-spec/SKILL.md | .opencode/skills/analyze-spec.md |
| hooks-core-tools | hooks | core-tools | 48% Red | claude/core-tools/hooks/hooks.json | .opencode/hooks/core-tools-hooks.md |
| git-commit | skill | git-tools | 39% Red | claude/git-tools/skills/git-commit/SKILL.md | .opencode/skills/git-commit.md |

### hooks-core-tools -- 48% (Red)

**Source:** claude/core-tools/hooks/hooks.json
**Target:** .opencode/hooks/core-tools-hooks.md

The core-tools hooks define a PreToolUse hook for auto-approving Write/Edit/Bash operations within `.claude/sessions/` directories. OpenCode has no path-based auto-approval mechanism -- hooks require JS/TS plugin format, and subagent tool calls do not trigger hooks. This component is converted to a migration documentation file rather than a functional hook.

**Key gaps:**
- PreToolUse shell-to-JS conversion not fully automated (path-based approval logic requires manual JS plugin creation)
- Subagent tool calls bypass hook events entirely in OpenCode

### git-commit -- 39% (Red)

**Source:** claude/git-tools/skills/git-commit/SKILL.md
**Target:** .opencode/skills/git-commit.md

The git-commit skill has the lowest fidelity because it depends heavily on Bash tool execution combined with AskUserQuestion for interactive commit message confirmation. OpenCode's `question` tool maps directly, but several frontmatter fields (allowed-tools, model, disable-model-invocation) have no equivalents, and the skill's tight coupling to specific bash+git workflows means behavioral parity is reduced.

**Key gaps:**
- `allowed-tools` field omitted (no per-skill tool restrictions)
- `model: haiku` tier not directly configurable per-skill
- Interactive bash+question workflow may behave differently

---

## Post-Conversion Steps

The following manual steps are recommended after conversion:

### Required Actions

1. **Reference file inlining**: Skills that use `references/` subdirectories need their reference content inlined into the skill body or added to `opencode.json` instructions. Search for `TODO` comments containing "reference" in converted files. Affected skills: deep-analysis, feature-dev, docs-manager, tdd-cycle, execute-tasks, generate-tests, create-tasks, create-tdd-tasks, execute-tdd-tasks, analyze-coverage, analyze-spec.

2. **hooks-core-tools**: Manually create a JS plugin for `.opencode/hooks/` that implements the auto-approve session path logic, or use the "Allow for session" manual approval workflow.

3. **Team/SendMessage restructuring verification**: Skills that used TeamCreate/SendMessage (deep-analysis, create-spec, codebase-analysis) have been restructured to use parallel task calls with embedded context. Verify the restructured workflows produce equivalent results.

### Recommended Verifications

1. Verify that `todoread`/`todowrite` workarounds for TaskGet/TaskUpdate/TaskList/TaskCreate produce correct behavior in sdd-tools skills (create-tasks, execute-tasks, create-tdd-tasks, execute-tdd-tasks).
2. Test the `question` tool interactions in all interactive skills (create-spec, analyze-spec, feature-dev, docs-manager, tdd-cycle).
3. Confirm agent permission fields correctly grant the tools each agent needs.
4. Verify cross-plugin skill composition via `skill({ name: "..." })` syntax works at runtime.

### Platform Setup

1. Test the converted plugin on OpenCode to verify runtime behavior
2. Review all TODO comments in converted files (search for `TODO [opencode]` or `TODO:`)
3. Consult `GAP-REPORT.md` for a detailed breakdown of all conversion gaps
4. Configure any MCP servers needed for your OpenCode environment (context7 MCP tools used by researcher agent)

---

## Output Files

**Skills (20 files):**
- `.opencode/skills/language-patterns.md`
- `.opencode/skills/project-conventions.md`
- `.opencode/skills/deep-analysis.md`
- `.opencode/skills/codebase-analysis.md`
- `.opencode/skills/architecture-patterns.md`
- `.opencode/skills/code-quality.md`
- `.opencode/skills/changelog-format.md`
- `.opencode/skills/release-python-package.md`
- `.opencode/skills/feature-dev.md`
- `.opencode/skills/docs-manager.md`
- `.opencode/skills/create-spec.md`
- `.opencode/skills/analyze-spec.md`
- `.opencode/skills/create-tasks.md`
- `.opencode/skills/execute-tasks.md`
- `.opencode/skills/create-tdd-tasks.md`
- `.opencode/skills/execute-tdd-tasks.md`
- `.opencode/skills/generate-tests.md`
- `.opencode/skills/tdd-cycle.md`
- `.opencode/skills/analyze-coverage.md`
- `.opencode/skills/git-commit.md`

**Agents (12 files):**
- `.opencode/agents/code-explorer.md`
- `.opencode/agents/code-synthesizer.md`
- `.opencode/agents/code-architect.md`
- `.opencode/agents/code-reviewer.md`
- `.opencode/agents/changelog-manager.md`
- `.opencode/agents/docs-writer.md`
- `.opencode/agents/test-reviewer.md`
- `.opencode/agents/test-writer.md`
- `.opencode/agents/spec-analyzer.md`
- `.opencode/agents/researcher.md`
- `.opencode/agents/task-executor.md`
- `.opencode/agents/tdd-executor.md`

**Hooks (2 files):**
- `.opencode/hooks/sdd-tools-hooks.js` (or .md)
- `.opencode/hooks/core-tools-hooks.md`

**Reports:**
- `.opencode/MIGRATION-GUIDE.md` -- this file
- `.opencode/GAP-REPORT.md` -- conversion gap analysis

<!-- PORT-METADATA
source_commit: 2f754d953401d4c22cba29967dc34b620ec1b93d
port_date: 2026-02-18
adapter_version: 1.0.0
target_platform: opencode
target_platform_version: 0.0.55
components:
  - source: claude/core-tools/skills/language-patterns/SKILL.md
    target: .opencode/skills/language-patterns.md
    fidelity: 68
  - source: claude/core-tools/skills/project-conventions/SKILL.md
    target: .opencode/skills/project-conventions.md
    fidelity: 68
  - source: claude/core-tools/skills/deep-analysis/SKILL.md
    target: .opencode/skills/deep-analysis.md
    fidelity: 66
  - source: claude/core-tools/skills/codebase-analysis/SKILL.md
    target: .opencode/skills/codebase-analysis.md
    fidelity: 87
  - source: claude/dev-tools/skills/architecture-patterns/SKILL.md
    target: .opencode/skills/architecture-patterns.md
    fidelity: 68
  - source: claude/dev-tools/skills/code-quality/SKILL.md
    target: .opencode/skills/code-quality.md
    fidelity: 68
  - source: claude/dev-tools/skills/changelog-format/SKILL.md
    target: .opencode/skills/changelog-format.md
    fidelity: 68
  - source: claude/dev-tools/skills/release-python-package/SKILL.md
    target: .opencode/skills/release-python-package.md
    fidelity: 67
  - source: claude/dev-tools/skills/feature-dev/SKILL.md
    target: .opencode/skills/feature-dev.md
    fidelity: 72
  - source: claude/dev-tools/skills/docs-manager/SKILL.md
    target: .opencode/skills/docs-manager.md
    fidelity: 80
  - source: claude/sdd-tools/skills/create-spec/SKILL.md
    target: .opencode/skills/create-spec.md
    fidelity: 59
  - source: claude/sdd-tools/skills/analyze-spec/SKILL.md
    target: .opencode/skills/analyze-spec.md
    fidelity: 54
  - source: claude/sdd-tools/skills/create-tasks/SKILL.md
    target: .opencode/skills/create-tasks.md
    fidelity: 57
  - source: claude/sdd-tools/skills/execute-tasks/SKILL.md
    target: .opencode/skills/execute-tasks.md
    fidelity: 77
  - source: claude/tdd-tools/skills/create-tdd-tasks/SKILL.md
    target: .opencode/skills/create-tdd-tasks.md
    fidelity: 62
  - source: claude/tdd-tools/skills/execute-tdd-tasks/SKILL.md
    target: .opencode/skills/execute-tdd-tasks.md
    fidelity: 68
  - source: claude/tdd-tools/skills/generate-tests/SKILL.md
    target: .opencode/skills/generate-tests.md
    fidelity: 82
  - source: claude/tdd-tools/skills/tdd-cycle/SKILL.md
    target: .opencode/skills/tdd-cycle.md
    fidelity: 68
  - source: claude/tdd-tools/skills/analyze-coverage/SKILL.md
    target: .opencode/skills/analyze-coverage.md
    fidelity: 56
  - source: claude/git-tools/skills/git-commit/SKILL.md
    target: .opencode/skills/git-commit.md
    fidelity: 39
  - source: claude/core-tools/agents/code-explorer.md
    target: .opencode/agents/code-explorer.md
    fidelity: 56
  - source: claude/core-tools/agents/code-synthesizer.md
    target: .opencode/agents/code-synthesizer.md
    fidelity: 76
  - source: claude/core-tools/agents/code-architect.md
    target: .opencode/agents/code-architect.md
    fidelity: 75
  - source: claude/dev-tools/agents/code-reviewer.md
    target: .opencode/agents/code-reviewer.md
    fidelity: 77
  - source: claude/dev-tools/agents/changelog-manager.md
    target: .opencode/agents/changelog-manager.md
    fidelity: 95
  - source: claude/dev-tools/agents/docs-writer.md
    target: .opencode/agents/docs-writer.md
    fidelity: 97
  - source: claude/tdd-tools/agents/test-reviewer.md
    target: .opencode/agents/test-reviewer.md
    fidelity: 100
  - source: claude/tdd-tools/agents/test-writer.md
    target: .opencode/agents/test-writer.md
    fidelity: 79
  - source: claude/sdd-tools/agents/spec-analyzer.md
    target: .opencode/agents/spec-analyzer.md
    fidelity: 84
  - source: claude/sdd-tools/agents/researcher.md
    target: .opencode/agents/researcher.md
    fidelity: 100
  - source: claude/sdd-tools/agents/task-executor.md
    target: .opencode/agents/task-executor.md
    fidelity: 82
  - source: claude/tdd-tools/agents/tdd-executor.md
    target: .opencode/agents/tdd-executor.md
    fidelity: 87
  - source: claude/sdd-tools/hooks/hooks.json
    target: .opencode/hooks/sdd-tools-hooks.js
    fidelity: 85
  - source: claude/core-tools/hooks/hooks.json
    target: .opencode/hooks/core-tools-hooks.md
    fidelity: 48
PORT-METADATA -->
