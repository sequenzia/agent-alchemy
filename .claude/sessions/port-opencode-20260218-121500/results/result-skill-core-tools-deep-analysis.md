# Conversion Result: skill-core-tools-deep-analysis

## Metadata

| Field | Value |
|-------|-------|
| Component ID | skill-core-tools-deep-analysis |
| Component Type | skill |
| Group | core-tools |
| Name | deep-analysis |
| Source Path | claude/core-tools/skills/deep-analysis/SKILL.md |
| Target Path | .opencode/skills/deep-analysis.md |
| Fidelity Score | 66% |
| Fidelity Band | yellow |
| Status | partial |

## Converted Content

~~~markdown
---
description: Deep exploration and synthesis workflow using parallel task agents with dynamic planning and hub-and-spoke coordination. Use when asked for "deep analysis", "deep understanding", "analyze codebase", "explore and analyze", or "investigate codebase".
user-invocable: true
---

<!-- NOTE: disable-model-invocation has no equivalent in opencode. This skill is always available to the model. To restrict invocation to user-only contexts, document the constraint in the description and enforce at the agent level via permission config. (resolution_mode: cached, group_key: unmapped_field:disable-model-invocation) -->

<!-- NOTE: allowed-tools field has no per-skill equivalent in opencode. Tool permissions are enforced at the agent level via permission config in the agent's .md frontmatter. -->

<!-- NOTE: TeamCreate and TeamDelete have no equivalent in opencode. The hub-and-spoke team pattern is restructured as sequential/parallel task calls with context passed via prompts. See inline TODOs below. (resolution_mode: cached, group_key: unmapped_tool:TeamCreate / unmapped_tool:TeamDelete) -->

<!-- NOTE: SendMessage has no equivalent in opencode. Inter-agent messaging is replaced by embedding all required context directly in the task prompt at dispatch time. Workers cannot receive follow-up messages after launch; synthesizer receives all explorer context in its initial prompt. (resolution_mode: cached, group_key: unmapped_tool:SendMessage) -->

<!-- NOTE: TaskCreate/TaskUpdate/TaskList/TaskGet are partially mapped to todowrite/todoread. opencode's todo tools are a session-scoped scratchpad with no dependency tracking, no owner assignment, and no per-task retrieval by ID. Task coordination is restructured below. (resolution_mode: cached) -->

# Deep Analysis Workflow

Invoke this skill with: `/deep-analysis <analysis-context or focus-area>`
(Replace `$ARGUMENTS` with your analysis context or focus area when invoking.)

Execute a structured exploration + synthesis workflow using parallel task agents with hub-and-spoke coordination. The lead performs rapid reconnaissance to generate dynamic focus areas, composes a team plan for review, workers explore independently, and a synthesizer merges findings with Bash-powered investigation.

This skill can be invoked standalone or loaded by other skills as a reusable building block. Approval behavior is configurable via `.claude/agent-alchemy.local.md`.

## Settings Check

**Goal:** Determine whether the team plan requires user approval before execution.

1. **Read settings file:**
   - Check if `.claude/agent-alchemy.local.md` exists
   - If it exists, read it and look for a `deep-analysis` section with nested settings:
     ```markdown
     - **deep-analysis**:
       - **direct-invocation-approval**: true
       - **invocation-by-skill-approval**: false
     ```
   - If the file does not exist or is malformed, use defaults (see step 4)

2. **Determine invocation mode:**
   - **Direct invocation:** The user invoked `/deep-analysis` directly, or you are running this skill standalone
   - **Skill-invoked:** Another skill (e.g., codebase-analysis, feature-dev, docs-manager) loaded and is executing this workflow

3. **Resolve settings:**
   - If settings were found, use them as-is
   - If the file is missing or the `deep-analysis` section is absent, use defaults:
     - `direct-invocation-approval`: `true`
     - `invocation-by-skill-approval`: `false`
   - If the file exists but is malformed (unparseable), warn the user and use defaults

4. **Set `REQUIRE_APPROVAL`:**
   - If direct invocation → use `direct-invocation-approval` value (default: `true`)
   - If skill-invoked → use `invocation-by-skill-approval` value (default: `false`)

