# sdd-tools Standalone Refactor Report

**Date**: 2026-02-21
**Scope**: sdd-tools plugin group — removal of cross-plugin dependency on core-tools
**Summary**: Replaced `create-spec`'s cross-plugin dependency on `deep-analysis` (core-tools) with a standalone codebase exploration system built from a new `codebase-explorer` agent and a `codebase-exploration.md` reference procedure. sdd-tools is now fully self-contained with zero external plugin dependencies.

---

## Motivation

The `create-spec` skill (sdd-tools) previously loaded `deep-analysis` from core-tools for codebase exploration during "new feature" type specs. This cross-plugin reference meant sdd-tools could not be distributed or installed independently — it required core-tools to be present.

The deep-analysis skill is a heavyweight hub-and-spoke team engine (521 lines, spawning N explorer agents + 1 synthesizer with team coordination, caching, and checkpointing). For create-spec's use case — gathering enough codebase context to ask informed interview questions — this was over-engineered. The refactoring replaces it with a lightweight, purpose-built exploration system that preserves the parallel exploration pattern while dropping the team coordination overhead.

---

## Files Changed

| File | Action | Description |
|------|--------|-------------|
| `claude/sdd-tools/agents/codebase-explorer.md` | **Created** | New Sonnet-tier agent for parallel codebase exploration |
| `claude/sdd-tools/skills/create-spec/references/codebase-exploration.md` | **Created** | 4-step exploration procedure replacing deep-analysis workflow |
| `claude/sdd-tools/skills/create-spec/SKILL.md` | **Modified** | Rewired exploration section + trimmed frontmatter tools |
| `claude/sdd-tools/README.md` | **Modified** | Added standalone callout, agent table entry, directory tree entries |
| `CLAUDE.md` | **Modified** | Updated dependency count, composition chain, plugin inventory |

---

## Detailed Changes

### 1. `claude/sdd-tools/agents/codebase-explorer.md` (Created — 120 lines)

A new Sonnet-tier exploration agent purpose-built for create-spec. Designed to be spawned 2-3 times in parallel via the `Task` tool, each instance exploring a different focus area of the codebase.

**Comparison with core-tools' `code-explorer`:**

| Aspect | core-tools `code-explorer` | sdd-tools `codebase-explorer` |
|--------|---------------------------|-------------------------------|
| Model | Sonnet | Sonnet |
| Tools | Read, Glob, Grep, Bash, SendMessage, TaskUpdate, TaskGet, TaskList | Read, Glob, Grep, Bash |
| Skills | project-conventions, language-patterns | — |
| Team comms | Full (assignment ack, synthesizer Q&A, duplicate avoidance) | None (fire-and-forget) |
| Spawned by | deep-analysis (core-tools) | create-spec (sdd-tools) |
| Coordination | Team-based via SendMessage + TaskUpdate | Independent via Task tool return |
| Output delivery | SendMessage to team lead + TaskUpdate | Direct return as Task tool result |
| Lines | 157 | 120 |

The key design decision: `codebase-explorer` drops team communication tools (`SendMessage`, `TaskUpdate`, `TaskGet`, `TaskList`) and skill bindings (`project-conventions`, `language-patterns`). It uses the simpler Task tool pattern where agents return their findings as their final message, eliminating the need for team coordination infrastructure.

---

### 2. `claude/sdd-tools/skills/create-spec/references/codebase-exploration.md` (Created — 136 lines)

A 4-step exploration procedure that replaces deep-analysis's 6-phase team workflow:

| Step | Purpose |
|------|---------|
| **1. Quick Reconnaissance** | Map project structure and identify language/framework/architecture (3-5 tool calls) |
| **2. Plan Focus Areas** | Determine 2-3 exploration themes based on feature + recon findings |
| **3. Parallel Exploration** | Spawn 2-3 `codebase-explorer` agents concurrently via Task tool |
| **4. Synthesis** | Merge all agent findings into structured "Codebase Context" |

