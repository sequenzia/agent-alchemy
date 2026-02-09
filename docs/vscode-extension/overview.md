<!-- docs/vscode-extension/overview.md -->
# VS Code Extension

The `claude-code-schemas` extension (v0.2.0) provides real-time schema validation, autocomplete, and hover documentation for Claude Code plugin files. It is a development-time tool that catches frontmatter errors as you write skills and agents.

## What It Does

The extension targets two categories of plugin files:

### YAML Frontmatter Validation (Markdown)

For skill (`SKILL.md`) and agent (`.md` under `agents/`) files, the extension:

- **Diagnostics** -- Validates YAML frontmatter against JSON schemas using [Ajv](https://ajv.js.org/). Errors appear inline as you type (debounced at 300ms) and immediately on save.
- **Completions** -- Autocompletes frontmatter keys, enum values, and boolean fields with snippet support. Already-present keys are excluded from suggestions.
- **Hover info** -- Shows type, description, allowed values, defaults, and patterns for any frontmatter key on hover.

### JSON Schema Validation

For JSON configuration files, the extension contributes schemas via VS Code's built-in JSON validation:

| File Pattern | Schema | Purpose |
|-------------|--------|---------|
| `.claude-plugin/plugin.json` | `plugin.schema.json` | Plugin manifest |
| `hooks/hooks.json` | `hooks.schema.json` | Hook configuration |
| `.mcp.json` | `mcp.schema.json` | MCP server configuration |
| `.lsp.json` | `lsp.schema.json` | LSP configuration |
| `marketplace.json` | `marketplace.schema.json` | Plugin marketplace registry |

## Architecture

```
extensions/vscode/
├── src/
│   ├── extension.ts              # Entry point — registers providers and diagnostics
│   ├── types.ts                  # Shared type definitions
│   └── frontmatter/
│       ├── validator.ts          # Ajv-based frontmatter validation
│       ├── completions.ts        # CompletionItemProvider for keys and enums
│       ├── hover.ts              # HoverProvider with type and description info
│       └── utils.ts              # Frontmatter extraction, file kind detection
├── schemas/                      # JSON Schema definitions
│   ├── skill-frontmatter.schema.json
│   ├── agent-frontmatter.schema.json
│   ├── plugin.schema.json
│   ├── hooks.schema.json
│   ├── mcp.schema.json
│   ├── lsp.schema.json
│   └── marketplace.schema.json
├── package.json                  # Extension manifest (publisher: claude-alchemy)
├── tsconfig.json
└── esbuild.mjs                   # Build configuration
```

### File Detection

The extension determines which schema to apply based on file location:

- **Skill files** -- Any file named `SKILL.md` under a `skills/` directory
- **Agent files** -- Any `.md` file (except `SKILL.md`) under an `agents/` directory
- **Other markdown** -- Ignored (no diagnostics applied)

### Activation

The extension activates when:

- A workspace contains a `.claude-plugin/plugin.json` file, or
- Any markdown file is opened

## Setup

```bash
cd extensions/vscode
npm install
```

!!! warning "Separate Package Manager"
    The VS Code extension uses **npm**, not pnpm. It is a standalone project and is **not** part of the pnpm workspace.

### Build

```bash
cd extensions/vscode
npm run build
```

This runs esbuild to bundle the extension into `dist/extension.js`.

### Package

```bash
cd extensions/vscode
npm run package
```

This creates a `.vsix` file that can be installed in VS Code via **Extensions > Install from VSIX**.

### Development

| Script | Command | Purpose |
|--------|---------|---------|
| `build` | `node esbuild.mjs` | One-time production build |
| `watch` | `node esbuild.mjs --watch` | Rebuild on file changes |
| `package` | `vsce package --no-dependencies` | Create `.vsix` installer |
| `lint` | `tsc --noEmit` | Type-check without emitting |

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `ajv` | ^8.17.0 | JSON Schema validation for frontmatter |
| `js-yaml` | ^4.1.0 | YAML parsing for frontmatter extraction |

The extension requires VS Code 1.85.0 or later.
