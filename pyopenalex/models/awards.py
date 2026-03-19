from __future__ import annotations

from pyopenalex.models.base import DehydratedFunder, OpenAlexModel


class Award(OpenAlexModel):
    """A research grant or funding award.

    Convenience aliases: ``.name``.
    """

    id: str
    display_name: str | None = None
    funder: DehydratedFunder | None = None
    funder_award_id: str | None = None
    funded_outputs_count: int | None = None
    funded_outputs: list[str] = []
    works_api_url: str | None = None
    created_date: str | None = None
    updated_date: str | None = None

    @property
    def name(self) -> str | None:
        return self.display_name