The procedure includes:
- A Task prompt template with required fields (feature description, project context, focus area, recon summary)
- Output format for the merged "Codebase Context" section
- Error handling at three levels: partial agent failure, total agent failure, and reconnaissance failure
- Optional skip via `AskUserQuestion` before exploration begins

---

### 3. `claude/sdd-tools/skills/create-spec/SKILL.md` (Modified — 659 lines, was ~665)

Two changes:

#### 3a. Frontmatter: `allowed-tools` trimmed

```yaml
# Before
allowed-tools: AskUserQuestion, Task, Read, Write, Glob, Grep, Bash, TeamCreate, TeamDelete, TaskCreate, TaskUpdate, TaskList, TaskGet, SendMessage

# After
allowed-tools: AskUserQuestion, Task, Read, Write, Glob, Grep, Bash
```

Removed 7 team coordination tools: `TeamCreate`, `TeamDelete`, `TaskCreate`, `TaskUpdate`, `TaskList`, `TaskGet`, `SendMessage`. These were only needed because deep-analysis creates a formal team with task lists and inter-agent messaging. The standalone approach uses the simpler `Task` tool for fire-and-forget agent spawning.

#### 3b. Codebase Exploration section (lines 253-280) rewritten

**Before** (36 lines): Instructed create-spec to load and execute the full deep-analysis workflow by reading `${CLAUDE_PLUGIN_ROOT}/../core-tools/skills/deep-analysis/SKILL.md`. Included notes about cache behavior and a 2-option fallback (quick exploration or skip).

**After** (27 lines): Points to the local reference file at `${CLAUDE_PLUGIN_ROOT}/skills/create-spec/references/codebase-exploration.md` and instructs the skill to follow all 4 steps. Error handling now has three tiers instead of two:

| Tier | Before | After |
|------|--------|-------|
| Partial failure | Not handled separately | Continue with successful agents' findings |
| Total failure | "Inform user, offer fallback" | Use reconnaissance findings as minimal context |
| Reconnaissance failure | Not handled | AskUserQuestion fallback (quick explore or skip) |

---

### 4. `claude/sdd-tools/README.md` (Modified)

Three additions:

1. **Standalone callout** — Added blockquote after the intro:
   > **Standalone plugin** — sdd-tools has no external plugin dependencies. Codebase exploration for "new feature" specs uses a built-in `codebase-explorer` agent instead of cross-plugin references.

2. **Agent table** — Added `codebase-explorer` row:
   | Agent | Model | Purpose |
   |-------|-------|---------|
   | `codebase-explorer` | sonnet | Explores codebases to discover architecture, patterns, and feature-relevant code. Spawned in parallel by `/create-spec` for "new feature" type specs. |

3. **Directory tree** — Added two entries:
   - `agents/codebase-explorer.md` in the agents section
   - `references/codebase-exploration.md` in the create-spec references section

---

### 5. `CLAUDE.md` (Modified)

Three updates to the project-level documentation:

1. **Cross-Plugin Dependencies** — Updated dependency count:
   ```
   # Before
   loaded by 4 skills across 3 plugin groups
   - create-spec (sdd-tools) — optionally loads for "new feature" type specs

   # After
   loaded by 3 skills across 2 plugin groups
   (create-spec line removed)
   ```

2. **Key Skill Composition Chains** — Updated create-spec chain:
   ```
   # Before
   create-spec -> deep-analysis (optional, for "new feature" type)

   # After
   create-spec -> codebase-explorer (sonnet) x 2-3 (optional, for "new feature" type)
   ```

3. **Plugin Inventory** — Updated sdd-tools agents column:
   ```
   # Before
   researcher, spec-analyzer, task-executor

   # After
   codebase-explorer, researcher, spec-analyzer, task-executor
   ```

---

## Architecture Comparison

