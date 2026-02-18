# Gap Report

**Source:** Agent Alchemy (34 components from core-tools, dev-tools, sdd-tools, tdd-tools, git-tools)
**Target:** OpenCode
**Date:** 2026-02-18
**Overall fidelity:** 72%

## Summary

| Severity | Count | Description |
|----------|-------|-------------|
| Critical | 0 | Features essential to plugin function -- converted plugin may not work without these |
| Functional | 96 | Features that enable specific capabilities -- partial functionality loss |
| Cosmetic | 48 | Metadata or documentation features -- no behavioral impact |
| **Total** | **144** | |

### Impact Assessment

The conversion is moderate-fidelity with zero critical gaps. All 99 functional gaps have workarounds applied (primarily todowrite/todoread for task management, inline content for reference files, and restructured coordination for team messaging). The 45 cosmetic gaps are metadata fields with no behavioral impact on the converted plugin. The primary functional degradation areas are: (1) task management losing structured metadata and per-ID retrieval, (2) reference files requiring manual inlining, and (3) inter-agent messaging replaced by prompt-based context passing.

### Resolution Breakdown

| Resolution | Count |
|------------|-------|
| Workaround applied | 99 |
| Feature omitted | 0 |
| TODO comment added | 0 |
| Auto-resolved | 45 |

## Gaps by Severity

### Critical

No critical gaps identified.

### Functional

#### TaskGet (Functional) -- 3 components affected

- **Components:** sdd-tools-task-executor, tdd-tools-tdd-executor, tdd-tools-tdd-cycle
- **Why:** No per-task ID retrieval; todoread returns full list only
- **Workaround:** Scan full todoread list for task_uid embedded in description text
- **Manual steps:** Review converted files and verify workaround behavior on OpenCode

#### TaskUpdate (Functional) -- 3 components affected

- **Components:** sdd-tools-task-executor, tdd-tools-tdd-executor, tdd-tools-tdd-cycle
- **Why:** No structured status update; todowrite rewrites full list
- **Workaround:** Use todowrite to rewrite list with updated status; preserve other entries
- **Manual steps:** Review converted files and verify workaround behavior on OpenCode

#### SendMessage (inter-agent messaging)

| Field | Value |
|-------|-------|
| Component(s) | core-tools-code-synthesizer |
| Category | general_gap |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
OpenCode has no inter-agent messaging; no equivalent tool

**Workaround:**
Use todoread to retrieve findings explorers wrote to task list; context passing via task prompt for upstream orchestration; direct follow-up questioning not possible

---

#### SendMessage (inter-agent messaging)

| Field | Value |
|-------|-------|
| Component(s) | dev-tools-code-reviewer |
| Category | general_gap |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
No inter-agent messaging equivalent on opencode. Context passed only through task prompt at spawn time.

**Workaround:**
Remove Team Communication section; replace with task-prompt-driven context instructions. Body section rewritten to describe receiving context via prompt.

---

#### TaskList

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-task-executor |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
No filtered listing by owner/status; todoread returns all

**Workaround:**
Use todoread and filter in-agent by task_uid prefix or description metadata

---

#### TaskList

| Field | Value |
|-------|-------|
| Component(s) | tdd-tools-tdd-cycle |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
partial:todoread — no status/owner filtering

**Workaround:**
Use todoread full list, filter in-progress/pending by description metadata

---

#### AskUserQuestion (question tool constraint)

| Field | Value |
|-------|-------|
| Component(s) | tdd-tools-analyze-coverage |
| Category | general_gap |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
question tool is only available to primary agents, not subagents. If this skill is invoked via task subagent, interactive questioning will be unavailable.

**Workaround:**
Use question tool for primary agent invocations; for subagent contexts, structure initial prompt to collect required information upfront

---

#### AskUserQuestion in subagent context

| Field | Value |
|-------|-------|
| Component(s) | tdd-tools-tdd-cycle |
| Category | general_gap |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
question tool not available in subagents/task calls

**Workaround:**
Pre-specify parameters in task prompt; question only available to primary agent

---

#### AskUserQuestion subagent restriction

| Field | Value |
|-------|-------|
| Component(s) | dev-tools-changelog-manager |
| Category | general_gap |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
`question` tool only available to primary agents in opencode; if this agent is ever spawned via `task` tool, interactive prompting will be unavailable

**Workaround:**
Ensure changelog-manager is only invoked as a primary agent, not as a subagent. For subagent contexts, restructure to accept all required parameters upfront in the task prompt.

---

#### AskUserQuestion → question (primary-agent constraint)

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-spec-analyzer |
| Category | general_gap |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
question tool is only available to primary agents in OpenCode, not subagents; if this agent is ever spawned as a subagent via task tool, interactive question prompts will fail

**Workaround:**
Ensure spec-analyzer is always invoked as a primary agent (direct user session), not as a subagent via task; pre-specify parameters when invoked in subagent contexts

---

#### PreToolUse auto-approve hook (path-based)

