import pytest
from funpayparsers.types.enums import MessageType


@pytest.fixture
def new_order_ru() -> str:
    return '''Покупатель Buyer оплатил заказ #ABCDEFGH. Название лота
Buyer, не забудьте потом нажать кнопку «Подтвердить выполнение заказа».'''


@pytest.fixture
def new_order_en() -> str:
    return '''The buyer Buyer has paid for order #ABCDEFGH. Lot Name
Buyer, do not forget to press the «Confirm order fulfilment» button once you finish.'''


@pytest.fixture
def order_closed_ru() -> str:
    return (
        'Покупатель Buyer подтвердил успешное выполнение заказа #ABCDEFGH '
        'и отправил деньги продавцу Seller.'
    )


@pytest.fixture
def order_closed_en() -> str:
    return (
        'The buyer Buyer has confirmed that order #ABCDEFGH has been fulfilled '
        'successfully and that the seller Seller has been paid.'
    )


@pytest.fixture
def order_closed_by_admin_ru() -> str:
    return (
        'Администратор Admin подтвердил успешное выполнение заказа #ABCDEFGH '
        'и отправил деньги продавцу Seller.'
    )


@pytest.fixture
def order_closed_by_admin_en() -> str:
    return (
        'The administrator Admin has confirmed that order #ABCDEFGH '
        'has been fulfilled successfully '
        'and that the seller Seller has been paid.'
    )


@pytest.fixture
def order_reopened_ru() -> str:
    return 'Заказ #ABCDEFGH открыт повторно.'


@pytest.fixture
def order_reopened_en() -> str:
    return 'Order #ABCDEFGH has been reopened.'


@pytest.fixture
def order_refunded_ru() -> str:
    return 'Продавец Seller вернул деньги покупателю Buyer по заказу #ABCDEFGH.'


@pytest.fixture
def order_refunded_en() -> str:
    return 'The seller Seller has refunded the buyer Buyer on order #ABCDEFGH.'


@pytest.fixture
def order_partially_refunded_ru() -> str:
    return 'Часть средств по заказу #ABCDEFGH возвращена покупателю.'


@pytest.fixture
def order_partially_refunded_en() -> str:
    return 'A part of the funds pertaining to the order #ABCDEFGH has been refunded.'


@pytest.fixture
def new_feedback_ru() -> str:
    return 'Покупатель Seller написал отзыв к заказу #ABCDEFGH.'


@pytest.fixture
def new_feedback_en() -> str:
    return 'The buyer Seller has given feedback to the order #ABCDEFGH.'


@pytest.fixture
def feedback_changed_ru() -> str:
     return 'Покупатель Seller изменил отзыв к заказу #ABCDEFGH.'


@pytest.fixture
def feedback_changed_en() -> str:
    return 'The buyer Seller has edited their feedback to the order #ABCDEFGH.'


@pytest.fixture
def feedback_deleted_ru() -> str:
    return 'Покупатель Seller удалил отзыв к заказу #ABCDEFGH.'


@pytest.fixture
def feedback_deleted_en() -> str:
    return 'The buyer Seller has deleted their feedback to the order #ABCDEFGH.'


@pytest.fixture
def new_feedback_reply_ru() -> str:
    return 'Продавец Seller ответил на отзыв к заказу #ABCDEFGH.'


@pytest.fixture
def new_feedback_reply_en() -> str:
    return 'The seller Seller has replied to their feedback to the order #ABCDEFGH.'

@pytest.fixture
def feedback_reply_changed_ru() -> str:
    return 'Продавец Seller изменил ответ на отзыв к заказу #ABCDEFGH.'


@pytest.fixture
def feedback_reply_changed_en() -> str:
    return 'The seller Seller has edited a reply to their feedback to the order #ABCDEFGH.'


@pytest.fixture
def feedback_reply_deleted_ru() -> str:
    return 'Продавец Seller удалил ответ на отзыв к заказу #ABCDEFGH.'


@pytest.fixture
def feedback_reply_deleted_en() -> str:
    return 'The seller Seller has deleted a reply to their feedback to the order #ABCDEFGH.'


@pytest.mark.parametrize(
    'message,expected', [
        ('new_order_ru', MessageType.NEW_ORDER),
        ('new_order_en', MessageType.NEW_ORDER),
        ('order_closed_ru', MessageType.ORDER_CLOSED),
        ('order_closed_en', MessageType.ORDER_CLOSED),
        ('order_closed_by_admin_ru', MessageType.ORDER_CLOSED_BY_ADMIN),
        ('order_closed_by_admin_en', MessageType.ORDER_CLOSED_BY_ADMIN),
        ('order_reopened_ru', MessageType.ORDER_REOPENED),
        ('order_reopened_en', MessageType.ORDER_REOPENED),
        ('order_refunded_ru', MessageType.ORDER_REFUNDED),
        ('order_refunded_en', MessageType.ORDER_REFUNDED),
        ('order_partially_refunded_ru', MessageType.ORDER_PARTIALLY_REFUNDED),
        ('order_partially_refunded_en', MessageType.ORDER_PARTIALLY_REFUNDED),
        ('new_feedback_ru', MessageType.NEW_FEEDBACK),
        ('new_feedback_en', MessageType.NEW_FEEDBACK),
        ('feedback_changed_ru', MessageType.FEEDBACK_CHANGED),
        ('feedback_changed_en', MessageType.FEEDBACK_CHANGED),
        ('feedback_deleted_ru', MessageType.FEEDBACK_DELETED),
        ('feedback_deleted_en', MessageType.FEEDBACK_DELETED),
        ('new_feedback_reply_ru', MessageType.NEW_FEEDBACK_REPLY),
        ('new_feedback_reply_en', MessageType.NEW_FEEDBACK_REPLY),
        ('feedback_reply_changed_ru', MessageType.FEEDBACK_REPLY_CHANGED),
        ('feedback_reply_changed_en', MessageType.FEEDBACK_REPLY_CHANGED),
        ('feedback_reply_deleted_ru', MessageType.FEEDBACK_REPLY_DELETED),
        ('feedback_reply_deleted_en', MessageType.FEEDBACK_REPLY_DELETED),
    ]
)
def test_message_type_determination(message, expected, request):
    message_text = request.getfixturevalue(message)
    assert MessageType.get_by_message_text(message_text) is expected