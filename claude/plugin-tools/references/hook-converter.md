# Hook Converter

Reference for converting Claude Code hook configurations (`hooks.json`) to target platform equivalents. The hook converter handles JSON parsing, event type mapping, matcher pattern transformation, command/script path transformation, and graceful degradation for platforms with no hook support.

---

## Overview

Claude Code hooks are defined in `hooks.json` files within each plugin group's `hooks/` directory. Each hook configuration maps event types (such as `PreToolUse`, `PostToolUse`, `Stop`) to arrays of hook entries that execute shell commands in response to those events. Hooks provide automation capabilities like auto-approving file operations, running linters, or triggering custom scripts.

Many target platforms have no equivalent hook or lifecycle event system. The converter must handle this gracefully by documenting what is lost, suggesting workarounds where the target platform offers partial alternatives, and producing clear gap report entries for features that cannot be ported.

---

## Input Format: Claude Code hooks.json

### Schema

A `hooks.json` file has this structure:

```json
{
  "description": "Human-readable description of what these hooks do",
  "hooks": {
    "<EventType>": [
      {
        "matcher": "<ToolPattern>",
        "hooks": [
          {
            "type": "command",
            "command": "<ShellCommand>",
            "timeout": <seconds>
          }
        ]
      }
    ]
  }
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `description` | string | No | Top-level description of the hook configuration's purpose |
| `hooks` | object | Yes | Map of event type keys to arrays of hook entries |
| `hooks.<EventType>` | array | Yes | Array of hook entry objects for this event type |
| `hooks.<EventType>[].matcher` | string | No | Pipe-delimited tool name pattern (e.g., `Write\|Edit\|Bash`). Only applicable to `PreToolUse` and `PostToolUse` events. If omitted, the hook fires for all tool invocations of that event type. |
| `hooks.<EventType>[].hooks` | array | Yes | Array of hook action objects to execute when the event fires |
| `hooks.<EventType>[].hooks[].type` | string | Yes | Hook action type. Currently only `command` is supported. |
| `hooks.<EventType>[].hooks[].command` | string | Yes | Shell command to execute. May contain `${CLAUDE_PLUGIN_ROOT}` for path resolution. |
| `hooks.<EventType>[].hooks[].timeout` | number | No | Maximum execution time in seconds. Default varies by event type. |

### Event Types

| Event Type | When It Fires | Matcher Support | Typical Use Cases |
|------------|---------------|-----------------|-------------------|
| `PreToolUse` | Before a tool is executed | Yes (tool name pattern) | Auto-approve operations, validate inputs, enforce policies |
| `PostToolUse` | After a tool completes | Yes (tool name pattern) | Log results, trigger follow-up actions, update state |
| `Stop` | When the session ends | No | Cleanup, save state, generate reports |
| `SessionStart` | When a new session begins | No | Initialize environment, load context, set up directories |
| `Notification` | System notification events | No | Alert on events, trigger external integrations |

### Hook Input/Output Protocol

Hooks receive JSON on stdin with context about the triggering event:

```json
{
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/file.txt",
    "content": "..."
  }
}
```

For `PreToolUse` hooks, the script can influence behavior by outputting JSON to stdout:

```json
{
  "hookSpecificOutput": {
    "permissionDecision": "allow",
    "permissionDecisionReason": "Auto-approved: session file operation"
  }
}
```

Permission decision values:
- `"allow"` -- Approve the tool invocation without user prompt
- `"deny"` -- Block the tool invocation
- No output (empty stdout) -- No opinion; fall through to normal permission flow

For all other event types, stdout output is informational only.

### Matcher Pattern Syntax

Matchers use pipe-delimited (`|`) tool name patterns:

| Pattern | Matches |
|---------|---------|
| `Write` | Only the Write tool |
| `Write\|Edit` | Write or Edit tools |
| `Write\|Edit\|Bash` | Write, Edit, or Bash tools |
| (omitted) | All tools for that event type |

Matchers are case-sensitive and must match Claude Code tool names exactly.

---

## Conversion Algorithm

### Step 1: Parse the hooks.json File

1. Read the `hooks.json` file from the source plugin group's `hooks/` directory
2. Parse the JSON structure
3. Extract the top-level `description` for use in migration guide documentation
4. Iterate over each key in the `hooks` object to get event types and their hook arrays

```
For each event_type in hooks.hooks:
  For each hook_entry in hooks.hooks[event_type]:
    Extract: matcher (optional), hooks array
    For each hook_action in hook_entry.hooks:
      Extract: type, command, timeout
      Store as a HookDefinition:
        {
          event_type: string,
          matcher: string | null,
          action_type: string,
          command: string,
          timeout: number | null,
          source_description: string
        }
