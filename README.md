<p align="center">
  <img src="https://raw.githubusercontent.com/nthomsencph/pyopenalex/main/logo.png" alt="PyOpenAlex" width="320">
</p>

<p align="center">
  A Pydantic-powered Python client for the <a href="https://openalex.org">OpenAlex API</a>.
</p>

OpenAlex is an open catalog of the global research system: 270M+ scholarly works, 90M+ authors, and 100K+ sources. PyOpenAlex gives you typed access to all of it with an API that follows the patterns of FastAPI and Pydantic.

```python
from pyopenalex import OpenAlex, gt

with OpenAlex() as client:
    for work in client.works.filter(cited_by_count=gt(1000), publication_year=2024).limit(10):
        print(f"{work.title} ({work.cited_by_count} citations)")
```

## Installation

```bash
pip install pyopenalex
```

Requires Python 3.13+.

## Quick Start

```python
from pyopenalex import OpenAlex

client = OpenAlex(api_key="your-key")  # or set OPENALEX_API_KEY env var

# Get a single work by ID
work = client.works.get("W2741809807")
print(work.title)
print(work.doi)
print(work.abstract)  # reconstructed from inverted index

# Search for authors
results = client.authors.search("Einstein").per_page(5).get()
for author in results.results:
    print(f"{author.display_name}: {author.works_count} works")
```

## Entities

PyOpenAlex supports all core OpenAlex entity types:

```python
client.works          # Scholarly documents (articles, books, datasets)
client.authors        # Researcher profiles
client.sources        # Journals, repositories, conferences
client.institutions   # Universities, research organizations
client.topics         # Subject classifications
client.keywords       # Extracted keywords
client.publishers     # Publishing organizations
client.funders        # Funding agencies
```

Every entity is a Pydantic model with fully typed fields:

```python
work = client.works.get("W2741809807")

work.title                              # str | None
work.publication_year                   # int | None
work.cited_by_count                     # int | None
work.open_access.is_oa                  # bool
work.open_access.oa_status              # str (gold, green, hybrid, bronze, diamond, closed)
work.authorships[0].author.display_name # str | None
work.authorships[0].institutions        # list[DehydratedInstitution]
work.primary_location.source            # DehydratedSource | None
```

## Looking Up Entities

### By OpenAlex ID

```python
work = client.works.get("W2741809807")
author = client.authors.get("A5023888391")
```

### By External ID

Works accept DOIs, authors accept ORCIDs, institutions accept ROR IDs:

```python
work = client.works.get("https://doi.org/10.7717/peerj.4375")
author = client.authors.get("https://orcid.org/0000-0001-6187-6610")
institution = client.institutions.get("https://ror.org/0161xgx34")
```

### Batch Lookup

Fetch up to 100 entities at once:

```python
works = client.works.get(["W2741809807", "W2100837269", "W1775749144"])
```

### Random Entity

```python
work = client.works.random()
```

## Filtering

Chain `.filter()` calls to narrow results. Multiple filters combine with AND:

```python
results = (
    client.works
    .filter(publication_year=2024, is_oa=True)
    .sort("cited_by_count", desc=True)
    .per_page(100)
    .get()
)
```

### Filter Expressions

PyOpenAlex provides expression functions for building filters, similar to how FastAPI uses `Query()`, `Path()`, and `Body()`:

```python
from pyopenalex import gt, lt, ne, or_, between

# Greater than / less than
client.works.filter(cited_by_count=gt(100))
client.works.filter(publication_year=lt(2020))

# Not equal
client.works.filter(type=ne("paratext"))

# OR (up to 100 values)
client.works.filter(doi=or_(
    "https://doi.org/10.7717/peerj.4375",
    "https://doi.org/10.1038/nature12373",
))

# Range
client.works.filter(publication_year=between(2020, 2024))
```

### Nested Filters

Use dicts for dot-notation filter paths. PyOpenAlex flattens them automatically:

```python
# These are equivalent:
client.works.filter(authorships={"institutions": {"id": "I136199984"}})
client.works.filter_raw("authorships.institutions.id:I136199984")
```

### Raw Filters

For full control, pass the filter string directly:

```python
client.works.filter_raw("publication_year:2024,is_oa:true,cited_by_count:>100")
```

