# Incompatibility Resolver

Reference for detecting, categorizing, and interactively resolving incompatibilities during plugin conversion. The resolver handles all cases where a Claude Code feature has no direct equivalent on the target platform, presenting resolution options to the user and tracking all decisions for the migration guide and gap report.

---

## Overview

During Phase 5 (Interactive Conversion), each component converter (skill, agent, hook, reference, MCP) encounters features that cannot be directly mapped to the target platform. The incompatibility resolver provides a unified flow for handling these gaps: it detects incompatibility categories, groups similar incompatibilities for batch resolution, presents concrete workaround suggestions from research and adapter data, and tracks every decision made.

The resolver is invoked by the conversion engine (Steps 3-7 of Phase 5) whenever a mapping lookup returns `null` and the feature is non-trivial, or when research/adapter notes flag a feature as unsupported.

---

## Incompatibility Categories

Every incompatibility falls into one of five categories. Detection uses the adapter mappings and research findings from `CONVERSION_KNOWLEDGE`.

### Category 1: Unmapped Tool

A Claude Code tool referenced in the component has no target platform equivalent.

**Detection:**
- Tool appears in `allowed-tools` frontmatter list and maps to `null` in `MAPPINGS.tool_names`
- Tool appears in body text (backtick-quoted or in prose) and maps to `null`
- Tool appears in a matcher pattern (hooks) and maps to `null`

**Severity classification:**
- **Critical**: Tool is central to the component's purpose (e.g., `Task` in a skill that spawns subagents, `AskUserQuestion` in an interactive workflow)
- **Functional**: Tool is used for a specific capability but the component can partially work without it (e.g., `WebSearch` in a research agent)
- **Cosmetic**: Tool appears in documentation or examples but is not essential to behavior (e.g., mentioned in a comment)

**Severity heuristic:**
1. Count occurrences of the tool in the body text
2. Check if the tool appears in the `allowed-tools` list
3. If occurrences > 3 and in `allowed-tools`: **Critical**
4. If occurrences > 0 and in `allowed-tools`: **Functional**
5. If occurrences > 0 but not in `allowed-tools`: **Functional** (referenced in prose)
6. If only in `allowed-tools` with 0 body references: **Cosmetic**

### Category 2: Unmapped Frontmatter Field

A YAML frontmatter field has no target platform equivalent.

**Detection:**
- Field appears in source frontmatter and maps to `null` in `MAPPINGS.frontmatter_skill` or `MAPPINGS.frontmatter_agent`
- Field is not in the adapter's mapping table at all (unknown field)

**Severity classification:**
- **Functional**: Field controls runtime behavior (e.g., `allowed-tools`, `disable-model-invocation`, `model`)
- **Cosmetic**: Field is metadata-only (e.g., `description`, `argument-hint`)

### Category 3: Unsupported Composition Pattern

A skill composition pattern (skill loading, cross-plugin reference) is not supported on the target platform.

**Detection:**
- `MAPPINGS.composition.mechanism` is `none` and the component contains `Read ${CLAUDE_PLUGIN_ROOT}/...` patterns
- `MAPPINGS.composition.supports_cross_plugin` is `false` and the component has cross-plugin references (`${CLAUDE_PLUGIN_ROOT}/../{group}/...`)
- Recursive composition depth exceeds `MAPPINGS.composition.max_depth`

**Severity classification:**
- **Critical**: The composition chain is essential to the component's function (e.g., `feature-dev` loading `deep-analysis`)
- **Functional**: The composition provides supplementary behavior that can be worked around

### Category 4: Unsupported Hook Event

A hook event type has no target platform equivalent.

**Detection:**
- Event type maps to `null` in `MAPPINGS.hook_events`
- Adapter has no Hook/Lifecycle Event Mappings section (entire hook system unsupported)

**Severity classification:**
- **Critical**: Hook enforces security or prevents data loss (validation hooks blocking dangerous operations)
- **Functional**: Hook enables workflow automation (auto-approve, state management)
- **Cosmetic**: Hook provides informational value only (logging, notifications)

