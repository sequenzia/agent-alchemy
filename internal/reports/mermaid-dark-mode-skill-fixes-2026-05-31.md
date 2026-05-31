# Skill Fixes Report — Mermaid Dark-Mode Breakage

## Metadata

| Field | Value |
|-------|-------|
| **Date** | 2026-05-31 |
| **Time** | 18:25 EDT |
| **Branch** | main |
| **Author** | Stephen Sequenzia |
| **Base Commit** | `f70a74b` |
| **Latest Commit** | uncommitted |
| **Repository** | git@github.com:sequenzia/agent-alchemy.git |

**Scope**: Fix the `technical-diagrams` and `docs-manager` skills so generated MkDocs sites render Mermaid diagrams correctly in dark mode, plus three adjacent `docs-manager` defects hit during the same work.

**Summary**: The skills produced Mermaid diagrams that are unreadable in MkDocs Material's dark (`slate`) scheme — and the docs-manager scaffold actively ships a dark-mode toggle while omitting the stylesheet needed to make diagrams legible under it. Encoded the root-cause knowledge into `technical-diagrams`, made `docs-manager` ship and wire the dark-mode companion stylesheet automatically, removed a build-breaking config option, added a dependency-install step, and added a dark-mode verification step. All changes are documentation/templates inside the two skills; no agent or hook code changed.

## How this surfaced

While building a full MkDocs site for an unrelated project (AMC), every Mermaid diagram followed the `technical-diagrams` palette (light pastel fills + `color:#000` dark text). In light mode they were perfect. In dark mode the diagram text was invisible (light-on-light), and after fixing the text, the arrows/edges were invisible wherever they crossed a light fill. It took two fix rounds on the live site (text, then edges) before the diagrams were legible in both palettes. This report captures *why* the skills produced broken diagrams and the changes that prevent it going forward.

---

## The Problems

### P1 — `technical-diagrams` is light-mode-only by design (root cause)

`SKILL.md` "Critical Styling Rules → Rule 1: Always use dark text on nodes" mandates `color:#000` on every node, paired with a fixed light-fill palette (`#dbeafe`, `#f3e8ff`, `#fef3c7`, …). This is correct **only on a light page**. The skill had **zero dark-mode awareness**: no mention of theme adaptivity, MkDocs Material's dark scheme, the `--md-mermaid-*` CSS variables, or what happens to hard-coded colors when a renderer auto-switches themes. It even claimed Mermaid "renders natively in … MkDocs (with Material theme)" without noting the dark-mode contrast trap.

### P2 — `docs-manager` ships the dark toggle but not the fix (the systemic defect)

`references/mkdocs-config-template.md` provides a `mkdocs.yml` whose `palette` block includes **both** a light `default` scheme and a dark `slate` scheme — so *every* generated site has a dark-mode toggle. The Phase 5 docs-writer prompt then instructs writers to produce light-fill/dark-text diagrams (per P1) with **no companion stylesheet and no `extra_css` wiring**. The result is a guaranteed regression: ship a dark mode, fill it with diagrams that only work in light mode.

**The underlying mechanism (verified in `mkdocs-material` 9.7.6):** Material themes every Mermaid diagram by injecting a `themeCSS` that reads CSS custom properties — `--md-mermaid-label-fg-color`, `--md-mermaid-label-bg-color`, `--md-mermaid-edge-color`, `--md-mermaid-node-bg-color`, the `--md-mermaid-sequence-*` set — which **flip** for the `slate` scheme (label text becomes light, etc.). The diagram SVG is rendered into a **closed shadow root**, so ordinary `.mermaid text { … }` page CSS cannot reach it — but those custom properties **inherit through the shadow boundary**, which is exactly how Material themes the diagram. So the only correct fix is to redefine the variables for the dark scheme.

This produced two distinct dark-mode failures:
- **Light-on-light text** — the flipped light label color lands on the hard-coded light node/subgraph/ER fills, so titles and labels vanish.
- **Edges disappear on light fills** — Material draws edges light so they show on the dark page, but a single edge frequently crosses **both** the dark page *and* a light fill, so neither a light nor a dark stroke works alone. The fix is a **mid-tone** edge color (and keeping sequence *message* text light, since it floats over the dark page).

### P3 — Build-breaking `pygments_lang_guess: false` in the template

The `pymdownx.highlight` block in the template set `pygments_lang_guess: false`. With current `pymdown-extensions` (10.21.x) that option no longer exists and `mkdocs build` aborts with `KeyError: 'pygments_lang_guess'`. Any site generated from the template fails to build until the line is removed.

### P4 — No dependency-install step

The MkDocs initialization (Phase 2, Step 3) generated `mkdocs.yml` and pages but never installed `mkdocs`/`mkdocs-material`. The workflow then assumed the `mkdocs` CLI was available for Phase 6 validation. On a fresh project nothing is installed, so the build/serve checks can't run.

### P5 — No dark-mode verification

Phase 6 validation was structural only (nav files exist, cross-references resolve, `mkdocs build --strict`). Nothing rendered the site or checked dark mode — so the P1/P2 contrast failure would (and did) sail straight through to the user. There was no step that could have caught it.

---

## The Fixes

### `technical-diagrams` — encode the "why"

File: `claude/core-tools/skills/technical-diagrams/SKILL.md`

