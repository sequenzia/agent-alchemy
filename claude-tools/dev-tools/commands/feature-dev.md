---
description: Feature development workflow with exploration, architecture, implementation, and review phases
argument-hint: <feature-description>
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Task
  - TodoWrite
  - AskUserQuestion
arguments:
  - name: feature-description
    description: Description of the feature to implement
    required: true
---

# Feature Development Workflow

You are executing a structured 7-phase feature development workflow. This workflow guides you through understanding, exploring, designing, implementing, and reviewing a feature.

**CRITICAL: You MUST complete ALL 7 phases.** The workflow is not complete until Phase 7: Summary is finished. After completing each phase, immediately proceed to the next phase without waiting for user prompts.

## Phase Overview

Execute these phases in order, completing ALL of them:

1. **Discovery** - Understand the feature requirements
2. **Codebase Exploration** - Map relevant code areas
3. **Clarifying Questions** - Resolve ambiguities
4. **Architecture Design** - Design the implementation approach
5. **Implementation** - Build the feature
6. **Quality Review** - Review for issues
7. **Summary** - Document accomplishments

---

## Phase 1: Discovery

**Goal:** Understand what the user wants to build.

1. Create a TodoWrite entry for each phase:
   ```
   - Phase 1: Discovery
   - Phase 2: Codebase Exploration
   - Phase 3: Clarifying Questions
   - Phase 4: Architecture Design
   - Phase 5: Implementation
   - Phase 6: Quality Review
   - Phase 7: Summary
   ```

2. Mark Phase 1 as `in_progress`

3. Analyze the feature description:
   - What is the core functionality?
   - What are the expected inputs and outputs?
   - Are there any constraints mentioned?
   - What success criteria can you infer?

4. Summarize your understanding to the user. Ask if your understanding is correct before proceeding.

5. Mark Phase 1 as `completed`

---

## Phase 2: Codebase Exploration

**Goal:** Understand the relevant parts of the codebase.

1. Mark Phase 2 as `in_progress`

2. **Load skills for this phase:**
   - Read `${CLAUDE_PLUGIN_ROOT}/skills/project-conventions/SKILL.md` and apply its guidance
   - Read `${CLAUDE_PLUGIN_ROOT}/skills/language-patterns/SKILL.md` and apply its guidance

3. **Launch code-explorer agents:**

   Launch 2-3 code-explorer agents in parallel with different focus areas:
   ```
   Agent 1: Explore entry points and user-facing code related to the feature
   Agent 2: Explore data models, schemas, and storage related to the feature
   Agent 3: Explore utilities, helpers, and shared infrastructure (if applicable)
   ```

   Use the Task tool with `subagent_type: "dev-tools:code-explorer"`:
   ```
   Feature: [feature description]
   Focus area: [specific focus for this agent]

   Find and analyze:
   - Relevant files and their purposes
   - Key functions/classes that would be modified or extended
   - Existing patterns to follow
   - Potential integration points

   Return a structured report of your findings.
   ```

4. **Synthesize findings:**
   - Collect results from all agents
   - Identify the key files that will need modification
   - Note existing patterns and conventions
   - List any potential challenges discovered

5. **Read key files:**
   - Read all files identified as critical for the implementation
   - Build a mental model of how they work together

6. Present exploration findings to the user.

7. Mark Phase 2 as `completed`

---

## Phase 3: Clarifying Questions

**Goal:** Resolve any ambiguities before designing.

1. Mark Phase 3 as `in_progress`

2. Review the feature requirements and exploration findings.

3. Identify underspecified aspects:
   - Edge cases not covered
   - Technical decisions that could go multiple ways
   - Integration points that need clarification
   - Performance or scale requirements

4. **Ask clarifying questions:**
   Use AskUserQuestion to get answers for critical unknowns. Only ask questions that would significantly impact the implementation.

   If no clarifying questions are needed, inform the user and proceed.

5. Mark Phase 3 as `completed`

---

## Phase 4: Architecture Design

**Goal:** Design the implementation approach.

1. Mark Phase 4 as `in_progress`

2. **Load skills for this phase:**
   - Read `${CLAUDE_PLUGIN_ROOT}/skills/architecture-patterns/SKILL.md` and apply its guidance
   - Read `${CLAUDE_PLUGIN_ROOT}/skills/language-patterns/SKILL.md` and apply its guidance

3. **Launch code-architect agents:**

   Launch 2-3 code-architect agents (Opus) with different approaches:
   ```
   Agent 1: Design a minimal, focused approach prioritizing simplicity
   Agent 2: Design a flexible, extensible approach prioritizing future changes
   Agent 3: Design an approach optimized for the project's existing patterns (if applicable)
   ```

   Use the Task tool with `subagent_type: "dev-tools:code-architect"`:
   ```
   Feature: [feature description]
   Design approach: [specific approach for this agent]

   Based on the codebase exploration:
   [Summary of relevant files and patterns]

   Design an implementation that:
   - Lists files to create/modify
   - Describes the changes needed in each file
   - Explains the data flow
   - Identifies risks and mitigations

   Return a detailed implementation blueprint.
   ```

4. **Present approaches:**
   - Summarize each approach
   - Compare trade-offs (simplicity, flexibility, performance, maintainability)
   - Make a recommendation with justification

