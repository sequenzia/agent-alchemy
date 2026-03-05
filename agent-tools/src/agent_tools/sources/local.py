"""Local filesystem source adapter for skill discovery and retrieval."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from agent_tools.models import SkillContent, SkillInfo

logger = logging.getLogger(__name__)

# Files recognized as skill manifests (checked in priority order).
_MANIFEST_FILENAMES = ("SKILL.md", "skill.md", "manifest.json", "skill.json")

# File extensions to include when collecting skill content.
_CONTENT_EXTENSIONS = {".md", ".json", ".yaml", ".yml", ".txt"}


def _parse_description_from_skill_md(path: Path) -> str:
    """Extract a one-line description from a SKILL.md file.

    Looks for a YAML frontmatter ``description`` field first, then falls back
    to the first non-empty, non-heading line in the body.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""

    lines = text.splitlines()

    # Check for YAML frontmatter
    if lines and lines[0].strip() == "---":
        for line in lines[1:]:
            stripped = line.strip()
            if stripped == "---":
                break
            if stripped.lower().startswith("description:"):
                value = stripped.split(":", 1)[1].strip().strip("\"'")
                if value:
                    return value

    # Fallback: first non-empty, non-heading line
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and stripped != "---":
            return stripped

    return ""


def _parse_description_from_json(path: Path) -> str:
    """Extract a description field from a JSON manifest."""
    import json

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return str(data.get("description", ""))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        pass
    return ""


def _find_manifest(directory: Path) -> Path | None:
    """Return the first recognized manifest file found in *directory*."""
    for name in _MANIFEST_FILENAMES:
        candidate = directory / name
        if candidate.is_file():
            return candidate
    return None


def _extract_description(manifest: Path) -> str:
    """Extract a description string from a manifest file."""
    suffix = manifest.suffix.lower()
    if suffix == ".md":
        return _parse_description_from_skill_md(manifest)
    if suffix == ".json":
        return _parse_description_from_json(manifest)
    return ""


class LocalSourceAdapter:
    """Discovers and retrieves skills from local filesystem directories.

    Each configured path is scanned for subdirectories containing a recognized
    skill manifest file (``SKILL.md``, ``manifest.json``, etc.).  A flat layout
    where the manifest lives directly inside the configured path is also
    supported (the directory itself is treated as a single skill).

    Args:
        paths: One or more directory paths to scan for skills.
    """

    def __init__(self, paths: list[str | Path]) -> None:
        self._paths = [Path(p) for p in paths]

    # ------------------------------------------------------------------
    # SourceAdapter interface
    # ------------------------------------------------------------------

    def list_skills(self) -> list[SkillInfo]:
        """Enumerate all skills found under the configured paths."""
        skills: list[SkillInfo] = []
        for base in self._paths:
            skills.extend(self._scan_path(base))
        return skills

    def get_skill(self, name: str) -> SkillContent:
        """Retrieve a skill's content by name.

        Raises:
            KeyError: If the skill is not found in any configured path.
        """
        for info in self.list_skills():
            if info.name == name:
                return self._load_content(info)
        raise KeyError(f"Skill not found: {name}")

    def search(self, query: str) -> list[SkillInfo]:
        """Search skills by substring match on name or description."""
        query_lower = query.lower()
        return [
            s
            for s in self.list_skills()
            if query_lower in s.name.lower() or query_lower in s.description.lower()
        ]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _scan_path(self, base: Path) -> list[SkillInfo]:
        """Scan a single base path for skills."""
        resolved = base.resolve()

        if not resolved.exists():
            logger.warning("Source path does not exist, skipping: %s", base)
            return []

        if not resolved.is_dir():
            logger.warning("Source path is not a directory, skipping: %s", base)
            return []

        try:
            entries = list(resolved.iterdir())
        except PermissionError:
            logger.warning("Permission denied reading directory: %s", base)
            return []

        skills: list[SkillInfo] = []

        # Flat layout: manifest lives directly in the base directory
        manifest = _find_manifest(resolved)
        if manifest is not None:
            info = self._build_info(resolved, manifest, base)
            if info is not None:
                skills.append(info)
            return skills

        # Nested layout: each subdirectory may contain a manifest
        for entry in sorted(entries, key=lambda e: e.name):
            if not entry.is_dir():
                continue
            if not os.access(entry, os.R_OK):
                logger.warning("Permission denied reading directory: %s", entry)
                continue
            try:
                sub_manifest = _find_manifest(entry)
            except PermissionError:
                logger.warning("Permission denied reading directory: %s", entry)
                continue
            if sub_manifest is not None:
                info = self._build_info(entry, sub_manifest, base)
                if info is not None:
                    skills.append(info)

        return skills

    def _build_info(self, skill_dir: Path, manifest: Path, base: Path) -> SkillInfo | None:
        """Build a SkillInfo from a discovered manifest, or None on parse error."""
        try:
            description = _extract_description(manifest)
        except Exception:
            logger.warning("Malformed skill manifest, skipping: %s", manifest)
            return None

        return SkillInfo(
            name=skill_dir.name,
            description=description,
            source=f"local:{base}",
            path=str(skill_dir),
        )

    def _load_content(self, info: SkillInfo) -> SkillContent:
        """Read all content files from a skill directory."""
        skill_dir = Path(info.path)
        files: dict[str, str] = {}

        for root, _dirs, filenames in os.walk(skill_dir):
            root_path = Path(root)
            for filename in filenames:
                file_path = root_path / filename
                if file_path.suffix.lower() in _CONTENT_EXTENSIONS:
                    relative = str(file_path.relative_to(skill_dir))
                    try:
                        files[relative] = file_path.read_text(encoding="utf-8")
                    except (OSError, UnicodeDecodeError):
                        logger.warning("Could not read file: %s", file_path)

        return SkillContent(info=info, files=files)
