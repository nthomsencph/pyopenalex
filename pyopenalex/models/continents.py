from __future__ import annotations

from typing import Any

from pyopenalex.models.base import DehydratedEntity, OpenAlexModel


class Continent(OpenAlexModel):
    """A continent (7 total) for geographic filtering.

    Convenience aliases: ``.name``.
    """

    id: str
    display_name: str
    description: str | None = None
    ids: dict[str, Any] | None = None
    display_name_alternatives: list[str] = []
    countries: list[DehydratedEntity] = []
    created_date: str | None = None
    updated_date: str | None = None

    @property
    def name(self) -> str:
        return self.display_name
