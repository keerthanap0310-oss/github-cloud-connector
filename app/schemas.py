"""
Pydantic schemas for request bodies and API responses.
Keeping schemas separate from business logic enforces clean architecture.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


# ---------------------------------------------------------------------------
# Shared / primitive models
# ---------------------------------------------------------------------------


class GitHubUser(BaseModel):
    login: str
    id: int
    avatar_url: str | None = None
    html_url: str | None = None


# ---------------------------------------------------------------------------
# Repository schemas
# ---------------------------------------------------------------------------


class RepoSummary(BaseModel):
    """Slim view of a GitHub repository."""

    id: int
    name: str
    full_name: str
    private: bool
    description: str | None = None
    html_url: str
    language: str | None = None
    stargazers_count: int = 0
    forks_count: int = 0
    open_issues_count: int = 0
    default_branch: str = "main"
    updated_at: datetime | None = None

    @classmethod
    def from_github(cls, data: dict[str, Any]) -> "RepoSummary":
        return cls(
            id=data["id"],
            name=data["name"],
            full_name=data["full_name"],
            private=data["private"],
            description=data.get("description"),
            html_url=data["html_url"],
            language=data.get("language"),
            stargazers_count=data.get("stargazers_count", 0),
            forks_count=data.get("forks_count", 0),
            open_issues_count=data.get("open_issues_count", 0),
            default_branch=data.get("default_branch", "main"),
            updated_at=data.get("updated_at"),
        )


# ---------------------------------------------------------------------------
# Issue schemas
# ---------------------------------------------------------------------------


class IssueSummary(BaseModel):
    """Slim view of a GitHub issue."""

    id: int
    number: int
    title: str
    state: str
    body: str | None = None
    html_url: str
    user: str | None = None  # login of the author
    labels: list[str] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_github(cls, data: dict[str, Any]) -> "IssueSummary":
        return cls(
            id=data["id"],
            number=data["number"],
            title=data["title"],
            state=data["state"],
            body=data.get("body"),
            html_url=data["html_url"],
            user=data.get("user", {}).get("login") if data.get("user") else None,
            labels=[lbl["name"] for lbl in data.get("labels", [])],
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )


class CreateIssueRequest(BaseModel):
    """Request body for creating a new issue."""

    title: str = Field(..., min_length=1, max_length=256, description="Issue title")
    body: str | None = Field(None, description="Issue description (markdown supported)")
    labels: list[str] = Field(default_factory=list, description="Label names to apply")
    assignees: list[str] = Field(
        default_factory=list, description="GitHub logins to assign"
    )


# ---------------------------------------------------------------------------
# Pull Request schemas
# ---------------------------------------------------------------------------


class PullRequestSummary(BaseModel):
    """Slim view of a GitHub pull request."""

    id: int
    number: int
    title: str
    state: str
    draft: bool = False
    html_url: str
    user: str | None = None
    head: str  # branch name
    base: str  # branch name
    body: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_github(cls, data: dict[str, Any]) -> "PullRequestSummary":
        return cls(
            id=data["id"],
            number=data["number"],
            title=data["title"],
            state=data["state"],
            draft=data.get("draft", False),
            html_url=data["html_url"],
            user=data.get("user", {}).get("login") if data.get("user") else None,
            head=data["head"]["ref"],
            base=data["base"]["ref"],
            body=data.get("body"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )


class CreatePullRequestRequest(BaseModel):
    """Request body for creating a pull request."""

    title: str = Field(..., min_length=1, max_length=256)
    head: str = Field(..., description="Branch containing the changes")
    base: str = Field(..., description="Branch to merge changes into")
    body: str | None = Field(None, description="PR description (markdown supported)")
    draft: bool = Field(False, description="Open as a draft PR")


# ---------------------------------------------------------------------------
# Commit schemas
# ---------------------------------------------------------------------------


class CommitSummary(BaseModel):
    """Slim view of a GitHub commit."""

    sha: str
    message: str
    author_name: str | None = None
    author_email: str | None = None
    author_date: datetime | None = None
    html_url: str
    committer_name: str | None = None

    @classmethod
    def from_github(cls, data: dict[str, Any]) -> "CommitSummary":
        commit = data.get("commit", {})
        author = commit.get("author") or {}
        committer = commit.get("committer") or {}
        return cls(
            sha=data["sha"],
            message=commit.get("message", ""),
            author_name=author.get("name"),
            author_email=author.get("email"),
            author_date=author.get("date"),
            html_url=data.get("html_url", ""),
            committer_name=committer.get("name"),
        )


# ---------------------------------------------------------------------------
# Generic response wrappers
# ---------------------------------------------------------------------------


class PaginatedResponse(BaseModel):
    """Generic paginated list wrapper."""

    page: int
    per_page: int
    count: int
    items: list[Any]


class ErrorResponse(BaseModel):
    """Standard error response body."""

    error: str
    detail: Any = None
    status_code: int
