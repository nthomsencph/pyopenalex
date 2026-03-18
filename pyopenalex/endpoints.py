from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar, overload

from pyopenalex.models.autocomplete import AutocompleteResult
from pyopenalex.models.base import OpenAlexModel
from pyopenalex.query import QueryBuilder

if TYPE_CHECKING:
    from pyopenalex._http import HttpClient

T = TypeVar("T", bound=OpenAlexModel)


class Endpoint(Generic[T]):
    def __init__(self, http: HttpClient, path: str, model: type[T]) -> None:
        self._http = http
        self._path = path
        self._model = model

    @overload
    def get(self, id: str) -> T: ...
    @overload
    def get(self, id: list[str]) -> list[T]: ...

    def get(self, id: str | list[str]) -> T | list[T]:
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
        """Fetch up to 100 entities by ID using OR filter."""
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
        data = self._http.request("GET", f"{self._path}/random")
        return self._model(**data)

    def autocomplete(self, query: str) -> list[AutocompleteResult]:
        entity_type = self._path.strip("/")
        data = self._http.request("GET", f"/autocomplete/{entity_type}", params={"q": query})
        return [AutocompleteResult(**r) for r in data.get("results", [])]

    def _query(self) -> QueryBuilder[T]:
        return QueryBuilder(self._http, self._path, self._model)

    def __call__(self, **kwargs: object) -> QueryBuilder[T]:
        return self._query().filter(**kwargs)

    def filter(self, **kwargs: object) -> QueryBuilder[T]:
        return self._query().filter(**kwargs)

    def filter_raw(self, raw: str) -> QueryBuilder[T]:
        return self._query().filter_raw(raw)

    def search(self, query: str) -> QueryBuilder[T]:
        return self._query().search(query)

    def search_filter(self, **kwargs: str) -> QueryBuilder[T]:
        return self._query().search_filter(**kwargs)

    def sort(self, field: str, desc: bool = False) -> QueryBuilder[T]:
        return self._query().sort(field, desc)

    def per_page(self, n: int) -> QueryBuilder[T]:
        return self._query().per_page(n)

    def select(self, *fields: str) -> QueryBuilder[T]:
        return self._query().select(*fields)

    def sample(self, n: int, seed: int | None = None) -> QueryBuilder[T]:
        return self._query().sample(n, seed)

    def group_by(self, field: str) -> QueryBuilder[T]:
        return self._query().group_by(field)

    def list(self, **kwargs: object) -> QueryBuilder[T]:
        return self._query().filter(**kwargs)

    def count(self, **kwargs: object) -> int:
        return self.filter(**kwargs).count()
