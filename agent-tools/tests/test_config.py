"""Tests for agent-tools config module and CLI commands."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

import agent_tools.cli as cli_module
from agent_tools.cli import app
from agent_tools.config import (
    Config,
    SourceEntry,
    add_source,
    load_config,
    remove_source,
    save_config,
    validate_harness,
)

runner = CliRunner()


# ---------------------------------------------------------------------------
# Unit: Config read/write operations
# ---------------------------------------------------------------------------


class TestConfigReadWrite:
    """Unit tests for config loading and saving."""

    def test_load_creates_default_config_on_first_run(self, tmp_path: Path) -> None:
        """First run creates config file with sensible defaults."""
        config_path = tmp_path / "config.toml"
        config = load_config(config_path=config_path)

        assert config.default_harness == "claude-code"
        assert config.sources == []
        assert config_path.exists()

    def test_load_creates_nested_directory(self, tmp_path: Path) -> None:
        """Handle missing config directory gracefully by creating it."""
        config_path = tmp_path / "deep" / "nested" / "config.toml"
        config = load_config(config_path=config_path)

        assert config.default_harness == "claude-code"
        assert config_path.exists()

    def test_save_and_load_roundtrip(self, tmp_path: Path) -> None:
        """Config survives a save/load roundtrip."""
        config_path = tmp_path / "config.toml"
        original = Config(
            default_harness="opencode",
            sources=[SourceEntry(type="local", path="/tmp/skills")],
        )
        save_config(original, config_path=config_path)
        loaded = load_config(config_path=config_path)

        assert loaded.default_harness == "opencode"
        assert len(loaded.sources) == 1
        assert loaded.sources[0].type == "local"
        assert loaded.sources[0].path == "/tmp/skills"

    def test_save_multiple_sources_roundtrip(self, tmp_path: Path) -> None:
        """Multiple sources survive a roundtrip."""
        config_path = tmp_path / "config.toml"
        original = Config(
            default_harness="cursor",
            sources=[
                SourceEntry(type="local", path="/path/a"),
                SourceEntry(type="git", path="https://github.com/example/repo"),
            ],
        )
        save_config(original, config_path=config_path)
        loaded = load_config(config_path=config_path)

        assert loaded.default_harness == "cursor"
        assert len(loaded.sources) == 2
        assert loaded.sources[1].type == "git"

    def test_load_empty_file_returns_defaults(self, tmp_path: Path) -> None:
        """An empty config file returns defaults rather than crashing."""
        config_path = tmp_path / "config.toml"
        config_path.write_text("", encoding="utf-8")
        config = load_config(config_path=config_path)

        assert config.default_harness == "claude-code"
        assert config.sources == []


# ---------------------------------------------------------------------------
# Unit: Source add/remove logic
# ---------------------------------------------------------------------------


class TestSourceAddRemove:
    """Unit tests for source add/remove operations."""

    def test_add_source_appends(self) -> None:
        """Adding a source appends it to the list."""
        config = Config()
        updated = add_source(config, "local", "/path/to/skills")

        assert len(updated.sources) == 1
        assert updated.sources[0].path == "/path/to/skills"

    def test_add_source_prevents_duplicates(self) -> None:
        """Adding the same source twice does not create a duplicate."""
        config = Config()
        config = add_source(config, "local", "/path/to/skills")
        config = add_source(config, "local", "/path/to/skills")

        assert len(config.sources) == 1

    def test_remove_source_removes_by_path(self) -> None:
        """Removing a source by path filters it out."""
        config = Config(sources=[SourceEntry(type="local", path="/path/to/skills")])
        updated, removed = remove_source(config, "/path/to/skills")

        assert removed is True
        assert len(updated.sources) == 0

    def test_remove_source_returns_false_when_not_found(self) -> None:
        """Removing a non-existent source returns False."""
        config = Config()
        updated, removed = remove_source(config, "/nonexistent")

        assert removed is False
        assert len(updated.sources) == 0

    def test_remove_source_preserves_others(self) -> None:
        """Removing one source preserves the rest."""
        config = Config(
            sources=[
                SourceEntry(type="local", path="/a"),
                SourceEntry(type="git", path="/b"),
            ]
        )
        updated, removed = remove_source(config, "/a")

        assert removed is True
        assert len(updated.sources) == 1
        assert updated.sources[0].path == "/b"


# ---------------------------------------------------------------------------
# Unit: Harness validation
# ---------------------------------------------------------------------------


class TestValidateHarness:
    """Unit tests for harness name validation."""

    def test_valid_harness_names(self) -> None:
        """All valid harness names pass validation."""
        for name in ("claude-code", "opencode", "cursor", "codex"):
            assert validate_harness(name) is None

    def test_invalid_harness_returns_error(self) -> None:
        """Invalid harness name returns an error message."""
        error = validate_harness("invalid-harness")
        assert error is not None
        assert "Invalid harness" in error
        assert "claude-code" in error


# ---------------------------------------------------------------------------
# Integration: Full config workflow via CLI (set -> get -> list)
# ---------------------------------------------------------------------------


@pytest.fixture()
def config_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Provide a temporary config path and patch the CLI to use it."""
    path = tmp_path / "config.toml"
    monkeypatch.setattr(cli_module, "_config_path_override", path)
    return path


