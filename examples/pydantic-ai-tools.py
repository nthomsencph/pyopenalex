"""Using pyopenalex as pydantic-ai tools for a research assistant agent."""

from pydantic_ai import Agent

from pyopenalex import OpenAlex, between

client = OpenAlex()

research_agent = Agent(
    "openai:gpt-5-nano",
    instructions=(
        "You are an academic research assistant. Use your tools to find "
        "and analyze scholarly literature. Cite papers by author and year."
    ),
)


@research_agent.tool_plain
def search_papers(query: str, max_results: int = 5) -> str:
    """Search for academic papers on a topic.

    Args:
        query: Search query describing the research topic.
        max_results: Number of papers to return (default 5, max 10).
    """
    if results := (
        client.works.search(query).sort("cited_by_count", desc=True).get(max_results).results
    ):
        return "\n\n".join(work.to_markdown(limit_abstract=300) for work in results)
    return "No papers found for this query."


@research_agent.tool_plain
def search_by_author(author_name: str, max_results: int = 5) -> str:
    """Search for papers by a specific author.

    Args:
        author_name: Name of the author to search for.
        max_results: Number of papers to return (default 5, max 10).
    """
    if results := (
        client.works.by_author(author_name)
        .sort("cited_by_count", desc=True)
        .get(max_results)
        .results
    ):
        return "\n\n".join(work.to_markdown(limit_abstract=0) for work in results)
    return f"No papers found for author '{author_name}'."


@research_agent.tool_plain
def get_citation_trends(query: str) -> str:
    """Get publication trends for a topic per year.

    Args:
        query: The research topic to analyze.
    """
    if response := (
        client.works.search(query)
        .filter(publication_year=between(2015, 2026))
        .group_by("publication_year")
        .get()
    ):
        groups = sorted(response.group_by, key=lambda g: g.key)
        lines = [f"Publication trends for '{query}':"]
        lines.extend(f"  {g.key}: {g.count} papers" for g in groups)
        return "\n".join(lines)

    return "No trend data available for this query."


@research_agent.tool_plain
def find_related_topics(openalex_id: str) -> str:
    """Fetch related topics for a paper given its OpenAlex ID.

    Args:
        openalex_id: OpenAlex ID like 'W2741809807'.
    """
    work = client.works.get(openalex_id)
    if not work.topics:
        return f"No topics found for: {work.title}"

    lines = [f"Topics for '{work.title}':"]
    for t in work.topics:
        lines.append(f"  - {t.display_name} (score: {t.score})")
    return "\n".join(lines)


if __name__ == "__main__":
    result = research_agent.run_sync(
        "Find the most cited papers on transformer architecture "
        "and explore what topics are connected to the top result."
    )
    print(result.output)
