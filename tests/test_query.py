from pyopenalex.expressions import between, gt, lt, ne, or_
from pyopenalex.query import QueryBuilder, _flatten_filters
from tests.conftest import FakeHttpClient, load_fixture


def make_qb(fake_http: FakeHttpClient | None = None) -> QueryBuilder:
    from pyopenalex.models.works import Work

    http = fake_http or FakeHttpClient()
    return QueryBuilder(http, "/works", Work)


# --- Filter serialization ---


class TestFilterSerialization:
    def test_simple_filter(self):
        qb = make_qb().filter(publication_year=2024)
        params = qb._build_params()
        assert params["filter"] == "publication_year:2024"

    def test_bool_filter(self):
        qb = make_qb().filter(is_oa=True)
        params = qb._build_params()
        assert params["filter"] == "is_oa:true"

    def test_list_filter(self):
        qb = make_qb().filter(type=["article", "book"])
        params = qb._build_params()
        assert params["filter"] == "type:article|book"

    def test_multiple_filters_and(self):
        qb = make_qb().filter(publication_year=2024, is_oa=True)
        params = qb._build_params()
        assert "publication_year:2024" in params["filter"]
        assert "is_oa:true" in params["filter"]
        assert "," in params["filter"]

    def test_gt_expression(self):
        qb = make_qb().filter(cited_by_count=gt(100))
        params = qb._build_params()
        assert params["filter"] == "cited_by_count:>100"

    def test_lt_expression(self):
        qb = make_qb().filter(publication_year=lt(2020))
        params = qb._build_params()
        assert params["filter"] == "publication_year:<2020"

    def test_ne_expression(self):
        qb = make_qb().filter(type=ne("paratext"))
        params = qb._build_params()
        assert params["filter"] == "type:!paratext"

    def test_or_expression(self):
        qb = make_qb().filter(doi=or_("10.1/a", "10.1/b"))
        params = qb._build_params()
        assert params["filter"] == "doi:10.1/a|10.1/b"

    def test_between_expression(self):
        qb = make_qb().filter(publication_year=between(2020, 2024))
        params = qb._build_params()
        assert params["filter"] == "publication_year:2020-2024"

    def test_filter_raw(self):
        qb = make_qb().filter_raw("publication_year:2024,is_oa:true")
        params = qb._build_params()
        assert params["filter"] == "publication_year:2024,is_oa:true"


# --- Nested dict flattening ---


class TestNestedDictFilters:
    def test_flatten_one_level(self):
        pairs = _flatten_filters("authorships", {"author": {"id": "A123"}})
        assert pairs == [("authorships.author.id", "A123")]

    def test_flatten_two_levels(self):
        pairs = _flatten_filters("authorships", {"institutions": {"country_code": "US"}})
        assert pairs == [("authorships.institutions.country_code", "US")]

    def test_nested_filter_in_query(self):
        qb = make_qb().filter(authorships={"institutions": {"id": "I136199984"}})
        params = qb._build_params()
        assert params["filter"] == "authorships.institutions.id:I136199984"


# --- Clone immutability ---


class TestCloneImmutability:
    def test_filter_does_not_mutate_original(self):
        base = make_qb().filter(publication_year=2024)
        derived = base.filter(is_oa=True)

        base_params = base._build_params()
        derived_params = derived._build_params()

        assert "is_oa" not in base_params.get("filter", "")
        assert "is_oa:true" in derived_params["filter"]

    def test_sort_does_not_mutate_original(self):
        base = make_qb().filter(publication_year=2024)
        derived = base.sort("cited_by_count", desc=True)

        assert "sort" not in base._build_params()
        assert derived._build_params()["sort"] == "cited_by_count:desc"

    def test_limit_does_not_mutate_original(self):
        base = make_qb()
        derived = base.limit(100)

        assert base._limit is None
        assert derived._limit == 100


# --- Parameter building ---


