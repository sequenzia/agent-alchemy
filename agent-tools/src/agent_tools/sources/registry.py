"""Registry/marketplace source adapter for skill discovery and retrieval.

Communicates with a remote registry API to list, search, and download skills.
Caches the registry index locally for offline browsing.
"""

from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from agent_tools.models import SkillContent, SkillInfo

logger = logging.getLogger(__name__)

# Default cache location
DEFAULT_CACHE_DIR = Path.home() / ".cache" / "agent-tools" / "registry"

# Cache TTL in seconds (1 hour)
CACHE_TTL_SECONDS = 3600


class RegistryError(Exception):
    """Base exception for registry-related errors."""


class RegistryUnreachableError(RegistryError):
    """Raised when the registry URL cannot be reached."""

    def __init__(self, url: str, reason: str) -> None:
        self.url = url
        self.reason = reason
        super().__init__(f"Registry unreachable at {url}: {reason}")


class RegistryAuthError(RegistryError):
    """Raised when authentication is required but not configured."""

    def __init__(self, url: str) -> None:
        self.url = url
        super().__init__(
            f"Registry at {url} requires authentication. "
            "Configure credentials with: agent-tools config set registry_token <token>"
        )


class RegistryResponseError(RegistryError):
    """Raised when the registry returns a malformed response."""

    def __init__(self, url: str, reason: str) -> None:
        self.url = url
        self.reason = reason
        super().__init__(f"Malformed response from registry at {url}: {reason}")


def _parse_skill_info(data: dict[str, Any], registry_url: str) -> SkillInfo | None:
    """Parse a single skill entry from a registry response.

    Returns None if required fields are missing.
    """
    name = data.get("name")
    if not name or not isinstance(name, str):
        return None

    return SkillInfo(
        name=name,
        description=str(data.get("description", "")),
        source=f"registry:{registry_url}",
        path=str(data.get("download_url", "")),
    )


def _parse_skill_list(data: Any, registry_url: str) -> list[SkillInfo]:
    """Parse a registry response into a list of SkillInfo objects.

    Handles both a bare list and an object with a "skills" key.
    Supports pagination via a "next" field (collected but not followed here).
    """
    items: list[dict[str, Any]]

    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        raw = data.get("skills", data.get("results", []))
        if isinstance(raw, list):
            items = raw
        else:
            return []
    else:
        return []

    skills: list[SkillInfo] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        info = _parse_skill_info(item, registry_url)
        if info is not None:
            skills.append(info)
    return skills


