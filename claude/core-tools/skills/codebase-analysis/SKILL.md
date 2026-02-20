---
name: codebase-analysis
description: Execute a structured codebase exploration workflow to gather insights. Use when asked to "analyze codebase", "explore codebase", "understand this codebase", or "map the codebase".
argument-hint: <analysis-context or feature-description>
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task, AskUserQuestion, TeamCreate, TeamDelete, TaskCreate, TaskUpdate, TaskList, TaskGet, SendMessage
---

# Codebase Analysis Workflow

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
   - Read `${CLAUDE_PLUGIN_ROOT}/skills/deep-analysis/SKILL.md` and follow its workflow
   - Pass the analysis context from step 1
   - This handles reconnaissance, team planning, approval (auto-approved when skill-invoked), team creation, parallel exploration (code-explorer agents), and synthesis (code-synthesizer agent)
   - **Note:** Deep-analysis may return cached results if a valid exploration cache exists. In skill-invoked mode, cache hits are auto-accepted — this is expected behavior that avoids redundant exploration.

3. **Verify results:**
   - Ensure the synthesis covers the analysis context adequately
   - If critical gaps remain, use Glob/Grep to fill them directly

---

## Phase 2: Reporting

**Goal:** Present a structured analysis to the user.

1. **Load report template:**
   - Read `${CLAUDE_PLUGIN_ROOT}/skills/codebase-analysis/references/report-template.md`
   - Use it to structure the presentation

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

**Goal:** Let the user save, document, or retain analysis insights from the report through a multi-step interactive flow.

### Step 1: Select actions

Use `AskUserQuestion` with `multiSelect: true` to present all available actions:

