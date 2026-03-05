"""Data models for agent-tools skill discovery and retrieval."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SkillInfo:
    """Metadata about a discoverable skill or agent.

    Attributes:
        name: The skill's identifier (e.g. "deep-analysis").
        skill_type: Either "skill" or "agent".
        description: Human-readable summary of what the skill does.
        source: Where this skill was found (e.g. "local:/path/to/skills").
        path: Absolute filesystem path to the skill directory.
        compatible_harnesses: List of harness names this skill works with.
    """

    name: str
    description: str
    source: str
    path: str
    skill_type: str = "skill"
    compatible_harnesses: tuple[str, ...] = ()


@dataclass(frozen=True)
class SkillContent:
    """The retrieved content of a skill, including all relevant files.

    Attributes:
        info: Metadata about the skill.
        files: Mapping of relative file paths to their text content.
    """

    info: SkillInfo
    files: dict[str, str] = field(default_factory=dict)
