# Conversion Result: skill-core-tools-codebase-analysis

## Metadata

| Field | Value |
|-------|-------|
| Component ID | skill-core-tools-codebase-analysis |
| Component Type | skill |
| Group | core-tools |
| Name | codebase-analysis |
| Source Path | claude/core-tools/skills/codebase-analysis/SKILL.md |
| Target Path | .opencode/skills/codebase-analysis.md |
| Fidelity Score | 87% |
| Fidelity Band | green |
| Status | full |

## Converted Content

~~~markdown
---
description: Execute a structured codebase exploration workflow to gather insights. Use when asked to "analyze codebase", "explore codebase", "understand this codebase", or "map the codebase".
user-invocable: true
---

<!-- NOTE: disable-model-invocation has no equivalent in opencode. This skill is always available to the model. To restrict invocation to user-only contexts, document the constraint in the description and enforce at the agent level via permission config. (resolution_mode: cached, group_key: unmapped_field:disable-model-invocation) -->

<!-- NOTE: allowed-tools field has no per-skill equivalent in opencode. Tool permissions are enforced at the agent level via permission config in the agent's .md frontmatter. -->

<!-- NOTE: TeamCreate and TeamDelete have no equivalent in opencode. Agent team coordination in the deep-analysis dependency is restructured as parallel task calls. See the converted deep-analysis skill for details. (resolution_mode: cached, group_key: unmapped_tool:TeamCreate / unmapped_tool:TeamDelete) -->

<!-- NOTE: SendMessage has no equivalent in opencode. Inter-agent messaging is replaced by embedding all required context directly in task prompts at dispatch time. (resolution_mode: cached, group_key: unmapped_tool:SendMessage) -->

<!-- NOTE: TaskCreate/TaskUpdate/TaskList/TaskGet are partially mapped to todowrite/todoread in opencode. These are session-scoped scratchpads with no dependency tracking, no owner assignment, and no per-task retrieval by ID. (resolution_mode: cached) -->

# Codebase Analysis Workflow

Invoke this skill with: `/codebase-analysis <analysis-context or feature-description>`
(Replace `$ARGUMENTS` with your analysis context or feature description when invoking.)

Execute a structured 3-phase codebase analysis workflow to gather insights.

**CRITICAL: Complete ALL 3 phases.** The workflow is not complete until Phase 3: Post-Analysis Actions is finished. After completing each phase, immediately proceed to the next phase without waiting for user prompts.

## Phase Overview

1. **Deep Analysis** — Explore and synthesize codebase findings via deep-analysis skill
2. **Reporting** — Present structured analysis to the user
3. **Post-Analysis Actions** — Save, document, or retain analysis insights

---

## Phase 1: Deep Analysis

**Goal:** Explore the codebase and synthesize findings.

1. **Determine analysis context:**
   - If `$ARGUMENTS` is provided, use it as the analysis context
   - If no arguments, set context to "general codebase understanding"

2. **Run deep-analysis workflow:**
   - Invoke `skill({ name: "deep-analysis" })` and follow its workflow
   - Pass the analysis context from step 1
   - This handles reconnaissance, team planning, approval (auto-approved when skill-invoked), parallel exploration (code-explorer task agents), and synthesis (code-synthesizer task agent)
   - **Note:** Deep-analysis may return cached results if a valid exploration cache exists. In skill-invoked mode, cache hits are auto-accepted — this is expected behavior that avoids redundant exploration.

3. **Verify results:**
   - Ensure the synthesis covers the analysis context adequately
   - If critical gaps remain, use `glob`/`grep` to fill them directly

---

## Phase 2: Reporting

**Goal:** Present a structured analysis to the user.

1. **Load report template:**

   <!-- NOTE: reference_dir is null in opencode. The report-template.md reference file cannot be loaded via path. The template structure is inlined below. (resolution_mode: cached, group_key: unsupported_composition:reference_dir_null) -->

   Use the following report structure to format the presentation:

   **Report Structure (inlined from references/report-template.md):**
   - **Executive Summary** — Lead with the most important finding (1-2 paragraphs)
   - **Architecture Overview** — How the codebase is structured (directory layout, key modules, data flow)
   - **Critical Files** — The 5-10 most important files with details (path, role, why it matters)
   - **Patterns & Conventions** — Recurring patterns and coding conventions (naming, structure, idioms)
   - **Relationship Map** — How components connect to each other (dependencies, integrations, data flows)
   - **Challenges & Risks** — Technical risks and complexity hotspots (table: Challenge | Severity | Impact)
   - **Recommendations** — Actionable next steps (numbered list, each with rationale)

