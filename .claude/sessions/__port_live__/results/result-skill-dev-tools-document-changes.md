# Conversion Result: skill-dev-tools-document-changes

## Metadata

| Field | Value |
|-------|-------|
| Component ID | skill-dev-tools-document-changes |
| Component Type | skill |
| Group | dev-tools |
| Name | document-changes |
| Source Path | claude/dev-tools/skills/document-changes/SKILL.md |
| Target Path | skills/document-changes/SKILL.md |
| Fidelity Score | 61% |
| Fidelity Band | yellow |
| Status | partial |

## Converted Content

~~~markdown
---
description: >-
  Generate a markdown report documenting codebase changes from the current session —
  files added, modified, deleted, and a summary of what was done. Use when asked to
  "document changes", "generate change report", "save changes report", "what did I change",
  "session report", "summarize my changes", or "write a changes report".
user-invocable: true
---

# Document Changes

Generate a structured markdown report documenting codebase changes from the current working session. The report captures files changed, commit history, and a human-readable summary suitable for team reviews, handoff documentation, or personal records.

## Arguments

- `$ARGUMENTS` — Optional scope or description for the report (e.g., `"auth refactor"`, `"add OAuth2 support"`). Used to name the output file and populate the report's scope field. If not provided, scope is inferred from commit messages or changed file paths.

## Workflow

Execute these 4 steps in order. **Stop early** if Step 1 or Step 2 determines there is nothing to report.

---

### Step 1: Validate Git Repository

Verify the current directory is inside a git repository:

```bash
git rev-parse --is-inside-work-tree
```

- If the command fails or returns `false`, stop and report: "Not inside a git repository. This skill requires git to gather change data."
- If successful, continue to Step 2.

---

### Step 2: Gather Changes and Metadata

Collect all change data by running these git commands. If any individual command fails, continue with the data that is available.

#### 2.1 Repository Metadata

```bash
git branch --show-current
```

```bash
git config user.name
```

```bash
git remote get-url origin 2>/dev/null
```

```bash
date "+%Y-%m-%d %H:%M %Z"
```

#### 2.2 Uncommitted Changes

```bash
git status --porcelain
```

```bash
git diff --stat
```

```bash
git diff --name-status
```

#### 2.3 Staged Changes

```bash
git diff --cached --stat
```

```bash
git diff --cached --name-status
```

#### 2.4 Recent Commits (up to 20)

```bash
git log --oneline -20
```

```bash
git log --format="%H|%s|%an|%ai" -20
```

#### 2.5 Session Commit Diffs

If there are recent commits (N > 0 from Step 2.4):

```bash
git diff --stat HEAD~N..HEAD
```

```bash
git diff --name-status HEAD~N..HEAD
```

Replace `N` with the number of recent commits found (capped at 20). If the repo has fewer than N commits, use `git diff --stat $(git rev-list --max-parents=0 HEAD)..HEAD` instead.

#### 2.6 Combine and Deduplicate

Build a unified list of all affected files from Steps 2.2–2.5, deduplicating entries. For each file, track:
- **Status**: Added (A), Modified (M), Deleted (D), Renamed (R)
- **Source**: Whether the change is committed, staged, unstaged, or untracked

**Stop condition:** If there are no uncommitted changes (Step 2.2 is empty), no staged changes (Step 2.3 is empty), and no recent commits (Step 2.4 is empty), stop and report: "No changes found in the current repository. Nothing to document."

---

### Step 3: Determine Report Location

#### 3.1 Generate Filename Description

Create a short kebab-case description (2-4 words) for the filename:
- **If `$ARGUMENTS` is provided**: Convert to kebab-case (e.g., `"auth refactor"` → `auth-refactor`)
- **If `$ARGUMENTS` is not provided**: Infer from the most common theme in commit messages or changed file paths (e.g., `api-bug-fixes`, `add-oauth2-support`, `ui-component-updates`)

Build the recommended path: `internal/reports/<description>-YYYY-MM-DD.md` using today's date.

#### 3.2 Ask User for Report Location

<!-- NOTE: question tool header must be 30 chars or fewer. Header truncated from "Where should the change report be saved?" to fit constraint. -->
Use the `question` tool:

```
Where save report?

Recommended: internal/reports/<description>-YYYY-MM-DD.md
```

