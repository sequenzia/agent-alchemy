"""Install command logic for agent-tools.

Resolves skills from configured sources, routes them through the harness
adapter, and copies files to the correct harness-specific location.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from agent_tools.config import Config, SourceEntry
from agent_tools.harnesses.base import HarnessAdapter
from agent_tools.harnesses.registry import HarnessRegistry
from agent_tools.models import SkillContent
from agent_tools.sources.local import LocalSourceAdapter


class SkillNotFoundError(Exception):
    """Raised when a skill cannot be found in any configured source."""

    def __init__(self, name: str, sources_tried: list[str]) -> None:
        self.name = name
        self.sources_tried = sources_tried
        tried = ", ".join(sources_tried) if sources_tried else "(no sources configured)"
        super().__init__(
            f"Skill {name!r} not found. Sources searched: {tried}"
        )


class SourceUnreachableError(Exception):
    """Raised when a configured source cannot be accessed."""

    def __init__(self, source: str, reason: str) -> None:
        self.source = source
        self.reason = reason
        super().__init__(f"Source unreachable: {source} ({reason})")


class DestinationNotWritableError(Exception):
    """Raised when the destination path cannot be written to."""

    def __init__(self, path: Path, reason: str) -> None:
        self.path = path
        self.reason = reason
        super().__init__(f"Cannot write to {path}: {reason}")


def _build_source_adapter(entry: SourceEntry) -> LocalSourceAdapter | None:
    """Build a source adapter from a config entry.

    Returns None for unsupported source types, raises SourceUnreachableError
    for sources that can't be accessed.
    """
    if entry.type == "local":
        source_path = Path(entry.path)
        if not source_path.exists():
            raise SourceUnreachableError(
                entry.path, "path does not exist"
            )
        if not source_path.is_dir():
            raise SourceUnreachableError(
                entry.path, "path is not a directory"
            )
        return LocalSourceAdapter([source_path])
    # Other source types (git, registry) not yet implemented
    return None


def resolve_skill(
    name: str, sources: list[SourceEntry]
) -> SkillContent:
    """Try each configured source in order to find and retrieve a skill.

    Args:
        name: The skill name to resolve.
        sources: Ordered list of source entries to search.

    Returns:
        The resolved SkillContent.

    Raises:
        SkillNotFoundError: If the skill is not found in any source.
        SourceUnreachableError: If a source cannot be accessed.
    """
    sources_tried: list[str] = []

    for entry in sources:
        adapter = _build_source_adapter(entry)
        if adapter is None:
            # Unsupported source type, skip
            continue
        sources_tried.append(f"[{entry.type}] {entry.path}")
        try:
            return adapter.get_skill(name)
        except KeyError:
            continue

    raise SkillNotFoundError(name, sources_tried)


def resolve_harness(
    harness_name: str, registry: HarnessRegistry
) -> HarnessAdapter:
    """Resolve a harness adapter by name.

    Args:
        harness_name: The harness identifier (e.g. "claude-code").
        registry: The harness registry to look up.

    Returns:
        The resolved HarnessAdapter.

    Raises:
        HarnessNotFoundError: If the harness is not registered.
    """
    return registry.get(harness_name)


def copy_skill_to_harness(
    skill: SkillContent,
    adapter: HarnessAdapter,
) -> list[tuple[str, Path]]:
    """Copy skill files to the harness-specific destination.

    Args:
        skill: The resolved skill content.
        adapter: The harness adapter that determines destination paths.

    Returns:
        A list of (relative_path, absolute_dest) tuples for each file copied.

    Raises:
        DestinationNotWritableError: If the destination cannot be written.
    """
    dest_base = adapter.get_skill_path(skill.info.name)
    installed_files: list[tuple[str, Path]] = []

    # If the skill was loaded from a local path, copy from source directory
    source_dir = Path(skill.info.path)

    try:
        dest_base.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise DestinationNotWritableError(dest_base, str(e)) from e

    if source_dir.is_dir():
        # Copy from source directory to preserve all files (not just text content)
        for src_file in sorted(source_dir.rglob("*")):
            if src_file.is_file():
                relative = src_file.relative_to(source_dir)
                dest_file = dest_base / relative
                try:
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_file, dest_file)
                except OSError as e:
                    raise DestinationNotWritableError(dest_file, str(e)) from e
                installed_files.append((str(relative), dest_file))
    else:
        # Fallback: write from in-memory content (e.g. from a remote source)
        for relative_path, content in sorted(skill.files.items()):
            dest_file = dest_base / relative_path
            try:
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                dest_file.write_text(content, encoding="utf-8")
            except OSError as e:
                raise DestinationNotWritableError(dest_file, str(e)) from e
            installed_files.append((relative_path, dest_file))

    return installed_files


def install_skill(
    name: str,
    config: Config,
    registry: HarnessRegistry,
    harness_override: str | None = None,
) -> tuple[str, list[tuple[str, Path]]]:
    """Full install workflow: resolve skill -> resolve harness -> copy.

    Args:
        name: The skill name to install.
        config: The user configuration.
        registry: The harness registry.
        harness_override: If set, overrides the default harness from config.

    Returns:
        A tuple of (harness_name, list of (relative_path, dest_path) tuples).

    Raises:
        SkillNotFoundError: If the skill is not found.
        SourceUnreachableError: If a source is unreachable.
        HarnessNotFoundError: If the harness is invalid.
        DestinationNotWritableError: If destination is not writable.
    """
    harness_name = harness_override or config.default_harness
    adapter = resolve_harness(harness_name, registry)
    skill = resolve_skill(name, config.sources)
    installed = copy_skill_to_harness(skill, adapter)
    return harness_name, installed


def check_skill_exists(
    skill_name: str,
    adapter: HarnessAdapter,
) -> bool:
    """Check if a skill is already installed at the harness destination.

    Args:
        skill_name: The skill identifier.
        adapter: The harness adapter.

    Returns:
        True if the destination directory already exists and contains files.
    """
    dest = adapter.get_skill_path(skill_name)
    if not dest.exists():
        return False
    if dest.is_dir():
        return any(dest.iterdir())
    return dest.is_file()
