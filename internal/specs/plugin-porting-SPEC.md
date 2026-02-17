# Plugin Porting PRD

**Version**: 1.0
**Author**: Stephen Sequenzia
**Date**: 2026-02-17
**Status**: Draft
**Spec Type**: New feature
**Spec Depth**: Detailed specifications
**Description**: A new plugin for Agent Alchemy that converts Claude Code plugins into formats compatible with other AI coding harnesses (MVP: OpenCode), using an extensible adapter framework, real-time platform research, and interactive conversion workflows.

---

## 1. Executive Summary

Plugin Porting adds a new plugin group to Agent Alchemy that converts existing Claude Code plugins into formats compatible with other AI coding tools. The porter uses an extensible markdown-based adapter framework, a research subagent for live platform documentation, and a guided wizard that interactively resolves incompatibilities during conversion. The MVP targets OpenCode as the first supported platform.

## 2. Problem Statement

### 2.1 The Problem

Agent Alchemy plugins (skills, agents, hooks, references, MCP configs) are built exclusively for Claude Code's plugin architecture. Users who work with or manage teams using other AI coding tools — such as OpenCode — have no automated migration path. Porting plugins today requires manually understanding both platform architectures and rewriting every component from scratch.

### 2.2 Current State

There is no tooling for cross-platform plugin portability. Plugin authors who want their plugins available on other platforms must:
1. Manually study the target platform's plugin system
2. Understand Claude Code's YAML frontmatter, tool names, model tiering, and composition patterns
3. Rewrite each skill, agent, hook, and reference file in the target format
4. Test for functional parity with no automated verification

### 2.3 Impact Analysis

Without a porting solution:
- Plugin authors' work remains locked to Claude Code, limiting adoption and reuse
- Teams using mixed tooling cannot benefit from Agent Alchemy's capabilities
- The investment in building comprehensive plugin groups (20 skills, 12 agents across 5 groups) has no portability value
- Community growth is constrained to Claude Code users only

### 2.4 Business Value

- **Reach expansion**: Makes Agent Alchemy plugins accessible to users of other AI coding platforms
- **Plugin portability**: Transforms plugins from platform-locked assets into portable investments
- **Community growth**: Attracts contributors from the broader AI coding tool ecosystem
- **Strategic positioning**: Positions Agent Alchemy as a platform-agnostic plugin authoring framework

## 3. Goals & Success Metrics

### 3.1 Primary Goals
1. Enable automated conversion of Agent Alchemy plugins to OpenCode format
2. Build an extensible adapter framework that supports adding new target platforms
3. Provide comprehensive reporting on conversion fidelity, gaps, and workarounds
4. Maintain interactive, user-guided resolution of platform incompatibilities

### 3.2 Success Metrics

| Metric | Current Baseline | Target | Measurement Method | Timeline |
|--------|------------------|--------|-------------------|----------|
| Conversion fidelity (simple plugins) | 0% | 90%+ average score | Fidelity scoring system | Phase 2 |
| Conversion fidelity (complex plugins) | 0% | 70%+ average score | Fidelity scoring system | Phase 3 |
| Feature coverage | 0 components | All 5 component types (skills, agents, hooks, refs, MCP) | Component type support count | Phase 3 |
| Gap report completeness | N/A | Every unconverted feature has explanation + workaround | Manual review of gap reports | Phase 3 |

### 3.3 Non-Goals
- Automated testing of converted plugins on the target platform
- Bidirectional porting (target platform → Claude Code)
- Runtime compatibility layer (converted plugins should be native to the target)
- Supporting platforms without a documented plugin/extension system

## 4. User Research

### 4.1 Target Users

#### Primary Persona: Plugin Author
- **Role/Description**: A developer who creates Agent Alchemy plugins and wants to share them across platforms
- **Goals**: Maximize the reach and reuse of their plugin development investment
- **Pain Points**: Manual porting is tedious, error-prone, and requires deep knowledge of both platforms
- **Context**: After developing or updating a plugin in Claude Code, they want to quickly produce an equivalent for other platforms

