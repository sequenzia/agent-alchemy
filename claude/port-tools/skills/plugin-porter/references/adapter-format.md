# Adapter File Format Specification

This reference defines the markdown-based adapter file format used by the plugin porter to map Claude Code plugin constructs to a target platform's equivalents. Each target platform has one adapter file stored in `references/adapters/`. The format is designed to be machine-parseable by an LLM during conversion while remaining human-readable for adapter authors.

---

## Format Overview

An adapter file is a markdown document with a fixed set of sections, each using structured tables, lists, or code blocks. Sections use H2 (`##`) headers. Subsections use H3 (`###`). The porter reads each section by header name, so headers must match exactly.

### Required vs Optional Sections

| Section | Required | Default if Omitted |
|---------|----------|--------------------|
| Platform Metadata | Yes | N/A (adapter is invalid without this) |
| Directory Structure | Yes | N/A (adapter is invalid without this) |
| Tool Name Mappings | Yes | N/A (adapter is invalid without this) |
| Model Tier Mappings | Yes | All models map to `generic` |
| Frontmatter Translations | Yes | N/A (adapter is invalid without this) |
| Hook/Lifecycle Event Mappings | No | All hooks treated as unsupported (`null`) |
| Composition Mechanism | Yes | N/A (conversion cannot proceed without this) |
| Path Resolution | Yes | N/A (conversion cannot proceed without this) |
| Adapter Version | Yes | N/A (staleness check requires this) |

If an optional section is omitted, the conversion engine applies the listed defaults and logs a warning in the migration guide.

---

## Section 1: Platform Metadata

**Required.** Identifies the target platform and links to its documentation.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Display name of the target platform |
| `slug` | string | Yes | Lowercase identifier used in file paths and references (e.g., `opencode`) |
| `documentation_url` | URL | Yes | Primary documentation URL for the platform's plugin system |
| `repository_url` | URL | No | GitHub or source repository URL, if public |
| `plugin_docs_url` | URL | No | Direct link to the plugin/extension authoring docs |
| `notes` | text | No | General caveats, maturity level, or important context for adapter authors |

### Format

```markdown
## Platform Metadata

| Field | Value |
|-------|-------|
| name | OpenCode |
| slug | opencode |
| documentation_url | https://opencode.ai/docs |
| repository_url | https://github.com/opencode-ai/opencode |
| plugin_docs_url | https://opencode.ai/docs/plugins |
| notes | Plugin system is in beta; API may change between minor versions. |
```

---

## Section 2: Directory Structure

**Required.** Defines how the target platform organizes plugin files and what naming conventions it uses.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `plugin_root` | path | Yes | Root directory for plugins relative to the project (e.g., `.opencode/plugins/`) |
| `skill_dir` | path | Yes | Subdirectory for skill/prompt files relative to plugin root |
| `agent_dir` | path | No | Subdirectory for agent definitions, if the platform has a distinct agent concept. Default: same as `skill_dir` |
| `hook_dir` | path | No | Subdirectory for hook/lifecycle configs. Default: plugin root |
| `reference_dir` | path | No | Subdirectory for reference/knowledge files. Default: same as `skill_dir` |
| `config_dir` | path | No | Subdirectory for configuration files (MCP, etc.). Default: plugin root |
| `file_extension` | string | Yes | File extension for skill/agent files (e.g., `.md`, `.yaml`, `.json`) |
| `naming_convention` | string | Yes | File naming pattern: `kebab-case`, `snake_case`, `camelCase`, or `PascalCase` |
| `notes` | text | No | Platform-specific directory layout caveats |

### Format

```markdown
## Directory Structure

| Field | Value |
|-------|-------|
| plugin_root | .opencode/plugins/ |
| skill_dir | prompts/ |
| agent_dir | agents/ |
| hook_dir | hooks/ |
| reference_dir | prompts/references/ |
| config_dir | config/ |
| file_extension | .md |
| naming_convention | kebab-case |
| notes | OpenCode uses a flat prompt directory; nested subdirectories are not supported for prompts. |
```

