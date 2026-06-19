from __future__ import annotations

import pytest

from funpayparsers.types.enums import Currency, Language
from funpayparsers.parsers.page_header_parser import PageHeaderParser


@pytest.mark.parametrize(
    'source',
    [
        '',
        '<html><body><div>no header here</div></body></html>',
    ],
)
def test_missing_header_yields_empty_header(source: str):
    # Regression: a source without a `<header>` (empty string, error/redirect
    # page) must yield an empty header instead of raising on `css('header')[0]`.
    header = PageHeaderParser(source).parse()

    assert header.user_id is None
    assert header.username is None
    assert header.avatar_url is None
    assert header.language is Language.UNKNOWN
    assert header.currency is Currency.UNKNOWN
    assert header.sales_available is False
    assert header.logout_token is None
