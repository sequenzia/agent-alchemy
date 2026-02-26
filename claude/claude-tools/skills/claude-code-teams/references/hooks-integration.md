# Hooks Integration Reference

Hook events for Agent Teams enable quality gates and automation at key lifecycle points. Use these hooks to enforce standards, validate output, and coordinate team behavior without modifying skill or agent logic.

This reference covers two team-specific hook events: **TeammateIdle** and **TaskCompleted**. Both support command, prompt, and agent hook types.

---

## TeammateIdle Hook Event

### Trigger

Fires when a teammate goes idle — that is, when the teammate's turn ends and it has no pending messages or work. This is the natural resting state between work assignments. The hook fires each time a teammate transitions to idle, not just the first time.

### Input Schema

The hook receives a JSON object on stdin with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `agent_name` | string | Name of the idle teammate (e.g., `"researcher-1"`). Matches the `name` parameter from the Task spawn call. |
| `team_name` | string | Name of the team the teammate belongs to (e.g., `"analysis-team"`). |
| `session_id` | string | The teammate's Claude Code session identifier. Unique per spawn; can be used to correlate logs and artifacts. |
| `task_list_id` | string | The task list ID associated with the team. Can be used to query task status via the Tasks API. |
| `agent_type` | string | Whether the agent is `"lead"` or `"member"`. Useful for hooks that should only apply to members. |
| `idle_count` | number | How many times this teammate has gone idle during its lifetime. Starts at 1 on first idle event. |

### Hook Types Supported

| Type | Supported | Description |
|------|-----------|-------------|
| `command` | Yes | Runs a shell script. Receives the input schema as JSON on stdin. |
| `prompt` | Yes | Injects a natural language instruction into the agent's context before idle processing. |
| `agent` | Yes | Spawns a subagent to evaluate whether the teammate should remain idle. |

### Practical Example: Quality Gate on Idle

A command hook that checks whether a teammate completed its assigned task before going idle. If the teammate has pending tasks in a non-completed state, the hook blocks the idle transition and sends feedback instructing the teammate to continue working.

```bash
#!/usr/bin/env bash
# hooks/check-idle-quality.sh
# Verify teammate completed assigned work before allowing idle

set -euo pipefail

# Read hook input from stdin
INPUT=$(cat)

AGENT_NAME=$(echo "$INPUT" | jq -r '.agent_name')
TEAM_NAME=$(echo "$INPUT" | jq -r '.team_name')
TASK_LIST_ID=$(echo "$INPUT" | jq -r '.task_list_id')

# Check if the teammate has incomplete tasks
TASKS_DIR="$HOME/.claude/tasks/$TASK_LIST_ID"
if [ -d "$TASKS_DIR" ]; then
  # Look for tasks assigned to this agent that are still in_progress
  INCOMPLETE=$(find "$TASKS_DIR" -name "*.json" -exec \
    jq -r --arg agent "$AGENT_NAME" \
    'select(.metadata.assignee == $agent and .status == "in_progress") | .id' {} \; 2>/dev/null)

  if [ -n "$INCOMPLETE" ]; then
    # Exit 2: Block idle with feedback
    echo "You have incomplete tasks assigned to you. Please continue working on them before going idle: $INCOMPLETE" >&2
    exit 2
  fi
fi

# Exit 0: Allow idle to proceed
exit 0
```

---

## TaskCompleted Hook Event

### Trigger

Fires when a task's status is set to `completed` (via TaskUpdate). This applies to both team-based and standalone tasks. The hook fires after the status change is recorded but before the completion is finalized, allowing the hook to reject the completion and revert the task to its previous status.

### Input Schema

The hook receives a JSON object on stdin with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | string | ID of the task being marked as completed. |
| `task_subject` | string | The task's subject line. Useful for logging and display in hook output. |
| `owner` | string | Name of the agent that completed the task. For team tasks, this is the teammate's `agent_name`. |
| `team_name` | string or null | Team the task belongs to, or `null` for standalone tasks. |
| `task_list_id` | string | The task list ID containing this task. |
| `previous_status` | string | The task's status before it was set to completed (typically `"in_progress"`). Used by the system to revert if the hook blocks. |
| `metadata` | object | The task's full metadata object. Contains any custom fields set during task creation or update. |