```

### Step 2: Classify Hook Behavior

For each `HookDefinition`, analyze the command to determine its behavioral category. This classification guides workaround selection for platforms without hook support.

| Category | Detection Heuristic | Description |
|----------|-------------------|-------------|
| `auto-approve` | Command outputs `permissionDecision` JSON | Script auto-approves certain tool operations based on path or context patterns |
| `validation` | Command exits non-zero on invalid input | Script validates tool inputs before execution |
| `logging` | Command writes to a log file or stdout | Script logs tool activity for auditing |
| `state-management` | Command reads/writes state files | Script manages persistent state across tool invocations |
| `cleanup` | Used with `Stop` event | Script performs cleanup when session ends |
| `initialization` | Used with `SessionStart` event | Script sets up environment when session starts |
| `notification` | Used with `Notification` event | Script triggers external alerts or integrations |
| `general` | None of the above match | Generic hook with custom behavior |

Classification is determined by:
1. Inspecting the shell script contents (read the file referenced in the `command` field)
2. Checking the event type (`Stop` implies cleanup, `SessionStart` implies initialization)
3. Looking for output patterns (JSON with `permissionDecision` implies auto-approve)

### Step 3: Map Event Types to Target Platform

Look up each event type in the adapter's Hook/Lifecycle Event Mappings section:

```
For each HookDefinition:
  target_event = adapter.hook_mappings[definition.event_type]

  If target_event is a valid event name:
    -> Proceed to Step 4 (convert the hook)

  If target_event is null:
    -> Mark as conversion gap
    -> Proceed to Step 5 (find workarounds)

  If adapter has no Hook/Lifecycle Event Mappings section:
    -> Treat ALL events as null (no hook support)
    -> Proceed to Step 5 for every hook
```

### Step 4: Convert Supported Hooks

When the target platform has a matching event type, convert the hook:

1. **Map the event type**: Replace the Claude Code event name with the target platform's event name
2. **Transform the matcher**: Convert the pipe-delimited tool name pattern using the adapter's Tool Name Mappings:
   - For each tool name in the matcher pattern, look up the target equivalent
   - If a tool maps to `null`, remove it from the matcher
   - If all tools in the matcher map to `null`, the entire hook entry becomes a gap
   - Rebuild the matcher in the target platform's pattern syntax
3. **Transform the command path**: See Step 4a below
4. **Adjust the timeout**: Keep the timeout value unless the target platform has different timeout semantics (documented in the adapter)
5. **Format the output**: Write the hook in the target platform's hook configuration format (from the adapter's Hook Configuration subsection)

#### Step 4a: Command Path Transformation

Hook commands often reference scripts via `${CLAUDE_PLUGIN_ROOT}`:

```
bash ${CLAUDE_PLUGIN_ROOT}/hooks/auto-approve-session.sh
```

Transform these paths using the adapter's Path Resolution and Directory Structure:

1. Replace `${CLAUDE_PLUGIN_ROOT}` with the target platform's root variable or resolution strategy
2. Map the `hooks/` directory to the target platform's `hook_dir` (from Directory Structure)
3. If the target platform has no path variable (`root_variable: null`), use relative paths from the plugin root
4. Copy the referenced script file to the target output directory, adjusting internal paths as needed

For scripts that reference Claude Code-specific constructs (tool names in JSON parsing, `${CLAUDE_PLUGIN_ROOT}` in path checks):
- Replace Claude Code tool names with target equivalents where they appear in the script
- Replace `${CLAUDE_PLUGIN_ROOT}` with the target path resolution
- Document any script modifications in the migration guide

### Step 5: Handle Unsupported Hooks (Workarounds)

When the target platform has no equivalent for a hook event, generate workarounds based on the hook's behavioral category:

#### Auto-Approve Hooks

| Platform Capability | Workaround | Fidelity |
|---------------------|-----------|----------|
| Has a permission/approval system | Document the paths and conditions that were auto-approved; instruct user to configure the target's permission system to replicate the behavior | Medium |
| Has a config file for permissions | Generate the target platform's permission config entries that approximate the auto-approve behavior | High |
| No permission system | Document the auto-approve behavior as a workflow change: users will need to manually approve these operations | Low |

**Example workaround for OpenCode**: OpenCode's permission system supports allow/deny/allow-for-session per tool invocation. While it cannot auto-approve based on file path patterns, users can manually allow-for-session on first prompt. Document this in the migration guide:

```markdown
### Auto-Approve Hook Workaround

**Source**: PreToolUse hook with `Write|Edit|Bash` matcher
**Purpose**: Auto-approves file operations in session directories

**OpenCode equivalent**: Use OpenCode's built-in permission system:
1. When prompted for Write/Edit/Bash operations on session files, select "Allow for session"
2. This must be done manually on first encounter each session
3. No path-based auto-approval is possible

