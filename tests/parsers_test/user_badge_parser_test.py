import pytest
from funpayparsers.parsers import UserBadgeParser, UserBadgeParserOptions
from funpayparsers.types import UserBadge



class TestUserBadgeParser:
    OPTIONS = UserBadgeParserOptions(empty_raw_source=True)

    def test_badge_parser(self, user_badge_html, user_badge_obj):
        assert UserBadgeParser(user_badge_html, options=self.OPTIONS).parse() == user_badge_obj
