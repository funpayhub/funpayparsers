from __future__ import annotations

from funpayparsers.types import Message, MessageMeta, UserBadge
from funpayparsers.types.enums import MessageType
from funpayparsers.parsers.messages_parser import MessagesParser, MessagesParsingOptions


OPTIONS = MessagesParsingOptions(empty_raw_source=True)

heading_message_html = """<div class="chat-msg-item chat-msg-with-head" id="message-12345">
    <div class="chat-message">
        <div class="media-user-name">
            <a href="https://funpay.com/users/54321/" class="chat-msg-author-link">Username</a>
            <div class="chat-msg-date" title="26 мая, 11:21:41">11:21:41</div>
        </div>
        <div class="chat-msg-body">
            <div class="chat-msg-text">MessageText</div>
        </div>
    </div>
</div>"""

heading_message_obj = Message(
    raw_source='',
    id=12345,
    is_heading=True,
    sender_id=54321,
    sender_username='Username',
    badge=None,
    send_date_text='26 мая, 11:21:41',
    text='MessageText',
    image_url=None,
    chat_id=None,
    chat_name=None,
    meta=MessageMeta(raw_source='')
)


non_heading_message_html = """<div class="chat-msg-item" id="message-12346">
    <div class="chat-message">
        <div class="chat-msg-body">
            <div class="chat-msg-text">MessageText</div>
        </div>
    </div>
</div>"""

non_heading_message_obj = Message(
    raw_source='',
    id=12346,
    is_heading=False,
    sender_id=None,
    sender_username=None,
    badge=None,
    send_date_text=None,
    text='MessageText',
    image_url=None,
    chat_id=None,
    chat_name=None,
    meta=MessageMeta(raw_source='')
)


notification_message_html = """<div class="chat-msg-item chat-msg-with-head" id="message-12347">
    <div class="chat-message">
        <div class="media-user-name">
            FunPay <span class="chat-msg-author-label label label-primary">оповещение</span>
            <div class="chat-msg-date" title="4 мая, 10:41:16">04.05.2025</div>
        </div>
        <div class="chat-msg-body">
            <div class="alert alert-with-icon alert-info" role="alert">
                <i class="fas fa-info-circle alert-icon"></i>
                <div class="chat-msg-text">Продавец <a href="https://funpay.com/users/10/">SellerUsername</a> вернул деньги покупателю <a href="https://funpay.com/users/54321/">BuyerUsername</a> по <a href="https://funpay.com/orders/AAAAAAAA/">заказу #AAAAAAAA</a>.</div>
            </div>
        </div>
    </div>
</div>"""

notification_message_obj = Message(
    raw_source='',
    id=12347,
    is_heading=True,
    sender_id=0,
    sender_username='FunPay',
    send_date_text='4 мая, 10:41:16',
    text='Продавец SellerUsername вернул деньги покупателю BuyerUsername по заказу #AAAAAAAA.',
    image_url=None,
    badge=UserBadge(
        raw_source='',
        css_class='chat-msg-author-label label label-primary',
        text='оповещение'
    ),
    chat_id=None,
    chat_name=None,
    meta=MessageMeta(
        raw_source='',
        type=MessageType.ORDER_REFUNDED,
        seller_id=10,
        seller_username='SellerUsername',
        buyer_id=54321,
        buyer_username='BuyerUsername',
        order_id='AAAAAAAA'
    )
)


multiple_messages = f'{heading_message_html}\n{non_heading_message_html}'
multiple_messages_obj = [
    heading_message_obj,
    Message(
        raw_source='',
        id=12346,
        is_heading=False,
        sender_id=heading_message_obj.sender_id,
        sender_username=heading_message_obj.sender_username,
        badge=heading_message_obj.badge,
        send_date_text=heading_message_obj.send_date_text,
        text='MessageText',
        image_url=None,
        chat_id=None,
        chat_name=None,
        meta=MessageMeta(raw_source='')
    )
]



def test_heading_message_parsing():
    parser = MessagesParser(heading_message_html, options=OPTIONS)
    assert parser.parse()[0] == heading_message_obj


def test_non_heading_message_parsing():
    parser = MessagesParser(non_heading_message_html, options=OPTIONS)
    assert parser.parse()[0] == non_heading_message_obj


def test_notification_message_parsing():
    parser = MessagesParser(notification_message_html, options=OPTIONS)
    assert parser.parse()[0] == notification_message_obj


def test_multiple_messages_parsing():
    parser = MessagesParser(multiple_messages, options=OPTIONS)
    assert parser.parse() == multiple_messages_obj