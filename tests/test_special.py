"""Tests for special endpoints: rate_limit, changefiles, download_pdf."""

from __future__ import annotations

from pyopenalex.client import OpenAlex
from pyopenalex.models.special import ChangefileDate, ChangefileEntry, RateLimit
from tests.conftest import FakeHttpClient


def _client_with_fake(fake_http: FakeHttpClient) -> OpenAlex:
    """Create an OpenAlex client backed by a FakeHttpClient."""
    client = OpenAlex()
    client._http = fake_http
    return client


class TestRateLimit:
    def test_returns_rate_limit(self, fake_http):
        fake_http.enqueue(
            {
                "max_cost_per_day_usd": 1.0,
                "current_cost_today_usd": 0.05,
                "remaining_cost_today_usd": 0.95,
            }
        )
        client = _client_with_fake(fake_http)
        rl = client.rate_limit()

        assert isinstance(rl, RateLimit)
        assert rl.max_cost_per_day_usd == 1.0
        assert rl.current_cost_today_usd == 0.05
        assert rl.remaining_cost_today_usd == 0.95
        assert fake_http.last_request[1] == "/rate-limit"


class TestChangefiles:
    def test_list_changefiles(self, fake_http):
        fake_http.enqueue(
            {
                "meta": {"count": 2},
                "results": [
                    {
                        "date": "2026-03-18",
                        "url": "https://api.openalex.org/changefiles/2026-03-18",
                    },
                    {
                        "date": "2026-03-17",
                        "url": "https://api.openalex.org/changefiles/2026-03-17",
                    },
                ],
            }
        )
        client = _client_with_fake(fake_http)
        dates = client.changefiles()

        assert len(dates) == 2
        assert all(isinstance(d, ChangefileDate) for d in dates)
        assert dates[0].date == "2026-03-18"
        assert fake_http.last_request[1] == "/changefiles"

    def test_changefile_detail(self, fake_http):
        fake_http.enqueue(
            {
                "meta": {"count": 2, "date": "2026-03-18"},
                "results": [
                    {
                        "entity": "works",
                        "records": 5969651,
                        "formats": {
                            "jsonl": {
                                "size_bytes": 16805867909,
                                "size_display": "15.7 GB",
                                "url": "https://content.openalex.org/changefiles/2026-03-18/works.jsonl.gz",
                            },
                            "parquet": {
                                "size_bytes": 19480640576,
                                "size_display": "18.1 GB",
                                "url": "https://content.openalex.org/changefiles/2026-03-18/works.parquet",
                            },
                        },
                    },
                    {
                        "entity": "authors",
                        "records": 1846992,
                        "formats": {
                            "jsonl": {
                                "size_bytes": 6118990397,
                                "size_display": "5.7 GB",
                                "url": "https://content.openalex.org/changefiles/2026-03-18/authors.jsonl.gz",
                            },
                        },
                    },
                ],
            }
        )
        client = _client_with_fake(fake_http)
        entries = client.changefile("2026-03-18")

        assert len(entries) == 2
        assert all(isinstance(e, ChangefileEntry) for e in entries)
        assert entries[0].entity == "works"
        assert entries[0].records == 5969651
        assert "jsonl" in entries[0].formats
        assert entries[0].formats["jsonl"].size_bytes == 16805867909
        assert entries[0].formats["parquet"].url.endswith("works.parquet")
        assert fake_http.last_request[1] == "/changefiles/2026-03-18"


class TestDownloadPdf:
    def test_download_to_file(self, fake_http, tmp_path):
        fake_http._responses = []  # Clear default

        # Monkey-patch request_bytes to return fake PDF content
        fake_pdf = b"%PDF-1.4 fake content"
        calls = []

        def mock_request_bytes(method, url, params=None):
            calls.append((method, url))
            return fake_pdf

        client = _client_with_fake(fake_http)
        client._http.request_bytes = mock_request_bytes

        dest = tmp_path / "paper.pdf"
        result = client.download_pdf("W2741809807", dest)

        assert result == dest
        assert dest.read_bytes() == fake_pdf
        assert calls[0][1] == "https://content.openalex.org/works/W2741809807.pdf"

    def test_download_to_directory(self, fake_http, tmp_path):
        fake_pdf = b"%PDF-1.4 fake"
        client = _client_with_fake(fake_http)
        client._http.request_bytes = lambda m, u, params=None: fake_pdf

        result = client.download_pdf("W123", tmp_path)

        assert result == tmp_path / "W123.pdf"
        assert result.read_bytes() == fake_pdf

    def test_download_strips_openalex_url(self, fake_http, tmp_path):
        calls = []
        client = _client_with_fake(fake_http)
        client._http.request_bytes = lambda m, u, params=None: (calls.append(u), b"pdf")[1]

        client.download_pdf("https://openalex.org/W999", tmp_path / "out.pdf")

        assert calls[0] == "https://content.openalex.org/works/W999.pdf"
