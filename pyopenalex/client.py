from __future__ import annotations

from pathlib import Path

from pyopenalex._http import HttpClient
from pyopenalex.config import Settings
from pyopenalex.endpoints import Endpoint, WorksEndpoint
from pyopenalex.models.authors import Author
from pyopenalex.models.awards import Award
from pyopenalex.models.continents import Continent
from pyopenalex.models.countries import Country
from pyopenalex.models.domains import Domain
from pyopenalex.models.fields import Field
from pyopenalex.models.funders import Funder
from pyopenalex.models.institution_types import InstitutionType
from pyopenalex.models.institutions import Institution
from pyopenalex.models.keywords import Keyword
from pyopenalex.models.languages import Language
from pyopenalex.models.licenses import License
from pyopenalex.models.publishers import Publisher
from pyopenalex.models.sdgs import Sdg
from pyopenalex.models.source_types import SourceType
from pyopenalex.models.sources import Source
from pyopenalex.models.special import ChangefileDate, ChangefileEntry, RateLimit
from pyopenalex.models.subfields import Subfield
from pyopenalex.models.topics import Topic
from pyopenalex.models.work_types import WorkType
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
        base_url: str | None = None,
        **kwargs: object,
    ) -> None:
        overrides: dict[str, object] = {**kwargs}
        if api_key is not None:
            overrides["api_key"] = api_key
        if base_url is not None:
            overrides["base_url"] = base_url
        settings = Settings(**overrides)  # type: ignore[arg-type]
        self._http = HttpClient(settings)

        self.works: WorksEndpoint[Work] = WorksEndpoint(self._http, "/works", Work)
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

        self.domains: Endpoint[Domain] = Endpoint(self._http, "/domains", Domain)
        """Top-level topic categories (4 total)."""

        self.fields: Endpoint[Field] = Endpoint(self._http, "/fields", Field)
        """Second-level topic categories (26 total)."""

        self.subfields: Endpoint[Subfield] = Endpoint(self._http, "/subfields", Subfield)
        """Third-level topic categories (254 total)."""

        self.sdgs: Endpoint[Sdg] = Endpoint(self._http, "/sdgs", Sdg)
        """UN Sustainable Development Goals (17 total)."""

        self.countries: Endpoint[Country] = Endpoint(self._http, "/countries", Country)
        """Countries for geographic filtering."""

        self.continents: Endpoint[Continent] = Endpoint(self._http, "/continents", Continent)
        """Continents (7 total)."""

        self.languages: Endpoint[Language] = Endpoint(self._http, "/languages", Language)
        """Languages in scholarly works."""

        self.work_types: Endpoint[WorkType] = Endpoint(self._http, "/work-types", WorkType)
        """Work types (article, book, dataset, etc.)."""

        self.source_types: Endpoint[SourceType] = Endpoint(self._http, "/source-types", SourceType)
        """Source types (journal, repository, conference, etc.)."""

        self.institution_types: Endpoint[InstitutionType] = Endpoint(
            self._http, "/institution-types", InstitutionType
        )
        """Institution types (education, healthcare, company, etc.)."""

        self.licenses: Endpoint[License] = Endpoint(self._http, "/licenses", License)
        """Open access licenses (CC BY, CC BY-SA, etc.)."""

        self.awards: Endpoint[Award] = Endpoint(self._http, "/awards", Award)
        """Research grants and funding awards."""

    def rate_limit(self) -> RateLimit:
        """Check current rate limit status. Requires an API key.

        Returns:
            A ``RateLimit`` object with daily cost usage and remaining budget.
        """
        data = self._http.request("GET", "/rate-limit")
        return RateLimit(**data)

    def changefiles(self) -> list[ChangefileDate]:
        """List available changefile dates for bulk data sync.

        Returns:
            A list of ``ChangefileDate`` objects with date and download URL.
        """
        data = self._http.request("GET", "/changefiles")
        return [ChangefileDate(**r) for r in data.get("results", [])]

    def changefile(self, date: str) -> list[ChangefileEntry]:
        """Get changefile details for a specific date.

        Args:
            date: Date string in ``YYYY-MM-DD`` format.

        Returns:
            A list of ``ChangefileEntry`` objects with entity, record count,
            and download URLs for each format.
        """
        data = self._http.request("GET", f"/changefiles/{date}")
        return [ChangefileEntry(**r) for r in data.get("results", [])]

    def download_pdf(self, work_id: str, dest: str | Path) -> Path:
        """Download a PDF for a work ($0.01 per download).

        Args:
            work_id: An OpenAlex work ID (e.g. ``"W2741809807"``).
                Accepts short IDs or full OpenAlex URLs.
            dest: Destination file path or directory. If a directory,
                the file is saved as ``{work_id}.pdf``.

        Returns:
            The path to the downloaded PDF file.
        """
        if work_id.startswith("https://openalex.org/"):
            work_id = work_id.split("openalex.org/")[-1]

        dest = Path(dest)
        if dest.is_dir():
            dest = dest / f"{work_id}.pdf"

        content = self._http.request_bytes(
            "GET", f"https://content.openalex.org/works/{work_id}.pdf"
        )
        dest.write_bytes(content)
        return dest

    def close(self) -> None:
        """Close the underlying HTTP connection."""
        self._http.close()

    def __enter__(self) -> OpenAlex:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
