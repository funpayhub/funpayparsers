from funpayparsers.parsers import UserBadgeParser, UserBadgeParserOptions
from funpayparsers.types import UserBadge


OPTIONS = UserBadgeParserOptions(empty_raw_source=True)


banned_badge_html = """<span class="label label-danger">заблокирован</span>"""
auto_issue_badge_html = """<span class="chat-msg-author-label label label-default">автоответ</span>"""
support_badge_html = """<span class="chat-msg-author-label label label-success">поддержка</span>"""


banned_badge_obj = UserBadge('', 'заблокирован', 'label label-danger')
auto_issue_badge_obj = UserBadge('', 'автоответ', 'chat-msg-author-label label label-default')
support_badge_obj = UserBadge('', 'поддержка', 'chat-msg-author-label label label-success')


def test_banned_badge_parsing():
    assert UserBadgeParser(banned_badge_html, options=OPTIONS).parse() == banned_badge_obj


def test_auto_issue_badge_parsing():
    assert UserBadgeParser(auto_issue_badge_html, options=OPTIONS).parse() == auto_issue_badge_obj


def test_support_badge_parsing():
    assert UserBadgeParser(support_badge_html, options=OPTIONS).parse() == support_badge_obj
