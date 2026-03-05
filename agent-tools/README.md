# agent-tools

A universal skill and subagent installer for AI coding harnesses. Discover skills across multiple sources and install them into any supported harness with automatic file placement.

## Supported Harnesses

| Harness | Identifier | Skill Path | Detection |
|---------|-----------|------------|-----------|
| Claude Code | `claude-code` | `.claude/skills/<name>` | `.claude/` directory |
| OpenCode | `opencode` | `.opencode/skills/<name>` | `.opencode/` dir or `opencode.json` |
| Cursor/Windsurf | `cursor` | `.cursor/rules/<name>` | `.cursor/` or `.windsurf/` directory |
| Codex | `codex` | `.codex/skills/<name>` | `.codex/` dir, `codex.md`, or `AGENTS.md` |

## Installation

Requires Python 3.10 or later.

```bash
# Install with uv (recommended)
uv pip install agent-tools

# Or install from source
git clone https://github.com/your-org/agent-alchemy.git
cd agent-alchemy/agent-tools
uv pip install -e .
```

### Development Setup

```bash
cd agent-tools
uv pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check src/ tests/
```

## Quick Start

```bash
# 1. Add a local skill source
agent-tools config add-source local ~/my-skills

# 2. Set your default harness
agent-tools config set default_harness claude-code

# 3. Browse available skills
agent-tools list

# 4. Search for a skill
agent-tools search "analysis"

# 5. Install a skill
agent-tools install deep-analysis
```

## Command Reference

### `config` -- Manage sources and default harness

#### `config list`

Show all current configuration.

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

#### `config get <key>`

Retrieve a configuration value.

```bash
# Get the default harness
agent-tools config get default_harness

# List all configured sources
agent-tools config get sources
```

Valid keys: `default_harness`, `sources`.

#### `config set <key> <value>`

Set a configuration value.

```bash
agent-tools config set default_harness opencode
```

Valid keys: `default_harness`.
Valid harness values: `claude-code`, `opencode`, `cursor`, `codex`.

#### `config add-source <type> <path>`

Add a skill source.

```bash
# Add a local directory
agent-tools config add-source local ~/my-skills

# Add a git repository
agent-tools config add-source git https://github.com/org/shared-skills.git

# Add a registry
agent-tools config add-source registry https://registry.example.com/api/v1
```

Source types: `local`, `git`, `registry`.

Duplicate sources (same type and path) are silently ignored. A warning is printed if a local path does not exist, but the source is still saved.

#### `config remove-source <path>`

Remove a skill source by its path.

```bash
agent-tools config remove-source ~/my-skills
```

### `list` -- List available skills

List all skills across configured sources.

```bash
# List all skills
agent-tools list

# Filter to a specific source
agent-tools list --source ~/my-skills
```

**Options:**

| Option | Short | Description |
|--------|-------|-------------|
| `--source <path>` | `-s` | Filter results to a specific configured source path |

Output is a formatted table with columns: Name, Source, Description.

```
Name             Source       Description
---------------  ----------   --------------------------------------------------
deep-analysis    my-skills    Hub-and-spoke team engine for codebase exploration
feature-dev      my-skills    7-phase feature development lifecycle
git-commit       git-tools    Git commit automation with conventional commits

3 skill(s) found.
```

If no sources are configured, the command prints a hint to add one:

```
No sources configured. Run 'agent-tools config add-source' to add one.
```

### `search` -- Search for skills

Search for skills by name or keyword across all configured sources.

```bash
# Search by keyword
agent-tools search analysis

# Search with source filter
agent-tools search "code review" --source ~/my-skills
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `<query>` | Yes | Substring to match against skill names and descriptions |

**Options:**

| Option | Short | Description |
|--------|-------|-------------|
| `--source <path>` | `-s` | Filter results to a specific configured source path |

The search is case-insensitive and matches against both skill names and descriptions.

### `install` -- Install a skill

Install a skill into a target harness with automatic file placement.

```bash
# Install using default harness
agent-tools install deep-analysis

# Install into a specific harness
agent-tools install deep-analysis --harness opencode

# Overwrite an existing installation
agent-tools install deep-analysis --force
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `<skill-name>` | Yes | Name of the skill to install |

**Options:**

| Option | Description |
|--------|-------------|
| `--harness <name>` | Target harness (overrides the configured default) |
| `--force` | Overwrite if the skill is already installed |
| `--source <path>` | Specific source to search (reserved for future use) |

