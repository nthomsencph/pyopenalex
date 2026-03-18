from __future__ import annotations

from typing import Any

from pyopenalex.models.base import DehydratedEntity, OpenAlexModel


class Topic(OpenAlexModel):
    """A subject classification in a 4-level hierarchy: domain > field > subfield > topic.

    Convenience aliases: ``.name``, ``.citations``.
    """

    id: str
    display_name: str
    description: str | None = None
    keywords: list[str] = []
    ids: dict[str, Any] | None = None
    subfield: DehydratedEntity | None = None
    field: DehydratedEntity | None = None
    domain: DehydratedEntity | None = None
    siblings: list[DehydratedEntity] = []
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