- **Reframed Rule 1** (did not remove it): added a caveat that `color:#000` assumes a light page and is *not* self-sufficient on auto-theming renderers (MkDocs Material `slate`), with a pointer to the new section and an explicit warning not to "fix" it by switching to light text (that just inverts the problem).
- **Added a "Dark-mode rendering" subsection** under "Styling and Theming" (kept in `SKILL.md`, not a reference file, so it always loads alongside the palette that causes the issue). It documents the `--md-mermaid-*` mechanism, the closed-shadow-DOM/variable-inheritance detail, the two failure modes, the canonical companion CSS, and the two non-obvious choices (**mid-tone edge**, **keep sequence message text light**).

### `docs-manager` — ship + wire + install + verify (the "how")

Files under `claude/dev-tools/skills/docs-manager/`:

- **`references/mkdocs-config-template.md`**
  - Removed `pygments_lang_guess: false` (fixes P3).
  - Added `extra_css:\n  - stylesheets/extra.css` to the `mkdocs.yml` template, with a "required, not optional" callout.
  - Added a new "Mermaid dark-mode stylesheet" section containing the exact `docs/stylesheets/extra.css` to write, with a "keep in sync with technical-diagrams" note.
  - Updated "Usage Instructions → Write the files" to include `docs/stylesheets/extra.css`.
- **`SKILL.md` Phase 2, Step 3** — added a dependency-install step (Python: a `docs` group with `mkdocs-material` + `pymdown-extensions`; otherwise `pip install mkdocs-material`) and made the step scaffold `docs/stylesheets/extra.css` alongside `mkdocs.yml` (fixes P4 + ships the companion).
- **`SKILL.md` Phase 5** — updated both docs-writer "Diagram guidance" lines: keep the standard light-fill palette, don't hand-roll per-diagram dark-mode colors (the site ships the companion). The Basic-Markdown line notes that standalone GitHub Markdown can't ship a stylesheet, so the standard palette is the right choice there.
- **`SKILL.md` Phase 6, Step 2** — added a dark-mode verification step (confirm `extra.css` exists and is wired; `mkdocs serve`, toggle to `slate`, check node/subgraph titles, edge labels, **edges crossing light fills**, and sequence/ER text in both modes), explicitly called out as the check that catches hard-coded-color contrast regressions (fixes P5).

### The canonical companion stylesheet

This is the battle-tested block now carried (byte-identical property values) by both skills and written to `docs/stylesheets/extra.css` on every scaffold:

```css
[data-md-color-scheme="slate"] {
  --md-mermaid-label-fg-color: #1b2330;            /* node + subgraph titles + edge-label text */
  --md-mermaid-label-bg-color: #eef1f6;            /* edge-label / actor / note chip backgrounds */
  --md-mermaid-node-fg-color: #5b4b86;             /* node / ER-entity / actor borders */
  --md-mermaid-node-bg-color: #ece9f6;             /* ER entity + attribute fills, sequence frames */
  --md-mermaid-edge-color: #737d91;                /* edges/arrows: mid-tone — one edge can cross BOTH the dark page and a light fill */
  --md-mermaid-sequence-message-fg-color: #cfd6e2; /* message text floats over the dark page — keep it light */
  --md-mermaid-sequence-note-fg-color: #1b2330;    /* note text sits on a light note box */
  --md-mermaid-sequence-loop-fg-color: #1b2330;    /* alt/par/loop labels on the now-light frame */
  --md-mermaid-sequence-box-fg-color: #1b2330;
}
```

It is scoped to `slate`, so light mode is untouched, and it edits no diagram source. Verified on the live AMC site (passes `mkdocs build --strict`, legible in both palettes).

---

## Files Changed

| File | Status | Lines | Description |
|------|--------|-------|-------------|
| `claude/core-tools/skills/technical-diagrams/SKILL.md` | Modified | +60 | Rule 1 caveat + new "Dark-mode rendering" subsection with the companion CSS and the why |
| `claude/dev-tools/skills/docs-manager/references/mkdocs-config-template.md` | Modified | +49 / -1 | Removed `pygments_lang_guess`; added `extra_css`; added "Mermaid dark-mode stylesheet" section; updated write-files list |
| `claude/dev-tools/skills/docs-manager/SKILL.md` | Modified | +18 / -6 | Phase 2 deps-install + scaffold CSS; Phase 5 diagram-guidance lines; Phase 6 dark-mode verification |

Totals: **3 files, +120 / −7.**

## Verification

- `pygments_lang_guess` no longer present in the template (grep count 0).
- `extra_css` wired to `stylesheets/extra.css`; scaffold writes `docs/stylesheets/extra.css` — paths consistent across both files.
- The `[data-md-color-scheme="slate"]` rule body is **byte-identical** between `technical-diagrams/SKILL.md` and the docs-manager template, and the property values match the live, proven AMC `docs/stylesheets/extra.css` (only inline-comment wording was polished in the skill versions).
- Rule 1's anchor link resolves to the new "Dark-mode rendering" heading.

## Git Status & follow-ups

All three files are **modified and uncommitted** on `main` (base `f70a74b`). No commits made in this session.

**Marketplace re-sync required:** these are the *source* skills. Live Claude sessions load the installed copies under `~/.claude/plugins/marketplaces/agent-alchemy/…`; they must be re-synced (publish/pull the marketplace, bump versions in `.claude-plugin/marketplace.json` as other reports do) before a future `docs-manager` run picks up the fix.