2. **Present the analysis:**
   Structure the report with these sections:
   - **Executive Summary** — Lead with the most important finding
   - **Architecture Overview** — How the codebase is structured
   - **Critical Files** — The 5-10 most important files with details
   - **Patterns & Conventions** — Recurring patterns and coding conventions
   - **Relationship Map** — How components connect to each other
   - **Challenges & Risks** — Technical risks and complexity hotspots
   - **Recommendations** — Actionable next steps

3. **IMPORTANT: Proceed immediately to Phase 3.**
   Do NOT stop here. Do NOT wait for user input. The report is presented, but the workflow requires Post-Analysis Actions. Continue directly to Phase 3 now.

---

## Phase 3: Post-Analysis Actions

**Goal:** Let the user save, document, or retain analysis insights from the report.

1. **Present action menu:**

   Use the `question` tool with `multiSelect: true` to present all available actions:
   - **Save report as Markdown file** — Write the full report to a file
   - **Update README.md with analysis insights** — Add architecture/structure info to README
   - **Update CLAUDE.md with analysis insights** — Add patterns/conventions to CLAUDE.md
   - **Keep a condensed summary in memory** — Retain a quick-reference summary in conversation context
   - **Address actionable insights** — Fix challenges and implement recommendations from the report

   If the user selects no actions, the workflow is complete. Thank the user and end.