### Category 5: General Feature Gap

A feature where both adapter and research report no equivalent, and it does not fit into the other categories.

**Detection:**
- Adapter maps the feature to `null` AND research findings confirm no equivalent
- Research explicitly notes the feature as a platform limitation
- Feature is platform-specific (e.g., Claude Code runtime constructs like `TeamCreate`, `SendMessage`)

**Examples:**
- Inter-agent communication (`SendMessage`, `TeamCreate`)
- Task management tools (`TaskCreate`, `TaskUpdate`, `TaskList`, `TaskGet`)
- MCP server configuration when target has no MCP support
- Permission model constructs (`permissionMode`, `permissionDecision`)

**Severity:**
- Determined by impact on the component's core functionality
- Use the same heuristic as Category 1 (body occurrence count + role centrality)

---

## Incompatibility Collection

Before presenting resolution options to the user, the resolver collects all incompatibilities for a single component into a structured list. This enables grouping and batch resolution.

### Collection Structure

```
COMPONENT_INCOMPATIBILITIES = [
  {
    id: string,               -- Unique identifier (e.g., "tool-SendMessage", "field-description")
    category: string,         -- One of: "unmapped_tool", "unmapped_field", "unsupported_composition",
                              --         "unsupported_hook", "general_gap"
    feature_name: string,     -- Human-readable name of the incompatible feature
    original_content: string, -- The original Claude Code content/value
    reason: string,           -- Why this feature is incompatible
    severity: string,         -- "critical", "functional", "cosmetic"
    adapter_notes: string,    -- Notes from the adapter file about this gap (if any)
    research_notes: string,   -- Notes from research findings about this gap (if any)
    suggested_workaround: {
      description: string,    -- What the workaround does
      confidence: string,     -- "high", "medium", "low", "uncertain"
      source: string,         -- "adapter", "research", "inferred"
      implementation: string  -- Concrete steps or code for applying the workaround
    } | null,                 -- null if no workaround is available
    affected_locations: [     -- Where in the component this feature appears
      { line_context: string, location_type: string }
    ],
    group_key: string         -- Key for batch grouping (e.g., "unmapped_tool:SendMessage")
  }
]
```

### Collection Process

During each conversion step (skill frontmatter, body transformation, composition, etc.):

1. When a mapping returns `null` or a feature is flagged as unsupported, create an incompatibility entry
2. Set the `group_key` to enable batch resolution:
   - For unmapped tools: `unmapped_tool:{tool_name}` (same tool across locations groups together)
   - For unmapped fields: `unmapped_field:{field_name}`
   - For composition gaps: `unsupported_composition:{mechanism_type}`
   - For hook events: `unsupported_hook:{event_type}`
   - For general gaps: `general_gap:{feature_name}`
3. Populate `suggested_workaround` from adapter notes and research findings:
   - Check `CONVERSION_KNOWLEDGE` for notes about this specific feature
   - Check research findings for alternative approaches documented on the target platform
   - If both provide suggestions, prefer the more specific one (adapter notes if detailed, research if adapter is generic)
   - If neither provides a suggestion, set to `null`
4. Track all `affected_locations` so the resolution can be applied to every occurrence

---

## Workaround Suggestion Generation

When building the `suggested_workaround` for an incompatibility, follow this procedure to produce concrete, actionable suggestions.

### Source Priority

1. **Adapter notes** (highest priority): If the adapter's mapping table includes a `Notes` column entry for this feature, use it as the basis for the workaround
2. **Research findings** (second priority): If research documented an alternative approach or partial equivalent, use it
3. **Pattern-based inference** (fallback): If neither adapter nor research provide a suggestion, infer a workaround from the incompatibility category

### Pattern-Based Workarounds by Category

When no specific suggestion exists, use these default workarounds:

| Category | Default Workaround | Confidence |
|----------|-------------------|------------|
| Unmapped tool (in body) | Replace tool references with prose instructions describing the equivalent manual action | low |
| Unmapped tool (in `allowed-tools`) | Remove from tool list; document the capability loss | medium |
| Unmapped field (metadata) | Preserve as comment in the output file body | medium |
| Unmapped field (behavioral) | Inline the behavior description into the body text | low |
| Unsupported composition (same-plugin) | Inline the referenced content into this file | medium |
| Unsupported composition (cross-plugin) | Inline the referenced content or provide a manual copy instruction | low |
| Unsupported hook event | Document the hook's purpose and suggest manual alternatives (pre/post scripts, platform settings) | low |
| General gap (inter-agent) | Remove inter-agent instructions; restructure as single-agent workflow with TODO markers | low |
| General gap (task management) | Remove task management; document as a workflow limitation | low |
| General gap (MCP) | Document MCP servers used and suggest manual configuration on target platform | medium |

### Confidence Levels

| Level | Meaning | Presentation |
|-------|---------|-------------|
| **high** | Workaround is well-documented and verified by both adapter and research | Present without qualification |
| **medium** | Workaround is based on one source (adapter or research) or is a standard pattern | Present with note: "Based on {source}" |
| **low** | Workaround is inferred from patterns; may not fully replicate the feature | Present with note: "Best-effort suggestion -- verify on target platform" |
| **uncertain** | Workaround is speculative; the research found conflicting or incomplete information | Present with warning: "This workaround has not been verified -- research found limited information about this feature on {TARGET_PLATFORM}" |

---

## Resolution Flow

The resolver presents incompatibilities to the user through one of two paths: individual resolution or batch resolution, determined by the number and similarity of incompatibilities.

### Pre-Resolution: Grouping and Triage

Before presenting options, analyze the collected `COMPONENT_INCOMPATIBILITIES`:

1. **Group by `group_key`**: Combine entries with the same `group_key` into batches. For example, if `SendMessage` is referenced 5 times in the body, these become one batch entry with 5 affected locations.

2. **Count unique incompatibility groups**: This determines the resolution path.

3. **Sort groups by severity**: Present critical items first, then functional, then cosmetic.

4. **Auto-resolve cosmetic gaps**: Incompatibilities with `severity: "cosmetic"` that have a `suggested_workaround` with `confidence: "high"` or `confidence: "medium"` are auto-resolved using the workaround. Record the decision with `resolution_mode: "auto"`. Inform the user in the progress output:
   ```
   Auto-resolved {count} cosmetic incompatibilities (details in migration guide)
   ```

### Path A: Individual Resolution (5 or fewer unique groups after triage)

When 5 or fewer unique incompatibility groups remain after auto-resolution, present each one individually via `AskUserQuestion`.

For each incompatibility group:

```yaml
AskUserQuestion:
  questions:
    - header: "Incompatible Feature: {feature_name}"
      question: "{component.name}: '{feature_name}' has no direct equivalent on {TARGET_PLATFORM}. {reason}\n\n{If multiple locations: 'This affects {count} locations in the component.'}\n\n{If suggested_workaround: 'Suggested workaround ({confidence}): {workaround.description}'}"
      options:
        - label: "Use workaround"
          description: "{workaround.description} [{confidence} confidence{, source: workaround.source}]"
        - label: "Omit this feature"
          description: "Remove from converted output -- documented in gap report"
        - label: "Add as TODO comment"
          description: "Leave a placeholder: <!-- TODO [{TARGET_PLATFORM}]: {feature_name} -- {reason} -->"
      multiSelect: false
```

**When no workaround is available** (suggested_workaround is null):

```yaml
AskUserQuestion:
  questions:
    - header: "Incompatible Feature: {feature_name}"
      question: "{component.name}: '{feature_name}' has no direct equivalent on {TARGET_PLATFORM}. {reason}\n\nNo automated workaround is available for this feature."
      options:
        - label: "Omit this feature"
          description: "Remove from converted output -- documented in gap report"
        - label: "Add as TODO comment"
          description: "Leave a placeholder: <!-- TODO [{TARGET_PLATFORM}]: {feature_name} -- {reason} -->"
      multiSelect: false
```

