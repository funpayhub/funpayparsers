from __future__ import annotations


__all__ = ('MoneyValueParser', 'MoneyValueParsingOptions', 'MoneyValueParsingMode')

from typing import cast
from dataclasses import dataclass
from enum import Enum

from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.types.common import MoneyValue
from funpayparsers.parsers.utils import parse_money_value_string


class MoneyValueParsingMode(Enum):
    """``MoneyValueParser`` parsing modes enumeration."""

    FROM_STRING = 0
    """Raw source is a regular string, e.g., ``+12345.67$``."""

    FROM_ORDER_PREVIEW = 1
    """Raw source is/from an order preview HTML."""

    FROM_TRANSACTION_PREVIEW = 2
    """Raw source is/from a transaction preview HTML."""

    FROM_OFFER_PREVIEW = 3
    """Raw source is/from an offer preview HTML."""


@dataclass(frozen=True)
class MoneyValueParsingOptions(ParsingOptions):
    """Options class for ``MoneyValueParser``."""

    parsing_mode: MoneyValueParsingMode = MoneyValueParsingMode.FROM_STRING
    """
    ``MoneyValueParser`` parsing mode.
    
    Defaults to ``MoneyValueParsingMode.FROM_STRING``.
    """

    parse_value_from_attribute: bool = True
    """
    Whether to take money value from ``node`` attribute or not.
    
    Uses when parsing from offer preview.
    
    This parameter is necessary because standard offers have an exact price 
    in the ``data-s`` attribute, 
    while currency offers have a minimum purchase amount instead.
    
    If parsing standard offer, set it to ``True``.
    
    If parsing currency offer, set it to ``False``.
    
    Defaults to ``True``.
    """


class MoneyValueParser(FunPayHTMLObjectParser[MoneyValue, MoneyValueParsingOptions]):
    """
    Class for parsing money values.

    Possible locations:
        - On transactions page (https://funpay.com/account/balance)
        - On sales page (https://funpay.com/orders/trade)
        - On purchases page (https://funpay.com/orders/)
        - On subcategory offers list page (https://funpay.com/lots/<subcategory_id>/)
        - etc.
    """

    def _parse(self) -> MoneyValue:
        types = {
            MoneyValueParsingMode.FROM_ORDER_PREVIEW: self._parse_order_preview_type,
            MoneyValueParsingMode.FROM_TRANSACTION_PREVIEW: self._parse_transaction_preview_type,
            MoneyValueParsingMode.FROM_OFFER_PREVIEW: self._parse_offer_preview_type,
            MoneyValueParsingMode.FROM_STRING: self._parse_string_type,
        }
        return types[self.options.parsing_mode]()

    def _parse_order_preview_type(self) -> MoneyValue:
        val = self.tree.css_first('div.tc-price')
        return parse_money_value_string(
            val.text().strip(),
            raw_source=val.html or '',
            raise_on_error=True,
        )

    def _parse_transaction_preview_type(self) -> MoneyValue:
        val = self.tree.css_first('div.tc-price')
        return parse_money_value_string(
            val.text().strip(),
            raw_source=val.html,
            raise_on_error=True,
        )

    def _parse_offer_preview_type(self) -> MoneyValue:
        div = self.tree.css_first('div.tc-price')
        val_str = div.css('div')[0].text().strip()
        value = parse_money_value_string(
            val_str,
            raw_source=div.html,
            raise_on_error=True,
        )
        if self.options.parse_value_from_attribute:
            value.value = float(cast(str, div.attributes.get('data-s')))
        return value

    def _parse_string_type(self) -> MoneyValue:
        return parse_money_value_string(self.raw_source, raise_on_error=True)