On success, the command shows which files were installed and where:

```
Installed 'deep-analysis' into Claude Code:
  SKILL.md -> /path/to/project/.claude/skills/deep-analysis/SKILL.md
  references/patterns.md -> /path/to/project/.claude/skills/deep-analysis/references/patterns.md
```

If the skill is already installed, the command exits with an error unless `--force` is used:

```
Skill 'deep-analysis' is already installed in Claude Code.
Use --force to overwrite.
```

## Configuration

Configuration is stored in TOML format at `~/.config/agent-tools/config.toml`. The file is created automatically on first use with sensible defaults.

```toml
default_harness = "claude-code"

[[sources]]
type = "local"
path = "/Users/me/my-skills"

[[sources]]
type = "git"
path = "https://github.com/org/shared-skills.git"

[[sources]]
type = "registry"
path = "https://registry.example.com/api/v1"
```

### Source Types

**Local** (`local`): A directory on the local filesystem. Each subdirectory containing a recognized skill manifest is treated as a skill. The manifest is discovered by looking for these files in priority order: `SKILL.md`, `skill.md`, `manifest.json`, `skill.json`.

**Git** (`git`): A remote git repository (HTTPS or SSH URL). The repository is shallow-cloned into `~/.cache/agent-tools/repos/` and refreshed when the cache expires (default: 24 hours). Supports both HTTPS (`https://github.com/org/repo.git`) and SSH (`git@github.com:org/repo.git`) URLs.

**Registry** (`registry`): A remote registry API endpoint. The adapter communicates via REST endpoints (`GET /skills`, `GET /skills/search?q=...`, `GET /skills/<name>/download`). Responses are cached locally at `~/.cache/agent-tools/registry/` with a 1-hour TTL. Falls back to the stale cache when the registry is unreachable.

## Skill Manifest Format

For a skill to be discoverable, its directory must contain a manifest file. The recommended format is `SKILL.md` with YAML frontmatter:

```markdown
---
name: my-skill
description: A brief summary of what this skill does
version: 1.0.0
---

# My Skill

Detailed instructions for the AI coding assistant...
```

Alternatively, a `manifest.json` or `skill.json` file can be used:

```json
{
  "name": "my-skill",
  "description": "A brief summary of what this skill does",
  "version": "1.0.0"
}
```

### Directory Structure

Skills are discovered using either a flat or nested layout:

**Flat layout** -- the manifest is directly inside the source directory (treated as a single skill):

```
my-skills/
  SKILL.md
  references/
    patterns.md
```

**Nested layout** -- each subdirectory is a separate skill:

```
my-skills/
  deep-analysis/
    SKILL.md
    references/
      patterns.md
  feature-dev/
    SKILL.md
```

## Troubleshooting

### "No sources configured"

You need to add at least one skill source before listing, searching, or installing:

```bash
agent-tools config add-source local ~/my-skills
```

### "Invalid harness" error

The harness name must be one of: `claude-code`, `opencode`, `cursor`, `codex`.

```bash
# Check your current default
agent-tools config get default_harness

# Fix it
agent-tools config set default_harness claude-code
```

### "Skill not found" error

The skill name was not found in any configured source. Verify your sources are correct:

```bash
# Check configured sources
agent-tools config get sources

# List all available skills to see what's discoverable
agent-tools list
```

### Git source authentication failures

If a git source fails with an authentication error:

- **SSH**: Ensure your SSH key is loaded (`ssh-add ~/.ssh/id_ed25519`) and the remote host is in `~/.ssh/config`.
- **HTTPS**: Run `git credential approve` or configure a personal access token.

### Git source cache is stale

Git repositories are cached at `~/.cache/agent-tools/repos/` with a 24-hour TTL. To force a refresh, delete the cached clone:

```bash
rm -rf ~/.cache/agent-tools/repos/github.com_org_repo
```

### Registry unreachable

When the registry is unreachable, the CLI falls back to the locally cached index. If no cache exists, results will be empty. Check your network connection and verify the registry URL:

```bash
agent-tools config get sources
```

### Permission denied writing skill files

The destination directory for the harness must be writable. Check file permissions on the project's harness directory (e.g., `.claude/skills/`).

### Python version error

`agent-tools` requires Python 3.10 or later. Check your version:

```bash
python --version
```

## License

See the repository root for license information.
