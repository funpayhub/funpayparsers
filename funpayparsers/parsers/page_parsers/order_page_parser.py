__all__ = ()

from dataclasses import dataclass
from funpayparsers.parsers.base import FunPayHTMLObjectParser, ParsingOptions
from funpayparsers.parsers.page_header_parser import PageHeaderParser, PageHeaderParsingOptions
from funpayparsers.parsers.appdata_parser import AppDataParser, AppDataParsingOptions
from funpayparsers.parsers.money_value_parser import MoneyValueParser, MoneyValueParsingOptions
from funpayparsers.parsers.chat_parser import ChatParser, ChatParsingOptions
from funpayparsers.parsers.reviews_parser import ReviewsParser, ReviewsParsingOptions
from funpayparsers.types.pages import OrderPage


@dataclass(frozen=True)
class OrderPageParsingOptions(ParsingOptions):
    """Options class for ``MainPageParser``."""

    page_header_parsing_options: PageHeaderParsingOptions = PageHeaderParsingOptions()
    """
    Options instance for ``PageHeaderParser``, which is used by ``OrderPageParser``.

    Defaults to ``PageHeaderParsingOptions()``.
    """

    app_data_parsing_options: AppDataParsingOptions = AppDataParsingOptions()
    """
    Options instance for ``AppDataParser``, which is used by ``OrderPageParser``.

    Defaults to ``AppDataParsingOptions()``.
    """

    chat_parsing_options: ChatParsingOptions = ChatParsingOptions()
    """
    Options instance for ``ChatParser``, which is used by ``OrderPageParser``.

    Defaults to ``ChatParsingOptions()``.
    """

    reviews_parsing_options: ReviewsParsingOptions = ReviewsParsingOptions()
    """
    Options instance for ``ReviewsParser``, which is used by ``OrderPageParser``.

    Defaults to ``ReviewsParsingOptions()``.
    """

    money_value_parsing_options: MoneyValueParsingOptions = MoneyValueParsingOptions()
    """
    Options instance for ``MoneyValueParser``, which is used by ``OrderPageParser``.
    
    ``parsing_mode`` option is hardcoded in ``OrderPageParser`` and is therefore ignored 
    if provided externally.

    Defaults to ``MoneyValueParsingOptions()``.
    """


class OrderPageParser(FunPayHTMLObjectParser[OrderPage, OrderPageParsingOptions]):
    """
    Class for parsing order pages (`https://funpay.com/users/<user_id>/`).
    """

    def parse(self):
        ...