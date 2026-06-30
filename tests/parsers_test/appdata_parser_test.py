from __future__ import annotations

import pytest

from funpayparsers.types.enums import Language
from funpayparsers.parsers.appdata_parser import AppDataParser


@pytest.mark.parametrize('source', ['', '   '])
def test_empty_source_yields_empty_app_data(source: str) -> None:
    # Regression: pages may be served without a `data-app-data` attribute,
    # in which case an empty string reaches the parser. It must not fail on
    # `json.loads('')`.
    app_data = AppDataParser(source).parse()

    assert app_data.locale is Language.UNKNOWN
    assert app_data.csrf_token is None
    assert app_data.user_id is None
    assert app_data.webpush is None


def test_valid_source_still_parses() -> None:
    app_data = AppDataParser('{"locale": "en", "csrf-token": "tok", "userId": 42}').parse()

    assert app_data.locale is Language.EN
    assert app_data.csrf_token == 'tok'
    assert app_data.user_id == 42
