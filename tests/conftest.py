from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from pyopenalex._http import HttpClient
from pyopenalex.config import Settings

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict[str, Any]:
    with open(FIXTURES / f"{name}.json") as f:
        return json.load(f)


class FakeHttpClient(HttpClient):
    """HttpClient that returns canned responses instead of making real requests."""

    def __init__(self) -> None:
        super().__init__(Settings())
        self._responses: list[dict[str, Any]] = []
        self._requests: list[tuple[str, str, dict[str, Any] | None]] = []

    def enqueue(self, *responses: dict[str, Any]) -> None:
        self._responses.extend(responses)

    def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self._requests.append((method, path, params))
        if not self._responses:
            raise RuntimeError("FakeHttpClient: no responses enqueued")
        return self._responses.pop(0)

    @property
    def last_request(self) -> tuple[str, str, dict[str, Any] | None]:
        return self._requests[-1]

    @property
    def last_params(self) -> dict[str, Any]:
        return self._requests[-1][2] or {}


@pytest.fixture
def fake_http() -> FakeHttpClient:
    return FakeHttpClient()
