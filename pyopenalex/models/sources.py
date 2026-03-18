from __future__ import annotations

from typing import Any

from pyopenalex.models.base import (
    CountsByYear,
    OpenAlexModel,
    SummaryStats,
)


class ApcPrice(OpenAlexModel):
    price: int
    currency: str


class Source(OpenAlexModel):
    id: str
    issn_l: str | None = None
    issn: list[str] | None = None
    display_name: str
    type: str | None = None
    host_organization: str | None = None
    host_organization_name: str | None = None
    host_organization_lineage: list[str] = []
    is_oa: bool | None = None
    is_in_doaj: bool | None = None
    is_in_doaj_since_year: int | None = None
    is_high_oa_rate: bool | None = None
    is_high_oa_rate_since_year: int | None = None
    is_in_scielo: bool | None = None
    is_ojs: bool | None = None
    is_core: bool | None = None
    oa_flip_year: int | None = None
    first_publication_year: int | None = None
    last_publication_year: int | None = None
    works_count: int | None = None
    oa_works_count: int | None = None
    cited_by_count: int | None = None
    summary_stats: SummaryStats | None = None
    ids: dict[str, Any] | None = None
    homepage_url: str | None = None
    apc_prices: list[ApcPrice] = []
    apc_usd: int | None = None
    country_code: str | None = None
    societies: list[dict[str, Any]] = []
    alternate_titles: list[str] = []
    topics: list[dict[str, Any]] = []
    topic_share: list[dict[str, Any]] = []
    counts_by_year: list[CountsByYear] = []
    works_api_url: str | None = None
    created_date: str | None = None
    updated_date: str | None = None

    @property
    def name(self) -> str:
        return self.display_name

    @property
    def citations(self) -> int | None:
        return self.cited_by_count
