# Communication Protocols Reference

For generic SendMessage types (message, broadcast, shutdown_request, shutdown_response, plan_approval_response), delivery mechanics, and best practices, see the claude-code-teams messaging protocol reference:

```
Read ${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/claude-code-teams/references/messaging-protocol.md
```

This file documents the **SDD-specific message schemas** used within the run-tasks 3-tier hierarchy (Orchestrator, Wave Lead, Context Manager, Task Executors). All messages use plain-text structured formats with labeled section headers.

---

## Protocol 1: Orchestrator to Wave Lead (via Task prompt)

**Direction**: Orchestrator -> Wave Lead
**Transport**: Task tool prompt (wave-lead is launched with this as its initial prompt)
**Phase**: Phase 1

The orchestrator provides the wave assignment as the wave-lead agent's launch prompt. This is not a SendMessage call but rather the initial context injected when spawning the wave-lead via `Task`.

### Schema

| Field | Required | Description |
|-------|----------|-------------|
| `Wave` | Required | Wave number and total waves (e.g., `2 of 4`) |
| `Max Parallel` | Required | Hint for concurrent executor count |
| `Max Retries` | Required | Number of autonomous retry attempts per tier |
| `Retry Partial` | Required | Whether to retry PARTIAL tasks (`true` or `false`). When `false`, PARTIAL tasks are marked completed. |
| `CM Threshold` | Required | Minimum task count to spawn a Context Manager. Waves with fewer tasks skip CM spawning. |
| `Session Dir` | Required | Absolute path to `.claude/sessions/__live_session__/` |
| `TASKS` | Required | List of tasks with full details (see sub-fields below) |
| `CROSS-WAVE CONTEXT` | Optional | Summary of `execution_context.md` from prior waves. Omitted for Wave 1 if no prior context exists. |
| `PRODUCER OUTPUTS` | Optional | Structured per-task producer results for tasks with `produces_for` dependencies. Omitted when no tasks have producer relationships. |

**Task sub-fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `Task #{id}` | Required | Task ID and subject |
| `Description` | Required | Full task description including acceptance criteria |
| `Acceptance Criteria` | Optional | Extracted criteria if present in description |
| `Priority` | Required | Task priority (critical, high, medium, low, unprioritized) |
| `Complexity` | Optional | Task complexity (XS, S, M, L, XL). Omitted if not specified. |
| `Metadata` | Optional | Additional metadata (spec_path, task_group, spec_phase, etc.). Omitted if empty. |

### Example Message

```
WAVE ASSIGNMENT
Wave: 2 of 4
Max Parallel: 5
Max Retries: 3
Retry Partial: false
CM Threshold: 3
Session Dir: /Users/dev/my-project/.claude/sessions/__live_session__/

TASKS:
- Task #5: Implement user authentication middleware
  Description: Create Express middleware that validates JWT tokens...
  Acceptance Criteria:
    _Functional:_
    - [ ] Middleware extracts Bearer token from Authorization header
    - [ ] Invalid tokens return 401 with error message
    _Edge Cases:_
    - [ ] Missing Authorization header returns 401
  Priority: critical
  Complexity: M
  Metadata: spec_path=internal/specs/auth-SPEC.md, task_group=auth-feature, spec_phase=1

- Task #6: Create user session store
  Description: Implement Redis-backed session storage...
  Priority: high
  Complexity: S

CROSS-WAVE CONTEXT:
Wave 1 completed: Tasks #1 (PASS), #2 (PASS), #3 (PASS), #4 (PASS)
Learnings:
- Runtime: Node.js 22 with pnpm
- Tests: vitest with `__tests__/{name}.test.ts` pattern
- Imports: Named exports, barrel files for public API
Key Decisions:
- [Task #1] Used Zod for runtime validation
- [Task #2] Shared types in `src/types/` directory
Issues:
- Vitest mock.calls behavior differs from Jest -- reset between tests
```

---

## Protocol 2: Wave Lead to Orchestrator (via SendMessage)

**Direction**: Wave Lead -> Orchestrator
**Transport**: SendMessage
**Phase**: Phase 1

