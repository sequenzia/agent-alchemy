"""Claude Code harness adapter.

Places skills in ``.claude/skills/`` and agents in ``.claude/agents/``
relative to the project root.  Detection checks for a ``.claude/`` directory.
"""

from __future__ import annotations

from pathlib import Path


class ClaudeCodeAdapter:
    """Harness adapter for Claude Code.

    Args:
        project_root: Workspace root directory.  File paths are resolved
            relative to this directory.
    """

    def __init__(self, project_root: Path | None = None) -> None:
        self._root = project_root or Path.cwd()

    def get_skill_path(self, skill_name: str) -> Path:
        """Return ``<root>/.claude/skills/<skill_name>``."""
        return self._root / ".claude" / "skills" / skill_name

    def get_agent_path(self, agent_name: str) -> Path:
        """Return ``<root>/.claude/agents/<agent_name>``."""
        return self._root / ".claude" / "agents" / agent_name

    def get_harness_name(self) -> str:
        return "Claude Code"

    def detect(self) -> bool:
        """Detect by checking for a ``.claude/`` directory in the project root."""
        return (self._root / ".claude").is_dir()
