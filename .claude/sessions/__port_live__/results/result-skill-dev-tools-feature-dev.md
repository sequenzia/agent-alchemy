# Conversion Result: skill-dev-tools-feature-dev

## Metadata

| Field | Value |
|-------|-------|
| Component ID | skill-dev-tools-feature-dev |
| Component Type | skill |
| Group | dev-tools |
| Name | feature-dev |
| Source Path | claude/dev-tools/skills/feature-dev/SKILL.md |
| Target Path | skills/feature-dev/SKILL.md |
| Fidelity Score | 45% |
| Fidelity Band | red |
| Status | limited |

## Converted Content

~~~markdown
---
description: Feature development workflow with exploration, architecture, implementation, and review phases. Use for implementing new features or significant changes.
user-invocable: true
---

# Feature Development Workflow

Execute a structured 7-phase feature development workflow. This workflow guides you through understanding, exploring, designing, implementing, and reviewing a feature.

The feature to implement is provided via `$ARGUMENTS` (e.g., `/feature-dev add user profile editing`).

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

2. Summarize your understanding to the user. Use the `question` tool to confirm if your understanding is correct before proceeding.

---

## Phase 2: Codebase Exploration

**Goal:** Understand the relevant parts of the codebase.

1. **Run deep-analysis workflow:**
   - Invoke `skill({ name: "deep-analysis" })` and follow its workflow
   - Pass the feature description from Phase 1 as the analysis context
   - This handles reconnaissance, team planning, approval (auto-approved when skill-invoked), parallel exploration (code-explorer subagents via task tool), and synthesis (code-synthesizer subagent via task tool)
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
   Use the `question` tool to get answers for critical unknowns. Only ask questions that would significantly impact the implementation.

   If no clarifying questions are needed, inform the user and proceed.

---

## Phase 4: Architecture Design

**Goal:** Design the implementation approach.

1. **Load skills for this phase:**
   - Invoke `skill({ name: "architecture-patterns" })` and apply its guidance
   - Invoke `skill({ name: "language-patterns" })` and apply its guidance

2. **Launch code-architect subagents:**

   Launch 2-3 code-architect subagents (Opus) with different approaches:
   ```
   Agent 1: Design a minimal, focused approach prioritizing simplicity
   Agent 2: Design a flexible, extensible approach prioritizing future changes
   Agent 3: Design an approach optimized for the project's existing patterns (if applicable)
   ```

   Use the `task` tool with `command: "code-architect"`:
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
   Use the `question` tool to let the user select an approach or request modifications.

5. **Generate ADR artifact:**

   Use the following ADR template when creating the Architecture Decision Record:

   ---
   **ADR Template:**

   ```markdown
   # ADR-NNNN: [Title]

   **Date:** YYYY-MM-DD
   **Status:** Accepted
   **Feature:** [Feature name/description]

   ## Context

   [Describe the situation that led to this decision. Include:]
   - What problem are we solving?
   - What constraints do we have?
   - What are the driving forces?

   ## Decision

   [State the decision clearly and concisely. Include:]
   - What approach are we taking?
   - Key architectural choices made
   - Technologies/patterns selected

   ## Consequences

   ### Positive
   - [Benefit 1]
   - [Benefit 2]
   - [Benefit 3]

   ### Negative
   - [Tradeoff 1]
   - [Tradeoff 2]

   ### Risks
   - [Risk 1 and mitigation]
   - [Risk 2 and mitigation]

   ## Alternatives Considered

   ### Alternative 1: [Name]
   [Brief description]
   - **Pros:** [List]
   - **Cons:** [List]
   - **Why rejected:** [Reason]

   ### Alternative 2: [Name]
   [Brief description]
   - **Pros:** [List]
   - **Cons:** [List]
   - **Why rejected:** [Reason]

   ## Implementation Notes

   [Any specific implementation guidance:]
   - Key files to create/modify
   - Important patterns to follow
   - Integration points

   ## References

   - [Link to related docs]
   - [Link to similar implementations]
   ```

   **ADR Usage Instructions:**

   1. **Determine ADR number:** Check existing files in `internal/docs/adr/`. Use the next sequential number (e.g., 0001, 0002). If no ADRs exist, start with 0001.
   2. **Create filename:** Format: `NNNN-feature-slug.md`. Use kebab-case for the slug.
   3. **Fill in the template:** Be specific about the context. State the decision clearly. List real consequences. Document alternatives considered.
   4. **Save location:** Create `internal/docs/adr/` directory if it doesn't exist. Save the ADR there.

   ---

   Create an ADR documenting:
   - Context: Why this feature is needed
   - Decision: The chosen approach
   - Consequences: Trade-offs and implications
   - Alternatives: Other approaches considered

   Determine the next ADR number by checking existing files in `internal/docs/adr/`.
   Save to `internal/docs/adr/NNNN-[feature-slug].md` (create `internal/docs/adr/` if needed).
   Inform the user of the saved ADR location.

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
   - Update existing files using the `edit` tool
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
   - Invoke `skill({ name: "code-quality" })` and apply its guidance

