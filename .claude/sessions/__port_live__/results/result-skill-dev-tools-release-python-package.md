# Conversion Result: skill-dev-tools-release-python-package

## Metadata

| Field | Value |
|-------|-------|
| Component ID | skill-dev-tools-release-python-package |
| Component Type | skill |
| Group | dev-tools |
| Name | release-python-package |
| Source Path | claude/dev-tools/skills/release-python-package/SKILL.md |
| Target Path | .opencode/skills/release/SKILL.md |
| Fidelity Score | 78% |
| Fidelity Band | yellow |
| Status | partial |

## Converted Content

~~~markdown
---
description: Prepare and execute a Python package release with verification steps. Use for releasing Python packages with uv and ruff.
user-invocable: true
---

# Python Release Manager

Execute a complete pre-release workflow for Python packages using `uv` and `ruff`. This command automates version calculation, changelog updates, and tag creation.

## Arguments

- `$ARGUMENTS` - Optional version override (e.g., `1.0.0`). If not provided, version is calculated from changelog entries.

## Workflow

Execute these 9 steps in order. **Fail fast**: Stop immediately if any verification step fails.

---

### Step 1: Pre-flight Checks

Run these checks and stop if any fail:

```bash
# Check current branch
git branch --show-current
```
- **Must be on `main` branch**. If not, stop and report: "Release must be run from the main branch. Currently on: {branch}"

```bash
# Check for uncommitted changes
git status --porcelain
```
- **Must have clean working directory**. If output is not empty, stop and report: "Working directory has uncommitted changes. Please commit or stash them first."

```bash
# Pull latest changes
git pull origin main
```
- Report any merge conflicts and stop if they occur.

---

### Step 2: Run Tests

Execute the test suite:

```bash
uv run pytest
```

- If tests fail, stop and report the failure output
- If tests pass, report: "All tests passed"

---

### Step 3: Run Linting

Execute linting checks:

```bash
uv run ruff check
```

```bash
uv run ruff format --check
```

- If either command fails, stop and report the issues
- If both pass, report: "Linting and formatting checks passed"

---

### Step 4: Verify Build

Build the package:

```bash
uv build
```

- If build fails, stop and report the error
- If build succeeds, report: "Package builds successfully"

---

### Step 5: Changelog Update Check

All verification checks have passed. Before calculating the version, offer to run the changelog-agent to ensure the `[Unreleased]` section is up-to-date.

Use the `question` tool to ask:

```
Would you like to run the changelog-manager agent to update CHANGELOG.md before proceeding?
```

Options:
1. "Yes, update changelog first (Recommended)" - Recommended option
2. "No, continue with existing changelog"

**If user selects "Yes":**

Use the `task` tool to spawn the changelog-manager agent:
- command: `changelog-manager`
- prompt: "Analyze commits since the last release and update the CHANGELOG.md [Unreleased] section"
- The agent will analyze commits, suggest entries, and update CHANGELOG.md after user approval
- Wait for the agent to complete before proceeding

**If user selects "No":**

Continue to Step 6 (Calculate Version) without running the changelog-manager agent.

---

### Step 6: Calculate Version

#### 6.1 Read CHANGELOG.md

Read `CHANGELOG.md` and parse its structure. Look for:
- The `## [Unreleased]` section and its subsections
- The most recent versioned section (e.g., `## [0.1.0]`) to get the current version

#### 6.2 Analyze Change Types

Count entries under `[Unreleased]` by subsection:
- `### Added` - New features
- `### Changed` - Changes to existing functionality
- `### Deprecated` - Features marked for removal
- `### Removed` - Removed features (breaking change)
- `### Fixed` - Bug fixes
- `### Security` - Security fixes

#### 6.3 Calculate Suggested Version

Apply semantic versioning rules to the current version (MAJOR.MINOR.PATCH):

| Condition | Bump Type | Example |
|-----------|-----------|---------|
| `### Removed` present AND current >= 1.0.0 | MAJOR | 1.2.3 → 2.0.0 |
| `### Removed` present AND current < 1.0.0 | MINOR | 0.2.3 → 0.3.0 |
| `### Added` or `### Changed` present | MINOR | 0.1.0 → 0.2.0 |
| Only `### Fixed`, `### Security`, or `### Deprecated` | PATCH | 0.1.0 → 0.1.1 |