Sent by the wave-lead to the orchestrator after all executors in the wave have completed (or timed out). This is the primary result channel for the orchestrator to understand wave outcomes.

### Schema

| Field | Required | Description |
|-------|----------|-------------|
| `Wave` | Required | Wave number |
| `Duration` | Required | Total wave duration from first executor launch to last result |
| `Tasks Passed` | Required | Count of tasks with PASS status |
| `Tasks Partial` | Required | Count of tasks with PARTIAL status (completed without retry when `retry_partial: false`) |
| `Tasks Failed` | Required | Count of tasks with FAIL status (or PARTIAL when `retry_partial: true` and retries exhausted) |
| `Tasks Skipped` | Required | Count of tasks not attempted (spawn failure, shutdown, etc.) |
| `RESULTS` | Required | Per-task breakdown (see sub-fields below) |
| `FAILED TASKS (for escalation)` | Optional | Failed task details for Tier 3 escalation. Omit section entirely if no tasks failed. |
| `CONTEXT UPDATES` | Optional | Summary of new learnings from this wave. Omit if no new learnings. |
| `CLEANUP` | Required | Sub-agent shutdown results from the wave-lead's Step 6b. Always include — gives the orchestrator visibility into cleanup success. |

**Cleanup sub-fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `Agents shutdown cooperatively` | Required | Count of agents that responded to `shutdown_request` with `approve: true` |
| `Agents force-stopped` | Required | Count of agents terminated via `TaskStop` (did not respond within 15s) |
| `Agents already terminated` | Required | Count of agents where `SendMessage` failed (already gone before shutdown attempt) |

**Results sub-fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `Task #{id}` | Required | Task ID, status, and duration |
| `Summary` | Required | Brief description of what was accomplished or why it failed |
| `Files` | Optional | Comma-separated list of modified files. Omit if no files were modified. |
| `Tokens` | Optional | Estimated token usage for the executor (if available from wave-lead tracking). Omit if unavailable. |

**Failed Tasks sub-fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `Task #{id}` | Required | Task ID and failure reason |
| `Tier 1 Retry` | Required | Whether Tier 1 retry was attempted and the outcome |
| `Tier 2 Retry` | Required | Whether Tier 2 retry was attempted and the outcome |

### Example Message

```
WAVE SUMMARY
Wave: 2
Duration: 8m 32s
Tasks Passed: 3
Tasks Partial: 0
Tasks Failed: 1
Tasks Skipped: 0

RESULTS:
- Task #5: PASS (3m 10s)
  Summary: Implemented JWT authentication middleware with token extraction and validation
  Files: src/middleware/auth.ts, src/middleware/__tests__/auth.test.ts

- Task #6: PASS (2m 45s)
  Summary: Created Redis-backed session store with TTL management
  Files: src/services/session-store.ts, src/services/__tests__/session-store.test.ts

- Task #7: PASS (4m 01s)
  Summary: Added user profile API endpoint with CRUD operations
  Files: src/api/users/route.ts, src/api/users/__tests__/route.test.ts

- Task #8: FAIL (5m 22s)
  Summary: Rate limiter implementation failed -- Redis connection pooling caused test timeouts
  Files: src/middleware/rate-limiter.ts

FAILED TASKS (for escalation):
- Task #8: Redis connection pool exhaustion during concurrent test execution
  Tier 1 Retry: attempted -> FAIL (same connection pool issue)
  Tier 2 Retry: attempted -> FAIL (enriched context did not resolve pool config)

CONTEXT UPDATES:
- Redis connection pooling requires explicit pool size configuration in test environment
- Auth middleware follows `src/middleware/{name}.ts` pattern with co-located tests
- Session TTL defaults should be configurable via environment variables

CLEANUP:
Agents shutdown cooperatively: 3
Agents force-stopped: 1
Agents already terminated: 0
```

---

## Protocol 3: Task Executor to Wave Lead (via SendMessage)

**Direction**: Task Executor -> Wave Lead
**Transport**: SendMessage
**Phase**: Phase 1

Sent by each task executor to the wave-lead upon completing a task (whether PASS, PARTIAL, or FAIL). This is the primary result channel for the wave-lead to track executor completion.

### Schema