#### Secondary Persona: Team Lead
- **Role/Description**: A technical lead adopting Agent Alchemy plugins for teams using different AI coding tools
- **Goals**: Bring the same development workflows and capabilities to all team members, regardless of which AI tool they use
- **Pain Points**: Team members on different tools get inconsistent capabilities; no standardized way to distribute plugins cross-platform

### 4.2 User Journey Map

```
[Plugin developed in Claude Code] --> [Invoke porter skill] --> [Select plugin group] --> [Select components]
    --> [Dependency graph validation] --> [Research target platform] --> [Interactive conversion]
    --> [Preview output (optional)] --> [Write converted files] --> [Review migration guide + gap report]
```

**Typical flow:**
1. Developer finishes a plugin or wants to port an existing one
2. Invokes the plugin-porting skill
3. Selects a target platform (MVP: OpenCode)
4. Picks plugin groups, then individual components
5. System validates dependencies and alerts on missing cross-plugin references
6. Research subagent investigates the target platform's latest plugin architecture
7. Conversion proceeds component-by-component with interactive resolution of incompatibilities
8. Optional dry-run preview before writing files
9. Converted files + migration guide are written to output directory

## 5. Functional Requirements

### 5.1 Feature: Plugin Selection Wizard

**Priority**: P0 (Critical)

#### User Stories

**US-001**: As a plugin author, I want to select which plugins and components to port so that I only convert what I need.

**Acceptance Criteria**:
- [ ] Display all plugin groups from the marketplace registry (core-tools, dev-tools, sdd-tools, tdd-tools, git-tools)
- [ ] Allow multi-selection at the group level using `AskUserQuestion`
- [ ] After group selection, display individual components (skills, agents, hooks, references, MCP configs) within selected groups
- [ ] Allow component-level multi-selection
- [ ] Display component counts and brief descriptions for informed selection

**Edge Cases**:
- Empty plugin group (no components): Skip group, inform user
- All components selected: Proceed with full group conversion

---

### 5.2 Feature: Dependency Graph Pre-Check

**Priority**: P0 (Critical)

#### User Stories

**US-002**: As a plugin author, I want to be alerted about missing dependencies before conversion starts so that I don't end up with a broken partial conversion.

**Acceptance Criteria**:
- [ ] Parse all selected components to build a full dependency graph
- [ ] Detect skill-to-skill references (e.g., `Read ${CLAUDE_PLUGIN_ROOT}/../core-tools/skills/deep-analysis/SKILL.md`)
- [ ] Detect agent-to-skill references (e.g., `skills:` field in agent frontmatter)
- [ ] Detect hook-to-script references (e.g., `command` fields in hooks.json)
- [ ] Detect cross-plugin references (e.g., `${CLAUDE_PLUGIN_ROOT}/../{source-dir-name}/`)
- [ ] Alert the user about any dependency that is NOT in the selected component set
- [ ] Offer to add missing dependencies to the selection or proceed without them
- [ ] Display the dependency graph summary (component count, dependency count, any circular refs)

**Edge Cases**:
- Circular dependencies: Detect and report, allow user to proceed with warning
- External dependencies (MCP servers, bash scripts): Flag as "requires manual porting" in the gap report
- Self-contained plugin (no cross-refs): Skip dependency check, proceed directly

---

### 5.3 Feature: Platform Research Subagent

**Priority**: P0 (Critical)

#### User Stories

**US-003**: As a plugin author, I want the porter to automatically research the target platform's latest plugin architecture so that I don't have to manually study their documentation.

**Acceptance Criteria**:
- [ ] Spawn a research subagent before conversion begins
- [ ] Research subagent fetches official documentation for the target platform's plugin/extension system
- [ ] Research subagent searches for community examples, GitHub repos, and blog posts about building plugins for the target
- [ ] Research subagent analyzes existing plugins on the target platform for conventions and patterns
- [ ] Research findings are structured into a platform profile: supported features, file format, tool equivalents, composition patterns, limitations
- [ ] Research is always fresh per session — no caching of results
- [ ] Research findings are stored internally and used throughout the conversion process

