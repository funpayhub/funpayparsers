from __future__ import annotations

import pytest

from funpayparsers.types.enums import TransactionStatus


@pytest.mark.parametrize(
    'css_cls,expected_value',
    [
        ('some_cls transaction-status-waiting some_cls2', TransactionStatus.PENDING),
        ('some_cls transaction-status-complete', TransactionStatus.COMPLETED),
        ('some_cls transaction-status-cancel', TransactionStatus.CANCELLED),
        ('some_cls some_cls2', TransactionStatus.UNKNOWN),
    ]
)
def test_currency_determination(css_cls, expected_value):
    assert TransactionStatus.get_by_css_class(css_cls) is expected_value
