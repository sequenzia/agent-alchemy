"""Configuration management for agent-tools.

Handles reading, writing, and validating the user configuration file
stored at ~/.config/agent-tools/config.toml.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomllib  # type: ignore[import-not-found]
    except ImportError:
        tomllib = None  # type: ignore[assignment]

VALID_HARNESSES = ("claude-code", "opencode", "cursor", "codex")

DEFAULT_CONFIG_DIR = Path.home() / ".config" / "agent-tools"
DEFAULT_CONFIG_PATH = DEFAULT_CONFIG_DIR / "config.toml"


@dataclass
class SourceEntry:
    """A configured skill source.

    Attributes:
        type: Source type (e.g. 'local', 'git', 'registry').
        path: Filesystem path or URL for the source.
    """

    type: str
    path: str


@dataclass
class Config:
    """User configuration for agent-tools.

    Attributes:
        default_harness: The default target harness for installations.
        sources: List of configured skill sources.
    """

    default_harness: str = "claude-code"
    sources: list[SourceEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert config to a dictionary suitable for TOML serialization."""
        data: dict[str, Any] = {"default_harness": self.default_harness}
        if self.sources:
            data["sources"] = [
                {"type": s.type, "path": s.path} for s in self.sources
            ]
        return data


def _serialize_toml(data: dict[str, Any]) -> str:
    """Serialize a simple dictionary to TOML format.

    Handles top-level string values and a list of inline tables for sources.
    This is intentionally limited to the config structure we use.
    """
    lines: list[str] = []
    sources = data.pop("sources", None)

    for key, value in data.items():
        if isinstance(value, str):
            lines.append(f'{key} = "{value}"')
        elif isinstance(value, bool):
            lines.append(f"{key} = {'true' if value else 'false'}")
        elif isinstance(value, int | float):
            lines.append(f"{key} = {value}")

    if sources is not None:
        lines.append("")
        lines.append("[[sources]]")
        for i, source in enumerate(sources):
            if i > 0:
                lines.append("")
                lines.append("[[sources]]")
            for k, v in source.items():
                lines.append(f'{k} = "{v}"')

    lines.append("")  # trailing newline
    return "\n".join(lines)


def _parse_config(data: dict[str, Any]) -> Config:
    """Parse a TOML dictionary into a Config object."""
    default_harness = data.get("default_harness", "claude-code")
    raw_sources = data.get("sources", [])
    sources = [
        SourceEntry(type=s.get("type", "local"), path=s.get("path", ""))
        for s in raw_sources
    ]
    return Config(default_harness=default_harness, sources=sources)


def load_config(config_path: Path | None = None) -> Config:
    """Load configuration from the TOML file.

    If the config file does not exist, returns a Config with sensible defaults
    and creates the config file and directory.

    Args:
        config_path: Path to the config file. Defaults to ~/.config/agent-tools/config.toml.

    Returns:
        The loaded (or default) Config.
    """
    path = config_path or DEFAULT_CONFIG_PATH

    if not path.exists():
        config = Config()
        save_config(config, config_path=path)
        return config

    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return Config()

    if tomllib is not None:
        data = tomllib.loads(text)
    else:
        # Minimal fallback parser for our simple config format
        data = _minimal_toml_parse(text)

    return _parse_config(data)


def _minimal_toml_parse(text: str) -> dict[str, Any]:
    """Minimal TOML parser for the simple config format we generate.

    Only handles: key = "value" strings, [[sources]] array of tables.
    This is a fallback for Python 3.10 without tomllib.
    """
    data: dict[str, Any] = {}
    sources: list[dict[str, str]] = []
    current_source: dict[str, str] | None = None

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped == "[[sources]]":
            if current_source is not None:
                sources.append(current_source)
            current_source = {}
            continue

        if "=" in stripped:
            key, _, value = stripped.partition("=")
            key = key.strip()
            value = value.strip().strip('"')

            if current_source is not None:
                current_source[key] = value
            else:
                data[key] = value

    if current_source is not None:
        sources.append(current_source)

    if sources:
        data["sources"] = sources

    return data


def save_config(config: Config, config_path: Path | None = None) -> None:
    """Save configuration to the TOML file.

    Creates the config directory if it does not exist.

    Args:
        config: The Config object to save.
        config_path: Path to the config file. Defaults to ~/.config/agent-tools/config.toml.
    """
    path = config_path or DEFAULT_CONFIG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    content = _serialize_toml(config.to_dict())
    path.write_text(content, encoding="utf-8")


def validate_harness(name: str) -> str | None:
    """Validate a harness name.

    Args:
        name: The harness name to validate.

    Returns:
        None if valid, or an error message string if invalid.
    """
    if name not in VALID_HARNESSES:
        valid_list = ", ".join(VALID_HARNESSES)
        return f"Invalid harness '{name}'. Valid options: {valid_list}"
    return None


def add_source(config: Config, source_type: str, path: str) -> Config:
    """Add a source entry to the config.

    Args:
        config: The current Config.
        source_type: The source type (e.g. 'local', 'git').
        path: The path or URL for the source.

    Returns:
        A new Config with the source added.
    """
    new_source = SourceEntry(type=source_type, path=path)
    # Avoid duplicates
    for existing in config.sources:
        if existing.type == source_type and existing.path == path:
            return config
    return Config(
        default_harness=config.default_harness,
        sources=[*config.sources, new_source],
    )


def remove_source(config: Config, path: str) -> tuple[Config, bool]:
    """Remove a source entry by path.

    Args:
        config: The current Config.
        path: The path to match for removal.

    Returns:
        A tuple of (new Config, whether a source was removed).
    """
    original_count = len(config.sources)
    filtered = [s for s in config.sources if s.path != path]
    removed = len(filtered) < original_count
    return Config(default_harness=config.default_harness, sources=filtered), removed