**Edge Cases**:
- Target platform has minimal/no documentation: Report to user, suggest manual investigation, allow proceeding with best-effort
- Research subagent timeout or failure: Inform user, offer to retry or proceed with adapter file defaults only
- Conflicting information between sources: Present both to user, let them decide which to follow

---

### 5.4 Feature: Interactive Conversion Engine

**Priority**: P0 (Critical)

#### User Stories

**US-004**: As a plugin author, I want to be guided through the conversion process and have a say in how incompatible features are handled so that the converted plugin reflects my intent.

**Acceptance Criteria**:
- [ ] Convert each selected component one at a time, in dependency order
- [ ] For each component, map Claude Code constructs to target platform equivalents:
  - YAML frontmatter fields → target format metadata
  - Tool names (Read, Glob, Grep, Edit, Write, Bash, Task, etc.) → target equivalents
  - Model references (opus, sonnet, haiku) → target model identifiers or generic labels
  - `${CLAUDE_PLUGIN_ROOT}` paths → target path resolution mechanism
  - Hook events → target lifecycle events
  - AskUserQuestion patterns → target user interaction mechanism
- [ ] When a feature has no direct equivalent, pause and present options via `AskUserQuestion`:
  - Find a workaround (suggest alternatives based on research)
  - Omit the feature (remove it from converted output)
  - Add as TODO comment (leave a placeholder with explanation)
- [ ] Track all conversion decisions for inclusion in the migration guide
- [ ] Process components in parallel where no dependencies exist between them

**Edge Cases**:
- Deeply nested skill composition (skill loads skill loads skill): Resolve recursively, maintain chain
- Agent with restricted tool set: Map only the tools that have equivalents, flag rest
- Hook with shell script dependency: Copy script and adjust paths, or flag for manual porting

---

### 5.5 Feature: Dry-Run Preview Mode

**Priority**: P1 (High)

#### User Stories

**US-005**: As a plugin author, I want to preview what the conversion will produce before committing so that I can verify the scope and catch issues early.

**Acceptance Criteria**:
- [ ] Offer dry-run as an optional step after dependency validation and research, before conversion
- [ ] Display: target file tree structure, per-component conversion status (full/partial/unsupported), expected issues
- [ ] Allow user to approve and proceed, or cancel
- [ ] No files are written to disk during dry-run

**Edge Cases**:
- Large plugin group (many components): Summarize instead of listing every file
- All components unsupported: Warn user that conversion may not be worthwhile

---

### 5.6 Feature: File Output & Migration Guide

**Priority**: P0 (Critical)

#### User Stories

**US-006**: As a plugin author, I want converted files written to the correct location with a migration guide so that I can understand all the changes made.

**Acceptance Criteria**:
- [ ] Ask user for output directory, recommending the target platform's expected plugin location
- [ ] Write converted plugin files in the target platform's directory structure and file format
- [ ] Generate a `MIGRATION-GUIDE.md` file alongside the converted files containing:
  - Summary of conversion (source plugin, target platform, date)
  - Per-component conversion details and decisions made
  - Conversion fidelity score per component (0-100%)
  - Overall conversion fidelity score
- [ ] Include a `GAP-REPORT.md` section (or separate file) with:
  - Each unconverted feature with explanation of why
  - Suggested workarounds or alternatives for each
  - Severity indicators for each gap (cosmetic, functional, critical)

**Edge Cases**:
- Output directory already exists with files: Warn before overwriting
- File path conflicts between converted components: Rename with suffix, document in guide
- Empty conversion (all components unsupported): Write gap report only, no plugin files

---

### 5.7 Feature: Conversion Fidelity Scoring

**Priority**: P1 (High)

#### User Stories

**US-007**: As a plugin author, I want a numerical quality score for each converted component so that I can quickly identify which parts need manual attention.

**Acceptance Criteria**:
- [ ] Calculate a fidelity score (0-100%) for each converted component based on:
  - Percentage of features successfully mapped
  - Percentage of references preserved
  - Number of TODOs/omissions
  - Presence of workarounds vs. direct mappings
