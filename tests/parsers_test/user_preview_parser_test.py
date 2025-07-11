from __future__ import annotations

import pytest

from funpayparsers.types import UserPreview
from funpayparsers.parsers import UserPreviewParser, UserPreviewParsingOptions


OPTIONS = UserPreviewParsingOptions(empty_raw_source=True)


@pytest.fixture
def online_user_preview_html():
    return """
<div class="tc-user">
    <div class="media media-user online">
        <div class="media-left">
            <div class="avatar-photo pseudo-a" tabindex="0" data-href="https://funpay.com/en/users/12345/" style="background-image: url(/img/layout/avatar.png);"></div>
        </div>
        <div class="media-body">
            <div class="media-user-name">
                <span class="pseudo-a" tabindex="0" data-href="https://funpay.com/en/users/12345/">Username</span>
            </div>
            <div class="media-user-status">online</div>
        </div>
    </div>
</div>
"""


@pytest.fixture
def online_user_preview_obj():
    return UserPreview(
        raw_source='',
        id=12345,
        username='Username',
        online=True,
        banned=False,
        status_text='online',
        avatar_url='/img/layout/avatar.png'
    )


@pytest.fixture
def offline_user_preview_html():
    return """
<div class="tc-user">
    <div class="media media-user offline">
        <div class="media-left">
            <div class="avatar-photo pseudo-a" tabindex="0" data-href="https://funpay.com/en/users/12345/" style="background-image: url(/img/layout/avatar.png);"></div>
        </div>
        <div class="media-body">
            <div class="media-user-name">
                <span class="pseudo-a" tabindex="0" data-href="https://funpay.com/en/users/12345/">Username</span>
            </div>
            <div class="media-user-status">was online 2 weeks ago</div>
        </div>
    </div>
</div>
"""


@pytest.fixture
def offline_user_preview_obj():
    return UserPreview(
        raw_source='',
        id=12345,
        username='Username',
        online=False,
        banned=False,
        status_text='was online 2 weeks ago',
        avatar_url='/img/layout/avatar.png'
    )


@pytest.fixture
def banned_user_preview_html():
    return """
<div class="tc-user">
    <div class="media media-user offline banned">
        <div class="media-left">
            <div class="avatar-photo pseudo-a" tabindex="0" data-href="https://funpay.com/en/users/12345/" style="background-image: url(/img/layout/avatar.png);"></div>
        </div>
        <div class="media-body">
            <div class="media-user-name">
                <span class="pseudo-a" tabindex="0" data-href="https://funpay.com/en/users/12345/">Username</span>
            </div>
            <div class="media-user-status">banned</div>
        </div>
    </div>
</div>
"""

@pytest.fixture
def banned_user_preview_obj():
    return UserPreview(
        raw_source='',
        id=12345,
        username='Username',
        online=False,
        banned=True,
        status_text='banned',
        avatar_url='/img/layout/avatar.png'
    )


@pytest.mark.parametrize('html,expected',
                         [
                             ('online_user_preview_html', 'online_user_preview_obj'),
                             ('offline_user_preview_html', 'offline_user_preview_obj'),
                             ('banned_user_preview_html', 'banned_user_preview_obj'),
                         ])
def test_user_preview_parsing(html, expected, request):
    html = request.getfixturevalue(html)
    expected = request.getfixturevalue(expected)
    assert UserPreviewParser(html, OPTIONS).parse() == expected