class TestParamBuilding:
    def test_sort_asc(self):
        qb = make_qb().sort("cited_by_count")
        assert qb._build_params()["sort"] == "cited_by_count"

    def test_sort_desc(self):
        qb = make_qb().sort("cited_by_count", desc=True)
        assert qb._build_params()["sort"] == "cited_by_count:desc"

    def test_per_page(self):
        qb = make_qb().per_page(50)
        assert qb._build_params()["per_page"] == 50

    def test_page(self):
        qb = make_qb().page(3)
        assert qb._build_params()["page"] == 3

    def test_select(self):
        qb = make_qb().select("id", "title", "doi")
        assert qb._build_params()["select"] == "id,title,doi"

    def test_sample_with_seed(self):
        qb = make_qb().sample(50, seed=42)
        params = qb._build_params()
        assert params["sample"] == 50
        assert params["seed"] == 42

    def test_group_by(self):
        qb = make_qb().group_by("type")
        assert qb._build_params()["group_by"] == "type"

    def test_search(self):
        qb = make_qb().search("machine learning")
        assert qb._build_params()["search"] == "machine learning"

    def test_search_filter(self):
        qb = make_qb().search_filter(title="neural networks")
        assert qb._build_params()["filter"] == "title.search:neural networks"

    def test_chaining_combines_params(self):
        qb = (
            make_qb()
            .filter(publication_year=2024)
            .sort("cited_by_count", desc=True)
            .per_page(50)
            .select("id", "title")
        )
        params = qb._build_params()
        assert params["filter"] == "publication_year:2024"
        assert params["sort"] == "cited_by_count:desc"
        assert params["per_page"] == 50
        assert params["select"] == "id,title"


# --- Get and count ---


class TestGetAndCount:
    def test_get_parses_response(self, fake_http):
        fake_http.enqueue(load_fixture("works_list"))
        from pyopenalex.models.works import Work

        qb = QueryBuilder(fake_http, "/works", Work)
        result = qb.filter(publication_year=2024).get()

        assert result.meta.count > 0
        assert len(result.results) == 2
        assert result.results[0].id is not None

    def test_count_uses_per_page_1(self, fake_http):
        fake_http.enqueue(load_fixture("works_list"))
        from pyopenalex.models.works import Work

        qb = QueryBuilder(fake_http, "/works", Work)
        count = qb.filter(publication_year=2024).count()

        assert count > 0
        # Verify it sent per_page=1 and select=id
        params = fake_http.last_params
        assert params.get("per_page") == 1
        assert params.get("select") == "id"


# --- Cursor iterator ---


class TestCursorIterator:
    def test_iterates_through_pages(self, fake_http):
        from pyopenalex.models.works import Work

        page1 = load_fixture("works_list")
        page1["meta"]["next_cursor"] = "abc123"

        page2 = load_fixture("works_list")
        page2["meta"]["next_cursor"] = None

        fake_http.enqueue(page1, page2)
        qb = QueryBuilder(fake_http, "/works", Work)
        items = list(qb.filter(publication_year=2024))

        assert len(items) == 4  # 2 per page × 2 pages
        assert len(fake_http._requests) == 2

    def test_limit_stops_early(self, fake_http):
        from pyopenalex.models.works import Work

        page = load_fixture("works_list")
        page["meta"]["next_cursor"] = "abc123"
        fake_http.enqueue(page)

        qb = QueryBuilder(fake_http, "/works", Work)
        items = list(qb.limit(1))

        assert len(items) == 1
        assert len(fake_http._requests) == 1  # only one page fetched

    def test_cursor_passed_in_params(self, fake_http):
        from pyopenalex.models.works import Work

        page = load_fixture("works_list")
        page["meta"]["next_cursor"] = None
        fake_http.enqueue(page)

        qb = QueryBuilder(fake_http, "/works", Work)
        list(qb)

        assert fake_http.last_params["cursor"] == "*"
        assert "page" not in fake_http.last_params