Options:
1. "Use recommended path (Recommended)" — Save to `internal/reports/<description>-YYYY-MM-DD.md`
2. "Custom path" — User provides their own file path

**If user selects "Custom path":** Use a follow-up `question` call asking for the full file path:

```
Enter custom report file path
```

#### 3.3 Validate Path

- The path must end with `.md`
- If the parent directory does not exist, create it with `mkdir -p`

---

### Step 4: Generate and Write Report

Build the markdown report with the following structure, then write it using the `write` tool.

#### Report Template

```markdown
# Codebase Changes Report

## Metadata

| Field | Value |
|-------|-------|
| **Date** | YYYY-MM-DD |
| **Time** | HH:MM TZ |
| **Branch** | {current branch} |
| **Author** | {git user.name} |
| **Base Commit** | {earliest commit hash before session changes, or N/A} |
| **Latest Commit** | {most recent commit hash, or "uncommitted"} |
| **Repository** | {remote URL, or "local only"} |

**Scope**: {from $ARGUMENTS, or inferred from changes}

**Summary**: {1-2 sentence executive summary of what was done}

## Overview

{High-level stats paragraph}

- **Files affected**: N
- **Lines added**: +N
- **Lines removed**: -N
- **Commits**: N

## Files Changed

| File | Status | Lines | Description |
|------|--------|-------|-------------|
| `path/to/file.ts` | Modified | +12 / -3 | Brief description of changes |
| `path/to/new.ts` | Added | +45 | Brief description |
| `path/to/old.ts` | Deleted | -20 | Brief description |

## Change Details

### Added

- **`path/to/new.ts`** — Description of the new file and its purpose.

### Modified

- **`path/to/file.ts`** — What was changed and why (based on diff context).

### Deleted

- **`path/to/old.ts`** — Why it was removed or what replaced it.

## Git Status

### Staged Changes

{List of staged files from `git diff --cached --name-status`, or "No staged changes."}

### Unstaged Changes

{List of unstaged modifications from `git diff --name-status`, or "No unstaged changes."}

### Untracked Files

{List of untracked files from `git status --porcelain` (lines starting with `??`), or "No untracked files."}

## Session Commits

| Hash | Message | Author | Date |
|------|---------|--------|------|
| `abc1234` | feat: add login flow | Author Name | 2026-02-21 |

{Or "No commits in this session." if no recent commits}
```

#### Writing the Report

1. If the parent directory does not exist, create it:
   ```bash
   mkdir -p {parent_directory}
   ```
2. Use the `write` tool to create the report file at the chosen path.
3. If the write fails, report the error and use the `question` tool to offer an alternative path:

   ```
   Write failed. Enter alternate path
   ```

#### Present Summary

After writing the report, present a brief summary of what was generated, then use the `question` tool:

<!-- NOTE: question tool header must be 30 chars or fewer. Original dynamic header "Report written to {path}." exceeds limit when path is long. Present the path in the body text instead and use a fixed short header. -->
```
What would you like to do next?

Report saved. Summary: {1-2 sentence overview}
Files documented: N | Commits: N | Lines: +N / -N
```

Options:
1. "Review report" — Read the report back to the user using the `read` tool
2. "Commit changes" — Suggest using `/git-commit` to commit outstanding changes
3. "Done" — End the workflow

---

## Error Handling

| Scenario | Action |
|----------|--------|
| Not a git repo | Stop with clear message (Step 1) |
| No changes found | Stop with clear message (Step 2) |
| Individual git command fails | Continue with available data |
| Write fails | Offer alternative path via `question` tool |
| Cannot determine scope | Use `"session-changes"` as the fallback description |

## Section Guidelines

- **Omit empty sections**: If a section has no data (e.g., no deleted files, no untracked files), omit that section or subsection entirely rather than showing "None."
- **File descriptions**: Generate brief descriptions from diff context and file names. Keep each to one sentence.
- **Commit hashes**: Use short hashes (7 characters) in the report for readability.
- **Line counts**: Use `--stat` output to extract per-file line additions/deletions. If unavailable, omit the Lines column.
~~~

## Fidelity Report

| Mapping Type | Count | Weight | Contribution |
|-------------|-------|--------|-------------|
| Direct | 2 | 1.0 | 2.0 |
| Workaround | 5 | 0.7 | 3.5 |
| TODO | 0 | 0.2 | 0.0 |
| Omitted | 2 | 0.0 | 0.0 |
| **Total** | **9** | | **5.5** |

