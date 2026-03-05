# Conversion Rules Reference

Detailed transformation rules for converting Claude Code plugin components into platform-agnostic format. These rules are applied during Phase 3 of port-master.

The guiding principle: preserve the *intent* of each instruction while removing anything that assumes the Claude Code runtime environment. A developer reading the output should understand what the component does without needing to know how Claude Code works.

---

## 1. Skill Frontmatter Rules

### Fields to Keep

| Field | Treatment |
|-------|-----------|
| `name` | Keep as-is |
| `description` | Keep. Remove trigger phrases that reference Claude Code mechanics (e.g., "Use when the user invokes /skill-name"). Keep phrases describing the task domain |

### Fields to Remove

| Field | Why |
|-------|-----|
| `allowed-tools` | Tool restrictions are Claude Code-specific. Capability needs go in Integration Notes prose instead |
| `user-invocable` | Slash command registration is a Claude Code feature |
| `disable-model-invocation` | Model auto-invocation is a Claude Code feature |
| `model` | Model selection is harness-specific. Complexity hints go in Integration Notes instead |
| `context` | Fork/subagent context is a Claude Code feature |
| `agent` | Subagent type routing is a Claude Code feature |
| `argument-hint` | Autocomplete UI is a Claude Code feature |
| `hooks` | Inline hooks are Claude Code-specific lifecycle events |
| `arguments` | Structured argument definitions are a Claude Code feature |

### Fields to Add

| Field | Value |
|-------|-------|
| `dependencies` | List of skill/agent names this component needs (extracted from dependency analysis) |

---

## 2. Agent Frontmatter Rules

### Fields to Keep

| Field | Treatment |
|-------|-----------|
| `name` | Keep as-is |
| `description` | Keep. Remove tool-list references. Focus on what the agent *does*, not what tools it has |

### Fields to Remove

| Field | Why |
|-------|-----|
| `tools` | Tool lists are Claude Code-specific. Capabilities described in prose instead |
| `disallowedTools` | Same as above |
| `model` | Model tier is harness-specific |
| `permissionMode` | Permission modes are a Claude Code feature |
| `maxTurns` | Turn limits are a Claude Code feature |
| `skills` | Preload mechanism is Claude Code-specific. Resolved into body text |
| `hooks` | Inline hooks are Claude Code-specific |
| `memory` | Memory scoping is a Claude Code feature |
| `mcpServers` | MCP configuration is Claude Code-specific |

### Fields to Add

| Field | Value |
|-------|-------|
| `role` | One of: `explorer`, `reviewer`, `architect`, `executor`, `synthesizer`, `investigator`, `writer`, `researcher`, `validator`. Inferred from the agent's description and body |
| `dependencies` | Skills this agent needs access to (from `skills:` frontmatter array) |

---

## 3. Body Transformation Rules

Apply these transformations in order to both skill and agent bodies. Each rule includes the pattern to detect, what to replace it with, and an example.

### 3a. Path Variable Resolution

Remove all `${CLAUDE_PLUGIN_ROOT}` path references. The replacement depends on what the path points to:

| Pattern | Replacement |
|---------|-------------|
| `Read ${CLAUDE_PLUGIN_ROOT}/skills/{name}/SKILL.md` | Inline the content (if marked "inline" in resolution plan) or replace with: `Refer to the **{name}** skill for {brief description of what it provides}.` |
| `Read ${CLAUDE_PLUGIN_ROOT}/../{group}/skills/{name}/SKILL.md` | Replace with: `Refer to the **{name}** skill (from the {group} package) for {brief description}.` |
| `Read ${CLAUDE_PLUGIN_ROOT}/skills/{name}/references/{file}` | Inline the content (if marked "inline"), or if the reference is owned by the current skill: `See **references/{file}** for {brief description}.`, or if owned by another skill: `See the **{file}** reference in the **{owner-skill}** skill directory for {brief description}.` |
| `${CLAUDE_PLUGIN_ROOT}/hooks/{script}` | Replace with relative path: `hooks/scripts/{script}` |
| Any remaining `${CLAUDE_PLUGIN_ROOT}` | Remove the path variable, use relative paths or named references |