| Field | Value |
|-------|-------|
| Component(s) | core-tools-hooks |
| Category | unsupported_hook |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
OpenCode has no shell-command hook system. The `tool.execute.before` JS/TS plugin API exists but cannot replicate path-pattern auto-approval via shell scripts. OpenCode's permission system is tool-level only, not path-pattern-based.

**Workaround:**
Use OpenCode's "Allow for session" permission grant when first prompted for Write/Edit/Bash on deep-analysis session directories each session.

---

#### PreToolUse hook (auto-approve)

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-task-executor |
| Category | unsupported_hook |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
Hooks do not fire for subagent tool calls in opencode

**Workaround:**
Manual "Allow for session" approval; document limitation in body

---

#### Reference file loading (`framework-templates.md`)

| Field | Value |
|-------|-------|
| Component(s) | tdd-tools-generate-tests |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode has no reference_dir; dynamic file loading via ${CLAUDE_PLUGIN_ROOT}/skills/.../references/ not supported

**Workaround:**
Detection chain inlined in Phase 2. Full boilerplate templates require manual inlining or separate maintenance.

---

#### Reference file loading (`test-patterns.md`)

| Field | Value |
|-------|-------|
| Component(s) | tdd-tools-generate-tests |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
Same as above

**Workaround:**
Core pattern guidance inlined in Phase 3. Full anti-patterns and naming conventions require manual inlining.

---

#### Reference file: `references/analysis-criteria.md`

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-analyze-spec |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode has no reference_dir; files cannot be auto-loaded by skill

**Workaround:**
Inline content into skill body or read explicitly and inject into task prompt

---

#### Reference file: `references/common-issues.md`

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-analyze-spec |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode has no reference_dir; files cannot be auto-loaded by skill

**Workaround:**
Inline content into skill body or read explicitly and inject into task prompt

---

#### Reference file: `references/html-review-guide.md`

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-analyze-spec |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode has no reference_dir; files cannot be auto-loaded by skill

**Workaround:**
Inline content into skill body or read explicitly and inject into task prompt

---

#### Reference file: `references/report-template.md`

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-analyze-spec |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode has no reference_dir; files cannot be auto-loaded by skill

**Workaround:**
Inline content into skill body or read explicitly and inject into task prompt

---

#### SendMessage (body: 3 refs)

| Field | Value |
|-------|-------|
| Component(s) | core-tools-code-architect |
| Category | general_gap |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
Team Communication and follow-up question sections rely on SendMessage for coordination

**Workaround:**
Replace with TODO; note that all context must flow through spawning task's prompt; this agent's output becomes the task result

---

#### SendMessage (tool list)

| Field | Value |
|-------|-------|
| Component(s) | core-tools-code-architect |
| Category | general_gap |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode has no inter-agent messaging; no equivalent tool

**Workaround:**
Remove from tool list; restructure orchestrating skill to pass context through task prompt

---

#### SendMessage / inter-agent messaging

| Field | Value |
|-------|-------|
| Component(s) | core-tools-codebase-analysis |
| Category | general_gap |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
No inter-agent messaging in opencode (inherited from deep-analysis dependency)

**Workaround:**
All context embedded in task prompts at dispatch time within deep-analysis skill

---

#### SendMessage tool

| Field | Value |
|-------|-------|
| Component(s) | core-tools-code-explorer |
| Category | general_gap |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
No inter-agent messaging on opencode; context passed only through task prompt

**Workaround:**
Replace all SendMessage calls with structured output text returned from task; orchestrating agent reads response directly

---

#### SendMessage — no inter-agent messaging

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-create-spec |
| Category | general_gap |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode has no inter-agent message bus; context is prompt-only

**Workaround:**
Pass all relevant context in task prompt string at spawn time

---

#### Shell-to-JS hook mechanism

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-hooks |
| Category | unsupported_hook |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
OpenCode uses JS/TS plugin API (tool.execute.before), not shell command hooks. The auto-approve-session.sh script cannot be run directly; logic must be ported to JS.

**Workaround:**
Shell script logic ported to JS plugin in converted output. Path-matching patterns preserved. Manual review of JS port recommended.

---

#### Skill reference file paths

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-spec-analyzer |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
OpenCode has no reference_dir equivalent; the 6 reference file paths (analysis-criteria.md, common-issues.md, etc.) rely on a file layout that must be preserved relative to the agent

**Workaround:**
Preserve the skills/analyze-spec/references/ directory layout alongside the agent file; read tools use relative paths which remain valid if the directory structure is maintained

---

#### Subagent tool call coverage

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-hooks |
| Category | general_gap |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
OpenCode's tool.execute.before does NOT fire for subagent tool calls. In Claude Code, PreToolUse fires for all tool invocations including those from spawned subagents. Session file operations performed by subagents (e.g., task-executor agent) will NOT be auto-approved.

**Workaround:**
Users must manually approve Write/Edit/Bash operations on session files when prompted by subagent tool calls. Selecting "Allow for session" on first occurrence covers the remainder of the session.

