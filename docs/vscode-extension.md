# VS Code Extension

**Version:** 0.1.1 | **Publisher:** agent-alchemy

The Claude Code Plugin Schemas extension provides schema validation, YAML frontmatter autocomplete, and hover documentation for Claude Code plugin development.

## Features

### YAML Frontmatter Validation

Real-time validation of YAML frontmatter in skill (`SKILL.md`) and agent (`.md`) files using [Ajv](https://ajv.js.org/) compiled schemas. Catches invalid fields, wrong types, and missing required properties as you type.

**Validated frontmatter fields for skills:**

- `name`, `description`, `argument-hint`
- `user-invocable`, `disable-model-invocation`
- `model`, `allowed-tools`

**Validated frontmatter fields for agents:**

- `name`, `description`, `model`
- `tools`, `skills`

### JSON Schema Validation

Native VS Code JSON schema validation for 5 configuration file types:

| File | Schema | Purpose |
|------|--------|---------|
| `.claude-plugin/plugin.json` | `plugin.schema.json` | Plugin manifest structure |
| `hooks/hooks.json` | `hooks.schema.json` | Lifecycle hook configuration |
| `.mcp.json` | `mcp.schema.json` | MCP server configuration |
| `.lsp.json` | `lsp.schema.json` | LSP server configuration |
| `marketplace.json` | `marketplace.schema.json` | Plugin marketplace registry |

### Autocomplete and Hover

- **Autocomplete** — Suggests valid frontmatter fields and enum values as you type
- **Hover documentation** — Shows field descriptions and allowed values on hover

## Installation

### From Source

```bash
cd extensions/vscode
npm install
npm run build
npm run package    # Creates .vsix file
```

Then install the `.vsix` file via VS Code: Extensions > "..." menu > "Install from VSIX..."

### Activation

The extension auto-activates when it detects:

- A workspace containing `.claude-plugin/plugin.json`
- Any open Markdown file

## Architecture

```
extensions/vscode/
├── src/
│   ├── extension.ts           # Entry point, registers providers
│   ├── frontmatter/
│   │   ├── validator.ts       # Ajv-based YAML validation
│   │   ├── completionProvider.ts  # Autocomplete suggestions
│   │   └── hoverProvider.ts   # Hover documentation
│   └── utils/
│       └── fileDetection.ts   # Path-based file type detection
├── schemas/                   # 7 JSON schemas
│   ├── skill-frontmatter.schema.json
│   ├── agent-frontmatter.schema.json
│   ├── plugin.schema.json
│   ├── hooks.schema.json
│   ├── mcp.schema.json
│   ├── lsp.schema.json
│   └── marketplace.schema.json
└── package.json               # Extension manifest
```

**Key implementation details:**

- **Ajv compilation** — Schemas are compiled once at activation for fast validation
- **Path-based detection** — Files are classified by their directory path (`skills/` → skill, `agents/` → agent)
- **Line-number mapping** — Validation errors are mapped back to YAML source lines for accurate diagnostics
- **esbuild bundling** — Single-file output for fast extension loading

!!! warning "Known Limitation"
    The extension currently has zero test coverage. The Ajv compilation, path detection, and line-number mapping logic are untested. This is flagged as a high-severity known challenge.

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Runtime | VS Code Extension API (^1.85.0) |
| Validation | Ajv (JSON Schema validator) |
| YAML Parsing | js-yaml |
| Bundler | esbuild |
| Language | TypeScript (strict mode) |
