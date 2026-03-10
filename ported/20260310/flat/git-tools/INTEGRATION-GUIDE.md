# Integration Guide: git-tools

## Overview
This package provides git workflow automation — specifically, a skill for creating conventional commits with automatically generated commit messages based on staged changes analysis.

## Component Inventory
| Component | Type | Origin | Description |
|-----------|------|--------|-------------|
| git-commit | skill | skill | Commit staged changes with conventional commit message |

## Capability Requirements

- **Shell execution**: `git-commit` runs git commands via shell

## Per-Component Notes

### git-commit
Automates the git commit workflow: stages all changes, analyzes the diff, generates a conventional commit message, and creates the commit. Handles pre-commit hook failures gracefully. Originally ran on a lightweight model since the logic is straightforward.

## Adaptation Checklist
- [ ] Review the skill instructions and adapt tool-specific language for your harness
- [ ] Ensure shell command execution is available for git operations
- [ ] Test with a sample repository to verify commit message generation
