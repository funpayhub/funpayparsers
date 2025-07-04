__all__ = ('private_chat_data_factory',
           'unread_private_chat_preview_html',
           'unread_private_chat_preview_obj',
           'read_private_chat_preview_html',
           'read_private_chat_preview_obj',
           'private_chat_preview_data')

from funpayparsers.types import PrivateChatPreview
import pytest


@pytest.fixture
def private_chat_data_factory():
    def factory(id: int,
                unread: bool,
                username: str | None = None,
                last_message_id: int = 12345,
                last_read_message_id: int = 12345,
                last_message_preview: str | None = None,
                last_message_time_text: str | None = None) -> tuple[str, PrivateChatPreview]:

        username = username if username is not None else f'Username{id}'
        last_message_preview = last_message_preview if last_message_preview is not None else 'Message Text Preview'
        last_message_time_text = last_message_time_text if last_message_time_text is not None else '12:34'
        avatar_url = '/img/layout/avatar.png'

        html = f"""<a href="https://funpay.com/chat/?node={id}" class="contact-item{' unread' if unread else ''}" data-id="{id}" data-node-msg="{last_message_id}" data-user-msg="{last_read_message_id}">
    <div class="contact-item-photo">
        <div class="avatar-photo" style="background-image: url({avatar_url});"></div>
    </div>
    <div class="media-user-name">{username}</div>
    <div class="contact-item-message">{last_message_preview}</div>
    <div class="contact-item-time">{last_message_time_text}</div>
</a>
"""
        obj = PrivateChatPreview(
            raw_source='',
            id=id,
            is_unread=unread,
            name=username,
            avatar_url=avatar_url,
            last_message_id=last_message_id,
            last_read_message_id=last_read_message_id,
            last_message_preview=last_message_preview,
            last_message_time_text=last_message_time_text,
        )

        return html, obj
    return factory


@pytest.fixture
def unread_private_chat_preview_html(private_chat_data_factory) -> str:
    html, _ = private_chat_data_factory(1, True)
    return html


@pytest.fixture
def unread_private_chat_preview_obj(private_chat_data_factory) -> list[PrivateChatPreview]:
    _, obj = private_chat_data_factory(1, True)
    return [obj]


@pytest.fixture
def read_private_chat_preview_html(private_chat_data_factory) -> str:
    html, _ = private_chat_data_factory(1, False)
    return html


@pytest.fixture
def read_private_chat_preview_obj(private_chat_data_factory) -> list[PrivateChatPreview]:
    _, obj = private_chat_data_factory(1, False)
    return [obj]


@pytest.fixture(
    params=[
        ('unread_private_chat_preview_html', 'unread_private_chat_preview_obj'),
        ('read_private_chat_preview_html', 'read_private_chat_preview_obj'),
    ],
    ids=['unread_chat_preview', 'read_chat_preview']
)
def private_chat_preview_data(request) -> tuple[str, PrivateChatPreview]:
    html, obj = request.param
    html = request.getfixturevalue(html)
    obj = request.getfixturevalue(obj)
    return html, obj
