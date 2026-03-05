"""Cursor / Windsurf harness adapter.

Cursor and Windsurf share similar conventions, using a ``.cursor/rules/``
directory for rule files.  Skills are placed as rule files and agents as
agent configuration files under ``.cursor/``.

Detection checks for a ``.cursor/`` or ``.windsurf/`` directory.
"""

from __future__ import annotations

from pathlib import Path


class CursorWindsurfAdapter:
    """Harness adapter for Cursor and Windsurf.

    Args:
        project_root: Workspace root directory.  File paths are resolved
            relative to this directory.
    """

    def __init__(self, project_root: Path | None = None) -> None:
        self._root = project_root or Path.cwd()

    def get_skill_path(self, skill_name: str) -> Path:
        """Return ``<root>/.cursor/rules/<skill_name>``."""
        return self._root / ".cursor" / "rules" / skill_name

    def get_agent_path(self, agent_name: str) -> Path:
        """Return ``<root>/.cursor/agents/<agent_name>``."""
        return self._root / ".cursor" / "agents" / agent_name

    def get_harness_name(self) -> str:
        return "Cursor/Windsurf"

    def detect(self) -> bool:
        """Detect by checking for ``.cursor/`` or ``.windsurf/`` directory."""
        return (
            (self._root / ".cursor").is_dir()
            or (self._root / ".windsurf").is_dir()
        )