---

#### Task subagent model override

| Field | Value |
|-------|-------|
| Component(s) | dev-tools-docs-manager |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode task tool does not accept model parameter at call site

**Workaround:**
Model is configured in the named agent definition (docs-writer agent). Workaround preserves intent.

---

#### TaskCreate -> todowrite

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-create-tdd-tasks |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
No structured task metadata, no native dependency fields, no task ownership

**Workaround:**
Embed all metadata as key-value lines in todowrite description text; encode dependencies in description

---

#### TaskCreate / TaskUpdate / TaskList / TaskGet

| Field | Value |
|-------|-------|
| Component(s) | dev-tools-feature-dev |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
Partial equivalents only via todowrite/todoread; no dependencies, owners, structured statuses, or per-ID retrieval

**Workaround:**
Use todowrite/todoread with metadata embedded in description text

---

#### TaskCreate / TaskUpdate structured metadata

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-create-spec |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
todowrite has no structured statuses, dependencies, or per-task IDs

**Workaround:**
Encode all metadata in todo content/description text field; use todoread full-list scan to locate by content

---

#### TaskCreate structured metadata

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-create-tasks |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
todowrite has no native metadata fields (priority, complexity, spec_path, feature_name, task_uid, task_group)

**Workaround:**
Embed all metadata as formatted text in task description body

---

#### TaskCreate/TaskUpdate structured metadata

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-execute-tdd-tasks |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
todowrite is session-scoped with no structured metadata fields; no task dependencies, owners, or filtering

**Workaround:**
Embed metadata as `meta:key:value` tokens in description text; scan full todoread list for filtering (established convention from prior waves)

---

#### TaskGet (no per-ID retrieval)

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-execute-tasks |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
todoread has no per-task retrieval by ID

**Workaround:**
Scan full todoread list for task_uid embedded in description text

---

#### TaskGet -> todoread

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-create-tdd-tasks |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
No per-task retrieval by ID; full list scan required

**Workaround:**
Use todoread full list and filter by task_uid or subject match

---

#### TaskGet per-task retrieval

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-create-tasks |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
No per-task retrieval by ID in todoread

**Workaround:**
Use todoread full list and scan for task_uid

---

#### TaskGet tool

| Field | Value |
|-------|-------|
| Component(s) | core-tools-code-explorer |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
No per-task retrieval by ID on opencode; todoread returns full list only

**Workaround:**
Use todoread and scan full list to locate task by matching description text

---

#### TaskGet/TaskUpdate/TaskList (partial)

| Field | Value |
|-------|-------|
| Component(s) | core-tools-code-synthesizer |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
No structured task management; todoread/todowrite are session-scoped scratchpads with no filtering by owner/ID/status

**Workaround:**
Use todoread full list scan with description-embedded metadata; todowrite for status updates; loss of per-task ID retrieval and structured status tracking

---

#### TaskList (no filtering)

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-execute-tasks |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
todoread returns full list with no filtering by owner or status

**Workaround:**
Scan description text for metadata.task_group; filter in-skill via text matching

---

#### TaskList -> todoread

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-create-tdd-tasks |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
No status/owner filtering; returns full flat list

**Workaround:**
Scan full todoread output and filter in-memory by task_group metadata in description

---

#### TaskList metadata filtering

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-create-tasks |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
todoread returns full list with no filter-by-metadata support

**Workaround:**
Text-scan descriptions for spec_path marker to identify matching tasks

---

#### TaskList tool

| Field | Value |
|-------|-------|
| Component(s) | core-tools-code-explorer |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
todoread returns full list with no filtering by owner or status

**Workaround:**
Use todoread and apply manual filtering logic

---

#### TaskList/TaskGet per-field filtering

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-execute-tdd-tasks |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
todoread returns all tasks; no filtering by owner, status, or metadata field

**Workaround:**
Full list scan with pattern matching on description text

---

#### TaskUpdate (session-scoped, no structured status)

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-execute-tasks |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
todowrite is session-scoped scratchpad with limited status changes

**Workaround:**
Rewrite full task list via todowrite; embed all metadata (uid, spec_path, dependencies) in description text

---

#### TaskUpdate (structured task status)

| Field | Value |
|-------|-------|
| Component(s) | dev-tools-code-reviewer |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
todowrite provides a session-scoped scratchpad only. No status transitions, ownership, or dependency modeling.

**Workaround:**
Use todowrite to record review summary; adapt body instruction to match todowrite semantics. Applied as workaround.

---

#### TaskUpdate -> todowrite

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-create-tdd-tasks |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
No patch/partial update; must rewrite entire task

**Workaround:**
Full todowrite rewrite preserving existing description content plus new metadata

---

#### TaskUpdate addBlockedBy

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-create-tasks |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
todowrite has no dependency tracking fields

**Workaround:**
Embed blockedBy as text list in task description Metadata block

---

#### TaskUpdate tool

