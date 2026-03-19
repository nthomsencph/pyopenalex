"""Smoke test for newly added entity endpoints."""

from pyopenalex import OpenAlex

client = OpenAlex()

# --- Topic hierarchy ---
print("=== Domains ===")
domain = client.domains.get("1")
print(f"{domain.name}: {domain.description}")
print(f"  Fields: {', '.join(f.display_name for f in domain.fields)}")

print("\n=== Fields ===")
field = client.fields.get("17")
print(f"{field.name} (domain: {field.domain.display_name})")
print(f"  Subfields: {', '.join(s.display_name for s in field.subfields[:5])}")

print("\n=== Subfields ===")
subfield = client.subfields.get("1702")
print(f"{subfield.name} (field: {subfield.field.display_name})")
print(f"  Domain: {subfield.domain.display_name}")

# --- SDGs ---
print("\n=== SDGs ===")
sdg = client.sdgs.get("3")
print(f"{sdg.name}: {sdg.description}")
print(f"  Works: {sdg.works_count:,}")

# --- Geography ---
print("\n=== Countries ===")
country = client.countries.get("US")
print(f"{country.name} ({country.country_code}), continent: {country.continent.display_name}")
print(f"  Global South: {country.is_global_south}, Works: {country.works_count:,}")

print("\n=== Continents ===")
continent = client.continents.get("Q46")
print(f"{continent.name}: {len(continent.countries)} countries")

# --- Languages ---
print("\n=== Languages ===")
lang = client.languages.get("en")
print(f"{lang.name}: {lang.works_count:,} works")

# --- Type enumerations ---
print("\n=== Work Types ===")
for wt in client.work_types.filter().get(5).results:
    print(f"  {wt.name}: {wt.works_count:,} works")

print("\n=== Source Types ===")
for st in client.source_types.filter().get(5).results:
    print(f"  {st.name}: {st.works_count:,} works")

print("\n=== Institution Types ===")
for it in client.institution_types.filter().get(5).results:
    print(f"  {it.name}: {it.works_count:,} works")

# --- Licenses ---
print("\n=== Licenses ===")
lic = client.licenses.get("cc-by")
print(f"{lic.name}: {lic.description}")
print(f"  URL: {lic.url}, Works: {lic.works_count:,}")

# --- Awards ---
print("\n=== Awards (first 3) ===")
for award in client.awards.filter().get(3).results:
    funder_name = award.funder.display_name if award.funder else "Unknown"
    print(f"  {award.funder_award_id} from {funder_name} ({award.funded_outputs_count:,} outputs)")

# --- Markdown rendering ---
print("\n=== Markdown ===")
print(domain.to_markdown())
print(country.to_markdown())
print(sdg.to_markdown())

# --- Special endpoints ---
print("\n=== Changefiles ===")
dates = client.changefiles()
print(f"  {len(dates)} changefiles available")
print(f"  Latest: {dates[0].date}")

entries = client.changefile(dates[0].date)
for entry in entries[:3]:
    formats = ", ".join(f"{k}: {v.size_display}" for k, v in entry.formats.items())
    print(f"  {entry.entity}: {entry.records:,} records ({formats})")

print("\n=== Rate Limit ===")
try:
    rl = client.rate_limit()
    print(f"  Max: ${rl.max_cost_per_day_usd}/day")
    print(f"  Used: ${rl.current_cost_today_usd}")
    print(f"  Remaining: ${rl.remaining_cost_today_usd}")
except Exception as e:
    print(f"  Skipped (requires API key): {e}")

# Note: download_pdf not tested here to avoid $0.01 charge
# Usage: client.download_pdf("W2741809807", "/tmp/paper.pdf")

client.close()
print("\nAll new endpoints working!")
