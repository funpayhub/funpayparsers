import pytest
from funpayparsers.parsers import (CategoriesParser, CategoriesParserOptions)


class TestCategoriesParsing:
    OPTIONS = CategoriesParserOptions(empty_raw_source=True)

    @pytest.mark.parametrize('html,expected',
                             [
                                 ('single_category_html', 'single_category_obj'),
                                 ('multiple_categories_html', 'multiple_categories_obj')
                             ])
    def test_categories_parser(self, html, expected, request):
        html = request.getfixturevalue(html)
        expected = request.getfixturevalue(expected)
        parser = CategoriesParser(html, options=self.OPTIONS)
        assert parser.parse() == expected
