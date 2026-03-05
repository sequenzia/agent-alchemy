"""Base protocol for source adapters."""

from __future__ import annotations

from typing import Protocol

from agent_tools.models import SkillContent, SkillInfo


class SourceAdapter(Protocol):
    """Protocol defining the interface all source adapters must implement.

    Source adapters are responsible for discovering and retrieving skills
    from a particular source type (local filesystem, git repo, registry, etc.).
    """

    def list_skills(self) -> list[SkillInfo]:
        """Enumerate all available skills from this source.

        Returns:
            A list of SkillInfo objects describing each discovered skill.
        """
        ...

    def get_skill(self, name: str) -> SkillContent:
        """Retrieve the full content of a skill by name.

        Args:
            name: The skill identifier to retrieve.

        Returns:
            A SkillContent object containing the skill's metadata and files.

        Raises:
            KeyError: If no skill with the given name exists in this source.
        """
        ...

    def search(self, query: str) -> list[SkillInfo]:
        """Search for skills matching a query string.

        The search checks skill names and descriptions for substring matches.

        Args:
            query: The search string to match against.

        Returns:
            A list of SkillInfo objects for matching skills.
        """
        ...
