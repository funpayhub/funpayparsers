from __future__ import annotations


__all__ = ('OrderPageParsingOptions', 'OrderPageParser')

import re
from typing import cast
from dataclasses import dataclass

from funpayparsers.types.enums import OrderStatus, SubcategoryType
from funpayparsers.types.pages import OrderPage
from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.parsers.chat_parser import ChatParser, ChatParsingOptions
from funpayparsers.parsers.appdata_parser import AppDataParser, AppDataParsingOptions
from funpayparsers.parsers.reviews_parser import ReviewsParser, ReviewsParsingOptions
from funpayparsers.parsers.page_header_parser import (
    PageHeaderParser,
    PageHeaderParsingOptions,
)


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


class OrderPageParser(FunPayHTMLObjectParser[OrderPage, OrderPageParsingOptions]):
    """
    Class for parsing order pages (`https://funpay.com/users/<user_id>/`).
    """

    def _parse(self) -> OrderPage:
        order_header = self.tree.css_first('h1.page-header')
        order_id = re.search(  # type: ignore[union-attr]
            r'#[A-Z0-9]{8}',
            order_header.text(deep=False).strip(),
        ).group()[1:]
        order_status = (
            OrderStatus.REFUNDED
            if order_header.css('span.text-warning')
            else OrderStatus.COMPLETED
            if order_header.css('span.text-success')
            else OrderStatus.PAID
        )

        goods = self.tree.css('ul.order-secrets-list')
        if not goods:
            delivered_goods = None
        else:
            delivered_goods = [i.attributes['data-copy'] or '' for i in goods[0].css('a.btn-copy')]

        data = {}
        for i in self.tree.css('div.param-item:has(h5):not(:has(ul, ol))'):
            name = i.css('h5')
            if not name:
                continue

            try:
                value = i.css('div')
            except Exception:
                continue

            data[name[0].text().strip().lower()] = value[-1].text().strip()

        subcategory_url: str = self.tree.css_first(  # type: ignore[assignment,union-attr]
            'div.param-item:has(h5):not(:has(ul, ol)) a',
            strict=False,
        ).attributes['href']

        return OrderPage(
            raw_source=self.raw_source,
            header=PageHeaderParser(
                self.tree.css_first('header').html or '',
                options=self.options.page_header_parsing_options,
            ).parse(),
            app_data=AppDataParser(
                self.tree.css_first('body').attributes['data-app-data'] or '',
                self.options.app_data_parsing_options,
            ).parse(),
            order_id=order_id,
            order_status=order_status,
            delivered_goods=delivered_goods,
            images=[cast(str, i.attributes['href']) for i in self.tree.css('a.attachments-thumb')]
            or None,
            order_subcategory_id=int(subcategory_url.split('/')[-2]),
            order_subcategory_type=SubcategoryType.get_by_url(subcategory_url),
            review=(
                ReviewsParser(
                    self.tree.css_first('div.review-container').html or '',
                    options=self.options.reviews_parsing_options,
                )
                .parse()
                .reviews[0]
                if self.tree.css('div.review-container')
                else None
            ),
            chat=ChatParser(
                self.tree.css_first('div.chat').html or '',
                options=self.options.chat_parsing_options,
            ).parse(),
            data=data,
        )
