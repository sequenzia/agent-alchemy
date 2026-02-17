# Agent Converter Reference

This reference defines the conversion logic for transforming Claude Code agent definitions (`.md` files with YAML frontmatter and a markdown system prompt body) into target platform equivalents. The porter skill loads this reference during Phase 5 (Interactive Conversion) when processing components of type `agent`.

---

## Agent File Structure

A Claude Code agent file has two parts:

1. **YAML frontmatter** -- metadata fields between `---` delimiters at the top of the file
2. **Markdown body** -- the system prompt that instructs the agent's behavior

Example source agent:

```yaml
---
name: code-explorer
description: Explores codebases to find relevant files and map architecture
model: sonnet
tools:
  - Read
  - Glob
  - Grep
  - Bash
  - SendMessage
skills:
  - project-conventions
  - language-patterns
---

# Code Explorer Agent

You are a code exploration specialist. Use `Read` to examine files, `Glob` to find files by pattern...

## Team Communication

Use `SendMessage` to respond to questions from other agents...
```

---

## Conversion Pipeline

Process each agent file through these stages in order:

```
1. Parse Source         -- Extract frontmatter fields and body text
2. Map Frontmatter     -- Translate each frontmatter field using adapter mappings
3. Transform Body      -- Rewrite tool names, model references, and paths in the body
4. Handle Gaps         -- Resolve features with no target equivalent
5. Assemble Output     -- Produce the converted file in target format
6. Score Fidelity      -- Calculate conversion quality metrics
7. Record Decisions    -- Log all conversion choices for the migration guide
```

---

## Stage 1: Parse Source

Read the source agent file and extract:

| Component | Description |
|-----------|-------------|
| `frontmatter.name` | Agent identifier (string) |
| `frontmatter.description` | Human-readable description (string) |
| `frontmatter.model` | Model tier: `opus`, `sonnet`, `haiku`, or `inherit` (string) |
| `frontmatter.tools` | List of tool names the agent can access (array of strings) |
| `frontmatter.skills` | List of skill names the agent can use (array of strings) |
| `body` | Full markdown content below the closing `---` delimiter |

### Optional Frontmatter Fields

Some agent files may include additional frontmatter fields. These are less common but must be handled:

| Field | Description | Handling |
|-------|-------------|----------|
| `hooks` | Agent-level hook configuration | Check adapter Hook/Lifecycle section |
| `memory` | Memory/context persistence settings | Check if target has equivalent; likely a gap |
| `mcpServers` | MCP server configurations for this agent | Check adapter MCP tool mappings |
| `permissionMode` | Tool permission level | Check if target has equivalent |
| `maxTurns` | Maximum conversation turns | Check if target has equivalent |
| `disallowedTools` | Tools explicitly denied to this agent | Check if target supports tool deny-lists |

If an optional field is present but the adapter has no mapping for it, treat it as a conversion gap and apply the gap handling procedure from Stage 4.

---

## Stage 2: Map Frontmatter

For each frontmatter field, look up the mapping in the adapter's **Frontmatter Translations > Agent Frontmatter** table. The adapter table has three columns: `Claude Code Field`, `Target Field`, and `Notes`.

### Field Mapping Rules

#### `name`