### Path B: Batch Resolution (more than 5 unique groups after triage)

When more than 5 unique incompatibility groups remain, present a summary first to avoid overwhelming the user.

#### Step B1: Present Summary

```yaml
AskUserQuestion:
  questions:
    - header: "Multiple Incompatibilities in {component.name}"
      question: "{component.name} has {count} features without direct equivalents on {TARGET_PLATFORM}:\n\n{For each group, one line:}\n- {feature_name} ({severity}) -- {brief_reason}{, workaround available: yes/no}\n\nHow would you like to handle them?"
      options:
        - label: "Review each individually"
          description: "Pause on each incompatibility for case-by-case decisions ({count} prompts)"
        - label: "Apply workarounds where available, TODO for the rest"
          description: "Auto-apply: workaround if suggested ({workaround_count}), TODO comment for others ({no_workaround_count})"
        - label: "Omit all incompatible features"
          description: "Remove all {count} features from output -- documented in gap report"
        - label: "Review critical/functional only, auto-resolve cosmetic"
          description: "Individually review {critical_functional_count} important items; auto-apply workarounds or TODO for {cosmetic_count} cosmetic items"
      multiSelect: false
```

#### Step B2: Apply Batch Decision

- **"Review each individually"**: Fall through to Path A for every group
- **"Apply workarounds where available, TODO for the rest"**: For each group:
  - If `suggested_workaround` exists: apply the workaround, record `decision_type: "workaround"` with `resolution_mode: "batch"`
  - If no workaround: add a TODO comment, record `decision_type: "todo"` with `resolution_mode: "batch"`
- **"Omit all incompatible features"**: For each group:
  - Remove the feature from output, record `decision_type: "omitted"` with `resolution_mode: "batch"`
- **"Review critical/functional only, auto-resolve cosmetic"**:
  - For critical and functional severity groups: fall through to Path A
  - For cosmetic groups: apply workaround if available, TODO if not, with `resolution_mode: "batch"`

### Batch Resolution for Repeated Types Across Components

When the same incompatibility type appears in multiple components (e.g., `SendMessage` is unmapped and appears in 3 different agents), the resolver offers to apply the same decision globally.

**After the first resolution of a given `group_key`:**

Store the decision in a `RESOLUTION_CACHE`:

```
RESOLUTION_CACHE = {
  "unmapped_tool:SendMessage": {
    decision_type: "workaround",
    workaround_applied: "Removed inter-agent messaging references",
    component: "code-explorer",  -- where the decision was first made
    apply_globally: null          -- not yet asked
  }
}
```

**When the same `group_key` appears in a subsequent component:**

```yaml
AskUserQuestion:
  questions:
    - header: "Repeated Incompatibility"
      question: "'{feature_name}' was already resolved in {previous_component.name} (decision: {previous_decision_type}). Apply the same decision to {current_component.name}?"
      options:
        - label: "Apply same decision"
          description: "{previous_decision_description}"
        - label: "Apply to this and all future occurrences"
          description: "Use '{previous_decision_type}' for all remaining '{feature_name}' incompatibilities"
        - label: "Choose differently for this component"
          description: "Open the full resolution options for this instance"
      multiSelect: false
```

- **"Apply same decision"**: Reuse the cached resolution for this component only
- **"Apply to this and all future occurrences"**: Set `RESOLUTION_CACHE[group_key].apply_globally = true`. All future occurrences of this group_key are auto-resolved without prompting.
- **"Choose differently"**: Present the full resolution options (Path A) for this instance

---

## Applying Resolutions

After the user makes a decision, apply the resolution to the component's converted content.

### Workaround Application

