__all__ = ('MoneyValueParser', 'MoneyValueParserOptions', 'MoneyValueParsingType')

from dataclasses import dataclass
from funpayparsers.parsers.base import FunPayObjectParserOptions, FunPayHTMLObjectParser
from funpayparsers.types.common import MoneyValue
from funpayparsers.parsers.utils import parse_money_value_string
from enum import Enum


class MoneyValueParsingType(Enum):
    FROM_STRING = 0
    FROM_ORDER_PREVIEW = 1
    FROM_TRANSACTION_PREVIEW = 2
    FROM_OFFER_PREVIEW = 3



@dataclass(frozen=True)
class MoneyValueParserOptions(FunPayObjectParserOptions):
    parsing_type: MoneyValueParsingType = MoneyValueParsingType.FROM_STRING
    parse_value_from_attribute: bool = True
    """
    Take numeric value from node attribute or not.
    Uses when parsing from offer preview.
    This parameter is necessary because standard offers have an exact price in the data-s attribute, 
    while currency offers have a minimum purchase amount in the data-s attribute.
    
    If parsing standard offer, set it to True.
    If parsing currency offer, set it to False.
    Defaults to True.
    """


class MoneyValueParser(FunPayHTMLObjectParser[MoneyValue, MoneyValueParserOptions]):
    """
    Class for parsing money values.
    Possible locations:
        - On transactions page (https://funpay.com/account/balance)
        - On sales page (https://funpay.com/orders/trade)
        - On purchases page (https://funpay.com/orders/)
        - On subcategory offers list page (https://funpay.com/lots/<subcategory_id>/)
        - etc.
    """
    def _parse(self):
        types = {
            MoneyValueParsingType.FROM_ORDER_PREVIEW: self._parse_order_preview_type,
            MoneyValueParsingType.FROM_TRANSACTION_PREVIEW: self._parse_transaction_preview_type,
            MoneyValueParsingType.FROM_OFFER_PREVIEW: self._parse_offer_preview_type,
            MoneyValueParsingType.FROM_STRING: self._parse_string_type,
        }
        return types[self.options.parsing_type]()

    def _parse_order_preview_type(self) -> MoneyValue:
        val_str = self.tree.css('div.tc-price')[0].text().strip()
        return parse_money_value_string(val_str, raw_source=self.raw_source, raise_on_error=True)

    def _parse_transaction_preview_type(self) -> MoneyValue:
        val_str = self.tree.css('div.tc-price')[0].text().strip()
        return parse_money_value_string(val_str, raw_source=self.raw_source, raise_on_error=True)

    def _parse_offer_preview_type(self) -> MoneyValue:
        div = self.tree.css('div.tc-price')[0]
        val_str = div.css('div')[0].text().strip()
        value = parse_money_value_string(val_str, raw_source=self.raw_source, raise_on_error=True)
        if self.options.parse_value_from_attribute:
            value.value = float(div.attributes.get('data-s'))
        return value

    def _parse_string_type(self) -> MoneyValue:
        return parse_money_value_string(self.raw_source, raise_on_error=True)
