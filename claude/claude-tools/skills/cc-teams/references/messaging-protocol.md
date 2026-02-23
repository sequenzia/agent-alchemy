# SendMessage Protocol Reference

Complete documentation of all 5 SendMessage protocol types for inter-agent communication within Claude Code Agent Teams. Each type has specific fields, routing behavior, and use cases.

**Automatic message delivery**: Messages sent via `SendMessage` are written as JSON files to the recipient's inbox directory. Claude Code monitors these directories and delivers messages automatically to the recipient agent. Teammates do not need to poll or check their inboxes — delivery is push-based, not polling-based.

**Peer DM visibility**: When teammates send direct messages to each other (peer-to-peer), the team lead receives brief summaries of those messages in idle notifications. This gives the team lead oversight of teammate coordination without requiring all communication to route through the lead. Summaries are concise (5-10 words) and appear in the lead's idle notification feed.

---

## 1. message (Direct Message)

Send a targeted message to a specific teammate by name. This is the default and most common message type.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Must be `"message"` |
| `recipient` | string | Yes | Name of the teammate to send to (e.g., `"researcher-1"`). Use the teammate's human-readable name, not a UUID. |
| `content` | string | Yes | The message text. Keep focused on a single topic or instruction. |
| `summary` | string | Yes | A 5-10 word preview of the message. Displayed in UI notifications and team lead's idle feed. |

### Usage Guidance

- **Always prefer `message` over `broadcast`** for all teammate communication
- Use the teammate's name as it was set during spawning (the `name` parameter in the Task tool call)
- Include enough context in `content` for the recipient to act without needing additional back-and-forth
- The `summary` field is required and appears in the Claude Code UI task list — make it descriptive

### Example

```
SendMessage(
  type="message",
  recipient="researcher-1",
  content="Please analyze the authentication module in src/auth/ and report back with a summary of the public API surface, including function signatures and any external dependencies.",
  summary="Analyze auth module public API"
)
```

---

## 2. broadcast (Team-Wide Message)

Send a message to every team member simultaneously.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Must be `"broadcast"` |
| `content` | string | Yes | The message text sent to all team members. |
| `summary` | string | Yes | A 5-10 word preview. Each recipient sees this in their notification. |

### Cost Warning

A broadcast sends **N separate messages for N team members**. For a team of 5 members, a single broadcast creates 5 message deliveries. This is expensive in terms of context consumption across all teammates. Use sparingly.

### Valid Use Cases

- **Critical blocking issues**: A shared dependency is broken and all teammates need to pause or adjust
- **Major team-wide announcements**: A fundamental requirement change that affects everyone's work
- **Coordination checkpoints**: All teammates need to reach a sync point before proceeding

### Invalid Use Cases

- **Responding to one person**: Use `message` type instead — broadcast wastes context for uninvolved teammates
- **Normal conversation**: Direct messages are always preferred for one-on-one exchanges
- **Task follow-ups**: Send targeted messages to the specific teammate working on that task
- **Status requests**: Ask individual teammates for their status, not the whole team

### Example

```
SendMessage(
  type="broadcast",
  content="BLOCKING ISSUE: The database schema has changed. All tasks involving the users table must pause until the migration is complete. I will send a follow-up message when it is safe to resume.",
  summary="Database schema change — pause users table work"
)
```

---

## 3. shutdown_request (Request Teammate Shutdown)

Request a specific teammate to shut down gracefully. Sent by the team lead when a teammate's work is complete.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Must be `"shutdown_request"` |
| `recipient` | string | Yes | Name of the teammate to shut down. |
| `content` | string | No | Optional reason for the shutdown request (e.g., `"All analysis tasks complete"`). |

### Behavior

1. The team lead sends `shutdown_request` to a teammate
2. The teammate receives the shutdown request, which includes a `request_id` in the delivered message JSON
3. The teammate must respond with a `shutdown_response` (see next section), referencing the `request_id`
4. If approved, the teammate terminates; if rejected, the teammate continues working

### Usage Guidance

- Only team leads should send shutdown requests
- Send shutdown requests only when the teammate's role is fully complete — not when they are merely idle
- Wait for the `shutdown_response` before considering the teammate stopped

### Example

```
SendMessage(
  type="shutdown_request",
  recipient="researcher-1",
  content="All research tasks are complete. Thank you for your analysis."
)
```

---

## 4. shutdown_response (Respond to Shutdown Request)