1. Retrieve the `suggested_workaround.implementation` text
2. For each `affected_location` in the incompatibility:
   - Apply the workaround transformation to the converted content at that location
   - If the workaround modifies body text: replace the original pattern with the workaround text
   - If the workaround adds configuration: append to the config fragment
   - If the workaround restructures content: apply the structural change
3. Record in `CONVERSION_DECISIONS`:
   ```
   {
     component: component.name,
     feature: feature_name,
     decision_type: "workaround",
     original: original_content,
     converted: workaround_result,
     rationale: workaround.description,
     confidence: workaround.confidence,
     source: workaround.source,
     resolution_mode: "individual" | "batch" | "cached" | "auto",
     affected_count: affected_locations.length
   }
   ```

### Omission Application

1. For each `affected_location`:
   - Remove the feature from the converted content
   - If removing from frontmatter: delete the field
   - If removing from body text: delete the line or block referencing the feature
   - If removing from a list (e.g., `allowed-tools`): remove the entry from the list
   - Clean up any orphaned formatting (empty lists, trailing commas, blank sections)
2. Record in `CONVERSION_DECISIONS`:
   ```
   {
     component: component.name,
     feature: feature_name,
     decision_type: "omitted",
     original: original_content,
     converted: null,
     rationale: "User chose to omit -- no equivalent on {TARGET_PLATFORM}",
     resolution_mode: "individual" | "batch" | "cached",
     affected_count: affected_locations.length
   }
   ```
3. Add to `CONVERSION_GAPS`:
   ```
   {
     component: component.name,
     feature: feature_name,
     reason: reason,
     severity: severity,
     workaround: "Omitted by user decision",
     user_acknowledged: true
   }
   ```

### TODO Comment Application

1. For each `affected_location`:
   - Insert a TODO comment at the relevant location in the converted content
   - Format: `<!-- TODO [{TARGET_PLATFORM}]: {feature_name} -- {reason}. Original: {brief_original_snippet} -->`
   - If the original content is longer than 200 characters, truncate with `...`
   - Place the TODO comment:
     - For frontmatter fields: as a comment above where the field would have been
     - For body text references: inline, replacing the original reference
     - For composition patterns: at the location of the original `Read` directive
     - For hook entries: in the converted hook config or in a separate TODO list at the end of the file
2. Record in `CONVERSION_DECISIONS`:
   ```
   {
     component: component.name,
     feature: feature_name,
     decision_type: "todo",
     original: original_content,
     converted: todo_comment_text,
     rationale: "User chose TODO placeholder -- manual implementation needed",
     resolution_mode: "individual" | "batch" | "cached",
     affected_count: affected_locations.length
   }
   ```
3. Add to `CONVERSION_GAPS`:
   ```
   {
     component: component.name,
     feature: feature_name,
     reason: reason,
     severity: severity,
     workaround: "TODO comment added -- requires manual implementation",
     user_acknowledged: true
   }
   ```

---

## Cascading Impact Detection

When a resolution affects other components, the resolver warns the user before applying.

### When to Check for Cascading Impact

Check for cascading impact when:
1. A workaround modifies a feature that other selected components depend on
2. An omission removes a feature that other components reference
3. A composition pattern resolution changes how content is loaded, potentially affecting downstream components

### Cascade Detection Algorithm

After the user selects a resolution but before applying it:

1. **Check dependency graph**: Look up the current component in the dependency graph from Phase 3
2. **Identify dependents**: Find all components that depend on or reference the current component
3. **Check for feature references**: For each dependent component, check if it references the affected feature:
   - Tool references in body text
   - Skill loading patterns that reference this component
   - Agent `skills:` field that lists this component
4. **If dependents reference the affected feature**: Present a cascading impact warning

```yaml
AskUserQuestion:
  questions:
    - header: "Cascading Impact Warning"
      question: "Your decision on '{feature_name}' in {component.name} may affect {dependent_count} other component(s):\n\n{For each dependent:}\n- {dependent.name} ({dependent.type}) -- references {feature_name} in {location}\n\nProceed with this resolution?"
      options:
        - label: "Proceed"
          description: "Apply the resolution -- cascading effects will be handled when converting the dependent components"
        - label: "Choose differently"
          description: "Go back and select a different resolution for this incompatibility"
      multiSelect: false
```