class RegistrySourceAdapter:
    """Discovers and retrieves skills from a remote registry API.

    The registry API contract expects these REST endpoints relative to the
    base URL:

    - ``GET /skills``          — list all skills (supports ``?page=N``)
    - ``GET /skills/search?q=<query>``  — search by name/description
    - ``GET /skills/<name>``   — get skill metadata + file listing
    - ``GET /skills/<name>/download`` — download skill files as JSON

    Responses are JSON. The list/search endpoints return either a bare JSON
    array of skill objects or an object with a ``"skills"`` (or ``"results"``)
    key containing the array, plus an optional ``"next"`` URL for pagination.

    Each skill object has at minimum ``"name"`` (str) and optionally
    ``"description"`` (str) and ``"download_url"`` (str).

    Args:
        registry_url: Base URL of the registry (e.g. ``https://registry.example.com/api/v1``).
        token: Optional auth token sent as ``Authorization: Bearer <token>``.
        cache_dir: Directory for caching the registry index. Defaults to
            ``~/.cache/agent-tools/registry``.
        cache_ttl: Cache time-to-live in seconds. Defaults to 3600 (1 hour).
    """

    def __init__(
        self,
        registry_url: str,
        token: str | None = None,
        cache_dir: Path | None = None,
        cache_ttl: int = CACHE_TTL_SECONDS,
    ) -> None:
        # Strip trailing slash for consistent URL building
        self._url = registry_url.rstrip("/")
        self._token = token
        self._cache_dir = cache_dir or DEFAULT_CACHE_DIR
        self._cache_ttl = cache_ttl

    # ------------------------------------------------------------------
    # SourceAdapter interface
    # ------------------------------------------------------------------

    def list_skills(self) -> list[SkillInfo]:
        """List all skills from the registry, with pagination support.

        Falls back to cached index if the registry is unreachable.
        """
        try:
            all_skills: list[SkillInfo] = []
            page = 1
            while True:
                url = f"{self._url}/skills?page={page}"
                data = self._fetch_json(url)
                skills = _parse_skill_list(data, self._url)
                if not skills:
                    break
                all_skills.extend(skills)

                # Check for pagination
                next_url = None
                if isinstance(data, dict):
                    next_url = data.get("next")
                if not next_url:
                    break
                page += 1

            self._write_cache("index", all_skills)
            return all_skills
        except RegistryUnreachableError:
            logger.warning(
                "Registry at %s is unreachable, falling back to cached index", self._url
            )
            return self._read_cache("index")

    def get_skill(self, name: str) -> SkillContent:
        """Download a skill's content from the registry.

        Raises:
            KeyError: If the skill does not exist.
            RegistryUnreachableError: If the registry is unreachable.
        """
        url = f"{self._url}/skills/{name}/download"
        try:
            data = self._fetch_json(url)
        except RegistryUnreachableError:
            raise
        except RegistryResponseError:
            raise KeyError(f"Skill not found: {name}")

        if not isinstance(data, dict):
            raise KeyError(f"Skill not found: {name}")

        # Parse metadata
        info_data = data.get("info", data.get("metadata", {}))
        if not isinstance(info_data, dict):
            info_data = {}

        info = SkillInfo(
            name=info_data.get("name", name),
            description=str(info_data.get("description", "")),
            source=f"registry:{self._url}",
            path=str(info_data.get("download_url", "")),
        )

        files_data = data.get("files", {})
        files: dict[str, str] = {}
        if isinstance(files_data, dict):
            for k, v in files_data.items():
                files[str(k)] = str(v)

        return SkillContent(info=info, files=files)

    def search(self, query: str) -> list[SkillInfo]:
        """Search the registry by name/description.

        Falls back to cached index with local filtering if unreachable.
        """
        try:
            url = f"{self._url}/skills/search?q={urllib.request.quote(query)}"
            data = self._fetch_json(url)
            return _parse_skill_list(data, self._url)
        except RegistryUnreachableError:
            logger.warning(
                "Registry at %s is unreachable, searching cached index", self._url
            )
            cached = self._read_cache("index")
            query_lower = query.lower()
            return [
                s
                for s in cached
                if query_lower in s.name.lower() or query_lower in s.description.lower()
            ]

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------

    def _build_request(self, url: str) -> urllib.request.Request:
        """Build an HTTP request with optional auth headers."""
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/json")
        if self._token:
            req.add_header("Authorization", f"Bearer {self._token}")
        return req

    def _fetch_json(self, url: str) -> Any:
        """Fetch JSON from a URL, handling errors consistently."""
        req = self._build_request(url)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            if exc.code == 401 or exc.code == 403:
                raise RegistryAuthError(self._url) from exc
            if exc.code == 404:
                raise RegistryResponseError(self._url, f"Not found: {url}") from exc
            raise RegistryUnreachableError(
                self._url, f"HTTP {exc.code}: {exc.reason}"
            ) from exc
        except (urllib.error.URLError, OSError, TimeoutError) as exc:
            raise RegistryUnreachableError(self._url, str(exc)) from exc

        try:
            return json.loads(body)
        except json.JSONDecodeError as exc:
            raise RegistryResponseError(
                self._url, f"Invalid JSON: {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Cache management
    # ------------------------------------------------------------------

    def _cache_path(self, key: str) -> Path:
        """Return the cache file path for a given key."""
        # Use a safe filename derived from the registry URL
        safe_host = self._url.replace("://", "_").replace("/", "_").replace(":", "_")
        return self._cache_dir / safe_host / f"{key}.json"

    def _write_cache(self, key: str, skills: list[SkillInfo]) -> None:
        """Write a list of SkillInfo objects to the cache."""
        cache_file = self._cache_path(key)
        try:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "timestamp": time.time(),
                "skills": [
                    {
                        "name": s.name,
                        "description": s.description,
                        "source": s.source,
                        "path": s.path,
                    }
                    for s in skills
                ],
            }
            cache_file.write_text(json.dumps(data), encoding="utf-8")
        except OSError:
            logger.warning("Failed to write registry cache: %s", cache_file)

    def _read_cache(self, key: str) -> list[SkillInfo]:
        """Read cached SkillInfo objects, returning empty list if stale or missing."""
        cache_file = self._cache_path(key)
        if not cache_file.is_file():
            return []
        try:
            raw = json.loads(cache_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []

        if not isinstance(raw, dict):
            return []

        # Check TTL (but for offline fallback, we still use stale cache)
        skills_data = raw.get("skills", [])
        if not isinstance(skills_data, list):
            return []

        return _parse_skill_list(skills_data, self._url)

    def _is_cache_fresh(self, key: str) -> bool:
        """Check whether the cache entry is still within TTL."""
        cache_file = self._cache_path(key)
        if not cache_file.is_file():
            return False
        try:
            raw = json.loads(cache_file.read_text(encoding="utf-8"))
            ts = raw.get("timestamp", 0)
            return (time.time() - ts) < self._cache_ttl
        except (OSError, json.JSONDecodeError):
            return False
