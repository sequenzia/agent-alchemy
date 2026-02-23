# Execution Context

## Project Patterns
- Agent definitions: YAML frontmatter (name, description, model, tools) + markdown prompt body
- Communication protocol canonical headers: WAVE ASSIGNMENT, WAVE SUMMARY, TASK RESULT, CONTEXT CONTRIBUTION, SESSION CONTEXT, ENRICHED CONTEXT
- Context manager signals: CONTEXT DISTRIBUTED, CONTEXT FINALIZED
- wave-lead.md uses step-based structure (Step 1, Step 2, etc.)

## Key Decisions
- [Task #1] 7-step orchestration loop — wave execution delegated via TeamCreate/SendMessage
- [Task #1] Session artifacts use progress.jsonl (JSONL events)
- [Task #2] 3-tier hierarchy: orchestrator -> wave-lead -> executors
- [Task #7] Wave-lead runs as foreground Task (orchestrator blocks)
- [Task #9] Per-task timeout: XS/S=5min, M=10min, L/XL=20min; metadata.timeout_minutes override
- [Task #9] Rate limit backoff: 2s, 4s, 8s, 16s, max 30s
- [Task #10] Cross-wave context bridge in Step 5d — orchestrator summarizes execution_context.md for wave-lead prompt
- [Task #10] Tier 3: Fix manually, Skip (warn downstream), Provide guidance (retry loop), Abort
- [Task #10] Crash recovery: first crash = auto retry; second crash = user escalation with 3 options

## Known Issues
- [Task #11] hooks.json schema validation requires Ajv (not globally installed)

## File Map
- `claude/sdd-tools/skills/run-tasks/SKILL.md` — Skill entry point (193 lines)
- `claude/sdd-tools/skills/run-tasks/references/orchestration.md` — Complete 7-step reference (~942 lines)
- `claude/sdd-tools/skills/run-tasks/references/verification-patterns.md` — Verification logic (message-based)
- `claude/sdd-tools/skills/run-tasks/references/communication-protocols.md` — 6 inter-agent message schemas (~416 lines)
- `claude/sdd-tools/agents/wave-lead.md` — Wave lead agent (327 lines, opus)
- `claude/sdd-tools/agents/task-executor-v2.md` — Revised task executor (SendMessage-based)
- `claude/sdd-tools/agents/context-manager.md` — Context manager agent (~265 lines, sonnet)
- `claude/sdd-tools/hooks/auto-approve-session.sh` — Auto-approve hook

## Task History
### Tasks [1-9]: All PASS (Wave 1-4 summary)
- Created: SKILL.md, wave-lead.md, task-executor-v2.md, context-manager.md, communication-protocols.md, verification-patterns.md, orchestration.md (Steps 1-7), auto-approve-session.sh
- Enhanced: wave-lead.md (165→327 lines with CM lifecycle, 3-tier retry, timeouts, rate limits)

### Task [10]: Enhance orchestration with context bridge, user escalation, crash recovery - PASS
- Files modified: orchestration.md (enhanced Step 5, ~794→942 lines)
- Added: cross-wave context bridge (5d), crash recovery (5e), Tier 3 escalation (5f)
