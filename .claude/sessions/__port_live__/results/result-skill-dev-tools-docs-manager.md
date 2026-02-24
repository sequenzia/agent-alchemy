# Conversion Result: skill-dev-tools-docs-manager

## Metadata

| Field | Value |
|-------|-------|
| Component ID | skill-dev-tools-docs-manager |
| Component Type | skill |
| Group | dev-tools |
| Name | docs-manager |
| Source Path | claude/dev-tools/skills/docs-manager/SKILL.md |
| Target Path | skills/docs-manager/SKILL.md |
| Fidelity Score | 85% |
| Fidelity Band | green |
| Status | full |

## Converted Content

~~~markdown
---
description: >-
  Documentation management workflow for MkDocs sites and standalone markdown files —
  initialize, generate, update docs, and create change summaries. Use when asked to
  "create docs", "write README", "update documentation", "generate docs site",
  "write CONTRIBUTING", "manage documentation", or "docs changelog".
user-invocable: true
---

# Documentation Manager Workflow

Execute a structured 6-phase workflow for managing documentation. Supports two documentation formats (MkDocs sites and standalone markdown files) and three action types (generate, update, change summary).

The user's input is available as `$ARGUMENTS` (e.g., "create README", "update docs site", "generate changelog").

**CRITICAL: Complete ALL applicable phases.** Some phases are conditional. After completing each phase, immediately proceed to the next phase without waiting for user prompts.

## Phase Overview

Execute these phases in order, completing ALL of them:

1. **Interactive Discovery** — Determine documentation type, format, and scope through user interaction
2. **Project Detection & Setup** — Detect project context, conditionally scaffold MkDocs
3. **Codebase Analysis** — Deep codebase exploration using the deep-analysis skill
4. **Documentation Planning** — Translate analysis findings into a concrete plan for user approval
5. **Documentation Generation** — Launch docs-writer agents to generate content
6. **Integration & Finalization** — Write files, validate, present results

---

## Phase 1: Interactive Discovery

**Goal:** Determine through user interaction what documentation to create and in what format.

### Step 1 — Infer intent from `$ARGUMENTS`

Parse the user's input to pre-fill selections:
- Keywords like "README", "CONTRIBUTING", "ARCHITECTURE" → infer `basic-markdown`
- Keywords like "mkdocs", "docs site", "documentation site" → infer `mkdocs`
- Keywords like "changelog", "release notes", "what changed" → infer `change-summary`

If the intent is clear, present a summary for quick confirmation before proceeding (skip to Step 4). If ambiguous, proceed to Step 2.

### Step 2 — Q1: Documentation type

If the documentation type is ambiguous or needs confirmation, use the `question` tool:

```
What type of documentation would you like to create?
1. "MkDocs documentation site" — Full docs site with mkdocs.yml, Material theme
2. "Basic markdown files" — Standalone files like README.md, CONTRIBUTING.md, ARCHITECTURE.md
3. "Change summary" — Changelog, release notes, commit message
```

Store as `DOC_TYPE` = `mkdocs` | `basic-markdown` | `change-summary`.

### Step 3 — Conditional follow-up questions

**If `DOC_TYPE = mkdocs`:**

Q2: Use the `question` tool — Existing project or new setup?
- "Existing MkDocs project" → `MKDOCS_MODE = existing`
- "New MkDocs setup" → `MKDOCS_MODE = new`

Q3 (if `existing`): Use the `question` tool — What to do?
- "Generate new pages"
- "Update existing pages"
- "Both — generate and update"
Store as `ACTION`.

Q3 (if `new`): Use the `question` tool — Scope?
- "Full documentation"
- "Getting started only (minimal init)"
- "Custom pages"
Store as `MKDOCS_SCOPE`. If custom, use the `question` tool for desired pages (free text).

**If `DOC_TYPE = basic-markdown`:**

Q2: Use the `question` tool (multi-select) — Which files?
- "README.md"
- "CONTRIBUTING.md"
- "ARCHITECTURE.md"
- "API documentation"
Store as `MARKDOWN_FILES`. If "Other" is selected, use the `question` tool for custom file paths/descriptions.

**If `DOC_TYPE = change-summary`:**

Q2: Use the `question` tool — What range?
- "Since last tag"
- "Between two refs"
- "Recent changes"
Follow up for specific range details (tag name, ref pair, etc.).

### Step 4 — Confirm selections

Present a summary of all selections and use the `question` tool:
- "Proceed"
- "Change selections"

If the user wants to change, loop back to the relevant question.

**Immediately proceed to Phase 2.**

---

## Phase 2: Project Detection & Setup

**Goal:** Detect project context automatically, conditionally scaffold MkDocs.

### Step 1 — Detect project metadata (all paths)

