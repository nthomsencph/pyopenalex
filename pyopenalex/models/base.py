from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class OpenAlexModel(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)


class Meta(OpenAlexModel):
    count: int
    db_response_time_ms: int
    page: int | None = None
    per_page: int | None = None
    next_cursor: str | None = None
    groups_count: int | None = None
    cost_usd: float | None = None


class GroupByResult(OpenAlexModel):
    key: str
    key_display_name: str
    count: int


class SummaryStats(OpenAlexModel):
    two_yr_mean_citedness: float | None = None
    h_index: int | None = None
    i10_index: int | None = None

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        alias_generator=None,
    )

    def __init__(self, **data: object) -> None:
        if "2yr_mean_citedness" in data:
            data["two_yr_mean_citedness"] = data.pop("2yr_mean_citedness")
        super().__init__(**data)


class CountsByYear(OpenAlexModel):
    year: int
    works_count: int | None = None
    cited_by_count: int | None = None
    oa_works_count: int | None = None


class Role(OpenAlexModel):
    role: str
    id: str
    works_count: int


class DehydratedEntity(OpenAlexModel):
    id: str
    display_name: str


class DehydratedAuthor(OpenAlexModel):
    id: str | None = None
    display_name: str | None = None
    orcid: str | None = None


class DehydratedInstitution(OpenAlexModel):
    id: str
    display_name: str
    ror: str | None = None
    country_code: str | None = None
    type: str | None = None
    lineage: list[str] = []


class DehydratedSource(OpenAlexModel):
    id: str
    display_name: str
    issn_l: str | None = None
    issn: list[str] | None = None
    is_oa: bool | None = None
    is_in_doaj: bool | None = None
    is_core: bool | None = None
    host_organization: str | None = None
    host_organization_name: str | None = None
    host_organization_lineage: list[str] = []
    type: str | None = None


class DehydratedFunder(OpenAlexModel):
    id: str
    display_name: str
    ror: str | None = None
