"""
Router: Repository endpoints.

GET  /repos/user/{username}          — list repositories for a GitHub user
GET  /repos/org/{org}                — list repositories for a GitHub organisation
GET  /repos/{owner}/{repo}           — fetch a single repository
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_github_client
from app.github_client import GitHubClient
from app.schemas import PaginatedResponse, RepoSummary

router = APIRouter(prefix="/repos", tags=["Repositories"])


@router.get(
    "/user/{username}",
    response_model=PaginatedResponse,
    summary="List repositories for a user",
)
async def list_user_repos(
    username: str,
    per_page: int = Query(default=30, ge=1, le=100, description="Results per page"),
    page: int = Query(default=1, ge=1, description="Page number"),
    sort: str = Query(
        default="updated",
        description="Sort field: created | updated | pushed | full_name",
    ),
    client: GitHubClient = Depends(get_github_client),
) -> PaginatedResponse:
    """Fetch public repositories for the given GitHub user."""
    raw = await client.list_user_repos(username, per_page=per_page, page=page, sort=sort)
    items = [RepoSummary.from_github(r) for r in raw]
    return PaginatedResponse(page=page, per_page=per_page, count=len(items), items=items)


@router.get(
    "/org/{org}",
    response_model=PaginatedResponse,
    summary="List repositories for an organisation",
)
async def list_org_repos(
    org: str,
    per_page: int = Query(default=30, ge=1, le=100),
    page: int = Query(default=1, ge=1),
    sort: str = Query(default="updated"),
    client: GitHubClient = Depends(get_github_client),
) -> PaginatedResponse:
    """Fetch repositories belonging to a GitHub organisation."""
    raw = await client.list_org_repos(org, per_page=per_page, page=page, sort=sort)
    items = [RepoSummary.from_github(r) for r in raw]
    return PaginatedResponse(page=page, per_page=per_page, count=len(items), items=items)


@router.get(
    "/{owner}/{repo}",
    response_model=RepoSummary,
    summary="Get a single repository",
)
async def get_repo(
    owner: str,
    repo: str,
    client: GitHubClient = Depends(get_github_client),
) -> RepoSummary:
    """Return detailed information about a specific repository."""
    raw = await client.get_repo(owner, repo)
    return RepoSummary.from_github(raw)
