from __future__ import annotations

import pytest

from funpayparsers.types.enums import UpdateType


@pytest.mark.parametrize(
    'update_type_str,expected_value',
    [
        ('orders_counters', UpdateType.ORDERS_COUNTERS),
        ('chat_counter', UpdateType.CHAT_COUNTER),
        ('chat_bookmarks', UpdateType.CHAT_BOOKMARKS),
        ('chat_node', UpdateType.CHAT_NODE),
        ('c-p-u', UpdateType.CPU),
        ('some-unknown-update-type', None),
    ]
)
def test_update_type_determination(update_type_str, expected_value):
    assert UpdateType.get_by_type_str(update_type_str) is expected_value
