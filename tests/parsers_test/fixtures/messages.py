__all__ = ('message_data_factory',
           'non_heading_message_html',
           'non_heading_message_obj',
           'heading_message_html',
           'heading_message_obj',
           'notification_message_html',
           'notification_message_obj',
           'multiple_messages_html',
           'multiple_messages_obj',
           'messages_data')

from funpayparsers.types import Message
from funpayparsers.parsers.utils import resolve_messages_senders
import pytest


@pytest.fixture
def message_data_factory(user_badge_obj, user_badge_html):
    def factory(id: int,
                heading: bool = False,
                notification: bool = False,
                text: str | None = None,
                image: str | None = None,
                sender_id: int | None = None,
                sender_username: str | None = None,
                ) -> tuple[str, Message]:
        heading = heading or notification

        html = f"""<div class="chat-msg-item {' chat-msg-with-head' if heading else ''}" id="message-{id}">
    <div class="chat-message">
        {{user_div}}
        <div class="chat-msg-body">
            {{msg_body}}
        </div>
    </div>
</div>"""
        send_date_text = '4 мая, 10:41:16'

        # header div creation
        if notification:
            sender_id, sender_username = 0, 'FunPay'
            user_div = f"""<div class="media-user-name">
FunPay {user_badge_html}
<div class="chat-msg-date" title="{send_date_text}">04.05.2025</div>
</div>"""

        elif heading:
            sender_id = sender_id if sender_id is not None else 1
            sender_username = sender_username if sender_username is not None else 'Username'
            user_div = f"""<a href="https://funpay.com/users/{sender_id}/" class="chat-msg-author-link">{sender_username}</a>
<div class="chat-msg-date" title="{send_date_text}">04.05.2025</div>"""
        else:
            sender_id, sender_username  = None, None
            user_div = ''

        # text div creation
        if notification:
            text_html = ('Продавец <a href="https://funpay.com/users/10/">SellerUsername</a> вернул деньги покупателю '
                    '<a href="https://funpay.com/users/54321/">BuyerUsername</a> по '
                    '<a href="https://funpay.com/orders/AAAAAAAA/">заказу #AAAAAAAA</a>.') if text is None else text
            text = 'Продавец SellerUsername вернул деньги покупателю BuyerUsername по заказу #AAAAAAAA.' if text is None else text

            text_div = f'''<div class="alert alert-with-icon alert-info" role="alert">
<i class="fas fa-info-circle alert-icon"></i>
<div class="chat-msg-text">{text_html}</div>
</div>'''
        else:
            if image is None:
                text = text if text is not None else 'MessageText'
                text_div = f'<div class="chat-msg-text">{text}</div>'
            else:
                text = None
                text_div = f'''<div class="chat-msg-text">
  <a class="chat-img-link" href="{image}">
    <img class="chat-img" src="{image}" width="185" height="83" alt="AltText">
  </a>
'''
        html = html.format(user_div=user_div, msg_body=text_div)

        obj = Message(
            raw_source='',
            id=id,
            is_heading=heading,
            sender_id=sender_id,
            sender_username=sender_username,
            badge=user_badge_obj if notification else None,
            send_date_text=send_date_text if heading else None,
            text=text,
            image_url=image
        )
        return html, obj

    return factory


@pytest.fixture
def non_heading_message_html(message_data_factory) -> str:
    html, _ = message_data_factory(id=1)
    return html


@pytest.fixture
def non_heading_message_obj(message_data_factory) -> list[Message]:
    _, obj = message_data_factory(id=1)
    return [obj]


@pytest.fixture
def heading_message_html(message_data_factory) -> str:
    html, _ = message_data_factory(id=1, heading=True)
    return html


@pytest.fixture
def heading_message_obj(message_data_factory) -> list[Message]:
    _, obj = message_data_factory(id=1, heading=True)
    return [obj]


@pytest.fixture
def notification_message_html(message_data_factory) -> str:
    html, _ = message_data_factory(id=1, notification=True)
    return html


@pytest.fixture
def notification_message_obj(message_data_factory) -> list[Message]:
    _, obj = message_data_factory(id=1, notification=True)
    return [obj]


@pytest.fixture
def multiple_messages_html(message_data_factory) -> str:
    html1, _ = message_data_factory(id=1, heading=True)
    html2, _ = message_data_factory(id=2)
    html3, _ = message_data_factory(id=3, notification=True)
    return '\n'.join([html1, html2, html3])


@pytest.fixture
def multiple_messages_obj(message_data_factory) -> list[Message]:
    _, obj1 = message_data_factory(id=1, heading=True)
    _, obj2 = message_data_factory(id=2)
    _, obj3 = message_data_factory(id=3, notification=True)
    messages = [obj1, obj2, obj3]
    resolve_messages_senders(messages)
    return messages


@pytest.fixture(params=[
    ('non_heading_message_html', 'non_heading_message_obj'),
    ('heading_message_html', 'heading_message_obj'),
    ('notification_message_html', 'notification_message_obj'),
    ('multiple_messages_html', 'multiple_messages_obj')
],
    ids=['non_heading_message', 'heading_message', 'notification_message', 'multiple_messages']
)
def messages_data(request) -> tuple[str, list[Message]]:
    html, obj = request.param
    html = request.getfixturevalue(html)
    obj = request.getfixturevalue(obj)
    return html, obj
