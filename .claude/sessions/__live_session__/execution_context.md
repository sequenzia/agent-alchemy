# Execution Context

## Project Patterns
- Plugin naming: `agent-alchemy-{group-name}` for marketplace, `{group-name}` for directory
- Reference files: H1 title, intro paragraph, horizontal rule, structured sections with tables/code/bullets
- Agent frontmatter: `name`, `description`, `model`, `tools`, `skills` in YAML + markdown system prompt
- Sonnet-tier for worker agents; Opus for synthesis/review/autonomous execution
- Cross-plugin composition via `${CLAUDE_PLUGIN_ROOT}/../{plugin-name}/skills/{skill}/SKILL.md`
- Skill YAML frontmatter: name, description, argument-hint, user-invocable, disable-model-invocation, allowed-tools
- Phase-based workflows with "CRITICAL: Complete ALL N phases" directive
- AskUserQuestion enforcement with NEVER/ALWAYS examples
- Settings in `.claude/agent-alchemy.local.md` with kebab-case keys
- Plugin groups can have `.claude-plugin/plugin.json` for standalone use even though marketplace.json is the central registry
- New plugin version pattern: start at 0.1.0
- Claude Code tools across all plugins: Read, Write, Edit, Glob, Grep, NotebookEdit, Bash, Task, TeamCreate, TeamDelete, TaskCreate, TaskUpdate, TaskList, TaskGet, SendMessage, AskUserQuestion, WebSearch, WebFetch, mcp__context7__resolve-library-id, mcp__context7__query-docs
- Hook events: PreToolUse (with matcher patterns), PostToolUse, Stop, SessionStart, Notification
- Hook config format: JSON with event type keys mapping to arrays of hook objects
- Agent frontmatter schema validates: name, description, model (enum: sonnet/opus/haiku/inherit), tools (string or array), skills (array), plus optional hooks, memory, mcpServers, permissionMode, maxTurns, disallowedTools
- Agent description should be 1-2 sentence summary; detailed usage in markdown body
- Adapter format defines 9 mapping sections for platform-specific translation
- OpenCode tools: glob, grep, ls, view, write, edit, patch, bash, fetch, sourcegraph, diagnostics, agent (lowercase names)
- OpenCode MCP convention: `{mcpName}_{toolName}` (single underscore vs Claude Code double underscore)
- OpenCode has no hooks, no per-command model overrides, no per-command tool restrictions, no composition mechanism
- OpenCode custom commands use `$NAME` placeholders for arguments (uppercase+numbers+underscores)
- Marketplace registry at `claude/.claude-plugin/marketplace.json` is source of truth for plugin group enumeration
- Component scanning: `claude/{group}/skills/*/SKILL.md` for skills, `claude/{group}/agents/*.md` for agents
- Adapter file lookup: `${CLAUDE_PLUGIN_ROOT}/skills/plugin-porter/references/adapters/{platform}.md`
- Porter skill has 7 phases (+Phase 4.5): Settings & Arguments, Plugin Selection Wizard, Dependency Validation, Platform Research, Dry-Run Preview (4.5), Interactive Conversion, Output & Reporting, Summary
- Conversion engine consumes CONVERSION_KNOWLEDGE (merged adapter + research), not raw ADAPTER directly
- Three tracking structures in Phase 5: CONVERTED_COMPONENTS, CONVERSION_DECISIONS, CONVERSION_GAPS
- Skill conversion is the most detailed sub-step (7 sub-steps: frontmatter, tool refs, composition, paths, AskUserQuestion, assembly)
- Agent conversion delegates to agent-converter.md reference (7-stage pipeline)
- Hook conversion delegates to hook-converter.md reference (event mapping, behavioral classification, workaround strategies)
- Reference file conversion delegates to reference-converter.md reference (4-stage: discovery, analysis, transformation, output)
- MCP conversion delegates to mcp-converter.md reference (server mapping, transport types, tool reference renaming)
- Incompatibility resolution delegates to incompatibility-resolver.md reference (detection, resolution, batch handling, decision tracking)
- Fidelity scoring uses 4 categories: direct (1.0), workaround (0.7), TODO (0.2), omitted (0.0) — unified across all component types
- Color bands: Green (80-100% High), Yellow (50-79% Moderate), Red (0-49% Low)
- FIDELITY_REPORT structure stores per-component breakdown; FIDELITY_COUNTERS tracked during Steps 3-7
- Agent fidelity weighted: frontmatter 25% + tools 25% + body 30% + skills 10% + gaps 10%
- Hook scripts protocol: read JSON stdin, output permissionDecision JSON stdout, exit 0 always
- `${CLAUDE_PLUGIN_ROOT}` used in hook commands for script path resolution
- Matcher patterns use pipe-delimited tool names (e.g., `Write|Edit|Bash`)
- Reference file deduplication important because deep-analysis references loaded by 4 skills across 3 plugin groups
- OpenCode: all hook events map to null (no hook system) — hook converter's "no hook support" path is primary flow for MVP
- OpenCode agents map to fixed types (coder/task) based on tool profile (write tools -> coder, read-only -> task)
- MCP tool naming: Claude Code `mcp__{serverName}__{toolName}` (double underscore), OpenCode `{mcpName}_{toolName}` (single underscore)
- .mcp.json schema supports: command, args, env, cwd, type (stdio/sse/http), url, headers, oauth
- Phase 3 dependency graph has 5 dependency types: skill-to-skill, cross-plugin, reference-include, hook-to-script, agent-to-skill
- DEPENDENCY_GRAPH structure includes: nodes, edges, circular_refs, conversion_order, external_deps, classification_counts
- CONVERSION_ORDER produced via topological sort with cycle-breaking (depth 10 cap)
- Incompatibility resolver has 5 categories: unmapped tool, unmapped frontmatter field, unsupported composition, unsupported hook event, general feature gap
- Batch resolution uses RESOLUTION_CACHE with group_key for cross-component decision reuse
- Workaround suggestions prioritize: adapter notes > research findings > pattern-based inference
- 4 confidence levels for workarounds: high, medium, low, uncertain
- Cascading impact detection uses Phase 3 dependency graph to warn about cross-component effects
- STALENESS_STATUS tracking structure for adapter version comparison, carried to migration guide
- Adapter file uses `target_platform_version` (not `platform_version`) in its Adapter Version section
- Dry-run preview uses same component type weights as fidelity scoring: skill=3, agent=2, hooks/reference/mcp=1
- Preview data structures (PREVIEW_FILE_TREE, PREVIEW_STATUS, PREVIEW_ISSUES) are read-only and do not modify Phase 3/4 outputs
- Error-safe wrapping pattern: wrap preview generation in error-safe logic so failures fall through to user decision step
- Gap report consumes three data structures: CONVERSION_GAPS, CONVERSION_DECISIONS, CONVERSION_KNOWLEDGE
- Gap data enrichment: gaps matched to decisions by component+feature keys for decision_type, rationale, confidence
- Similar gaps grouped for readability (3+ threshold); platform comparison table covers 11 Claude Code capabilities
- Three status levels for platform comparison: Supported, Partial, Unsupported
- Manual steps derivation uses category x decision_type matrix (7 categories, 3+ decision types)
- Phase 6 has 8 steps: output dir, existing file check, empty conversion check, dir creation, file writing, migration guide, gap report, output summary
- WRITE_RESULTS tracking: files_written, files_failed, files_renamed, gap_report_only
- File path conflict resolution uses group-name suffix pattern: `{filename}-{group}.md`
- Migration guide has 8 sections: Header, Conversion Fidelity, Platform Adapter Status, Conversion Summary, Per-Component Details, Decisions Log, Post-Conversion Steps, File Inventory
- Edge case flags for migration guide: CLEAN_CONVERSION, LARGE_CONVERSION (20+ components → condensed table), NO_DECISIONS
- Post-conversion steps derived from 4 sources: CONVERSION_GAPS, CONVERSION_DECISIONS, STALENESS_STATUS, platform knowledge

