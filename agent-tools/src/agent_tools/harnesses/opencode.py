"""OpenCode harness adapter.

OpenCode uses an ``.opencode/`` directory at the project root for
configuration and instructions.  Skills map to instruction files and
agents map to agent configuration files within that directory.

Detection checks for an ``.opencode/`` directory or ``opencode.json``
configuration file.
"""

from __future__ import annotations

from pathlib import Path


class OpenCodeAdapter:
    """Harness adapter for OpenCode.

    Args:
        project_root: Workspace root directory.  File paths are resolved
            relative to this directory.
    """

    def __init__(self, project_root: Path | None = None) -> None:
        self._root = project_root or Path.cwd()

    def get_skill_path(self, skill_name: str) -> Path:
        """Return ``<root>/.opencode/skills/<skill_name>``."""
        return self._root / ".opencode" / "skills" / skill_name

    def get_agent_path(self, agent_name: str) -> Path:
        """Return ``<root>/.opencode/agents/<agent_name>``."""
        return self._root / ".opencode" / "agents" / agent_name

    def get_harness_name(self) -> str:
        return "OpenCode"

    def detect(self) -> bool:
        """Detect by checking for ``.opencode/`` dir or ``opencode.json``."""
        return (
            (self._root / ".opencode").is_dir()
            or (self._root / "opencode.json").is_file()
        )
