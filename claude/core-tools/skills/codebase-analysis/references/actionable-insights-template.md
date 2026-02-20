# Actionable Insights Template

Use this template when presenting and processing actionable items in Phase 3's "Address Actionable Insights" action.

---

## Item List Format

Present extracted items grouped by severity, highest first:

```markdown
### High Severity

1. **{Title}** — _{Source: Challenges & Risks}_
   {Brief description of the issue and its impact}

2. **{Title}** — _{Source: Recommendations}_
   {Brief description and rationale}

### Medium Severity

3. **{Title}** — _{Source: Recommendations}_
   {Brief description and rationale}

### Low Severity

4. **{Title}** — _{Source: Other Findings}_
   {Brief description}
```

---

## Severity Assignment Guidelines

### From Challenges & Risks Table
- Use the **Severity** column value directly (High, Medium, or Low)
- Title comes from the **Challenge** column
- Description comes from the **Impact** column

### From Recommendations Section
- Each recommendation in the report should explicitly cite which challenge it addresses (see report template). Use this citation to inherit severity:
  - Recommendation cites a **High** challenge → assign **High**
  - Recommendation cites a **Medium** challenge → assign **Medium**
  - Recommendation cites a **Low** challenge → assign **Low**
- If a recommendation addresses multiple challenges, use the highest severity among them
- If no challenge link is present (legacy reports or standalone recommendations), infer from context or default to **Medium**

### From Other Findings
- Default to **Low** unless the finding explicitly describes a critical issue
- Only include findings that have a concrete, implementable fix

---

## Complexity Assessment Criteria

### Simple (No agent needed)
- Single file change
- Clear, localized fix (rename, add validation, fix import, update config)
- No architectural impact
- Change is self-contained — no cascading modifications needed

### Complex — Architectural (Use `agent-alchemy-core-tools:code-architect`)
- Requires refactoring across multiple files
- Introduces or changes a pattern (new abstraction, restructured module boundaries)
- Affects system architecture (data flow, component relationships, API contracts)
- Requires design decisions about approach

### Complex — Investigation Needed (Use `agent-alchemy-core-tools:code-explorer` with Sonnet)
- Root cause is unclear or needs tracing through the codebase
- Multiple potential locations for the fix
- Requires understanding current behavior before proposing changes
- Dependencies or side effects need mapping

### Effort Estimates

Provide rough effort alongside complexity to help users prioritize:

| Complexity | Typical Effort | Description |
|-----------|---------------|-------------|
| Simple | Low (~minutes) | Single targeted change, clear fix |
| Complex — Architectural | Medium–High (~30min–1hr+) | Multi-file refactoring, design decisions |
| Complex — Investigation | Medium (~15-30min) + varies | Investigation phase + fix implementation |

---

## Change Proposal Format

Present each proposed fix using this structure:

```markdown
#### {Item Title} ({Severity})

**Complexity:** Simple / Complex (architectural) / Complex (investigation)
**Effort:** Low (~minutes) / Medium (~30min) / High (~1hr+)

**Files to modify:**
| File | Change Type |
|------|-------------|
| `path/to/file` | Edit / Create / Delete |

**Proposed changes:**
{Description of what will change and why. For simple fixes, show the specific code changes. For complex fixes, describe the approach.}

**Rationale:**
{Why this approach was chosen. Reference the original finding.}
```

---

## Summary Format

After processing all selected items, present:

```markdown
## Actionable Insights Summary

### Items Addressed
| # | Item | Severity | Files Modified |
|---|------|----------|----------------|
| 1 | {Title} | High | `file1.ts`, `file2.ts` |
| 2 | {Title} | Medium | `file3.ts` |

### Items Skipped
| # | Item | Severity | Reason |
|---|------|----------|--------|
| 3 | {Title} | Low | User skipped |

### Files Modified
| File | Changes |
|------|---------|
| `path/to/file` | {Brief description of change} |

**Total:** {N} items addressed, {M} items skipped, {P} files modified
```

---

## Section Guidelines

### Item Extraction
- Only extract items with concrete, actionable fixes — skip vague observations
- **Deduplication criteria** — Merge items that match on any of:
  - Same target file or component mentioned in both items
  - Significant keyword overlap in titles (2+ shared meaningful words)
  - One item is a superset of the other (e.g., "fix error handling in auth" subsumes "add try-catch to login endpoint")
- When deduplicating, keep the higher severity, merge descriptions, and note both source sections

### User Selection
- Present items in severity order so the user sees the most impactful items first
- Keep descriptions concise in the selection list — details come in the proposal

### Processing Order
- Process items in the order the user selected them, but within that, prioritize by severity
- **Conflict detection** — Before starting fixes, scan the selected items for potential conflicts:
  - **Same-file modifications**: Two items targeting the same file(s) — flag ordering risk
  - **Contradictory changes**: One item adds what another removes, or they modify the same function/component in incompatible ways
  - **Ordering dependencies**: One fix creates a prerequisite for another (e.g., "add error type" must precede "use error type in handler")
- If conflicts are detected, present them to the user before proceeding and suggest a processing order that resolves dependencies

### Revision Cycles
- Maximum 3 revision cycles per item when user selects "Modify"
- After 3 cycles, present final proposal with Apply or Skip only
- Track what the user changed in each cycle to converge on the right fix