### 3b. Tool-Specific Language

Rewrite instructions that reference Claude Code tools by name. The goal is to describe the *action*, not the tool.

| Pattern to Detect | Generic Replacement |
|-------------------|-------------------|
| "Use the Read tool to..." / "Read the file at..." | "Read..." / "Open..." |
| "Use Glob to find..." / "Glob for..." | "Search for files matching..." / "Find files..." |
| "Use Grep to search..." / "Grep for..." | "Search file contents for..." / "Find occurrences of..." |
| "Use the Bash tool to..." / "Run with Bash:" | "Run the command:" / "Execute:" |
| "Use Write to create..." / "Write the file:" | "Create the file:" / "Write:" |
| "Use Edit to modify..." / "Edit the file:" | "Modify the file:" / "Update:" |
| "Use the Agent tool to spawn..." | "Delegate to..." / "Have a sub-agent..." |
| "Use the Task tool..." | "Create a background task to..." |

Also remove tool name lists in prose like "You have access to Read, Glob, Grep, Bash" or "allowed tools: Read, Write, Edit" — these are implementation details.

### 3c. Orchestration Decomposition

Claude Code's team orchestration features (TeamCreate, SendMessage, TaskCreate, etc.) should be decomposed into plain-language workflow descriptions. The intent is to describe *what work happens* and *in what order*, not the specific API.

**Team creation and coordination:**

Before (Claude Code):
```
1. Create a team with TeamCreate
2. Spawn 3 explorer agents via Agent tool with subagent_type: "code-explorer"
3. Create tasks for each explorer using TaskCreate
4. Wait for all explorers to complete (monitor via TaskList)
5. Spawn a synthesizer agent to merge findings
6. Read findings via SendMessage
```

After (generic):
```
1. Delegate exploration to 3 independent workers, each assigned a different focus area
   - These can run in parallel if the harness supports concurrent agents
2. Once all exploration is complete, have a synthesizer agent merge the findings into a unified analysis
```

**Task management:**

Before: `TaskCreate`, `TaskUpdate`, `TaskList`, `TaskGet`
After: Describe as a checklist or workflow steps. "Track progress on these sub-tasks:" followed by the task descriptions.

**Message passing:**

Before: `SendMessage` with `type: "message"`, `type: "broadcast"`, `type: "shutdown_request"`
After: Describe as coordination. "Share findings with the team lead" → "The exploration results feed into the next step." Remove shutdown requests entirely (harness manages agent lifecycle).

**Wave-based execution:**

Before: "Process in waves: Wave 1 handles leaf nodes, Wave 2 handles components depending on Wave 1..."
After: "Process in dependency order. Components with no dependencies can be processed first (and in parallel if supported). Components that depend on earlier results should wait until their dependencies are complete."

### 3d. Claude-Specific Prompt Engineering

Remove directives that are specific to steering Claude's behavior rather than describing the task:

| Pattern | Action |
|---------|--------|
| `"CRITICAL: Complete ALL N phases"` | Remove. The phase structure itself conveys this |
| `"After completing each phase, immediately proceed to the next"` | Remove |
| `"Do NOT create an implementation plan"` (plan mode workarounds) | Remove |
| Model-tier instructions: "Use Sonnet for...", "Spawn as Opus" | Remove |
| `"NEVER do this" / "ALWAYS do this"` blocks about AskUserQuestion | Remove (AskUserQuestion patterns are Claude Code-specific) |
| References to `$ARGUMENTS` parsing | Replace with: "Accept the following inputs:" followed by parameter descriptions |
| `context: fork` behavior descriptions | Remove |

**Keep** phase structure, step numbering, and workflow ordering — these are useful organizational patterns regardless of platform.

