---
name: pyopenalex
description: Use this skill when writing Python code that queries OpenAlex (scholarly works, authors, institutions, sources, topics, publishers, funders). Provides the pyopenalex API reference and usage patterns.
---

# PyOpenAlex

A Pydantic-powered Python client for the OpenAlex API. Install with `pip install pyopenalex`.

## Setup

```python
from pyopenalex import OpenAlex

# API key via constructor or OPENALEX_API_KEY env var
client = OpenAlex(api_key="...")

# Or as context manager
with OpenAlex() as client:
    ...
```

## Entity Endpoints

```python
client.works          # Scholarly documents
client.authors        # Researcher profiles
client.sources        # Journals, repositories
client.institutions   # Universities, organizations
client.topics         # Subject classifications
client.keywords       # Extracted keywords
client.publishers     # Publishing organizations
client.funders        # Funding agencies
```

## Single Entity Lookup

```python
# By OpenAlex ID
work = client.works.get("W2741809807")

# By external ID
work = client.works.get("https://doi.org/10.7717/peerj.4375")
author = client.authors.get("https://orcid.org/0000-0001-6187-6610")
inst = client.institutions.get("https://ror.org/0161xgx34")

# Batch (up to 100)
works = client.works.get(["W2741809807", "W2100837269"])

# Random
work = client.works.random()
```

## Finding Works by Name

Two-step ID resolution handled automatically:

```python
client.works.by_author("Yann LeCun").sort("cited_by_count", desc=True).get(10)
client.works.by_institution("MIT").filter(publication_year=2024).get(10)
client.works.by_source("Nature").filter(publication_year=2024).count()
client.works.by_topic("machine learning").get(10)
client.works.by_funder("NIH").filter(is_oa=True).get(10)
```

## Fetching Results

```python
# Get exactly n results (auto-paginates if n > 100)
results = client.works.search("CRISPR").get(10)

# Get all matching results
results = client.works.filter(publication_year=2024, type="dataset").get(all=True)

# Default: single page (25 results)
results = client.works.search("CRISPR").get()

# Access response
results.meta        # Meta: count, page, per_page, cost_usd
results.results     # list[Work]
results.group_by    # list[GroupByResult]
```

## Filtering

IMPORTANT: Always resolve entity names to IDs first. Never filter by name directly.

```python
# Simple filters
client.works.filter(publication_year=2024, is_oa=True)

# Filter expressions
from pyopenalex import gt, lt, ne, or_, between

client.works.filter(cited_by_count=gt(100))
client.works.filter(type=ne("paratext"))
client.works.filter(publication_year=between(2020, 2024))
client.works.filter(doi=or_("https://doi.org/10.1/a", "https://doi.org/10.1/b"))

# Nested filters (auto-flattened to dot notation)
client.works.filter(authorships={"institutions": {"id": "I136199984"}})

# Raw filter string
client.works.filter_raw("publication_year:2024,cited_by_count:>100")
```

## Search

```python
# Full-text search
client.works.search("machine learning")

# Field-specific search
client.works.search_filter(title="neural networks")
```

## Chaining

The query builder is immutable. Each method returns a new instance.

```python
results = (
    client.works
    .filter(publication_year=2024, is_oa=True)
    .search("CRISPR")
    .sort("cited_by_count", desc=True)
    .select("id", "title", "doi", "cited_by_count")
    .get(10)
)
```

## Iteration

```python
# Automatic cursor pagination
for work in client.works.filter(publication_year=2024):
    print(work.title)

# With safety cap
for work in client.works.filter(publication_year=2024).limit(500):
    process(work)
```

## Other Operations

```python
# Count
count = client.works.filter(publication_year=2024).count()

# Group by
response = client.works.filter(publication_year=2024).group_by("type").get()
for group in response.group_by:
    print(f"{group.key_display_name}: {group.count}")

# Sample
results = client.works.sample(100, seed=42).get()

# Autocomplete
results = client.institutions.autocomplete("harvard")
```

## Markdown Rendering

All entities support `.to_markdown()` for LLM-friendly output:

```python
work = client.works.get("W2741809807")
print(work.to_markdown())

# Truncate long abstracts
print(work.to_markdown(limit_abstract=150))
```

## Convenience Aliases

All entities have `.name` (alias for `display_name`) and `.citations` (alias for `cited_by_count`).

Work also has:
- `.year` (alias for `publication_year`)
- `.authors` (list of author name strings)
- `.abstract` (reconstructed from inverted index)

```python
work = client.works.get("W2741809807")
print(f"{work.title} ({work.year}), {work.citations} citations")
print(f"Authors: {', '.join(work.authors)}")
```

## Two-Step ID Resolution Pattern

IMPORTANT: Never filter by entity names directly. Use `by_*` methods or resolve to IDs first.

```python
# WRONG: filtering by name
client.works.filter(author_name="Einstein")  # Will fail

# BEST: use convenience methods
client.works.by_author("Einstein").get(10)

# ALSO CORRECT: manual two-step
authors = client.authors.search("Einstein").get(1)
author_id = authors.results[0].id
works = client.works.filter(authorships={"author": {"id": author_id}}).get(10)
```

## Key Model Fields

### Work
`id`, `doi`, `title`, `publication_year`, `publication_date`, `type`, `language`, `cited_by_count`, `is_retracted`, `is_paratext`, `primary_location`, `locations`, `best_oa_location`, `open_access`, `authorships`, `biblio`, `abstract` (property), `topics`, `primary_topic`, `keywords`, `funders`, `awards`, `fwci`, `counts_by_year`, `referenced_works`, `related_works`

### Author
`id`, `orcid`, `display_name`, `works_count`, `cited_by_count`, `summary_stats`, `affiliations`, `last_known_institutions`, `topics`

### Institution
`id`, `ror`, `display_name`, `country_code`, `type`, `geo`, `works_count`, `cited_by_count`, `summary_stats`

### Source
`id`, `issn_l`, `issn`, `display_name`, `type`, `is_oa`, `is_in_doaj`, `works_count`, `cited_by_count`, `apc_usd`

### Topic
`id`, `display_name`, `description`, `keywords`, `subfield`, `field`, `domain`, `siblings`

## Error Handling

```python
from pyopenalex.exceptions import NotFoundError, RateLimitError, APIError

try:
    work = client.works.get("W0000000000")
except NotFoundError:
    ...
except RateLimitError:
    ...
except APIError as e:
    print(e.status_code)
```

Retries with exponential backoff are automatic for 429 and 5xx responses.

## Common Filter Fields (Works)

`publication_year`, `cited_by_count`, `is_oa`, `is_retracted`, `type`, `language`, `has_fulltext`, `has_doi`, `doi`, `authorships.author.id`, `authorships.institutions.id`, `authorships.institutions.country_code`, `primary_location.source.id`, `topics.id`, `primary_topic.id`, `funders.id`, `open_access.oa_status`

## Sort Fields

`cited_by_count`, `publication_date`, `relevance_score` (requires search), `works_count`, `display_name`
