"""
Router: Issue endpoints.

GET    /repos/{owner}/{repo}/issues            — list issues
GET    /repos/{owner}/{repo}/issues/{number}   — get a single issue
POST   /repos/{owner}/{repo}/issues            — create an issue
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.dependencies import get_github_client
from app.github_client import GitHubClient
from app.schemas import CreateIssueRequest, IssueSummary, PaginatedResponse

router = APIRouter(tags=["Issues"])


@router.get(
    "/repos/{owner}/{repo}/issues",
    response_model=PaginatedResponse,
    summary="List issues for a repository",
)
async def list_issues(
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
    """
    Return a paginated list of issues (pull requests excluded)
    for the specified repository.
    """
    raw = await client.list_issues(
        owner, repo, state=state, per_page=per_page, page=page
    )
    items = [IssueSummary.from_github(i) for i in raw]
    return PaginatedResponse(page=page, per_page=per_page, count=len(items), items=items)


@router.get(
    "/repos/{owner}/{repo}/issues/{issue_number}",
    response_model=IssueSummary,
    summary="Get a single issue",
)
async def get_issue(
    owner: str,
    repo: str,
    issue_number: int,
    client: GitHubClient = Depends(get_github_client),
) -> IssueSummary:
    """Fetch a specific issue by its number."""
    raw = await client.get_issue(owner, repo, issue_number)
    return IssueSummary.from_github(raw)


@router.post(
    "/repos/{owner}/{repo}/issues",
    response_model=IssueSummary,
    status_code=status.HTTP_201_CREATED,
    summary="Create an issue",
)
async def create_issue(
    owner: str,
    repo: str,
    payload: CreateIssueRequest,
    client: GitHubClient = Depends(get_github_client),
) -> IssueSummary:
    """
    Open a new issue in the specified repository.

    The authenticated token must have the **repo** scope (or **public_repo**
    for public repositories).
    """
    raw = await client.create_issue(
        owner,
        repo,
        title=payload.title,
        body=payload.body,
        labels=payload.labels or None,
        assignees=payload.assignees or None,
    )
    return IssueSummary.from_github(raw)