### 3e. User Interaction Patterns

Claude Code's `AskUserQuestion` tool has a specific structured format. Convert to generic interaction descriptions:

Before:
```yaml
AskUserQuestion:
  questions:
    - header: "Approach"
      question: "Which approach should we use?"
      options:
        - label: "Option A"
          description: "Fast but less thorough"
        - label: "Option B"
          description: "Slower but comprehensive"
      multiSelect: false
```

After:
```
Prompt the user to choose an approach:
- **Option A**: Fast but less thorough
- **Option B**: Slower but comprehensive
```

For `multiSelect: true`, note "The user may select multiple options."

### 3f. Settings and Configuration

References to `.claude/agent-alchemy.local.md` or other Claude Code settings files should be generalized:

Before: "Read `.claude/agent-alchemy.local.md` for `deep-analysis.cache-ttl-hours`"
After: "Check configuration for cache TTL (default: 24 hours)"

If the skill reads settings, list them in the Integration Notes as configurable parameters.

Note: After generalization, any remaining `.claude/` paths are caught by rule 3g (Platform Path Replacement) which converts them to `.agents/`.

### 3g. Platform Path Replacement

Replace ALL `.claude/` path references with `.agents/` in converted output. This applies as a blanket text replacement AFTER all other body transformations (3a-3f) have completed.

| Pattern | Replacement |
|---------|-------------|
| `.claude/sessions/` | `.agents/sessions/` |
| `.claude/tasks/` | `.agents/tasks/` |
| `.claude/teams/` | `.agents/teams/` |
| `.claude/worktrees/` | `.agents/worktrees/` |
| `.claude/agent-alchemy.local.md` | `.agents/agent-alchemy.local.md` |
| Any remaining `.claude/` path | `.agents/` equivalent |

This applies to:
- Skill and agent body text
- Reference file content
- Hook script content (shell scripts)
- Integration guide text
- Manifest metadata (if paths appear)

**Implementation:** After all other transformations (3a-3f) are complete, perform a global search-and-replace of `.claude/` with `.agents/` on the final output text.

**Exclusion:** The string `.claude-plugin` must NOT be affected — only standalone `.claude/` path segments are replaced. Use a pattern that matches `.claude/` followed by a path segment (e.g., `.claude/sessions/`) but not `.claude-plugin/`.

---

## 4. Hook Event Mapping

Map Claude Code lifecycle events to generic event names with descriptions:

| Claude Code Event | Generic Event | Description |
|-------------------|---------------|-------------|
| `PreToolUse` | `before_action` | Fires before the agent executes any action (file write, shell command, etc.) |
| `PostToolUse` | `after_action` | Fires after an action completes successfully |
| `PostToolUseFailure` | `after_action_failure` | Fires after an action fails |
| `Stop` | `agent_stop` | Fires when the agent finishes its turn |
| `SubagentStop` | `subagent_stop` | Fires when a delegated sub-agent completes |
| `SubagentStart` | `subagent_start` | Fires when a delegated sub-agent is launched |
| `SessionStart` | `session_start` | Fires when a new conversation session begins |
| `SessionEnd` | `session_end` | Fires when a conversation session ends |
| `UserPromptSubmit` | `user_input` | Fires when the user submits a message |
| `PreCompact` | `before_context_compact` | Fires before the conversation context is compressed |
| `Notification` | `notification` | Fires on system notifications |
| `TaskCompleted` | `task_completed` | Fires when a tracked task is marked complete |
| `TeammateIdle` | `agent_idle` | Fires when a delegated agent becomes idle |
| `PermissionRequest` | `permission_request` | Fires when an action requires user approval |

### Hook Entry Format

Convert each hook entry from JSON to YAML:

```yaml
hooks:
  - event: before_action
    matcher: "Write|Edit|Bash"  # Optional regex filter on action type
    description: "Auto-approve file operations targeting session directories"
    type: command  # "command" or "prompt"
    command: "./scripts/auto-approve-session.sh"
    timeout: 5
```

