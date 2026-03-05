# Contributing: Adding Harness Adapters

This guide explains how to add support for a new AI coding harness to `agent-tools`.

## Architecture Overview

Harness adapters implement a Protocol-based interface that maps abstract skill and agent names to concrete filesystem paths. The adapter system uses Python's `runtime_checkable` Protocol pattern -- no base class inheritance is required.

```
HarnessAdapter (Protocol)
  get_skill_path(skill_name) -> Path
  get_agent_path(agent_name) -> Path
  get_harness_name() -> str
  detect() -> bool
```

Existing adapters:

| Adapter | File | Skill Path | Detection |
|---------|------|------------|-----------|
| `ClaudeCodeAdapter` | `harnesses/claude_code.py` | `.claude/skills/<name>` | `.claude/` dir |
| `OpenCodeAdapter` | `harnesses/opencode.py` | `.opencode/skills/<name>` | `.opencode/` dir or `opencode.json` |
| `CursorWindsurfAdapter` | `harnesses/cursor.py` | `.cursor/rules/<name>` | `.cursor/` or `.windsurf/` dir |
| `CodexAdapter` | `harnesses/codex.py` | `.codex/skills/<name>` | `.codex/` dir, `codex.md`, or `AGENTS.md` |

## Step-by-Step: Adding a New Adapter

### 1. Create the Adapter Module

Create a new file in `src/agent_tools/harnesses/`. Follow the naming convention: lowercase with underscores.

```python
"""MyHarness adapter.

Describe where skills and agents are placed, and how
detection works for this harness.
"""

from __future__ import annotations

from pathlib import Path


class MyHarnessAdapter:
    """Harness adapter for MyHarness.

    Args:
        project_root: Workspace root directory. File paths are resolved
            relative to this directory.
    """

    def __init__(self, project_root: Path | None = None) -> None:
        self._root = project_root or Path.cwd()

    def get_skill_path(self, skill_name: str) -> Path:
        """Return the path where a skill should be placed."""
        return self._root / ".myharness" / "skills" / skill_name

    def get_agent_path(self, agent_name: str) -> Path:
        """Return the path where an agent should be placed."""
        return self._root / ".myharness" / "agents" / agent_name

    def get_harness_name(self) -> str:
        """Return a human-readable name."""
        return "MyHarness"

    def detect(self) -> bool:
        """Auto-detect whether this harness is active in the project."""
        return (self._root / ".myharness").is_dir()
```

### 2. Register the Adapter

Update `src/agent_tools/harnesses/__init__.py` to import your adapter and add it to the default registry factory:

```python
from agent_tools.harnesses.my_harness import MyHarnessAdapter

# In __all__:
__all__ = [
    # ... existing exports ...
    "MyHarnessAdapter",
]

# In create_default_registry():
def create_default_registry(project_root: Path | None = None) -> HarnessRegistry:
    root = project_root or Path.cwd()
    registry = HarnessRegistry()
    registry.register("claude-code", ClaudeCodeAdapter(project_root=root))
    registry.register("opencode", OpenCodeAdapter(project_root=root))
    registry.register("cursor", CursorWindsurfAdapter(project_root=root))
    registry.register("codex", CodexAdapter(project_root=root))
    registry.register("myharness", MyHarnessAdapter(project_root=root))  # Add here
    return registry
```

### 3. Add the Harness Name to Validation

Update the `VALID_HARNESSES` tuple in `src/agent_tools/config.py` so the harness name is accepted by `config set default_harness`:

```python
VALID_HARNESSES = ("claude-code", "opencode", "cursor", "codex", "myharness")
```

### 4. Write Tests

Create `tests/test_my_harness.py` following the existing test patterns in `tests/test_harness_adapters.py`:

```python
"""Tests for MyHarness adapter."""

from pathlib import Path

from agent_tools.harnesses.my_harness import MyHarnessAdapter


def test_get_skill_path(tmp_path: Path) -> None:
    adapter = MyHarnessAdapter(project_root=tmp_path)
    result = adapter.get_skill_path("deep-analysis")
    assert result == tmp_path / ".myharness" / "skills" / "deep-analysis"


def test_get_agent_path(tmp_path: Path) -> None:
    adapter = MyHarnessAdapter(project_root=tmp_path)
    result = adapter.get_agent_path("code-explorer")
    assert result == tmp_path / ".myharness" / "agents" / "code-explorer"


def test_get_harness_name(tmp_path: Path) -> None:
    adapter = MyHarnessAdapter(project_root=tmp_path)
    assert adapter.get_harness_name() == "MyHarness"


def test_detect_true(tmp_path: Path) -> None:
    (tmp_path / ".myharness").mkdir()
    adapter = MyHarnessAdapter(project_root=tmp_path)
    assert adapter.detect() is True


def test_detect_false(tmp_path: Path) -> None:
    adapter = MyHarnessAdapter(project_root=tmp_path)
    assert adapter.detect() is False


def test_protocol_compliance(tmp_path: Path) -> None:
    """Verify the adapter satisfies the HarnessAdapter protocol."""
    from agent_tools.harnesses.base import HarnessAdapter
    adapter = MyHarnessAdapter(project_root=tmp_path)
    assert isinstance(adapter, HarnessAdapter)
```

### 5. Run the Test Suite

```bash
cd agent-tools
pytest tests/ -v
ruff check src/ tests/
```

## The HarnessAdapter Protocol

The full protocol is defined in `src/agent_tools/harnesses/base.py`:

```python
@runtime_checkable
class HarnessAdapter(Protocol):
    def get_skill_path(self, skill_name: str) -> Path: ...
    def get_agent_path(self, agent_name: str) -> Path: ...
    def get_harness_name(self) -> str: ...
    def detect(self) -> bool: ...
```

Key points:

- **`get_skill_path`**: Returns the absolute path where a skill directory should be placed. The install command copies all skill files under this path.
- **`get_agent_path`**: Returns the absolute path for agent files. Follows the same pattern as skills.
- **`get_harness_name`**: Returns a human-readable display name (e.g., "Claude Code", not "claude-code"). Used in CLI output messages.
- **`detect`**: Returns `True` if the harness appears active in the current project. Typically checks for marker files or directories. Used by `HarnessRegistry.detect_all()`.

## The HarnessRegistry

The `HarnessRegistry` class maps string identifiers to adapter instances:

```python
registry = HarnessRegistry()
registry.register("myharness", MyHarnessAdapter(project_root=root))

# Retrieve by name
adapter = registry.get("myharness")

# List all registered names
names = registry.list_harnesses()  # -> ["claude-code", "codex", "cursor", ...]

# Auto-detect active harnesses in a project
detected = registry.detect_all()  # -> [("claude-code", adapter), ...]
```

Calling `registry.get("unknown")` raises `HarnessNotFoundError` with the list of available harnesses.

## Adding a Source Adapter

Source adapters follow a similar Protocol pattern. See `src/agent_tools/sources/base.py` for the `SourceAdapter` protocol, and `sources/local.py`, `sources/git.py`, `sources/registry.py` for implementations.

## Code Style

- Type hints on all functions and public APIs
- Docstrings on all public methods
- Format with `ruff` (line length 100, target Python 3.10)
- Test with `pytest`
- Use `from __future__ import annotations` for modern type syntax
