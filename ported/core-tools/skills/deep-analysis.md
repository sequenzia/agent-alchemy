---
name: deep-analysis
description: Deep exploration and synthesis workflow using a team of agents with dynamic planning and hub-and-spoke coordination. Use when asked for "deep analysis", "deep understanding", "analyze codebase", "explore and analyze", or "investigate codebase".
dependencies:
  - code-explorer
  - code-synthesizer
---

# Deep Analysis Workflow

Execute a structured exploration + synthesis workflow using a team of agents with hub-and-spoke coordination. The lead performs rapid reconnaissance to generate dynamic focus areas, composes a team plan for review, workers explore independently, and a synthesizer merges findings with shell-command-powered investigation.

This skill can be invoked standalone or loaded by other skills as a reusable building block.

**Inputs:** An optional analysis context or focus area describing what to explore.

## Configurable Settings

The following parameters can be configured by the user or harness:

| Setting | Default | Description |
|---------|---------|-------------|
| `approval-required` | `true` (standalone), `false` (loaded by another skill) | Whether the team plan requires user approval before execution |
| `cache-ttl-hours` | `24` | Hours before exploration cache expires. Set to `0` to disable caching. |
| `enable-checkpointing` | `true` | Write session checkpoints at phase boundaries for recovery |
| `enable-progress-indicators` | `true` | Display phase progress messages during execution |

---

## Phase 0: Session Setup

**Goal:** Check for cached exploration results, detect interrupted sessions, and initialize the session directory.

> Skip this phase entirely if caching and checkpointing are both disabled.

### Step 1: Exploration Cache Check

If caching is enabled:

1. Check if a cached exploration manifest exists
2. If found, verify:
   - The analysis context matches the current request (or is a superset)
   - The codebase path matches the current working directory
   - The timestamp is within the cache TTL
   - Config files referenced in the manifest haven't been modified since caching
3. **If cache is valid:**
   - **Loaded by another skill:** Auto-accept the cache. Read cached synthesis and reconnaissance summary. Skip to Phase 6 step 2 (present/return results).
   - **Standalone invocation:** Prompt the user:
     - **Use cached results** — Skip to Phase 6 step 2
     - **Refresh analysis** — Proceed normally
4. **If cache is invalid or absent:** Proceed normally

### Step 2: Interrupted Session Check

If checkpointing is enabled:

1. Check if an in-progress session checkpoint exists
2. If found, read the checkpoint to determine the last completed phase
3. Prompt the user:
   - **Resume from next phase** — Load checkpoint state and resume
   - **Start fresh** — Archive the interrupted session and proceed normally
4. If not found: proceed normally

### Step 3: Initialize Session Directory

If checkpointing is enabled and no cache hit:

1. Create a session directory
2. Write a checkpoint file with session metadata (analysis context, codebase path, timestamp, current phase)
3. Write an initial progress log

---

## Phase 1: Reconnaissance & Planning

**Goal:** Perform codebase reconnaissance, generate dynamic focus areas, and compose a team plan.

1. **Determine analysis context:**
   - If an input argument is provided, use it as the analysis context (feature area, question, or general exploration goal)
   - If no arguments and this skill was loaded by another skill, use the calling skill's context
   - If no arguments and standalone invocation, set context to "general codebase understanding"
   - Inform the user: "Exploring codebase at: [path]" with the analysis context

