from __future__ import annotations

import time
from typing import Any

import httpx

from pyopenalex.config import Settings
from pyopenalex.exceptions import APIError, NotFoundError, RateLimitError


class HttpClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = httpx.Client(
            base_url=settings.base_url,
            timeout=settings.timeout,
        )

    def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        params = dict(params or {})
        if self._settings.api_key:
            params.setdefault("api_key", self._settings.api_key)

        last_exc: Exception | None = None
        for attempt in range(self._settings.max_retries):
            response = self._client.request(method, path, params=params)

            if response.status_code == 200:
                return response.json()  # type: ignore[no-any-return]
            if response.status_code == 404:
                raise NotFoundError(f"Not found: {path}")
            if response.status_code == 429:
                last_exc = RateLimitError("Rate limit exceeded")
                time.sleep(2**attempt)
                continue
            if response.status_code >= 500:
                last_exc = APIError(response.status_code, response.text)
                time.sleep(2**attempt)
                continue

            raise APIError(response.status_code, response.text)

        raise last_exc or APIError(0, "Max retries exceeded")

    def close(self) -> None:
        self._client.close()