| Capability | deep-analysis (before) | Standalone replacement (after) |
|-----------|----------------------|-------------------------------|
| **Agent model** | Sonnet (explorers) + Opus (synthesizer) | Sonnet (explorers only) |
| **Parallelism** | N explorers via TeamCreate + TaskList | 2-3 explorers via Task tool |
| **Synthesis** | Dedicated Opus synthesizer agent with follow-up questions + Bash investigation | Inline by create-spec skill itself |
| **Team coordination** | Full (SendMessage, TaskUpdate, TaskGet) | None (fire-and-forget Task returns) |
| **Caching** | Session-level cache with configurable TTL | None |
| **Checkpointing** | Phase-boundary checkpoints for recovery | None |
| **Skill bindings** | project-conventions, language-patterns | None |
| **Error recovery** | 2-tier (team failure → quick explore/skip) | 3-tier (partial → recon fallback → quick explore/skip) |
| **Tool permissions** | 14 tools in frontmatter | 7 tools in frontmatter |
| **Cross-plugin deps** | Yes (core-tools required) | None (fully standalone) |
| **Total agent lines** | 157 (code-explorer) + 521 (deep-analysis SKILL.md) | 120 (codebase-explorer) + 136 (exploration procedure) |

---

## What's Preserved

These behavioral aspects carry over from the deep-analysis approach:

- **Parallel exploration** — Multiple agents explore different focus areas concurrently
- **Structured output** — Agents return findings in a consistent markdown format with tables, file paths, and relevance ratings
- **Focus area planning** — Exploration targets are determined based on the feature description, not hardcoded
- **Graceful degradation** — Exploration failures don't block spec creation; fallbacks are offered
- **User control** — Users can skip exploration entirely via AskUserQuestion
- **Reconnaissance phase** — Quick project structure mapping before spawning agents
- **Exploration strategies** — Same 4-strategy approach (entry points, data flow, similar features, dependencies)

---

## What's Changed

| Removed | Rationale |
|---------|-----------|
| Opus synthesizer agent | Synthesis is simple enough for create-spec to do inline — no need for a separate high-reasoning agent |
| Team coordination (SendMessage, TaskList, etc.) | Task tool's return-value pattern is sufficient for fire-and-forget exploration |
| Session caching | Spec creation is typically a one-shot workflow; caching adds complexity without proportional benefit |
| Phase-boundary checkpointing | The 4-step procedure is lightweight enough that checkpoint recovery isn't needed |
| project-conventions / language-patterns skill bindings | Agents are exploring for spec context, not implementing code — convention awareness isn't required |
| Follow-up question protocol | Synthesizer asking explorers clarifying questions added latency; inline synthesis can read files directly if needed |
| Assignment acknowledgment protocol | Fire-and-forget agents don't need handshake protocols |

---

## Verification Checklist

- [ ] `claude/sdd-tools/agents/codebase-explorer.md` exists with Sonnet model, 4 tools (Read, Glob, Grep, Bash), and no team tools
- [ ] `claude/sdd-tools/skills/create-spec/references/codebase-exploration.md` exists with 4-step procedure
- [ ] `claude/sdd-tools/skills/create-spec/SKILL.md` frontmatter has 7 allowed-tools (no TeamCreate, TaskCreate, SendMessage, etc.)
- [ ] `claude/sdd-tools/skills/create-spec/SKILL.md` line 257 references `${CLAUDE_PLUGIN_ROOT}/skills/create-spec/references/codebase-exploration.md` (same-plugin path, no `/../core-tools/` reference)
- [ ] No remaining references to `deep-analysis` or `core-tools` anywhere in `claude/sdd-tools/`
- [ ] `claude/sdd-tools/README.md` has standalone callout, codebase-explorer in agent table, both new files in directory tree
- [ ] `CLAUDE.md` Cross-Plugin Dependencies says "3 skills across 2 plugin groups" (not 4/3)
- [ ] `CLAUDE.md` composition chain shows `create-spec -> codebase-explorer (sonnet) x 2-3`
- [ ] `CLAUDE.md` plugin inventory sdd-tools agents column includes `codebase-explorer`
- [ ] Running `/create-spec` with "New feature" type triggers the standalone exploration procedure (functional test)
