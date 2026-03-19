from __future__ import annotations

from typing import Any

from pyopenalex.models.base import DehydratedEntity, OpenAlexModel


class Subfield(OpenAlexModel):
    """A third-level topic category (254 total), e.g. Artificial Intelligence.

    Convenience aliases: ``.name``, ``.citations``.
    """

    id: str
    display_name: str
    description: str | None = None
    ids: dict[str, Any] | None = None
    display_name_alternatives: list[str] = []
    field: DehydratedEntity | None = None
    domain: DehydratedEntity | None = None
    topics: list[DehydratedEntity] = []
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