If "Choose differently": return to the resolution options for this incompatibility.
If "Proceed": apply the resolution and note the cascading impact in `CONVERSION_DECISIONS` with an additional field: `cascading_impact: [list of affected component names]`.

---

## Decision Review

At any point during conversion, the user can review all decisions made so far. This is triggered via the batch resolution flow or by the conversion engine when it detects a large number of accumulated decisions.

### Decision Summary Format

Present a summary of all decisions made so far:

```
## Conversion Decisions So Far

**Component:** {current_component} ({n}/{total} in conversion order)
**Total decisions:** {count}

### By Resolution Type
- Workarounds applied: {count} ({with_high_confidence} high confidence, {with_low_confidence} low confidence)
- Features omitted: {count}
- TODO comments added: {count}
- Auto-resolved (cosmetic): {count}

### By Severity
- Critical incompatibilities resolved: {count}
- Functional incompatibilities resolved: {count}
- Cosmetic incompatibilities resolved: {count}

### Recent Decisions
{Last 5 decisions with component, feature, and resolution type}
```

### Review Trigger

The conversion engine should offer a decision review checkpoint:
- After every 10 decisions made (across all components)
- After completing a component with 3 or more individual resolutions
- At the transition between dependency levels in the conversion order

The review is informational only; the user can see what has been decided but cannot change past decisions (since the converted content has already been modified). Future occurrences of the same incompatibility type can still be resolved differently.

---

## Decision Persistence

All decisions are stored in `CONVERSION_DECISIONS` and `CONVERSION_GAPS` throughout the conversion process. These structures are resilient to later failures:

### Resilience Properties

1. **Append-only**: Decisions are appended to the tracking structures as they are made. They are never removed or overwritten during conversion.
2. **Component-scoped snapshots**: After each component completes conversion, its decisions are finalized. If a later component's conversion fails, earlier decisions remain intact.
3. **Gap report always available**: Even if the conversion process is interrupted, `CONVERSION_GAPS` contains all gaps identified up to the point of failure, and `CONVERSION_DECISIONS` contains all user decisions. These can be used to generate a partial gap report.
4. **Resolution cache survives**: The `RESOLUTION_CACHE` persists across components within the same conversion session, enabling batch resolution for repeated incompatibility types.

### Data Flow to Output

The decision and gap data flows to Phase 6 (Output & Reporting) as follows:

```
CONVERSION_DECISIONS --> MIGRATION-GUIDE.md
  - Per-component decision tables
  - Overall conversion strategy summary
  - Workaround explanations with confidence levels

CONVERSION_GAPS --> GAP-REPORT.md
  - Per-component gap entries with severity
  - Suggested workarounds and alternatives
  - Features requiring manual implementation (TODO items)

RESOLUTION_CACHE --> Conversion Session State
  - Not persisted to files
  - Used only within the conversion session for batch resolution
```

---

## Agent vs. Orchestrator Responsibility

When Phase 5 runs as a wave-based agent team (port-converter agents coordinated by the orchestrator), the incompatibility resolver's responsibilities split between two execution contexts:

### Converter Agent Responsibility (per-component, isolated context)

