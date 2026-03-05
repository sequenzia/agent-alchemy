"""Git repository source adapter for skill discovery and retrieval."""

from __future__ import annotations

import logging
import re
import subprocess
import time
from pathlib import Path

from agent_tools.models import SkillContent, SkillInfo
from agent_tools.sources.local import LocalSourceAdapter

logger = logging.getLogger(__name__)

# Default cache directory for cloned repos.
DEFAULT_CACHE_DIR = Path.home() / ".cache" / "agent-tools" / "repos"

# Default cache TTL in seconds (24 hours).
DEFAULT_CACHE_TTL = 24 * 60 * 60

# Patterns for validating git URLs.
_HTTPS_PATTERN = re.compile(
    r"^https?://[^\s/]+/[^\s/]+(?:/[^\s/]+)*(?:\.git)?/?$"
)
_SSH_PROTOCOL_PATTERN = re.compile(
    r"^ssh://(?:[^@\s]+@)?[^\s/]+/[^\s]+(?:\.git)?/?$"
)
_SSH_SHORTHAND_PATTERN = re.compile(
    r"^[^@\s]+@[^\s:/]+:[^\s]+(?:\.git)?/?$"
)


def is_valid_git_url(url: str) -> bool:
    """Check whether *url* looks like a valid HTTPS or SSH git URL.

    Args:
        url: The URL string to validate.

    Returns:
        True if the URL matches a known git URL pattern.
    """
    return bool(
        _HTTPS_PATTERN.match(url)
        or _SSH_PROTOCOL_PATTERN.match(url)
        or _SSH_SHORTHAND_PATTERN.match(url)
    )


def parse_repo_name(url: str) -> str:
    """Derive a filesystem-safe cache key from a git URL.

    Examples:
        https://github.com/org/repo.git  -> github.com_org_repo
        git@github.com:org/repo.git      -> github.com_org_repo
    """
    cleaned = url.rstrip("/")
    if cleaned.endswith(".git"):
        cleaned = cleaned[:-4]

    # SSH shorthand: git@host:org/repo
    if ":" in cleaned and not cleaned.startswith("http"):
        # Strip ssh:// prefix if present
        cleaned = re.sub(r"^ssh://", "", cleaned)
        # Strip user@ prefix
        cleaned = re.sub(r"^[^@]+@", "", cleaned)
        # Replace : with /
        cleaned = cleaned.replace(":", "/", 1)

    # HTTPS: strip protocol
    cleaned = re.sub(r"^https?://", "", cleaned)

    # Replace path separators with underscores for a flat filename
    return re.sub(r"[/\\]+", "_", cleaned)


def _cache_is_stale(repo_dir: Path, ttl_seconds: int) -> bool:
    """Check whether a cached repo clone is older than *ttl_seconds*.

    Staleness is determined from a ``.fetch_timestamp`` marker file
    written after each successful clone or fetch.
    """
    marker = repo_dir / ".fetch_timestamp"
    if not marker.exists():
        return True
    try:
        ts = float(marker.read_text(encoding="utf-8").strip())
    except (ValueError, OSError):
        return True
    return (time.time() - ts) > ttl_seconds


def _write_fetch_marker(repo_dir: Path) -> None:
    """Write a timestamp marker after a successful fetch/clone."""
    marker = repo_dir / ".fetch_timestamp"
    marker.write_text(str(time.time()), encoding="utf-8")


