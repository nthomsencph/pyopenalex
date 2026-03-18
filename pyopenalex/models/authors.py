from __future__ import annotations

from typing import Any

from pyopenalex.models.base import (
    CountsByYear,
    DehydratedInstitution,
    OpenAlexModel,
    SummaryStats,
)


class AuthorAffiliation(OpenAlexModel):
    institution: DehydratedInstitution
    years: list[int] = []


class Author(OpenAlexModel):
    """A researcher profile with disambiguated identity.

    Convenience aliases: ``.name``, ``.citations``.
    """

    id: str
    orcid: str | None = None
    display_name: str
    display_name_alternatives: list[str] = []
    longest_name: str | None = None
    parsed_longest_name: dict[str, Any] | None = None
    works_count: int | None = None
    cited_by_count: int | None = None
    summary_stats: SummaryStats | None = None
    affiliations: list[AuthorAffiliation] = []
    last_known_institutions: list[DehydratedInstitution] | None = None
    topics: list[dict[str, Any]] = []
    counts_by_year: list[CountsByYear] = []
    ids: dict[str, Any] | None = None
    works_api_url: str | None = None
    created_date: str | None = None
    updated_date: str | None = None

    @property
    def name(self) -> str:
        return self.display_name

    @property
    def citations(self) -> int | None:
        return self.cited_by_count
