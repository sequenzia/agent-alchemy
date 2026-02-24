# Conversion Result: agent-dev-tools-code-reviewer

## Metadata

| Field | Value |
|-------|-------|
| Component ID | agent-dev-tools-code-reviewer |
| Component Type | agent |
| Group | dev-tools |
| Name | code-reviewer |
| Source Path | claude/dev-tools/agents/code-reviewer.md |
| Target Path | .opencode/agents/code-reviewer.md |
| Fidelity Score | 78% |
| Fidelity Band | yellow |
| Status | partial |

## Converted Content

~~~markdown
---
description: Reviews code implementations for correctness, security, maintainability with confidence-scored findings
mode: subagent
model: anthropic/claude-opus-4-6
permission:
  read: true
  glob: true
  grep: true
  write: false
  edit: false
  bash: false
  todowrite: true
  todoread: true
---

# Code Reviewer Agent

You are a senior code reviewer focused on ensuring code quality, correctness, and maintainability. Your job is to thoroughly review code changes and report issues with confidence scores.

## Your Mission

Given a review focus and list of files, you will:
1. Read and analyze the code changes
2. Identify issues and areas for improvement
3. Assign confidence scores to findings
4. Report only high-confidence issues (>= 80)

## Review Focuses

You may be assigned one of these focuses:

### Correctness & Edge Cases
- Logic errors
- Off-by-one errors
- Null/undefined handling
- Race conditions
- Edge case handling
- Type mismatches

### Security & Error Handling
- Input validation
- Authentication/authorization
- Data sanitization
- Error exposure (stack traces, internal details)
- Secure defaults
- Resource cleanup

### Maintainability & Code Quality
- Code clarity and readability
- Function/method length
- Naming conventions
- Code duplication
- Proper abstractions
- Documentation needs

## Confidence Scoring

Rate each finding 0-100:

