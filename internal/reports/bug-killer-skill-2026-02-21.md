# Codebase Changes Report

## Metadata

| Field | Value |
|-------|-------|
| **Date** | 2026-02-21 |
| **Time** | 16:41 EST |
| **Branch** | main |
| **Author** | Stephen Sequenzia |
| **Base Commit** | a751fc5 |
| **Latest Commit** | uncommitted |
| **Repository** | git@github.com:sequenzia/agent-alchemy.git |

**Scope**: Add `bug-killer` debugging skill, `project-learnings` internal skill, and `bug-investigator` agent to dev-tools plugin

**Summary**: Created a systematic, hypothesis-driven debugging workflow (`bug-killer`) for the dev-tools plugin with triage-based routing (quick/deep track), language-specific debugging references, a dedicated investigation agent (`bug-investigator`), and a reusable internal skill (`project-learnings`) for capturing project-specific patterns into CLAUDE.md. Updated all relevant documentation.

## Overview

Added 6 new files and modified 2 existing files to introduce debugging capabilities to the dev-tools plugin group. The implementation follows existing plugin composition patterns — hub-and-spoke agent coordination, phase-based workflows, and progressive reference loading.

- **Files affected**: 8
- **Lines added**: +1,585
- **Lines removed**: -3
- **Commits**: 0 (all changes uncommitted)

## Files Changed

| File | Status | Lines | Description |
|------|--------|-------|-------------|
| `claude/dev-tools/skills/bug-killer/SKILL.md` | Added | +470 | Main 5-phase debugging workflow with triage routing |
| `claude/dev-tools/skills/bug-killer/references/typescript-debugging.md` | Added | +325 | TypeScript/JavaScript debugging reference |
| `claude/dev-tools/skills/bug-killer/references/python-debugging.md` | Added | +265 | Python debugging reference |
| `claude/dev-tools/skills/bug-killer/references/general-debugging.md` | Added | +221 | Language-agnostic debugging reference |
| `claude/dev-tools/agents/bug-investigator.md` | Added | +168 | Sonnet investigation agent for hypothesis testing |
| `claude/dev-tools/skills/project-learnings/SKILL.md` | Added | +117 | Internal skill for CLAUDE.md learning capture |
| `CLAUDE.md` | Modified | +8 / -2 | Updated repo structure, composition chains, plugin inventory, critical files |
| `claude/dev-tools/README.md` | Modified | +14 / -1 | Added skills, agents, and directory structure entries |

## Change Details

### Added

- **`claude/dev-tools/skills/bug-killer/SKILL.md`** — Main skill implementing a 5-phase debugging workflow: Triage & Reproduction, Investigation, Root Cause Analysis, Fix & Verify, Wrap-up & Report. Features triage-based routing (quick vs deep track), hypothesis journal maintenance, auto-escalation from quick to deep after 2 rejected hypotheses, and `--deep` flag support. Both user-invocable (`/bug-killer`) and model-invocable.

- **`claude/dev-tools/agents/bug-investigator.md`** — Sonnet-model investigation agent with read-only + Bash access (no Write/Edit). Tests debugging hypotheses by running tests, tracing execution, checking git history, and reporting structured evidence. Follows the separation-of-concerns pattern from `code-reviewer` (investigate and report, don't fix).

- **`claude/dev-tools/skills/project-learnings/SKILL.md`** — Internal skill (`user-invocable: false`) that captures project-specific patterns into CLAUDE.md. 5-step workflow: evaluate if the discovery qualifies as project-specific, read existing CLAUDE.md, format the learning, confirm with user via AskUserQuestion, write the update. Designed for reuse by bug-killer and other skills.

- **`claude/dev-tools/skills/bug-killer/references/python-debugging.md`** — Python-specific debugging reference covering pytest flags, traceback analysis (bottom-to-top reading), common exception types table, Python gotchas (mutable defaults, late binding closures, circular imports), diagnostic logging, cProfile profiling, and git bisect with pytest.

- **`claude/dev-tools/skills/bug-killer/references/typescript-debugging.md`** — TypeScript/JavaScript debugging reference covering Jest/Vitest flags, async/await pitfalls (missing await, unhandled rejections), TS/JS gotchas (`this` binding, closure scope, type narrowing, equality), stack trace analysis, console debugging patterns, Node.js inspector, and common error patterns table.

- **`claude/dev-tools/skills/bug-killer/references/general-debugging.md`** — Language-agnostic debugging reference covering systematic methods (binary search, git bisect, delta debugging, rubber duck, 5 Whys), stack trace reading, bug categories (off-by-one, null/undefined, race conditions, resource leaks, state corruption), diagnostic logging strategy, and investigation checklist.

### Modified

- **`CLAUDE.md`** — Four updates: (1) Repository structure description changed from "Feature dev, code review, docs, changelog" to include "debugging"; (2) Added bug-killer composition chains to Key Skill Composition Chains section; (3) Updated dev-tools row in Plugin Inventory to include bug-killer, project-learnings, and bug-investigator; (4) Added bug-killer to Critical Plugin Files table.

- **`claude/dev-tools/README.md`** — Four updates: (1) Added `/bug-killer` row to Skills table; (2) Added `project-learnings` and updated `code-quality` entries in Skills table; (3) Added `bug-investigator` row to Agents table; (4) Expanded Directory Structure with bug-killer, project-learnings, and bug-investigator entries.

## Git Status

### Unstaged Changes

| Status | File |
|--------|------|
| Modified | `CLAUDE.md` |
| Modified | `claude/dev-tools/README.md` |

### Untracked Files

| File |
|------|
| `claude/dev-tools/agents/bug-investigator.md` |
| `claude/dev-tools/skills/bug-killer/` |
| `claude/dev-tools/skills/project-learnings/` |

## Composition & Architecture Notes

### Agent Composition

| Agent | Model | Plugin | Spawned By | Access |
|-------|-------|--------|------------|--------|
| `bug-investigator` | Sonnet | dev-tools (same) | bug-killer Phase 3 | Read-only + Bash |
| `code-explorer` | Sonnet | core-tools (cross) | bug-killer Phase 2 | Read-only + Bash |

### Skill Composition

| Loaded Skill | Source Plugin | Loaded By | Phase |
|-------------|--------------|-----------|-------|
| `code-quality` | dev-tools (same) | bug-killer | Phase 4 (deep only) |
| `project-learnings` | dev-tools (same) | bug-killer | Phase 5 (both tracks) |
| `python-debugging.md` | dev-tools reference | bug-killer | Phase 2 (auto-detect) |
| `typescript-debugging.md` | dev-tools reference | bug-killer | Phase 2 (auto-detect) |
| `general-debugging.md` | dev-tools reference | bug-killer | Phase 2 (always) |

### Cross-Plugin References

- `subagent_type: "agent-alchemy-core-tools:code-explorer"` — uses fully-qualified marketplace name (correct for cross-plugin agent spawning)
- `subagent_type: "bug-investigator"` — uses short name (correct for same-plugin agent spawning)
- All `${CLAUDE_PLUGIN_ROOT}` references are same-plugin paths (no cross-plugin `/../` path references needed)
