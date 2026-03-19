from pyopenalex.models.authors import Author
from pyopenalex.models.awards import Award
from pyopenalex.models.base import CountsByYear, Meta, SummaryStats
from pyopenalex.models.continents import Continent
from pyopenalex.models.countries import Country
from pyopenalex.models.domains import Domain
from pyopenalex.models.fields import Field
from pyopenalex.models.funders import Funder
from pyopenalex.models.institution_types import InstitutionType
from pyopenalex.models.institutions import Institution
from pyopenalex.models.keywords import Keyword
from pyopenalex.models.languages import Language
from pyopenalex.models.licenses import License
from pyopenalex.models.publishers import Publisher
from pyopenalex.models.sdgs import Sdg
from pyopenalex.models.source_types import SourceType
from pyopenalex.models.sources import Source
from pyopenalex.models.subfields import Subfield
from pyopenalex.models.topics import Topic
from pyopenalex.models.work_types import WorkType
from pyopenalex.models.works import Work
from tests.conftest import load_fixture


class TestWorkModel:
    def test_parse_fixture(self):
        work = Work(**load_fixture("work"))
        assert work.id.startswith("https://openalex.org/")
        assert work.title is not None
        assert work.doi is not None
        assert work.publication_year is not None
        assert isinstance(work.cited_by_count, int)

    def test_authorships_parsed(self):
        work = Work(**load_fixture("work"))
        assert len(work.authorships) > 0
        first = work.authorships[0]
        assert first.author.display_name is not None
        assert first.author_position in ("first", "middle", "last")

    def test_locations_parsed(self):
        work = Work(**load_fixture("work"))
        assert work.primary_location is not None

    def test_open_access_parsed(self):
        work = Work(**load_fixture("work"))
        assert work.open_access is not None
        assert isinstance(work.open_access.is_oa, bool)

    def test_abstract_inversion(self):
        work = Work(**load_fixture("work"))
        if work.abstract_inverted_index:
            abstract = work.abstract
            assert isinstance(abstract, str)
            assert len(abstract) > 0

    def test_abstract_none_when_no_index(self):
        work = Work(id="test", abstract_inverted_index=None)
        assert work.abstract is None

    def test_counts_by_year(self):
        work = Work(**load_fixture("work"))
        assert len(work.counts_by_year) > 0
        assert work.counts_by_year[0].year > 2000

    def test_extra_fields_allowed(self):
        """Models should accept unknown fields without error."""
        data = load_fixture("work")
        data["some_new_api_field"] = "value"
        work = Work(**data)
        assert work.id is not None


class TestAuthorModel:
    def test_parse_fixture(self):
        author = Author(**load_fixture("author"))
        assert author.display_name is not None
        assert isinstance(author.works_count, int)
        assert isinstance(author.cited_by_count, int)

    def test_summary_stats(self):
        author = Author(**load_fixture("author"))
        assert author.summary_stats is not None
        assert author.summary_stats.h_index is not None


class TestSourceModel:
    def test_parse_fixture(self):
        source = Source(**load_fixture("source"))
        assert source.display_name is not None
        assert source.type is not None


class TestInstitutionModel:
    def test_parse_fixture(self):
        inst = Institution(**load_fixture("institution"))
        assert inst.display_name is not None
        assert inst.country_code is not None
        assert inst.geo is not None


class TestTopicModel:
    def test_parse_fixture(self):
        topic = Topic(**load_fixture("topic"))
        assert topic.display_name is not None
        assert topic.domain is not None
        assert topic.field is not None
        assert topic.subfield is not None


class TestKeywordModel:
    def test_parse_fixture(self):
        kw = Keyword(**load_fixture("keyword"))
        assert kw.display_name is not None
        assert isinstance(kw.works_count, int)


class TestPublisherModel:
    def test_parse_fixture(self):
        pub = Publisher(**load_fixture("publisher"))
        assert pub.display_name is not None
        assert isinstance(pub.works_count, int)


class TestFunderModel:
    def test_parse_fixture(self):
        funder = Funder(**load_fixture("funder"))
        assert funder.display_name is not None
        assert isinstance(funder.works_count, int)


class TestDomainModel:
    def test_parse_fixture(self):
        domain = Domain(**load_fixture("domain"))
        assert domain.display_name == "Life Sciences"
        assert len(domain.fields) == 2
        assert domain.fields[0].display_name == "Agricultural and Biological Sciences"
        assert isinstance(domain.works_count, int)

    def test_aliases(self):
        domain = Domain(**load_fixture("domain"))
        assert domain.name == domain.display_name
        assert domain.citations == domain.cited_by_count


class TestFieldModel:
    def test_parse_fixture(self):
        field = Field(**load_fixture("field"))
        assert field.display_name == "Computer Science"
        assert field.domain is not None
        assert field.domain.display_name == "Physical Sciences"
        assert len(field.subfields) == 2

    def test_aliases(self):
        field = Field(**load_fixture("field"))
        assert field.name == field.display_name
        assert field.citations == field.cited_by_count


