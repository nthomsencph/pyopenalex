from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar, overload

from pyopenalex.models.autocomplete import AutocompleteResult
from pyopenalex.models.base import OpenAlexModel
from pyopenalex.query import QueryBuilder

if TYPE_CHECKING:
    from pyopenalex._http import HttpClient

T = TypeVar("T", bound=OpenAlexModel)


class Endpoint(Generic[T]):
    """Typed access to a single OpenAlex entity type.

    Provides methods for fetching, filtering, searching, and iterating
    over entities. Each method returns either an entity instance or a
    ``QueryBuilder`` for further chaining.
    """

    def __init__(self, http: HttpClient, path: str, model: type[T]) -> None:
        self._http = http
        self._path = path
        self._model = model

    @overload
    def get(self, id: str) -> T: ...
    @overload
    def get(self, id: list[str]) -> list[T]: ...

    def get(self, id: str | list[str]) -> T | list[T]:
        """Fetch one or more entities by ID.

        Args:
            id: An OpenAlex ID (``"W2741809807"``), external ID URL
                (DOI, ORCID, ROR), or a list of IDs for batch lookup
                (up to 100).

        Returns:
            A single entity when given a string, or a list when given a list.
        """
        if isinstance(id, list):
            return self._batch_get(id)
        path = self._resolve_path(id)
        data = self._http.request("GET", path)
        return self._model(**data)

    def _resolve_path(self, id: str) -> str:
        if id.startswith("https://openalex.org/"):
            return "/" + id.split("openalex.org/")[-1]
        if id.startswith("http"):
            return f"{self._path}/{id}"
        return f"{self._path}/{id}"

    def _batch_get(self, ids: list[str]) -> list[T]:
        openalex_ids = []
        for id in ids:
            if id.startswith("https://openalex.org/"):
                openalex_ids.append(id)
            elif not id.startswith("http"):
                openalex_ids.append(id)
            else:
                openalex_ids.append(id)
        filter_value = "|".join(openalex_ids)
        qb = self._query().filter_raw(f"openalex:{filter_value}").per_page(len(ids))
        return qb.get().results

    def random(self) -> T:
        """Fetch a random entity of this type."""
        data = self._http.request("GET", f"{self._path}/random")
        return self._model(**data)

    def autocomplete(self, query: str) -> list[AutocompleteResult]:
        """Fast typeahead search, returning up to 10 results.

        Args:
            query: The search prefix to autocomplete.

        Returns:
            A list of ``AutocompleteResult`` objects.
        """
        entity_type = self._path.strip("/")
        data = self._http.request("GET", f"/autocomplete/{entity_type}", params={"q": query})
        return [AutocompleteResult(**r) for r in data.get("results", [])]

    def _query(self) -> QueryBuilder[T]:
        return QueryBuilder(self._http, self._path, self._model)

    def __call__(self, **kwargs: object) -> QueryBuilder[T]:
        """Shorthand for ``.filter(**kwargs)``."""
        return self._query().filter(**kwargs)

    def filter(self, **kwargs: object) -> QueryBuilder[T]:
        """Filter entities. Accepts field names as keyword arguments.

        Supports filter expressions: ``gt()``, ``lt()``, ``ne()``,
        ``or_()``, ``between()``, and nested dicts for dot-notation paths.
        """
        return self._query().filter(**kwargs)

    def filter_raw(self, raw: str) -> QueryBuilder[T]:
        """Filter with a raw OpenAlex filter string.

        Args:
            raw: A filter string like ``"publication_year:2024,is_oa:true"``.
        """
        return self._query().filter_raw(raw)

    def search(self, query: str) -> QueryBuilder[T]:
        """Full-text search across the entity's searchable fields.

        Args:
            query: The search query. Supports boolean operators (AND, OR, NOT),
                phrases (``"exact phrase"``), and wildcards (``*``, ``?``).
        """
        return self._query().search(query)

    def search_filter(self, **kwargs: str) -> QueryBuilder[T]:
        """Field-specific search.

        Example::

            client.works.search_filter(title="neural networks")
        """
        return self._query().search_filter(**kwargs)

    def sort(self, field: str, desc: bool = False) -> QueryBuilder[T]:
        """Sort results by a field.

        Args:
            field: Sort field (e.g. ``"cited_by_count"``, ``"publication_date"``).
            desc: Sort descending if ``True``.
        """
        return self._query().sort(field, desc)

    def per_page(self, n: int) -> QueryBuilder[T]:
        """Set the number of results per page (1-100)."""
        return self._query().per_page(n)

    def select(self, *fields: str) -> QueryBuilder[T]:
        """Limit response to specific top-level fields.

        Args:
            *fields: Field names to include (e.g. ``"id"``, ``"title"``, ``"doi"``).
        """
        return self._query().select(*fields)

    def sample(self, n: int, seed: int | None = None) -> QueryBuilder[T]:
        """Return a random sample of results.

        Args:
            n: Number of results to sample (max 10,000).
            seed: Seed for reproducible sampling.
        """
        return self._query().sample(n, seed)

    def group_by(self, field: str) -> QueryBuilder[T]:
        """Aggregate results by a field.

        Args:
            field: The field to group by (e.g. ``"type"``, ``"publication_year"``).
        """
        return self._query().group_by(field)

    def list(self, **kwargs: object) -> QueryBuilder[T]:
        """Alias for ``.filter(**kwargs)``."""
        return self._query().filter(**kwargs)

    def count(self, **kwargs: object) -> int:
        """Count matching entities without fetching them.

        Args:
            **kwargs: Optional filters to apply before counting.

        Returns:
            The total number of matching entities.
        """
        return self.filter(**kwargs).count()
