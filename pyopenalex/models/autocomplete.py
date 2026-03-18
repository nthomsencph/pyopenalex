from __future__ import annotations

from pyopenalex.models.base import OpenAlexModel


class AutocompleteResult(OpenAlexModel):
    id: str
    display_name: str | None = None
    hint: str | None = None
    cited_by_count: int | None = None
    works_count: int | None = None
    entity_type: str | None = None
    external_id: str | None = None
