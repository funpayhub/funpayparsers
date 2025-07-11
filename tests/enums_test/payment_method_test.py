from __future__ import annotations

import pytest

from funpayparsers.types.enums import PaymentMethod


@pytest.mark.parametrize(
    'css_class,expected_value',
    [
        ('some_cls payment-method-1 some_cls2', PaymentMethod.QIWI),
        ('some_cls payment-method-2 some_cls2', PaymentMethod.YANDEX),
        ('some_cls payment-method-3 some_cls2', PaymentMethod.WEBMONEY_WME),
        ('some_cls payment-method-4 some_cls2', PaymentMethod.WEBMONEY_WMP),
        ('some_cls payment-method-5 some_cls2', PaymentMethod.WEBMONEY_WMR),
        ('some_cls payment-method-6 some_cls2', PaymentMethod.WEBMONEY_WMZ),
        ('some_cls payment-method-7 some_cls2', PaymentMethod.CARD_RUB),
        ('some_cls payment-method-8 some_cls2', PaymentMethod.MOBILE),
        ('some_cls payment-method-9 some_cls2', PaymentMethod.APPLE),
        ('some_cls payment-method-10 some_cls2', PaymentMethod.WEBMONEY_UNKNOWN),
        ('some_cls payment-method-11 some_cls2', PaymentMethod.CARD_UNKNOWN),
        ('some_cls payment-method-12 some_cls2', PaymentMethod.MASTERCARD),
        ('some_cls payment-method-13 some_cls2', PaymentMethod.VISA),
        ('some_cls payment-method-14 some_cls2', PaymentMethod.GOOGLE),
        ('some_cls payment-method-15 some_cls2', PaymentMethod.CARD_UNKNOWN),
        ('some_cls payment-method-16 some_cls2', PaymentMethod.CARD_UNKNOWN),
        ('some_cls payment-method-17 some_cls2', PaymentMethod.GOOGLE),
        ('some_cls payment-method-18 some_cls2', PaymentMethod.GOOGLE),
        ('some_cls payment-method-19 some_cls2', PaymentMethod.APPLE),
        ('some_cls payment-method-20 some_cls2', PaymentMethod.APPLE),
        ('some_cls payment-method-21 some_cls2', PaymentMethod.FPS),
        ('some_cls payment-method-22 some_cls2', PaymentMethod.MASTERCARD),
        ('some_cls payment-method-23 some_cls2', PaymentMethod.MASTERCARD),
        ('some_cls payment-method-24 some_cls2', PaymentMethod.FUNPAY),
        ('some_cls payment-method-25 some_cls2', PaymentMethod.CARD_UNKNOWN),
        ('some_cls payment-method-26 some_cls2', PaymentMethod.CARD_UNKNOWN),
        ('some_cls payment-method-27 some_cls2', PaymentMethod.CARD_UNKNOWN),
        ('some_cls payment-method-28 some_cls2', PaymentMethod.VISA),
        ('some_cls payment-method-29 some_cls2', PaymentMethod.VISA),
        ('some_cls payment-method-30 some_cls2', PaymentMethod.LITECOIN),
        ('some_cls payment-method-31 some_cls2', PaymentMethod.BINANCE),
        ('some_cls payment-method-32 some_cls2', PaymentMethod.CARD_UNKNOWN),
        ('some_cls payment-method-33 some_cls2', PaymentMethod.CARD_UNKNOWN),
        ('some_cls payment-method-34 some_cls2', PaymentMethod.CARD_UNKNOWN),
        ('some_cls payment-method-35 some_cls2', PaymentMethod.CARD_UNKNOWN),
        ('some_cls payment-method-36 some_cls2', PaymentMethod.PAYPAL),
        ('some_cls payment-method-37 some_cls2', PaymentMethod.CARD_UNKNOWN),
        ('some_cls payment-method-38 some_cls2', PaymentMethod.CARD_UNKNOWN),
        ('some_cls payment-method-39 some_cls2', PaymentMethod.CARD_UNKNOWN),
        ('some_cls payment-method-40 some_cls2', PaymentMethod.CARD_UNKNOWN),

        ('some_cls payment-method-qiwi some_cls2', PaymentMethod.QIWI),
        ('some_cls payment-method-yandex some_cls2', PaymentMethod.YANDEX),
        ('some_cls payment-method-fps some_cls2', PaymentMethod.YANDEX),
        ('some_cls payment-method-wme some_cls2', PaymentMethod.WEBMONEY_WME),
        ('some_cls payment-method-wmr some_cls2', PaymentMethod.WEBMONEY_WMR),
        ('some_cls payment-method-wmp some_cls2', PaymentMethod.WEBMONEY_WMP),
        ('some_cls payment-method-wmz some_cls2', PaymentMethod.WEBMONEY_WMZ),
        ('some_cls payment-method-card_rub some_cls2', PaymentMethod.CARD_RUB),
        ('some_cls payment-method-card_usd some_cls2', PaymentMethod.CARD_USD),
        ('some_cls payment-method-card_eur some_cls2', PaymentMethod.CARD_EUR),
        ('some_cls payment-method-card_uah some_cls2', PaymentMethod.CARD_UAH),
        ('some_cls payment-method-binance_usdt some_cls2', PaymentMethod.BINANCE_USDT),
        ('some_cls payment-method-binance_usdc some_cls2', PaymentMethod.BINANCE_USDC),
        ('some_cls payment-method-usdt_trc some_cls2', PaymentMethod.USDT_TRC),
    ]
)
def test_badge_type_determination(css_class, expected_value):
    assert PaymentMethod.get_by_css_class(css_class) is expected_value