## Key Decisions
- port-tools plugin group created at `claude/port-tools/` with v0.1.0
- Adapter file format uses markdown with YAML code blocks for mappings (9 sections)
- Research agent is Sonnet-tier with web search + context7 tools
- OpenCode (v0.0.55) has been archived, moved to "Crush" by Charm team — adapter targets final release
- Porter skill excludes port-tools from its own selection list (self-porting prevention)
- Phase 4 introduced CONVERSION_KNOWLEDGE as merged data structure combining adapter + research findings with precedence rules
- Adapter staleness detection via target_platform_version comparison between adapter and research
- All conversion logic is adapter-driven (generic), no OpenCode-specific hardcoding
- Agent and reference converters are separate reference files (not inline) for modularity
- MCP converter follows same reference file pattern as other converters
- Incompatibility resolver is a reference file (579 lines) rather than inline in SKILL.md
- Decision persistence is append-only; survives partial conversion failures
- Fidelity scoring unified to 4 categories (direct/workaround/TODO/omitted) replacing earlier 3-category system
- Dry-run preview placed at Phase 4.5 (between Research and Conversion) as it uses CONVERSION_KNOWLEDGE but precedes actual conversion
- Phase 6 file writer handles path conflicts via group-name disambiguation suffixes
- Migration guide includes fidelity scores, adapter staleness status, per-component details, renames, and failed writes