---

## Section 3: Tool Name Mappings

**Required.** Maps each Claude Code tool to its equivalent on the target platform. Use `null` for tools with no equivalent. Use `partial:{target_name}` for tools that exist but with reduced functionality.

### Value Conventions

| Value | Meaning |
|-------|---------|
| `{target_tool_name}` | Direct equivalent exists; use this name |
| `null` | No equivalent on the target platform; feature is a conversion gap |
| `partial:{target_tool_name}` | Equivalent exists but with limitations (document in the `notes` column) |
| `composite:{tool1}+{tool2}` | Requires combining multiple target tools to approximate the behavior |

### Mapping Table

The table must include all Claude Code tools used in Agent Alchemy plugins. Tools are grouped by category for readability.

```markdown
## Tool Name Mappings

### File Operations

| Claude Code Tool | Target Equivalent | Notes |
|-----------------|-------------------|-------|
| Read | {value} | {notes or empty} |
| Write | {value} | |
| Edit | {value} | |
| Glob | {value} | |
| Grep | {value} | |
| NotebookEdit | {value} | |

### Execution

| Claude Code Tool | Target Equivalent | Notes |
|-----------------|-------------------|-------|
| Bash | {value} | |
| Task | {value} | |

### Agent Coordination

| Claude Code Tool | Target Equivalent | Notes |
|-----------------|-------------------|-------|
| TeamCreate | {value} | |
| TeamDelete | {value} | |
| TaskCreate | {value} | |
| TaskUpdate | {value} | |
| TaskList | {value} | |
| TaskGet | {value} | |
| SendMessage | {value} | |

### User Interaction

| Claude Code Tool | Target Equivalent | Notes |
|-----------------|-------------------|-------|
| AskUserQuestion | {value} | |

### Web & Research

| Claude Code Tool | Target Equivalent | Notes |
|-----------------|-------------------|-------|
| WebSearch | {value} | |
| WebFetch | {value} | |

### MCP Tools

| Claude Code Tool | Target Equivalent | Notes |
|-----------------|-------------------|-------|
| mcp__context7__resolve-library-id | {value} | |
| mcp__context7__query-docs | {value} | |
| mcp__*  (generic pattern) | {value} | How the target references MCP-provided tools |
```

### Handling `null` Mappings

When a tool maps to `null`, the conversion engine will:
1. Remove the tool from converted skill/agent tool lists
2. Flag any skill logic that depends on the tool as a conversion gap
3. Record the gap in the migration guide with the notes from this table

### Handling `partial` Mappings

When a tool maps to `partial:{name}`, the conversion engine will:
1. Use the target tool name in converted files
2. Add a TODO comment at each usage site noting the limitation
3. Record the limitation in the migration guide

---

## Section 4: Model Tier Mappings

**Required.** Maps Claude Code model tiers to target platform equivalents.

### Fields

| Claude Code Model | Target Equivalent | Description |
|------------------|-------------------|-------------|
| `opus` | string | Highest-capability model; used for synthesis, architecture, review |
| `sonnet` | string | Mid-tier model; used for exploration, parallel worker tasks |
| `haiku` | string | Lightweight model; used for simple/quick tasks |
| `default` | string | Fallback when no specific tier is referenced |

### Value Conventions

- Use the target platform's model identifier if it has tiered models (e.g., `gpt-4o`, `gpt-4o-mini`)
- Use `generic` if the target platform does not support model selection
- Use `null` if the target has no concept of model specification

### Format

```markdown
## Model Tier Mappings

| Claude Code Model | Target Equivalent | Notes |
|------------------|-------------------|-------|
| opus | {value} | |
| sonnet | {value} | |
| haiku | {value} | |
| default | {value} | Used when source does not specify a model tier |
```

### Default Values

If the Model Tier Mappings section is present but a specific tier is missing from the table, map the missing tier to the `default` value. If `default` is also missing, use `generic`.

---

## Section 5: Frontmatter Translations

**Required.** Maps Claude Code YAML frontmatter fields (used in skill and agent files) to their target platform equivalents.

