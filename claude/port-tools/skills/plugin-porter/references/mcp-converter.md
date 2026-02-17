# MCP Config Converter

Reference for converting Claude Code MCP server configurations (`.mcp.json` files) to target platform equivalents. The MCP config converter handles JSON parsing, server type mapping, command and argument transformation, environment variable conversion, `${CLAUDE_PLUGIN_ROOT}` path resolution, MCP tool reference renaming, and graceful degradation for platforms with no MCP support.

---

## Overview

Claude Code plugins can include `.mcp.json` files that define Model Context Protocol server configurations. Each configuration maps server names to server definitions specifying transport type, startup commands, arguments, environment variables, and optional authentication settings. MCP servers provide additional tools to the AI agent at runtime (e.g., `context7` for documentation lookup).

During porting, the converter must determine whether the target platform supports MCP natively. If it does, the configuration is transformed to the target's MCP config format with adjusted naming conventions and paths. If it does not, the entire MCP configuration is flagged as a conversion gap with clear explanations and alternative suggestions.

---

## Input Format: Claude Code .mcp.json

### Schema

A `.mcp.json` file has this structure:

```json
{
  "mcpServers": {
    "<serverName>": {
      "command": "<executable>",
      "args": ["<arg1>", "<arg2>"],
      "env": {
        "<VAR_NAME>": "<value>"
      },
      "cwd": "<working_directory>",
      "type": "<transport_type>",
      "url": "<server_url>",
      "headers": {
        "<Header-Name>": "<value>"
      },
      "oauth": {
        "clientId": "<client_id>",
        "callbackPort": <port>
      }
    }
  }
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mcpServers` | object | Yes | Map of server names to server configuration objects |
| `mcpServers.<name>.command` | string | No | Command to start the MCP server (for stdio transport). May contain `${CLAUDE_PLUGIN_ROOT}` for path resolution. |
| `mcpServers.<name>.args` | array | No | Arguments to pass to the server command. May contain `${CLAUDE_PLUGIN_ROOT}` in path arguments. |
| `mcpServers.<name>.env` | object | No | Environment variables to set for the server process. Values may contain `${CLAUDE_PLUGIN_ROOT}` for path resolution. |
| `mcpServers.<name>.cwd` | string | No | Working directory for the server process. May contain `${CLAUDE_PLUGIN_ROOT}`. |
| `mcpServers.<name>.type` | string | No | Transport type: `stdio`, `sse`, or `http`. Defaults to `stdio` if `command` is present, inferred from `url` otherwise. |
| `mcpServers.<name>.url` | string | No | URL for HTTP/SSE transport MCP servers. Required for `sse` and `http` types. |
| `mcpServers.<name>.headers` | object | No | HTTP headers to send with requests (for HTTP/SSE transport). |
| `mcpServers.<name>.oauth` | object | No | OAuth configuration for authenticated MCP servers. Contains `clientId` and optional `callbackPort`. |

### Transport Types

| Type | Key Fields | Description |
|------|-----------|-------------|
| `stdio` | `command`, `args`, `env`, `cwd` | Server runs as a local process; communication via stdin/stdout |
| `sse` | `url`, `headers`, `oauth` | Server-Sent Events over HTTP; client connects to a running server |
| `http` | `url`, `headers`, `oauth` | HTTP Streamable transport; client sends requests to a running server |

### MCP Tool Naming in Claude Code

Claude Code names MCP tools using a double-underscore convention:

```
mcp__{serverName}__{toolName}
```

For example, an MCP server named `context7` that exposes a tool named `query-docs` is referenced as:

```
mcp__context7__query-docs
```

These tool references appear in:
- Agent frontmatter `tools:` lists
- Skill `allowed-tools` lists
- Skill and agent body text (instructional references)

---

## Conversion Algorithm

### Step 1: Parse the .mcp.json File

1. Read the `.mcp.json` file from the source plugin group's root directory (`claude/{group}/.mcp.json`)
2. Parse the JSON structure
3. Validate that the `mcpServers` key exists and is a non-empty object
4. For each server entry, extract the server name and configuration fields

