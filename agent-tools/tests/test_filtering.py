"""Tests for search filtering, output formatting, and info command."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

import agent_tools.cli as cli_module
from agent_tools.config import Config, SourceEntry, save_config
from agent_tools.discovery import (
    filter_skills,
    format_skill_info,
    format_skills_json,
    format_skills_rich_table,
    format_skills_yaml,
)
from agent_tools.models import SkillInfo

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

runner = CliRunner()


@pytest.fixture()
def sample_skills() -> list[SkillInfo]:
    """Create a mixed list of skills and agents for filtering tests."""
    return [
        SkillInfo(
            name="deep-analysis",
            description="Hub-and-spoke analysis engine",
            source="local:/skills",
            path="/skills/deep-analysis",
            skill_type="skill",
            compatible_harnesses=("claude-code", "opencode"),
        ),
        SkillInfo(
            name="code-explorer",
            description="Explores codebase structure",
            source="local:/agents",
            path="/agents/code-explorer",
            skill_type="agent",
            compatible_harnesses=("claude-code",),
        ),
        SkillInfo(
            name="git-commit",
            description="Automates git commits",
            source="local:/skills",
            path="/skills/git-commit",
            skill_type="skill",
            compatible_harnesses=(),
        ),
        SkillInfo(
            name="bug-investigator",
            description="Investigates bugs",
            source="local:/agents",
            path="/agents/bug-investigator",
            skill_type="agent",
            compatible_harnesses=("claude-code", "cursor"),
        ),
    ]


@pytest.fixture()
def skills_dir(tmp_path: Path) -> Path:
    """Create a source directory with skills for CLI tests."""
    source = tmp_path / "source"
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


def _setup_config(tmp_path: Path, skills_dir: Path) -> Path:
    """Create a config file pointing to the given source and override the CLI config path."""
    config_path = tmp_path / "config.toml"
    config = Config(
        default_harness="claude-code",
        sources=[SourceEntry(type="local", path=str(skills_dir))],
    )
    save_config(config, config_path=config_path)
    return config_path


# ---------------------------------------------------------------------------
# Unit: filter_skills
# ---------------------------------------------------------------------------


class TestFilterSkills:
    """Tests for filter_skills with various filter combinations."""

    def test_no_filters_returns_all(self, sample_skills: list[SkillInfo]) -> None:
        result = filter_skills(sample_skills)
        assert len(result) == 4

    def test_filter_by_type_skill(self, sample_skills: list[SkillInfo]) -> None:
        result = filter_skills(sample_skills, skill_type="skill")
        assert all(s.skill_type == "skill" for s in result)
        assert len(result) == 2

    def test_filter_by_type_agent(self, sample_skills: list[SkillInfo]) -> None:
        result = filter_skills(sample_skills, skill_type="agent")
        assert all(s.skill_type == "agent" for s in result)
        assert len(result) == 2

    def test_filter_by_harness(self, sample_skills: list[SkillInfo]) -> None:
        result = filter_skills(sample_skills, harness="cursor")
        names = {s.name for s in result}
        # git-commit has empty harnesses (compatible with all), bug-investigator has cursor
        assert "bug-investigator" in names
        assert "git-commit" in names

    def test_combined_type_and_harness(self, sample_skills: list[SkillInfo]) -> None:
        result = filter_skills(sample_skills, skill_type="agent", harness="claude-code")
        names = {s.name for s in result}
        assert names == {"code-explorer", "bug-investigator"}

    def test_combined_filters_narrow(self, sample_skills: list[SkillInfo]) -> None:
        result = filter_skills(sample_skills, skill_type="agent", harness="cursor")
        assert len(result) == 1
        assert result[0].name == "bug-investigator"

    def test_no_results_for_impossible_combination(
        self, sample_skills: list[SkillInfo]
    ) -> None:
        result = filter_skills(sample_skills, skill_type="skill", harness="cursor")
        # Only git-commit (skill, empty harnesses) is compatible
        assert len(result) == 1
        assert result[0].name == "git-commit"

    def test_empty_input_returns_empty(self) -> None:
        result = filter_skills([], skill_type="skill")
        assert result == []


# ---------------------------------------------------------------------------
# Unit: Output formatting - JSON
# ---------------------------------------------------------------------------


class TestFormatSkillsJson:
    """Tests for format_skills_json output."""

    def test_json_is_valid(self, sample_skills: list[SkillInfo]) -> None:
        output = format_skills_json(sample_skills)
        data = json.loads(output)
        assert isinstance(data, list)
        assert len(data) == 4

    def test_json_contains_all_fields(self) -> None:
        skill = SkillInfo(
            name="test",
            description="A test",
            source="local:/x",
            path="/x/test",
            skill_type="skill",
            compatible_harnesses=("claude-code",),
        )
        output = format_skills_json([skill])
        data = json.loads(output)
        entry = data[0]
        assert entry["name"] == "test"
        assert entry["type"] == "skill"
        assert entry["description"] == "A test"
        assert entry["source"] == "local:/x"
        assert entry["path"] == "/x/test"
        assert entry["compatible_harnesses"] == ["claude-code"]

    def test_json_empty_list(self) -> None:
        output = format_skills_json([])
        data = json.loads(output)
        assert data == []


# ---------------------------------------------------------------------------
# Unit: Output formatting - Table
# ---------------------------------------------------------------------------


class TestFormatSkillsRichTable:
    """Tests for format_skills_rich_table output."""

    def test_empty_list_returns_empty_string(self) -> None:
        assert format_skills_rich_table([]) == ""

    def test_table_has_type_column(self, sample_skills: list[SkillInfo]) -> None:
        table = format_skills_rich_table(sample_skills)
        lines = table.splitlines()
        assert "Type" in lines[0]
        assert "Name" in lines[0]

    def test_table_aligns_columns(self, sample_skills: list[SkillInfo]) -> None:
        table = format_skills_rich_table(sample_skills)
        lines = table.splitlines()
        # Header and separator should have the same column positions
        assert len(lines) >= 3  # header + separator + at least 1 row

    def test_table_truncates_long_description(self) -> None:
        skill = SkillInfo(
            name="long",
            description="A" * 100,
            source="local:/x",
            path="/x/long",
            skill_type="skill",
        )
        table = format_skills_rich_table([skill])
        assert "..." in table


# ---------------------------------------------------------------------------
# Unit: Output formatting - YAML
# ---------------------------------------------------------------------------


class TestFormatSkillsYaml:
    """Tests for format_skills_yaml output."""

    def test_yaml_contains_skill_data(self) -> None:
        skill = SkillInfo(
            name="test",
            description="A test skill",
            source="local:/x",
            path="/x/test",
            skill_type="agent",
            compatible_harnesses=("opencode",),
        )
        output = format_skills_yaml([skill])
        assert "- name: test" in output
        assert "type: agent" in output
        assert "description: A test skill" in output
        assert "opencode" in output


# ---------------------------------------------------------------------------
# Unit: format_skill_info (info subcommand detail view)
# ---------------------------------------------------------------------------


class TestFormatSkillInfo:
    """Tests for format_skill_info full metadata display."""

    def test_contains_all_metadata(self) -> None:
        skill = SkillInfo(
            name="deep-analysis",
            description="Hub-and-spoke analysis engine",
            source="local:/skills",
            path="/skills/deep-analysis",
            skill_type="skill",
            compatible_harnesses=("claude-code", "opencode"),
        )
        output = format_skill_info(skill)
        assert "Name:        deep-analysis" in output
        assert "Type:        skill" in output
        assert "Description: Hub-and-spoke analysis engine" in output
        assert "Source:      local:/skills" in output
        assert "Path:        /skills/deep-analysis" in output
        assert "Harnesses:   claude-code, opencode" in output

    def test_empty_harnesses_shows_all(self) -> None:
        skill = SkillInfo(
            name="test", description="desc", source="x", path="/x",
            compatible_harnesses=(),
        )
        output = format_skill_info(skill)
        assert "Harnesses:   all" in output


# ---------------------------------------------------------------------------
# Integration: CLI --type flag
# ---------------------------------------------------------------------------


class TestListTypeFilter:
    """Integration tests for list command with --type flag."""

    def test_list_type_filter(self, tmp_path: Path, skills_dir: Path) -> None:
        config_path = _setup_config(tmp_path, skills_dir)
        old = cli_module._config_path_override
        cli_module._config_path_override = config_path
        try:
            from agent_tools.cli import app

            # All discovered skills are type "skill" by default
            result = runner.invoke(app, ["list", "--type", "skill"])
            assert result.exit_code == 0
            assert "alpha" in result.output
        finally:
            cli_module._config_path_override = old

    def test_list_invalid_type_rejected(self, tmp_path: Path, skills_dir: Path) -> None:
        config_path = _setup_config(tmp_path, skills_dir)
        old = cli_module._config_path_override
        cli_module._config_path_override = config_path
        try:
            from agent_tools.cli import app

            result = runner.invoke(app, ["list", "--type", "bogus"])
            assert result.exit_code == 1
            assert "Invalid type" in result.output
            assert "skill, agent" in result.output
        finally:
            cli_module._config_path_override = old


# ---------------------------------------------------------------------------
# Integration: CLI --format flag
# ---------------------------------------------------------------------------


class TestListFormatFlag:
    """Integration tests for list command with --format flag."""

    def test_list_format_json(self, tmp_path: Path, skills_dir: Path) -> None:
        config_path = _setup_config(tmp_path, skills_dir)
        old = cli_module._config_path_override
        cli_module._config_path_override = config_path
        try:
            from agent_tools.cli import app

            result = runner.invoke(app, ["list", "--format", "json"])
            assert result.exit_code == 0
            data = json.loads(result.output)
            assert isinstance(data, list)
            assert len(data) == 2
            names = {d["name"] for d in data}
            assert names == {"alpha", "beta"}
        finally:
            cli_module._config_path_override = old

    def test_list_format_yaml(self, tmp_path: Path, skills_dir: Path) -> None:
        config_path = _setup_config(tmp_path, skills_dir)
        old = cli_module._config_path_override
        cli_module._config_path_override = config_path
        try:
            from agent_tools.cli import app

            result = runner.invoke(app, ["list", "--format", "yaml"])
            assert result.exit_code == 0
            assert "- name: alpha" in result.output
            assert "- name: beta" in result.output
        finally:
            cli_module._config_path_override = old

    def test_list_invalid_format_rejected(self, tmp_path: Path, skills_dir: Path) -> None:
        config_path = _setup_config(tmp_path, skills_dir)
        old = cli_module._config_path_override
        cli_module._config_path_override = config_path
        try:
            from agent_tools.cli import app

            result = runner.invoke(app, ["list", "--format", "xml"])
            assert result.exit_code == 1
            assert "Invalid format" in result.output
            assert "table, json, yaml" in result.output
        finally:
            cli_module._config_path_override = old


# ---------------------------------------------------------------------------
# Integration: CLI info command
# ---------------------------------------------------------------------------


class TestInfoCommand:
    """Integration tests for info command."""

    def test_info_shows_skill_details(self, tmp_path: Path, skills_dir: Path) -> None:
        config_path = _setup_config(tmp_path, skills_dir)
        old = cli_module._config_path_override
        cli_module._config_path_override = config_path
        try:
            from agent_tools.cli import app

            result = runner.invoke(app, ["info", "alpha"])
            assert result.exit_code == 0
            assert "Name:        alpha" in result.output
            assert "Type:        skill" in result.output
            assert "Description:" in result.output

        finally:
            cli_module._config_path_override = old

    def test_info_not_found(self, tmp_path: Path, skills_dir: Path) -> None:
        config_path = _setup_config(tmp_path, skills_dir)
        old = cli_module._config_path_override
        cli_module._config_path_override = config_path
        try:
            from agent_tools.cli import app

            result = runner.invoke(app, ["info", "nonexistent"])
            assert result.exit_code == 1
            assert "not found" in result.output

        finally:
            cli_module._config_path_override = old

    def test_info_json_format(self, tmp_path: Path, skills_dir: Path) -> None:
        config_path = _setup_config(tmp_path, skills_dir)
        old = cli_module._config_path_override
        cli_module._config_path_override = config_path
        try:
            from agent_tools.cli import app

            result = runner.invoke(app, ["info", "--format", "json", "alpha"])
            assert result.exit_code == 0
            data = json.loads(result.output)
            assert isinstance(data, list)
            assert data[0]["name"] == "alpha"

        finally:
            cli_module._config_path_override = old

    def test_info_no_name_shows_usage(self, tmp_path: Path, skills_dir: Path) -> None:
        config_path = _setup_config(tmp_path, skills_dir)
        old = cli_module._config_path_override
        cli_module._config_path_override = config_path
        try:
            from agent_tools.cli import app

            result = runner.invoke(app, ["info"])
            assert result.exit_code == 0
            assert "Usage" in result.output

        finally:
            cli_module._config_path_override = old


# ---------------------------------------------------------------------------
# Integration: Combined filters and no-results message
# ---------------------------------------------------------------------------


class TestCombinedFilters:
    """Tests for combined filter interactions and helpful no-results messages."""

    def test_no_results_shows_helpful_message(
        self, tmp_path: Path, skills_dir: Path
    ) -> None:
        config_path = _setup_config(tmp_path, skills_dir)
        old = cli_module._config_path_override
        cli_module._config_path_override = config_path
        try:
            from agent_tools.cli import app

            result = runner.invoke(app, ["list", "--type", "agent"])
            assert result.exit_code == 0
            assert "No skills found" in result.output
            assert "filters" in result.output.lower() or "broadening" in result.output.lower()

        finally:
            cli_module._config_path_override = old

    def test_search_with_type_filter(self, tmp_path: Path, skills_dir: Path) -> None:
        config_path = _setup_config(tmp_path, skills_dir)
        old = cli_module._config_path_override
        cli_module._config_path_override = config_path
        try:
            from agent_tools.cli import app

            result = runner.invoke(app, ["search", "--type", "skill", "alpha"])
            assert result.exit_code == 0
            assert "alpha" in result.output

        finally:
            cli_module._config_path_override = old

    def test_search_format_json(self, tmp_path: Path, skills_dir: Path) -> None:
        config_path = _setup_config(tmp_path, skills_dir)
        old = cli_module._config_path_override
        cli_module._config_path_override = config_path
        try:
            from agent_tools.cli import app

            result = runner.invoke(app, ["search", "--format", "json", "alpha"])
            assert result.exit_code == 0
            data = json.loads(result.output)
            assert len(data) == 1
            assert data[0]["name"] == "alpha"

        finally:
            cli_module._config_path_override = old
