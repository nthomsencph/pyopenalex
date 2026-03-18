from pyopenalex.models.authors import Author
from pyopenalex.models.funders import Funder
from pyopenalex.models.institutions import Institution
from pyopenalex.models.keywords import Keyword
from pyopenalex.models.publishers import Publisher
from pyopenalex.models.sources import Source
from pyopenalex.models.topics import Topic
from pyopenalex.models.works import Work
from pyopenalex.models.base import SummaryStats, Meta, CountsByYear

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
