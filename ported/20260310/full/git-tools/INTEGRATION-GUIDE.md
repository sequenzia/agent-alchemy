# Integration Guide: git-tools

## Overview

The git-tools package provides a single skill for automated git commit creation with conventional commit message formatting. It is self-contained with no dependencies on other packages.

## Component Inventory

| Component | Type | Description |
|-----------|------|-------------|
| git-commit | Skill | Stages all changes, analyzes diffs, generates conventional commit messages |

## Capability Requirements

- **Shell execution**: Run git commands (status, add, diff, commit). This is the primary capability needed.
- **User interaction**: Confirm or customize commit messages when needed.

## Per-Component Notes

### git-commit

**What it does:** Automates the git commit workflow: checks for changes, stages all files, analyzes the diff, constructs a conventional commit message, and creates the commit.

**Capabilities needed:** Shell execution (git CLI), user interaction.

**Adaptation guidance:**
- Requires the `git` CLI to be available in the execution environment.
- The skill uses heredoc syntax for commit messages — ensure your shell supports this.
- Pre-commit hook failures are handled gracefully with instructions to create a new commit (never amend).
- No agent delegation needed — this is a simple sequential workflow.

## Dependency Map

No dependencies. git-commit is a standalone skill.

## Adaptation Checklist

- [ ] Ensure git CLI is available in the agent's execution environment
- [ ] Map shell execution to your harness's command running mechanism
- [ ] Map user interaction to your harness's input prompting mechanism
- [ ] Test with a simple change to verify the full stage → analyze → commit workflow