2. **Execute selected actions in the following fixed order:**

   ### Action: Save Report as Markdown File

   - Check if a `docs/` directory exists in the project root
     - If yes, suggest default path: `docs/codebase-analysis.md`
     - If no, suggest default path: `codebase-analysis.md` in the project root
   - Use the `question` tool to let the user confirm or customize the file path
   - Write the full report content (same as Phase 2 output) to the confirmed path using the `write` tool
   - Confirm the file was saved

   ### Action: Update README.md

   - `read` the existing README.md at the project root
     - If no README.md exists, skip this action and inform the user
   - Draft updates based on analysis insights — focus on:
     - Architecture overview
     - Project structure
     - Tech stack summary
   - Present the draft to the user for approval using the `question` tool with options:
     - **Apply** — Apply the drafted updates
     - **Modify** — Let the user describe what to change, then re-draft
     - **Skip** — Skip this action entirely
   - If approved, apply updates using the `edit` tool

   ### Action: Update CLAUDE.md

   - `read` the existing CLAUDE.md at the project root
     - If no CLAUDE.md exists, use the `question` tool to ask if one should be created
     - If user declines, skip this action
   - Draft updates based on analysis insights — focus on:
     - Key patterns and conventions discovered
     - Critical files and their roles
     - Important dependencies
     - Architectural decisions and constraints
   - Present the draft to the user for approval using the `question` tool with options:
     - **Apply** — Apply the drafted updates
     - **Modify** — Let the user describe what to change, then re-draft
     - **Skip** — Skip this action entirely
   - If approved, apply updates using the `edit` tool (or `write` tool if creating new)

   ### Action: Keep Insights in Memory

   - Present a condensed **Codebase Quick Reference** inline in the conversation:
     - **Architecture** — 1-2 sentence summary of how the codebase is structured
     - **Key Files** — 3-5 most critical files with one-line descriptions
     - **Conventions** — Important patterns and naming conventions
     - **Tech Stack** — Core technologies and frameworks
     - **Watch Out For** — Top risks or complexity hotspots
   - No file is written — this summary stays in conversation context for reference during the session

   ### Action: Address Actionable Insights

   **IMPORTANT:** This action always executes **last** among all selected actions. Code changes could invalidate analysis if documentation is generated after, and this is the most interactive action — it should not block simpler actions.

   **Step 1: Extract actionable items from the report**

   Parse the Phase 2 report (in conversation context) to extract items from:
   - **Challenges & Risks** table rows — title from Challenge column, severity from Severity column, description from Impact column
   - **Recommendations** section — each numbered item; infer severity from linked challenges (High if linked to a High challenge, otherwise Medium)
   - **Other findings** with concrete fixes — default to Low severity

   If no actionable items are found, inform the user and skip this action.

   **Step 2: Present severity-ranked item list**

   <!-- NOTE: reference_dir is null in opencode. The actionable-insights-template.md reference file cannot be loaded via path. The template structure is inlined below. (resolution_mode: cached, group_key: unsupported_composition:reference_dir_null) -->

   **Actionable Insights Format (inlined from references/actionable-insights-template.md):**
   Present items in a table sorted High → Medium → Low:

   | # | Title | Severity | Source | Description |
   |---|-------|----------|--------|-------------|
   | 1 | [title] | High | Challenges & Risks | [brief description] |
   | 2 | [title] | Medium | Recommendations | [brief description] |
   | 3 | [title] | Low | Other | [brief description] |

   - Present items sorted High → Medium → Low, each showing:
     - Title
     - Severity (High / Medium / Low)
     - Source section (Challenges & Risks, Recommendations, or Other)
     - Brief description
   - Use the `question` tool with `multiSelect: true` for the user to select which items to address
   - If no items selected, skip this action

   **Step 3: Process each selected item in priority order (High → Medium → Low)**

   For each item:

   1. **Assess complexity:**
      - **Simple** — Single file, clear fix, localized change
      - **Complex** — Multi-file, architectural impact, requires investigation

   2. **Plan the fix:**
      - Simple: `read` the target file, propose changes directly
      - Complex (architectural): Spawn a `task` with `command: "code-architect"` to design the fix:
        ```
        task(
          description: "Design fix for: [item title]",
          prompt: "You are a code architect. Design a fix for the following issue identified during codebase analysis:

        Issue: [item title]
        Severity: [severity]
        Description: [description]

        Codebase context: [relevant summary from deep-analysis synthesis]

        Provide a detailed architectural plan including files to modify, changes to make, and rationale.",
          subagent_type: "build",
          command: "code-architect"
        )
        ```
      - Complex (needs investigation): Spawn a `task` with `command: "code-explorer"` to investigate before proposing:
        ```
        task(
          description: "Investigate: [item title]",
          prompt: "You are a code explorer. Investigate the following issue to inform a fix proposal:

        Issue: [item title]
        Severity: [severity]
        Description: [description]

        Use read, glob, grep, and bash to thoroughly investigate. Identify root causes, affected files, and potential fix approaches.

        Write your findings to: .claude/sessions/__ca_live__/investigation-[item-slug].md",
          subagent_type: "build",
          command: "code-explorer"
        )
        ```

   3. **Present proposal:** Show files to modify, specific changes, and rationale

   4. **User approval** via the `question` tool:
      - **Apply** — Execute changes with `edit`/`write` tools, confirm success
      - **Skip** — Record the skip, move to next item
      - **Modify** — User describes adjustments, re-propose the fix (max 3 revision cycles, then must Apply or Skip)

   **Step 4: Summarize results**

   Present a summary covering:
   - Items addressed (with list of files modified per item)
   - Items skipped
   - Total files modified table

3. **Complete the workflow:**
   Summarize which actions were executed and confirm the workflow is complete.

---

## Error Handling

If any phase fails:
1. Explain what went wrong
2. Ask the user how to proceed using the `question` tool:
   - Retry the phase
   - Skip to next phase (with partial results)
   - Abort the workflow

---

## Agent Coordination

Exploration and synthesis agent coordination is handled by the `deep-analysis` skill in Phase 1, which uses parallel task agents with hub-and-spoke coordination. Deep-analysis performs reconnaissance, composes a team plan (auto-approved when invoked by another skill), dispatches parallel explorer tasks, and manages the exploration/synthesis lifecycle. See that skill for task dispatch details, approval flow, agent model tiers, and failure handling.

---

## Additional Resources

- For report structure, see the inlined template in Phase 2 Step 1 above
- For actionable insights format, see the inlined template in Phase 3 Step 2 above
~~~

## Fidelity Report

| Mapping Type | Count | Weight | Contribution |
|-------------|-------|--------|-------------|
| Direct | 21 | 1.0 | 21.0 |
| Workaround | 12 | 0.7 | 8.4 |
| TODO | 0 | 0.2 | 0.0 |
| Omitted | 1 | 0.0 | 0.0 |
| **Total** | **34** | | **29.4** |

