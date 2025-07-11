from __future__ import annotations

import pytest

from funpayparsers.types.enums import OrderStatus


@pytest.mark.parametrize(
    'css_class,expected_value',
    [
        ('some_cls text-primary some_cls2', OrderStatus.PAID),
        ('some_cls text-success some_cls2', OrderStatus.COMPLETED),
        ('some_cls text-warning some_cls2', OrderStatus.REFUNDED),
        ('some_cls some_cls2', OrderStatus.UNKNOWN),
    ]
)
def test_order_status_determination(css_class, expected_value):
    assert OrderStatus.get_by_css_class(css_class) is expected_value