| Field | Required | Description |
|-------|----------|-------------|
| `Task` | Required | Task ID (e.g., `#5`) |
| `Status` | Required | One of: `PASS`, `PARTIAL`, `FAIL` |
| `Summary` | Required | 1-3 sentence description of what was accomplished or what failed |
| `Files Modified` | Optional | List of files created, modified, or deleted. Each entry: `{path} (created\|modified\|deleted)`. Omit section if no files were changed. |
| `Verification` | Required | List of criteria checked with PASS/FAIL status per criterion |
| `Issues` | Optional | List of issues encountered. Omit section if no issues. |

**Status values:**
- **PASS**: All Functional criteria met and all tests pass
- **PARTIAL**: Core functionality works but non-critical criteria (Edge Cases, Error Handling, Performance) have issues
- **FAIL**: Any Functional criterion unmet, any test failure, or unrecoverable implementation error

### Example Message

```
TASK RESULT
Task: #5
Status: PASS
Summary: Implemented JWT authentication middleware that extracts Bearer tokens from the Authorization header, validates them using jsonwebtoken library, and attaches decoded user data to the request object.
Files Modified:
- src/middleware/auth.ts (created)
- src/middleware/__tests__/auth.test.ts (created)
- src/types/express.d.ts (modified)
Verification:
- [PASS] Middleware extracts Bearer token from Authorization header
- [PASS] Invalid tokens return 401 with error message
- [PASS] Missing Authorization header returns 401
Issues:
```

**Example with failure:**

```
TASK RESULT
Task: #8
Status: FAIL
Summary: Rate limiter skeleton implemented but Redis connection pool exhaustion causes all concurrent tests to time out after 30 seconds.
Files Modified:
- src/middleware/rate-limiter.ts (created)
- src/middleware/__tests__/rate-limiter.test.ts (created)
Verification:
- [PASS] Rate limiter tracks request counts per IP
- [FAIL] Rate limiter returns 429 when limit exceeded -- test timed out
- [FAIL] Rate limiter resets after window expires -- test timed out
Issues:
- Redis connection pool exhausted during concurrent test execution (pool size: 10, tests need: 15+)
- Test timeout at 30s suggests pool starvation, not logic error
```

**Example with no files or issues (documentation-only task):**

```
TASK RESULT
Task: #12
Status: PASS
Summary: Created API documentation reference with all endpoint schemas and example requests.
Files Modified:
- docs/api-reference.md (created)
Verification:
- [PASS] All endpoints documented with request/response schemas
- [PASS] Example requests included for each endpoint
```

---

## Protocol 4: Task Executor to Context Manager (via SendMessage)

**Direction**: Task Executor -> Context Manager
**Transport**: SendMessage
**Phase**: Phase 2 (defined here for consistency; Context Manager is a Phase 2 agent)

Sent by each task executor to the Context Manager alongside the result message to the wave-lead. Contains learnings, patterns, and decisions discovered during task execution that may benefit other executors in the current or future waves.

### Schema

| Field | Required | Description |
|-------|----------|-------------|
| `Task` | Required | Task ID (e.g., `#5`) |
| `Decisions` | Optional | Key implementation decisions and their rationale. Omit section if no significant decisions were made. |
| `Patterns` | Optional | Coding patterns discovered or followed. Omit section if none. |
| `Insights` | Optional | Useful information for other tasks (file locations, build commands, gotchas). Omit section if none. |
| `Issues` | Optional | Problems encountered and workarounds applied. Omit section if none. |

At least one of the optional sections must be present. If the task had no learnings worth sharing, include a minimal Insights entry noting the task completed without notable discoveries.

### Example Message

```
CONTEXT CONTRIBUTION
Task: #5
Decisions:
- Used jsonwebtoken library (already in package.json) over jose for JWT validation
- Attached decoded token to `req.user` following existing middleware pattern in src/middleware/cors.ts
Patterns:
- Middleware files follow `src/middleware/{name}.ts` with co-located `__tests__/{name}.test.ts`
- Error responses use `{ error: string, code: string }` shape consistently
Insights:
- Express type augmentation lives in `src/types/express.d.ts` -- extend this for new request properties
- Test helper `createMockRequest()` available in `src/test-utils/express.ts`
Issues:
- TypeScript strict mode required explicit null checks on `req.headers.authorization` -- not obvious from existing code
```

