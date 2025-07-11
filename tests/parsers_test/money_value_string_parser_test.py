from __future__ import annotations

import random

from funpayparsers.parsers.base import ParsingOptions
from funpayparsers.types.common import MoneyValue
from funpayparsers.parsers.money_value_parser import (
    MoneyValueParser,
    MoneyValueParsingMode,
    MoneyValueParsingOptions,
)


OPTIONS = ParsingOptions(empty_raw_source=True)


RANDOM_VALUE = round(random.uniform(10.0, 99.999), 6)
CURR = random.choice(["€", "$", "₽"])


def explicit_positive_value_parsing_test():
    raw_str = f"+{RANDOM_VALUE} {CURR}"
    need = MoneyValue(raw_source='', value=RANDOM_VALUE, character=CURR)
    options = MoneyValueParsingOptions(parsing_mode=MoneyValueParsingMode.FROM_STRING)
    parser = MoneyValueParser(raw_str, options=options & OPTIONS)
    assert parser.parse() == need


def value_with_spaces_parsing_test():
    raw_str = f"                  {RANDOM_VALUE}                          {CURR}"
    need = MoneyValue(raw_source='', value=RANDOM_VALUE, character=CURR)
    options = MoneyValueParsingOptions(parsing_mode=MoneyValueParsingMode.FROM_STRING)
    parser = MoneyValueParser(raw_str, options=options & OPTIONS)
    assert parser.parse() == need


def negative_value_parsing_test():
    raw_str = f"{-RANDOM_VALUE} {CURR}"
    need = MoneyValue(raw_source='', value=-RANDOM_VALUE, character=CURR)
    options = MoneyValueParsingOptions(parsing_mode=MoneyValueParsingMode.FROM_STRING)
    parser = MoneyValueParser(raw_str, options=options & OPTIONS)
    assert parser.parse() == need


def custom_negative_value_parsing_test():
    raw_str = f"−{RANDOM_VALUE} {CURR}"
    need = MoneyValue(raw_source='', value=-RANDOM_VALUE, character=CURR)
    options = MoneyValueParsingOptions(parsing_mode=MoneyValueParsingMode.FROM_STRING)
    parser = MoneyValueParser(raw_str, options=options & OPTIONS)
    assert parser.parse() == need