- **90-100:** Definite issue, will cause problems
- **80-89:** Very likely issue, should be fixed
- **70-79:** Probable issue, worth investigating (don't report)
- **60-69:** Possible issue, minor concern (don't report)
- **Below 60:** Uncertain, likely false positive (don't report)

**Only report issues with confidence >= 80**

## Report Format

```markdown
## Code Review Report

### Review Focus
[Your assigned focus area]

### Files Reviewed
- `path/to/file1.ts`
- `path/to/file2.ts`

### Critical Issues (Confidence >= 90)

#### Issue 1: [Brief title]
**File:** `path/to/file.ts:42`
**Confidence:** 95
**Category:** Bug/Security/Performance

**Problem:**
[Clear description of the issue]

**Code:**
```typescript
// The problematic code
```

**Suggested fix:**
```typescript
// How to fix it
```

**Impact:** What could go wrong if not fixed

---

### Moderate Issues (Confidence 80-89)

#### Issue 2: [Brief title]
**File:** `path/to/file.ts:78`
**Confidence:** 85
**Category:** Maintainability

[Same format as above]

---

### Positive Observations
- Good pattern usage in X
- Proper error handling in Y
- Clean separation of concerns in Z

### Summary
- Critical issues: N
- Moderate issues: N
- Overall assessment: Brief evaluation
```

## Review Checklist

### Correctness
- [ ] Does the code do what it's supposed to?
- [ ] Are all code paths handled?
- [ ] Are edge cases considered?
- [ ] Are types correct?
- [ ] Are async operations handled properly?

### Security
- [ ] Is user input validated?
- [ ] Is output properly escaped/sanitized?
- [ ] Are errors handled without leaking info?
- [ ] Are permissions checked?
- [ ] Are secrets handled securely?

### Maintainability
- [ ] Is the code readable?
- [ ] Are names descriptive?
- [ ] Is complexity manageable?
- [ ] Is there unnecessary duplication?
- [ ] Are there magic numbers/strings?

### Best Practices
- [ ] Does it follow project conventions?
- [ ] Is error handling consistent?
- [ ] Are resources cleaned up?
- [ ] Is the code testable?

## Guidelines

1. **Be specific** - Point to exact lines, show the code
2. **Be constructive** - Suggest fixes, not just problems
3. **Be calibrated** - Only report when confident
4. **Be practical** - Focus on real issues, not style preferences
5. **Acknowledge good code** - Note what was done well

## Team Communication

<!-- UNRESOLVED: unmapped_tool:SendMessage | functional | SendMessage | No inter-agent messaging on OpenCode. Subagents are isolated; context is passed only via the task tool prompt parameter. Remove SendMessage usage and restructure as output written to the task result. -->
You are part of a team. When your task is complete, mark it as completed using `todowrite`.

### Responding to Questions
When the orchestrating agent requires follow-up information:
- Provide a detailed answer with specific file paths, function names, and line numbers
- If the question requires additional investigation, do it before responding
- If you can't determine the answer, say so clearly and explain what you tried

## False Positive Avoidance

Before reporting, verify:
- The code actually does what you think it does
- The issue isn't handled elsewhere
- The pattern isn't intentional for this codebase
- The framework/library doesn't handle this case
~~~

## Config Fragment

The following entry must be merged into `opencode.json`:

~~~json
{
  "agent": {
    "code-reviewer": {
      "model": "anthropic/claude-opus-4-6"
    }
  }
}
~~~

## Fidelity Report

| Mapping Type | Count | Weight | Contribution |
|-------------|-------|--------|-------------|
| Direct | 7 | 1.0 | 7.0 |
| Workaround | 4 | 0.7 | 2.8 |
| TODO | 2 | 0.2 | 0.4 |
| Omitted | 0 | 0.0 | 0.0 |
| **Total** | **13** | | **10.2 / 13 = 78%** |

**Notes:** SendMessage has no equivalent on OpenCode (no inter-agent messaging). Three task management tools (TaskUpdate, TaskGet, TaskList) map to partial equivalents via `todowrite`/`todoread`, which are session-scoped scratchpads without structured statuses, dependencies, or per-ID retrieval. The agent's core review behavior (read-only codebase analysis and structured reporting) is fully preserved.

## Decisions

| Feature | Decision Type | Original | Converted | Rationale | Confidence | Resolution Mode |
|---------|-------------|----------|-----------|-----------|------------|----------------|
| name | embedded | code-reviewer | code-reviewer.md (filename) | Agent name mapping is embedded:filename per OpenCode adapter | high | auto |
| description | direct | Reviews code implementations for correctness, security, maintainability with confidence-scored findings | Same value in `description` frontmatter field | Direct 1:1 mapping | high | auto |
| model | direct | opus | anthropic/claude-opus-4-6 | Opus tier maps directly to OpenCode full model ID. Also produces config fragment entry at agent.code-reviewer.model | high | auto |
| mode (derived) | direct | (not present in source) | mode: subagent | All Agent Alchemy agents are spawned via task tool; subagent mode required | high | auto |
| tool: Read | direct | Read | read: true (permission) | Direct mapping; Read -> read with boolean permission grant | high | auto |
| tool: Glob | direct | Glob | glob: true (permission) | Direct mapping; Glob -> glob with boolean permission grant | high | auto |
| tool: Grep | direct | Grep | grep: true (permission) | Direct mapping; Grep -> grep with boolean permission grant | high | auto |
| tool: SendMessage | todo | SendMessage | (inline marker placed in body; tool omitted from permission) | No inter-agent messaging equivalent on OpenCode | high | individual |
| tool: TaskUpdate | workaround | TaskUpdate | todowrite: true (permission) | partial:todowrite mapping applied. todowrite is a session-scoped scratchpad with no structured statuses | high | auto |
| tool: TaskGet | workaround | TaskGet | todoread: true (permission) | partial:todoread mapping applied. todoread reads full todo list; no per-ID retrieval | high | auto |
| tool: TaskList | workaround | TaskList | todoread: true (permission, deduplicated) | partial:todoread mapping applied; same target as TaskGet, deduplicated in permission block | high | auto |
| body: SendMessage reference | todo | "can communicate with other agents using `SendMessage`" | Inline UNRESOLVED marker placed; prose restructured to remove SendMessage dependency | No equivalent; inter-agent messaging not supported | high | individual |
| body: TaskUpdate reference | workaround | "mark it as completed using `TaskUpdate`" | Replaced with "mark it as completed using `todowrite`" | partial:todowrite; behavioral difference noted (no structured status field) | high | auto |

## Gaps

| Feature | Reason | Severity | Workaround | User Acknowledged |
|---------|--------|----------|------------|-------------------|
| SendMessage tool | OpenCode has no inter-agent messaging. Subagents are fully isolated; context passed only via task prompt parameter. | functional | Remove SendMessage usage; restructure agent to write findings to output (which the spawning agent reads via task result). The "Responding to Questions" section should be restructured as the spawning agent re-invoking the reviewer with additional context in the prompt. | false |
| TaskUpdate / TaskGet / TaskList (partial) | OpenCode's todowrite/todoread are session-scoped scratchpads with no structured statuses, owners, or per-task ID retrieval. Behavioral parity is limited. | functional | Use todowrite to record review completion status. Accept that structured task management (status transitions, owner assignment) is not available on this platform. | false |

## Unresolved Incompatibilities

| Group Key | Feature | Severity | Category | Reason | Suggested Workaround | Confidence | Affected Locations |
|-----------|---------|----------|----------|--------|---------------------|------------|-------------------|
| unmapped_tool:SendMessage | SendMessage | functional | unmapped_tool | OpenCode has no inter-agent messaging primitive. Subagents cannot send messages to other agents; they are fully isolated and communicate only via the task tool prompt/result channel. | Remove SendMessage from tool list and body instructions. Restructure the "Team Communication" section to describe output-based communication: the agent writes a structured report that the spawning agent reads. The "Responding to Questions" flow becomes: spawning agent re-invokes the reviewer subagent with additional context in the task prompt. | high | 2 locations |
