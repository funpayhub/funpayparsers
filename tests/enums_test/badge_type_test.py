from __future__ import annotations

import pytest

from funpayparsers.types.enums import BadgeType


@pytest.mark.parametrize(
    'css_class,expected_value',
    [
        ('some_cls label-danger some_cls2', BadgeType.BANNED),
        ('some_cls label-primary some_cls2', BadgeType.NOTIFICATIONS),
        ('some_cls label-success some_cls2', BadgeType.SUPPORT),
        ('some_cls label-default some_cls2', BadgeType.AUTO_DELIVERY),
        ('some_cls label-warning some_cls2', BadgeType.NOT_ACTIVATED),
        ('some_cls some_cls2', BadgeType.UNKNOWN),
    ]
)
def test_badge_type_determination(css_class, expected_value):
    assert BadgeType.get_by_css_class(css_class) is expected_value
