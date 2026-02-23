# Execution Plan

**Task Group**: (all tasks)
**Total Tasks**: 14
**Total Waves**: 7
**Max Parallel**: 5
**Retry Limit**: 3 per task
**Generated**: 2026-02-23T18:03:03Z

## Wave 1 (5 tasks)
| Task | Subject | Priority | Unblocks |
|------|---------|----------|----------|
| #2 | Create wave-lead agent definition | — | #4, #7, #9 |
| #1 | Create run-tasks SKILL.md entry point | — | #6 |
| #3 | Create task-executor agent definition (revised) | — | #4 |
| #11 | Create auto-approve hook and hooks.json configuration | — | #13 |
| #5 | Copy and adapt verification-patterns reference | — | — |

## Wave 2 (2 tasks)
| Task | Subject | Priority | Blocked By |
|------|---------|----------|------------|
| #4 | Create communication-protocols reference | — | #2, #3 |
| #6 | Create orchestration reference - Planning phase (Steps 1-3) | — | #1 |

## Wave 3 (2 tasks)
| Task | Subject | Priority | Blocked By |
|------|---------|----------|------------|
| #7 | Create orchestration reference - Execution phase (Steps 4-7) | — | #6, #2, #4 |
| #8 | Create context-manager agent definition | — | #4 |

## Wave 4 (1 task)
| Task | Subject | Priority | Blocked By |
|------|---------|----------|------------|
| #9 | Enhance wave-lead with context management, retry, timeouts, and rate limits | — | #8, #2 |

## Wave 5 (1 task)
| Task | Subject | Priority | Blocked By |
|------|---------|----------|------------|
| #10 | Enhance orchestration with context bridge, user escalation, and crash recovery | — | #9, #7 |

## Wave 6 (2 tasks)
| Task | Subject | Priority | Blocked By |
|------|---------|----------|------------|
| #13 | Update CLAUDE.md with new architecture documentation | — | #10, #11 |
| #12 | Enhance orchestration with progress events, configuration, and plan persistence | — | #10 |

## Wave 7 (1 task)
| Task | Subject | Priority | Blocked By |
|------|---------|----------|------------|
| #14 | Create migration guide for execute-tasks to run-tasks | — | #13 |
