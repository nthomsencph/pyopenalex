"""PyOpenAlex - A Pydantic-powered Python client for the OpenAlex API."""

from pyopenalex.client import OpenAlex
from pyopenalex.config import Settings
from pyopenalex.expressions import between, gt, lt, ne, or_
from pyopenalex.models import (
    Author,
    Funder,
    Institution,
    Keyword,
    Publisher,
    Source,
    Topic,
    Work,
)

__all__ = [
    "OpenAlex",
    "Settings",
    "Author",
    "Funder",
    "Institution",
    "Keyword",
    "Publisher",
    "Source",
    "Topic",
    "Work",
    "between",
    "gt",
    "lt",
    "ne",
    "or_",
]