**Minimal example (no notable learnings):**

```
CONTEXT CONTRIBUTION
Task: #12
Insights:
- Task completed without notable discoveries; followed existing patterns
```

---

## Protocol 5: Context Manager to Task Executors (via SendMessage)

**Direction**: Context Manager -> Task Executors
**Transport**: SendMessage
**Phase**: Phase 2 (defined here for consistency; Context Manager is a Phase 2 agent)

Sent by the Context Manager to each task executor at the start of their execution. Provides a curated summary of project context accumulated from prior waves and the current wave's early completions.

### Schema

| Field | Required | Description |
|-------|----------|-------------|
| `Wave` | Required | Current wave number |
| `PROJECT SETUP` | Optional | Tech stack, build commands, environment details. Omit if not yet discovered. |
| `CONVENTIONS` | Optional | Coding style, naming patterns, import conventions. Omit if not yet discovered. |
| `KEY DECISIONS` | Optional | Architecture choices from prior waves. Omit if no decisions recorded yet. |
| `KNOWN ISSUES` | Optional | Problems to avoid, workarounds in place. Omit if none. |

For Wave 1, some or all sections may be empty if no prior context exists. The Context Manager should still send the message with the wave number and whatever context is available (even if minimal).

### Example Message

```
SESSION CONTEXT
Wave: 2

PROJECT SETUP:
- Runtime: Node.js 22 with pnpm package manager
- Test framework: Vitest with `__tests__/{name}.test.ts` pattern
- Build: `pnpm build` (TypeScript compilation via tsc)
- Lint: `pnpm lint` (ESLint with TypeScript plugin)

CONVENTIONS:
- Named exports only; barrel files (`index.ts`) for public API surfaces
- Error responses: `{ error: string, code: string }` shape
- Middleware pattern: `src/middleware/{name}.ts` with co-located tests
- Import style: absolute imports via `@/` path alias

KEY DECISIONS:
- [Task #1] Zod for runtime validation (over io-ts) -- better TypeScript inference
- [Task #2] Shared types in `src/types/` directory
- [Task #5] JWT validation via jsonwebtoken library (already in deps)

KNOWN ISSUES:
- Vitest mock.calls behavior differs from Jest -- must reset mocks between tests
- Redis connection pool requires explicit size config in test environment (default too small for concurrent tests)
```

**Wave 1 example (minimal context):**

```
SESSION CONTEXT
Wave: 1

PROJECT SETUP:
- See CLAUDE.md for project conventions (no prior wave data available)
```

---

## Protocol 6: Context Manager to Wave Lead (Tier 2 enrichment)

**Direction**: Context Manager -> Wave Lead
**Transport**: SendMessage (on Tier 2 enrichment request from wave-lead)
**Phase**: Phase 2 (defined here for consistency; Context Manager is a Phase 2 agent)

Sent by the Context Manager to the wave-lead when a Tier 2 retry is requested for a failed task. The wave-lead asks the Context Manager for enriched context related to the specific failure, and the Context Manager responds with detailed project context that may help the retry succeed.

### Schema

| Field | Required | Description |
|-------|----------|-------------|
| `Task` | Required | Task ID of the failed task (e.g., `#8`) |
| `Original Failure` | Required | The failure reason from the Tier 1 attempt |
| `ADDITIONAL CONTEXT` | Required | Detailed project context relevant to this task's failure. Must include at least one of: related task results, relevant conventions, or supplementary technical context. |

**Additional Context sub-sections (all optional, at least one required):**

| Sub-section | Description |
|-------------|-------------|
| Related task results | Results from tasks that touched similar files or systems |
| Relevant conventions | Project patterns that may inform the fix |
| Supplementary context | Technical details, configuration notes, or workarounds from prior waves |

### Example Message