## Known Issues
- OpenCode has been archived → future adapter may need to target Crush instead
- Concurrent edits to SKILL.md by multiple agents require re-read/retry patterns (confirmed in all waves)
- Some task-executor agents cannot use TaskUpdate from subprocess — orchestrator must fix statuses manually

## File Map
- `claude/port-tools/.claude-plugin/plugin.json` - Plugin manifest (name: agent-alchemy-port-tools, v0.1.0)
- `claude/port-tools/skills/plugin-porter/SKILL.md` - Full porter skill with 7-phase (+4.5) workflow (~2728 lines, all phases fully implemented)
- `claude/port-tools/skills/plugin-porter/references/adapter-format.md` - Adapter file format spec (~620 lines, 9 mapping sections)
- `claude/port-tools/skills/plugin-porter/references/adapters/opencode.md` - OpenCode platform adapter (184 lines)
- `claude/port-tools/skills/plugin-porter/references/agent-converter.md` - Agent conversion logic (7-stage pipeline, ~541 lines, unified fidelity scoring)
- `claude/port-tools/skills/plugin-porter/references/hook-converter.md` - Hook conversion logic (524 lines)
- `claude/port-tools/skills/plugin-porter/references/reference-converter.md` - Reference file conversion logic (4-stage, 361 lines)
- `claude/port-tools/skills/plugin-porter/references/mcp-converter.md` - MCP config conversion logic (713 lines)
- `claude/port-tools/skills/plugin-porter/references/incompatibility-resolver.md` - Incompatibility detection and resolution (579 lines)
- `claude/port-tools/agents/researcher.md` - Platform research agent (Sonnet tier)
- `claude/port-tools/README.md` - Plugin group README
- `claude/.claude-plugin/marketplace.json` - Updated with port-tools entry

## Task History
### Task [30]: Create port-tools plugin group scaffold - PASS
- Files: plugin.json, SKILL.md placeholder, researcher.md, README.md, marketplace.json updated

### Task [31]: Define adapter file format specification - PASS
- Files: `references/adapter-format.md` (~620 lines, 9 mapping sections)

### Task [33]: Create research agent definition - PASS
- Files: `agents/researcher.md` (Sonnet tier, web search + context7 tools)

### Task [32]: Research and create OpenCode platform adapter - PASS
- Files: `references/adapters/opencode.md` (184 lines)
- OpenCode built-in tools mapped; agent types fixed in code (coder, task, title, summarizer)

### Task [34]: Implement porter skill with plugin selection wizard - PASS
- Files: `SKILL.md` replaced placeholder (647 lines, 7 phases)
- Plugin selection wizard with AskUserQuestion multiSelect for groups and components

### Task [36]: Implement skill conversion engine in porter skill - PASS
- Files modified: `SKILL.md` (Phase 5 placeholder replaced with ~345 lines of conversion engine logic)
- Phase 5 has 10 steps covering all component types; file grew from ~833 to 1178 lines

### Task [37]: Implement agent conversion engine in porter skill - PASS
- Files modified: `references/agent-converter.md` (new, 523 lines), SKILL.md updated
- 7-stage pipeline with 5-pass body transformation and weighted fidelity scoring

### Task [38]: Integrate research subagent into porter workflow - PASS
- Files modified: `SKILL.md` (Phase 4 expanded from ~90 to ~275 lines)
- CONVERSION_KNOWLEDGE as merged data, graceful degradation on research failure

