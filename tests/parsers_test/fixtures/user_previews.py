__all__ = ('user_preview_data_factory',
           'online_user_preview_html',
           'online_user_preview_obj',
           'offline_user_preview_html',
           'offline_user_preview_obj',
           'banned_user_preview_html',
           'banned_user_preview_obj',)

import pytest
from funpayparsers.types import UserPreview


@pytest.fixture
def user_preview_data_factory():
    def factory(id: int,
                username: str,
                online: bool,
                banned: bool,
                status_text: str | None = None) -> tuple[str, UserPreview]:
        online = online if not banned else False
        status_text = 'online' if online else 'banned' if banned else 'was online 2 weeks ago' if status_text is None else status_text
        avatar_url = '/img/layout/avatar.png'

        html = f'''<div class="tc-user">
    <div class="media media-user {'online' if online else 'offline banned' if banned else 'offline'}">
        <div class="media-left">
            <div class="avatar-photo pseudo-a" tabindex="0" data-href="https://funpay.com/en/users/{id}/" style="background-image: url({avatar_url});"></div>
        </div>
        <div class="media-body">
            <div class="media-user-name">
                <span class="pseudo-a" tabindex="0" data-href="https://funpay.com/en/users/{id}/">{username}</span>
            </div>
            <div class="media-user-status">{status_text}</div>
        </div>
    </div>
</div>
'''

        obj = UserPreview(
            raw_source='',
            id=id,
            username=username,
            online=online,
            banned=banned,
            status_text=status_text,
            avatar_url=avatar_url
        )

        return html, obj
    return factory


@pytest.fixture
def online_user_preview_html(user_preview_data_factory) -> str:
    html, _ = user_preview_data_factory(id=1,
                                        username='Username',
                                        online=True,
                                        banned=False)
    return html


@pytest.fixture
def online_user_preview_obj(user_preview_data_factory) -> UserPreview:
    _, obj = user_preview_data_factory(id=1,
                                       username='Username',
                                       online=True,
                                       banned=False)
    return obj


@pytest.fixture
def offline_user_preview_html(user_preview_data_factory) -> str:
    html, _ = user_preview_data_factory(id=1,
                                        username='Username',
                                        online=False,
                                        banned=False)
    return html


@pytest.fixture
def offline_user_preview_obj(user_preview_data_factory) -> UserPreview:
    _, obj = user_preview_data_factory(id=1,
                                       username='Username',
                                       online=False,
                                       banned=False)
    return obj


@pytest.fixture
def banned_user_preview_html(user_preview_data_factory) -> str:
    html, _ = user_preview_data_factory(id=1,
                                        username='Username',
                                        online=False,
                                        banned=True)
    return html


@pytest.fixture
def banned_user_preview_obj(user_preview_data_factory) -> UserPreview:
    _, obj = user_preview_data_factory(id=1,
                                       username='Username',
                                       online=False,
                                       banned=True)
    return obj
