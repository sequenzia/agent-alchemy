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
