from __future__ import annotations

from typing import Any

from pyopenalex.models.base import DehydratedEntity, OpenAlexModel


class Field(OpenAlexModel):
    """A second-level topic category (26 total), e.g. Computer Science, Medicine.

    Convenience aliases: ``.name``, ``.citations``.
    """

    id: str
    display_name: str
    description: str | None = None
    ids: dict[str, Any] | None = None
    display_name_alternatives: list[str] = []
    domain: DehydratedEntity | None = None
    subfields: list[DehydratedEntity] = []
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
