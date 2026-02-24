# Conversion Result: skill-dev-tools-project-learnings

## Metadata

| Field | Value |
|-------|-------|
| Component ID | skill-dev-tools-project-learnings |
| Component Type | skill |
| Group | dev-tools |
| Name | project-learnings |
| Source Path | claude/dev-tools/skills/project-learnings/SKILL.md |
| Target Path | skills/project-learnings/SKILL.md |
| Fidelity Score | 75% |
| Fidelity Band | yellow |
| Status | partial |

## Converted Content

~~~markdown
---
description: >-
  Captures project-specific patterns and anti-patterns into the project's CLAUDE.md.
  Loaded by other skills (bug-killer, feature-dev, etc.) when they discover
  project-specific knowledge worth encoding for future sessions.
user-invocable: false
---

# Project Learnings

Capture project-specific patterns and anti-patterns into the project's CLAUDE.md. This creates a self-improving feedback loop where discoveries from debugging, development, and review make future Claude sessions smarter.

**CRITICAL:** Only project-specific knowledge qualifies. Generic programming advice does not belong in CLAUDE.md.

---

## Step 1: Evaluate Discovery

Determine if the finding qualifies as project-specific. The finding must pass at least ONE of these criteria:

| Criteria | Example That Qualifies | Example That Doesn't |
|----------|------------------------|----------------------|
| Would a developer unfamiliar with this project likely hit this issue? | "The `processOrder()` function expects amounts in cents, not dollars" | "Always validate function inputs" |
| Is this pattern specific to this codebase's architecture, APIs, or conventions? | "The `UserProfile` type has an optional `metadata` field that is always present at runtime" | "Use TypeScript strict mode" |
| Is it something Claude's training data wouldn't cover? | "Never call `db.query()` without the `timeout` option — the default is infinite" | "Use async/await instead of callbacks" |

**If NO to all criteria → STOP.** Do not add generic programming knowledge to CLAUDE.md. Return to the calling skill and report that no project-specific learning was found.

**If YES to any → proceed to Step 2.**

---

## Step 2: Read Existing CLAUDE.md

1. **Find the project's CLAUDE.md:**
   - Check the repository root first
   - If not found, check if there's a project-level `.claude/` directory

2. **Parse existing content:**
   - Understand the existing structure, headings, and conventions
   - Look for sections where this learning would fit (e.g., "Known Gotchas", "Bug Patterns", "Conventions", "Known Challenges")
   - Check for duplicate or similar entries already present

3. **If a similar entry already exists → STOP.** Report to the calling skill that this knowledge is already captured. Do not create duplicates.

4. **Identify placement:**
   - If an appropriate section exists, plan to add the entry there
   - If no appropriate section exists, plan to propose a new section (e.g., `## Known Gotchas` or `## Project-Specific Patterns`)
   - New sections should be placed after the main documentation sections but before appendices or settings

---

## Step 3: Format the Learning

Write a concise, actionable instruction following these rules:

**Format:**
- Use imperative form: "Always validate X before calling Y"
- Include the WHY: "...because the API returns dates as strings, not Date objects"
- Keep it to 1-3 lines
- Follow the existing CLAUDE.md style and conventions

**Templates:**

For bug patterns:
```
- **[Area/Component]**: [What to do/avoid] — [why, with specific details]
```

For API gotchas:
```
- `functionName()` in `path/to/file`: [What's surprising about it] — [consequence if ignored]
```

For architectural constraints:
```
- [Constraint description] — [why it exists and what breaks if violated]
```

**Examples of well-formatted learnings:**
- **Order processing**: Always multiply amounts by 100 before passing to `processOrder()` — it expects cents, not dollars
- `db.query()` in `src/database.ts`: Always pass the `timeout` option — the default is infinite and has caused production hangs (30 second timeout recommended)
- Never import from `internal/` directories in `src/api/` — the build system treats these as separate compilation units and circular dependencies will silently break HMR

---

## Step 4: Confirm with User

Present the proposed addition via the `question` tool:

Show:
1. The exact text to be added
2. Where it will be placed in CLAUDE.md (section name, after which line/entry)
3. Why this qualifies as project-specific

Options:
- **"Add this"** — Write the entry as proposed
- **"Edit before adding"** — User provides modified text, then write that instead
- **"Skip"** — Do not add anything, return to calling skill

