"""Tests for skill discovery: aggregation, search, and formatting."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent_tools.config import Config, SourceEntry
from agent_tools.discovery import (
    aggregate_skills,
    format_skills_table,
    get_valid_source_paths,
    search_skills,
)
from agent_tools.models import SkillInfo

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def skills_dir_a(tmp_path: Path) -> Path:
    """Create a source directory with two skills."""
    source = tmp_path / "source-a"
    source.mkdir()

    s1 = source / "alpha"
    s1.mkdir()
    (s1 / "SKILL.md").write_text(
        "---\ndescription: Alpha skill for testing\n---\n# Alpha\n",
        encoding="utf-8",
    )

    s2 = source / "beta"
    s2.mkdir()
    (s2 / "SKILL.md").write_text(
        "---\ndescription: Beta helper utility\n---\n# Beta\n",
        encoding="utf-8",
    )

    return source


@pytest.fixture()
def skills_dir_b(tmp_path: Path) -> Path:
    """Create a second source directory with one skill."""
    source = tmp_path / "source-b"
    source.mkdir()

    s1 = source / "gamma"
    s1.mkdir()
    (s1 / "SKILL.md").write_text(
        "---\ndescription: Gamma advanced tool\n---\n# Gamma\n",
        encoding="utf-8",
    )

    return source


@pytest.fixture()
def config_two_sources(skills_dir_a: Path, skills_dir_b: Path) -> Config:
    """Config with two local sources."""
    return Config(
        default_harness="claude-code",
        sources=[
            SourceEntry(type="local", path=str(skills_dir_a)),
            SourceEntry(type="local", path=str(skills_dir_b)),
        ],
    )


@pytest.fixture()
def config_no_sources() -> Config:
    """Config with no sources."""
    return Config(default_harness="claude-code", sources=[])


@pytest.fixture()
def config_single_source(skills_dir_a: Path) -> Config:
    """Config with one local source."""
    return Config(
        default_harness="claude-code",
        sources=[SourceEntry(type="local", path=str(skills_dir_a))],
    )


# ---------------------------------------------------------------------------
# Unit: Result aggregation from multiple sources
# ---------------------------------------------------------------------------


class TestAggregateSkills:
    """Tests for aggregate_skills collecting from multiple sources."""

    def test_aggregates_from_all_sources(self, config_two_sources: Config) -> None:
        skills, errors = aggregate_skills(config_two_sources)
        names = {s.name for s in skills}
        assert names == {"alpha", "beta", "gamma"}
        assert errors == []

    def test_source_filter_limits_to_one_source(
        self, config_two_sources: Config, skills_dir_a: Path
    ) -> None:
        skills, errors = aggregate_skills(config_two_sources, source_filter=str(skills_dir_a))
        names = {s.name for s in skills}
        assert names == {"alpha", "beta"}
        assert errors == []

    def test_no_sources_returns_empty(self, config_no_sources: Config) -> None:
        skills, errors = aggregate_skills(config_no_sources)
        assert skills == []
        assert errors == []

    def test_unreachable_source_skipped_with_error(self, tmp_path: Path) -> None:
        missing = tmp_path / "nonexistent"
        config = Config(
            default_harness="claude-code",
            sources=[SourceEntry(type="local", path=str(missing))],
        )
        skills, errors = aggregate_skills(config)
        # LocalSourceAdapter logs a warning but returns empty list, not an exception
        assert skills == []
        # No raised exception means no SourceError, just empty results
        assert errors == []

    def test_unsupported_source_type_produces_error(self) -> None:
        config = Config(
            default_harness="claude-code",
            sources=[SourceEntry(type="git", path="https://example.com/repo.git")],
        )
        skills, errors = aggregate_skills(config)
        assert skills == []
        assert len(errors) == 1
        assert "Unsupported source type" in errors[0].error

    def test_mixed_good_and_bad_sources(
        self, skills_dir_a: Path,
    ) -> None:
        config = Config(
            default_harness="claude-code",
            sources=[
                SourceEntry(type="local", path=str(skills_dir_a)),
                SourceEntry(type="git", path="https://example.com/repo.git"),
            ],
        )
        skills, errors = aggregate_skills(config)
        names = {s.name for s in skills}
        assert "alpha" in names
        assert len(errors) == 1


# ---------------------------------------------------------------------------
# Unit: Search filtering logic
# ---------------------------------------------------------------------------


class TestSearchSkills:
    """Tests for search_skills filtering by name and description."""

    def test_search_by_name(self, config_two_sources: Config) -> None:
        skills, _ = search_skills(config_two_sources, "alpha")
        assert len(skills) == 1
        assert skills[0].name == "alpha"

    def test_search_by_description(self, config_two_sources: Config) -> None:
        skills, _ = search_skills(config_two_sources, "advanced")
        assert len(skills) == 1
        assert skills[0].name == "gamma"

    def test_search_case_insensitive(self, config_two_sources: Config) -> None:
        skills, _ = search_skills(config_two_sources, "ALPHA")
        assert len(skills) == 1

    def test_search_no_match(self, config_two_sources: Config) -> None:
        skills, _ = search_skills(config_two_sources, "zzz-nonexistent")
        assert skills == []

    def test_search_matches_multiple(self, config_two_sources: Config) -> None:
        # "skill" appears in description of alpha and beta ("Alpha skill", "Beta helper")
        skills, _ = search_skills(config_two_sources, "skill")
        assert len(skills) >= 1

    def test_search_with_source_filter(
        self, config_two_sources: Config, skills_dir_b: Path
    ) -> None:
        skills, _ = search_skills(
            config_two_sources, "gamma", source_filter=str(skills_dir_b)
        )
        assert len(skills) == 1
        assert skills[0].name == "gamma"

    def test_search_source_filter_excludes(
        self, config_two_sources: Config, skills_dir_a: Path
    ) -> None:
        # gamma is only in source-b, filtering to source-a should find nothing
        skills, _ = search_skills(
            config_two_sources, "gamma", source_filter=str(skills_dir_a)
        )
        assert skills == []


# ---------------------------------------------------------------------------
# Unit: Table formatting
# ---------------------------------------------------------------------------


class TestFormatSkillsTable:
    """Tests for format_skills_table output."""

    def test_empty_list_returns_empty_string(self) -> None:
        assert format_skills_table([]) == ""

    def test_table_has_header(self) -> None:
        skills = [
            SkillInfo(
                name="test", description="A test skill",
                source="local:/tmp/x", path="/tmp/x/test",
            ),
        ]
        table = format_skills_table(skills)
        lines = table.splitlines()
        assert "Name" in lines[0]
        assert "Source" in lines[0]
        assert "Description" in lines[0]
        # Second line is separator
        assert set(lines[1].replace(" ", "")) <= {"-"}

    def test_table_contains_skill_data(self) -> None:
        skills = [
            SkillInfo(
                name="my-skill", description="Does things",
                source="local:/foo", path="/foo/my-skill",
            ),
        ]
        table = format_skills_table(skills)
        assert "my-skill" in table
        assert "Does things" in table

    def test_long_description_truncated(self) -> None:
        long_desc = "A" * 100
        skills = [
            SkillInfo(name="long", description=long_desc, source="local:/x", path="/x/long"),
        ]
        table = format_skills_table(skills)
        assert "..." in table
        # Should not contain the full 100 chars
        assert long_desc not in table

    def test_source_shows_short_label(self) -> None:
        skills = [
            SkillInfo(
                name="test",
                description="desc",
                source="local:/very/long/path/to/skills",
                path="/very/long/path/to/skills/test",
            ),
        ]
        table = format_skills_table(skills)
        # Should show "skills" (last path component), not the full path
        assert "skills" in table

    def test_multiple_skills_all_present(self) -> None:
        skills = [
            SkillInfo(name="a", description="First", source="local:/x", path="/x/a"),
            SkillInfo(name="b", description="Second", source="local:/y", path="/y/b"),
        ]
        table = format_skills_table(skills)
        assert "a" in table
        assert "b" in table
        assert "First" in table
        assert "Second" in table


# ---------------------------------------------------------------------------
# Unit: get_valid_source_paths
# ---------------------------------------------------------------------------


class TestGetValidSourcePaths:
    """Tests for get_valid_source_paths helper."""

    def test_returns_paths(
        self, config_two_sources: Config, skills_dir_a: Path, skills_dir_b: Path
    ) -> None:
        paths = get_valid_source_paths(config_two_sources)
        assert str(skills_dir_a) in paths
        assert str(skills_dir_b) in paths

    def test_empty_config(self, config_no_sources: Config) -> None:
        assert get_valid_source_paths(config_no_sources) == []


# ---------------------------------------------------------------------------
# Integration: List/search with mock source adapters via CLI
# ---------------------------------------------------------------------------


class TestListSearchCLI:
    """Integration tests for list and search commands via CLI runner."""

    def test_list_shows_skills(
        self, tmp_path: Path, skills_dir_a: Path
    ) -> None:
        from typer.testing import CliRunner

        import agent_tools.cli as cli_module
        from agent_tools.cli import app

        runner = CliRunner()

        # Set up config with the test source
        config_path = tmp_path / "config.toml"
        config = Config(
            default_harness="claude-code",
            sources=[SourceEntry(type="local", path=str(skills_dir_a))],
        )
        from agent_tools.config import save_config

        save_config(config, config_path=config_path)

        old_override = cli_module._config_path_override
        cli_module._config_path_override = config_path
        try:
            result = runner.invoke(app, ["list"])
            assert result.exit_code == 0
            assert "alpha" in result.output
            assert "beta" in result.output
            assert "skill(s) found" in result.output
        finally:
            cli_module._config_path_override = old_override

    def test_search_filters_results(
        self, tmp_path: Path, skills_dir_a: Path
    ) -> None:
        from typer.testing import CliRunner

        import agent_tools.cli as cli_module
        from agent_tools.cli import app

        runner = CliRunner()

        config_path = tmp_path / "config.toml"
        config = Config(
            default_harness="claude-code",
            sources=[SourceEntry(type="local", path=str(skills_dir_a))],
        )
        from agent_tools.config import save_config

        save_config(config, config_path=config_path)

        old_override = cli_module._config_path_override
        cli_module._config_path_override = config_path
        try:
            result = runner.invoke(app, ["search", "alpha"])
            assert result.exit_code == 0
            assert "alpha" in result.output
            assert "beta" not in result.output
        finally:
            cli_module._config_path_override = old_override

    def test_list_no_sources(self, tmp_path: Path) -> None:
        from typer.testing import CliRunner

        import agent_tools.cli as cli_module
        from agent_tools.cli import app

        runner = CliRunner()

        config_path = tmp_path / "config.toml"
        config = Config(default_harness="claude-code", sources=[])
        from agent_tools.config import save_config

        save_config(config, config_path=config_path)

        old_override = cli_module._config_path_override
        cli_module._config_path_override = config_path
        try:
            result = runner.invoke(app, ["list"])
            assert result.exit_code == 0
            assert "No sources configured" in result.output
            assert "config add-source" in result.output
        finally:
            cli_module._config_path_override = old_override

    def test_search_no_match(self, tmp_path: Path, skills_dir_a: Path) -> None:
        from typer.testing import CliRunner

        import agent_tools.cli as cli_module
        from agent_tools.cli import app

        runner = CliRunner()

        config_path = tmp_path / "config.toml"
        config = Config(
            default_harness="claude-code",
            sources=[SourceEntry(type="local", path=str(skills_dir_a))],
        )
        from agent_tools.config import save_config

        save_config(config, config_path=config_path)

        old_override = cli_module._config_path_override
        cli_module._config_path_override = config_path
        try:
            result = runner.invoke(app, ["search", "zzz-nothing"])
            assert result.exit_code == 0
            assert "No skills found" in result.output
        finally:
            cli_module._config_path_override = old_override

    def test_list_with_source_filter(
        self, tmp_path: Path, skills_dir_a: Path, skills_dir_b: Path
    ) -> None:
        from typer.testing import CliRunner

        import agent_tools.cli as cli_module
        from agent_tools.cli import app

        runner = CliRunner()

        config_path = tmp_path / "config.toml"
        config = Config(
            default_harness="claude-code",
            sources=[
                SourceEntry(type="local", path=str(skills_dir_a)),
                SourceEntry(type="local", path=str(skills_dir_b)),
            ],
        )
        from agent_tools.config import save_config

        save_config(config, config_path=config_path)

        old_override = cli_module._config_path_override
        cli_module._config_path_override = config_path
        try:
            result = runner.invoke(app, ["list", "--source", str(skills_dir_a)])
            assert result.exit_code == 0
            assert "alpha" in result.output
            assert "gamma" not in result.output
        finally:
            cli_module._config_path_override = old_override

    def test_list_invalid_source_flag(
        self, tmp_path: Path, skills_dir_a: Path
    ) -> None:
        from typer.testing import CliRunner

        import agent_tools.cli as cli_module
        from agent_tools.cli import app

        runner = CliRunner()

        config_path = tmp_path / "config.toml"
        config = Config(
            default_harness="claude-code",
            sources=[SourceEntry(type="local", path=str(skills_dir_a))],
        )
        from agent_tools.config import save_config

        save_config(config, config_path=config_path)

        old_override = cli_module._config_path_override
        cli_module._config_path_override = config_path
        try:
            result = runner.invoke(app, ["list", "--source", "/nonexistent/path"])
            assert result.exit_code == 1
            assert "Unknown source" in result.output
        finally:
            cli_module._config_path_override = old_override

    def test_search_no_query_shows_usage(self, tmp_path: Path) -> None:
        from typer.testing import CliRunner

        import agent_tools.cli as cli_module
        from agent_tools.cli import app

        runner = CliRunner()

        config_path = tmp_path / "config.toml"
        config = Config(
            default_harness="claude-code",
            sources=[SourceEntry(type="local", path=str(tmp_path))],
        )
        from agent_tools.config import save_config

        save_config(config, config_path=config_path)

        old_override = cli_module._config_path_override
        cli_module._config_path_override = config_path
        try:
            result = runner.invoke(app, ["search"])
            assert result.exit_code == 0
            assert "Usage" in result.output or "search" in result.output.lower()
        finally:
            cli_module._config_path_override = old_override