- Check manifests: `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `pom.xml`
- Run `git remote get-url origin 2>/dev/null`
- Note primary language and framework

### Step 2 — Check existing documentation (all paths)

- Use glob to find `docs/**/*.md`, `README.md`, `CONTRIBUTING.md`, `ARCHITECTURE.md`
- For MkDocs: check for `mkdocs.yml`/`mkdocs.yaml`, read if found

### Step 3 — MkDocs Initialization (only if `DOC_TYPE = mkdocs` AND `MKDOCS_MODE = new`)

Use the MkDocs configuration template below (see **Reference: MkDocs Configuration Template** section at the end of this skill):

1. Fill the template with detected metadata (ask via the `question` tool if incomplete)
2. Generate `mkdocs.yml`, create `docs/index.md` and `docs/getting-started.md`
3. Present scaffold for confirmation before writing

If `MKDOCS_SCOPE = minimal` (getting started only): write the scaffold files and skip to Phase 6.

### Step 4 — Set action-specific context (for update/change-summary)

For **update** modes, determine the approach:
- **git-diff** — Update docs affected by recent code changes (default if user mentions "recent changes" or a branch/tag)
- **full-scan** — Compare all source code against all docs for gap analysis (default if user says "full update" or "sync all")
- **targeted** — Update specific pages or sections (default if user specifies file paths or page names)

For **change-summary**, run `git log` and `git diff --stat` for the determined range.

**Immediately proceed to Phase 3.**

---

## Phase 3: Codebase Analysis

**Goal:** Deep codebase exploration using the deep-analysis skill.

**Skip conditions:**
- Skip for `change-summary` (uses git-based analysis instead — see below)
- Skip for MkDocs minimal init-only (`MKDOCS_SCOPE = minimal`)

### Step 1 — Build documentation-focused analysis context

Construct a specific context string based on Phase 1 selections:

| Selection | Analysis Context |
|-----------|-----------------|
| MkDocs generate | "Documentation generation — find all public APIs, architecture, integration points, and existing documentation..." |
| MkDocs update | "Documentation update — identify changes to public APIs, outdated references, documentation gaps..." |
| Basic markdown README | "Project overview — understand purpose, architecture, setup, key features, configuration, and dependencies..." |
| Basic markdown ARCHITECTURE | "Architecture documentation — map system structure, components, data flow, design decisions, key dependencies..." |
| Basic markdown API docs | "API documentation — find all public functions, classes, methods, types, their signatures and usage patterns..." |
| Basic markdown CONTRIBUTING | "Contribution guidelines — find dev workflow, testing setup, code style rules, commit conventions, CI process..." |
| Multiple files | Combine relevant contexts from above |

### Step 2 — Run deep-analysis

Invoke skill({ name: "deep-analysis" }) and follow its workflow.

Pass the documentation-focused analysis context from Step 1.

Deep-analysis handles all agent orchestration (reconnaissance, team planning, approval — auto-approved when skill-invoked — team creation, code-explorers + code-synthesizer). Since docs-manager is the calling skill, deep-analysis returns control without standalone summary.

**Note:** Deep-analysis may return cached results if a valid exploration cache exists. In skill-invoked mode, cache hits are auto-accepted — this is expected behavior that avoids redundant exploration.

### Step 3 — Supplemental analysis for update with git-diff mode

After deep-analysis, additionally:
1. Run `git diff --name-only [base-ref]` for changed files
2. Use grep to search existing docs for references to changed files/functions
3. Cross-reference with synthesis findings

### For change-summary path (instead of deep-analysis)

1. Run `git log --oneline [range]` and `git diff --stat [range]`
2. Launch 1 code-explorer agent using the `task` tool with `command: "code-explorer"` to analyze the changed files:
   ```
   Analysis context: Change summary for [range]
   Focus area: These files changed in the specified range:
   [list from git diff --stat]

   For each significant change, identify:
   - What was added, modified, or removed
   - Impact on public APIs and user-facing behavior
   - Whether any changes are breaking
   Return a structured report of your findings.
   ```

**Immediately proceed to Phase 4.**

---

## Phase 4: Documentation Planning

**Goal:** Translate analysis findings into a concrete documentation plan.

### Step 1 — Produce plan based on doc type

**MkDocs:**
- Pages to create (with `docs/` paths)
- Pages to update (with specific sections)
- Proposed `mkdocs.yml` nav updates
- Page dependency ordering (independent pages first, then pages that cross-reference them)

**Basic Markdown:**
- Files to create/update (with target paths)
- Proposed structure/outline for each file
- Content scope per file

**Change Summary:**
- Output formats to generate (Format 1: Changelog, Format 2: Commit message, Format 3: MkDocs page — only if MkDocs site exists)
- Range confirmation
- Scope of changes

### Step 2 — User approval

Use the `question` tool:
- "Approve the plan as-is"
- "Modify the plan" (describe changes)
- "Reduce scope" (select specific items only)

**Immediately proceed to Phase 5.**

---

## Phase 5: Documentation Generation

**Goal:** Generate content using docs-writer agents.

### Step 1 — Load templates

Use the appropriate template from the reference sections at the end of this skill:

- If `DOC_TYPE = change-summary`: See **Reference: Change Summary Templates** section below
- If `DOC_TYPE = basic-markdown`: See **Reference: Markdown File Templates** section below

### Step 2 — Group by dependency

- **Independent pages/files** — Can be written without referencing other new content (API reference, standalone guides, individual markdown files)
- **Dependent pages/files** — Reference or summarize content from other pages (index pages, overview pages, README that links to CONTRIBUTING)

### Step 3 — Launch docs-writer agents

Launch agents using the `task` tool with `command: "docs-writer"` and model opus (anthropic/claude-opus-4-6).

Launch independent pages/files in parallel, then sequential for dependent ones (include generated content from independent pages in the prompt context).

**MkDocs prompt template:**
```
Documentation task: [page type — API reference / architecture / how-to / change summary]
Target file: [docs/path/to/page.md]
Output format: MkDocs
Project: [project name] at [project root]

