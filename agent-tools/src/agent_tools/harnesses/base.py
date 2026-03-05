"""Base protocol for harness adapters.

A harness adapter encapsulates the file-placement conventions for a specific
AI coding harness (Claude Code, OpenCode, Cursor/Windsurf, Codex, etc.).
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class HarnessAdapter(Protocol):
    """Protocol defining the interface all harness adapters must implement.

    Harness adapters translate abstract skill/agent names into concrete
    filesystem paths where the harness expects those files to reside.

    Implementations should be stateless where possible.  Any project-specific
    state (e.g. workspace root) is typically passed at construction time.
    """

    def get_skill_path(self, skill_name: str) -> Path:
        """Return the filesystem path where *skill_name* should be placed.

        Args:
            skill_name: Identifier of the skill (e.g. ``"deep-analysis"``).

        Returns:
            Absolute or project-relative ``Path`` for the skill file.
        """
        ...

    def get_agent_path(self, agent_name: str) -> Path:
        """Return the filesystem path where *agent_name* should be placed.

        Args:
            agent_name: Identifier of the agent (e.g. ``"code-explorer"``).

        Returns:
            Absolute or project-relative ``Path`` for the agent file.
        """
        ...

    def get_harness_name(self) -> str:
        """Return a human-readable name for this harness.

        Examples: ``"Claude Code"``, ``"OpenCode"``, ``"Cursor/Windsurf"``.
        """
        ...

    def detect(self) -> bool:
        """Auto-detect whether this harness is active in the current project.

        Detection typically checks for harness-specific marker files or
        directories (e.g. ``.claude/`` for Claude Code).

        Returns:
            ``True`` if the harness appears to be in use, ``False`` otherwise.
        """
        ...