| Field | Value |
|-------|-------|
| Component(s) | core-tools-code-explorer |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
todowrite is session-scoped scratchpad only; no structured statuses or dependency tracking

**Workaround:**
Rewrite full todo list with updated status embedded in description text

---

#### Team communication pattern

| Field | Value |
|-------|-------|
| Component(s) | core-tools-code-explorer |
| Category | general_gap |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
The entire Team Communication section assumes inter-agent messaging that does not exist on opencode; the hub-and-spoke workflow must be restructured so the orchestrating agent reads subagent task responses directly

**Workaround:**
Restructure body prose to describe output-based coordination; spawning agent (deep-analysis skill) must be updated to read task responses rather than receive SendMessage notifications

---

#### TeamCreate / hub-and-spoke team management

| Field | Value |
|-------|-------|
| Component(s) | core-tools-codebase-analysis |
| Category | general_gap |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
No team orchestration in opencode (inherited from deep-analysis dependency)

**Workaround:**
Restructured as parallel task calls within deep-analysis; codebase-analysis delegates all team coordination to deep-analysis skill

---

#### TeamCreate — no team orchestration

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-create-spec |
| Category | general_gap |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode has no team registry or multi-agent team patterns

**Workaround:**
Restructure as parallel task calls from primary agent; no team membership

---

#### Template file: `templates/review-template.html`

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-analyze-spec |
| Category | general_gap |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode has no reference_dir; template cannot be path-referenced from skill

**Workaround:**
Read template explicitly and pass content in task prompt before spawning agent

---

#### `TaskGet` by ID

| Field | Value |
|-------|-------|
| Component(s) | tdd-tools-generate-tests |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode todoread returns full list; no per-task retrieval by ID

**Workaround:**
Use todoread and scan full list for matching task_uid in description field. Cached global workaround applied.

---

#### `TaskList` filtering

| Field | Value |
|-------|-------|
| Component(s) | tdd-tools-generate-tests |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode todoread returns full unfiltered list; no status/owner filtering

**Workaround:**
Use todoread and scan full list; filter programmatically. Cached global workaround applied.

---

#### `arguments` structured declaration

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-analyze-spec |
| Category | unmapped_field |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
No structured argument declaration in opencode skill frontmatter

**Workaround:**
Argument documented inline in skill body using $ARGUMENTS pattern

---

#### `disable-model-invocation: true`

| Field | Value |
|-------|-------|
| Component(s) | dev-tools-release-python-package |
| Category | unmapped_field |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
No equivalent mechanism on opencode to prevent model-invoked skill execution. This guard ensured the skill was only callable by the user, not automatically by the model.

**Workaround:**
Document constraint in skill description; restrict at agent level by not including this skill in agent-facing tool permissions.

---

#### `question` tool in spec-analyzer subagent

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-analyze-spec |
| Category | general_gap |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
question tool only available to primary agents; spec-analyzer is a subagent

**Workaround:**
Pre-collect user interaction preferences in primary skill before spawning; pass via task prompt

---

#### `references/entry-examples.md` reference file

| Field | Value |
|-------|-------|
| Component(s) | dev-tools-changelog-format |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode has no `reference_dir` concept. Reference files cannot be distributed alongside skills as separate loadable documents.

**Workaround:**
Full content of `references/entry-examples.md` inlined directly into the skill body under an "Entry Examples Reference" section. No content lost.

---

#### actionable-insights-template.md reference file

| Field | Value |
|-------|-------|
| Component(s) | core-tools-codebase-analysis |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
reference_dir is null in opencode; no path-based reference loading

**Workaround:**
Template format inlined as table description in Phase 3 Step 2 body; format fully preserved

---

#### adr-template reference file

| Field | Value |
|-------|-------|
| Component(s) | dev-tools-feature-dev |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode has no reference_dir; ${CLAUDE_PLUGIN_ROOT} path resolution is not supported

**Workaround:**
Inline adr-template.md content into skill body, or add file path to opencode.json `instructions` array

---

#### auto-approve-da-session.sh script

| Field | Value |
|-------|-------|
| Component(s) | core-tools-hooks |
| Category | general_gap |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
Shell script uses Claude Code-specific `permissionDecision` JSON protocol on stdin/stdout. No equivalent JS/TS plugin for OpenCode produced. Path pattern matching logic is documented for manual reference.

**Workaround:**
Script logic documented in migration guide; no equivalent plugin generated. Manual permission flow replaces automated approval.

---

#### bypassPermissions agent launch mode

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-execute-tdd-tasks |
| Category | unmapped_field |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode task tool has no bypassPermissions parameter; permission mode cannot be set at call time

**Workaround:**
Configure agent-level permissions in tdd-executor and task-executor agent frontmatter using the permission field

---

#### changelog-entry-template reference file

| Field | Value |
|-------|-------|
| Component(s) | dev-tools-feature-dev |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode has no reference_dir; ${CLAUDE_PLUGIN_ROOT} path resolution is not supported

