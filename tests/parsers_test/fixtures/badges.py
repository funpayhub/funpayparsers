__all__ = ('user_badge_html', 'user_badge_obj')

import pytest
from funpayparsers.types import UserBadge


@pytest.fixture
def user_badge_html():
    return '<span class="label css_class">BadgeText</span>'


@pytest.fixture
def user_badge_obj():
    return UserBadge(
        raw_source='',
        text='BadgeText',
        css_class='label css_class'
    )
