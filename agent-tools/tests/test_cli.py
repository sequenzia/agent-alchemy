"""Tests for agent-tools CLI entry point."""

from typer.testing import CliRunner

from agent_tools.cli import app

runner = CliRunner()


def test_cli_loads_without_errors() -> None:
    """CLI entry point loads and responds to --help without errors."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0


def test_help_includes_config_subcommand() -> None:
    """--help output includes the config subcommand."""
    result = runner.invoke(app, ["--help"])
    assert "config" in result.output


def test_help_includes_install_subcommand() -> None:
    """--help output includes the install subcommand."""
    result = runner.invoke(app, ["--help"])
    assert "install" in result.output


def test_help_includes_list_subcommand() -> None:
    """--help output includes the list subcommand."""
    result = runner.invoke(app, ["--help"])
    assert "list" in result.output


def test_help_includes_search_subcommand() -> None:
    """--help output includes the search subcommand."""
    result = runner.invoke(app, ["--help"])
    assert "search" in result.output


def test_help_includes_all_subcommands() -> None:
    """Integration: --help output includes all four subcommands."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for cmd in ("config", "install", "list", "search"):
        assert cmd in result.output, f"Missing subcommand: {cmd}"


def test_config_subcommand_responds() -> None:
    """Config subcommand responds without errors."""
    result = runner.invoke(app, ["config"])
    assert result.exit_code == 0


def test_install_subcommand_responds() -> None:
    """Install subcommand responds without errors."""
    result = runner.invoke(app, ["install"])
    assert result.exit_code == 0


def test_list_subcommand_responds() -> None:
    """List subcommand responds without errors."""
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0


def test_search_subcommand_responds() -> None:
    """Search subcommand responds without errors."""
    result = runner.invoke(app, ["search"])
    assert result.exit_code == 0
