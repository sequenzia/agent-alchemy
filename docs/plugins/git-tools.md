# Git Tools

**Version:** 0.1.0 | **Skills:** 1 | **Agents:** 0

Git Tools provides lightweight git automation — currently a single skill for conventional commit message generation.

## Skills

### `/git-commit` — Conventional Commit Automation

Analyzes staged changes and generates a [Conventional Commits](https://www.conventionalcommits.org/) message. Runs on the **Haiku** model for fast, low-cost execution.

```bash
/git-commit           # Analyze staged changes and commit
```

**Workflow:**

1. **Check Repository State** — Runs `git status --porcelain`. If clean, reports nothing to commit.
2. **Stage Changes** — Stages all modified and untracked files (`git add -A`).
3. **Analyze Diff** — Reads the staged diff to understand what changed.
4. **Generate Message** — Creates a conventional commit message following the format:

    ```
    type(scope): description
    ```

    Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

5. **User Confirmation** — Presents the message for approval via `AskUserQuestion`.
6. **Commit** — Executes `git commit` with the approved message.

!!! tip "Model Choice"
    Git-commit uses Haiku intentionally — commit message generation is a quick, focused task that doesn't need the reasoning power of Sonnet or Opus. This keeps the operation fast and cost-effective.
