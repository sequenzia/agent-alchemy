# Conversion Result: skill-sdd-tools-analyze-spec

## Metadata

| Field | Value |
|-------|-------|
| Component ID | skill-sdd-tools-analyze-spec |
| Component Type | skill |
| Group | sdd-tools |
| Name | analyze-spec |
| Source Path | claude/sdd-tools/skills/analyze-spec/SKILL.md |
| Target Path | skills/analyze-spec.md |
| Fidelity Score | 54% |
| Fidelity Band | yellow |
| Status | partial |

## Converted Content

~~~markdown
---
description: Analyze an existing spec for inconsistencies, missing information, ambiguities, and structure issues. Use when user says "analyze spec", "review spec", "spec quality check", "validate requirements", "audit spec", or "check spec quality".
user-invocable: true
---

# Spec Analysis Skill

You are initiating the spec analysis workflow. This process will analyze an existing spec for quality issues and optionally guide the user through resolving them interactively.

**Usage:** Provide the path to the spec file to analyze as an argument: `analyze-spec [spec-path]`

The spec path is available as `$ARGUMENTS` (or `$1` for the first argument).

## Workflow

### Step 1: Validate File

Verify the spec file exists at the provided path (`$ARGUMENTS`). If not found:
- Check if user provided relative path and try common locations
- Use glob to search for similar filenames
- Ask user for correct path if needed

### Step 2: Read Spec Content

Read the entire spec file using the read tool.

### Step 3: Detect Depth Level

Analyze the spec content to detect its depth level:

**Full-Tech Indicators** (check first):
- Contains `API Specifications` section OR `### 7.4 API` or similar
- Contains API endpoint definitions (`POST /api/`, `GET /api/`, etc.)
- Contains `Testing Strategy` section
- Contains data model schemas

**Detailed Indicators**:
- Uses numbered sections (`## 1.`, `### 2.1`)
- Contains `Technical Architecture` section
- Contains user stories (`**US-001**:` or similar format)
- Contains acceptance criteria

**High-Level Indicators**:
- Contains feature table with Priority column
- Executive summary focus
- No user stories or acceptance criteria
- Shorter document (~50-100 lines)

**Detection Priority**:
1. If Full-Tech indicators found → Full-Tech
2. Else if Detailed indicators found → Detailed
3. Else if High-Level indicators found → High-Level
4. Default → Detailed

### Step 4: Check Settings

Check for settings at `.claude/agent-alchemy.local.md` to get:
- Author name (if configured)
- Any custom preferences

### Step 5: Determine Report Paths

The analysis outputs should be saved in the same directory as the spec:

- Spec: `specs/SPEC-User-Auth.md`
- Report: `specs/SPEC-User-Auth.analysis.md`
- HTML Review: `specs/SPEC-User-Auth.analysis.html`

Extract the spec filename and construct both output paths.

### Step 6: Launch Analyzer Agent

<!-- UNRESOLVED: general_gap:question_tool_subagent | functional | question tool not available in subagents | Note about primary-agent-only constraint; pre-specify params for subagent contexts -->

> **Note (cached workaround — general_gap:question_tool_subagent):** The `question` tool (equivalent to AskUserQuestion) is only available to primary agents in opencode, not to subagents spawned via task. The spec-analyzer agent below is a subagent and cannot use the question tool directly. To work around this, any user interaction required during analysis (review mode selection, finding resolution choices) must be pre-specified in the task prompt or handled by this primary skill before launching the agent. If interactive resolution is needed, consider collecting user preferences (e.g., preferred review mode) via `question` in this skill before spawning the agent, then passing those preferences in the task prompt.

Launch the Spec Analyzer Agent using the task tool with the `spec-analyzer` custom agent.

```
task({
  description: "Analyze spec and generate quality report",
  prompt: "...",
  subagent_type: "build",
  command: "spec-analyzer"
})
```

Provide this context in the prompt:

```
Analyze the spec at: {spec_path}

Spec Content:
{full_spec_content}

Detected Depth Level: {depth_level}
Report Output Path: {report_path}
HTML Review Path: {html_review_path}
<!-- TODO: reference_dir is null in opencode — the HTML template at skills/analyze-spec/templates/review-template.html cannot be auto-loaded. Inline the template content into this prompt or load it with read before spawning the agent. See general_gap:reference_dir. -->
HTML Template Path: skills/analyze-spec/templates/review-template.html
Author: {author_from_settings or "Not specified"}

Instructions:
1. Load the analysis skill, reference files, and HTML review guide
<!-- TODO: reference_dir is null in opencode — reference files (analysis-criteria.md, report-template.md, common-issues.md, html-review-guide.md) cannot be auto-discovered. Inline their content into this prompt, or use read to load them before launching. See general_gap:reference_dir. -->
2. Perform systematic analysis based on the depth level
3. Generate the analysis report (.analysis.md)
4. Generate the interactive HTML review (.analysis.html)
5. Present findings summary
6. Ask user to choose review mode (HTML review, CLI update, or reports only)
7. Handle chosen mode accordingly
8. Update report with final resolution status
```

