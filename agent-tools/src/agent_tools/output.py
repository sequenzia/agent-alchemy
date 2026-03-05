"""Colored terminal output and verbosity control for agent-tools.

Provides a Console wrapper around Rich that respects --verbose/--quiet flags
and automatically disables colors in non-TTY environments.
"""

from __future__ import annotations

import sys
from enum import IntEnum

from rich.console import Console as RichConsole
from rich.theme import Theme

_THEME = Theme(
    {
        "success": "bold green",
        "warning": "bold yellow",
        "error": "bold red",
        "info": "bold blue",
        "dim": "dim",
    }
)


class Verbosity(IntEnum):
    """Output verbosity levels."""

    QUIET = 0
    NORMAL = 1
    VERBOSE = 2


# Module-level state for the active console
_console: Console | None = None


class Console:
    """Colored terminal output with verbosity control.

    Wraps Rich's Console to provide success/warning/error/debug helpers
    that respect the current verbosity level. Colors are automatically
    disabled when stdout is not a TTY (e.g. piped output).
    """

    def __init__(self, verbosity: Verbosity = Verbosity.NORMAL) -> None:
        self.verbosity = verbosity
        force_terminal: bool | None = None
        # Let Rich auto-detect TTY; we don't force anything
        self._out = RichConsole(theme=_THEME, force_terminal=force_terminal)
        self._err = RichConsole(theme=_THEME, stderr=True, force_terminal=force_terminal)

    def success(self, message: str) -> None:
        """Print a success message (green). Suppressed in quiet mode."""
        if self.verbosity >= Verbosity.NORMAL:
            self._out.print(f"[success]{message}[/success]")

    def info(self, message: str) -> None:
        """Print an informational message. Suppressed in quiet mode."""
        if self.verbosity >= Verbosity.NORMAL:
            self._out.print(message)

    def warning(self, message: str) -> None:
        """Print a warning message (yellow). Always shown."""
        self._err.print(f"[warning]Warning:[/warning] {message}")

    def error(self, message: str, *, hint: str | None = None) -> None:
        """Print an error message (red) with optional actionable hint.

        Args:
            message: The error description.
            hint: An actionable suggestion for resolving the error.
        """
        self._err.print(f"[error]Error:[/error] {message}")
        if hint:
            self._err.print(f"  [dim]Hint: {hint}[/dim]")

    def debug(self, message: str) -> None:
        """Print a debug message. Only shown in verbose mode."""
        if self.verbosity >= Verbosity.VERBOSE:
            self._err.print(f"[dim][DEBUG] {message}[/dim]")

    def plain(self, message: str) -> None:
        """Print a plain message (no styling). Suppressed in quiet mode."""
        if self.verbosity >= Verbosity.NORMAL:
            self._out.print(message, highlight=False)

    def plain_always(self, message: str) -> None:
        """Print a plain message that is never suppressed."""
        self._out.print(message, highlight=False)


def get_console() -> Console:
    """Return the active console instance, creating a default if needed."""
    global _console  # noqa: PLW0603
    if _console is None:
        _console = Console()
    return _console


def set_console(console: Console) -> None:
    """Set the active console instance (used during CLI startup)."""
    global _console  # noqa: PLW0603
    _console = console


def reset_console() -> None:
    """Reset the active console to None (for testing)."""
    global _console  # noqa: PLW0603
    _console = None


def format_error_message(error: str, *, hint: str | None = None) -> str:
    """Format an error message with optional hint as plain text (no markup).

    Useful for contexts where Rich markup is not available (e.g. logging).

    Args:
        error: The error description.
        hint: An actionable suggestion.

    Returns:
        A formatted error string.
    """
    msg = f"Error: {error}"
    if hint:
        msg += f"\n  Hint: {hint}"
    return msg


def format_bug_report(exc: BaseException) -> str:
    """Format an unhandled exception into a user-friendly bug report message.

    Args:
        exc: The unhandled exception.

    Returns:
        A multi-line string suggesting the user file a bug report.
    """
    exc_type = type(exc).__name__
    exc_msg = str(exc) if str(exc) else "(no message)"
    return (
        f"An unexpected error occurred: {exc_type}: {exc_msg}\n"
        f"\n"
        f"This is a bug in agent-tools. Please report it at:\n"
        f"  https://github.com/agent-alchemy/agent-tools/issues\n"
        f"\n"
        f"Include the full output above and the command you ran.\n"
        f"Run with --verbose for additional debug information."
    )


def is_tty() -> bool:
    """Check if stdout is a TTY (terminal)."""
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