2. **Launch code-reviewer subagents:**

   Launch 3 code-reviewer subagents (Opus) with different focuses:
   ```
   Agent 1: Review for correctness and edge cases
   Agent 2: Review for security and error handling
   Agent 3: Review for maintainability and code quality
   ```

   Use the `task` tool with `command: "code-reviewer"`:
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
   - Collect results from all reviewer subagents
   - Deduplicate similar issues
   - Prioritize by severity and confidence

4. **Present findings:**
   Show the user:
   - Critical issues (must fix)
   - Moderate issues (should fix)
   - Minor suggestions (nice to have)

5. **User decides:**
   Use the `question` tool:
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

   Use the following changelog entry format when adding entries:

   ---
   **Changelog Entry Format:**

   Entries should be concise, user-focused lines under the appropriate category:

   ```markdown
   ### Added
   - Add [feature name] with [key capability]

   ### Changed
   - Update [component] to [new behavior]

   ### Fixed
   - Fix [issue description]
   ```

   **Changelog Usage Instructions:**

   1. **Locate CHANGELOG.md:** Find the project's `CHANGELOG.md` in the repository root. If it doesn't exist, create it using the structure below.
   2. **Find the `[Unreleased]` section:** Entries go under `## [Unreleased]`. If the section doesn't exist, add it after the header.
   3. **Choose the appropriate category:** Added (new features), Changed (existing functionality), Deprecated, Removed, Fixed (bug fixes), Security.
   4. **Write concise entries:** Use imperative mood ("Add feature" not "Added feature"). Focus on user-facing changes. One line per distinct change.

   **If creating a new CHANGELOG.md:**

   ```markdown
   # Changelog

   All notable changes to this project will be documented in this file.

   The format is based on [Keep a Changelog](https://keepachangelog.com/),
   and this project adheres to [Semantic Versioning](https://semver.org/).

   ## [Unreleased]

   ### Added
   - Your new feature entry here
   ```

   ---

   - Invoke `skill({ name: "changelog-format" })` for additional Keep a Changelog guidelines
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
2. Ask the user how to proceed using the `question` tool:
   - Retry the phase
   - Skip to next phase
   - Abort the workflow

---

## Agent Coordination

Exploration and synthesis subagent coordination is handled by the `deep-analysis` skill in Phase 2, which uses orchestrated `task` tool calls with hub-and-spoke coordination. Deep-analysis performs reconnaissance, composes a plan (auto-approved when invoked by another skill), and manages the exploration/synthesis lifecycle via sequential/parallel `task` calls. See that skill for subagent setup, approval flow, model tiers, and failure handling details.

When launching other parallel subagents (code-architect from core-tools, code-reviewer):
- Give each subagent a distinct focus area
- Wait for all subagents to complete before proceeding
- Handle subagent failures gracefully (continue with partial results)

When calling the `task` tool for subagents:
- Use `command: "code-architect"` for architecture design subagents (Opus tier)
- Use `command: "code-reviewer"` for review subagents (Opus tier)
- Code-explorer and code-synthesizer subagents are managed by deep-analysis
- Each subagent receives all necessary context via the `prompt` parameter — subagents are fully isolated and cannot receive messages after spawning
~~~

## Fidelity Report

| Mapping Type | Count | Weight | Contribution |
|-------------|-------|--------|-------------|
| Direct | 12 | 1.0 | 12.0 |
| Workaround | 8 | 0.7 | 5.6 |
| TODO | 0 | 0.2 | 0.0 |
| Omitted | 19 | 0.0 | 0.0 |
| **Total** | **39** | | **17.6** |

