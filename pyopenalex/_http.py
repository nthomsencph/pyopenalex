from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from pyopenalex.config import Settings
from pyopenalex.exceptions import APIError, NotFoundError, RateLimitError


class _Retryable(Exception):
    """Raised internally to trigger tenacity retry."""

    def __init__(self, exc: Exception) -> None:
        self.exc = exc


class HttpClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = httpx.Client(
            base_url=settings.base_url,
            timeout=settings.timeout,
        )
        self._request_with_retry = retry(
            retry=retry_if_exception_type(_Retryable),
            stop=stop_after_attempt(settings.max_retries),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            reraise=True,
        )(self._do_request)

    def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        params = dict(params or {})
        if self._settings.api_key:
            params.setdefault("api_key", self._settings.api_key)

        try:
            return self._request_with_retry(method, path, params)
        except _Retryable as e:
            raise e.exc from None

    def _do_request(
        self,
        method: str,
        path: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        response = self._client.request(method, path, params=params)

        if response.status_code == 200:
            return response.json()  # type: ignore[no-any-return]
        if response.status_code == 404:
            raise NotFoundError(f"Not found: {path}")
        if response.status_code == 429:
            raise _Retryable(RateLimitError("Rate limit exceeded"))
        if response.status_code >= 500:
            raise _Retryable(APIError(response.status_code, response.text))

        raise APIError(response.status_code, response.text)

    def close(self) -> None:
        self._client.close()
