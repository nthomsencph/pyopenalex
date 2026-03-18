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

        self.works = Endpoint(self._http, "/works", Work)
        self.authors = Endpoint(self._http, "/authors", Author)
        self.sources = Endpoint(self._http, "/sources", Source)
        self.institutions = Endpoint(self._http, "/institutions", Institution)
        self.topics = Endpoint(self._http, "/topics", Topic)
        self.keywords = Endpoint(self._http, "/keywords", Keyword)
        self.publishers = Endpoint(self._http, "/publishers", Publisher)
        self.funders = Endpoint(self._http, "/funders", Funder)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> OpenAlex:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
