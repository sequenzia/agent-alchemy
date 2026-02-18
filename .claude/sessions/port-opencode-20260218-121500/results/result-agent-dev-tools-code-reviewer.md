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
| Fidelity Score | 77% |
| Fidelity Band | yellow |
| Status | partial |

## Converted Content

~~~markdown
---
description: Reviews code implementations for correctness, security, maintainability with confidence-scored findings
model: anthropic/claude-opus-4-6
tools:
  read: true
  glob: true
  grep: true
  todowrite: true
  todoread: true
  write: false
  edit: false
  bash: false
---

<!-- RESOLVED: SendMessage — No inter-agent messaging in opencode. Context passed via task prompt. TODO comment preserved. -->

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

## Task Completion

When your review task is complete, record your findings summary using `todowrite`. Use `todoread` to check your current task context and status before beginning.

<!-- TODO: SendMessage has no equivalent on opencode. OpenCode has no inter-agent messaging. The Team Communication section below has been adapted: context is passed only through the task prompt when this agent is spawned. Remove any expectations of receiving follow-up questions from other agents at runtime. -->

## Receiving Review Instructions

Your review focus and file list are passed to you through the task prompt when you are spawned. Read your task prompt carefully to identify:
- The specific review focus assigned to you
- The list of files to review
- Any additional context about the changes being reviewed

If you need to investigate additional files not listed in your task prompt, use `read`, `glob`, and `grep` to explore them.

## False Positive Avoidance

Before reporting, verify:
- The code actually does what you think it does
- The issue isn't handled elsewhere
- The pattern isn't intentional for this codebase
- The framework/library doesn't handle this case
~~~

## Fidelity Report

| Mapping Type | Count | Weight | Contribution |
|-------------|-------|--------|-------------|
| Direct | 7 | 1.0 | 7.0 |
| Workaround | 4 | 0.7 | 2.8 |
| TODO | 1 | 0.2 | 0.2 |
| Omitted | 1 | 0.0 | 0.0 |
| **Total** | **13** | | **10.0** |

**Score:** 10.0 / 13 * 100 = **77%** (Yellow — Moderate fidelity)

**Notes:** SendMessage is the primary fidelity loss. The agent's core review behavior (read-only code analysis, structured reporting, confidence scoring) is fully preserved. Behavioral loss is limited to inter-agent communication and structured task status updates.

**Sub-scores (informational):**

| Area | Direct | Workaround | TODO | Omitted | Area Score |
|------|--------|------------|------|---------|------------|
| Frontmatter fields | 4 | 0 | 0 | 0 | 100% |
| Tools preserved | 3 | 3 | 0 | 1 | ~77% |
| Body transformations | 0 | 1 | 1 | 0 | ~46% |
| Skills assignable | — | — | — | — | N/A (no skills field) |
| Gaps resolved | — | — | — | — | 1 unresolved |

## Decisions

| Feature | Decision Type | Original | Converted | Rationale | Confidence | Resolution Mode |
|---------|-------------|----------|-----------|-----------|------------|----------------|
| name | embedded | code-reviewer | code-reviewer.md (filename) | Agent name -> embedded in filename per opencode naming convention | high | auto |
| description | direct | Reviews code implementations for correctness, security, maintainability with confidence-scored findings | Same value in description field | description maps directly to opencode agent description field | high | auto |
| model | direct | opus | anthropic/claude-opus-4-6 | Model tier mapped via Model Tier Mappings table; opus -> claude-opus-4-6 | high | auto |
| tools field | direct | tools list | permission block | tools maps to permission in opencode agent frontmatter; per-tool allow/deny config | high | auto |
| tool: Read | direct | Read | read: true | Direct 1:1 mapping; opencode read tool | high | auto |
| tool: Glob | direct | Glob | glob: true | Direct 1:1 mapping; opencode glob tool | high | auto |
| tool: Grep | direct | Grep | grep: true | Direct 1:1 mapping; opencode grep tool | high | auto |
| tool: SendMessage | omitted | SendMessage | removed from permission block | No inter-agent messaging equivalent on opencode. Removed from tool permission list. Body references replaced with TODO and adapted prose. | high | individual |
| tool: TaskUpdate | workaround | TaskUpdate | todowrite: true | Partial mapping: todowrite provides session-scoped scratchpad. No structured status field or dependency support. Body instruction updated to use todowrite. | high | auto |
| tool: TaskGet | workaround | TaskGet | todoread: true | Partial mapping: todoread returns full list, no per-task retrieval by ID. Only in tools list, no body reference — cosmetic auto-resolved. | high | auto |
| tool: TaskList | workaround | TaskList | todoread: true | Partial mapping: same todoread tool. Only in tools list, no body reference — cosmetic auto-resolved. | high | auto |
| body: SendMessage refs | todo | Two SendMessage references in Team Communication section | Replaced with TODO comment + adapted prose section | SendMessage null-mapped. Body section rewritten to describe context-passing via task prompt instead of inter-agent messaging. | high | individual |
| body: TaskUpdate ref | workaround | "mark it as completed using `TaskUpdate`" | "record your findings summary using `todowrite`" | TaskUpdate -> todowrite partial mapping applied in body; prose updated to reflect todowrite semantics. | high | auto |
| agent type | direct | (read-only tool profile) | task-capable agent (permission block restricts write/edit/bash) | Agent uses Read, Glob, Grep only (read-only profile). write, edit, bash set to false in permission block. Reviewer role preserved via system prompt. | high | auto |

## Gaps

| Feature | Reason | Severity | Workaround | User Acknowledged |
|---------|--------|----------|------------|-------------------|
| SendMessage (inter-agent messaging) | No inter-agent messaging equivalent on opencode. Context passed only through task prompt at spawn time. | functional | Remove Team Communication section; replace with task-prompt-driven context instructions. Body section rewritten to describe receiving context via prompt. | false |
| TaskUpdate (structured task status) | todowrite provides a session-scoped scratchpad only. No status transitions, ownership, or dependency modeling. | functional | Use todowrite to record review summary; adapt body instruction to match todowrite semantics. Applied as workaround. | false |
| TaskGet / TaskList (per-task retrieval) | todoread returns full list only; no per-task retrieval by ID. | cosmetic | Use todoread; no body references to update. Auto-resolved. | false |

## Unresolved Incompatibilities

| Group Key | Feature | Severity | Category | Reason | Suggested Workaround | Confidence | Affected Locations |
|-----------|---------|----------|----------|--------|---------------------|------------|-------------------|
| (all resolved — auto-applied workarounds globally) | | | | | | | |
