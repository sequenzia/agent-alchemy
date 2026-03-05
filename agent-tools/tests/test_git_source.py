"""Tests for the git repository source adapter."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from agent_tools.models import SkillContent
from agent_tools.sources.git import (
    DEFAULT_CACHE_TTL,
    GitSourceAdapter,
    GitSourceError,
    _cache_is_stale,
    _write_fetch_marker,
    is_valid_git_url,
    parse_repo_name,
)

# ---------------------------------------------------------------------------
# Unit: Git URL parsing and validation
# ---------------------------------------------------------------------------


class TestIsValidGitUrl:
    """Tests for git URL validation."""

    def test_https_url(self) -> None:
        assert is_valid_git_url("https://github.com/org/repo.git") is True

    def test_https_url_no_dotgit(self) -> None:
        assert is_valid_git_url("https://github.com/org/repo") is True

    def test_https_url_trailing_slash(self) -> None:
        assert is_valid_git_url("https://github.com/org/repo/") is True

    def test_http_url(self) -> None:
        assert is_valid_git_url("http://github.com/org/repo.git") is True

    def test_ssh_shorthand(self) -> None:
        assert is_valid_git_url("git@github.com:org/repo.git") is True

    def test_ssh_shorthand_no_dotgit(self) -> None:
        assert is_valid_git_url("git@github.com:org/repo") is True

    def test_ssh_protocol(self) -> None:
        assert is_valid_git_url("ssh://git@github.com/org/repo.git") is True

    def test_invalid_empty(self) -> None:
        assert is_valid_git_url("") is False

    def test_invalid_plain_text(self) -> None:
        assert is_valid_git_url("not-a-url") is False

    def test_invalid_local_path(self) -> None:
        assert is_valid_git_url("/home/user/repo") is False

    def test_invalid_ftp(self) -> None:
        assert is_valid_git_url("ftp://example.com/repo.git") is False


class TestParseRepoName:
    """Tests for deriving cache keys from git URLs."""

    def test_https_url(self) -> None:
        assert parse_repo_name("https://github.com/org/repo.git") == "github.com_org_repo"

    def test_https_url_no_dotgit(self) -> None:
        assert parse_repo_name("https://github.com/org/repo") == "github.com_org_repo"

    def test_ssh_shorthand(self) -> None:
        assert parse_repo_name("git@github.com:org/repo.git") == "github.com_org_repo"

    def test_ssh_protocol(self) -> None:
        assert parse_repo_name("ssh://git@github.com/org/repo.git") == "github.com_org_repo"

    def test_trailing_slash_stripped(self) -> None:
        assert parse_repo_name("https://github.com/org/repo/") == "github.com_org_repo"

    def test_nested_path(self) -> None:
        result = parse_repo_name("https://gitlab.com/group/subgroup/repo.git")
        assert result == "gitlab.com_group_subgroup_repo"


# ---------------------------------------------------------------------------
# Unit: Cache staleness logic
# ---------------------------------------------------------------------------


class TestCacheStaleness:
    """Tests for cache TTL checking."""

    def test_missing_marker_is_stale(self, tmp_path: Path) -> None:
        assert _cache_is_stale(tmp_path, DEFAULT_CACHE_TTL) is True

    def test_fresh_cache_is_not_stale(self, tmp_path: Path) -> None:
        _write_fetch_marker(tmp_path)
        assert _cache_is_stale(tmp_path, DEFAULT_CACHE_TTL) is False

    def test_expired_cache_is_stale(self, tmp_path: Path) -> None:
        marker = tmp_path / ".fetch_timestamp"
        marker.write_text(str(time.time() - 100000), encoding="utf-8")
        assert _cache_is_stale(tmp_path, DEFAULT_CACHE_TTL) is True

    def test_zero_ttl_always_stale(self, tmp_path: Path) -> None:
        _write_fetch_marker(tmp_path)
        assert _cache_is_stale(tmp_path, 0) is True

    def test_corrupt_marker_is_stale(self, tmp_path: Path) -> None:
        marker = tmp_path / ".fetch_timestamp"
        marker.write_text("not-a-number", encoding="utf-8")
        assert _cache_is_stale(tmp_path, DEFAULT_CACHE_TTL) is True


# ---------------------------------------------------------------------------
# Unit: Constructor validation
# ---------------------------------------------------------------------------


class TestGitSourceAdapterInit:
    """Tests for adapter construction and URL validation."""

    def test_invalid_url_raises(self) -> None:
        with pytest.raises(GitSourceError, match="Invalid git URL"):
            GitSourceAdapter("not-a-valid-url")

    def test_valid_https_url_accepted(self, tmp_path: Path) -> None:
        adapter = GitSourceAdapter(
            "https://github.com/org/repo.git",
            cache_dir=tmp_path,
        )
        assert adapter.repo_dir == tmp_path / "github.com_org_repo"

    def test_valid_ssh_url_accepted(self, tmp_path: Path) -> None:
        adapter = GitSourceAdapter(
            "git@github.com:org/repo.git",
            cache_dir=tmp_path,
        )
        assert adapter.repo_dir == tmp_path / "github.com_org_repo"


# ---------------------------------------------------------------------------
# Unit: Error handling with mocked git
# ---------------------------------------------------------------------------


class TestGitErrors:
    """Tests for error handling during clone/fetch operations."""

    def test_clone_auth_failure_suggests_credentials(self, tmp_path: Path) -> None:
        adapter = GitSourceAdapter(
            "https://github.com/private/repo.git",
            cache_dir=tmp_path,
        )
        fake_result = subprocess.CompletedProcess(
            args=[], returncode=128, stdout="", stderr="Authentication failed for 'https://github.com/private/repo.git'"
        )
        with patch("agent_tools.sources.git._run_git", return_value=fake_result):
            with pytest.raises(GitSourceError, match="Authentication failed"):
                adapter.list_skills()

    def test_clone_network_failure_suggests_retry(self, tmp_path: Path) -> None:
        adapter = GitSourceAdapter(
            "https://github.com/org/repo.git",
            cache_dir=tmp_path,
        )
        fake_result = subprocess.CompletedProcess(
            args=[], returncode=128, stdout="", stderr="Could not resolve host: github.com"
        )
        with patch("agent_tools.sources.git._run_git", return_value=fake_result):
            with pytest.raises(GitSourceError, match="try again"):
                adapter.list_skills()

    def test_private_repo_publickey_failure(self, tmp_path: Path) -> None:
        adapter = GitSourceAdapter(
            "git@github.com:private/repo.git",
            cache_dir=tmp_path,
        )
        fake_result = subprocess.CompletedProcess(
            args=[], returncode=128, stdout="", stderr="Permission denied (publickey)"
        )
        with patch("agent_tools.sources.git._run_git", return_value=fake_result):
            with pytest.raises(GitSourceError, match="SSH keys"):
                adapter.list_skills()


# ---------------------------------------------------------------------------
# Unit: Cache reuse with mocked git
# ---------------------------------------------------------------------------


class TestCacheReuse:
    """Tests for cache hit/miss behavior."""

    def _setup_cached_repo(self, tmp_path: Path) -> Path:
        """Create a fake cached repo directory with a .git dir and a skill."""
        cache_dir = tmp_path / "cache"
        repo_dir = cache_dir / "github.com_org_repo"
        repo_dir.mkdir(parents=True)
        (repo_dir / ".git").mkdir()
        # Add a skill
        skill_dir = repo_dir / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\ndescription: Cached skill\n---\n# My Skill\n",
            encoding="utf-8",
        )
        return cache_dir

    def test_cache_hit_skips_fetch(self, tmp_path: Path) -> None:
        cache_dir = self._setup_cached_repo(tmp_path)
        repo_dir = cache_dir / "github.com_org_repo"
        _write_fetch_marker(repo_dir)

        adapter = GitSourceAdapter(
            "https://github.com/org/repo.git",
            cache_dir=cache_dir,
            cache_ttl=DEFAULT_CACHE_TTL,
        )
        with patch("agent_tools.sources.git._run_git") as mock_git:
            skills = adapter.list_skills()
            mock_git.assert_not_called()
        assert len(skills) == 1
        assert skills[0].name == "my-skill"

    def test_stale_cache_triggers_fetch(self, tmp_path: Path) -> None:
        cache_dir = self._setup_cached_repo(tmp_path)
        repo_dir = cache_dir / "github.com_org_repo"
        # Write old timestamp
        marker = repo_dir / ".fetch_timestamp"
        marker.write_text(str(time.time() - 100000), encoding="utf-8")

        adapter = GitSourceAdapter(
            "https://github.com/org/repo.git",
            cache_dir=cache_dir,
            cache_ttl=DEFAULT_CACHE_TTL,
        )
        fake_result = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        with patch("agent_tools.sources.git._run_git", return_value=fake_result) as mock_git:
            adapter.list_skills()
            # Should have called fetch + reset
            assert mock_git.call_count == 2

    def test_repo_with_no_skills_returns_empty(self, tmp_path: Path) -> None:
        cache_dir = tmp_path / "cache"
        repo_dir = cache_dir / "github.com_org_empty"
        repo_dir.mkdir(parents=True)
        (repo_dir / ".git").mkdir()
        _write_fetch_marker(repo_dir)

        adapter = GitSourceAdapter(
            "https://github.com/org/empty.git",
            cache_dir=cache_dir,
        )
        skills = adapter.list_skills()
        assert skills == []


# ---------------------------------------------------------------------------
# Unit: Source tagging
# ---------------------------------------------------------------------------


class TestSourceTagging:
    """Verify skills are tagged with git: source."""

    def test_list_skills_tagged_with_git_source(self, tmp_path: Path) -> None:
        cache_dir = tmp_path / "cache"
        repo_dir = cache_dir / "github.com_org_repo"
        repo_dir.mkdir(parents=True)
        (repo_dir / ".git").mkdir()
        skill = repo_dir / "tagged-skill"
        skill.mkdir()
        (skill / "SKILL.md").write_text("# Tagged\nA tagged skill.\n", encoding="utf-8")
        _write_fetch_marker(repo_dir)

        adapter = GitSourceAdapter(
            "https://github.com/org/repo.git",
            cache_dir=cache_dir,
        )
        skills = adapter.list_skills()
        assert skills[0].source == "git:https://github.com/org/repo.git"

    def test_get_skill_tagged_with_git_source(self, tmp_path: Path) -> None:
        cache_dir = tmp_path / "cache"
        repo_dir = cache_dir / "github.com_org_repo"
        repo_dir.mkdir(parents=True)
        (repo_dir / ".git").mkdir()
        skill = repo_dir / "tagged-skill"
        skill.mkdir()
        (skill / "SKILL.md").write_text("# Tagged\nA tagged skill.\n", encoding="utf-8")
        _write_fetch_marker(repo_dir)

        adapter = GitSourceAdapter(
            "https://github.com/org/repo.git",
            cache_dir=cache_dir,
        )
        content = adapter.get_skill("tagged-skill")
        assert isinstance(content, SkillContent)
        assert content.info.source == "git:https://github.com/org/repo.git"


# ---------------------------------------------------------------------------
# Integration: Clone and scan a real local bare repo
# ---------------------------------------------------------------------------


class TestIntegrationCloneAndScan:
    """Integration test: create a real git repo, clone it via the adapter."""

    def test_clone_local_repo_and_list_skills(self, tmp_path: Path) -> None:
        """Create a bare repo with skills, clone via adapter, list them."""
        # Create a bare repo
        bare_dir = tmp_path / "bare-repo.git"
        bare_dir.mkdir()
        subprocess.run(["git", "init", "--bare", str(bare_dir)], capture_output=True, check=True)

        # Create a working clone to populate the bare repo
        work_dir = tmp_path / "work"
        subprocess.run(
            ["git", "clone", str(bare_dir), str(work_dir)],
            capture_output=True, check=True,
        )

        # Add a skill
        skill_dir = work_dir / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\ndescription: Integration test skill\n---\n# My Skill\n",
            encoding="utf-8",
        )

        # Commit and push
        git_env = {
            "GIT_AUTHOR_NAME": "test",
            "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "test",
            "GIT_COMMITTER_EMAIL": "t@t",
            "HOME": str(tmp_path),
            "PATH": "/usr/bin:/usr/local/bin:/opt/homebrew/bin",
        }
        subprocess.run(
            ["git", "-C", str(work_dir), "add", "."],
            capture_output=True, check=True,
        )
        subprocess.run(
            ["git", "-C", str(work_dir), "commit", "-m", "add skill"],
            capture_output=True, check=True, env=git_env,
        )
        subprocess.run(
            ["git", "-C", str(work_dir), "push"],
            capture_output=True, check=True,
        )

        # Use the adapter to clone the bare repo via file:// URL
        cache_dir = tmp_path / "cache"
        # file:// URLs won't match HTTPS/SSH patterns, so we test with
        # the bare path directly — patch is_valid_git_url for this test
        url = f"file://{bare_dir}"
        with patch("agent_tools.sources.git.is_valid_git_url", return_value=True):
            adapter = GitSourceAdapter(url, cache_dir=cache_dir)
            skills = adapter.list_skills()

        assert len(skills) == 1
        assert skills[0].name == "my-skill"
        assert skills[0].description == "Integration test skill"
        assert skills[0].source == f"git:{url}"

        # get_skill should work too
        with patch("agent_tools.sources.git.is_valid_git_url", return_value=True):
            adapter2 = GitSourceAdapter(url, cache_dir=cache_dir)
            content = adapter2.get_skill("my-skill")
        assert "SKILL.md" in content.files

    def test_search_in_cloned_repo(self, tmp_path: Path) -> None:
        """Create a bare repo with skills, clone, search by keyword."""
        bare_dir = tmp_path / "bare-repo.git"
        bare_dir.mkdir()
        subprocess.run(["git", "init", "--bare", str(bare_dir)], capture_output=True, check=True)

        work_dir = tmp_path / "work"
        subprocess.run(
            ["git", "clone", str(bare_dir), str(work_dir)],
            capture_output=True, check=True,
        )

        # Add two skills
        for name, desc in [
            ("alpha", "Alpha analysis"),
            ("beta", "Beta builder"),
        ]:
            d = work_dir / name
            d.mkdir()
            (d / "SKILL.md").write_text(
                f"---\ndescription: {desc}\n---\n# {name}\n",
                encoding="utf-8",
            )

        git_env = {
            "GIT_AUTHOR_NAME": "test",
            "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "test",
            "GIT_COMMITTER_EMAIL": "t@t",
            "HOME": str(tmp_path),
            "PATH": "/usr/bin:/usr/local/bin:/opt/homebrew/bin",
        }
        subprocess.run(
            ["git", "-C", str(work_dir), "add", "."],
            capture_output=True, check=True,
        )
        subprocess.run(
            ["git", "-C", str(work_dir), "commit", "-m", "add skills"],
            capture_output=True, check=True, env=git_env,
        )
        subprocess.run(
            ["git", "-C", str(work_dir), "push"],
            capture_output=True, check=True,
        )

        url = f"file://{bare_dir}"
        cache_dir = tmp_path / "cache"
        with patch("agent_tools.sources.git.is_valid_git_url", return_value=True):
            adapter = GitSourceAdapter(url, cache_dir=cache_dir)
            results = adapter.search("analysis")

        assert len(results) == 1
        assert results[0].name == "alpha"