### Step 7: Handoff Complete

Once you have launched the Analyzer Agent, your role is complete. The agent will handle:
- Loading analysis criteria for the depth level
- Performing comprehensive analysis
- Generating and saving the report (.analysis.md)
- Generating the interactive HTML review (.analysis.html)
- Offering three review modes: HTML review, CLI update, or reports only
- Updating the spec with approved changes

## Example Usage

```
/analyze-spec specs/SPEC-User-Authentication.md
```

This will:
1. Read the spec at the specified path
2. Detect it's a Detailed-level spec
3. Analyze for issues across all four categories
4. Save report to `specs/SPEC-User-Authentication.analysis.md`
5. Offer interactive resolution mode

## Notes

- Always read the full spec before launching the analyzer
- Depth detection determines which criteria apply
- Report is always saved alongside the spec
- The analyzer agent handles all user interaction for resolution

---

## Analysis Philosophy

### Depth-Aware Analysis

Spec analysis must respect the intended depth level of the document. A high-level spec should not be flagged for missing API specifications, just as a full-tech spec should be scrutinized for technical completeness.

**Key Principle**: Only flag what's expected at the document's depth level.

### Constructive Approach

Findings should be:
- **Actionable**: Clear recommendation for how to fix
- **Specific**: Exact location and description of issue
- **Prioritized**: Severity indicates importance
- **Helpful**: Explain why this matters, not just what's wrong

### Systematic Coverage

Analysis covers four distinct categories to ensure comprehensive review:
1. **Inconsistencies**: Internal contradictions or mismatches
2. **Missing Information**: Expected content that's absent
3. **Ambiguities**: Unclear or vague statements
4. **Structure Issues**: Formatting, organization, missing sections

---

## Finding Categories

### 1. Inconsistencies

Issues where the spec contradicts itself or uses conflicting information.

**What to Look For**:
- Feature named differently in different sections
- Priority mismatches (feature marked P2 but in Phase 1)
- Metrics that don't align with stated goals
- Contradictory requirements
- Timeline/phase misalignment

**Detection Strategy**:
1. Build glossary of feature names from first mention
2. Track priority assignments
3. Map goals to metrics
4. Compare requirements for conflicts

### 2. Missing Information

Expected content that is absent based on the spec's depth level.

**What to Look For**:
- Required sections for depth level
- Undefined technical terms
- Features without acceptance criteria (detailed/full-tech)
- Error scenarios not addressed
- Dependencies not listed
- Incomplete personas

**Detection Strategy**:
1. Compare against depth-level checklist
2. Identify domain terms without definitions
3. Check each feature for expected attributes
4. Scan for external system references

### 3. Ambiguities

Statements that are unclear or could be interpreted multiple ways.

**What to Look For**:
- Vague quantifiers ("fast", "many", "scalable")
- Undefined priority language ("should" vs "must")
- Ambiguous pronouns ("it", "this", "they")
- Open-ended lists ("etc.", "and more")
- Undefined scope boundaries

**Detection Strategy**:
1. Flag quantifiers without numbers
2. Check for RFC 2119 language consistency
3. Identify pronouns with unclear antecedents
4. Find incomplete enumerations

### 4. Structure Issues

Problems with document organization, formatting, or references.

**What to Look For**:
- Missing required sections
- Content in wrong section
- Inconsistent formatting
- Orphaned references
- Circular dependencies

**Detection Strategy**:
1. Verify all template sections exist
2. Check content placement logic
3. Validate formatting consistency
4. Test all internal references

---

## Severity Levels

### Critical

**Definition**: Issues that would cause implementation to fail or go significantly wrong.

**Assign When**:
- Fundamental contradiction in requirements
- Core requirement completely undefined
- Required section missing entirely
- Circular dependencies that block implementation
- Security requirement absent (when security is mentioned)

**Examples**:
- "User authentication required" but no auth requirements defined
- Feature A depends on Feature B, Feature B depends on Feature A
- Full-tech spec with no API specifications

### Warning

**Definition**: Issues that could cause confusion or implementation problems.

**Assign When**:
- Inconsistent naming that could cause misunderstanding
- Acceptance criteria too vague to test
- Important feature lacks error handling
- Ambiguous language for significant functionality
- Minor dependencies unlisted

**Examples**:
- "Search should be fast" without defining "fast"
- User story without acceptance criteria
- Integration mentioned but not in dependencies