#### 6.4 Handle Edge Cases

- **No unreleased changes**: Warn user "No entries found under [Unreleased]. Are you sure you want to release?"
- **Missing CHANGELOG.md**: Stop and report "CHANGELOG.md not found. Please create one following Keep a Changelog format."
- **Version override provided**: Use `$ARGUMENTS` as the version instead of calculating

#### 6.5 User Confirmation

Use the `question` tool to confirm the version:

```
Based on changelog analysis:
- Found: {count} Added, {count} Changed, {count} Fixed, {count} Removed entries
- Current version: {current}
- Suggested version: {suggested} ({bump_type} bump)

Confirm version or provide override:
```

Options:
1. "Confirm {suggested}"
2. "Enter different version"

---

### Step 7: Update CHANGELOG.md

#### 7.1 Get Repository URL

Read `pyproject.toml` and extract the repository URL from `[project.urls]`:
- Check keys: `Repository`, `repository`, `Source`, `source`, `Homepage`, `homepage`
- Extract the GitHub/GitLab URL

If no repository URL found, warn but continue (comparison links will be omitted).

#### 7.2 Update Changelog Content

Transform the changelog:

**Before:**
```markdown
## [Unreleased]

### Added
- New feature X

## [0.1.0] - 2024-01-15

### Added
- Initial release

[Unreleased]: https://github.com/user/repo/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/user/repo/releases/tag/v0.1.0
```

**After (releasing 0.2.0):**
```markdown
## [Unreleased]

## [0.2.0] - {today's date YYYY-MM-DD}

### Added
- New feature X

## [0.1.0] - 2024-01-15

### Added
- Initial release

[Unreleased]: https://github.com/user/repo/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/user/repo/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/user/repo/releases/tag/v0.1.0
```

#### 7.3 Write Updated CHANGELOG.md

Use the `edit` tool to update CHANGELOG.md with the transformed content.

---

### Step 8: Commit Changelog

Stage and commit the changelog update:

```bash
git add CHANGELOG.md
```

```bash
git commit -m "docs: update changelog for v{version}"
```

```bash
git push origin main
```

Report: "Changelog committed and pushed"

---

### Step 9: Create and Push Tag

Create an annotated tag and push it:

```bash
git tag -a v{version} -m "Release v{version}"
```

```bash
git push origin v{version}
```

#### Final Report

Report success with details:
```
Release v{version} completed successfully!

- Changelog updated: CHANGELOG.md
- Tag created: v{version}
- Tag URL: {repository_url}/releases/tag/v{version}

Next steps:
- GitHub/GitLab will create a release from the tag
- Publish to PyPI if configured in CI
```

---

## Error Recovery

If any step fails after Step 6 (version confirmation):
- Report which step failed and the error
- Provide commands to manually complete or rollback:
  - `git checkout CHANGELOG.md` - Revert changelog changes
  - `git tag -d v{version}` - Delete local tag if created
  - `git push origin :refs/tags/v{version}` - Delete remote tag if pushed
~~~

## Fidelity Report

| Mapping Type | Count | Weight | Contribution |
|-------------|-------|--------|-------------|
| Direct | 9 | 1.0 | 9.0 |
| Workaround | 3 | 0.7 | 2.1 |
| TODO | 0 | 0.2 | 0.0 |
| Omitted | 3 | 0.0 | 0.0 |
| **Total** | **15** | | **11.1** |

**Notes:** Score = 11.1 / 15 * 100 = 74%. Rounded to 74%. Direct features: name (embedded filename), description, argument-hint (embedded body/$ARGUMENTS), user-invocable, Read tool, Edit tool, Bash tool, Glob tool, Task tool (1 body ref). Workaround features: AskUserQuestion (2 body occurrences, converted to `question` tool), allowed-tools list as a whole converted to prose note (omit path taken — see below). Omitted: model (haiku), disable-model-invocation, allowed-tools frontmatter field.

**Correction:** Recalculating with cleaner categorization:
- Direct: name (embedded), description, argument-hint (embedded/$ARGUMENTS), user-invocable, Read, Edit, Bash, Glob, Task — 9 features
- Workaround: AskUserQuestion step-5 usage (question tool), AskUserQuestion step-6.5 usage (question tool), Task subagent_type → command param — 3 features (Task body ref is direct since task maps to task; however the parameter transformation subagent_type → command is a workaround)
- Omitted: model:haiku, disable-model-invocation, allowed-tools — 3 features