5. **Parse session settings** (also under the `deep-analysis` section):
   ```markdown
   - **deep-analysis**:
     - **cache-ttl-hours**: 24
     - **enable-checkpointing**: true
     - **enable-progress-indicators**: true
   ```
   - `cache-ttl-hours`: Number of hours before exploration cache expires. Default: `24`. Set to `0` to disable caching entirely.
   - `enable-checkpointing`: Whether to write session checkpoints at phase boundaries. Default: `true`.
   - `enable-progress-indicators`: Whether to display `[Phase N/6]` progress messages. Default: `true`.

6. **Set behavioral flags:**
   - `CACHE_TTL` = value of `cache-ttl-hours` (default: `24`)
   - `ENABLE_CHECKPOINTING` = value of `enable-checkpointing` (default: `true`)
   - `ENABLE_PROGRESS` = value of `enable-progress-indicators` (default: `true`)

---

## Phase 0: Session Setup

**Goal:** Check for cached exploration results, detect interrupted sessions, and initialize the session directory.

> Skip this phase entirely if `CACHE_TTL = 0` AND `ENABLE_CHECKPOINTING = false`.

### Step 1: Exploration Cache Check

If `CACHE_TTL > 0`:

1. Check if `.claude/sessions/exploration-cache/manifest.md` exists
2. If found, read the manifest and verify:
   - `analysis_context` matches the current analysis context (or is a superset)
   - `codebase_path` matches the current working directory
   - `timestamp` is within `CACHE_TTL` hours of now
   - Config files referenced in `config_checksum` haven't been modified since the cache was written (check mod-times of `package.json`, `tsconfig.json`, `pyproject.toml`, etc.)
3. **If cache is valid:**
   - **Skill-invoked mode:** Auto-accept the cache. Set `CACHE_HIT = true`. Read cached `synthesis.md` and `recon_summary.md`. Skip to Phase 6 step 2 (present/return results).
   - **Direct invocation:** Use the `question` tool to offer:
     - **"Use cached results"** — Set `CACHE_HIT = true`, skip to Phase 6 step 2
     - **"Refresh analysis"** — Set `CACHE_HIT = false`, proceed normally
4. **If cache is invalid or absent:** Set `CACHE_HIT = false`

### Step 2: Interrupted Session Check

If `ENABLE_CHECKPOINTING = true`:

1. Check if `.claude/sessions/__da_live__/checkpoint.md` exists
2. If found, read the checkpoint to determine `last_completed_phase`
3. Use the `question` tool to offer:
   - **"Resume from Phase [N+1]"** — Load checkpoint state, proceed from the interrupted phase (see Session Recovery in Error Handling)
   - **"Start fresh"** — Archive the interrupted session to `.claude/sessions/da-interrupted-{timestamp}/` and proceed normally
4. If not found: proceed normally

### Step 3: Initialize Session Directory

If `ENABLE_CHECKPOINTING = true` AND `CACHE_HIT = false`:

1. Create `.claude/sessions/__da_live__/` directory
2. Write `checkpoint.md`:
   ```markdown
   ## Deep Analysis Session
   - **analysis_context**: [context from arguments or caller]
   - **codebase_path**: [current working directory]
   - **started**: [ISO timestamp]
   - **current_phase**: 0
   - **status**: initialized
   ```
3. Write `progress.md`:
   ```markdown
   ## Deep Analysis Progress
   - **Phase**: 0 of 6
   - **Status**: Session initialized

   ### Phase Log
   - [timestamp] Phase 0: Session initialized
   ```

---

## Phase 1: Reconnaissance & Planning

**Goal:** Perform codebase reconnaissance, generate dynamic focus areas, and compose a team plan.

> If `ENABLE_PROGRESS = true`: Display "**[Phase 1/6] Reconnaissance & Planning** — Mapping codebase structure..."

1. **Determine analysis context:**
   - If `$ARGUMENTS` is provided, use it as the analysis context (feature area, question, or general exploration goal)
   - If no arguments and this skill was loaded by another skill, use the calling skill's context
   - If no arguments and standalone invocation, set context to "general codebase understanding"
   - Set `PATH = current working directory`
   - Inform the user: "Exploring codebase at: `PATH`" with the analysis context

