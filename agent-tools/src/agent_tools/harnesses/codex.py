"""Codex (OpenAI) harness adapter.

Codex uses a ``codex.md`` or ``AGENTS.md`` file at the project root for
instructions, and an ``.codex/`` directory for additional configuration.
Skills are placed under ``.codex/skills/`` and agents under ``.codex/agents/``.

Detection checks for ``codex.md``, ``AGENTS.md``, or a ``.codex/`` directory.
"""

from __future__ import annotations

from pathlib import Path


class CodexAdapter:
    """Harness adapter for OpenAI Codex.

    Args:
        project_root: Workspace root directory.  File paths are resolved
            relative to this directory.
    """

    def __init__(self, project_root: Path | None = None) -> None:
        self._root = project_root or Path.cwd()

    def get_skill_path(self, skill_name: str) -> Path:
        """Return ``<root>/.codex/skills/<skill_name>``."""
        return self._root / ".codex" / "skills" / skill_name

    def get_agent_path(self, agent_name: str) -> Path:
        """Return ``<root>/.codex/agents/<agent_name>``."""
        return self._root / ".codex" / "agents" / agent_name

    def get_harness_name(self) -> str:
        return "Codex"

    def detect(self) -> bool:
        """Detect by checking for ``codex.md``, ``AGENTS.md``, or ``.codex/``."""
        return (
            (self._root / ".codex").is_dir()
            or (self._root / "codex.md").is_file()
            or (self._root / "AGENTS.md").is_file()
        )
