from __future__ import annotations

from typing import Any

from pyopenalex.models.base import DehydratedEntity, OpenAlexModel


class Country(OpenAlexModel):
    """A country for geographic filtering of scholarly works.

    Convenience aliases: ``.name``, ``.citations``.
    """

    id: str
    display_name: str
    country_code: str | None = None
    description: str | None = None
    ids: dict[str, Any] | None = None
    display_name_alternatives: list[str] = []
    continent: DehydratedEntity | None = None
    is_global_south: bool | None = None
    works_count: int | None = None
    cited_by_count: int | None = None
    authors_api_url: str | None = None
    institutions_api_url: str | None = None
    works_api_url: str | None = None
    created_date: str | None = None
    updated_date: str | None = None

    @property
    def name(self) -> str:
        return self.display_name

    @property
    def citations(self) -> int | None:
        return self.cited_by_count