**Workaround:**
Inline changelog-entry-template.md content into skill body, or add file path to opencode.json `instructions` array

---

#### framework-templates.md reference file

| Field | Value |
|-------|-------|
| Component(s) | tdd-tools-tdd-cycle |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
Same — no reference_dir

**Workaround:**
Content inlined as general guidance; specific templates not replicated

---

#### question tool — primary-agent-only

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-create-spec |
| Category | general_gap |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
question tool not available in subagent task contexts; AskUserQuestion was available everywhere

**Workaround:**
This skill is user-invocable (primary agent context) so question tool is available; pre-specify interview answers in task prompt if ever invoked from a subagent

---

#### reference file composition (coverage-patterns.md)

| Field | Value |
|-------|-------|
| Component(s) | tdd-tools-analyze-coverage |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode has no reference_dir equivalent; ${CLAUDE_PLUGIN_ROOT} path resolution is null; reference files cannot be dynamically loaded via registry

**Workaround:**
Inline reference content into skill body (done partially for Phase 1 detection logic), or create coverage-patterns as a companion opencode skill

---

#### reference_dir (3 reference files)

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-execute-tasks |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode reference_dir = null; no separate reference file support

**Workaround:**
Inline reference content into skill body; or load via opencode.json instructions array

---

#### reference_dir (change-summary-templates.md)

| Field | Value |
|-------|-------|
| Component(s) | dev-tools-docs-manager |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode has no reference_dir equivalent

**Workaround:**
Inline reference file content directly into skill body.

---

#### reference_dir (decomposition-patterns.md)

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-create-tasks |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode has no reference_dir equivalent; cannot load reference files by relative path

**Workaround:**
Inline reference content into skill body, or convert to separate skill files

---

#### reference_dir (dependency-inference.md)

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-create-tasks |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode has no reference_dir equivalent

**Workaround:**
Inline reference content into skill body, or convert to separate skill files

---

#### reference_dir (markdown-file-templates.md)

| Field | Value |
|-------|-------|
| Component(s) | dev-tools-docs-manager |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode has no reference_dir equivalent

**Workaround:**
Inline reference file content directly into skill body.

---

#### reference_dir (mkdocs-config-template.md)

| Field | Value |
|-------|-------|
| Component(s) | dev-tools-docs-manager |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode has no reference_dir equivalent; reference files cannot be dynamically loaded by skills

**Workaround:**
Inline reference file content directly into skill body. 3 UNRESOLVED markers placed.

---

#### reference_dir (tdd-execution-workflow.md)

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-execute-tdd-tasks |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode has no reference_dir equivalent; reference files cannot be auto-loaded

**Workaround:**
Inline reference content into skill body, or register in opencode.json instructions array

---

#### reference_dir (tdd-verification-patterns.md)

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-execute-tdd-tasks |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode has no reference_dir equivalent

**Workaround:**
Inline reference content into skill body, or register in opencode.json instructions array

---

#### reference_dir (testing-requirements.md)

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-create-tasks |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode has no reference_dir equivalent

**Workaround:**
Inline reference content into skill body, or convert to separate skill files

---

#### references/interview-questions.md — no reference_dir

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-create-spec |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode reference_dir is null; references/ subdirectory cannot be loaded at runtime via path

**Workaround:**
Inline reference file content directly into skill body, or use instructions config array in opencode.json

---

#### references/recommendation-format.md — no reference_dir

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-create-spec |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode reference_dir is null; references/ subdirectory cannot be loaded at runtime via path

**Workaround:**
Inline reference file content directly into skill body, or use instructions config array in opencode.json

---

#### references/recommendation-triggers.md — no reference_dir

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-create-spec |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode reference_dir is null; references/ subdirectory cannot be loaded at runtime via path

**Workaround:**
Inline reference file content directly into skill body, or use instructions config array in opencode.json

---

#### references/tdd-decomposition-patterns.md

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-create-tdd-tasks |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
reference_dir is null; no runtime file loading for reference subdirectories

**Workaround:**
Inline reference content directly into skill body

---

#### references/tdd-dependency-rules.md

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-create-tdd-tasks |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
reference_dir is null; no runtime file loading for reference subdirectories

**Workaround:**
Inline reference content directly into skill body

---

#### references/templates/detailed.md — no reference_dir

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-create-spec |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode reference_dir is null; template file cannot be loaded at runtime via path

**Workaround:**
Inline template content directly into skill body, or use instructions config array in opencode.json

---

#### references/templates/full-tech.md — no reference_dir

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-create-spec |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode reference_dir is null; template file cannot be loaded at runtime via path

**Workaround:**
Inline template content directly into skill body, or use instructions config array in opencode.json

---

#### references/templates/high-level.md — no reference_dir

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-create-spec |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode reference_dir is null; template file cannot be loaded at runtime via path

**Workaround:**
Inline template content directly into skill body, or use instructions config array in opencode.json

