"""
Centralised error handling utilities.

Translates GitHubAPIError exceptions into structured FastAPI HTTP responses
so all routers share consistent error handling without boilerplate.
"""

from __future__ import annotations

import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from app.github_client import GitHubAPIError

logger = logging.getLogger(__name__)

# Map selected GitHub status codes to friendlier descriptions
_STATUS_MESSAGES: dict[int, str] = {
    401: "Authentication failed. Check your GitHub PAT.",
    403: "Forbidden. Your token may lack the required scopes.",
    404: "Resource not found on GitHub.",
    422: "Validation failed. Check your request payload.",
    429: "GitHub API rate limit exceeded. Please retry later.",
}


def github_error_to_response(exc: GitHubAPIError) -> JSONResponse:
    """Convert a GitHubAPIError into a JSONResponse."""
    friendly = _STATUS_MESSAGES.get(exc.status_code, exc.message)
    logger.warning(
        "GitHub API error | status=%s | message=%s", exc.status_code, exc.message
    )
    status_code = exc.status_code if exc.status_code >= 400 else 502
    return JSONResponse(
        status_code=status_code,
        content={
            "error": friendly,
            "detail": exc.detail,
            "status_code": status_code,
        },
    )


async def github_api_error_handler(
    request: Request, exc: GitHubAPIError
) -> JSONResponse:
    """Global FastAPI exception handler for GitHubAPIError."""
    return github_error_to_response(exc)
