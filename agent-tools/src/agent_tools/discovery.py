"""Skill discovery: aggregation and formatting for list/search commands."""

from __future__ import annotations

import json
import logging
from typing import Any, TextIO

from agent_tools.config import Config, SourceEntry
from agent_tools.models import SkillInfo
from agent_tools.sources.local import LocalSourceAdapter

logger = logging.getLogger(__name__)

# Valid skill types for the --type filter.
VALID_SKILL_TYPES = ("skill", "agent")

# Maximum description width in the table output.
_MAX_DESC_WIDTH = 50


class SourceError:
    """Represents a source that failed during skill enumeration.

    Attributes:
        source: The source entry that failed.
        error: The error message.
    """

    def __init__(self, source: SourceEntry, error: str) -> None:
        self.source = source
        self.error = error


def _build_adapter(source: SourceEntry) -> LocalSourceAdapter | None:
    """Build a source adapter for a given source entry.

    Returns None if the source type is not supported.
    """
    if source.type == "local":
        return LocalSourceAdapter([source.path])
    logger.warning("Unsupported source type '%s', skipping: %s", source.type, source.path)
    return None


def aggregate_skills(
    config: Config,
    source_filter: str | None = None,
) -> tuple[list[SkillInfo], list[SourceError]]:
    """Collect skills from all configured sources.

    Args:
        config: The loaded user configuration.
        source_filter: If set, only query sources whose path matches this value.

    Returns:
        A tuple of (skills found, errors encountered).
    """
    skills: list[SkillInfo] = []
    errors: list[SourceError] = []

    sources = config.sources
    if source_filter is not None:
        sources = [s for s in sources if s.path == source_filter]

    for source in sources:
        adapter = _build_adapter(source)
        if adapter is None:
            errors.append(SourceError(source, f"Unsupported source type: {source.type}"))
            continue
        try:
            skills.extend(adapter.list_skills())
        except Exception as exc:
            errors.append(SourceError(source, str(exc)))
            logger.warning("Error querying source [%s] %s: %s", source.type, source.path, exc)

    return skills, errors


def search_skills(
    config: Config,
    query: str,
    source_filter: str | None = None,
) -> tuple[list[SkillInfo], list[SourceError]]:
    """Search for skills matching a query across configured sources.

    Args:
        config: The loaded user configuration.
        query: Substring to match against skill name and description.
        source_filter: If set, only query sources whose path matches this value.

    Returns:
        A tuple of (matching skills, errors encountered).
    """
    skills: list[SkillInfo] = []
    errors: list[SourceError] = []

    sources = config.sources
    if source_filter is not None:
        sources = [s for s in sources if s.path == source_filter]

    for source in sources:
        adapter = _build_adapter(source)
        if adapter is None:
            errors.append(SourceError(source, f"Unsupported source type: {source.type}"))
            continue
        try:
            skills.extend(adapter.search(query))
        except Exception as exc:
            errors.append(SourceError(source, str(exc)))
            logger.warning("Error querying source [%s] %s: %s", source.type, source.path, exc)

    return skills, errors


def _truncate(text: str, max_width: int) -> str:
    """Truncate a string to max_width, adding '...' if shortened."""
    if len(text) <= max_width:
        return text
    return text[: max_width - 3] + "..."


def _source_label(source: str) -> str:
    """Extract a short label from a source string like 'local:/long/path'.

    Returns the last path component for local sources.
    """
    if source.startswith("local:"):
        path_part = source[len("local:"):]
        # Use the last path component
        parts = path_part.rstrip("/").rsplit("/", 1)
        return parts[-1] if parts else path_part
    return source


def format_skills_table(
    skills: list[SkillInfo],
    file: TextIO | None = None,
) -> str:
    """Format skills as a readable table.

    Args:
        skills: The skills to display.
        file: Unused; kept for API compatibility.

    Returns:
        The formatted table as a string.
    """
    if not skills:
        return ""

    # Compute column widths
    name_width = max(len(s.name) for s in skills)
    name_width = max(name_width, 4)  # minimum "Name" header

    source_labels = [_source_label(s.source) for s in skills]
    source_width = max(len(lbl) for lbl in source_labels)
    source_width = max(source_width, 6)  # minimum "Source" header

    desc_width = _MAX_DESC_WIDTH

    # Header
    lines = [
        f"{'Name':<{name_width}}  {'Source':<{source_width}}  {'Description'}",
        f"{'-' * name_width}  {'-' * source_width}  {'-' * desc_width}",
    ]

    # Rows
    for skill, src_label in zip(skills, source_labels):
        desc = _truncate(skill.description, desc_width)
        lines.append(f"{skill.name:<{name_width}}  {src_label:<{source_width}}  {desc}")

    return "\n".join(lines)