1. **Detection**: Identify all 5 categories of incompatibilities during conversion (unmapped tool, unmapped field, unsupported composition, unsupported hook, general gap)
2. **Severity classification**: Apply the severity heuristics (critical/functional/cosmetic) based on body occurrence count and role centrality
3. **Cosmetic auto-resolution**: Auto-resolve cosmetic gaps that have a suggested workaround with confidence "high" or "medium". Apply the workaround directly in the converted content. Record with `resolution_mode: "auto"` in the result file's Decisions table.
4. **Cache lookup**: Read `resolution_cache.md` and auto-apply any cached decision where `apply_globally = true`. Record with `resolution_mode: "cached"`.
5. **Inline marking**: For all remaining non-cosmetic incompatibilities (not cached or cached with `apply_globally = false`), insert inline markers in the converted content: `<!-- UNRESOLVED: {group_key} | {severity} | {feature_name} | {workaround_or_none} -->`
6. **Result file reporting**: List all unresolved incompatibilities in the result file's Unresolved Incompatibilities table with full context (group_key, feature, severity, category, reason, suggested workaround, confidence, affected location count)
7. **Workaround suggestion generation**: Build `suggested_workaround` entries using the same source priority (adapter notes > research findings > pattern-based inference) and confidence levels documented in this reference

### Orchestrator Responsibility (cross-component, main context)

1. **Batch collection**: After each wave completes, read all result files and collect `Unresolved Incompatibilities` across all agents in that wave
2. **Grouping**: Group collected incompatibilities by `group_key` across all wave results
3. **Cache check**: For each group, check `resolution_cache.md` for cached decisions not yet applied (entries with `apply_globally = false`)
4. **User interaction**: Present remaining unresolved incompatibilities to the user via `AskUserQuestion`, using the same resolution flow (individual for 5 or fewer groups, batch for more) documented in this reference
5. **Resolution application**: Replace `<!-- UNRESOLVED: ... -->` inline markers in result files with the applied resolution (workaround text, omission cleanup, or TODO comment)
6. **Cache management**: Update `resolution_cache.md` with new decisions. When a user chooses "Apply to this and all future occurrences", set `apply_globally = true` so subsequent waves auto-apply.
7. **Cascade impact detection**: Check the dependency graph for components in later waves that depend on the current wave's resolved components. Flag cascading impacts before applying resolutions.
8. **Decision review checkpoints**: Offer periodic decision reviews (after every 10 decisions, after a wave with 3+ individual resolutions, at wave transitions) as documented in the Decision Review section of this reference

---

## Integration with Conversion Engine

The incompatibility resolver is invoked by the porter skill's Phase 5 conversion engine. The integration points are:

### Invocation Points

1. **Skill conversion (Step 3)**: After frontmatter mapping, tool reference transformation, composition pattern handling, and AskUserQuestion transformation -- any feature returning `null` from the mappings triggers the resolver
2. **Agent conversion (Step 4)**: After the agent converter's Stage 4 (Handle Gaps) -- gaps classified as Medium or High severity are routed through the resolver
3. **Hook conversion (Step 5)**: After event type mapping -- unsupported events with Functional or Critical severity trigger the resolver
4. **Reference file conversion (Step 6)**: When a reference file's path resolution fails or the target has no reference directory concept
5. **MCP conversion (Step 7)**: When the target platform has no MCP support

### Invocation Protocol

Each converter calls the resolver by:

1. Collecting all incompatibilities for the current component into `COMPONENT_INCOMPATIBILITIES`
2. Passing the list to the resolver's Pre-Resolution grouping step
3. The resolver handles auto-resolution of cosmetic items and determines the resolution path (individual or batch)
4. The resolver presents options to the user and records decisions
5. The resolver returns the decisions to the converter, which applies the resolutions to the converted content

### Return Value

The resolver returns:

```
{
  decisions: [           -- Array of resolution decisions made
    {
      id: string,
      decision_type: "workaround" | "omitted" | "todo",
      resolution_mode: "individual" | "batch" | "cached" | "auto",
      workaround_applied: string | null,
      confidence: string | null,
      cascading_impact: string[] | null
    }
  ],
  auto_resolved_count: number,  -- Count of cosmetic items auto-resolved
  reviewed_count: number,       -- Count of items the user individually reviewed
  batch_resolved_count: number  -- Count of items resolved via batch decision
}
```

The converter uses these decisions to modify the converted content and append to `CONVERSION_DECISIONS` and `CONVERSION_GAPS`.