**Notes:** Score = 5.5 / 9 * 100 = 61%. Omitted features (`disable-model-invocation`, `allowed-tools`) are cosmetic auto-resolved. Workarounds cover frontmatter relocations (name→filename, argument-hint→body) and three `AskUserQuestion`→`question` partial mappings due to the 30-character header constraint.

## Decisions

| Feature | Decision Type | Original | Converted | Rationale | Confidence | Resolution Mode |
|---------|-------------|----------|-----------|-----------|------------|----------------|
| `name` frontmatter field | relocated | `name: document-changes` | Derived from directory name: `skills/document-changes/SKILL.md` | OpenCode derives skill name from directory path; no explicit `name` field in frontmatter | high | auto |
| `description` frontmatter field | direct | `description: Generate a markdown report...` | `description: Generate a markdown report...` | Direct 1:1 mapping; field name and semantics preserved | high | N/A |
| `argument-hint` frontmatter field | relocated | `argument-hint: "[scope-or-description]"` | Body already uses `$ARGUMENTS` placeholder; frontmatter field omitted | OpenCode uses `$ARGUMENTS`/`$1`/`$2` placeholders in body; argument-hint info embedded via existing `$ARGUMENTS` reference | high | auto |
| `user-invocable` frontmatter field | direct | `user-invocable: true` | `user-invocable: true` | Direct 1:1 mapping; controls command dialog visibility | high | N/A |
| `disable-model-invocation` frontmatter field | omitted | `disable-model-invocation: false` | (omitted) | No equivalent on OpenCode; value was `false` (default behavior), so omission has no behavioral impact | high | auto |
| `allowed-tools` frontmatter field | omitted | `allowed-tools: Read, Write, Glob, Grep, Bash, AskUserQuestion` | (omitted) | No per-skill tool restrictions in OpenCode; tool access controlled at agent level via `permission` frontmatter only | high | auto |
| `AskUserQuestion` usage #1 — report location | workaround | `AskUserQuestion` with header "Where should the change report be saved?" (41 chars) | `question` tool with header "Where save report?" (18 chars) | Direct tool equivalent exists (`question`), but OpenCode enforces 30-char header max; header truncated to preserve intent | medium | auto |
| `AskUserQuestion` usage #2 — custom path follow-up | workaround | `AskUserQuestion` for custom path entry | `question` tool with header "Enter custom report file path" (29 chars) | Header fits within 30-char limit; direct functional equivalent | medium | auto |
| `AskUserQuestion` usage #3 — post-write next action | workaround | `AskUserQuestion` with dynamic header "Report written to {path}." | `question` tool with fixed header "What would you like to do next?" (30 chars); path moved to body text | Dynamic headers can exceed 30-char limit when path is long; restructured to fixed header with path info in body | medium | auto |

## Gaps

| Feature | Reason | Severity | Workaround | User Acknowledged |
|---------|--------|----------|------------|-------------------|
| `allowed-tools` per-skill restriction | OpenCode has no per-skill tool restrictions; `allowed-tools` maps to null; tool access is agent-level only via `permission` | cosmetic | Omit from output; document that tool access must be controlled at agent level if restriction is needed | false |
| `disable-model-invocation` field | No equivalent concept in OpenCode; skills are always discoverable via the `skill` tool | cosmetic | Omit; value was `false` so default behavior is unchanged | false |
| `question` tool header length constraint | OpenCode enforces max 30-char headers on `question` tool; two original `AskUserQuestion` headers exceeded this limit | functional | Truncate/rewrite headers to fit; move excess context into body text | false |

## Unresolved Incompatibilities

No unresolved incompatibilities. All gaps were auto-resolved:
- `allowed-tools` and `disable-model-invocation` omissions are cosmetic with high-confidence workarounds (omit, no behavioral loss).
- `question` tool header truncations are functional gaps but were resolved inline with medium-confidence rewrites; no user decision required as the semantic intent is preserved.

| Group Key | Feature | Severity | Category | Reason | Suggested Workaround | Confidence | Affected Locations |
|-----------|---------|----------|----------|--------|---------------------|------------|-------------------|
| (none) | — | — | — | — | — | — | — |
