import random

from funpayparsers.parsers.money_value_parser import MoneyValueParser, MoneyValueParserOptions, MoneyValueParsingType
from funpayparsers.parsers.base import FunPayObjectParserOptions
from funpayparsers.types.common import MoneyValue

OPTIONS = FunPayObjectParserOptions(empty_raw_source=True)

RANDOM_SUMM_PLUS = round(random.uniform(10.0, 99.999), 6)
RANDOM_SUMM_MINUS = round(random.uniform(-99.999, -10.0), 6)
CURR = random.choice(["€", "$", "₽"])

def test_parse_plus():
    raw_str = f"{RANDOM_SUMM_PLUS} {CURR}"
    need = MoneyValue(raw_source='', value=RANDOM_SUMM_PLUS, character=CURR)
    options = MoneyValueParserOptions(parsing_type=MoneyValueParsingType.FROM_STRING)
    parser = MoneyValueParser(raw_str, options=options & OPTIONS)
    assert parser.parse() == need

def test_parse_plus_space():
    raw_str = f"                  {RANDOM_SUMM_PLUS}                          {CURR}"
    need = MoneyValue(raw_source='', value=RANDOM_SUMM_PLUS, character=CURR)
    options = MoneyValueParserOptions(parsing_type=MoneyValueParsingType.FROM_STRING)
    parser = MoneyValueParser(raw_str, options=options & OPTIONS)
    assert parser.parse() == need

def test_parse_minus():
    raw_str = f"{RANDOM_SUMM_MINUS} {CURR}"
    need = MoneyValue(raw_source='', value=RANDOM_SUMM_MINUS, character=CURR)
    options = MoneyValueParserOptions(parsing_type=MoneyValueParsingType.FROM_STRING)
    parser = MoneyValueParser(raw_str, options=options & OPTIONS)
    assert parser.parse() == need

def test_parse_funpay_minus():
    raw_str = f"−{RANDOM_SUMM_PLUS} {CURR}"
    need = MoneyValue(raw_source='', value=-RANDOM_SUMM_PLUS, character=CURR)
    options = MoneyValueParserOptions(parsing_type=MoneyValueParsingType.FROM_STRING)
    parser = MoneyValueParser(raw_str, options=options & OPTIONS)
    assert parser.parse() == need