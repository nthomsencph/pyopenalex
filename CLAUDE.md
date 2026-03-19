# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

PyOpenAlex is a Pydantic-powered Python client for the OpenAlex API (270M+ scholarly works, 90M+ authors, 100K+ sources). Python 3.10+, version 0.3.2.

## Commands

Use `uv`, not pip.

```bash
uv sync --dev              # Install dependencies
uv run pytest tests/ -v    # Run all tests
uv run pytest tests/test_query.py::test_name -v  # Run single test
uv build                   # Build distribution
ruff check --fix           # Lint (also runs via pre-commit)
ruff format                # Format (also runs via pre-commit)
```

Ruff config: line-length 100, target py313, select E/F/I/UP (ignore UP046).

## Architecture

### Request Flow

`OpenAlex` client exposes typed endpoints (`client.works`, `client.authors`, etc.) → each endpoint method returns either an entity or a `QueryBuilder[T]` → QueryBuilder is **immutable** (every method returns a clone) → no HTTP until `.get()`, `.count()`, or iteration → `HttpClient` executes with tenacity retry (exponential backoff on 429/5xx).

### Key Modules

- **`client.py`** — `OpenAlex` class, registers all endpoints
- **`endpoints.py`** — `Endpoint[T]` (generic), `WorksEndpoint` adds convenience methods (`by_author`, `by_institution`, etc. — two-step ID resolution via search)
- **`query.py`** — `QueryBuilder[T]` (immutable, chainable), `ListResponse[T]`, `_CursorIterator` for pagination
- **`expressions.py`** — Filter expression descriptors (`gt`, `lt`, `ne`, `or_`, `between`) — frozen dataclasses with `to_value()` for serialization
- **`_http.py`** — `HttpClient` wrapping httpx with tenacity retry, injects API key from Settings
- **`config.py`** — `Settings` via pydantic-settings, env prefix `OPENALEX_` (supports .env files)
- **`models/`** — Pydantic models inheriting `OpenAlexModel(extra="allow", populate_by_name=True)`, with convenience aliases (`.name` → `.display_name`, `.citations` → `.cited_by_count`), dehydrated entity variants, and `.to_markdown()` rendering
- **`exceptions.py`** — `NotFoundError` (404), `RateLimitError` (429), `APIError` (5xx)

### Key Patterns

- **Immutable QueryBuilder**: All methods clone state. Enables safe branching: `base = client.works.filter(year=2024); a = base.sort(...); b = base.filter(...)`.
- **Nested filter flattening**: `filter(authorships={"institutions": {"id": "I123"}})` → `authorships.institutions.id:I123`.
- **Cursor-based iteration**: `_CursorIterator` uses `next_cursor` from API meta; `.limit(n)` caps results.
- **Abstract reconstruction**: `Work.abstract` property reconstructs text from inverted index on access.
- **Generic typing**: `Endpoint[T]` and `QueryBuilder[T]` propagate the model type for type checker support.

## Testing

Tests use `FakeHttpClient` (from `tests/conftest.py`) — queue responses with `.enqueue()`, inspect with `.last_request` / `.last_params`. Fixtures are JSON files in `tests/fixtures/`.

## Adding New Things

**New filter expression**: Add frozen dataclass in `expressions.py` with `to_value()`, add factory function, export from `__init__.py`.

**New entity type**: Create model in `models/`, export from `models/__init__.py`, add endpoint in `client.py`, export from `__init__.py`, add markdown renderer in `markdown.py`.

**New QueryBuilder method**: Must return `self._clone()` with updated state. Test that original is not mutated.
