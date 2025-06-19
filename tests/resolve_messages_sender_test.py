import pytest
from funpayparsers.parsers.utils import resolve_messages_senders
from funpayparsers.types import Message, UserBadge

support_badge = UserBadge(
    raw_source='',
    text='поддержка',
    css_class='label-success'
)

msg_1 = Message(
    raw_source='',
    id=20,
    is_heading=True,
    sender_id=555,
    sender_username='giga',
    badge=support_badge,
    send_date_text='01.06.2025',
    text='zdarova, vam ban',
    image_url=None
)

msg_2 = Message(
    raw_source='',
    id=21,
    is_heading=False,
    sender_id=555,
    sender_username='giga',
    badge=None,
    send_date_text='01.06.2025',
    text='eto fiasko bratan',
    image_url=None
)

msg_3 = Message(
    raw_source='',
    id=22,
    is_heading=True,
    sender_id=666,
    sender_username='valerka2013',
    badge=None,
    send_date_text='01.06.2025',
    text='jean claude van damme?',
    image_url=None
)

msg_4 = Message(
    raw_source='',
    id=23,
    is_heading=True,
    sender_id=555,
    sender_username='giga',
    badge=support_badge,
    send_date_text='01.06.2025',
    text='no no no, BAN!',
    image_url=None
)

def test_message_sender_resolver():
    messages = [msg_1, msg_2, msg_3, msg_4]
    resolve_messages_senders(messages)
    assert messages == [msg_1, msg_2, msg_3, msg_4]
