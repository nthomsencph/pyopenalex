from __future__ import annotations

from pyopenalex.models.base import OpenAlexModel


class SourceType(OpenAlexModel):
    """A type of source (journal, repository, conference, etc.).

    Convenience aliases: ``.name``, ``.citations``.
    """

    id: str
    display_name: str
    description: str | None = None
    works_count: int | None = None
    cited_by_count: int | None = None
    works_api_url: str | None = None
    created_date: str | None = None
    updated_date: str | None = None

    @property
    def name(self) -> str:
        return self.display_name

    @property
    def citations(self) -> int | None:
        return self.cited_by_count
