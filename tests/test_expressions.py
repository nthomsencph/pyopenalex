from pyopenalex.expressions import between, gt, lt, ne, or_


def test_gt():
    assert gt(100).to_value() == ">100"


def test_lt():
    assert lt(2020).to_value() == "<2020"


def test_ne_string():
    assert ne("paratext").to_value() == "!paratext"


def test_ne_bool():
    assert ne(True).to_value() == "!true"


def test_or():
    assert or_("a", "b", "c").to_value() == "a|b|c"


def test_or_ints():
    assert or_(2020, 2021, 2022).to_value() == "2020|2021|2022"


def test_between():
    assert between(2020, 2024).to_value() == "2020-2024"


def test_expressions_are_frozen():
    expr = gt(100)
    assert hash(expr)  # frozen dataclasses are hashable