**Impact**: Minor friction increase; user must manually approve on first occurrence per session
```

#### Validation Hooks

| Platform Capability | Workaround | Fidelity |
|---------------------|-----------|----------|
| Has pre-execution hooks | Convert directly to target hook format | High |
| Has a linter/formatter integration | Configure the target's linter to catch the same issues | Medium |
| No validation mechanism | Add validation instructions to the converted skill's prompt body | Low |

#### Logging Hooks

| Platform Capability | Workaround | Fidelity |
|---------------------|-----------|----------|
| Has post-execution hooks | Convert logging logic to target hook format | High |
| Has built-in audit logging | Document how to enable the target's native logging | Medium |
| No logging mechanism | Omit; document as informational gap (logging is typically non-critical for functionality) | Low |

#### State Management Hooks

| Platform Capability | Workaround | Fidelity |
|---------------------|-----------|----------|
| Has lifecycle hooks | Convert state read/write to target hook format | High |
| Has config/context file loading | Move state initialization into loaded context files | Medium |
| No state mechanism | Inline state management instructions into the converted skill prompts | Low |

#### Cleanup / Initialization / Notification Hooks

| Platform Capability | Workaround | Fidelity |
|---------------------|-----------|----------|
| Has corresponding lifecycle event | Convert directly | High |
| Has context file loading (for initialization) | Use context file to replicate session-start behavior | Medium |
| No lifecycle events | Document as gap; suggest manual pre/post-session scripts the user can run outside the AI tool | Low |

### Step 6: Generate Conversion Output

For each hook configuration, produce:

1. **Converted hook file** (if the target supports hooks):
   - Written in the target platform's hook configuration format
   - Placed in the target platform's `hook_dir`
   - Contains only the hooks that had successful mappings

2. **Script files** (if hooks were converted):
   - Copy and transform referenced shell scripts
   - Place in the target platform's expected location
   - Adjust internal paths and tool name references

3. **Gap report entries** (for every unconverted hook):
   - Source hook description (event type, matcher, command purpose)
   - Reason it could not be converted
   - Behavioral category
   - Suggested workaround (from Step 5)
   - Severity classification

4. **Migration guide entries** (for all hooks):
   - What was converted and how
   - What was not converted and why
   - Manual steps the user needs to take
   - Behavioral differences between source and target

---

## Gap Report Severity Classification

When a hook cannot be converted, classify its severity based on impact:

| Severity | Criteria | Examples |
|----------|----------|----------|
| **Critical** | Hook prevents data loss or enforces security constraints | Validation hooks that block dangerous operations |
| **Functional** | Hook enables core workflow automation | Auto-approve hooks that enable autonomous execution |
| **Cosmetic** | Hook provides convenience or informational value | Logging hooks, notification hooks |

### Severity Decision Tree

```
Is the hook a security/safety gate?
  Yes -> Critical
  No -> Does the hook enable autonomous workflow execution?
    Yes -> Functional
    No -> Does the hook affect correctness of output?
      Yes -> Functional
      No -> Cosmetic
```

---

## Fidelity Scoring for Hook Conversion

Calculate a fidelity score for the hook component using these weights:

| Factor | Weight | Scoring |
|--------|--------|---------|
| Event type mapping | 40% | 100% if mapped, 0% if gap |
| Matcher transformation | 20% | 100% if all tools mapped, proportional if partial, 0% if all null |
| Command/script portability | 25% | 100% if script runs as-is, 50% if modified, 0% if not portable |
| Behavioral equivalence | 15% | 100% if identical behavior, 50% if workaround achieves partial parity, 0% if no equivalent |

### Formula

```
hook_fidelity = (
  (event_mapped ? 1.0 : 0.0) * 0.40 +
  (matched_tools / total_tools) * 0.20 +
  (script_portability_score) * 0.25 +
  (behavioral_equivalence_score) * 0.15
) * 100
```

### Component-Level Score

When a `hooks.json` has multiple hook entries, the component-level fidelity score is the weighted average of individual hook fidelity scores, weighted by severity:

| Severity | Weight Multiplier |
|----------|------------------|
| Critical | 3x |
| Functional | 2x |
| Cosmetic | 1x |

---

## Platform-Specific Handling

### Platforms with Full Hook Support

If the adapter's Hook/Lifecycle Event Mappings section maps all (or most) Claude Code events to target equivalents:

1. Convert each hook entry using Steps 1-4
2. Transform scripts and place in the correct directory
3. Note any behavioral differences in the migration guide
4. Score fidelity based on mapping completeness

### Platforms with Partial Hook Support

If the adapter maps some events but not others:

1. Convert supported events using Steps 1-4
2. Apply workarounds for unsupported events using Step 5
3. Clearly separate "converted" from "workaround" entries in the migration guide
4. Score fidelity as a blend of converted and gap scores

### Platforms with No Hook Support

If the adapter's Hook/Lifecycle Event Mappings section is omitted, or all events map to `null`:

1. Skip hook file generation entirely (no hook config file to write)
2. For each hook in the source:
   a. Classify its behavior (Step 2)
   b. Generate the best available workaround (Step 5)
   c. Create a detailed gap report entry
   d. Create a migration guide entry explaining the workaround
3. Check for partial alternatives on the target platform:
   - Permission systems that can approximate auto-approve behavior
   - Context file loading that can approximate session-start hooks
   - Built-in logging that can approximate post-tool logging
4. Set the component fidelity score to reflect gap severity:
   - All cosmetic gaps: 30% (basic awareness documented)
   - Mix of functional and cosmetic: 15% (workarounds available but limited)
   - Any critical gaps: 5% (significant capability loss)
5. Include a summary block at the top of the gap report's hook section:

```markdown
### Hooks: Not Supported on {Target Platform}

