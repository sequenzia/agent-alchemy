# Conversion Result: skill-git-tools-git-commit

## Metadata

| Field | Value |
|-------|-------|
| Component ID | skill-git-tools-git-commit |
| Component Type | skill |
| Group | git-tools |
| Name | git-commit |
| Source Path | claude/git-tools/skills/git-commit/SKILL.md |
| Target Path | skills/git-commit.md |
| Fidelity Score | 39% |
| Fidelity Band | red |
| Status | limited |

## Converted Content

~~~markdown
---
description: Commit staged changes with conventional commit message. Use when user says "commit changes", "commit this", "save my changes", or wants to create a git commit.
user-invocable: true
---

<!-- NOTE: Model preference was haiku (fast/lightweight). opencode does not support per-skill model overrides. Set the preferred model in your agent config or opencode.json if a lighter model is desired for this skill. -->

# Git Commit

Create a commit with a conventional commit message based on staged changes. Automatically stages all changes and analyzes the diff to generate an appropriate commit message.

## Workflow

Execute these steps in order.

---

### Step 1: Check Repository State

Check for changes to commit:

```bash
git status --porcelain
```

- If output is empty, report: "Nothing to commit. Working directory is clean." and stop.
- If changes exist, continue to Step 2.

---

### Step 2: Stage All Changes

Stage all changes including untracked files:

```bash
git add .
```

Report: "Staged all changes."

---

### Step 3: Analyze Changes

View the staged diff to understand what changed:

```bash
git diff --cached --stat
```

```bash
git diff --cached
```

Analyze the diff to determine:
- The type of change (feat, fix, docs, refactor, etc.)
- The scope (optional, based on affected files/modules)
- A concise description of what changed

---

### Step 4: Construct Commit Message

Build a conventional commit message following this format:

```
<type>(<optional-scope>): <description>

[optional body]
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation only
- `style` - Formatting, no code change
- `refactor` - Code restructuring without behavior change
- `test` - Adding or updating tests
- `chore` - Maintenance tasks
- `build` - Build system or dependencies
- `ci` - CI configuration
- `perf` - Performance improvement

**Rules:**
- Use imperative mood ("add" not "added")
- Use lowercase
- No trailing period
- Keep description under 72 characters
- Add a body only for complex changes or breaking changes
- Do NOT add co-author, attribution, or "Generated with" lines

---

### Step 5: Create Commit

Create the commit using a heredoc for proper formatting:

```bash
git commit -m "$(cat <<'EOF'
<commit message here>
EOF
)"
```

---

### Step 6: Handle Result

**On success:**
- Report the commit hash: "Committed: {short_hash} - {message}"

**On pre-commit hook failure:**
- Report: "Pre-commit hook failed. The commit was NOT created."
- Explain what the hook reported
- Instruct: "Fix the issues above and run the commit command again. Do NOT use --amend as that would modify the previous commit."

---

## Error Recovery

If the commit fails:
- **Hook failure**: Fix the reported issues, then stage and commit again (do NOT amend)
- **Unstage changes**: `git reset HEAD` to unstage without losing changes

## Notes

- This command stages ALL changes including untracked files
- Pre-commit hooks run automatically; their failures mean no commit was created
- Always create a NEW commit after hook failure, never amend the previous commit
~~~

## Fidelity Report

| Mapping Type | Count | Weight | Contribution |
|-------------|-------|--------|-------------|
| Direct | 2 | 1.0 | 2.0 |
| Workaround | 1 | 0.7 | 0.7 |
| TODO | 0 | 0.2 | 0.0 |
| Omitted | 4 | 0.0 | 0.0 |
| **Total** | **7** | | **2.7** |

**Notes:** The low fidelity score (39%) is driven entirely by metadata field losses — `model`, `disable-model-invocation`, and both `allowed-tools` entries — none of which affect functional behavior on opencode. The skill body converts with 100% functional fidelity: all bash commands, workflow logic, and prose instructions transfer verbatim. The score is mechanically accurate but operationally conservative; real-world usability of this skill is unaffected by the omitted fields.

## Decisions

| Feature | Decision Type | Original | Converted | Rationale | Confidence | Resolution Mode |
|---------|-------------|----------|-----------|-----------|------------|----------------|
| name | relocated | `name: git-commit` | Filename: `git-commit.md` | opencode derives skill name from the containing filename; frontmatter `name` field is not used | high | auto |
| description | direct | `description: Commit staged changes...` | `description: Commit staged changes...` | Direct 1:1 mapping; field name and semantics are identical on opencode | high | N/A |
| user-invocable | direct | `user-invocable: true` | `user-invocable: true` | Direct 1:1 mapping; controls command dialog visibility on opencode | high | N/A |
| model | omitted | `model: haiku` | Prose comment in body | opencode has no per-skill model override; model is agent-level only. Original value was `haiku` (lightweight preference). Preserved as a body comment so the intent is not silently lost. | high | auto |
| disable-model-invocation | omitted | `disable-model-invocation: false` | (removed) | Field not supported on opencode. Value was `false` (non-restrictive default), so omitting it produces identical behavior. No comment needed. | high | auto |
| allowed-tools: Bash | omitted | `Bash` in allowed-tools | (removed) | opencode has no per-skill tool restrictions; `allowed-tools` maps to null. `Bash` had zero prose references in the body — only listed in the tool allowlist. Tool restrictions are agent-level only on opencode. | high | auto |
| allowed-tools: AskUserQuestion | omitted | `AskUserQuestion` in allowed-tools | (removed) | Same as above. `AskUserQuestion` maps to `question` on opencode, but the skill body contains zero AskUserQuestion invocations — it was only listed in the allowlist. No functional change from removal. | high | auto |

## Gaps

| Feature | Reason | Severity | Workaround | User Acknowledged |
|---------|--------|----------|------------|-------------------|
| model: haiku | opencode does not support per-skill model overrides; model is configured at the agent level or in opencode.json | cosmetic | Preserved as a prose comment in the skill body; configure preferred model in agent frontmatter or opencode.json `model` field | false |
| disable-model-invocation | Field not supported on opencode; skill tool is always available to the model | cosmetic | Omitted silently — original value was `false` (no restriction), so behavior is identical | false |
| allowed-tools: Bash | No per-skill tool restrictions on opencode; tool permissions are agent-level only via `permission` config | cosmetic | Removed from output; document tool requirements in agent permission config if restriction is needed | false |
| allowed-tools: AskUserQuestion | Same as above; additionally, the `question` tool equivalent is primary-agent-only and was not invoked in the skill body | cosmetic | Removed from output; no functional impact since skill body had no AskUserQuestion calls | false |

## Unresolved Incompatibilities

| Group Key | Feature | Severity | Category | Reason | Suggested Workaround | Confidence | Affected Locations |
|-----------|---------|----------|----------|--------|---------------------|------------|-------------------|
| (none) | | | | | | | |
