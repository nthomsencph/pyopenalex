from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from pyopenalex.config import Settings
from pyopenalex.exceptions import APIError, AuthenticationError, NotFoundError, RateLimitError


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

    @staticmethod
    def _extract_error_message(response: httpx.Response) -> str:
        """Extract a human-readable message from an API error response."""
        try:
            body = response.json()
            parts = []
            if body.get("error"):
                parts.append(body["error"])
            if body.get("message"):
                parts.append(body["message"])
            if parts:
                return ". ".join(parts)
        except Exception:
            pass
        return response.text or f"HTTP {response.status_code}"

    def _rate_limit_message(self, response: httpx.Response, params: dict[str, Any]) -> str:
        msg = self._extract_error_message(response)
        if not params.get("api_key"):
            msg += (
                " No API key set. Get a free key at https://openalex.org/settings/api"
                " and pass it via OpenAlex(api_key=...) or set OPENALEX_API_KEY."
            )
        return msg

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
            raise NotFoundError(self._extract_error_message(response))
        if response.status_code == 401:
            raise AuthenticationError(self._extract_error_message(response))
        if response.status_code == 403:
            # Burst rate limit — retry with backoff
            raise _Retryable(RateLimitError(self._rate_limit_message(response, params)))
        if response.status_code == 429:
            # Daily limit exhausted — retrying won't help
            raise RateLimitError(self._rate_limit_message(response, params))
        if response.status_code >= 500:
            raise _Retryable(APIError(response.status_code, self._extract_error_message(response)))

        raise APIError(response.status_code, self._extract_error_message(response))

    def request_bytes(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
    ) -> bytes:
        """Make a request and return raw bytes (for binary downloads)."""
        params = dict(params or {})
        if self._settings.api_key:
            params.setdefault("api_key", self._settings.api_key)

        response = self._client.request(method, url, params=params)

        if response.status_code == 200:
            return response.content
        if response.status_code == 404:
            raise NotFoundError(self._extract_error_message(response))
        if response.status_code == 401:
            raise AuthenticationError(self._extract_error_message(response))
        if response.status_code in (403, 429):
            raise RateLimitError(self._rate_limit_message(response, params))
        if response.status_code >= 500:
            raise APIError(response.status_code, self._extract_error_message(response))

        raise APIError(response.status_code, self._extract_error_message(response))

    def close(self) -> None:
        self._client.close()
