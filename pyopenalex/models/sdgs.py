from __future__ import annotations

from typing import Any

from pyopenalex.models.base import OpenAlexModel


class Sdg(OpenAlexModel):
    """A UN Sustainable Development Goal (17 total).

    Convenience aliases: ``.name``, ``.citations``.
    """

    id: str
    display_name: str
    description: str | None = None
    ids: dict[str, Any] | None = None
    image_url: str | None = None
    image_thumbnail_url: str | None = None
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