### Skill Frontmatter Fields

| Claude Code Field | Type | Target Equivalent | Notes |
|------------------|------|-------------------|-------|
| `name` | string | {target_field or null} | Skill identifier |
| `description` | string | {target_field or null} | Human-readable description |
| `argument-hint` | string | {target_field or null} | Usage hint shown to user |
| `user-invocable` | boolean | {target_field or null} | Whether users can invoke directly |
| `disable-model-invocation` | boolean | {target_field or null} | Whether to prevent model from auto-invoking |
| `allowed-tools` | list | {target_field or null} | Tool access restrictions for the skill |
| `model` | string | {target_field or null} | Model override for this skill (if supported) |

### Agent Frontmatter Fields

| Claude Code Field | Type | Target Equivalent | Notes |
|------------------|------|-------------------|-------|
| `name` | string | {target_field or null} | Agent identifier |
| `description` | string | {target_field or null} | Human-readable description |
| `model` | string | {target_field or null} | Model tier for this agent |
| `tools` | list | {target_field or null} | Tool access list |
| `skills` | list | {target_field or null} | Skills this agent can use |

### Value Conventions

- Use the target platform's field name if a direct equivalent exists
- Use `null` if the target has no equivalent concept (the field will be omitted from output)
- Use `embedded:{location}` if the information maps to a different location (e.g., metadata in the body instead of frontmatter)
- Include the target field's expected type in the notes if it differs from the source type

### Format

```markdown
## Frontmatter Translations

### Skill Frontmatter

| Claude Code Field | Target Field | Notes |
|------------------|-------------|-------|
| name | {value} | |
| description | {value} | |
| argument-hint | {value} | |
| user-invocable | {value} | |
| disable-model-invocation | {value} | |
| allowed-tools | {value} | |
| model | {value} | |

### Agent Frontmatter

| Claude Code Field | Target Field | Notes |
|------------------|-------------|-------|
| name | {value} | |
| description | {value} | |
| model | {value} | |
| tools | {value} | |
| skills | {value} | |
```

---

## Section 6: Hook/Lifecycle Event Mappings

**Optional.** Maps Claude Code hook events to target platform lifecycle events. If the target platform has no hook/lifecycle system, omit this section entirely.

### Event Mapping Table

| Claude Code Event | Target Equivalent | Notes |
|------------------|-------------------|-------|
| `PreToolUse` | {value or null} | Fired before a tool is executed |
| `PostToolUse` | {value or null} | Fired after a tool completes |
| `Stop` | {value or null} | Fired when the session is about to end |
| `SessionStart` | {value or null} | Fired when a new session begins |
| `Notification` | {value or null} | System notification events |

### Hook Configuration Format

Describe how the target platform configures hooks, if applicable:

```markdown
## Hook/Lifecycle Event Mappings

### Event Mappings

| Claude Code Event | Target Event | Notes |
|------------------|-------------|-------|
| PreToolUse | {value} | |
| PostToolUse | {value} | |
| Stop | {value} | |
| SessionStart | {value} | |
| Notification | {value} | |

### Hook Configuration

Target platform hook format: {describe the config format}

Example:
{show a minimal hook config example in the target platform's format}
```

### Default When Omitted

If this section is omitted from an adapter file, the conversion engine treats all hook events as unsupported (`null`) and moves all hook configurations to the gap report.

---

## Section 7: Composition Mechanism

**Required.** Describes how the target platform handles the equivalent of Claude Code's skill composition -- that is, how one prompt/skill loads or references another.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mechanism` | string | Yes | One of: `import`, `include`, `inline`, `reference`, `none` |
| `syntax` | string | Yes | The syntax or pattern used to compose (e.g., `@import "path/to/file"`) |
| `supports_cross_plugin` | boolean | Yes | Whether the target supports referencing prompts from other plugin groups |
| `supports_recursive` | boolean | No | Whether composition can be nested (skill loads skill loads skill). Default: `true` |
| `max_depth` | number | No | Maximum nesting depth, if limited. Default: unlimited |
| `notes` | text | No | Caveats about composition behavior |

