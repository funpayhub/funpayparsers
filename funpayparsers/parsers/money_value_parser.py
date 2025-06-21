__all__ = ('MoneyValueParser', 'MoneyValueParserOptions')

from lxml import html
from dataclasses import dataclass
from funpayparsers.parsers.base import FunPayObjectParserOptions, FunPayObjectParser, T
from funpayparsers.types.common import MoneyValue
from enum import Enum


class MoneyValueParsingType(Enum):
    FROM_STRING = 0
    FROM_ORDER_PREVIEW = 1
    FROM_TRANSACTION_PREVIEW = 2
    FROM_LOT_PREVIEW = 3



@dataclass(frozen=True)
class MoneyValueParserOptions(FunPayObjectParserOptions):
    parsing_type: MoneyValueParsingType = MoneyValueParsingType.FROM_STRING


class MoneyValueParser(FunPayObjectParser[MoneyValue, MoneyValueParserOptions]):

    __options_cls__ = MoneyValueParserOptions

    def _parse(self):
        types = {
            MoneyValueParsingType.FROM_ORDER_PREVIEW: self._parse_order_preview_type,
            MoneyValueParsingType.FROM_TRANSACTION_PREVIEW: self._parse_transaction_preview_type,
            MoneyValueParsingType.FROM_LOT_PREVIEW: self._parse_lot_preview_type,
            MoneyValueParsingType.FROM_STRING: self._parse_string_type,
        }

    def _parse_order_preview_type(self):
        ...

    def _parse_transaction_preview_type(self):
        ...

    def _parse_lot_preview_type(self):
        ...

    def _parse_string_type(self):
        ...