Note: `question` tool header must be 30 characters or fewer. Use a concise header such as "Add to CLAUDE.md?" and present details in the options or as preceding prose.

---

## Step 5: Write Update

If the user confirmed (or provided edited text):

1. Use the `edit` tool to add the entry to CLAUDE.md at the identified location
2. If a new section was needed, create the section heading first
3. Verify the edit was applied correctly by reading the modified area
4. Report success to the calling skill with a summary of what was added

If the user chose "Skip":
- Report to the calling skill that the learning was declined
- Do not modify any files
~~~

## Fidelity Report

| Mapping Type | Count | Weight | Contribution |
|-------------|-------|--------|-------------|
| Direct | 6 | 1.0 | 6.0 |
| Workaround | 0 | 0.7 | 0.0 |
| TODO | 0 | 0.2 | 0.0 |
| Omitted | 2 | 0.0 | 0.0 |
| **Total** | **8** | | **75** |

**Notes:** Two frontmatter fields (`disable-model-invocation` and `allowed-tools`) were omitted as cosmetic gaps — both map to null in OpenCode's skill frontmatter model. The skill's core functionality (body logic, tool references, user interaction flow) is fully preserved with direct mappings. The `AskUserQuestion` -> `question` mapping has medium confidence; a note about the 30-char header limit was added inline.

## Decisions

| Feature | Decision Type | Original | Converted | Rationale | Confidence | Resolution Mode |
|---------|-------------|----------|-----------|-----------|------------|----------------|
| name field | relocated | `name: project-learnings` in frontmatter | Derived from directory name `skills/project-learnings/SKILL.md` | Frontmatter `name` maps to `embedded:filename` in OpenCode skill convention | high | auto |
| description field | direct | `description: Captures project-specific...` | `description: Captures project-specific...` (unchanged) | Direct 1:1 mapping — `description` is required in OpenCode skill frontmatter | high | N/A |
| user-invocable field | direct | `user-invocable: false` | `user-invocable: false` | Direct 1:1 mapping — controls appearance in command dialog | high | N/A |
| disable-model-invocation field | omitted | `disable-model-invocation: false` | (omitted) | Maps to null in OpenCode. Field was `false` (already permissive default), no behavioral loss. Skills are always model-discoverable in OpenCode. | high | auto |
| allowed-tools field | omitted | `allowed-tools: Read, Edit, Glob, AskUserQuestion` | (omitted) | OpenCode has no per-skill tool restrictions. All four tools (read, edit, glob, question) have OpenCode equivalents; only the restriction mechanism is lost. Agent-level `permission` is the alternative if restriction is needed. | high | auto |
| AskUserQuestion body reference | direct | `via AskUserQuestion` / `Present the proposed addition via AskUserQuestion:` | `via the \`question\` tool` / `Present the proposed addition via the \`question\` tool:` | AskUserQuestion maps directly to `question` tool (medium confidence). Added note about 30-char header constraint. | medium | N/A |
| Edit tool body reference | direct | `Use the Edit tool` | `Use the \`edit\` tool` | Edit maps directly to `edit` in OpenCode (high confidence) | high | N/A |

## Gaps

| Feature | Reason | Severity | Workaround | User Acknowledged |
|---------|--------|----------|------------|-------------------|
| allowed-tools restriction | OpenCode has no per-skill tool restrictions; `allowed-tools` maps to null | cosmetic | Omit field; tools (read, edit, glob, question) remain available unrestricted. Use agent-level `permission` frontmatter if restriction is required. | false |
| disable-model-invocation | No concept of preventing model auto-invocation of skills in OpenCode | cosmetic | Omit field; skills are always discoverable. Value was `false` so no behavioral change. | false |
| question tool header limit | `question` tool (AskUserQuestion equivalent) has a 30-character maximum header length | functional | Added inline note to Step 4 instructing skill to use a concise header such as "Add to CLAUDE.md?" | false |

## Unresolved Incompatibilities

| Group Key | Feature | Severity | Category | Reason | Suggested Workaround | Confidence | Affected Locations |
|-----------|---------|----------|----------|--------|---------------------|------------|-------------------|
| (none) | | | | | | | |

No unresolved incompatibilities. All gaps were auto-resolved (cosmetic severity) or handled via inline notes (functional, low-impact).
