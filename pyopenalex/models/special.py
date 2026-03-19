from __future__ import annotations

from pyopenalex.models.base import OpenAlexModel


class RateLimit(OpenAlexModel):
    """Current rate limit status for the authenticated API key."""

    max_cost_per_day_usd: float | None = None
    current_cost_today_usd: float | None = None
    remaining_cost_today_usd: float | None = None


class ChangefileFormat(OpenAlexModel):
    """A single format (jsonl or parquet) of a changefile."""

    size_bytes: int
    size_display: str
    url: str


class ChangefileEntry(OpenAlexModel):
    """A single entity's changefile for a given date."""

    entity: str
    records: int
    formats: dict[str, ChangefileFormat] = {}


class ChangefileDate(OpenAlexModel):
    """An available changefile date."""

    date: str
    url: str
