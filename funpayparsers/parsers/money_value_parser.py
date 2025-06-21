__all__ = ('MoneyValueParser', 'MoneyValueParserOptions')

from lxml import html
from dataclasses import dataclass
from funpayparsers.parsers.base import FunPayObjectParserOptions, FunPayObjectParser, T
from funpayparsers.types.common import MoneyValue


@dataclass(frozen=True)
class MoneyValueParserOptions(FunPayObjectParserOptions):
    ...


class MoneyValueParser(FunPayObjectParser[MoneyValue, MoneyValueParserOptions]):

    __options_cls__ = MoneyValueParserOptions

    def _parse(self):
        ...