- [ ] Display per-component scores in the migration guide
- [ ] Calculate and display an overall weighted score for the entire conversion
- [ ] Color-code or label scores: green (80%+), yellow (50-79%), red (<50%)

**Edge Cases**:
- Component with no mappable features: Score 0%, flag in gap report
- Component with all features mapped but via workarounds: Score reflects workaround quality (e.g., 70% vs direct 100%)

---

### 5.8 Feature: Platform Adapter Framework

**Priority**: P0 (Critical)

#### User Stories

**US-008**: As a plugin author, I want the porter to use an extensible adapter system so that new target platforms can be added without rewriting the conversion engine.

**Acceptance Criteria**:
- [ ] Each target platform is represented by a markdown-based adapter file
- [ ] Adapter files define:
  - Platform name and version
  - Plugin directory structure and file naming conventions
  - Tool name mappings (Claude Code tool → target equivalent or null)
  - Model tier mappings (opus/sonnet/haiku → target equivalents)
  - Frontmatter format translations
  - Supported hook/lifecycle events and their mappings
  - Composition mechanism (how the target handles skill/reference loading)
  - Path resolution mechanism (equivalent of `${CLAUDE_PLUGIN_ROOT}`)
- [ ] Adapter files include a version field tied to the target platform version
- [ ] During research phase, the porter checks adapter version against latest platform docs and warns if stale
- [ ] Adding a new target platform requires only creating a new adapter file

**Edge Cases**:
- Adapter file is incomplete (missing mappings): Convert what's possible, flag unmapped items
- Target platform has no equivalent for a Claude Code concept (e.g., no hook system): Adapter marks as `null`, conversion engine treats as gap
- Multiple adapter versions for same platform: Use the latest matching the platform's current version

## 6. Non-Functional Requirements

### 6.1 Performance
- Research phase should complete within reasonable time for a subagent performing web searches
- Conversion of individual components should not exceed a few seconds per component (excluding user interaction time)
- Dry-run preview should generate within seconds for any plugin group size

### 6.2 Security
- No secrets or credentials should be included in converted plugin files
- Research subagent should only access public documentation and repositories
- Converted files should not contain sensitive path information from the source environment

### 6.3 Scalability
- Support conversion of all 5 plugin groups simultaneously
- Adapter framework should support adding unlimited target platforms
- Research findings should scale gracefully with complex plugin structures

### 6.4 Reliability
- Conversion engine should handle partial failures gracefully (continue with remaining components)
- Research subagent failure should not block the entire conversion
- All user decisions should be recoverable (no irrevocable actions until final file write)

## 7. Technical Considerations

### 7.1 Architecture Overview

The plugin-porting feature is implemented as a new Agent Alchemy plugin group (`claude/port-tools/`) following existing conventions. It consists of:

1. **Porter Skill** — Main entry point, orchestrates the guided wizard workflow
2. **Research Agent** — Subagent that performs full investigation of the target platform
3. **Adapter Files** — Markdown files in a `references/adapters/` directory, one per target platform
4. **Conversion Engine** — Logic embedded in the porter skill for mapping components using adapter definitions

The architecture follows the skill-as-orchestrator pattern used by `create-spec` and `feature-dev`: the main skill drives the workflow, spawns subagents for research, and uses `AskUserQuestion` for interactive decisions.

### 7.2 Tech Stack
- **Plugin format**: Markdown-as-code (YAML frontmatter + markdown body) — consistent with all Agent Alchemy plugins
- **Adapter format**: Markdown files with structured sections for mappings
- **Research**: Subagent using `WebSearch`, `WebFetch`, `context7` MCP tools
- **Conversion output**: Platform-native files in target format

### 7.3 Integration Points

| System | Integration Type | Purpose |
|--------|-----------------|---------|
| Marketplace registry (`marketplace.json`) | File read | Enumerate available plugins for selection |
| Plugin source files (skills, agents, hooks) | File read | Read source components for conversion |
| Platform adapter files | File read | Load target platform mappings |
| Research subagent | Task spawn | Live platform documentation research |
| Target output directory | File write | Write converted plugin files |

