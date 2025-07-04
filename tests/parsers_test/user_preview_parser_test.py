from funpayparsers.parsers import UserPreviewParser, UserPreviewParserOptions
from funpayparsers.types import UserPreview
import pytest


class TestUserPreviewParsing:
    OPTIONS = UserPreviewParserOptions(empty_raw_source=True)

    @pytest.mark.parametrize('html,expected',
                             [
                                 ('online_user_preview_html', 'online_user_preview_obj'),
                                 ('offline_user_preview_html', 'offline_user_preview_obj'),
                                 ('banned_user_preview_html', 'banned_user_preview_obj'),
                             ])
    def test_user_preview_parsing(self, html, expected, request):
        html = request.getfixturevalue(html)
        expected = request.getfixturevalue(expected)
        assert UserPreviewParser(html, self.OPTIONS).parse() == expected
