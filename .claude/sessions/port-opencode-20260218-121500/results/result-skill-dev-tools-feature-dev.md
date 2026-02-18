# Conversion Result: skill-dev-tools-feature-dev

## Metadata

| Field | Value |
|-------|-------|
| Component ID | skill-dev-tools-feature-dev |
| Component Type | skill |
| Group | dev-tools |
| Name | feature-dev |
| Source Path | claude/dev-tools/skills/feature-dev/SKILL.md |
| Target Path | .opencode/skills/feature-dev.md |
| Fidelity Score | 72% |
| Fidelity Band | yellow |
| Status | partial |

## Converted Content

~~~markdown
---
description: Feature development workflow with exploration, architecture, implementation, and review phases. Use for implementing new features or significant changes. Note: per-skill tool restrictions are not supported in opencode; tool access is controlled at the agent level.
user-invocable: true
---

# Feature Development Workflow

Execute a structured 7-phase feature development workflow. This workflow guides you through understanding, exploring, designing, implementing, and reviewing a feature.

**CRITICAL: Complete ALL 7 phases.** The workflow is not complete until Phase 7: Summary is finished. After completing each phase, immediately proceed to the next phase without waiting for user prompts.

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

1. Analyze the feature description from `$ARGUMENTS`:
   - What is the core functionality?
   - What are the expected inputs and outputs?
   - Are there any constraints mentioned?
   - What success criteria can you infer?

2. Summarize your understanding to the user. Use the question tool to confirm if your understanding is correct before proceeding.

---

## Phase 2: Codebase Exploration

**Goal:** Understand the relevant parts of the codebase.

1. **Run deep-analysis workflow:**
   - Invoke skill({ name: "deep-analysis" }) and follow its workflow
   - Pass the feature description from Phase 1 as the analysis context
   - This handles reconnaissance, team planning, approval (auto-approved when skill-invoked), team creation, parallel exploration (code-explorer agents), and synthesis (code-synthesizer agent)
   - **Note:** Deep-analysis may return cached results if a valid exploration cache exists. In skill-invoked mode, cache hits are auto-accepted — this is expected behavior that avoids redundant exploration.

2. Present the synthesized analysis to the user.

---

## Phase 3: Clarifying Questions

**Goal:** Resolve any ambiguities before designing.

1. Review the feature requirements and exploration findings.

2. Identify underspecified aspects:
   - Edge cases not covered
   - Technical decisions that could go multiple ways
   - Integration points that need clarification
   - Performance or scale requirements

3. **Ask clarifying questions:**
   Use the question tool to get answers for critical unknowns. Only ask questions that would significantly impact the implementation.

   If no clarifying questions are needed, inform the user and proceed.

---

## Phase 4: Architecture Design

**Goal:** Design the implementation approach.

1. **Load skills for this phase:**
   - Invoke skill({ name: "architecture-patterns" }) and apply its guidance
   - Invoke skill({ name: "language-patterns" }) and apply its guidance

2. **Launch code-architect agents:**

   Launch 2-3 code-architect agents (anthropic/claude-opus-4-6) with different approaches:
   ```
   Agent 1: Design a minimal, focused approach prioritizing simplicity
   Agent 2: Design a flexible, extensible approach prioritizing future changes
   Agent 3: Design an approach optimized for the project's existing patterns (if applicable)
   ```

   Use the task tool with `command: "code-architect"`:
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

3. **Present approaches:**
   - Summarize each approach
   - Compare trade-offs (simplicity, flexibility, performance, maintainability)
   - Make a recommendation with justification

4. **User chooses approach:**
   Use the question tool to let the user select an approach or request modifications.

5. **Generate ADR artifact:**
   <!-- RESOLVED: unsupported_composition:reference_dir_null — Inline reference file content into skill body; TODO for reference inlining. Cached decision (apply_globally=true). -->
   - Load the ADR template (reference file `references/adr-template.md` is not resolvable via opencode path resolution; inline the template content below or configure via opencode.json `instructions` array)
   - Create an ADR documenting:
     - Context: Why this feature is needed
     - Decision: The chosen approach
     - Consequences: Trade-offs and implications
     - Alternatives: Other approaches considered
   - Determine the next ADR number by checking existing files in `internal/docs/adr/`
   - Save to `internal/docs/adr/NNNN-[feature-slug].md` (create `internal/docs/adr/` if needed)
   - Inform the user of the saved ADR location

---

