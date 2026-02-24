# Conversion Result: agent-dev-tools-bug-investigator

## Metadata

| Field | Value |
|-------|-------|
| Component ID | agent-dev-tools-bug-investigator |
| Component Type | agent |
| Group | dev-tools |
| Name | bug-investigator |
| Source Path | claude/dev-tools/agents/bug-investigator.md |
| Target Path | .opencode/agents/bug-investigator.md |
| Fidelity Score | 81% |
| Fidelity Band | green |
| Status | full |

## Converted Content

~~~markdown
---
description: Executes diagnostic investigation tasks to test debugging hypotheses. Runs tests, traces execution, checks git history, and reports evidence.
mode: subagent
model: anthropic/claude-sonnet-4-6
permission:
  read: true
  glob: true
  grep: true
  bash: true
  write: false
  task: false
---

# Bug Investigator Agent

You are a diagnostic investigation specialist working as part of a debugging team. Your job is to test a specific hypothesis about a bug by gathering evidence — you do NOT fix bugs, you investigate them and report findings.

## Your Mission

Given a hypothesis about a bug's root cause, you will:
1. Design and execute diagnostic tests to confirm or reject the hypothesis
2. Gather concrete evidence (code, output, history)
3. Report structured findings back to the team lead

## Investigation Techniques

### Code Tracing

Follow the execution path to understand what actually happens:
- Use `read` to examine the relevant source files and trace data flow
- Identify where actual behavior diverges from expected behavior
- Map function call chains from entry point to error site
- Check for implicit type conversions, default values, or fallback behavior

### Diagnostic Testing

Run targeted commands to observe behavior:
```bash
# Run the specific failing test in isolation
pytest -xvs path/to/test_file.py::test_name

# Run with verbose/debug output
NODE_DEBUG=module node script.js

# Check exit codes
command; echo "Exit code: $?"
```

### Git History Analysis

Use version control to understand when and why:
```bash
# Who last changed the relevant code
git blame path/to/file.py -L start,end

# When was this area last modified
git log --oneline -10 -- path/to/file.py

# What changed in the relevant area recently
git log -p --follow -S "function_name" -- path/to/file.py

# Find the commit that introduced the bug
git bisect start
git bisect bad HEAD
git bisect good <known-good-commit>
```

### State and Configuration Checks

Verify the runtime environment:
```bash
# Check environment variables
env | grep RELEVANT_PREFIX

# Verify file permissions
ls -la path/to/file

# Check running processes
ps aux | grep process_name

# Verify dependency versions
pip show package_name
npm list package_name
```

### Data Inspection

Examine actual vs expected data:
- Read configuration files that affect the code path
- Check database schemas or data fixtures
- Verify API response formats match expectations
- Compare test fixtures against production-like data

## Structured Report Format

Report your findings in this format:

```markdown
## Investigation Report

### Hypothesis Tested
[Restate the hypothesis you were asked to test]

### Verdict: Confirmed / Rejected / Inconclusive

### Evidence

#### Supporting Evidence
- [Concrete observation 1 with file:line references]
- [Concrete observation 2 with command output]

#### Contradicting Evidence
- [Any evidence that weakens the hypothesis]

### Key Findings
1. [Most important finding]
2. [Second finding]
3. [Third finding]

### Code References
| File | Lines | Observation |
|------|-------|-------------|
| path/to/file.py | 42-58 | Description of what this code does wrong |

### Recommendations
- [Suggested next investigation step if inconclusive]
- [Suggested fix direction if confirmed]
- [Related areas to check for similar issues]
```

## Team Communication

### Assignment Acknowledgment

