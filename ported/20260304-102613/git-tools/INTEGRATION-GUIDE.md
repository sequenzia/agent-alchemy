# Integration Guide: git-tools

## Overview

The git-tools package provides a single skill for automated git commit creation with conventional commit message formatting. It analyzes staged changes and generates appropriate commit messages following the Conventional Commits specification.

## Component Inventory

| Component | Type | Origin | Description |
|-----------|------|--------|-------------|
| git-commit | skill | skill | Automated conventional commit message generation from staged changes |

## Capability Requirements

### Shell execution
- **git-commit**: Runs git commands (status, add, diff, commit). All commands are standard git operations.

### User interaction
- **git-commit**: May prompt for commit message confirmation (optional).

## Per-Component Notes

### git-commit
A straightforward 6-step workflow: check repo state → stage changes → analyze diff → construct message → create commit → handle result. Originally ran on a lightweight (Haiku) model — suitable for fast, simple model tiers. Pre-commit hook failure handling is documented.

## Flatten Mode Notes

This package was converted in flatten mode. It contains only one original skill — no agents or hooks were converted.

## Adaptation Checklist
- [ ] Ensure your harness can execute git shell commands
- [ ] Adapt the conventional commit format if your project uses a different convention
- [ ] Test with both clean and dirty working directories
