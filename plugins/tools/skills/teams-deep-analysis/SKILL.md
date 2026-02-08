---
name: teams-deep-analysis
description: Team-based deep exploration and synthesis workflow using Agent Teams for inter-agent collaboration. Use when asked for "teams deep analysis", "team-based analysis", "collaborative analysis", or "teams-deep-analysis".
argument-hint: <analysis-context or focus-area>
model: inherit
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Glob, Grep, Bash, Task, TeamCreate, TeamDelete, TaskCreate, TaskUpdate, TaskList, TaskGet, SendMessage, AskUserQuestion
---

# Teams Deep Analysis Workflow

Execute a structured exploration + synthesis workflow using Agent Teams for inter-agent collaboration. Explorers share discoveries with each other as they work, and the synthesizer can ask explorers follow-up questions to clarify conflicts and fill gaps.

This skill can be invoked standalone or loaded by other skills as a reusable building block.

## Phase 1: Team Setup

**Goal:** Create the team, spawn teammates, and assign exploration tasks.

1. **Determine analysis context:**
   - If `$ARGUMENTS` is provided, use it as the analysis context (feature area, question, or general exploration goal)
   - If no arguments and this skill was loaded by another skill, use the calling skill's context
   - If no arguments and standalone invocation, set context to "general codebase understanding"
   - Set `PATH = current working directory`
   - Inform the user: "Exploring codebase at: `PATH`" with the analysis context

2. **Load skills for this phase:**
   - Read `${CLAUDE_PLUGIN_ROOT}/skills/project-conventions/SKILL.md` and apply its guidance
   - Read `${CLAUDE_PLUGIN_ROOT}/skills/language-patterns/SKILL.md` and apply its guidance

3. **Create the team:**
   - Use `TeamCreate` with name `deep-analysis-{timestamp}` (e.g., `deep-analysis-1707300000`)
   - Description: "Collaborative deep analysis of [analysis context]"

4. **Spawn teammates:**
   Use the Task tool with the `team_name` parameter to spawn 5 teammates:

   - **3 explorers** — `subagent_type: "claude-alchemy-tools:team-code-explorer"`, model: sonnet
     - Named: `explorer-1`, `explorer-2`, `explorer-3`
     - Prompt each with: "You are part of a deep analysis team. Wait for your task assignment. The codebase is at: [PATH]. Analysis context: [context]"

   - **1 synthesizer** — `subagent_type: "claude-alchemy-tools:team-codebase-synthesizer"`, model: opus
     - Named: `synthesizer`
     - Prompt with: "You are the synthesizer for a deep analysis team. Wait for your task assignment. The codebase is at: [PATH]. Analysis context: [context]"

   - **1 analyst** — `subagent_type: "claude-alchemy-tools:team-deep-analyst"`, model: opus
     - Named: `analyst`
     - Prompt with: "You are the deep analyst for a deep analysis team. You have no pre-assigned task. Wait for analysis requests from the synthesizer. The codebase is at: [PATH]. Analysis context: [context]"

5. **Determine focus areas:**
   - For feature-focused analysis:
     ```
     Focus 1: Explore entry points and user-facing code related to the context
     Focus 2: Explore data models, schemas, and storage related to the context
     Focus 3: Explore utilities, helpers, and shared infrastructure
     ```
   - For general codebase understanding:
     ```
     Focus 1: Explore application structure, entry points, and core logic
     Focus 2: Explore configuration, infrastructure, and shared utilities
     Focus 3: Explore shared utilities, patterns, and cross-cutting concerns
     ```

6. **Create tasks:**
   Use `TaskCreate` for each task:

   - **Exploration Task 1:** Subject: "Explore: [Focus 1]", Description: detailed exploration instructions for focus area 1
   - **Exploration Task 2:** Subject: "Explore: [Focus 2]", Description: detailed exploration instructions for focus area 2
   - **Exploration Task 3:** Subject: "Explore: [Focus 3]", Description: detailed exploration instructions for focus area 3
   - **Synthesis Task:** Subject: "Synthesize exploration findings", Description: "Merge and synthesize findings from all 3 exploration tasks into a unified analysis. Ask explorers follow-up questions to clarify conflicts and fill gaps."
     - Use `TaskUpdate` to set `addBlockedBy` pointing to all 3 exploration task IDs

7. **Assign exploration tasks:**
   Use `TaskUpdate` to assign:
   - Exploration Task 1 → `owner: "explorer-1"`
   - Exploration Task 2 → `owner: "explorer-2"`
   - Exploration Task 3 → `owner: "explorer-3"`

