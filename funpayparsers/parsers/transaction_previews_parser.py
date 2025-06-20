__all__ = ('TransactionPreviewsParser', 'TransactionPreviewsParserOptions')

from dataclasses import dataclass
from funpayparsers.parsers.base import FunPayObjectParser, FunPayObjectParserOptions
from funpayparsers.types import TransactionPreview, TransactionStatus


@dataclass(frozen=True)
class TransactionPreviewsParserOptions(FunPayObjectParserOptions):
    ...


class TransactionPreviewsParser(FunPayObjectParser[
    list[TransactionPreview],
    TransactionPreviewsParserOptions
]):

    __options_cls__ = TransactionPreviewsParserOptions

    def _parse(self):
        ...