**Score:** 17.6 / 39 * 100 = **45%**

**Notes:** The low fidelity score is driven primarily by the 15 `allowed-tools` entries (all omitted because `allowed-tools` maps to null in OpenCode — tool restrictions are agent-level only) and the 4 omitted frontmatter fields (`name`, `disable-model-invocation`, `model` absence, `allowed-tools` field itself). Functionally, this conversion is high-fidelity: all 7 phases are preserved, all skill compositions converted to `skill()` references, both reference files inlined, all `AskUserQuestion` calls converted to `question`, and all `task` subagent spawns preserved. The structural loss is metadata-only.

## Decisions

| Feature | Decision Type | Original | Converted | Rationale | Confidence | Resolution Mode |
|---------|-------------|----------|-----------|-----------|------------|----------------|
| `name` frontmatter field | omitted | `name: feature-dev` | Derived from directory `skills/feature-dev/SKILL.md` | `name` maps to `embedded:filename` in OpenCode; directory name serves as the skill identifier | high | auto |
| `disable-model-invocation` frontmatter field | omitted | `disable-model-invocation: false` | Removed | Maps to null; OpenCode has no concept of preventing model auto-invocation. Value was `false` so no behavioral change. | high | auto |
| `allowed-tools` frontmatter field | omitted | 15-tool list | Removed | Maps to null; OpenCode has no per-skill tool restrictions. Tool restrictions are agent-level via `permission` frontmatter only. | high | auto |
| `argument-hint` frontmatter field | relocated | `argument-hint: <feature-description>` | `$ARGUMENTS` placeholder in body | Maps to `embedded:body`; OpenCode auto-detects `$NAME` placeholders in skill body | high | auto |
| `description` frontmatter field | direct | `description: Feature development workflow...` | `description: Feature development workflow...` | Direct 1:1 mapping | high | N/A |
| `user-invocable` frontmatter field | direct | `user-invocable: true` | `user-invocable: true` | Direct 1:1 mapping | high | N/A |
| AskUserQuestion (Phase 1 confirm) | direct | `AskUserQuestion` | `question` tool | AskUserQuestion maps to `question` tool in OpenCode | medium | N/A |
| AskUserQuestion (Phase 3 clarify) | direct | `AskUserQuestion` | `question` tool | AskUserQuestion maps to `question` tool in OpenCode | medium | N/A |
| AskUserQuestion (Phase 4 approach select) | direct | `AskUserQuestion` | `question` tool | AskUserQuestion maps to `question` tool in OpenCode | medium | N/A |
| AskUserQuestion (Phase 6 fix decision) | direct | `AskUserQuestion` | `question` tool | AskUserQuestion maps to `question` tool in OpenCode | medium | N/A |
| AskUserQuestion (error handling) | direct | `AskUserQuestion` | `question` tool | AskUserQuestion maps to `question` tool in OpenCode | medium | N/A |
| deep-analysis composition (Phase 2) | direct | `Read ${CLAUDE_PLUGIN_ROOT}/../core-tools/skills/deep-analysis/SKILL.md` | `skill({ name: "deep-analysis" })` | Cross-plugin composition supported; reference mechanism with registry-based resolution | high | N/A |
| architecture-patterns composition (Phase 4) | direct | `Read ${CLAUDE_PLUGIN_ROOT}/skills/architecture-patterns/SKILL.md` | `skill({ name: "architecture-patterns" })` | Same-plugin composition; reference mechanism | high | N/A |
| language-patterns composition (Phase 4) | direct | `Read ${CLAUDE_PLUGIN_ROOT}/../core-tools/skills/language-patterns/SKILL.md` | `skill({ name: "language-patterns" })` | Cross-plugin composition supported | high | N/A |
| code-quality composition (Phase 6) | direct | `Read ${CLAUDE_PLUGIN_ROOT}/skills/code-quality/SKILL.md` | `skill({ name: "code-quality" })` | Same-plugin composition; reference mechanism | high | N/A |
| changelog-format skill load (Phase 7) | direct | Load `changelog-format` skill | `skill({ name: "changelog-format" })` | Same-plugin reference mechanism | high | N/A |
| adr-template.md reference (Phase 4) | workaround | `Read ${CLAUDE_PLUGIN_ROOT}/skills/feature-dev/references/adr-template.md` | ADR template content inlined into Phase 4 body | `reference_dir` is null in OpenCode; cached decision: inline reference content into skill body | high | cached |
| changelog-entry-template.md reference (Phase 7) | workaround | `Read ${CLAUDE_PLUGIN_ROOT}/skills/feature-dev/references/changelog-entry-template.md` | Changelog entry format inlined into Phase 7 body | `reference_dir` is null in OpenCode; cached decision: inline reference content into skill body | high | cached |
| TeamCreate in body/Agent Coordination | workaround | `TeamCreate` / Agent Teams hub-and-spoke | Restructured as orchestrated `task` tool calls with explicit context passing | TeamCreate maps to null; cached decision: replace with sequential/parallel task calls | high | cached |
| TeamDelete in body/Agent Coordination | workaround | `TeamDelete` | Removed — no cleanup needed when using `task` tool | TeamDelete maps to null; cached decision: remove | high | cached |
| SendMessage in Agent Coordination | workaround | `SendMessage` / inter-agent messaging | Output-based communication — subagents output findings in final response, `task` tool returns to parent | SendMessage maps to null; cached decision: output-based communication | high | cached |
| code-architect subagent type (Phase 4) | workaround | `subagent_type: "agent-alchemy-core-tools:code-architect"` | `command: "code-architect"` | OpenCode uses `command` with agent name; cross-plugin agent names resolve from merged registry | high | N/A |
| code-reviewer subagent type (Phase 6) | workaround | `subagent_type: "code-reviewer"` | `command: "code-reviewer"` | OpenCode uses `command` with agent name | high | N/A |
| TaskCreate (allowed-tools only) | omitted | `TaskCreate` in allowed-tools | Removed from tool list | Maps to partial:todowrite; only appeared in allowed-tools (no body references) — omitted per null allowed-tools field | high | cached |
| TaskUpdate (allowed-tools only) | omitted | `TaskUpdate` in allowed-tools | Removed from tool list | Maps to partial:todowrite; only in allowed-tools | high | cached |
| TaskList (allowed-tools only) | omitted | `TaskList` in allowed-tools | Removed from tool list | Maps to partial:todoread; only in allowed-tools | high | cached |
| TaskGet (allowed-tools only) | omitted | `TaskGet` in allowed-tools | Removed from tool list | Maps to partial:todoread; only in allowed-tools | high | cached |