def _run_git(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Run a git command and return the result.

    Raises:
        GitSourceError: On non-zero exit code.
    """
    cmd = ["git", *args]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=cwd,
        )
    except FileNotFoundError:
        raise GitSourceError(
            "git is not installed or not on PATH. "
            "Install git and try again."
        )
    except subprocess.TimeoutExpired:
        raise GitSourceError(
            "git command timed out. Check your network connection and try again."
        )
    return result


class GitSourceError(Exception):
    """Raised when a git operation fails.

    Attributes:
        message: Human-readable error description.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class GitSourceAdapter:
    """Discovers and retrieves skills from a remote git repository.

    The repository is shallow-cloned (or fetched) into a local cache
    directory.  Subsequent calls reuse the cache unless the configured
    TTL has expired.

    Args:
        url: HTTPS or SSH git URL of the repository.
        cache_dir: Root directory for cached clones.
            Defaults to ``~/.cache/agent-tools/repos/``.
        cache_ttl: Seconds before a cached clone is considered stale.
            Defaults to 86400 (24 hours).
    """

    def __init__(
        self,
        url: str,
        cache_dir: Path | None = None,
        cache_ttl: int = DEFAULT_CACHE_TTL,
    ) -> None:
        if not is_valid_git_url(url):
            raise GitSourceError(
                f"Invalid git URL: {url!r}. "
                "Provide an HTTPS (https://...) or SSH (git@host:...) URL."
            )
        self._url = url
        self._cache_dir = cache_dir or DEFAULT_CACHE_DIR
        self._cache_ttl = cache_ttl
        self._repo_dir = self._cache_dir / parse_repo_name(url)

    # ------------------------------------------------------------------
    # SourceAdapter interface
    # ------------------------------------------------------------------

    def list_skills(self) -> list[SkillInfo]:
        """Clone/fetch the repo and list all discovered skills."""
        self._ensure_repo()
        local = LocalSourceAdapter([self._repo_dir])
        skills = local.list_skills()
        # Re-tag source to show git origin
        return [
            SkillInfo(
                name=s.name,
                description=s.description,
                source=f"git:{self._url}",
                path=s.path,
            )
            for s in skills
        ]

    def get_skill(self, name: str) -> SkillContent:
        """Retrieve skill content by name from the cached repo.

        Raises:
            KeyError: If the skill is not found.
        """
        self._ensure_repo()
        local = LocalSourceAdapter([self._repo_dir])
        content = local.get_skill(name)
        # Re-tag the info source
        retagged = SkillInfo(
            name=content.info.name,
            description=content.info.description,
            source=f"git:{self._url}",
            path=content.info.path,
        )
        return SkillContent(info=retagged, files=content.files)

    def search(self, query: str) -> list[SkillInfo]:
        """Search skills in the cached repo by substring match."""
        self._ensure_repo()
        local = LocalSourceAdapter([self._repo_dir])
        results = local.search(query)
        return [
            SkillInfo(
                name=s.name,
                description=s.description,
                source=f"git:{self._url}",
                path=s.path,
            )
            for s in results
        ]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @property
    def repo_dir(self) -> Path:
        """Return the local cache path for this repo."""
        return self._repo_dir

    def _ensure_repo(self) -> None:
        """Clone the repo if missing, or fetch if the cache is stale."""
        if self._repo_dir.exists() and (self._repo_dir / ".git").is_dir():
            if not _cache_is_stale(self._repo_dir, self._cache_ttl):
                logger.debug("Cache hit for %s", self._url)
                return
            self._fetch()
        else:
            self._clone()

    def _clone(self) -> None:
        """Shallow clone the repo into the cache directory."""
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        result = _run_git([
            "clone",
            "--depth", "1",
            "--single-branch",
            self._url,
            str(self._repo_dir),
        ])
        if result.returncode != 0:
            stderr = result.stderr.strip()
            # Detect auth failures
            if any(
                hint in stderr.lower()
                for hint in ("authentication", "permission denied", "publickey", "403", "401")
            ):
                raise GitSourceError(
                    f"Authentication failed for {self._url}. "
                    "Ensure your SSH keys or HTTPS credentials are configured. "
                    "For SSH: ssh-add ~/.ssh/id_ed25519 or check ~/.ssh/config. "
                    "For HTTPS: run 'git credential approve' or set a personal access token."
                )
            raise GitSourceError(
                f"Failed to clone {self._url}: {stderr}. "
                "Check the URL and your network connection, then try again."
            )
        _write_fetch_marker(self._repo_dir)

    def _fetch(self) -> None:
        """Fetch updates for an already-cloned repo."""
        result = _run_git(["fetch", "--depth", "1"], cwd=self._repo_dir)
        if result.returncode != 0:
            stderr = result.stderr.strip()
            if any(
                hint in stderr.lower()
                for hint in ("authentication", "permission denied", "publickey", "403", "401")
            ):
                raise GitSourceError(
                    f"Authentication failed fetching {self._url}. "
                    "Ensure your SSH keys or HTTPS credentials are configured."
                )
            raise GitSourceError(
                f"Failed to fetch updates for {self._url}: {stderr}. "
                "Check your network connection and try again."
            )
        # Reset working tree to match fetched HEAD
        _run_git(["reset", "--hard", "FETCH_HEAD"], cwd=self._repo_dir)
        _write_fetch_marker(self._repo_dir)
