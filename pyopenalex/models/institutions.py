from __future__ import annotations

from typing import Any

from pyopenalex.models.base import (
    CountsByYear,
    OpenAlexModel,
    Role,
    SummaryStats,
)


class Geo(OpenAlexModel):
    city: str | None = None
    geonames_city_id: str | None = None
    region: str | None = None
    country_code: str | None = None
    country: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class Institution(OpenAlexModel):
    """A university, research organization, or other institution.

    Convenience aliases: ``.name``, ``.citations``.
    """

    id: str
    ror: str | None = None
    display_name: str
    country_code: str | None = None
    type: str | None = None
    homepage_url: str | None = None
    image_url: str | None = None
    image_thumbnail_url: str | None = None
    display_name_acronyms: list[str] = []
    display_name_alternatives: list[str] = []
    works_count: int | None = None
    cited_by_count: int | None = None
    summary_stats: SummaryStats | None = None
    geo: Geo | None = None
    lineage: list[str] = []
    ids: dict[str, Any] | None = None
    counts_by_year: list[CountsByYear] = []
    roles: list[Role] = []
    topics: list[dict[str, Any]] = []
    works_api_url: str | None = None
    created_date: str | None = None
    updated_date: str | None = None

    @property
    def name(self) -> str:
        return self.display_name

    @property
    def citations(self) -> int | None:
        return self.cited_by_count
