---
name: codebase-analysis
description: Produce a structured codebase analysis report with architecture overview, critical files, patterns, and actionable recommendations. Use when asked to "analyze codebase", "explore codebase", "understand this codebase", "map the codebase", "give me an overview of this project", "what does this codebase do", "codebase report", "project analysis", "audit this codebase", or "how is this project structured".
dependencies:
  - deep-analysis
  - technical-diagrams
  - code-explorer
  - code-architect
---

# Codebase Analysis Workflow

Execute a structured 3-phase codebase analysis workflow to gather insights.

Complete all 3 phases. The workflow is not complete until Phase 3: Post-Analysis Actions is finished. After completing each phase, immediately proceed to the next phase.

## Phase Overview

1. **Deep Analysis** — Explore and synthesize codebase findings via the deep-analysis skill
2. **Reporting** — Present structured analysis to the user
3. **Post-Analysis Actions** — Save, document, or retain analysis insights

---

## Phase 1: Deep Analysis

**Goal:** Explore the codebase and synthesize findings.

1. **Determine analysis context:**
   - If an input argument is provided, use it as the analysis context
   - If no arguments, set context to "general codebase understanding"

2. **Check for cached results:**
   - Check if an exploration cache manifest exists
   - If found, verify: codebase path matches the current working directory, and timestamp is within the configured cache TTL (default 24 hours)
   - **If cache is valid**, prompt the user:
     - **Use cached results** (show the formatted cache date) — Read cached synthesis and reconnaissance summary. Set `CACHE_HIT = true`. Skip step 3 and proceed directly to step 4.
     - **Run fresh analysis** — Remove the cache, set `CACHE_HIT = false`, and proceed to step 3
   - **If no valid cache**: set `CACHE_HIT = false` and proceed to step 3

3. **Run deep-analysis workflow:**
   - Refer to the **deep-analysis** skill and follow its workflow
   - Pass the analysis context from step 1
   - This handles reconnaissance, team planning, approval (auto-approved when loaded by another skill), team creation, parallel exploration (code-explorer agents), and synthesis (code-synthesizer agent)
   - After completion, set `CACHE_TIMESTAMP = null` (fresh results, no prior cache)

4. **Verify results and capture metadata:**
   - Ensure the synthesis covers the analysis context adequately
   - If critical gaps remain, fill them directly using file search and reading
   - Record analysis metadata for Phase 2 reporting: whether results were cached, cache timestamp if applicable, and the number of explorer agents used

---

## Phase 2: Reporting

**Goal:** Present a structured analysis to the user.

1. **Apply diagram guidance:**
   - Refer to the **technical-diagrams** skill for Mermaid diagram conventions
   - Use Mermaid diagrams in the Architecture Overview and Relationship Map sections

2. **Present the analysis** using this report structure:

### Report Template

```markdown
# Codebase Analysis Report

**Analysis Context**: {What was analyzed and why}
**Codebase Path**: {Path analyzed}
**Date**: {YYYY-MM-DD}

{If the report exceeds approximately 100 lines, add a Table of Contents here.}

---

## Executive Summary

{Lead with the most important finding. 2-3 sentences covering: what was analyzed, the key architectural insight, and the primary recommendation or risk.}

---

## Architecture Overview

{2-3 paragraphs describing:}
- How the codebase is structured (layers, modules, boundaries)
- The design philosophy and architectural style
- Key architectural decisions and their rationale

{Include a Mermaid architecture diagram (flowchart or C4 Context) showing major layers/components.}

---

## Tech Stack

| Category | Technology | Version (if detected) | Role |
|----------|-----------|----------------------|------|
| Language | {e.g., TypeScript} | {e.g., 5.x} | Primary language |

{Include only technologies actually detected in config files or code.}

---

## Critical Files

{Limit to 5-10 most important files}

| File | Purpose | Relevance |
|------|---------|-----------|
| `path/to/file` | Brief description | High/Medium |

### File Details

#### `path/to/critical-file`
- **Key exports**: What this file provides to others
- **Core logic**: What it does
- **Connections**: What depends on it and what it depends on

---

## Patterns & Conventions

### Code Patterns
- **Pattern**: Description and where it's used

### Naming Conventions
- **Convention**: Description and examples

### Project Structure
- **Organization**: How files and directories are organized

---

## Relationship Map

{Describe how key components connect — limit to 15-20 most significant connections. Use Mermaid flowcharts for data flows and dependency maps.}

---

## Challenges & Risks

| Challenge | Severity | Impact |
|-----------|----------|--------|
| {Description} | High/Medium/Low | {What could go wrong} |

---

## Recommendations

1. **{Recommendation}** _(addresses: {Challenge name})_: {Brief rationale}
2. **{Recommendation}** _(addresses: {Challenge name})_: {Brief rationale}

---

## Analysis Methodology

- **Exploration agents**: {Number} agents with focus areas: {list}
- **Synthesis**: Findings merged and critical files read in depth
- **Scope**: {What was included and excluded}
- **Cache status**: {Fresh analysis / Cached results from date}
```

3. **Proceed immediately to Phase 3.** The report is presented, but the workflow requires Post-Analysis Actions.

---

## Phase 3: Post-Analysis Actions

**Goal:** Let the user save, document, or retain analysis insights from the report through a multi-step interactive flow.

### Step 1: Select actions

Prompt the user to select one or more actions (multiple selections allowed):

- **Save Codebase Analysis Report** — Write the structured report to a markdown file
- **Save a custom report** — Generate a report tailored to specific goals (user provides instructions)
- **Update project documentation** — Add/update README.md, CLAUDE.md, or AGENTS.md with analysis insights
- **Keep a condensed summary in memory** — Retain a quick-reference summary in conversation context

