from __future__ import annotations


class OpenAlexError(Exception):
    pass


class NotFoundError(OpenAlexError):
    pass


class AuthenticationError(OpenAlexError):
    """Raised on 401 — invalid or missing API key."""

    pass


class RateLimitError(OpenAlexError):
    """Raised on 403 (burst rate limit) or 429 (daily limit exceeded)."""

    pass


class APIError(OpenAlexError):
    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        super().__init__(f"HTTP {status_code}: {message}")