```
For each server_name in mcpServers:
  server_config = mcpServers[server_name]
  Determine transport_type:
    If server_config.type exists: use it
    Else if server_config.command exists: "stdio"
    Else if server_config.url exists: infer from url scheme ("sse" or "http")
    Else: "unknown"

  Detect runtime_dependency:
    If command starts with "npx" or "node": runtime = "node"
    If command starts with "python" or "python3" or "pip" or "uvx" or "uv": runtime = "python"
    If command starts with "go" or contains ".go": runtime = "go"
    If command starts with "cargo" or "rustc": runtime = "rust"
    Else: runtime = null

  Store as MCPServerDefinition:
    {
      name: string,
      transport_type: "stdio" | "sse" | "http" | "unknown",
      command: string | null,
      args: string[] | null,
      env: Record<string, string> | null,
      cwd: string | null,
      url: string | null,
      headers: Record<string, string> | null,
      oauth: { clientId: string, callbackPort?: number } | null,
      runtime_dependency: string | null,
      has_plugin_root_paths: boolean
    }
```

5. Set `has_plugin_root_paths = true` if `${CLAUDE_PLUGIN_ROOT}` appears in any of: `command`, `args` entries, `env` values, or `cwd`

### Step 2: Determine Target MCP Support

Check the adapter and research findings for MCP support level:

```
MCP support detection:
  1. Check adapter Tool Name Mappings for "MCP Tools" subsection
     - If present with non-null generic pattern: mcp_supported = true
     - If present with null generic pattern: mcp_supported = false
     - If MCP Tools subsection is absent: mcp_supported = false

  2. Check research findings for MCP-related capabilities
     - Look for mentions of "MCP", "Model Context Protocol", or "mcpServers"
     - If research confirms MCP support: mcp_supported = true
     - If research explicitly denies MCP support: mcp_supported = false

  3. Determine MCP support level:
     If mcp_supported = true:
       Check for specific capabilities:
         - stdio transport support: boolean
         - sse transport support: boolean
         - http transport support: boolean
         - tool naming convention: string (e.g., "{mcpName}_{toolName}")
         - config location: string (e.g., ".opencode.json under mcpServers key")
         - config format: "json" | "yaml" | "toml" | other
       Set support_level = "native"
     Else:
       Set support_level = "none"
```

### Step 3: Route by Support Level

Based on the determined support level, route to the appropriate conversion path:

- **`support_level = "native"`**: Proceed to Step 4 (Convert for MCP-native platform)
- **`support_level = "none"`**: Proceed to Step 5 (Handle no MCP support)

---

## Step 4: Convert for MCP-Native Platform

When the target platform supports MCP natively, transform the configuration to the target's format.

### 4a: Transform Server Configurations

For each `MCPServerDefinition`:

1. **Map transport type**: Check which transports the target supports
   - If the server's transport is supported: proceed with conversion
   - If the server's transport is not supported: record as a gap with explanation (e.g., "Target platform supports stdio and SSE but not HTTP Streamable transport")

2. **Transform server name**: Apply the target platform's naming convention if it differs from Claude Code's. Most platforms use the same server name as-is.

3. **Transform command and args** (for stdio servers):
   - Replace any `${CLAUDE_PLUGIN_ROOT}` occurrences in the `command` field using the adapter's Path Resolution mappings:
     - If `MAPPINGS.path_resolution.root_variable` is a string: substitute the variable
     - If `MAPPINGS.path_resolution.root_variable` is `null`: convert to a relative path from the target platform's config location
   - Apply the same transformation to each entry in the `args` array
   - Keep the command executable name unchanged (e.g., `npx`, `node`, `python3`)

4. **Transform environment variables** (if `env` exists):
   - Replace `${CLAUDE_PLUGIN_ROOT}` in environment variable values using the same path resolution as above
   - Keep variable names unchanged (environment variable names are platform-agnostic)

5. **Transform cwd** (if present):
   - Apply path resolution to the `cwd` value
   - If `cwd` references `${CLAUDE_PLUGIN_ROOT}`, convert to the target's equivalent

6. **Transform URL** (for sse/http servers):
   - Keep the URL unchanged (MCP server URLs are external and platform-independent)
   - If the URL contains `${CLAUDE_PLUGIN_ROOT}` (unlikely but possible for local servers): apply path resolution

7. **Transform headers and OAuth** (if present):
   - Keep headers unchanged (HTTP headers are platform-independent)
   - Keep OAuth configuration unchanged (OAuth flows are standardized)

### 4b: Build Target MCP Configuration

