from __future__ import annotations

import pytest

from funpayparsers.types.enums import RunnerDataType


@pytest.mark.parametrize(
    'update_type_str,expected_value',
    [
        ('orders_counters', RunnerDataType.ORDERS_COUNTERS),
        ('chat_counter', RunnerDataType.CHAT_COUNTER),
        ('chat_bookmarks', RunnerDataType.CHAT_BOOKMARKS),
        ('chat_node', RunnerDataType.CHAT_NODE),
        ('c-p-u', RunnerDataType.CPU),
        ('some-unknown-update-type', None),
    ]
)
def test_update_type_determination(update_type_str, expected_value):
    assert RunnerDataType.get_by_type_str(update_type_str) is expected_value
