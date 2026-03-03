---
name: port-master
description: >-
  Convert Claude Code plugins into generic, platform-agnostic skills, agents, and hooks
  that work with any coding agent harness. Strips Claude Code-specific implementation details
  to produce clean markdown files preserving only the intent and instructions.
  Use when asked to "make this portable", "convert to generic format", "export plugin",
  "create universal skills", "strip platform dependencies", "make harness-agnostic",
  "decouple from Claude Code", or when the user wants their plugin content usable
  outside Claude Code. Also use when the user wants to share skills with teams using
  different agent frameworks.
argument-hint: <plugin-group-or-component> [--all] [--output <dir>]
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

# Port Master

Extract the platform-agnostic intent from Claude Code plugins, producing clean markdown files that any agent harness developer can read and adapt. The output preserves the *what* and *why* of each skill, agent, and hook while removing implementation details tied to Claude Code.

The goal is portability through clarity — a developer familiar with any agent framework should be able to read the output and integrate it into their system without needing to understand Claude Code's internals.

Complete ALL 5 phases. After completing each phase, immediately proceed to the next without waiting for user prompts.

## Critical Rules

### AskUserQuestion is MANDATORY

Use the `AskUserQuestion` tool for ALL questions to the user. Never ask questions through regular text output.

- Selection questions → AskUserQuestion
- Confirmation questions → AskUserQuestion
- Clarifying questions → AskUserQuestion

Text output is only for status updates, summaries, and informational context.

### Plan Mode Behavior

This skill performs an interactive conversion workflow. When invoked during plan mode:

- Proceed with the full wizard and conversion workflow immediately
- Write converted files to the output directory as normal
- Do NOT create an implementation plan or defer work to an "execution phase"

## Phase Overview

1. **Arguments & Component Selection** — Parse arguments, load registry, interactive selection wizard
2. **Dependency Analysis** — Build dependency graph, classify dependencies, plan smart resolution
3. **Conversion** — Transform each component using rules from `references/conversion-rules.md`
4. **Output Generation** — Write files, manifest, and integration guide
5. **Summary** — Present results and next steps

---

## Phase 1: Arguments & Component Selection

**Goal:** Determine what to convert and where to put the output.

### Step 1: Parse Arguments

Parse `$ARGUMENTS` for:
- Plugin group name(s) — positional arguments
- `--all` — Convert all plugin groups
- `--output <dir>` — Output directory (default: `./ported/{group-name}/`)

### Step 2: Load Marketplace Registry

Read the plugin registry to enumerate available plugin groups:

```
Read: ${CLAUDE_PLUGIN_ROOT}/../../.claude-plugin/marketplace.json
```

Parse the `plugins` array. Each entry has `name`, `version`, `description`, and `source` (relative path like `./core-tools`). Extract the short group name from the source path.

**Exclude `plugin-tools` from the selection list** — the converter should not attempt to convert itself.

### Step 3: Group-Level Selection

Determine which plugin groups to convert based on the parsed arguments. Exactly one of these three branches applies:

**If specific plugin names were provided as positional arguments:**

Validate each name against the short group names extracted from the registry's `source` paths (e.g., `core-tools`, `dev-tools`). If all names are valid, use them as `SELECTED_GROUPS`.

If any name doesn't match, present a correction prompt:

```yaml
AskUserQuestion:
  questions:
    - header: "Invalid Plugin"
      question: "'{invalid-name}' was not found. Which plugin groups would you like to convert?"
      options:
        - label: "{group-name} (v{version})"
          description: "{skill_count} skills, {agent_count} agents{, hooks} — {description}"
      multiSelect: true
```

**If `--all` was specified:**

Select all groups from the registry (excluding `plugin-tools`). No user interaction needed.

**If NO arguments were provided (no plugin names, no `--all`):**

Present the full list of available plugin groups for interactive selection. This is MANDATORY — do not assume defaults or skip this step.

```yaml
AskUserQuestion:
  questions:
    - header: "Plugin Groups"
      question: "Which plugin groups would you like to convert to generic format?"
      options:
        - label: "{group-name} (v{version})"
          description: "{skill_count} skills, {agent_count} agents{, hooks} — {description}"
      multiSelect: true
```

