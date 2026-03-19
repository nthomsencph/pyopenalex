# OpenAlex API Coverage

Gap analysis between the [OpenAlex API](https://developers.openalex.org) and pyopenalex.

## Covered

### Entity Endpoints

| Endpoint | Client attribute | Model |
|---|---|---|
| `/works` | `client.works` | `Work` |
| `/authors` | `client.authors` | `Author` |
| `/sources` | `client.sources` | `Source` |
| `/institutions` | `client.institutions` | `Institution` |
| `/topics` | `client.topics` | `Topic` |
| `/keywords` | `client.keywords` | `Keyword` |
| `/publishers` | `client.publishers` | `Publisher` |
| `/funders` | `client.funders` | `Funder` |
| `/domains` | `client.domains` | `Domain` |
| `/fields` | `client.fields` | `Field` |
| `/subfields` | `client.subfields` | `Subfield` |
| `/sdgs` | `client.sdgs` | `Sdg` |
| `/countries` | `client.countries` | `Country` |
| `/continents` | `client.continents` | `Continent` |
| `/languages` | `client.languages` | `Language` |
| `/work-types` | `client.work_types` | `WorkType` |
| `/source-types` | `client.source_types` | `SourceType` |
| `/institution-types` | `client.institution_types` | `InstitutionType` |
| `/licenses` | `client.licenses` | `License` |
| `/awards` | `client.awards` | `Award` |
| `/autocomplete/{entity}` | `endpoint.autocomplete()` | `AutocompleteResult` |

### Special Endpoints

| Feature | Client method | Model |
|---|---|---|
| Rate limit status | `client.rate_limit()` | `RateLimit` |
| List changefile dates | `client.changefiles()` | `list[ChangefileDate]` |
| Changefile detail | `client.changefile(date)` | `list[ChangefileEntry]` |
| PDF download | `client.download_pdf(id, dest)` | writes to file |

## Deprecated (do NOT implement)

| Endpoint | Replacement |
|---|---|
| `/concepts` | Use `/topics` |
| `/text/topics` | Deprecated text classification |