### Hook Types Supported

| Type | Supported | Description |
|------|-----------|-------------|
| `command` | Yes | Runs a shell script. Receives the input schema as JSON on stdin. |
| `prompt` | Yes | Injects a natural language verification instruction before accepting completion. |
| `agent` | Yes | Spawns a subagent to validate the completed work (e.g., run tests, check output). |

### Practical Example: Verification Gate on Completion

A command hook that verifies output files exist before accepting a task as completed.

```bash
#!/usr/bin/env bash
# hooks/verify-task-output.sh
# Ensure expected output files exist before accepting task completion

set -euo pipefail

INPUT=$(cat)

TASK_ID=$(echo "$INPUT" | jq -r '.task_id')
TASK_SUBJECT=$(echo "$INPUT" | jq -r '.task_subject')
OWNER=$(echo "$INPUT" | jq -r '.owner')

# Check for expected output based on task metadata
OUTPUT_PATH=$(echo "$INPUT" | jq -r '.metadata.output_path // empty')

if [ -n "$OUTPUT_PATH" ]; then
  if [ ! -e "$OUTPUT_PATH" ]; then
    echo "Task [$TASK_ID] '$TASK_SUBJECT' completed by $OWNER but expected output not found at: $OUTPUT_PATH" >&2
    exit 2
  fi
fi

# Exit 0: Allow completion
exit 0
```

---

## Exit Code Behavior

Hooks communicate their result back to Claude Code through exit codes. The behavior is consistent across all hook types (command, prompt, agent).

| Exit Code | Meaning | Behavior |
|-----------|---------|----------|
| **0** | Hook passes | The action proceeds normally. For TeammateIdle, the teammate enters idle state. For TaskCompleted, the completion is accepted. |
| **1** | Hook error | The action proceeds (not blocked), but the error is logged. Use this for non-critical hook failures — e.g., a monitoring script that crashes should not block the workflow. |
| **2** | Block with feedback | The action is blocked and feedback is delivered back to the agent. For TeammateIdle, the teammate is told to continue working with the feedback message. For TaskCompleted, the completion is rejected and the task reverts to its previous status. |

### How Blocked Feedback Is Delivered

When a hook exits with code 2, the content written to **stderr** is captured and delivered as feedback to the agent that triggered the event:

- **TeammateIdle**: The idle teammate receives the stderr content as a message instructing it to take corrective action. The teammate remains active rather than transitioning to idle.
- **TaskCompleted**: The agent that attempted to complete the task receives the stderr content as a rejection reason. The task status reverts to `previous_status` (typically `in_progress`), and the agent can address the feedback and attempt completion again.

**Best practices for feedback messages**:
- Write clear, actionable instructions to stderr (e.g., "Tests failed. Run `pytest tests/` and fix failures before completing.")
- Keep messages concise — the agent receives them as context, so lengthy output wastes context window
- Include specific details: which files are missing, which tests failed, what criteria were not met

---

## Hook Type Support Matrix

| Event | command | prompt | agent |
|-------|---------|--------|-------|
| TeammateIdle | Supported | Supported | Supported |
| TaskCompleted | Supported | Supported | Supported |

### When to Use Each Hook Type

**Command hooks** are best for automated, deterministic checks:
- File existence validation
- Test suite execution
- Linting or formatting checks
- External API calls (e.g., CI status checks)

**Prompt hooks** are best for natural language evaluation:
- Verify acceptance criteria are met (inject criteria text, let the agent self-evaluate)
- Check documentation quality or completeness
- Enforce coding conventions that are hard to check programmatically

**Agent hooks** are best for complex, multi-step validation:
- Run a test suite, analyze failures, and provide structured feedback
- Cross-reference task output against a specification
- Perform code review on the completed changes

---

## Practical Examples

### Command Hook: Validate Task Output Files Exist

A shell script that checks whether the files a task was expected to produce actually exist on disk.

```bash
#!/usr/bin/env bash
# hooks/validate-output-files.sh
set -euo pipefail

INPUT=$(cat)
TASK_ID=$(echo "$INPUT" | jq -r '.task_id')
EXPECTED_FILES=$(echo "$INPUT" | jq -r '.metadata.expected_files[]? // empty')

MISSING=""
for FILE in $EXPECTED_FILES; do
  if [ ! -f "$FILE" ]; then
    MISSING="$MISSING\n  - $FILE"
  fi
done

if [ -n "$MISSING" ]; then
  echo "Task [$TASK_ID] is missing expected output files:$MISSING" >&2
  exit 2
fi

exit 0
```

