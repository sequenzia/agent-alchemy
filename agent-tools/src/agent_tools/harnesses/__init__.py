"""Harness adapters for AI coding harness file placement."""

from pathlib import Path

from agent_tools.harnesses.base import HarnessAdapter
from agent_tools.harnesses.claude_code import ClaudeCodeAdapter
from agent_tools.harnesses.codex import CodexAdapter
from agent_tools.harnesses.cursor import CursorWindsurfAdapter
from agent_tools.harnesses.opencode import OpenCodeAdapter
from agent_tools.harnesses.registry import HarnessNotFoundError, HarnessRegistry

__all__ = [
    "ClaudeCodeAdapter",
    "CodexAdapter",
    "CursorWindsurfAdapter",
    "HarnessAdapter",
    "HarnessNotFoundError",
    "HarnessRegistry",
    "OpenCodeAdapter",
    "create_default_registry",
]


def create_default_registry(
    project_root: Path | None = None,
) -> HarnessRegistry:
    """Create a :class:`HarnessRegistry` pre-populated with all built-in adapters.

    Args:
        project_root: Workspace root passed to each adapter.  Defaults to
            the current working directory when ``None``.

    Returns:
        A registry with ``claude-code``, ``opencode``, ``cursor``, and
        ``codex`` adapters registered.
    """
    root = project_root or Path.cwd()
    registry = HarnessRegistry()
    registry.register("claude-code", ClaudeCodeAdapter(project_root=root))
    registry.register("opencode", OpenCodeAdapter(project_root=root))
    registry.register("cursor", CursorWindsurfAdapter(project_root=root))
    registry.register("codex", CodexAdapter(project_root=root))
    return registry