---

## Phase 2: Collaborative Exploration

**Goal:** Explorers work in parallel, sharing discoveries with each other.

- Explorers work on their assigned focus areas
- They proactively share significant discoveries with each other via `SendMessage` (this behavior is built into the `team-code-explorer` agent)
- Each explorer marks its task as completed when done
- You (the lead) receive idle notifications as explorers finish
- **Wait for all 3 exploration tasks to be marked complete** before proceeding to Phase 3

---

## Phase 3: Lead Checkpoint + Synthesis

**Goal:** Verify exploration completeness, then launch synthesis.

### Step 1: Structural Completeness Check

This is a structural check, not a quality assessment:

1. Use `TaskList` to verify all 3 exploration tasks are completed
2. Check that each explorer produced a report with content (review the messages/reports received)
3. **If an explorer failed completely** (empty or error output):
   - Create a follow-up exploration task targeting the gap
   - Assign it to an idle explorer
   - Add the new task to the synthesis task's `blockedBy` list
   - Wait for the follow-up task to complete
4. **If all 3 produced content**: proceed immediately to Step 2

### Step 2: Launch Synthesis

1. Use `TaskUpdate` to assign the synthesis task: `owner: "synthesizer"`
2. Send the synthesizer a message with the exploration context:
   ```
   SendMessage type: "message", recipient: "synthesizer",
   content: "All 3 exploration tasks are complete. Your synthesis task is now assigned.

   Exploration context: [analysis context]
   Codebase path: [PATH]

   The explorers are: explorer-1, explorer-2, explorer-3. You can message them with follow-up questions if you find conflicts or gaps in their findings.

   The deep analyst is: analyst. You can delegate complex investigations to it when you need deeper analysis — it has Bash access for git history, dependency trees, and static analysis. Use it for cross-cutting concerns, security audits, performance analysis, or when explorer reports conflict and you need ground truth from git history.

   Read the completed exploration tasks via TaskGet to access their reports, then synthesize into a unified analysis.",
   summary: "Synthesis task assigned, begin work"
   ```
3. Wait for the synthesizer to mark the synthesis task as completed

---

## Phase 4: Completion + Cleanup

**Goal:** Collect results, present to user, and tear down the team.

1. **Collect synthesis output:**
   - The synthesizer's findings are in the messages it sent and/or the task completion output
   - Read the synthesis results

2. **Present or return results:**
   - **Standalone invocation:** Present the synthesized analysis to the user. The results remain in conversation memory for follow-up questions.
   - **Loaded by another skill:** The synthesis is complete. Control returns to the calling workflow — do not present a standalone summary.

3. **Shutdown teammates:**
   Send shutdown requests to all 5 teammates:
   ```
   SendMessage type: "shutdown_request", recipient: "explorer-1", content: "Analysis complete"
   SendMessage type: "shutdown_request", recipient: "explorer-2", content: "Analysis complete"
   SendMessage type: "shutdown_request", recipient: "explorer-3", content: "Analysis complete"
   SendMessage type: "shutdown_request", recipient: "synthesizer", content: "Analysis complete"
   SendMessage type: "shutdown_request", recipient: "analyst", content: "Analysis complete"
   ```

4. **Cleanup team:**
   - Use `TeamDelete` to remove the team and its task list

---

## Error Handling

### Partial Explorer Failure
- If one explorer fails: create a follow-up task targeting the missed focus area, assign to an idle explorer, add to synthesis `blockedBy`
- If two explorers fail: attempt follow-ups, but if they also fail, instruct the synthesizer to work with partial results
- If all explorers fail: inform the user and offer to retry or abort

### Analyst Failure
- If the analyst fails or doesn't respond: the synthesizer falls back to its own tools (Read, Glob, Grep)
- Analyst findings are supplementary — synthesis should never block on analyst response
- Note in the final output if analyst-dependent areas have reduced depth

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

---

## Agent Coordination

- Give each explorer a distinct focus area to minimize overlap
- Explorers collaborate by sharing notable discoveries via `SendMessage`
- The synthesizer can ask explorers follow-up questions to resolve conflicts
- The deep analyst activates on demand from the synthesizer for complex investigations
- Wait for task dependencies to resolve before proceeding
- Handle agent failures gracefully — continue with partial results

When calling Task tool for teammates:
- Use `model: "opus"` for the synthesizer and analyst
- Use default model (sonnet) for explorers
- Always include `team_name` parameter to join the team
