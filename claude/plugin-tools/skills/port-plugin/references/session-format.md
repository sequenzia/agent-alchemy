# Session Format Reference

Defines the contract between the port-plugin orchestrator and port-converter agents during wave-based conversion. All session files live in `.claude/sessions/__port_live__/`.

---

## Session Directory Structure

```
.claude/sessions/__port_live__/
├── conversion_knowledge.md    # Merged adapter + research (written once by orchestrator)
├── dependency_graph.md        # Serialized DEPENDENCY_GRAPH (written once by orchestrator)
├── resolution_cache.md        # Cached incompatibility decisions (grows between waves)
└── results/                   # Per-component result files (written by converter agents)
    ├── result-{component-id}.md
    ├── result-{component-id}.md
    └── ...
```

**Component ID format:** `{type}-{group}-{name}` (e.g., `skill-core-tools-deep-analysis`, `agent-dev-tools-code-reviewer`, `hooks-core-tools-hooks`, `mcp-sdd-tools-mcp`).

---

## conversion_knowledge.md

Written once by the orchestrator before the first wave. Contains the merged adapter + research knowledge base serialized in a format the converter agent can parse.

```markdown
# Conversion Knowledge

## Target Platform
- **Platform:** {TARGET_PLATFORM}
- **Platform version:** {version from research or adapter}
- **Adapter version:** {adapter_version or "none"}
- **Confidence basis:** {adapter+research / adapter-only / research-only}

## Tool Name Mappings

| Claude Code Tool | Target Equivalent | Notes | Confidence |
|------------------|-------------------|-------|------------|
| {tool} | {target or "null"} | {notes} | {high/medium/low/conflict} |

## Model Tier Mappings

| Claude Tier | Target Equivalent | Notes | Confidence |
|-------------|-------------------|-------|------------|
| {tier} | {target or "null"} | {notes} | {confidence} |

## Skill Frontmatter Mappings

| Claude Field | Target Field | Notes | Confidence |
|-------------|-------------|-------|------------|
| {field} | {target or "null" or "embedded:{location}"} | {notes} | {confidence} |

## Agent Frontmatter Mappings

| Claude Field | Target Field | Notes | Confidence |
|-------------|-------------|-------|------------|
| {field} | {target or "null" or "embedded:{location}"} | {notes} | {confidence} |

## Hook Event Mappings

| Claude Event | Target Event | Notes | Confidence |
|-------------|-------------|-------|------------|
| {event} | {target or "null"} | {notes} | {confidence} |

## Directory Structure

| Field | Value |
|-------|-------|
| plugin_root | {path} |
| skill_dir | {dir or "null"} |
| agent_dir | {dir or "null"} |
| hook_dir | {dir or "null"} |
| reference_dir | {dir or "null"} |
| config_dir | {dir or "null"} |
| file_extension | {ext} |
| naming_convention | {convention} |

## Composition Mechanism

| Field | Value |
|-------|-------|
| mechanism | {import/include/inline/reference/none} |
| syntax | {target syntax or "N/A"} |
| supports_cross_plugin | {true/false} |
| supports_recursive | {true/false} |
| max_depth | {number or "unlimited"} |

## Path Resolution

| Field | Value |
|-------|-------|
| root_variable | {variable or "null"} |
| resolution_strategy | {strategy} |
| same_plugin_pattern | {pattern} |
| cross_plugin_pattern | {pattern or "null"} |

## Known Limitations

- {limitation}: {impact on conversion}
```

---

## dependency_graph.md

Written once by the orchestrator. Contains the serialized dependency graph from Phase 3.

```markdown
# Dependency Graph

## Conversion Order

| Wave | Component ID | Type | Group | Name | Dependencies |
|------|-------------|------|-------|------|-------------|
| 1 | {id} | {type} | {group} | {name} | none |
| 1 | {id} | {type} | {group} | {name} | none |
| 2 | {id} | {type} | {group} | {name} | {dep1}, {dep2} |

## Dependency Edges

| Source | Target | Dependency Type |
|--------|--------|----------------|
| {source_id} | {target_id} | {skill-to-skill/cross-plugin/reference-include/agent-to-skill/external} |

## Circular References

{If any:}
- {cycle[0]} -> {cycle[1]} -> ... -> {cycle[0]}

{If none:}
No circular references detected.

## External Dependencies

| Source | External Dependency | Type |
|--------|-------------------|------|
| {source_id} | {description} | {MCP server/bash script/system} |

## Classification Counts

| Classification | Count |
|---------------|-------|
| Internal | {n} |
| External-selected | {n} |
| External-missing | {n} |
| External | {n} |
| System | {n} |
```

