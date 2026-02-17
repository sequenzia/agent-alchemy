# Reference File Converter

This reference defines the conversion logic for reference files during plugin porting. Reference files are markdown documents stored under `skills/{name}/references/` that contain knowledge bases, patterns, workflow guides, and supplementary content. They are loaded at runtime via `Read ${CLAUDE_PLUGIN_ROOT}/...` patterns in skill and agent bodies. The converter handles path transformation, tool and model name replacement, cross-plugin resolution, and content flattening for platforms that lack a composition mechanism.

---

## Overview

Reference file conversion operates in four stages:

```
1. Discovery    — Find all reference files in selected components
2. Analysis     — Parse loading patterns and cross-references
3. Transformation — Apply path, tool, and model name replacements
4. Output       — Copy to target structure or flatten/inline as needed
```

Each stage must complete before the next begins. The converter processes reference files after skills and agents have been analyzed (so that loading patterns are already known) but before final output is written (so that flattened content can be injected into skill files if needed).

---

## Stage 1: Discovery

Identify all reference files that belong to selected components.

### Primary Discovery

For each selected skill, scan its reference directory:

```
claude/{group}/skills/{skill-name}/references/**/*.md
```

Use `Glob` with the recursive pattern to capture all files, including those in subdirectories (e.g., `references/adapters/opencode.md`).

### Secondary Discovery

Scan all selected skill and agent bodies for `Read` patterns that reference files not found by primary discovery:

```
Read ${CLAUDE_PLUGIN_ROOT}/skills/{name}/references/{path}
Read ${CLAUDE_PLUGIN_ROOT}/../{group}/skills/{name}/references/{path}
```

Any referenced file not already in the discovered set should be added, with a flag indicating it is a cross-skill or cross-plugin reference.

### Discovery Output

Build a reference file manifest:

| Field | Type | Description |
|-------|------|-------------|
| `source_path` | string | Absolute path to the reference file |
| `relative_path` | string | Path relative to the skill directory (e.g., `references/tdd-workflow.md`) |
| `parent_skill` | string | The skill that owns this reference directory |
| `parent_group` | string | The plugin group the skill belongs to |
| `loaded_by` | list | Skills/agents that load this file via `Read` patterns |
| `is_cross_plugin` | boolean | Whether this file is referenced from another plugin group |
| `size_lines` | number | Line count for large-file handling |

### Deduplication

If the same reference file is loaded by multiple skills (e.g., `deep-analysis` references loaded by `codebase-analysis`, `feature-dev`, `docs-manager`, and `create-spec`), include it once in the manifest but track all consumers in the `loaded_by` list. This prevents duplicate copies in the output and ensures all loading patterns are updated consistently.

---

## Stage 2: Analysis

Parse each reference file and catalog the constructs that require transformation.

### Path References

Scan each reference file for path patterns that use `${CLAUDE_PLUGIN_ROOT}`:

| Pattern | Type | Example |
|---------|------|---------|
| `${CLAUDE_PLUGIN_ROOT}/skills/{name}/...` | Same-plugin reference | `${CLAUDE_PLUGIN_ROOT}/skills/deep-analysis/SKILL.md` |
| `${CLAUDE_PLUGIN_ROOT}/../{group}/skills/{name}/...` | Cross-plugin reference | `${CLAUDE_PLUGIN_ROOT}/../core-tools/skills/deep-analysis/SKILL.md` |
| `${CLAUDE_PLUGIN_ROOT}/agents/{name}.md` | Agent reference | `${CLAUDE_PLUGIN_ROOT}/agents/code-explorer.md` |
| `${CLAUDE_PLUGIN_ROOT}/../../.claude-plugin/...` | Registry reference | `${CLAUDE_PLUGIN_ROOT}/../../.claude-plugin/marketplace.json` |

Record each occurrence with its line number, the full pattern, and whether the referenced target is within the selected component set.

### Tool Name References

Scan for Claude Code tool names that appear in reference content. Tool names commonly appear in:

- Instructional text (e.g., "Use `Glob` to find files...")
- Code block examples (e.g., "`Read: path/to/file`")
- Inline references (e.g., "the Read tool")
- Tool lists (e.g., "Allowed tools: Read, Glob, Grep, Write")

Match tool names from the full tool inventory:

```
Read, Write, Edit, Glob, Grep, NotebookEdit, Bash, Task,
TeamCreate, TeamDelete, TaskCreate, TaskUpdate, TaskList, TaskGet, SendMessage,
AskUserQuestion, WebSearch, WebFetch,
mcp__context7__resolve-library-id, mcp__context7__query-docs
```

Use word-boundary matching to avoid false positives (e.g., do not match "Reading" when looking for "Read"). For inline code references (backtick-wrapped), match the exact tool name. For prose text, match tool names that appear as standalone capitalized words or in tool-listing contexts.

### Model Name References

Scan for Claude Code model tier names that appear in reference content:

```
opus, sonnet, haiku
```

These commonly appear in:

- Model tier descriptions (e.g., "Sonnet-tier for worker agents")
- Agent definitions within reference text (e.g., "model: sonnet")
- Architectural guidance (e.g., "Use Opus for synthesis tasks")

Match these case-insensitively when they refer to model tiers (not when they appear as unrelated words). Context clues: proximity to "model", "tier", "agent", capitalization as a proper noun (e.g., "Sonnet" vs. "a sonnet").

### Analysis Output

For each reference file, produce a transformation plan:

```
File: references/tdd-workflow.md
  Path references: 3
    Line 42: ${CLAUDE_PLUGIN_ROOT}/skills/tdd-cycle/SKILL.md -> [transform]
    Line 98: ${CLAUDE_PLUGIN_ROOT}/../sdd-tools/skills/create-tasks/SKILL.md -> [transform]
    Line 155: ${CLAUDE_PLUGIN_ROOT}/agents/tdd-executor.md -> [transform]
  Tool references: 5
    Line 29: `Glob` -> [map to target]
    Line 30: `Grep` -> [map to target]
    Line 45: `Read` -> [map to target]
    Line 67: `Bash` -> [map to target]
    Line 88: `Task` -> [map to target]
  Model references: 2
    Line 12: Opus -> [map to target]
    Line 13: Sonnet -> [map to target]
```

---

## Stage 3: Transformation

Apply replacements to reference file content using the adapter mappings.

### Path Reference Transformation

Read the adapter's **Path Resolution** section to determine the target path mechanism.

#### When `root_variable` is not null (target has a path variable)

Replace `${CLAUDE_PLUGIN_ROOT}` with the target's `root_variable`:

| Source Pattern | Target Pattern |
|---------------|---------------|
| `${CLAUDE_PLUGIN_ROOT}/skills/{name}/references/{file}` | `{root_variable}/{reference_dir}/{file}` |
| `${CLAUDE_PLUGIN_ROOT}/skills/{name}/SKILL.md` | `{root_variable}/{skill_dir}/{name}.{ext}` |
| `${CLAUDE_PLUGIN_ROOT}/agents/{name}.md` | `{root_variable}/{agent_dir}/{name}.{ext}` |
| `${CLAUDE_PLUGIN_ROOT}/../{group}/skills/{name}/...` | `{cross_plugin_pattern}` with group and name substituted |

Use the adapter's **Directory Structure** section to determine `skill_dir`, `agent_dir`, `reference_dir`, and `file_extension`.

#### When `root_variable` is null (no path variable)

The target platform does not support path-based file references. Options depend on the adapter's `resolution_strategy`:

| Strategy | Action |
|----------|--------|
| `relative` | Convert to relative paths from the reference file's output location |
| `absolute` | Convert to absolute paths using the `same_plugin_pattern` from the adapter |
| `registry` | Replace file paths with registry name/ID references |

If the adapter's `resolution_strategy` does not support the reference pattern (e.g., `relative` strategy with cross-plugin references), flag the path as a conversion gap and add a TODO comment.

### Tool Name Replacement

Read the adapter's **Tool Name Mappings** section. For each tool reference found in Stage 2:

| Mapping Value | Action |
|--------------|--------|
| Direct mapping (e.g., `view`) | Replace the tool name in text |
| `null` | Replace with descriptive text (e.g., "`Read`" becomes "`[no equivalent]`") and add a TODO comment |
| `partial:{name}` | Replace with the target name and append a note about limitations |
| `composite:{a}+{b}` | Replace with the composite name and add a clarifying comment |

#### Replacement Rules

