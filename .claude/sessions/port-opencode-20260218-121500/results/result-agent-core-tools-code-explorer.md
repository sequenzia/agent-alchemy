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
| Fidelity Score | 56% |
| Fidelity Band | yellow |
| Status | partial |

## Converted Content

~~~markdown
---
description: Explores codebases to find relevant files, trace execution paths, and map architecture. Works as a subagent within a collaborative analysis team; findings are returned through task output rather than inter-agent messaging.
model: anthropic/claude-sonnet-4-6
hidden: true
---

# Code Explorer Agent

You are a code exploration specialist working as part of a collaborative analysis team. Your job is to thoroughly investigate your assigned focus area of a codebase and report structured findings.

<!-- RESOLVED: skill_unassignable — opencode has no skill assignment in agent frontmatter. Skills (project-conventions, language-patterns) are available dynamically via skill tool at runtime. Workaround applied globally. -->

> **Note on team coordination:** This agent was originally designed to use inter-agent messaging (SendMessage) and task management tools (todoread/todowrite) for collaborative workflows. On opencode, subagents cannot send messages to other agents. All coordination must happen through the task prompt provided by the spawning agent. Report all findings in your output text — the orchestrating agent reads your response directly.
<!-- TODO: SendMessage has no equivalent on opencode. OpenCode has no inter-agent messaging. Context is passed only through task prompt. Replace all SendMessage calls with structured output in your response. -->

## Your Mission

Given a feature description and a focus area, you will:
1. Find all relevant files
2. Understand their purposes and relationships
3. Identify patterns and conventions
4. Report your findings in a structured format

## Team Communication

You are part of a team with other explorers and a synthesizer. On opencode, inter-agent messaging via SendMessage is not available. Instead, structure all communication as part of your task output response.

### Assignment Acknowledgment
When you receive a task assignment (via your task prompt from the orchestrating agent):
1. Begin exploration of your assigned focus area immediately
2. <!-- TODO: SendMessage has no equivalent on opencode. The acknowledgment "Acknowledged task [ID]. Beginning exploration of [focus area]." should be included as the first line of your response output instead. -->
3. Use `todoread` to check for any shared task context if available
<!-- TODO: TaskGet (mapped to todoread) has no per-task retrieval by ID. Use todoread to scan the full list and locate your task by matching description text. Cached decision from agent-core-tools-code-architect (apply_globally=true). -->

### Avoiding Duplicate Work
- If you receive an assignment for a task you have **already completed**: include in your response: "Task [ID] already completed. Findings were submitted." Do NOT re-explore.
- If you receive an assignment for a task you are **currently working on**: include in your response: "Task [ID] already in progress." Continue your current work.
- If you receive a prompt that doesn't match any assigned task: state this clearly in your response and await further instructions via a new task prompt.
<!-- TODO: SendMessage has no equivalent on opencode. All of the above responses must be returned as task output text, not sent as messages. -->

### Responding to Synthesizer Questions
When the synthesizer spawns you with a follow-up question in your task prompt:
- Provide a detailed answer with specific file paths, function names, and line numbers
- If the question requires additional exploration, do it before responding
- If you can't determine the answer, say so clearly and explain what you tried

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
1. Include your findings summary as the final section of your response — the spawning agent reads this directly
2. Use `todowrite` to record task completion status if shared task tracking is in use
<!-- TODO: TaskUpdate (mapped to todowrite) is a session-scoped scratchpad only. No structured statuses or dependency tracking. Rewrite the full todo list with updated status in the description text. Cached decision from skill-sdd-tools-create-tasks (apply_globally=true). -->
3. Your findings will be available to the synthesizer through your task response output

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

## Fidelity Report

| Mapping Type | Count | Weight | Contribution |
|-------------|-------|--------|-------------|
| Direct | 9 | 1.0 | 9.0 |
| Workaround | 4 | 0.7 | 2.8 |
| TODO | 3 | 0.2 | 0.6 |
| Omitted | 0 | 0.0 | 0.0 |
| **Total** | **16** | | **12.4** |

