from __future__ import annotations

import pytest

from funpayparsers.types.enums import Currency


@pytest.mark.parametrize(
    'char,expected_value',
    [
        ('₽', Currency.RUB),
        ('$', Currency.USD),
        ('€', Currency.EUR),
        ('any_char', Currency.UNKNOWN),
    ]
)
def test_currency_determination(char, expected_value):
    assert Currency.get_by_character(char) is expected_value