## Phase 5: Implementation

**Goal:** Build the feature.

1. **Require explicit approval:**
   Ask the user: "Ready to begin implementation of [feature] using [chosen approach]?"
   Wait for confirmation before proceeding.

2. **Read all relevant files:**
   Before making any changes, read the complete content of every file you'll modify.

3. **Implement the feature:**
   - Follow the chosen architecture design
   - Match existing code patterns and conventions
   - Create new files as needed
   - Update existing files using the edit tool
   - Add appropriate error handling
   - Include inline comments only where logic isn't obvious

4. **Test if applicable:**
   - If the project has tests, add tests for the new functionality
   - Run existing tests to ensure nothing broke

5. **IMPORTANT: Proceed immediately to Phase 6.**
   Do NOT stop here. Do NOT wait for user input. Implementation is complete, but the workflow requires Quality Review and Summary phases. Continue directly to Phase 6 now.

---

## Phase 6: Quality Review

**Goal:** Review the implementation for issues.

1. **Load skills for this phase:**
   - Invoke skill({ name: "code-quality" }) and apply its guidance

2. **Launch code-reviewer agents:**

   Launch 3 code-reviewer agents (anthropic/claude-opus-4-6) with different focuses:
   ```
   Agent 1: Review for correctness and edge cases
   Agent 2: Review for security and error handling
   Agent 3: Review for maintainability and code quality
   ```

   Use the task tool with `command: "code-reviewer"`:
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

3. **Aggregate findings:**
   - Collect results from all reviewers
   - Deduplicate similar issues
   - Prioritize by severity and confidence

4. **Present findings:**
   Show the user:
   - Critical issues (must fix)
   - Moderate issues (should fix)
   - Minor suggestions (nice to have)

5. **User decides:**
   Use the question tool:
   - "Fix all issues now"
   - "Fix critical issues only"
   - "Proceed without fixes"
   - "I'll fix manually later"

6. If fixing: make the changes and re-review if needed.

7. **IMPORTANT: Proceed immediately to Phase 7.**
   Do NOT stop here. The workflow requires a Summary phase to document accomplishments and update the CHANGELOG. Continue directly to Phase 7 now.

---

## Phase 7: Summary

**Goal:** Document and celebrate accomplishments.

1. **Summarize accomplishments:**
   Present to the user:
   - What was built
   - Key files created/modified
   - Architecture decisions made
   - Any known limitations or future work

2. **Update CHANGELOG.md:**
   <!-- RESOLVED: unsupported_composition:reference_dir_null — Inline reference file content into skill body; TODO for reference inlining. Cached decision (apply_globally=true). -->
   - Load the changelog entry template (reference file `references/changelog-entry-template.md` is not resolvable via opencode path resolution; inline the template content or configure via opencode.json `instructions` array)
   - Invoke skill({ name: "changelog-format" }) for Keep a Changelog guidelines
   - Create an entry under the `[Unreleased]` section with:
     - Appropriate category (Added, Changed, Fixed, etc.)
     - Concise description of the feature
   - If `CHANGELOG.md` doesn't exist, create it with proper header
   - Add the entry to the appropriate section under `[Unreleased]`
   - Inform the user of the update

3. **Final message:**
   Congratulate the user and offer next steps:
   - Commit the changes
   - Create a PR
   - Additional testing suggestions

---

## Error Handling

If any phase fails:
1. Explain what went wrong
2. Ask the user how to proceed:
   - Retry the phase
   - Skip to next phase
   - Abort the workflow

---

## Agent Coordination

Exploration and synthesis agent coordination is handled by the `deep-analysis` skill in Phase 2, which uses parallel task calls with hub-and-spoke coordination. Deep-analysis performs reconnaissance, composes a team plan (auto-approved when invoked by another skill), assembles the team, and manages the exploration/synthesis lifecycle. See that skill for team setup, approval flow, agent model tiers, and failure handling details.

Note: opencode does not support TeamCreate or inter-agent messaging (SendMessage). Agent teams are orchestrated as sequential or parallel task calls with context passed through task prompts. The deep-analysis skill handles this internally.

When launching other parallel agents (code-architect from core-tools, code-reviewer):
- Give each agent a distinct focus area
- Wait for all agents to complete before proceeding
- Handle agent failures gracefully (continue with partial results)

When calling the task tool for agents:
- Use `command: "code-architect"` (cross-plugin agent from core-tools group)
- Use `command: "code-reviewer"` for review agents (same plugin group)
- Code-explorer and code-synthesizer models are managed by deep-analysis

