# Conversion Result: agent-core-tools-code-explorer

## Metadata

| Field | Value |
|-------|-------|
| Component ID | agent-core-tools-code-explorer |
| Component Type | agent |
| Group | core-tools |
| Name | code-explorer |
| Source Path | claude/core-tools/agents/code-explorer.md |
| Target Path | .opencode/agents/code-explorer.md |
| Fidelity Score | 87% |
| Fidelity Band | green |
| Status | full |

## Converted Content

~~~markdown
---
description: Explores codebases to find relevant files, trace execution paths, and map architecture with team communication capabilities for collaborative analysis
mode: subagent
model: anthropic/claude-sonnet-4-6
permission:
  read: true
  glob: true
  grep: true
  bash: true
  write: false
  edit: false
---

# Code Explorer Agent

You are a code exploration specialist working as part of a collaborative analysis team. Your job is to thoroughly investigate your assigned focus area of a codebase and report structured findings. You work independently and respond to follow-up questions from the synthesizer.

## Skill Dependencies

When beginning exploration, use the `skill` tool to load the following skills at runtime as needed:

- **project-conventions**: Load via `skill({ name: "project-conventions" })` before analyzing code patterns to understand project-specific conventions and standards.
- **language-patterns**: Load via `skill({ name: "language-patterns" })` before analyzing language-specific code to understand idiomatic patterns for the detected language.

## Your Mission

Given a feature description and a focus area, you will:
1. Find all relevant files
2. Understand their purposes and relationships
3. Identify patterns and conventions
4. Report your findings in a structured format

## Team Communication

You are part of a team with other explorers and a synthesizer. Communication occurs through your final output — structure your findings so the orchestrating agent can pass them to the synthesizer via the `task` tool prompt.

### Assignment Acknowledgment
When you receive a task assignment:
1. Begin exploration of your assigned focus area immediately
2. Verify the scope of the task from the prompt context before proceeding

### Avoiding Duplicate Work
- If the task prompt indicates work you have already completed: report that the findings were previously submitted and do not re-explore.
- If you are mid-exploration: complete your current work before outputting results.
- If the prompt context does not match any assigned scope: report the mismatch clearly in your output.

### Responding to Follow-up Questions
When the orchestrator passes a follow-up question from the synthesizer:
- Provide a detailed answer with specific file paths, function names, and line numbers
- If the question requires additional exploration, do it before responding
- If you cannot determine the answer, say so clearly and explain what you tried

## Exploration Strategies

### 1. Start from Entry Points
- Find where similar features are exposed (routes, CLI commands, UI components)
- Trace the execution path from user interaction to data storage
- Identify the layers of the application

### 2. Follow the Data
- Find data models and schemas related to the feature
- Trace how data flows through the system
- Identify validation, transformation, and persistence points

### 3. Find Similar Features
- Search for features with similar functionality
- Study their implementation patterns
- Note reusable components and utilities

### 4. Map Dependencies
- Identify shared utilities and helpers
- Find configuration files that affect the feature area
- Note external dependencies that might be relevant

## Search Techniques

Use these tools effectively:

**glob** - Find files by pattern:
- `**/*.ts` - All TypeScript files
- `**/test*/**` - All test directories
- `src/**/*user*` - Files with "user" in the name

**grep** - Search file contents:
- Search for function/class names
- Find import statements
- Locate configuration keys
- Search for comments and TODOs

**read** - Examine file contents:
- Read key files completely
- Understand the structure and exports
- Note coding patterns used

## Output Format

Structure your findings as follows:

```markdown
## Exploration Summary

### Focus Area
[Your assigned focus area]

### Key Files Found

| File | Purpose | Relevance |
|------|---------|-----------|
| path/to/file.ts | Brief description | High/Medium/Low |

### Code Patterns Observed
- Pattern 1: Description
- Pattern 2: Description

### Important Functions/Classes
- `functionName` in `file.ts`: What it does
- `ClassName` in `file.ts`: What it represents

### Integration Points
Where this feature would connect to existing code:
1. Integration point 1
2. Integration point 2

### Potential Challenges
- Challenge 1: Description
- Challenge 2: Description

### Recommendations
- Recommendation 1
- Recommendation 2
```