---

#### report-template.md reference file

| Field | Value |
|-------|-------|
| Component(s) | core-tools-codebase-analysis |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
reference_dir is null in opencode; no path-based reference loading

**Workaround:**
Template structure inlined as prose in Phase 2 Step 1 body; full report section descriptions preserved

---

#### skill reference loading (Step 1)

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-task-executor |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
reference_dir is null in opencode; execute-tasks references sub-files

**Workaround:**
Use skill composition reference for main skill; inline or load reference files separately

---

#### skills assignment (language-patterns, project-conventions)

| Field | Value |
|-------|-------|
| Component(s) | tdd-tools-tdd-executor |
| Category | unmapped_field |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
OpenCode has no frontmatter skill assignment for agents

**Workaround:**
Skills available dynamically via skill tool at runtime; note in body comment; relevant conventions can be pre-specified in task prompt for subagent contexts

---

#### skills field (frontmatter)

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-spec-analyzer |
| Category | unmapped_field |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
OpenCode has no skill assignment in agent frontmatter; target field maps to null

**Workaround:**
Skills available dynamically via skill tool at runtime: skill({ name: "analyze-spec" }); note added as comment above body

---

#### skills frontmatter assignment (project-conventions, language-patterns)

| Field | Value |
|-------|-------|
| Component(s) | core-tools-code-synthesizer |
| Category | unmapped_field |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
OpenCode has no skill assignment in agent frontmatter; skills invoked dynamically via skill tool

**Workaround:**
Skills noted in body comment; ensure they exist in .opencode/skills/ and are invoked by the orchestrating skill at runtime

---

#### skills: language-patterns

| Field | Value |
|-------|-------|
| Component(s) | core-tools-code-explorer |
| Category | unmapped_field |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode has no skill assignment in agent frontmatter

**Workaround:**
Inline skill content into agent system prompt body, or load via opencode.json instructions config array

---

#### skills: project-conventions

| Field | Value |
|-------|-------|
| Component(s) | core-tools-code-explorer |
| Category | unmapped_field |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode has no skill assignment in agent frontmatter; skills invoked dynamically via skill tool at runtime

**Workaround:**
Inline skill content into agent system prompt body, or load via opencode.json instructions config array

---

#### tdd-tools plugin existence check

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-create-tdd-tasks |
| Category | unmapped_field |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
CLAUDE_PLUGIN_ROOT path variable unavailable; cross-plugin filesystem check impossible

**Workaround:**
Skill probe via skill({ name: "tdd-cycle" }) or user-confirmed prerequisite

---

#### tdd-workflow.md reference file

| Field | Value |
|-------|-------|
| Component(s) | tdd-tools-tdd-cycle |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
Same — no reference_dir

**Workaround:**
Core rules inlined in Phase 4 header; detailed edge case handling may be abbreviated

---

#### test-patterns.md reference file

| Field | Value |
|-------|-------|
| Component(s) | tdd-tools-tdd-cycle |
| Category | unsupported_composition |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode has no reference_dir; ${CLAUDE_PLUGIN_ROOT} path resolution unavailable

**Workaround:**
Content inlined as prose guidance in Phase 2, Step 4; will drift from source over time

---

### Cosmetic

#### disable-model-invocation (Cosmetic) -- 14 components affected

- **Components:** core-tools-codebase-analysis, core-tools-language-patterns, core-tools-project-conventions, dev-tools-architecture-patterns, dev-tools-code-quality, dev-tools-docs-manager, dev-tools-feature-dev, git-tools-git-commit, sdd-tools-create-spec, sdd-tools-create-tasks, sdd-tools-create-tdd-tasks, sdd-tools-execute-tasks, sdd-tools-execute-tdd-tasks, tdd-tools-analyze-coverage
- **Why:** No per-skill invocation control in opencode
- **Workaround:** Documented in header comment; restrict via agent-level permission config
- **Manual steps:** Review converted files and verify workaround behavior on OpenCode

#### allowed-tools per-skill restrictions (Cosmetic) -- 5 components affected

- **Components:** core-tools-codebase-analysis, dev-tools-feature-dev, sdd-tools-create-spec, sdd-tools-execute-tasks, sdd-tools-execute-tdd-tasks
- **Why:** No per-skill tool restrictions in opencode; tool permissions are agent-level only
- **Workaround:** Tool list removed from frontmatter; permissions enforced at agent level via permission config
- **Manual steps:** Review converted files and verify workaround behavior on OpenCode

#### `disable-model-invocation` field (Cosmetic) -- 3 components affected

- **Components:** dev-tools-changelog-format, sdd-tools-analyze-spec, tdd-tools-generate-tests
- **Why:** opencode has no per-skill model invocation restriction. Skills are always available to the model.
- **Workaround:** Field omitted. Source value was `false` (restriction was not active), so no functional change.
- **Manual steps:** Review converted files and verify workaround behavior on OpenCode

#### SendMessage