Assemble the converted server configurations into the target platform's MCP config format:

1. **Determine config file location**: Use `MAPPINGS.directory_structure.config_dir` to find where MCP config belongs on the target platform
2. **Determine config format**: Check if MCP config is:
   - A standalone file (like Claude Code's `.mcp.json`)
   - Part of a larger config file (like OpenCode's `.opencode.json` with a `mcpServers` key)
   - A separate section in a YAML/TOML config

3. **Build the configuration object** with transformed server entries:

   For a standalone JSON config (similar to Claude Code):
   ```json
   {
     "mcpServers": {
       "<serverName>": {
         "command": "<transformed_command>",
         "args": ["<transformed_args>"],
         "env": { "<VAR>": "<transformed_value>" }
       }
     }
   }
   ```

   For an embedded config (e.g., inside a larger platform config file):
   ```json
   {
     "mcpServers": {
       "<serverName>": {
         "command": "<transformed_command>",
         "args": ["<transformed_args>"],
         "env": { "<VAR>": "<transformed_value>" }
       }
     }
   }
   ```

   The converter outputs the `mcpServers` block. The output phase (Phase 6) is responsible for embedding it into the target's config file if needed.

### 4c: Transform MCP Tool References

Scan all selected skill and agent files for MCP tool references and transform them to the target platform's naming convention.

1. **Identify MCP tool references**: Search for the pattern `mcp__{serverName}__{toolName}` in:
   - Skill `allowed-tools` lists
   - Agent `tools` lists
   - Skill and agent body text

2. **Apply target naming convention**: Use the adapter's MCP tool mapping pattern (from the Tool Name Mappings MCP Tools subsection):
   - Extract `serverName` and `toolName` from the Claude Code pattern
   - Apply the target's convention (e.g., `{mcpName}_{toolName}` for single-underscore platforms)
   - Replace each occurrence in the converted content

3. **Track transformations**: Record each tool reference rename in `CONVERSION_DECISIONS`:
   ```
   {
     component: "<skill or agent name>",
     feature: "MCP tool reference",
     decision_type: "direct",
     original: "mcp__context7__query-docs",
     converted: "context7_query-docs",
     rationale: "Applied target platform MCP tool naming convention"
   }
   ```

**Note**: MCP tool reference transformation in skill and agent bodies is also handled by the skill converter (Step 3c) and agent converter body transformation stages. The MCP converter coordinates by providing the tool name mapping table. Do not duplicate transformations -- if the skill/agent converters have already applied the rename using the adapter's Tool Name Mappings, the MCP converter should verify consistency rather than re-apply.

### 4d: Note Runtime Dependencies

For each server with a detected `runtime_dependency`:

1. **Record the dependency** in the migration guide:
   ```markdown
   ### MCP Server Runtime Dependencies

   The following MCP servers require specific runtimes to be installed on the target system:

   | Server | Runtime | Command | Notes |
   |--------|---------|---------|-------|
   | context7 | Node.js | npx -y @upstash/context7-mcp@latest | Requires Node.js and npm/npx in PATH |
   | custom-server | Python | python3 -m custom_mcp | Requires Python 3 and the custom_mcp package |
   ```

2. **Check for runtime availability** in the research findings:
   - If the target platform documentation mentions the runtime: note as "likely available"
   - If the research is silent on the runtime: note as "verify runtime availability on target system"

---

## Step 5: Handle No MCP Support

When the target platform does not support MCP, the entire MCP configuration becomes a conversion gap.

### 5a: Generate Gap Report Entries

For each `MCPServerDefinition`:

1. **Identify what the MCP server provides**: Determine the server's purpose from its name, command, and any known tool listings. Common MCP servers and their purposes:

   | Server Name Pattern | Likely Purpose | Alternative Suggestions |
   |---------------------|---------------|------------------------|
   | `context7` | Documentation lookup | Use the target platform's built-in web fetch or search tools to query documentation manually |
   | `filesystem` | Extended file operations | Most platforms have built-in file tools; document any gaps in specific file operations |
   | `github` | GitHub API access | Use the target platform's built-in web fetch or bash with `gh` CLI |
   | `postgres`, `sqlite`, `mysql` | Database access | Use bash tool with database CLI clients (`psql`, `sqlite3`, `mysql`) |
   | `puppeteer`, `playwright` | Browser automation | Use bash tool with headless browser CLI or suggest manual testing |
   | Custom / unknown | Varies | Flag for manual evaluation; suggest bash tool with the MCP server's underlying CLI if one exists |

2. **Create a gap entry** for each server:
   ```
   {
     component: "mcp:{group}",
     feature: "MCP server: {serverName}",
     reason: "{TARGET_PLATFORM} does not support the Model Context Protocol. MCP servers cannot be configured.",
     severity: "functional",
     workaround: "{alternative suggestion from the table above}"
   }
   ```

3. **Create a gap entry for MCP tool references** found in selected skills/agents:
   ```
   {
     component: "mcp:{group}",
     feature: "MCP tool references in skills/agents",
     reason: "Skills and agents reference MCP tools (e.g., mcp__context7__query-docs) that will not be available on {TARGET_PLATFORM}",
     severity: "functional",
     workaround: "Replace MCP tool invocations in converted skill/agent prompts with instructions to use alternative tools (e.g., web fetch, bash with CLI tools)"
   }
   ```

### 5b: Generate Migration Guide Entries

Create a migration guide section documenting the MCP gap:

```markdown
### MCP Configuration: Not Supported on {Target Platform}

{Target Platform} does not support the Model Context Protocol. The following MCP servers
from the source plugin could not be converted.

**Impact**: MCP tools provided by these servers will not be available. Skills and agents
that reference MCP tools will need manual adjustment to use alternative approaches.

| Server | Purpose | Tools Provided | Alternative |
|--------|---------|---------------|-------------|
| {name} | {purpose} | {tool list or "unknown"} | {alternative} |

#### Affected Components

The following skills and agents reference MCP tools that are unavailable on {TARGET_PLATFORM}:

| Component | MCP Tool Reference | Usage Context |
|-----------|-------------------|---------------|
| {skill/agent name} | mcp__{server}__{tool} | {where it appears: allowed-tools, body text, etc.} |

#### Recommended Actions

1. Review each affected component and replace MCP tool references with alternative approaches
2. Install any necessary CLI tools on the target system (e.g., `gh` for GitHub operations)
3. Update prompt instructions to guide the AI toward using available built-in tools instead of MCP tools
```

### 5c: Transform Skill/Agent References

Even though MCP is not supported, the converter must still handle MCP tool references in converted skill and agent files:

1. For each `mcp__{serverName}__{toolName}` reference in skill `allowed-tools` lists:
   - Remove the MCP tool from the list
   - Add a TODO comment noting the removal

2. For each MCP tool reference in agent `tools` lists:
   - Remove the MCP tool from the list
   - Add a TODO comment noting the removal

3. For each MCP tool reference in skill/agent body text:
   - Replace with a TODO comment: `<!-- TODO [{TARGET_PLATFORM}]: MCP tool mcp__{server}__{tool} is not available. Alternative: {suggestion} -->`
   - Record in `CONVERSION_DECISIONS` with `decision_type: "omitted"`

---

## Error Handling

### Malformed .mcp.json

If the `.mcp.json` file cannot be parsed as valid JSON:

1. **Report the parse error** clearly:
   ```
   {
     component: "mcp:{group}",
     feature: "MCP configuration file",
     reason: "Failed to parse .mcp.json: {error_message}",
     severity: "functional",
     workaround: "Fix the JSON syntax error in the source file, then re-run the porter"
   }
   ```

2. **Skip MCP conversion** for this group and continue with other components
3. **Add to migration guide**: Document the parse failure and suggest manual review

### Missing mcpServers Key

If the JSON parses successfully but has no `mcpServers` key or it is empty:

1. Log a warning: "MCP config file exists but contains no server definitions"
2. Skip conversion for this component
3. Set fidelity to 100% (nothing to convert means no loss)

### Unsupported Transport Type

If a server uses a transport type not recognized by the converter:

1. Record the server as a gap with the explanation
2. Include the raw server config in the gap report for manual review
3. Suggest checking the target platform's documentation for compatible transport options

### Servers That Cannot Be Ported

When a specific MCP server cannot be ported (regardless of platform MCP support):

1. **Document the reason** precisely:
   - Transport type not supported by target
   - Server requires `${CLAUDE_PLUGIN_ROOT}` paths and target has no path variable
   - Server requires OAuth and target's MCP implementation does not support OAuth
   - Server binary/package is platform-specific

2. **Record in gap report** with:
   - Server name and purpose
   - Specific reason it cannot be ported
   - The original server configuration (for manual reference)
   - Suggested alternative approach

---

## Fidelity Scoring for MCP Conversion

Calculate a fidelity score for the MCP component using these weights:

| Factor | Weight | Scoring |
|--------|--------|---------|
| Server config portability | 40% | 100% if all servers converted, proportional for partial, 0% if none |
| Transport type mapping | 20% | 100% if all transports supported, 0% if unsupported |
| Path resolution | 15% | 100% if no `${CLAUDE_PLUGIN_ROOT}` paths or all resolved, 50% if partial resolution, 0% if unresolvable |
| Tool reference mapping | 15% | 100% if all MCP tool references mapped, proportional for partial, 0% if none |
| Runtime dependency clarity | 10% | 100% if all runtimes documented, 50% if some unclear |

### Formula

```
mcp_fidelity = (
  (converted_servers / total_servers) * 0.40 +
  (supported_transports / total_transports) * 0.20 +
  (path_resolution_score) * 0.15 +
  (mapped_tool_refs / total_tool_refs) * 0.15 +
  (runtime_clarity_score) * 0.10
) * 100
```

### Special Cases

- **No MCP support on target**: If `support_level = "none"`, the component fidelity score is determined by the severity of the gap:
  - All MCP tools have viable alternatives (bash, fetch, etc.): 20%
  - Some MCP tools have alternatives, some do not: 10%
  - No alternatives available: 5%

- **MCP supported, all servers portable**: Score 100% (minus any path resolution or runtime issues)

- **Empty .mcp.json** (no servers): Score 100% (nothing to lose)

---

## Platform-Specific Handling

### Platforms with Native MCP Support

If the target platform supports MCP natively (like OpenCode):

1. Transform the `.mcp.json` server configurations using Step 4
2. Adjust tool naming convention using the adapter's MCP tool mapping
3. Place the config in the target's expected location
4. Note any transport type differences
5. Document runtime dependencies

### Platforms with Partial MCP Support

If the target supports MCP but only for certain transports or with limitations:

1. Convert supported servers using Step 4
2. Flag unsupported servers as gaps
3. Document the partial support clearly in the migration guide
4. Score fidelity based on the proportion of successfully converted servers

### Platforms with No MCP Support

If the target has no MCP support at all:

1. Skip MCP config file generation entirely
2. Generate comprehensive gap report entries (Step 5a)
3. Generate migration guide entries with alternatives (Step 5b)
4. Transform MCP tool references in skills/agents to TODO comments (Step 5c)
5. Set component fidelity to reflect gap severity

---

## Conversion Examples

### Example 1: stdio Server to MCP-Native Platform

**Source** (`claude/sdd-tools/.mcp.json`):
```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    }
  }
}
```

**Conversion for OpenCode (MCP supported)**:

1. Server `context7`: stdio transport, command `npx`, no `${CLAUDE_PLUGIN_ROOT}` paths
2. OpenCode stores MCP config in `.opencode.json` under `mcpServers` key
3. Transport type `stdio` is supported
4. Tool naming convention changes from `mcp__context7__query-docs` to `context7_query-docs`
5. Runtime dependency: Node.js (for `npx`)

**Target config** (embedded in `.opencode.json`):
```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    }
  }
}
```

**Tool reference transformations**:

| Source Reference | Target Reference |
|-----------------|-----------------|
| `mcp__context7__resolve-library-id` | `context7_resolve-library-id` |
| `mcp__context7__query-docs` | `context7_query-docs` |

### Example 2: Server with ${CLAUDE_PLUGIN_ROOT} Paths

**Source** (hypothetical):
```json
{
  "mcpServers": {
    "custom-tools": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/mcp-servers/custom-tools/index.js"],
      "env": {
        "CONFIG_PATH": "${CLAUDE_PLUGIN_ROOT}/mcp-servers/custom-tools/config.json"
      }
    }
  }
}
```

**Conversion for a platform with path variable `$PLUGIN_DIR`**:
```json
{
  "mcpServers": {
    "custom-tools": {
      "command": "node",
      "args": ["$PLUGIN_DIR/mcp-servers/custom-tools/index.js"],
      "env": {
        "CONFIG_PATH": "$PLUGIN_DIR/mcp-servers/custom-tools/config.json"
      }
    }
  }
}
```

**Conversion for OpenCode (no path variable)**:
```json
{
  "mcpServers": {
    "custom-tools": {
      "command": "node",
      "args": [".opencode/mcp-servers/custom-tools/index.js"],
      "env": {
        "CONFIG_PATH": ".opencode/mcp-servers/custom-tools/config.json"
      }
    }
  }
}
```

With a gap entry noting that the MCP server files must be manually placed in the correct directory.

### Example 3: MCP Config on Platform with No MCP Support

**Source** (`claude/sdd-tools/.mcp.json`):
```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    }
  }
}
```

**Conversion for a platform with no MCP support**:

- No config file generated
- Gap report entry:

```markdown
#### MCP Server: context7

- **Source**: `claude/sdd-tools/.mcp.json`
- **Purpose**: Documentation lookup via Context7 service (provides `resolve-library-id` and `query-docs` tools)
- **Runtime**: Node.js (npx)
- **Severity**: Functional
- **Why not converted**: {TARGET_PLATFORM} does not support the Model Context Protocol
- **Workaround**: Use the platform's built-in web fetch tool to query documentation APIs directly. If the platform has a search tool, use it to find relevant documentation pages. Alternatively, use bash with `curl` to call documentation APIs.
- **Affected components**:
  - `researcher` agent: references `mcp__context7__resolve-library-id` and `mcp__context7__query-docs` in tools list and body
```

### Example 4: SSE Transport Server

**Source** (hypothetical):
```json
{
  "mcpServers": {
    "remote-db": {
      "type": "sse",
      "url": "https://mcp.example.com/db",
      "headers": {
        "Authorization": "Bearer ${DB_TOKEN}"
      }
    }
  }
}
```

**Conversion for MCP-native platform (SSE supported)**:
```json
{
  "mcpServers": {
    "remote-db": {
      "type": "sse",
      "url": "https://mcp.example.com/db",
      "headers": {
        "Authorization": "Bearer ${DB_TOKEN}"
      }
    }
  }
}
```

Note: URL and headers are platform-independent and pass through unchanged. The `${DB_TOKEN}` is an environment variable reference (not `${CLAUDE_PLUGIN_ROOT}`) and should not be transformed.

**Conversion for MCP-native platform (SSE not supported)**:

Gap entry noting that the server uses SSE transport which is not supported. Suggest checking if the MCP server also offers a stdio-based launcher as an alternative.

---

## Integration with Conversion Engine

The MCP config converter is invoked during Phase 5 (Interactive Conversion) of the porter skill when processing a component of type `mcp`. It follows this integration flow:

1. **Input**: The conversion engine passes the MCP component's source path (`claude/{group}/.mcp.json`) and the loaded `CONVERSION_KNOWLEDGE` (merged adapter + research)

2. **Processing**: The converter runs Steps 1-5, producing:
   - Converted MCP config (or nothing if target lacks MCP support)
   - Tool reference mapping table (for use by skill and agent converters)
   - Gap entries for unconvertible servers
   - Migration guide entries

3. **Interactive resolution**: When the converter encounters servers that cannot be ported, it presents options to the user via `AskUserQuestion`:

   ```yaml
   AskUserQuestion:
     questions:
       - header: "MCP Server Conversion"
         question: "The MCP server '{serverName}' cannot be directly ported to {TARGET_PLATFORM}. {reason}"
         options:
           - label: "Use suggested alternative"
             description: "{alternative_suggestion}"
           - label: "Omit this server"
             description: "Remove from conversion; document in gap report"
           - label: "Add as TODO"
             description: "Leave a TODO comment for manual configuration"
         multiSelect: false
   ```

4. **Output**: The converter returns:
   - `converted_config`: The target platform's MCP configuration object (or `null` if no MCP support)
   - `config_target_path`: Where to write/embed the config on the target platform
   - `tool_name_mappings`: Map of Claude Code MCP tool names to target tool names (for skill/agent converters)
   - `gap_entries`: Array of gap report entries for unconverted servers or unsupported features
   - `migration_entries`: Array of migration guide entries for all MCP-related findings
   - `runtime_dependencies`: Array of runtime requirements for MCP servers
   - `fidelity_score`: Component-level fidelity score (0-100%)
   - `decisions`: Array of conversion decisions made during processing