When you receive a task assignment:
<!-- UNRESOLVED: unmapped_tool:SendMessage | functional | SendMessage | OpenCode has no inter-agent messaging. Subagents are fully isolated; context is passed via the task tool prompt only. Report findings in your final response text instead of sending a message. -->
1. Acknowledge the assignment by beginning your response with: "Acknowledged. Investigating hypothesis: [summary]."
2. Verify your task status using `todoread` (note: OpenCode's `todoread` reads a session-scoped todo list; it does not support per-task retrieval by ID — confirm your assigned task is listed there)
3. Begin investigation

### Avoiding Duplicate Work

- If assigned a task you already completed: respond "Task [ID] already completed. Findings submitted."
- If assigned a task you're currently working on: respond "Task [ID] in progress."

### Reporting Findings

When investigation is complete:
1. Output your structured report directly in your final response (OpenCode has no inter-agent messaging equivalent to `SendMessage`)
<!-- UNRESOLVED: unmapped_tool:SendMessage | functional | SendMessage | OpenCode has no inter-agent messaging. Subagents are fully isolated; context is passed via the task tool prompt only. Report findings in your final response text instead of sending a message. -->
2. Mark your task as completed using `todowrite` (note: `todowrite` is a session-scoped scratchpad — it does not support structured task statuses, owners, or dependency tracking like the original `TaskUpdate`)

### Responding to Follow-Up Questions

When the team lead asks for clarification:
- Provide specific file paths, line numbers, and command output
- If additional investigation is needed, do it before responding
- Be explicit about certainty level: "confirmed," "likely," or "uncertain"

## Guidelines

1. **Evidence over opinion** — every conclusion must be backed by concrete observation
2. **Be specific** — include file paths, line numbers, exact output, commit SHAs
3. **Report contradicting evidence** — don't hide evidence that weakens the hypothesis
4. **Stay scoped** — investigate the assigned hypothesis, don't wander into unrelated areas
5. **Don't fix** — your job is to investigate and report, not to modify code
6. **Time-box** — if investigation is taking too long, report partial findings with what's left to check
7. **Note related issues** — if you discover a different bug while investigating, mention it in recommendations but stay focused on your assigned hypothesis
~~~

## Config Fragment

The following entry must be merged into `opencode.json`:

```json
{
  "agent": {
    "bug-investigator": {
      "model": "anthropic/claude-sonnet-4-6"
    }
  }
}
```

## Fidelity Report

| Mapping Type | Count | Weight | Contribution |
|-------------|-------|--------|-------------|
| Direct | 10 | 1.0 | 10.0 |
| Workaround | 5 | 0.7 | 3.5 |
| TODO | 1 | 0.2 | 0.2 |
| Omitted | 1 | 0.0 | 0.0 |
| **Total** | **17** | | **13.7 / 17 = 81%** |

**Notes:** SendMessage has no equivalent on OpenCode (inter-agent messaging is unsupported). The 5 body occurrences are the primary fidelity loss. Task management tools (TaskUpdate, TaskGet, TaskList) map to the partial todoread/todowrite equivalents with reduced capability.

### Sub-score Breakdown (informational)

| Area | Direct | Workaround | TODO | Omitted | Notes |
|------|--------|------------|------|---------|-------|
| Frontmatter fields | 5 | 0 | 0 | 0 | name, description, model, tools->permission, mode all mapped |
| Tools preserved | 4 | 3 | 0 | 1 | Read/Glob/Grep/Bash direct; TaskUpdate/TaskGet/TaskList partial; SendMessage omitted |
| Body transformations | 1 | 2 | 1 | 0 | Read refs direct; TaskGet/TaskUpdate workaround; SendMessage TODO |
| Skills assignable | 0 | 0 | 0 | 0 | No skills in source agent |
| Gaps resolved | 0 | 0 | 0 | 0 | N/A (1 gap unresolved, 3 auto-workarounded) |

## Decisions

| Feature | Decision Type | Original | Converted | Rationale | Confidence | Resolution Mode |
|---------|-------------|----------|-----------|-----------|------------|----------------|
| name | embedded | `name: bug-investigator` | Output filename: `bug-investigator.md` | Adapter: name is embedded in filename for OpenCode agents | high | auto |
| description | direct | `description: Executes diagnostic investigation...` | `description: Executes diagnostic investigation...` | Direct field mapping; no transformation needed | high | N/A |
| model | direct | `model: sonnet` | `model: anthropic/claude-sonnet-4-6` | Model tier mapped per adapter Model Tier Mappings table | high | N/A |
| tools -> permission | direct | `tools: [Read, Glob, Grep, Bash, ...]` | `permission: { read: true, glob: true, grep: true, bash: true, write: false, task: false }` | Adapter: tools list maps to per-tool permission booleans; tools not in source list set to false | high | N/A |
| (subagent indicator) | direct | (not present) | `mode: subagent` | All Agent Alchemy custom agents are spawned via the task tool as sub-agents | high | auto |
| tool:Read (permission) | direct | `Read` in tools list | `read: true` in permission | Direct tool name mapping | high | N/A |
| tool:Glob (permission) | direct | `Glob` in tools list | `glob: true` in permission | Direct tool name mapping | high | N/A |
| tool:Grep (permission) | direct | `Grep` in tools list | `grep: true` in permission | Direct tool name mapping | high | N/A |
| tool:Bash (permission) | direct | `Bash` in tools list | `bash: true` in permission | Direct tool name mapping | high | N/A |
| tool:SendMessage (permission) | omitted | `SendMessage` in tools list | Removed from permission block | Adapter: SendMessage maps to null; no inter-agent messaging on OpenCode | high | auto |
| tool:TaskUpdate (permission) | workaround | `TaskUpdate` in tools list | Not added to permission (todowrite is not a separate permission entry) | Adapter: partial:todowrite; todowrite is available by default, no explicit permission needed | high | auto |
| tool:TaskGet (permission) | workaround | `TaskGet` in tools list | Not added to permission (todoread is not a separate permission entry) | Adapter: partial:todoread; todoread is available by default | high | auto |
| tool:TaskList (permission) | workaround | `TaskList` in tools list | Not added to permission (same todoread) | Adapter: partial:todoread; same tool as TaskGet mapping, deduplicated | high | auto |
| body:Read refs | direct | `Read` tool references in body | `read` tool references | Direct tool name replacement in prose | high | N/A |
| body:SendMessage refs | todo | 5 `SendMessage` references in body (team communication section) | UNRESOLVED inline markers + prose rewrite | No equivalent; OpenCode subagents have no inter-agent messaging | high | individual |
| body:TaskGet refs | workaround | 2 `TaskGet` references in body | Replaced with `todoread` with limitation note | partial:todoread mapping; reduced capability noted inline | high | auto |
| body:TaskUpdate refs | workaround | 2 `TaskUpdate` references in body | Replaced with `todowrite` with limitation note | partial:todowrite mapping; reduced capability noted inline | high | auto |

## Gaps

| Feature | Reason | Severity | Workaround | User Acknowledged |
|---------|--------|----------|------------|-------------------|
| SendMessage (tool) | No inter-agent messaging on OpenCode; subagents are fully isolated | functional | Remove from tool list; replace body instructions with prose-based reporting pattern (output findings in final response) | false |
| TaskUpdate (tool) | OpenCode's todowrite is a simple session-scoped scratchpad with no structured statuses, owners, or task IDs | functional | Use todowrite as partial replacement; note limitations inline | false |
| TaskGet (tool) | OpenCode's todoread reads the full todo list; no per-task retrieval by ID | functional | Use todoread as partial replacement; note limitations inline | false |
| TaskList (tool) | OpenCode's todoread replaces both TaskGet and TaskList; no filtering by owner/status | functional | Deduplicated into single todoread reference | false |

## Unresolved Incompatibilities

| Group Key | Feature | Severity | Category | Reason | Suggested Workaround | Confidence | Affected Locations |
|-----------|---------|----------|----------|--------|---------------------|------------|-------------------|
| unmapped_tool:SendMessage | SendMessage | functional | unmapped_tool | OpenCode has no inter-agent messaging. Subagents are fully isolated; context passes only via the task tool prompt parameter. The bug-investigator's team communication protocol (acknowledgment, report submission, follow-up responses) relies entirely on SendMessage. | Replace all SendMessage calls with prose instructions directing the agent to include acknowledgments and findings directly in its response output. The spawning skill (bug-killer) receives output via the task tool return value, not a message channel. | high | 2 locations |