---

## resolution_cache.md

Starts empty, grows between waves as the orchestrator resolves incompatibilities. Converter agents read this to apply cached decisions without prompting.

```markdown
# Resolution Cache

## Cached Decisions

| Group Key | Decision Type | Workaround Applied | First Component | Apply Globally |
|-----------|-------------|-------------------|-----------------|---------------|
| {group_key} | {workaround/omitted/todo} | {description or "N/A"} | {component_name} | {true/false} |
```

**Reading protocol for converter agents:**

1. Read `resolution_cache.md` before processing incompatibilities
2. For each detected incompatibility, compute its `group_key`
3. Look up the `group_key` in the cache table
4. If found with `Apply Globally = true`: auto-apply the cached decision, record in result file with `resolution_mode: "cached"`
5. If found with `Apply Globally = false`: mark with inline marker for orchestrator review (the orchestrator will ask the user whether to reuse the previous decision)
6. If not found: mark with inline marker for orchestrator resolution

---

## result-{component-id}.md

Written by each converter agent. Contains the full conversion result for a single component.

```markdown
# Conversion Result: {component_id}

## Metadata

| Field | Value |
|-------|-------|
| Component ID | {component_id} |
| Component Type | {skill/agent/hooks/reference/mcp} |
| Group | {group_name} |
| Name | {component_name} |
| Source Path | {source_path} |
| Target Path | {target_path} |
| Fidelity Score | {score}% |
| Fidelity Band | {green/yellow/red} |
| Status | {full/partial/limited} |

## Converted Content

~~~
{full converted file content}
~~~

## Fidelity Report

| Mapping Type | Count | Weight | Contribution |
|-------------|-------|--------|-------------|
| Direct | {n} | 1.0 | {n * 1.0} |
| Workaround | {n} | 0.7 | {n * 0.7} |
| TODO | {n} | 0.2 | {n * 0.2} |
| Omitted | {n} | 0.0 | 0 |
| **Total** | **{n}** | | **{score}** |

{If estimation notes:}
**Notes:** {notes}

## Decisions

| Feature | Decision Type | Original | Converted | Rationale | Confidence | Resolution Mode |
|---------|-------------|----------|-----------|-----------|------------|----------------|
| {feature} | {workaround/omitted/todo/partial/composite/flattened/relocated/interaction_downgraded} | {original} | {converted} | {rationale} | {confidence or "N/A"} | {individual/batch/cached/auto/N/A} |

## Gaps

| Feature | Reason | Severity | Workaround | User Acknowledged |
|---------|--------|----------|------------|-------------------|
| {feature} | {reason} | {critical/functional/cosmetic} | {workaround or "None"} | {true/false} |

## Unresolved Incompatibilities

Incompatibilities the converter agent could not auto-resolve. The orchestrator batches these between waves.

| Group Key | Feature | Severity | Category | Reason | Suggested Workaround | Confidence | Affected Locations |
|-----------|---------|----------|----------|--------|---------------------|------------|-------------------|
| {group_key} | {feature_name} | {critical/functional/cosmetic} | {unmapped_tool/unmapped_field/unsupported_composition/unsupported_hook/general_gap} | {reason} | {workaround description or "None"} | {high/medium/low/uncertain/N/A} | {count} locations |
```

### Inline Markers for Deferred Resolution

When a converter agent encounters a non-cosmetic incompatibility that is not in the resolution cache (or is cached with `apply_globally = false`), it inserts an inline marker in the converted content:

```
<!-- UNRESOLVED: {group_key} | {severity} | {feature_name} | {workaround_description_or_none} -->
```

The orchestrator scans result files for these markers between waves and:
1. Groups markers by `group_key` across all results in the wave
2. Checks the resolution cache for cached decisions
3. Presents remaining unresolved items to the user via AskUserQuestion
4. Applies resolutions by replacing markers in the converted content
5. Updates `resolution_cache.md` with new decisions

### Cosmetic Auto-Resolution

Converter agents auto-resolve cosmetic incompatibilities (severity = "cosmetic") that have a suggested workaround with confidence "high" or "medium". These are:
- Applied directly in the converted content
- Recorded in the Decisions table with `Resolution Mode = auto`
- NOT listed in Unresolved Incompatibilities
- NOT marked with inline markers
