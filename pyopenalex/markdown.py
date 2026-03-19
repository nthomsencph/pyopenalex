"""Markdown rendering for OpenAlex entities.

Each entity type has a dedicated renderer that produces clean, LLM-friendly
markdown. Called via `entity.to_markdown()` on any model instance.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pyopenalex.models.base import OpenAlexModel


def _line(label: str, value: object) -> str:
    if value is None:
        return ""
    return f"- **{label}:** {value}\n"


def _count(n: int | None) -> str | None:
    if n is None:
        return None
    return f"{n:,}"


def to_markdown(entity: OpenAlexModel, limit_abstract: int | None = None) -> str:
    """Dispatch to the appropriate renderer based on entity class name."""
    renderer = _RENDERERS.get(type(entity).__name__, _default)
    return renderer(entity, limit_abstract=limit_abstract)


def _default(entity: Any, **kwargs: Any) -> str:
    name = getattr(entity, "display_name", None) or getattr(entity, "id", "")
    lines = [f"## {name}\n\n"]
    for field_name, value in entity:
        if value is not None and field_name != "display_name":
            lines.append(f"- **{field_name}:** {value}\n")
    return "".join(lines)


def _work(entity: Any, limit_abstract: int | None = None, **kwargs: Any) -> str:
    year = f" ({entity.publication_year})" if entity.publication_year else ""
    parts = [f"## {entity.title or 'Untitled'}{year}\n\n"]

    meta = ""
    meta += _line("DOI", entity.doi)
    meta += _line("Type", entity.type)
    meta += _line("Citations", _count(entity.cited_by_count))
    meta += _line("Language", entity.language)

    if entity.open_access:
        oa = "Yes" if entity.open_access.is_oa else "No"
        if entity.open_access.oa_status:
            oa += f" ({entity.open_access.oa_status})"
        meta += _line("Open Access", oa)

    if entity.is_retracted:
        meta += _line("Retracted", "Yes")

    if entity.primary_location and entity.primary_location.source:
        meta += _line("Source", entity.primary_location.source.display_name)

    if entity.authorships:
        names = [a.author.display_name or "Unknown" for a in entity.authorships]
        if len(names) > 5:
            author_str = ", ".join(names[:5]) + f", ... (+{len(names) - 5} more)"
        else:
            author_str = ", ".join(names)
        meta += _line("Authors", author_str)

    if entity.primary_topic:
        meta += _line("Topic", entity.primary_topic.display_name)

    if entity.keywords:
        meta += _line("Keywords", ", ".join(k.display_name for k in entity.keywords[:5]))

    if entity.fwci is not None:
        meta += _line("FWCI", f"{entity.fwci:.2f}")

    parts.append(meta)

    abstract = entity.abstract
    if abstract:
        if limit_abstract is not None and len(abstract) > limit_abstract:
            abstract = abstract[:limit_abstract] + "..."
        parts.append(f"\n{abstract}\n")

    return "".join(parts)


def _author(entity: Any, **kwargs: Any) -> str:
    parts = [f"## {entity.display_name}\n\n"]

    meta = ""
    meta += _line("ORCID", entity.orcid)
    meta += _line("Works", _count(entity.works_count))
    meta += _line("Citations", _count(entity.cited_by_count))

    if entity.summary_stats:
        meta += _line("h-index", entity.summary_stats.h_index)
        meta += _line("i10-index", entity.summary_stats.i10_index)

    if entity.last_known_institutions:
        names = [i.display_name for i in entity.last_known_institutions]
        meta += _line("Institutions", ", ".join(names))

    if entity.topics:
        top = [t.get("display_name", "") for t in entity.topics[:5] if t.get("display_name")]
        if top:
            meta += _line("Topics", ", ".join(top))

    parts.append(meta)
    return "".join(parts)


def _institution(entity: Any, **kwargs: Any) -> str:
    parts = [f"## {entity.display_name}\n\n"]

    meta = ""
    meta += _line("ROR", entity.ror)
    meta += _line("Country", entity.country_code)
    meta += _line("Type", entity.type)
    meta += _line("Homepage", entity.homepage_url)
    meta += _line("Works", _count(entity.works_count))
    meta += _line("Citations", _count(entity.cited_by_count))

    if entity.summary_stats:
        meta += _line("h-index", entity.summary_stats.h_index)

    if entity.geo:
        location_parts = [p for p in [entity.geo.city, entity.geo.region, entity.geo.country] if p]
        if location_parts:
            meta += _line("Location", ", ".join(location_parts))

    parts.append(meta)
    return "".join(parts)


def _source(entity: Any, **kwargs: Any) -> str:
    parts = [f"## {entity.display_name}\n\n"]

    meta = ""
    meta += _line("Type", entity.type)
    meta += _line("ISSN-L", entity.issn_l)
    meta += _line("Publisher", entity.host_organization_name)
    meta += _line("Homepage", entity.homepage_url)
    meta += _line("Works", _count(entity.works_count))
    meta += _line("Citations", _count(entity.cited_by_count))

    if entity.is_oa is not None:
        meta += _line("Open Access", "Yes" if entity.is_oa else "No")
    if entity.is_in_doaj:
        meta += _line("In DOAJ", "Yes")
    if entity.apc_usd is not None:
        meta += _line("APC (USD)", f"${entity.apc_usd:,}")

    parts.append(meta)
    return "".join(parts)


def _topic(entity: Any, limit_abstract: int | None = None, **kwargs: Any) -> str:
    parts = [f"## {entity.display_name}\n\n"]

    meta = ""
    if entity.domain:
        meta += _line("Domain", entity.domain.display_name)
    if entity.field:
        meta += _line("Field", entity.field.display_name)
    if entity.subfield:
        meta += _line("Subfield", entity.subfield.display_name)
    meta += _line("Works", _count(entity.works_count))
    meta += _line("Citations", _count(entity.cited_by_count))

    if entity.keywords:
        meta += _line("Keywords", ", ".join(entity.keywords[:10]))

    parts.append(meta)

    if entity.description:
        desc = entity.description
        if limit_abstract is not None and len(desc) > limit_abstract:
            desc = desc[:limit_abstract] + "..."
        parts.append(f"\n{desc}\n")

    return "".join(parts)


def _publisher(entity: Any, **kwargs: Any) -> str:
    parts = [f"## {entity.display_name}\n\n"]

    meta = ""
    meta += _line("Homepage", entity.homepage_url)
    if entity.country_codes:
        meta += _line("Countries", ", ".join(entity.country_codes))
    meta += _line("Works", _count(entity.works_count))
    meta += _line("Citations", _count(entity.cited_by_count))
    meta += _line("Hierarchy Level", entity.hierarchy_level)

    parts.append(meta)
    return "".join(parts)


def _funder(entity: Any, limit_abstract: int | None = None, **kwargs: Any) -> str:
    parts = [f"## {entity.display_name}\n\n"]

    meta = ""
    meta += _line("Country", entity.country_code)
    meta += _line("Homepage", entity.homepage_url)
    meta += _line("Works", _count(entity.works_count))
    meta += _line("Citations", _count(entity.cited_by_count))
    meta += _line("Awards", _count(entity.awards_count))

    parts.append(meta)

    if entity.description:
        desc = entity.description
        if limit_abstract is not None and len(desc) > limit_abstract:
            desc = desc[:limit_abstract] + "..."
        parts.append(f"\n{desc}\n")

    return "".join(parts)


def _keyword(entity: Any, **kwargs: Any) -> str:
    parts = [f"## {entity.display_name}\n\n"]

    meta = ""
    meta += _line("Works", _count(entity.works_count))
    meta += _line("Citations", _count(entity.cited_by_count))

    parts.append(meta)
    return "".join(parts)


def _domain(entity: Any, limit_abstract: int | None = None, **kwargs: Any) -> str:
    parts = [f"## {entity.display_name}\n\n"]

    meta = ""
    meta += _line("Works", _count(entity.works_count))
    meta += _line("Citations", _count(entity.cited_by_count))

    if entity.fields:
        names = [f.display_name for f in entity.fields]
        meta += _line("Fields", ", ".join(names))

    parts.append(meta)

    if entity.description:
        desc = entity.description
        if limit_abstract is not None and len(desc) > limit_abstract:
            desc = desc[:limit_abstract] + "..."
        parts.append(f"\n{desc}\n")

    return "".join(parts)


def _field(entity: Any, limit_abstract: int | None = None, **kwargs: Any) -> str:
    parts = [f"## {entity.display_name}\n\n"]

    meta = ""
    if entity.domain:
        meta += _line("Domain", entity.domain.display_name)
    meta += _line("Works", _count(entity.works_count))
    meta += _line("Citations", _count(entity.cited_by_count))

    if entity.subfields:
        names = [s.display_name for s in entity.subfields[:10]]
        suffix = f" (+{len(entity.subfields) - 10} more)" if len(entity.subfields) > 10 else ""
        meta += _line("Subfields", ", ".join(names) + suffix)

    parts.append(meta)

    if entity.description:
        desc = entity.description
        if limit_abstract is not None and len(desc) > limit_abstract:
            desc = desc[:limit_abstract] + "..."
        parts.append(f"\n{desc}\n")

    return "".join(parts)


def _subfield(entity: Any, limit_abstract: int | None = None, **kwargs: Any) -> str:
    parts = [f"## {entity.display_name}\n\n"]

    meta = ""
    if entity.domain:
        meta += _line("Domain", entity.domain.display_name)
    if entity.field:
        meta += _line("Field", entity.field.display_name)
    meta += _line("Works", _count(entity.works_count))
    meta += _line("Citations", _count(entity.cited_by_count))

    parts.append(meta)

    if entity.description:
        desc = entity.description
        if limit_abstract is not None and len(desc) > limit_abstract:
            desc = desc[:limit_abstract] + "..."
        parts.append(f"\n{desc}\n")

    return "".join(parts)


def _sdg(entity: Any, limit_abstract: int | None = None, **kwargs: Any) -> str:
    parts = [f"## {entity.display_name}\n\n"]

    meta = ""
    meta += _line("Works", _count(entity.works_count))
    meta += _line("Citations", _count(entity.cited_by_count))

    parts.append(meta)

    if entity.description:
        desc = entity.description
        if limit_abstract is not None and len(desc) > limit_abstract:
            desc = desc[:limit_abstract] + "..."
        parts.append(f"\n{desc}\n")

    return "".join(parts)


def _country(entity: Any, **kwargs: Any) -> str:
    parts = [f"## {entity.display_name}\n\n"]

    meta = ""
    meta += _line("Country Code", entity.country_code)
    if entity.continent:
        meta += _line("Continent", entity.continent.display_name)
    if entity.is_global_south is not None:
        meta += _line("Global South", "Yes" if entity.is_global_south else "No")
    meta += _line("Works", _count(entity.works_count))
    meta += _line("Citations", _count(entity.cited_by_count))

    parts.append(meta)
    return "".join(parts)


def _continent(entity: Any, **kwargs: Any) -> str:
    parts = [f"## {entity.display_name}\n\n"]

    meta = ""
    if entity.countries:
        meta += _line("Countries", f"{len(entity.countries)} countries")

    parts.append(meta)
    return "".join(parts)


def _award(entity: Any, **kwargs: Any) -> str:
    name = entity.display_name or entity.funder_award_id or entity.id
    parts = [f"## {name}\n\n"]

    meta = ""
    if entity.funder:
        meta += _line("Funder", entity.funder.display_name)
    meta += _line("Award ID", entity.funder_award_id)
    meta += _line("Funded Outputs", _count(entity.funded_outputs_count))

    parts.append(meta)
    return "".join(parts)


_RENDERERS = {
    "Work": _work,
    "Author": _author,
    "Institution": _institution,
    "Source": _source,
    "Topic": _topic,
    "Publisher": _publisher,
    "Funder": _funder,
    "Keyword": _keyword,
    "Domain": _domain,
    "Field": _field,
    "Subfield": _subfield,
    "Sdg": _sdg,
    "Country": _country,
    "Continent": _continent,
    "Award": _award,
}
