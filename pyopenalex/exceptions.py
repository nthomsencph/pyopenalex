from __future__ import annotations


class OpenAlexError(Exception):
    pass


class NotFoundError(OpenAlexError):
    pass


class RateLimitError(OpenAlexError):
    pass


class APIError(OpenAlexError):
    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        super().__init__(f"HTTP {status_code}: {message}")