1. **Backtick-wrapped tool names** (e.g., `` `Read` ``): Replace the name inside backticks with the target equivalent. Keep backticks.
2. **Prose references** (e.g., "the Read tool"): Replace the tool name. Adjust casing to match the target convention (e.g., "Read" to "view" if the target uses lowercase).
3. **Tool lists** (e.g., "Read, Glob, Grep"): Replace each tool name individually. Remove tools that map to `null` and add a note about removed tools.
4. **Code block examples**: Replace tool names in code blocks. If the example syntax changes between platforms (e.g., `Read: path` vs `view path`), adjust the syntax based on the target's conventions documented in the adapter.
5. **MCP tool references** (e.g., `mcp__context7__resolve-library-id`): Replace using the adapter's MCP tool naming convention (e.g., `context7_resolve-library-id` for OpenCode).

### Model Name Replacement

Read the adapter's **Model Tier Mappings** section. For each model reference found in Stage 2:

| Source | Replacement |
|--------|------------|
| `opus` / `Opus` | Target equivalent from adapter (e.g., `claude-4-opus`) |
| `sonnet` / `Sonnet` | Target equivalent from adapter (e.g., `claude-4-sonnet`) |
| `haiku` / `Haiku` | Target equivalent from adapter (e.g., `claude-3.5-haiku`) |

#### Replacement Rules

1. **Model tier labels** (e.g., "Opus-tier", "Sonnet-tier"): Replace the tier name and adjust phrasing if the target uses model IDs instead of tier names (e.g., "Opus-tier" becomes "claude-4-opus-tier" or is rewritten as "high-capability model").
2. **Frontmatter-style references** (e.g., `model: sonnet`): Replace with the target model ID.
3. **Architectural guidance** (e.g., "Use Opus for synthesis"): Replace the model name. If the target does not support model selection (`null` mapping), add a note that model selection is not configurable on the target platform.
4. **Preserve context**: When model names appear in explanatory text about why a particular tier is used, preserve the explanation but update the model identifier.

### Cross-Plugin Reference Resolution

When a reference file contains cross-plugin references (`${CLAUDE_PLUGIN_ROOT}/../{group}/...`):

