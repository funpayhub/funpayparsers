import pytest
from funpayparsers.parsers import (CategoriesParser, CategoriesParserOptions)


class TestCategoriesParsing:
    OPTIONS = CategoriesParserOptions(empty_raw_source=True)

    def test_categories_parser(self, categories_data):
        html, obj = categories_data
        assert CategoriesParser(html, options=self.OPTIONS).parse() == obj