For each group option, scan its directory to count components:
- Skills: `Glob claude/{group}/skills/*/SKILL.md`
- Agents: `Glob claude/{group}/agents/*.md`
- Hooks: check for `claude/{group}/hooks/hooks.json`

Store selections as `SELECTED_GROUPS`.

### Step 4: Component-Level Selection

For each selected group, enumerate components by reading frontmatter from each file to extract `name` and `description`. Present for selection:

```yaml
AskUserQuestion:
  questions:
    - header: "{group-name}"
      question: "Select components from {group-name}:"
      options:
        - label: "All components"
          description: "Convert everything ({total} components)"
        - label: "skill: {name}"
          description: "{description}"
        - label: "agent: {name}"
          description: "{description}"
        - label: "hooks"
          description: "{hook_count} lifecycle hooks"
      multiSelect: true
```

If "All components" is selected, include everything from that group.

Build `SELECTED_COMPONENTS` — a flat list:
```
[{ type: "skill"|"agent"|"hooks", group: "{group}", name: "{name}", path: "{file path}" }]
```

### Step 5: Confirm Selection

Present a summary table and confirm with the user:

```yaml
AskUserQuestion:
  questions:
    - header: "Confirm"
      question: "Proceed with converting {count} components?"
      options:
        - label: "Proceed"
          description: "Continue to dependency analysis"
        - label: "Modify"
          description: "Change component selection"
        - label: "Cancel"
          description: "Exit"
      multiSelect: false
```

---

## Phase 2: Dependency Analysis & Resolution Planning

**Goal:** Map all dependencies between selected components and plan how to resolve them in the generic output.

### Step 1: Parse Dependencies

For each component in `SELECTED_COMPONENTS`, read its source file and scan for dependency patterns.

**Five dependency patterns to detect:**

| Pattern | Example | Type |
|---------|---------|------|
| Same-plugin skill load | `Read ${CLAUDE_PLUGIN_ROOT}/skills/{name}/SKILL.md` | skill-to-skill |
| Cross-plugin load | `${CLAUDE_PLUGIN_ROOT}/../{group}/skills/{name}/SKILL.md` | cross-plugin |
| Reference file include | `${CLAUDE_PLUGIN_ROOT}/skills/{name}/references/{file}` | reference |
| Agent spawn | `subagent_type: "{name}"` or `subagent_type: "{plugin}:{name}"` | agent-ref |
| Agent skill preload | `skills:` array in agent frontmatter | agent-to-skill |

Also detect external dependencies (MCP servers, shell scripts) for informational tracking.

### Step 2: Classify Dependencies

For each dependency found, classify it:

| Classification | Meaning | Action |
|----------------|---------|--------|
| **Internal** | Target is in `SELECTED_COMPONENTS` | Will be converted; reference by name |
| **External-available** | Target exists on disk but wasn't selected | Reference by name in manifest |
| **External-missing** | Target doesn't exist locally | Note as unresolved in manifest |
| **Reference file** | Points to a `references/*.md` file | Smart resolution (see Step 3) |

### Step 3: Smart Resolution Planning

For each reference file dependency, determine how to handle it based on line count, consumer count, and consumer type.

1. Count lines in the referenced file using `Bash: wc -l < {path}`
2. Determine the **primary owner** — the skill whose source directory originally contained the reference file (from the source path `skills/{owner}/references/{file}`). If the primary owner was not selected for conversion, assign ownership to the first selected consumer
3. Identify all consumers — which skills and agents use this reference

**Decision logic for skill-consumed references:**

