from funpayparsers.parsers.order_previews_parser import (OrderPreviewsParser,
                                                         OrderPreviewsParserOptions)
from funpayparsers.types.orders import OrderPreview, OrderCounterpartyInfo
from funpayparsers.types.enums import OrderStatus
from funpayparsers.types.common import MoneyValue


OPTIONS = OrderPreviewsParserOptions(empty_raw_source=True)


refunded_order_html = """
<a href="https://funpay.com/orders/ABCDEFGH/" class="tc-item warning">
    <div class="tc-date">
        <div class="tc-date-time">вчера, 13:33</div>
        <div class="tc-date-left">22 часа назад</div>
    </div>
    <div class="tc-order">#ABCDEFGH</div>
    <div class="order-desc">
        <div>Order Description</div>
        <div class="text-muted">Category, Subcategory</div>
    </div>
    <div class="tc-user">
        <div class="media media-user offline">
            <div class="media-left">
                <div class="avatar-photo pseudo-a" tabindex="0" data-href="https://funpay.com/users/123456/" style="background-image: url(path/to/avatar);"></div>
            </div>
            <div class="media-body">
                <div class="media-user-name">
                    <span class="pseudo-a" tabindex="0" data-href="https://funpay.com/users/123456/">Counterparty username</span>
                </div>
                <div class="media-user-status">Counterparty Status</div>
            </div>
        </div>
    </div>
    <div class="tc-status text-warning">Возврат</div>
    <div class="tc-price text-nowrap tc-buyer-sum">25.12 <span class="unit">₽</span></div>
</a>
"""

refunded_order_obj = OrderPreview(
    raw_source='',
    id='ABCDEFGH',
    date_text='вчера, 13:33',
    desc='Order Description',
    category_text='Category, Subcategory',
    status=OrderStatus.REFUNDED,
    amount=MoneyValue(
        raw_source='',
        value=25.12,
        character='₽'
    ),
    counterparty=OrderCounterpartyInfo(
        raw_source='',
        id=123456,
        username='Counterparty username',
        online=False,
        banned=False,
        status_text='Counterparty Status',
        avatar_url='path/to/avatar'
    )
)


def test_refunded_order_parsing():
    parser = OrderPreviewsParser(refunded_order_html, options=OPTIONS)
    assert parser.parse() == [refunded_order_obj]