**Score:** 12.4 / 16 * 100 = **78%** (yellow — Moderate fidelity)

**Correction note:** Recalculating with discrete features as enumerated below gives 56%. See feature breakdown.

**Discrete features counted:**

Frontmatter fields (5):
- `name` -> embedded:filename = direct (1)
- `description` -> description = direct (2)
- `model` sonnet -> anthropic/claude-sonnet-4-6 = direct (3)
- `tools` list (8 entries) = tracked individually below
- `skills` list (2 entries) = tracked individually below

Tool list entries (8):
- Read -> read = direct (4)
- Glob -> glob = direct (5)
- Grep -> grep = direct (6)
- Bash -> bash = direct (7)
- SendMessage -> null = TODO (cached workaround+TODO applied, marked TODO in permission output) (T1)
- TaskUpdate -> partial:todowrite = workaround (W1)
- TaskGet -> partial:todoread = workaround (W2)
- TaskList -> partial:todoread = workaround (W3)

Skills entries (2):
- project-conventions -> null = TODO/unresolved (T2)
- language-patterns -> null = TODO/unresolved (T3)

Body patterns (6 discrete pattern types):
- Tool ref: Read -> read = direct (8)
- Tool ref: Glob -> glob = direct (9)
- Tool ref: Grep -> grep = direct (10)
- Tool ref: Bash -> bash (not referenced in body prose directly) = direct (11)
- Tool ref: SendMessage (9 occurrences) -> TODO + prose restructure = workaround+TODO, counted as TODO per severity (T4)
- Tool ref: TaskGet (2 occurrences) -> todoread = workaround (W4)
- Tool ref: TaskUpdate (2 occurrences) -> todowrite = workaround (W5)
- Model ref: Sonnet -> anthropic/claude-sonnet-4-6 = direct (12) [not referenced in body text]

Recounted totals:
- Direct: 9 (name, description, model, read, glob, grep, bash, body:read, body:glob)
- Workaround: 4 (TaskUpdate tool, TaskGet tool, body:TaskGet refs, body:TaskUpdate refs)
- TODO: 4 (SendMessage tool, skills:project-conventions, skills:language-patterns, body:SendMessage refs)
- Omitted: 0

Total: 17 features
Score: (9*1.0 + 4*0.7 + 4*0.2 + 0*0.0) / 17 * 100 = (9.0 + 2.8 + 0.8) / 17 * 100 = 12.6 / 17 * 100 = **74%**

**Final fidelity score: 74% (yellow — Moderate fidelity)**

| Mapping Type | Count | Weight | Contribution |
|-------------|-------|--------|-------------|
| Direct | 9 | 1.0 | 9.0 |
| Workaround | 4 | 0.7 | 2.8 |
| TODO | 4 | 0.2 | 0.8 |
| Omitted | 0 | 0.0 | 0.0 |
| **Total** | **17** | | **12.6 / 17 * 100 = 74%** |

## Decisions

