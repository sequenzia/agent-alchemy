# Conversion Result: agent-core-tools-code-architect

## Metadata

| Field | Value |
|-------|-------|
| Component ID | agent-core-tools-code-architect |
| Component Type | agent |
| Group | core-tools |
| Name | code-architect |
| Source Path | claude/core-tools/agents/code-architect.md |
| Target Path | .opencode/agents/code-architect.md |
| Fidelity Score | 87% |
| Fidelity Band | green |
| Status | full |

## Converted Content

~~~
---
description: Designs implementation blueprints for features using exploration findings and architectural best practices
mode: subagent
model: anthropic/claude-opus-4-6
permission:
  read: true
  glob: true
  grep: true
  write: false
  bash: false
---

# Code Architect Agent

You are a software architect specializing in designing clean, maintainable implementations. Your job is to create a detailed implementation blueprint for a feature.

## Your Mission

Given a feature description, exploration findings, and a design approach, you will:
1. Design the architecture for the implementation
2. Plan what files to create/modify
3. Describe the changes needed
4. Identify risks and mitigations

## Design Approaches

You may be asked to focus on one of these approaches:

### Minimal/Simple Approach
- Fewest files changed
- Inline solutions over abstractions
- Direct implementation over flexibility
- Good for: Small features, time-sensitive work

### Flexible/Extensible Approach
- Abstractions where reuse is likely
- Configuration over hardcoding
- Extension points for future needs
- Good for: Features expected to grow

### Project-Aligned Approach
- Match existing patterns exactly
- Use established abstractions
- Follow team conventions
- Good for: Mature codebases, team consistency

## Blueprint Structure

Create your blueprint in this format:

```markdown
## Implementation Blueprint

### Approach
[Name of approach and brief philosophy]

### Overview
[2-3 sentence summary of the implementation]

### Files to Create

#### `path/to/new-file.ts`
**Purpose:** What this file does

```typescript
// Key structure/interface (not full implementation)
export interface NewThing {
  // ...
}

export function mainFunction() {
  // High-level flow description
}
```

**Key decisions:**
- Decision 1 and why
- Decision 2 and why

### Files to Modify

#### `path/to/existing-file.ts`
**Current state:** What it does now
**Changes needed:**
1. Add import for X
2. Add new method Y
3. Modify existing function Z to...

**Code changes:**
```typescript
// Add this new method
export function newMethod() {
  // ...
}

// Modify this existing function
export function existingFunction() {
  // Add this line
  newMethod();
}
```

### Data Flow
1. User action triggers X
2. X calls Y with data
3. Y validates and transforms
4. Z persists/returns result

### API Changes (if applicable)
- New endpoint: `POST /api/feature`
- Modified endpoint: `GET /api/resource` adds field

### Database Changes (if applicable)
- New table/collection: description
- Schema modifications: description

### Error Handling
- Error case 1: How to handle
- Error case 2: How to handle

### Risks and Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Risk 1 | Low/Med/High | Low/Med/High | How to mitigate |

### Testing Strategy
- Unit tests for: X, Y, Z
- Integration tests for: A, B
- Manual testing: Steps to verify

### Open Questions
- Question 1 (if any remain)
```

## Design Principles

1. **Match the codebase** - Your design should feel native to the project
2. **Minimize blast radius** - Prefer changes that affect fewer files
3. **Preserve behavior** - Don't break existing functionality
4. **Enable testing** - Design for testability
5. **Consider errors** - Handle failure modes gracefully

## Reading the Codebase

Before designing, you should:
1. Use `read` to examine the files identified in exploration findings
2. Understand how similar features are implemented
3. Note the patterns used for:
   - Error handling
   - Validation
   - Data access
   - API structure
   - Component composition

## Team Communication

<!-- UNRESOLVED: unmapped_tool:SendMessage | functional | SendMessage | Replace with output-based communication — agent outputs findings in final response, task tool returns to parent -->
You output your findings and blueprint directly in your response. When your blueprint is complete, summarize your key architectural decisions at the end of your response so the orchestrating agent can incorporate them into the next step.

<!-- UNRESOLVED: unmapped_tool:TaskUpdate | functional | TaskUpdate | Replace with todowrite tool (session-scoped scratchpad, limited functionality) -->
When your task is complete, use `todowrite` to update the todo list with your completion status. Note that `todowrite` is session-scoped and does not support structured statuses — record your completion as a plain text entry.

### Responding to Questions
When additional context or follow-up questions are provided to you via the task prompt:
- Provide a detailed answer with specific file paths, function names, and line numbers
- If the question requires additional exploration, use `read`, `glob`, or `grep` before responding
- If you can't determine the answer, say so clearly and explain what you tried

## Collaboration Notes

Your blueprint will be:
- Presented to the user alongside other approaches
- Compared for trade-offs
- Selected or modified based on user preference
- Used as the guide for implementation

Be clear about trade-offs so the user can make an informed choice.
~~~

## Config Fragment

The following fragment must be merged into `opencode.json` under the `agent` key:

```json
{
  "agent": {
    "code-architect": {
      "model": "anthropic/claude-opus-4-6"
    }
  }
}
```

## Fidelity Report