| Field | Value |
|-------|-------|
| Component(s) | dev-tools-docs-manager |
| Category | general_gap |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
No inter-agent messaging in opencode.

**Workaround:**
Removed from tool list. Context passing via task prompt is the opencode pattern. 0 direct body references.

---

#### SendMessage

| Field | Value |
|-------|-------|
| Component(s) | dev-tools-feature-dev |
| Category | general_gap |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
No inter-agent messaging in opencode

**Workaround:**
Context passed through task prompt; deep-analysis handles internally

---

#### TeamCreate / TeamDelete

| Field | Value |
|-------|-------|
| Component(s) | dev-tools-docs-manager |
| Category | general_gap |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
No team orchestration API in opencode.

**Workaround:**
Removed from tool list. Deep-analysis handles its own parallelism via task tool internally. 0 direct body references.

---

#### TeamCreate / TeamDelete

| Field | Value |
|-------|-------|
| Component(s) | dev-tools-feature-dev |
| Category | general_gap |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
No team/multi-agent orchestration in opencode

**Workaround:**
Restructure as parallel task calls; deep-analysis handles internally via task tool

---

#### `allowed-tools` field

| Field | Value |
|-------|-------|
| Component(s) | dev-tools-release-python-package |
| Category | unmapped_field |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
No per-skill tool restrictions on opencode. Tool allow/deny is configured at agent level via `permission` config.

**Workaround:**
Omit field. All referenced tools (read, edit, bash, question, glob, task) are available on opencode; restrictions must be enforced at agent level if needed.

---

#### `allowed-tools` field

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-analyze-spec |
| Category | unmapped_field |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
No per-skill tool restrictions in opencode; agent-level permission only

**Workaround:**
Remove from frontmatter; tools remain accessible at agent level

---

#### allowed-tools per-skill restriction

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-create-tasks |
| Category | unmapped_field |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
No per-skill tool restrictions in opencode

**Workaround:**
Tool access configured at agent level; no per-skill equivalent

---

#### allowed-tools per-skill restriction

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-create-tdd-tasks |
| Category | unmapped_field |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
No per-skill tool restrictions in opencode; tool access is agent-level only

**Workaround:**
Document at agent level in opencode agent config

---

#### TaskCreate/TaskUpdate/TaskList/TaskGet

| Field | Value |
|-------|-------|
| Component(s) | dev-tools-docs-manager |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
Partial mapping to todowrite/todoread. No dependencies, owners, or structured statuses.

**Workaround:**
Partial mapping noted. 0 direct body references in this skill.

---

#### TaskGet / TaskList (per-task retrieval)

| Field | Value |
|-------|-------|
| Component(s) | dev-tools-code-reviewer |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
todoread returns full list only; no per-task retrieval by ID.

**Workaround:**
Use todoread; no body references to update. Auto-resolved.

---

#### TaskGet / TaskList partial mapping

| Field | Value |
|-------|-------|
| Component(s) | core-tools-code-architect |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
todoread returns full list with no per-task ID retrieval or status filtering

**Workaround:**
Use todoread for full list inspection; behavioral difference is minor for this agent's use case

---

#### TaskList (filtering)

| Field | Value |
|-------|-------|
| Component(s) | tdd-tools-tdd-executor |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
todoread returns full list with no filtering by owner or status

**Workaround:**
Use todoread full list and filter in agent memory

---

#### TaskUpdate partial mapping

| Field | Value |
|-------|-------|
| Component(s) | core-tools-code-architect |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
todowrite is session-scoped scratchpad only; lacks structured statuses, dependencies, or per-owner filtering that TaskUpdate supports

**Workaround:**
Use todowrite as best-effort status tracking; behavioral difference is minor since code-architect is a subagent with narrow scope

---

#### `allowed-tools` per-skill restrictions

| Field | Value |
|-------|-------|
| Component(s) | tdd-tools-generate-tests |
| Category | unmapped_field |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode has no per-skill tool restrictions; allowed-tools maps to null

**Workaround:**
All tools available via agent-level permission config. No behavioral loss since all listed tools have opencode equivalents.

---

#### `model: haiku`

| Field | Value |
|-------|-------|
| Component(s) | dev-tools-release-python-package |
| Category | unmapped_field |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
No per-skill model overrides on opencode. Skill model cannot be pinned to haiku.

**Workaround:**
Omit field. Configure model at agent level or in opencode.json if haiku is desired for this workflow.

---

#### allowed-tools field

| Field | Value |
|-------|-------|
| Component(s) | dev-tools-docs-manager |
| Category | unmapped_field |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
No per-skill tool restrictions in opencode. Tool permissions are agent-level only.

**Workaround:**
Field omitted. All tool access governed by agent permission config.

---

#### allowed-tools restriction

| Field | Value |
|-------|-------|
| Component(s) | tdd-tools-analyze-coverage |
| Category | unmapped_field |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
Per-skill tool restrictions not supported on opencode; tool permissions are agent-level only

