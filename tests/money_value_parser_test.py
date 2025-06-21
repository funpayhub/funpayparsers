from funpayparsers.parsers.money_value_parser import MoneyValueParser, MoneyValueParserOptions
from funpayparsers.types.common import MoneyValue
from funpayparsers.types.enums import Currency


OPTIONS = MoneyValueParserOptions(empty_raw_source=True)


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
lot_preview_money_value_obj = MoneyValue(
    raw_source='',
    value=90.427699,
    character='₽'
)

string_money_value_str = """"""