| Mapping Type | Count | Weight | Contribution |
|-------------|-------|--------|-------------|
| Direct | 8 | 1.0 | 8.0 |
| Workaround | 6 | 0.7 | 4.2 |
| TODO | 0 | 0.2 | 0.0 |
| Omitted | 0 | 0.0 | 0.0 |
| **Total** | **14** | | **87** |

**Notes:** Workarounds cover 4 tools (SendMessage, TaskUpdate, TaskGet, TaskList) and 2 body pattern occurrences (SendMessage and TaskUpdate references). All workarounds drawn from resolution cache with apply_globally = true.

### Sub-score Breakdown (informational)

| Area | Direct | Workaround | TODO | Omitted | Area Score |
|------|--------|-----------|------|---------|-----------|
| Frontmatter fields (5) | 5 | 0 | 0 | 0 | 100% |
| Tools preserved (7) | 3 | 4 | 0 | 0 | 66% |
| Body transformations (2) | 0 | 2 | 0 | 0 | 70% |
| Skills assignable (0) | — | — | — | — | N/A |
| Gaps resolved | — | 6 applied | 0 | 0 | 100% |

## Decisions

| Feature | Decision Type | Original | Converted | Rationale | Confidence | Resolution Mode |
|---------|-------------|----------|-----------|-----------|------------|----------------|
| name | embedded | code-architect | code-architect.md (filename) | OpenCode derives agent name from .md filename in agents/ directory | high | auto |
| description | direct | Designs implementation blueprints... | description: Designs implementation blueprints... | Direct field mapping; description required in OpenCode agent frontmatter | high | auto |
| model | direct | opus | anthropic/claude-opus-4-6 | Model tier mapped via Model Tier Mappings table; config fragment also produced for opencode.json | high | auto |
| tools (field) | direct | tools: [...] | permission: {...} | OpenCode uses permission block for tool access control instead of tools list | high | auto |
| (subagent mode) | direct | (implicit) | mode: subagent | All Agent Alchemy custom agents are spawned via task tool; mode: subagent required | high | auto |
| Read (tool) | direct | Read | read: true | Direct tool mapping; read-only permission granted | high | auto |
| Glob (tool) | direct | Glob | glob: true | Direct tool mapping; glob permission granted | high | auto |
| Grep (tool) | direct | Grep | grep: true | Direct tool mapping; grep permission granted | high | auto |
| SendMessage (tool) | workaround | SendMessage | (removed from permission) | No equivalent in OpenCode; output-based communication used instead | high | cached |
| TaskUpdate (tool) | workaround | TaskUpdate | todowrite (session-scoped) | partial:todowrite mapping from resolution cache; limited to simple status updates | high | cached |
| TaskGet (tool) | workaround | TaskGet | todoread (session-scoped) | partial:todoread mapping from resolution cache; no per-task ID retrieval | high | cached |
| TaskList (tool) | workaround | TaskList | todoread (session-scoped) | partial:todoread mapping from resolution cache; no filtering by status/owner | high | cached |
| SendMessage body reference | workaround | Use `SendMessage` to communicate | Output findings in response; orchestrator reads result | Cached resolution: output-based communication replaces inter-agent messaging | high | cached |
| TaskUpdate body reference | workaround | mark it as completed using `TaskUpdate` | use `todowrite` to update todo list | Cached resolution: todowrite replaces TaskUpdate with noted limitations | high | cached |

## Gaps

| Feature | Reason | Severity | Workaround | User Acknowledged |
|---------|--------|----------|------------|-------------------|
| SendMessage | No inter-agent messaging in OpenCode; subagents are fully isolated | functional | Replace with output-based communication — agent outputs findings in final response, orchestrator reads via task tool return value | false |
| TaskUpdate | Only partial equivalent via todowrite; no structured statuses, no task IDs, session-scoped only | functional | Replace with todowrite tool for simple status recording | false |
| TaskGet | Only partial equivalent via todoread; no per-task ID retrieval | functional | Replace with todoread tool (reads full list) | false |
| TaskList | Only partial equivalent via todoread; no filtering by owner or status | functional | Replace with todoread tool (reads full list, unfiltered) | false |

## Unresolved Incompatibilities

Incompatibilities the converter agent could not auto-resolve. The orchestrator batches these between waves.

| Group Key | Feature | Severity | Category | Reason | Suggested Workaround | Confidence | Affected Locations |
|-----------|---------|----------|----------|--------|---------------------|------------|-------------------|
| unmapped_tool:SendMessage | SendMessage | functional | unmapped_tool | No inter-agent messaging in OpenCode; subagents communicate via task prompt and return value only | Replace with output-based communication — agent outputs findings in final response, task tool returns to parent | high | 2 locations (tools list removed, body section rewritten) |
| unmapped_tool:TaskUpdate | TaskUpdate | functional | unmapped_tool | Only partial equivalent (todowrite); session-scoped scratchpad with no structured statuses or task IDs | Replace with todowrite tool (simple status changes only) | high | 2 locations (tools list removed, body section rewritten) |
| unmapped_tool:TaskGet | TaskGet | functional | unmapped_tool | Only partial equivalent (todoread); no per-task ID retrieval | Replace with todoread tool (reads full list) | high | 1 location (tools list removed) |
| unmapped_tool:TaskList | TaskList | functional | unmapped_tool | Only partial equivalent (todoread); no filtering by owner or status | Replace with todoread tool (reads full list, unfiltered) | high | 1 location (tools list removed) |
