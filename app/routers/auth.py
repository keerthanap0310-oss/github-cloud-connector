"""
Router: Authentication / user identity endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies import get_github_client
from app.github_client import GitHubClient

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get(
    "/me",
    summary="Get authenticated user",
    description=(
        "Returns the GitHub profile of the account associated with the "
        "configured Personal Access Token (PAT)."
    ),
)
async def get_authenticated_user(
    client: GitHubClient = Depends(get_github_client),
) -> dict:
    """
    Validate the token and return the authenticated GitHub user's profile.
    Useful as a health-check for the configured credentials.
    """
    data = await client.get_authenticated_user()
    return {
        "login": data.get("login"),
        "id": data.get("id"),
        "name": data.get("name"),
        "email": data.get("email"),
        "avatar_url": data.get("avatar_url"),
        "html_url": data.get("html_url"),
        "public_repos": data.get("public_repos"),
        "followers": data.get("followers"),
        "following": data.get("following"),
    }