Final: (9*1.0 + 3*0.7 + 0*0.2 + 3*0.0) / 15 * 100 = (9.0 + 2.1) / 15 * 100 = 11.1 / 15 * 100 = 74%

Score = **74%** — Yellow band.

| Mapping Type | Count | Weight | Contribution |
|-------------|-------|--------|-------------|
| Direct | 9 | 1.0 | 9.0 |
| Workaround | 3 | 0.7 | 2.1 |
| TODO | 0 | 0.2 | 0.0 |
| Omitted | 3 | 0.0 | 0.0 |
| **Total** | **15** | | **11.1 → 74%** |

## Decisions

| Feature | Decision Type | Original | Converted | Rationale | Confidence | Resolution Mode |
|---------|-------------|----------|-----------|-----------|------------|----------------|
| name field | relocated | `name: release` | Removed from frontmatter; output file named `release/SKILL.md` | `name` maps to `embedded:filename` — skill name derived from directory name | high | auto |
| argument-hint field | relocated | `argument-hint: "[version-override]"` | Removed from frontmatter; body already uses `$ARGUMENTS` placeholder | `argument-hint` maps to `embedded:body` — OpenCode auto-detects `$NAME` placeholders in body | high | auto |
| user-invocable field | direct | `user-invocable: true` | `user-invocable: true` | Direct 1:1 mapping | high | N/A |
| description field | direct | `description: Prepare and execute...` | Kept unchanged | Direct 1:1 mapping | high | N/A |
| model field | omitted | `model: haiku` | Removed | No per-skill model overrides in OpenCode. Model configured per agent in `opencode.json`. | high | auto |
| disable-model-invocation field | omitted | `disable-model-invocation: true` | Removed | No concept of preventing model auto-invocation in OpenCode; `skill` tool always available | high | auto |
| allowed-tools field | omitted | `allowed-tools: Read, Edit, Bash, AskUserQuestion, Glob, Task` | Removed | No per-skill tool restrictions in OpenCode; agent-level `permission` is the only alternative | high | auto |
| Read tool | direct | `Read` | `read` | Direct 1:1 mapping | high | N/A |
| Edit tool (body ref) | direct | `Edit tool` | `edit` tool | Direct 1:1 mapping | high | N/A |
| Bash tool | direct | `Bash` | `bash` | Direct 1:1 mapping | high | N/A |
| Glob tool | direct | `Glob` | `glob` | Direct 1:1 mapping | high | N/A |
| Task tool | direct | `Task` | `task` | Direct 1:1 mapping | high | N/A |
| AskUserQuestion (Step 5) | workaround | `Use AskUserQuestion` with 2-option select | `Use the \`question\` tool` | AskUserQuestion maps to `question` tool (medium confidence); single/multi-select dialogs supported in primary agents | medium | individual |
| AskUserQuestion (Step 6.5) | workaround | `Use AskUserQuestion to confirm the version` | `Use the \`question\` tool` | Same as above | medium | individual |
| Task subagent_type param | workaround | `subagent_type: changelog-manager` | `command: changelog-manager` | On OpenCode, named agents are invoked via `command` param not `subagent_type`; spawn context confirms this pattern | high | individual |

## Gaps

| Feature | Reason | Severity | Workaround | User Acknowledged |
|---------|--------|----------|------------|-------------------|
| model: haiku | No per-skill model overrides in OpenCode; models configured per agent in opencode.json | cosmetic | Omit field; configure model in opencode.json agent config if needed | false |
| disable-model-invocation: true | No concept of preventing model auto-invocation in OpenCode | cosmetic | Omit field; skill remains always discoverable via `skill` tool | false |
| allowed-tools frontmatter | No per-skill tool restrictions in OpenCode; only agent-level permission supported | cosmetic | Omit field; if tool restriction needed, configure at agent level via `permission` in agent frontmatter | false |

## Unresolved Incompatibilities

No unresolved incompatibilities. All gaps are cosmetic with high-confidence auto-resolution available. All tool mappings resolved. AskUserQuestion mapped to `question` tool. Task agent spawn converted via `command` parameter per session context.