### 7.4 Technical Constraints
- Must follow Agent Alchemy's markdown-as-code plugin conventions
- Research subagent cannot cache results across sessions (always fresh)
- Adapter files are markdown (not code) — conversion logic must work from declarative mappings
- Conversion must respect the existing `${CLAUDE_PLUGIN_ROOT}` path convention

### 7.5 Codebase Context

#### Existing Architecture

Agent Alchemy's plugin system uses markdown files as executable code. YAML frontmatter defines metadata (name, description, model, tools, skills) while the markdown body contains the system prompt or workflow instructions. Five plugin groups contain 20 skills, 12 agents, 33 reference files, and 2 hook configurations.

Key structural elements that must be understood for conversion:
- **Skills**: `SKILL.md` files — frontmatter fields: `name`, `description`, `model`, `user-invocable`, `disable-model-invocation`, `allowed-tools`, `argument-hint`
- **Agents**: `{name}.md` files — frontmatter fields: `name`, `description`, `model`, `tools` (list), `skills` (list)
- **Hooks**: `hooks.json` — event matchers (`PreToolUse`, `PostToolUse`, `Stop`, etc.) with shell commands
- **References**: Supporting markdown files in `references/` subdirectories
- **MCP configs**: `.mcp.json` files for Model Context Protocol server integration

#### Integration Points

| File/Module | Purpose | How This Feature Connects |
|------------|---------|---------------------------|
| `claude/.claude-plugin/marketplace.json` | Plugin registry | Read to enumerate available plugins and groups |
| `claude/*/skills/*/SKILL.md` | Skill definitions | Source files to convert |
| `claude/*/agents/*.md` | Agent definitions | Source files to convert |
| `claude/*/hooks/hooks.json` | Hook configurations | Source files to convert |
| `claude/*/skills/*/references/**` | Reference materials | Files to include or flatten during conversion |

#### Patterns to Follow
- **Skill composition via prompt injection**: `Read ${CLAUDE_PLUGIN_ROOT}/path/to/skill` — used in `feature-dev`, `codebase-analysis`, `docs-manager`
- **Hub-and-spoke team coordination**: Main skill spawns specialized subagents — used in `deep-analysis`
- **AskUserQuestion enforcement**: All user interaction via structured tool — used in all interactive skills
- **Phase workflow with completeness enforcement**: Numbered phases with critical directives — used in `deep-analysis`, `tdd-cycle`
- **Reference file progressive loading**: Large knowledge bases in `references/` loaded on demand — used in `create-spec`, `tdd-cycle`

#### Related Features
- **create-spec**: Similar guided wizard pattern with multi-round interview and structured output — reusable UX patterns
- **deep-analysis**: Hub-and-spoke agent team pattern — reusable for research orchestration
- **create-tasks**: Reads structured input and generates structured output — similar pattern to reading plugins and generating converted output

## 8. Scope Definition

### 8.1 In Scope
- Plugin selection wizard with group-level and component-level selection
- Dependency graph pre-check with cross-plugin reference validation
- Research subagent for live target platform investigation
- Interactive conversion with pause-and-ask on incompatibilities
- Conversion of all component types: skills, agents, hooks, references, MCP configs
- Platform adapter framework with markdown-based adapter files
- Adapter versioning with staleness detection
- Dry-run preview mode
- Migration guide generation
- Gap report with workarounds
- Conversion fidelity scoring
- OpenCode as MVP target platform

### 8.2 Out of Scope
- **Automated testing on target platform**: Converted plugins must be manually tested on the target — no automated execution validation
- **Bidirectional porting**: Only Claude Code → target direction; no target → Claude Code conversion
- **Runtime compatibility layer**: Converted plugins should be native to the target, not wrappers
- **Supporting undocumented platforms**: Target platforms without a documented plugin/extension system are not supported
- **Partial re-conversion**: Updating a previously ported plugin when the source changes (future consideration)

