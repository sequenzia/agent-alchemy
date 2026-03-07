# Codebase Changes Report

## Metadata

| Field | Value |
|-------|-------|
| **Date** | 2026-03-07 |
| **Time** | 00:40 EST |
| **Branch** | main |
| **Author** | Stephen Sequenzia |
| **Base Commit** | `f02b4e9` |
| **Latest Commit** | uncommitted |
| **Repository** | git@github.com:sequenzia/agent-alchemy.git |

**Scope**: Fix cross-plugin dependency resolution in Claude Code plugin cache

**Summary**: Added SessionStart hooks to 4 plugins that create short-name symlinks in the cache directory, fixing broken `${CLAUDE_PLUGIN_ROOT}/../{short-name}/` cross-plugin references. Also fixed a same-plugin self-reference in claude-tools and bumped versions for all affected plugins.

## Overview

Cross-plugin references using `${CLAUDE_PLUGIN_ROOT}/../{short-name}/` worked in the local monorepo but broke in Claude Code's plugin cache due to the extra version subdirectory and org-prefixed directory names. The fix adds a SessionStart hook to each affected plugin that creates compatibility symlinks, bridging the gap transparently without changing any skill or agent content.

- **Files affected**: 10
- **Lines added**: +298
- **Lines removed**: -7

## Files Changed

| File | Status | Lines | Description |
|------|--------|-------|-------------|
| `claude/sdd-tools/hooks/resolve-cross-plugins.sh` | Added | +68 | Symlink resolution script for cache environments |
| `claude/dev-tools/hooks/resolve-cross-plugins.sh` | Added | +68 | Symlink resolution script for cache environments |
| `claude/tdd-tools/hooks/resolve-cross-plugins.sh` | Added | +68 | Symlink resolution script for cache environments |
| `claude/plugin-tools/hooks/resolve-cross-plugins.sh` | Added | +68 | Symlink resolution script for cache environments |
| `claude/dev-tools/hooks/hooks.json` | Added | +13 | New hooks config with SessionStart hook |
| `claude/plugin-tools/hooks/hooks.json` | Added | +13 | New hooks config with SessionStart hook |
| `claude/sdd-tools/hooks/hooks.json` | Modified | +11 | Added SessionStart hook entry |
| `claude/tdd-tools/hooks/hooks.json` | Modified | +11 | Added SessionStart hook entry |
| `claude/claude-tools/skills/claude-code-teams/SKILL.md` | Modified | +1 / -1 | Fixed self-reference to use same-plugin path |
| `.claude-plugin/marketplace.json` | Modified | +5 / -5 | Bumped versions for 5 affected plugins |

## Change Details

### Added

- **`claude/{sdd,dev,tdd,plugin}-tools/hooks/resolve-cross-plugins.sh`** — SessionStart hook script that detects when running from the plugin cache, iterates over sibling plugins in the same org directory, strips the org prefix to derive short names, looks up the installed version from `~/.claude/plugins/installed_plugins.json` (falling back to `sort -V`), and creates symlinks at the plugin-name directory level. Uses `trap 'exit 0' ERR` to never block session start, supports debug logging via `AGENT_ALCHEMY_HOOK_DEBUG=1`.

- **`claude/dev-tools/hooks/hooks.json`** — New hooks configuration with a single SessionStart hook that invokes the resolve script.

- **`claude/plugin-tools/hooks/hooks.json`** — New hooks configuration with a single SessionStart hook that invokes the resolve script.

### Modified

- **`claude/sdd-tools/hooks/hooks.json`** — Added `SessionStart` event entry alongside existing `PreToolUse`, `TaskCompleted`, and `TeammateIdle` hooks.

- **`claude/tdd-tools/hooks/hooks.json`** — Added `SessionStart` event entry alongside existing `PreToolUse` hook.

- **`claude/claude-tools/skills/claude-code-teams/SKILL.md`** — Fixed line 15 self-reference from `${CLAUDE_PLUGIN_ROOT}/../claude-tools/skills/claude-code-tasks/SKILL.md` to `${CLAUDE_PLUGIN_ROOT}/skills/claude-code-tasks/SKILL.md` since both skills are in the same plugin.

- **`.claude-plugin/marketplace.json`** — Bumped patch versions: claude-tools 0.2.3→0.2.4, dev-tools 0.3.3→0.3.4, sdd-tools 0.2.8→0.2.9, tdd-tools 0.2.0→0.2.1, plugin-tools 0.2.5→0.2.6.

## Git Status

### Unstaged Changes

| File | Status |
|------|--------|
| `.claude-plugin/marketplace.json` | Modified |
| `claude/claude-tools/skills/claude-code-teams/SKILL.md` | Modified |
| `claude/sdd-tools/hooks/hooks.json` | Modified |
| `claude/tdd-tools/hooks/hooks.json` | Modified |

### Untracked Files

| File |
|------|
| `claude/dev-tools/hooks/` |
| `claude/plugin-tools/hooks/` |
| `claude/sdd-tools/hooks/resolve-cross-plugins.sh` |
| `claude/tdd-tools/hooks/resolve-cross-plugins.sh` |

## Session Commits

No commits in this session. All changes are uncommitted.