- **Under 250 lines AND single consumer** → mark for **inline** (content will be embedded directly in the consuming skill's SKILL.md)
- **250+ lines AND single consumer** → mark as **separate** in the consuming skill's `references/` directory
- **Multiple skill consumers** → mark as **separate** in the **primary owner** skill's `references/` directory; other consumers reference via relative path `../{owner-skill}/references/{file}`

**Decision logic for agent-consumed references:**

- **Under 250 lines** → mark for **inline** into the agent's body
- **250+ lines** → mark as **promote_to_skill** — the reference becomes a new skill at `skills/{ref-name}/SKILL.md` with its content as the body. The agent's converted text will reference it as a dependency. If the name collides with an existing skill, prefix with the agent name: `{agent-name}-{ref-name}`

**Mixed consumers (skill + agent):** Skill-consumed rules take precedence. The agent references the owning skill's directory.

Store decisions as `RESOLUTION_PLAN`:
```
[{ ref_path, line_count, decision: "inline"|"separate"|"promote_to_skill", owner_skill: "{skill-name}", used_by: [component names] }]
```

### Step 4: Present Dependency Summary

Show the user:
- Total dependencies found
- How many will be inlined vs. kept as separate files
- Which skill directories will contain `references/` subdirectories and what they own
- Any references promoted from agent references to standalone skills
- Any external/missing dependencies that won't be included
- Ask for confirmation to proceed

---

## Phase 3: Conversion

**Goal:** Transform each component into a clean, platform-agnostic format.

Before starting conversion, read the detailed transformation rules:

```
Read ${CLAUDE_PLUGIN_ROOT}/skills/port-master/references/conversion-rules.md
```

Process components in dependency order (leaf nodes first) so that when a component references another, the referenced component has already been converted.

### Skill Conversion

For each skill:

1. **Read source** — Read the SKILL.md file, split into YAML frontmatter and markdown body
2. **Transform frontmatter** — Apply the Skill Frontmatter Rules from conversion-rules.md: keep `name` and `description`, remove platform-specific fields, add `dependencies` list
3. **Transform body** — Apply all Body Transformation Rules from conversion-rules.md in order:
   - Resolve `${CLAUDE_PLUGIN_ROOT}` references (inline small content or add `See: {name}` pointers)
   - Rewrite tool-specific language to generic descriptions
   - Decompose orchestration patterns (teams, tasks, waves) into sequential/parallel prose
   - Remove prompt engineering directives aimed at Claude specifically
4. **Append Integration Notes** — Add a `## Integration Notes` section describing what capabilities the target harness needs to support this skill
5. **Store result** for output in Phase 4

### Agent Conversion

For each agent:

1. **Read source** — Read the agent `.md` file
2. **Transform frontmatter** — Keep `name` and `description`. Add `role` (inferred from description: explorer, reviewer, architect, executor, etc.). Add `dependencies` for any preloaded skills
3. **Transform body** — Same rules as skills, plus:
   - Resolve `skills:` preloads into prose ("This agent draws on knowledge from {skill-name}")
   - Remove tool-restriction prose ("You only have access to Read, Glob, Grep")
4. **Append Integration Notes**
5. **Store result**

### Hook Conversion

For each hooks component:

1. **Read source** — Read `hooks.json` and parse JSON
2. **Convert to YAML** — Map Claude Code event names to generic lifecycle events using the Hook Event Mapping table from conversion-rules.md
3. **Process hook entries:**
   - **Command hooks** → Copy referenced scripts, resolve `${CLAUDE_PLUGIN_ROOT}` paths to relative paths within the output directory. Add a comment explaining what the script does (read the script to understand its purpose)
   - **Prompt hooks** → Preserve the prompt text as-is (already platform-agnostic)
4. **Add descriptions** — For each hook entry, add a `description` field explaining when and why this hook fires
5. **Store result**

### Reference File Handling

For reference files marked as **"separate"** in the `RESOLUTION_PLAN`:

1. Read the source file
2. Clean any `${CLAUDE_PLUGIN_ROOT}` paths in the content
3. Remove Claude Code-specific tool references if present
4. Store for copying to the owning skill's `references/` directory (i.e., `skills/{owner_skill}/references/{file}`)

For reference files marked as **"promote_to_skill"**:

1. Read the source file
2. Apply the same body transformation rules (3a-3f from conversion-rules.md) to the content
3. Wrap the content as a new skill with minimal frontmatter (`name` and `description` inferred from the reference content and heading)
4. Store as a new skill entry at `skills/{ref-name}/SKILL.md`
5. Update the consuming agent's `dependencies` list to include the new skill name

For reference files marked as **"inline"** — their content was already embedded during skill/agent conversion.

---

## Phase 4: Output Generation

**Goal:** Write all converted files, the manifest, and the integration guide.

### Step 1: Determine Output Directory

If `--output` was specified, use that. Otherwise ask:

```yaml
AskUserQuestion:
  questions:
    - header: "Output Directory"
      question: "Where should the converted files be written?"
      options:
        - label: "./ported/{group-name}/ (Recommended)"
          description: "Standard ported output location"
        - label: "Custom path"
          description: "Specify a different output directory"
      multiSelect: false
```

Check for existing files in the output directory and warn before overwriting.

### Step 2: Write Component Files

Create the output directory structure and write all converted files:

```
{output}/
├── manifest.yaml
├── INTEGRATION-GUIDE.md
├── skills/
│   └── {name}/
│       ├── SKILL.md
│       └── references/         (only if this skill owns reference files)
│           └── {file}.md
├── agents/
│   └── {name}.md
└── hooks/
    ├── hooks.yaml
    └── scripts/
        └── {script-name}.sh
```

Each skill gets its own directory with `SKILL.md` inside. Reference files are co-located in the owning skill's `references/` subdirectory — only create the `references/` subdirectory when at least one separate reference file exists. There is no root-level `references/` directory. Agents remain as flat files.

Write each converted component to its appropriate location.

### Step 3: Generate manifest.yaml

The manifest provides a machine-readable inventory of the package:

```yaml
name: {group-name}
description: {from marketplace registry}
source:
  platform: "Claude Code"
  plugin: "{marketplace-name}"
  version: "{version}"
converted: "{YYYY-MM-DD}"

components:
  skills:
    - name: {name}
      file: skills/{name}/SKILL.md
      description: {description}
      references:                          # only if this skill owns reference files
        - name: {ref-name}
          file: skills/{name}/references/{ref-name}.md
          used_by: [{component names}]
  agents:
    - name: {name}
      file: agents/{name}.md
      description: {description}
      role: {role}
  hooks:
    - event: {generic-event-name}
      file: hooks/hooks.yaml
      description: {what the hook does}

dependencies:
  internal:
    - from: {component}
      to: {component}
      relationship: "{what it loads/uses}"
  external:
    - from: {component}
      to: {external name}
      source_plugin: "{plugin group}"
      relationship: "{what it needs}"
      note: "Not included — convert separately if needed"
```

### Step 4: Generate INTEGRATION-GUIDE.md

The guide helps harness developers understand and integrate the converted components:

```markdown
# Integration Guide: {group-name}

## Overview
{What this package provides — summarize the plugin group's purpose}

## Component Inventory
| Component | Type | Description |
|-----------|------|-------------|
{table of all components}

## Capability Requirements
{What features the target harness needs — organized by category:}
- **File operations**: Which components need to read/write/search files
- **Shell execution**: Which components run shell commands
- **User interaction**: Which components prompt for user input
- **Sub-agent delegation**: Which components spawn child agents
- **Web access**: Which components fetch external content (if any)

## Per-Component Notes
{For each component, compile the Integration Notes section from the converted file}

## Dependency Map
{If more than 5 internal dependencies, include a text-based dependency diagram}

## Adaptation Checklist
- [ ] Review each skill's instructions and adapt tool-specific language for your harness
- [ ] Configure agent spawning for components that delegate to sub-agents
- [ ] Set up lifecycle hooks if your harness supports them
- [ ] Resolve external dependencies listed in manifest.yaml
- [ ] Test each component individually before combining
```

### Step 5: Write All Files

Write all files to the output directory using the `Write` tool. Track every file written for the summary.

---

## Phase 5: Summary

**Goal:** Present conversion results and suggest next steps.

### Results Table

```
## Conversion Complete

| Component | Type | Lines (source → output) | Notes |
|-----------|------|------------------------|-------|
{for each component}

**Files written:** {count}
**Skill directories created:** {count}
**References inlined:** {count} ({total lines})
**References co-located with skills:** {count}
**References promoted to skills:** {count} (from agent references)
**External dependencies:** {count} (not included)
```

### Next Steps

Suggest:
1. Review the INTEGRATION-GUIDE.md for capability requirements
2. Start with the simplest skill to validate integration with the target harness
3. If external dependencies exist, note which plugin groups they come from
4. For components that used team orchestration (now decomposed to sequential/parallel steps), test the simplified workflow to ensure it meets needs
