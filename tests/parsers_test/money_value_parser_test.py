from __future__ import annotations

from funpayparsers.parsers.base import ParsingOptions
from funpayparsers.types.common import MoneyValue
from funpayparsers.parsers.money_value_parser import (
    MoneyValueParser,
    MoneyValueParsingMode,
    MoneyValueParsingOptions,
)


OPTIONS = ParsingOptions(empty_raw_source=True)


transaction_preview_money_value_html = """<div class="tc-price">+ 1.42 <span class="unit">₽</span></div>"""
transaction_preview_money_value_obj = MoneyValue(
    raw_source='',
    value=1.42,
    character='₽'
)

order_preview_money_value_html = """<div class="tc-price text-nowrap tc-seller-sum">10.00 <span class="unit">₽</span></div>"""
order_preview_money_value_obj = MoneyValue(
    raw_source='',
    value=10.00,
    character='₽'
)

lot_preview_money_value_html = """
<div class="tc-price" data-s="90.427699">
<div>90.43 <span class="unit">₽</span></div>
</div>
"""
standard_lot_preview_money_value_obj = MoneyValue(
    raw_source='',
    value=90.427699,
    character='₽'
)

currency_lot_preview_money_value_obj = MoneyValue(
    raw_source='',
    value=90.43,
    character='₽'
)

string_money_value_str = """ + 1.23 ₽ """
string_money_value_obj = MoneyValue(
    raw_source='',
    value=1.23,
    character='₽'
)


def test_transaction_preview_money_value_parsing():
    options = MoneyValueParsingOptions(parsing_mode=MoneyValueParsingMode.FROM_TRANSACTION_PREVIEW)
    parser = MoneyValueParser(transaction_preview_money_value_html, options=options & OPTIONS)
    assert parser.parse() == transaction_preview_money_value_obj


def test_order_preview_money_value_parsing():
    options = MoneyValueParsingOptions(parsing_mode=MoneyValueParsingMode.FROM_ORDER_PREVIEW)
    parser = MoneyValueParser(order_preview_money_value_html, options=options & OPTIONS)
    assert parser.parse() == order_preview_money_value_obj


def test_standard_lot_preview_money_value_parsing():
    options = MoneyValueParsingOptions(parsing_mode=MoneyValueParsingMode.FROM_OFFER_PREVIEW)
    parser = MoneyValueParser(lot_preview_money_value_html, options=options & OPTIONS)
    assert parser.parse() == standard_lot_preview_money_value_obj


def test_currency_lot_preview_money_value_parsing():
    options = MoneyValueParsingOptions(parsing_mode=MoneyValueParsingMode.FROM_OFFER_PREVIEW,
                                       parse_value_from_attribute=False)
    parser = MoneyValueParser(lot_preview_money_value_html, options=options & OPTIONS)
    assert parser.parse() == currency_lot_preview_money_value_obj


def test_string_money_value_parsing():
    options = MoneyValueParsingOptions(parsing_mode=MoneyValueParsingMode.FROM_STRING)
    parser = MoneyValueParser(string_money_value_str, options=options & OPTIONS)
    assert parser.parse() == string_money_value_obj