## Searching

### Full-Text Search

```python
results = client.works.search("machine learning").get()
```

### Field-Specific Search

```python
results = client.works.search_filter(title="neural networks").get()
```

Search and filters can be combined:

```python
results = (
    client.works
    .search("CRISPR")
    .filter(publication_year=2024, is_oa=True)
    .sort("cited_by_count", desc=True)
    .get()
)
```

## Sorting

```python
# Ascending (default)
client.works.sort("publication_date")

# Descending
client.works.sort("cited_by_count", desc=True)
```

## Field Selection

Request only the fields you need to reduce response size:

```python
results = client.works.select("id", "title", "doi", "cited_by_count").get()
```

## Pagination

### Page-Based

```python
page1 = client.works.filter(publication_year=2024).page(1).per_page(100).get()
page2 = client.works.filter(publication_year=2024).page(2).per_page(100).get()
```

### Cursor-Based (Automatic)

Iterate over any query and PyOpenAlex handles cursor pagination automatically:

```python
for work in client.works.filter(publication_year=2024, is_oa=True):
    print(work.title)
```

Use `.limit()` to cap the total number of results:

```python
for work in client.works.filter(publication_year=2024).limit(500):
    process(work)
```

## Counting

Get the total number of matching results without fetching them:

```python
count = client.works.filter(publication_year=2024, is_oa=True).count()
```

## Grouping

Aggregate results by a field:

```python
response = client.works.filter(publication_year=2024).group_by("type").get()
for group in response.group_by:
    print(f"{group.key_display_name}: {group.count}")
```

## Sampling

Get a random sample of results:

```python
results = client.works.sample(100, seed=42).get()
```

## Autocomplete

Fast typeahead search returning up to 10 results:

```python
results = client.institutions.autocomplete("harvard")
for r in results:
    print(f"{r.display_name} ({r.works_count} works)")
```

## Query Reuse

The query builder is immutable. Each method returns a new instance, so you can safely branch from a base query:

```python
base = client.works.filter(publication_year=2024, is_oa=True)

most_cited = base.sort("cited_by_count", desc=True).per_page(10).get()
recent = base.sort("publication_date", desc=True).per_page(10).get()
count = base.count()
```

## Response Objects

List queries return a `ListResponse` with three parts:

```python
response = client.works.search("CRISPR").get()

response.meta        # Meta: count, page, per_page, cost_usd, ...
response.results     # list[Work]: the entities
response.group_by    # list[GroupByResult]: populated when using group_by
```

## Configuration

### API Key

Set your API key in any of these ways (in order of precedence):

```python
# 1. Constructor argument
client = OpenAlex(api_key="your-key")

# 2. Environment variable
# export OPENALEX_API_KEY=your-key
client = OpenAlex()
```

Get a free API key at [openalex.org/settings/api](https://openalex.org/settings/api).

### Other Settings

```python
client = OpenAlex(
    api_key="your-key",
    base_url="https://api.openalex.org",  # default
    timeout=30.0,                          # request timeout in seconds
    max_retries=3,                         # retries on 429/5xx errors
)
```

All settings can be set via environment variables with the `OPENALEX_` prefix:

```bash
export OPENALEX_API_KEY=your-key
export OPENALEX_TIMEOUT=60
export OPENALEX_MAX_RETRIES=5
```

### Context Manager

The client can be used as a context manager to ensure the HTTP connection is closed:

```python
with OpenAlex() as client:
    work = client.works.get("W2741809807")
```

## Error Handling

PyOpenAlex raises typed exceptions:

```python
from pyopenalex.exceptions import NotFoundError, RateLimitError, APIError

try:
    work = client.works.get("W0000000000")
except NotFoundError:
    print("Work not found")
except RateLimitError:
    print("Daily rate limit exceeded")
except APIError as e:
    print(f"HTTP {e.status_code}: {e}")
```

Retries with exponential backoff are automatic for 429 (rate limit) and 5xx (server error) responses.

## Abstract Reconstruction

OpenAlex stores abstracts as inverted indexes. PyOpenAlex reconstructs them for you:

```python
work = client.works.get("W2741809807")
print(work.abstract)  # full abstract text, or None if unavailable
```

## License

MIT
