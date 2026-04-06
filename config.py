"""
Configuration management using Pydantic Settings.
All sensitive values are loaded from environment variables / .env file.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # GitHub API base URL
    github_api_base_url: str = "https://api.github.com"

    # GitHub Personal Access Token — set via GITHUB_PAT env var
    github_pat: str

    # App metadata
    app_title: str = "GitHub Cloud Connector"
    app_description: str = (
        "A FastAPI-powered connector that integrates with the GitHub API "
        "to manage repositories, issues, pull requests and commits."
    )
    app_version: str = "1.0.0"

    # Request timeout (seconds)
    request_timeout: int = 10

    model_config = SettingsConfigDict(
        env_file=(".env", "app/.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (created once per process)."""
    return Settings()  # type: ignore[call-arg]