1. **Check if the referenced component is in the selected set**: If yes, transform the path to the target's cross-plugin pattern (from the adapter's Path Resolution section).
2. **Check if the target supports cross-plugin references** (adapter's `supports_cross_plugin` field in Composition Mechanism):
   - If `true`: Transform using the `cross_plugin_pattern`
   - If `false`: Flag as a conversion gap. Add a TODO comment explaining that the reference cannot be resolved on the target platform.
3. **If the referenced component is NOT in the selected set**: Flag as a missing dependency. Add a TODO comment: `TODO: This reference points to {component} which was not included in the conversion. Port this component separately or inline the needed content.`

---

## Stage 4: Output

Write transformed reference files to the target structure, or flatten them into parent skill files.

### Decision: Copy vs. Flatten

Read the adapter's **Composition Mechanism** section to determine the output strategy:

| Mechanism | Strategy |
|-----------|----------|
| `import` | Copy reference files to target structure; convert `Read` patterns to import syntax |
| `include` | Copy reference files to target structure; place in auto-include directory |
| `reference` | Copy reference files; convert `Read` patterns to name/ID references |
| `inline` | Flatten reference content into the consuming skill file |
| `none` | Flatten reference content into the consuming skill file |

### Copy Strategy (mechanism: import, include, reference)

When the target platform supports some form of file composition:

1. **Create the target directory structure** using the adapter's `reference_dir` path:
   ```
   {output_dir}/{plugin_root}/{reference_dir}/{file}
   ```

2. **Preserve relative hierarchy**: If the source has nested reference directories (e.g., `references/adapters/opencode.md`), mirror the hierarchy in the target unless the adapter notes state that subdirectories are unsupported.

3. **Update loading patterns** in the parent skill/agent:
   - Replace `Read ${CLAUDE_PLUGIN_ROOT}/skills/{name}/references/{file}` with the target's composition syntax
   - Example for `import` mechanism: `@import "{reference_dir}/{file}"`

4. **Write the transformed reference file** to the target location.

### Flatten Strategy (mechanism: inline, none)

When the target platform has no composition mechanism and reference content must be inlined:

1. **Determine the insertion point**: Find where the `Read ${CLAUDE_PLUGIN_ROOT}/.../references/{file}` pattern appears in the parent skill body. This is where the reference content should be inserted.

2. **Add section delimiters**: Wrap the inlined content with clear boundaries so the user can identify what was flattened:

   ```markdown
   <!-- BEGIN INLINED REFERENCE: {original-relative-path} -->

   {transformed reference content}

   <!-- END INLINED REFERENCE: {original-relative-path} -->
   ```

3. **Remove the original loading pattern**: Delete or comment out the `Read ${CLAUDE_PLUGIN_ROOT}/...` line since the content is now inlined.

4. **Handle multiple references**: If a skill loads multiple reference files, inline them in the order they appear in the skill body.

5. **Handle large references**: For reference files exceeding 500 lines:
   - Still inline the full content (do not truncate)
   - Add a warning comment at the insertion point: `<!-- WARNING: Large inlined reference ({line_count} lines). Consider extracting to a project-level context file (e.g., OpenCode.md) if the combined file is too large for the target platform's context window. -->`
   - Record the large file in the migration guide with a recommendation to consider alternative placement

6. **Handle shared references**: When a reference file is loaded by multiple skills:
   - Inline the content into each consuming skill
   - Add a comment noting the duplication: `<!-- NOTE: This content is also inlined in {other-skill-files}. Changes should be applied to all copies. -->`
   - Record the duplication in the migration guide with a recommendation to use the target platform's project context mechanism (if available) for shared content

### Reference Files Not Loaded by Any Selected Skill

If a reference file is discovered in a selected skill's `references/` directory but is not loaded by any `Read` pattern in the selected components:

- Include the file in the output using the copy strategy (if the target supports file composition)
- Include the file as an appendix in the parent skill using the flatten strategy
- Add a note in the migration guide: "Reference file `{name}` was found in the skill directory but no loading pattern was detected. It has been included for completeness."

---

## Error Handling

### Missing Reference File

If a `Read` pattern in a skill body references a file that does not exist on disk:

1. Log a warning: `WARNING: Reference file not found: {path}`
2. Add a TODO comment in the converted skill at the `Read` line: `TODO: Referenced file {path} was not found during conversion. Verify the reference path.`
3. Continue processing other reference files without aborting

### Unresolvable Cross-Plugin Reference

If a cross-plugin reference points to a plugin group that is not available in the codebase:

1. Log a warning: `WARNING: Cross-plugin reference to unavailable group: {group}`
2. Add a TODO comment in the converted content
3. Record in the gap report with severity "functional"

### Permission or I/O Errors

If a reference file cannot be read due to permission issues or other I/O errors:

1. Log the error with the file path
2. Skip the file and continue
3. Record the skipped file in the migration guide

---

## Fidelity Scoring Impact

Reference file conversion affects the overall fidelity score for a component. The scoring adjustments:

| Outcome | Score Impact |
|---------|-------------|
| Reference copied with all paths/tools/models transformed | No penalty |
| Reference flattened (platform has no composition) | -5% per reference (minor structural loss) |
| Reference has unresolvable cross-plugin references | -10% per unresolved reference |
| Reference file missing from disk | -10% per missing file |
| Large reference inlined with duplication across skills | -5% (maintainability concern) |
| Shared reference extracted to project context file | No penalty (valid alternative) |

---

## Integration with Conversion Engine

The reference converter integrates with the porter skill's Phase 5 (Interactive Conversion) as follows:

1. **After skill/agent analysis**: The conversion engine calls the reference converter's Discovery and Analysis stages to build the reference manifest.
2. **During component conversion**: When converting a skill that loads references, the conversion engine checks the reference manifest for transformation plans.
3. **For flatten strategy**: The conversion engine passes the transformed reference content back to the skill converter for inline injection.
4. **For copy strategy**: The conversion engine writes the transformed reference files alongside the converted skill files.
5. **Fidelity scoring**: The reference converter reports its scoring adjustments to the conversion engine for inclusion in the per-component fidelity score.

### Conversion Order

Reference files should be processed after all skills and agents have been analyzed but before final output:

```
1. Skills analyzed (loading patterns extracted)
2. Agents analyzed (skill references extracted)
3. Reference converter runs (Discovery -> Analysis -> Transformation)
4. Output phase (reference files written or injected into skills)
```

This ordering ensures that all loading patterns are known before references are processed, and that flattened content is available for injection into skill files during output.