class TestConfigCLI:
    """Integration tests for config CLI subcommands."""

    def test_config_set_default_harness(self, config_path: Path) -> None:
        """config set default_harness persists preference."""
        result = runner.invoke(app, ["config", "set", "default_harness", "opencode"])
        assert result.exit_code == 0
        assert "Set default_harness = opencode" in result.output

        # Verify it persisted
        config = load_config(config_path=config_path)
        assert config.default_harness == "opencode"

    def test_config_get_default_harness(self, config_path: Path) -> None:
        """config get default_harness displays current value."""
        # Set first
        runner.invoke(app, ["config", "set", "default_harness", "cursor"])
        result = runner.invoke(app, ["config", "get", "default_harness"])

        assert result.exit_code == 0
        assert "cursor" in result.output

    def test_config_list_shows_all(self, config_path: Path) -> None:
        """config list shows all current configuration."""
        runner.invoke(app, ["config", "set", "default_harness", "codex"])
        runner.invoke(app, ["config", "add-source", "local", "/tmp/my-skills"])

        result = runner.invoke(app, ["config", "list"])
        assert result.exit_code == 0
        assert "default_harness = codex" in result.output
        assert "/tmp/my-skills" in result.output

    def test_config_add_source(self, config_path: Path) -> None:
        """config add-source adds a source."""
        result = runner.invoke(app, ["config", "add-source", "local", "/path/to/skills"])
        assert result.exit_code == 0
        assert "Added source" in result.output

        config = load_config(config_path=config_path)
        assert len(config.sources) == 1
        assert config.sources[0].path == "/path/to/skills"

    def test_config_remove_source(self, config_path: Path) -> None:
        """config remove-source removes a source."""
        runner.invoke(app, ["config", "add-source", "local", "/path/to/skills"])
        result = runner.invoke(app, ["config", "remove-source", "/path/to/skills"])

        assert result.exit_code == 0
        assert "Removed source" in result.output

        config = load_config(config_path=config_path)
        assert len(config.sources) == 0

    def test_config_set_invalid_harness_rejected(self, config_path: Path) -> None:
        """Invalid harness name is rejected with helpful message."""
        result = runner.invoke(app, ["config", "set", "default_harness", "invalid"])
        assert result.exit_code == 1
        assert "Invalid harness" in result.output

    def test_config_add_source_warns_invalid_path(self, config_path: Path) -> None:
        """Invalid source path warns but still saves."""
        result = runner.invoke(
            app, ["config", "add-source", "local", "/nonexistent/path/xyz"]
        )
        assert result.exit_code == 0
        assert "Warning" in result.output
        assert "Added source" in result.output

        config = load_config(config_path=config_path)
        assert len(config.sources) == 1

    def test_full_config_workflow(self, config_path: Path) -> None:
        """Integration: set -> get -> add-source -> list -> remove-source."""
        # Set harness
        result = runner.invoke(app, ["config", "set", "default_harness", "claude-code"])
        assert result.exit_code == 0

        # Get harness
        result = runner.invoke(app, ["config", "get", "default_harness"])
        assert result.exit_code == 0
        assert "claude-code" in result.output

        # Add source
        result = runner.invoke(app, ["config", "add-source", "local", "/tmp/skills"])
        assert result.exit_code == 0

        # List all
        result = runner.invoke(app, ["config", "list"])
        assert result.exit_code == 0
        assert "claude-code" in result.output
        assert "/tmp/skills" in result.output

        # Remove source
        result = runner.invoke(app, ["config", "remove-source", "/tmp/skills"])
        assert result.exit_code == 0

        # Verify removal
        result = runner.invoke(app, ["config", "list"])
        assert "/tmp/skills" not in result.output

    def test_config_list_shows_defaults_on_first_run(self, config_path: Path) -> None:
        """First run config list shows sensible defaults."""
        result = runner.invoke(app, ["config", "list"])
        assert result.exit_code == 0
        assert "default_harness = claude-code" in result.output
        assert "(none)" in result.output
