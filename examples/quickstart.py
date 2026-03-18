"""Example usage of pyopenalex."""

from pyopenalex import OpenAlex, between, gt

client = OpenAlex()

# Search for papers
print("=== Search ===")
for work in client.works.search("large language model agents").get(3).results:
    print(work.to_markdown(limit_abstract=150))

# Find papers by author (two-step ID resolution handled automatically)
print("=== By Author ===")
for work in client.works.by_author("Yann LeCun").sort("cited_by_count", desc=True).get(3).results:
    print(f"{work.title} ({work.year}) - {work.citations:,} citations")

# Find papers from an institution
print("\n=== By Institution ===")
for work in client.works.by_institution("MIT").filter(publication_year=2024).get(3).results:
    print(f"{work.title} ({work.year})")

# Find papers in a journal
print("\n=== By Source ===")
count = client.works.by_source("Nature").filter(publication_year=2024).count()
print(f"Papers in Nature in 2024: {count:,}")

# Filter expressions
print("\n=== Highly Cited Open Access ===")
for work in (
    client.works.filter(cited_by_count=gt(1000), publication_year=between(2020, 2024), is_oa=True)
    .sort("cited_by_count", desc=True)
    .get(3)
    .results
):
    print(f"[{work.citations:,}] {work.title}")

# Publication trends
print("\n=== Trends ===")
response = (
    client.works.search("transformer architecture")
    .filter(publication_year=between(2017, 2026))
    .group_by("publication_year")
    .get()
)
for g in sorted(response.group_by, key=lambda g: g.key):
    print(f"  {g.key}: {g.count:,} papers")

# Autocomplete
print("\n=== Autocomplete ===")
for r in client.institutions.autocomplete("stanf")[:3]:
    print(f"  {r.display_name}")

# Random work
print("\n=== Random ===")
work = client.works.random()
print(f"{work.title} ({work.year})")

client.close()
