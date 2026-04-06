"""
GitHub API HTTP client.

Wraps httpx.AsyncClient to provide:
  - Bearer-token authentication via PAT
  - Consistent base URL and headers
  - Centralised error handling / response parsing
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any

import httpx

from app.config import Settings

logger = logging.getLogger(__name__)

# GitHub requires this Accept header for most v3 endpoints
GITHUB_ACCEPT = "application/vnd.github+json"
GITHUB_API_VERSION = "2022-11-28"


class GitHubAPIError(Exception):
    """Raised when the GitHub API returns a non-2xx response."""

    def __init__(self, status_code: int, message: str, detail: Any = None):
        self.status_code = status_code
        self.message = message
        self.detail = detail
        super().__init__(f"GitHub API error {status_code}: {message}")


class GitHubClient:
    """
    Async GitHub REST API client.

    Usage (within FastAPI dependency injection):
        client = GitHubClient(settings)
        async with client:
            repos = await client.get_user_repos("octocat")
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: httpx.AsyncClient | None = None

    # ------------------------------------------------------------------
    # Context-manager lifecycle
    # ------------------------------------------------------------------

    async def __aenter__(self) -> "GitHubClient":
        self._client = httpx.AsyncClient(
            base_url=self._settings.github_api_base_url,
            headers=self._build_headers(),
            timeout=self._settings.request_timeout,
        )
        return self

    async def __aexit__(self, *_: Any) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._settings.github_pat}",
            "Accept": GITHUB_ACCEPT,
            "X-GitHub-Api-Version": GITHUB_API_VERSION,
        }

    @property
    def _http(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError(
                "GitHubClient must be used as an async context manager."
            )
        return self._client

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> Any:
        """Make an HTTP request and return parsed JSON."""
        logger.debug("%s %s", method.upper(), endpoint)
        try:
            response = await self._http.request(method, endpoint, **kwargs)
        except httpx.RequestError as exc:
            raise GitHubAPIError(
                status_code=0,
                message=f"Network error: {exc}",
            ) from exc

        if not response.is_success:
            try:
                body = response.json()
                msg = body.get("message", response.text)
                detail = body.get("errors")
            except Exception:
                msg = response.text
                detail = None

            raise GitHubAPIError(
                status_code=response.status_code,
                message=msg,
                detail=detail,
            )

        # 204 No Content → nothing to parse
        if response.status_code == 204 or not response.content:
            return None

        return response.json()

    # ------------------------------------------------------------------
    # Authenticated user
    # ------------------------------------------------------------------

    async def get_authenticated_user(self) -> dict[str, Any]:
        """Return the currently authenticated GitHub user."""
        return await self._request("GET", "/user")

    # ------------------------------------------------------------------
    # Repositories
    # ------------------------------------------------------------------

    async def list_user_repos(
        self,
        username: str,
        per_page: int = 30,
        page: int = 1,
        sort: str = "updated",
    ) -> list[dict[str, Any]]:
        """List public repositories for a given GitHub user."""
        return await self._request(
            "GET",
            f"/users/{username}/repos",
            params={"per_page": per_page, "page": page, "sort": sort},
        )

    async def list_org_repos(
        self,
        org: str,
        per_page: int = 30,
        page: int = 1,
        sort: str = "updated",
    ) -> list[dict[str, Any]]:
        """List repositories for a GitHub organisation."""
        return await self._request(
            "GET",
            f"/orgs/{org}/repos",
            params={"per_page": per_page, "page": page, "sort": sort},
        )

    async def get_repo(self, owner: str, repo: str) -> dict[str, Any]:
        """Fetch a single repository by owner/repo."""
        return await self._request("GET", f"/repos/{owner}/{repo}")

    # ------------------------------------------------------------------
    # Issues
    # ------------------------------------------------------------------

    async def list_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        per_page: int = 30,
        page: int = 1,
    ) -> list[dict[str, Any]]:
        """List issues (excluding pull requests) for a repository."""
        data = await self._request(
            "GET",
            f"/repos/{owner}/{repo}/issues",
            params={"state": state, "per_page": per_page, "page": page},
        )
        # GitHub returns PRs in the issues list — filter them out
        return [item for item in data if "pull_request" not in item]

    async def get_issue(
        self, owner: str, repo: str, issue_number: int
    ) -> dict[str, Any]:
        """Fetch a single issue by number."""
        return await self._request(
            "GET", f"/repos/{owner}/{repo}/issues/{issue_number}"
        )

    async def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str | None = None,
        labels: list[str] | None = None,
        assignees: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a new issue in a repository."""
        payload: dict[str, Any] = {"title": title}
        if body:
            payload["body"] = body
        if labels:
            payload["labels"] = labels
        if assignees:
            payload["assignees"] = assignees

        return await self._request(
            "POST", f"/repos/{owner}/{repo}/issues", json=payload
        )

    # ------------------------------------------------------------------
    # Pull Requests
    # ------------------------------------------------------------------

    async def list_pull_requests(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        per_page: int = 30,
        page: int = 1,
    ) -> list[dict[str, Any]]:
        """List pull requests for a repository."""
        return await self._request(
            "GET",
            f"/repos/{owner}/{repo}/pulls",
            params={"state": state, "per_page": per_page, "page": page},
        )

    async def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        head: str,
        base: str,
        body: str | None = None,
        draft: bool = False,
    ) -> dict[str, Any]:
        """Create a pull request."""
        payload: dict[str, Any] = {
            "title": title,
            "head": head,
            "base": base,
            "draft": draft,
        }
        if body:
            payload["body"] = body

        return await self._request(
            "POST", f"/repos/{owner}/{repo}/pulls", json=payload
        )

    # ------------------------------------------------------------------
    # Commits
    # ------------------------------------------------------------------

    async def list_commits(
        self,
        owner: str,
        repo: str,
        branch: str | None = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[dict[str, Any]]:
        """List commits for a repository (optionally filtered by branch)."""
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if branch:
            params["sha"] = branch

        return await self._request(
            "GET", f"/repos/{owner}/{repo}/commits", params=params
        )
