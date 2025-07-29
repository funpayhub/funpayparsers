from __future__ import annotations

import pytest

from funpayparsers.types.enums import SubcategoryType


@pytest.mark.parametrize(
    'url,expected_value',
    [
        ('https://funpay.com/en/lots/3031/', SubcategoryType.COMMON),
        ('https://funpay.com/lots/3031/', SubcategoryType.COMMON),
        ('https://funpay.com/en/chips/125/', SubcategoryType.CURRENCY),
        ('https://funpay.com/chips/125/', SubcategoryType.CURRENCY),
        ('https://funpay.com/en/unknown_type/123/', SubcategoryType.UNKNOWN),
        ('https://funpay.com/unknown_type/123/', SubcategoryType.UNKNOWN),
    ]
)
def test_subcategory_type_by_url_determination(url, expected_value):
    assert SubcategoryType.get_by_url(url) is expected_value


@pytest.mark.parametrize(
    'url,expected_value',
    [
        ('lot-3031', SubcategoryType.COMMON),
        ('chip-128', SubcategoryType.CURRENCY),
        ('unknown-12345', SubcategoryType.UNKNOWN),
    ]
)
def test_subcategory_type_by_showcase_determination(url, expected_value):
    assert SubcategoryType.get_by_showcase_data_section(url) is expected_value