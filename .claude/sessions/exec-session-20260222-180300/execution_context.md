# Execution Context

## Project Patterns
- Plugin naming: `agent-alchemy-{group-name}` for marketplace, `{group-name}` for directory
- Reference files: H1 title, intro paragraph, structured sections with tables/code/bullets
- Agent frontmatter: `name`, `description`, `model`, `tools`, `skills` in YAML + markdown system prompt
- Phase-based workflows with "CRITICAL: Complete ALL N phases" directive
- Hook scripts: trap ERR, debug function, jq parsing. All hooks must NEVER exit non-zero
- Shared test fixtures: `claude/sdd-tools/tests/fixtures/`

## Key Decisions
- [Task #155] Structured context schema: 6 sections; compaction at 10+ entries
- [Task #156] task-executor.md has embedded rules (414 lines); reference files documentation-only
- [Task #161] Watch-first, poll-fallback completion detection
- [Task #163] File conflict detection at Step 7a.5
- [Task #164] produces_for injection uses `CONTEXT FROM COMPLETED DEPENDENCIES` header
- [Task #166] 3-tier retry escalation: Standard → Context Enrichment → User Escalation
- [Task #167] Progress streaming: session start, wave start, wave completion summaries
- [Task #168] Post-merge validation: OK/WARN/ERROR; force compaction at >1000 lines
- [Task #165] create-tasks now 9 phases; Phase 6 = producer-consumer detection
- [Task #169] task-executor.md result file format is authoritative; orchestration.md needs updating

## Known Issues
- Result file format in orchestration.md (Result File Protocol + 7c prompt template) doesn't match task-executor.md. Non-blocking: validate-result.sh enforces correct format.
- SKILL.md and orchestration.md step numbering diverge at Step 5/5.5
- Concurrent edits to orchestration.md caused Edit conflicts in Wave 3a
- hooks.json timeout field is in seconds, not milliseconds

## File Map
- `claude/sdd-tools/skills/execute-tasks/references/orchestration.md` — ~1223 lines
- `claude/sdd-tools/agents/task-executor.md` — 414 lines with embedded rules
- `claude/sdd-tools/skills/execute-tasks/references/execution-workflow.md` — 380 lines, documentation-only
- `claude/sdd-tools/skills/execute-tasks/scripts/watch-for-results.sh` — Event-driven watcher
- `claude/sdd-tools/skills/execute-tasks/scripts/poll-for-results.sh` — Adaptive polling (133 lines)
- `claude/sdd-tools/hooks/validate-result.sh` — Result validation (~100 lines)
- `claude/sdd-tools/skills/create-tasks/SKILL.md` — 9-phase workflow (~738 lines)

## Task History
### Prior Sessions Summary
Previous session implemented 14 TDD tools plugin tasks. All passed.

### Tasks [155-161]: Foundation — ALL PASS
Structured context schema, embedded rules, watch/poll scripts, validation hook, event-driven detection.

### Tasks [163-168]: Orchestration hardening — ALL PASS
Conflict detection, produces_for, retry escalation, progress streaming, merge validation.

### Tasks [162, 165]: Tests and create-tasks — ALL PASS
44 bats tests passing. create-tasks Phase 6 for produces_for detection.

### Task [169]: E2E validation — PASS
10/10 features validated, 44/44 tests pass, 1 non-blocking format inconsistency noted.
