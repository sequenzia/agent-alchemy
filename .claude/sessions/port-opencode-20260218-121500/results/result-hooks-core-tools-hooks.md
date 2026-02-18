# Conversion Result: hooks-core-tools-hooks

## Metadata

| Field | Value |
|-------|-------|
| Component ID | hooks-core-tools-hooks |
| Component Type | hooks |
| Group | core-tools |
| Name | hooks |
| Source Path | claude/core-tools/hooks/hooks.json |
| Target Path | .opencode/plugins/core-tools-hooks/ |
| Fidelity Score | 48% |
| Fidelity Band | red |
| Status | limited |

## Converted Content

~~~
## Hooks: Not Fully Supported on OpenCode

OpenCode does not support shell-command-based lifecycle hooks. The Claude Code
`PreToolUse` event maps to OpenCode's `tool.execute.before` JS/TS plugin API,
but the auto-approve behavior implemented via shell script outputting
`permissionDecision` JSON has no equivalent in OpenCode's permission model.

**Impact**: File operations targeting deep-analysis session directories
(`.claude/sessions/__da_live__/`, `.claude/sessions/exploration-cache/`,
`.claude/sessions/da-*/`) that were previously auto-approved will require
manual permission approval in OpenCode each session.

**Overall hook fidelity**: 48%

---

### PreToolUse: Auto-Approve Deep-Analysis Session Files

- **Source**: `claude/core-tools/hooks/hooks.json`
- **Matcher**: Write|Edit|Bash
- **Purpose**: Automatically approves Write, Edit, and Bash operations targeting
  deep-analysis session directories, enabling autonomous exploration without
  manual permission prompts per operation.
- **Script**: `claude/core-tools/hooks/auto-approve-da-session.sh`
- **Behavioral category**: auto-approve
- **Severity**: Functional

**Why not directly converted**: OpenCode's `tool.execute.before` event is a
JS/TS plugin API. The source hook uses a shell script that reads stdin JSON and
outputs `permissionDecision` JSON — a Claude Code-specific protocol. OpenCode
has no equivalent path-pattern-based auto-approval mechanism. Its permission
system (allow/ask/deny) operates at the tool level globally, not per file path.

<!-- RESOLVED: PreToolUse_auto-approve — Manual "Allow for session" workflow documented as workaround. No path-based auto-approval available in OpenCode. Workaround applied globally. -->

**OpenCode workaround**: Use OpenCode's built-in permission system:
1. When OpenCode prompts for Write/Edit/Bash operations on files under
   `.claude/sessions/__da_live__/`, `.claude/sessions/exploration-cache/`, or
   `.claude/sessions/da-*/`, select "Allow for session".
2. This grants permission for that tool on those paths for the remainder of the
   session.
3. This must be done manually on first encounter each session.
4. No path-based pattern auto-approval is configurable in OpenCode.

**Impact**: Users will see permission prompts for session file operations that
were previously auto-approved. Autonomous deep-analysis execution workflows
will require manual permission grant at first Write/Edit/Bash boundary per
session. After granting "Allow for session", subsequent operations in the same
session will not prompt again.

---

### Script Reference (Not Ported)

The source script `claude/core-tools/hooks/auto-approve-da-session.sh` cannot
be ported directly because:

1. OpenCode's plugin API is JS/TS, not shell-based
2. The `permissionDecision` JSON protocol is Claude Code-specific
3. OpenCode has no equivalent stdin/stdout hook execution model

The script logic (path pattern matching for DA session directories) is
documented above in the workaround section so the behavior can be replicated
manually or via a future OpenCode plugin if the platform adds path-based
permission rules.
~~~

## Fidelity Report

| Mapping Type | Count | Weight | Contribution |
|-------------|-------|--------|-------------|
| Direct | 0 | 1.0 | 0.0 |
| Workaround | 1 | 0.7 | 0.7 |
| TODO | 0 | 0.2 | 0.0 |
| Omitted | 1 | 0.0 | 0.0 |
| **Total** | **2** | | **0.7** |

**Notes:** Hook fidelity calculated using hook-converter weighted formula rather than the standard feature-count formula, as specified in hook-converter.md. Hook entries scored:

- Event type mapping: `PreToolUse` has a target event (`tool.execute.before`) but the execution model is fundamentally incompatible (JS/TS plugin API vs. shell command with stdin/stdout protocol). Partial credit applied: 0.5 * 0.40 = 0.20
- Matcher transformation: All 3 tools map directly (Write→write, Edit→edit, Bash→bash): 3/3 = 1.0 * 0.20 = 0.20
- Command/script portability: Shell script cannot run as-is in JS/TS plugin context; no ported script produced: 0.0 * 0.25 = 0.00
- Behavioral equivalence: No path-pattern auto-approval available; manual "Allow for session" workaround achieves partial parity: 0.5 * 0.15 = 0.075

Total: (0.20 + 0.20 + 0.00 + 0.075) * 100 = 47.5% → rounded to 48%

Feature-count breakdown for standard scoring tables: the PreToolUse hook entry treated as `workaround` (documented migration path exists); the script file treated as `omitted` (not portable to target platform). Total 2 discrete features: 0 direct + 1 workaround + 0 todo + 1 omitted.

## Decisions

| Feature | Decision Type | Original | Converted | Rationale | Confidence | Resolution Mode |
|---------|-------------|----------|-----------|-----------|------------|----------------|
| PreToolUse event | workaround | `PreToolUse` shell hook → `permissionDecision` JSON | Migration guide with "Allow for session" manual workflow | OpenCode's `tool.execute.before` is JS/TS API; shell-based auto-approve protocol is Claude Code-specific. Best available workaround is manual permission grant documented in migration guide. | medium | individual |
| Matcher tools (Write, Edit, Bash) | direct | `Write\|Edit\|Bash` | `write`, `edit`, `bash` — all tools map 1:1 | All three tools have direct equivalents in OpenCode tool name mappings at high confidence. Not used in converted output since no hook config file is generated, but documented for reference. | high | auto |
| Shell script auto-approve-da-session.sh | omitted | `bash ${CLAUDE_PLUGIN_ROOT}/hooks/auto-approve-da-session.sh` | Not ported | Script uses Claude Code-specific stdin JSON + stdout `permissionDecision` protocol. OpenCode has no shell hook execution model. Script logic documented in migration guide. | high | individual |

## Gaps

| Feature | Reason | Severity | Workaround | User Acknowledged |
|---------|--------|----------|------------|-------------------|
| PreToolUse auto-approve hook (path-based) | OpenCode has no shell-command hook system. The `tool.execute.before` JS/TS plugin API exists but cannot replicate path-pattern auto-approval via shell scripts. OpenCode's permission system is tool-level only, not path-pattern-based. | functional | Use OpenCode's "Allow for session" permission grant when first prompted for Write/Edit/Bash on deep-analysis session directories each session. | false |
| auto-approve-da-session.sh script | Shell script uses Claude Code-specific `permissionDecision` JSON protocol on stdin/stdout. No equivalent JS/TS plugin for OpenCode produced. Path pattern matching logic is documented for manual reference. | functional | Script logic documented in migration guide; no equivalent plugin generated. Manual permission flow replaces automated approval. | false |

## Unresolved Incompatibilities

| Group Key | Feature | Severity | Category | Reason | Suggested Workaround | Confidence | Affected Locations |
|-----------|---------|----------|----------|--------|---------------------|------------|-------------------|
| (all resolved — auto-applied workarounds globally) | | | | | | | |