```
ENRICHED CONTEXT
Task: #8
Original Failure: Redis connection pool exhaustion during concurrent test execution

ADDITIONAL CONTEXT:
Related task results:
- Task #6 (PASS): Created Redis-backed session store with pool size of 20 -- tests passed with explicit pool.end() in afterAll()
- Task #5 (PASS): Auth middleware tests use mock Redis, not real connections

Relevant conventions:
- Test files must call pool.end() in afterAll() to release Redis connections
- Concurrent test suites use `--pool forks` vitest flag to isolate connection pools
- Redis test config lives in `src/config/test.ts` with `REDIS_POOL_SIZE=20`

Supplementary context:
- The project uses ioredis (not node-redis) -- connection pooling API differs
- Vitest runs test files in parallel by default; each file gets its own module scope but shares the process-level connection pool
```

---

## Malformed Message Handling

If an agent receives a message that does not match the expected schema:

1. **Missing required fields**: Log a warning noting which fields are missing. Attempt to proceed with available data if possible (e.g., a TASK RESULT without a Summary can still be processed for status). If critical fields are missing (Task ID, Status), treat the message as unprocessable.

2. **Unexpected format**: If the message structure does not match any known protocol (no recognizable header like `TASK RESULT`, `WAVE SUMMARY`, etc.), log the raw message content and treat it as an error. For wave-leads receiving unrecognized executor messages, record the executor as failed with reason "malformed result message."

3. **Extra fields**: Ignore any fields not defined in the schema. Do not reject messages that contain additional information beyond the schema.

4. **Empty optional sections**: Optional sections may be omitted entirely (section header and content both absent). This is normal and should not trigger warnings. Do not include empty section headers with no content -- simply omit the section.

---

## Shutdown Lifecycle

Agent shutdown follows the claude-code-teams shutdown protocol (`shutdown_request` / `shutdown_response` via SendMessage). See the claude-code-teams messaging protocol reference for the generic shutdown mechanics.

The SDD-specific shutdown sequence uses **defense-in-depth** — multiple layers ensure all agents are terminated before the next wave begins, even if any single layer fails.

### Layer 1: Wave-Lead Internal Cleanup (wave-lead Step 6b)

After all executors complete and Context Manager finalizes:

1. Wave-lead sends `shutdown_request` to all task executors and context manager
2. Wave-lead waits 15 seconds for `shutdown_response` from each agent
3. Wave-lead force-stops non-responsive agents via `TaskStop`
4. Wave-lead waits 2 seconds for terminations to propagate
5. Wave-lead reports cleanup results in the CLEANUP section of the WAVE SUMMARY

This is the first and most cooperative layer. If the wave-lead completes Step 6b fully, the orchestrator's verification (Layer 2) will find all agents already terminated.

### Layer 2: Orchestrator Verification (orchestration Step 5g-2)

After receiving the wave summary and shutting down the wave-lead:

1. Orchestrator reads `~/.claude/teams/{wave-team-name}/config.json` to enumerate ALL team members
2. Orchestrator sends `shutdown_request` to any member not yet confirmed terminated
3. Orchestrator waits 5 seconds for responses (batch wait, not per-agent)
4. Orchestrator force-stops non-responsive agents via `TaskStop`

This layer does NOT trust the wave-lead's self-reported cleanup. It independently verifies by reading the team config and checking each member. This catches cases where the wave-lead skipped or partially completed Step 6b.

### Layer 3: TeamDelete with Retry (orchestration Step 5g-3)

1. Orchestrator calls `TeamDelete`
2. On failure: force-stop ALL members again via `TaskStop`, retry `TeamDelete` (up to 3 attempts total)
3. On persistent failure: escalate to user (force retry / skip cleanup and continue / abort session)

### Layer 4: Inter-Wave Verification (orchestration Step 5h)

Before starting the next wave:

1. Orchestrator verifies previous wave's team directory is removed
2. Brief 2-second cooldown for async cleanup propagation
3. Proceed to next wave only after verification passes

### Crash Scenario Cleanup

If the wave-lead crashes, Layer 1 is skipped (wave-lead never executed its cleanup). The orchestrator compensates with an aggressive variant of Layer 2: force-stop ALL members immediately via `TaskStop` without attempting cooperative shutdown first (agents are likely unresponsive after a crash), then proceed to Layer 3.