## Gaps

| Feature | Reason | Severity | Workaround | User Acknowledged |
|---------|--------|----------|------------|-------------------|
| `allowed-tools` field | No per-skill tool restrictions in OpenCode; agent-level `permission` only | cosmetic | Tool restrictions can be set at agent level in `opencode.json` under `permission` key | false |
| `disable-model-invocation` field | OpenCode has no concept of preventing model auto-invocation via skills | cosmetic | Skills are always discoverable via `skill` tool; no workaround needed (field was `false`) | false |
| `name` frontmatter field | Derived from directory name in OpenCode, not declared in frontmatter | cosmetic | Directory `skills/feature-dev/` provides the skill name automatically | false |
| Reference directory (`references/`) | `reference_dir` is null in OpenCode; no equivalent standalone reference file mechanism | functional | Both reference files (adr-template.md, changelog-entry-template.md) inlined into skill body per cached resolution | false |
| TeamCreate / Agent Teams | No team/multi-agent orchestration primitives in OpenCode | functional | Restructured as orchestrated sequential/parallel `task` tool calls with explicit context passing in prompts | false |
| TeamDelete | No team management in OpenCode | cosmetic | Removed; no cleanup needed when using task tool calls | false |
| SendMessage | No inter-agent messaging; subagents are fully isolated | functional | Output-based communication: subagents output findings, task tool returns result to parent | false |
| Cross-plugin agent reference (`agent-alchemy-core-tools:code-architect`) | OpenCode uses `command` key with agent name; cross-plugin namespace prefix not used | functional | Use `command: "code-architect"` — agent resolves from merged registry across all plugin groups | false |

## Unresolved Incompatibilities

No unresolved incompatibilities. All gaps were resolved via cached decisions (reference inlining, task-based team restructuring, SendMessage output-based pattern) or auto-resolved as cosmetic (allowed-tools, disable-model-invocation, name field).