### Task [40]: Implement hook converter in porter skill - PASS
- Files modified: `references/hook-converter.md` (created, 524 lines)
- OpenCode: all hook events map to null — "no hook support" is primary flow

### Task [41]: Implement reference file converter in porter skill - PASS
- Files modified: `references/reference-converter.md` (created, 361 lines)
- 4-stage pipeline with flatten strategy for platforms without composition

### Task [42]: Implement MCP config converter in porter skill - PASS
- Files modified: `references/mcp-converter.md` (created, 713 lines), SKILL.md Step 7 + Reference Files updated
- Claude Code .mcp.json schema: command, args, env, cwd, type, url, headers, oauth
- MCP tool naming convention difference: double vs single underscore

### Task [35]: Implement dependency graph pre-check in porter skill - PASS
- Files modified: `SKILL.md` Phase 3 (93 → 353 lines, total file ~1623 lines)
- 5 steps: Parse, Build Graph, Self-Contained Check, Alert Missing, Summary
- Topological sort with cycle-breaking produces CONVERSION_ORDER for Phase 5
- Required 3 re-reads due to concurrent modifications by other agents

### Task [39]: Implement incompatibility resolver in porter skill - PASS
- Files modified: `references/incompatibility-resolver.md` (created, 579 lines), SKILL.md Step 8 expanded
- 5 incompatibility categories, batch resolution via RESOLUTION_CACHE
- Cascading impact detection, append-only decision persistence

### Task [48]: Implement adapter version staleness checker - PASS
- Files modified: `SKILL.md` (1178 → 1302 lines before other concurrent modifications)
- STALENESS_STATUS tracking, fuzzy version comparison, error-safe wrapper
- AskUserQuestion: proceed with adapter or update adapter first

### Task [46]: Implement fidelity scoring system in porter skill - PASS
- Files modified: `SKILL.md` (Step 9 expanded from ~48 to ~106 lines), `references/agent-converter.md` (Stage 6 rewritten)
- Unified 4-category scoring: direct (1.0), workaround (0.7), TODO (0.2), omitted (0.0)
- Color bands: Green 80-100%, Yellow 50-79%, Red 0-49%
- FIDELITY_REPORT and FIDELITY_COUNTERS tracking structures
- Agent converter Stage 6 now delegates to unified formula

### Task [45]: Implement gap report generator in porter skill - PASS
- Files modified: `SKILL.md` (Phase 6: ~220 lines added for gap report generation)
- Gap data enrichment: gaps matched to decisions by component+feature keys
- Similar gaps grouped (3+ threshold), platform comparison table (11 capabilities)
- Three status levels: Supported, Partial, Unsupported
- Manual steps derivation uses category x decision_type matrix

### Task [47]: Implement dry-run preview mode in porter skill - PASS
- Files modified: `SKILL.md` (added ~237 lines for Phase 4.5, updated Phase Overview)
- Phase 4.5 inserted between Research and Conversion
- Pessimistic/optimistic fidelity score range using 0.7/1.0 weights for partial mappings
- Preview data structures are read-only; error-safe wrapping for graceful failure

### Task [43]: Implement converted file writer in porter skill - PASS
- Files modified: `SKILL.md` (Phase 6 expanded to ~610 lines across 8 steps, total file ~2489 lines)
- WRITE_RESULTS tracking: files_written, files_failed, files_renamed, gap_report_only
- File path conflict resolution via group-name suffix
- Migration guide with fidelity scores, adapter status, per-component details
- Required 4 re-reads due to concurrent edits from other Wave 4 agents

### Task [44]: Implement migration guide generator in porter skill - PASS
- Files modified: `SKILL.md` (Step 6 expanded from ~139 to ~378 lines, total file 2489 → 2728 lines)
- 8 migration guide sections: Header, Conversion Fidelity, Platform Adapter Status, Conversion Summary, Per-Component Details, Decisions Log, Post-Conversion Steps, File Inventory
- Edge case flags: CLEAN_CONVERSION (all green + zero gaps), LARGE_CONVERSION (20+ components), NO_DECISIONS
- Post-conversion steps derived from 4 sources: gaps, decisions, staleness, platform knowledge
- Graceful degradation for missing data; write failure resilience (display in Phase 7 summary)
