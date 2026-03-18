from __future__ import annotations

from typing import Any

from pyopenalex.models.base import (
    CountsByYear,
    DehydratedAuthor,
    DehydratedFunder,
    DehydratedInstitution,
    DehydratedSource,
    OpenAlexModel,
)


class Location(OpenAlexModel):
    is_oa: bool | None = None
    landing_page_url: str | None = None
    pdf_url: str | None = None
    source: DehydratedSource | None = None
    license: str | None = None
    license_id: str | None = None
    version: str | None = None
    is_accepted: bool | None = None
    is_published: bool | None = None


class OpenAccess(OpenAlexModel):
    is_oa: bool
    oa_status: str | None = None
    oa_url: str | None = None
    any_repository_has_fulltext: bool | None = None


class Affiliation(OpenAlexModel):
    raw_affiliation_string: str | None = None
    institution_ids: list[str] = []


class Authorship(OpenAlexModel):
    author_position: str | None = None
    author: DehydratedAuthor
    institutions: list[DehydratedInstitution] = []
    countries: list[str] = []
    is_corresponding: bool | None = None
    raw_author_name: str | None = None
    raw_affiliation_strings: list[str] = []
    affiliations: list[Affiliation] = []


class WorkTopic(OpenAlexModel):
    id: str
    display_name: str
    score: float | None = None
    subfield: dict[str, str] | None = None
    field: dict[str, str] | None = None
    domain: dict[str, str] | None = None


class WorkKeyword(OpenAlexModel):
    id: str
    display_name: str
    score: float | None = None


class Award(OpenAlexModel):
    id: str | None = None
    display_name: str | None = None
    funder_award_id: str | None = None
    funder_id: str | None = None


class Biblio(OpenAlexModel):
    volume: str | None = None
    issue: str | None = None
    first_page: str | None = None
    last_page: str | None = None


class HasContent(OpenAlexModel):
    pdf: bool | None = None
    plain: bool | None = None


class Work(OpenAlexModel):
    id: str
    doi: str | None = None
    title: str | None = None
    display_name: str | None = None
    publication_year: int | None = None
    publication_date: str | None = None
    type: str | None = None
    language: str | None = None
    cited_by_count: int | None = None
    is_retracted: bool | None = None
    is_paratext: bool | None = None
    primary_location: Location | None = None
    locations: list[Location] = []
    best_oa_location: Location | None = None
    open_access: OpenAccess | None = None
    authorships: list[Authorship] = []
    ids: dict[str, Any] | None = None
    biblio: Biblio | None = None
    abstract_inverted_index: dict[str, list[int]] | None = None
    referenced_works: list[str] = []
    referenced_works_count: int | None = None
    related_works: list[str] = []
    topics: list[WorkTopic] = []
    primary_topic: WorkTopic | None = None
    keywords: list[WorkKeyword] = []
    funders: list[DehydratedFunder] = []
    awards: list[Award] = []
    fwci: float | None = None
    citation_normalized_percentile: dict[str, Any] | None = None
    cited_by_percentile_year: dict[str, Any] | None = None
    counts_by_year: list[CountsByYear] = []
    sustainable_development_goals: list[dict[str, Any]] = []
    mesh: list[dict[str, Any]] = []
    indexed_in: list[str] = []
    has_content: HasContent | None = None
    content_url: str | None = None
    created_date: str | None = None
    updated_date: str | None = None

    @property
    def abstract(self) -> str | None:
        if not self.abstract_inverted_index:
            return None
        word_positions: list[tuple[int, str]] = []
        for word, positions in self.abstract_inverted_index.items():
            for pos in positions:
                word_positions.append((pos, word))
        word_positions.sort()
        return " ".join(w for _, w in word_positions)