2. **Rapid codebase reconnaissance:**
   Quickly map the codebase structure (target: 1-2 minutes, not deep investigation):

   - **Directory structure:** List top-level directories to understand the project layout
   - **Language and framework detection:** Read config files (`package.json`, `tsconfig.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, etc.) to identify primary language(s) and framework(s)
   - **File distribution:** Search for files matching patterns like `src/**/*.ts`, `**/*.py` to gauge the size and shape of different areas
   - **Key documentation:** Read `README.md`, `CLAUDE.md`, or similar docs if they exist
   - **For feature-focused analysis:** Search for feature-related terms to find hotspot directories
   - **For general analysis:** Identify the 3-5 largest or most architecturally significant directories

   **Fallback:** If reconnaissance fails (empty project, unusual structure, errors), use the static focus area templates from Step 3b.

3. **Generate dynamic focus areas:**

   Based on reconnaissance findings, create focus areas tailored to the actual codebase. Default to 3 focus areas, but adjust based on codebase size and complexity (2 for small projects, up to 4 for large ones).

   **a) Dynamic focus areas (default):**

   Each focus area should include:
   - **Label:** Short description (e.g., "API layer in src/api/")
   - **Directories:** Specific directories to explore
   - **Starting files:** 2-3 key files to read first
   - **Search terms:** Patterns to find related code
   - **Complexity estimate:** Low/Medium/High based on file count and apparent structure

   For feature-focused analysis, focus areas should track the feature's actual footprint:
   ```
   Example:
   Focus 1: "API routes and middleware in src/api/ and src/middleware/"
   Focus 2: "React components in src/pages/profile/ and src/components/user/"
   Focus 3: "Data models and services in src/db/ and src/services/"
   ```

   For general analysis, focus areas should map to the codebase's actual structure:
   ```
   Example:
   Focus 1: "Next.js app layer in apps/web/src/"
   Focus 2: "Shared library in packages/core/src/"
   Focus 3: "CLI and tooling in packages/cli/"
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

   Assemble a structured plan from the reconnaissance and focus area findings:

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
   - **Search patterns:** [patterns]
   - **Complexity:** [Low/Medium/High]
   - **Assigned to:** explorer-1

   #### Focus Area 2: [Label]
   [... repeated for each focus area]

   ### Agent Composition
   | Role | Count | Purpose |
   |------|-------|---------|
   | Explorer | [N] | Independent focus area exploration |
   | Synthesizer | 1 | Merge findings, deep investigation |

   ### Task Dependencies
   - Exploration Tasks 1-[N]: parallel (no dependencies)
   - Synthesis Task: blocked by all exploration tasks
   ```

5. **Checkpoint** (if enabled):
   - Save the team plan and reconnaissance findings to the session directory
   - Update progress log

---

## Phase 2: Review & Approval

**Goal:** Present the team plan for user review and approval before allocating resources.

### If approval is not required

Skip to Phase 3 with a brief note: "Auto-approving team plan. Proceeding with [N] explorers and 1 synthesizer."

### If approval is required

1. **Present the team plan** to the user, then prompt for a decision:
   - **Approve** — Proceed to Phase 3 as-is
   - **Modify** — User describes changes (adjust focus areas, add/remove explorers, change scope)
   - **Regenerate** — Re-run reconnaissance with user feedback

2. **If "Modify"** (up to 3 cycles):
   - Ask what to change
   - Apply modifications to the team plan
   - Re-present the updated plan for approval
   - If 3 modification cycles are exhausted, offer "Approve current plan" or "Abort analysis"

3. **If "Regenerate"** (up to 2 cycles):
   - Ask for feedback/new direction
   - Return to Phase 1 Step 2 with the user's feedback incorporated
   - Re-compose and re-present the team plan
   - If 2 regeneration cycles are exhausted, offer "Approve current plan" or "Abort analysis"

4. **Checkpoint** (if enabled): Save approval status

---

## Phase 3: Team Assembly

**Goal:** Create the team, define tasks, and assign work using the approved plan.

1. **Set up the team workspace** for coordinating the analysis agents.

2. **Spawn worker agents:**
   Based on the approved plan:

   - **N explorer agents** (one per focus area):
     - Named: `explorer-1`, `explorer-2`, ... `explorer-N`
     - Each is a **code-explorer** agent
     - Each can run in parallel if the harness supports concurrent agents

   - **1 synthesizer agent:**
     - Named: `synthesizer`
     - A **code-synthesizer** agent
     - Has shell command access for git history, dependency analysis, and static analysis

3. **Define tasks:**
   Create sub-tasks based on the approved plan's focus areas:

   - **Exploration task per focus area:** Include detailed instructions with directories, starting files, search terms, and complexity estimate
   - **Synthesis task:** "Merge and synthesize findings from all exploration tasks into a unified analysis. Investigate gaps. Evaluate completeness before finalizing."
     - The synthesis task depends on all exploration tasks completing first

4. **Assign exploration tasks:**

   For each exploration task:
   1. Check the task's current status
   2. Only assign if the task is pending and unassigned
   3. If already assigned or completed: skip (do not re-assign)
   4. Assign the task to the corresponding explorer
   5. Send the explorer its task details: focus area, directories, starting files, search patterns

   **Never re-assign a completed or in-progress task.**

5. **Checkpoint** (if enabled): Save team name, explorer names, task IDs

---

## Phase 4: Focused Exploration

**Goal:** Workers explore their assigned areas independently.

### Monitoring Loop

After assigning exploration tasks, monitor progress:

1. When an explorer finishes or reports status, check its task state
2. **If task is completed**: Record the explorer's findings. Save to session directory if checkpointing.
3. **If task is in progress**: The explorer is still working — do not re-send the assignment
4. **If task is pending and assigned**: The explorer received the assignment but hasn't started — wait
5. **If task is pending and unassigned**: Assignment may have been lost — re-assign (with status guard)

**Never re-assign a completed or in-progress task.** This is the primary duplicate prevention mechanism.

Update progress as explorers complete: "[completed]/[N] explorers complete"

- Workers explore their assigned focus areas independently — no cross-worker messaging (hub-and-spoke topology)
- Workers can respond to follow-up questions from the synthesizer
- Each worker reports task completion when done
- **Wait for all exploration tasks to complete** before proceeding to Phase 5

---

## Phase 5: Evaluation and Synthesis

**Goal:** Verify exploration completeness, launch synthesis with deep investigation.

### Step 1: Structural Completeness Check

This is a structural check, not a quality assessment:

1. Verify all exploration tasks are completed
2. Check that each worker produced a report with content
3. **If a worker failed completely** (empty or error output):
   - Create a follow-up exploration task targeting the gap
   - Assign it to an idle worker
   - Add it as a prerequisite for the synthesis task
   - Wait for the follow-up task to complete
4. **If all produced content**: proceed immediately to Step 2

### Step 2: Launch Synthesis

1. Assign the synthesis task to the synthesizer agent
2. Provide the synthesizer with all exploration context:
   - Analysis context and codebase path
   - Reconnaissance findings from Phase 1
   - The list of explorer names so it can ask them follow-up questions
   - Instructions to investigate gaps using shell commands (git history, dependency analysis, static analysis)
   - Instructions to evaluate completeness before finalizing
3. Wait for the synthesizer to complete its task

4. **Checkpoint** (if enabled): Save synthesis results

---

## Phase 6: Completion + Cleanup

**Goal:** Collect results, present to user, and tear down the team.

1. **Collect synthesis output:**
   - Read the synthesizer's findings from its task report or messages

2. **Write exploration cache** (if caching is enabled):
   - Save a manifest with: analysis context, codebase path, timestamp, config file checksums, TTL, explorer count
   - Save the full synthesis output
   - Save the reconnaissance summary
   - Save each explorer's findings

3. **Present or return results:**
   - **Standalone invocation:** Present the synthesized analysis to the user. The results remain in conversation memory for follow-up questions.
   - **Loaded by another skill:** The synthesis is complete. Control returns to the calling workflow.

4. **Shut down agents:**
   Gracefully terminate all spawned agents (explorers and synthesizer). The harness manages agent lifecycle.

5. **Archive session and clean up:**
   - If checkpointing is enabled: archive the session directory
   - Clean up the team workspace

---

## Error Handling

### Planning Phase Failure
- If reconnaissance fails (errors, empty results, unusual structure): fall back to static focus area templates
- If the codebase appears empty: inform the user and ask how to proceed

### Approval Phase Failure
- If maximum modification (3) or regeneration (2) cycles are reached without approval, offer:
  - **Approve current plan** — Proceed with the latest version
  - **Abort analysis** — Cancel entirely

### Partial Worker Failure
- If one worker fails: create a follow-up task targeting the missed focus area, assign to an idle worker
- If two workers fail: attempt follow-ups, but if they also fail, instruct the synthesizer to work with partial results
- If all workers fail: inform the user and offer to retry or abort

### Synthesizer Failure
- If the synthesizer fails: present the raw exploration results to the user directly
- Offer to retry synthesis or let the user work with partial results

### General Failures
If any phase fails:
1. Explain what went wrong
2. Ask the user how to proceed:
   - Retry the phase
   - Continue with partial results
   - Abort the analysis

### Session Recovery

When resuming from an interrupted session (detected in Phase 0 Step 2):

| Interrupted At | Recovery Strategy |
|----------------|-------------------|
| **Phase 1** | Restart from Phase 1 (reconnaissance is fast, ~1-2 min) |
| **Phase 2** | Load saved team plan, re-present for approval |
| **Phase 3** | Load approved plan, restart team assembly |
| **Phase 4** | Read saved explorer findings. Only spawn and assign explorers whose findings are missing. Add existing findings to synthesizer context. |
| **Phase 5** | Load all explorer findings. Spawn a fresh synthesizer and launch synthesis with the persisted findings. |
| **Phase 6** | Load saved synthesis. Proceed directly to present/return results and cleanup. |

---

## Agent Coordination

- The lead (you) acts as the planner: performs recon, composes the team plan, handles approval, assigns work
- Workers explore independently — no cross-worker messaging (hub-and-spoke topology)
- The synthesizer can ask workers follow-up questions to resolve conflicts and fill gaps
- The synthesizer has shell command access for deep investigation (git history, dependency trees, static analysis)
- Wait for task dependencies to resolve before proceeding
- Handle agent failures gracefully — continue with partial results
- Agent count and focus area details come from the approved plan, not hardcoded values

---

## Integration Notes

**What this component does:** Orchestrates a multi-agent codebase exploration workflow where independent explorers investigate focus areas in parallel, and a synthesizer merges their findings into a unified analysis.

**Capabilities needed:**
- File reading and searching (for reconnaissance)
- Shell command execution (for reconnaissance and the synthesizer's deep investigation)
- User interaction / prompting (for approval flow and cache decisions)
- Sub-agent delegation (to spawn explorer and synthesizer agents)
- Task tracking (to manage exploration and synthesis tasks)
- Team coordination (to create team workspace and manage agent lifecycle)

**Adaptation guidance:**
- The core pattern is hub-and-spoke: a lead coordinates N independent workers + 1 synthesizer
- If your harness doesn't support concurrent agents, run explorers sequentially — the workflow still works, just slower
- The original used balanced-tier models for explorers (cost-effective parallelism) and a high-reasoning model for the synthesizer (quality synthesis) — adapt model selection to your harness's capabilities
- Session checkpointing and caching are optional optimizations — disable them for simplicity in initial integration
- The approval flow can be bypassed entirely by setting `approval-required: false`

**Configurable parameters:**
- `approval-required` (default: true for standalone, false when loaded by another skill)
- `cache-ttl-hours` (default: 24, set to 0 to disable)
- `enable-checkpointing` (default: true)
- `enable-progress-indicators` (default: true)
