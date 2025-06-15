from funpayparsers.types import PrivateChatPreview
from funpayparsers.parsers import PrivateChatPreviewParser
import pytest
import random
import string
from dataclasses import replace


html = """
<a href="https://funpay.com/chat/?node={id}" class="contact-item" data-id="{id}" data-node-msg="{last_message_id}" data-user-msg="{last_read_message_id}">
    <div class="contact-item-photo">
        <div class="avatar-photo" style="background-image: url({avatar_url});"></div>
    </div>
    <div class="media-user-name">{name}</div>
    <div class="contact-item-message">{last_message_preview}</div>
    <div class="contact-item-time">{last_message_time_text}</div>
</a>
"""


@pytest.fixture
def chat_preview_data() -> PrivateChatPreview:
    last_msg_id = random.randint(1, 999999999)
    last_read_msg_id = random.randint(last_msg_id, last_msg_id + 1000000)
    chars = string.ascii_letters + string.digits

    return PrivateChatPreview(
        raw_source='',
        id=random.randint(1, 999999999),
        is_unread=False,
        name=''.join(
            random.choice(chars) for _ in range(random.randint(5, 25))
        ),
        avatar_url='',  # todo
        last_message_id=last_msg_id,
        last_read_message_id=last_read_msg_id,
        last_message_preview=''.join(
            random.choice(chars) for _ in range(random.randint(1, 250))
        ),
        last_message_time_text='12:23'  # todo
    )


@pytest.fixture
def private_chat_preview_data(chat_preview_data: PrivateChatPreview):
    source = html.format(**chat_preview_data.as_dict()).strip()
    return source, replace(chat_preview_data, raw_source=source)


def test_private_chat_preview_parser(private_chat_preview_data):
    source, data = private_chat_preview_data
    parser = PrivateChatPreviewParser(source)
    assert parser.parse() == [data]