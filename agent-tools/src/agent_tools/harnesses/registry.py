"""Adapter registry for looking up harness adapters by name."""

from __future__ import annotations

from agent_tools.harnesses.base import HarnessAdapter


class HarnessNotFoundError(Exception):
    """Raised when a harness name cannot be resolved to an adapter."""

    def __init__(self, name: str, available: list[str]) -> None:
        self.name = name
        self.available = available
        available_str = ", ".join(sorted(available)) if available else "(none)"
        super().__init__(
            f"Unknown harness {name!r}. Available harnesses: {available_str}"
        )


class HarnessRegistry:
    """Registry that maps harness names to adapter factories.

    Adapters are registered by a canonical name string and can be
    retrieved later via :meth:`get`.  The registry also supports
    auto-detection: :meth:`detect_all` returns every adapter whose
    ``detect()`` method returns ``True``.
    """

    def __init__(self) -> None:
        self._adapters: dict[str, HarnessAdapter] = {}

    def register(self, name: str, adapter: HarnessAdapter) -> None:
        """Register an adapter under *name*.

        Args:
            name: Canonical name for the harness (e.g. ``"claude-code"``).
            adapter: An object satisfying the :class:`HarnessAdapter` protocol.
        """
        self._adapters[name] = adapter

    def get(self, name: str) -> HarnessAdapter:
        """Retrieve a registered adapter by name.

        Args:
            name: The canonical harness name.

        Returns:
            The registered :class:`HarnessAdapter`.

        Raises:
            HarnessNotFoundError: If *name* is not registered.
        """
        try:
            return self._adapters[name]
        except KeyError:
            raise HarnessNotFoundError(name, list(self._adapters.keys())) from None

    def list_harnesses(self) -> list[str]:
        """Return sorted list of all registered harness names."""
        return sorted(self._adapters.keys())

    def detect_all(self) -> list[tuple[str, HarnessAdapter]]:
        """Return all adapters whose ``detect()`` reports active.

        Returns:
            List of ``(name, adapter)`` tuples for every detected harness,
            sorted by name for deterministic ordering.
        """
        detected: list[tuple[str, HarnessAdapter]] = []
        for name in sorted(self._adapters):
            adapter = self._adapters[name]
            if adapter.detect():
                detected.append((name, adapter))
        return detected