MkDocs site context:
- Theme: Material for MkDocs
- Extensions available: admonitions, code highlighting, tabbed content, Mermaid diagrams
- Diagram guidance: The technical-diagrams skill is loaded — use Mermaid for all diagrams. Follow its styling rules (dark text on nodes).
- Existing pages: [list of current doc pages]

Exploration findings:
[Relevant findings from Phase 3 for this page]

Existing page content (if updating):
[Current content of the page, or "New page — no existing content"]

Generate the complete page content in MkDocs-flavored Markdown.
```

**Basic Markdown prompt template:**
```
Documentation task: [file type — README / CONTRIBUTING / ARCHITECTURE / API docs]
Target file: [path/to/file.md]
Output format: Basic Markdown
Project: [project name] at [project root]

File type guidance:
[Relevant structural template from the Markdown File Templates reference below]

Exploration findings:
[Relevant findings from Phase 3 for this file]

Existing file content (if updating):
[Current content, or "New file — no existing content"]

Generate the complete file content in standard GitHub-flavored Markdown.
Do NOT use MkDocs-specific extensions (admonitions, tabbed content, code block titles).
Diagram guidance: The technical-diagrams skill is loaded — use Mermaid for all diagrams. Follow its styling rules (dark text on nodes). GitHub renders Mermaid natively.
```

### Step 4 — Review generated content

- Verify structure, check for unfilled placeholders
- Validate cross-references between pages/files use correct relative paths

**Immediately proceed to Phase 6.**

---

## Phase 6: Integration & Finalization

**Goal:** Write files, validate, present results.

### Step 1 — Write files

**MkDocs:**
- Write pages under `docs/`
- Update `mkdocs.yml` nav — read current config, add new pages in logical positions, preserve existing structure

**Basic Markdown:**
- Write files to their target paths (project root or specified directories)
- For updates, use the edit tool to modify existing files

**Change Summary:**
- Present outputs inline for review
- Write files as applicable (e.g., append to CHANGELOG.md)

### Step 2 — Validate

**MkDocs:**
- Verify all files referenced in `nav` exist on disk using glob
- Check for broken cross-references between pages using grep
- If `mkdocs` CLI is available, run `mkdocs build --strict 2>&1` to check for warnings (non-blocking)

**Basic Markdown:**
- Validate internal cross-references between files (e.g., README links to CONTRIBUTING)
- Check that referenced paths exist

### Step 3 — Present results

Summarize what was done:
- Files created (with paths)
- Files updated (with description of changes)
- Navigation changes (if MkDocs)
- Any validation warnings

For **change-summary**, present generated outputs directly inline.

### Step 4 — Next steps

Use the `question` tool with relevant options:

**MkDocs:**
- "Preview the site" (if `mkdocs serve` is available)
- "Commit the changes"
- "Generate additional pages"
- "Done — no further action"

**Basic Markdown:**
- "Commit the changes"
- "Generate additional files"
- "Review a specific file"
- "Done — no further action"

---

## Error Handling

If any phase fails:
1. Explain what went wrong
2. Ask the user how to proceed via the `question` tool:
   - Retry the phase
   - Skip to next phase (with partial results)
   - Abort the workflow

### Non-Git Projects
If the project is not a git repository:
- Skip git remote detection in Phase 2 (omit `repo_url` and `repo_name` from mkdocs.yml)
- The `update` action with git-diff mode is unavailable — fall back to full-scan or targeted mode
- The `change-summary` action is unavailable — inform the user and suggest alternatives

### Basic Markdown on Non-Git Projects
- CONTRIBUTING.md is still viable — use project conventions instead of git workflow sections
- Skip branch naming and PR process sections; focus on code style, testing, and setup

### Phase Failure
- Explain the error clearly
- Offer retry/skip/abort options via the `question` tool

---

## Agent Coordination

- **Phase 3**: Exploration and synthesis handled by the deep-analysis skill via `skill({ name: "deep-analysis" })`. Deep-analysis performs reconnaissance, composes a team plan (auto-approved when invoked by another skill), and orchestrates its own code-explorer and code-synthesizer subagents via the `task` tool. Context from subagents is passed through task prompts and returned in final task responses.
- **Phase 5**: docs-writer agents launched with `task` tool (`command: "docs-writer"`, model: anthropic/claude-opus-4-6) for high-quality content generation. Parallel for independent files, sequential for dependent files. Each agent receives full context in its task prompt and returns generated content in its response.

---

## Reference: MkDocs Configuration Template

Use this template when scaffolding a new MkDocs project in Phase 2.

### Template

```yaml
site_name: PROJECT_NAME
site_description: PROJECT_DESCRIPTION
site_url: ""
repo_url: REPO_URL
repo_name: REPO_NAME

theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - navigation.top
    - search.suggest
    - search.highlight
    - content.code.copy
    - content.tabs.link
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-4
        name: Switch to light mode

markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.highlight:
      anchor_linenums: true
      line_spans: __span
      pygments_lang_guess: false
  - pymdownx.inlinehilite
  - pymdownx.tabbed:
      alternate_style: true
  - pymdownx.snippets
  - attr_list
  - md_in_html
  - toc:
      permalink: true

nav:
  - Home: index.md
  - Getting Started: getting-started.md
```

### Field Descriptions

| Field | Description | How to Set |
|-------|-------------|------------|
| `site_name` | Display name in header and browser tab | Use the project name from `package.json`, `pyproject.toml`, `Cargo.toml`, or directory name |
| `site_description` | Meta description for SEO | Use the project description from manifest file, or summarize from README |
| `repo_url` | Link to source repository | Detect from `git remote get-url origin` |
| `repo_name` | Display text for repo link | Extract `owner/repo` from the remote URL |
| `site_url` | Production URL for the docs site | Leave empty during scaffolding — user can set later |

### Git Remote Detection

Use this approach to populate `repo_url` and `repo_name`:

```bash
# Get the remote URL
REMOTE_URL=$(git remote get-url origin 2>/dev/null)

# Convert SSH to HTTPS if needed
# git@github.com:owner/repo.git → https://github.com/owner/repo
if [[ "$REMOTE_URL" == git@* ]]; then
  REMOTE_URL=$(echo "$REMOTE_URL" | sed 's|git@\(.*\):\(.*\)\.git|https://\1/\2|')
fi

# Extract owner/repo for repo_name
REPO_NAME=$(echo "$REMOTE_URL" | sed 's|.*/\([^/]*/[^/]*\)$|\1|' | sed 's|\.git$||')
```

If not a git repository or no remote is configured, omit `repo_url` and `repo_name` from the config.

### Starter Pages

#### `docs/index.md`

```markdown
# PROJECT_NAME

PROJECT_DESCRIPTION

## Overview

Brief overview of what the project does and who it's for.

## Quick Start

Minimal steps to get started:

1. Install the project
2. Run a basic example
3. Explore further documentation

## Documentation

| Section | Description |
|---------|-------------|
| [Getting Started](getting-started.md) | Installation and first steps |
```

#### `docs/getting-started.md`

```markdown
# Getting Started

## Prerequisites

List prerequisites here (language runtime, tools, etc.).

## Installation

Installation instructions for the project.

## Basic Usage

A minimal working example demonstrating core functionality.

## Next Steps

Links to further documentation sections.
```

### Usage Instructions

1. **Detect project metadata:** Read `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, or similar manifest files. Run `git remote get-url origin` to detect the repository URL. Fall back to directory name if no manifest is found.
2. **Fill in template fields:** Replace `PROJECT_NAME`, `PROJECT_DESCRIPTION`, `REPO_URL`, `REPO_NAME` with detected values. Remove `repo_url` and `repo_name` if not in a git repository.
3. **Write the files:** Write `mkdocs.yml` to the project root. Create `docs/` directory. Write `docs/index.md` and `docs/getting-started.md` with project-specific content.
4. **Customize the nav:** The starter nav includes Home and Getting Started. Additional pages are added to nav as they are generated in later phases.

---

## Reference: Change Summary Templates

Use these templates when generating change summaries in Phase 4.

### Format 1: Markdown Changelog