def get_valid_source_paths(config: Config) -> list[str]:
    """Return the list of configured source paths.

    Args:
        config: The loaded user configuration.

    Returns:
        List of source path strings.
    """
    return [s.path for s in config.sources]


def filter_skills(
    skills: list[SkillInfo],
    *,
    skill_type: str | None = None,
    harness: str | None = None,
) -> list[SkillInfo]:
    """Filter a list of skills by type and/or harness compatibility.

    Args:
        skills: The skills to filter.
        skill_type: If set, only include skills matching this type ("skill" or "agent").
        harness: If set, only include skills compatible with this harness name.

    Returns:
        Filtered list of skills.
    """
    result = skills
    if skill_type is not None:
        result = [s for s in result if s.skill_type == skill_type]
    if harness is not None:
        result = [
            s for s in result
            if not s.compatible_harnesses or harness in s.compatible_harnesses
        ]
    return result


def _skill_to_dict(skill: SkillInfo) -> dict[str, Any]:
    """Convert a SkillInfo to a plain dictionary for serialization."""
    return {
        "name": skill.name,
        "type": skill.skill_type,
        "description": skill.description,
        "source": skill.source,
        "path": skill.path,
        "compatible_harnesses": list(skill.compatible_harnesses),
    }


def format_skills_json(skills: list[SkillInfo]) -> str:
    """Format skills as a JSON array string.

    Args:
        skills: The skills to format.

    Returns:
        JSON string with pretty-printed skill data.
    """
    data = [_skill_to_dict(s) for s in skills]
    return json.dumps(data, indent=2)


def format_skills_yaml(skills: list[SkillInfo]) -> str:
    """Format skills as YAML string (no external dependency).

    Args:
        skills: The skills to format.

    Returns:
        YAML-formatted string with skill data.
    """
    lines: list[str] = []
    for skill in skills:
        lines.append(f"- name: {skill.name}")
        lines.append(f"  type: {skill.skill_type}")
        lines.append(f"  description: {skill.description}")
        lines.append(f"  source: {skill.source}")
        lines.append(f"  path: {skill.path}")
        harnesses = ", ".join(skill.compatible_harnesses) if skill.compatible_harnesses else "all"
        lines.append(f"  compatible_harnesses: {harnesses}")
    return "\n".join(lines)


def format_skills_rich_table(skills: list[SkillInfo]) -> str:
    """Format skills as a rich aligned table with type column.

    Args:
        skills: The skills to display.

    Returns:
        The formatted table as a string.
    """
    if not skills:
        return ""

    # Compute column widths
    name_width = max(len(s.name) for s in skills)
    name_width = max(name_width, 4)  # minimum "Name" header

    type_width = max(len(s.skill_type) for s in skills)
    type_width = max(type_width, 4)  # minimum "Type" header

    source_labels = [_source_label(s.source) for s in skills]
    source_width = max(len(lbl) for lbl in source_labels)
    source_width = max(source_width, 6)  # minimum "Source" header

    desc_width = _MAX_DESC_WIDTH

    # Header
    lines = [
        (
            f"{'Name':<{name_width}}  {'Type':<{type_width}}  "
            f"{'Source':<{source_width}}  {'Description'}"
        ),
        (
            f"{'-' * name_width}  {'-' * type_width}  "
            f"{'-' * source_width}  {'-' * desc_width}"
        ),
    ]

    # Rows
    for skill, src_label in zip(skills, source_labels):
        desc = _truncate(skill.description, desc_width)
        lines.append(
            f"{skill.name:<{name_width}}  {skill.skill_type:<{type_width}}  "
            f"{src_label:<{source_width}}  {desc}"
        )

    return "\n".join(lines)


def format_skill_info(skill: SkillInfo) -> str:
    """Format a single skill's full metadata for the 'info' subcommand.

    Args:
        skill: The skill to display.

    Returns:
        A multi-line string with full metadata.
    """
    harnesses = ", ".join(skill.compatible_harnesses) if skill.compatible_harnesses else "all"
    lines = [
        f"Name:        {skill.name}",
        f"Type:        {skill.skill_type}",
        f"Description: {skill.description}",
        f"Source:      {skill.source}",
        f"Path:        {skill.path}",
        f"Harnesses:   {harnesses}",
    ]
    return "\n".join(lines)


def find_skill_by_name(
    config: Config,
    name: str,
    source_filter: str | None = None,
) -> SkillInfo | None:
    """Find a single skill by exact name across configured sources.

    Args:
        config: The loaded user configuration.
        name: Exact skill name to look up.
        source_filter: If set, only query sources whose path matches this value.

    Returns:
        The matching SkillInfo, or None if not found.
    """
    skills, _ = aggregate_skills(config, source_filter=source_filter)
    for skill in skills:
        if skill.name == name:
            return skill
    return None


# Valid output formats for the --format flag.
VALID_FORMATS = ("table", "json", "yaml")