### Suggestion

**Definition**: Improvements that would enhance spec quality but aren't blocking.

**Assign When**:
- Style or clarity improvements
- Non-critical sections could be clearer
- Best practices not followed
- Minor formatting inconsistencies
- Documentation enhancements

**Examples**:
- User stories formatted inconsistently
- Glossary would help but isn't critical
- Additional context would be helpful

---

## Analysis Workflow

### Step 1: Read and Detect Depth

1. Read the entire spec
2. Detect depth level using indicators
<!-- TODO: reference_dir is null in opencode — the file references/analysis-criteria.md (depth detection indicators) cannot be auto-loaded. Inline its content into the skill body or read it explicitly before the agent uses it. See general_gap:reference_dir. -->
3. Note the detected depth for criteria selection

### Step 2: Load Criteria

<!-- TODO: reference_dir is null in opencode — the file references/analysis-criteria.md (depth-specific checklists) cannot be auto-loaded. Its content must be inlined into this skill or passed in the task prompt. See general_gap:reference_dir. -->
Load the appropriate checklist from `references/analysis-criteria.md` based on detected depth level.

### Step 3: Systematic Scan

Analyze the spec section by section:

1. **Structure Scan**: Verify all required sections exist
2. **Consistency Scan**: Build glossary, track priorities, map goals to metrics
3. **Completeness Scan**: Check each feature for expected attributes
4. **Clarity Scan**: Flag vague language and ambiguities

### Step 4: Categorize and Prioritize

For each finding:
1. Assign to one of four categories
2. Determine severity based on impact
3. Identify specific location (section, line)
4. Draft recommendation

### Step 5: Generate Report

<!-- TODO: reference_dir is null in opencode — the file references/report-template.md cannot be auto-loaded. Inline the report template content directly into this skill body or pass it via the task prompt. See general_gap:reference_dir. -->
Create report using `references/report-template.md`:
1. Fill in header information
2. Calculate summary statistics
3. List findings by severity
4. Write overall assessment

---

## Update Mode Workflow

When entering update mode for interactive resolution:

### Finding Presentation

Present each finding with:
```
FINDING X/Y (N resolved, M skipped)

Category: {category}
Severity: {severity}
Location: {section, line}

CURRENT:
{Quoted text from spec}

ISSUE:
{Clear explanation of the problem}

PROPOSED:
{Suggested fix text}

[Apply] [Modify] [Skip]
```

### User Response Handling

**Apply**:
1. Use edit tool to apply the proposed change
2. Mark finding as "Resolved" in report
3. Increment resolved counter
4. Move to next finding

**Modify**:
1. Ask user for their preferred text via question tool
2. Apply their modified version
3. Mark finding as "Resolved"
4. Move to next finding

**Skip**:
1. Ask if they want to provide a reason (optional)
2. Mark finding as "Skipped" with reason if provided
3. Increment skipped counter
4. Move to next finding

### Session Completion

After all findings processed:
1. Update report with Resolution Summary
2. Show final statistics
3. List resolved and skipped findings
4. Provide recommendations for future specs

---

## Reference Files

<!-- TODO: reference_dir is null in opencode — none of these reference files can be auto-discovered or loaded by path. All reference content must be inlined into this skill body or read explicitly and injected into task prompts before spawning the spec-analyzer agent. See general_gap:reference_dir (cached: apply globally). -->
- `references/analysis-criteria.md` - Depth-specific checklists and detection algorithms
- `references/report-template.md` - Standard report format
- `references/common-issues.md` - Issue pattern library with examples
- `references/html-review-guide.md` - HTML review generation instructions and data schemas
- `templates/review-template.html` - Self-contained interactive HTML review template
~~~

## Fidelity Report

| Mapping Type | Count | Weight | Contribution |
|-------------|-------|--------|-------------|
| Direct | 6 | 1.0 | 6.0 |
| Workaround | 3 | 0.7 | 2.1 |
| TODO | 5 | 0.2 | 1.0 |
| Omitted | 3 | 0.0 | 0.0 |
| **Total** | **17** | | **9.1 / 17 = 53.5% → 54%** |

**Notes:** The 5 TODO items are all reference file dependencies (4 reference files + 1 HTML template). These are structural gaps caused by opencode having no reference_dir concept. The workarounds require manually inlining reference content into the skill body — significant manual work but the core workflow logic is fully preserved. The question tool subagent constraint is addressed via cached workaround note in the body.

## Decisions