Follows [Keep a Changelog](https://keepachangelog.com/) conventions.

```markdown
## [Unreleased]

### Added
- Add [feature] with [key capability]
- Add [new component] for [purpose]

### Changed
- Update [component] to [new behavior]
- Refactor [module] for [improvement]

### Fixed
- Fix [bug] that caused [symptom]

### Removed
- Remove [deprecated feature] in favor of [replacement]
```

**Guidelines:**
- Use imperative mood ("Add feature" not "Added feature")
- One entry per distinct change
- Group related changes under the same category
- Focus on user-facing impact, not implementation details
- Order categories: Added, Changed, Deprecated, Removed, Fixed, Security

### Format 2: Git Commit Message

Follows [Conventional Commits](https://www.conventionalcommits.org/) style.

```
type(scope): summary of changes

Detailed description of what changed and why. Cover the motivation
for the change and contrast with previous behavior.

Changes:
- List specific modifications
- Include file paths for significant changes
- Note any breaking changes

BREAKING CHANGE: Description of breaking change (if applicable)
```

**Type Reference:**

| Type | Use For |
|------|---------|
| `feat` | New features |
| `fix` | Bug fixes |
| `docs` | Documentation changes |
| `refactor` | Code restructuring without behavior change |
| `perf` | Performance improvements |
| `test` | Adding or updating tests |
| `chore` | Build, CI, or tooling changes |

**Guidelines:**
- Subject line: max 72 characters, imperative mood, no period
- Body: wrap at 72 characters, explain "why" not just "what"
- Include `BREAKING CHANGE:` footer for breaking changes
- Reference issue numbers where applicable: `Closes #123`

### Format 3: MkDocs Documentation Page

> **Scope:** This format applies only when the documentation target is an MkDocs site. For basic markdown projects, use Format 1 (Markdown Changelog) as the primary change summary output.

A full documentation page suitable for a changelog or release notes section.

```markdown
# Changes: VERSION_OR_RANGE

Summary of changes for this release or period.

## Highlights

!!! tip "Key Changes"
    Brief summary of the most important changes in this release.

### New Features

#### Feature Name

Description of the new feature and its purpose.

### Improvements

- **Component**: Description of improvement
- **Performance**: Description of optimization

### Bug Fixes

- Fix [issue description] that affected [scenario] (#issue-number)

### Breaking Changes

!!! warning "Breaking Changes"
    The following changes require action when upgrading.

#### Change Description

**Before:** (old API or behavior)

**After:** (new API or behavior)

**Migration:** Steps to update existing code.

## Affected Files

| File | Change Type | Description |
|------|-------------|-------------|
| `path/to/file` | Modified | Brief description |

## Contributors

- @username — Description of contribution
```

**Guidelines:**
- Use admonitions to highlight breaking changes and key features
- Include before/after code examples for API changes
- Provide migration guidance for breaking changes
- Link to relevant documentation pages for new features
- List affected files with change types (Added, Modified, Removed)

### Choosing Formats

| Format | Best For |
|--------|----------|
| **Markdown Changelog** | Appending to an existing CHANGELOG.md |
| **Git Commit Message** | Describing changes in a commit or PR |
| **MkDocs Page** | Publishing release notes in the documentation site |

The user may select multiple formats. Generate each independently — they serve different audiences and purposes.

---

## Reference: Markdown File Templates

Use these templates when generating standalone markdown files in Basic Markdown mode (Phase 5).

### README.md Template

```markdown
# PROJECT_NAME

[![Build Status](BADGE_URL)](CI_URL) [![Version](BADGE_URL)](PACKAGE_URL) [![License](BADGE_URL)](LICENSE_URL)

PROJECT_DESCRIPTION

## Table of Contents

- [Getting Started](#getting-started)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Getting Started

### Prerequisites

- PREREQUISITE_1 (version requirement)
- PREREQUISITE_2 (version requirement)

### Installation

INSTALLATION_STEPS

## Usage

BASIC_USAGE_DESCRIPTION

### Advanced Usage

ADVANCED_USAGE_DESCRIPTION (optional — include only if project has notable advanced features)

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `OPTION_NAME` | `TYPE` | `DEFAULT` | DESCRIPTION |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

LICENSE_TYPE — see [LICENSE](LICENSE) for details.
```

**Field Descriptions:**

| Field | How to Populate |
|-------|-----------------|
| `PROJECT_NAME` | From manifest (`name` in package.json, pyproject.toml, etc.) or directory name |
| `PROJECT_DESCRIPTION` | From manifest `description` field, or summarize from code analysis |
| `BADGE_URL`, `CI_URL`, etc. | Detect CI provider (GitHub Actions, etc.) and package registry; omit badges if not detectable |
| `PREREQUISITE_*` | From manifest engines/requires fields, or detected runtime (Node, Python, Rust, etc.) |
| `INSTALLATION_STEPS` | From detected package manager (npm, pip, cargo, etc.) and manifest |
| `USAGE_EXAMPLE` | From existing examples, tests, or main entry point analysis |
| `OPTION_NAME`, etc. | From configuration files, environment variables, or CLI flag analysis |
| `LICENSE_TYPE` | From LICENSE file or manifest `license` field |

### CONTRIBUTING.md Template

```markdown
# Contributing to PROJECT_NAME

Thank you for your interest in contributing! This guide covers the development workflow and conventions.

## Development Setup

### Prerequisites

- PREREQUISITE_1 (version requirement)
- PREREQUISITE_2 (version requirement)

### Getting Started

1. Fork and clone the repository
2. INSTALL_DEPENDENCIES_COMMAND
3. VERIFY_SETUP_COMMAND

## Code Style

CODE_STYLE_DESCRIPTION

LINTING_INSTRUCTIONS

## Testing

### Running Tests

TEST_COMMAND

### Writing Tests

TESTING_CONVENTIONS

## Pull Request Process

1. Create a feature branch from `DEFAULT_BRANCH`
2. BRANCH_NAMING_CONVENTION
3. Make your changes with clear, atomic commits
4. COMMIT_CONVENTION
5. Push and open a pull request
6. Ensure CI checks pass
7. Request review from maintainers

## Issue Guidelines

- Search existing issues before creating a new one
- Use descriptive titles
- Include reproduction steps for bugs
- ADDITIONAL_ISSUE_GUIDELINES
```

**Field Descriptions:**

| Field | How to Populate |
|-------|-----------------|
| `PROJECT_NAME` | Same as README |
| `PREREQUISITE_*` | Same as README — runtime and tool requirements |
| `INSTALL_DEPENDENCIES_COMMAND` | Detected from package manager (e.g., `pnpm install`, `pip install -e ".[dev]"`) |
| `VERIFY_SETUP_COMMAND` | Test command or build command to verify setup works |
| `CODE_STYLE_DESCRIPTION` | From linter configs (.eslintrc, .prettierrc, ruff.toml, etc.) or existing patterns |
| `LINTING_INSTRUCTIONS` | From detected linter/formatter commands |
| `TEST_COMMAND` | From manifest scripts, detected test framework (jest, pytest, cargo test, etc.) |
| `TESTING_CONVENTIONS` | Infer from existing test file patterns (location, naming, structure) |
| `DEFAULT_BRANCH` | From `git symbolic-ref refs/remotes/origin/HEAD` or default to `main` |
| `BRANCH_NAMING_CONVENTION` | From existing branch patterns or conventional (`feature/`, `fix/`, etc.) |
| `COMMIT_CONVENTION` | From existing commit history patterns (Conventional Commits, etc.) |

### ARCHITECTURE.md Template

```markdown
# Architecture

## System Overview

SYSTEM_OVERVIEW_DESCRIPTION

## Component Diagram

(Insert Mermaid graph TD diagram mapping discovered modules, services, and their relationships)

## Directory Structure

PROJECT_ROOT/
├── DIRECTORY_1/          # DESCRIPTION_1
│   ├── SUBDIRECTORY/     # DESCRIPTION
│   └── FILE              # DESCRIPTION
├── DIRECTORY_2/          # DESCRIPTION_2
└── DIRECTORY_3/          # DESCRIPTION_3

## Data Flow

DATAFLOW_DESCRIPTION

(Insert Mermaid sequenceDiagram tracing entry points through the system)

## Design Decisions

### DECISION_1_TITLE

**Context:** CONTEXT_DESCRIPTION
**Decision:** DECISION_DESCRIPTION
**Rationale:** RATIONALE_DESCRIPTION

## Key Dependencies

| Dependency | Purpose | Why Chosen |
|------------|---------|------------|
| `DEPENDENCY_NAME` | PURPOSE | RATIONALE |
```

**Field Descriptions:**

| Field | How to Populate |
|-------|-----------------|
| `SYSTEM_OVERVIEW_DESCRIPTION` | Synthesize from code analysis — what the system does, its main purpose |
| Component diagram | Map from discovered modules, services, and their import/call relationships |
| Directory structure | From actual directory listing with descriptions inferred from file contents |
| `DATAFLOW_DESCRIPTION` | Trace from entry points (HTTP handlers, CLI commands, main) through the system |
| Design decisions | Infer from architecture patterns (monorepo, plugin system, etc.) and README/comments |
| Dependencies | From manifest files with purposes inferred from usage in code |

### API Documentation Template

```markdown
# API Reference

## MODULE_NAME

MODULE_DESCRIPTION

### `FUNCTION_NAME`

FUNCTION_DESCRIPTION

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `PARAM_NAME` | `PARAM_TYPE` | Yes/No | PARAM_DESCRIPTION |

**Returns:** `RETURN_TYPE` — RETURN_DESCRIPTION

**Raises/Throws:** (if applicable)

| Error | Condition |
|-------|-----------|
| `ERROR_TYPE` | CONDITION_DESCRIPTION |

**Example:** (usage example showing the function in context)

---

### `CLASS_NAME`

CLASS_DESCRIPTION

#### Constructor

| Parameter | Type | Description |
|-----------|------|-------------|
| `PARAM_NAME` | `PARAM_TYPE` | PARAM_DESCRIPTION |

#### Methods

##### `METHOD_NAME`

METHOD_DESCRIPTION

**Parameters:** (same table format as functions)

**Returns:** `RETURN_TYPE` — RETURN_DESCRIPTION
```

**Field Descriptions:**

| Field | How to Populate |
|-------|-----------------|
| `MODULE_NAME` | From file/module paths and export structure |
| `FUNCTION_NAME` | From exported/public function declarations |
| `FUNCTION_SIGNATURE` | From source code — include full typed signature |
| Parameter tables | From function parameters, docstrings, type annotations |
| `RETURN_TYPE` | From return type annotations or inferred from code |
| Error tables | From throw/raise statements or documented exceptions |
| Usage examples | From existing tests, docstring examples, or constructed from API shape |

### Template Usage Instructions

1. **Select the appropriate template** based on the file type being generated
2. **Fill placeholder fields** using findings from Phase 3 codebase analysis
3. **Remove inapplicable sections** — not every project needs every section (e.g., skip Configuration if none exists)
4. **Add project-specific sections** where the template doesn't cover a significant aspect
5. **Write in Basic Markdown mode** — use blockquotes for callouts, standard code blocks, no MkDocs extensions
~~~

## Fidelity Report

| Mapping Type | Count | Weight | Contribution |
|-------------|-------|--------|-------------|
| Direct | 24 | 1.0 | 24.0 |
| Workaround | 13 | 0.7 | 9.1 |
| TODO | 0 | 0.2 | 0.0 |
| Omitted | 2 | 0.0 | 0.0 |
| **Total** | **39** | | **33.1 / 39 = 84.9% → 85%** |

**Notes:** Feature counts include: 6 frontmatter fields, 15 allowed-tools entries, 4 composition/path references, and 14 AskUserQuestion invocations in body (counted individually across all 6 phases + error handling). TeamCreate/TeamDelete/SendMessage appear only in allowed-tools and Agent Coordination prose (not as direct tool call syntax in body), so workaround is applied there. Three reference files inlined per cached resolution.

## Decisions

| Feature | Decision Type | Original | Converted | Rationale | Confidence | Resolution Mode |
|---------|-------------|----------|-----------|-----------|------------|----------------|
| name field | relocated | `name: docs-manager` | Filename `docs-manager/SKILL.md` | OpenCode derives skill name from directory structure | high | auto |
| argument-hint field | relocated | `argument-hint: <action-or-description>` | `$ARGUMENTS` placeholder in body intro | OpenCode uses `$ARGUMENTS` in body; no frontmatter argument-hint field | high | auto |
| description field | direct | `description: ...` | `description: ...` (kept) | Direct 1:1 mapping | high | N/A |
| user-invocable field | direct | `user-invocable: true` | `user-invocable: true` (kept) | Direct 1:1 mapping | high | N/A |
| disable-model-invocation | omitted | `disable-model-invocation: false` | (removed) | No equivalent in OpenCode; skills are always model-discoverable | high | auto |
| allowed-tools field | omitted | Full tool list | (removed) | No per-skill tool restrictions in OpenCode; agent-level permission is the only alternative | high | auto |
| allowed-tools: Read | direct | `Read` | `read` | Direct tool name mapping | high | N/A |
| allowed-tools: Write | direct | `Write` | `write` | Direct tool name mapping | high | N/A |
| allowed-tools: Edit | direct | `Edit` | `edit` | Direct tool name mapping | high | N/A |
| allowed-tools: Glob | direct | `Glob` | `glob` | Direct tool name mapping | high | N/A |
| allowed-tools: Grep | direct | `Grep` | `grep` | Direct tool name mapping | high | N/A |
| allowed-tools: Bash | direct | `Bash` | `bash` | Direct tool name mapping | high | N/A |
| allowed-tools: Task | direct | `Task` | `task` | Direct tool name mapping | high | N/A |
| allowed-tools: AskUserQuestion | direct | `AskUserQuestion` | `question` | Direct tool name mapping | medium | N/A |
| allowed-tools: TeamCreate | workaround | `TeamCreate` | Orchestrated `task` calls with context passing | No team orchestration in OpenCode; cached decision applied globally | high | cached |
| allowed-tools: TeamDelete | workaround | `TeamDelete` | (removed from list) | No team management needed when using task calls; cached decision applied globally | high | cached |
| allowed-tools: TaskCreate | workaround | `TaskCreate` | `todowrite` (partial) | Session-scoped scratchpad; limited functionality; cached decision applied globally | high | cached |
| allowed-tools: TaskUpdate | workaround | `TaskUpdate` | `todowrite` (partial) | Same todowrite tool; cached decision applied globally | high | cached |
| allowed-tools: TaskList | workaround | `TaskList` | `todoread` (partial) | Reads full list, no filtering; cached decision applied globally | high | cached |
| allowed-tools: TaskGet | workaround | `TaskGet` | `todoread` (partial) | No per-task ID retrieval; cached decision applied globally | high | cached |
| allowed-tools: SendMessage | workaround | `SendMessage` | Output-based communication via task response | No inter-agent messaging; cached decision applied globally | high | cached |
| Cross-plugin deep-analysis ref | direct | `Read ${CLAUDE_PLUGIN_ROOT}/../core-tools/skills/deep-analysis/SKILL.md` | `skill({ name: "deep-analysis" })` | OpenCode merged registry; cross-plugin becomes same-plugin reference pattern | high | N/A |
| Reference: mkdocs-config-template.md | workaround | `Read ${CLAUDE_PLUGIN_ROOT}/skills/docs-manager/references/mkdocs-config-template.md` | Inlined as "Reference: MkDocs Configuration Template" section | No reference_dir in OpenCode; content inlined per cached global decision | high | cached |
| Reference: change-summary-templates.md | workaround | `Read ${CLAUDE_PLUGIN_ROOT}/skills/docs-manager/references/change-summary-templates.md` | Inlined as "Reference: Change Summary Templates" section | Same cached decision as above | high | cached |
| Reference: markdown-file-templates.md | workaround | `Read ${CLAUDE_PLUGIN_ROOT}/skills/docs-manager/references/markdown-file-templates.md` | Inlined as "Reference: Markdown File Templates" section | Same cached decision as above | high | cached |
| AskUserQuestion (Phase 1 Step 2) | direct | `AskUserQuestion` | `question` tool | Direct mapping with single-select options | medium | N/A |
| AskUserQuestion (Phase 1 Step 3 mkdocs Q2) | direct | `AskUserQuestion` | `question` tool | Direct mapping | medium | N/A |
| AskUserQuestion (Phase 1 Step 3 mkdocs Q3 existing) | direct | `AskUserQuestion` | `question` tool | Direct mapping | medium | N/A |
| AskUserQuestion (Phase 1 Step 3 mkdocs Q3 new) | direct | `AskUserQuestion` | `question` tool | Direct mapping | medium | N/A |
| AskUserQuestion (Phase 1 Step 3 markdown Q2) | direct | `AskUserQuestion` | `question` tool (multi-select) | Direct mapping; header 30-char limit applies | medium | N/A |
| AskUserQuestion (Phase 1 Step 3 change-summary Q2) | direct | `AskUserQuestion` | `question` tool | Direct mapping | medium | N/A |
| AskUserQuestion (Phase 1 Step 4 confirm) | direct | `AskUserQuestion` | `question` tool | Direct mapping | medium | N/A |
| AskUserQuestion (Phase 4 Step 2 approval) | direct | `AskUserQuestion` | `question` tool | Direct mapping | medium | N/A |
| AskUserQuestion (Phase 6 Step 4 MkDocs) | direct | `AskUserQuestion` | `question` tool | Direct mapping | medium | N/A |
| AskUserQuestion (Phase 6 Step 4 markdown) | direct | `AskUserQuestion` | `question` tool | Direct mapping | medium | N/A |
| AskUserQuestion (error handling) | direct | `AskUserQuestion` | `question` tool | Direct mapping | medium | N/A |
| Agent Coordination — TeamCreate/SendMessage/TeamDelete prose | workaround | Hub-and-spoke team description via TeamCreate/SendMessage | Restructured as task tool calls with context passing; prose updated to reflect task-based coordination | Cached global decision; deep-analysis internal coordination preserved as-is (it handles its own orchestration) | high | cached |
| subagent_type: "code-explorer" | direct | `Task tool with subagent_type: "code-explorer"` | `task tool with command: "code-explorer"` | Direct parameter name change per OpenCode task tool spec | high | N/A |
| subagent_type: "docs-writer" | direct | `Task tool with subagent_type: "docs-writer"` | `task tool with command: "docs-writer"` | Direct parameter name change per OpenCode task tool spec | high | N/A |

## Gaps

| Feature | Reason | Severity | Workaround | User Acknowledged |
|---------|--------|----------|------------|-------------------|
| allowed-tools field | No per-skill tool restrictions in OpenCode; agent-level permission only | cosmetic | Field omitted; tool permissions managed at agent level via opencode.json permission config | false |
| disable-model-invocation | No concept of preventing model auto-invocation in OpenCode | cosmetic | Field omitted; skills always discoverable via skill tool | false |
| TeamCreate / TeamDelete / SendMessage | No team orchestration or inter-agent messaging in OpenCode | functional | Replaced with orchestrated task tool calls with explicit context passing in prompts; deep-analysis handles its own internal orchestration | false |
| TaskCreate / TaskUpdate / TaskList / TaskGet | Partial replacement via todowrite/todoread — session-scoped scratchpad only; no dependencies, owners, or structured statuses | functional | todowrite/todoread used; workflow relies on in-prompt state management rather than structured task tracking | false |
| reference_dir (3 reference files) | OpenCode has no reference directory; no equivalent of `reference_dir` path loading | functional | All three reference files (mkdocs-config-template, change-summary-templates, markdown-file-templates) inlined directly into skill body as named sections | false |
| question tool header 30-char limit | AskUserQuestion had no header length restriction; OpenCode question tool caps headers at 30 characters | cosmetic | Question headers kept descriptive but operators should verify length in practice | false |

## Unresolved Incompatibilities

No unresolved incompatibilities. All gaps were resolved using cached decisions (apply_globally=true) or auto-resolved as cosmetic.
