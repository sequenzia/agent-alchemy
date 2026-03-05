# Integration Guide: git-tools

## Overview

The git-tools package provides a single skill for creating git commits with conventional commit messages. It analyzes staged changes and generates appropriate commit messages following the Conventional Commits specification.

## Component Inventory

| Component | Type | Origin | Parent Skill | Description |
|-----------|------|--------|-------------|-------------|
| git-commit | skill | skill | — | Commit staged changes with conventional commit message |

## Capability Requirements

- **Shell command execution**: Required for all git operations (status, add, diff, commit)

## Per-Component Notes

### git-commit
A highly portable skill that primarily executes git commands. The conventional commit format (`type(scope): description`) is a widely-adopted standard. The skill stages all changes, analyzes the diff, constructs a commit message, and handles pre-commit hook failures gracefully.

Originally ran on a lightweight model — suitable for any model tier.

## Nested Mode Notes

This package was converted in nested mode. It contains no agents or hooks, so the nested structure is straightforward — just one skill directory.

### Orphan Agents
No agents in this package.

### Lifecycle Hooks Skill
No hooks in this package.

## Dependency Map

```
git-commit (standalone, no dependencies)
```

## Adaptation Checklist

- [ ] Review the skill instructions and adapt any remaining tool-specific language for your harness
- [ ] Ensure the harness can execute shell commands (git operations)
- [ ] Test with a simple commit to verify the conventional commit format works as expected
