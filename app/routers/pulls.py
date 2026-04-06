
"""
Router: Pull Request endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.dependencies import get_github_client
from app.github_client import GitHubClient
from app.schemas import CreatePullRequestRequest, PaginatedResponse, PullRequestSummary

router = APIRouter(prefix="/repos/{owner}/{repo}/pulls", tags=["Pull Requests"])


@router.get(
    "",
    response_model=PaginatedResponse,
    summary="List pull requests",
)
async def list_pull_requests(
    owner: str,
    repo: str,
    state: str = Query(
        default="open",
        description="Filter by state: open | closed | all",
        pattern="^(open|closed|all)$",
    ),
    per_page: int = Query(default=30, ge=1, le=100),
    page: int = Query(default=1, ge=1),
    client: GitHubClient = Depends(get_github_client),
) -> PaginatedResponse:
    """List pull requests for a repository."""
    raw = await client.list_pull_requests(
        owner, repo, state=state, per_page=per_page, page=page
    )
    items = [PullRequestSummary.from_github(p) for p in raw]
    return PaginatedResponse(page=page, per_page=per_page, count=len(items), items=items)


@router.post(
    "",
    response_model=PullRequestSummary,
    status_code=status.HTTP_201_CREATED,
    summary="Create a pull request",
)
async def create_pull_request(
    owner: str,
    repo: str,
    payload: CreatePullRequestRequest,
    client: GitHubClient = Depends(get_github_client),
) -> PullRequestSummary:
    """Create a new pull request."""
    raw = await client.create_pull_request(
        owner,
        repo,
        title=payload.title,
        head=payload.head,
        base=payload.base,
        body=payload.body,
        draft=payload.draft,
    )
    return PullRequestSummary.from_github(raw)
