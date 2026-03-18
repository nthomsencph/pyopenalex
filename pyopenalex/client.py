from __future__ import annotations

from pyopenalex._http import HttpClient
from pyopenalex.config import Settings
from pyopenalex.endpoints import Endpoint
from pyopenalex.models.authors import Author
from pyopenalex.models.funders import Funder
from pyopenalex.models.institutions import Institution
from pyopenalex.models.keywords import Keyword
from pyopenalex.models.publishers import Publisher
from pyopenalex.models.sources import Source
from pyopenalex.models.topics import Topic
from pyopenalex.models.works import Work


class OpenAlex:
    """Client for the OpenAlex API.

    Provides typed access to scholarly works, authors, sources, institutions,
    topics, keywords, publishers, and funders.

    Args:
        api_key: OpenAlex API key. Falls back to ``OPENALEX_API_KEY`` env var.
        base_url: API base URL. Defaults to ``https://api.openalex.org``.
        **kwargs: Additional settings (``timeout``, ``max_retries``).

    Example::

        with OpenAlex(api_key="...") as client:
            work = client.works.get("W2741809807")
            print(work.title)
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.openalex.org",
        **kwargs: object,
    ) -> None:
        settings = Settings(
            api_key=api_key,
            base_url=base_url,
            **kwargs,  # type: ignore[arg-type]
        )
        self._http = HttpClient(settings)

        self.works: Endpoint[Work] = Endpoint(self._http, "/works", Work)
        """Scholarly documents: articles, books, datasets, preprints."""

        self.authors: Endpoint[Author] = Endpoint(self._http, "/authors", Author)
        """Researcher profiles with disambiguated identities."""

        self.sources: Endpoint[Source] = Endpoint(self._http, "/sources", Source)
        """Journals, repositories, and conferences."""

        self.institutions: Endpoint[Institution] = Endpoint(
            self._http, "/institutions", Institution
        )
        """Universities and research organizations."""

        self.topics: Endpoint[Topic] = Endpoint(self._http, "/topics", Topic)
        """Subject classifications in a 4-level hierarchy."""

        self.keywords: Endpoint[Keyword] = Endpoint(self._http, "/keywords", Keyword)
        """Extracted keywords from scholarly works."""

        self.publishers: Endpoint[Publisher] = Endpoint(self._http, "/publishers", Publisher)
        """Publishing organizations."""

        self.funders: Endpoint[Funder] = Endpoint(self._http, "/funders", Funder)
        """Funding agencies."""

    def close(self) -> None:
        """Close the underlying HTTP connection."""
        self._http.close()

    def __enter__(self) -> OpenAlex:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
