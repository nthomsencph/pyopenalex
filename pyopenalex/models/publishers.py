from __future__ import annotations

from typing import Any

from pyopenalex.models.base import (
    CountsByYear,
    OpenAlexModel,
    Role,
    SummaryStats,
)


class Publisher(OpenAlexModel):
    """A publishing organization.

    Convenience aliases: ``.name``, ``.citations``.
    """

    id: str
    display_name: str
    alternate_titles: list[str] = []
    country_codes: list[str] = []
    hierarchy_level: int | None = None
    parent_publisher: str | None = None
    lineage: list[str] = []
    works_count: int | None = None
    cited_by_count: int | None = None
    summary_stats: SummaryStats | None = None
    ids: dict[str, Any] | None = None
    counts_by_year: list[CountsByYear] = []
    roles: list[Role] = []
    sources_api_url: str | None = None
    homepage_url: str | None = None
    image_url: str | None = None
    image_thumbnail_url: str | None = None
    created_date: str | None = None
    updated_date: str | None = None

    @property
    def name(self) -> str:
        return self.display_name

    @property
    def citations(self) -> int | None:
        return self.cited_by_count
