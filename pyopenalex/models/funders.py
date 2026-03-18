from __future__ import annotations

from typing import Any

from pyopenalex.models.base import (
    CountsByYear,
    OpenAlexModel,
    Role,
    SummaryStats,
)


class Funder(OpenAlexModel):
    id: str
    display_name: str
    alternate_titles: list[str] = []
    country_code: str | None = None
    description: str | None = None
    homepage_url: str | None = None
    image_url: str | None = None
    image_thumbnail_url: str | None = None
    awards_count: int | None = None
    works_count: int | None = None
    cited_by_count: int | None = None
    summary_stats: SummaryStats | None = None
    ids: dict[str, Any] | None = None
    counts_by_year: list[CountsByYear] = []
    roles: list[Role] = []
    created_date: str | None = None
    updated_date: str | None = None