For `type: "prompt"` hooks, the `prompt` field contains plain text instructions — keep as-is since they're already generic.

### Script Cleanup

For shell scripts referenced by hooks:

1. Replace `${CLAUDE_PLUGIN_ROOT}` with relative paths (e.g., `./scripts/`)
2. Remove references to Claude Code-specific JSON input format (`tool_name`, `tool_input`) — add a comment noting the script expects action context as JSON on stdin
3. Keep the script's core logic intact (path matching, validation, approval decisions)
4. Add a header comment explaining the script's purpose and expected input format

---

## 5. Integration Notes Template

Append this section to every converted skill and agent. Tailor the content based on what the component actually needs.

```markdown
## Integration Notes

**What this component does:** {One sentence summary of purpose}

**Capabilities needed:**
{List only capabilities this specific component requires}
- File reading and searching (if it reads/searches files)
- File writing and editing (if it creates/modifies files)
- Shell command execution (if it runs commands)
- User interaction / prompting (if it asks the user questions)
- Sub-agent delegation (if it spawns other agents)
- Web access (if it fetches URLs or searches the web)

**Adaptation guidance:**
{Specific notes about what needs manual attention, e.g.:}
- "The exploration step delegates to multiple agents in parallel — implement as concurrent tasks if your harness supports it, or serialize if not"
- "References to {skill-name} should point to wherever you've placed that converted skill"
- "The original used a 3-tier model strategy (fast/balanced/powerful) — use your default model unless specific steps need stronger reasoning"

**Configurable parameters:**
{If the skill reads settings, list them here with defaults}
```

---

## 6. Smart Resolution Decision Tree

When deciding how to handle a reference file, first determine the **primary owner** — the skill whose source directory originally contained the reference (from the source path `skills/{owner}/references/{file}`). If the primary owner was not selected for conversion, assign ownership to the first selected consumer.

### Skill-consumed references

```
Is the reference consumed by a single skill?
├── Yes → Check line count
│   ├── Under 250 lines → INLINE into the consuming skill's SKILL.md
│   │   Insert content under a heading: ## {Reference Name}
│   │   Add a brief intro: "The following reference provides {purpose}:"
│   └── 250+ lines → Keep SEPARATE in the consuming skill's references/ directory
│       File path: skills/{consumer}/references/{filename}
│       Replace the Read directive with: See **references/{filename}** for {purpose}.
└── No (multiple skill consumers) → Keep SEPARATE in the PRIMARY OWNER's references/ directory
    File path: skills/{owner}/references/{filename}
    For the owning skill: See **references/{filename}** for {purpose}.
    For other consumers: See the **{filename}** reference in the **{owner-skill}** skill directory for {purpose}.
```

### Agent-consumed references

When an agent directly reads a reference file:

```
Check line count:
├── Under 250 lines → INLINE into the agent body
│   Insert content under a heading: ## {Reference Name}
│   Add a brief intro: "The following reference provides {purpose}:"
└── 250+ lines → PROMOTE TO SKILL
    Create a new skill: skills/{ref-name}/SKILL.md
    Frontmatter: name and description inferred from reference content
    Body: the reference content (with body transformation rules applied)
    Add the new skill to the agent's dependencies list
```

If a reference is consumed by both skills and agents, follow the skill-consumed rules. The agent references the owning skill's directory like any other cross-skill reference.

### Path conventions

