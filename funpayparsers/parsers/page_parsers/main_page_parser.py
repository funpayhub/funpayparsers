from __future__ import annotations


__all__ = ('MainPageParser', 'MainPageParsingOptions')

from dataclasses import dataclass

from funpayparsers.parsers.base import ParsingOptions, FunPayHTMLObjectParser
from funpayparsers.parsers.chat_parser import ChatParser, ChatParsingOptions
from funpayparsers.types.pages.main_page import MainPage
from funpayparsers.parsers.appdata_parser import AppDataParser, AppDataParsingOptions
from funpayparsers.parsers.categories_parser import (
    CategoriesParser,
    CategoriesParsingOptions,
)
from funpayparsers.parsers.page_header_parser import (
    PageHeaderParser,
    PageHeaderParsingOptions,
)


@dataclass(frozen=True)
class MainPageParsingOptions(ParsingOptions):
    """Options class for ``MainPageParser``."""

    page_header_parsing_options: PageHeaderParsingOptions = PageHeaderParsingOptions()
    """
    Options instance for ``PageHeaderParser``, which is used by ``MainPageParser``.

    Defaults to ``PageHeaderParsingOptions()``.
    """

    app_data_parsing_options: AppDataParsingOptions = AppDataParsingOptions()
    """
    Options instance for ``AppDataParser``, which is used by ``MainPageParser``.

    Defaults to ``AppDataParsingOptions()``.
    """

    categories_parsing_options: CategoriesParsingOptions = CategoriesParsingOptions()
    """
    Options instance for ``CategoriesParser``, which is used by ``MainPageParser``.

    Defaults to ``CategoriesParsingOptions()``.
    """

    chat_parsing_options: ChatParsingOptions = ChatParsingOptions()
    """
    Options instance for ``ChatParser``, which is used by ``MainPageParser``.

    Defaults to ``ChatParsingOptions()``.
    """


class MainPageParser(FunPayHTMLObjectParser[MainPage, MainPageParsingOptions]):
    """
    Class for parsing the main page (https://funpay.com).
    """

    def _parse(self) -> MainPage:
        header_div = self.tree.css('header')[0]
        categories_divs = self.tree.css('div.promo-game-list')
        if len(categories_divs) == 1:
            last_categories = []
            categories = CategoriesParser(
                categories_divs[0].html or '',
                options=self.options.categories_parsing_options,
            ).parse()
        else:
            last_categories = CategoriesParser(
                categories_divs[0].html or '',
                options=self.options.categories_parsing_options,
            ).parse()
            categories = CategoriesParser(
                categories_divs[1].html or '',
                options=self.options.categories_parsing_options,
            ).parse()

        secret_chat_div = self.tree.css('div.chat')

        return MainPage(
            raw_source=self.tree.html or '',
            header=PageHeaderParser(
                header_div.html or '',
                options=self.options.page_header_parsing_options,
            ).parse(),
            last_categories=last_categories,
            categories=categories,
            secret_chat=ChatParser(
                secret_chat_div[0].html or '',
                options=self.options.chat_parsing_options,
            ).parse()
            if secret_chat_div
            else None,
            app_data=AppDataParser(
                self.tree.css('body')[0].attributes.get('data-app-data') or '',
                self.options.app_data_parsing_options,
            ).parse(),
        )
