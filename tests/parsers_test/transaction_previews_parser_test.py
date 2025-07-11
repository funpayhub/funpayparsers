from __future__ import annotations

from funpayparsers.types import PaymentMethod, TransactionStatus
from funpayparsers.types.common import MoneyValue
from funpayparsers.types.finances import TransactionPreview, TransactionPreviewsBatch
from funpayparsers.parsers.transaction_previews_parser import (
    TransactionPreviewsParser,
    TransactionPreviewsParsingOptions,
)


OPTIONS = TransactionPreviewsParsingOptions(empty_raw_source=True)


complete_order_transaction_html = """
<div class="tc-item transaction-status-complete" data-transaction="12345">
  <div class="tc-date">
    <span class="tc-date-time">20 января 2024, 23:11 </span>
    <span class="tc-date-left">год назад</span>
  </div>
  <div class="tc-desc">
    <span class="tc-title">Заказ #ABCDEFGH</span>
  </div>
  <div class="tc-status transaction-status">Завершено</div>
  <div class="tc-price">+ 1.23 <span class="unit">₽</span>
  </div>
  <div class="tc-go">
    <i class="fa fa-chevron-right"></i>
  </div>
</div>

<form method="post" class="dyn-table-form" action="https://funpay.com/en/users/transactions">
    <input type="hidden" name="user_id" value="12345">
    <input type="hidden" name="continue" value="101010">
    <input type="hidden" name="filter" value="">
</form>
"""


complete_order_transaction_obj = TransactionPreviewsBatch(
    raw_source='',
    transactions=[
        TransactionPreview(
            raw_source='',
            id=12345,
            date_text='20 января 2024, 23:11',
            desc='Заказ #ABCDEFGH',
            status=TransactionStatus.COMPLETED,
            amount=MoneyValue(
                raw_source='',
                value=1.23,
                character='₽'
            ),
            payment_method=None,
            withdrawal_number=None
        )
    ],
    user_id=12345,
    filter="",
    next_transaction_id=101010
)


cancelled_withdrawal_transaction_html = """
<div class="tc-item transaction-status-cancel" data-transaction="12345">
  <div class="tc-date">
    <span class="tc-date-time">20 января 2024, 23:11 </span>
    <span class="tc-date-left">год назад</span>
  </div>
  <div class="tc-desc">
    <span class="tc-title">Вывод денег #54321</span>
    <span class="tc-payment-number">123456••••••7890</span>
    <span class="tc-txn-obj-info">
      <span class="payment-logo payment-method-card_rub"></span>
    </span>
  </div>
  <div class="tc-status transaction-status">Отменено</div>
  <div class="tc-price">− 1234.56 <span class="unit">₽</span>
  </div>
  <div class="tc-go">
    <i class="fa fa-chevron-right"></i>
  </div>
</div>
"""

cancelled_withdrawal_transaction_obj = TransactionPreviewsBatch(
    raw_source='',
    transactions=[
        TransactionPreview(
            raw_source='',
            id=12345,
            date_text='20 января 2024, 23:11',
            desc='Вывод денег #54321',
            status=TransactionStatus.CANCELLED,
            amount=MoneyValue(
                raw_source='',
                value=-1234.56,
                character='₽'
            ),
            payment_method=PaymentMethod.CARD_RUB,
            withdrawal_number='123456••••••7890'
        )
    ],
    user_id=None,
    filter=None,
    next_transaction_id=None
)


def test_complete_order_transaction_parsing():
    parser = TransactionPreviewsParser(complete_order_transaction_html, options=OPTIONS)
    assert parser.parse() == complete_order_transaction_obj


def test_cancelled_withdrawal_transaction_parsing():
    parser = TransactionPreviewsParser(cancelled_withdrawal_transaction_html, options=OPTIONS)
    assert parser.parse() == cancelled_withdrawal_transaction_obj