### Prompt Hook: Verify Acceptance Criteria

A prompt hook injects a natural language instruction into the agent's context. The agent evaluates itself against the criteria before the completion is accepted.

```json
{
  "type": "prompt",
  "prompt": "Before this task can be marked complete, verify that ALL acceptance criteria from the task description are satisfied. For each criterion, confirm the implementation exists and works. If any criterion is not met, explain which one failed and what remains to be done. Only proceed if all criteria pass."
}
```

This works because prompt hooks run in the agent's context — the agent already has the task description and acceptance criteria available. The prompt instructs it to self-verify before the completion proceeds.

### Agent Hook: Run Tests and Report Results

An agent hook spawns a subagent that runs the project's test suite and evaluates the results.

```json
{
  "type": "agent",
  "agent": {
    "prompt": "Run the test suite for the project. If any tests fail, report which tests failed and why. Exit with code 2 if there are test failures, providing the failure details as feedback. Exit with code 0 if all tests pass.",
    "model": "fast"
  }
}
```

The subagent has access to the same project files and can run commands, read test output, and provide structured feedback if tests fail.

---

## hooks.json Configuration

Team hook events are configured in the plugin's `hooks.json` file, following the same structure as other Claude Code hooks. The `hooks.json` file lives at `{plugin-root}/hooks/hooks.json`.

### Structure

```json
{
  "description": "Team quality gates for task completion and idle monitoring",
  "hooks": {
    "TeammateIdle": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/check-idle-quality.sh",
            "timeout": 10
          }
        ]
      }
    ],
    "TaskCompleted": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/verify-task-output.sh",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### Configuration Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `description` | string | No | Human-readable description of the hook configuration's purpose. |
| `hooks` | object | Yes | Map of event type keys to arrays of hook entries. |
| `hooks.TeammateIdle` | array | No | Hook entries that fire when a teammate goes idle. |
| `hooks.TaskCompleted` | array | No | Hook entries that fire when a task is marked completed. |
| `hooks.<Event>[].hooks` | array | Yes | Array of hook action objects to execute for this event. |
| `hooks.<Event>[].hooks[].type` | string | Yes | Hook type: `"command"`, `"prompt"`, or `"agent"`. |
| `hooks.<Event>[].hooks[].command` | string | Conditional | Shell command to execute. Required when `type` is `"command"`. Supports `${CLAUDE_PLUGIN_ROOT}` for path resolution. |
| `hooks.<Event>[].hooks[].prompt` | string | Conditional | Natural language instruction. Required when `type` is `"prompt"`. |
| `hooks.<Event>[].hooks[].agent` | object | Conditional | Agent configuration. Required when `type` is `"agent"`. Contains `prompt` and optional `model` fields. |
| `hooks.<Event>[].hooks[].timeout` | number | No | Maximum execution time in seconds. Prevents runaway hooks from blocking the workflow. Default varies by event type. |

### Multiple Hooks per Event

You can chain multiple hooks on the same event. They execute in order, and the first hook that exits with code 2 (block) stops the chain:

```json
{
  "hooks": {
    "TaskCompleted": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/check-output-files.sh",
            "timeout": 10
          },
          {
            "type": "command",
            "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/run-tests.sh",
            "timeout": 60
          },
          {
            "type": "prompt",
            "prompt": "Verify all acceptance criteria from the task description are met before completing."
          }
        ]
      }
    ]
  }
}
```

### Context: Single-Agent vs. Multi-Agent

These hooks work in both single-agent and multi-agent contexts:

- **Multi-agent (team) context**: TeammateIdle fires for team members as they finish turns. TaskCompleted fires when any agent in the team marks a task as completed. The `team_name` field is populated in the hook input.
- **Single-agent context**: TeammateIdle does not fire (no team, no teammates). TaskCompleted fires when the single agent marks a task as completed. The `team_name` field is `null` in the hook input.

This means TaskCompleted hooks are portable across both contexts, while TeammateIdle hooks are team-specific by nature.
