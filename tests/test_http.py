import pytest

from pyopenalex._http import HttpClient
from pyopenalex.config import Settings
from pyopenalex.exceptions import APIError, NotFoundError, RateLimitError


class FakeResponse:
    def __init__(self, status_code: int, data: dict | str = ""):
        self.status_code = status_code
        self._data = data
        self.text = data if isinstance(data, str) else ""

    def json(self):
        return self._data


class TestHttpClient:
    def _make_client(self, responses: list[FakeResponse], **kwargs) -> HttpClient:
        settings = Settings(**kwargs)
        client = HttpClient(settings)

        call_count = 0

        def fake_request(method, url, params=None):
            nonlocal call_count
            resp = responses[min(call_count, len(responses) - 1)]
            call_count += 1
            return resp

        client._client.request = fake_request
        client._call_count = lambda: call_count  # expose for assertions
        return client

    def test_200_returns_json(self):
        client = self._make_client([FakeResponse(200, {"results": []})])
        result = client.request("GET", "/works")
        assert result == {"results": []}

    def test_404_raises_not_found(self):
        client = self._make_client([FakeResponse(404)])
        with pytest.raises(NotFoundError):
            client.request("GET", "/works/W999")

    def test_400_raises_api_error(self):
        client = self._make_client([FakeResponse(400, "Bad request")])
        with pytest.raises(APIError) as exc_info:
            client.request("GET", "/works")
        assert exc_info.value.status_code == 400

    def test_429_retries_then_raises(self):
        responses = [FakeResponse(429)] * 3
        client = self._make_client(responses, max_retries=3)
        with pytest.raises(RateLimitError):
            client.request("GET", "/works")

    def test_500_retries_then_raises(self):
        responses = [FakeResponse(500, "Server error")] * 2
        client = self._make_client(responses, max_retries=2)
        with pytest.raises(APIError):
            client.request("GET", "/works")

    def test_429_then_success(self):
        responses = [FakeResponse(429), FakeResponse(200, {"ok": True})]
        client = self._make_client(responses, max_retries=3)
        result = client.request("GET", "/works")
        assert result == {"ok": True}

    def test_api_key_added_to_params(self):
        client = self._make_client([FakeResponse(200, {})], api_key="test-key")

        captured_params = {}
        original_request = client._client.request

        def capture_request(method, url, params=None):
            captured_params.update(params or {})
            return FakeResponse(200, {})

        client._client.request = capture_request
        client.request("GET", "/works")
        assert captured_params["api_key"] == "test-key"