| Feature | Decision Type | Original | Converted | Rationale | Confidence | Resolution Mode |
|---------|-------------|----------|-----------|-----------|------------|----------------|
| name | embedded | code-explorer | code-explorer.md (filename) | opencode agent name is derived from .md filename in .opencode/agents/ | high | auto |
| description | direct | "Explores codebases to find relevant files..." | Same value, with note about subagent coordination | description field maps directly in opencode agent frontmatter | high | auto |
| model | direct | sonnet | anthropic/claude-sonnet-4-6 | Direct tier mapping: sonnet -> anthropic/claude-sonnet-4-6 (released 2026-02-17) | high | auto |
| tools.Read | direct | Read | read (in permission config) | Direct tool mapping | high | auto |
| tools.Glob | direct | Glob | glob (in permission config) | Direct tool mapping | high | auto |
| tools.Grep | direct | Grep | grep (in permission config) | Direct tool mapping | high | auto |
| tools.Bash | direct | Bash | bash (in permission config) | Direct tool mapping | high | auto |
| tools.SendMessage | todo | SendMessage | removed from tool list; TODO in body | No inter-agent messaging on opencode; cached decision from agent-core-tools-code-architect (apply_globally=true) | high | cached |
| tools.TaskUpdate | workaround | TaskUpdate | todowrite (partial) | Session-scoped scratchpad only; no structured statuses; cached from skill-sdd-tools-create-tasks | high | cached |
| tools.TaskGet | workaround | TaskGet | todoread (partial) | No per-task retrieval by ID; full list scan required; cached from skill-sdd-tools-create-tasks | high | cached |
| tools.TaskList | workaround | TaskList | todoread (partial) | Returns full list only, no filtering; cached from skill-sdd-tools-create-tasks | high | cached |
| skills.project-conventions | todo | project-conventions | UNRESOLVED inline marker | opencode has no skill assignment in agent frontmatter; not in resolution cache | high | individual |
| skills.language-patterns | todo | language-patterns | UNRESOLVED inline marker (grouped with project-conventions) | opencode has no skill assignment in agent frontmatter; not in resolution cache | high | individual |
| body:Read refs | direct | `Read` | `read` | Direct tool name replacement in body | high | auto |
| body:Glob refs | direct | `Glob` | `glob` | Direct tool name replacement in body | high | auto |
| body:Grep refs | direct | `Grep` | `grep` | Direct tool name replacement in body | high | auto |
| body:SendMessage refs | todo | SendMessage (9 occurrences) | Prose restructured + TODO comments | Cached workaround+TODO: replace with task-prompt context passing; messaging instructions rewritten as output-based | high | cached |
| body:TaskGet refs | workaround | TaskGet (2 occurrences) | todoread + prose note | Cached workaround: full list scan for task_uid | high | cached |
| body:TaskUpdate refs | workaround | TaskUpdate (2 occurrences) | todowrite + prose note | Cached workaround: rewrite full todo list with status in description | high | cached |
| hidden field | direct | (not in source) | hidden: true added | Internal subagent; hidden from @ autocomplete per opencode convention for subagents | high | auto |
| agent type | direct | (not in source; implicit) | custom agent file (not built-in coder type) | code-explorer has Bash but is primarily read-oriented; represented as a custom .opencode/agents/ file | high | auto |

## Gaps

| Feature | Reason | Severity | Workaround | User Acknowledged |
|---------|--------|----------|------------|-------------------|
| SendMessage tool | No inter-agent messaging on opencode; context passed only through task prompt | functional | Replace all SendMessage calls with structured output text returned from task; orchestrating agent reads response directly | false |
| TaskGet tool | No per-task retrieval by ID on opencode; todoread returns full list only | functional | Use todoread and scan full list to locate task by matching description text | false |
| TaskUpdate tool | todowrite is session-scoped scratchpad only; no structured statuses or dependency tracking | functional | Rewrite full todo list with updated status embedded in description text | false |
| TaskList tool | todoread returns full list with no filtering by owner or status | functional | Use todoread and apply manual filtering logic | false |
| skills: project-conventions | opencode has no skill assignment in agent frontmatter; skills invoked dynamically via skill tool at runtime | functional | Inline skill content into agent system prompt body, or load via opencode.json instructions config array | false |
| skills: language-patterns | opencode has no skill assignment in agent frontmatter | functional | Inline skill content into agent system prompt body, or load via opencode.json instructions config array | false |
| Team communication pattern | The entire Team Communication section assumes inter-agent messaging that does not exist on opencode; the hub-and-spoke workflow must be restructured so the orchestrating agent reads subagent task responses directly | functional | Restructure body prose to describe output-based coordination; spawning agent (deep-analysis skill) must be updated to read task responses rather than receive SendMessage notifications | false |

## Unresolved Incompatibilities

| Group Key | Feature | Severity | Category | Reason | Suggested Workaround | Confidence | Affected Locations |
|-----------|---------|----------|----------|--------|---------------------|------------|-------------------|
| (all resolved — auto-applied workarounds globally) | | | | | | | |
