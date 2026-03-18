import pytest

from pyopenalex.endpoints import Endpoint
from pyopenalex.models.autocomplete import AutocompleteResult
from pyopenalex.models.works import Work

from tests.conftest import FakeHttpClient, load_fixture


@pytest.fixture
def works_endpoint(fake_http):
    return Endpoint(fake_http, "/works", Work)


# --- Path resolution ---


class TestPathResolution:
    def test_short_id(self, works_endpoint, fake_http):
        fake_http.enqueue(load_fixture("work"))
        works_endpoint.get("W2741809807")
        assert fake_http.last_request[1] == "/works/W2741809807"

    def test_openalex_url(self, works_endpoint, fake_http):
        fake_http.enqueue(load_fixture("work"))
        works_endpoint.get("https://openalex.org/W2741809807")
        assert fake_http.last_request[1] == "/W2741809807"

    def test_doi_url(self, works_endpoint, fake_http):
        fake_http.enqueue(load_fixture("work"))
        works_endpoint.get("https://doi.org/10.7717/peerj.4375")
        assert fake_http.last_request[1] == "/works/https://doi.org/10.7717/peerj.4375"

    def test_orcid_url(self, fake_http):
        from pyopenalex.models.authors import Author

        endpoint = Endpoint(fake_http, "/authors", Author)
        fake_http.enqueue(load_fixture("author"))
        endpoint.get("https://orcid.org/0000-0001-6187-6610")
        assert fake_http.last_request[1] == "/authors/https://orcid.org/0000-0001-6187-6610"

    def test_ror_url(self, fake_http):
        from pyopenalex.models.institutions import Institution

        endpoint = Endpoint(fake_http, "/institutions", Institution)
        fake_http.enqueue(load_fixture("institution"))
        endpoint.get("https://ror.org/0161xgx34")
        assert fake_http.last_request[1] == "/institutions/https://ror.org/0161xgx34"


# --- Batch get ---


class TestBatchGet:
    def test_batch_get_returns_list(self, works_endpoint, fake_http):
        fake_http.enqueue(load_fixture("works_list"))
        results = works_endpoint.get(["W2741809807", "W2100837269"])

        assert isinstance(results, list)
        assert len(results) == 2
        assert all(isinstance(w, Work) for w in results)

    def test_batch_get_uses_or_filter(self, works_endpoint, fake_http):
        fake_http.enqueue(load_fixture("works_list"))
        works_endpoint.get(["W1", "W2"])

        params = fake_http.last_params
        assert "openalex:W1|W2" in params["filter"]


# --- Random ---


class TestRandom:
    def test_random_returns_entity(self, works_endpoint, fake_http):
        fake_http.enqueue(load_fixture("work"))
        work = works_endpoint.random()

        assert isinstance(work, Work)
        assert fake_http.last_request[1] == "/works/random"


# --- Autocomplete ---


class TestAutocomplete:
    def test_autocomplete_returns_results(self, works_endpoint, fake_http):
        fake_http.enqueue(load_fixture("autocomplete"))
        results = works_endpoint.autocomplete("harvard")

        assert all(isinstance(r, AutocompleteResult) for r in results)
        assert len(results) > 0
        assert fake_http.last_request[1] == "/autocomplete/works"
        assert fake_http.last_params["q"] == "harvard"


# --- Delegation to QueryBuilder ---


class TestDelegation:
    def test_filter(self, works_endpoint, fake_http):
        fake_http.enqueue(load_fixture("works_list"))
        works_endpoint.filter(publication_year=2024).get()
        assert "publication_year:2024" in fake_http.last_params.get("filter", "")

    def test_search(self, works_endpoint, fake_http):
        fake_http.enqueue(load_fixture("works_list"))
        works_endpoint.search("test").get()
        assert fake_http.last_params["search"] == "test"

    def test_count(self, works_endpoint, fake_http):
        fake_http.enqueue(load_fixture("works_list"))
        count = works_endpoint.count(publication_year=2024)
        assert count > 0

    def test_callable_syntax(self, works_endpoint, fake_http):
        fake_http.enqueue(load_fixture("works_list"))
        works_endpoint(publication_year=2024).get()
        assert "publication_year:2024" in fake_http.last_params.get("filter", "")
