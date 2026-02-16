# Agent Alchemy Git Tools

Git workflow automation with Conventional Commits support.

## Skills

| Skill | Invocable | Description |
|-------|-----------|-------------|
| `/git-commit` | Yes | Automates git commits following Conventional Commits format (`type(scope): description`). Analyzes staged changes, drafts commit messages, and handles the commit workflow. |

## Conventional Commits Format

```
type(scope): description

Types: feat, fix, docs, style, refactor, test, chore, build
Example: feat(auth): add OAuth2 login flow
```

## Directory Structure

```
git-tools/
├── skills/
│   └── git-commit/
│       └── SKILL.md            # Commit workflow
└── README.md
```
