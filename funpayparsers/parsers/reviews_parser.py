__all__ = (
    'ReviewsParser',
    'ReviewsParserOptions'
)

from funpayparsers.parsers.base import FunPayObjectParserOptions, FunPayObjectParser
from funpayparsers.types.review import Review
from dataclasses import dataclass


@dataclass(frozen=True)
class ReviewsParserOptions(FunPayObjectParserOptions):
    ...


class ReviewsParser(FunPayObjectParser[
                        list[Review],
                        ReviewsParserOptions
                    ]):

    __options_cls__ = ReviewsParserOptions

    def _parse(self):
        ...

