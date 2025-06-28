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
    FROM_LOT_PREVIEW = 3



@dataclass(frozen=True)
class MoneyValueParserOptions(FunPayObjectParserOptions):
    parsing_type: MoneyValueParsingType = MoneyValueParsingType.FROM_STRING
    parse_value_from_attribute: bool = True
    """
    Take numeric value from node attribute or not.
    Uses when parsing from lot preview.
    This parameter is necessary because standard lots have an exact price in the data-s attribute, 
    while currency lots have a minimum purchase amount in the data-s attribute.
    
    If parsing standard lot, set it to True.
    If parsing currency lot, set it to False.
    Defaults to True.
    """


class MoneyValueParser(FunPayHTMLObjectParser[MoneyValue, MoneyValueParserOptions]):
    # todo: note about "tc-price" div in doc-string.

    __options_cls__ = MoneyValueParserOptions

    def _parse(self):
        types = {
            MoneyValueParsingType.FROM_ORDER_PREVIEW: self._parse_order_preview_type,
            MoneyValueParsingType.FROM_TRANSACTION_PREVIEW: self._parse_transaction_preview_type,
            MoneyValueParsingType.FROM_LOT_PREVIEW: self._parse_lot_preview_type,
            MoneyValueParsingType.FROM_STRING: self._parse_string_type,
        }
        return types[self.options.parsing_type]()

    def _parse_order_preview_type(self) -> MoneyValue:
        div = self.tree.xpath('//div[contains(@class, "tc-price")]')[0]
        string = div.xpath('string(.)')
        return parse_money_value_string(string, raw_source=self.raw_source, raise_on_error=True)

    def _parse_transaction_preview_type(self) -> MoneyValue:
        div = self.tree.xpath('//div[contains(@class, "tc-price")]')[0]
        string = div.xpath('string(.)')
        return parse_money_value_string(string, raw_source=self.raw_source, raise_on_error=True)

    def _parse_lot_preview_type(self) -> MoneyValue:
        div = self.tree.xpath('//div[contains(@class, "tc-price")]')[0]
        inner_div = div.xpath('.//div')[0]
        string = inner_div.xpath('string(.)')
        value = parse_money_value_string(string, raw_source=self.raw_source, raise_on_error=True)
        if self.options.parse_value_from_attribute:
            value.value = float(div.get('data-s'))
        return value

    def _parse_string_type(self) -> MoneyValue:
        return parse_money_value_string(self.raw_source, raise_on_error=True)
