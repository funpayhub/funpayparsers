from __future__ import annotations

import pytest

from funpayparsers.types.enums import SubcategoryFieldType


@pytest.mark.parametrize(
    'code,expected',
    [
        (0, SubcategoryFieldType.UNKNOWN),
        (1, SubcategoryFieldType.NUMERIC_RANGE),
        (2, SubcategoryFieldType.TEXT),
        (3, SubcategoryFieldType.TEXTAREA),
        (4, SubcategoryFieldType.SELECT),
        (5, SubcategoryFieldType.DROPDOWN),
        (6, SubcategoryFieldType.IMAGES),
        (999, SubcategoryFieldType.UNKNOWN),
        (-1, SubcategoryFieldType.UNKNOWN),
    ],
)
def test_from_type_code(code, expected):
    assert SubcategoryFieldType.from_type_code(code) is expected


@pytest.mark.parametrize(
    'code,expected',
    [
        (1, SubcategoryFieldType.NUMERIC_RANGE),
        (4, SubcategoryFieldType.SELECT),
        (999, SubcategoryFieldType.UNKNOWN),
    ],
)
def test_direct_construction_matches_from_type_code(code, expected):
    # Regression: previously the enum used auto(), so SubcategoryFieldType(1)
    # returned UNKNOWN instead of NUMERIC_RANGE. Direct construction must now
    # agree with from_type_code for both known and unknown codes.
    assert SubcategoryFieldType(code) is expected
