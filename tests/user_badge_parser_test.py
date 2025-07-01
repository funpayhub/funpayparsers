import pytest
from funpayparsers.parsers import UserBadgeParser, UserBadgeParserOptions
from funpayparsers.types import UserBadge


OPTIONS = UserBadgeParserOptions(empty_raw_source=True)

@pytest.mark.parametrize(
    'html,obj',
    [
        ('<span class="label css_class">BadgeText</span>',
         UserBadge(raw_source='', css_class='label css_class', text='BadgeText')),
    ]
)
def test_badge_parser(html, obj):
    assert UserBadgeParser(html, options=OPTIONS).parse() == obj


@pytest.mark.parametrize(
    'html',
    [
        ('<span class="label css_class">BadgeText</span>',)
    ]
)
def test_badge_parser_raise_error_if_no_label_css_class(html):
    with pytest.raises(Exception) as e:
        UserBadgeParser(html, options=OPTIONS).parse()

    # todo: make custom parsing exception and assertation for this exception
