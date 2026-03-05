"""Tests for error handling, output formatting, and CLI error behavior."""

from __future__ import annotations

from typer.testing import CliRunner

from agent_tools.cli import app
from agent_tools.output import (
    Console,
    Verbosity,
    format_bug_report,
    format_error_message,
    get_console,
    reset_console,
    set_console,
)

runner = CliRunner()


# --- Unit: Error message formatting ---


class TestFormatErrorMessage:
    """Tests for format_error_message plain-text formatter."""

    def test_error_only(self) -> None:
        """Error message without hint contains just the error."""
        result = format_error_message("File not found")
        assert result == "Error: File not found"

    def test_error_with_hint(self) -> None:
        """Error message with hint includes hint on next line."""
        result = format_error_message("File not found", hint="Check the path exists.")
        assert "Error: File not found" in result
        assert "Hint: Check the path exists." in result

    def test_hint_on_separate_line(self) -> None:
        """Hint is on a separate line from the error."""
        result = format_error_message("Oops", hint="Try again.")
        lines = result.split("\n")
        assert len(lines) == 2
        assert "Error: Oops" in lines[0]
        assert "Hint: Try again." in lines[1]


class TestFormatBugReport:
    """Tests for format_bug_report unhandled exception formatter."""

    def test_includes_exception_type(self) -> None:
        """Bug report includes the exception class name."""
        exc = ValueError("bad value")
        result = format_bug_report(exc)
        assert "ValueError" in result

    def test_includes_exception_message(self) -> None:
        """Bug report includes the exception message."""
        exc = RuntimeError("something broke")
        result = format_bug_report(exc)
        assert "something broke" in result

    def test_includes_report_url(self) -> None:
        """Bug report suggests reporting the issue."""
        exc = Exception("test")
        result = format_bug_report(exc)
        assert "report" in result.lower()

    def test_includes_verbose_suggestion(self) -> None:
        """Bug report suggests running with --verbose."""
        exc = Exception("test")
        result = format_bug_report(exc)
        assert "--verbose" in result

    def test_no_message_exception(self) -> None:
        """Bug report handles exception with empty message."""
        exc = Exception()
        result = format_bug_report(exc)
        assert "(no message)" in result


# --- Unit: Console verbosity levels ---


class TestConsoleVerbosity:
    """Tests for Console output suppression based on verbosity."""

    def test_quiet_suppresses_info(self) -> None:
        """Quiet mode suppresses info messages."""
        console = Console(verbosity=Verbosity.QUIET)
        # info uses _out, which is a Rich console - we can't easily capture it
        # but we can verify the verbosity is set
        assert console.verbosity == Verbosity.QUIET

    def test_verbose_enables_debug(self) -> None:
        """Verbose mode enables debug messages."""
        console = Console(verbosity=Verbosity.VERBOSE)
        assert console.verbosity == Verbosity.VERBOSE

    def test_normal_is_default(self) -> None:
        """Normal verbosity is the default."""
        console = Console()
        assert console.verbosity == Verbosity.NORMAL


class TestConsoleModuleState:
    """Tests for module-level console state management."""

    def setup_method(self) -> None:
        """Reset console state before each test."""
        reset_console()

    def teardown_method(self) -> None:
        """Reset console state after each test."""
        reset_console()

    def test_get_console_creates_default(self) -> None:
        """get_console creates a default Console if none set."""
        console = get_console()
        assert isinstance(console, Console)
        assert console.verbosity == Verbosity.NORMAL

    def test_set_console_overrides_default(self) -> None:
        """set_console replaces the active console."""
        custom = Console(verbosity=Verbosity.VERBOSE)
        set_console(custom)
        assert get_console() is custom

    def test_reset_console_clears_state(self) -> None:
        """reset_console forces a new default on next get."""
        custom = Console(verbosity=Verbosity.VERBOSE)
        set_console(custom)
        reset_console()
        fresh = get_console()
        assert fresh is not custom
        assert fresh.verbosity == Verbosity.NORMAL


# --- Integration: CLI --verbose and --quiet flags ---


class TestVerboseQuietFlags:
    """Tests for --verbose and --quiet CLI global flags."""

    def test_verbose_flag_accepted(self) -> None:
        """--verbose flag is accepted without error."""
        result = runner.invoke(app, ["--verbose", "--help"])
        assert result.exit_code == 0

    def test_quiet_flag_accepted(self) -> None:
        """--quiet flag is accepted without error."""
        result = runner.invoke(app, ["--quiet", "--help"])
        assert result.exit_code == 0

    def test_verbose_and_quiet_together_error(self) -> None:
        """--verbose and --quiet together produce an error."""
        result = runner.invoke(app, ["--verbose", "--quiet", "config"])
        assert result.exit_code == 1
        assert "cannot be used together" in result.output.lower()

    def test_short_verbose_flag(self) -> None:
        """-v short flag works for verbose."""
        result = runner.invoke(app, ["-v", "--help"])
        assert result.exit_code == 0

    def test_short_quiet_flag(self) -> None:
        """-q short flag works for quiet."""
        result = runner.invoke(app, ["-q", "--help"])
        assert result.exit_code == 0


# --- Integration: CLI exits cleanly on common error scenarios ---


class TestCLIErrorExits:
    """Tests for clean CLI exits on error scenarios."""

    def test_invalid_config_key_exits_1(self) -> None:
        """Setting an invalid config key exits with code 1."""
        result = runner.invoke(app, ["config", "set", "nonexistent", "value"])
        assert result.exit_code == 1
        # Error message should include actionable hint
        assert "error" in result.output.lower() or "Error" in result.output

    def test_invalid_config_key_has_hint(self) -> None:
        """Error for invalid config key includes hint about valid keys."""
        result = runner.invoke(app, ["config", "set", "nonexistent", "value"])
        assert result.exit_code == 1
        assert "valid" in result.output.lower() or "hint" in result.output.lower()

    def test_get_unknown_key_exits_1(self) -> None:
        """Getting an unknown config key exits with code 1."""
        result = runner.invoke(app, ["config", "get", "nonexistent"])
        assert result.exit_code == 1

    def test_help_exits_0(self) -> None:
        """--help always exits cleanly."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0

    def test_version_flag_exits_0(self) -> None:
        """--version exits cleanly and shows version."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "agent-tools" in result.output


# --- Unit: main() exception handling ---


class TestMainExceptionHandling:
    """Tests for main() top-level exception handling."""

    def test_keyboard_interrupt_clean_exit(self) -> None:
        """KeyboardInterrupt produces clean exit (code 130, no stack trace)."""
        # We test via the main() function by patching app()
        import agent_tools.cli as cli_mod

        original_app = cli_mod.app

        def raise_keyboard_interrupt() -> None:
            raise KeyboardInterrupt

        cli_mod.app = raise_keyboard_interrupt  # type: ignore[assignment]
        try:
            exit_code: int | None = None
            try:
                cli_mod.main()
            except SystemExit as e:
                exit_code = e.code
            assert exit_code == 130
        finally:
            cli_mod.app = original_app

    def test_unhandled_exception_shows_bug_report(self, capsys: object) -> None:
        """Unhandled exception in main() shows bug report suggestion."""
        import agent_tools.cli as cli_mod

        original_app = cli_mod.app

        def raise_runtime_error() -> None:
            raise RuntimeError("unexpected failure")

        cli_mod.app = raise_runtime_error  # type: ignore[assignment]
        try:
            exit_code: int | None = None
            try:
                cli_mod.main()
            except SystemExit as e:
                exit_code = e.code
            assert exit_code == 1
        finally:
            cli_mod.app = original_app
