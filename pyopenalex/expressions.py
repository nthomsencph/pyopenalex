"""Filter expressions for building OpenAlex queries.

Inspired by FastAPI's Query/Path/Body pattern — small descriptor objects
that the QueryBuilder knows how to serialize into OpenAlex filter syntax.

Usage:
    from pyopenalex import gt, lt, ne, or_, between

    client.works.filter(cited_by_count=gt(100))
    client.works.filter(type=ne("paratext"))
    client.works.filter(publication_year=between(2020, 2024))
    client.works.filter(doi=or_("10.1234/a", "10.1234/b"))
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FilterExpression:
    def to_value(self) -> str:
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class Gt(FilterExpression):
    value: int | float | str

    def to_value(self) -> str:
        return f">{self.value}"


@dataclass(frozen=True, slots=True)
class Lt(FilterExpression):
    value: int | float | str

    def to_value(self) -> str:
        return f"<{self.value}"


@dataclass(frozen=True, slots=True)
class Ne(FilterExpression):
    value: str | int | float | bool

    def to_value(self) -> str:
        v = str(self.value).lower() if isinstance(self.value, bool) else str(self.value)
        return f"!{v}"


@dataclass(frozen=True, slots=True)
class Or(FilterExpression):
    values: tuple[str | int | float, ...]

    def to_value(self) -> str:
        return "|".join(str(v) for v in self.values)


@dataclass(frozen=True, slots=True)
class Between(FilterExpression):
    low: int | float | str
    high: int | float | str

    def to_value(self) -> str:
        return f"{self.low}-{self.high}"


def gt(value: int | float | str) -> Gt:
    return Gt(value)


def lt(value: int | float | str) -> Lt:
    return Lt(value)


def ne(value: str | int | float | bool) -> Ne:
    return Ne(value)


def or_(*values: str | int | float) -> Or:
    return Or(values)


def between(low: int | float | str, high: int | float | str) -> Between:
    return Between(low, high)