{Target Platform} does not have a hook/lifecycle event system. The following
hooks from the source plugin could not be converted. Workarounds are provided
where the target platform offers partial alternatives.

**Impact**: {summary of what is lost}
**Overall hook fidelity**: {score}%
```

---

## Conversion Examples

### Example 1: Auto-Approve Hook (No Target Support)

**Source** (`claude/sdd-tools/hooks/hooks.json`):
```json
{
  "description": "Auto-approve file operations for execute-tasks session management",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/auto-approve-session.sh",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

**Conversion for OpenCode (no hook support)**:

- Event type `PreToolUse` maps to `null` in OpenCode adapter
- Behavioral category: `auto-approve` (script outputs `permissionDecision` JSON)
- Severity: **Functional** (enables autonomous workflow execution)

**Gap report entry**:
```markdown
#### PreToolUse: Auto-Approve Session Files

- **Source**: `claude/sdd-tools/hooks/hooks.json`
- **Matcher**: Write|Edit|Bash
- **Purpose**: Automatically approves file operations targeting `.claude/sessions/` directories, enabling autonomous task execution without manual permission prompts
- **Severity**: Functional
- **Why not converted**: OpenCode has no hook/lifecycle event system
- **Workaround**: When OpenCode prompts for permission on Write/Edit/Bash operations targeting session files, select "Allow for session" to grant permission for the remainder of the session. This must be done manually each session. Alternatively, configure OpenCode's permission settings to reduce friction.
- **Impact**: Users will see permission prompts for session file operations that were previously auto-approved. Autonomous multi-task execution workflows will require manual intervention at permission boundaries.
```

### Example 2: Hook with Supported Target Events

**Source** (hypothetical target platform with partial hook support):
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/validate-paths.sh",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

**Conversion** (target platform with `before_tool` event):

1. Map `PreToolUse` to `before_tool`
2. Transform matcher: `Write|Edit` becomes target's tool filter syntax with mapped tool names
3. Transform command path: Replace `${CLAUDE_PLUGIN_ROOT}/hooks/` with target path
4. Copy and adapt the script file
5. Write target hook config:

```yaml
# Target platform hook config (hypothetical YAML format)
hooks:
  before_tool:
    - tools: ["write", "edit"]
      command: ".plugins/hooks/validate-paths.sh"
      timeout: 10
```

---

## Integration with Conversion Engine

The hook converter is invoked during Phase 5 (Interactive Conversion) of the porter skill when processing a component of type `hooks`. It follows this integration flow:

1. **Input**: The conversion engine passes the hook component's source path and the loaded adapter
2. **Processing**: The converter runs Steps 1-6, producing converted files, gap entries, and migration guide entries
3. **Interactive resolution**: When the converter encounters gaps classified as `Functional` or `Critical`, it pauses and presents workaround options to the user via `AskUserQuestion`:

```yaml
AskUserQuestion:
  questions:
    - header: "Hook Conversion Gap"
      question: "The PreToolUse auto-approve hook has no equivalent on {target}. How should this be handled?"
      options:
        - label: "Use suggested workaround"
          description: "Document the permission system workaround in the migration guide"
        - label: "Omit entirely"
          description: "Remove this hook from the conversion; document in gap report only"
        - label: "Add as TODO"
          description: "Leave a TODO comment in the output for manual implementation"
      multiSelect: false
```

4. **Output**: The converter returns:
   - `converted_files`: Array of file paths written (hook config + scripts), or empty if no target support
   - `gap_entries`: Array of gap report entries for unconverted hooks
   - `migration_entries`: Array of migration guide entries for all hooks (converted and unconverted)
   - `fidelity_score`: Component-level fidelity score (0-100%)
   - `decisions`: Array of user decisions made during interactive resolution