If the user selects no actions, the workflow is complete. Thank the user and end.

### Step 2: Execute selected actions

Process selected actions in the following fixed order:

#### Action: Save Codebase Analysis Report

1. **Prompt for file location:**
   - Check if an `internal/docs/` directory exists in the project root
   - If yes, suggest default path: `internal/docs/codebase-analysis-report-{YYYY-MM-DD}.md`
   - If no, suggest default path: `codebase-analysis-report-{YYYY-MM-DD}.md` in the project root
   - Let the user confirm or customize the file path

2. **Generate and save the report:**
   - Generate the full structured report using the Phase 2 analysis findings and the template structure
   - Write the report to the confirmed path
   - Confirm the file was saved

#### Action: Save Custom Report

1. **Gather report requirements:**
   - Ask the user to describe the goals and requirements — what it should focus on, what questions it should answer, and any format preferences

2. **Prompt for file location:**
   - Suggest default path similar to the standard report
   - Let the user confirm or customize

3. **Generate and save the custom report:**
   - Generate a report shaped by the user's requirements, drawing from Phase 2 analysis data
   - Write to the confirmed path and confirm

#### Action: Update Project Documentation

1. **Select documentation files and gather directions:**
   Prompt the user to select which files to update (multiple selections allowed):
   - **README.md** — Architecture, structure, tech stack
   - **CLAUDE.md** — Patterns, conventions, critical files, architectural decisions
   - **AGENTS.md** — Agent descriptions, capabilities, coordination patterns

   Then ask for update directions: "What content from the analysis should be added or updated?"

2. **Generate and approve documentation drafts:**
   For each selected file, read the existing file and draft updates based on user directions and Phase 2 analysis data. Present all drafts together, then prompt:
   - **Apply all** — Apply all drafted updates
   - **Modify** — Specify which file(s) to revise (max 3 revision cycles)
   - **Skip all** — Skip documentation updates

   If approved, apply updates.

#### Action: Keep Insights in Memory

Present a condensed **Codebase Quick Reference** inline in the conversation:
- **Architecture** — 1-2 sentence summary
- **Key Files** — 3-5 most critical files with one-line descriptions
- **Conventions** — Important patterns and naming conventions
- **Tech Stack** — Core technologies and frameworks
- **Watch Out For** — Top risks or complexity hotspots

No file is written — this summary stays in conversation context.

### Step 3: Actionable Insights Follow-up

This step always executes after Step 2 completes.

Prompt the user:
- **Address actionable insights** — Fix challenges and implement recommendations from the report
- **Skip** — No further action needed

If the user selects "Skip", proceed to Step 4.

If the user selects "Address actionable insights":

**Step 3a: Extract actionable items**

Parse the Phase 2 report to extract items from:
- **Challenges & Risks** table rows — title, severity, description
- **Recommendations** section — each item with its cited challenge and inherited severity
- **Other findings** with concrete fixes — default to Low severity

Only extract items with concrete, actionable fixes. Deduplicate items targeting the same files or with overlapping descriptions.

**Step 3b: Present severity-ranked item list**

Present items sorted High → Medium → Low, each showing title, severity, source section, and brief description.

Prompt the user to select which items to address (multiple selections allowed). If none selected, skip to Step 4.

**Step 3c: Process each selected item in priority order**

For each item:

1. **Assess complexity:**
   - **Simple** — Single file, clear fix, localized change
   - **Complex (architectural)** — Multi-file, introduces or changes patterns. Delegate to a **code-architect** agent for design.
   - **Complex (investigation needed)** — Root cause unclear. Delegate to a **code-explorer** agent for investigation.
   - If agent delegation fails, fall back to direct investigation.

2. **Present proposal:** Show files to modify, specific changes, and rationale

3. **User approval:**
   - **Apply** — Execute changes, confirm success
   - **Skip** — Record the skip, move to next item
   - **Modify** — User describes adjustments, re-propose (max 3 revision cycles)

**Step 3d: Summarize results**

Present: items addressed (with files modified per item), items skipped, total files modified.

### Step 4: Complete the workflow

Summarize which actions were executed and confirm the workflow is complete.

---

## Error Handling

### General

If any phase fails:
1. Explain what went wrong
2. Ask the user how to proceed:
   - Retry the phase
   - Skip to next phase (with partial results)
   - Abort the workflow

### Documentation Update Failures

If file writing fails when applying documentation updates:
1. Retry once
2. If still failing, present the drafted content to the user inline and suggest manual application
3. Continue with the remaining selected files

### Agent Failures

If a code-architect or code-explorer agent fails during actionable insight processing:
1. Fall back to direct investigation using file reading and searching
2. Propose a simpler fix based on available information
3. If the item is too complex without agent assistance, inform the user and offer to skip

---

## Integration Notes

**What this component does:** Orchestrates a full codebase analysis workflow — from deep multi-agent exploration through structured reporting to interactive follow-up actions including documentation updates and issue remediation.

**Capabilities needed:**
- File reading and searching (throughout all phases)
- File writing and editing (for reports and documentation updates)
- Shell command execution (for reconnaissance and deep investigation)
- User interaction / prompting (for cache decisions, action selection, approvals)
- Sub-agent delegation (deep-analysis uses explorer and synthesizer agents; actionable insights may use architect and explorer agents)

**Adaptation guidance:**
- This skill composes the deep-analysis skill for Phase 1 — ensure that skill is also available
- The report template (Phase 2) and actionable insights template (Phase 3) are embedded above — no separate files needed
- For the actionable insights step, agent delegation to code-architect and code-explorer is optional — direct investigation works as a fallback
- The multi-step interactive flow in Phase 3 requires a harness that supports multiple rounds of user prompting within a single skill execution
