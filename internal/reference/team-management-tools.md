# Team Management Tools API Reference

## TeamCreate

Creates a new team for coordinating multiple agents. Teams have a 1:1 correspondence with task lists.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `team_name` | string | **Yes** | Name for the new team |
| `description` | string | No | Team description/purpose |
| `agent_type` | string | No | Type/role of the team lead (e.g., "researcher", "test-runner"). Used for team file and inter-agent coordination |

### What It Creates

- Team file at `~/.claude/teams/{team-name}.json`
- Task list directory at `~/.claude/tasks/{team-name}/`

### Team Lifecycle

1. **Create team** — creates team + task list
2. **Create tasks** via TaskCreate — they auto-use the team's task list
3. **Spawn teammates** via Agent tool with `team_name` and `name` params
4. **Assign tasks** via TaskUpdate with `owner`
5. **Teammates work** — complete tasks — go idle between turns
6. **Shutdown** — send `shutdown_request` via SendMessage to each teammate
7. **Cleanup** — call TeamDelete

### Key Behaviors

- Teammates go idle after every turn — this is normal, not an error
- Messages from teammates are **automatically delivered** (no polling needed)
- Team config at `~/.claude/teams/{team-name}/config.json` contains a `members` array with `name`, `agentId`, and `agentType` per member
- Always refer to teammates by **name**, never by UUID

---

## TeamDelete

Removes team and task directories when work is complete. Takes **no parameters** — the team name is determined from the current session's team context.

### Parameters

None.

### What It Removes

- Team directory: `~/.claude/teams/{team-name}/`
- Task directory: `~/.claude/tasks/{team-name}/`
- Clears team context from the current session

### Constraints

- **Will fail if the team still has active members.** You must gracefully shut down all teammates first (via `SendMessage` with `type: "shutdown_request"`), then call TeamDelete after all have exited.

---

## SendMessage

Send messages to teammates and handle protocol requests/responses. This is the sole communication channel between agents — plain text output is **not visible** to other teammates.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | enum | **Yes** | One of: `"message"`, `"broadcast"`, `"shutdown_request"`, `"shutdown_response"`, `"plan_approval_response"` |
| `recipient` | string | Conditional | Agent name of the recipient. Required for `message`, `shutdown_request`, `plan_approval_response` |
| `content` | string | No | Message text, reason, or feedback |
| `summary` | string | Conditional | 5-10 word preview shown in UI. Required for `message` and `broadcast` |
| `request_id` | string | Conditional | ID of the request being responded to. Required for `shutdown_response` and `plan_approval_response` |
| `approve` | boolean | Conditional | Whether to approve. Required for `shutdown_response` and `plan_approval_response` |

### Message Types

#### 1. `"message"` — Direct Message (Default)

Send to a **single specific teammate**. This should be the default for most communication.

```json
{
  "type": "message",
  "recipient": "researcher",
  "content": "Your message here",
  "summary": "Brief status update on auth module"
}
```

#### 2. `"broadcast"` — Message All Teammates

Sends the same message to **every** teammate. **Use sparingly** — costs scale linearly with team size (N teammates = N deliveries).

```json
{
  "type": "broadcast",
  "content": "Stop all work, blocking bug found",
  "summary": "Critical blocking issue found"
}
```

Valid use cases: critical blockers, major announcements affecting everyone.

#### 3. `"shutdown_request"` — Ask a Teammate to Shut Down

```json
{
  "type": "shutdown_request",
  "recipient": "researcher",
  "content": "Task complete, wrapping up the session"
}
```

The recipient can approve (exits) or reject (keeps working).

#### 4. `"shutdown_response"` — Respond to a Shutdown Request

Approve:

```json
{
  "type": "shutdown_response",
  "request_id": "abc-123",
  "approve": true
}
```

Reject:

```json
{
  "type": "shutdown_response",
  "request_id": "abc-123",
  "approve": false,
  "content": "Still working on task #3"
}
```

#### 5. `"plan_approval_response"` — Approve/Reject a Teammate's Plan

Approve:

```json
{
  "type": "plan_approval_response",
  "request_id": "abc-123",
  "recipient": "researcher",
  "approve": true
}
```

Reject with feedback:

```json
{
  "type": "plan_approval_response",
  "request_id": "abc-123",
  "recipient": "researcher",
  "approve": false,
  "content": "Please add error handling for the API calls"
}
```

### Key Rules

- Teammates **must** use SendMessage to communicate — plain text is invisible to others
- Always use teammate **names**, never UUIDs
- Don't send structured JSON status messages — use TaskUpdate instead
- Prefer `"message"` over `"broadcast"` in almost all cases
- Idle notifications are sent automatically by the system when a teammate's turn ends