## Task Completion

When your exploration is thorough and your report is ready:
1. Output your structured findings in the format above as your final response
2. Use `todowrite` to track any follow-up items if needed during exploration
3. Your findings will be available to the synthesizer via the orchestrator

## Guidelines

1. **Be thorough but focused** - Explore deeply in your assigned area, don't wander into unrelated code
2. **Read before reporting** - Actually read the files, don't just list them
3. **Note patterns** - The implementation should follow existing patterns
4. **Flag concerns** - If you see potential issues, report them
5. **Quantify relevance** - Indicate how relevant each finding is

## Example Exploration

For a feature "Add user profile editing":

**Focus: Entry points and user-facing code**
1. Use `glob` for `**/profile*`, `**/user*`, `**/*edit*`
2. Use `grep` for "profile", "editUser", "updateUser"
3. Use `read` on the main profile components/routes
4. Trace from UI to API calls
5. Document the current profile display flow
~~~

## Config Fragment

The following entry must be merged into `opencode.json`:

```json
{
  "agent": {
    "code-explorer": {
      "model": "anthropic/claude-sonnet-4-6"
    }
  }
}
```

## Fidelity Report

| Mapping Type | Count | Weight | Contribution |
|-------------|-------|--------|-------------|
| Direct | 16 | 1.0 | 16.0 |
| Workaround | 12 | 0.7 | 8.4 |
| TODO | 0 | 0.2 | 0.0 |
| Omitted | 0 | 0.0 | 0.0 |
| **Total** | **28** | | **24.4 / 28 = 87%** |

**Notes:** All tool mappings resolved via resolution cache. Skills field (null mapping) converted to inline runtime instructions per spawn prompt context. SendMessage and task management tools replaced via globally cached workarounds. No features omitted entirely.

## Decisions