- **Save Codebase Analysis Report** — Write the structured report to a markdown file
- **Save a custom report** — Generate a report tailored to your specific goals (you'll provide instructions next)
- **Update project documentation** — Add/update README.md, CLAUDE.md, or AGENTS.md with analysis insights
- **Keep a condensed summary in memory** — Retain a quick-reference summary in conversation context

If the user selects no actions, the workflow is complete. Thank the user and end.

### Step 2: Execute selected actions

Process selected actions in the following fixed order. Complete all sub-steps for each action before moving to the next.

#### Action: Save Codebase Analysis Report

**Step 2a-1: Prompt for file location**

- Check if an `internal/docs/` directory exists in the project root
  - If yes, suggest default path: `internal/docs/codebase-analysis-report-{YYYY-MM-DD}.md`
  - If no, suggest default path: `codebase-analysis-report-{YYYY-MM-DD}.md` in the project root
- Use `AskUserQuestion` to let the user confirm or customize the file path

**Step 2a-2: Generate and save the report**

- Load the report template from `${CLAUDE_PLUGIN_ROOT}/skills/codebase-analysis/references/report-template.md`
- Generate the full structured report using the Phase 2 analysis findings and the template structure
- Write the report to the confirmed path using the Write tool
- Confirm the file was saved
- Set `STRUCTURED_REPORT_SAVED = true` (used in Step 3)

#### Action: Save Custom Report

**Step 2b-1: Gather report requirements**

- Use `AskUserQuestion` to ask the user to describe the goals and requirements for their custom report — what it should focus on, what questions it should answer, and any format preferences

**Step 2b-2: Prompt for file location**

- Check if an `internal/docs/` directory exists in the project root
  - If yes, suggest default path: `internal/docs/custom-report-{YYYY-MM-DD}.md`
  - If no, suggest default path: `custom-report-{YYYY-MM-DD}.md` in the project root
- Use `AskUserQuestion` to let the user confirm or customize the file path

**Step 2b-3: Generate and save the custom report**

- Generate a report shaped by the user's requirements from Step 2b-1, drawing from the Phase 2 analysis data — this is a repackaging of existing findings, not a re-analysis
- Write the report to the confirmed path using the Write tool
- Confirm the file was saved

#### Action: Update Project Documentation

**Step 2c-1: Select documentation files to update**

Use `AskUserQuestion` with `multiSelect: true`:

- **README.md** — Add architecture, structure, and tech stack information
- **CLAUDE.md** — Add patterns, conventions, critical files, and architectural decisions
- **AGENTS.md** — Add agent descriptions, capabilities, and coordination patterns

**Step 2c-2: Process each selected documentation file**

For each selected file:

##### If README.md selected:

- Read the existing README.md at the project root
  - If no README.md exists, skip this file and inform the user
- Use `AskUserQuestion` to ask what content the user wants to add or update based on the analysis findings (e.g., "update the architecture section", "add project structure", "rewrite tech stack")
- Draft the updates based on the user's direction and the Phase 2 analysis data
- Present the draft to the user for approval using `AskUserQuestion`:
  - **Apply** — Apply the drafted updates
  - **Modify** — User describes what to change, then re-draft
  - **Skip** — Skip this file entirely
- If approved, apply updates using the Edit tool

##### If CLAUDE.md selected:

- Read the existing CLAUDE.md at the project root
  - If no CLAUDE.md exists, use `AskUserQuestion` to ask if one should be created
  - If user declines, skip this file
- Use `AskUserQuestion` to ask what content the user wants to add or update based on the analysis findings (e.g., "add critical files section", "update conventions", "document architectural decisions")
- Draft the updates based on the user's direction and the Phase 2 analysis data
- Present the draft to the user for approval using `AskUserQuestion`:
  - **Apply** — Apply the drafted updates
  - **Modify** — User describes what to change, then re-draft
  - **Skip** — Skip this file entirely
- If approved, apply updates using the Edit tool (or Write tool if creating new)

##### If AGENTS.md selected:

- Read the existing AGENTS.md at the project root
  - If no AGENTS.md exists, inform the user that a new file will be created
- Use `AskUserQuestion` to ask what content the user wants to add or update based on the analysis findings (e.g., "document all agents and their roles", "add coordination patterns", "list model tiers")
- Draft content based on the user's direction and the Phase 2 analysis data — potential focus areas include:
  - Agent inventory (name, model tier, purpose)
  - Agent capabilities and tool access
  - Coordination patterns (hub-and-spoke, wave-based, sequential)
  - Which skills spawn which agents
  - Model tiering rationale
- Present the draft to the user for approval using `AskUserQuestion`:
  - **Apply** — Apply the drafted content
  - **Modify** — User describes what to change, then re-draft
  - **Skip** — Skip this file entirely
- If approved, write content using the Write tool (new file) or Edit tool (existing file)

#### Action: Keep Insights in Memory

- Present a condensed **Codebase Quick Reference** inline in the conversation:
  - **Architecture** — 1-2 sentence summary of how the codebase is structured
  - **Key Files** — 3-5 most critical files with one-line descriptions
  - **Conventions** — Important patterns and naming conventions
  - **Tech Stack** — Core technologies and frameworks
  - **Watch Out For** — Top risks or complexity hotspots
- No file is written — this summary stays in conversation context for reference during the session

### Step 3: Actionable Insights Follow-up

**Condition:** This step only executes if `STRUCTURED_REPORT_SAVED = true` (the user selected "Save Codebase Analysis Report" in Step 1 and it was saved successfully).

Use `AskUserQuestion` to ask:
- **Address actionable insights** — Fix challenges and implement recommendations from the report
- **Skip** — No further action needed

If the user selects "Skip" or if the condition is not met, proceed to Step 4.

If the user selects "Address actionable insights":

**Step 3a: Extract actionable items from the report**

Parse the Phase 2 report (in conversation context) to extract items from:
- **Challenges & Risks** table rows — title from Challenge column, severity from Severity column, description from Impact column
- **Recommendations** section — each numbered item; infer severity from linked challenges (High if linked to a High challenge, otherwise Medium)
- **Other findings** with concrete fixes — default to Low severity

If no actionable items are found, inform the user and skip to Step 4.

**Step 3b: Present severity-ranked item list**

- Load reference template from `${CLAUDE_PLUGIN_ROOT}/skills/codebase-analysis/references/actionable-insights-template.md`
- Present items sorted High → Medium → Low, each showing:
  - Title
  - Severity (High / Medium / Low)
  - Source section (Challenges & Risks, Recommendations, or Other)
  - Brief description
- Use `AskUserQuestion` with `multiSelect: true` for the user to select which items to address
- If no items selected, skip to Step 4

**Step 3c: Process each selected item in priority order (High → Medium → Low)**

For each item:

1. **Assess complexity:**
   - **Simple** — Single file, clear fix, localized change
   - **Complex** — Multi-file, architectural impact, requires investigation

2. **Plan the fix:**
   - Simple: Read the target file, propose changes directly
   - Complex (architectural): Launch `agent-alchemy-core-tools:code-architect` agent to design the fix
   - Complex (needs investigation): Launch `agent-alchemy-core-tools:code-explorer` agent to investigate before proposing

3. **Present proposal:** Show files to modify, specific changes, and rationale

4. **User approval** via `AskUserQuestion`:
   - **Apply** — Execute changes with Edit/Write tools, confirm success
   - **Skip** — Record the skip, move to next item
   - **Modify** — User describes adjustments, re-propose the fix (max 3 revision cycles, then must Apply or Skip)

**Step 3d: Summarize results**

Present a summary covering:
- Items addressed (with list of files modified per item)
- Items skipped
- Total files modified table

### Step 4: Complete the workflow

Summarize which actions were executed and confirm the workflow is complete.

---

## Error Handling

If any phase fails:
1. Explain what went wrong
2. Ask the user how to proceed:
   - Retry the phase
   - Skip to next phase (with partial results)
   - Abort the workflow

---

## Agent Coordination

Exploration and synthesis agent coordination is handled by the `deep-analysis` skill in Phase 1, which uses Agent Teams with hub-and-spoke coordination. Deep-analysis performs reconnaissance, composes a team plan (auto-approved when invoked by another skill), assembles the team, and manages the exploration/synthesis lifecycle. See that skill for team setup, approval flow, agent model tiers, and failure handling details.

---

## Additional Resources

- For report structure, see [references/report-template.md](references/report-template.md)
- For actionable insights format, see [references/actionable-insights-template.md](references/actionable-insights-template.md)