### 8.3 Future Considerations
- **Additional target platforms**: Cursor, Windsurf, Cline, Aider, and other AI coding tools
- **Incremental re-porting**: Detect changes in source plugin since last conversion and port only the delta
- **Bidirectional porting**: Import plugins from other platforms into Claude Code format
- **Community adapter contributions**: Allow users to submit and share adapter files for new platforms
- **Conversion validation**: Automated functional testing of converted plugins on the target platform

## 9. Implementation Plan

### 9.1 Phase 1: Foundation — Adapter Framework & OpenCode Research

**Completion Criteria**: Adapter framework is defined, OpenCode adapter file is researched and created, plugin group scaffold exists.

| Deliverable | Description | Dependencies |
|-------------|-------------|--------------|
| Plugin group scaffold | Create `claude/port-tools/` with standard structure (skills/, agents/, references/) | None |
| Adapter file format spec | Define the markdown format for platform adapter files (sections, fields, mappings) | None |
| OpenCode adapter | Research OpenCode's plugin architecture and create the initial adapter file | Adapter format spec |
| Research agent definition | Define the research agent (`researcher.md`) with web search, context7, and web fetch tools | Plugin scaffold |

**Checkpoint Gate**: Review adapter file format and OpenCode adapter accuracy before proceeding to conversion engine.

---

### 9.2 Phase 2: Core Conversion — Selection & Conversion Engine

**Completion Criteria**: Users can select plugins, validate dependencies, and convert simple components (skills, agents) to OpenCode format.

| Deliverable | Description | Dependencies |
|-------------|-------------|--------------|
| Porter skill (wizard framework) | Main `SKILL.md` with selection wizard, group-level and component-level selection | Plugin scaffold |
| Dependency graph analyzer | Parse selected components, build dependency graph, detect cross-plugin references, alert on missing deps | Porter skill |
| Skill converter | Convert SKILL.md files to OpenCode format using adapter mappings | Adapter framework, OpenCode adapter |
| Agent converter | Convert agent .md files to OpenCode format using adapter mappings | Adapter framework, OpenCode adapter |

**Checkpoint Gate**: Review conversion quality of simple skills (e.g., git-commit) and agents before adding complex components.

---

### 9.3 Phase 3: Interactive Porting — Research, Resolution & Full Coverage

**Completion Criteria**: Full conversion pipeline works end-to-end including research, interactive resolution, hooks, references, and MCP configs.

| Deliverable | Description | Dependencies |
|-------------|-------------|--------------|
| Research subagent integration | Spawn research agent before conversion, feed findings into conversion engine | Research agent, porter skill |
| Incompatibility resolver | Interactive pause-and-ask flow for features without direct equivalents | Porter skill |
| Hook converter | Convert hooks.json to target format, map event types and shell commands | Adapter framework |
| Reference converter | Copy/flatten reference files, adjust paths for target platform | Adapter framework |
| MCP config converter | Convert .mcp.json to target format | Adapter framework |

**Checkpoint Gate**: End-to-end test converting a complex plugin group (e.g., core-tools with deep-analysis) to verify composition chain handling.

---

### 9.4 Phase 4: Output & Reporting — Migration Guide, Scoring, Preview

**Completion Criteria**: Full output pipeline including migration guide, gap report, fidelity scoring, and dry-run preview.

| Deliverable | Description | Dependencies |
|-------------|-------------|--------------|
| File writer | Write converted files to user-chosen directory in target structure | Phase 3 converters |
| Migration guide generator | Generate MIGRATION-GUIDE.md with per-component details and decisions | File writer |
| Gap report generator | Generate gap report with unconverted features, explanations, and workarounds | Incompatibility resolver |
| Fidelity scoring system | Calculate per-component and overall fidelity scores | All converters |
| Dry-run preview | Show expected output structure and issues before writing files | Dependency analyzer, converters |
| Adapter version checker | Compare adapter version against research findings, warn if stale | Research subagent, adapter framework |

## 10. Dependencies

### 10.1 Technical Dependencies