Note: The question tool is only available to primary agents, not subagents. Skills invoked via task that require user input must structure questions into the initial task prompt.

## Additional Resources

- For ADR template, see references/adr-template.md (inline content into this skill body or configure via opencode.json `instructions` array — opencode has no reference_dir support)
- For changelog entry format, see references/changelog-entry-template.md (same constraint)
~~~

## Fidelity Report

| Mapping Type | Count | Weight | Contribution |
|-------------|-------|--------|-------------|
| Direct | 14 | 1.0 | 14.0 |
| Workaround | 5 | 0.7 | 3.5 |
| TODO | 2 | 0.2 | 0.4 |
| Omitted | 4 | 0.0 | 0.0 |
| **Total** | **25** | | **17.9 / 25 = 71.6 → 72%** |

**Notes:** The 4 omitted features are the `allowed-tools` field itself (no per-skill tool restrictions in opencode), `TeamCreate`, `TeamDelete`, and `SendMessage` (no team/inter-agent messaging support). The 5 workarounds cover `disable-model-invocation` (documented in description), `TaskCreate`, `TaskUpdate`, `TaskList`, `TaskGet` (partial todowrite/todoread equivalents). The 2 TODOs are the `adr-template.md` and `changelog-entry-template.md` reference files which cannot be resolved via opencode path resolution.

## Decisions

| Feature | Decision Type | Original | Converted | Rationale | Confidence | Resolution Mode |
|---------|-------------|----------|-----------|-----------|------------|----------------|
| name field | relocated | `name: feature-dev` | Derived from filename `feature-dev.md` | opencode derives skill name from filename; field omitted from frontmatter | high | auto |
| argument-hint field | relocated | `argument-hint: <feature-description>` | `$ARGUMENTS` placeholder in body (already present) | opencode detects `$ARGUMENTS` in body automatically; field omitted from frontmatter | high | auto |
| disable-model-invocation field | workaround | `disable-model-invocation: false` | Documented in description text | Field has no equivalent in opencode. Behavior note added to description. Cached decision applied globally. | high | cached |
| allowed-tools field | omitted | Full tool list | Field removed | opencode has no per-skill tool restrictions; access controlled at agent level only | high | auto |
| TeamCreate in allowed-tools | omitted | `TeamCreate` | Removed from tool list | No team/multi-agent orchestration in opencode. Cached: restructure as parallel task calls. | high | cached |
| TeamDelete in allowed-tools | omitted | `TeamDelete` | Removed from tool list | No team management in opencode; tasks are ephemeral, no cleanup needed. Cached decision applied globally. | high | cached |
| TaskCreate in allowed-tools | workaround | `TaskCreate` | `todowrite` (partial) | Session-scoped scratchpad only; no dependencies, owners, or structured statuses. Cached decision applied globally. | high | cached |
| TaskUpdate in allowed-tools | workaround | `TaskUpdate` | `todowrite` (partial) | Same todowrite tool; limited status changes. Cached decision applied globally. | high | cached |
| TaskList in allowed-tools | workaround | `TaskList` | `todoread` (partial) | Returns full list only; no filtering by owner or status. Cached decision applied globally. | high | cached |
| TaskGet in allowed-tools | workaround | `TaskGet` | `todoread` (partial) | No per-task retrieval by ID; must scan full list. Cached decision applied globally. | high | cached |
| SendMessage in allowed-tools | omitted | `SendMessage` | Removed from tool list | No inter-agent messaging in opencode; context passed only through task prompt. Cached decision applied globally. | high | cached |
| AskUserQuestion body refs | partial | `AskUserQuestion` | `question tool` | Direct equivalent exists but only available to primary agents, not subagents. Feature-dev is user-invocable so primary-agent constraint is met. | high | auto |
| Task tool body refs | direct | `Task tool` / `subagent_type` | `task tool` / `command:` | Direct equivalent; subagent_type syntax updated to opencode `command:` parameter | high | auto |
| deep-analysis composition | direct | `Read ${CLAUDE_PLUGIN_ROOT}/../core-tools/skills/deep-analysis/SKILL.md` | `skill({ name: "deep-analysis" })` | Cross-plugin reference supported; mechanism is `reference`; registry-based resolution | high | auto |
| architecture-patterns composition | direct | `Read ${CLAUDE_PLUGIN_ROOT}/skills/architecture-patterns/SKILL.md` | `skill({ name: "architecture-patterns" })` | Same-plugin reference; mechanism is `reference` | high | auto |
| language-patterns composition | direct | `Read ${CLAUDE_PLUGIN_ROOT}/../core-tools/skills/language-patterns/SKILL.md` | `skill({ name: "language-patterns" })` | Cross-plugin reference supported; registry-based resolution | high | auto |
| code-quality composition | direct | `Read ${CLAUDE_PLUGIN_ROOT}/skills/code-quality/SKILL.md` | `skill({ name: "code-quality" })` | Same-plugin reference; mechanism is `reference` | high | auto |
| changelog-format composition | direct | `load the changelog-format skill` (body prose) | `skill({ name: "changelog-format" })` | Same-plugin reference; mechanism is `reference` | high | auto |
| adr-template reference file | TODO | `Read ${CLAUDE_PLUGIN_ROOT}/skills/feature-dev/references/adr-template.md` | UNRESOLVED marker + prose instruction | opencode has no reference_dir; cached decision: inline content or use opencode.json instructions array | medium | cached |
| changelog-entry-template reference file | TODO | `Read ${CLAUDE_PLUGIN_ROOT}/skills/feature-dev/references/changelog-entry-template.md` | UNRESOLVED marker + prose instruction | opencode has no reference_dir; cached decision: inline content or use opencode.json instructions array | medium | cached |
| code-architect subagent_type | direct | `subagent_type: "agent-alchemy-core-tools:code-architect"` | `command: "code-architect"` | opencode Task tool uses `command` parameter for named agents | high | auto |
| code-reviewer subagent_type | direct | `subagent_type: "code-reviewer"` | `command: "code-reviewer"` | opencode Task tool uses `command` parameter for named agents | high | auto |
| model tier references (Opus) | direct | `Opus` (prose) | `anthropic/claude-opus-4-6` | Updated model tier references in body prose | high | auto |

