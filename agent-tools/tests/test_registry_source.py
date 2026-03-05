"""Tests for the registry/marketplace source adapter."""

from __future__ import annotations

import json
import time
import urllib.error
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from agent_tools.models import SkillContent, SkillInfo
from agent_tools.sources.registry import (
    RegistryAuthError,
    RegistryResponseError,
    RegistrySourceAdapter,
    RegistryUnreachableError,
    _parse_skill_info,
    _parse_skill_list,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SAMPLE_SKILLS = [
    {"name": "deep-analysis", "description": "Hub-and-spoke analysis engine"},
    {"name": "feature-dev", "description": "Feature development workflow"},
    {"name": "bug-killer", "description": "Hypothesis-driven debugging"},
]

SAMPLE_SKILL_DOWNLOAD = {
    "info": {
        "name": "deep-analysis",
        "description": "Hub-and-spoke analysis engine",
        "download_url": "https://registry.example.com/skills/deep-analysis/download",
    },
    "files": {
        "SKILL.md": "# Deep Analysis\nHub-and-spoke exploration.",
        "references/agents.md": "Agent configuration details.",
    },
}


def _make_adapter(
    url: str = "https://registry.example.com/api/v1",
    token: str | None = None,
    cache_dir: Path | None = None,
    cache_ttl: int = 3600,
) -> RegistrySourceAdapter:
    return RegistrySourceAdapter(
        registry_url=url,
        token=token,
        cache_dir=cache_dir,
        cache_ttl=cache_ttl,
    )


# ---------------------------------------------------------------------------
# Unit: Registry response parsing
# ---------------------------------------------------------------------------


class TestParseSkillInfo:
    """Tests for _parse_skill_info parsing."""

    def test_valid_entry(self) -> None:
        data = {"name": "my-skill", "description": "A great skill"}
        info = _parse_skill_info(data, "https://reg.example.com")
        assert info is not None
        assert info.name == "my-skill"
        assert info.description == "A great skill"
        assert info.source == "registry:https://reg.example.com"

    def test_missing_name_returns_none(self) -> None:
        assert _parse_skill_info({"description": "no name"}, "url") is None

    def test_empty_name_returns_none(self) -> None:
        assert _parse_skill_info({"name": ""}, "url") is None

    def test_non_string_name_returns_none(self) -> None:
        assert _parse_skill_info({"name": 123}, "url") is None

    def test_missing_description_defaults_empty(self) -> None:
        info = _parse_skill_info({"name": "x"}, "url")
        assert info is not None
        assert info.description == ""

    def test_download_url_stored_in_path(self) -> None:
        info = _parse_skill_info(
            {"name": "x", "download_url": "https://dl.example.com/x.tar.gz"}, "url"
        )
        assert info is not None
        assert info.path == "https://dl.example.com/x.tar.gz"


class TestParseSkillList:
    """Tests for _parse_skill_list parsing."""

    def test_bare_list(self) -> None:
        skills = _parse_skill_list(SAMPLE_SKILLS, "url")
        assert len(skills) == 3
        assert skills[0].name == "deep-analysis"

    def test_object_with_skills_key(self) -> None:
        data = {"skills": SAMPLE_SKILLS, "next": None}
        skills = _parse_skill_list(data, "url")
        assert len(skills) == 3

    def test_object_with_results_key(self) -> None:
        data = {"results": SAMPLE_SKILLS[:1]}
        skills = _parse_skill_list(data, "url")
        assert len(skills) == 1

    def test_empty_list(self) -> None:
        assert _parse_skill_list([], "url") == []

    def test_non_dict_items_skipped(self) -> None:
        skills = _parse_skill_list(["not-a-dict", {"name": "ok"}], "url")
        assert len(skills) == 1
        assert skills[0].name == "ok"

    def test_invalid_type_returns_empty(self) -> None:
        assert _parse_skill_list("not-a-list-or-dict", "url") == []

    def test_items_with_missing_name_skipped(self) -> None:
        data = [{"name": "good"}, {"description": "no-name"}]
        skills = _parse_skill_list(data, "url")
        assert len(skills) == 1


# ---------------------------------------------------------------------------
# Unit: Cache management
# ---------------------------------------------------------------------------


class TestCacheManagement:
    """Tests for cache read/write/freshness."""

    def test_write_and_read_cache(self, tmp_path: Path) -> None:
        adapter = _make_adapter(cache_dir=tmp_path)
        skills = [
            SkillInfo(name="cached-skill", description="From cache", source="registry:url", path="")
        ]
        adapter._write_cache("index", skills)
        result = adapter._read_cache("index")
        assert len(result) == 1
        assert result[0].name == "cached-skill"
        assert result[0].description == "From cache"

    def test_read_missing_cache_returns_empty(self, tmp_path: Path) -> None:
        adapter = _make_adapter(cache_dir=tmp_path)
        assert adapter._read_cache("nonexistent") == []

    def test_read_corrupted_cache_returns_empty(self, tmp_path: Path) -> None:
        adapter = _make_adapter(cache_dir=tmp_path)
        cache_file = adapter._cache_path("index")
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text("not valid json", encoding="utf-8")
        assert adapter._read_cache("index") == []

    def test_cache_freshness_check(self, tmp_path: Path) -> None:
        adapter = _make_adapter(cache_dir=tmp_path, cache_ttl=3600)
        skills = [SkillInfo(name="a", description="", source="", path="")]
        adapter._write_cache("index", skills)
        assert adapter._is_cache_fresh("index") is True

    def test_stale_cache_not_fresh(self, tmp_path: Path) -> None:
        adapter = _make_adapter(cache_dir=tmp_path, cache_ttl=1)
        cache_file = adapter._cache_path("index")
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        data = {"timestamp": time.time() - 100, "skills": [{"name": "old"}]}
        cache_file.write_text(json.dumps(data), encoding="utf-8")
        assert adapter._is_cache_fresh("index") is False

    def test_missing_cache_not_fresh(self, tmp_path: Path) -> None:
        adapter = _make_adapter(cache_dir=tmp_path)
        assert adapter._is_cache_fresh("missing") is False

    def test_cache_per_registry_url(self, tmp_path: Path) -> None:
        adapter1 = _make_adapter(url="https://reg1.example.com", cache_dir=tmp_path)
        adapter2 = _make_adapter(url="https://reg2.example.com", cache_dir=tmp_path)
        skills = [SkillInfo(name="s1", description="", source="", path="")]
        adapter1._write_cache("index", skills)
        # adapter2 should NOT see adapter1's cache
        assert adapter2._read_cache("index") == []


# ---------------------------------------------------------------------------
# Unit: HTTP fetch with mocked responses
# ---------------------------------------------------------------------------


class TestListSkills:
    """Tests for list_skills with mocked HTTP."""

    def test_list_skills_success(self, tmp_path: Path) -> None:
        adapter = _make_adapter(cache_dir=tmp_path)
        with patch.object(adapter, "_fetch_json", return_value=SAMPLE_SKILLS):
            skills = adapter.list_skills()
        assert len(skills) == 3
        assert skills[0].name == "deep-analysis"

    def test_list_skills_caches_result(self, tmp_path: Path) -> None:
        adapter = _make_adapter(cache_dir=tmp_path)
        with patch.object(adapter, "_fetch_json", return_value=SAMPLE_SKILLS):
            adapter.list_skills()
        cached = adapter._read_cache("index")
        assert len(cached) == 3

    def test_list_skills_falls_back_to_cache_when_offline(self, tmp_path: Path) -> None:
        adapter = _make_adapter(cache_dir=tmp_path)
        # Populate cache first
        skills = [SkillInfo(name="cached", description="offline", source="registry:url", path="")]
        adapter._write_cache("index", skills)
        # Make fetch fail
        with patch.object(
            adapter, "_fetch_json", side_effect=RegistryUnreachableError("url", "timeout")
        ):
            result = adapter.list_skills()
        assert len(result) == 1
        assert result[0].name == "cached"

    def test_list_skills_offline_no_cache_returns_empty(self, tmp_path: Path) -> None:
        adapter = _make_adapter(cache_dir=tmp_path)
        with patch.object(
            adapter, "_fetch_json", side_effect=RegistryUnreachableError("url", "timeout")
        ):
            result = adapter.list_skills()
        assert result == []

    def test_list_skills_pagination(self, tmp_path: Path) -> None:
        page1 = {"skills": [{"name": "s1"}], "next": "page2"}
        page2 = {"skills": [{"name": "s2"}], "next": None}

        call_count = 0

        def mock_fetch(url: str) -> dict[str, Any]:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return page1
            return page2

        adapter = _make_adapter(cache_dir=tmp_path)
        with patch.object(adapter, "_fetch_json", side_effect=mock_fetch):
            skills = adapter.list_skills()
        assert len(skills) == 2
        assert {s.name for s in skills} == {"s1", "s2"}

    def test_empty_registry_returns_empty(self, tmp_path: Path) -> None:
        adapter = _make_adapter(cache_dir=tmp_path)
        with patch.object(adapter, "_fetch_json", return_value=[]):
            skills = adapter.list_skills()
        assert skills == []


class TestSearch:
    """Tests for search with mocked HTTP."""

    def test_search_success(self, tmp_path: Path) -> None:
        adapter = _make_adapter(cache_dir=tmp_path)
        result_data = [{"name": "deep-analysis", "description": "Analysis engine"}]
        with patch.object(adapter, "_fetch_json", return_value=result_data):
            results = adapter.search("analysis")
        assert len(results) == 1
        assert results[0].name == "deep-analysis"

    def test_search_no_match(self, tmp_path: Path) -> None:
        adapter = _make_adapter(cache_dir=tmp_path)
        with patch.object(adapter, "_fetch_json", return_value=[]):
            results = adapter.search("zzz-nonexistent")
        assert results == []

    def test_search_falls_back_to_cache(self, tmp_path: Path) -> None:
        adapter = _make_adapter(cache_dir=tmp_path)
        skills = [
            SkillInfo(name="deep-analysis", description="Analysis", source="", path=""),
            SkillInfo(name="bug-killer", description="Debug", source="", path=""),
        ]
        adapter._write_cache("index", skills)
        with patch.object(
            adapter, "_fetch_json", side_effect=RegistryUnreachableError("url", "timeout")
        ):
            results = adapter.search("analysis")
        assert len(results) == 1
        assert results[0].name == "deep-analysis"


class TestGetSkill:
    """Tests for get_skill with mocked HTTP."""

    def test_get_skill_success(self, tmp_path: Path) -> None:
        adapter = _make_adapter(cache_dir=tmp_path)
        with patch.object(adapter, "_fetch_json", return_value=SAMPLE_SKILL_DOWNLOAD):
            content = adapter.get_skill("deep-analysis")
        assert isinstance(content, SkillContent)
        assert content.info.name == "deep-analysis"
        assert "SKILL.md" in content.files
        assert "references/agents.md" in content.files

    def test_get_skill_not_found(self, tmp_path: Path) -> None:
        adapter = _make_adapter(cache_dir=tmp_path)
        with patch.object(
            adapter,
            "_fetch_json",
            side_effect=RegistryResponseError("url", "Not found"),
        ):
            with pytest.raises(KeyError, match="Skill not found"):
                adapter.get_skill("nonexistent")

    def test_get_skill_propagates_unreachable(self, tmp_path: Path) -> None:
        adapter = _make_adapter(cache_dir=tmp_path)
        with patch.object(
            adapter,
            "_fetch_json",
            side_effect=RegistryUnreachableError("url", "timeout"),
        ):
            with pytest.raises(RegistryUnreachableError):
                adapter.get_skill("any-skill")


# ---------------------------------------------------------------------------
# Unit: Error handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    """Tests for HTTP error handling in _fetch_json."""

    def test_unreachable_url_raises(self, tmp_path: Path) -> None:
        adapter = _make_adapter(
            url="https://nonexistent.invalid/api/v1", cache_dir=tmp_path
        )
        with pytest.raises(RegistryUnreachableError) as exc_info:
            adapter._fetch_json("https://nonexistent.invalid/api/v1/skills")
        assert "nonexistent.invalid" in str(exc_info.value)

    def test_auth_required_raises(self, tmp_path: Path) -> None:
        adapter = _make_adapter(cache_dir=tmp_path)
        exc = urllib.error.HTTPError(
            url="https://reg.example.com/skills",
            code=401,
            msg="Unauthorized",
            hdrs=MagicMock(),  # type: ignore[arg-type]
            fp=None,
        )
        with patch("urllib.request.urlopen", side_effect=exc):
            with pytest.raises(RegistryAuthError) as exc_info:
                adapter._fetch_json("https://reg.example.com/skills")
        assert "authentication" in str(exc_info.value).lower()
        assert "agent-tools config set registry_token" in str(exc_info.value)

    def test_forbidden_raises_auth_error(self, tmp_path: Path) -> None:
        adapter = _make_adapter(cache_dir=tmp_path)
        exc = urllib.error.HTTPError(
            url="url", code=403, msg="Forbidden", hdrs=MagicMock(), fp=None  # type: ignore[arg-type]
        )
        with patch("urllib.request.urlopen", side_effect=exc):
            with pytest.raises(RegistryAuthError):
                adapter._fetch_json("https://reg.example.com/skills")

    def test_404_raises_response_error(self, tmp_path: Path) -> None:
        adapter = _make_adapter(cache_dir=tmp_path)
        exc = urllib.error.HTTPError(
            url="url", code=404, msg="Not Found", hdrs=MagicMock(), fp=None  # type: ignore[arg-type]
        )
        with patch("urllib.request.urlopen", side_effect=exc):
            with pytest.raises(RegistryResponseError):
                adapter._fetch_json("https://reg.example.com/skills/missing")

    def test_500_raises_unreachable(self, tmp_path: Path) -> None:
        adapter = _make_adapter(cache_dir=tmp_path)
        exc = urllib.error.HTTPError(
            url="url", code=500, msg="Internal Server Error", hdrs=MagicMock(), fp=None  # type: ignore[arg-type]
        )
        with patch("urllib.request.urlopen", side_effect=exc):
            with pytest.raises(RegistryUnreachableError):
                adapter._fetch_json("https://reg.example.com/skills")

    def test_malformed_json_raises_response_error(self, tmp_path: Path) -> None:
        adapter = _make_adapter(cache_dir=tmp_path)
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"not json at all"
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        with patch("urllib.request.urlopen", return_value=mock_resp):
            with pytest.raises(RegistryResponseError, match="Invalid JSON"):
                adapter._fetch_json("https://reg.example.com/skills")

    def test_auth_token_sent_in_header(self, tmp_path: Path) -> None:
        adapter = _make_adapter(token="my-secret-token", cache_dir=tmp_path)
        req = adapter._build_request("https://reg.example.com/skills")
        assert req.get_header("Authorization") == "Bearer my-secret-token"

    def test_no_token_no_auth_header(self, tmp_path: Path) -> None:
        adapter = _make_adapter(cache_dir=tmp_path)
        req = adapter._build_request("https://reg.example.com/skills")
        assert req.get_header("Authorization") is None


# ---------------------------------------------------------------------------
# Integration: Full registry workflow with mock HTTP server
# ---------------------------------------------------------------------------


class _MockRegistryHandler(BaseHTTPRequestHandler):
    """A minimal HTTP handler simulating a registry API."""

    skills_db: list[dict[str, Any]] = SAMPLE_SKILLS  # type: ignore[assignment]
    download_db: dict[str, dict[str, Any]] = {"deep-analysis": SAMPLE_SKILL_DOWNLOAD}

    def do_GET(self) -> None:  # noqa: N802
        if self.path.startswith("/skills/search"):
            # Extract query
            query = ""
            if "?q=" in self.path:
                query = self.path.split("?q=", 1)[1].lower()
            results = [
                s for s in self.skills_db if query in s.get("name", "").lower()
                or query in s.get("description", "").lower()
            ]
            self._respond_json(results)
        elif self.path.endswith("/download"):
            name = self.path.split("/skills/")[1].split("/download")[0]
            if name in self.download_db:
                self._respond_json(self.download_db[name])
            else:
                self.send_error(404, "Not found")
        elif self.path.startswith("/skills"):
            self._respond_json(self.skills_db)
        else:
            self.send_error(404, "Not found")

    def _respond_json(self, data: Any) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        # Suppress log output during tests
        pass


@pytest.fixture()
def mock_registry_server() -> tuple[str, HTTPServer]:
    """Start a local HTTP server simulating a registry API."""
    server = HTTPServer(("127.0.0.1", 0), _MockRegistryHandler)
    port = server.server_address[1]
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}", server
    server.shutdown()


