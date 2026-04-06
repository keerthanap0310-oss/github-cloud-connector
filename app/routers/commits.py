
"""
Router: Commit endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_github_client
from app.github_client import GitHubClient
from app.schemas import CommitSummary, PaginatedResponse

router = APIRouter(prefix="/repos/{owner}/{repo}/commits", tags=["Commits"])


@router.get(
    "",
    response_model=PaginatedResponse,
    summary="List commits",
)
async def list_commits(
    owner: str,
    repo: str,
    branch: str | None = Query(default=None, description="Filter by branch name"),
    per_page: int = Query(default=30, ge=1, le=100),
    page: int = Query(default=1, ge=1),
    client: GitHubClient = Depends(get_github_client),
) -> PaginatedResponse:
    """List commits for a repository."""
    raw = await client.list_commits(
        owner, repo, branch=branch, per_page=per_page, page=page
    )
    items = [CommitSummary.from_github(c) for c in raw]
    return PaginatedResponse(page=page, per_page=per_page, count=len(items), items=items)