## Gaps

| Feature | Reason | Severity | Workaround | User Acknowledged |
|---------|--------|----------|------------|-------------------|
| allowed-tools per-skill restrictions | opencode has no per-skill tool restrictions; only agent-level permission config | functional | Document restriction; control tools at agent level via permission config | false |
| TeamCreate / TeamDelete | No team/multi-agent orchestration in opencode | functional | Restructure as parallel task calls; deep-analysis handles internally via task tool | false |
| SendMessage | No inter-agent messaging in opencode | functional | Context passed through task prompt; deep-analysis handles internally | false |
| TaskCreate / TaskUpdate / TaskList / TaskGet | Partial equivalents only via todowrite/todoread; no dependencies, owners, structured statuses, or per-ID retrieval | functional | Use todowrite/todoread with metadata embedded in description text | false |
| adr-template reference file | opencode has no reference_dir; ${CLAUDE_PLUGIN_ROOT} path resolution is not supported | functional | Inline adr-template.md content into skill body, or add file path to opencode.json `instructions` array | false |
| changelog-entry-template reference file | opencode has no reference_dir; ${CLAUDE_PLUGIN_ROOT} path resolution is not supported | functional | Inline changelog-entry-template.md content into skill body, or add file path to opencode.json `instructions` array | false |
| disable-model-invocation | No per-skill model invocation control in opencode | cosmetic | Documented in skill description; restrict at agent level if needed | false |
| question tool subagent restriction | question tool only available to primary agents, not subagents | cosmetic | feature-dev is user-invocable (primary agent context); constraint is noted in Agent Coordination section | false |

## Unresolved Incompatibilities

| Group Key | Feature | Severity | Category | Reason | Suggested Workaround | Confidence | Affected Locations |
|-----------|---------|----------|----------|--------|---------------------|------------|-------------------|
| unsupported_composition:reference_dir_null | adr-template reference file | functional | unsupported_composition | opencode has no reference_dir; reference files cannot be resolved at runtime via path | Inline adr-template.md content directly into this skill body, or add the file path to opencode.json `instructions` array for session-wide loading | medium | 1 location (Phase 4, Step 5) |
| unsupported_composition:reference_dir_null | changelog-entry-template reference file | functional | unsupported_composition | opencode has no reference_dir; reference files cannot be resolved at runtime via path | Inline changelog-entry-template.md content directly into this skill body, or add the file path to opencode.json `instructions` array for session-wide loading | medium | 1 location (Phase 7, Step 2) |