| Feature | Decision Type | Original | Converted | Rationale | Confidence | Resolution Mode |
|---------|-------------|----------|-----------|-----------|------------|----------------|
| `name` field | relocated | `name: analyze-spec` | Derived from filename `analyze-spec.md` | name maps to embedded:filename in opencode | high | auto |
| `description` field | direct | `description: Analyze an existing spec...` | `description: Analyze an existing spec...` | Direct 1:1 mapping | high | N/A |
| `argument-hint` field | relocated | `argument-hint: "[spec-path]"` | Inline $ARGUMENTS/$1 usage instructions in body | argument-hint maps to embedded:body | high | auto |
| `user-invocable` field | direct | `user-invocable: true` | `user-invocable: true` | Direct 1:1 mapping | high | N/A |
| `disable-model-invocation` field | omitted | `disable-model-invocation: false` | (removed) | Maps to null; not supported in opencode | high | auto |
| `allowed-tools` field | omitted | `allowed-tools: AskUserQuestion, Task, Read, Glob` | (removed) | No per-skill tool restrictions in opencode; agent-level only | high | auto |
| `arguments` block | omitted | `arguments: [{name: spec-path, ...}]` | (removed) | No structured argument declaration in opencode skill frontmatter | high | auto |
| `Read` tool reference | direct | `Read tool` | `read` | Direct tool name mapping | high | N/A |
| `Glob` tool reference | direct | `Glob` | `glob` | Direct tool name mapping | high | N/A |
| `Task` tool reference | direct | `Task tool` | `task` | Direct tool name mapping; added command: "spec-analyzer" syntax note | high | N/A |
| `AskUserQuestion` reference | direct | `AskUserQuestion` | `question` | Direct tool name mapping | high | N/A |
| `general_gap:question_tool_subagent` | workaround | AskUserQuestion in spec-analyzer subagent context | Cached workaround note; pre-specify interaction params before spawning | question tool not available in subagents; cached decision apply_globally=true | high | cached |
| `references/analysis-criteria.md` | todo | File path reference | TODO comment to inline or read explicitly | reference_dir is null; cached general_gap:reference_dir apply_globally=true | high | cached |
| `references/report-template.md` | todo | File path reference | TODO comment to inline or read explicitly | reference_dir is null; cached general_gap:reference_dir apply_globally=true | high | cached |
| `references/common-issues.md` | todo | File path reference | TODO comment to inline or read explicitly | reference_dir is null; cached general_gap:reference_dir apply_globally=true | high | cached |
| `references/html-review-guide.md` | todo | File path reference | TODO comment to inline or read explicitly | reference_dir is null; cached general_gap:reference_dir apply_globally=true | high | cached |
| `templates/review-template.html` | todo | File path reference in task prompt | TODO comment to inline template before spawning agent | reference_dir is null; no path-based loading | high | cached |

## Gaps

| Feature | Reason | Severity | Workaround | User Acknowledged |
|---------|--------|----------|------------|-------------------|
| `disable-model-invocation` field | No equivalent in opencode skill frontmatter | cosmetic | Remove from frontmatter; has no behavioral impact (was false) | false |
| `allowed-tools` field | No per-skill tool restrictions in opencode; agent-level permission only | cosmetic | Remove from frontmatter; tools remain accessible at agent level | false |
| `arguments` structured declaration | No structured argument declaration in opencode skill frontmatter | functional | Argument documented inline in skill body using $ARGUMENTS pattern | false |
| Reference file: `references/analysis-criteria.md` | opencode has no reference_dir; files cannot be auto-loaded by skill | functional | Inline content into skill body or read explicitly and inject into task prompt | false |
| Reference file: `references/report-template.md` | opencode has no reference_dir; files cannot be auto-loaded by skill | functional | Inline content into skill body or read explicitly and inject into task prompt | false |
| Reference file: `references/common-issues.md` | opencode has no reference_dir; files cannot be auto-loaded by skill | functional | Inline content into skill body or read explicitly and inject into task prompt | false |
| Reference file: `references/html-review-guide.md` | opencode has no reference_dir; files cannot be auto-loaded by skill | functional | Inline content into skill body or read explicitly and inject into task prompt | false |
| Template file: `templates/review-template.html` | opencode has no reference_dir; template cannot be path-referenced from skill | functional | Read template explicitly and pass content in task prompt before spawning agent | false |
| `question` tool in spec-analyzer subagent | question tool only available to primary agents; spec-analyzer is a subagent | functional | Pre-collect user interaction preferences in primary skill before spawning; pass via task prompt | false |

## Unresolved Incompatibilities

All incompatibilities for this component were resolved via cached decisions (apply_globally = true from prior wave conversions). No items require orchestrator resolution.

| Group Key | Feature | Severity | Category | Reason | Suggested Workaround | Confidence | Affected Locations |
|-----------|---------|----------|----------|--------|---------------------|------------|-------------------|
| (none — all resolved via cache) | | | | | | | |
