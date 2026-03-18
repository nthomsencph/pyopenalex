from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Iterator, TypeVar

from pyopenalex.expressions import FilterExpression
from pyopenalex.models.base import GroupByResult, Meta, OpenAlexModel

if TYPE_CHECKING:
    from pyopenalex._http import HttpClient

T = TypeVar("T", bound=OpenAlexModel)


class ListResponse(OpenAlexModel, Generic[T]):
    meta: Meta
    results: list[T]
    group_by: list[GroupByResult] = []


def _flatten_filters(prefix: str, value: Any) -> list[tuple[str, str]]:
    """Flatten nested dicts into dot-notation filter pairs.

    Example:
        _flatten_filters("authorships", {"institutions": {"id": "I123"}})
        → [("authorships.institutions.id", "I123")]
    """
    if isinstance(value, dict):
        pairs: list[tuple[str, str]] = []
        for k, v in value.items():
            pairs.extend(_flatten_filters(f"{prefix}.{k}", v))
        return pairs
    return [(prefix, value)]


def _serialize_value(value: Any) -> str:
    if isinstance(value, FilterExpression):
        return value.to_value()
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (list, tuple)):
        return "|".join(str(v) for v in value)
    return str(value)


class QueryBuilder(Generic[T]):
    def __init__(
        self,
        http: HttpClient,
        path: str,
        model: type[T],
    ) -> None:
        self._http = http
        self._path = path
        self._model = model
        self._params: dict[str, Any] = {}
        self._filters: dict[str, str] = {}
        self._limit: int | None = None

    def _clone(self) -> QueryBuilder[T]:
        qb = QueryBuilder(self._http, self._path, self._model)
        qb._params = dict(self._params)
        qb._filters = dict(self._filters)
        qb._limit = self._limit
        return qb

    def filter(self, **kwargs: Any) -> QueryBuilder[T]:
        qb = self._clone()
        for key, value in kwargs.items():
            if isinstance(value, dict):
                for flat_key, flat_val in _flatten_filters(key, value):
                    qb._filters[flat_key] = _serialize_value(flat_val)
            else:
                qb._filters[key] = _serialize_value(value)
        return qb

    def filter_raw(self, raw: str) -> QueryBuilder[T]:
        qb = self._clone()
        qb._params["filter"] = raw
        qb._filters.clear()
        return qb

    def search(self, query: str) -> QueryBuilder[T]:
        qb = self._clone()
        qb._params["search"] = query
        return qb

    def search_filter(self, **kwargs: str) -> QueryBuilder[T]:
        """Field-specific search: search_filter(title="neural networks")."""
        qb = self._clone()
        for key, value in kwargs.items():
            qb._filters[f"{key}.search"] = value
        return qb

    def sort(self, field: str, desc: bool = False) -> QueryBuilder[T]:
        qb = self._clone()
        suffix = ":desc" if desc else ""
        qb._params["sort"] = f"{field}{suffix}"
        return qb

    def per_page(self, n: int) -> QueryBuilder[T]:
        qb = self._clone()
        qb._params["per_page"] = n
        return qb

    def page(self, n: int) -> QueryBuilder[T]:
        qb = self._clone()
        qb._params["page"] = n
        return qb

    def select(self, *fields: str) -> QueryBuilder[T]:
        qb = self._clone()
        qb._params["select"] = ",".join(fields)
        return qb

    def sample(self, n: int, seed: int | None = None) -> QueryBuilder[T]:
        qb = self._clone()
        qb._params["sample"] = n
        if seed is not None:
            qb._params["seed"] = seed
        return qb

    def group_by(self, field: str) -> QueryBuilder[T]:
        qb = self._clone()
        qb._params["group_by"] = field
        return qb

    def limit(self, n: int) -> QueryBuilder[T]:
        """Cap the total number of results yielded during iteration."""
        qb = self._clone()
        qb._limit = n
        return qb

    def _build_params(self) -> dict[str, Any]:
        params = dict(self._params)
        if self._filters:
            parts = [f"{k}:{v}" for k, v in self._filters.items()]
            existing = params.get("filter", "")
            if existing:
                parts.insert(0, existing)
            params["filter"] = ",".join(parts)
        return params

    def get(self) -> ListResponse[T]:
        params = self._build_params()
        data = self._http.request("GET", self._path, params=params)
        return ListResponse[self._model](
            meta=Meta(**data["meta"]),
            results=[self._model(**r) for r in data.get("results", [])],
            group_by=[GroupByResult(**g) for g in data.get("group_by", [])],
        )

    def count(self) -> int:
        qb = self.per_page(1).select("id")
        return qb.get().meta.count

    def __iter__(self) -> Iterator[T]:
        return _CursorIterator(self, self._limit)


class _CursorIterator(Iterator[T]):
    def __init__(self, qb: QueryBuilder[T], limit: int | None) -> None:
        self._qb = qb
        self._limit = limit
        self._cursor: str | None = "*"
        self._buffer: list[T] = []
        self._pos = 0
        self._yielded = 0

    def __next__(self) -> T:
        if self._limit is not None and self._yielded >= self._limit:
            raise StopIteration
        if self._pos < len(self._buffer):
            item = self._buffer[self._pos]
            self._pos += 1
            self._yielded += 1
            return item
        if self._cursor is None:
            raise StopIteration
        self._fetch_next()
        if not self._buffer:
            raise StopIteration
        self._pos = 1
        self._yielded += 1
        return self._buffer[0]

    def _fetch_next(self) -> None:
        params = self._qb._build_params()
        params["cursor"] = self._cursor
        params.pop("page", None)
        data = self._qb._http.request("GET", self._qb._path, params=params)
        self._buffer = [self._qb._model(**r) for r in data.get("results", [])]
        self._cursor = data["meta"].get("next_cursor")