Sent by a teammate in response to a `shutdown_request`. The teammate either approves (and terminates) or rejects (and continues working).

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Must be `"shutdown_response"` |
| `request_id` | string | Yes | The `request_id` from the received shutdown request. Must be extracted from the JSON message delivered to the teammate's inbox. |
| `approve` | boolean | Yes | `true` to accept shutdown and terminate, `false` to reject and continue working. |
| `content` | string | No | If `approve` is `false`, provide the reason for rejection (e.g., `"Still processing final analysis"`). |

### Approve Flow

1. Teammate sets `approve: true`
2. The shutdown confirmation is sent to the team lead
3. The teammate's process terminates

### Reject Flow

1. Teammate sets `approve: false` with a reason in `content`
2. The rejection reason is delivered to the team lead
3. The teammate continues working normally
4. The team lead can send another `shutdown_request` later

### Critical: request_id Handling

The `request_id` **must** be extracted from the JSON payload of the received shutdown request message. A text acknowledgment alone (e.g., replying "OK" via a regular `message`) is **NOT sufficient** — the shutdown protocol requires the structured `shutdown_response` type with the matching `request_id` to properly complete the handshake.

### Example: Approving Shutdown

```
SendMessage(
  type="shutdown_response",
  request_id="sr-abc123-def456",
  approve=true,
  content="All work complete. Shutting down."
)
```

### Example: Rejecting Shutdown

```
SendMessage(
  type="shutdown_response",
  request_id="sr-abc123-def456",
  approve=false,
  content="Still processing the final module analysis. Need approximately 2 more minutes."
)
```

---

## 5. plan_approval_response (Approve/Reject Plan)

Sent by a team lead (or designated approver) in response to a teammate's plan that requires approval. This is triggered when a teammate with `plan_mode_required` calls `ExitPlanMode` — the plan is routed to the approver for review.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Must be `"plan_approval_response"` |
| `request_id` | string | Yes | The `request_id` from the plan approval request. Extracted from the message delivered when the teammate called `ExitPlanMode`. |
| `recipient` | string | Yes | Name of the teammate whose plan is being reviewed. |
| `approve` | boolean | Yes | `true` to approve the plan (teammate exits plan mode and can implement), `false` to reject (teammate receives feedback and revises). |
| `content` | string | No | If `approve` is `false`, provide feedback explaining what needs to change. If `approve` is `true`, optional confirmation message. |

### Approve Flow

1. Approver sets `approve: true`
2. The teammate receives confirmation and exits plan mode
3. The teammate can now implement the approved plan

### Reject Flow

1. Approver sets `approve: false` with feedback in `content`
2. The teammate receives the rejection with feedback
3. The teammate revises the plan based on feedback
4. The teammate calls `ExitPlanMode` again to re-submit for approval

### Example: Approving a Plan

```
SendMessage(
  type="plan_approval_response",
  request_id="pa-xyz789-ghi012",
  recipient="implementer-1",
  approve=true,
  content="Plan looks good. Proceed with implementation."
)
```

### Example: Rejecting a Plan

```
SendMessage(
  type="plan_approval_response",
  request_id="pa-xyz789-ghi012",
  recipient="implementer-1",
  approve=false,
  content="The plan does not account for error handling in the payment module. Please add retry logic for failed transactions and document the rollback strategy."
)
```

---

## Message Best Practices

### Naming

- **Always refer to teammates by name** (e.g., `"researcher-1"`), not by UUID or other identifiers
- Use the exact name that was set during spawning via the `name` parameter in the Task tool call

### Summary Field

- **Always include a summary** — it is required for all message types that have the field
- Keep summaries to 5-10 words that capture the essence of the message
- Summaries appear in the Claude Code UI task list and in the team lead's idle notification feed

### Content Guidelines

- Keep each message focused on a single topic or instruction
- Include enough context for the recipient to act independently
- For task assignments, specify: what to do, where to look, and what to report back
- For results, include: what was found, key details, and any follow-up recommendations

### Type Selection

| Scenario | Correct Type |
|----------|-------------|
| Assign work to a specific teammate | `message` |
| Ask a teammate for a status update | `message` |
| Share results with the team lead | `message` |
| Report a critical issue affecting everyone | `broadcast` |
| Respond to a message from a teammate | `message` |
| End a teammate's session after work is done | `shutdown_request` |
| Acknowledge a shutdown request | `shutdown_response` |
| Review a teammate's submitted plan | `plan_approval_response` |
