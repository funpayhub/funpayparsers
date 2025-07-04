from funpayparsers.parsers import UserPreviewParser, UserPreviewParserOptions
from funpayparsers.types import UserPreview
import pytest


class TestUserPreviewParsing:
    OPTIONS = UserPreviewParserOptions(empty_raw_source=True)

    def test_user_preview_parsing(self, user_preview_data):
        html, obj = user_preview_data
        assert UserPreviewParser(html, self.OPTIONS).parse() == obj