1. Read the adapter mapping for `name` (e.g., `embedded:config-key`, `name`, or `null`)
2. If the target field is a standard field name (e.g., `name`): use it directly with the same value
3. If the target field is `embedded:{location}`: the name is not in frontmatter but derived from another mechanism
   - `embedded:filename` -- The agent name becomes the output filename (apply the adapter's `naming_convention` from Directory Structure)
   - `embedded:config-key` -- The agent name is used as a configuration key in a config file; note the config file path in the conversion decisions
4. If the target field is `null`: the target platform has no agent naming mechanism; use the name for the output filename and log as informational

#### `description`

1. Read the adapter mapping for `description`
2. If a target field exists: map directly
3. If `null`: the description cannot be represented in the target format
   - Preserve the description as a comment at the top of the converted body (e.g., `<!-- Original description: {description} -->`) so it is not lost
   - Record the gap: "Agent description field has no target equivalent; preserved as comment"

#### `model`

1. Read the adapter mapping for `model` to find the target field name
2. Read the adapter's **Model Tier Mappings** table to translate the model value:
   - Look up `frontmatter.model` (e.g., `sonnet`) in the Claude Code Model column
   - Use the corresponding Target Equivalent value (e.g., `claude-4-sonnet`)
3. If the adapter `model` target field is a config path (e.g., `agents.{name}.model`):
   - Replace `{name}` with the agent's name (or its target equivalent)
   - Note that model configuration requires a config file entry, not a frontmatter field
   - Record a config-file instruction: "Add `agents.{name}.model = {target_model}` to {config_file}"
4. If the target field is `null`: model cannot be configured
   - Record the gap: "Model tier '{model}' cannot be specified on the target platform"

#### `tools`

1. Read the adapter mapping for `tools` (the frontmatter field mapping)
2. If a target field exists: translate each tool name using the adapter's **Tool Name Mappings** table
   - For each tool in the source `tools` list:
     - Look up the tool in the Tool Name Mappings table
     - If the target equivalent is a tool name: include it in the converted tools list
     - If the target equivalent is `null`: omit it from the list; record: "Tool '{tool}' has no equivalent; removed from agent tool list"
     - If the target equivalent is `partial:{name}`: include the target name; add a note about limitations
     - If the target equivalent is `composite:{t1}+{t2}`: include both target tools; note the composite mapping
   - Remove duplicates from the resulting list
3. If the target `tools` field is `null`: the target platform does not support configurable tool lists
   - Record the gap: "Agent tool restrictions cannot be configured; target platform uses fixed tool sets per agent type"
   - If the body text references specific tools, those references still need transformation in Stage 3

#### `skills`

1. Read the adapter mapping for `skills`
2. If a target field exists: translate skill names to target references
   - For each skill in the source `skills` list:
     - Determine the target skill path or reference using the adapter's composition mechanism and directory structure
     - If the target platform supports skill references: map to the target format
     - If a skill is from a different plugin group (cross-plugin reference): check if the adapter supports cross-plugin composition
3. If the target field is `null`: the target platform has no concept of skills assigned to agents
   - Check the adapter Notes for alternative mechanisms (e.g., `contextPaths`, system prompt injection)
   - If an alternative exists: record instruction for the alternative mechanism
   - If no alternative: record the gap: "Skills '{skills}' cannot be assigned to agents; consider inlining skill content into the agent's system prompt"
   - **Inlining consideration**: if the adapter's composition mechanism is `none` or `inline`, and the skills are essential to the agent's behavior, flag for the incompatibility resolver to ask the user whether to inline the skill content

---

## Stage 3: Transform Body

The agent's markdown body is a system prompt that typically references Claude Code-specific constructs. Scan and transform the body text through these passes:

### Pass 1: Tool Name References

Scan the body for references to Claude Code tool names and replace with target equivalents.

**Detection patterns:**
- Backtick-quoted tool names: `` `Read` ``, `` `Glob` ``, `` `Bash` ``
- Tool names in natural language: "Use Read to...", "the Glob tool", "via Bash"
- Tool names in code blocks or examples: `Read: path/to/file`, `Glob: **/*.ts`
- Composite tool references: "Use `TaskCreate` and `TaskUpdate`"

**Transformation rules:**
1. For each Claude Code tool name found in the body:
   - Look up the tool in the adapter's Tool Name Mappings table
   - If a target equivalent exists: replace the tool name with the target name
   - If `null`: replace with a placeholder and add a TODO comment
     - Example: `` `Read` `` -> `` `[NO_EQUIVALENT: Read]` `` with inline comment `<!-- TODO: No equivalent for Read on {platform} -->`
   - If `partial:{name}`: replace with the target name and add a note about limitations
2. Preserve the surrounding context (backticks, prose, code blocks)
3. Be case-sensitive: `Read` is a tool, `read` in prose may not be

**Example transformation:**

Source:
```markdown
Use `Read` to examine file contents and `Glob` to find files by pattern.
Use `SendMessage` to communicate with other agents.
```

Target (OpenCode):
```markdown
Use `view` to examine file contents and `glob` to find files by pattern.
<!-- TODO: No equivalent for SendMessage on OpenCode. OpenCode has no inter-agent messaging. -->
```

### Pass 2: Model Tier References

Scan the body for references to Claude Code model tiers and replace with target equivalents.

**Detection patterns:**
- Direct model names: "Sonnet", "Opus", "Haiku" (case-insensitive)
- Model tier descriptions: "sonnet-tier", "opus-level", "haiku-class"
- Model assignment context: "model: sonnet", "uses Sonnet for..."
- Comparative references: "higher-capability model like Opus"

**Transformation rules:**
1. For each model tier reference:
   - Look up the tier in the adapter's Model Tier Mappings table
   - Replace with the target equivalent model identifier
   - If the target has no model tiers (all map to `generic`): replace with "the configured model" or similar generic phrasing
2. Preserve the intent of the reference (e.g., "use a powerful model" stays meaningful even if specific names change)

**Example transformation:**

Source:
```markdown
This agent uses Sonnet for fast exploration tasks. For complex synthesis, the orchestrator uses Opus.
```

Target (OpenCode):
```markdown
This agent uses claude-4-sonnet for fast exploration tasks. For complex synthesis, the orchestrator uses claude-4-opus.
```

### Pass 3: Path Variable References

Scan the body for `${CLAUDE_PLUGIN_ROOT}` path patterns and transform based on the adapter's Path Resolution section.

**Detection patterns:**
- `${CLAUDE_PLUGIN_ROOT}/path/to/file`
- `${CLAUDE_PLUGIN_ROOT}/../other-plugin/path/to/file`
- Read/load instructions: "Read: ${CLAUDE_PLUGIN_ROOT}/..."

**Transformation rules:**
1. Read the adapter's Path Resolution section for `root_variable` and `resolution_strategy`
2. If the target has a root variable: replace `${CLAUDE_PLUGIN_ROOT}` with the target variable
3. If the resolution strategy is `relative`: convert to relative paths from the output file location
4. If the root variable is `null` and the strategy is `relative`:
   - Convert to relative paths based on the target directory structure
   - If the path references a file that will be converted: use the target output path
   - If the path references a file that will not be converted: flag as gap
5. For cross-plugin references (`${CLAUDE_PLUGIN_ROOT}/../{group}/...`):
   - Check adapter's `cross_plugin_pattern`
   - If `null` or not supported: flag as gap; the referenced content may need inlining

**Example transformation:**

Source:
```markdown
Read the skill definition:
Read: ${CLAUDE_PLUGIN_ROOT}/skills/deep-analysis/SKILL.md
```

Target (OpenCode, where composition is `none`):
```markdown
<!-- TODO: Cross-file reference not supported on OpenCode. The content from skills/deep-analysis/SKILL.md must be inlined or placed in OpenCode.md -->
```

### Pass 4: Claude Code-Specific Patterns

Scan for patterns that are specific to Claude Code's runtime and have no general equivalent.

**Patterns to detect and transform:**

| Pattern | Detection | Transformation |
|---------|-----------|----------------|
| `AskUserQuestion` usage instructions | "Use AskUserQuestion to...", "via AskUserQuestion" | Replace with target user interaction mechanism per adapter; or add TODO if `null` |
| Task management instructions | "Mark your task as completed using TaskUpdate", "Use TaskCreate to..." | Replace with target equivalent or remove with TODO |
| Team communication instructions | "Send your findings via SendMessage", "Use TeamCreate to..." | Replace with target equivalent or remove with TODO |
| Subagent spawning instructions | "Spawn a subagent using Task tool", "Launch an agent via Task" | Replace with target agent spawning mechanism per adapter |
| Claude Code runtime references | "Claude Code will...", "the Claude Code platform..." | Replace with target platform name where appropriate |
| Phase workflow directives | "CRITICAL: Complete ALL N phases" | Preserve as-is (these are prompt engineering patterns, not platform-specific) |
| Permission model references | "Requires user permission approval" | Adapt to target platform's permission model or remove |

### Pass 5: Structural Adaptations

Some body transformations require structural changes, not just text replacement.

**Composition flattening:**
If the adapter's composition mechanism is `none` or `inline`:
- Skill loading instructions (e.g., "Load the project-conventions skill") become irrelevant
- Remove or replace with: "The following guidelines are incorporated from {skill-name}:" followed by a recommendation to inline the content
- The actual inlining of skill content is handled separately by the skill converter; the agent converter flags the dependency

**Agent type mapping:**
If the target platform has fixed agent types (e.g., OpenCode has `coder`, `task`, `title`, `summarizer`):
- Map the Claude Code agent's role to the closest target agent type based on capabilities:
  - Agents with write tools (`Write`, `Edit`, `Bash`) -> map to the full-capability agent type (e.g., `coder`)
  - Agents with read-only tools (`Read`, `Glob`, `Grep`) -> map to the restricted agent type (e.g., `task`)
  - Agents with specific roles (reviewer, architect) -> map to the closest match or the full-capability type
- Record the mapping decision: "Agent '{name}' (model: {model}) mapped to target agent type '{type}' based on tool profile"

**Output format adaptation:**
If the target platform uses a different file format for agent definitions:
- Convert frontmatter from YAML to the target format (JSON, TOML, etc.)
- Restructure the file layout per adapter's Directory Structure section
- If the target has no separate agent files: produce a config entry and a system prompt file (or just a system prompt if agents are config-only)

---

## Stage 4: Handle Gaps

When a feature has no direct target equivalent, apply the incompatibility resolution flow.

### Gap Classification

| Gap Type | Severity | Description |
|----------|----------|-------------|
| `field-unsupported` | Low | A frontmatter field has no target equivalent (e.g., `description` -> `null`) |
| `tool-missing` | Medium | A tool the agent depends on does not exist on the target platform |
| `skill-unassignable` | Medium | Skills cannot be assigned to agents on the target platform |
| `composition-unavailable` | High | The agent references other files but the target has no composition mechanism |
| `agent-type-mismatch` | High | The agent's role does not map to any target agent type |
| `model-unconfigurable` | Low | Model tier cannot be specified on the target platform |

### Resolution Options

For each gap, present options to the user via `AskUserQuestion` (unless the gap is Low severity, in which case apply the default automatically):

```yaml
AskUserQuestion:
  questions:
    - header: "Agent Conversion: {agent-name}"
      question: "{description of the gap}"
      options:
        - label: "Workaround"
          description: "{suggested workaround based on research}"
        - label: "Omit"
          description: "Remove this feature from the converted agent"
        - label: "TODO comment"
          description: "Leave a TODO placeholder in the output"
      multiSelect: false
```

### Default Resolutions for Low-Severity Gaps

Apply these automatically without user interaction:

| Gap | Default Resolution |
|-----|-------------------|
| `field-unsupported` (description) | Preserve as comment in body |
| `field-unsupported` (argument-hint) | Add as comment in body |
| `model-unconfigurable` | Use generic model reference; note in migration guide |

---

## Stage 5: Assemble Output

Produce the converted agent file(s) in the target platform's format.

### Output File Determination

1. Read the adapter's **Directory Structure** section:
   - `agent_dir` -- where agent files are stored
   - `file_extension` -- what extension to use
   - `naming_convention` -- how to format the filename
2. If `agent_dir` is `null`: agents do not have dedicated files on the target
   - Determine the best output based on the adapter notes:
     - If agents map to config entries: produce a config fragment
     - If agents map to custom commands: output to the skill/command directory
     - If agents have no equivalent at all: produce a standalone system prompt file in a reasonable location and document the limitation

### Filename Generation

Apply the adapter's naming convention to the agent name:

| Convention | Example (input: `code-explorer`) |
|------------|----------------------------------|
| `kebab-case` | `code-explorer` |
| `snake_case` | `code_explorer` |
| `camelCase` | `codeExplorer` |
| `PascalCase` | `CodeExplorer` |

Combine: `{agent_dir}/{formatted-name}{file_extension}`

### File Assembly

Build the output file by combining the mapped frontmatter and transformed body:

1. If the target uses frontmatter (YAML, TOML, JSON header): write the mapped frontmatter fields
2. If the target embeds metadata differently: place metadata per the adapter's conventions
3. Write the transformed body text
4. Append any TODO comments or gap annotations at the end of the file

### Config File Entries

If the frontmatter mapping produced config-file instructions (e.g., model configuration):

1. Collect all config entries for this agent
2. Produce a config fragment that can be merged into the target's config file
3. Include the fragment in the conversion output alongside the agent file
4. Note in the migration guide: "Merge the following config into {config_file}:"

---

## Stage 6: Score Fidelity

Calculate a fidelity score (0-100%) for the converted agent using the unified scoring system from Phase 5 Step 9.

### Feature Classification

During Stages 1-5, classify every discrete agent feature into the four-category system:

- **Direct** (weight 1.0) -- feature has a 1:1 target equivalent with no loss
- **Workaround** (weight 0.7) -- feature mapped via partial/composite/workaround with behavioral differences
- **TODO** (weight 0.2) -- feature converted to a placeholder comment for manual implementation
- **Omitted** (weight 0.0) -- feature removed entirely from converted output

Agent-specific discrete features include:
- Each frontmatter field (`name`, `description`, `model`, `tools`, `skills`, `hooks`, `memory`, `mcpServers`, `permissionMode`, `maxTurns`, `disallowedTools`)
- Each entry in the `tools` list
- Each entry in the `skills` list
- Each body pattern (composition references, path references, tool references)

### Score Calculation

```
fidelity_score = ((direct_count * 1.0) + (workaround_count * 0.7) + (todo_count * 0.2) + (omitted_count * 0.0)) / total_features * 100
```

Round to the nearest integer.

### Agent-Specific Weighting (Optional Refinement)

For agents, the per-area breakdown provides additional diagnostic detail beyond the unified score. Track sub-scores for the migration guide:

| Area | Weight | Scoring |
|------|--------|---------|
| Frontmatter fields | 25% | (fields direct/workaround/todo/omitted classification) |
| Tools preserved | 25% | (tools direct/workaround/todo/omitted classification) |
| Body transformations | 30% | (patterns direct/workaround/todo/omitted classification) |
| Skills assignable | 10% | (skills direct/workaround/todo/omitted classification) |
| Gaps resolved | 10% | (workarounds applied vs. omitted/TODO) |

These sub-scores are informational and included in the agent's `FIDELITY_REPORT` for the migration guide. The primary `fidelity_score` uses the unified formula above.

### Score Color Bands

| Range | Band | Label | Meaning |
|-------|------|-------|---------|
| 80-100% | Green | High fidelity | Agent is well-represented on the target platform |
| 50-79% | Yellow | Moderate fidelity | Core behavior preserved but notable gaps exist |
| 0-49% | Red | Low fidelity | Significant features cannot be represented; manual work needed |

Set `band` on the result: `"green"` (>= 80), `"yellow"` (50-79), `"red"` (< 50).

---

## Stage 7: Record Decisions

Track every conversion decision for inclusion in the migration guide and gap report.

### Decision Record Format

For each agent, produce a decision log:

```markdown
### Agent: {name}

**Source:** {source_file_path}
**Output:** {output_file_path}
**Fidelity:** {score}% ({Green/Yellow/Red} -- {High/Moderate/Low} fidelity)

#### Frontmatter Mappings

| Field | Source Value | Target Value | Status |
|-------|-------------|-------------|--------|
| name | {value} | {target_value} | mapped/embedded/gap |
| description | {value} | {target_value or "N/A"} | mapped/comment/gap |
| model | {value} | {target_value} | mapped/config/gap |
| tools | {list} | {target_list} | mapped/partial/gap |
| skills | {list} | {target_value or "N/A"} | mapped/inlined/gap |

#### Tool Transformations

| Source Tool | Target Tool | Status |
|-------------|-------------|--------|
| Read | {target} | direct/partial/gap |
| Glob | {target} | direct/partial/gap |
| SendMessage | {target or "N/A"} | direct/gap |

#### Body Transformations

| Pattern | Occurrences | Action |
|---------|-------------|--------|
| Tool name: `Read` | {count} | Replaced with `{target}` |
| Tool name: `SendMessage` | {count} | Removed with TODO comment |
| Model reference: Sonnet | {count} | Replaced with `{target}` |
| Path: ${CLAUDE_PLUGIN_ROOT}/... | {count} | {action taken} |

#### Gaps Identified

| Feature | Severity | Resolution | User Decision |
|---------|----------|------------|---------------|
| {feature} | {severity} | {workaround/omit/todo} | {auto/user-chosen} |

#### Config File Entries

{Any config fragments that need to be merged into the target platform's config file.}
```

### Migration Guide Contribution

The decision record for each agent feeds into two sections of the migration guide:

1. **Per-component details**: The full decision record is included in the MIGRATION-GUIDE.md under the agent's entry
2. **Gap report entries**: Each gap from the "Gaps Identified" table is added to the GAP-REPORT.md with its severity and resolution

---

## OpenCode-Specific Conversion Notes

Since OpenCode is the MVP target platform, the following notes document expected conversion behavior for common agent patterns when using the OpenCode adapter:

### Agent Type Mapping

Claude Code agents map to OpenCode agent types based on their tool profile:

| Claude Code Agent Pattern | OpenCode Agent Type | Rationale |
|--------------------------|---------------------|-----------|
| Write + Edit + Bash tools | `coder` | Full-capability agent with file modification |
| Read + Glob + Grep only | `task` | Read-only sub-agent for exploration |
| WebSearch + WebFetch tools | `coder` | No dedicated research agent type; use coder with fetch |
| Any agent with SendMessage/TeamCreate | `coder` | No team coordination; map to most capable type |

### Expected Gaps

| Agent Feature | Gap | Default Resolution |
|---------------|-----|-------------------|
| `skills` field | OpenCode has no skill assignment | Record as gap; suggest inlining skill content into the system prompt or placing in OpenCode.md |
| `tools` field (configurable list) | OpenCode tool sets are fixed per agent type | Record as gap; note which tools are available for the mapped agent type |
| `description` field | OpenCode auto-generates descriptions | Preserve as comment in body |
| Inter-agent communication (SendMessage) | No equivalent | Remove from body with TODO; note in gap report |
| Task management (TaskCreate, TaskUpdate, etc.) | No equivalent | Remove from body with TODO; note in gap report |
| Team coordination (TeamCreate, TeamDelete) | No equivalent | Remove from body with TODO; note in gap report |

### Output Structure

For OpenCode, converted agents produce:

1. **A custom command file** at `.opencode/commands/{agent-name}.md` -- contains the transformed system prompt
2. **A config fragment** for `.opencode.json` -- contains model configuration (e.g., `"agents": {"coder": {"model": "claude-4-sonnet"}}`)
3. **Migration notes** -- which built-in agent type to use and what was lost in conversion
