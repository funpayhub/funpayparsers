import pytest
from funpayparsers.parsers import FunPayObjectParserOptions


@pytest.fixture
def options1() -> FunPayObjectParserOptions:
    return FunPayObjectParserOptions(empty_raw_source=True)

@pytest.fixture
def options2() -> FunPayObjectParserOptions:
    return FunPayObjectParserOptions(context={'key': 'value'})


class TestOptionsMerge:
    def test_and_options_merge(self, options1, options2):
        expected = FunPayObjectParserOptions(empty_raw_source=True,
                                             context={'key': 'value'})
        assert options1 & options2 == expected


    def test_or_options_merge(self, options1, options2):
        expected = FunPayObjectParserOptions(context={'key': 'value'})
        assert options1 | options2 == expected
