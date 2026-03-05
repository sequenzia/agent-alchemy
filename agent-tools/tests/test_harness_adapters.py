"""Tests for the four concrete harness adapter implementations."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent_tools.harnesses import (
    ClaudeCodeAdapter,
    CodexAdapter,
    CursorWindsurfAdapter,
    HarnessAdapter,
    OpenCodeAdapter,
    create_default_registry,
)

# ---------------------------------------------------------------------------
# Protocol compliance — each adapter satisfies HarnessAdapter
# ---------------------------------------------------------------------------


class TestProtocolCompliance:
    """All concrete adapters satisfy the HarnessAdapter protocol."""

    @pytest.mark.parametrize(
        "adapter_cls",
        [ClaudeCodeAdapter, OpenCodeAdapter, CursorWindsurfAdapter, CodexAdapter],
    )
    def test_is_harness_adapter(self, adapter_cls: type, tmp_path: Path) -> None:
        adapter = adapter_cls(project_root=tmp_path)
        assert isinstance(adapter, HarnessAdapter)


# ---------------------------------------------------------------------------
# Claude Code adapter
# ---------------------------------------------------------------------------


class TestClaudeCodeAdapter:
    """File path generation and auto-detection for Claude Code."""

    def test_get_skill_path(self, tmp_path: Path) -> None:
        adapter = ClaudeCodeAdapter(project_root=tmp_path)
        result = adapter.get_skill_path("deep-analysis")
        assert result == tmp_path / ".claude" / "skills" / "deep-analysis"

    def test_get_agent_path(self, tmp_path: Path) -> None:
        adapter = ClaudeCodeAdapter(project_root=tmp_path)
        result = adapter.get_agent_path("code-explorer")
        assert result == tmp_path / ".claude" / "agents" / "code-explorer"

    def test_harness_name(self, tmp_path: Path) -> None:
        adapter = ClaudeCodeAdapter(project_root=tmp_path)
        assert adapter.get_harness_name() == "Claude Code"

    def test_detect_true_when_claude_dir_exists(self, tmp_path: Path) -> None:
        (tmp_path / ".claude").mkdir()
        adapter = ClaudeCodeAdapter(project_root=tmp_path)
        assert adapter.detect() is True

    def test_detect_false_when_no_claude_dir(self, tmp_path: Path) -> None:
        adapter = ClaudeCodeAdapter(project_root=tmp_path)
        assert adapter.detect() is False

    def test_skill_path_is_absolute(self, tmp_path: Path) -> None:
        adapter = ClaudeCodeAdapter(project_root=tmp_path)
        assert adapter.get_skill_path("my-skill").is_absolute()


# ---------------------------------------------------------------------------
# OpenCode adapter
# ---------------------------------------------------------------------------


class TestOpenCodeAdapter:
    """File path generation and auto-detection for OpenCode."""

    def test_get_skill_path(self, tmp_path: Path) -> None:
        adapter = OpenCodeAdapter(project_root=tmp_path)
        result = adapter.get_skill_path("my-skill")
        assert result == tmp_path / ".opencode" / "skills" / "my-skill"

    def test_get_agent_path(self, tmp_path: Path) -> None:
        adapter = OpenCodeAdapter(project_root=tmp_path)
        result = adapter.get_agent_path("my-agent")
        assert result == tmp_path / ".opencode" / "agents" / "my-agent"

    def test_harness_name(self, tmp_path: Path) -> None:
        adapter = OpenCodeAdapter(project_root=tmp_path)
        assert adapter.get_harness_name() == "OpenCode"

    def test_detect_true_with_opencode_dir(self, tmp_path: Path) -> None:
        (tmp_path / ".opencode").mkdir()
        adapter = OpenCodeAdapter(project_root=tmp_path)
        assert adapter.detect() is True

    def test_detect_true_with_opencode_json(self, tmp_path: Path) -> None:
        (tmp_path / "opencode.json").write_text("{}")
        adapter = OpenCodeAdapter(project_root=tmp_path)
        assert adapter.detect() is True

    def test_detect_false_when_nothing(self, tmp_path: Path) -> None:
        adapter = OpenCodeAdapter(project_root=tmp_path)
        assert adapter.detect() is False


# ---------------------------------------------------------------------------
# Cursor / Windsurf adapter
# ---------------------------------------------------------------------------


class TestCursorWindsurfAdapter:
    """File path generation and auto-detection for Cursor/Windsurf."""

    def test_get_skill_path(self, tmp_path: Path) -> None:
        adapter = CursorWindsurfAdapter(project_root=tmp_path)
        result = adapter.get_skill_path("my-rule")
        assert result == tmp_path / ".cursor" / "rules" / "my-rule"

    def test_get_agent_path(self, tmp_path: Path) -> None:
        adapter = CursorWindsurfAdapter(project_root=tmp_path)
        result = adapter.get_agent_path("my-agent")
        assert result == tmp_path / ".cursor" / "agents" / "my-agent"

    def test_harness_name(self, tmp_path: Path) -> None:
        adapter = CursorWindsurfAdapter(project_root=tmp_path)
        assert adapter.get_harness_name() == "Cursor/Windsurf"

    def test_detect_true_with_cursor_dir(self, tmp_path: Path) -> None:
        (tmp_path / ".cursor").mkdir()
        adapter = CursorWindsurfAdapter(project_root=tmp_path)
        assert adapter.detect() is True

    def test_detect_true_with_windsurf_dir(self, tmp_path: Path) -> None:
        (tmp_path / ".windsurf").mkdir()
        adapter = CursorWindsurfAdapter(project_root=tmp_path)
        assert adapter.detect() is True

    def test_detect_false_when_nothing(self, tmp_path: Path) -> None:
        adapter = CursorWindsurfAdapter(project_root=tmp_path)
        assert adapter.detect() is False


# ---------------------------------------------------------------------------
# Codex adapter
# ---------------------------------------------------------------------------


class TestCodexAdapter:
    """File path generation and auto-detection for Codex."""

    def test_get_skill_path(self, tmp_path: Path) -> None:
        adapter = CodexAdapter(project_root=tmp_path)
        result = adapter.get_skill_path("my-skill")
        assert result == tmp_path / ".codex" / "skills" / "my-skill"

    def test_get_agent_path(self, tmp_path: Path) -> None:
        adapter = CodexAdapter(project_root=tmp_path)
        result = adapter.get_agent_path("my-agent")
        assert result == tmp_path / ".codex" / "agents" / "my-agent"

    def test_harness_name(self, tmp_path: Path) -> None:
        adapter = CodexAdapter(project_root=tmp_path)
        assert adapter.get_harness_name() == "Codex"

    def test_detect_true_with_codex_dir(self, tmp_path: Path) -> None:
        (tmp_path / ".codex").mkdir()
        adapter = CodexAdapter(project_root=tmp_path)
        assert adapter.detect() is True

    def test_detect_true_with_codex_md(self, tmp_path: Path) -> None:
        (tmp_path / "codex.md").write_text("# Codex instructions")
        adapter = CodexAdapter(project_root=tmp_path)
        assert adapter.detect() is True

    def test_detect_true_with_agents_md(self, tmp_path: Path) -> None:
        (tmp_path / "AGENTS.md").write_text("# Agents")
        adapter = CodexAdapter(project_root=tmp_path)
        assert adapter.detect() is True

    def test_detect_false_when_nothing(self, tmp_path: Path) -> None:
        adapter = CodexAdapter(project_root=tmp_path)
        assert adapter.detect() is False


# ---------------------------------------------------------------------------
# Multiple harnesses detected (edge case)
# ---------------------------------------------------------------------------


class TestMultipleHarnessDetection:
    """When multiple harnesses are detected, detect_all returns all of them."""

    def test_two_harnesses_detected(self, tmp_path: Path) -> None:
        (tmp_path / ".claude").mkdir()
        (tmp_path / ".cursor").mkdir()
        registry = create_default_registry(project_root=tmp_path)
        detected = registry.detect_all()
        names = [name for name, _ in detected]
        assert "claude-code" in names
        assert "cursor" in names
        assert len(names) == 2

    def test_all_four_harnesses_detected(self, tmp_path: Path) -> None:
        (tmp_path / ".claude").mkdir()
        (tmp_path / ".opencode").mkdir()
        (tmp_path / ".cursor").mkdir()
        (tmp_path / ".codex").mkdir()
        registry = create_default_registry(project_root=tmp_path)
        detected = registry.detect_all()
        names = [name for name, _ in detected]
        assert sorted(names) == ["claude-code", "codex", "cursor", "opencode"]

    def test_no_harnesses_detected(self, tmp_path: Path) -> None:
        registry = create_default_registry(project_root=tmp_path)
        detected = registry.detect_all()
        assert detected == []


# ---------------------------------------------------------------------------
# Target directory creation (edge case)
# ---------------------------------------------------------------------------


class TestDirectoryCreation:
    """Paths returned by adapters can be used to create directories."""

    @pytest.mark.parametrize(
        "adapter_cls",
        [ClaudeCodeAdapter, OpenCodeAdapter, CursorWindsurfAdapter, CodexAdapter],
    )
    def test_skill_parent_can_be_created(
        self, adapter_cls: type, tmp_path: Path
    ) -> None:
        adapter = adapter_cls(project_root=tmp_path)
        skill_path = adapter.get_skill_path("test-skill")
        skill_path.mkdir(parents=True, exist_ok=True)
        assert skill_path.is_dir()

    @pytest.mark.parametrize(
        "adapter_cls",
        [ClaudeCodeAdapter, OpenCodeAdapter, CursorWindsurfAdapter, CodexAdapter],
    )
    def test_agent_parent_can_be_created(
        self, adapter_cls: type, tmp_path: Path
    ) -> None:
        adapter = adapter_cls(project_root=tmp_path)
        agent_path = adapter.get_agent_path("test-agent")
        agent_path.mkdir(parents=True, exist_ok=True)
        assert agent_path.is_dir()


# ---------------------------------------------------------------------------
# Default registry factory
# ---------------------------------------------------------------------------


class TestCreateDefaultRegistry:
    """create_default_registry returns a fully-populated registry."""

    def test_all_four_registered(self, tmp_path: Path) -> None:
        registry = create_default_registry(project_root=tmp_path)
        names = registry.list_harnesses()
        assert sorted(names) == ["claude-code", "codex", "cursor", "opencode"]

    def test_get_each_adapter(self, tmp_path: Path) -> None:
        registry = create_default_registry(project_root=tmp_path)
        assert registry.get("claude-code").get_harness_name() == "Claude Code"
        assert registry.get("opencode").get_harness_name() == "OpenCode"
        assert registry.get("cursor").get_harness_name() == "Cursor/Windsurf"
        assert registry.get("codex").get_harness_name() == "Codex"