5. **User chooses approach:**
   Use AskUserQuestion to let the user select an approach or request modifications.

6. **Generate ADR artifact:**
   - Read the ADR template from `${CLAUDE_PLUGIN_ROOT}/references/adr-template.md`
   - Create an ADR documenting:
     - Context: Why this feature is needed
     - Decision: The chosen approach
     - Consequences: Trade-offs and implications
     - Alternatives: Other approaches considered
   - Determine the next ADR number by checking existing files in `internal/docs/adr/`
   - Save to `internal/docs/adr/NNNN-[feature-slug].md` (create `internal/docs/adr/` if needed)
   - Inform the user of the saved ADR location

7. Mark Phase 4 as `completed`

---

## Phase 5: Implementation

**Goal:** Build the feature.

1. Mark Phase 5 as `in_progress`

2. **Require explicit approval:**
   Ask the user: "Ready to begin implementation of [feature] using [chosen approach]?"
   Wait for confirmation before proceeding.

3. **Read all relevant files:**
   Before making any changes, read the complete content of every file you'll modify.

4. **Implement the feature:**
   - Follow the chosen architecture design
   - Match existing code patterns and conventions
   - Create new files as needed
   - Update existing files using Edit tool
   - Add appropriate error handling
   - Include inline comments only where logic isn't obvious

5. **Track progress:**
   Create sub-tasks in TodoWrite for each major implementation step.
   Mark each as completed when done.

6. **Test if applicable:**
   - If the project has tests, add tests for the new functionality
   - Run existing tests to ensure nothing broke

7. Mark Phase 5 as `completed`

8. **IMPORTANT: Proceed immediately to Phase 6.**
   Do NOT stop here. Do NOT wait for user input. Implementation is complete, but the workflow requires Quality Review and Summary phases. Continue directly to Phase 6 now.

---

## Phase 6: Quality Review

**Goal:** Review the implementation for issues.

1. Mark Phase 6 as `in_progress`

2. **Load skills for this phase:**
   - Read `${CLAUDE_PLUGIN_ROOT}/skills/code-quality/SKILL.md` and apply its guidance

3. **Launch code-reviewer agents:**

   Launch 3 code-reviewer agents (Opus) with different focuses:
   ```
   Agent 1: Review for correctness and edge cases
   Agent 2: Review for security and error handling
   Agent 3: Review for maintainability and code quality
   ```

   Use the Task tool with `subagent_type: "dev-tools:code-reviewer"`:
   ```
   Review focus: [specific focus for this agent]

   Files to review:
   [List of files modified/created]

   Review the implementation and report:
   - Issues found with confidence scores (0-100)
   - Suggestions for improvement
   - Positive observations

   Only report issues with confidence >= 80.
   ```

4. **Aggregate findings:**
   - Collect results from all reviewers
   - Deduplicate similar issues
   - Prioritize by severity and confidence

5. **Present findings:**
   Show the user:
   - Critical issues (must fix)
   - Moderate issues (should fix)
   - Minor suggestions (nice to have)

6. **User decides:**
   Use AskUserQuestion:
   - "Fix all issues now"
   - "Fix critical issues only"
   - "Proceed without fixes"
   - "I'll fix manually later"

7. If fixing: make the changes and re-review if needed.

8. Mark Phase 6 as `completed`

9. **IMPORTANT: Proceed immediately to Phase 7.**
   Do NOT stop here. The workflow requires a Summary phase to document accomplishments and update the CHANGELOG. Continue directly to Phase 7 now.

---

## Phase 7: Summary

**Goal:** Document and celebrate accomplishments.

1. Mark Phase 7 as `in_progress`

2. **Ensure all todos complete:**
   Mark any remaining sub-tasks as completed.

3. **Summarize accomplishments:**
   Present to the user:
   - What was built
   - Key files created/modified
   - Architecture decisions made
   - Any known limitations or future work

4. **Update CHANGELOG.md:**
   - Read the entry template from `${CLAUDE_PLUGIN_ROOT}/references/feature-changelog-template.md`
   - Load the `changelog-format` skill for Keep a Changelog guidelines
   - Create an entry under the `[Unreleased]` section with:
     - Appropriate category (Added, Changed, Fixed, etc.)
     - Concise description of the feature
   - If `CHANGELOG.md` doesn't exist, create it with proper header
   - Add the entry to the appropriate section under `[Unreleased]`
   - Inform the user of the update

5. Mark Phase 7 as `completed`

6. **Final message:**
   Congratulate the user and offer next steps:
   - Commit the changes
   - Create a PR
   - Additional testing suggestions

7. **Verify workflow completion:**
   Confirm all 7 phases in TodoWrite are marked `completed`. If any phase was skipped, note it in your final summary.

---

## Error Handling

If any phase fails:
1. Mark the phase as blocked in TodoWrite
2. Explain what went wrong
3. Ask the user how to proceed:
   - Retry the phase
   - Skip to next phase
   - Abort the workflow

---

## Agent Coordination

When launching parallel agents:
- Give each agent a distinct focus area
- Wait for all agents to complete before synthesizing
- Handle agent failures gracefully (continue with partial results)

When calling Task tool for agents:
- Use `model: "opus"` for code-architect and code-reviewer agents
- Use default model (sonnet) for code-explorer agents
- Use `run_in_background: false` to wait for results
