from __future__ import annotations

import pytest

from funpayparsers.types.enums import Language


@pytest.mark.parametrize(
    'appdata_alias,expected_value',
    [
        ('ru', Language.RU),
        ('en', Language.EN),
        ('uk', Language.UK),
        ('any_lang', Language.UNKNOWN),
    ]
)
def test_language_by_appdata_determination(appdata_alias, expected_value):
    assert Language.get_by_lang_code(appdata_alias) is expected_value


@pytest.mark.parametrize(
    'css_class,expected_value',
    [
        ('some_class menu-icon-lang-ru some_class', Language.RU),
        ('some_class menu-icon-lang-en some_class', Language.EN),
        ('some_class menu-icon-lang-uk some_class', Language.UK),
        ('some_class menu-icon-lang some_class', Language.UNKNOWN),
    ]
)
def test_language_by_header_css_class_determination(css_class, expected_value):
    assert Language.get_by_header_menu_css_class(css_class) is expected_value
