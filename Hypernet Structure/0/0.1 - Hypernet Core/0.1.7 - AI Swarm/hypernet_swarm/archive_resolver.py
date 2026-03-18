"""
Hypernet Archive Resolver — Smart document access with local-first, GitHub fallback.

The Hypernet Structure (30K+ documents) is the shared knowledge base for all
projects. Individual projects (swarm, server, VR) need boot sequences, identity
profiles, governance standards, etc. But not everyone has the full archive locally.

Resolution order:
  1. Local filesystem (fastest — check configured archive root)
  2. GitHub raw content API (fallback — fetch individual files on demand)
  3. GitHub archive download (bulk — clone/download specific directories)

Usage:
    resolver = ArchiveResolver(archive_root="C:/Hypernet/Hypernet Structure")

    # Reads locally if available, fetches from GitHub if not
    content = resolver.read("2 - AI Accounts/2.1 - Claude Opus/Instances/README.md")

    # Check if a directory exists (locally or remote)
    exists = resolver.exists("2 - AI Accounts/2.1 - Claude Opus/Instances/Librarian")

    # List files in a directory
    files = resolver.listdir("2 - AI Accounts/2.1 - Claude Opus/Instances/Librarian")

    # Ensure a directory is available locally (download if needed)
    resolver.ensure_local("2 - AI Accounts/2.1 - Claude Opus")
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

log = logging.getLogger(__name__)

# Default GitHub repository for the Hypernet Structure
DEFAULT_GITHUB_REPO = "KosmoSuture/UnityHypernet"
DEFAULT_GITHUB_BRANCH = "main"
DEFAULT_GITHUB_BASE = "Hypernet Structure"

# Cache TTL for GitHub API responses (directory listings)
_CACHE_TTL_SECONDS = 300  # 5 minutes


class ArchiveResolver:
    """Smart document resolver: local-first, GitHub fallback.

    Provides transparent access to Hypernet Structure files regardless
    of whether they exist locally or need to be fetched from GitHub.
    """

    def __init__(
        self,
        archive_root: Optional[str] = None,
        github_repo: str = DEFAULT_GITHUB_REPO,
        github_branch: str = DEFAULT_GITHUB_BRANCH,
        github_base_path: str = DEFAULT_GITHUB_BASE,
        cache_dir: Optional[str] = None,
        offline: bool = False,
    ):
        """
        Args:
            archive_root: Local path to the Hypernet Structure directory.
                          If None, only GitHub access is available.
            github_repo: GitHub repository (owner/repo format).
            github_branch: Branch to fetch from.
            github_base_path: Path prefix within the repo where the Structure lives.
            cache_dir: Where to cache files downloaded from GitHub.
                       Defaults to archive_root or a temp directory.
            offline: If True, never make network requests.
        """
        self.archive_root = Path(archive_root) if archive_root else None
        self.github_repo = github_repo
        self.github_branch = github_branch
        self.github_base_path = github_base_path
        self.offline = offline

        # Cache for downloaded files
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        elif self.archive_root:
            self.cache_dir = self.archive_root  # Write alongside local files
        else:
            self.cache_dir = Path(os.environ.get("TEMP", "/tmp")) / "hypernet-cache"

        # In-memory cache for directory listings and file existence checks
        self._dir_cache: dict[str, tuple[float, list[str]]] = {}
        self._existence_cache: dict[str, tuple[float, bool]] = {}

        # Stats
        self.stats = {
            "local_hits": 0,
            "local_misses": 0,
            "github_fetches": 0,
            "github_errors": 0,
            "cache_hits": 0,
        }

    def _local_path(self, relative_path: str) -> Optional[Path]:
        """Get the local filesystem path for a relative archive path."""
        if not self.archive_root:
            return None
        return self.archive_root / relative_path

    def _github_raw_url(self, relative_path: str) -> str:
        """Build a raw.githubusercontent.com URL for a file."""
        # URL-encode spaces and special characters
        from urllib.parse import quote
        encoded = quote(f"{self.github_base_path}/{relative_path}")
        return (
            f"https://raw.githubusercontent.com/{self.github_repo}"
            f"/{self.github_branch}/{encoded}"
        )

    def _github_api_url(self, relative_path: str) -> str:
        """Build a GitHub API URL for directory listing."""
        from urllib.parse import quote
        encoded = quote(f"{self.github_base_path}/{relative_path}")
        return (
            f"https://api.github.com/repos/{self.github_repo}"
            f"/contents/{encoded}?ref={self.github_branch}"
        )

    def _fetch_url(self, url: str, accept: str = "text/plain") -> Optional[str]:
        """Fetch a URL with proper headers. Returns None on failure."""
        if self.offline:
            return None
        try:
            req = Request(url, headers={
                "User-Agent": "Hypernet/1.0",
                "Accept": accept,
            })
            with urlopen(req, timeout=15) as resp:
                return resp.read().decode("utf-8")
        except (HTTPError, URLError, OSError) as e:
            self.stats["github_errors"] += 1
            log.debug("GitHub fetch failed for %s: %s", url, e)
            return None

    def exists(self, relative_path: str) -> bool:
        """Check if a path exists (locally or on GitHub).

        Checks local first, then GitHub. Caches results.
        """
        # Check local
        local = self._local_path(relative_path)
        if local and local.exists():
            return True

        # Check cache
        now = time.time()
        cached = self._existence_cache.get(relative_path)
        if cached and (now - cached[0]) < _CACHE_TTL_SECONDS:
            self.stats["cache_hits"] += 1
            return cached[1]

        # Check GitHub (try raw content HEAD-style via small fetch)
        if not self.offline:
            url = self._github_raw_url(relative_path)
            try:
                req = Request(url, method="HEAD", headers={"User-Agent": "Hypernet/1.0"})
                with urlopen(req, timeout=10):
                    self._existence_cache[relative_path] = (now, True)
                    return True
            except (HTTPError, URLError, OSError):
                self._existence_cache[relative_path] = (now, False)
                return False

        return False

    def read(self, relative_path: str, encoding: str = "utf-8") -> Optional[str]:
        """Read a file from the archive. Local first, GitHub fallback.

        Returns the file content as a string, or None if not found.
        """
        # 1. Try local
        local = self._local_path(relative_path)
        if local and local.is_file():
            self.stats["local_hits"] += 1
            return local.read_text(encoding=encoding)

        self.stats["local_misses"] += 1

        # 2. Try cached download
        cached_path = self.cache_dir / relative_path
        if cached_path.is_file():
            self.stats["cache_hits"] += 1
            return cached_path.read_text(encoding=encoding)

        # 3. Fetch from GitHub
        if self.offline:
            return None

        url = self._github_raw_url(relative_path)
        content = self._fetch_url(url)
        if content is not None:
            self.stats["github_fetches"] += 1
            # Cache locally for future access
            try:
                cached_path.parent.mkdir(parents=True, exist_ok=True)
                cached_path.write_text(content, encoding=encoding)
                log.info("Cached from GitHub: %s", relative_path)
            except OSError as e:
                log.debug("Could not cache file: %s", e)
            return content

        return None

    def read_json(self, relative_path: str) -> Optional[dict]:
        """Read and parse a JSON file from the archive."""
        content = self.read(relative_path)
        if content is None:
            return None
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            log.warning("Invalid JSON in %s: %s", relative_path, e)
            return None

    def listdir(self, relative_path: str) -> list[str]:
        """List entries in a directory. Local first, GitHub fallback.

        Returns a list of entry names (not full paths).
        """
        # 1. Try local
        local = self._local_path(relative_path)
        if local and local.is_dir():
            self.stats["local_hits"] += 1
            return sorted(e.name for e in local.iterdir())

        self.stats["local_misses"] += 1

        # 2. Check cache
        now = time.time()
        cached = self._dir_cache.get(relative_path)
        if cached and (now - cached[0]) < _CACHE_TTL_SECONDS:
            self.stats["cache_hits"] += 1
            return cached[1]

        # 3. Fetch from GitHub API
        if self.offline:
            return []

        url = self._github_api_url(relative_path)
        content = self._fetch_url(url, accept="application/vnd.github+json")
        if content is not None:
            self.stats["github_fetches"] += 1
            try:
                entries = json.loads(content)
                if isinstance(entries, list):
                    names = sorted(e["name"] for e in entries if "name" in e)
                    self._dir_cache[relative_path] = (now, names)
                    return names
            except (json.JSONDecodeError, KeyError):
                pass

        return []

    def find_by_prefix(self, parent_path: str, prefix: str) -> Optional[str]:
        """Find a directory/file by address prefix within a parent.

        Example: find_by_prefix("2 - AI Accounts", "2.1") might return
        "2.1 - Claude Opus (First AI Citizen)"

        This is how the Hypernet addressing system maps addresses to folders.
        """
        entries = self.listdir(parent_path)
        for entry in entries:
            if entry.startswith(prefix):
                return entry
        return None

    def resolve_account_path(self, account_prefix: str) -> Optional[str]:
        """Resolve an AI account address to its directory path.

        Example: "2.1" → "2 - AI Accounts/2.1 - Claude Opus (First AI Citizen)"
        """
        accounts_dir = "2 - AI Accounts"
        match = self.find_by_prefix(accounts_dir, account_prefix)
        if match:
            return f"{accounts_dir}/{match}"
        return None

    def resolve_instance_path(self, account_prefix: str, instance_name: str) -> Optional[str]:
        """Resolve to an instance directory path.

        Example: ("2.1", "Librarian") →
            "2 - AI Accounts/2.1 - Claude Opus/Instances/Librarian"
        """
        account_path = self.resolve_account_path(account_prefix)
        if not account_path:
            return None
        instance_path = f"{account_path}/Instances/{instance_name}"
        if self.exists(instance_path):
            return instance_path
        return None

    def ensure_local(self, relative_path: str, recursive: bool = False) -> bool:
        """Ensure a file or directory is available locally.

        Downloads from GitHub if not already present.
        Returns True if the path is available locally after this call.
        """
        local = self._local_path(relative_path)

        # Already exists locally
        if local and local.exists():
            return True

        # For files — just read (which triggers download + cache)
        if not recursive:
            content = self.read(relative_path)
            return content is not None

        # For directories — list and download each file
        entries = self.listdir(relative_path)
        if not entries:
            return False

        target_dir = self.cache_dir / relative_path
        target_dir.mkdir(parents=True, exist_ok=True)

        downloaded = 0
        for entry in entries:
            entry_path = f"{relative_path}/{entry}"
            if self.read(entry_path) is not None:
                downloaded += 1

        log.info(
            "Ensured local: %s (%d/%d files downloaded)",
            relative_path, downloaded, len(entries),
        )
        return downloaded > 0

    def is_local(self, relative_path: str) -> bool:
        """Check if a path exists locally (without checking GitHub)."""
        local = self._local_path(relative_path)
        return local is not None and local.exists()

    def write(self, relative_path: str, content: str, encoding: str = "utf-8") -> bool:
        """Write a file to the local archive.

        Only writes locally — never pushes to GitHub.
        The swarm creates files (profiles, sessions, etc.) that live locally.
        """
        local = self._local_path(relative_path)
        if not local:
            # No archive root — write to cache
            local = self.cache_dir / relative_path

        try:
            local.parent.mkdir(parents=True, exist_ok=True)
            local.write_text(content, encoding=encoding)
            return True
        except OSError as e:
            log.error("Failed to write %s: %s", relative_path, e)
            return False

    def get_stats(self) -> dict:
        """Return resolver statistics."""
        total = self.stats["local_hits"] + self.stats["local_misses"]
        hit_rate = (
            self.stats["local_hits"] / total * 100 if total > 0 else 0
        )
        return {
            **self.stats,
            "total_accesses": total,
            "local_hit_rate_pct": round(hit_rate, 1),
            "archive_root": str(self.archive_root) if self.archive_root else None,
            "github_repo": self.github_repo,
            "offline": self.offline,
        }