**Notes:** Score = 29.4 / 34 * 100 = 86.5%, rounded to 87%. The primary fidelity reductions come from the null mapping of `allowed-tools` (omitted, cosmetic — no per-skill restrictions in opencode), workaround mappings for TeamCreate/TeamDelete/SendMessage/Task* (all handled by the deep-analysis dependency rather than this skill directly), reference file inlining (report-template.md and actionable-insights-template.md both inlined as structured prose since reference_dir is null), and the standard disable-model-invocation / name / argument-hint field relocations. All AskUserQuestion invocations map directly to `question`. All core tool references (read, write, edit, glob, grep, bash, task) map directly. Core skill composition for deep-analysis maps directly via `skill({ name: "deep-analysis" })`.

## Decisions

| Feature | Decision Type | Original | Converted | Rationale | Confidence | Resolution Mode |
|---------|-------------|----------|-----------|-----------|------------|----------------|
| name field | relocated | `name: codebase-analysis` in frontmatter | Derived from filename `codebase-analysis.md` | opencode derives skill name from filename; embedded:filename mapping | high | auto |
| description field | direct | `description: Execute a structured codebase...` | `description: Execute a structured codebase...` | Direct 1:1 mapping | high | N/A |
| argument-hint field | relocated | `argument-hint: <analysis-context or feature-description>` | `$ARGUMENTS` placeholder note in skill body header | opencode uses $ARGUMENTS in body; embedded:body mapping | high | auto |
| user-invocable field | direct | `user-invocable: true` | `user-invocable: true` | Direct 1:1 mapping | high | N/A |
| disable-model-invocation field | workaround | `disable-model-invocation: false` | Documented in header comment; enforce at agent level | No per-skill model-invocation control in opencode; cached global decision | high | cached |
| allowed-tools field | omitted | Full tool list in frontmatter | Field removed | No per-skill tool restrictions in opencode; enforced at agent level | high | auto |
| Read tool (allowed-tools) | direct | `Read` | `read` | Direct mapping | high | N/A |
| Write tool (allowed-tools) | direct | `Write` | `write` | Direct mapping | high | N/A |
| Edit tool (allowed-tools) | direct | `Edit` | `edit` | Direct mapping | high | N/A |
| Glob tool (allowed-tools) | direct | `Glob` | `glob` | Direct mapping | high | N/A |
| Grep tool (allowed-tools) | direct | `Grep` | `grep` | Direct mapping | high | N/A |
| Bash tool (allowed-tools) | direct | `Bash` | `bash` | Direct mapping | high | N/A |
| Task tool (allowed-tools) | direct | `Task` | `task` | Direct mapping | high | N/A |
| AskUserQuestion tool (allowed-tools) | direct | `AskUserQuestion` | `question` | Direct equivalent for primary agents | high | N/A |
| TeamCreate tool (allowed-tools) | workaround | `TeamCreate` | Comment noting hub-and-spoke restructured as task calls in deep-analysis | No team management in opencode; deep-analysis handles all team coordination; cached global decision | high | cached |
| TeamDelete tool (allowed-tools) | workaround | `TeamDelete` | Comment noting ephemeral tasks need no cleanup | No team management in opencode; cached global decision | high | cached |
| TaskCreate tool (allowed-tools) | workaround | `TaskCreate` | `todowrite` (partial, via deep-analysis) | Session-scoped scratchpad; no dependency or owner tracking; cached global decision | high | cached |
| TaskUpdate tool (allowed-tools) | workaround | `TaskUpdate` | `todowrite` (partial, via deep-analysis) | Same todowrite tool; limited status changes; cached global decision | high | cached |
| TaskList tool (allowed-tools) | workaround | `TaskList` | `todoread` (partial, via deep-analysis) | Full list scan; no filtering by owner or status; cached global decision | high | cached |
| TaskGet tool (allowed-tools) | workaround | `TaskGet` | `todoread` (partial, via deep-analysis) | No per-task retrieval by ID; cached global decision | high | cached |
| SendMessage tool (allowed-tools) | workaround | `SendMessage` | Comment noting context embedded in task prompts; handled in deep-analysis | No inter-agent messaging in opencode; cached global decision | high | cached |
| deep-analysis skill composition | direct | `Read ${CLAUDE_PLUGIN_ROOT}/skills/deep-analysis/SKILL.md` | `skill({ name: "deep-analysis" })` | Reference mechanism; opencode skill composition supports cross-skill by name | high | N/A |
| report-template.md reference | workaround | `Read ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analysis/references/report-template.md` | Inlined as structured prose description in Phase 2 Step 1 | reference_dir is null in opencode; cached global decision to inline reference content | high | cached |
| actionable-insights-template.md reference | workaround | `Read ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analysis/references/actionable-insights-template.md` | Inlined as table format description in Phase 3 Step 2 | reference_dir is null in opencode; cached global decision to inline reference content | high | cached |
| AskUserQuestion body (Phase 3 main menu) | direct | `AskUserQuestion` with `multiSelect: true` | `question` tool with `multiSelect: true` | Direct equivalent; question tool supports 1-8 questions with 2-8 options | high | N/A |
| AskUserQuestion body (save file path) | direct | `AskUserQuestion` for file path confirmation | `question` tool | Direct equivalent | high | N/A |
| AskUserQuestion body (README approval) | direct | `AskUserQuestion` with Apply/Modify/Skip | `question` tool | Direct equivalent | high | N/A |
| AskUserQuestion body (CLAUDE.md creation) | direct | `AskUserQuestion` for creation decision | `question` tool | Direct equivalent | high | N/A |
| AskUserQuestion body (CLAUDE.md approval) | direct | `AskUserQuestion` with Apply/Modify/Skip | `question` tool | Direct equivalent | high | N/A |
| AskUserQuestion body (insights selection) | direct | `AskUserQuestion` with `multiSelect: true` | `question` tool with `multiSelect: true` | Direct equivalent | high | N/A |
| AskUserQuestion body (item approval) | direct | `AskUserQuestion` with Apply/Skip/Modify | `question` tool | Direct equivalent | high | N/A |
| AskUserQuestion body (error handling) | direct | `AskUserQuestion` for retry/skip/abort | `question` tool | Direct equivalent | high | N/A |
| code-architect agent task spawn | direct | `Launch agent-alchemy-core-tools:code-architect` | `task(command: "code-architect")` | Direct equivalent; opencode task tool with command parameter routes to named agent | high | N/A |
| code-explorer agent task spawn | direct | `Launch agent-alchemy-core-tools:code-explorer` | `task(command: "code-explorer")` | Direct equivalent; opencode task tool with command parameter routes to named agent | high | N/A |

