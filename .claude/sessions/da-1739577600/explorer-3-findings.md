## Explorer 3: VS Code Extension & Developer Infrastructure

### Key Findings

**VS Code Extension Capabilities:**
- 3 core features: YAML frontmatter validation (Ajv-based), autocomplete, hover documentation
- Validates 2 file types with custom logic: SKILL.md and agent .md files
- Validates 5 file types with native VS Code JSON schemas: plugin.json, hooks.json, .mcp.json, .lsp.json, marketplace.json
- Auto-activates on workspaces containing .claude-plugin/plugin.json
- Built with esbuild, TypeScript strict mode, 2 production dependencies (Ajv, js-yaml)

**JSON Schema System (7 schemas in extensions/vscode/schemas/):**
- skill-frontmatter.schema.json (125 lines) — skill YAML contract
- agent-frontmatter.schema.json (110 lines) — agent YAML contract
- plugin.schema.json (168 lines) — plugin manifest contract
- hooks.schema.json, mcp.schema.json, lsp.schema.json, marketplace.schema.json — config file contracts
- All schemas include source URLs and validation dates in $comment fields
- Use $defs for reusable components (e.g., matcherGroupArray for hooks)

**Integration with Plugin System:**
- Schemas define the contracts that markdown-as-code plugins must follow
- Path-based file detection (skills/, agents/ directories)
- Real-time validation guides plugin authoring
- Extension provides IDE-like experience for markdown plugin development

**Key Pattern:** Schema-driven authoring — JSON schemas are source of truth for plugin API contracts, enabling progressive disclosure through autocomplete/hover

**Developer Infrastructure:**
- scripts/deploy-docs.sh: MkDocs deployment to gh-pages (14 lines)
- internal/docs/: 4 markdown docs (project description, task cheatsheet, codebase analysis, sdd-tools workflow)
- specs/: tdd-features-SPEC.md (specification in progress)

### Challenges Identified
1. Zero test coverage for VS Code extension
2. Manual schema updates — potential schema drift from actual plugin conventions
3. Extension only works when .claude-plugin/plugin.json exists in workspace
