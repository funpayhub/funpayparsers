from __future__ import annotations

import pytest

from funpayparsers.types import Message, UserBadge, MessageMeta
from funpayparsers.parsers.utils import resolve_messages_senders


support_badge = UserBadge(
    raw_source='',
    text='поддержка',
    css_class='label-success'
)


processed_messages = [
    Message(
        raw_source='',
        id=1,
        is_heading=True,
        sender_id=1,
        sender_username='SomeUser1',
        badge=support_badge,
        send_date_text='01.01.2077',
        text='MessageText1',
        image_url=None,
        chat_id=None,
        chat_name=None,
        meta=MessageMeta(raw_source='')
    ),
    Message(
        raw_source='',
        id=2,
        is_heading=False,
        sender_id=1,
        sender_username='SomeUser1',
        badge=support_badge,
        send_date_text='01.01.2077',
        text='MessageText2',
        image_url=None,
        chat_id=None,
        chat_name=None,
        meta=MessageMeta(raw_source='')
    )
]


@pytest.fixture
def original_messages():
    messages = [
        Message(
            raw_source='',
            id=1,
            is_heading=True,
            sender_id=1,
            sender_username='SomeUser1',
            badge=support_badge,
            send_date_text='01.01.2077',
            text='MessageText1',
            image_url=None,
            chat_id=None,
            chat_name=None,
            meta=MessageMeta(raw_source='')
        ),
        Message(
            raw_source='',
            id=2,
            is_heading=False,
            sender_id=None,
            sender_username=None,
            badge=None,
            send_date_text='01.01.2077',
            text='MessageText2',
            image_url=None,
            chat_id=None,
            chat_name=None,
            meta=MessageMeta(raw_source='')
        )
    ]

    return messages


def test_message_sender_resolver(original_messages):
    resolve_messages_senders(original_messages)
    assert original_messages == processed_messages
