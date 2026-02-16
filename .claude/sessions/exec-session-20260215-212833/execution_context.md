# Execution Context

## Project Patterns
- Plugin naming: `agent-alchemy-{group-name}` for marketplace, `{group-name}` for directory
- Reference files: H1 title, intro paragraph, horizontal rule, structured sections with tables/code/bullets
- Agent frontmatter: `name`, `description`, `model`, `tools`, `skills` in YAML + markdown system prompt
- Sonnet-tier for worker agents; Opus for synthesis/review/autonomous execution
- Cross-plugin composition via `${CLAUDE_PLUGIN_ROOT}/../{plugin-name}/skills/{skill}/SKILL.md`
- Skill YAML frontmatter: name, description, argument-hint, user-invocable, disable-model-invocation, allowed-tools
- Phase-based workflows with "CRITICAL: Complete ALL N phases" directive
- AskUserQuestion enforcement with NEVER/ALWAYS examples
- Test framework detection: config files > existing tests > settings > user prompt
- Settings in `.claude/agent-alchemy.local.md` under `tdd:` namespace with kebab-case keys (unified by task #16)
- TDD pair insertion: test task inherits upstream deps, impl task adds test task to blockedBy
- Task UID convention for TDD pairs: append `:red` to original UID
- Merge mode detection uses 4 signals: metadata, paired_task_id, UID suffix, subject match
- Coverage JSON formats: Python (coverage.py with `files`/`totals`), TypeScript (istanbul with `s`/`b`/`f` maps)
- TDD compliance reporting fields: red_verified, green_verified, refactored, coverage_delta
- Context sharing between RED/GREEN phases: per-task context file + direct prompt injection

## Key Decisions
- tdd-executor: 6-phase workflow (Understand -> Write Tests -> RED -> Implement -> GREEN -> Complete)
- generate-tests: two modes (criteria-driven + code-analysis)
- tdd-cycle: 7 phases (Parse Input + Plan added vs tdd-workflow.md's 6)
- Weakest-link scoring: TDD pair (1) < same-feature cross-layer (2) < cross-feature (3)
- Settings unified to `tdd:` namespace with kebab-case (not `tdd-tools:` or underscore)

## Known Issues
<!-- No issues encountered across all 14 tasks -->

## File Map
- `claude/tdd-tools/plugin.json` — TDD tools plugin manifest
- `claude/tdd-tools/README.md` — Plugin docs with settings section
- `claude/tdd-tools/skills/generate-tests/SKILL.md` — P0 test generation, 6-phase
- `claude/tdd-tools/skills/generate-tests/references/test-patterns.md` — Framework test patterns
- `claude/tdd-tools/skills/generate-tests/references/framework-templates.md` — Auto-detection chain
- `claude/tdd-tools/skills/tdd-cycle/SKILL.md` — P0 TDD cycle, 7-phase
- `claude/tdd-tools/skills/tdd-cycle/references/tdd-workflow.md` — RED-GREEN-REFACTOR phases
- `claude/tdd-tools/skills/tdd-cycle/references/test-rubric.md` — Test quality rubric (4 dimensions)
- `claude/tdd-tools/skills/analyze-coverage/SKILL.md` — P1 coverage analysis, 6-phase
- `claude/tdd-tools/skills/analyze-coverage/references/coverage-patterns.md` — Coverage tool integration
- `claude/tdd-tools/agents/test-writer.md` — Sonnet-tier test generation worker
- `claude/tdd-tools/agents/tdd-executor.md` — Opus-tier 6-phase TDD executor
- `claude/sdd-tools/skills/create-tdd-tasks/SKILL.md` — P0 SDD-to-TDD bridge, 8-phase
- `claude/sdd-tools/skills/create-tdd-tasks/references/tdd-decomposition-patterns.md` — Task pairing rules
- `claude/sdd-tools/skills/create-tdd-tasks/references/tdd-dependency-rules.md` — Dependency insertion algorithm
- `claude/sdd-tools/skills/execute-tdd-tasks/references/tdd-execution-workflow.md` — TDD-aware wave execution
- `claude/sdd-tools/skills/execute-tdd-tasks/references/tdd-verification-patterns.md` — RED/GREEN/REFACTOR verification

## Task History
### Tasks [1-6]: Plugin structure, references, agents, generate-tests skill - ALL PASS
### Task [7]: Create tdd-cycle skill - PASS (~718 lines, 7 phases, 3 integration modes)
### Task [8]: Create TDD decomposition/dependency references - PASS (two files, ~735 lines total)
### Task [14]: Create coverage-patterns reference - PASS (~696 lines)
### Task [9]: Create create-tdd-tasks skill - PASS (~687 lines, 8-phase workflow)
### Task [10]: Create TDD execution/verification references - PASS (two files, ~786 lines total)
### Task [12]: Create behavior-driven test rubric - PASS (~531 lines, 4 scoring dimensions)
### Task [15]: Create analyze-coverage skill - PASS (~618 lines, 6-phase workflow)
### Task [16]: Add TDD settings documentation - PASS (9 files updated, unified `tdd:` namespace)