### Mechanism Types

| Mechanism | Description |
|-----------|-------------|
| `import` | Target has an explicit import statement that loads another file's content |
| `include` | Target automatically includes files from a directory or glob pattern |
| `inline` | Content must be inlined (flattened) into the consuming file |
| `reference` | Target supports referencing by name/ID without file path |
| `none` | Target has no composition mechanism; all content must be self-contained |

### Format

```markdown
## Composition Mechanism

| Field | Value |
|-------|-------|
| mechanism | import |
| syntax | @import "relative/path/to/file.md" |
| supports_cross_plugin | true |
| supports_recursive | true |
| max_depth | 10 |
| notes | Imports are resolved at load time, not runtime. Circular imports cause an error. |
```

### Conversion Implications

- **`import`/`include`/`reference`**: Convert `Read ${CLAUDE_PLUGIN_ROOT}/...` patterns to the target's equivalent syntax
- **`inline`**: Flatten referenced skill content directly into the consuming file body
- **`none`**: Flatten all referenced content and produce fully self-contained files; flag in migration guide

---

## Section 8: Path Resolution

**Required.** Defines how the target platform resolves paths to plugin files, equivalent to Claude Code's `${CLAUDE_PLUGIN_ROOT}` variable.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `root_variable` | string | Yes | The target platform's equivalent of `${CLAUDE_PLUGIN_ROOT}`, or `null` if none |
| `resolution_strategy` | string | Yes | One of: `variable`, `relative`, `absolute`, `registry` |
| `same_plugin_pattern` | string | Yes | Pattern for referencing files within the same plugin |
| `cross_plugin_pattern` | string | No | Pattern for referencing files in other plugins. Default: same as `same_plugin_pattern` |
| `notes` | text | No | Caveats about path resolution |

### Resolution Strategies

| Strategy | Description |
|----------|-------------|
| `variable` | Uses a platform-provided variable (like `${CLAUDE_PLUGIN_ROOT}`) |
| `relative` | All paths are relative to the current file |
| `absolute` | Paths are absolute from the plugin root directory |
| `registry` | References are by name/ID, not file path (platform resolves internally) |

### Format

```markdown
## Path Resolution

| Field | Value |
|-------|-------|
| root_variable | ${OPENCODE_PLUGIN_DIR} |
| resolution_strategy | variable |
| same_plugin_pattern | ${OPENCODE_PLUGIN_DIR}/prompts/{skill-name}.md |
| cross_plugin_pattern | ${OPENCODE_PLUGIN_DIR}/../{plugin-name}/prompts/{skill-name}.md |
| notes | Variable is set at runtime; cannot be used in static config files. |
```

---

## Section 9: Adapter Version

**Required.** Tracks which version of the target platform's plugin system this adapter was written for. Used by the research phase to detect staleness.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `adapter_version` | semver | Yes | Version of this adapter file (e.g., `1.0.0`) |
| `target_platform_version` | string | Yes | Version of the target platform this adapter was tested against |
| `last_updated` | date | Yes | ISO 8601 date when this adapter was last reviewed/updated |
| `author` | string | No | Who created or last updated this adapter |
| `changelog` | text | No | Brief history of adapter changes |

### Format

```markdown
## Adapter Version

| Field | Value |
|-------|-------|
| adapter_version | 1.0.0 |
| target_platform_version | 0.5.2 |
| last_updated | 2026-02-17 |
| author | research-agent |
| changelog | Initial adapter created from live research. |
```

### Staleness Detection

During the research phase, the porter compares `target_platform_version` against the latest version discovered through live research. If they differ, the porter warns the user and offers to update the adapter before proceeding with conversion.

---

## Complete Adapter File Template

Below is a complete adapter file template showing all sections with placeholder values. Adapter authors should copy this template and fill in the values for their target platform.

