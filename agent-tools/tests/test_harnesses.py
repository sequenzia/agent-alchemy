"""Tests for harness abstraction layer — adapter protocol and registry."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent_tools.harnesses import HarnessAdapter, HarnessNotFoundError, HarnessRegistry

# ---------------------------------------------------------------------------
# Mock adapter for testing
# ---------------------------------------------------------------------------


class MockHarness:
    """A minimal harness adapter used for protocol compliance tests."""

    def __init__(self, *, name: str = "mock", active: bool = False) -> None:
        self._name = name
        self._active = active

    def get_skill_path(self, skill_name: str) -> Path:
        return Path(f"/mock/skills/{skill_name}")

    def get_agent_path(self, agent_name: str) -> Path:
        return Path(f"/mock/agents/{agent_name}")

    def get_harness_name(self) -> str:
        return self._name

    def detect(self) -> bool:
        return self._active


# ---------------------------------------------------------------------------
# Protocol compliance
# ---------------------------------------------------------------------------


class TestProtocolCompliance:
    """Verify that a class implementing the four required methods satisfies HarnessAdapter."""

    def test_mock_adapter_is_harness_adapter(self) -> None:
        adapter = MockHarness()
        assert isinstance(adapter, HarnessAdapter)

    def test_get_skill_path_returns_path(self) -> None:
        adapter = MockHarness()
        result = adapter.get_skill_path("deep-analysis")
        assert isinstance(result, Path)
        assert "deep-analysis" in str(result)

    def test_get_agent_path_returns_path(self) -> None:
        adapter = MockHarness()
        result = adapter.get_agent_path("code-explorer")
        assert isinstance(result, Path)
        assert "code-explorer" in str(result)

    def test_get_harness_name_returns_str(self) -> None:
        adapter = MockHarness(name="Test Harness")
        assert adapter.get_harness_name() == "Test Harness"

    def test_detect_returns_bool(self) -> None:
        adapter = MockHarness(active=True)
        assert adapter.detect() is True

    def test_object_missing_method_is_not_adapter(self) -> None:
        """An object missing required methods does not satisfy the protocol."""

        class Incomplete:
            def get_skill_path(self, skill_name: str) -> Path:
                return Path(skill_name)

        assert not isinstance(Incomplete(), HarnessAdapter)


# ---------------------------------------------------------------------------
# Registry — lookup by name
# ---------------------------------------------------------------------------


class TestRegistryLookup:
    """Registry.get resolves adapters by name string."""

    def test_register_and_get(self) -> None:
        registry = HarnessRegistry()
        adapter = MockHarness(name="claude-code")
        registry.register("claude-code", adapter)
        assert registry.get("claude-code") is adapter

    def test_get_unknown_raises_harness_not_found(self) -> None:
        registry = HarnessRegistry()
        with pytest.raises(HarnessNotFoundError) as exc_info:
            registry.get("nonexistent")
        assert "nonexistent" in str(exc_info.value)
        assert exc_info.value.name == "nonexistent"

    def test_error_message_lists_available(self) -> None:
        registry = HarnessRegistry()
        registry.register("claude-code", MockHarness())
        registry.register("opencode", MockHarness())
        with pytest.raises(HarnessNotFoundError) as exc_info:
            registry.get("missing")
        msg = str(exc_info.value)
        assert "claude-code" in msg
        assert "opencode" in msg

    def test_list_harnesses(self) -> None:
        registry = HarnessRegistry()
        registry.register("b-harness", MockHarness())
        registry.register("a-harness", MockHarness())
        assert registry.list_harnesses() == ["a-harness", "b-harness"]

    def test_list_harnesses_empty(self) -> None:
        registry = HarnessRegistry()
        assert registry.list_harnesses() == []


# ---------------------------------------------------------------------------
# Registry — auto-detection
# ---------------------------------------------------------------------------


class TestRegistryDetection:
    """Registry.detect_all returns adapters whose detect() is True."""

    def test_detect_all_returns_active_only(self) -> None:
        registry = HarnessRegistry()
        registry.register("active", MockHarness(active=True))
        registry.register("inactive", MockHarness(active=False))
        detected = registry.detect_all()
        names = [name for name, _ in detected]
        assert names == ["active"]

    def test_detect_all_multiple_active(self) -> None:
        registry = HarnessRegistry()
        registry.register("a", MockHarness(active=True))
        registry.register("b", MockHarness(active=True))
        registry.register("c", MockHarness(active=False))
        detected = registry.detect_all()
        names = [name for name, _ in detected]
        assert names == ["a", "b"]

    def test_detect_all_none_active(self) -> None:
        registry = HarnessRegistry()
        registry.register("x", MockHarness(active=False))
        assert registry.detect_all() == []
