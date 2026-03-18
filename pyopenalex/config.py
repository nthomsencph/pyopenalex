from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "OPENALEX_"}

    api_key: str | None = None
    base_url: str = "https://api.openalex.org"
    per_page: int = 25
    timeout: float = 30.0
    max_retries: int = 3
