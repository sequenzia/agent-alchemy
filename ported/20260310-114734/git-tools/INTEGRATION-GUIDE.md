# git-tools Integration Guide

## Overview

git-tools contains a single skill for automating git commits with conventional commit messages. It is a self-contained workflow with no internal or external dependencies.

## Skill Summary

| Skill | Purpose |
|-------|---------|
| git-commit | Stages all changes, analyzes the diff, generates a conventional commit message, creates the commit, and handles pre-commit hook failures |

## Capability Requirements

| Capability | Required | Used By |
|------------|----------|---------|
| Shell command execution | Yes | All steps (git status, add, diff, commit) |
| Text analysis | Yes | Step 3-4 (diff interpretation, message generation) |

## Adaptation Checklist

- [ ] Verify the agent runtime can execute shell commands (specifically `git`)
- [ ] Confirm the working directory is a git repository when the skill is invoked
- [ ] Map `git` CLI commands to platform-native git APIs if shell access is restricted
- [ ] Validate that conventional commit format aligns with project conventions (types, scopes)
- [ ] Test pre-commit hook failure path to ensure the agent does not amend previous commits

## Notes

- The skill stages **all** changes (`git add .`) by default. If selective staging is needed, modify Step 2.
- No user interaction is required during execution; the skill runs autonomously from analysis through commit.
- The heredoc pattern in Step 5 ensures multi-line commit messages are formatted correctly in bash. Adapt if the target shell differs.