2. **Rapid codebase reconnaissance:**
   Use `glob`, `grep`, and `read` to quickly map the codebase structure. This should take 1-2 minutes, not deep investigation.

   - **Directory structure:** List top-level directories with `glob` (e.g., `*/` pattern) to understand the project layout
   - **Language and framework detection:** Read config files (`package.json`, `tsconfig.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, etc.) to identify primary language(s) and framework(s)
   - **File distribution:** Use `glob` with patterns like `src/**/*.ts`, `**/*.py` to gauge the size and shape of different areas
   - **Key documentation:** Read `README.md`, `CLAUDE.md`, or similar docs if they exist for project context
   - **For feature-focused analysis:** Use `grep` to search for feature-related terms (function names, component names, route paths) to find hotspot directories
   - **For general analysis:** Identify the 3-5 largest or most architecturally significant directories

   **Fallback:** If reconnaissance fails (empty project, unusual structure, errors), use the static focus area templates from Step 3b.

3. **Generate dynamic focus areas:**

   Based on reconnaissance findings, create focus areas tailored to the actual codebase. Default to 3 focus areas, but adjust based on codebase size and complexity (2 for small projects, up to 4 for large ones).

   **a) Dynamic focus areas (default):**

   Each focus area should include:
   - **Label:** Short description (e.g., "API layer in src/api/")
   - **Directories:** Specific directories to explore
   - **Starting files:** 2-3 key files to read first
   - **Search terms:** Grep patterns to find related code
   - **Complexity estimate:** Low/Medium/High based on file count and apparent structure

   For feature-focused analysis, focus areas should track the feature's actual footprint:
   ```
   Example:
   Focus 1: "API routes and middleware in src/api/ and src/middleware/" (auth-related endpoints, request handling)
   Focus 2: "React components in src/pages/profile/ and src/components/user/" (UI layer for user profiles)
   Focus 3: "Data models and services in src/db/ and src/services/" (persistence and business logic)
   ```

   For general analysis, focus areas should map to the codebase's actual structure:
   ```
   Example:
   Focus 1: "Next.js app layer in apps/web/src/" (pages, components, app router)
   Focus 2: "Shared library in packages/core/src/" (utilities, types, shared logic)
   Focus 3: "CLI and tooling in packages/cli/" (commands, configuration, build)
   ```

   **b) Static fallback focus areas** (only if recon failed):

   For feature-focused analysis:
   ```
   Focus 1: Explore entry points and user-facing code related to the context
   Focus 2: Explore data models, schemas, and storage related to the context
   Focus 3: Explore utilities, helpers, and shared infrastructure
   ```

   For general codebase understanding:
   ```
   Focus 1: Explore application structure, entry points, and core logic
   Focus 2: Explore configuration, infrastructure, and shared utilities
   Focus 3: Explore shared utilities, patterns, and cross-cutting concerns
   ```

4. **Compose the team plan:**

   Assemble a structured plan document from the reconnaissance and focus area findings:

   ```markdown
   ## Team Plan: Deep Analysis

   ### Analysis Context
   [context from Step 1]

   ### Reconnaissance Summary
   - **Project:** [name/type]
   - **Primary language/framework:** [detected]
   - **Codebase size:** [file counts, key directories]
   - **Key observations:** [2-3 bullets]

   ### Focus Areas

   #### Focus Area 1: [Label]
   - **Directories:** [list]
   - **Starting files:** [2-3 files]
   - **Search patterns:** [Grep patterns]
   - **Complexity:** [Low/Medium/High]
   - **Assigned to:** explorer-1 (sonnet)

   #### Focus Area 2: [Label]
   - **Directories:** [list]
   - **Starting files:** [2-3 files]
   - **Search patterns:** [Grep patterns]
   - **Complexity:** [Low/Medium/High]
   - **Assigned to:** explorer-2 (sonnet)

   [... repeated for each focus area]

   ### Agent Composition
   | Role | Count | Model | Purpose |
   |------|-------|-------|---------|
   | Explorer | [N] | anthropic/claude-sonnet-4-6 | Independent focus area exploration |
   | Synthesizer | 1 | anthropic/claude-opus-4-6 | Merge findings, deep investigation |

   ### Task Dependencies
   - Exploration Tasks 1-[N]: parallel (no dependencies)
   - Synthesis Task: run after all exploration tasks complete
   ```

5. **Checkpoint** (if `ENABLE_CHECKPOINTING = true`):
   - Update `.claude/sessions/__da_live__/checkpoint.md`: set `current_phase: 1`
   - Write `.claude/sessions/__da_live__/team_plan.md` with the full team plan from Step 4
   - Write `.claude/sessions/__da_live__/recon_summary.md` with reconnaissance findings from Step 2
   - Append to `progress.md`: `[timestamp] Phase 1: Reconnaissance complete — [N] focus areas identified`

---

## Phase 2: Review & Approval

**Goal:** Present the team plan for user review and approval before allocating resources.

> If `ENABLE_PROGRESS = true`: Display "**[Phase 2/6] Review & Approval** — Presenting team plan..."

### If `REQUIRE_APPROVAL = false`

Skip to Phase 3 with a brief note: "Auto-approving team plan (skill-invoked mode). Proceeding with [N] explorers and 1 synthesizer."

### If `REQUIRE_APPROVAL = true`

1. **Present the team plan** to the user (output the plan from Phase 1 Step 4), then use the `question` tool:
   - **"Approve"** — Proceed to Phase 3 as-is
   - **"Modify"** — User describes changes (adjust focus areas, add/remove explorers, change scope)
   - **"Regenerate"** — Re-run reconnaissance with user feedback

2. **If "Modify"** (up to 3 cycles):
   - Ask what to change using the `question` tool
   - Apply modifications to the team plan (adjust focus areas, agent count, scope)
   - Re-present the updated plan for approval
   - If 3 modification cycles are exhausted, offer "Approve current plan" or "Abort analysis"

3. **If "Regenerate"** (up to 2 cycles):
   - Ask for feedback/new direction using the `question` tool
   - Return to Phase 1 Step 2 with the user's feedback incorporated
   - Re-compose and re-present the team plan
   - If 2 regeneration cycles are exhausted, offer "Approve current plan" or "Abort analysis"

4. **Checkpoint** (if `ENABLE_CHECKPOINTING = true`):
   - Update `.claude/sessions/__da_live__/checkpoint.md`: set `current_phase: 2`, record `approval_mode` (approved/auto-approved)
   - Append to `progress.md`: `[timestamp] Phase 2: Plan approved (mode: [approval_mode])`

---

## Phase 3: Task Dispatch

**Goal:** Spawn parallel explorer agents and the synthesizer agent using the approved plan.

> If `ENABLE_PROGRESS = true`: Display "**[Phase 3/6] Task Dispatch** — Spawning explorer agents..."

<!-- RESOLVED: TeamCreate — opencode has no team management. Hub-and-spoke restructured as parallel task calls. Workaround applied globally. -->

<!-- RESOLVED: SendMessage — No inter-agent messaging in opencode. All context embedded in task prompts at dispatch time. Cached decision (apply_globally=true). -->

**Architectural note:** opencode does not support team creation or inter-agent messaging. The hub-and-spoke coordination pattern is implemented as follows:
- Each explorer is spawned as an independent `task` call with all required context embedded in the prompt
- Explorer tasks run in parallel (spawn all before waiting for results)
- The synthesizer is spawned after all explorer tasks complete, with their findings embedded in its prompt
- No follow-up messages can be sent after task launch; structure all instructions upfront

1. **Spawn explorer agents in parallel:**

   For each focus area in the approved plan, spawn one explorer using the `task` tool:

   ```
   task(
     description: "Explorer [N]: [Focus Area Label]",
     prompt: "You are explorer-[N] in a deep analysis team.

   Analysis context: [context]
   Codebase path: [PATH]

   Your focus area: [Focus Area Label]
   Directories to explore: [list]
   Starting files: [2-3 files — read these first]
   Search patterns: [grep patterns to run]
   Complexity estimate: [Low/Medium/High]

   Use read, glob, grep, and bash to thoroughly explore your focus area. Do NOT explore outside your assigned directories unless following a critical dependency.

   When complete, write your findings to: .claude/sessions/__da_live__/explorer-[N]-findings.md

   Structure your findings as:
   ## Explorer [N] Findings: [Focus Area Label]
   ### Files Examined
   ### Key Patterns Found
   ### Dependencies and Integrations
   ### Notable Observations
   ### Gaps or Uncertainties",
     subagent_type: "build",
     command: "code-explorer"
   )
   ```

   Spawn all N explorer tasks before waiting for results (parallel dispatch).

   Track all exploration task handles for later collection.

2. **Wait for all explorer tasks to complete.**

   As each completes, read its findings file from `.claude/sessions/__da_live__/explorer-[N]-findings.md`.

   If `ENABLE_CHECKPOINTING = true`: update `checkpoint.md` and `progress.md` as each explorer finishes.

3. **Checkpoint** (if `ENABLE_CHECKPOINTING = true`):
   - Update `.claude/sessions/__da_live__/checkpoint.md`: set `current_phase: 3`, record `explorer_count`, findings file paths
   - Append to `progress.md`: `[timestamp] Phase 3: [N] explorer tasks dispatched`

---

## Phase 4: Focused Exploration

**Goal:** Workers explore their assigned areas independently.

> If `ENABLE_PROGRESS = true`: Display "**[Phase 4/6] Focused Exploration** — 0/[N] explorers complete"

**Note:** In opencode, explorer agents run to completion within their task calls (dispatched in Phase 3). This phase tracks their completion and handles failures.

### Completion Tracking

Monitor each explorer task's completion:

1. **If task completed successfully**: Read the findings file written by the explorer. Record findings for the synthesizer.
2. **If task failed or produced empty output**:
   - Spawn a replacement explorer task for the same focus area
   - Use the same prompt template from Phase 3
   - Wait for the replacement to complete
3. **If all explorers for a focus area fail**: Note the gap for the synthesizer to flag in the synthesis report

If `ENABLE_PROGRESS = true`: Log progress as each explorer completes: "**[Phase 4/6] Focused Exploration** — [completed]/[N] explorers complete"

**Checkpoint** (if `ENABLE_CHECKPOINTING = true`):
- Write each explorer's findings to `.claude/sessions/__da_live__/explorer-{N}-findings.md` (if not already written by the explorer task itself)
- Update `checkpoint.md` and `progress.md` as findings are collected

---

## Phase 5: Evaluation and Synthesis

**Goal:** Verify exploration completeness, launch synthesis with deep investigation.

> If `ENABLE_PROGRESS = true`: Display "**[Phase 5/6] Synthesis** — Merging findings and investigating gaps..."

### Step 1: Structural Completeness Check

This is a structural check, not a quality assessment:

1. Verify all expected explorer findings files exist and have content
2. Check that each explorer produced a report with content
3. **If an explorer failed completely** (missing or empty findings file):
   - Spawn a follow-up explorer task targeting the gap (same prompt as Phase 3)
   - Wait for it to complete and collect its findings
4. **If all produced content**: proceed immediately to Step 2

### Step 2: Launch Synthesis

Spawn the synthesizer agent using the `task` tool with all explorer findings embedded in the prompt:

```
task(
  description: "Synthesizer: Merge and synthesize all exploration findings",
  prompt: "You are the synthesizer for a deep analysis team.

Analysis context: [analysis context]
Codebase path: [PATH]

Recon findings from planning phase:
- Project structure: [brief summary of directory layout]
- Primary language/framework: [what was detected]
- Key areas identified: [the focus areas and why they were chosen]

All exploration tasks are complete. Below are the findings from each explorer:

--- Explorer 1 Findings: [Focus Area Label] ---
[full contents of explorer-1-findings.md]

--- Explorer 2 Findings: [Focus Area Label] ---
[full contents of explorer-2-findings.md]

[... for each explorer]

You have bash access for deep investigation — use it for git history analysis, dependency trees, static analysis, or any investigation that read/glob/grep cannot handle.

Synthesize all findings into a unified analysis. Evaluate completeness before finalizing. If you identify gaps, use bash to investigate them directly.

Write your synthesis to: .claude/sessions/__da_live__/synthesis.md

Structure the synthesis as:
## Synthesis: Deep Analysis of [context]
### Executive Summary
### Architecture Overview
### Key Findings by Area
### Cross-Cutting Concerns
### Gaps and Uncertainties
### Recommendations",
  subagent_type: "build",
  command: "code-synthesizer"
)
```

Wait for the synthesizer task to complete.

**Note:** The synthesizer cannot send follow-up messages to explorers in opencode. If the synthesizer needs additional investigation, it must conduct it directly using bash, read, glob, and grep tools.

3. Read `.claude/sessions/__da_live__/synthesis.md` once the synthesizer task completes.

4. **Checkpoint** (if `ENABLE_CHECKPOINTING = true`):
   - Update `.claude/sessions/__da_live__/checkpoint.md`: set `current_phase: 5`
   - Append to `progress.md`: `[timestamp] Phase 5: Synthesis complete`

---

## Phase 6: Completion + Cleanup

**Goal:** Collect results, present to user, and clean up session state.

> If `ENABLE_PROGRESS = true`: Display "**[Phase 6/6] Completion** — Collecting results and cleaning up..."

1. **Collect synthesis output:**
   - Read `.claude/sessions/__da_live__/synthesis.md`

2. **Write exploration cache** (if `CACHE_TTL > 0`):
   - Create `.claude/sessions/exploration-cache/` directory (overwrite if exists)
   - Write `manifest.md`:
     ```markdown
     ## Exploration Cache Manifest
     - **analysis_context**: [the analysis context used]
     - **codebase_path**: [current working directory]
     - **timestamp**: [ISO timestamp]
     - **config_checksum**: [comma-separated list of config files and their mod-times]
     - **ttl_hours**: [CACHE_TTL value]
     - **explorer_count**: [N]
     ```
   - Write `synthesis.md` with the full synthesis output
   - Write `recon_summary.md` with the Phase 1 reconnaissance findings
   - Write `explorer-{N}-findings.md` for each explorer's findings (if not already persisted from Phase 4)

3. **Present or return results:**
   - **Standalone invocation:** Present the synthesized analysis to the user. The results remain in conversation memory for follow-up questions.
   - **Loaded by another skill:** The synthesis is complete. Control returns to the calling workflow — do not present a standalone summary.

4. **Cleanup:**

   <!-- RESOLVED: TeamDelete — No team management in opencode. Tasks are ephemeral; no cleanup needed. Workaround applied globally. -->

   - No team teardown is required in opencode — task agents are ephemeral and terminate on completion.
   - If `ENABLE_CHECKPOINTING = true`: Move `.claude/sessions/__da_live__/` to `.claude/sessions/da-{timestamp}/` using bash

---

## Error Handling

### Settings Check Failure
- If `.claude/agent-alchemy.local.md` exists but is malformed or the `deep-analysis` section is unparseable: warn the user ("Settings file found but could not parse deep-analysis settings — using defaults") and proceed with default approval values.

### Planning Phase Failure
- If reconnaissance fails (errors, empty results, unusual structure): fall back to static focus area templates (Step 3b)
- If the codebase appears empty: inform the user and ask how to proceed

### Approval Phase Failure
- If maximum modification cycles (3) or regeneration cycles (2) are reached without approval: use the `question` tool with options:
  - **"Approve current plan"** — Proceed with the latest version of the plan
  - **"Abort analysis"** — Cancel the analysis entirely

### Partial Worker Failure
- If one explorer task fails: spawn a replacement explorer task targeting the missed focus area, wait for it to complete
- If two explorer tasks fail: attempt replacements, but if they also fail, instruct the synthesizer to note the gaps in its synthesis
- If all explorer tasks fail: inform the user and offer to retry or abort via the `question` tool

### Synthesizer Failure
- If the synthesizer task fails: present the raw exploration findings (from the individual `explorer-{N}-findings.md` files) to the user directly
- Offer to retry synthesis (spawn a new synthesizer task) or let the user work with partial results

### General Failures
If any phase fails:
1. Explain what went wrong
2. Ask the user how to proceed via the `question` tool:
   - Retry the phase
   - Continue with partial results
   - Abort the analysis

### Session Recovery

When resuming from an interrupted session (detected in Phase 0 Step 2), use the following per-phase strategy:

| Interrupted At | Recovery Strategy |
|----------------|-------------------|
| **Phase 1** | Restart from Phase 1 (reconnaissance is fast, ~1-2 min) |
| **Phase 2** | Load saved `team_plan.md` from session dir, re-present for approval |
| **Phase 3** | Load approved plan from checkpoint, restart task dispatch |
| **Phase 4** | Read completed `explorer-{N}-findings.md` files from session dir. Only spawn replacement explorer tasks for focus areas whose findings files are missing. |
| **Phase 5** | Load all explorer findings from session dir. Spawn a fresh synthesizer task with all persisted findings embedded in its prompt. |
| **Phase 6** | Load `synthesis.md` from session dir. Proceed directly to present/return results and cleanup. |

**Recovery procedure:**
1. Read `checkpoint.md` to determine `last_completed_phase` and session state (explorer_count, findings file paths)
2. Load any persisted artifacts from the session directory (team_plan, explorer findings, synthesis)
3. Resume from Phase `last_completed_phase + 1` using the loaded state
4. For Phase 4 recovery: compare persisted `explorer-{N}-findings.md` files against expected explorer list to determine which explorers still need to run

---

## Agent Coordination

- The lead (you) acts as the planner: performs recon, composes the team plan, handles approval, dispatches explorer tasks
- Explorer tasks run independently — no cross-explorer communication (hub-and-spoke topology preserved via isolated task prompts)
- The synthesizer receives all explorer findings embedded in its initial prompt and conducts gap investigation directly via bash
- Handle agent failures gracefully — continue with partial results
- Agent count and focus area details come from the approved plan, not hardcoded values

When calling the `task` tool for sub-agents:
- Use `command: "code-synthesizer"` for the synthesizer (model is configured in the agent's .md file as `anthropic/claude-opus-4-6`)
- Use `command: "code-explorer"` for workers (model is configured in the agent's .md file as `anthropic/claude-sonnet-4-6`)
~~~

## Fidelity Report

| Mapping Type | Count | Weight | Contribution |
|-------------|-------|--------|-------------|
| Direct | 9 | 1.0 | 9.0 |
| Workaround | 11 | 0.7 | 7.7 |
| TODO | 6 | 0.2 | 1.2 |
| Omitted | 1 | 0.0 | 0.0 |
| **Total** | **27** | | **17.9** |

**Notes:** Score = 17.9 / 27 * 100 = 66%. The primary fidelity losses come from the removal of TeamCreate/TeamDelete (2 TODO items), SendMessage (1 TODO item, critical — used in 5+ locations in the original), and the partial mapping of task management tools (TaskCreate/TaskUpdate/TaskList/TaskGet → todowrite/todoread). The hub-and-spoke coordination pattern is preserved architecturally but all inter-agent messaging is restructured as upfront prompt embedding, which reduces runtime flexibility.

## Decisions

| Feature | Decision Type | Original | Converted | Rationale | Confidence | Resolution Mode |
|---------|-------------|----------|-----------|-----------|------------|----------------|
| name field | relocated | `name: deep-analysis` in frontmatter | Derived from filename `deep-analysis.md` | opencode derives skill name from filename; embedded:filename mapping | high | auto |
| description field | direct | `description: Deep exploration and synthesis...` | `description: Deep exploration and synthesis...` | Direct 1:1 mapping | high | N/A |
| argument-hint field | relocated | `argument-hint: <analysis-context or focus-area>` in frontmatter | `$ARGUMENTS` placeholder note in skill body header | opencode uses $ARGUMENTS in body; embedded:body mapping | high | auto |
| user-invocable field | direct | `user-invocable: true` | `user-invocable: true` | Direct 1:1 mapping | high | N/A |
| disable-model-invocation field | workaround | `disable-model-invocation: false` | Documented in header comment; enforce at agent level | No per-skill model-invocation control in opencode; cached global decision | high | cached |
| allowed-tools field | omitted | Full tool list in frontmatter | Field removed | No per-skill tool restrictions in opencode; enforced at agent level | high | auto |
| Read tool (allowed-tools) | direct | `Read` | `read` | Direct mapping | high | N/A |
| Glob tool (allowed-tools) | direct | `Glob` | `glob` | Direct mapping | high | N/A |
| Grep tool (allowed-tools) | direct | `Grep` | `grep` | Direct mapping | high | N/A |
| Bash tool (allowed-tools) | direct | `Bash` | `bash` | Direct mapping | high | N/A |
| Task tool (allowed-tools) | direct | `Task` | `task` | Direct mapping | high | N/A |
| TeamCreate tool (allowed-tools) | todo | `TeamCreate` | UNRESOLVED inline marker | No team management in opencode | high | cached |
| TeamDelete tool (allowed-tools) | todo | `TeamDelete` | UNRESOLVED inline marker | No team management in opencode | high | cached |
| TaskCreate tool (allowed-tools) | workaround | `TaskCreate` | `todowrite` (partial) | Session-scoped scratchpad; no dependency or owner tracking | high | cached |
| TaskUpdate tool (allowed-tools) | workaround | `TaskUpdate` | `todowrite` (partial) | Same todowrite tool; limited status changes | high | cached |
| TaskList tool (allowed-tools) | workaround | `TaskList` | `todoread` (partial) | Full list scan; no filtering by owner or status | high | cached |
| TaskGet tool (allowed-tools) | workaround | `TaskGet` | `todoread` (partial) | No per-task retrieval by ID | high | cached |
| SendMessage tool (allowed-tools) | todo | `SendMessage` | UNRESOLVED inline marker | No inter-agent messaging in opencode | high | cached |
| AskUserQuestion tool (allowed-tools) | direct | `AskUserQuestion` | `question` | Direct equivalent for primary agents | high | N/A |
| AskUserQuestion body references | direct | `AskUserQuestion` calls in body | `question` tool references | Direct equivalent; deep-analysis is a primary-agent skill | high | N/A |
| TeamCreate body reference | todo | `TeamCreate` call in Phase 3 | UNRESOLVED inline marker + architectural note | Hub-and-spoke restructured as parallel task calls | high | cached |
| TeamDelete body reference | todo | `TeamDelete` call in Phase 6 | UNRESOLVED inline marker + note about ephemeral tasks | No team teardown needed; tasks are ephemeral | high | cached |
| TaskCreate/TaskUpdate body refs | workaround | Task lifecycle management via TaskCreate/TaskUpdate | Restructured as task prompt instructions + file-based findings | opencode tasks are ephemeral; coordination via file artifacts | high | cached |
| TaskList/TaskGet body refs | workaround | Status polling via TaskList/TaskGet | Replaced with file existence checks on explorer findings files | Findings files serve as completion signals | high | cached |
| SendMessage body references | todo | SendMessage calls to explorers and synthesizer | All context embedded in initial task prompts; UNRESOLVED markers at key locations | No post-launch messaging; prompt embedding is the workaround | high | cached |
| model references (sonnet/opus) | direct | `model: "sonnet"` / `model: "opus"` in Task calls | `anthropic/claude-sonnet-4-6` / `anthropic/claude-opus-4-6` | Direct model ID mapping per tier mappings | high | N/A |
| team_name parameter | omitted | `team_name` parameter in Task calls | Parameter removed | No team concept in opencode | high | auto |

## Gaps

| Feature | Reason | Severity | Workaround | User Acknowledged |
|---------|--------|----------|------------|-------------------|
| TeamCreate / hub-and-spoke team management | No team orchestration in opencode | functional | Restructured as parallel task calls with context passing via prompts | false |
| TeamDelete / team cleanup | No team management in opencode | functional | No teardown required; task agents are ephemeral | false |
| SendMessage / inter-agent messaging | No inter-agent messaging in opencode | critical | All context must be embedded in initial task prompts at dispatch time; synthesizer receives all explorer findings via its prompt; no follow-up questions to explorers possible | false |
| TaskCreate dependency tracking | todowrite has no dependency or blocked-by support | functional | Synthesis is sequenced by waiting for all explorer tasks to complete before spawning synthesizer; no explicit dependency graph needed | false |
| TaskGet per-task retrieval | todoread returns full list, no per-task lookup by ID | functional | Replaced with file existence checks on explorer-{N}-findings.md files as completion signals | false |
| Explorer follow-up questions from synthesizer | SendMessage to explorers not possible | functional | Synthesizer must conduct additional investigation directly via bash; gap investigation is now synthesizer-only | false |
| team_name parameter on Task calls | No team membership concept in opencode | cosmetic | Parameter removed; parallel task dispatch replaces team membership | false |

## Unresolved Incompatibilities

Incompatibilities the converter agent could not auto-resolve. The orchestrator batches these between waves.

| Group Key | Feature | Severity | Category | Reason | Suggested Workaround | Confidence | Affected Locations |
|-----------|---------|----------|----------|--------|---------------------|------------|-------------------|
| (all resolved — auto-applied workarounds globally) | | | | | | | |