| Dependency | Owner | Status | Risk if Delayed |
|------------|-------|--------|-----------------|
| OpenCode plugin architecture documentation | OpenCode team (external) | Available at runtime via research | Research quality degrades if docs are poor |
| Agent Alchemy marketplace registry | Agent Alchemy | Stable | No plugin enumeration for selection wizard |
| WebSearch/WebFetch/context7 tools | Claude Code platform | Available | Research subagent cannot function |

### 10.2 Cross-Team Dependencies

| Team | Dependency | Status |
|------|------------|--------|
| N/A (single-author project) | No cross-team deps | N/A |

## 11. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation Strategy |
|------|--------|------------|-------------------|
| Target platform doc quality | High | Medium | Full investigation research (docs + community + existing plugins); adapter files serve as fallback mapping |
| Feature gap breadth | High | High | Interactive resolution (pause-and-ask); comprehensive gap report with workarounds; fidelity scoring sets expectations |
| Adapter maintenance burden | Medium | High | Adapter versioning with staleness detection; always-fresh research per session supplements adapter knowledge |
| Complex composition chains break during conversion | Medium | Medium | Dependency graph pre-check; convert in dependency order; preserve references where possible |
| Research subagent returns inconsistent information | Medium | Medium | Present conflicting findings to user for resolution; prioritize official docs over community sources |
| Target platform changes plugin format | Medium | Medium | Always-fresh research catches changes; adapter version check warns on staleness |

## 12. Open Questions

| # | Question | Owner | Due Date | Resolution |
|---|----------|-------|----------|------------|
| 1 | Exact structure of OpenCode's plugin system | Research subagent | Resolved at conversion time | Researched live per session |
| 2 | Should partial re-conversion (delta porting) be supported in a future phase? | Stephen | TBD | Scoped as future consideration |
| 3 | How should the porter handle plugins that depend on MCP servers not available on the target platform? | Stephen | Phase 3 | Flag in gap report with alternatives |

## 13. Appendix

### 13.1 Glossary

| Term | Definition |
|------|------------|
| Adapter file | A markdown file defining the mapping between Claude Code plugin constructs and a target platform's equivalents |
| Conversion fidelity | A percentage score (0-100%) representing how completely a plugin component was ported to the target format |
| Gap report | A document listing features that could not be fully converted, with explanations and workarounds |
| Porter | The plugin-porting skill that orchestrates the conversion workflow |
| Target platform | The AI coding tool that the plugin is being converted for (MVP: OpenCode) |
| Composition chain | A sequence of skill-loading-skill references that must be resolved during conversion |
| Platform profile | Structured research findings about a target platform's plugin architecture |

### 13.2 References
- Agent Alchemy CLAUDE.md — project architecture and plugin conventions
- Agent Alchemy marketplace.json — plugin registry structure
- Claude Code plugin documentation — skill, agent, hook, and MCP config formats
- OpenCode documentation — researched live at conversion time

### 13.3 Agent Recommendations (Accepted)

*The following recommendations were suggested based on industry best practices and accepted during the interview:*

1. **Architecture**: Dependency Graph Pre-Check Phase
   - Rationale: Deep composition chains (feature-dev → deep-analysis → code-explorer) need upfront validation to prevent partial conversions and wasted research cycles
   - Applies to: Conversion workflow Phase 2, Section 5.2

2. **UX**: Dry-Run / Preview Mode
   - Rationale: Time-intensive research + conversion benefits from upfront scope preview before committing
   - Applies to: Conversion workflow, optional step before file writing, Section 5.5

3. **Quality**: Conversion Fidelity Score
   - Rationale: Full-scope conversion (skills, agents, hooks, refs, MCP) needs quick health indicators per component to guide manual attention
   - Applies to: Migration guide output, Section 5.7

4. **Maintenance**: Platform Adapter Versioning
   - Rationale: Adapter staleness risk mitigated by version checking against live platform docs during research phase
   - Applies to: Adapter framework, research phase, Section 5.8

---

*Document generated by SDD Tools*
