
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.github_client import GitHubAPIError
from app.error_handlers import github_api_error_handler
from app.routers import auth, issues, repos, pulls, commits

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifecycle events.
    Useful for setting up shared resources (like HTTP clients)
    that should persist across requests.
    """
    settings = get_settings()
    logger.info("Starting %s v%s", settings.app_title, settings.app_version)
    yield
    logger.info("Shutting down %s", settings.app_title)

def create_app() -> FastAPI:
    """Initialize and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_title,
        description=settings.app_description,
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/",  # Make Swagger UI the landing page
    )

    # Enable CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register custom exception handlers
    app.add_exception_handler(GitHubAPIError, github_api_error_handler)

    # Include routers
    app.include_router(auth.router)
    app.include_router(repos.router)
    app.include_router(issues.router)
    app.include_router(pulls.router)
    app.include_router(commits.router)

    @app.get("/health", tags=["Status"], summary="Health Check")
    async def health_check() -> dict[str, str]:
        """Verify the service is running."""
        return {"status": "healthy", "version": settings.app_version}

    return app

app = create_app()
