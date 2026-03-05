# Getting Started with agent-tools

This guide walks you through installing `agent-tools`, configuring skill sources, discovering skills, and installing your first skill into an AI coding harness.

## Prerequisites

- Python 3.10 or later
- [uv](https://docs.astral.sh/uv/) package manager (recommended)
- Git (required only for git repository sources)

## Step 1: Install agent-tools

```bash
# Install with uv
uv pip install agent-tools

# Verify the installation
agent-tools --help
```

You should see:

```
Usage: agent-tools [OPTIONS] COMMAND [ARGS]...

  Universal skill/subagent installer for AI coding harnesses.

Options:
  --help  Show this message and exit.

Commands:
  config   Manage sources and default harness configuration.
  install  Install skills and subagents into a target harness.
  list     List available skills across configured sources.
  search   Search for skills by name or keyword.
```

## Step 2: Set Your Default Harness

The default harness determines where skills are installed when you don't specify `--harness` explicitly. The default out of the box is `claude-code`.

Available harnesses:

| Harness | Identifier | Where skills are placed |
|---------|-----------|------------------------|
| Claude Code | `claude-code` | `.claude/skills/<name>/` |
| OpenCode | `opencode` | `.opencode/skills/<name>/` |
| Cursor/Windsurf | `cursor` | `.cursor/rules/<name>/` |
| Codex | `codex` | `.codex/skills/<name>/` |

To change the default:

```bash
agent-tools config set default_harness opencode
```

You can always override the default per-install with `--harness`:

```bash
agent-tools install my-skill --harness cursor
```

## Step 3: Add Skill Sources

Sources tell `agent-tools` where to find skills. There are three source types.

### Local Directory

Point to a directory on your filesystem that contains skills:

```bash
agent-tools config add-source local ~/my-skills
```

The directory should contain skill subdirectories, each with a manifest file (`SKILL.md`, `skill.md`, `manifest.json`, or `skill.json`):

```
~/my-skills/
  deep-analysis/
    SKILL.md
    references/
      patterns.md
  code-review/
    SKILL.md
```

### Git Repository

Add a remote git repository containing skills:

```bash
# HTTPS
agent-tools config add-source git https://github.com/org/shared-skills.git

# SSH
agent-tools config add-source git git@github.com:org/shared-skills.git
```

The repository is shallow-cloned locally and cached for 24 hours.

### Registry (Marketplace)

Add a registry API endpoint:

```bash
agent-tools config add-source registry https://registry.example.com/api/v1
```

The registry index is cached locally for 1 hour. When the registry is unreachable, the CLI falls back to the cached index for browsing.

### Verify Your Sources

```bash
agent-tools config list
```

Output:

```
default_harness = claude-code

sources:
  [local] /Users/me/my-skills
  [git] https://github.com/org/shared-skills.git
```

## Step 4: Discover Skills

### List All Skills

```bash
agent-tools list
```

This queries all configured sources and displays a table:

```
Name             Source          Description
---------------  ------------   --------------------------------------------------
deep-analysis    my-skills       Hub-and-spoke team engine for codebase exploration
feature-dev      my-skills       7-phase feature development lifecycle
git-commit       shared-skills   Git commit automation with conventional commits

3 skill(s) found.
```

### Filter by Source

```bash
agent-tools list --source ~/my-skills
```

### Search by Keyword

```bash
agent-tools search "code review"
```

The search matches against both skill names and descriptions (case-insensitive).

## Step 5: Install a Skill

```bash
agent-tools install deep-analysis
```

Output:

```
Installed 'deep-analysis' into Claude Code:
  SKILL.md -> /path/to/project/.claude/skills/deep-analysis/SKILL.md
  references/patterns.md -> /path/to/project/.claude/skills/deep-analysis/references/patterns.md
```

### Install into a Different Harness

```bash
agent-tools install deep-analysis --harness cursor
```

### Reinstall (Overwrite)

If the skill is already installed, use `--force`:

```bash
agent-tools install deep-analysis --force
```

## Configuration File

All settings are stored in `~/.config/agent-tools/config.toml`. You can edit this file directly if you prefer:

```toml
default_harness = "claude-code"

[[sources]]
type = "local"
path = "/Users/me/my-skills"

[[sources]]
type = "git"
path = "https://github.com/org/shared-skills.git"
```

## Next Steps

- Read the full [Command Reference](../README.md#command-reference) for all options and flags
- See the [Contributing Guide](contributing.md) to learn how to add support for new harnesses
- Check the [Skill Manifest Format](../README.md#skill-manifest-format) to make your own skills discoverable