```markdown
# {Platform Name} Adapter

Platform adapter for converting Claude Code plugins to {Platform Name} format.

---

## Platform Metadata

| Field | Value |
|-------|-------|
| name | {Platform Name} |
| slug | {platform-slug} |
| documentation_url | {https://...} |
| repository_url | {https://... or empty} |
| plugin_docs_url | {https://... or empty} |
| notes | {General caveats or empty} |

## Directory Structure

| Field | Value |
|-------|-------|
| plugin_root | {path/} |
| skill_dir | {path/} |
| agent_dir | {path/ or empty} |
| hook_dir | {path/ or empty} |
| reference_dir | {path/ or empty} |
| config_dir | {path/ or empty} |
| file_extension | {.md} |
| naming_convention | {kebab-case} |
| notes | {empty} |

## Tool Name Mappings

### File Operations

| Claude Code Tool | Target Equivalent | Notes |
|-----------------|-------------------|-------|
| Read | {value} | |
| Write | {value} | |
| Edit | {value} | |
| Glob | {value} | |
| Grep | {value} | |
| NotebookEdit | {value} | |

### Execution

| Claude Code Tool | Target Equivalent | Notes |
|-----------------|-------------------|-------|
| Bash | {value} | |
| Task | {value} | |

### Agent Coordination

| Claude Code Tool | Target Equivalent | Notes |
|-----------------|-------------------|-------|
| TeamCreate | {value} | |
| TeamDelete | {value} | |
| TaskCreate | {value} | |
| TaskUpdate | {value} | |
| TaskList | {value} | |
| TaskGet | {value} | |
| SendMessage | {value} | |

### User Interaction

| Claude Code Tool | Target Equivalent | Notes |
|-----------------|-------------------|-------|
| AskUserQuestion | {value} | |

### Web & Research

| Claude Code Tool | Target Equivalent | Notes |
|-----------------|-------------------|-------|
| WebSearch | {value} | |
| WebFetch | {value} | |

### MCP Tools

| Claude Code Tool | Target Equivalent | Notes |
|-----------------|-------------------|-------|
| mcp__context7__resolve-library-id | {value} | |
| mcp__context7__query-docs | {value} | |
| mcp__* (generic pattern) | {value} | |

## Model Tier Mappings

| Claude Code Model | Target Equivalent | Notes |
|------------------|-------------------|-------|
| opus | {value} | |
| sonnet | {value} | |
| haiku | {value} | |
| default | {value} | |

## Frontmatter Translations

### Skill Frontmatter

| Claude Code Field | Target Field | Notes |
|------------------|-------------|-------|
| name | {value} | |
| description | {value} | |
| argument-hint | {value} | |
| user-invocable | {value} | |
| disable-model-invocation | {value} | |
| allowed-tools | {value} | |
| model | {value} | |

### Agent Frontmatter

| Claude Code Field | Target Field | Notes |
|------------------|-------------|-------|
| name | {value} | |
| description | {value} | |
| model | {value} | |
| tools | {value} | |
| skills | {value} | |

## Hook/Lifecycle Event Mappings

### Event Mappings

| Claude Code Event | Target Event | Notes |
|------------------|-------------|-------|
| PreToolUse | {value} | |
| PostToolUse | {value} | |
| Stop | {value} | |
| SessionStart | {value} | |
| Notification | {value} | |

### Hook Configuration

{Describe the target platform's hook config format here.}

## Composition Mechanism

| Field | Value |
|-------|-------|
| mechanism | {import|include|inline|reference|none} |
| syntax | {pattern} |
| supports_cross_plugin | {true|false} |
| supports_recursive | {true|false} |
| max_depth | {number or unlimited} |
| notes | {empty} |

## Path Resolution

| Field | Value |
|-------|-------|
| root_variable | {variable or null} |
| resolution_strategy | {variable|relative|absolute|registry} |
| same_plugin_pattern | {pattern} |
| cross_plugin_pattern | {pattern or empty} |
| notes | {empty} |

## Adapter Version

| Field | Value |
|-------|-------|
| adapter_version | {semver} |
| target_platform_version | {version} |
| last_updated | {YYYY-MM-DD} |
| author | {name} |
| changelog | {text} |
```