## Gaps

| Feature | Reason | Severity | Workaround | User Acknowledged |
|---------|--------|----------|------------|-------------------|
| allowed-tools per-skill restrictions | No per-skill tool restrictions in opencode; tool permissions are agent-level only | cosmetic | Tool list removed from frontmatter; permissions enforced at agent level via permission config | false |
| disable-model-invocation | No per-skill invocation control in opencode | cosmetic | Documented in header comment; restrict via agent-level permission config | false |
| report-template.md reference file | reference_dir is null in opencode; no path-based reference loading | functional | Template structure inlined as prose in Phase 2 Step 1 body; full report section descriptions preserved | false |
| actionable-insights-template.md reference file | reference_dir is null in opencode; no path-based reference loading | functional | Template format inlined as table description in Phase 3 Step 2 body; format fully preserved | false |
| TeamCreate / hub-and-spoke team management | No team orchestration in opencode (inherited from deep-analysis dependency) | functional | Restructured as parallel task calls within deep-analysis; codebase-analysis delegates all team coordination to deep-analysis skill | false |
| SendMessage / inter-agent messaging | No inter-agent messaging in opencode (inherited from deep-analysis dependency) | functional | All context embedded in task prompts at dispatch time within deep-analysis skill | false |

## Unresolved Incompatibilities

Incompatibilities the converter agent could not auto-resolve. The orchestrator batches these between waves.

| Group Key | Feature | Severity | Category | Reason | Suggested Workaround | Confidence | Affected Locations |
|-----------|---------|----------|----------|--------|---------------------|------------|-------------------|
| (all resolved — auto-applied workarounds globally via resolution cache) | | | | | | | |