class TestIntegrationFullWorkflow:
    """Integration tests against a mock HTTP server."""

    def test_list_search_download_workflow(
        self, mock_registry_server: tuple[str, HTTPServer], tmp_path: Path
    ) -> None:
        url, _ = mock_registry_server
        adapter = RegistrySourceAdapter(
            registry_url=url, cache_dir=tmp_path
        )

        # List all skills
        all_skills = adapter.list_skills()
        assert len(all_skills) == 3
        names = {s.name for s in all_skills}
        assert "deep-analysis" in names

        # Search
        results = adapter.search("debug")
        assert len(results) == 1
        assert results[0].name == "bug-killer"

        # Download
        content = adapter.get_skill("deep-analysis")
        assert isinstance(content, SkillContent)
        assert content.info.name == "deep-analysis"
        assert "SKILL.md" in content.files

    def test_cache_survives_server_shutdown(
        self, mock_registry_server: tuple[str, HTTPServer], tmp_path: Path
    ) -> None:
        url, server = mock_registry_server
        adapter = RegistrySourceAdapter(
            registry_url=url, cache_dir=tmp_path
        )

        # Populate cache
        skills = adapter.list_skills()
        assert len(skills) == 3

        # Shut down server
        server.shutdown()

        # Create new adapter pointing to same (now dead) URL
        adapter2 = RegistrySourceAdapter(
            registry_url=url, cache_dir=tmp_path
        )
        cached = adapter2.list_skills()
        assert len(cached) == 3
        assert cached[0].name == "deep-analysis"

    def test_search_by_description_integration(
        self, mock_registry_server: tuple[str, HTTPServer], tmp_path: Path
    ) -> None:
        url, _ = mock_registry_server
        adapter = RegistrySourceAdapter(
            registry_url=url, cache_dir=tmp_path
        )
        results = adapter.search("analysis")
        assert any(s.name == "deep-analysis" for s in results)

    def test_get_nonexistent_skill_integration(
        self, mock_registry_server: tuple[str, HTTPServer], tmp_path: Path
    ) -> None:
        url, _ = mock_registry_server
        adapter = RegistrySourceAdapter(
            registry_url=url, cache_dir=tmp_path
        )
        with pytest.raises(KeyError, match="Skill not found"):
            adapter.get_skill("nonexistent-skill")
