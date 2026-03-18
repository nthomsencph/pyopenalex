from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration for the OpenAlex client.

    All fields can be set via environment variables with the ``OPENALEX_`` prefix
    (e.g. ``OPENALEX_API_KEY``, ``OPENALEX_TIMEOUT``).
    """

    model_config = {"env_prefix": "OPENALEX_", "env_file": ".env", "extra": "ignore"}

    api_key: str | None = None
    base_url: str = "https://api.openalex.org"
    per_page: int = 25
    timeout: float = 30.0
    max_retries: int = 3