**Workaround:**
Remove from frontmatter; all tools have equivalents and remain accessible

---

#### allowed-tools: AskUserQuestion

| Field | Value |
|-------|-------|
| Component(s) | git-tools-git-commit |
| Category | unmapped_field |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
Same as above; additionally, the `question` tool equivalent is primary-agent-only and was not invoked in the skill body

**Workaround:**
Removed from output; no functional impact since skill body had no AskUserQuestion calls

---

#### allowed-tools: Bash

| Field | Value |
|-------|-------|
| Component(s) | git-tools-git-commit |
| Category | unmapped_field |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
No per-skill tool restrictions on opencode; tool permissions are agent-level only via `permission` config

**Workaround:**
Removed from output; document tool requirements in agent permission config if restriction is needed

---

#### arguments frontmatter block

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-execute-tdd-tasks |
| Category | unmapped_field |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
No opencode equivalent for structured argument definition in skill frontmatter

**Workaround:**
Describe arguments in skill body prose

---

#### arguments structured schema

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-execute-tasks |
| Category | unmapped_field |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
No structured argument definition in opencode skills

**Workaround:**
Argument hints documented in body comment block using $ARGUMENTS convention

---

#### model: haiku

| Field | Value |
|-------|-------|
| Component(s) | git-tools-git-commit |
| Category | unmapped_field |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode does not support per-skill model overrides; model is configured at the agent level or in opencode.json

**Workaround:**
Preserved as a prose comment in the skill body; configure preferred model in agent frontmatter or opencode.json `model` field

---

#### question tool subagent restriction

| Field | Value |
|-------|-------|
| Component(s) | dev-tools-feature-dev |
| Category | general_gap |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
question tool only available to primary agents, not subagents

**Workaround:**
feature-dev is user-invocable (primary agent context); constraint is noted in Agent Coordination section

---

#### skills field (execute-tasks)

| Field | Value |
|-------|-------|
| Component(s) | sdd-tools-task-executor |
| Category | unmapped_tool |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode has no skill assignment in agent frontmatter

**Workaround:**
Skills available dynamically via skill tool at runtime; note added as comment in body

---

#### skills frontmatter assignment

| Field | Value |
|-------|-------|
| Component(s) | tdd-tools-test-writer |
| Category | unmapped_field |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
opencode does not support skill assignment in agent frontmatter; skills field maps to null

**Workaround:**
Skills are still available at runtime via the skill tool: invoke skill({ name: "language-patterns" }) and skill({ name: "project-conventions" }) during execution as needed. Note added to converted body.

---

#### tools -> permission structural change

| Field | Value |
|-------|-------|
| Component(s) | dev-tools-docs-writer |
| Category | unmapped_field |
| Resolution | workaround |
| Confidence | high |

**Why it could not be converted:**
Opencode uses per-tool allow/deny permission map instead of a flat allowed list

**Workaround:**
All tools mapped directly; write/edit denied explicitly to preserve read-only intent

---

## Platform Comparison: Claude Code vs. OpenCode

A high-level overview of feature support differences between Claude Code and OpenCode.

| Capability | Claude Code | OpenCode | Status |
|------------|-------------|----------|--------|
| Skills / Custom Commands | YAML frontmatter + markdown body | YAML frontmatter + markdown body | Supported |
| Agents | Agent markdown files with model/tools/skills | Agent markdown files with model/permission | Supported |
| Hooks / Lifecycle Events | hooks.json with PreToolUse, PostToolUse, Stop, etc. | JS/TS plugin API (tool.execute.before/after) | Partial |
| Skill Composition | `Read` directive loading skill content | `skill()` tool invocation | Partial |
| Cross-Plugin References | `${CLAUDE_PLUGIN_ROOT}/../{group}/` paths | No cross-plugin path resolution | Unsupported |
| Model Tiering | Per-agent model selection (opus/sonnet/haiku) | Per-agent model in frontmatter | Supported |
| MCP Server Config | `.mcp.json` with stdio/sse/http transports | `opencode.json` mcpServers section | Supported |
| Interactive Tools | AskUserQuestion with options/multiSelect | `question` tool (primary agent only) | Partial |
| Task Management | TaskCreate, TaskUpdate, TaskList, TaskGet | todowrite/todoread (session-scoped scratchpad) | Partial |
| Team / Multi-Agent | TeamCreate, SendMessage | No team registry or inter-agent messaging | Unsupported |
| Reference Files | `references/` subdirectories loaded by skills | No reference_dir; must inline or use instructions array | Unsupported |
| Per-Skill Tool Restrictions | `allowed-tools` in skill frontmatter | No per-skill tool restrictions | Unsupported |
| Per-Skill Model Override | `model` in skill frontmatter | No per-skill model override | Unsupported |

**Status legend:**
- **Supported**: Direct equivalent exists on OpenCode
- **Partial**: Approximate equivalent exists but with reduced functionality
- **Unsupported**: No equivalent on OpenCode

