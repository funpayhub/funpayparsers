__all__ = ('OrderPageParsingOptions', 'OrderPageParser')

from dataclasses import dataclass
import re
from funpayparsers.parsers.base import FunPayHTMLObjectParser, ParsingOptions
from funpayparsers.parsers.page_header_parser import PageHeaderParser, PageHeaderParsingOptions
from funpayparsers.parsers.appdata_parser import AppDataParser, AppDataParsingOptions
from funpayparsers.parsers.money_value_parser import MoneyValueParser, MoneyValueParsingOptions
from funpayparsers.parsers.chat_parser import ChatParser, ChatParsingOptions
from funpayparsers.parsers.reviews_parser import ReviewsParser, ReviewsParsingOptions
from funpayparsers.types.pages import OrderPage
from funpayparsers.types.enums import OrderStatus


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

    def _parse(self):
        header_div = self.tree.css_first('header')
        app_data = self.tree.css_first('body').attributes['data-app-data']

        order_header = self.tree.css_first('h1.page-header')
        order_id = re.search(r'#[A-Z0-9]{8}', order_header.text(deep=False).strip()).group()[1:]
        order_status = OrderStatus.REFUNDED if order_header.css('span.text-warning') \
            else OrderStatus.COMPLETED if order_header.css('span.text-success') \
            else OrderStatus.PAID

        goods = self.tree.css('ul.order-secrets-list')
        if not goods:
            delivered_goods = None
        else:
            delivered_goods = [i.attributes['data-copy'] for i in goods[0].css('a.btn-copy')]

        review_div = self.tree.css_first('div.review-container')


        return OrderPage(
            raw_source=self.raw_source,
            header=PageHeaderParser(header_div.html, options=self.options.page_header_parsing_options).parse(),
            app_data=AppDataParser(app_data, self.options.app_data_parsing_options).parse(),
            order_id=order_id,
            order_status=order_status,
            order_total=...,
            delivered_goods=delivered_goods,
            images=...,
            order_category_name=...,
            order_subcategory_name=...,
            order_subcategory_id=...,
            review=ReviewsParser(review_div.html, options=self.options.reviews_parsing_options).parse().reviews[0],
            chat=...,
            data=...
        )