class TestSubfieldModel:
    def test_parse_fixture(self):
        subfield = Subfield(**load_fixture("subfield"))
        assert subfield.display_name == "Ecology, Evolution, Behavior and Systematics"
        assert subfield.field is not None
        assert subfield.domain is not None
        assert len(subfield.topics) == 2

    def test_aliases(self):
        subfield = Subfield(**load_fixture("subfield"))
        assert subfield.name == subfield.display_name
        assert subfield.citations == subfield.cited_by_count


class TestSdgModel:
    def test_parse_fixture(self):
        sdg = Sdg(**load_fixture("sdg"))
        assert sdg.display_name == "Good health and well-being"
        assert sdg.image_url is not None
        assert isinstance(sdg.works_count, int)

    def test_aliases(self):
        sdg = Sdg(**load_fixture("sdg"))
        assert sdg.name == sdg.display_name
        assert sdg.citations == sdg.cited_by_count


class TestCountryModel:
    def test_parse_fixture(self):
        country = Country(**load_fixture("country"))
        assert country.display_name == "United States of America"
        assert country.country_code == "US"
        assert country.continent is not None
        assert country.continent.display_name == "North America"
        assert country.is_global_south is False

    def test_aliases(self):
        country = Country(**load_fixture("country"))
        assert country.name == country.display_name
        assert country.citations == country.cited_by_count


class TestContinentModel:
    def test_parse_fixture(self):
        continent = Continent(**load_fixture("continent"))
        assert continent.display_name == "Europe"
        assert len(continent.countries) == 3

    def test_alias(self):
        continent = Continent(**load_fixture("continent"))
        assert continent.name == continent.display_name


class TestLanguageModel:
    def test_parse_fixture(self):
        lang = Language(**load_fixture("language"))
        assert lang.display_name == "English"
        assert isinstance(lang.works_count, int)

    def test_aliases(self):
        lang = Language(**load_fixture("language"))
        assert lang.name == lang.display_name
        assert lang.citations == lang.cited_by_count


class TestWorkTypeModel:
    def test_parse_fixture(self):
        wt = WorkType(**load_fixture("work_type"))
        assert wt.display_name == "article"
        assert wt.description is not None
        assert isinstance(wt.works_count, int)

    def test_aliases(self):
        wt = WorkType(**load_fixture("work_type"))
        assert wt.name == wt.display_name
        assert wt.citations == wt.cited_by_count


class TestSourceTypeModel:
    def test_parse_fixture(self):
        st = SourceType(**load_fixture("source_type"))
        assert st.display_name == "journal"
        assert isinstance(st.works_count, int)

    def test_aliases(self):
        st = SourceType(**load_fixture("source_type"))
        assert st.name == st.display_name
        assert st.citations == st.cited_by_count


class TestInstitutionTypeModel:
    def test_parse_fixture(self):
        it = InstitutionType(**load_fixture("institution_type"))
        assert it.display_name == "education"
        assert isinstance(it.works_count, int)

    def test_aliases(self):
        it = InstitutionType(**load_fixture("institution_type"))
        assert it.name == it.display_name
        assert it.citations == it.cited_by_count


class TestLicenseModel:
    def test_parse_fixture(self):
        lic = License(**load_fixture("license"))
        assert lic.display_name == "CC-BY"
        assert lic.url is not None
        assert isinstance(lic.works_count, int)

    def test_aliases(self):
        lic = License(**load_fixture("license"))
        assert lic.name == lic.display_name
        assert lic.citations == lic.cited_by_count


class TestAwardModel:
    def test_parse_fixture(self):
        award = Award(**load_fixture("award"))
        assert award.id == "https://openalex.org/G2087396116"
        assert award.funder is not None
        assert award.funder.display_name == "National Natural Science Foundation of China"
        assert award.funded_outputs_count == 839935

    def test_display_name_nullable(self):
        award = Award(**load_fixture("award"))
        assert award.display_name is None
        assert award.name is None


# --- Shared models ---


class TestSummaryStats:
    def test_alias_2yr(self):
        stats = SummaryStats(**{"2yr_mean_citedness": 5.5, "h_index": 10, "i10_index": 5})
        assert stats.two_yr_mean_citedness == 5.5

    def test_all_optional(self):
        stats = SummaryStats()
        assert stats.h_index is None


class TestMeta:
    def test_parse(self):
        meta = Meta(count=100, db_response_time_ms=50)
        assert meta.count == 100
        assert meta.next_cursor is None


class TestCountsByYear:
    def test_works_count_optional(self):
        """Work-level counts_by_year has no works_count."""
        cby = CountsByYear(year=2024, cited_by_count=10)
        assert cby.works_count is None

    def test_with_works_count(self):
        cby = CountsByYear(year=2024, cited_by_count=10, works_count=5)
        assert cby.works_count == 5
