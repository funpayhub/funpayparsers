from __future__ import annotations

import pytest

from funpayparsers.parsers import ParsingOptions


@pytest.fixture
def options1() -> ParsingOptions:
    return ParsingOptions(empty_raw_source=True)

@pytest.fixture
def options2() -> ParsingOptions:
    return ParsingOptions(context={'key': 'value'})


class TestOptionsMerge:
    def test_and_options_merge(self, options1, options2):
        expected = ParsingOptions(empty_raw_source=True,
                                  context={'key': 'value'})
        assert options1 & options2 == expected


    def test_or_options_merge(self, options1, options2):
        expected = ParsingOptions(context={'key': 'value'})
        assert options1 | options2 == expected
