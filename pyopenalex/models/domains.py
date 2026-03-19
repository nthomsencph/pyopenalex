from __future__ import annotations

from typing import Any

from pyopenalex.models.base import DehydratedEntity, OpenAlexModel


class Domain(OpenAlexModel):
    """A top-level topic category (4 total): Life Sciences, Social Sciences, etc.

    Convenience aliases: ``.name``, ``.citations``.
    """

    id: str
    display_name: str
    description: str | None = None
    ids: dict[str, Any] | None = None
    display_name_alternatives: list[str] = []
    fields: list[DehydratedEntity] = []
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