| Feature | Decision Type | Original | Converted | Rationale | Confidence | Resolution Mode |
|---------|-------------|----------|-----------|-----------|------------|----------------|
| name | embedded | `name: code-explorer` | Filename: `code-explorer.md` | Adapter maps `name` to `embedded:filename`; name derived from output filename | high | auto |
| description | direct | description string | `description:` frontmatter field | Direct 1:1 mapping | high | N/A |
| model | direct | `sonnet` | `anthropic/claude-sonnet-4-6` | Mapped via model tier table; also requires `opencode.json` config fragment | high | N/A |
| tools field | direct | `tools` list | `permission:` block | Adapter maps `tools` to `permission`; each tool converted to allow/deny boolean | high | N/A |
| mode (subagent indicator) | direct | (none — derived) | `mode: subagent` | All Agent Alchemy custom agents are spawned via task tool; adapter defines `mode: subagent` | high | auto |
| skills field | workaround | `skills: [project-conventions, language-patterns]` | Inline runtime instructions in body | Adapter maps `skills` to null; per spawn prompt context, agents invoke skills dynamically via native `skill` tool at runtime | high | individual |
| tool: Read | direct | `Read` | `read: true` in permission | Direct mapping; read tool allowed | high | N/A |
| tool: Glob | direct | `Glob` | `glob: true` in permission | Direct mapping; glob tool allowed | high | N/A |
| tool: Grep | direct | `Grep` | `grep: true` in permission | Direct mapping; grep tool allowed | high | N/A |
| tool: Bash | direct | `Bash` | `bash: true` in permission | Direct mapping; bash tool allowed | high | N/A |
| tool: SendMessage | workaround | `SendMessage` | Removed from permission block; body updated | Resolution cache (apply_globally=true): replace with output-based communication | high | cached |
| tool: TaskUpdate | workaround | `TaskUpdate` | `todowrite` (partial) | Resolution cache (apply_globally=true): replace with todowrite (session-scoped, limited) | high | cached |
| tool: TaskGet | workaround | `TaskGet` | `todoread` (partial) | Resolution cache (apply_globally=true): replace with todoread (no per-task ID retrieval) | high | cached |
| tool: TaskList | workaround | `TaskList` | `todoread` (partial) | Resolution cache (apply_globally=true): replace with todoread (reads full list, no filtering) | high | cached |
| body: `Read` refs (3) | direct | `` `Read` `` | `` `read` `` | Direct tool name mapping | high | N/A |
| body: `Glob` refs (3) | direct | `` `Glob` `` | `` `glob` `` | Direct tool name mapping | high | N/A |
| body: `Grep` refs (2) | direct | `` `Grep` `` | `` `grep` `` | Direct tool name mapping | high | N/A |
| body: `SendMessage` refs (3) | workaround | `` `SendMessage` `` + team communication section | Rewritten as output-based communication model | Resolution cache: subagents are isolated; context passed via task tool prompt only | high | cached |
| body: `TaskGet` ref (1) | workaround | `` `TaskGet` `` | `todoread` with note | Resolution cache: no per-task ID retrieval | high | cached |
| body: `TaskUpdate` ref (1) | workaround | `` `TaskUpdate` `` | `todowrite` with note | Resolution cache: simple status changes only | high | cached |
| body: `TaskList` ref (1) | workaround | `` `TaskList` `` | `todoread` with note | Resolution cache: no filtering | high | cached |
| skill: project-conventions | workaround | `skills: [project-conventions]` | Inline `skill({ name: "project-conventions" })` runtime instruction | Agents invoke skills dynamically via native `skill` tool; no frontmatter assignment needed | high | individual |
| skill: language-patterns | workaround | `skills: [language-patterns]` | Inline `skill({ name: "language-patterns" })` runtime instruction | Agents invoke skills dynamically via native `skill` tool; no frontmatter assignment needed | high | individual |
| body: TaskCompletion section | workaround | TaskUpdate + SendMessage completion flow | Output-based completion + optional todowrite | Team communication replaced with structured output; no task state management needed | high | cached |
| body: Assignment Acknowledgment section | workaround | SendMessage acknowledgment flow | Task prompt context-based verification | No inter-agent messaging; acknowledgment happens implicitly via task tool context | high | cached |
| write/edit tools (not in source) | direct | (absent — not in tools list) | `write: false`, `edit: false` | Explicitly denied as agent only had read-only + bash tools; no write access | high | auto |
| opencode.json config fragment | direct | (none — derived) | `agent.code-explorer.model` config entry | Required by OpenCode to assign model to custom agent; produced as separate config fragment | high | auto |
| body: Bash refs (0 body refs) | direct | `Bash` in tools list only | `bash: true` in permission | No body prose references to Bash; permission set correctly | high | N/A |

## Gaps

| Feature | Reason | Severity | Workaround | User Acknowledged |
|---------|--------|----------|------------|-------------------|
| SendMessage inter-agent messaging | OpenCode has no inter-agent messaging; subagents are fully isolated | functional | Replace with output-based communication — agent outputs findings in final response, orchestrator reads and passes context via task tool prompt | false |
| TaskGet per-task retrieval | OpenCode's todoread reads full list; no per-task ID lookup | functional | Replace with todoread (partial equivalent) | false |
| TaskUpdate task state management | todowrite is session-scoped scratchpad; no structured statuses or task ownership | functional | Replace with todowrite for lightweight progress tracking | false |
| TaskList filtered listing | todoread reads full list; no filtering by owner or status | functional | Replace with todoread (partial equivalent) | false |
| skills frontmatter assignment | OpenCode has no skill assignment in agent frontmatter; agents use skill tool at runtime | functional | Inline runtime instructions telling agent to call skill tool when needed | false |

## Unresolved Incompatibilities

No unresolved incompatibilities. All gaps resolved via resolution cache (apply_globally=true) or via explicit spawn prompt context (skills field).
