"""
FastAPI dependency providers.

These callables are designed to integrate cleanly with FastAPI's
Depends() system:
  - get_github_client  → yields a ready-to-use GitHubClient
"""

from __future__ import annotations

from typing import AsyncGenerator

from fastapi import Depends

from app.config import Settings, get_settings
from app.github_client import GitHubClient


async def get_github_client(
    settings: Settings = Depends(get_settings),
) -> AsyncGenerator[GitHubClient, None]:
    """
    FastAPI dependency that yields an authenticated GitHubClient.

    The client is opened (and its httpx session initialised) for the
    lifetime of a single request, then closed automatically.
    """
    async with GitHubClient(settings) as client:
        yield client