- Same-skill reference: `references/{filename}` (relative to the skill's own directory)
- Cross-skill reference: `../{owner-skill}/references/{filename}` (relative path between skill directories)
- Promoted skill: `skills/{ref-name}/SKILL.md` (treated as a regular skill)

### Name collision handling

If a promoted agent reference shares a name with an existing skill, prefix with the agent name: `skills/{agent-name}-{ref-name}/SKILL.md`.

When inlining, apply the same body transformation rules (sections 3a-3g) to the inlined content.

---

## 7. Agent-to-Skill Conversion Rules (Flatten Mode)

When flatten mode is active, agents are converted to skills instead of being output as agents. These rules govern the transformation.

### Frontmatter Mapping

| Agent Field | Skill Field | Treatment |
|-------------|-------------|-----------|
| `name` | `name` | Keep as-is |
| `description` | `description` | Keep. Append " (converted from agent)" |
| `tools` | *(removed)* | Capabilities listed in Integration Notes prose |
| `disallowedTools` | *(removed)* | Noted as restrictions in Integration Notes |
| `model` | *(removed)* | Complexity hint in Integration Notes (e.g., "originally required high-reasoning model") |
| `role` (inferred) | *(removed)* | Added as "Role context" note in Integration Notes |
| `skills` | `dependencies` | Each preloaded skill becomes a dependency |
| `permissionMode` | *(removed)* | Platform-specific |
| `maxTurns` | *(removed)* | Platform-specific |
| `hooks` | *(removed)* | Platform-specific |
| `memory` | *(removed)* | Platform-specific |
| `mcpServers` | *(removed)* | Platform-specific |

### Body Reframing

Agent system prompts are written as identity statements directed at the agent. Skills are written as task instructions for the invoking harness. Apply these reframing patterns:

| Agent Pattern | Skill Replacement |
|---------------|-------------------|
| "You are a {role} that..." | "When invoked, perform the following {role} tasks:" |
| "You are an agent responsible for..." | "This skill handles..." |
| "Your task is to..." | "Perform the following:" |
| "As a {role}, you should..." | "For {role} work:" |
| "You have been assigned to..." | "The objective is to..." |
| "Your role is..." | "This skill's purpose is..." |
| "You only have access to {tools}" | *(remove — tools go in Integration Notes)* |
| "You can use {tool} to..." | Rewrite using rule 3b (tool-specific language) |

Preserve the substantive instructions, workflow steps, and domain knowledge from the agent body. Only reframe the identity and capability framing — the core logic stays intact.

### Skill Preload Resolution

Agent frontmatter `skills:` entries that preload other skills at spawn time become explicit references in the skill body:

Before (agent frontmatter):
```yaml
skills:
  - technical-diagrams
  - language-patterns
```

After (in skill body, near the top):
```markdown
**Prerequisites:** This skill builds on knowledge from:
- **technical-diagrams** — Mermaid diagram conventions and styling
- **language-patterns** — Language-specific coding patterns and idioms
```

Read each preloaded skill's description to generate the brief summary after the dash.

### Tool Capability Summary

The agent's `tools` list becomes a paragraph in Integration Notes:

```markdown
**Original tool scope:** This component was originally an agent with access to: {tool list}.
The target harness may want to scope this skill's capabilities accordingly:
- File operations: {Read, Glob, Grep — if any present}
- File modifications: {Write, Edit — if any present}
- Shell execution: {Bash — if present}
- Sub-agent delegation: {Agent — if present}
- User interaction: {AskUserQuestion — if present}
- Web access: {WebSearch, WebFetch — if any present}
```

Only include capability lines for tools that were actually in the agent's tools list.

---

## 8. Hook-to-Skill Conversion Rules (Flatten Mode)

When flatten mode is active, all hooks from a group are merged into a single `lifecycle-hooks` skill rather than being output as a separate hooks directory.

### Skill Structure

```yaml
---
name: lifecycle-hooks
description: >-
  Behavioral rules and lifecycle event handlers for the {group-name} package.
  Defines automated behaviors that trigger at specific points in the agent workflow.
  (converted from hooks)
dependencies: []
---
```

### Name Collision Handling

If a group already has a skill named `lifecycle-hooks`, prefix with the group name: `{group}-lifecycle-hooks`.

### Event Conversion

Each hook entry becomes a subsection in the skill body. Use the event mapping from Section 4 (Hook Event Mapping) to translate event names.

Format for each hook:

```markdown
## On {generic-event-name}

**Trigger:** {description from Section 4 event mapping}
**Applies when:** {matcher pattern, if present — omit this line if no matcher}

{For prompt hooks: the prompt text verbatim}

{For command hooks: prose description of what the script does}
```

### Prompt Hook Handling

Prompt hooks contain plain text instructions that are already platform-agnostic. Include the prompt text directly as the rule body under the event heading.

### Command Hook Handling

Command hooks reference shell scripts. For each:

1. Read the referenced script to understand its purpose
2. Write a prose summary describing the script's behavior as a behavioral rule
3. Store the original script as a reference file at `skills/lifecycle-hooks/references/{script-name}.sh`
4. Apply rule 3g (`.claude/` → `.agents/` path replacement) to the script content
5. Reference the script from the skill body:

```markdown
The implementation logic is in **references/{script-name}.sh**. This script:
- {bullet point summary of what the script does}
- Expected input: {describe expected stdin/environment}
- Expected output: {describe what it returns/prints}
```

### Merging Multiple Hooks for Same Event

If multiple hooks fire on the same event (with different matchers), group them under the same `## On {event}` heading with sub-sections for each matcher:

```markdown
## On before_action

### When action matches `Write|Edit`
{behavior description}

### When action matches `Bash`
{behavior description}
```

### Integration Notes

Append to the lifecycle-hooks skill:

```markdown
## Integration Notes

**What this component does:** Defines automated behavioral rules that were originally enforced by platform lifecycle hooks.

**Origin:** Converted from {count} lifecycle hooks ({list of original event types})

**Capabilities needed:**
- Event/lifecycle hook system (if the target harness supports one)
- Alternatively, implement as middleware, conditional checks, or manual review steps

**Adaptation guidance:**
- These behaviors were originally enforced automatically by the platform. In the target harness, they may need to be implemented as middleware, event handlers, or manual review steps.
- Command hook scripts in `references/` can be executed directly if the harness supports shell-based hooks.
- Prompt hook text can be injected into agent context when the corresponding event fires.
```

---

## 9. Agent-to-Nested Conversion Rules (Nested Mode)

When nested mode is active, agents with a parent skill (determined by `AGENT_PARENT_MAP` from Phase 2) are converted to pure markdown instruction files and placed in the parent skill's `agents/` directory. Agents without a parent (orphans) are promoted to standalone skills using Section 7 rules.

The key difference from flatten mode: nested agents retain their role-based voice because they are still conceptually sub-agents — their instructions are read by the parent skill when spawning. Flatten mode rewrites agent identity as task instructions because the agent loses its sub-agent nature entirely.

### Output Format

Nested agent files have **no YAML frontmatter**. They are pure markdown with a consistent section structure:

```markdown
# {Agent Name}

{One-line summary of what this agent does — from the original frontmatter `description`.}

## Role

{Description of the agent's role and responsibilities.}

## Inputs

This agent receives:
- **{param}**: {description}

## Process

{Numbered steps and workflow phases — the core logic from the agent body.}

## Output Format

{Structured output format if the agent produces JSON, markdown sections, etc.
Omit this section entirely if the agent has no structured output.}

## Guidelines

{Behavioral rules, quality standards, and constraints.
Omit this section if there are no notable guidelines beyond the process steps.}
```

### Frontmatter Disposal

All YAML frontmatter fields are handled as follows:

| Agent Field | Treatment |
|-------------|-----------|
| `name` | Used as the markdown title: `# {Name}` |
| `description` | Used as the one-line summary below the title and as the basis for the Role section |
| `tools` | Removed. Noted in the **parent skill's** Integration Notes as capability requirements for this sub-agent |
| `disallowedTools` | Removed. Noted in the parent skill's Integration Notes as scope restrictions |
| `model` | Removed. Noted in the parent skill's Integration Notes as a complexity hint (e.g., "originally ran on a high-reasoning model") |
| `skills` | Converted to context references in the Role section (see Skill Preload Conversion below) |
| `permissionMode` | Removed — platform-specific |
| `maxTurns` | Removed — platform-specific |
| `hooks` | Removed — platform-specific |
| `memory` | Removed — platform-specific |
| `mcpServers` | Removed — platform-specific |

### Body Reframing

Nested agents keep their role-based voice — they describe *who they are* and *what they do*, not task instructions for an invoker. Apply these reframing patterns:

| Agent Pattern | Nested Replacement |
|---------------|-------------------|
| "You are a {role} that..." | "{Role} responsible for..." |
| "You are an agent responsible for..." | "Responsible for..." |
| "Your task is to..." | "The primary task is to..." |
| "As a {role}, you should..." | "For {role} work:" |
| "You have been assigned to..." | "The objective is to..." |
| "Your role is..." | "This agent's purpose is..." |
| "You only have access to {tools}" | *(remove — tools noted in parent skill's Integration Notes)* |
| "You can use {tool} to..." | Rewrite using rule 3b (tool-specific language) |

Preserve substantive instructions, workflow steps, and domain knowledge. Only reframe identity and capability framing — the core logic stays intact.

After reframing, apply all standard Body Transformation Rules (3a-3g) to the body content.

### Skill Preload Conversion

Agent frontmatter `skills:` entries become prose references in the Role section:

Before (agent frontmatter):
```yaml
skills:
  - technical-diagrams
  - language-patterns
```

After (in Role section):
```markdown
This agent draws on knowledge from:
- **technical-diagrams** — {brief description from the skill's description field}
- **language-patterns** — {brief description}
```

Read each preloaded skill's description to generate the brief summary after the dash.

### Parent Skill Augmentation

After converting all agents for a parent skill, augment the parent skill's converted SKILL.md:

**1. Add a `## Nested Agents` section** listing all nested agents with one-line descriptions:

```markdown
## Nested Agents

The `agents/` directory contains instructions for specialized sub-agents.
Read them when spawning the relevant sub-agent.

- `agents/{name}.md` — {one-line description from the agent's original description}
```

**2. Rewrite spawn instructions** in the parent skill body to reference nested files:

| Before | After |
|--------|-------|
| "Spawn N agents via Agent tool with subagent_type: '{name}'" | "Delegate to N independent {role} agents (see `agents/{name}.md` for instructions)" |
| "Launch a {name} agent to..." | "Delegate to a {role} agent (see `agents/{name}.md`) to..." |
| "subagent_type: '{plugin}:{name}'" | "Delegate to a {role} agent (see `agents/{name}.md` for instructions)" |

**3. Add agent capability requirements** to the parent skill's Integration Notes:

```markdown
**Sub-agent capabilities:**
{For each nested agent:}
- **{agent-name}**: Requires {capability list derived from the agent's original `tools` field}
```

### Cross-Skill Agent References

When a skill references an agent that is nested under a **different** parent skill:

- Do NOT duplicate the agent file
- Add a cross-reference in the referencing skill's body:
  ```
  This step uses the **{agent-name}** agent defined in the **{parent-skill}** skill
  (see `../{parent-skill}/agents/{agent-name}.md` for instructions).
  ```
- Add the cross-reference to the referencing skill's `## Nested Agents` section (or create one if it doesn't exist):
  ```
  - `../{parent-skill}/agents/{agent-name}.md` — {description} *(defined in {parent-skill})*
  ```

### Orphan Agent Handling

Agents not spawned by any selected skill are promoted to standalone skills using Section 7 (Agent-to-Skill Conversion Rules). Apply the full Section 7 transformation, then append to Integration Notes:

```markdown
**Origin:** Promoted from orphan agent `{name}` — no parent skill in this package spawns this agent directly.
```

These appear at the top level under `skills/{agent-name}/` with `origin: agent` in the manifest.
